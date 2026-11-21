"""
Serializers for Portfolio Management and Valuation Snapshots.
"""
from decimal import Decimal
from rest_framework import serializers

from apps.portfolio.models import Portfolio, PortfolioHolding, PortfolioSnapshot
from apps.market.models import Security


class PortfolioSecurityQuoteSerializer(serializers.ModelSerializer):
    """
    Minimal equity quote summary for holdings display.
    """
    ltp = serializers.SerializerMethodField()

    class Meta:
        model = Security
        fields = ['id', 'symbol', 'company_name', 'exchange', 'ltp']

    def get_ltp(self, obj):
        if hasattr(obj, 'quote') and obj.quote:
            return obj.quote.ltp
        return Decimal('0.0000')


class PortfolioHoldingSerializer(serializers.ModelSerializer):
    """
    Consolidated position serializer with real-time valuation and P&L metrics.
    """
    security = PortfolioSecurityQuoteSerializer(read_only=True)
    security_id = serializers.PrimaryKeyRelatedField(
        queryset=Security.objects.all(),
        source='security',
        write_only=True
    )
    current_value = serializers.DecimalField(
        max_digits=18,
        decimal_places=4,
        read_only=True
    )
    unrealized_pnl = serializers.DecimalField(
        max_digits=18,
        decimal_places=4,
        read_only=True
    )
    return_percent = serializers.DecimalField(
        max_digits=8,
        decimal_places=4,
        read_only=True
    )

    class Meta:
        model = PortfolioHolding
        fields = [
            'id',
            'portfolio',
            'security',
            'security_id',
            'quantity',
            'average_buy_price',
            'total_invested',
            'current_value',
            'unrealized_pnl',
            'return_percent',
            'realized_pnl',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'current_value',
            'unrealized_pnl',
            'return_percent',
            'created_at',
            'updated_at',
        ]

    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative.")
        return value

    def validate_average_buy_price(self, value):
        if value < Decimal('0.0000'):
            raise serializers.ValidationError("Average buy price cannot be negative.")
        return value


class PortfolioSerializer(serializers.ModelSerializer):
    """
    Portfolio container serializer including owner and holding count.
    """
    user = serializers.ReadOnlyField(source='user.username')
    holdings_count = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = [
            'id',
            'user',
            'name',
            'is_default',
            'holdings_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'holdings_count', 'created_at', 'updated_at']

    def get_holdings_count(self, obj):
        return obj.holdings.count()

    def validate_name(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Portfolio name cannot be blank.")
        return stripped


class PortfolioSnapshotSerializer(serializers.ModelSerializer):
    """
    Daily valuation snapshot serializer for portfolio performance tracking.
    """
    class Meta:
        model = PortfolioSnapshot
        fields = [
            'id',
            'portfolio',
            'snapshot_date',
            'total_equity_value',
            'total_cash_value',
            'total_portfolio_value',
            'day_pnl',
            'day_pnl_percent',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class PortfolioSummarySerializer(serializers.Serializer):
    """
    Aggregated P&L and net worth valuation summary serializer.
    """
    total_invested = serializers.DecimalField(max_digits=18, decimal_places=4)
    current_value = serializers.DecimalField(max_digits=18, decimal_places=4)
    total_unrealized_pnl = serializers.DecimalField(max_digits=18, decimal_places=4)
    total_realized_pnl = serializers.DecimalField(max_digits=18, decimal_places=4)
    day_change = serializers.DecimalField(max_digits=18, decimal_places=4)
    holdings_count = serializers.IntegerField()
