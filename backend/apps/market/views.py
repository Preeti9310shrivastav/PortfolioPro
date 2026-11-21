"""
Views for PortfolioPro Market Module.
Handles equity security masters, real-time quotes, historical price bars, and user watchlists.
"""
import uuid
import logging
from django.db import models
from django.utils import timezone
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.market.models import (
    Security,
    MarketQuote,
    HistoricalPrice,
    Watchlist,
    WatchlistItem,
)
from apps.market.serializers import (
    SecuritySerializer,
    MarketQuoteSerializer,
    SecurityWithQuoteSerializer,
    HistoricalPriceSerializer,
    WatchlistSerializer,
    WatchlistCreateSerializer,
    WatchlistItemSerializer,
    WatchlistAddSecuritySerializer,
)
from apps.common.responses import api_success, api_error
from apps.common.permissions import IsFinanceOfficer

logger = logging.getLogger(__name__)


class SecurityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public ViewSet to browse listed equities on NSE/BSE with live price quotes.
    Supports ticker search, sector/exchange filtering, and historical OHLCV data.
    """
    serializer_class = SecurityWithQuoteSerializer
    permission_classes = [AllowAny]
    lookup_field = 'symbol'

    def get_object(self):
        lookup = self.kwargs.get(self.lookup_field)
        queryset = self.get_queryset()

        # Check if valid UUID or symbol
        obj = queryset.filter(symbol__iexact=lookup).first()
        if not obj:
            try:
                uuid.UUID(str(lookup))
                obj = queryset.filter(id=lookup).first()
            except (ValueError, TypeError):
                pass

        if not obj:
            raise Http404(f"Security with symbol/ID '{lookup}' does not exist.")
        return obj

    def get_queryset(self):
        queryset = Security.objects.filter(is_active=True).select_related('quote')

        # Filter by sector
        sector = self.request.query_params.get('sector')
        if sector:
            queryset = queryset.filter(sector__iexact=sector)

        # Filter by exchange (NSE / BSE)
        exchange = self.request.query_params.get('exchange')
        if exchange:
            queryset = queryset.filter(exchange__iexact=exchange)

        # Search by symbol or company name
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(symbol__icontains=search) |
                models.Q(company_name__icontains=search)
            )

        # Ordering
        ordering = self.request.query_params.get('ordering', 'symbol')
        if ordering in ['symbol', '-symbol', 'company_name', '-company_name']:
            queryset = queryset.order_by(ordering)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return api_success(
                data={
                    "count": self.paginator.page.paginator.count,
                    "securities": serializer.data
                },
                message="Listed securities retrieved successfully."
            )
        serializer = self.get_serializer(queryset, many=True)
        return api_success(
            data={"count": queryset.count(), "securities": serializer.data},
            message="Listed securities retrieved successfully."
        )

    def retrieve(self, request, *args, **kwargs):
        security = self.get_object()
        serializer = self.get_serializer(security)
        return api_success(
            data={"security": serializer.data},
            message=f"Market data for {security.symbol} retrieved."
        )

    @extend_schema(responses={200: SecurityWithQuoteSerializer})
    @action(detail=True, methods=['get'], url_path='quote')
    def quote(self, request, symbol=None):
        """
        Retrieve latest live quote for a specific equity instrument.
        """
        security = self.get_object()
        serializer = SecurityWithQuoteSerializer(security)
        return api_success(
            data={"security": serializer.data},
            message=f"Live quote for {security.symbol} retrieved successfully."
        )

    @extend_schema(responses={200: HistoricalPriceSerializer(many=True)})
    @action(detail=True, methods=['get'], url_path='history')
    def history(self, request, symbol=None):
        """
        Fetch daily OHLCV historical time-series bars for candlestick charting.
        Timeframe options: 1W, 1M, 3M, 6M, 1Y, ALL (default: 1M).
        """
        security = self.get_object()
        timeframe = request.query_params.get('timeframe', '1M').upper()

        now = timezone.now().date()
        limit_days = 30
        if timeframe == '1W':
            limit_days = 7
        elif timeframe == '1M':
            limit_days = 30
        elif timeframe == '3M':
            limit_days = 90
        elif timeframe == '6M':
            limit_days = 180
        elif timeframe == '1Y':
            limit_days = 365
        elif timeframe == 'ALL':
            limit_days = 3650

        start_date = now - timezone.timedelta(days=limit_days)
        prices = HistoricalPrice.objects.filter(
            security=security,
            trade_date__gte=start_date
        ).order_by('trade_date')

        serializer = HistoricalPriceSerializer(prices, many=True)
        return api_success(
            data={
                "symbol": security.symbol,
                "timeframe": timeframe,
                "count": prices.count(),
                "bars": serializer.data
            },
            message=f"Historical price series for {security.symbol} retrieved."
        )


class WatchlistViewSet(viewsets.ModelViewSet):
    """
    ViewSet for authenticated customer watchlists.
    Allows creating, naming, pinning, and unpinning equity tickers with live quotes.
    """
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).prefetch_related(
            'items__security__quote'
        ).order_by('created_at')

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WatchlistCreateSerializer
        return WatchlistSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = WatchlistSerializer(queryset, many=True)
        return api_success(
            data={"count": queryset.count(), "watchlists": serializer.data},
            message="User watchlists retrieved successfully."
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = WatchlistSerializer(instance)
        return api_success(
            data={"watchlist": serializer.data},
            message=f"Watchlist '{instance.name}' retrieved."
        )

    def create(self, request, *args, **kwargs):
        serializer = WatchlistCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="Watchlist creation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        name = serializer.validated_data['name']
        if Watchlist.objects.filter(user=request.user, name__iexact=name).exists():
            return api_error(
                message=f"Watchlist with name '{name}' already exists for your account.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        watchlist = serializer.save(user=request.user)
        logger.info(f"Watchlist '{watchlist.name}' created by {request.user.username}")

        return api_success(
            data={"watchlist": WatchlistSerializer(watchlist).data},
            message=f"Watchlist '{watchlist.name}' created successfully.",
            status_code=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        name = instance.name
        instance.delete()
        logger.info(f"Watchlist '{name}' deleted by {request.user.username}")
        return api_success(message=f"Watchlist '{name}' deleted successfully.")

    @extend_schema(request=WatchlistAddSecuritySerializer, responses={200: WatchlistSerializer})
    @action(detail=True, methods=['post'], url_path='add-security')
    def add_security(self, request, pk=None):
        """
        Add a stock to this watchlist.
        """
        watchlist = self.get_object()
        serializer = WatchlistAddSecuritySerializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="Failed to add ticker to watchlist.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        security = serializer.validated_data['security']
        if WatchlistItem.objects.filter(watchlist=watchlist, security=security).exists():
            return api_error(
                message=f"{security.symbol} is already in watchlist '{watchlist.name}'.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        item_count = watchlist.items.count()
        WatchlistItem.objects.create(
            watchlist=watchlist,
            security=security,
            display_order=item_count + 1
        )

        refreshed = Watchlist.objects.prefetch_related('items__security__quote').get(id=watchlist.id)
        return api_success(
            data={"watchlist": WatchlistSerializer(refreshed).data},
            message=f"Added {security.symbol} to watchlist '{watchlist.name}'."
        )

    @extend_schema(responses={200: WatchlistSerializer})
    @action(detail=True, methods=['post', 'delete'], url_path='remove-security')
    def remove_security(self, request, pk=None):
        """
        Remove a stock from this watchlist.
        Accepts security_id or symbol in query_params or body.
        """
        watchlist = self.get_object()
        security_id = request.data.get('security_id') or request.query_params.get('security_id')
        symbol = request.data.get('symbol') or request.query_params.get('symbol')

        item = None
        if security_id:
            item = WatchlistItem.objects.filter(watchlist=watchlist, security_id=security_id).first()
        elif symbol:
            item = WatchlistItem.objects.filter(
                watchlist=watchlist,
                security__symbol__iexact=symbol.strip()
            ).first()

        if not item:
            return api_error(
                message="Specified ticker is not present in this watchlist.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        removed_symbol = item.security.symbol
        item.delete()

        refreshed = Watchlist.objects.prefetch_related('items__security__quote').get(id=watchlist.id)
        return api_success(
            data={"watchlist": WatchlistSerializer(refreshed).data},
            message=f"Removed {removed_symbol} from watchlist '{watchlist.name}'."
        )


class DefaultWatchlistView(APIView):
    """
    Direct endpoint for customer default watchlist matching checklist:
    - GET /api/market/watchlist/
    - POST /api/market/watchlist/ (add security)
    - DELETE /api/market/watchlist/<symbol>/ (remove security)
    """
    permission_classes = [IsAuthenticated]

    def _get_or_create_default(self, user):
        watchlist = Watchlist.objects.filter(user=user, is_default=True).first()
        if not watchlist:
            watchlist = Watchlist.objects.filter(user=user).first()
        if not watchlist:
            watchlist = Watchlist.objects.create(user=user, name='My Watchlist', is_default=True)
        return watchlist

    def get(self, request):
        watchlist = self._get_or_create_default(request.user)
        items = WatchlistItem.objects.filter(watchlist=watchlist).select_related(
            'security', 'security__quote'
        ).order_by('display_order')

        serializer = WatchlistItemSerializer(items, many=True)
        return api_success(
            data={
                "watchlist_id": str(watchlist.id),
                "watchlist_name": watchlist.name,
                "count": items.count(),
                "items": serializer.data
            },
            message="Default watchlist retrieved successfully."
        )

    def post(self, request):
        watchlist = self._get_or_create_default(request.user)
        serializer = WatchlistAddSecuritySerializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="Cannot add security to watchlist.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        security = serializer.validated_data['security']
        if WatchlistItem.objects.filter(watchlist=watchlist, security=security).exists():
            return api_error(
                message=f"{security.symbol} is already in your watchlist.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        WatchlistItem.objects.create(
            watchlist=watchlist,
            security=security,
            display_order=watchlist.items.count() + 1
        )

        return api_success(
            data={"symbol": security.symbol, "watchlist": watchlist.name},
            message=f"Added {security.symbol} to watchlist.",
            status_code=status.HTTP_201_CREATED
        )


class DefaultWatchlistDeleteView(APIView):
    """
    DELETE /api/market/watchlist/<symbol>/
    """
    permission_classes = [IsAuthenticated]

    def delete(self, request, symbol):
        watchlist = Watchlist.objects.filter(user=request.user, is_default=True).first()
        if not watchlist:
            watchlist = Watchlist.objects.filter(user=request.user).first()
        if not watchlist:
            return api_error(message="Watchlist not found.", status_code=status.HTTP_404_NOT_FOUND)

        item = WatchlistItem.objects.filter(
            watchlist=watchlist,
            security__symbol__iexact=symbol.strip()
        ).first()

        if not item:
            return api_error(
                message=f"{symbol} is not present in your watchlist.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        item.delete()
        return api_success(message=f"Removed {symbol.upper()} from your watchlist.")


class MarketFeedStatusView(APIView):
    """
    Finance Officer supervisory endpoint:
    GET /api/market/admin/feed-status/
    Reports health, active tickers, and quote refresh timestamps.
    """
    permission_classes = [IsAuthenticated, IsFinanceOfficer]

    def get(self, request):
        total_securities = Security.objects.filter(is_active=True).count()
        total_quotes = MarketQuote.objects.count()
        latest_quote = MarketQuote.objects.order_by('-updated_at').first()

        return api_success(
            data={
                "feed_status": "ONLINE",
                "active_securities": total_securities,
                "tracked_quotes": total_quotes,
                "latest_update": latest_quote.updated_at.isoformat() if latest_quote else None,
            },
            message="Market data feed status retrieved."
        )
