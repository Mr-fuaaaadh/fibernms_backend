from celery import shared_task
from django.utils import timezone

from .models import Alert
from .services import broadcast_alert_event
from noc.workflows.tasks import dispatch_event_task


@shared_task
def generate_alert_task(*, company_id: str, severity: str, alert_type: str, message: str, details: dict, device_id=None, route_id=None):
    alert = Alert.objects.create(
        company_id=company_id,
        severity=severity,
        type=alert_type,
        message=message,
        details=details or {},
        device_id=device_id,
        route_id=route_id,
    )
    broadcast_alert_event(alert=alert, event='created')
    dispatch_event_task.delay(company_id=company_id, name='alert.created', payload={'alert_id': str(alert.id), 'severity': alert.severity, 'type': alert.type})
    if alert.severity == Alert.Severity.CRITICAL:
        dispatch_event_task.delay(company_id=company_id, name='alert.critical', payload={'alert_id': str(alert.id)})
    return str(alert.id)


@shared_task
def calculate_sla_metrics_task(*, company_id: str):
    now = timezone.now()
    open_critical = Alert.objects.filter(
        company_id=company_id,
        severity=Alert.Severity.CRITICAL,
        status=Alert.Status.OPEN,
    ).count()
    return {
        'company_id': company_id,
        'generated_at': now.isoformat(),
        'open_critical_alerts': open_critical,
    }
