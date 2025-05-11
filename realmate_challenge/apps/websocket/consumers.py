import json

from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f"conversation_{self.conversation_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        print(f"✅ Cliente conectado à conversa {self.conversation_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"❌ Cliente desconectado da conversa {self.conversation_id} (código: {close_code})")

    async def receive(self, text_data):
        # Não se espera mensagens do front, mas se vier, sera logado
        print(f"⚠️ Mensagem inesperada recebida do cliente: {text_data}")

    async def send_message(self, event):
        """
        Recebe um evento com uma mensagem do webhook
        e envia via WebSocket para o frontend.
        """
        try:
            message = event.get("message", {})
            if message:
                await self.send(text_data=json.dumps(message))
                print(f"📤 Mensagem enviada via WebSocket na conversa {self.conversation_id}")
            else:
                print(f"🚫 Evento recebido sem conteúdo de mensagem válido: {event}")
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem para WebSocket: {e}")
