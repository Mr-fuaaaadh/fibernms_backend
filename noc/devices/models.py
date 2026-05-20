import uuid

from django.core.exceptions import ImproperlyConfigured
from django.db import models as django_models

try:
    from django.contrib.gis.db import models as gis_models
    HAS_GIS = True
except ImproperlyConfigured:
    gis_models = django_models
    HAS_GIS = False


class Device(gis_models.Model):
    class DeviceType(gis_models.TextChoices):
        OLT = 'OLT', 'OLT'
        ONT = 'ONT', 'ONT'
        SPLITTER = 'Splitter', 'Splitter'
        ROUTER = 'Router', 'Router'
        SWITCH = 'Switch', 'Switch'
        JJB = 'JJB', 'JJB'
        COUPLER = 'Coupler', 'Coupler'

    class DeviceStatus(gis_models.TextChoices):
        ONLINE = 'online', 'Online'
        OFFLINE = 'offline', 'Offline'
        DEGRADED = 'degraded', 'Degraded'
        MAINTENANCE = 'maintenance', 'Maintenance'

    id = gis_models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = gis_models.ForeignKey('companies.Company', on_delete=gis_models.CASCADE, related_name='devices')
    name = gis_models.CharField(max_length=255)
    type = gis_models.CharField(max_length=32, choices=DeviceType.choices)
    status = gis_models.CharField(max_length=32, choices=DeviceStatus.choices, default=DeviceStatus.OFFLINE)
    if HAS_GIS:
        location = gis_models.PointField(srid=4326, geography=True)
    else:
        location = gis_models.JSONField(default=dict, blank=True)
    region = gis_models.CharField(max_length=120, db_index=True)
    uptime = gis_models.FloatField(default=0.0)
    tx_power = gis_models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    rx_power = gis_models.DecimalField(max_digits=7, decimal_places=3, null=True, blank=True)
    parent = gis_models.ForeignKey(
        'self',
        on_delete=gis_models.SET_NULL,
        null=True,
        blank=True,
        related_name='children',
    )
    customer_count = gis_models.PositiveIntegerField(default=0)
    metadata = gis_models.JSONField(default=dict, blank=True)
    last_seen = gis_models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = gis_models.DateTimeField(auto_now_add=True)
    updated_at = gis_models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'noc_devices'
        indexes = [
            gis_models.Index(fields=['company', 'type', 'status']),
            gis_models.Index(fields=['company', 'region']),
            gis_models.Index(fields=['company', 'parent']),
            gis_models.Index(fields=['company', '-last_seen']),
        ]
        constraints = [
            gis_models.UniqueConstraint(fields=['company', 'name'], name='uq_device_company_name'),
        ]

    def __str__(self) -> str:
        return f'{self.name} ({self.type})'
