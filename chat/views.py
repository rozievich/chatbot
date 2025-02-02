from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.auth.models import User
from django.db.models import Q

from .serializers import UserModelSerializer, ChatMessageModelSerializer, ChatGroupModelSerializer, ChatGroupMessageModelSerializer
from .models import ChatMessage, ChatGroup, GroupMessage
from .permissions import OwnerBasePermission, GroupOwnerPermission



class UserModelViewSet(ModelViewSet):
    serializer_class = UserModelSerializer
    queryset = User.objects.all()


class ChatMessageListAPIView(ListAPIView):
    serializer_class = ChatMessageModelSerializer
    queryset = ChatMessage.objects.all()

    def get_queryset(self):
        username = self.request.user.username
        return ChatMessage.objects.filter(Q(from_user__username=username) | Q(to_user__username=username))


class ChatMessageRetrieveAPIView(RetrieveAPIView):
    serializer_class = ChatMessageModelSerializer
    queryset = ChatMessage.objects.all()
    permission_classes = (OwnerBasePermission, )


class ChatGroupModelViewSet(ModelViewSet):
    serializer_class = ChatGroupModelSerializer
    queryset = ChatGroup.objects.all()
    permission_classes = (GroupOwnerPermission, )


class ChatGroupMessageListAPIView(ListAPIView):
    serializer_class = ChatGroupMessageModelSerializer
    queryset = GroupMessage.objects.all()


class ChatGroupMessageRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ChatGroupMessageModelSerializer
    queryset = GroupMessage.objects.all()
