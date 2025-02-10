from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.validators import ValidationError


class CustomUser(AbstractUser):
    last_online = models.DateTimeField(auto_now=True)


class ChatMessage(models.Model):
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="send_messages")
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="chat_files/", blank=True, null=True)
    is_delivery = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        ordering = ["-created_at"]
    
    def clean(self):
        if not self.message and not self.file:
            raise ValidationError("Sending a message or file is mandatory!")

    def __str__(self):
        return self.message[:30] if self.message else "No message"


class ChatGroup(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    username = models.CharField(max_length=32, unique=True)
    members = models.ManyToManyField(CustomUser, related_name="chat_groups")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chat Group"
        verbose_name_plural = "Chat Groups"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username


class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="group_files/", blank=True, null=True)
    is_delivery = models.ManyToManyField(CustomUser, related_name="delivery_messages", blank=True)
    is_read = models.ManyToManyField(CustomUser, related_name="read_messages", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Group Message"
        verbose_name_plural = "Group Messages"
        ordering = ["-created_at"]
    
    def clean(self):
        if not self.message and not self.file:
            raise ValidationError("Sending a message or file is mandatory!")

    def __str__(self):
        return self.message[:30] if self.message else "No Message"
