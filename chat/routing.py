from django.urls import re_path

from .consumers import UserChatConsumer


websocket_urlpatterns = [
    re_path('ws/chat/users/', UserChatConsumer.as_asgi()),
]
