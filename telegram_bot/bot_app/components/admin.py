import logging
import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot_app.services.admin_service import AdminService
from django.db import IntegrityError
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
SUPER_ADMIN_ID = int(os.getenv('SUPER_ADMIN_ID'))
ADD_ADMIN, ADD_SUPER_ADMIN, REMOVE_ADMIN, REMOVE_SUPER_ADMIN = range(4)

async def add_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_super_admin(update.effective_user.id):
        await update.message.reply_text('You are not a super admin')
        return ConversationHandler.END
    await update.message.reply_text('Enter user id or telegram username at the format @username')
    return ADD_ADMIN

async def add_admin_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.strip()
    
    try:
        user_id = int(user_input)
        username = None
    except ValueError:
        username = user_input.strip('@')
        potential_admin = await AdminService.get_potential_admin_by_username(username=username)
        if potential_admin:
            user_id = potential_admin.user_id
        else:
            await update.message.reply_text(
                f'User with username @{username} not found or not registered as potential admin at /start command'
            )
            return ConversationHandler.END
    if await AdminService.add_admin(user_id=user_id, username=username):
        await update.message.reply_text(f'User @{username or user_id} was added as admin')
    else:
        await update.message.reply_text(f'User @{username or user_id} is already an admin')
    return ConversationHandler.END

async def add_super_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_super_admin(update.effective_user.id):
        await update.message.reply_text('You are not a super admin')
        return ConversationHandler.END
    await update.message.reply_text('Enter user id or telegram username at the format @username')
    return ADD_SUPER_ADMIN

async def add_super_admin_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.strip()
    
    try:
        user_id = int(user_input)
        username = None
    except ValueError:
        username = user_input.strip('@')
        admin = await AdminService.get_admin_by_username(username=username)
        if admin:
            user_id = admin.user_id
        else:
            await update.message.reply_text(
                f'User with username @{username} not found or not registered as admin'
            )
            return ConversationHandler.END
    message = await AdminService.add_super_admin(user_id=user_id)
    await update.message.reply_text(message)
    return ConversationHandler.END

async def remove_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_super_admin(update.effective_user.id):
        await update.message.reply_text('You are not a super admin')
        return ConversationHandler.END
    await update.message.reply_text('Enter user id or telegram username at the format @username')
    return REMOVE_ADMIN

async def remove_admin_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.strip()
    
    try:
        user_id = int(user_input)
        admin_identifier = user_id
    except ValueError:
        username = user_input.strip('@')
        admin_identifier = username

    message = await AdminService.remove_admin_by_identifier(admin_identifier=admin_identifier)
    await update.message.reply_text(message)
    return ConversationHandler.END

async def remove_super_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_super_admin(update.effective_user.id):
        await update.message.reply_text('You are not a super admin')
        return ConversationHandler.END
    await update.message.reply_text('Enter user id or telegram username at the format @username')
    return REMOVE_SUPER_ADMIN

async def remove_super_admin_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text.strip()
    
    try:
        user_id = int(user_input)
        super_admin_identifier = user_id
    except ValueError:
        username = user_input.strip('@')
        super_admin_identifier = username
    message = await AdminService.remove_super_admin_by_identifier(user_identifier=super_admin_identifier)
    await update.message.reply_text(message)
    return ConversationHandler.END

async def is_admin(user_id: int) -> bool:
    admin = await AdminService.get_admin_by_id(user_id=user_id)
    return bool(admin)

async def is_super_admin(user_id: int) -> bool:
    super_admin = await AdminService.get_super_admin_by_id(user_id=user_id)
    return bool(super_admin)

async def add_potential_admin(user_id: int, username: str) -> None:
    message = await AdminService.add_potential_admin(user_id=user_id, username=username)
    logger.info(message)

async def clean_old_potential_admins() -> None:
    message = await AdminService.clean_old_potential_admins()
    logger.info(message)