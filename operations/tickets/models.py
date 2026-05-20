import uuid

from django.db import models


class Ticket(models.Model):
    class Priority(models.TextChoices):
        P1 = 'p1', 'P1'
        P2 = 'p2', 'P2'
        P3 = 'p3', 'P3'
        P4 = 'p4', 'P4'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        WAITING_CUSTOMER = 'waiting_customer', 'Waiting Customer'
        ESCALATED = 'escalated', 'Escalated'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='tickets')
    ticket_number = models.CharField(max_length=32, db_index=True)
    subject = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    priority = models.CharField(max_length=8, choices=Priority.choices, default=Priority.P3, db_index=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.OPEN, db_index=True)
    customer = models.ForeignKey('customers.CustomerAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    incident = models.ForeignKey('incidents.Incident', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    assigned_team = models.ForeignKey('workforce.EngineerTeam', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    response_due_at = models.DateTimeField(null=True, blank=True)
    resolution_due_at = models.DateTimeField(null=True, blank=True)
    escalated_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_tickets')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ops_tickets'
        constraints = [
            models.UniqueConstraint(fields=['company', 'ticket_number'], name='uq_ops_ticket_number'),
        ]
        indexes = [
            models.Index(fields=['company', 'status', 'priority']),
            models.Index(fields=['company', 'assigned_to', 'status']),
            models.Index(fields=['company', '-created_at']),
        ]


class TicketComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='ticket_comments')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_comments')
    body = models.TextField()
    is_internal = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'ops_ticket_comments'
        indexes = [models.Index(fields=['company', 'ticket', '-created_at'])]


class TicketAttachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='ticket_attachments')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='attachments')
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_attachments')
    file = models.FileField(upload_to='ticket_attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    content_type = models.CharField(max_length=128, blank=True, default='')
    size_bytes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ops_ticket_attachments'
        indexes = [models.Index(fields=['company', 'ticket', '-created_at'])]

