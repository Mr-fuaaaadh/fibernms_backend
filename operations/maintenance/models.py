import uuid

from django.db import models


class MaintenanceWindow(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING_APPROVAL = 'pending_approval', 'Pending Approval'
        APPROVED = 'approved', 'Approved'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='maintenance_windows')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT, db_index=True)
    planned_start = models.DateTimeField(db_index=True)
    planned_end = models.DateTimeField(db_index=True)
    expected_outage_minutes = models.PositiveIntegerField(default=0)
    affected_services = models.JSONField(default=list, blank=True)
    affected_customers = models.PositiveIntegerField(default=0)
    device = models.ForeignKey('devices.Device', on_delete=models.SET_NULL, null=True, blank=True, related_name='maintenance_windows')
    requested_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='requested_maintenance_windows')
    approved_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_maintenance_windows')
    approved_at = models.DateTimeField(null=True, blank=True)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ops_maintenance_windows'
        indexes = [
            models.Index(fields=['company', 'status', 'planned_start']),
            models.Index(fields=['company', 'device', 'planned_start']),
        ]

