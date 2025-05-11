from drf_spectacular.utils import extend_schema

from django.utils import timezone
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.response import Response

from realmate_challenge.apps.conversation.models import Conversation

from .serializers import MessageSerializer
from .models import Message


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    @extend_schema(
        summary="Criar nova mensagem",
        description=(
            "Cria uma nova mensagem vinculada a uma conversa existente. "
            "Se a conversa estiver com status 'CLOSED', o envio será rejeitado com erro 400."
        ),
        tags=["Mensagens"]
    )
    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get("conversation")
        conversation = get_object_or_404(Conversation, id=conversation_id)

        if conversation.status == "CLOSED":
            return Response({"detail": "This conversation is closed."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Atualiza a última mensagem
        conversation.last_message_at = timezone.now()
        conversation.save(update_fields=["last_message_at"])

        return super().create(request, *args, **kwargs)
