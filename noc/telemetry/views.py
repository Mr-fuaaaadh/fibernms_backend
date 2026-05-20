from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .selectors import telemetry_for_company
from .serializers import TelemetryBulkIngestSerializer, TelemetryReadingSerializer
from .tasks import process_telemetry_batch_task


class TelemetryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TelemetryReadingSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.OrderingFilter]
    filterset_fields = ['device', 'parameter']
    ordering_fields = ['timestamp', 'created_at', 'value']
    ordering = ['-timestamp']

    def get_queryset(self):
        return telemetry_for_company(company_id=self.request.user.company_id)

    @action(detail=False, methods=['post'], url_path='ingest')
    def ingest(self, request):
        serializer = TelemetryBulkIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data['readings']
        process_telemetry_batch_task.delay(
            company_id=str(request.user.company_id),
            payload=payload,
        )
        return Response(
            {'success': True, 'message': 'Telemetry ingestion accepted', 'data': {'count': len(payload)}},
            status=status.HTTP_202_ACCEPTED,
        )
from django.shortcuts import render

# Create your views here.
