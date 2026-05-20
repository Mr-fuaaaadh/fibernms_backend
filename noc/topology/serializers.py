from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers

try:
    from rest_framework_gis.serializers import GeoFeatureModelSerializer
except ImproperlyConfigured:
    class GeoFeatureModelSerializer(serializers.ModelSerializer):
        pass

from .models import FiberRoute


class FiberRouteGeoSerializer(GeoFeatureModelSerializer):
    from_device_id = serializers.UUIDField(read_only=True)
    to_device_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = FiberRoute
        if hasattr(GeoFeatureModelSerializer, 'Meta'):
            geo_field = 'geometry'
            id_field = False
        fields = (
            'id',
            'company',
            'name',
            'route_type',
            'status',
            'from_device',
            'to_device',
            'from_device_id',
            'to_device_id',
            'length_meters',
            'attenuation_db_km',
            'capacity_gbps',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('company', 'length_meters', 'created_at', 'updated_at')
