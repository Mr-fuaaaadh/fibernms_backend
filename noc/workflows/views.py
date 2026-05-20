from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Workflow, WorkflowRun
from .selectors import workflow_runs_for_company, workflows_for_company
from .serializers import WorkflowRunSerializer, WorkflowSerializer
from .tasks import dispatch_event_task


class WorkflowViewSet(viewsets.ModelViewSet):
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['trigger_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['updated_at', 'created_at', 'name']
    ordering = ['-updated_at']

    def get_queryset(self):
        return workflows_for_company(company_id=self.request.user.company_id)

    def perform_create(self, serializer):
        serializer.save(company_id=self.request.user.company_id)

    @action(detail=True, methods=['post'], url_path='test-run')
    def test_run(self, request, pk=None):
        workflow: Workflow = self.get_object()
        dispatch_event_task.delay(
            company_id=str(request.user.company_id),
            name=workflow.trigger_type,
            payload=request.data.get('payload', {}),
            triggered_by='manual_test',
        )
        return Response({'success': True, 'message': 'Workflow dispatched'}, status=status.HTTP_202_ACCEPTED)


class WorkflowRunViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = WorkflowRunSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_fields = ['status', 'workflow', 'event_name']
    ordering_fields = ['started_at', 'finished_at', 'execution_time_ms']
    ordering = ['-started_at']

    def get_queryset(self):
        return workflow_runs_for_company(company_id=self.request.user.company_id)

