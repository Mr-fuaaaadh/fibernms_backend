from rest_framework.routers import DefaultRouter

from .views import WorkflowRunViewSet, WorkflowViewSet

router = DefaultRouter()
router.register('workflows', WorkflowViewSet, basename='workflows')
router.register('workflow-runs', WorkflowRunViewSet, basename='workflow-runs')

urlpatterns = router.urls

