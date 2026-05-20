from __future__ import annotations

from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from noc.workflows.tasks import dispatch_event_task
from operations.audit import record_operation_audit
from operations.sla.services import start_incident_sla_timer

from .models import Incident, IncidentTimelineEvent


SEVERITY_MATRIX = {
    Incident.Severity.SEV1: {'response_minutes': 15, 'resolution_minutes': 240, 'escalation_minutes': 15},
    Incident.Severity.SEV2: {'response_minutes': 30, 'resolution_minutes': 480, 'escalation_minutes': 30},
    Incident.Severity.SEV3: {'response_minutes': 120, 'resolution_minutes': 1440, 'escalation_minutes': 120},
    Incident.Severity.SEV4: {'response_minutes': 240, 'resolution_minutes': 4320, 'escalation_minutes': 240},
}


def next_incident_number(company_id) -> str:
    count = Incident.objects.filter(company_id=company_id).count() + 1
    return f'INC-{count:08d}'


def select_assignment(*, company_id, severity: str):
    from operations.workforce.models import EngineerProfile, EngineerTeam

    team_type = EngineerTeam.TeamType.NOC if severity in {Incident.Severity.SEV1, Incident.Severity.SEV2} else EngineerTeam.TeamType.FIELD
    team = EngineerTeam.objects.filter(company_id=company_id, team_type=team_type, is_active=True).first()
    engineer = (
        EngineerProfile.objects.filter(company_id=company_id, availability=EngineerProfile.Availability.AVAILABLE)
        .annotate(open_incidents=Count('user__assigned_incidents'))
        .order_by('current_load', 'open_incidents')
        .select_related('user')
        .first()
    )
    return team, engineer.user if engineer else None


def add_timeline_event(*, incident: Incident, event_type: str, message: str, actor=None, metadata: dict | None = None):
    return IncidentTimelineEvent.objects.create(
        company=incident.company,
        incident=incident,
        event_type=event_type,
        message=message,
        actor=actor if getattr(actor, 'is_authenticated', False) else None,
        metadata=metadata or {},
    )


@transaction.atomic
def create_incident(*, company_id, actor, data: dict) -> Incident:
    data = dict(data)
    requested_team = data.pop('assigned_team', None)
    requested_engineer = data.pop('assigned_to', None)
    outage_started_at = data.pop('outage_started_at', None)
    team, engineer = select_assignment(company_id=company_id, severity=data['severity'])
    incident = Incident.objects.create(
        company_id=company_id,
        incident_number=next_incident_number(company_id),
        created_by=actor if getattr(actor, 'is_authenticated', False) else None,
        assigned_team=requested_team or team,
        assigned_to=requested_engineer or engineer,
        outage_started_at=outage_started_at or timezone.now(),
        **data,
    )
    add_timeline_event(incident=incident, event_type='created', message='Incident created', actor=actor)
    if incident.assigned_to_id or incident.assigned_team_id:
        add_timeline_event(
            incident=incident,
            event_type='assigned',
            message='Incident assigned by routing engine',
            actor=actor,
            metadata={'assigned_to': str(incident.assigned_to_id or ''), 'assigned_team': str(incident.assigned_team_id or '')},
        )
    start_incident_sla_timer(incident=incident)
    record_operation_audit(company_id=company_id, actor=actor, action='incident.created', target=incident)
    dispatch_event_task.delay(
        company_id=str(company_id),
        name='incident.created',
        payload={'incident_id': str(incident.id), 'severity': incident.severity, 'status': incident.status},
        triggered_by='api',
    )
    return incident


@transaction.atomic
def transition_incident(*, incident: Incident, status: str, actor=None, rca_summary: str = '') -> Incident:
    old_status = incident.status
    incident.status = status
    now = timezone.now()
    update_fields = ['status', 'updated_at']
    if status == Incident.Status.MITIGATED:
        incident.mitigated_at = now
        update_fields.append('mitigated_at')
    if status == Incident.Status.RESOLVED:
        incident.resolved_at = now
        incident.outage_ended_at = incident.outage_ended_at or now
        update_fields.extend(['resolved_at', 'outage_ended_at'])
    if status == Incident.Status.CLOSED:
        incident.closed_at = now
        update_fields.append('closed_at')
    if rca_summary:
        incident.rca_summary = rca_summary
        incident.rca_completed_at = now
        update_fields.extend(['rca_summary', 'rca_completed_at'])
    incident.save(update_fields=update_fields)
    add_timeline_event(
        incident=incident,
        event_type='status_changed',
        message=f'Incident moved from {old_status} to {status}',
        actor=actor,
        metadata={'old_status': old_status, 'new_status': status},
    )
    record_operation_audit(company_id=incident.company_id, actor=actor, action='incident.status_changed', target=incident, metadata={'old_status': old_status, 'new_status': status})
    return incident
