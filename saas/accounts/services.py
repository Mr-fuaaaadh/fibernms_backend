import base64
from io import BytesIO
from typing import Any

import pyotp
import qrcode
from django.core.cache import cache
from django.utils import timezone

from .models import AuthEvent, User, UserSession


def get_client_ip(request) -> str | None:
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_auth_event(
    *,
    request,
    user: User | None,
    event_type: str,
    metadata: dict[str, Any] | None = None,
) -> AuthEvent:
    company = user.company if user else None
    return AuthEvent.objects.create(
        user=user,
        company=company,
        event_type=event_type,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        metadata=metadata or {},
    )


def generate_mfa_secret() -> str:
    return pyotp.random_base32()


def build_totp_uri(user: User, secret: str) -> str:
    issuer = 'FiberNMS'
    account_name = user.email or user.username
    return pyotp.TOTP(secret).provisioning_uri(name=account_name, issuer_name=issuer)


def build_qr_base64(uri: str) -> str:
    img = qrcode.make(uri)
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode('utf-8')


def verify_totp_code(secret: str, code: str) -> bool:
    return pyotp.TOTP(secret).verify(code, valid_window=1)


def upsert_session(
    *,
    user: User,
    refresh_jti: str,
    request,
) -> UserSession:
    session, _ = UserSession.objects.update_or_create(
        refresh_jti=refresh_jti,
        defaults={
            'user': user,
            'company': user.company,
            'ip_address': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'revoked_at': None,
        },
    )
    return session


def revoke_session_by_jti(refresh_jti: str) -> None:
    UserSession.objects.filter(refresh_jti=refresh_jti).update(revoked_at=timezone.now())


def _lock_key(username: str) -> str:
    return f'auth:lock:{username.lower()}'


def _fail_key(username: str) -> str:
    return f'auth:fail:{username.lower()}'


def is_login_locked(username: str) -> bool:
    return bool(cache.get(_lock_key(username)))


def register_login_failure(username: str) -> None:
    fail_key = _fail_key(username)
    failures = int(cache.get(fail_key, 0)) + 1
    cache.set(fail_key, failures, timeout=15 * 60)
    if failures >= 5:
        cache.set(_lock_key(username), True, timeout=15 * 60)


def clear_login_failures(username: str) -> None:
    cache.delete(_fail_key(username))
    cache.delete(_lock_key(username))
