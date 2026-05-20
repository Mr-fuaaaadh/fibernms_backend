from rest_framework.routers import DefaultRouter

from .views import APIKeyViewSet, IntegrationViewSet, WebhookViewSet

router = DefaultRouter()
router.register('integrations', IntegrationViewSet, basename='integrations')
router.register('webhooks', WebhookViewSet, basename='webhooks')
router.register('api-keys', APIKeyViewSet, basename='api-keys')

urlpatterns = router.urls

