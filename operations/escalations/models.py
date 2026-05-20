import uuid

from django.db import models


class EscalationPolicy(models.Model):
    class TargetType(models.TextChoices):
        INCIDENT = 'incident', 'Incident'
        TICKET = 'ticket', 'Ticket'
        SLA = 'sla', 'SLA'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='escalation_policies')
    name = models.CharField(max_length=255)
    target_type = models.CharField(max_length=32, choices=TargetType.choices, db_index=True)
    severity = models.CharField(max_length=32, blank=True, default='', db_index=True)
    timeout_minutes = models.PositiveIntegerField(default=30)
    noc_team = models.ForeignKey('workforce.EngineerTeam', on_delete=models.SET_NULL, null=True, blank=True, related_name='noc_escalation_policies')
    manager_team = models.ForeignKey('workforce.EngineerTeam', on_delete=models.SET_NULL, null=True, blank=True, related_name='manager_escalation_policies')
    steps = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ops_escalation_policies'
        constraints = [models.UniqueConstraint(fields=['company', 'name'], name='uq_ops_escalation_policy_name')]
        indexes = [models.Index(fields=['company', 'target_type', 'severity', 'is_active'])]


class EscalationEvent(models.Model):
    class Level(models.TextChoices):
        NOC = 'noc', 'NOC'
        MANAGER = 'manager', 'Manager'
        EXECUTIVE = 'executive', 'Executive'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='escalation_events')
    policy = models.ForeignKey(EscalationPolicy, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    target_type = models.CharField(max_length=32, db_index=True)
    target_id = models.UUIDField(db_index=True)
    level = models.CharField(max_length=32, choices=Level.choices, db_index=True)
    reason = models.TextField()
    assigned_team = models.ForeignKey('workforce.EngineerTeam', on_delete=models.SET_NULL, null=True, blank=True, related_name='escalation_events')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'ops_escalation_events'
        indexes = [
            models.Index(fields=['company', 'target_type', 'target_id']),
            models.Index(fields=['company', 'level', '-created_at']),
        ]
