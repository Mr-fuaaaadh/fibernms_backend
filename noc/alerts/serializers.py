from rest_framework import serializers

from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = (
            'id',
            'company',
            'severity',
            'type',
            'device',
            'route',
            'message',
            'details',
            'affected_customers',
            'status',
            'timestamp',
            'acknowledged_at',
            'acknowledged_by',
            'resolved_at',
            'resolved_by',
        )
        read_only_fields = ('company', 'timestamp', 'acknowledged_at', 'acknowledged_by', 'resolved_at', 'resolved_by')
