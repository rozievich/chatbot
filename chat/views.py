from webpush import send_user_notification
from webpush.models import SubscriptionInfo
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, \
    RetrieveDestroyAPIView
from django.db.models import Q
from rest_framework.response import Response
from rest_framework import status

from .serializers import CustomUserModelSerializer, ChatMessageModelSerializer, ChatGroupModelSerializer, \
    ChatGroupMessageModelSerializer, GroupMemberModelSerializer
from .models import ChatMessage, ChatGroup, GroupMessage, GroupMember, CustomUser
from .permissions import OwnerBasePermission, GroupOwnerPermission


class UserModelViewSet(ModelViewSet):
    serializer_class = CustomUserModelSerializer
    queryset = CustomUser.objects.all()

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
    permission_classes = (OwnerBasePermission,)


class ChatGroupModelViewSet(ModelViewSet):
    serializer_class = ChatGroupModelSerializer
    queryset = ChatGroup.objects.all()
    permission_classes = (GroupOwnerPermission,)


class ChatGroupMessageListAPIView(ListAPIView):
    serializer_class = ChatGroupMessageModelSerializer
    queryset = GroupMessage.objects.all()


class ChatGroupMessageRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ChatGroupMessageModelSerializer
    queryset = GroupMessage.objects.all()


class GroupMemberListCreateAPIView(ListCreateAPIView):
    serializer_class = GroupMemberModelSerializer
    queryset = ChatGroup.objects.all()


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


class SendNotificationAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "send_user_id": openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required=['send_user_id']
        )
    )

    def post(self, request, *args, **kwargs):
        send_user_id = request.data.get("send_user_id")
        subscription = SubscriptionInfo.objects.filter(user__id=send_user_id).first()
        
        if not subscription:
            return Response({"message": "This user is not subscribed."}, status=status.HTTP_404_NOT_FOUND)
        
        payload = {"head": "New message", "body": f"New message for you from {request.user.username}"}
        send_user_notification(subscription.user, payload, ttl=10000, subscription_info=subscription)
        return Response({"message": "Push bildirishnoma yuborildi"})


class SaveNotificationAPIView(APIView):
    def post(self, request, *args, **kwargs):
        send_user_id = request.data.get("send_user_id")
        subscription = request.data.get("subscription")

        if not subscription or not send_user_id:
            return Response({"error": "Subscription data and user_id are required"}, status=status.HTTP_400_BAD_REQUEST)

        SubscriptionInfo.objects.create(
            user_id=send_user_id,
            endpoint=subscription['endpoint'],
            auth_key=subscription['keys']['auth'],
            p256dh_key=subscription['keys']['p256dh']
        )

        return Response({"message": "Subscription saved successfully"})
