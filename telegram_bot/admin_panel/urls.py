from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('active_groups/', views.active_groups, name='active_groups'),
    path('search_groups/', views.search_groups, name='search_groups'),
    path('admins/', views.admins, name='admins'),
    path('scheduled_messages/', views.scheduled_messages, name='scheduled_messages'),
    path('group_details/<str:group_name>/', views.group_details, name='group_details'),
]