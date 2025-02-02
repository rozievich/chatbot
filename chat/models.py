from django.db import models
from django.contrib.auth.models import User


class ChatMessage(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="send_messages", null=True)
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="received_messages", null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"
        ordering = ["-created_at"]

    def __str__(self):
        return self.message[:30] if self.message else "No message"


class ChatGroup(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    username = models.CharField(max_length=32, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chat Group"
        verbose_name_plural = "Chat Groups"
        ordering = ["-created_at"]

    def __str__(self):
        return self.username


class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Group Message"
        verbose_name_plural = "Group Messages"
        ordering = ["-created_at"]

    def __str__(self):
        return self.message[:30] if self.message else "No Message"


class GroupMember(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Group Member"
        verbose_name_plural = "Group Members"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} in {self.group.username}" if self.user else "Delete account"
