# chatapp/utils.py
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

def get_online_users(minutes=5):
    now = timezone.now()
    threshold = now - timedelta(minutes=minutes)
    return User.objects.filter(last_login__gte=threshold)
