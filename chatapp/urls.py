from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
   # path('chat/<str:room_name>/', views.chat_room, name='chat_room'),  # main chat view
    path('chat/room/<str:room_name>/', views.chat_room, name='chat_room'),
    path('chat/clear/<str:room_name>/', views.clear_chat, name='clear_chat'),
]

