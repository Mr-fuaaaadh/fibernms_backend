from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from operations.incidents.models import Incident, IncidentTimelineEvent
from operations.sla.models import SLATimer
from saas.accounts.models import User
from saas.companies.models import Company


class IncidentLifecycleTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='FiberCo', contact_email='ops@example.com', region='IN')
        self.user = User.objects.create_user(username='noc', password='pass', company=self.company, role='operator')

    @patch('noc.workflows.tasks.dispatch_event_task.delay')
    def test_incident_creation_starts_timeline_and_sla_timer(self, _delay):
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        response = self.client.post('/api/v1/incidents/', {'title': 'OLT down', 'severity': Incident.Severity.SEV1}, format='json')

        self.assertEqual(response.status_code, 201)
        incident = Incident.objects.get()
        self.assertEqual(incident.status, Incident.Status.OPEN)
        self.assertEqual(IncidentTimelineEvent.objects.filter(incident=incident, event_type='created').count(), 1)
        self.assertEqual(SLATimer.objects.filter(target_id=incident.id, target_type='incident').count(), 1)

    @patch('noc.workflows.tasks.dispatch_event_task.delay')
    def test_incident_transition_records_resolution_and_rca(self, _delay):
        incident = Incident.objects.create(
            company=self.company,
            incident_number='INC-00000001',
            title='Packet loss',
            severity=Incident.Severity.SEV2,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        response = self.client.post(
            f'/api/v1/incidents/{incident.id}/transition/',
            {'status': Incident.Status.RESOLVED, 'rca_summary': 'Fiber attenuation corrected'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        incident.refresh_from_db()
        self.assertEqual(incident.status, Incident.Status.RESOLVED)
        self.assertIsNotNone(incident.resolved_at)
        self.assertIsNotNone(incident.outage_ended_at)
        self.assertEqual(incident.rca_summary, 'Fiber attenuation corrected')

