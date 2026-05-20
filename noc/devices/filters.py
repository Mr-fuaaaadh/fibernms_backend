from django_filters import rest_framework as filters

from .models import Device


class DeviceFilter(filters.FilterSet):
    type = filters.CharFilter(field_name='type')
    status = filters.CharFilter(field_name='status')
    region = filters.CharFilter(field_name='region', lookup_expr='iexact')
    parent_id = filters.UUIDFilter(field_name='parent_id')
    last_seen_after = filters.IsoDateTimeFilter(field_name='last_seen', lookup_expr='gte')
    last_seen_before = filters.IsoDateTimeFilter(field_name='last_seen', lookup_expr='lte')

    class Meta:
        model = Device
        fields = ['type', 'status', 'region', 'parent_id']
