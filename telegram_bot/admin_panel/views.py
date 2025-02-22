import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Admin, Group, UserGroup, PotentialAdmin, ScheduledMessage
from django.utils import timezone
import json
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def handle_scheduled_message_form(request):
    success_message = None
    if request.method == 'POST':
        logger.info('Received POST request')
        groups = request.POST.getlist('groups')
        message = request.POST.get('message')
        image = request.FILES.get('image')
        send_time = request.POST.get('send_time')

        logger.info(f'Groups: {groups}')
        logger.info(f'Message: {message}')
        logger.info(f'Image: {image}')
        logger.info(f'Send Time: {send_time}')

        for group_id in groups:
            try:
                group = Group.objects.get(id=group_id)
                send_time_aware = timezone.make_aware(datetime.strptime(send_time, '%Y-%m-%dT%H:%M'))
                ScheduledMessage.objects.create(
                    group=group,
                    message_text=message,
                    image=image,
                    send_time=send_time_aware
                )
                logger.info(f'Scheduled message for group {group_id}')
                success_message = "Message scheduled successfully!"
            except Group.DoesNotExist:
                logger.error(f'Group with id {group_id} does not exist')

    return success_message

def main(request):
    return render(request, 'base.html')

def active_groups(request):
    groups = Group.objects.all()
    context = {
        'groups': groups,
    }
    return render(request, 'active_groups.html', context)

def admins(request):
    admins = Admin.objects.all()
    potential_admins = PotentialAdmin.objects.all()
    context = {
        'admins': admins,
        'potential_admins': potential_admins,
    }
    return render(request, 'admins.html', context)

def scheduled_messages(request):
    success_message = handle_scheduled_message_form(request)
    groups = Group.objects.all()
    scheduled_messages = ScheduledMessage.objects.all()
    context = {
        'groups': groups,
        'scheduled_messages': scheduled_messages,
        'success_message': success_message,
    }
    return render(request, 'scheduled_messages.html', context)

