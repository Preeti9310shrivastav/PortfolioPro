"""
Django Admin registration for Support Helpdesk Tickets and Messages.
"""
from django.contrib import admin
from apps.support.models import SupportTicket, SupportMessage


class SupportMessageInline(admin.TabularInline):
    model = SupportMessage
    extra = 0
    fields = ('sender', 'message_text', 'is_internal_note', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_number',
        'user',
        'category',
        'priority',
        'status',
        'subject',
        'assigned_to',
        'created_at',
        'resolved_at',
    )
    list_filter = ('category', 'priority', 'status', 'created_at')
    search_fields = ('ticket_number', 'subject', 'user__username', 'assigned_to__username')
    inlines = [SupportMessageInline]


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = (
        'ticket',
        'sender',
        'is_internal_note',
        'created_at',
    )
    list_filter = ('is_internal_note', 'created_at')
    search_fields = ('ticket__ticket_number', 'sender__username', 'message_text')
