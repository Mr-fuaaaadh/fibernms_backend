import json

from channels.generic.websocket import AsyncWebsocketConsumer


class WorkflowRunsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return
        self.group_name = f'workflow_runs_company_{user.company_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def workflow_run_message(self, event):
        await self.send(text_data=json.dumps(event))

