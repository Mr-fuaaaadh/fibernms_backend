from rest_framework import serializers

from .models import TelemetryReading


class TelemetryReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelemetryReading
        fields = ('id', 'timestamp', 'device', 'company', 'parameter', 'value', 'created_at')
        read_only_fields = ('company', 'created_at')


class TelemetryBulkIngestSerializer(serializers.Serializer):
    readings = TelemetryReadingSerializer(many=True)
