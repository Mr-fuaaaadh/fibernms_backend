from rest_framework import serializers

from .models import MaintenanceWindow


class MaintenanceWindowSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceWindow
        fields = '__all__'
        read_only_fields = ('company', 'requested_by', 'approved_by', 'approved_at', 'notification_sent_at', 'created_at', 'updated_at')

