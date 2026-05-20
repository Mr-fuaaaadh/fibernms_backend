from django.db.models import QuerySet

from .models import Alert


def alerts_for_company(*, company_id) -> QuerySet[Alert]:
    return Alert.objects.filter(company_id=company_id).select_related('device', 'route')
