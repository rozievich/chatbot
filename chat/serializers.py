from rest_framework.serializers import ModelSerializer, CharField, DateTimeField, BooleanField
from django.contrib.auth.models import User

from .models import ChatMessageModel


class UserModelSerializer(ModelSerializer):
    username = CharField(max_length=32, default="string")
    password = CharField(max_length=250, write_only=True, default="string")
    date_joined = DateTimeField(read_only=True)
    is_staff = BooleanField(read_only=True)
    is_active = BooleanField(read_only=True)
    is_superuser = BooleanField(read_only=True)

    class Meta:
        model = User
        exclude = "groups", "user_permissions"


class ChatMessageModelSerializer(ModelSerializer):
    class Meta:
        model = ChatMessageModel
        fields = "__all__"
