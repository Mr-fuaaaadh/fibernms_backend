from __future__ import annotations

import hashlib
import hmac
import json
import urllib.request
from typing import Any

from django.utils import timezone

from .models import APIKey, Integration, WebhookSubscription


def deliver_webhook(*, company_id: str, target_url: str, secret_token: str, payload: dict[str, Any]) -> None:
    body = json.dumps(payload).encode('utf-8')
    headers = {'Content-Type': 'application/json'}
    if secret_token:
        signature = hmac.new(secret_token.encode('utf-8'), body, hashlib.sha256).hexdigest()
        headers['X-FiberNMS-Signature'] = signature
    req = urllib.request.Request(target_url, data=body, headers=headers, method='POST')
    urllib.request.urlopen(req, timeout=10)  # nosec - used for outgoing integrations


def send_slack_message(*, company_id: str, params: dict[str, Any], event) -> None:
    integration = Integration.objects.filter(company_id=company_id, service_name='slack', is_active=True).first()
    if not integration:
        return
    cfg = integration.get_config()
    webhook_url = cfg.get('webhook_url')
    if not webhook_url:
        return
    text = params.get('text') or f'FiberNMS event: {event.name}'
    deliver_webhook(company_id=company_id, target_url=webhook_url, secret_token='', payload={'text': text, 'event': event.payload})


def deliver_subscribed_webhooks(*, company_id: str, event_name: str, payload: dict[str, Any]) -> int:
    hooks = WebhookSubscription.objects.filter(company_id=company_id, is_active=True)
    sent = 0
    for hook in hooks:
        if hook.events and event_name not in hook.events:
            continue
        deliver_webhook(
            company_id=company_id,
            target_url=hook.target_url,
            secret_token=hook.get_secret(),
            payload={'event': event_name, 'data': payload},
        )
        sent += 1
    return sent


def create_api_key(*, company_id: str, name: str, scopes: list[str], expires_at=None) -> tuple[APIKey, str]:
    plain = APIKey.generate_plaintext_key()
    obj = APIKey.objects.create(
        company_id=company_id,
        name=name,
        key_prefix=APIKey.build_prefix(plain),
        key_hash=APIKey.hash_key(plain),
        scopes=scopes or [],
        expires_at=expires_at,
    )
    return obj, plain


def mark_api_key_used(*, api_key: APIKey) -> None:
    api_key.last_used_at = timezone.now()
    api_key.save(update_fields=['last_used_at'])

