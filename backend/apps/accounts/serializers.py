"""
Serializers for PortfolioPro Accounts Module.
Handles TradingAccount, Fund Deposits/Withdrawals, Account Transactions, and KYC Compliance.
"""
import re
from decimal import Decimal
from rest_framework import serializers

from apps.accounts.models import TradingAccount, AccountTransaction, KYCRecord


class TradingAccountSerializer(serializers.ModelSerializer):
    """
    Read-only serializer representing customer's virtual trading account.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    available_balance = serializers.DecimalField(
        max_digits=18,
        decimal_places=4,
        read_only=True
    )

    class Meta:
        model = TradingAccount
        fields = [
            'id',
            'user',
            'username',
            'account_number',
            'currency',
            'cash_balance',
            'margin_used',
            'available_balance',
            'account_status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'username',
            'account_number',
            'currency',
            'cash_balance',
            'margin_used',
            'available_balance',
            'account_status',
            'created_at',
            'updated_at',
        ]


class FundDepositSerializer(serializers.Serializer):
    """
    Write serializer for depositing virtual funds into a trading account.
    Max limit: ₹ 10,00,000 per transaction.
    """
    amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=4,
        required=True
    )
    reference_note = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default='Virtual Cash Deposit'
    )

    def validate_amount(self, value):
        if value <= Decimal('0.0000'):
            raise serializers.ValidationError("Deposit amount must be strictly greater than zero.")
        if value > Decimal('1000000.0000'):
            raise serializers.ValidationError("Single deposit limit cannot exceed ₹ 10,00,000.00.")
        return value


class FundWithdrawSerializer(serializers.Serializer):
    """
    Write serializer for withdrawing funds from a trading account.
    Validates that requested withdrawal does not exceed available unencumbered cash.
    """
    amount = serializers.DecimalField(
        max_digits=18,
        decimal_places=4,
        required=True
    )
    reference_note = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default='Virtual Cash Withdrawal'
    )

    def validate_amount(self, value):
        if value <= Decimal('0.0000'):
            raise serializers.ValidationError("Withdrawal amount must be strictly greater than zero.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'trading_account'):
            account = request.user.trading_account
            amount = data.get('amount')
            if amount is not None and amount > account.available_balance:
                raise serializers.ValidationError({
                    'amount': (
                        f"Withdrawal amount (₹ {amount:.2f}) exceeds available unencumbered "
                        f"balance (₹ {account.available_balance:.2f})."
                    )
                })
        return data


class AccountTransactionSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for immutable ledger transactions.
    """
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = AccountTransaction
        fields = [
            'id',
            'account',
            'transaction_type',
            'transaction_type_display',
            'amount',
            'balance_after',
            'reference_note',
            'status',
            'status_display',
            'created_at',
        ]
        read_only_fields = fields


class KYCRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for KYC Compliance Records.
    Supports reading and customer submission with format validation.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    verified_by_username = serializers.CharField(
        source='verified_by.username',
        read_only=True,
        default=None
    )
    verification_status_display = serializers.CharField(
        source='get_verification_status_display',
        read_only=True
    )

    class Meta:
        model = KYCRecord
        fields = [
            'id',
            'user',
            'username',
            'pan_number',
            'aadhaar_masked',
            'bank_account_number',
            'bank_ifsc',
            'verification_status',
            'verification_status_display',
            'verified_by',
            'verified_by_username',
            'verified_at',
            'rejection_reason',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'username',
            'verification_status',
            'verification_status_display',
            'verified_by',
            'verified_by_username',
            'verified_at',
            'rejection_reason',
            'created_at',
            'updated_at',
        ]

    def validate_pan_number(self, value):
        pan_clean = value.strip().upper()
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', pan_clean):
            raise serializers.ValidationError(
                "Invalid PAN format. Must be 10 characters: 5 letters, 4 digits, 1 letter (e.g. ABCDE1234F)."
            )
        return pan_clean

    def validate_aadhaar_masked(self, value):
        aadhaar_clean = value.strip().replace('-', '').replace(' ', '')
        if len(aadhaar_clean) != 12:
            raise serializers.ValidationError("Aadhaar number must contain exactly 12 characters.")
        if not re.match(r'^[0-9X]{12}$', aadhaar_clean, re.IGNORECASE):
            raise serializers.ValidationError("Masked Aadhaar format must be e.g. XXXXXXXX1234 or 12 digits.")
        return aadhaar_clean

    def validate_bank_account_number(self, value):
        account_clean = value.strip()
        if not re.match(r'^\d{9,18}$', account_clean):
            raise serializers.ValidationError(
                "Invalid bank account number. Must contain between 9 and 18 numerical digits."
            )
        return account_clean

    def validate_bank_ifsc(self, value):
        ifsc_clean = value.strip().upper()
        if not re.match(r'^[A-Z]{4}0[A-Z0-9]{6}$', ifsc_clean):
            raise serializers.ValidationError(
                "Invalid IFSC format. Must be 11 characters starting with 4 letters, 0, then 6 alphanumeric characters."
            )
        return ifsc_clean


class KYCVerifySerializer(serializers.Serializer):
    """
    Serializer used by Finance Officers to approve or reject customer KYC submissions.
    """
    verification_status = serializers.ChoiceField(
        choices=[KYCRecord.STATUS_VERIFIED, KYCRecord.STATUS_REJECTED],
        required=True
    )
    rejection_reason = serializers.CharField(
        max_length=500,
        required=False,
        allow_blank=True,
        default=''
    )

    def validate(self, data):
        status_val = data.get('verification_status')
        reason = data.get('rejection_reason', '').strip()
        if status_val == KYCRecord.STATUS_REJECTED and not reason:
            raise serializers.ValidationError({
                'rejection_reason': "Rejection reason is mandatory when rejecting KYC."
            })
        return data
