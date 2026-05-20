from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SLAMetricSnapshotViewSet, SLAProfileViewSet, SLATimerViewSet

router = DefaultRouter()
router.register('profiles', SLAProfileViewSet, basename='sla-profiles')
router.register('metrics', SLAMetricSnapshotViewSet, basename='sla-metrics')
router.register('timers', SLATimerViewSet, basename='sla-timers')

urlpatterns = [path('', include(router.urls))]

