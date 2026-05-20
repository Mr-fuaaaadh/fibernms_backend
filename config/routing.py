from noc.alerts.routing import websocket_urlpatterns as alert_ws
from noc.telemetry.routing import websocket_urlpatterns as telemetry_ws
from noc.workflows.routing import websocket_urlpatterns as workflow_ws

websocket_urlpatterns = [
    *alert_ws,
    *telemetry_ws,
    *workflow_ws,
]
