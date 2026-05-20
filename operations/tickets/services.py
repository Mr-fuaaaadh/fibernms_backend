from __future__ import annotations

from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from operations.audit import record_operation_audit
from operations.incidents.services import select_assignment

from .models import Ticket, TicketComment


PRIORITY_TARGETS = {
    Ticket.Priority.P1: {'response': 15, 'resolution': 240},
    Ticket.Priority.P2: {'response': 30, 'resolution': 480},
    Ticket.Priority.P3: {'response': 120, 'resolution': 1440},
    Ticket.Priority.P4: {'response': 240, 'resolution': 4320},
}


def next_ticket_number(company_id) -> str:
    count = Ticket.objects.filter(company_id=company_id).count() + 1
    return f'TKT-{count:08d}'


@transaction.atomic
def create_ticket(*, company_id, actor, data: dict) -> Ticket:
    data = dict(data)
    requested_team = data.pop('assigned_team', None)
    requested_engineer = data.pop('assigned_to', None)
    team, engineer = select_assignment(company_id=company_id, severity='sev1' if data.get('priority') == Ticket.Priority.P1 else 'sev3')
    targets = PRIORITY_TARGETS.get(data.get('priority', Ticket.Priority.P3), PRIORITY_TARGETS[Ticket.Priority.P3])
    now = timezone.now()
    ticket = Ticket.objects.create(
        company_id=company_id,
        ticket_number=next_ticket_number(company_id),
        created_by=actor if getattr(actor, 'is_authenticated', False) else None,
        assigned_team=requested_team or team,
        assigned_to=requested_engineer or engineer,
        response_due_at=now + timedelta(minutes=targets['response']),
        resolution_due_at=now + timedelta(minutes=targets['resolution']),
        **data,
    )
    record_operation_audit(company_id=company_id, actor=actor, action='ticket.created', target=ticket)
    return ticket


def add_ticket_comment(*, ticket: Ticket, actor, body: str, is_internal: bool = True) -> TicketComment:
    comment = TicketComment.objects.create(
        company=ticket.company,
        ticket=ticket,
        author=actor if getattr(actor, 'is_authenticated', False) else None,
        body=body,
        is_internal=is_internal,
    )
    record_operation_audit(company_id=ticket.company_id, actor=actor, action='ticket.comment_added', target=ticket, metadata={'comment_id': str(comment.id)})
    return comment
