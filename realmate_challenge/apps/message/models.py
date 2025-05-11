import uuid

from django.utils import timezone
from django.db import models

from realmate_challenge.apps.conversation.models import Conversation



class Message(models.Model):
    DIRECTION_CHOICES = (
        ('SENT', 'Sent'),
        ('RECEIVED', 'Received'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.PROTECT)
    direction = models.CharField(max_length=10, choices=DIRECTION_CHOICES)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
        
    def __str__(self):
        return f"{self.direction} - {self.content[:30]}"
    
    class Meta:
        ordering = ['timestamp']