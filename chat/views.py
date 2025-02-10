from webpush import send_user_notification
from webpush.models import SubscriptionInfo
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from django.core.files.storage import default_storage

from .serializers import CustomUserModelSerializer, ChatMessageModelSerializer, ChatGroupModelSerializer, ChatGroupMessageModelSerializer
from .models import ChatMessage, ChatGroup, GroupMessage, CustomUser
from .permissions import OwnerBasePermission, GroupOwnerPermission
from config import settings


class UserModelViewSet(ModelViewSet):
    serializer_class = CustomUserModelSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated, )

    def delete(self, request, *args, **kwargs):
        user = request.user
        user.is_active = False
        user.save()
        return Response({"message": "User deactivated, token is now invalid"}, status=status.HTTP_204_NO_CONTENT)


class ChatMessageListAPIView(ListAPIView):
    serializer_class = ChatMessageModelSerializer
    queryset = ChatMessage.objects.all()
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        username = self.request.user.username
        return ChatMessage.objects.filter(Q(from_user__username=username) | Q(to_user__username=username))


class ChatMessageRetrieveAPIView(RetrieveAPIView):
    serializer_class = ChatMessageModelSerializer
    queryset = ChatMessage.objects.all()
    permission_classes = (IsAuthenticated, OwnerBasePermission)


class ChatGroupModelViewSet(ModelViewSet):
    serializer_class = ChatGroupModelSerializer
    queryset = ChatGroup.objects.all()
    permission_classes = (IsAuthenticated, GroupOwnerPermission)


class ChatGroupMessageListAPIView(ListAPIView):
    serializer_class = ChatGroupMessageModelSerializer
    queryset = GroupMessage.objects.all()
    permission_classes = (IsAuthenticated, )


class ChatGroupMessageRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = ChatGroupMessageModelSerializer
    queryset = GroupMessage.objects.all()
    permission_classes = (IsAuthenticated, )


class GroupMemberAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "group_id": openapi.Schema(type=openapi.TYPE_INTEGER)
            },
            required=['group_id']
        )
    )

    def post(self, request, *args, **kwargs):
        group_id = request.data.get("group_id")
        
        group_info = ChatGroup.objects.filter(pk=group_id).first()
        if not group_info:
            return Response({"message": "Group not found!"}, status=status.HTTP_404_NOT_FOUND)
        
        if group_info.members.filter(id=request.user.id).exists():
            return Response({"message": "The user is already subscribed to this group!"}, status=status.HTTP_409_CONFLICT)
        
        group_info.members.add(request.user)
        return Response({"message": "You have successfully subscribed to the group!"}, status=status.HTTP_200_OK)


class GroupMemberDestroyAPIView(DestroyAPIView):
    serializer_class = ChatGroupModelSerializer
    queryset = ChatGroup.objects.all()
    permission_classes = (IsAuthenticated, )

    def delete(self, request, *args, **kwargs):
        group_id = kwargs.get('group_id')
        group_info = ChatGroup.objects.filter(pk=group_id).first()

        if not group_info:
            return Response({"message": "Group not found!"}, status=status.HTTP_404_NOT_FOUND)

        if not group_info.members.filter(id=request.user.id).exists():
            return Response({"message": "The user is not subscribed to this group!"}, status=status.HTTP_404_NOT_FOUND)
        
        group_info.members.remove(request.user)
        return Response({"message": "You have successfully left the group."}, status=status.HTTP_204_NO_CONTENT)


class SendNotificationAPIView(APIView):
    permission_classes = (IsAuthenticated, )

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
    permission_classes = (IsAuthenticated, )

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


class UploadFileAPIView(APIView):
    parser_classes = (FormParser, MultiPartParser)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "file",
                openapi.IN_FORM,
                description="Downloadable file",
                type=openapi.TYPE_FILE,
                required=True
            ),
            openapi.Parameter(
                "chat_type",
                openapi.IN_FORM,
                description="Chat type: 'private' or 'group'",
                type=openapi.TYPE_STRING,
                enum=["private", "group"],
                required=True
            )
        ]
    )

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        chat_type = request.data.get("chat_type")

        if not file:
            return Response({'error': 'No file uploaded'}, status=400)
        
        if chat_type not in ["private", "group"]:
            return Response({"error": "The chat_type field must be 'private' or 'group'!"}, status=status.HTTP_400_BAD_REQUEST)

        file_path = default_storage.save(f"{chat_type}_files/{file.name}", file)
        file_url = f"{file_path}"
        return Response({"file_url": file_url}, status=status.HTTP_201_CREATED)
