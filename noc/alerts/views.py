from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Alert
from .selectors import alerts_for_company
from .serializers import AlertSerializer
from .services import acknowledge_alert, broadcast_alert_event, resolve_alert
from noc.workflows.tasks import dispatch_event_task


class AlertViewSet(viewsets.ModelViewSet):
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['severity', 'status', 'type', 'device']
    search_fields = ['message']
    ordering_fields = ['timestamp', 'severity', 'affected_customers']
    ordering = ['-timestamp']

    def get_queryset(self):
        return alerts_for_company(company_id=self.request.user.company_id)

    def perform_create(self, serializer):
        alert = serializer.save(company_id=self.request.user.company_id)
        broadcast_alert_event(alert=alert, event='created')
        dispatch_event_task.delay(
            company_id=str(self.request.user.company_id),
            name='alert.created',
            payload={'alert_id': str(alert.id), 'severity': alert.severity, 'type': alert.type},
            triggered_by='api',
        )

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        acknowledge_alert(alert=alert, user=request.user)
        return Response(self.get_serializer(alert).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        resolve_alert(alert=alert, user=request.user)
        return Response(self.get_serializer(alert).data, status=status.HTTP_200_OK)
from django.shortcuts import render

# Create your views here.
