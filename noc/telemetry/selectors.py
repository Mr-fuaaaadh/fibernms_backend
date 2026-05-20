from django.db.models import QuerySet

from .models import TelemetryReading


def telemetry_for_company(*, company_id) -> QuerySet[TelemetryReading]:
    return TelemetryReading.objects.filter(company_id=company_id).select_related('device')
