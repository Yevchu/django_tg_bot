from django.urls import path
from .views import admin_panel

urlpatterns = [
    path('', admin_panel, name='admin_panel'),
]

