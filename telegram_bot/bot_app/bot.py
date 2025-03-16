import logging
import os
import django
import asyncio
import threading
import websockets
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, Application, ContextTypes
from telegram.error import Forbidden
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
from datetime import time
# Ініціалізація Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "telegram_bot.settings")
django.setup()

from bot_app.components.admin import (
    ADD_ADMIN, ADD_SUPER_ADMIN, REMOVE_ADMIN, REMOVE_SUPER_ADMIN, 
    add_admin_start, add_admin_process, add_super_admin_start, add_super_admin_process,
    remove_admin_start, remove_admin_process, remove_super_admin_start, remove_super_admin_process,
    add_potential_admin, clean_old_potential_admins
)
from bot_app.components.group import (
    REMOVE_GROUP, SPECIFIC_GROUP,
    new_chat_member,
    count_groups, count_specific_group_start, count_specific_group_process,
    remove_group_start, remove_group_process, leave_group
)
from bot_app.components.scheduled_messages import check_pending_messages
from admin_panel.models import Admin

# Налаштування логера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG  # Увімкнемо DEBUG-режим
)

# Логування всіх бібліотек
logging.getLogger("telegram").setLevel(logging.DEBUG)
logging.getLogger("telegram.ext").setLevel(logging.DEBUG)
logging.getLogger("asyncio").setLevel(logging.DEBUG)
logging.getLogger("django.db").setLevel(logging.DEBUG)  # Логування Django ORM

logger = logging.getLogger(__name__)  # Основний логер

load_dotenv()

SUPER_ADMIN_ID = os.getenv("SUPER_ADMIN_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await add_potential_admin(user.id, user.username)
    try:
        await update.message.reply_text(f"Привіт, {user.first_name}! Тебе додано в список потенційних адміністраторів.")
    except Forbidden:
        logger.warning(f"Користувач {user.id} заблокував бота.")

def add_super_admin_if_not_exist(super_admin_id: int) -> None:
    admin = Admin.objects.filter(user_id=super_admin_id, is_super_admin=True).first()
    if not admin:
        Admin.objects.create(user_id=super_admin_id, is_super_admin=True)
        message = f"Суперадміністратора з ID {super_admin_id} було успішно створено."
    else:
        message = f"Суперадміністратор з ID {super_admin_id} вже існує."
    return message

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"An error occurred: {context.error}")

    # Collecting detailed error information
    if update:
        logger.error(f"Update: {update}")
    if context:
        logger.error(f"Context: {context}")
    if context.error:
        logger.error(f"Error: {context.error}")

async def websockets_listener():
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        logger.info('Websocket connection established.')
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            logger.info(f"Message received: {data}")

async def send_message_to_websockets(group_name: str, group_id: int):
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        data = {
            'action': 'new_group',
            'group_name': group_name,
            'group_id': group_id
        }
        await websocket.send(json.dumps(data))
        logger.info(f"Message sent: {data}")

def run_websockets_listener():
    asyncio.run(websockets_listener())

def clean_old_potential_admins_job(app: Application):
    logger.info("Clean old potential admins job started.")
    app.job_queue.run_daily(clean_old_potential_admins, time=time(7, 0, 0))

def main():
    
    message = add_super_admin_if_not_exist(SUPER_ADMIN_ID)
    logger.info(message)

    # ws_thead = threading.Thread(target=run_websockets_listener, daemon=True)
    # ws_thead.start()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    logger.info("Бот запущено...")

    app.add_handler(CommandHandler("start", start))
    # app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_chat_member))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("add_admin", add_admin_start)],
        states={ADD_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_admin_process)]},
        fallbacks=[]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("add_super_admin", add_super_admin_start)],
        states={ADD_SUPER_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_super_admin_process)]},
        fallbacks=[]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("remove_admin", remove_admin_start)],
        states={REMOVE_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_admin_process)]},
        fallbacks=[]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("remove_super_admin", remove_super_admin_start)],
        states={REMOVE_SUPER_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_super_admin_process)]},
        fallbacks=[]
    ))

    app.add_handler(CommandHandler("active_groups", count_groups))
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("specific_group", count_specific_group_start)],
        states={SPECIFIC_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, count_specific_group_process)]},
        fallbacks=[]
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("remove_group", remove_group_start)],
        states={REMOVE_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, remove_group_process)]},
        fallbacks=[]
    ))

    app.add_handler(CommandHandler("leave_group", leave_group))

    clean_old_potential_admins_job(app=app)
    logger.info("Send scheduled messages job started.")
    job_q = app.job_queue
    try:
        logger.info("Checking pending messages...")
        job_q.run_repeating(check_pending_messages, interval=30, first=0)
    except Exception as e:
        logger.error(f"Error while sending scheduled messages: {e}")

    app.add_error_handler(error_handler)


    app.run_polling()

if __name__ == "__main__":
    main()