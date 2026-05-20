from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers

try:
    from rest_framework_gis.serializers import GeoFeatureModelSerializer
except ImproperlyConfigured:
    class GeoFeatureModelSerializer(serializers.ModelSerializer):
        pass

from .models import Device


class DeviceGeoSerializer(GeoFeatureModelSerializer):
    parent_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = Device
        if hasattr(GeoFeatureModelSerializer, 'Meta'):
            geo_field = 'location'
            id_field = False
        fields = (
            'id',
            'company',
            'name',
            'type',
            'status',
            'region',
            'uptime',
            'tx_power',
            'rx_power',
            'parent_id',
            'customer_count',
            'metadata',
            'last_seen',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('company', 'created_at', 'updated_at')
