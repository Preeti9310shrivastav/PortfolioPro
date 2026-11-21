from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class TradingAccount(TimeStampedModel):
    """
    Virtual trading account tracking cash balance, margin, and account state.
    """
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_FROZEN = 'FROZEN'
    STATUS_SUSPENDED = 'SUSPENDED'
    STATUS_CLOSED = 'CLOSED'

    STATUS_CHOICES = (
        (STATUS_ACTIVE, 'Active'),
        (STATUS_FROZEN, 'Frozen'),
        (STATUS_SUSPENDED, 'Suspended'),
        (STATUS_CLOSED, 'Closed'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trading_account'
    )
    account_number = models.CharField(max_length=32, unique=True, db_index=True)
    currency = models.CharField(max_length=3, default='INR')
    cash_balance = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('500000.0000')
    )
    margin_used = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    account_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        db_index=True
    )

    class Meta:
        db_table = 'trading_accounts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.account_number} ({self.user.username}) - Balance: ₹ {self.cash_balance:.2f}"

    @property
    def available_balance(self):
        return self.cash_balance - self.margin_used


class AccountTransaction(TimeStampedModel):
    """
    Immutable ledger record of fund deposits, withdrawals, and trade debits/credits.
    """
    TYPE_DEPOSIT = 'DEPOSIT'
    TYPE_WITHDRAWAL = 'WITHDRAWAL'
    TYPE_TRADE_DEBIT = 'TRADE_DEBIT'
    TYPE_TRADE_CREDIT = 'TRADE_CREDIT'
    TYPE_FEE_DEBIT = 'FEE_DEBIT'

    TRANSACTION_TYPE_CHOICES = (
        (TYPE_DEPOSIT, 'Fund Deposit'),
        (TYPE_WITHDRAWAL, 'Fund Withdrawal'),
        (TYPE_TRADE_DEBIT, 'Trade Buy Debit'),
        (TYPE_TRADE_CREDIT, 'Trade Sell Credit'),
        (TYPE_FEE_DEBIT, 'Brokerage / Regulatory Fee'),
    )

    STATUS_PENDING = 'PENDING'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    account = models.ForeignKey(
        TradingAccount,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPE_CHOICES,
        db_index=True
    )
    amount = models.DecimalField(max_digits=18, decimal_places=4)
    balance_after = models.DecimalField(max_digits=18, decimal_places=4)
    reference_note = models.TextField(blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_COMPLETED,
        db_index=True
    )

    class Meta:
        db_table = 'account_transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} of ₹ {self.amount:.2f} ({self.status})"


class KYCRecord(TimeStampedModel):
    """
    Customer KYC compliance records (PAN, Aadhaar, Bank Details).
    """
    STATUS_PENDING = 'PENDING'
    STATUS_VERIFIED = 'VERIFIED'
    STATUS_REJECTED = 'REJECTED'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending Verification'),
        (STATUS_VERIFIED, 'Verified / Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='kyc_record'
    )
    pan_number = models.CharField(max_length=10)
    aadhaar_masked = models.CharField(max_length=12)
    bank_account_number = models.CharField(max_length=30)
    bank_ifsc = models.CharField(max_length=11)
    verification_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_kycs'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'kyc_records'
        ordering = ['-created_at']

    def __str__(self):
        return f"KYC for {self.user.username} ({self.verification_status})"
