from django.contrib import admin

from realmate_challenge.apps.conversation.models import Conversation

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'timestamp', 'last_message_at')
    search_fields = ('id',)
    list_filter = ('status',)
    readonly_fields = ('id', 'timestamp', 'last_message_at')
    ordering = ('-last_message_at',)
