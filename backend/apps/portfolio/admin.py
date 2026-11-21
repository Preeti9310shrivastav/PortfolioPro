"""
Django Admin registration for Portfolio Models.
"""
from django.contrib import admin
from apps.portfolio.models import Portfolio, PortfolioHolding, PortfolioSnapshot


class PortfolioHoldingInline(admin.TabularInline):
    model = PortfolioHolding
    extra = 0
    fields = ('security', 'quantity', 'average_buy_price', 'total_invested', 'realized_pnl')
    readonly_fields = ('total_invested',)


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'is_default', 'created_at', 'updated_at')
    list_filter = ('is_default', 'created_at')
    search_fields = ('name', 'user__username', 'user__email')
    inlines = [PortfolioHoldingInline]


@admin.register(PortfolioHolding)
class PortfolioHoldingAdmin(admin.ModelAdmin):
    list_display = (
        'portfolio',
        'security',
        'quantity',
        'average_buy_price',
        'total_invested',
        'realized_pnl',
        'updated_at',
    )
    list_filter = ('portfolio__user', 'created_at')
    search_fields = ('portfolio__name', 'security__symbol', 'security__company_name')


@admin.register(PortfolioSnapshot)
class PortfolioSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        'portfolio',
        'snapshot_date',
        'total_portfolio_value',
        'day_pnl',
        'day_pnl_percent',
        'created_at',
    )
    list_filter = ('snapshot_date',)
    search_fields = ('portfolio__name', 'portfolio__user__username')
