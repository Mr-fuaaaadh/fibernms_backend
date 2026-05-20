from rest_framework import serializers

from .models import APIKey, Integration, WebhookSubscription


class IntegrationSerializer(serializers.ModelSerializer):
    config = serializers.JSONField(write_only=True, required=False)

    class Meta:
        model = Integration
        fields = ('id', 'company', 'service_name', 'config', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('company', 'created_at', 'updated_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['config'] = instance.get_config()
        return data

    def create(self, validated_data):
        config = validated_data.pop('config', {})
        obj = Integration(**validated_data)
        obj.set_config(config or {})
        obj.save()
        return obj

    def update(self, instance, validated_data):
        config = validated_data.pop('config', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if config is not None:
            instance.set_config(config or {})
        instance.save()
        return instance


class WebhookSerializer(serializers.ModelSerializer):
    secret_token = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = WebhookSubscription
        fields = ('id', 'company', 'target_url', 'events', 'secret_token', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('company', 'created_at', 'updated_at')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['secret_token_set'] = bool(instance.secret_token_encrypted)
        data.pop('secret_token', None)
        return data

    def create(self, validated_data):
        secret = validated_data.pop('secret_token', '')
        obj = WebhookSubscription(**validated_data)
        if secret:
            obj.set_secret(secret)
        obj.save()
        return obj

    def update(self, instance, validated_data):
        secret = validated_data.pop('secret_token', None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if secret is not None:
            instance.set_secret(secret)
        instance.save()
        return instance


class APIKeySerializer(serializers.ModelSerializer):
    plain_key = serializers.CharField(read_only=True)

    class Meta:
        model = APIKey
        fields = (
            'id',
            'company',
            'name',
            'key_prefix',
            'scopes',
            'expires_at',
            'created_at',
            'last_used_at',
            'plain_key',
        )
        read_only_fields = ('company', 'key_prefix', 'created_at', 'last_used_at', 'plain_key')

