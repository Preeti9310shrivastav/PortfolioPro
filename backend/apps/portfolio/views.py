"""
Views for Portfolio Management, Holdings, and Valuation Snapshots.
"""
from decimal import Decimal
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.portfolio.models import Portfolio, PortfolioHolding, PortfolioSnapshot
from apps.portfolio.serializers import (
    PortfolioSerializer,
    PortfolioHoldingSerializer,
    PortfolioSnapshotSerializer,
    PortfolioSummarySerializer,
)
from apps.common.responses import api_success, api_error


class PortfolioViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing, managing, and calculating portfolio holdings and performance.
    """
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Portfolio.objects.filter(user=self.request.user)
            .prefetch_related('holdings__security__quote')
            .order_by('-is_default', 'name')
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_success(
            data={"portfolios": serializer.data},
            message="Portfolios retrieved successfully."
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_success(
            data={"portfolio": serializer.data},
            message="Portfolio details retrieved successfully."
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="Portfolio creation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # If this is the user's first portfolio, make it default
        has_existing = Portfolio.objects.filter(user=request.user).exists()
        is_default = serializer.validated_data.get('is_default', not has_existing)

        if is_default:
            Portfolio.objects.filter(user=request.user, is_default=True).update(is_default=False)

        portfolio = serializer.save(user=request.user, is_default=is_default)
        return api_success(
            data={"portfolio": self.get_serializer(portfolio).data},
            message="Portfolio created successfully.",
            status_code=status.HTTP_201_CREATED
        )

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return api_error(
                message="Portfolio update failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        if serializer.validated_data.get('is_default'):
            Portfolio.objects.filter(user=request.user, is_default=True).exclude(pk=instance.pk).update(
                is_default=False
            )

        portfolio = serializer.save()
        return api_success(
            data={"portfolio": self.get_serializer(portfolio).data},
            message="Portfolio updated successfully."
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_default and Portfolio.objects.filter(user=request.user).count() > 1:
            return api_error(
                message="Cannot delete default portfolio. Set another portfolio as default first.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        instance.delete()
        return api_success(message="Portfolio deleted successfully.")

    @action(detail=True, methods=['get'])
    def holdings(self, request, pk=None):
        """
        List all security holdings for the specified portfolio with real-time valuation.
        """
        portfolio = self.get_object()
        holdings_qs = (
            PortfolioHolding.objects.filter(portfolio=portfolio)
            .select_related('security', 'security__quote')
            .order_by('security__symbol')
        )
        serializer = PortfolioHoldingSerializer(holdings_qs, many=True)
        return api_success(
            data={
                "portfolio_id": str(portfolio.id),
                "portfolio_name": portfolio.name,
                "holdings": serializer.data,
            },
            message="Portfolio holdings retrieved successfully."
        )

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """
        Aggregate valuation and P&L metrics across all positions in the portfolio.
        """
        portfolio = self.get_object()
        holdings = (
            PortfolioHolding.objects.filter(portfolio=portfolio)
            .select_related('security__quote')
        )

        total_invested = Decimal('0.0000')
        current_value = Decimal('0.0000')
        total_realized_pnl = Decimal('0.0000')
        day_change = Decimal('0.0000')

        for h in holdings:
            total_invested += h.total_invested
            c_val = h.current_value
            current_value += c_val
            total_realized_pnl += h.realized_pnl

            if hasattr(h.security, 'quote') and h.security.quote:
                day_change += Decimal(h.quantity) * h.security.quote.change_amount

        total_unrealized_pnl = current_value - total_invested
        total_pnl = total_unrealized_pnl + total_realized_pnl
        overall_return_pct = (
            (total_unrealized_pnl / total_invested) * Decimal('100.0000')
            if total_invested > Decimal('0.0000')
            else Decimal('0.0000')
        )

        summary_data = {
            "portfolio_id": str(portfolio.id),
            "portfolio_name": portfolio.name,
            "total_invested": total_invested,
            "current_value": current_value,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_realized_pnl": total_realized_pnl,
            "total_pnl": total_pnl,
            "overall_return_pct": overall_return_pct,
            "day_change": day_change,
            "holdings_count": holdings.count(),
        }

        return api_success(
            data=summary_data,
            message="Portfolio summary calculated successfully."
        )

    @action(detail=True, methods=['get'])
    def snapshots(self, request, pk=None):
        """
        Retrieve historical valuation snapshots for equity curve charting.
        """
        portfolio = self.get_object()
        snapshots_qs = (
            PortfolioSnapshot.objects.filter(portfolio=portfolio)
            .order_by('-snapshot_date')[:90]
        )
        serializer = PortfolioSnapshotSerializer(snapshots_qs, many=True)
        return api_success(
            data={
                "portfolio_id": str(portfolio.id),
                "snapshots": serializer.data,
            },
            message="Portfolio snapshots retrieved successfully."
        )
