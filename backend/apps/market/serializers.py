"""
Serializers for PortfolioPro Market Module.
Covers Security master, MarketQuote, HistoricalPrice, Watchlist, and Watchlist items.
"""
from rest_framework import serializers

from apps.market.models import (
    Security,
    MarketQuote,
    HistoricalPrice,
    Watchlist,
    WatchlistItem,
)


class MarketQuoteSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for live price quote and day metrics.
    """
    symbol = serializers.CharField(source='security.symbol', read_only=True)

    class Meta:
        model = MarketQuote
        fields = [
            'id',
            'symbol',
            'ltp',
            'open_price',
            'high_price',
            'low_price',
            'close_price',
            'volume',
            'change_amount',
            'change_percent',
            'week_52_high',
            'week_52_low',
            'updated_at',
        ]
        read_only_fields = fields


class SecuritySerializer(serializers.ModelSerializer):
    """
    Read-only serializer for equity security master.
    """
    exchange_display = serializers.CharField(source='get_exchange_display', read_only=True)

    class Meta:
        model = Security
        fields = [
            'id',
            'symbol',
            'company_name',
            'exchange',
            'exchange_display',
            'sector',
            'industry',
            'lot_size',
            'isin_code',
            'is_active',
        ]
        read_only_fields = fields


class SecurityWithQuoteSerializer(serializers.ModelSerializer):
    """
    Composite serializer embedding live market quote with equity security master.
    """
    quote = MarketQuoteSerializer(read_only=True)
    exchange_display = serializers.CharField(source='get_exchange_display', read_only=True)

    class Meta:
        model = Security
        fields = [
            'id',
            'symbol',
            'company_name',
            'exchange',
            'exchange_display',
            'sector',
            'industry',
            'lot_size',
            'isin_code',
            'is_active',
            'quote',
        ]
        read_only_fields = fields


class HistoricalPriceSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for daily OHLCV historical time-series data.
    """
    symbol = serializers.CharField(source='security.symbol', read_only=True)

    class Meta:
        model = HistoricalPrice
        fields = [
            'id',
            'symbol',
            'trade_date',
            'open',
            'high',
            'low',
            'close',
            'volume',
        ]
        read_only_fields = fields


class WatchlistItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual equity ticker pinned inside a watchlist.
    """
    security = SecurityWithQuoteSerializer(read_only=True)

    class Meta:
        model = WatchlistItem
        fields = [
            'id',
            'watchlist',
            'security',
            'display_order',
            'created_at',
        ]
        read_only_fields = fields


class WatchlistSerializer(serializers.ModelSerializer):
    """
    Read serializer for user watchlist with nested items and live quotes.
    """
    items_count = serializers.IntegerField(source='items.count', read_only=True)
    items = WatchlistItemSerializer(many=True, read_only=True)

    class Meta:
        model = Watchlist
        fields = [
            'id',
            'name',
            'is_default',
            'items_count',
            'items',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'items_count', 'items', 'created_at', 'updated_at']


class WatchlistCreateSerializer(serializers.ModelSerializer):
    """
    Write serializer for creating or renaming a custom watchlist.
    """
    class Meta:
        model = Watchlist
        fields = ['id', 'name', 'is_default']
        read_only_fields = ['id']

    def validate_name(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError("Watchlist name cannot be empty.")
        if len(cleaned) > 100:
            raise serializers.ValidationError("Watchlist name cannot exceed 100 characters.")
        return cleaned


class WatchlistAddSecuritySerializer(serializers.Serializer):
    """
    Write serializer for adding an active stock ticker to a user watchlist.
    Accepts either security_id or symbol string.
    """
    security_id = serializers.UUIDField(required=False)
    symbol = serializers.CharField(max_length=20, required=False)

    def validate(self, data):
        security_id = data.get('security_id')
        symbol = data.get('symbol')

        if not security_id and not symbol:
            raise serializers.ValidationError("Either security_id or symbol must be provided.")

        if security_id:
            security = Security.objects.filter(id=security_id, is_active=True).first()
        else:
            security = Security.objects.filter(symbol__iexact=symbol.strip(), is_active=True).first()

        if not security:
            raise serializers.ValidationError("Active security matching the input could not be found.")

        data['security'] = security
        return data
