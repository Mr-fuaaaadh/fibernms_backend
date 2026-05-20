from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import AuthEvent, User, UserSession


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ('FiberNMS', {'fields': ('company', 'role', 'mfa_enabled', 'mfa_secret', 'avatar_url')}),
    )
    list_display = ('username', 'email', 'company', 'role', 'is_active', 'mfa_enabled')
    list_filter = ('role', 'is_active', 'mfa_enabled', 'company')


@admin.register(AuthEvent)
class AuthEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'company', 'ip_address', 'created_at')
    list_filter = ('event_type', 'company')
    search_fields = ('user__username', 'user__email', 'ip_address')


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'refresh_jti', 'ip_address', 'revoked_at', 'created_at')
    list_filter = ('company', 'revoked_at')
