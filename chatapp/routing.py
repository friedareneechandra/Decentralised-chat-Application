'''from django.urls import re_path
from .consumers import ChatConsumer  # Ensure consumers.py exists and ChatConsumer is defined

websocket_urlpatterns = [
    re_path(r'^ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
]'''
'''from django.urls import re_path
from . import consumers  # Ensure consumers.py exists

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]'''

# chatapp/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]








