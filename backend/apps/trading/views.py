"""
Views for PortfolioPro Trading Module.
Handles Order placement, instant Market Order execution, Limit Order queue,
cancellations, execution contract notes, and back-office order supervision.
"""
import logging
from decimal import Decimal
from django.db import transaction, models
from django.utils import timezone
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.trading.models import TradeOrder, TradeExecution
from apps.trading.serializers import (
    TradeOrderSerializer,
    TradeOrderCreateSerializer,
    TradeOrderCancelSerializer,
    TradeExecutionSerializer,
)
from apps.accounts.models import TradingAccount, AccountTransaction
from apps.market.models import Security
from apps.portfolio.models import Portfolio, PortfolioHolding
from apps.common.responses import api_success, api_error
from apps.common.permissions import IsFinanceOfficer
from apps.authentication.models import User

logger = logging.getLogger(__name__)

BROKERAGE_RATE = Decimal('0.0003')  # 0.03%


class OrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for customer trading orders.
    Supports placing BUY/SELL Market & Limit orders, tracking order book, and cancellations.
    """
    serializer_class = TradeOrderSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        if user.role in (User.ROLE_FINANCE_OFFICER, User.ROLE_ADMIN) or user.is_staff:
            queryset = TradeOrder.objects.all()
        else:
            queryset = TradeOrder.objects.filter(user=user)

        queryset = queryset.select_related('user', 'account', 'security', 'security__quote').prefetch_related('executions')

        # Filter by order status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(order_status=status_filter.upper())

        # Filter by transaction type (BUY / SELL)
        tx_type = self.request.query_params.get('transaction_type') or self.request.query_params.get('type')
        if tx_type:
            queryset = queryset.filter(transaction_type=tx_type.upper())

        # Filter by stock symbol
        symbol = self.request.query_params.get('symbol')
        if symbol:
            queryset = queryset.filter(security__symbol__iexact=symbol.strip())

        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return api_success(
                data={
                    "count": self.paginator.page.paginator.count,
                    "orders": serializer.data
                },
                message="Order book retrieved successfully."
            )
        serializer = self.get_serializer(queryset, many=True)
        return api_success(
            data={"count": queryset.count(), "orders": serializer.data},
            message="Order book retrieved successfully."
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_success(
            data={"order": serializer.data},
            message=f"Order {instance.id} retrieved."
        )

    @extend_schema(request=TradeOrderCreateSerializer, responses={201: TradeOrderSerializer})
    def create(self, request, *args, **kwargs):
        """
        Place a new equity order.
        MARKET orders auto-execute immediately within an atomic transaction:
          - Cash / holding check
          - Balance update + Ledger transaction
          - Trade execution record
          - Portfolio holding position update
        LIMIT orders enter the order book with PENDING status.
        """
        create_serializer = TradeOrderCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        if not create_serializer.is_valid():
            return api_error(
                message="Order placement validation failed.",
                errors=create_serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        data = create_serializer.validated_data
        security = data['resolved_security']
        account = data['resolved_account']
        order_type = data['order_type']
        tx_type = data['transaction_type']
        quantity = data['quantity']
        limit_price = data.get('limit_price')

        if order_type == TradeOrder.TYPE_MARKET:
            return self._execute_market_order(request.user, account, security, tx_type, quantity)
        else:
            return self._create_limit_order(request.user, account, security, order_type, tx_type, quantity, limit_price)

    def _execute_market_order(self, user, account, security, tx_type, quantity):
        """
        Instant execution engine for MARKET orders.
        """
        with transaction.atomic():
            # Lock the trading account
            locked_account = TradingAccount.objects.select_for_update().get(id=account.id)
            locked_security = Security.objects.select_related('quote').get(id=security.id)

            if not hasattr(locked_security, 'quote') or not locked_security.quote:
                return api_error(
                    message=f"Live quote unavailable for {locked_security.symbol}.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            execution_price = locked_security.quote.ltp
            order_value = Decimal(quantity) * execution_price
            brokerage = (order_value * BROKERAGE_RATE).quantize(Decimal('0.0001'))

            # Create initial order record
            order = TradeOrder.objects.create(
                user=user,
                account=locked_account,
                security=locked_security,
                order_type=TradeOrder.TYPE_MARKET,
                transaction_type=tx_type,
                quantity=quantity,
                filled_quantity=0,
                executed_price=execution_price,
                order_status=TradeOrder.STATUS_PENDING
            )

            # Ensure default portfolio exists
            portfolio, _ = Portfolio.objects.get_or_create(
                user=user,
                is_default=True,
                defaults={'name': 'Primary Portfolio'}
            )

            if tx_type == TradeOrder.TX_BUY:
                total_cost = order_value + brokerage
                if locked_account.cash_balance < total_cost:
                    order.order_status = TradeOrder.STATUS_REJECTED
                    order.rejection_reason = (
                        f"Insufficient cash balance: Required ₹ {total_cost:.2f}, "
                        f"Available ₹ {locked_account.cash_balance:.2f}."
                    )
                    order.save()
                    return api_error(
                        message="Order rejected due to insufficient cash balance.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                # Deduct cash
                locked_account.cash_balance -= total_cost
                locked_account.save(update_fields=['cash_balance', 'updated_at'])

                # Create ledger debit transaction
                AccountTransaction.objects.create(
                    account=locked_account,
                    transaction_type=AccountTransaction.TYPE_TRADE_DEBIT,
                    amount=total_cost,
                    balance_after=locked_account.cash_balance,
                    reference_note=(
                        f"Buy: {quantity}x {locked_security.symbol} @ ₹ {execution_price:.2f} "
                        f"(Value: ₹ {order_value:.2f}, Brokerage: ₹ {brokerage:.2f})"
                    ),
                    status=AccountTransaction.STATUS_COMPLETED
                )

                # Update or create holding with weighted average buy price
                holding, created = PortfolioHolding.objects.select_for_update().get_or_create(
                    portfolio=portfolio,
                    security=locked_security,
                    defaults={
                        'quantity': quantity,
                        'average_buy_price': execution_price,
                        'total_invested': order_value,
                        'realized_pnl': Decimal('0.0000')
                    }
                )
                if not created:
                    new_qty = holding.quantity + quantity
                    new_invested = holding.total_invested + order_value
                    holding.quantity = new_qty
                    holding.total_invested = new_invested
                    holding.average_buy_price = (new_invested / Decimal(new_qty)).quantize(Decimal('0.0001'))
                    holding.save()

                net_amount = total_cost

            elif tx_type == TradeOrder.TX_SELL:
                holding = PortfolioHolding.objects.select_for_update().filter(
                    portfolio=portfolio,
                    security=locked_security
                ).first()

                if not holding or holding.quantity < quantity:
                    order.order_status = TradeOrder.STATUS_REJECTED
                    order.rejection_reason = "Insufficient equity holdings at time of market execution."
                    order.save()
                    return api_error(
                        message="Order rejected: Insufficient holdings to execute sell order.",
                        status_code=status.HTTP_400_BAD_REQUEST
                    )

                net_credit = order_value - brokerage

                # Credit cash
                locked_account.cash_balance += net_credit
                locked_account.save(update_fields=['cash_balance', 'updated_at'])

                # Create ledger credit transaction
                AccountTransaction.objects.create(
                    account=locked_account,
                    transaction_type=AccountTransaction.TYPE_TRADE_CREDIT,
                    amount=net_credit,
                    balance_after=locked_account.cash_balance,
                    reference_note=(
                        f"Sell: {quantity}x {locked_security.symbol} @ ₹ {execution_price:.2f} "
                        f"(Value: ₹ {order_value:.2f}, Brokerage: ₹ {brokerage:.2f})"
                    ),
                    status=AccountTransaction.STATUS_COMPLETED
                )

                # Update holdings & compute realized PnL
                cost_of_sold = Decimal(quantity) * holding.average_buy_price
                realized_gain = order_value - cost_of_sold - brokerage
                holding.realized_pnl = (holding.realized_pnl or Decimal('0.0000')) + realized_gain
                holding.quantity -= quantity

                if holding.quantity == 0:
                    holding.delete()
                else:
                    holding.total_invested = (Decimal(holding.quantity) * holding.average_buy_price).quantize(Decimal('0.0001'))
                    holding.save()

                net_amount = net_credit

            # Complete order record
            now = timezone.now()
            order.filled_quantity = quantity
            order.executed_price = execution_price
            order.order_status = TradeOrder.STATUS_FILLED
            order.executed_at = now
            order.save()

            # Generate contract note execution record
            execution = TradeExecution.objects.create(
                order=order,
                security=locked_security,
                user=user,
                quantity=quantity,
                execution_price=execution_price,
                brokerage_fee=brokerage,
                net_amount=net_amount
            )

            logger.info(
                f"Market order {order.id} FILLED: {tx_type} {quantity}x {locked_security.symbol} "
                f"@ ₹ {execution_price:.2f} for {user.username}"
            )

        refreshed_order = TradeOrder.objects.select_related(
            'user', 'account', 'security', 'security__quote'
        ).prefetch_related('executions').get(id=order.id)

        return api_success(
            data={"order": TradeOrderSerializer(refreshed_order).data},
            message=f"Market order executed successfully: {tx_type} {quantity} shares of {locked_security.symbol} @ ₹ {execution_price:.2f}.",
            status_code=status.HTTP_201_CREATED
        )

    def _create_limit_order(self, user, account, security, order_type, tx_type, quantity, limit_price):
        """
        Places a pending LIMIT order into the queue and reserves margin for BUYs.
        """
        with transaction.atomic():
            locked_account = TradingAccount.objects.select_for_update().get(id=account.id)
            trade_value = Decimal(quantity) * limit_price
            brokerage = (trade_value * BROKERAGE_RATE).quantize(Decimal('0.0001'))

            if tx_type == TradeOrder.TX_BUY:
                required_margin = trade_value + brokerage
                if locked_account.available_balance < required_margin:
                    return api_error(
                        message=(
                            f"Insufficient available balance to place limit order. "
                            f"Required margin: ₹ {required_margin:.2f}, Available: ₹ {locked_account.available_balance:.2f}."
                        ),
                        status_code=status.HTTP_400_BAD_REQUEST
                    )
                locked_account.margin_used += required_margin
                locked_account.save(update_fields=['margin_used', 'updated_at'])

            order = TradeOrder.objects.create(
                user=user,
                account=locked_account,
                security=security,
                order_type=order_type,
                transaction_type=tx_type,
                quantity=quantity,
                filled_quantity=0,
                limit_price=limit_price,
                order_status=TradeOrder.STATUS_PENDING
            )

            logger.info(
                f"Limit order {order.id} placed: {tx_type} {quantity}x {security.symbol} "
                f"@ ₹ {limit_price:.2f} by {user.username}"
            )

        refreshed_order = TradeOrder.objects.select_related(
            'user', 'account', 'security', 'security__quote'
        ).prefetch_related('executions').get(id=order.id)

        return api_success(
            data={"order": TradeOrderSerializer(refreshed_order).data},
            message=f"Limit order queued successfully: {tx_type} {quantity} shares of {security.symbol} @ limit ₹ {limit_price:.2f}.",
            status_code=status.HTTP_201_CREATED
        )

    @extend_schema(request=TradeOrderCancelSerializer, responses={200: TradeOrderSerializer})
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        """
        Cancel a pending order and release reserved margin if applicable.
        """
        order = self.get_object()

        with transaction.atomic():
            locked_order = TradeOrder.objects.select_for_update().get(id=order.id)
            if locked_order.order_status != TradeOrder.STATUS_PENDING:
                return api_error(
                    message=f"Cannot cancel order in status '{locked_order.order_status}'. Only PENDING orders can be cancelled.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Release locked margin for BUY limit orders
            if locked_order.transaction_type == TradeOrder.TX_BUY and locked_order.limit_price:
                locked_account = TradingAccount.objects.select_for_update().get(id=locked_order.account.id)
                margin_released = (
                    Decimal(locked_order.quantity) * locked_order.limit_price * (Decimal('1') + BROKERAGE_RATE)
                ).quantize(Decimal('0.0001'))
                locked_account.margin_used = max(Decimal('0.0000'), locked_account.margin_used - margin_released)
                locked_account.save(update_fields=['margin_used', 'updated_at'])

            locked_order.order_status = TradeOrder.STATUS_CANCELLED
            locked_order.cancelled_at = timezone.now()
            locked_order.save(update_fields=['order_status', 'cancelled_at', 'updated_at'])

            logger.info(f"Order {locked_order.id} cancelled by {request.user.username}")

        refreshed = TradeOrder.objects.select_related(
            'user', 'account', 'security', 'security__quote'
        ).prefetch_related('executions').get(id=order.id)

        return api_success(
            data={"order": TradeOrderSerializer(refreshed).data},
            message=f"Order {order.id} has been cancelled successfully."
        )

    @extend_schema(responses={200: TradeExecutionSerializer(many=True)})
    @action(detail=True, methods=['get'], url_path='trades')
    def trades(self, request, pk=None):
        """
        List all executions / contract notes for a specific order.
        """
        order = self.get_object()
        executions = order.executions.select_related('security', 'user').order_by('-executed_at')
        serializer = TradeExecutionSerializer(executions, many=True)
        return api_success(
            data={"count": executions.count(), "executions": serializer.data},
            message=f"Executions for order {order.id} retrieved."
        )


class TradeExecutionListView(generics.ListAPIView):
    """
    Paginated endpoint listing trade execution contract notes.
    Customers view their own executions; Finance Officers can view platform-wide.
    """
    serializer_class = TradeExecutionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in (User.ROLE_FINANCE_OFFICER, User.ROLE_ADMIN) or user.is_staff:
            queryset = TradeExecution.objects.all()
        else:
            queryset = TradeExecution.objects.filter(user=user)

        symbol = self.request.query_params.get('symbol')
        if symbol:
            queryset = queryset.filter(security__symbol__iexact=symbol.strip())

        return queryset.select_related('security', 'user', 'order').order_by('-executed_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return api_success(
                data={
                    "count": self.paginator.page.paginator.count,
                    "executions": serializer.data
                },
                message="Trade executions retrieved successfully."
            )
        serializer = self.get_serializer(queryset, many=True)
        return api_success(
            data={"count": queryset.count(), "executions": serializer.data},
            message="Trade executions retrieved successfully."
        )


class AllOrdersViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Supervisory ViewSet strictly for Finance Officers to audit all platform orders
    and intervene on anomalous or high-risk transactions.
    """
    serializer_class = TradeOrderSerializer
    permission_classes = [IsAuthenticated, IsFinanceOfficer]

    def get_queryset(self):
        queryset = TradeOrder.objects.all().select_related(
            'user', 'account', 'security', 'security__quote'
        ).prefetch_related('executions')

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(order_status=status_param.upper())

        symbol = self.request.query_params.get('symbol')
        if symbol:
            queryset = queryset.filter(security__symbol__iexact=symbol.strip())

        username = self.request.query_params.get('username')
        if username:
            queryset = queryset.filter(user__username__icontains=username.strip())

        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return api_success(
                data={
                    "count": self.paginator.page.paginator.count,
                    "orders": serializer.data
                },
                message="All platform orders retrieved for supervisory audit."
            )
        serializer = self.get_serializer(queryset, many=True)
        return api_success(
            data={"count": queryset.count(), "orders": serializer.data},
            message="All platform orders retrieved for supervisory audit."
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_success(
            data={"order": serializer.data},
            message=f"Order {instance.id} audit details retrieved."
        )

    @action(detail=True, methods=['post'], url_path='intervene')
    def intervene(self, request, pk=None):
        """
        Finance Officer action to freeze or cancel an anomalous order.
        """
        order = self.get_object()
        action_type = request.data.get('action', 'CANCEL').upper()
        reason = request.data.get('reason', 'Intervention by Finance Officer')

        with transaction.atomic():
            locked = TradeOrder.objects.select_for_update().get(id=order.id)
            if locked.order_status not in [TradeOrder.STATUS_PENDING, TradeOrder.STATUS_PARTIALLY_FILLED]:
                return api_error(
                    message=f"Order status is '{locked.order_status}'. Intervention is only allowed on active orders.",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # Release locked margin if BUY limit order
            if locked.transaction_type == TradeOrder.TX_BUY and locked.limit_price:
                account = TradingAccount.objects.select_for_update().get(id=locked.account.id)
                margin = (
                    Decimal(locked.quantity) * locked.limit_price * (Decimal('1') + BROKERAGE_RATE)
                ).quantize(Decimal('0.0001'))
                account.margin_used = max(Decimal('0.0000'), account.margin_used - margin)
                account.save(update_fields=['margin_used', 'updated_at'])

            locked.order_status = TradeOrder.STATUS_CANCELLED
            locked.rejection_reason = f"FO Intervention: {reason}"
            locked.cancelled_at = timezone.now()
            locked.save()

            logger.warning(
                f"Order {locked.id} intervened ({action_type}) by FO {request.user.username}: {reason}"
            )

        refreshed = TradeOrder.objects.select_related(
            'user', 'account', 'security', 'security__quote'
        ).prefetch_related('executions').get(id=order.id)

        return api_success(
            data={"order": TradeOrderSerializer(refreshed).data},
            message=f"Order {order.id} cancelled via Finance Officer intervention."
        )
