from drf_spectacular.utils import extend_schema

from django.shortcuts import render, get_object_or_404

from rest_framework import viewsets

from .models import Conversation
from .serializers import ConversationSerializer


@extend_schema(
    summary="Gerenciar conversas",
    description=(
        "Endpoint para listar, criar e acessar conversas pelo ID. "
        "Cada conversa possui status OPEN ou CLOSED e registra a última mensagem recebida."
    ),
    tags=["Conversas"]
)
class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer

# Lista todas as conversas
def conversation_list_view(request):
    conversations = Conversation.objects.all().order_by('-last_message_at', '-timestamp')
    return render(request, "realmate_challenge/conversations.html", {
        "conversations": conversations
    })

# Detalha uma conversa e suas mensagens
def conversation_detail_view(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    messages = conversation.messages.all().order_by('timestamp')
    return render(request, "realmate_challenge/conversation_detail.html", {
        "conversation": conversation,
        "messages": messages
    })

#  chat ao vivo

def live_conversation_view(request, pk):
    conversation = get_object_or_404(Conversation, pk=pk)
    messages = conversation.messages.order_by("timestamp")
    return render(request, "realmate_challenge/chat.html", {
        "conversation_id": conversation.id,
        "messages": messages
    })

