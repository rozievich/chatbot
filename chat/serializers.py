import re
from rest_framework.serializers import ModelSerializer, CharField, DateTimeField, BooleanField, HiddenField, \
    CurrentUserDefault, PrimaryKeyRelatedField, StringRelatedField
from rest_framework.exceptions import ValidationError

from .models import ChatMessage, ChatGroup, GroupMessage, CustomUser
from .consumers import redis_client
from .utils import decrypt_message_and_file


class CustomUserModelSerializer(ModelSerializer):
    username = CharField(max_length=32, default="string")
    password = CharField(max_length=250, write_only=True, default="string")
    date_joined = DateTimeField(read_only=True)
    is_staff = BooleanField(read_only=True)
    is_active = BooleanField(read_only=True)
    is_superuser = BooleanField(read_only=True)

    class Meta:
        model = CustomUser
        exclude = "groups", "user_permissions"

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, instance):
        represantation = super().to_representation(instance)
        user_status = redis_client.sismember("online_users", represantation['id'])
        if user_status:
            represantation['last_online'] = "online"
        represantation['groups'] = [{"id": group.id, "name": group.name, "username": group.username} for group in instance.chat_groups.all()]
        return represantation


class ChatMessageModelSerializer(ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = "__all__"

    def validate(self, attrs):
        message = attrs.get('message')
        file = attrs.get('file')

        if not message and not file:
            raise ValidationError("Sending a message or file is mandatory!")
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['message'] = decrypt_message_and_file(representation['message'])
        return representation


class ChatGroupModelSerializer(ModelSerializer):
    owner = HiddenField(default=CurrentUserDefault())
    members = PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True)

    class Meta:
        model = ChatGroup
        fields = "id", "name", "username", "owner", "created_at", "members"

    def validate_username(self, username):
        if not re.match(r"^[a-z0-9_]+$", username) or not (5 <= len(username) <= 32):
            raise ValidationError({"message": "The username must be at least 5 characters and at most 32 characters long and can contain letters, numbers, and _."})
        return username


class ChatGroupMessageModelSerializer(ModelSerializer):
    is_delivery = StringRelatedField(many=True)

    class Meta:
        model = GroupMessage
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['message'] = decrypt_message_and_file(representation['message'])
        return representation
