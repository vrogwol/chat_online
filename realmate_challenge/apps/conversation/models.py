import uuid

from django.utils import timezone
from django.db import models

# conversa pode ter um timestamp de criação maior que o timestamp das mensagens e isso não gera conflito (validar regra de negócios)
class Conversation(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('CLOSED', 'Closed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    last_message_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.id} ({self.status})"

    class Meta:
        ordering = ['-timestamp']
