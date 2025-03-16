import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot_app.services.message_service import MessageService, ScheduledMessage
from io import BytesIO

# Налаштування логера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO  # Увімкнемо DEBUG-режим
)

# Логування всіх бібліотек
logging.getLogger("telegram").setLevel(logging.DEBUG)
logging.getLogger("telegram.ext").setLevel(logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.DEBUG)
logging.getLogger("django.db").setLevel(logging.DEBUG)  # Логування Django ORM

logger = logging.getLogger(__name__)  # Основний логер

async def get_pending_messages() -> list[ScheduledMessage]:
    logger.info('Getting pending messages')
    return await MessageService.get_pending_messages()

async def check_pending_messages(context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.debug("🔍 [check_pending_messages] Запущено перевірку повідомлень...")

    messages = await get_pending_messages()
    logger.debug(f"📩 [check_pending_messages] Отримано {len(messages)} повідомлень")

    if messages:
        for message in messages:
            try:
                logger.debug(f"📝 [check_pending_messages] Обробляємо повідомлення {message.id} для групи {message.group.group_id}")

                if message.image:
                    logger.debug(f"🖼 [check_pending_messages] Відправляємо зображення у {message.group.group_name}")
                    image_stream = BytesIO(bytes(message.image))
                    image_stream.name = 'photo.jpg'
                    
                    await context.bot.send_photo(
                        chat_id=message.group.group_id,
                        photo=image_stream,
                        caption=message.message_text
                    )
                else:
                    logger.debug(f"💬 [check_pending_messages] Відправляємо текстове повідомлення у {message.group.group_name}")
                    await context.bot.send_message(
                        chat_id=message.group.group_id,
                        text=message.message_text
                    )

                logger.debug(f"✅ [check_pending_messages] Позначаємо повідомлення {message.id} як відправлене")
                await MessageService.mark_as_send(message)

            except Exception as e:
                logger.error(f"❌ [check_pending_messages] Помилка при відправці повідомлення {message.id}: {e}", exc_info=True)

