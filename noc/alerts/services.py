from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from .models import Alert


def broadcast_alert_event(*, alert: Alert, event: str) -> None:
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        f'alerts_company_{alert.company_id}',
        {
            'type': 'alert.message',
            'event': event,
            'payload': {
                'id': str(alert.id),
                'severity': alert.severity,
                'type': alert.type,
                'status': alert.status,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'device_id': str(alert.device_id) if alert.device_id else None,
                'route_id': str(alert.route_id) if alert.route_id else None,
            },
        },
    )


def acknowledge_alert(*, alert: Alert, user) -> Alert:
    alert.status = Alert.Status.ACKNOWLEDGED
    alert.acknowledged_at = timezone.now()
    alert.acknowledged_by = user
    alert.save(update_fields=['status', 'acknowledged_at', 'acknowledged_by'])
    broadcast_alert_event(alert=alert, event='acknowledged')
    return alert


def resolve_alert(*, alert: Alert, user) -> Alert:
    alert.status = Alert.Status.RESOLVED
    alert.resolved_at = timezone.now()
    alert.resolved_by = user
    alert.save(update_fields=['status', 'resolved_at', 'resolved_by'])
    broadcast_alert_event(alert=alert, event='resolved')
    return alert
