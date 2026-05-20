from django.urls import re_path

from .consumers import WorkflowRunsConsumer

websocket_urlpatterns = [
    re_path(r'^ws/workflow-runs/$', WorkflowRunsConsumer.as_asgi()),
]

