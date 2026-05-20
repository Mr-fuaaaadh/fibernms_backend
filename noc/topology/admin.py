from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured

try:
    from django.contrib.gis.admin import GISModelAdmin
except ImproperlyConfigured:
    GISModelAdmin = admin.ModelAdmin

from .models import FiberRoute


@admin.register(FiberRoute)
class FiberRouteAdmin(GISModelAdmin):
    list_display = ('name', 'company', 'route_type', 'status', 'from_device', 'to_device', 'length_meters')
    list_filter = ('company', 'route_type', 'status')
    search_fields = ('name',)
