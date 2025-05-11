from django.contrib import admin

from realmate_challenge.apps.message.models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'direction', 'timestamp')
    search_fields = ('content',)
    list_filter = ('direction', 'timestamp')
    ordering = ('-timestamp',)
    readonly_fields = ('id', 'conversation', 'direction', 'content', 'timestamp')
