import hashlib
import hmac
import secrets
import uuid

from django.db import models
from django.utils import timezone

from .crypto import decrypt_text, encrypt_text


class Integration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='integrations')
    service_name = models.CharField(max_length=64, db_index=True)
    config_encrypted = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'noc_integrations'
        constraints = [
            models.UniqueConstraint(fields=['company', 'service_name'], name='uq_integration_company_service'),
        ]
        indexes = [
            models.Index(fields=['company', 'service_name', 'is_active']),
        ]

    def set_config(self, config: dict) -> None:
        self.config_encrypted = encrypt_text(models.JSONField().get_prep_value(config) or '{}')

    def get_config(self) -> dict:
        if not self.config_encrypted:
            return {}
        raw = decrypt_text(self.config_encrypted)
        return models.JSONField().to_python(raw) or {}


class WebhookSubscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='webhooks')
    target_url = models.URLField()
    events = models.JSONField(default=list, blank=True)
    secret_token_encrypted = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'noc_webhooks'
        indexes = [
            models.Index(fields=['company', 'is_active']),
        ]

    def set_secret(self, secret: str) -> None:
        self.secret_token_encrypted = encrypt_text(secret)

    def get_secret(self) -> str:
        return decrypt_text(self.secret_token_encrypted) if self.secret_token_encrypted else ''


class APIKey(models.Model):
    """
    API keys are write-once: only store a hash + prefix. Return the plain key only at creation time.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='api_keys')
    name = models.CharField(max_length=255)
    key_prefix = models.CharField(max_length=16, db_index=True)
    key_hash = models.CharField(max_length=128, db_index=True)
    scopes = models.JSONField(default=list, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'noc_api_keys'
        constraints = [
            models.UniqueConstraint(fields=['company', 'name'], name='uq_api_key_company_name'),
        ]
        indexes = [
            models.Index(fields=['company', 'key_prefix']),
            models.Index(fields=['company', '-created_at']),
        ]

    @staticmethod
    def generate_plaintext_key() -> str:
        return secrets.token_urlsafe(40)

    @staticmethod
    def build_prefix(plain: str) -> str:
        return plain[:12]

    @staticmethod
    def hash_key(plain: str) -> str:
        return hashlib.sha256(plain.encode('utf-8')).hexdigest()

    def is_expired(self) -> bool:
        return bool(self.expires_at and self.expires_at <= timezone.now())

    def verify(self, plain: str) -> bool:
        return hmac.compare_digest(self.key_hash, self.hash_key(plain))

