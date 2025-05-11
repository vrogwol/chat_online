from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from realmate_challenge.apps.conversation.views import (
    ConversationViewSet,
    conversation_list_view,
    conversation_detail_view,
    live_conversation_view,
)

from realmate_challenge.apps.message.views import MessageViewSet
from realmate_challenge.webhooks.messages.views import WebhookView


# Router REST
router = DefaultRouter()
router.register("conversations", ConversationViewSet, basename="conversation")
router.register("messages", MessageViewSet, basename="message")

# URL Patterns
urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API REST
    path("", include(router.urls)),
    path("webhook/", WebhookView.as_view(), name="webhook"),

    # Frontend com Django Templates
    path("conversas/", conversation_list_view, name="conversation_list"),
    path("conversas/<uuid:pk>/", conversation_detail_view, name="conversation_detail"),

    # DIFERENCIAL: Chat ao vivo 
    # com WebSocket e Channels 
    # comando poetry run runserver reescrito para rodar o ASGI
    path("conversas/<uuid:pk>/ao-vivo/", live_conversation_view, name="live_conversation"),
]

urlpatterns += [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]
