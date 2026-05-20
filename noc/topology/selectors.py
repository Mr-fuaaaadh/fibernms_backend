from __future__ import annotations

from django.db.models import QuerySet

from .models import FiberRoute


def fiber_route_queryset_for_company(*, company_id) -> QuerySet[FiberRoute]:
    return FiberRoute.objects.filter(company_id=company_id).select_related('from_device', 'to_device', 'company')


def fiber_routes_touching_device(*, company_id, latitude: float, longitude: float, radius_meters: float) -> QuerySet[FiberRoute]:
    from django.contrib.gis.geos import Point

    point = Point(longitude, latitude, srid=4326)
    return fiber_route_queryset_for_company(company_id=company_id).filter(geometry__distance_lte=(point, radius_meters))


def annotate_route_lengths(*, queryset: QuerySet[FiberRoute]) -> QuerySet[FiberRoute]:
    from django.contrib.gis.db.models.functions import Length

    return queryset.annotate(calc_length_m=Length('geometry', spheroid=True))
