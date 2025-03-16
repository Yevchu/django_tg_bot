import logging
from datetime import datetime, timezone
from admin_panel.models import ScheduledMessage
from django.utils.timezone import now
from telegram.ext import ContextTypes
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

class MessageService:
    
    @staticmethod
    async def get_pending_messages() -> list[ScheduledMessage]:
        logger.info('Getting pending messages')
        messages_list = []
        async for message in ScheduledMessage.objects.filter(send_time__lte=now(), is_send=False).select_related("group"):
            messages_list.append(message)
        return messages_list
    
    @staticmethod
    async def mark_as_send(message: ScheduledMessage):
        message.is_send = True
        await message.asave()

