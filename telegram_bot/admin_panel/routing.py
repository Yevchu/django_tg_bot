from django.urls import path
from .consumers import GroupConsumer

websocket_urlpatterns = [
    path('ws/groups/', GroupConsumer.as_asgi()),
]