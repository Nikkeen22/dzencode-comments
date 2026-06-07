"""
ASGI config for core project — підтримує HTTP і WebSocket.
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
import comments.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = ProtocolTypeRouter({
    # Звичайні HTTP-запити
    'http': get_asgi_application(),
    # WebSocket-запити
    'websocket': AllowedHostsOriginValidator(
        URLRouter(comments.routing.websocket_urlpatterns)
    ),
})