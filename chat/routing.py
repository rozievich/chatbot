from django.urls import re_path

from .consumers import UserChatConsumer, ChatGroupConsumer

websocket_urlpatterns = [
    re_path('ws/chat/users/', UserChatConsumer.as_asgi()),
    re_path(r'ws/chat/group/(?P<username>\w+)/$', ChatGroupConsumer.as_asgi())
]
