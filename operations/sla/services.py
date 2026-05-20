from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from noc.workflows.tasks import dispatch_event_task
from operations.audit import record_operation_audit

from .models import SLAMetricSnapshot, SLAProfile, SLATimer


def start_incident_sla_timer(*, incident):
    profile = SLAProfile.objects.filter(company=incident.company, is_active=True).filter(
        customer=incident.customer
    ).first()
    minutes = profile.response_time_minutes_target if profile else {'sev1': 15, 'sev2': 30, 'sev3': 120, 'sev4': 240}.get(incident.severity, 120)
    timer = SLATimer.objects.create(
        company=incident.company,
        profile=profile,
        target_type=SLATimer.TargetType.INCIDENT,
        target_id=incident.id,
        metric='response_time',
        due_at=timezone.now() + timedelta(minutes=minutes),
    )
    record_operation_audit(company_id=incident.company_id, action='sla.timer_started', target=timer, metadata={'incident_id': str(incident.id)})
    return timer


def evaluate_sla_snapshot(*, snapshot: SLAMetricSnapshot) -> SLAMetricSnapshot:
    profile = snapshot.profile
    reasons = []
    if snapshot.uptime_percent < profile.uptime_target:
        reasons.append('uptime')
    if snapshot.mttr_minutes > profile.mttr_minutes_target:
        reasons.append('mttr')
    if snapshot.mtbf_hours < profile.mtbf_hours_target:
        reasons.append('mtbf')
    if snapshot.packet_loss_percent > profile.packet_loss_target:
        reasons.append('packet_loss')
    if snapshot.latency_ms > profile.latency_ms_target:
        reasons.append('latency')
    if snapshot.response_time_minutes > profile.response_time_minutes_target:
        reasons.append('response_time')
    snapshot.is_breached = bool(reasons)
    snapshot.breach_reasons = reasons
    snapshot.save(update_fields=['is_breached', 'breach_reasons'])
    if reasons:
        dispatch_event_task.delay(
            company_id=str(snapshot.company_id),
            name='sla.violation',
            payload={'snapshot_id': str(snapshot.id), 'profile_id': str(profile.id), 'reasons': reasons},
            triggered_by='sla-engine',
        )
        record_operation_audit(company_id=snapshot.company_id, action='sla.breached', target=snapshot, metadata={'reasons': reasons})
    return snapshot


def breach_due_timers(*, company_id=None):
    qs = SLATimer.objects.filter(status=SLATimer.Status.RUNNING, due_at__lte=timezone.now())
    if company_id:
        qs = qs.filter(company_id=company_id)
    breached = []
    for timer in qs:
        timer.status = SLATimer.Status.BREACHED
        timer.breach_notified_at = timezone.now()
        timer.save(update_fields=['status', 'breach_notified_at'])
        dispatch_event_task.delay(
            company_id=str(timer.company_id),
            name='sla.violation',
            payload={'timer_id': str(timer.id), 'target_type': timer.target_type, 'target_id': str(timer.target_id)},
            triggered_by='sla-engine',
        )
        record_operation_audit(company_id=timer.company_id, action='sla.timer_breached', target=timer)
        breached.append(timer)
    return breached

