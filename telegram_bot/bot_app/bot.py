import logging
import os
import django
import asyncio
import threading
import websockets
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext, MessageHandler, filters, ConversationHandler
from telegram.error import Forbidden
from dotenv import load_dotenv
# Ініціалізація Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "telegram_bot.settings")
django.setup()

from bot_app.services.admin_service import AdminService
from bot_app.components.admin import (
    ADD_ADMIN, ADD_SUPER_ADMIN, REMOVE_ADMIN, REMOVE_SUPER_ADMIN, 
    add_admin_start, add_admin_process, add_super_admin_start, add_super_admin_process,
    remove_admin_start, remove_admin_process, remove_super_admin_start, remove_super_admin_process,
    is_super_admin, is_admin, add_potential_admin, clean_old_potential_admins
)
from bot_app.components.group import (
    REMOVE_GROUP, SPECIFIC_GROUP,
    new_chat, new_chat_member, max_member_count,
    count_groups, count_specific_group_start, count_specific_group_process,
    remove_group_start, remove_group_process, leave_group
)
from admin_panel.models import Admin

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

SUPER_ADMIN_ID = os.getenv("SUPER_ADMIN_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBSOCKET_URL = os.getenv("WEBSOCKET_URL")

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user

    await clean_old_potential_admins()
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

async def error_handler(update: object, context: CallbackContext) -> None:
    print(f"An error occurred: {context.error}")

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

def main():
    
    message = add_super_admin_if_not_exist(SUPER_ADMIN_ID)
    logger.info(message)

    ws_thead = threading.Thread(target=run_websockets_listener, daemon=True)
    ws_thead.start()
    
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

    app.add_error_handler(error_handler)

    app.run_polling()

if __name__ == "__main__":
    main()