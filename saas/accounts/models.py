import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from saas.companies.models import Company


class User(AbstractUser):

    ROLE_CHOICES = [
        ('superAdmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('engineer', 'Engineer'),
        ('operator', 'Operator'),
        ('viewer', 'Viewer'),
    ]

    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    company = models.ForeignKey(Company,on_delete=models.CASCADE,related_name='users')
    role = models.CharField( max_length=50,choices=ROLE_CHOICES,default='viewer')
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=64, blank=True, default='')
    avatar_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    


class AuthEvent(models.Model):
    EVENT_LOGIN_SUCCESS = 'login_success'
    EVENT_LOGIN_FAILED = 'login_failed'
    EVENT_LOGOUT = 'logout'
    EVENT_MFA_ENABLED = 'mfa_enabled'
    EVENT_MFA_DISABLED = 'mfa_disabled'
    EVENT_MFA_VERIFIED = 'mfa_verified'

    EVENT_CHOICES = [
        (EVENT_LOGIN_SUCCESS, 'Login Success'),
        (EVENT_LOGIN_FAILED, 'Login Failed'),
        (EVENT_LOGOUT, 'Logout'),
        (EVENT_MFA_ENABLED, 'MFA Enabled'),
        (EVENT_MFA_DISABLED, 'MFA Disabled'),
        (EVENT_MFA_VERIFIED, 'MFA Verified'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='auth_events',
        null=True,
        blank=True,
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='auth_events',
        null=True,
        blank=True,
    )
    event_type = models.CharField(max_length=32, choices=EVENT_CHOICES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saas_auth_events'
        indexes = [
            models.Index(fields=['company', 'event_type', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]


class UserSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='sessions')
    refresh_jti = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default='')
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saas_user_sessions'
        indexes = [
            models.Index(fields=['company', 'user', '-created_at']),
            models.Index(fields=['refresh_jti']),
        ]