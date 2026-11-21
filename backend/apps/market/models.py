import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class Security(TimeStampedModel):
    """
    Security master entity representing listed equities on NSE/BSE.
    """
    EXCHANGE_NSE = 'NSE'
    EXCHANGE_BSE = 'BSE'
    EXCHANGE_CHOICES = (
        (EXCHANGE_NSE, 'National Stock Exchange (NSE)'),
        (EXCHANGE_BSE, 'Bombay Stock Exchange (BSE)'),
    )

    symbol = models.CharField(max_length=20, unique=True, db_index=True)
    company_name = models.CharField(max_length=255)
    exchange = models.CharField(max_length=10, choices=EXCHANGE_CHOICES, default=EXCHANGE_NSE, db_index=True)
    sector = models.CharField(max_length=100, db_index=True)
    industry = models.CharField(max_length=100, blank=True, default='')
    lot_size = models.PositiveIntegerField(default=1)
    isin_code = models.CharField(max_length=12, unique=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'securities'
        ordering = ['symbol']

    def __str__(self):
        return f"{self.symbol} - {self.company_name} ({self.exchange})"


class MarketQuote(models.Model):
    """
    Live market price quote for an active equity security.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    security = models.OneToOneField(Security, on_delete=models.CASCADE, related_name='quote')
    ltp = models.DecimalField(max_digits=18, decimal_places=4, db_index=True)
    open_price = models.DecimalField(max_digits=18, decimal_places=4)
    high_price = models.DecimalField(max_digits=18, decimal_places=4)
    low_price = models.DecimalField(max_digits=18, decimal_places=4)
    close_price = models.DecimalField(max_digits=18, decimal_places=4)
    volume = models.BigIntegerField(default=0)
    change_amount = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal('0.0000'))
    change_percent = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal('0.0000'))
    week_52_high = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal('0.0000'))
    week_52_low = models.DecimalField(max_digits=18, decimal_places=4, default=Decimal('0.0000'))
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'market_quotes'
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.security.symbol} LTP: ₹ {self.ltp:.2f} ({self.change_percent:+.2f}%)"


class HistoricalPrice(models.Model):
    """
    Daily OHLCV historical time-series bar data for technical charts and analytics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    security = models.ForeignKey(Security, on_delete=models.CASCADE, related_name='historical_prices')
    trade_date = models.DateField(db_index=True)
    open = models.DecimalField(max_digits=18, decimal_places=4)
    high = models.DecimalField(max_digits=18, decimal_places=4)
    low = models.DecimalField(max_digits=18, decimal_places=4)
    close = models.DecimalField(max_digits=18, decimal_places=4)
    volume = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historical_prices'
        ordering = ['-trade_date']
        constraints = [
            models.UniqueConstraint(fields=['security', 'trade_date'], name='uq_historical_price_security_date')
        ]

    def __str__(self):
        return f"{self.security.symbol} [{self.trade_date}] Close: ₹ {self.close:.2f}"


class Watchlist(TimeStampedModel):
    """
    Custom user-created watchlist of tracked equity instruments.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlists')
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'watchlists'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(fields=['user', 'name'], name='uq_watchlist_user_name')
        ]

    def __str__(self):
        return f"{self.user.username}'s Watchlist: {self.name}"


class WatchlistItem(models.Model):
    """
    Specific equity ticker mapped inside a user watchlist.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    watchlist = models.ForeignKey(Watchlist, on_delete=models.CASCADE, related_name='items')
    security = models.ForeignKey(Security, on_delete=models.CASCADE, related_name='watchlist_entries')
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'watchlist_items'
        ordering = ['display_order', 'created_at']
        constraints = [
            models.UniqueConstraint(fields=['watchlist', 'security'], name='uq_watchlist_security')
        ]

    def __str__(self):
        return f"{self.security.symbol} in {self.watchlist.name}"
