from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import TelemetryReading


def bulk_ingest_telemetry(*, company_id, payload: list[dict]) -> int:
    rows = [
        TelemetryReading(
            company_id=company_id,
            timestamp=item['timestamp'],
            device_id=item['device'],
            parameter=item['parameter'],
            value=item['value'],
        )
        for item in payload
    ]
    created = TelemetryReading.objects.bulk_create(rows, batch_size=1000)
    return len(created)


def broadcast_telemetry_event(*, company_id, payload: dict) -> None:
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    async_to_sync(channel_layer.group_send)(
        f'telemetry_company_{company_id}',
        {
            'type': 'telemetry.message',
            'event': 'telemetry_ingested',
            'payload': payload,
        },
    )
