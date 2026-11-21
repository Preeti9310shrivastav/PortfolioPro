"""
Views for Technical Analysis, Momentum Indicators, and User Charting Preferences.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.technical.models import TechnicalIndicator, UserChartPreference
from apps.technical.serializers import (
    TechnicalIndicatorSerializer,
    TechnicalAnalysisSerializer,
    UserChartPreferenceSerializer,
)
from apps.market.models import Security
from apps.common.responses import api_success, api_error


class TechnicalAnalysisViewSet(viewsets.ViewSet):
    """
    ViewSet delivering public technical momentum analytics and authenticated user chart preferences.
    """
    def _resolve_security(self, security_id):
        """
        Locates a Security by either its UUID primary key or ticker symbol.
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
        Return the latest technical indicator snapshot and computed signal summary for an equity.
        """
        security = self._resolve_security(security_id)
        if not security:
            return api_error(
                message=f"Security '{security_id}' not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        latest_indicator = (
            TechnicalIndicator.objects.filter(security=security)
            .order_by('-calculation_date')
            .first()
        )

        if latest_indicator:
            # Derive human-friendly indicator diagnostics
            rsi = latest_indicator.rsi_14
            if rsi < 30:
                rsi_status = "Oversold (Bullish Reversal Potential)"
            elif rsi > 70:
                rsi_status = "Overbought (Correction Risk)"
            else:
                rsi_status = "Neutral Momentum"

            macd_status = (
                "Bullish (MACD Line Above Signal)"
                if latest_indicator.macd_line >= latest_indicator.macd_signal
                else "Bearish (MACD Line Below Signal)"
            )

            if latest_indicator.sma_20 > latest_indicator.sma_50 > latest_indicator.sma_200:
                trend_status = "Strong Uptrend (Golden Alignment)"
            elif latest_indicator.sma_20 < latest_indicator.sma_50 < latest_indicator.sma_200:
                trend_status = "Strong Downtrend (Death Alignment)"
            else:
                trend_status = "Consolidation / Mixed Trend"

            summary = {
                "rsi_interpretation": rsi_status,
                "macd_interpretation": macd_status,
                "trend_alignment": trend_status,
                "overall_signal": latest_indicator.overall_signal,
                "overall_signal_display": latest_indicator.get_overall_signal_display(),
                "calculation_date": str(latest_indicator.calculation_date),
            }
        else:
            summary = {
                "message": "No technical calculations recorded for this instrument yet.",
                "overall_signal": "NEUTRAL",
                "overall_signal_display": "Neutral / Consolidation",
            }

        response_data = {
            "security_id": str(security.id),
            "symbol": security.symbol,
            "company_name": security.company_name,
            "latest_indicator": (
                TechnicalIndicatorSerializer(latest_indicator).data
                if latest_indicator else None
            ),
            "summary": summary,
        }

        return api_success(
            data=response_data,
            message=f"Technical analysis for {security.symbol} retrieved successfully."
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path=r'indicators/(?P<security_id>[^/]+)'
    )
    def indicators(self, request, security_id=None):
        """
        List historical technical indicator series for chart plotting.
        """
        security = self._resolve_security(security_id)
        if not security:
            return api_error(
                message=f"Security '{security_id}' not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        limit = min(int(request.query_params.get('limit', 100)), 365)
        indicators_qs = (
            TechnicalIndicator.objects.filter(security=security)
            .order_by('-calculation_date')[:limit]
        )

        serializer = TechnicalIndicatorSerializer(indicators_qs, many=True)
        return api_success(
            data={
                "security_id": str(security.id),
                "symbol": security.symbol,
                "count": len(serializer.data),
                "indicators": serializer.data,
            },
            message=f"Historical technical indicators for {security.symbol} retrieved successfully."
        )

    @action(
        detail=False,
        methods=['get', 'post', 'put', 'patch'],
        permission_classes=[IsAuthenticated]
    )
    def preferences(self, request):
        """
        Retrieve or update the customer's candlestick chart indicators and timeframe preferences.
        """
        preference, _ = UserChartPreference.objects.get_or_create(
            user=request.user,
            defaults={
                'chart_type': UserChartPreference.CHART_CANDLESTICK,
                'timeframe': '1D',
                'default_indicators': {
                    'sma_20': True,
                    'sma_50': True,
                    'rsi_14': True,
                    'macd': True,
                }
            }
        )

        if request.method == 'GET':
            serializer = UserChartPreferenceSerializer(preference)
            return api_success(
                data={"preferences": serializer.data},
                message="User chart preferences retrieved successfully."
            )

        serializer = UserChartPreferenceSerializer(
            preference,
            data=request.data,
            partial=(request.method in ['PATCH', 'POST'])
        )
        if serializer.is_valid():
            saved_pref = serializer.save()
            return api_success(
                data={"preferences": UserChartPreferenceSerializer(saved_pref).data},
                message="User chart preferences updated successfully."
            )

        return api_error(
            message="Invalid chart preference configuration.",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )
