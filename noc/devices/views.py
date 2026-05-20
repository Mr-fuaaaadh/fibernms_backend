from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import DeviceFilter
from .selectors import (
    device_queryset_for_company,
    devices_within_polygon_queryset,
    nearby_devices_queryset,
)
from .serializers import DeviceGeoSerializer
from .services import get_downstream_devices, get_topology_tree


class DeviceViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceGeoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = DeviceFilter
    search_fields = ['name', 'region', 'metadata']
    ordering_fields = ['name', 'last_seen', 'created_at', 'updated_at']
    ordering = ['name']

    def get_queryset(self):
        return device_queryset_for_company(company_id=self.request.user.company_id)

    def perform_create(self, serializer):
        serializer.save(company_id=self.request.user.company_id)

    @action(detail=False, methods=['get'], url_path='nearby')
    def nearby(self, request):
        try:
            lat = float(request.query_params.get('lat', ''))
            lon = float(request.query_params.get('lon', ''))
            radius = float(request.query_params.get('radius_m', '1000'))
        except ValueError:
            return Response({'detail': 'lat, lon and radius_m must be numeric.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = nearby_devices_queryset(
            company_id=request.user.company_id,
            latitude=lat,
            longitude=lon,
            radius_meters=radius,
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['post'], url_path='within-polygon')
    def within_polygon(self, request):
        polygon_geojson = request.data.get('polygon')
        if not polygon_geojson:
            return Response({'detail': 'polygon is required.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = devices_within_polygon_queryset(
            company_id=request.user.company_id,
            polygon_geojson=polygon_geojson,
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=True, methods=['get'], url_path='downstream')
    def downstream(self, request, pk=None):
        device = self.get_object()
        descendants = get_downstream_devices(root_device=device)
        serializer = self.get_serializer(descendants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='topology-tree')
    def topology_tree(self, request, pk=None):
        device = self.get_object()
        return Response(get_topology_tree(root_device=device))
from django.shortcuts import render

# Create your views here.
