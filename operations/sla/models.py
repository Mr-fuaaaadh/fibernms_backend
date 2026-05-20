import uuid

from django.db import models


class SLAProfile(models.Model):
    class Scope(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        DEVICE = 'device', 'Device'
        SERVICE = 'service', 'Service'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='sla_profiles')
    name = models.CharField(max_length=255)
    scope = models.CharField(max_length=32, choices=Scope.choices, db_index=True)
    customer = models.ForeignKey('customers.CustomerAccount', on_delete=models.CASCADE, null=True, blank=True, related_name='sla_profiles')
    device = models.ForeignKey('devices.Device', on_delete=models.CASCADE, null=True, blank=True, related_name='sla_profiles')
    service_name = models.CharField(max_length=255, blank=True, default='')
    uptime_target = models.DecimalField(max_digits=5, decimal_places=2, default=99.90)
    mttr_minutes_target = models.PositiveIntegerField(default=240)
    mtbf_hours_target = models.PositiveIntegerField(default=720)
    packet_loss_target = models.DecimalField(max_digits=5, decimal_places=2, default=1.00)
    latency_ms_target = models.PositiveIntegerField(default=100)
    response_time_minutes_target = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ops_sla_profiles'
        constraints = [models.UniqueConstraint(fields=['company', 'name'], name='uq_ops_sla_profile_name')]
        indexes = [models.Index(fields=['company', 'scope', 'is_active'])]


class SLAMetricSnapshot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='sla_metric_snapshots')
    profile = models.ForeignKey(SLAProfile, on_delete=models.CASCADE, related_name='metric_snapshots')
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField(db_index=True)
    uptime_percent = models.DecimalField(max_digits=6, decimal_places=3)
    mttr_minutes = models.PositiveIntegerField(default=0)
    mtbf_hours = models.PositiveIntegerField(default=0)
    packet_loss_percent = models.DecimalField(max_digits=6, decimal_places=3, default=0)
    latency_ms = models.PositiveIntegerField(default=0)
    response_time_minutes = models.PositiveIntegerField(default=0)
    is_breached = models.BooleanField(default=False, db_index=True)
    breach_reasons = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ops_sla_metric_snapshots'
        indexes = [
            models.Index(fields=['company', 'profile', '-period_end']),
            models.Index(fields=['company', 'is_breached', '-created_at']),
        ]


class SLATimer(models.Model):
    class TargetType(models.TextChoices):
        INCIDENT = 'incident', 'Incident'
        TICKET = 'ticket', 'Ticket'

    class Status(models.TextChoices):
        RUNNING = 'running', 'Running'
        PAUSED = 'paused', 'Paused'
        MET = 'met', 'Met'
        BREACHED = 'breached', 'Breached'
        CANCELLED = 'cancelled', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='sla_timers')
    profile = models.ForeignKey(SLAProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='timers')
    target_type = models.CharField(max_length=32, choices=TargetType.choices, db_index=True)
    target_id = models.UUIDField(db_index=True)
    metric = models.CharField(max_length=64, db_index=True)
    started_at = models.DateTimeField(auto_now_add=True)
    due_at = models.DateTimeField(db_index=True)
    stopped_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.RUNNING, db_index=True)
    breach_notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ops_sla_timers'
        indexes = [
            models.Index(fields=['company', 'target_type', 'target_id']),
            models.Index(fields=['company', 'status', 'due_at']),
        ]

