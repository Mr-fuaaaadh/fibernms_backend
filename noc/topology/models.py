import uuid

from django.core.exceptions import ImproperlyConfigured
from django.db import models as django_models

try:
    from django.contrib.gis.db import models as gis_models
    HAS_GIS = True
except ImproperlyConfigured:
    gis_models = django_models
    HAS_GIS = False


class FiberRoute(gis_models.Model):
    class RouteType(gis_models.TextChoices):
        FEEDER = 'feeder', 'Feeder'
        DISTRIBUTION = 'distribution', 'Distribution'
        DROP = 'drop', 'Drop'
        BACKBONE = 'backbone', 'Backbone'

    class RouteStatus(gis_models.TextChoices):
        ACTIVE = 'active', 'Active'
        PLANNED = 'planned', 'Planned'
        DEGRADED = 'degraded', 'Degraded'
        DOWN = 'down', 'Down'

    id = gis_models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = gis_models.ForeignKey('companies.Company', on_delete=gis_models.CASCADE, related_name='fiber_routes')
    name = gis_models.CharField(max_length=255)
    route_type = gis_models.CharField(max_length=32, choices=RouteType.choices)
    status = gis_models.CharField(max_length=32, choices=RouteStatus.choices, default=RouteStatus.PLANNED)
    if HAS_GIS:
        geometry = gis_models.LineStringField(srid=4326, geography=True)
    else:
        geometry = gis_models.JSONField(default=dict, blank=True)
    from_device = gis_models.ForeignKey('devices.Device', on_delete=gis_models.PROTECT, related_name='routes_out')
    to_device = gis_models.ForeignKey('devices.Device', on_delete=gis_models.PROTECT, related_name='routes_in')
    length_meters = gis_models.FloatField(default=0.0)
    attenuation_db_km = gis_models.DecimalField(max_digits=7, decimal_places=3, default=0)
    capacity_gbps = gis_models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = gis_models.DateTimeField(auto_now_add=True)
    updated_at = gis_models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'noc_fiber_routes'
        indexes = [
            gis_models.Index(fields=['company', 'route_type', 'status']),
            gis_models.Index(fields=['company', 'from_device']),
            gis_models.Index(fields=['company', 'to_device']),
        ]
        constraints = [
            gis_models.UniqueConstraint(fields=['company', 'name'], name='uq_fiber_route_company_name'),
        ]

    def __str__(self) -> str:
        return self.name
