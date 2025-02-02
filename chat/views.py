from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, RetrieveDestroyAPIView
from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserModelSerializer, ChatMessageModelSerializer, ChatGroupModelSerializer, ChatGroupMessageModelSerializer, GroupMemberModelSerializer
from .models import ChatMessage, ChatGroup, GroupMessage, GroupMember
from .permissions import OwnerBasePermission, GroupOwnerPermission



class UserModelViewSet(ModelViewSet):
    serializer_class = UserModelSerializer
    queryset = User.objects.all()

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.is_active = False
        user.save()
        return Response({"message": "User deactivated, token is now invalid"}, status=status.HTTP_204_NO_CONTENT)


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


class GroupMemberListCreateAPIView(ListCreateAPIView):
    serializer_class = GroupMemberModelSerializer
    queryset = GroupMember.objects.all()


class GroupMemberRetrieveDestroyAPIView(RetrieveDestroyAPIView):
    serializer_class = GroupMemberModelSerializer
    queryset = GroupMember.objects.all()
    lookup_field = "group_id"

    def delete(self, request, *args, **kwargs):
        group_id = kwargs.get('group_id')
        group_info = GroupMember.objects.filter(user=request.user, group=group_id).first()

        if not group_info:
            return Response({"message": "You are not a member of this group."}, status=status.HTTP_404_NOT_FOUND)
        
        group_info.delete()
        return Response({"message": "You have successfully left the group."}, status=status.HTTP_204_NO_CONTENT)
