"""
Views for Customer Support Tickets, Internal Messaging, and Supervisory Resolution.
"""
from django.utils import timezone
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from apps.support.models import SupportTicket, SupportMessage
from apps.support.serializers import (
    SupportTicketSerializer,
    SupportTicketCreateSerializer,
    SupportMessageSerializer,
    SupportMessageCreateSerializer,
    TicketAssignSerializer,
    TicketResolveSerializer,
)
from apps.common.responses import api_success, api_error
from apps.common.permissions import IsCustomer, IsFinanceOfficer


def generate_ticket_number():
    """
    Generate sequential ticket tracking code like TKT-000001.
    """
    count = SupportTicket.objects.count() + 1
    number = f"TKT-{count:06d}"
    while SupportTicket.objects.filter(ticket_number=number).exists():
        count += 1
        number = f"TKT-{count:06d}"
    return number


class SupportTicketViewSet(viewsets.ModelViewSet):
    """
    Customer portal ViewSet for submitting issues and interacting on ticket threads.
    """
    permission_classes = [IsAuthenticated, IsCustomer]

    def get_queryset(self):
        qs = (
            SupportTicket.objects.filter(user=self.request.user)
            .select_related('assigned_to', 'related_order')
            .order_by('-created_at')
        )
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param.upper())

        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category.upper())

        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return SupportTicketCreateSerializer
        return SupportTicketSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = SupportTicketSerializer(queryset, many=True, context={'request': request})
        return api_success(
            data={"tickets": serializer.data},
            message="Support tickets retrieved successfully."
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = SupportTicketSerializer(instance, context={'request': request})
        return api_success(
            data={"ticket": serializer.data},
            message="Support ticket details retrieved."
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = SupportTicketCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="Ticket submission validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        ticket_number = generate_ticket_number()
        initial_message_text = serializer.validated_data.pop('initial_message')

        ticket = SupportTicket.objects.create(
            ticket_number=ticket_number,
            user=request.user,
            **serializer.validated_data
        )

        SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message_text=initial_message_text,
            is_internal_note=False
        )

        read_serializer = SupportTicketSerializer(ticket, context={'request': request})
        return api_success(
            data={"ticket": read_serializer.data},
            message=f"Support ticket {ticket.ticket_number} created successfully.",
            status_code=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['get', 'post'])
    def messages(self, request, pk=None):
        """
        List public discussion messages for this ticket (excludes internal notes).
        POST posts a reply (same as add_message).
        """
        if request.method == 'POST':
            return self.add_message(request, pk=pk)
        ticket = self.get_object()
        messages_qs = (
            SupportMessage.objects.filter(ticket=ticket, is_internal_note=False)
            .select_related('sender')
            .order_by('created_at')
        )
        serializer = SupportMessageSerializer(messages_qs, many=True)
        return api_success(
            data={
                "ticket_id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "messages": serializer.data,
            },
            message="Messages retrieved successfully."
        )

    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """
        Customer posts a follow-up reply to an active support thread.
        """
        ticket = self.get_object()
        serializer = SupportMessageCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="Failed to post message.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Reopen or resume investigation if awaiting customer
        if ticket.status in [SupportTicket.STATUS_PENDING_CUSTOMER, SupportTicket.STATUS_RESOLVED]:
            ticket.status = SupportTicket.STATUS_IN_PROGRESS
            ticket.save(update_fields=['status', 'updated_at'])

        message = SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message_text=serializer.validated_data['message_text'],
            is_internal_note=False
        )

        return api_success(
            data={"message": SupportMessageSerializer(message).data},
            message="Reply submitted successfully.",
            status_code=status.HTTP_201_CREATED
        )


class AllTicketsViewSet(viewsets.ModelViewSet):
    """
    Supervisory ViewSet for Finance Officers to manage, triage, and resolve all tickets.
    """
    permission_classes = [IsAuthenticated, IsFinanceOfficer]
    serializer_class = SupportTicketSerializer

    def get_queryset(self):
        qs = (
            SupportTicket.objects.all()
            .select_related('user', 'assigned_to', 'related_order')
            .order_by('-created_at')
        )

        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param.upper())

        priority = self.request.query_params.get('priority')
        if priority:
            qs = qs.filter(priority=priority.upper())

        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category=category.upper())

        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            qs = qs.filter(assigned_to_id=assigned_to)

        return qs

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return api_success(
            data={
                "total_count": queryset.count(),
                "tickets": serializer.data,
            },
            message="All support tickets retrieved."
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return api_success(
            data={"ticket": serializer.data},
            message="Ticket details retrieved."
        )

    @action(detail=True, methods=['get', 'post'])
    def messages(self, request, pk=None):
        """
        List all discussion messages including staff-only internal notes.
        POST posts an officer reply (same as add_message).
        """
        if request.method == 'POST':
            return self.add_message(request, pk=pk)
        ticket = self.get_object()
        messages_qs = (
            SupportMessage.objects.filter(ticket=ticket)
            .select_related('sender')
            .order_by('created_at')
        )
        serializer = SupportMessageSerializer(messages_qs, many=True)
        return api_success(
            data={
                "ticket_id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "messages": serializer.data,
            },
            message="Ticket messages (with internal notes) retrieved."
        )

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign ticket to an authorized Finance Officer or Support Agent.
        """
        ticket = self.get_object()
        serializer = TicketAssignSerializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="Ticket assignment failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        assigned_agent = serializer.validated_data['assigned_to']
        ticket.assigned_to = assigned_agent
        if ticket.status == SupportTicket.STATUS_OPEN:
            ticket.status = SupportTicket.STATUS_IN_PROGRESS

        ticket.save(update_fields=['assigned_to', 'status', 'updated_at'])

        return api_success(
            data={"ticket": SupportTicketSerializer(ticket, context={'request': request}).data},
            message=f"Ticket {ticket.ticket_number} assigned to {assigned_agent.username}."
        )

    @transaction.atomic
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Mark ticket as resolved and optionally dispatch resolution explanation.
        """
        ticket = self.get_object()
        serializer = TicketResolveSerializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="Resolution validation failed.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        ticket.status = SupportTicket.STATUS_RESOLVED
        ticket.resolved_at = timezone.now()
        ticket.save(update_fields=['status', 'resolved_at', 'updated_at'])

        resolution_notes = serializer.validated_data.get('resolution_notes', '').strip()
        if resolution_notes:
            SupportMessage.objects.create(
                ticket=ticket,
                sender=request.user,
                message_text=f"Resolution Note:\n{resolution_notes}",
                is_internal_note=False
            )

        return api_success(
            data={"ticket": SupportTicketSerializer(ticket, context={'request': request}).data},
            message=f"Ticket {ticket.ticket_number} marked as resolved."
        )

    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        """
        Finance Officer posts reply to customer or records an internal compliance note.
        """
        ticket = self.get_object()
        serializer = SupportMessageCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return api_error(
                message="Failed to add message.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        is_internal_note = serializer.validated_data.get('is_internal_note', False)

        # If replying publicly to customer, change status to PENDING_CUSTOMER
        if not is_internal_note and ticket.status == SupportTicket.STATUS_IN_PROGRESS:
            ticket.status = SupportTicket.STATUS_PENDING_CUSTOMER
            ticket.save(update_fields=['status', 'updated_at'])

        message = SupportMessage.objects.create(
            ticket=ticket,
            sender=request.user,
            message_text=serializer.validated_data['message_text'],
            is_internal_note=is_internal_note
        )

        return api_success(
            data={"message": SupportMessageSerializer(message).data},
            message="Internal note recorded." if is_internal_note else "Reply sent to customer.",
            status_code=status.HTTP_201_CREATED
        )
