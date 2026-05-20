from celery import shared_task
from datetime import timedelta
from django.utils import timezone

from noc.alerts.tasks import generate_alert_task
from noc.workflows.tasks import dispatch_event_task
from .models import TelemetryReading
from .services import broadcast_telemetry_event, bulk_ingest_telemetry


THRESHOLDS = {
    'rx_power': {'op': 'lt', 'value': -25, 'severity': 'high'},
    'packet_loss': {'op': 'gt', 'value': 10, 'severity': 'critical'},
    'temperature': {'op': 'gt', 'value': 70, 'severity': 'medium'},
}


@shared_task
def process_telemetry_batch_task(*, company_id: str, payload: list[dict]):
    count = bulk_ingest_telemetry(company_id=company_id, payload=payload)
    evaluate_thresholds_task.delay(company_id=company_id, payload=payload)
    broadcast_telemetry_event(company_id=company_id, payload={'count': count})
    return count


@shared_task
def evaluate_thresholds_task(*, company_id: str, payload: list[dict]):
    alerts_created = 0
    for item in payload:
        rule = THRESHOLDS.get(item['parameter'])
        if not rule:
            continue
        val = float(item['value'])
        breached = (rule['op'] == 'lt' and val < rule['value']) or (rule['op'] == 'gt' and val > rule['value'])
        if not breached:
            continue
        dispatch_event_task.delay(
            company_id=company_id,
            name='telemetry.threshold_breach',
            payload={'device_id': item['device'], 'parameter': item['parameter'], 'value': val, 'threshold': rule['value']},
            triggered_by='telemetry',
        )
        generate_alert_task.delay(
            company_id=company_id,
            severity=rule['severity'],
            alert_type='threshold_breach',
            message=f"{item['parameter']} threshold breached on device {item['device']}",
            details={'parameter': item['parameter'], 'value': val, 'threshold': rule['value']},
            device_id=item['device'],
        )
        alerts_created += 1
    return alerts_created


@shared_task
def cleanup_old_telemetry_task(*, days: int = 30):
    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = TelemetryReading.objects.filter(timestamp__lt=cutoff).delete()
    return deleted
