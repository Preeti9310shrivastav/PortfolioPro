"""
Serializers for PortfolioPro Trading Module.
Handles TradeOrder placement, validation, cancellation, and TradeExecution contract notes.
"""
from decimal import Decimal
from rest_framework import serializers

from apps.trading.models import TradeOrder, TradeExecution
from apps.market.models import Security
from apps.accounts.models import TradingAccount
from apps.portfolio.models import Portfolio, PortfolioHolding


class TradeExecutionSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for trade execution confirmations and contract notes.
    """
    security_symbol = serializers.CharField(source='security.symbol', read_only=True)
    security_name = serializers.CharField(source='security.company_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    order_id = serializers.UUIDField(source='order.id', read_only=True)

    class Meta:
        model = TradeExecution
        fields = [
            'id',
            'order_id',
            'security',
            'security_symbol',
            'security_name',
            'user',
            'username',
            'quantity',
            'execution_price',
            'brokerage_fee',
            'net_amount',
            'executed_at',
        ]
        read_only_fields = fields


class TradeOrderSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for customer orders with execution details and calculated value.
    """
    security_symbol = serializers.CharField(source='security.symbol', read_only=True)
    security_name = serializers.CharField(source='security.company_name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    account_number = serializers.CharField(source='account.account_number', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    transaction_type_display = serializers.CharField(
        source='get_transaction_type_display',
        read_only=True
    )
    order_status_display = serializers.CharField(source='get_order_status_display', read_only=True)
    estimated_value = serializers.DecimalField(
        max_digits=18,
        decimal_places=4,
        read_only=True
    )
    executions = TradeExecutionSerializer(many=True, read_only=True)

    class Meta:
        model = TradeOrder
        fields = [
            'id',
            'user',
            'username',
            'account',
            'account_number',
            'security',
            'security_symbol',
            'security_name',
            'order_type',
            'order_type_display',
            'transaction_type',
            'transaction_type_display',
            'quantity',
            'filled_quantity',
            'limit_price',
            'executed_price',
            'order_status',
            'order_status_display',
            'rejection_reason',
            'estimated_value',
            'executions',
            'executed_at',
            'cancelled_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class TradeOrderCreateSerializer(serializers.Serializer):
    """
    Write serializer for placing a Buy or Sell equity order.
    Performs pre-trade validation against cash balance or portfolio holdings.
    """
    security_id = serializers.UUIDField(required=False)
    symbol = serializers.CharField(max_length=20, required=False)
    order_type = serializers.ChoiceField(choices=TradeOrder.ORDER_TYPE_CHOICES)
    transaction_type = serializers.ChoiceField(choices=TradeOrder.TX_CHOICES)
    quantity = serializers.IntegerField(min_value=1)
    limit_price = serializers.DecimalField(
        max_digits=18,
        decimal_places=4,
        required=False,
        allow_null=True
    )

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required to place trade orders.")

        user = request.user
        security_id = data.get('security_id')
        symbol = data.get('symbol')

        # 1. Resolve active security
        security = None
        if security_id:
            security = Security.objects.filter(id=security_id, is_active=True).first()
        elif symbol:
            security = Security.objects.filter(symbol__iexact=symbol.strip(), is_active=True).first()

        if not security:
            raise serializers.ValidationError({
                'security': "Active listed security could not be resolved from input."
            })
        data['resolved_security'] = security

        # 2. Resolve trading account
        account = TradingAccount.objects.filter(user=user).first()
        if not account:
            if user.role == 'CUSTOMER':
                account = TradingAccount.objects.create(
                    user=user,
                    account_number=f"PPRO-{user.id.hex[:6].upper()}"
                )
            else:
                raise serializers.ValidationError({
                    'account': "Trading account not found for current user."
                })

        if account.account_status != TradingAccount.STATUS_ACTIVE:
            raise serializers.ValidationError({
                'account': f"Trading account is {account.account_status}. Trading operations are suspended."
            })
        data['resolved_account'] = account

        order_type = data.get('order_type')
        tx_type = data.get('transaction_type')
        quantity = data.get('quantity')
        limit_price = data.get('limit_price')

        # 3. Limit Order validations
        if order_type == TradeOrder.TYPE_LIMIT:
            if not limit_price or limit_price <= Decimal('0.0000'):
                raise serializers.ValidationError({
                    'limit_price': "Limit price is mandatory and must be > 0 for Limit Orders."
                })
            exec_est_price = limit_price
        else:
            # MARKET order uses live CMP from MarketQuote
            if not hasattr(security, 'quote') or not security.quote:
                raise serializers.ValidationError({
                    'security': f"Live market price quote unavailable for {security.symbol}."
                })
            exec_est_price = security.quote.ltp
            if exec_est_price <= Decimal('0.0000'):
                raise serializers.ValidationError({
                    'security': f"Invalid market quote for {security.symbol} (LTP <= 0)."
                })

        data['estimated_price'] = exec_est_price
        trade_value = Decimal(quantity) * exec_est_price
        brokerage = trade_value * Decimal('0.0003')

        # 4. Pre-trade Cash balance check for BUY
        if tx_type == TradeOrder.TX_BUY:
            total_required = trade_value + brokerage
            if total_required > account.available_balance:
                raise serializers.ValidationError({
                    'balance': (
                        f"Insufficient funds to place BUY order. Required: ₹ {total_required:.2f} "
                        f"(Value: ₹ {trade_value:.2f} + Brokerage: ₹ {brokerage:.2f}), "
                        f"Available: ₹ {account.available_balance:.2f}."
                    )
                })

        # 5. Pre-trade Holdings check for SELL
        elif tx_type == TradeOrder.TX_SELL:
            holding = PortfolioHolding.objects.filter(
                portfolio__user=user,
                security=security
            ).first()

            available_held_qty = holding.quantity if holding else 0
            if available_held_qty < quantity:
                raise serializers.ValidationError({
                    'holdings': (
                        f"Insufficient equity holdings to place SELL order. "
                        f"You hold {available_held_qty} shares of {security.symbol}, requested {quantity}."
                    )
                })

        return data


class TradeOrderCancelSerializer(serializers.Serializer):
    """
    Serializer to validate order cancellation requests.
    """
    reason = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        default='Cancelled by user'
    )
