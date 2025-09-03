import uuid
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from realmate_challenge.apps.conversation.models import Conversation
from realmate_challenge.apps.message.models import Message


class Command(BaseCommand):
    help = 'Popula o banco de dados com conversas e mensagens sobre academia'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando população do banco de dados...')
        
        # Limpar dados existentes se necessário
        if self.confirm_clear():
            Message.objects.all().delete()
            Conversation.objects.all().delete()
            self.stdout.write(self.style.WARNING('Dados existentes removidos.'))
        
        # Criar conversas com mensagens sobre academia
        self.create_gym_conversations()
        
        self.stdout.write(
            self.style.SUCCESS('População do banco concluída com sucesso!')
        )
    
    def confirm_clear(self):
        """Pergunta se deve limpar dados existentes"""
        if Conversation.objects.exists() or Message.objects.exists():
            response = input('Existem dados no banco. Deseja limpar? (s/N): ')
            return response.lower() in ['s', 'sim', 'y', 'yes']
        return False
    
    def create_gym_conversations(self):
        """Cria conversas sobre academia com mensagens realistas"""
        
        # Conversa 1: Informações sobre planos
        conv1_id = uuid.uuid4()
        conv1_time = timezone.now() - timedelta(days=2)
        
        conv1 = Conversation.objects.create(
            id=conv1_id,
            status='CLOSED',
            timestamp=conv1_time
        )
        
        messages_conv1 = [
            ('RECEIVED', 'Olá! Gostaria de saber sobre os planos da academia.', 0),
            ('SENT', 'Olá! Temos 3 planos disponíveis: Básico (R$ 89/mês), Premium (R$ 129/mês) e VIP (R$ 179/mês).', 2),
            ('RECEIVED', 'Qual a diferença entre eles?', 5),
            ('SENT', 'O Básico inclui musculação e cardio. O Premium adiciona aulas coletivas. O VIP tem personal trainer incluso.', 8),
            ('RECEIVED', 'O VIP inclui quantas sessões de personal?', 12),
            ('SENT', 'São 8 sessões mensais de personal trainer, além de avaliação física completa.', 15),
            ('RECEIVED', 'Perfeito! Vou pensar e retorno. Obrigado!', 18),
            ('SENT', 'Por nada! Estamos aqui quando precisar. Tenha um ótimo dia!', 20)
        ]
        
        self.create_messages(conv1, messages_conv1, conv1_time)
        
        # Conversa 2: Horários de funcionamento
        conv2_id = uuid.uuid4()
        conv2_time = timezone.now() - timedelta(days=1, hours=8)
        
        conv2 = Conversation.objects.create(
            id=conv2_id,
            status='OPEN',
            timestamp=conv2_time
        )
        
        messages_conv2 = [
            ('RECEIVED', 'Bom dia! Quais são os horários de funcionamento?', 0),
            ('SENT', 'Bom dia! Funcionamos de segunda a sexta das 5h às 23h, sábados das 7h às 20h e domingos das 8h às 18h.', 3),
            ('RECEIVED', 'E as aulas coletivas? Têm horários específicos?', 7),
            ('SENT', 'Sim! Temos aulas de spinning às 7h, 12h e 19h. Zumba às 18h. Pilates às 9h e 17h. Yoga às 8h e 20h.', 10),
            ('RECEIVED', 'Preciso agendar as aulas ou posso chegar na hora?', 15),
            ('SENT', 'Para spinning e pilates é necessário agendamento pelo app. Zumba e yoga são por ordem de chegada.', 18)
        ]
        
        self.create_messages(conv2, messages_conv2, conv2_time)
        
        # Conversa 3: Equipamentos e estrutura
        conv3_id = uuid.uuid4()
        conv3_time = timezone.now() - timedelta(hours=4)
        
        conv3 = Conversation.objects.create(
            id=conv3_id,
            status='OPEN',
            timestamp=conv3_time
        )
        
        messages_conv3 = [
            ('RECEIVED', 'Oi! Vocês têm piscina e sauna?', 0),
            ('SENT', 'Olá! Sim, temos piscina aquecida e sauna seca. Ambas estão incluídas nos planos Premium e VIP.', 2),
            ('RECEIVED', 'E área de musculação? É bem equipada?', 5),
            ('SENT', 'Temos mais de 200 equipamentos! Área completa de musculação, cardio com TVs individuais e zona funcional.', 8),
            ('RECEIVED', 'Que legal! E vestiários?', 12),
            ('SENT', 'Vestiários amplos com armários, chuveiros quentes e área de descanso. Também temos estacionamento gratuito.', 15)
        ]
        
        self.create_messages(conv3, messages_conv3, conv3_time)
        
        # Conversa 4: Nutrição e acompanhamento
        conv4_id = uuid.uuid4()
        conv4_time = timezone.now() - timedelta(hours=1)
        
        conv4 = Conversation.objects.create(
            id=conv4_id,
            status='OPEN',
            timestamp=conv4_time
        )
        
        messages_conv4 = [
            ('RECEIVED', 'Vocês oferecem acompanhamento nutricional?', 0),
            ('SENT', 'Sim! Temos nutricionista 3x por semana. Consultas incluídas no plano VIP, demais planos com desconto de 50%.', 3),
            ('RECEIVED', 'E avaliação física? Como funciona?', 8),
            ('SENT', 'Fazemos bioimpedância, medidas corporais e teste de flexibilidade. Reavaliação a cada 3 meses.', 12),
            ('RECEIVED', 'Vocês têm lanchonete ou área de alimentação?', 16),
            ('SENT', 'Temos uma lanchonete com opções saudáveis: sucos naturais, sanduíches integrais, saladas e suplementos.', 20)
        ]
        
        self.create_messages(conv4, messages_conv4, conv4_time)
        
        self.stdout.write(f'Criadas {Conversation.objects.count()} conversas com {Message.objects.count()} mensagens.')
    
    def create_messages(self, conversation, messages_data, base_time):
        """Cria mensagens para uma conversa"""
        last_message_time = base_time
        
        for direction, content, minutes_offset in messages_data:
            message_time = base_time + timedelta(minutes=minutes_offset)
            
            Message.objects.create(
                id=uuid.uuid4(),
                conversation=conversation,
                direction=direction,
                content=content,
                timestamp=message_time
            )
            
            if message_time > last_message_time:
                last_message_time = message_time
        
        # Atualizar última mensagem da conversa
        conversation.last_message_at = last_message_time
        conversation.save(update_fields=['last_message_at'])