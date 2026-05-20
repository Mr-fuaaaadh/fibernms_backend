from rest_framework.throttling import ScopedRateThrottle


class AuthRateThrottle(ScopedRateThrottle):
    scope = 'auth'


class LoginRateThrottle(ScopedRateThrottle):
    scope = 'auth_login'


class MFARateThrottle(ScopedRateThrottle):
    scope = 'auth_mfa'
