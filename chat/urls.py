from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserModelViewSet,
    ChatMessageListAPIView,
    ChatMessageRetrieveAPIView,
    ChatGroupModelViewSet,
    ChatGroupMessageListAPIView,
    ChatGroupMessageRetrieveUpdateDestroyAPIView,
    GroupMemberDestroyAPIView,
    SendNotificationAPIView,
    SaveNotificationAPIView,
    GroupMemberAPIView
)

router = DefaultRouter()

router.register("groups", ChatGroupModelViewSet, basename="groups")
router.register("users", UserModelViewSet, basename="users")

urlpatterns = [
    path('push/send/', SendNotificationAPIView.as_view(), name="save_push_notification"),
    path('push/save/', SaveNotificationAPIView.as_view(), name="save_push_notification"),
    path('group-member/', GroupMemberAPIView.as_view(), name="group_member_create"),
    path('group-member/<int:group_id>/', GroupMemberDestroyAPIView.as_view(), name="group_member_delete"),
    path('group-messages/', ChatGroupMessageListAPIView.as_view(), name="get_group_messages"),
    path('group-messages/<int:pk>/', ChatGroupMessageRetrieveUpdateDestroyAPIView.as_view(), name="group_messages"),
    path('messages/', ChatMessageListAPIView.as_view(), name="all_messages"),
    path('messages/<int:pk>/', ChatMessageRetrieveAPIView.as_view(), name="get_message"),
    path('', include(router.urls)),
]
