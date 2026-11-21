import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class Portfolio(TimeStampedModel):
    """
    Portfolio container grouping customer equity holdings and valuation snapshots.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100, default='Primary Portfolio')
    is_default = models.BooleanField(default=True)

    class Meta:
        db_table = 'portfolios'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='uq_portfolio_user_name')
        ]

    def __str__(self):
        return f"{self.user.username}'s Portfolio: {self.name}"


class PortfolioHolding(TimeStampedModel):
    """
    Consolidated equity holding position with weighted average buy price and P&L.
    """
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='holdings')
    security = models.ForeignKey('market.Security', on_delete=models.CASCADE, related_name='held_in_portfolios')
    quantity = models.PositiveIntegerField(default=0)
    average_buy_price = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal('0.0000'))
    total_invested = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal('0.0000'))
    realized_pnl = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal('0.0000'))

    class Meta:
        db_table = 'portfolio_holdings'
        ordering = ['security__symbol']
        constraints = [
            models.UniqueConstraint(fields=['portfolio', 'security'], name='uq_portfolio_security')
        ]

    def __str__(self):
        return f"{self.quantity}x {self.security.symbol} @ Avg ₹ {self.average_buy_price:.2f}"

    @property
    def current_value(self):
        ltp = self.security.quote.ltp if hasattr(self.security, 'quote') else self.average_buy_price
        return self.quantity * ltp

    @property
    def unrealized_pnl(self):
        return self.current_value - self.total_invested

    @property
    def return_percent(self):
        if self.total_invested > 0:
            return (self.unrealized_pnl / self.total_invested) * 100
        return Decimal('0.0000')


class PortfolioSnapshot(models.Model):
    """
    Daily snapshot record of overall portfolio valuation for equity curve charting.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='snapshots')
    snapshot_date = models.DateField(db_index=True)
    total_equity_value = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal('0.0000'))
    total_cash_value = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal('0.0000'))
    total_portfolio_value = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal('0.0000'))
    day_pnl = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal('0.0000'))
    day_pnl_percent = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal('0.0000'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'portfolio_snapshots'
        ordering = ['-snapshot_date']
        constraints = [
            models.UniqueConstraint(fields=['portfolio', 'snapshot_date'], name='uq_portfolio_snapshot_date')
        ]

    def __str__(self):
        return f"{self.portfolio.name} [{self.snapshot_date}] Value: ₹ {self.total_portfolio_value:.2f}"
