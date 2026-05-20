from __future__ import annotations

from typing import Any

from django.contrib.contenttypes.models import ContentType


def record_operation_audit(*, company_id, actor=None, action: str, target: Any = None, metadata: dict | None = None) -> None:
    from saas.audit.models import AuditEvent

    content_type = None
    object_id = ''
    if target is not None:
        content_type = ContentType.objects.get_for_model(target.__class__)
        object_id = str(target.pk)

    AuditEvent.objects.create(
        company_id=company_id,
        actor=actor if getattr(actor, 'is_authenticated', False) else None,
        action=action,
        content_type=content_type,
        object_id=object_id,
        metadata=metadata or {},
    )

