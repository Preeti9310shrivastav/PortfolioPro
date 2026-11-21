from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel

class RiskAssessment(TimeStampedModel):
    """
    Quantitative risk metrics evaluating portfolio volatility, beta, and value-at-risk.
    """
    CAT_CONSERVATIVE = 'CONSERVATIVE'
    CAT_MODERATE = 'MODERATE'
    CAT_AGGRESSIVE = 'AGGRESSIVE'
    CAT_HIGH_RISK = 'HIGH_RISK'

    CATEGORY_CHOICES = (
        (CAT_CONSERVATIVE, 'Conservative Risk Profile'),
        (CAT_MODERATE, 'Moderate Risk Profile'),
        (CAT_AGGRESSIVE, 'Aggressive Growth Profile'),
        (CAT_HIGH_RISK, 'High Risk / Speculative Exposure'),
    )

    portfolio = models.ForeignKey(
        'portfolio.Portfolio',
        on_delete=models.CASCADE,
        related_name='risk_assessments'
    )
    portfolio_beta = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal('1.0000')
    )
    sharpe_ratio = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    var_95_daily = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    concentration_index = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    risk_score = models.PositiveIntegerField(
        default=50,
        help_text="Risk score index from 1 (lowest) to 100 (highest risk)"
    )
    risk_category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CAT_MODERATE,
        db_index=True
    )
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'risk_assessments'
        ordering = ['-calculated_at']

    def __str__(self):
        return f"Risk Assessment for {self.portfolio.name}: Score {self.risk_score}/100 ({self.risk_category})"


class RiskThreshold(TimeStampedModel):
    """
    User-configurable risk limits triggering automated concentration warnings.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='risk_thresholds'
    )
    max_drawdown_limit = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal('20.0000')
    )
    max_single_stock_pct = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal('25.0000')
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'risk_thresholds'
        ordering = ['-created_at']

    def __str__(self):
        return f"Thresholds of {self.user.username} (Max Single Stock: {self.max_single_stock_pct}%)"
