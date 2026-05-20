from __future__ import annotations

from django.db.models import QuerySet

from .models import Device


def device_queryset_for_company(*, company_id) -> QuerySet[Device]:
    return Device.objects.filter(company_id=company_id).select_related('parent', 'company')


def nearby_devices_queryset(*, company_id, latitude: float, longitude: float, radius_meters: float) -> QuerySet[Device]:
    from django.contrib.gis.db.models.functions import Distance
    from django.contrib.gis.geos import Point

    origin = Point(longitude, latitude, srid=4326)
    return (
        device_queryset_for_company(company_id=company_id)
        .filter(location__distance_lte=(origin, radius_meters))
        .annotate(distance_m=Distance('location', origin))
        .order_by('distance_m')
    )


def devices_within_polygon_queryset(*, company_id, polygon_geojson: str) -> QuerySet[Device]:
    from django.contrib.gis.geos import GEOSGeometry

    polygon = GEOSGeometry(polygon_geojson, srid=4326)
    return device_queryset_for_company(company_id=company_id).filter(location__within=polygon)
