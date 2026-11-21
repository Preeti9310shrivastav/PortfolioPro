"""
Admin configuration for PortfolioPro Accounts Module.
"""
from django.contrib import admin
from apps.accounts.models import TradingAccount, AccountTransaction, KYCRecord


@admin.register(TradingAccount)
class TradingAccountAdmin(admin.ModelAdmin):
    list_display = [
        'account_number',
        'user',
        'currency',
        'cash_balance',
        'margin_used',
        'available_balance_display',
        'account_status',
        'created_at',
    ]
    list_filter = ['account_status', 'currency', 'created_at']
    search_fields = ['account_number', 'user__username', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'available_balance_display']
    ordering = ['-created_at']

    @admin.display(description='Available Balance')
    def available_balance_display(self, obj):
        return f"₹ {obj.available_balance:.2f}"


@admin.register(AccountTransaction)
class AccountTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'account',
        'transaction_type',
        'amount',
        'balance_after',
        'status',
        'created_at',
    ]
    list_filter = ['transaction_type', 'status', 'created_at']
    search_fields = ['account__account_number', 'account__user__username', 'reference_note']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(KYCRecord)
class KYCRecordAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'pan_number',
        'aadhaar_masked',
        'bank_ifsc',
        'verification_status',
        'verified_by',
        'verified_at',
        'created_at',
    ]
    list_filter = ['verification_status', 'created_at']
    search_fields = ['user__username', 'user__email', 'pan_number', 'bank_account_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
