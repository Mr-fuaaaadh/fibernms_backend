from __future__ import annotations

import time

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from .engine import WorkflowEngine, WorkflowEvent
from .executors import ActionExecutor
from .models import Workflow, WorkflowRun


def broadcast_workflow_run(*, run: WorkflowRun, event: str) -> None:
    layer = get_channel_layer()
    if not layer:
        return
    async_to_sync(layer.group_send)(
        f'workflow_runs_company_{run.company_id}',
        {
            'type': 'workflow_run.message',
            'event': event,
            'payload': {
                'id': str(run.id),
                'workflow_id': str(run.workflow_id),
                'status': run.status,
                'event_name': run.event_name,
                'started_at': run.started_at.isoformat(),
                'finished_at': run.finished_at.isoformat() if run.finished_at else None,
                'execution_time_ms': run.execution_time_ms,
            },
        },
    )


def execute_workflow(*, workflow: Workflow, event: WorkflowEvent) -> WorkflowRun:
    run = WorkflowRun.objects.create(
        workflow=workflow,
        company_id=workflow.company_id,
        status=WorkflowRun.Status.RUNNING,
        triggered_by=event.triggered_by,
        event_name=event.name,
        event_payload=event.payload,
    )
    broadcast_workflow_run(run=run, event='started')

    started = time.perf_counter()
    engine = WorkflowEngine(action_executor=ActionExecutor())

    try:
        logs = engine.run(workflow=workflow, event=event)
        run.logs = logs
        run.status = WorkflowRun.Status.SUCCESS
    except Exception as exc:
        run.logs = [{'error': str(exc)}]
        run.status = WorkflowRun.Status.FAILED
    finally:
        run.finished_at = timezone.now()
        run.execution_time_ms = int((time.perf_counter() - started) * 1000)
        run.save(update_fields=['status', 'logs', 'finished_at', 'execution_time_ms'])
        broadcast_workflow_run(run=run, event='finished')

    return run

