from __future__ import annotations

from django.utils import timezone

from operations.audit import record_operation_audit
from operations.incidents.models import Incident
from operations.tickets.models import Ticket

from .models import EscalationEvent, EscalationPolicy


def find_policy(*, company_id, target_type: str, severity: str = ''):
    return EscalationPolicy.objects.filter(
        company_id=company_id,
        target_type=target_type,
        is_active=True,
    ).filter(severity__in=[severity, '']).order_by('-severity').first()


def escalate_target(*, target, reason: str, level=EscalationEvent.Level.NOC) -> EscalationEvent:
    if isinstance(target, Incident):
        target_type = EscalationPolicy.TargetType.INCIDENT
        severity = target.severity
    elif isinstance(target, Ticket):
        target_type = EscalationPolicy.TargetType.TICKET
        severity = target.priority
    else:
        target_type = EscalationPolicy.TargetType.SLA
        severity = ''
    policy = find_policy(company_id=target.company_id, target_type=target_type, severity=severity)
    assigned_team = policy.manager_team if policy and level == EscalationEvent.Level.MANAGER else policy.noc_team if policy else None
    event = EscalationEvent.objects.create(
        company_id=target.company_id,
        policy=policy,
        target_type=target_type,
        target_id=target.id,
        level=level,
        reason=reason,
        assigned_team=assigned_team,
    )
    if isinstance(target, Ticket):
        target.status = Ticket.Status.ESCALATED
        target.escalated_at = timezone.now()
        target.save(update_fields=['status', 'escalated_at', 'updated_at'])
    record_operation_audit(company_id=target.company_id, action='escalation.created', target=event, metadata={'target_id': str(target.id)})
    return event

