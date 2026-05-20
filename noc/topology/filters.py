from django_filters import rest_framework as filters

from .models import FiberRoute


class FiberRouteFilter(filters.FilterSet):
    route_type = filters.CharFilter(field_name='route_type')
    status = filters.CharFilter(field_name='status')
    from_device_id = filters.UUIDFilter(field_name='from_device_id')
    to_device_id = filters.UUIDFilter(field_name='to_device_id')
    min_capacity = filters.NumberFilter(field_name='capacity_gbps', lookup_expr='gte')
    max_capacity = filters.NumberFilter(field_name='capacity_gbps', lookup_expr='lte')

    class Meta:
        model = FiberRoute
        fields = ['route_type', 'status', 'from_device_id', 'to_device_id']
