# myapp/models.py
from django.db import models


class ChatMessage(models.Model):
    message_name = models.TextField()
    message_content = models.JSONField()
    message_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message_name
      