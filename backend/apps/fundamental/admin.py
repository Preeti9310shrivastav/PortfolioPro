"""
Django Admin registration for Fundamental Metrics & Financials.
"""
from django.contrib import admin
from apps.fundamental.models import FundamentalMetric, CompanyFinancial


@admin.register(FundamentalMetric)
class FundamentalMetricAdmin(admin.ModelAdmin):
    list_display = (
        'security',
        'financial_year',
        'market_cap',
        'pe_ratio',
        'pb_ratio',
        'eps',
        'roe',
        'health_score',
    )
    list_filter = ('financial_year', 'health_score')
    search_fields = ('security__symbol', 'security__company_name')


@admin.register(CompanyFinancial)
class CompanyFinancialAdmin(admin.ModelAdmin):
    list_display = (
        'security',
        'period_name',
        'revenue',
        'net_profit',
        'operating_margin',
        'ebitda',
        'created_at',
    )
    list_filter = ('period_name',)
    search_fields = ('security__symbol', 'security__company_name')
