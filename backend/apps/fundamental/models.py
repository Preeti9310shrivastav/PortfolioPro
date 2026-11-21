import uuid
from decimal import Decimal
from django.db import models
from apps.common.models import TimeStampedModel

class FundamentalMetric(TimeStampedModel):
    """
    Corporate valuation ratios, dividend yields, and financial health scores.
    """
    security = models.OneToOneField(
        'market.Security',
        on_delete=models.CASCADE,
        related_name='fundamental_metric'
    )
    market_cap = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        help_text="Market capitalization in INR"
    )
    pe_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000'),
        db_index=True
    )
    pb_ratio = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    eps = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    dividend_yield = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    debt_to_equity = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    roe = models.DecimalField(
        max_digits=8,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    book_value = models.DecimalField(
        max_digits=18,
        decimal_places=4,
        default=Decimal('0.0000')
    )
    health_score = models.PositiveIntegerField(
        default=5,
        db_index=True,
        help_text="Solvency and profitability score from 1 (weak) to 10 (exceptionally strong)"
    )
    financial_year = models.CharField(max_length=10, default='2024-25')

    class Meta:
        db_table = 'fundamental_metrics'
        ordering = ['-market_cap']

    def __str__(self):
        return f"{self.security.symbol} Fundamentals: P/E {self.pe_ratio:.1f}, Score {self.health_score}/10"


class CompanyFinancial(models.Model):
    """
    Historical financial statement entries (revenue, profit, EBITDA) for an equity.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    security = models.ForeignKey(
        'market.Security',
        on_delete=models.CASCADE,
        related_name='financials'
    )
    period_name = models.CharField(max_length=20, help_text="e.g. FY 2023-24 or Q2 FY25")
    revenue = models.DecimalField(max_digits=20, decimal_places=4, default=Decimal('0.0000'))
    net_profit = models.DecimalField(max_digits=20, decimal_places=4, default=Decimal('0.0000'))
    operating_margin = models.DecimalField(max_digits=8, decimal_places=4, default=Decimal('0.0000'))
    ebitda = models.DecimalField(max_digits=20, decimal_places=4, default=Decimal('0.0000'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'company_financials'
        ordering = ['-period_name']
        constraints = [
            models.UniqueConstraint(fields=['security', 'period_name'], name='uq_company_financial_period')
        ]

    def __str__(self):
        return f"{self.security.symbol} [{self.period_name}] Rev: ₹ {self.revenue:.2f} Net: ₹ {self.net_profit:.2f}"
