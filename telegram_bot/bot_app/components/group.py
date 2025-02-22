import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from bot_app.services.group_service import GroupService, Group
from django.db import IntegrityError
from bot_app.components.admin import is_admin

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
REMOVE_GROUP, SPECIFIC_GROUP = range(2)

async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Group:
    logger.info('Triggered new chat func: "%s" (%d)', update.effective_chat.title, update.effective_chat.id)

    try:
        group = await GroupService.get_group_by_identifier(group_identifier=update.effective_chat.id)
        if not group:
            new_group = await GroupService.create_group(group_id=update.effective_chat.id, group_name=update.effective_chat.title)
            logger.info('New group created: "%s" (%d)', update.effective_chat.title, update.effective_chat.id)
            return new_group
    except Exception as e:
        logger.error('Error creating group "%s" (%d): %s', update.effective_chat.title, update.effective_chat.id, str(e))

    return group

async def new_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info('New member in chat: "%s" (%d)', update.effective_chat.title, update.effective_chat.id)

    group_id = update.effective_chat.id
    group_title = update.effective_chat.title
        
    is_existing_group = await new_chat(update, context)

    if is_existing_group:
        for user in update.message.new_chat_members:
            if user.id != context.bot.id:
                logger.info('Trying to add user: ID %d, name: %s', user.id, user.full_name)
                try:
                    success = await GroupService.add_unique_member(is_existing_group, user.id)
                    if success:
                        logger.info('Success: User ID %d, name %s added to group "%s"', user.id, user.full_name, group_title)
                    else:
                        logger.warning('User ID %d already in group "%s"', user.id, group_title)
                except IntegrityError as e:
                    logger.error('IntegrityError: Error adding user ID %d to group "%s": %s', user.id, group_title, str(e))
                except Exception as e:
                    logger.error('Error: User ID %d was not added to group "%s": %s', user.id, group_title, str(e))

async def max_member_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    group_id = update.effective_chat.id
    groups = await GroupService.get_active_groups()

    for group in groups:
        logger.info(f'Group ID: {group.group_id}, Group Name: {group.group_id}, Max Member Count: {group.max_member_count}')
        try:
            member_count = await context.bot.get_chat_members_count(group_id)

            if group.max_member_count < member_count:
                group.max_member_count = member_count
                group.asave()
                logger.info(f'max_member_count updated for group {group.group_name}')
        except Exception as e:
            logger.error(f'Error updating max_member_count for group {group.group_name}: {str(e)}')

async def count_groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this command.')
        return
    
    groups = await GroupService.get_active_groups()
    group_info = "\n".join([f"ID: {group.group_id}, Name: {group.group_name}, Unique Members: {group.unique_members_count}, Max members count: {group.max_member_count}" for group in groups])
    await update.message.reply_text(f"Активні групи:\n{group_info}")

async def count_specific_group_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this command.')
        return ConversationHandler.END

    await update.message.reply_text('Enter the group ID or name:')
    return SPECIFIC_GROUP

async def count_specific_group_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    group_identifier = update.message.text.strip()

    try:
        group = await GroupService.get_group_by_identifier(group_identifier)
        await update.message.reply_text(f'Group ID: {group.group_id}, Group Name: {group.group_name}, Max Member Count: {group.max_member_count}, Unique Members Count: {group.unique_members_count}')
    except Group.DoesNotExist:
        await update.message.reply_text('Group not found.')

    return ConversationHandler.END

async def remove_group_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this command.')
        return ConversationHandler.END

    await update.message.reply_text('Enter the group ID or name:')
    return REMOVE_GROUP

async def remove_group_process(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    group_identifier = update.message.text.strip()

    try:
        group = await GroupService.get_group_by_identifier(group_identifier=group_identifier)
        group.adelete()
        await update.message.reply_text(update.effective_user.id, f'Group {group.group_name} deleted.')
    except Group.DoesNotExist:
        await update.message.reply_text(update.effective_user.id, 'Group not found.')

    return ConversationHandler.END

async def leave_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text('You are not authorized to use this command.')
        return ConversationHandler.END
    
    group_identifier = ' '.join(context.args).strip() if context.args else update.effective_chat.id

    try:
        group = await GroupService.get_group_by_identifier(group_identifier)
        group.adelete()
        await context.bot.leave_chat(group.group_id)
        await update.message.reply_text(f'Group {group.group_name} deleted and bot leave the group.')
    except Group.DoesNotExist:
        await update.message.reply_text('Group not found.')

