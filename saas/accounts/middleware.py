from django.db import connection
from django.utils.deprecation import MiddlewareMixin


class TenantContextMiddleware(MiddlewareMixin):
    """
    Inject tenant context for PostgreSQL RLS policies per request.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        user = getattr(request, 'user', None)
        if not user or not user.is_authenticated:
            return None

        company_id = getattr(user, 'company_id', None)
        if not company_id or connection.vendor != 'postgresql':
            return None

        with connection.cursor() as cursor:
            cursor.execute('SET app.current_company_id = %s;', [str(company_id)])
        return None
