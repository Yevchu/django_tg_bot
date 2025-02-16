import logging
from typing import Optional, List
from admin_panel.models import Group, UserGroup
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from asgiref.sync import sync_to_async

logging.basicConfig(
    level=logging.DEBUG,
    format='%(astime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class GroupService:

    @staticmethod
    async def add_user(user_id: int, group_id: int) -> Optional[UserGroup|str]:
        try:
            user = await UserGroup.objects.acreate(user_id=user_id, group_id=group_id)
            return user
        except IntegrityError as e:
            return f'Виникла помилка {e}'
        
    @staticmethod
    async def get_user(user_id: int, group_id: int) -> UserGroup:
        return await UserGroup.objects.filter(user_id=user_id, group_id=group_id).afirst()
    
    @staticmethod
    async def add_unique_member(group: Group, user_id: int) -> bool:
        logger.debug(f"Виклик add_unique_member для групи {group.group_id} з user_id={user_id}")
        
        existing_user = await GroupService.get_user(user_id=user_id, group_id=group.group_id)
        if existing_user:
            logger.info(f"Користувач {user_id} вже існує в групі {group.group_id}")
            return False
        
        try:
            await GroupService.add_user(user_id=user_id, group_id=group.group_id)
            await Group.objects.filter(group_id=group.group_id).aupdate({"unique_members_count": Group.unique_members_count + 1})
            return True
        except IntegrityError:
            logger.error(f"Помилка при додаванні користувача {user_id} до групи {group.group_id}", exc_info=True)
            return False
    
    @staticmethod
    async def get_group_by_identifier(group_identifier: str|int) -> Group:
        if isinstance(group_identifier, int):
            return await Group.objects.filter(group_id=group_identifier).afirst()
        else:
            return await Group.objects.filter(group_name=group_identifier).afirst()
    
    @staticmethod
    async def get_active_groups() -> List[Group]:
        groups = await sync_to_async(list)(Group.objects.filter(is_active=True))
        return groups

    @staticmethod
    async def create_group(group_id: int, group_name: str) -> Group:
        group = await Group.objects.acreate(group_id=group_id, group_name=group_name, is_active=True)
        return group
    
    @staticmethod
    async def delete_group(group_identifier: Optional[str|int]) -> str:
        group = await GroupService.get_group_by_identifier(group_identifier)
        if not group:
            return "Такої групи не було знайдено."

        try:
            await group.adelete()
            return f"Групу {group.group_name} було видаленно."
        except IntegrityError as e:
            return f"Сталася помилка {e} при видаленні групи"
        
