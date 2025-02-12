import json
import redis

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone

from .models import ChatMessage, GroupMessage, ChatGroup, CustomUser
from .utils import encrypt_message_and_file, decrypt_message_and_file

redis_client = redis.StrictRedis(host='127.0.0.1', port=6379, db=0, decode_responses=True)


class UserChatConsumer(WebsocketConsumer):
    def connect(self):
        if not self.scope["user"].is_authenticated:
            self.close()
            return

        self.sender_user = self.scope['user']
        self._check_user_online()
        self._add_user_to_channel()
        self.accept()
        self._delivery_user_messages()

    def disconnect(self, code):
        self._update_last_online()
        if hasattr(self, "user_chat_name"):
            async_to_sync(self.channel_layer.group_discard)(self.user_chat_name, self.channel_name)
        self.close(code=code)

    def receive(self, text_data=None):
        message_text, receiver_username, file_url = self._extract_message_data(text_data)

        if not receiver_username and not (message_text or file_url):
            self.close()
            return

        receiver_user = self._get_receiver_user(receiver_username)
        if not receiver_user or receiver_user == self.sender_user:
            self.close()
            return

        self.user_chat_name = self._generate_user_chat_name(receiver_user)
        self._send_message_to_channel(message_text, file_url, receiver_user)
        self._save_message(message_text, file_url, receiver_user)

    def chat_message(self, event):
        message = event["message"]
        receiver = event['receiver']
        sender = event['sender']
        file_url = event['file_url']
        created_at = str(timezone.now())

        self.send(text_data=json.dumps(
            {"receiver": receiver, "sender": sender, "message": message, "file_url": file_url, "created_at": created_at}))

    def _update_last_online(self):
        online_user = redis_client.sismember("online_users", self.sender_user.id)
        if online_user:
            redis_client.srem("online_users", self.sender_user.id)
            CustomUser.objects.filter(id=self.sender_user.id).update(last_online=timezone.now())

    def _check_user_online(self):
        online_user = redis_client.sismember("online_users", self.sender_user.id)
        if not online_user:
            redis_client.sadd("online_users", self.sender_user.id)

    def _extract_message_data(self, text_data=None):
        """Extract message data"""
        try:
            json_data = json.loads(text_data)
            return json_data.get('message'), json_data.get('username'), json_data.get('file_url')
        except json.JSONDecodeError:
            return None, None, None

    def _get_receiver_user(self, receiver_username: str):
        """Get receiver user info"""
        return CustomUser.objects.filter(username=receiver_username).first()

    def _generate_user_chat_name(self, receiver_user):
        """Generate chat channel name"""
        if receiver_user.username > self.sender_user.username:
            return f"chat_{self.sender_user}_{receiver_user.username}"
        else:
            return f"chat_{receiver_user.username}_{self.sender_user.username}"

    def _add_user_to_channel(self):
        """Add user to channel"""
        async_to_sync(self.channel_layer.group_add)(
            f"private_chat_{self.sender_user.id}",
            self.channel_name
        )

    def _send_message_to_channel(self, message_text, file_url, receiver_user):
        """Send message to channel"""
        async_to_sync(self.channel_layer.group_send)(
            f"private_chat_{receiver_user.id}",
            {"type": "chat.message", "message": message_text, "file_url": file_url, "sender": self.sender_user.username,
             "receiver": receiver_user.username}
        )

    def _save_message(self, message_text, file_url, receiver_user):
        """Save message to database"""
        if self.sender_user.is_authenticated and receiver_user.is_authenticated:
            client_status = redis_client.sismember("online_users", receiver_user.id)
            encrypt_text = encrypt_message_and_file(message_text)
            if client_status:
                ChatMessage.objects.create(from_user=self.sender_user, to_user=receiver_user, message=encrypt_text, file=file_url, is_delivery=True)
            else:
                ChatMessage.objects.create(from_user=self.sender_user, to_user=receiver_user, message=encrypt_text, file=file_url)

    def _delivery_user_messages(self):
        undelivery_messages = ChatMessage.objects.filter(to_user=self.sender_user, is_delivery=False)
        for msg in undelivery_messages:
            sh_message_text = decrypt_message_and_file(msg.message)
            self.send(text_data=json.dumps(
                {
                    "receiver": self.sender_user.username,
                    "sender": msg.from_user.username,
                    "created_at": str(msg.created_at),
                    "message": sh_message_text,
                    "file_url": msg.file.url if msg.file else ""
                }
            ))
            msg.is_delivery = True
            msg.save()



class ChatGroupConsumer(WebsocketConsumer):
    def connect(self):
        """Foydalanuvchini tekshirish va chat guruhiga qo'shish"""
        self.user = self.scope.get("user")
        if not self.user or not self.user.is_authenticated:
            return self.close()

        group_username = self.scope['url_route']['kwargs']['username']
        self.group_info = ChatGroup.objects.filter(username=group_username).first()

        if not self.group_info or not self.group_info.members.filter(id=self.user.id).exists():
            return self.close()

        self._check_user_online()
        self.group_channel_name = f"group_{group_username}"
        async_to_sync(self.channel_layer.group_add)(self.group_channel_name, self.channel_name)
        self.accept()

        self._delivery_group_messages()

    def disconnect(self, code):
        """Foydalanuvchini chat guruhidan chiqarish"""
        self._update_last_online()
        if hasattr(self, "group_channel_name"):
            async_to_sync(self.channel_layer.group_discard)(self.group_channel_name, self.channel_name)
        self.close(code=code)

    def receive(self, text_data=None, bytes_data=None):
        """Xabarlarni qabul qilish va yuborish"""
        message_text, file_url = self._extract_message_data(text_data)
        if not message_text and not file_url:
            return

        self.message = self._save_message_database(message_text, file_url)
        async_to_sync(self.channel_layer.group_send)(
            self.group_channel_name,
            {
                "type": "chat.message",
                "message_id": self.message.id,
                "sender": self.message.from_user.username,
                "message": self.message.message,
                "created_at": str(self.message.created_at),
                "update_at": str(self.message.update_at)
            }
        )

    def chat_message(self, event):
        self.send(text_data=json.dumps(
            {
                "message_id": event['message_id'],
                "sender": event['sender'],
                "message": event['message'],
                "created_at": event['created_at'],
                "update_at": event['update_at']
            })
        )
        self._mark_message_delivered()

    def _save_message_database(self, message: str, file_url: str):
        """Xabarni saqlash va unga yetkazilganini belgilash"""
        sh_message_text = encrypt_message_and_file(message)
        group_message = GroupMessage.objects.create(group=self.group_info, from_user=self.user, message=sh_message_text, file=file_url)
        return group_message

    def _mark_message_delivered(self):
        """Xabar foydalanuvchiga yetib borgandan keyin uni yetkazilgan deb belgilash"""
        if self.message and not self.message.is_delivery.filter(id=self.user.id).exists():
            self.message.is_delivery.add(self.user)

    def _check_user_online(self):
        online_user = redis_client.sismember("online_users", self.user.id)
        if not online_user:
            redis_client.sadd("online_users", self.user.id)    

    def _update_last_online(self):
        online_user = redis_client.sismember("online_users", self.user.id)
        if online_user:
            redis_client.srem("online_users", self.user.id)
            CustomUser.objects.filter(id=self.user.id).update(last_online=timezone.now())

    def _delivery_group_messages(self):
        """Delivery message"""
        undelivery_messages = GroupMessage.objects.filter(group=self.group_info).exclude(is_delivery=self.user)
        if not undelivery_messages.exists():
            return

        message_data = [{
            "message_id": msg.id,
            "sender": msg.from_user.username,
            "message": decrypt_message_and_file(msg.message),
            "file_url": msg.file.url,
            "created_at": str(msg.created_at),
            "update_at": str(msg.update_at)
        } for msg in undelivery_messages]

        self.send(text_data=json.dumps(message_data))
        for msg in undelivery_messages:
            msg.is_delivery.add(self.user)

    def _extract_message_data(self, text_data=None):
        """Extract message data"""
        try:
            json_data = json.loads(text_data)
            return json_data.get("message"), json_data.get("file_url")
        except json.JSONDecodeError:
            return None, None
