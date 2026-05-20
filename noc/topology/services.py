from __future__ import annotations

from django.db import transaction

from .models import FiberRoute


@transaction.atomic
def sync_fiber_route_length(*, route: FiberRoute) -> FiberRoute:
    """
    Keep denormalized length_meters updated from geometry.
    """
    if route.geometry:
        route.length_meters = route.geometry.length * 111_319.9
        route.save(update_fields=['length_meters', 'updated_at'])
    return route
