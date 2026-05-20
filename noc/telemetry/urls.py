from rest_framework.routers import DefaultRouter

from .views import TelemetryViewSet

router = DefaultRouter()
router.register('', TelemetryViewSet, basename='telemetry')

urlpatterns = router.urls
