from rest_framework import serializers

from .models import Workflow, WorkflowRun


class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = (
            'id',
            'company',
            'name',
            'description',
            'trigger_type',
            'nodes',
            'edges',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('company', 'created_at', 'updated_at')


class WorkflowRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowRun
        fields = (
            'id',
            'workflow',
            'company',
            'status',
            'triggered_by',
            'event_name',
            'event_payload',
            'logs',
            'execution_time_ms',
            'started_at',
            'finished_at',
        )
        read_only_fields = (
            'company',
            'status',
            'logs',
            'execution_time_ms',
            'started_at',
            'finished_at',
        )

