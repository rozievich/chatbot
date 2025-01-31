from django.db import models
from django.contrib.auth.models import User


class ChatMessageModel(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, related_name="send_messages", default="Deleted account")
    to_user = models.ForeignKey(User, on_delete=models.SET_DEFAULT, related_name="received_messages", default="Deleted account")
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.message[:30]
