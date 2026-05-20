import uuid

from django.db import models


class Alert(models.Model):
    class Severity(models.TextChoices):
        CRITICAL = 'critical', 'Critical'
        HIGH = 'high', 'High'
        MEDIUM = 'medium', 'Medium'
        LOW = 'low', 'Low'
        INFO = 'info', 'Info'

    class AlertType(models.TextChoices):
        DEVICE_DOWN = 'device_down', 'Device Down'
        CABLE_CUT = 'cable_cut', 'Cable Cut'
        SIGNAL_DEGRADED = 'signal_degraded', 'Signal Degraded'
        THRESHOLD_BREACH = 'threshold_breach', 'Threshold Breach'
        MAINTENANCE_DUE = 'maintenance_due', 'Maintenance Due'
        CAPACITY_WARNING = 'capacity_warning', 'Capacity Warning'
        SECURITY = 'security', 'Security'
        SYSTEM = 'system', 'System'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        ACKNOWLEDGED = 'acknowledged', 'Acknowledged'
        RESOLVED = 'resolved', 'Resolved'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='alerts')
    severity = models.CharField(max_length=16, choices=Severity.choices, db_index=True)
    type = models.CharField(max_length=32, choices=AlertType.choices, db_index=True)
    device = models.ForeignKey(
        'devices.Device',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts',
    )
    route = models.ForeignKey(
        'topology.FiberRoute',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='alerts',
    )
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    affected_customers = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.OPEN, db_index=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acknowledged_alerts',
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts',
    )

    class Meta:
        db_table = 'noc_alerts'
        indexes = [
            models.Index(fields=['company', 'status', '-timestamp']),
            models.Index(fields=['company', 'severity', '-timestamp']),
            models.Index(fields=['company', 'type', '-timestamp']),
            models.Index(fields=['company', 'device', '-timestamp']),
        ]
