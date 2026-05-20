from django.db.models import QuerySet

from .models import Workflow, WorkflowRun


def workflows_for_company(*, company_id) -> QuerySet[Workflow]:
    return Workflow.objects.filter(company_id=company_id)


def workflow_runs_for_company(*, company_id) -> QuerySet[WorkflowRun]:
    return WorkflowRun.objects.filter(company_id=company_id).select_related('workflow')

