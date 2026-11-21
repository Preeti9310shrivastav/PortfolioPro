"""
Django Admin registration for Risk Management Models.
"""
from django.contrib import admin
from apps.risk.models import RiskAssessment, RiskThreshold


@admin.register(RiskAssessment)
class RiskAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        'portfolio',
        'risk_category',
        'risk_score',
        'portfolio_beta',
        'sharpe_ratio',
        'var_95_daily',
        'concentration_index',
        'calculated_at',
    )
    list_filter = ('risk_category', 'calculated_at')
    search_fields = ('portfolio__name', 'portfolio__user__username')
    readonly_fields = ('calculated_at',)


@admin.register(RiskThreshold)
class RiskThresholdAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'max_drawdown_limit',
        'max_single_stock_pct',
        'is_active',
        'created_at',
        'updated_at',
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__username', 'user__email')
