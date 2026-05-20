from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from operations.sla.models import SLAMetricSnapshot, SLAProfile, SLATimer
from operations.sla.services import breach_due_timers, evaluate_sla_snapshot
from saas.companies.models import Company


class SLAEngineTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='FiberCo', contact_email='sla@example.com', region='IN')
        self.profile = SLAProfile.objects.create(
            company=self.company,
            name='Enterprise Gold',
            scope=SLAProfile.Scope.SERVICE,
            service_name='Internet DIA',
            uptime_target=99.90,
            latency_ms_target=50,
        )

    @patch('noc.workflows.tasks.dispatch_event_task.delay')
    def test_snapshot_marks_breach_reasons(self, _delay):
        snapshot = SLAMetricSnapshot.objects.create(
            company=self.company,
            profile=self.profile,
            period_start=timezone.now() - timedelta(hours=1),
            period_end=timezone.now(),
            uptime_percent=99.0,
            mttr_minutes=10,
            mtbf_hours=1000,
            packet_loss_percent=0.1,
            latency_ms=80,
            response_time_minutes=5,
        )

        evaluate_sla_snapshot(snapshot=snapshot)
        snapshot.refresh_from_db()
        self.assertTrue(snapshot.is_breached)
        self.assertEqual(snapshot.breach_reasons, ['uptime', 'latency'])

    @patch('noc.workflows.tasks.dispatch_event_task.delay')
    def test_due_timer_is_breached(self, _delay):
        timer = SLATimer.objects.create(
            company=self.company,
            profile=self.profile,
            target_type=SLATimer.TargetType.INCIDENT,
            target_id='00000000-0000-0000-0000-000000000001',
            metric='response_time',
            due_at=timezone.now() - timedelta(minutes=1),
        )

        breached = breach_due_timers(company_id=self.company.id)
        timer.refresh_from_db()
        self.assertEqual(len(breached), 1)
        self.assertEqual(timer.status, SLATimer.Status.BREACHED)

