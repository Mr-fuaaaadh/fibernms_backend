from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import APIKey, Integration, WebhookSubscription
from .serializers import APIKeySerializer, IntegrationSerializer, WebhookSerializer
from .services import create_api_key


class IntegrationViewSet(viewsets.ModelViewSet):
    serializer_class = IntegrationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = ['service_name', 'is_active']
    search_fields = ['service_name']

    def get_queryset(self):
        return Integration.objects.filter(company_id=self.request.user.company_id)

    def perform_create(self, serializer):
        serializer.save(company_id=self.request.user.company_id)


class WebhookViewSet(viewsets.ModelViewSet):
    serializer_class = WebhookSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']

    def get_queryset(self):
        return WebhookSubscription.objects.filter(company_id=self.request.user.company_id)

    def perform_create(self, serializer):
        serializer.save(company_id=self.request.user.company_id)


class APIKeyViewSet(viewsets.ModelViewSet):
    serializer_class = APIKeySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter]
    filterset_fields = []
    search_fields = ['name', 'key_prefix']

    def get_queryset(self):
        return APIKey.objects.filter(company_id=self.request.user.company_id).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        serializer = APIKeySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj, plain = create_api_key(
            company_id=str(request.user.company_id),
            name=serializer.validated_data['name'],
            scopes=serializer.validated_data.get('scopes') or [],
            expires_at=serializer.validated_data.get('expires_at'),
        )
        data = APIKeySerializer(obj).data
        data['plain_key'] = plain
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='rotate')
    def rotate(self, request, pk=None):
        old = self.get_object()
        obj, plain = create_api_key(
            company_id=str(request.user.company_id),
            name=f'{old.name} (rotated)',
            scopes=old.scopes or [],
            expires_at=old.expires_at,
        )
        data = APIKeySerializer(obj).data
        data['plain_key'] = plain
        return Response(data, status=status.HTTP_201_CREATED)

