"""
Admin configuration for PortfolioPro Market Module.
"""
from django.contrib import admin
from apps.market.models import (
    Security,
    MarketQuote,
    HistoricalPrice,
    Watchlist,
    WatchlistItem,
)


class MarketQuoteInline(admin.StackedInline):
    model = MarketQuote
    extra = 0
    readonly_fields = ['id', 'updated_at']


@admin.register(Security)
class SecurityAdmin(admin.ModelAdmin):
    list_display = [
        'symbol',
        'company_name',
        'exchange',
        'sector',
        'isin_code',
        'lot_size',
        'is_active',
        'created_at',
    ]
    list_filter = ['exchange', 'sector', 'is_active', 'created_at']
    search_fields = ['symbol', 'company_name', 'isin_code']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [MarketQuoteInline]
    ordering = ['symbol']


@admin.register(MarketQuote)
class MarketQuoteAdmin(admin.ModelAdmin):
    list_display = [
        'security',
        'ltp',
        'open_price',
        'high_price',
        'low_price',
        'close_price',
        'volume',
        'change_percent',
        'updated_at',
    ]
    search_fields = ['security__symbol', 'security__company_name']
    readonly_fields = ['id', 'updated_at']
    ordering = ['-updated_at']


@admin.register(HistoricalPrice)
class HistoricalPriceAdmin(admin.ModelAdmin):
    list_display = [
        'security',
        'trade_date',
        'open',
        'high',
        'low',
        'close',
        'volume',
        'created_at',
    ]
    list_filter = ['trade_date']
    search_fields = ['security__symbol']
    readonly_fields = ['id', 'created_at']
    ordering = ['-trade_date']


class WatchlistItemInline(admin.TabularInline):
    model = WatchlistItem
    extra = 1
    readonly_fields = ['id', 'created_at']


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_default', 'items_count_display', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'user__username', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    inlines = [WatchlistItemInline]
    ordering = ['name']

    @admin.display(description='Items')
    def items_count_display(self, obj):
        return obj.items.count()


@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ['watchlist', 'security', 'display_order', 'created_at']
    search_fields = ['watchlist__name', 'watchlist__user__username', 'security__symbol']
    readonly_fields = ['id', 'created_at']
    ordering = ['watchlist', 'display_order']
