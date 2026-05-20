import uuid

from django.db import models


class Incident(models.Model):
    class Severity(models.TextChoices):
        SEV1 = 'sev1', 'SEV1 - Critical Outage'
        SEV2 = 'sev2', 'SEV2 - Major Degradation'
        SEV3 = 'sev3', 'SEV3 - Minor Degradation'
        SEV4 = 'sev4', 'SEV4 - Informational'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        INVESTIGATING = 'investigating', 'Investigating'
        MITIGATED = 'mitigated', 'Mitigated'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='incidents')
    incident_number = models.CharField(max_length=32, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    severity = models.CharField(max_length=16, choices=Severity.choices, db_index=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.OPEN, db_index=True)
    impact = models.TextField(blank=True, default='')
    affected_customers = models.PositiveIntegerField(default=0)
    affected_services = models.JSONField(default=list, blank=True)
    device = models.ForeignKey('devices.Device', on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    customer = models.ForeignKey('customers.CustomerAccount', on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    assigned_team = models.ForeignKey('workforce.EngineerTeam', on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents')
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents')
    rca_summary = models.TextField(blank=True, default='')
    rca_completed_at = models.DateTimeField(null=True, blank=True)
    outage_started_at = models.DateTimeField(null=True, blank=True)
    outage_ended_at = models.DateTimeField(null=True, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True, db_index=True)
    mitigated_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_incidents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ops_incidents'
        constraints = [
            models.UniqueConstraint(fields=['company', 'incident_number'], name='uq_ops_incident_number'),
        ]
        indexes = [
            models.Index(fields=['company', 'status', 'severity']),
            models.Index(fields=['company', '-detected_at']),
            models.Index(fields=['company', 'assigned_team', 'status']),
        ]


class IncidentTimelineEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='incident_timeline_events')
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='timeline')
    event_type = models.CharField(max_length=64, db_index=True)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    actor = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='incident_timeline_events')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'ops_incident_timeline'
        indexes = [
            models.Index(fields=['company', 'incident', '-created_at']),
            models.Index(fields=['company', 'event_type', '-created_at']),
        ]

