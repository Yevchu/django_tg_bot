import logging
from django.shortcuts import render
from .models import Admin, Group, PotentialAdmin, ScheduledMessage
from django.utils import timezone
from django.db.models import Q
from datetime import datetime
import cloudinary.uploader

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

def handle_scheduled_message_form(request):
    message_state = None
    if request.method == 'POST':
        logger.info('Received POST request')
        groups = request.POST.getlist('groups')
        message = request.POST.get('message')
        image = request.FILES.get('image')
        send_time = request.POST.get('send_time')

        for group_id in groups:
            try:
                upload_result = None
                if image:
                    public_id = f'groupID_{group_id}_sendtime_{send_time}'
                    upload_result = cloudinary.uploader.upload(image, public_id=public_id)
                group = Group.objects.get(id=group_id)
                send_time_aware = timezone.make_aware(datetime.strptime(send_time, '%Y-%m-%dT%H:%M'))

                if send_time_aware < timezone.now():
                    logger.error('Send time is in the past')
                    message_state = 'Send time is in the past'
                    break

                ScheduledMessage.objects.create(
                    group=group,
                    message_text=message,
                    image=upload_result['secure_url'] if upload_result else image,
                    send_time=send_time_aware
                )
                logger.info(f'Scheduled message for group {group_id}')
                message_state = "Message scheduled successfully!"
            except Group.DoesNotExist:
                logger.error(f'Group with id {group_id} does not exist')

    return message_state

def main(request):
    return render(request, 'base.html')

def active_groups(request):
    groups = Group.objects.all()
    context = {
        'groups': groups,
    }
    return render(request, 'active_groups.html', context)

def search_groups(request):
    search_query = request.GET.get('search', '')
    if search_query:
        groups = Group.objects.filter(Q(group_name__icontains=search_query))
    else:
        context['search_error'] = 'Не було знайдено жодної групи'
    context = {
        'groups': groups,
        'search_query': search_query,
    }
    return render(request, 'search_results.html', context)

def group_details(request, group_name):
    group = Group.objects.get(group_name=group_name)
    scheduled_messages = ScheduledMessage.objects.filter(group=group)
    context = {
        'group': group,
        'scheduled_messages': scheduled_messages,
    }
    return render(request, 'group_details.html', context)

def admins(request):
    admins = Admin.objects.all()
    potential_admins = PotentialAdmin.objects.all()
    context = {
        'admins': admins,
        'potential_admins': potential_admins,
    }
    return render(request, 'admins.html', context)

def scheduled_messages(request):
    message_state = handle_scheduled_message_form(request)
    groups = Group.objects.all()
    scheduled_messages = ScheduledMessage.objects.all()
    context = {
        'groups': groups,
        'scheduled_messages': scheduled_messages,
        'message_state': message_state,
    }
    return render(request, 'scheduled_messages.html', context)

