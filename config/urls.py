from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

schema_view = get_schema_view(
    openapi.Info(
        title="ChatBot API",
        default_version="v1.0",
        description="ChatBot for users to communicate in real time",
        terms_of_service="https://github.com/rozievich/chatbot",
        contact=openapi.Contact(email="oybekrozievich@gmail.com"),
        license=openapi.License(name="BSD License")
    ),
    public=True,
    permission_classes=(AllowAny,)
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('chat/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('chat/token/verify/', TokenVerifyView.as_view(), name="token_verify"),
    path('swdoc/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/', include('chat.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
