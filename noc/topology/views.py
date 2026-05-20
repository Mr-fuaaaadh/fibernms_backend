from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters as drf_filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import FiberRouteFilter
from .selectors import annotate_route_lengths, fiber_route_queryset_for_company, fiber_routes_touching_device
from .serializers import FiberRouteGeoSerializer
from .services import sync_fiber_route_length


class FiberRouteViewSet(viewsets.ModelViewSet):
    serializer_class = FiberRouteGeoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = FiberRouteFilter
    search_fields = ['name']
    ordering_fields = ['name', 'length_meters', 'capacity_gbps', 'created_at', 'updated_at']
    ordering = ['name']

    def get_queryset(self):
        return fiber_route_queryset_for_company(company_id=self.request.user.company_id)

    def perform_create(self, serializer):
        route = serializer.save(company_id=self.request.user.company_id)
        sync_fiber_route_length(route=route)

    def perform_update(self, serializer):
        route = serializer.save()
        sync_fiber_route_length(route=route)

    @action(detail=False, methods=['get'], url_path='near-point')
    def near_point(self, request):
        try:
            lat = float(request.query_params.get('lat', ''))
            lon = float(request.query_params.get('lon', ''))
            radius = float(request.query_params.get('radius_m', '1000'))
        except ValueError:
            return Response({'detail': 'lat, lon and radius_m must be numeric.'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = fiber_routes_touching_device(
            company_id=request.user.company_id,
            latitude=lat,
            longitude=lon,
            radius_meters=radius,
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            return self.get_paginated_response(self.get_serializer(page, many=True).data)
        return Response(self.get_serializer(queryset, many=True).data)

    @action(detail=False, methods=['get'], url_path='length-analysis')
    def length_analysis(self, request):
        queryset = annotate_route_lengths(queryset=self.get_queryset())
        data = [
            {
                'id': str(item.id),
                'name': item.name,
                'stored_length_meters': item.length_meters,
                'calculated_length_meters': item.calc_length_m.m if item.calc_length_m else None,
            }
            for item in queryset
        ]
        return Response(data)
from django.shortcuts import render

# Create your views here.
