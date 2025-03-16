from django.db import models
from django.utils.timezone import now
from cloudinary.models import CloudinaryField

# Create your models here.
class Admin(models.Model):
    user_id = models.BigIntegerField(unique=True)
    username = models.CharField(null=True)
    is_super_admin = models.BooleanField(default=False)

    class Meta:
        db_table = 'admin'

    def __str__(self):
        return self.user_id

class Group(models.Model):
    group_id = models.BigIntegerField(unique=True)
    group_name = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)
    unique_members_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'groups'
    
    def __str__(self):
        return self.group_name

class UserGroup(models.Model):
    user_id = models.BigIntegerField(null=False)
    group = models.ForeignKey(
        'Group', on_delete=models.CASCADE, related_name='unique_user'
    )
    class Meta:
        db_table = 'user_groups'
        unique_together = ('user_id', 'group')

    def __str__(self):
        return f"User {self.user_id} in Group {self.group_id}"

class PotentialAdmin(models.Model):
    user_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    requested_at = models.DateTimeField(default=now)

    class Meta:
        db_table = 'potential_admins'

    def __str__(self):
        return f"Potential Admin {self.username or self.user_id}"

class ScheduledMessage(models.Model):
    group = models.ForeignKey(
        'Group', on_delete=models.CASCADE, related_name='scheduled_messages'
    )
    send_time = models.DateTimeField()
    message_text = models.TextField(blank=True)
    image = CloudinaryField(null=True, blank=True)
    is_send = models.BooleanField(default=False)

    class Meta:
        db_table = 'scheduled_messages'

    def __str__(self):
        return f"Message to {self.group.group_name} at {self.send_time}"

