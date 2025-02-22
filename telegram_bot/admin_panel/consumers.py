import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

async_to_sync(channel_layer.group_send)(
    "admin_updates",
    {
        "type": "update_data",
        "action": "update",
        "group": {"group_name": "Test Group", "is_active": True}
    }
)

class GroupConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("admin_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("admin_updates", self.channel_name)

    async def update_data(self, event):
        await self.send(text_data=json.dumps({"message": event["message"]}))
