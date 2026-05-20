from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from operations.audit import record_operation_audit

from .models import MaintenanceWindow
from .serializers import MaintenanceWindowSerializer


class MaintenanceWindowViewSet(viewsets.ModelViewSet):
    serializer_class = MaintenanceWindowSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['status', 'device']
    search_fields = ['title', 'description']
    ordering_fields = ['planned_start', 'planned_end', 'created_at']
    ordering = ['planned_start']

    def get_queryset(self):
        return MaintenanceWindow.objects.filter(company_id=self.request.user.company_id).select_related('device', 'requested_by', 'approved_by')

    def perform_create(self, serializer):
        window = serializer.save(company_id=self.request.user.company_id, requested_by=self.request.user)
        record_operation_audit(company_id=self.request.user.company_id, actor=self.request.user, action='maintenance.created', target=window)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        window = self.get_object()
        window.status = MaintenanceWindow.Status.PENDING_APPROVAL
        window.save(update_fields=['status', 'updated_at'])
        record_operation_audit(company_id=window.company_id, actor=request.user, action='maintenance.submitted', target=window)
        return Response(self.get_serializer(window).data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        window = self.get_object()
        window.status = MaintenanceWindow.Status.APPROVED
        window.approved_by = request.user
        window.approved_at = timezone.now()
        window.save(update_fields=['status', 'approved_by', 'approved_at', 'updated_at'])
        record_operation_audit(company_id=window.company_id, actor=request.user, action='maintenance.approved', target=window)
        return Response(self.get_serializer(window).data)

