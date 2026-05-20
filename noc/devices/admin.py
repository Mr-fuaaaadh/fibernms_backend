from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured

try:
    from django.contrib.gis.admin import GISModelAdmin
except ImproperlyConfigured:
    GISModelAdmin = admin.ModelAdmin

from .models import Device


@admin.register(Device)
class DeviceAdmin(GISModelAdmin):
    list_display = ('name', 'company', 'type', 'status', 'region', 'last_seen')
    list_filter = ('company', 'type', 'status', 'region')
    search_fields = ('name',)
