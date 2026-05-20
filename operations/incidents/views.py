from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Incident
from .serializers import IncidentSerializer, IncidentTransitionSerializer
from .services import create_incident, transition_incident


class IncidentViewSet(viewsets.ModelViewSet):
    serializer_class = IncidentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_fields = ['severity', 'status', 'assigned_team', 'assigned_to', 'customer', 'device']
    search_fields = ['incident_number', 'title', 'description', 'impact']
    ordering_fields = ['detected_at', 'updated_at', 'affected_customers', 'severity']
    ordering = ['-detected_at']

    def get_queryset(self):
        return Incident.objects.filter(company_id=self.request.user.company_id).select_related(
            'company', 'device', 'customer', 'assigned_team', 'assigned_to', 'created_by'
        ).prefetch_related('timeline')

    def perform_create(self, serializer):
        self.instance = create_incident(company_id=self.request.user.company_id, actor=self.request.user, data=serializer.validated_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(self.get_serializer(self.instance).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def transition(self, request, pk=None):
        serializer = IncidentTransitionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        incident = transition_incident(incident=self.get_object(), actor=request.user, **serializer.validated_data)
        return Response(self.get_serializer(incident).data)

