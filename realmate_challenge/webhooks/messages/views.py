import uuid
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from drf_spectacular.utils import extend_schema, OpenApiExample

from django.utils.dateparse import parse_datetime

from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from realmate_challenge.apps.conversation.models import Conversation
from realmate_challenge.apps.message.models import Message


@extend_schema(
    summary="Receber eventos de atendimento",
    description=(
        "Recebe webhooks de eventos externos.\n\n"
        "**Suporta:**\n"
        "- `NEW_CONVERSATION`\n"
        "- `NEW_MESSAGE`\n"
        "- `CLOSE_CONVERSATION`\n\n"
        "Cria ou atualiza os registros no banco e retorna status apropriado.\n"
        "Evita qualquer erro 500 com tratamento completo de exceções."
    ),
    request=OpenApiExample(
        name="Exemplo de NEW_MESSAGE",
        value={
            "type": "NEW_MESSAGE",
            "timestamp": "2025-02-21T10:20:44.349308",
            "data": {
                "id": "16b63b04-60de-4257-b1a1-20a5154abc6d",
                "direction": "SENT",
                "content": "Tudo ótimo e você?",
                "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
            }
        },
        request_only=True
    ),
    tags=["Webhook"],
    responses={
        200: OpenApiExample("Sucesso padrão", value={"detail": "Mensagem criada."}),
        201: OpenApiExample("Criado com sucesso", value={"detail": "Conversation created."}),
        400: OpenApiExample("Payload inválido", value={"detail": "Invalid payload."}),
        404: OpenApiExample("Conversa não encontrada", value={"detail": "Conversation not found."})
    }
)
class WebhookView(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        event_type = request.data.get("type")
        timestamp_str = request.data.get("timestamp")
        data = request.data.get("data")

        if not event_type or not timestamp_str or not data:
            return Response({"detail": "Campos obrigatórios faltando: 'type', 'timestamp' e 'data'."}, status=400)

        timestamp = parse_datetime(timestamp_str)
        if not timestamp:
            return Response({"detail": "Formato de timestamp inválido. Use ISO 8601."}, status=400)

        match event_type:
            case "NEW_CONVERSATION":
                return self._handle_new_conversation(data, timestamp)
            case "NEW_MESSAGE":
                return self._handle_new_message(data, timestamp)
            case "CLOSE_CONVERSATION":
                return self._handle_close_conversation(data)
            case _:
                return Response({"detail": f"Tipo de evento '{event_type}' não suportado."}, status=400)

    def _handle_new_conversation(self, data, timestamp):
        try:
            conv_id = uuid.UUID(data.get("id"))
        except Exception:
            return Response({"detail": "ID da conversa inválido (UUID malformado)."}, status=400)

        try:
            if Conversation.objects.filter(id=conv_id).exists():
                return Response({"detail": "Conversa já existe (ID duplicado)."}, status=409)
            
            conversation, created = Conversation.objects.get_or_create(
                id=conv_id,
                defaults={
                    "status": "OPEN",
                    "timestamp": timestamp,
                }
            )
            if not created:
                return Response({"detail": "Conversation already exists."}, status=200)
            return Response({"detail": "Conversation created."}, status=201)
        except Exception as e:
            return Response({"detail": f"Erro ao criar a conversa: {str(e)}"}, status=400)

    def _handle_new_message(self, data, timestamp):
        try:
            message_id = uuid.UUID(data.get("id"))
            conv_id = uuid.UUID(data.get("conversation_id"))
        except Exception:
            return Response({"detail": "IDs inválidos. Certifique-se de que são UUIDs válidos."}, status=400)

        direction = data.get("direction")
        content = data.get("content")
        if direction not in {"SENT", "RECEIVED"} or not content:
            return Response({"detail": "Direção deve ser 'SENT' ou 'RECEIVED' e conteúdo não pode ser vazio."}, status=400)

        try:
            conversation = Conversation.objects.get(id=conv_id)
        except Conversation.DoesNotExist:
            return Response({"detail": "Conversation not found."}, status=404)

        if conversation.status == "CLOSED":
            return Response({"detail": "Conversation is closed."}, status=400)
        if Message.objects.filter(id=message_id).exists():
            return Response({"detail": "Mensagem já existe (ID duplicado)."}, status=409)

        try:
            Message.objects.create(
                id=message_id,
                conversation=conversation,
                direction=direction,
                content=content,
                timestamp=timestamp,
            )

            conversation.last_message_at = timestamp
            conversation.save(update_fields=["last_message_at"])

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"conversation_{conversation.id}",
                {
                    "type": "send_message",
                    "message": {
                        "id": str(message_id),
                        "direction": direction,
                        "content": content,
                        "timestamp": timestamp.isoformat(),
                    }
                }
            )

            return Response({"detail": "Message created."}, status=201)

        except Exception as e:
            return Response({"detail": f"Erro ao salvar mensagem: {str(e)}"}, status=400)

    def _handle_close_conversation(self, data):
        try:
            conv_id = uuid.UUID(data.get("id"))
        except Exception:
            return Response({"detail": "ID inválido (UUID malformado)."}, status=400)

        try:
            conversation = Conversation.objects.get(id=conv_id)
            conversation.status = "CLOSED"
            conversation.save(update_fields=["status"])
            return Response({"detail": "Conversation closed."}, status=200)
        except Conversation.DoesNotExist:
            return Response({"detail": "Conversation not found."}, status=404)
        except Exception as e:
            return Response({"detail": f"Erro ao fechar a conversa: {str(e)}"}, status=400)
