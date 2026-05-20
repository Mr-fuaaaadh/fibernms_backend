from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WorkflowEvent:
    name: str
    company_id: str
    payload: dict[str, Any]
    triggered_by: str = ''


class WorkflowEngine:
    """
    Minimal execution foundation.
    Nodes/edges are stored for visual builder compatibility (n8n-style).
    Execution uses a controlled action registry (executors) to avoid arbitrary code execution.
    """

    def __init__(self, *, action_executor):
        self.action_executor = action_executor

    def run(self, *, workflow, event: WorkflowEvent) -> list[dict[str, Any]]:
        logs: list[dict[str, Any]] = []
        for node in workflow.nodes or []:
            node_type = node.get('type')
            if node_type != 'action':
                continue
            action = node.get('action')
            params = node.get('params', {})
            result = self.action_executor.execute(action=action, params=params, event=event)
            logs.append({'node_id': node.get('id'), 'action': action, 'result': result})
        return logs

