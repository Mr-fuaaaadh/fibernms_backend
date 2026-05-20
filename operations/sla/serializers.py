from rest_framework import serializers

from .models import SLAMetricSnapshot, SLAProfile, SLATimer


class SLAProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SLAProfile
        fields = '__all__'
        read_only_fields = ('company', 'created_at', 'updated_at')


class SLAMetricSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = SLAMetricSnapshot
        fields = '__all__'
        read_only_fields = ('company', 'is_breached', 'breach_reasons', 'created_at')


class SLATimerSerializer(serializers.ModelSerializer):
    class Meta:
        model = SLATimer
        fields = '__all__'
        read_only_fields = ('company', 'started_at', 'stopped_at', 'breach_notified_at')

