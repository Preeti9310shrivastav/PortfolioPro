"""
Views for Fundamental Analysis, Corporate Financial Statements, and Sector Peer Comparisons.
"""
from decimal import Decimal
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from apps.fundamental.models import FundamentalMetric, CompanyFinancial
from apps.fundamental.serializers import (
    FundamentalMetricSerializer,
    CompanyFinancialSerializer,
    FundamentalAnalysisSerializer,
    PeerComparisonItemSerializer,
)
from apps.market.models import Security
from apps.common.responses import api_success, api_error


class FundamentalAnalysisViewSet(viewsets.ViewSet):
    """
    Public ViewSet providing equity fundamental metrics, balance sheet statements, and sector peers.
    """
    permission_classes = [AllowAny]

    def _resolve_security(self, security_id):
        """
        Resolves security by UUID or by ticker symbol.
        """
        try:
            return Security.objects.filter(id=security_id).first()
        except (ValueError, TypeError):
            pass
        return Security.objects.filter(symbol__iexact=security_id).first()

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path=r'analysis/(?P<security_id>[^/]+)'
    )
    def analysis(self, request, security_id=None):
        """
        Return comprehensive fundamental valuation ratios and recent quarterly/annual financials.
        """
        security = self._resolve_security(security_id)
        if not security:
            return api_error(
                message=f"Security '{security_id}' not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        metric = FundamentalMetric.objects.filter(security=security).first()
        financials = (
            CompanyFinancial.objects.filter(security=security)
            .order_by('-period_name')[:8]
        )

        response_data = {
            "security_id": str(security.id),
            "symbol": security.symbol,
            "company_name": security.company_name,
            "sector": security.sector,
            "metric": FundamentalMetricSerializer(metric).data if metric else None,
            "financials": CompanyFinancialSerializer(financials, many=True).data,
        }

        return api_success(
            data=response_data,
            message=f"Fundamental analysis for {security.symbol} retrieved successfully."
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path=r'peers/(?P<security_id>[^/]+)'
    )
    def peers(self, request, security_id=None):
        """
        Compare target equity with industry peers operating in the same market sector.
        """
        security = self._resolve_security(security_id)
        if not security:
            return api_error(
                message=f"Security '{security_id}' not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        peers_qs = (
            Security.objects.filter(sector=security.sector, is_active=True)
            .select_related('fundamental_metric', 'quote')
            .order_by('-fundamental_metric__market_cap')[:10]
        )

        peer_items = []
        for peer in peers_qs:
            ltp = peer.quote.ltp if hasattr(peer, 'quote') and peer.quote else Decimal('0.0000')
            fm = getattr(peer, 'fundamental_metric', None)

            peer_items.append({
                "security_id": str(peer.id),
                "symbol": peer.symbol,
                "company_name": peer.company_name,
                "sector": peer.sector,
                "ltp": ltp,
                "market_cap": fm.market_cap if fm else None,
                "pe_ratio": fm.pe_ratio if fm else None,
                "pb_ratio": fm.pb_ratio if fm else None,
                "roe": fm.roe if fm else None,
                "dividend_yield": fm.dividend_yield if fm else None,
                "health_score": fm.health_score if fm else None,
            })

        return api_success(
            data={
                "target_symbol": security.symbol,
                "sector": security.sector,
                "peers_count": len(peer_items),
                "peers": peer_items,
            },
            message=f"Peer comparison for {security.symbol} [{security.sector}] retrieved successfully."
        )
