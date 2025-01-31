from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.contrib.auth.models import User
from django.db.models import Q

from .serializers import UserModelSerializer, ChatMessageModelSerializer
from .models import ChatMessageModel
from .permissions import OwnerBasePermission



class UserModelViewSet(ModelViewSet):
    serializer_class = UserModelSerializer
    queryset = User.objects.all()


class ChatMessageListAPIView(ListAPIView):
    serializer_class = ChatMessageModelSerializer
    queryset = ChatMessageModel.objects.all()

    def get_queryset(self):
        username = self.request.user.username
        return ChatMessageModel.objects.filter(Q(from_user__username=username) | Q(to_user__username=username))


class ChatMessageRetrieveAPIView(RetrieveAPIView):
    serializer_class = ChatMessageModelSerializer
    queryset = ChatMessageModel.objects.all()
    permission_classes = (OwnerBasePermission, )
