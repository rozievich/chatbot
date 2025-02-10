from django.contrib import admin

from .models import ChatMessage, CustomUser

# Register your models here.
admin.site.register(ChatMessage)
admin.site.register(CustomUser)
