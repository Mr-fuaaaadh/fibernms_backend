from __future__ import annotations

from typing import Any

from noc.integrations.services import deliver_webhook, send_slack_message

from .engine import WorkflowEvent


class ActionExecutor:
    """
    Enterprise-safe action registry.
    Add new connectors here (Jira/PagerDuty/etc) without changing engine logic.
    """

    def execute(self, *, action: str, params: dict[str, Any], event: WorkflowEvent) -> dict[str, Any]:
        if action == 'webhook.send':
            deliver_webhook(
                company_id=event.company_id,
                target_url=params['target_url'],
                secret_token=params.get('secret_token', ''),
                payload={'event': event.name, 'data': event.payload},
            )
            return {'ok': True}

        if action == 'slack.notify':
            send_slack_message(company_id=event.company_id, params=params, event=event)
            return {'ok': True}

        return {'ok': False, 'error': f'Unknown action: {action}'}

