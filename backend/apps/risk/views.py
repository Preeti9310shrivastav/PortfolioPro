"""
Views for Portfolio Risk Analytics, Thresholds, and Supervisory System Risk.
"""
from decimal import Decimal
from django.db import models
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.risk.models import RiskAssessment, RiskThreshold
from apps.risk.serializers import (
    RiskAssessmentSerializer,
    RiskThresholdSerializer,
    RiskDashboardSerializer,
)
from apps.portfolio.models import Portfolio, PortfolioHolding
from apps.common.responses import api_success, api_error
from apps.common.permissions import IsFinanceOfficer


class RiskViewSet(viewsets.ViewSet):
    """
    ViewSet providing risk dashboard, recalculation engine, and user threshold configurations.
    """
    permission_classes = [IsAuthenticated]

    def _get_user_portfolio(self, request):
        portfolio_id = request.query_params.get('portfolio_id') or request.data.get('portfolio_id')
        if portfolio_id:
            return Portfolio.objects.filter(user=request.user, id=portfolio_id).first()
        return (
            Portfolio.objects.filter(user=request.user, is_default=True).first()
            or Portfolio.objects.filter(user=request.user).first()
        )

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Return the complete risk posture: latest assessment, configured limits, and concentration.
        """
        portfolio = self._get_user_portfolio(request)
        if not portfolio:
            return api_success(
                data={
                    "portfolio_id": "",
                    "portfolio_name": "No Active Portfolio",
                    "latest_assessment": None,
                    "thresholds": None,
                    "top_holdings": [],
                    "total_portfolio_value": Decimal('0.0000'),
                    "is_concentration_breached": False,
                },
                message="No portfolio found for user."
            )

        latest_assessment = (
            RiskAssessment.objects.filter(portfolio=portfolio)
            .order_by('-calculated_at')
            .first()
        )

        threshold, _ = RiskThreshold.objects.get_or_create(
            user=request.user,
            defaults={
                'max_drawdown_limit': Decimal('20.0000'),
                'max_single_stock_pct': Decimal('25.0000'),
                'is_active': True,
            }
        )

        holdings = (
            PortfolioHolding.objects.filter(portfolio=portfolio)
            .select_related('security', 'security__quote')
        )

        total_value = sum((h.current_value for h in holdings), Decimal('0.0000'))
        top_holdings = []
        is_breached = False

        for h in sorted(holdings, key=lambda x: x.current_value, reverse=True):
            c_val = h.current_value
            weight_pct = (
                (c_val / total_value) * Decimal('100.0000')
                if total_value > Decimal('0.0000')
                else Decimal('0.0000')
            )
            breaching = threshold.is_active and (weight_pct > threshold.max_single_stock_pct)
            if breaching:
                is_breached = True

            top_holdings.append({
                "symbol": h.security.symbol,
                "company_name": h.security.company_name,
                "quantity": h.quantity,
                "current_value": c_val,
                "weight_percent": weight_pct,
                "is_breaching_threshold": breaching,
            })

        dashboard_data = {
            "portfolio_id": str(portfolio.id),
            "portfolio_name": portfolio.name,
            "latest_assessment": RiskAssessmentSerializer(latest_assessment).data if latest_assessment else None,
            "thresholds": RiskThresholdSerializer(threshold).data if threshold else None,
            "top_holdings": top_holdings[:10],
            "total_portfolio_value": total_value,
            "is_concentration_breached": is_breached,
        }

        return api_success(
            data=dashboard_data,
            message="Risk dashboard metrics loaded successfully."
        )

    @action(detail=False, methods=['post'])
    def recalculate(self, request):
        """
        Trigger fresh quantitative assessment calculation for the target portfolio.
        """
        portfolio = self._get_user_portfolio(request)
        if not portfolio:
            return api_error(
                message="No portfolio found to assess.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        holdings = list(
            PortfolioHolding.objects.filter(portfolio=portfolio)
            .select_related('security', 'security__quote')
        )

        total_value = sum((h.current_value for h in holdings), Decimal('0.0000'))

        if holdings and total_value > Decimal('0.0000'):
            weights = [(h.current_value / total_value) for h in holdings]
            concentration = max(weights)

            weighted_beta_acc = Decimal('0.0000')
            weighted_ret_acc = Decimal('0.0000')

            for h, w in zip(holdings, weights):
                # Deterministic pseudo-beta between 0.65 and 1.75 per security
                sec_hash = abs(hash(h.security.symbol)) % 110
                sec_beta = Decimal('0.6500') + (Decimal(sec_hash) / Decimal('100.0000'))
                weighted_beta_acc += sec_beta * w
                weighted_ret_acc += h.return_percent * w

            portfolio_beta = weighted_beta_acc
            annualized_return = weighted_ret_acc / Decimal('100.0000')

            # Sharpe Ratio using 6.5% risk-free rate and benchmark 15% volatility
            rf_rate = Decimal('0.0650')
            volatility = Decimal('0.1500')
            sharpe_ratio = (annualized_return - rf_rate) / volatility
            sharpe_ratio = max(Decimal('-3.0000'), min(Decimal('5.0000'), sharpe_ratio))

            # Daily 95% Value at Risk (2% daily standard assumption)
            var_95_daily = total_value * Decimal('0.0200')

            # Risk score calculation [1 - 100]
            beta_factor = (portfolio_beta / Decimal('1.8000')) * Decimal('50.0000')
            conc_factor = concentration * Decimal('50.0000')
            raw_score = int(beta_factor + conc_factor)
            risk_score = max(1, min(100, raw_score))
        else:
            portfolio_beta = Decimal('1.0000')
            sharpe_ratio = Decimal('0.0000')
            var_95_daily = Decimal('0.0000')
            concentration = Decimal('0.0000')
            risk_score = 50

        if risk_score < 30:
            category = RiskAssessment.CAT_CONSERVATIVE
        elif risk_score < 50:
            category = RiskAssessment.CAT_MODERATE
        elif risk_score < 75:
            category = RiskAssessment.CAT_AGGRESSIVE
        else:
            category = RiskAssessment.CAT_HIGH_RISK

        assessment = RiskAssessment.objects.create(
            portfolio=portfolio,
            portfolio_beta=portfolio_beta.quantize(Decimal('0.0001')),
            sharpe_ratio=sharpe_ratio.quantize(Decimal('0.0001')),
            var_95_daily=var_95_daily.quantize(Decimal('0.0001')),
            concentration_index=concentration.quantize(Decimal('0.0001')),
            risk_score=risk_score,
            risk_category=category,
        )

        serializer = RiskAssessmentSerializer(assessment)
        return api_success(
            data={"assessment": serializer.data},
            message="Risk assessment recalculated successfully.",
            status_code=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['get', 'post', 'put', 'patch'])
    def thresholds(self, request):
        """
        Manage user-configured risk thresholds.
        """
        threshold, _ = RiskThreshold.objects.get_or_create(
            user=request.user,
            defaults={
                'max_drawdown_limit': Decimal('20.0000'),
                'max_single_stock_pct': Decimal('25.0000'),
                'is_active': True,
            }
        )

        if request.method == 'GET':
            serializer = RiskThresholdSerializer(threshold)
            return api_success(
                data={"thresholds": serializer.data},
                message="Risk thresholds retrieved successfully."
            )

        serializer = RiskThresholdSerializer(
            threshold,
            data=request.data,
            partial=(request.method in ['PATCH', 'POST'])
        )
        if serializer.is_valid():
            saved_threshold = serializer.save()
            return api_success(
                data={"thresholds": RiskThresholdSerializer(saved_threshold).data},
                message="Risk thresholds updated successfully."
            )

        return api_error(
            message="Invalid threshold parameters.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )


class SystemRiskView(APIView):
    """
    Supervisory risk oversight view for Finance Officers and Compliance Officers.
    """
    permission_classes = [IsAuthenticated, IsFinanceOfficer]

    def get(self, request):
        assessments_qs = RiskAssessment.objects.all()
        total_count = assessments_qs.count()

        if total_count == 0:
            return api_success(
                data={
                    "total_portfolios_assessed": 0,
                    "category_distribution": {},
                    "average_beta": Decimal('1.0000'),
                    "average_sharpe": Decimal('0.0000'),
                    "high_risk_portfolios_count": 0,
                    "average_risk_score": 50,
                },
                message="No risk assessments recorded yet."
            )

        category_counts = {}
        for code, label in RiskAssessment.CATEGORY_CHOICES:
            category_counts[code] = assessments_qs.filter(risk_category=code).count()

        aggregates = assessments_qs.aggregate(
            avg_beta=models.Avg('portfolio_beta'),
            avg_sharpe=models.Avg('sharpe_ratio'),
            avg_score=models.Avg('risk_score'),
        )

        high_risk_count = category_counts.get(RiskAssessment.CAT_HIGH_RISK, 0)

        return api_success(
            data={
                "total_portfolios_assessed": total_count,
                "category_distribution": category_counts,
                "average_beta": (
                    aggregates['avg_beta'].quantize(Decimal('0.0001'))
                    if aggregates['avg_beta'] else Decimal('1.0000')
                ),
                "average_sharpe": (
                    aggregates['avg_sharpe'].quantize(Decimal('0.0001'))
                    if aggregates['avg_sharpe'] else Decimal('0.0000')
                ),
                "high_risk_portfolios_count": high_risk_count,
                "average_risk_score": (
                    round(aggregates['avg_score'], 1)
                    if aggregates['avg_score'] else 50.0
                ),
            },
            message="System-wide aggregate risk metrics retrieved successfully."
        )
