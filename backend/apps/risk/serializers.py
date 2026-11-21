"""
Serializers for Risk Management, Assessment, and Threshold Monitoring.
"""
from decimal import Decimal
from rest_framework import serializers

from apps.risk.models import RiskAssessment, RiskThreshold
from apps.portfolio.models import Portfolio


class RiskAssessmentSerializer(serializers.ModelSerializer):
    """
    Serializer for quantitative portfolio risk assessment metrics.
    """
    portfolio_name = serializers.ReadOnlyField(source='portfolio.name')
    portfolio_id = serializers.PrimaryKeyRelatedField(
        queryset=Portfolio.objects.all(),
        source='portfolio',
        write_only=True,
        required=False
    )

    class Meta:
        model = RiskAssessment
        fields = [
            'id',
            'portfolio',
            'portfolio_id',
            'portfolio_name',
            'portfolio_beta',
            'sharpe_ratio',
            'var_95_daily',
            'concentration_index',
            'risk_score',
            'risk_category',
            'calculated_at',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'portfolio_name',
            'calculated_at',
            'created_at',
            'updated_at',
        ]


class RiskThresholdSerializer(serializers.ModelSerializer):
    """
    Serializer for user-configured portfolio risk boundaries.
    """
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = RiskThreshold
        fields = [
            'id',
            'user',
            'max_drawdown_limit',
            'max_single_stock_pct',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def validate_max_drawdown_limit(self, value):
        if value <= Decimal('0.0000') or value > Decimal('100.0000'):
            raise serializers.ValidationError("Max drawdown limit must be between 0% and 100%.")
        return value

    def validate_max_single_stock_pct(self, value):
        if value <= Decimal('0.0000') or value > Decimal('100.0000'):
            raise serializers.ValidationError("Max single stock percentage must be between 0% and 100%.")
        return value


class ConcentratedHoldingItemSerializer(serializers.Serializer):
    """
    Item serializer for individual holding exposure inside the risk dashboard.
    """
    symbol = serializers.CharField()
    company_name = serializers.CharField()
    quantity = serializers.IntegerField()
    current_value = serializers.DecimalField(max_digits=18, decimal_places=4)
    weight_percent = serializers.DecimalField(max_digits=8, decimal_places=4)
    is_breaching_threshold = serializers.BooleanField(default=False)


class RiskDashboardSerializer(serializers.Serializer):
    """
    Composite serializer aggregating latest assessment, active thresholds, and concentration.
    """
    portfolio_id = serializers.CharField()
    portfolio_name = serializers.CharField()
    latest_assessment = RiskAssessmentSerializer(allow_null=True)
    thresholds = RiskThresholdSerializer(allow_null=True)
    top_holdings = ConcentratedHoldingItemSerializer(many=True)
    total_portfolio_value = serializers.DecimalField(max_digits=18, decimal_places=4)
    is_concentration_breached = serializers.BooleanField()
