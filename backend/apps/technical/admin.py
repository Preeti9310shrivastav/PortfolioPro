"""
Django Admin registration for Technical Analysis Models.
"""
from django.contrib import admin
from apps.technical.models import TechnicalIndicator, UserChartPreference


@admin.register(TechnicalIndicator)
class TechnicalIndicatorAdmin(admin.ModelAdmin):
    list_display = (
        'security',
        'calculation_date',
        'overall_signal',
        'rsi_14',
        'macd_line',
        'sma_20',
        'sma_50',
        'sma_200',
    )
    list_filter = ('overall_signal', 'calculation_date')
    search_fields = ('security__symbol', 'security__company_name')


@admin.register(UserChartPreference)
class UserChartPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'chart_type', 'timeframe', 'created_at', 'updated_at')
    list_filter = ('chart_type', 'timeframe')
    search_fields = ('user__username', 'user__email')
