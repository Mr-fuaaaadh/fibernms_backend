from rest_framework.routers import DefaultRouter

from .views import MaintenanceWindowViewSet

router = DefaultRouter()
router.register('', MaintenanceWindowViewSet, basename='maintenance')

urlpatterns = router.urls
