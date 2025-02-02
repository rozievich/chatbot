import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User
from django.utils import timezone

from .models import ChatMessage, GroupMessage, ChatGroup, GroupMember


class UserChatConsumer(WebsocketConsumer):
    def connect(self):
        if not self.scope["user"].is_authenticated:
            self.close()
            return

        self.sender_user = self.scope['user']
        self.accept()

    def disconnect(self, code):
        if hasattr(self, "user_chat_name"):
            async_to_sync(self.channel_layer.group_discard)(self.user_chat_name, self.channel_name)
        self.close(code=code)

    def receive(self, text_data=None):
        message_text, receiver_username = self._extract_message_data(text_data)

        if not receiver_username and not message_text:
            self.close()
            return

        receiver_user = self._get_receiver_user(receiver_username)
        if not receiver_user:
            self.close()
            return

        self.user_chat_name = self._generate_user_chat_name(receiver_user)
        self._add_user_to_channel()
        self._send_message_to_channel(message_text, receiver_user)
        self._save_message(message_text, receiver_user)

    def chat_message(self, event):
        message = event["message"]
        receiver = event['receiver']
        sender = event['sender']
        created_at = str(timezone.now())

        self.send(text_data=json.dumps(
            {"receiver": receiver, "sender": sender, "message": message, "created_at": created_at}))

    def _extract_message_data(self, text_data=None):
        """Extract message data"""
        try:
            json_data = json.loads(text_data)
            return json_data.get("message"), json_data.get('receiver_username')
        except json.JSONDecodeError:
            return None, None

    def _get_receiver_user(self, receiver_username: str):
        """Get receiver user info"""
        return User.objects.filter(username=receiver_username).first()

    def _generate_user_chat_name(self, receiver_user):
        """Generate chat channel name"""
        if receiver_user.username > self.sender_user.username:
            return f"chat_{self.sender_user}_{receiver_user.username}"
        else:
            return f"chat_{receiver_user.username}_{self.sender_user.username}"

    def _add_user_to_channel(self):
        """Add user to channel"""
        async_to_sync(self.channel_layer.group_add)(
            self.user_chat_name,
            self.channel_name
        )

    def _send_message_to_channel(self, message_text, receiver_user):
        """Send message to channel"""
        async_to_sync(self.channel_layer.group_send)(
            self.user_chat_name,
            {"type": "chat.message", "message": message_text, "sender": self.sender_user.username,
             "receiver": receiver_user.username}
        )

    def _save_message(self, message_text, receiver_user):
        """Save message to database"""
        if self.sender_user.is_authenticated and receiver_user.is_authenticated:
            ChatMessage.objects.create(from_user=self.sender_user, to_user=receiver_user, message=message_text)


class ChatGroupConsumer(WebsocketConsumer):
    def connect(self):
        """Foydalanuvchini tekshirish va chat guruhiga qo'shish"""
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            return self.close()

        group_username = self.scope['url_route']['kwargs']['username']
        self.group_info = ChatGroup.objects.filter(username=group_username).first()
        if not self.group_info:
            return self.close()

        check_user_group = GroupMember.objects.filter(group=self.group_info, user=self.user).first()
        if not check_user_group:
            return self.close()

        self.group_channel_name = f"group_{group_username}"
        async_to_sync(self.channel_layer.group_add)(
            self.group_channel_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, code):
        """Foydalanuvchini chat guruhidan chiqarish"""
        if hasattr(self, "group_channel_name"):
            async_to_sync(self.channel_layer.group_discard)(self.group_channel_name, self.channel_name)
        self.close(code=code)

    def receive(self, text_data=None, bytes_data=None):
        """Xabarlarni qabul qilish va yuborish"""
        if not text_data:
            return

        async_to_sync(self.channel_layer.group_send)(
            self.group_channel_name,
            {
                "type": "chat.message",
                "sender": self.user.username,
                "message": text_data
            }
        )

    def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        created_at = str(timezone.now())

        GroupMessage.objects.create(
            group=self.group_info,
            from_user=self.user,
            message=message,
            created_at=created_at,
            update_at=created_at
        )

        self.send(text_data=json.dumps({"sender": sender, "message": message, "created_at": created_at}))
