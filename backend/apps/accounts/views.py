"""
Views for PortfolioPro Accounts Module.
Handles TradingAccount balances, deposits, withdrawals, ledger transactions, and KYC verification.
"""
import logging
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.accounts.models import TradingAccount, AccountTransaction, KYCRecord
from apps.accounts.serializers import (
    TradingAccountSerializer,
    FundDepositSerializer,
    FundWithdrawSerializer,
    AccountTransactionSerializer,
    KYCRecordSerializer,
    KYCVerifySerializer,
)
from apps.common.responses import api_success, api_error
from apps.common.permissions import IsCustomer, IsFinanceOfficer, IsAdminUser
from apps.authentication.models import User

logger = logging.getLogger(__name__)


class TradingAccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for customer trading account management, balance inquiries,
    and cash deposit/withdrawal operations.
    """
    serializer_class = TradingAccountSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.role in (User.ROLE_FINANCE_OFFICER, User.ROLE_ADMIN) or user.is_staff:
            return TradingAccount.objects.all().select_related('user')
        return TradingAccount.objects.filter(user=user).select_related('user')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return api_success(
                data={
                    "count": self.paginator.page.paginator.count,
                    "accounts": serializer.data
                },
                message="Trading accounts retrieved successfully."
            )
        serializer = self.get_serializer(queryset, many=True)
        return api_success(
            data={"accounts": serializer.data},
            message="Trading accounts retrieved successfully."
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_success(
            data={"account": serializer.data},
            message="Trading account details retrieved."
        )

    @extend_schema(responses={200: TradingAccountSerializer})
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        Retrieve summary of the authenticated customer's trading account.
        """
        account = TradingAccount.objects.filter(user=request.user).first()
        if not account:
            if request.user.role == User.ROLE_CUSTOMER:
                account = TradingAccount.objects.create(
                    user=request.user,
                    account_number=f"PPRO-{request.user.id.hex[:6].upper()}"
                )
            else:
                return api_error(
                    message="Trading account not found for privileged supervisory role.",
                    status_code=status.HTTP_404_NOT_FOUND
                )

        serializer = self.get_serializer(account)
        return api_success(
            data={"account": serializer.data},
            message="Trading account summary retrieved successfully."
        )

    @extend_schema(request=FundDepositSerializer, responses={200: TradingAccountSerializer})
    @action(detail=False, methods=['post'], url_path='deposit')
    def deposit(self, request):
        """
        Simulate an instant virtual cash deposit into customer's trading account.
        """
        serializer = FundDepositSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return api_error(
                message="Deposit validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        amount = serializer.validated_data['amount']
        note = serializer.validated_data.get('reference_note') or 'Virtual Cash Deposit'

        with transaction.atomic():
            account = TradingAccount.objects.select_for_update().filter(user=request.user).first()
            if not account:
                return api_error(
                    message="Trading account not found.",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            if account.account_status != TradingAccount.STATUS_ACTIVE:
                return api_error(
                    message=f"Account status is {account.account_status}. Deposits are disallowed.",
                    status_code=status.HTTP_403_FORBIDDEN
                )

            account.cash_balance += amount
            account.save(update_fields=['cash_balance', 'updated_at'])

            tx = AccountTransaction.objects.create(
                account=account,
                transaction_type=AccountTransaction.TYPE_DEPOSIT,
                amount=amount,
                balance_after=account.cash_balance,
                reference_note=note,
                status=AccountTransaction.STATUS_COMPLETED
            )

            logger.info(
                f"Deposit successful: ₹ {amount:.2f} to {account.account_number} by {request.user.username}"
            )

        updated_account = TradingAccountSerializer(account).data
        return api_success(
            data={
                "account": updated_account,
                "transaction_id": str(tx.id),
                "deposited_amount": str(amount),
                "new_balance": str(account.cash_balance),
            },
            message=f"Successfully credited ₹ {amount:.2f} to trading account {account.account_number}."
        )

    @extend_schema(request=FundWithdrawSerializer, responses={200: TradingAccountSerializer})
    @action(detail=False, methods=['post'], url_path='withdraw')
    def withdraw(self, request):
        """
        Submit a fund withdrawal request against available unencumbered cash balance.
        """
        serializer = FundWithdrawSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return api_error(
                message="Withdrawal validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        amount = serializer.validated_data['amount']
        note = serializer.validated_data.get('reference_note') or 'Virtual Cash Withdrawal'

        with transaction.atomic():
            account = TradingAccount.objects.select_for_update().filter(user=request.user).first()
            if not account:
                return api_error(
                    message="Trading account not found.",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            if account.account_status != TradingAccount.STATUS_ACTIVE:
                return api_error(
                    message=f"Account status is {account.account_status}. Withdrawals are disallowed.",
                    status_code=status.HTTP_403_FORBIDDEN
                )

            if amount > account.available_balance:
                return api_error(
                    message=(
                        f"Insufficient available balance. Requested: ₹ {amount:.2f}, "
                        f"Available: ₹ {account.available_balance:.2f}"
                    ),
                    errors={"amount": ["Withdrawal exceeds available balance."]},
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            account.cash_balance -= amount
            account.save(update_fields=['cash_balance', 'updated_at'])

            tx = AccountTransaction.objects.create(
                account=account,
                transaction_type=AccountTransaction.TYPE_WITHDRAWAL,
                amount=amount,
                balance_after=account.cash_balance,
                reference_note=note,
                status=AccountTransaction.STATUS_COMPLETED
            )

            logger.info(
                f"Withdrawal successful: ₹ {amount:.2f} from {account.account_number} by {request.user.username}"
            )

        updated_account = TradingAccountSerializer(account).data
        return api_success(
            data={
                "account": updated_account,
                "transaction_id": str(tx.id),
                "withdrawn_amount": str(amount),
                "new_balance": str(account.cash_balance),
            },
            message=f"Successfully debited ₹ {amount:.2f} from trading account {account.account_number}."
        )

    @extend_schema(responses={200: TradingAccountSerializer(many=True)})
    @action(
        detail=False,
        methods=['get'],
        url_path='admin/all',
        permission_classes=[IsAuthenticated, IsFinanceOfficer]
    )
    def admin_all(self, request):
        """
        Supervisory endpoint for Finance Officers: List all customer trading accounts with KYC state.
        """
        accounts = TradingAccount.objects.all().select_related('user', 'user__kyc_record')
        status_filter = request.query_params.get('status')
        if status_filter:
            accounts = accounts.filter(account_status=status_filter.upper())

        page = self.paginate_queryset(accounts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return api_success(
                data={
                    "count": self.paginator.page.paginator.count,
                    "accounts": serializer.data
                },
                message="All customer trading accounts retrieved."
            )
        serializer = self.get_serializer(accounts, many=True)
        return api_success(
            data={"count": accounts.count(), "accounts": serializer.data},
            message="All customer trading accounts retrieved."
        )


class AccountTransactionListView(generics.ListAPIView):
    """
    Paginated ledger view of account transactions (deposits, withdrawals, trades).
    Customers see their own transactions; Finance Officers can inspect all accounts.
    """
    serializer_class = AccountTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (User.ROLE_FINANCE_OFFICER, User.ROLE_ADMIN) or user.is_staff:
            queryset = AccountTransaction.objects.all()
        else:
            queryset = AccountTransaction.objects.filter(account__user=user)

        tx_type = self.request.query_params.get('type')
        if tx_type:
            queryset = queryset.filter(transaction_type=tx_type.upper())

        tx_status = self.request.query_params.get('status')
        if tx_status:
            queryset = queryset.filter(status=tx_status.upper())

        return queryset.select_related('account', 'account__user').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return api_success(
                data={
                    "count": self.paginator.page.paginator.count,
                    "transactions": serializer.data
                },
                message="Transaction ledger retrieved successfully."
            )
        serializer = self.get_serializer(queryset, many=True)
        return api_success(
            data={"count": queryset.count(), "transactions": serializer.data},
            message="Transaction ledger retrieved successfully."
        )


class KYCViewSet(viewsets.ModelViewSet):
    """
    ViewSet for KYC verification lifecycle.
    Customers submit and inspect their KYC details.
    Finance Officers review, approve, or reject KYC submissions.
    """
    serializer_class = KYCRecordSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.role in (User.ROLE_FINANCE_OFFICER, User.ROLE_ADMIN) or user.is_staff:
            queryset = KYCRecord.objects.all().select_related('user', 'verified_by')
            status_param = self.request.query_params.get('status')
            if status_param:
                queryset = queryset.filter(verification_status=status_param.upper())
            return queryset
        return KYCRecord.objects.filter(user=user).select_related('user', 'verified_by')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return api_success(
            data={"count": queryset.count(), "kyc_records": serializer.data},
            message="KYC records retrieved successfully."
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_success(
            data={"kyc": serializer.data},
            message="KYC record retrieved."
        )

    def create(self, request, *args, **kwargs):
        """
        Submit KYC compliance details for the authenticated user.
        """
        if KYCRecord.objects.filter(user=request.user).exists():
            return api_error(
                message="KYC record already exists for this account. Submission cannot be duplicated.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="KYC submission validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        kyc = serializer.save(
            user=request.user,
            verification_status=KYCRecord.STATUS_PENDING
        )
        logger.info(f"KYC submitted for review by user {request.user.username}")

        return api_success(
            data={"kyc": KYCRecordSerializer(kyc).data},
            message="KYC documents submitted successfully. Verification pending with Finance Officer.",
            status_code=status.HTTP_201_CREATED
        )

    @extend_schema(responses={200: KYCRecordSerializer})
    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Retrieve authenticated user's KYC record.
        """
        kyc = KYCRecord.objects.filter(user=request.user).first()
        if not kyc:
            return api_error(
                message="No KYC record found for authenticated user.",
                status_code=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(kyc)
        return api_success(
            data={"kyc": serializer.data},
            message="User KYC record retrieved."
        )

    @extend_schema(request=KYCVerifySerializer, responses={200: KYCRecordSerializer})
    @action(
        detail=True,
        methods=['patch', 'post'],
        url_path='verify',
        permission_classes=[IsAuthenticated, IsFinanceOfficer]
    )
    def verify(self, request, pk=None):
        """
        Finance Officer action: Approve or reject customer KYC record.
        """
        kyc = self.get_object()
        serializer = KYCVerifySerializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="KYC verification input invalid.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        status_val = serializer.validated_data['verification_status']
        reason = serializer.validated_data.get('rejection_reason', '')

        kyc.verification_status = status_val
        kyc.verified_by = request.user
        kyc.verified_at = timezone.now()
        kyc.rejection_reason = reason if status_val == KYCRecord.STATUS_REJECTED else ''
        kyc.save()

        logger.info(
            f"KYC {kyc.id} for {kyc.user.username} updated to {status_val} by {request.user.username}"
        )

        return api_success(
            data={"kyc": KYCRecordSerializer(kyc).data},
            message=f"KYC record has been marked as {status_val}."
        )
