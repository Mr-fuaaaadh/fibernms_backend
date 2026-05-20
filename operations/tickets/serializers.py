from rest_framework import serializers

from .models import Ticket, TicketAttachment, TicketComment


class TicketCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketComment
        fields = ('id', 'ticket', 'author', 'body', 'is_internal', 'created_at')
        read_only_fields = ('id', 'ticket', 'author', 'created_at')


class TicketAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = ('id', 'ticket', 'uploaded_by', 'file', 'filename', 'content_type', 'size_bytes', 'created_at')
        read_only_fields = ('id', 'ticket', 'uploaded_by', 'filename', 'content_type', 'size_bytes', 'created_at')


class TicketSerializer(serializers.ModelSerializer):
    comments = TicketCommentSerializer(many=True, read_only=True)
    attachments = TicketAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = (
            'id', 'company', 'ticket_number', 'subject', 'description', 'priority', 'status', 'customer',
            'incident', 'assigned_team', 'assigned_to', 'response_due_at', 'resolution_due_at', 'escalated_at',
            'resolved_at', 'closed_at', 'created_by', 'created_at', 'updated_at', 'comments', 'attachments',
        )
        read_only_fields = (
            'company', 'ticket_number', 'response_due_at', 'resolution_due_at', 'escalated_at',
            'resolved_at', 'closed_at', 'created_by', 'created_at', 'updated_at', 'comments', 'attachments',
        )

