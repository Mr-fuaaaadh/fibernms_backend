from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import AuthEvent
from .serializers import AuthEventSerializer, LoginSerializer, MFAVerifySerializer, RegisterSerializer
from .services import (
    build_qr_base64,
    build_totp_uri,
    clear_login_failures,
    generate_mfa_secret,
    is_login_locked,
    log_auth_event,
    register_login_failure,
    revoke_session_by_jti,
)
from .throttles import AuthRateThrottle, LoginRateThrottle, MFARateThrottle


def api_response(*, success: bool, message: str, data=None, code=status.HTTP_200_OK):
    return Response(
        {
            'success': success,
            'message': message,
            'data': data or {},
        },
        status=code,
    )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginRateThrottle]
    throttle_scope = 'auth_login'

    def post(self, request):
        username = request.data.get('username', '')
        if username and is_login_locked(username):
            return api_response(
                success=False,
                message='Too many failed attempts. Try again later.',
                code=status.HTTP_423_LOCKED,
            )

        serializer = LoginSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            if username:
                register_login_failure(username)
            log_auth_event(
                request=request,
                user=None,
                event_type=AuthEvent.EVENT_LOGIN_FAILED,
                metadata={'errors': serializer.errors},
            )
            return api_response(
                success=False,
                message='Authentication failed.',
                data=serializer.errors,
                code=status.HTTP_400_BAD_REQUEST,
            )

        tokens = serializer.build_token_payload()
        user = serializer.validated_data['user']
        clear_login_failures(user.username)
        log_auth_event(request=request, user=user, event_type=AuthEvent.EVENT_LOGIN_SUCCESS)
        return api_response(success=True, message='Login successful', data=tokens)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AuthRateThrottle]
    throttle_scope = 'auth'

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(
                success=False,
                message='Registration failed.',
                data=serializer.errors,
                code=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()
        return api_response(
            success=True,
            message='User registered successfully',
            data={
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'company_id': str(user.company_id),
                'role': user.role,
            },
            code=status.HTTP_201_CREATED,
        )


class RefreshTokenView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code != status.HTTP_200_OK:
            return api_response(
                success=False,
                message='Token refresh failed.',
                data=response.data,
                code=response.status_code,
            )
        return api_response(success=True, message='Token refreshed', data=response.data)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return api_response(
                success=False,
                message='Refresh token is required.',
                code=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            jti = token['jti']
            token.blacklist()
            revoke_session_by_jti(jti)
        except Exception:
            return api_response(
                success=False,
                message='Invalid refresh token.',
                code=status.HTTP_400_BAD_REQUEST,
            )

        log_auth_event(request=request, user=request.user, event_type=AuthEvent.EVENT_LOGOUT)
        return api_response(success=True, message='Logout successful')


class MFAEnableView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [MFARateThrottle]
    throttle_scope = 'auth_mfa'

    def post(self, request):
        user = request.user
        secret = generate_mfa_secret()
        user.mfa_secret = secret
        user.mfa_enabled = False
        user.save(update_fields=['mfa_secret', 'mfa_enabled'])

        uri = build_totp_uri(user, secret)
        qr_base64 = build_qr_base64(uri)
        return api_response(
            success=True,
            message='MFA setup initialized.',
            data={
                'secret': secret,
                'otpauth_url': uri,
                'qr_base64': qr_base64,
            },
        )


class MFAVerifyView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [MFARateThrottle]
    throttle_scope = 'auth_mfa'

    def post(self, request):
        serializer = MFAVerifySerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return api_response(
                success=False,
                message='OTP verification failed.',
                data=serializer.errors,
                code=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user.mfa_enabled = True
        user.save(update_fields=['mfa_enabled'])
        log_auth_event(request=request, user=user, event_type=AuthEvent.EVENT_MFA_VERIFIED)
        log_auth_event(request=request, user=user, event_type=AuthEvent.EVENT_MFA_ENABLED)
        return api_response(success=True, message='MFA enabled successfully')


class MFADisableView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [MFARateThrottle]
    throttle_scope = 'auth_mfa'

    def post(self, request):
        user = request.user
        user.mfa_enabled = False
        user.mfa_secret = ''
        user.save(update_fields=['mfa_enabled', 'mfa_secret'])
        log_auth_event(request=request, user=user, event_type=AuthEvent.EVENT_MFA_DISABLED)
        return api_response(success=True, message='MFA disabled successfully')


class AuthEventListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        events = request.user.auth_events.all().order_by('-created_at')[:100]
        return api_response(
            success=True,
            message='Authentication events fetched',
            data={'results': AuthEventSerializer(events, many=True).data},
        )
