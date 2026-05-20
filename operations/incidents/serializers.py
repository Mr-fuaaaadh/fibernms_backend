from rest_framework import serializers

from .models import Incident, IncidentTimelineEvent


class IncidentTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncidentTimelineEvent
        fields = ('id', 'event_type', 'message', 'metadata', 'actor', 'created_at')
        read_only_fields = fields


class IncidentSerializer(serializers.ModelSerializer):
    timeline = IncidentTimelineEventSerializer(many=True, read_only=True)

    class Meta:
        model = Incident
        fields = (
            'id', 'company', 'incident_number', 'title', 'description', 'severity', 'status', 'impact',
            'affected_customers', 'affected_services', 'device', 'customer', 'assigned_team', 'assigned_to',
            'rca_summary', 'rca_completed_at', 'outage_started_at', 'outage_ended_at', 'detected_at',
            'mitigated_at', 'resolved_at', 'closed_at', 'created_by', 'created_at', 'updated_at', 'timeline',
        )
        read_only_fields = (
            'company', 'incident_number', 'status', 'rca_completed_at', 'detected_at', 'mitigated_at',
            'resolved_at', 'closed_at', 'created_by', 'created_at', 'updated_at', 'timeline',
        )


class IncidentTransitionSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Incident.Status.choices)
    rca_summary = serializers.CharField(required=False, allow_blank=True)

