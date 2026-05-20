import uuid

from django.db import models


class Workflow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='workflows')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    trigger_type = models.CharField(max_length=64, db_index=True)
    nodes = models.JSONField(default=list, blank=True)
    edges = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'noc_workflows'
        constraints = [
            models.UniqueConstraint(fields=['company', 'name'], name='uq_workflow_company_name'),
        ]
        indexes = [
            models.Index(fields=['company', 'trigger_type', 'is_active']),
            models.Index(fields=['company', '-updated_at']),
        ]


class WorkflowRun(models.Model):
    class Status(models.TextChoices):
        RUNNING = 'running', 'Running'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name='runs')
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='workflow_runs')
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.RUNNING, db_index=True)
    triggered_by = models.CharField(max_length=64, blank=True, default='')
    event_name = models.CharField(max_length=128, db_index=True)
    event_payload = models.JSONField(default=dict, blank=True)
    logs = models.JSONField(default=list, blank=True)
    execution_time_ms = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True, db_index=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'noc_workflow_runs'
        indexes = [
            models.Index(fields=['company', 'status', '-started_at']),
            models.Index(fields=['company', 'event_name', '-started_at']),
            models.Index(fields=['workflow', '-started_at']),
        ]

