import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class TradeOrder(TimeStampedModel):
    """
    Equity order record submitted by a customer for market execution.
    """
    TYPE_MARKET = 'MARKET'
    TYPE_LIMIT = 'LIMIT'
    TYPE_STOP_LOSS = 'STOP_LOSS'
    ORDER_TYPE_CHOICES = (
        (TYPE_MARKET, 'Market Order (Execute at CMP)'),
        (TYPE_LIMIT, 'Limit Order (Execute at target price or better)'),
        (TYPE_STOP_LOSS, 'Stop-Loss Order'),
    )

    TX_BUY = 'BUY'
    TX_SELL = 'SELL'
    TX_CHOICES = (
        (TX_BUY, 'Buy Equity'),
        (TX_SELL, 'Sell Equity'),
    )

    STATUS_PENDING = 'PENDING'
    STATUS_FILLED = 'FILLED'
    STATUS_PARTIALLY_FILLED = 'PARTIALLY_FILLED'
    STATUS_CANCELLED = 'CANCELLED'
    STATUS_REJECTED = 'REJECTED'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending / In Queue'),
        (STATUS_FILLED, 'Completely Filled'),
        (STATUS_PARTIALLY_FILLED, 'Partially Filled'),
        (STATUS_CANCELLED, 'Cancelled by User'),
        (STATUS_REJECTED, 'Rejected by Risk / Balance Check'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    account = models.ForeignKey('accounts.TradingAccount', on_delete=models.CASCADE, related_name='orders')
    security = models.ForeignKey('market.Security', on_delete=models.CASCADE, related_name='orders')
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES, db_index=True)
    transaction_type = models.CharField(max_length=10, choices=TX_CHOICES, db_index=True)
    quantity = models.PositiveIntegerField()
    filled_quantity = models.PositiveIntegerField(default=0)
    limit_price = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    executed_price = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING, db_index=True)
    rejection_reason = models.TextField(blank=True, default='')
    executed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'trade_orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} {self.quantity}x {self.security.symbol} @ {self.order_type} ({self.order_status})"

    @property
    def estimated_value(self):
        price = self.limit_price or (self.security.quote.ltp if hasattr(self.security, 'quote') else Decimal('0.0000'))
        return self.quantity * price


class TradeExecution(models.Model):
    """
    Immutable contract note record generated upon order execution.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(TradeOrder, on_delete=models.CASCADE, related_name='executions')
    security = models.ForeignKey('market.Security', on_delete=models.CASCADE, related_name='executions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='executions')
    quantity = models.PositiveIntegerField()
    execution_price = models.DecimalField(max_digits=18, decimal_places=4)
    brokerage_fee = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal('0.0000'))
    net_amount = models.DecimalField(max_digits=18, decimal_places=4)
    executed_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'trade_executions'
        ordering = ['-executed_at']

    def __str__(self):
        return f"Execution of {self.quantity}x {self.security.symbol} @ ₹ {self.execution_price:.2f}"
