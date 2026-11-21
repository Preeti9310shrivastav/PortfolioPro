"""
Serializers for Technical Indicators, Moving Averages, and User Chart Preferences.
"""
from rest_framework import serializers

from apps.technical.models import TechnicalIndicator, UserChartPreference
from apps.market.models import Security


class TechnicalIndicatorSerializer(serializers.ModelSerializer):
    """
    Serializer for quantitative technical indicators (RSI, MACD, SMAs, EMAs).
    """
    security_symbol = serializers.ReadOnlyField(source='security.symbol')
    company_name = serializers.ReadOnlyField(source='security.company_name')

    class Meta:
        model = TechnicalIndicator
        fields = [
            'id',
            'security',
            'security_symbol',
            'company_name',
            'calculation_date',
            'rsi_14',
            'macd_line',
            'macd_signal',
            'macd_hist',
            'sma_20',
            'sma_50',
            'sma_200',
            'ema_20',
            'overall_signal',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'security_symbol', 'company_name', 'created_at', 'updated_at']


class TechnicalAnalysisSerializer(serializers.Serializer):
    """
    Consolidated technical analysis snapshot with signal breakdown.
    """
    security_id = serializers.CharField()
    symbol = serializers.CharField()
    company_name = serializers.CharField()
    latest_indicator = TechnicalIndicatorSerializer(allow_null=True)
    summary = serializers.DictField()


class UserChartPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for user-customized charting workspace layouts and default overlays.
    """
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UserChartPreference
        fields = [
            'id',
            'user',
            'chart_type',
            'timeframe',
            'default_indicators',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_timeframe(self, value):
        allowed_timeframes = ['1m', '5m', '15m', '1H', '1D', '1W', '1M']
        if value not in allowed_timeframes:
            # If not in short list, allow reasonable string or validate
            pass
        return value

    def validate_default_indicators(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("default_indicators must be a JSON dictionary of boolean flags.")
        return value
