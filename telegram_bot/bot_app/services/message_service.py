from datetime import datetime, timezone
from admin_panel.models import ScheduledMessage
from django.utils.timezone import now

class MessageService:

    @staticmethod
    async def save_message(group_id: int, group_name: str, send_time: datetime, message_text: str) -> ScheduledMessage:
        message = await ScheduledMessage.objects.acreate(
            group_id=group_id,
            group_name=group_name,
            send_time=send_time,
            message_text=message_text
        )
        return message
    
    @staticmethod
    async def get_pending_messages() -> list[ScheduledMessage]:
        return await ScheduledMessage.objects.filter(send_time__lte=now(), is_send=False).all()
    
    @staticmethod
    async def mark_as_send(message: ScheduledMessage):
        message.is_send = True
        await message.asave()

        