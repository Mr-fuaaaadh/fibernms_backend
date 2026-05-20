from celery import shared_task

from .models import Workflow
from .services import execute_workflow
from .engine import WorkflowEvent


@shared_task(bind=True, max_retries=5, default_retry_delay=10)
def execute_workflow_task(self, *, workflow_id: str, event: dict):
    workflow = Workflow.objects.get(id=workflow_id, is_active=True)
    wf_event = WorkflowEvent(**event)
    execute_workflow(workflow=workflow, event=wf_event)


@shared_task
def dispatch_event_task(*, company_id: str, name: str, payload: dict, triggered_by: str = ''):
    workflows = Workflow.objects.filter(company_id=company_id, trigger_type=name, is_active=True).only('id')
    event = {
        'name': name,
        'company_id': company_id,
        'payload': payload,
        'triggered_by': triggered_by,
    }
    for wf in workflows:
        execute_workflow_task.delay(workflow_id=str(wf.id), event=event)

