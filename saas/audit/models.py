import uuid

from django.db import models


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='audit_events')
    actor = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_events')
    action = models.CharField(max_length=128, db_index=True)
    content_type = models.ForeignKey('contenttypes.ContentType', on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.CharField(max_length=64, blank=True, default='', db_index=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'saas_audit_events'
        indexes = [
            models.Index(fields=['company', 'action', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]
