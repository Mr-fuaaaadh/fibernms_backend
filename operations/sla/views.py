from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SLAMetricSnapshot, SLAProfile, SLATimer
from .serializers import SLAMetricSnapshotSerializer, SLAProfileSerializer, SLATimerSerializer
from .services import breach_due_timers, evaluate_sla_snapshot


class SLAProfileViewSet(viewsets.ModelViewSet):
    serializer_class = SLAProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SLAProfile.objects.filter(company_id=self.request.user.company_id)

    def perform_create(self, serializer):
        serializer.save(company_id=self.request.user.company_id)


class SLAMetricSnapshotViewSet(viewsets.ModelViewSet):
    serializer_class = SLAMetricSnapshotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SLAMetricSnapshot.objects.filter(company_id=self.request.user.company_id).select_related('profile')

    def perform_create(self, serializer):
        snapshot = serializer.save(company_id=self.request.user.company_id)
        evaluate_sla_snapshot(snapshot=snapshot)


class SLATimerViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SLATimerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SLATimer.objects.filter(company_id=self.request.user.company_id).select_related('profile')

    @action(detail=False, methods=['post'])
    def breach_due(self, request):
        timers = breach_due_timers(company_id=request.user.company_id)
        return Response({'breached': len(timers)})

