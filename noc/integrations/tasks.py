from celery import shared_task

from .services import deliver_subscribed_webhooks


@shared_task(bind=True, max_retries=5, default_retry_delay=10)
def deliver_webhooks_task(self, *, company_id: str, event_name: str, payload: dict):
    return deliver_subscribed_webhooks(company_id=company_id, event_name=event_name, payload=payload)

