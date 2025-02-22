import logging
from django.shortcuts import render, redirect
from .models import Admin, Group, UserGroup, PotentialAdmin, ScheduledMessage
from django.utils import timezone
from django.db.models import Q
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
    success_message = handle_scheduled_message_form(request)
    groups = Group.objects.all()
    scheduled_messages = ScheduledMessage.objects.all()
    context = {
        'groups': groups,
        'scheduled_messages': scheduled_messages,
        'success_message': success_message,
    }
    return render(request, 'scheduled_messages.html', context)

