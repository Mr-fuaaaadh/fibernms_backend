from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import AuthEvent, User
from saas.companies.models import Company
from .services import upsert_session, verify_totp_code


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    otp_code = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        request = self.context['request']
        user = authenticate(request=request, username=attrs['username'], password=attrs['password'])

        if not user:
            raise serializers.ValidationError('Invalid credentials.')
        if not user.is_active:
            raise serializers.ValidationError('Inactive user.')

        otp_code = attrs.get('otp_code', '')
        if user.mfa_enabled:
            if not otp_code:
                raise serializers.ValidationError('OTP code is required for MFA-enabled accounts.')
            if not user.mfa_secret or not verify_totp_code(user.mfa_secret, otp_code):
                raise serializers.ValidationError('Invalid OTP code.')

        attrs['user'] = user
        return attrs

    def build_token_payload(self):
        user = self.validated_data['user']
        refresh = RefreshToken.for_user(user)
        refresh['company_id'] = str(user.company_id)
        refresh['role'] = user.role
        upsert_session(user=user, refresh_jti=refresh['jti'], request=self.context['request'])
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    company_id = serializers.UUIDField(write_only=True, required=False)
    company = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'company_id',
            'company',
            'role',
        )

    def validate_company_id(self, value):
        if not Company.objects.filter(id=value).exists():
            raise serializers.ValidationError('Invalid company_id.')
        return value

    def validate(self, attrs):
        company_id = attrs.get('company_id')
        company_payload = attrs.get('company')

        if not company_id and not company_payload:
            raise serializers.ValidationError('Provide either company_id or company details.')
        if company_id and company_payload:
            raise serializers.ValidationError('Provide only one of company_id or company.')

        if company_payload:
            required = ['name', 'contact_email', 'region']
            missing = [k for k in required if not company_payload.get(k)]
            if missing:
                raise serializers.ValidationError({'company': f"Missing fields: {', '.join(missing)}"})
            if Company.objects.filter(contact_email=company_payload['contact_email']).exists():
                raise serializers.ValidationError({'company': 'contact_email already exists.'})

            # Force first user of a newly created company to be superAdmin unless explicitly admin.
            role = attrs.get('role') or 'viewer'
            if role not in ('superAdmin', 'admin'):
                attrs['role'] = 'superAdmin'

        return attrs

    def create(self, validated_data):
        company_payload = validated_data.pop('company', None)
        company_id = validated_data.pop('company_id', None)
        password = validated_data.pop('password')
        if company_payload:
            company = Company.objects.create(
                name=company_payload['name'],
                contact_email=company_payload['contact_email'],
                region=company_payload['region'],
                status='trial',
            )
            company_id = company.id

        user = User(**validated_data, company_id=company_id)
        user.set_password(password)
        user.save()
        return user


class MFAVerifySerializer(serializers.Serializer):
    otp_code = serializers.CharField()

    def validate(self, attrs):
        user: User = self.context['request'].user
        if not user.mfa_secret:
            raise serializers.ValidationError('MFA is not initialized for this account.')
        if not verify_totp_code(user.mfa_secret, attrs['otp_code']):
            raise serializers.ValidationError('Invalid OTP code.')
        return attrs


class AuthEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthEvent
        fields = ('id', 'event_type', 'ip_address', 'user_agent', 'metadata', 'created_at')
