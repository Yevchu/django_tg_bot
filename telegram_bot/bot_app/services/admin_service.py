from typing import Optional
from admin_panel.models import Admin, PotentialAdmin
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now, timedelta


class AdminService:

    @staticmethod
    async def get_admin_by_id(user_id: int) -> Optional[Admin]:
        return await Admin.objects.filter(user_id=user_id).afirst()
    
    @staticmethod
    async def get_admin_by_username(username: str) -> Optional[Admin]:
        return await Admin.objects.filter(username=username).afirst()
    
    @staticmethod
    async def get_potential_admin_by_username(username: str) -> Optional[PotentialAdmin]:
        return await PotentialAdmin.objects.filter(username=username).afirst()
    
    @staticmethod
    async def add_admin(user_id: int, username: Optional[str] = None) -> bool:
        try:
            await Admin.objects.acreate(user_id=user_id, username=username, is_super_admin=False)
            return True
        except IntegrityError:
            return False
        
    @staticmethod
    async def remove_admin_by_identifier(admin_identifier: Optional[str|int]) -> str:
        if isinstance(admin_identifier, int):
            admin = await AdminService.get_admin_by_id(admin_identifier)
        else:
            admin = await AdminService.get_admin_by_username(admin_identifier)
        if not admin:
            return "Адміністратора з таким ім'ям або ID не знайдено."
        await admin.adelete()
        return "Адміністратора успішно видаленно."
    
    @staticmethod
    async def get_super_admin_by_id(user_id: int) -> Optional[Admin]:
        return await Admin.objects.filter(user_id=user_id, is_super_admin=True).afirst()
    
    @staticmethod 
    async def get_super_admin_by_username(username: str) -> Optional[Admin]:
        return await Admin.objects.filter(username=username, is_super_admin=True).afirst()
    
    @staticmethod
    async def add_super_admin(user_id: int) -> str:
        admin = await AdminService.get_admin_by_id(user_id)
        if admin:
            if admin.is_super_admin:
                return "Користувач вже є супердміністратором."
            admin.is_super_admin = True
            await admin.asave()
            return "Адміністратора було успішно призначено суперадміністратором."
        return "Адміністратор не знайдений."
    
    @staticmethod
    async def remove_super_admin_by_identifier(user_identifier: Optional[str|int]) -> str:
        if isinstance(user_identifier, int):
            super_admin = await AdminService.get_super_admin_by_id(user_id=user_identifier)
        else:
            super_admin = await AdminService.get_super_admin_by_username(username=user_identifier)
        if not super_admin:
            return 'Суперадміністратора з таким ID не знайдено.'
        await super_admin.adelete()
        return 'Суперадміністратора успішно видаленою'
    
    @staticmethod
    async def add_potential_admin(user_id: int, username: str) -> str:
        try:
            await PotentialAdmin.objects.acreate(user_id=user_id, username=username)
            return f'Potential admin @{username} was successfully registered'
        except IntegrityError:
            return f'This user: @{username} is already registered as potential admin'

    @staticmethod
    async def clean_old_potential_admins() -> str:
        expiry_time = now() - timedelta(hours=24)
        await PotentialAdmin.objects.filter(requested_at__lt=expiry_time).adelete()
        message = 'Old potential admins were successfully deleted'
        return message