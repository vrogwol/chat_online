import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from django.core.asgi import get_asgi_application

import realmate_challenge.apps.websocket.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "realmate_challenge.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            realmate_challenge.apps.websocket.routing.websocket_urlpatterns
        )
    ),
})
