import uuid

from django.db import models


class CustomerAccount(models.Model):
    class Segment(models.TextChoices):
        ENTERPRISE = 'enterprise', 'Enterprise'
        WHOLESALE = 'wholesale', 'Wholesale'
        SMB = 'smb', 'SMB'
        RESIDENTIAL = 'residential', 'Residential'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        SUSPENDED = 'suspended', 'Suspended'
        CHURNED = 'churned', 'Churned'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='operation_customers')
    external_id = models.CharField(max_length=128, blank=True, default='')
    name = models.CharField(max_length=255)
    segment = models.CharField(max_length=32, choices=Segment.choices, default=Segment.ENTERPRISE, db_index=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE, db_index=True)
    contact_name = models.CharField(max_length=255, blank=True, default='')
    contact_email = models.EmailField(blank=True, default='')
    contact_phone = models.CharField(max_length=64, blank=True, default='')
    service_address = models.TextField(blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ops_customer_accounts'
        constraints = [
            models.UniqueConstraint(fields=['company', 'external_id'], condition=~models.Q(external_id=''), name='uq_ops_customer_external_id'),
        ]
        indexes = [
            models.Index(fields=['company', 'status', 'segment']),
            models.Index(fields=['company', 'name']),
        ]

    def __str__(self):
        return self.name

