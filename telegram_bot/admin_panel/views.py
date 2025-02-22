from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Admin, Group, UserGroup, PotentialAdmin, ScheduledMessage
import json

# Create your views here.
def admin_panel(request):
    groups = Group.objects.all()
    # users = UserGroup.objects.all()
    # admins = Admin.objects.all()
    # potential_admins = PotentialAdmin.objects.all()
    # scheduled_messages = ScheduledMessage.objects.all()

    context = {
        'groups': groups,
        # 'users': users,
        # 'admins': admins,
        # 'potential_admins': potential_admins,
        # 'scheduled_messages': scheduled_messages
    }

    return render(request, './admin_panel.html', context)

@csrf_exempt
def add_group(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        group_id = data.get('group_id')
        group_name = data.get('group_name')

