from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserModelViewSet, ChatMessageListAPIView, ChatMessageRetrieveAPIView


router = DefaultRouter()
router.register(f"", UserModelViewSet, basename="users")


urlpatterns = [
    path('messages/', ChatMessageListAPIView.as_view(), name="all_messages"),
    path('message/<int:pk>/', ChatMessageRetrieveAPIView.as_view(), name="get_message"),
    path('', include(router.urls)),
]
