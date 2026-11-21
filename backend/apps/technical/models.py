from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class TechnicalIndicator(TimeStampedModel):
    """
    Calculated momentum, trend, and moving average indicators for an equity security.
    """
    SIGNAL_STRONG_BUY = 'STRONG_BUY'
    SIGNAL_BUY = 'BUY'
    SIGNAL_NEUTRAL = 'NEUTRAL'
    SIGNAL_SELL = 'SELL'
    SIGNAL_STRONG_SELL = 'STRONG_SELL'

    SIGNAL_CHOICES = (
        (SIGNAL_STRONG_BUY, 'Strong Buy'),
        (SIGNAL_BUY, 'Buy / Bullish'),
        (SIGNAL_NEUTRAL, 'Neutral / Consolidation'),
        (SIGNAL_SELL, 'Sell / Bearish'),
        (SIGNAL_STRONG_SELL, 'Strong Sell'),
    )

    security = models.ForeignKey(
        'market.Security',
        on_delete=models.CASCADE,
        related_name='technical_indicators'
    )
    calculation_date = models.DateField(db_index=True)
    rsi_14 = models.DecimalField(max_digits=8, decimal_places=4)
    macd_line = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    macd_signal = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    macd_hist = models.DecimalField(max_digits=12, decimal_places=4, default=Decimal('0.0000'))
    sma_20 = models.DecimalField(max_digits=18, decimal_places=4)
    sma_50 = models.DecimalField(max_digits=18, decimal_places=4)
    sma_200 = models.DecimalField(max_digits=18, decimal_places=4)
    ema_20 = models.DecimalField(max_digits=18, decimal_places=4)
    overall_signal = models.CharField(
        max_length=20,
        choices=SIGNAL_CHOICES,
        default=SIGNAL_NEUTRAL,
        db_index=True
    )

    class Meta:
        db_table = 'technical_indicators'
        ordering = ['-calculation_date']
        constraints = [
            models.UniqueConstraint(fields=['security', 'calculation_date'], name='uq_technical_security_date')
        ]

    def __str__(self):
        return f"{self.security.symbol} [{self.calculation_date}] RSI: {self.rsi_14:.1f} Signal: {self.overall_signal}"


class UserChartPreference(TimeStampedModel):
    """
    User-saved candlestick indicator parameters and chart overlay settings.
    """
    CHART_CANDLESTICK = 'CANDLESTICK'
    CHART_LINE = 'LINE'
    CHART_AREA = 'AREA'

    CHART_CHOICES = (
        (CHART_CANDLESTICK, 'Japanese Candlestick'),
        (CHART_LINE, 'Line Chart'),
        (CHART_AREA, 'Mountain / Area Chart'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chart_preferences'
    )
    chart_type = models.CharField(
        max_length=20,
        choices=CHART_CHOICES,
        default=CHART_CANDLESTICK
    )
    timeframe = models.CharField(max_length=10, default='1D')
    default_indicators = models.JSONField(
        default=dict,
        help_text="Key-value flags for active chart indicators e.g. {'sma_20': true, 'rsi': true}"
    )

    class Meta:
        db_table = 'user_chart_preferences'
        ordering = ['-created_at']

    def __str__(self):
        return f"Chart Preferences for {self.user.username} ({self.chart_type})"
