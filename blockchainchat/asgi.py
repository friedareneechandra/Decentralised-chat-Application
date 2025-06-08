"""
ASGI config for blockchainchat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chatapp.routing  # Make sure this file exists and contains websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blockchainchat.settings')

# Initialize Django ASGI application early to ensure model loading
django_asgi_app = get_asgi_application()

# Define the ASGI application
application = ProtocolTypeRouter({
    # Handle traditional HTTP requests
    "http": django_asgi_app,

    # Handle WebSocket connections with authentication
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chatapp.routing.websocket_urlpatterns
        )
    ),
})








