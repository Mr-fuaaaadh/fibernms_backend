from django.test import TestCase

from operations.escalations.models import EscalationEvent, EscalationPolicy
from operations.escalations.services import escalate_target
from operations.tickets.models import Ticket
from operations.workforce.models import EngineerTeam
from saas.companies.models import Company


class EscalationEngineTests(TestCase):
    def test_ticket_escalation_uses_policy_and_marks_ticket(self):
        company = Company.objects.create(name='FiberCo', contact_email='esc@example.com', region='IN')
        noc = EngineerTeam.objects.create(company=company, name='NOC L2', team_type=EngineerTeam.TeamType.NOC)
        EscalationPolicy.objects.create(
            company=company,
            name='P1 Ticket Policy',
            target_type=EscalationPolicy.TargetType.TICKET,
            severity=Ticket.Priority.P1,
            noc_team=noc,
        )
        ticket = Ticket.objects.create(company=company, ticket_number='TKT-00000001', subject='LOS alarm', priority=Ticket.Priority.P1)

        event = escalate_target(target=ticket, reason='Response timer exceeded')
        ticket.refresh_from_db()

        self.assertEqual(event.level, EscalationEvent.Level.NOC)
        self.assertEqual(event.assigned_team, noc)
        self.assertEqual(ticket.status, Ticket.Status.ESCALATED)
        self.assertIsNotNone(ticket.escalated_at)
