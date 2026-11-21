"""
Serializers for Fundamental Valuation Ratios, Financial Statements, and Peer Comparisons.
"""
from rest_framework import serializers

from apps.fundamental.models import FundamentalMetric, CompanyFinancial
from apps.market.models import Security


class FundamentalMetricSerializer(serializers.ModelSerializer):
    """
    Serializer for key corporate valuation multiples, solvency, and health scores.
    """
    symbol = serializers.ReadOnlyField(source='security.symbol')
    company_name = serializers.ReadOnlyField(source='security.company_name')
    sector = serializers.ReadOnlyField(source='security.sector')

    class Meta:
        model = FundamentalMetric
        fields = [
            'id',
            'security',
            'symbol',
            'company_name',
            'sector',
            'market_cap',
            'pe_ratio',
            'pb_ratio',
            'eps',
            'dividend_yield',
            'debt_to_equity',
            'roe',
            'book_value',
            'health_score',
            'financial_year',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'symbol',
            'company_name',
            'sector',
            'created_at',
            'updated_at',
        ]


class CompanyFinancialSerializer(serializers.ModelSerializer):
    """
    Serializer for historical quarterly or annual financial statements.
    """
    symbol = serializers.ReadOnlyField(source='security.symbol')

    class Meta:
        model = CompanyFinancial
        fields = [
            'id',
            'security',
            'symbol',
            'period_name',
            'revenue',
            'net_profit',
            'operating_margin',
            'ebitda',
            'created_at',
        ]
        read_only_fields = ['id', 'symbol', 'created_at']


class FundamentalAnalysisSerializer(serializers.Serializer):
    """
    Composite analysis aggregating fundamental ratios with chronological financial reports.
    """
    security_id = serializers.CharField()
    symbol = serializers.CharField()
    company_name = serializers.CharField()
    sector = serializers.CharField()
    metric = FundamentalMetricSerializer(allow_null=True)
    financials = CompanyFinancialSerializer(many=True)


class PeerComparisonItemSerializer(serializers.Serializer):
    """
    Comparative metric item for peer evaluation within the same market sector.
    """
    security_id = serializers.CharField()
    symbol = serializers.CharField()
    company_name = serializers.CharField()
    sector = serializers.CharField()
    ltp = serializers.DecimalField(max_digits=18, decimal_places=4)
    market_cap = serializers.DecimalField(max_digits=20, decimal_places=4, allow_null=True)
    pe_ratio = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True)
    pb_ratio = serializers.DecimalField(max_digits=10, decimal_places=4, allow_null=True)
    roe = serializers.DecimalField(max_digits=8, decimal_places=4, allow_null=True)
    dividend_yield = serializers.DecimalField(max_digits=8, decimal_places=4, allow_null=True)
    health_score = serializers.IntegerField(allow_null=True)
