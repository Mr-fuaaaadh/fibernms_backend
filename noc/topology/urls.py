from rest_framework.routers import DefaultRouter

from .views import FiberRouteViewSet

router = DefaultRouter()
router.register('', FiberRouteViewSet, basename='fiber-routes')

urlpatterns = router.urls
