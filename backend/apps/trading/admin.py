"""
Admin configuration for PortfolioPro Trading Module.
"""
from django.contrib import admin
from apps.trading.models import TradeOrder, TradeExecution


class TradeExecutionInline(admin.TabularInline):
    model = TradeExecution
    extra = 0
    readonly_fields = [
        'id',
        'security',
        'user',
        'quantity',
        'execution_price',
        'brokerage_fee',
        'net_amount',
        'executed_at',
    ]
    can_delete = False


@admin.register(TradeOrder)
class TradeOrderAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'security',
        'order_type',
        'transaction_type',
        'quantity',
        'filled_quantity',
        'limit_price',
        'executed_price',
        'order_status',
        'executed_at',
        'created_at',
    ]
    list_filter = ['order_status', 'order_type', 'transaction_type', 'created_at']
    search_fields = [
        'id',
        'user__username',
        'security__symbol',
        'account__account_number',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'executed_at',
        'cancelled_at',
        'estimated_value_display',
    ]
    inlines = [TradeExecutionInline]
    ordering = ['-created_at']

    @admin.display(description='Estimated Value')
    def estimated_value_display(self, obj):
        return f"₹ {obj.estimated_value:.2f}"


@admin.register(TradeExecution)
class TradeExecutionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order',
        'security',
        'user',
        'quantity',
        'execution_price',
        'brokerage_fee',
        'net_amount',
        'executed_at',
    ]
    list_filter = ['executed_at']
    search_fields = ['security__symbol', 'user__username', 'order__id']
    readonly_fields = ['id', 'executed_at']
    ordering = ['-executed_at']
