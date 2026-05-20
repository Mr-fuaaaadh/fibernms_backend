from __future__ import annotations

from collections import deque

from django.db.models import QuerySet

from .models import Device


def get_downstream_devices(*, root_device: Device) -> list[Device]:
    """
    Iterative BFS traversal to avoid recursion-depth issues
    on large telecom topologies.
    """
    descendants: list[Device] = []
    queue: deque[Device] = deque([root_device])

    while queue:
        node = queue.popleft()
        children = list(node.children.all().order_by('name'))
        descendants.extend(children)
        queue.extend(children)

    return descendants


def get_topology_tree(*, root_device: Device) -> dict:
    def build(node: Device) -> dict:
        children = list(node.children.all().order_by('name'))
        return {
            'id': str(node.id),
            'name': node.name,
            'type': node.type,
            'status': node.status,
            'children': [build(child) for child in children],
        }

    return build(root_device)


def outage_impact_queryset(*, root_device: Device) -> QuerySet[Device]:
    downstream_ids = [device.id for device in get_downstream_devices(root_device=root_device)]
    return Device.objects.filter(id__in=downstream_ids)
