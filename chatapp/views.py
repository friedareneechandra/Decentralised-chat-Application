from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.http import JsonResponse
from .models import Room, Message
from .utils import get_online_users


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request, room_name=None):
    list(messages.get_messages(request))

    users = User.objects.all()
    rooms = Room.objects.all()
    online_usernames = []  # populate using get_online_users() if available
    request_user = request.user

    if request.method == "POST":
        room_name_form = request.POST.get('room', '').strip()
        pin = request.POST.get('pin', '').strip()

        room = Room.objects.filter(room_name=room_name_form).first()

        if room:
            if room.room_pin and not room.check_pin(pin):
                messages.error(request, "Incorrect PIN for the room.")
                return redirect('dashboard_with_room', room_name=room_name_form)

            request.session[f'pin_verified_{room_name_form}'] = True
            return redirect('chat_room', room_name=room_name_form)
        else:
            new_room = Room(room_name=room_name_form, owner=request.user)
            if pin:
                new_room.set_pin(pin)
            new_room.save()
            request.session[f'pin_verified_{room_name_form}'] = True
            messages.success(request, f"Room '{room_name_form}' created successfully!")
            return redirect('chat_room', room_name=room_name_form)

    context = {
        'users': users,
        'rooms': rooms,
        'online_usernames': online_usernames,
        'request_user': request_user,
        'room_name_from_url': room_name,
    }
    return render(request, 'chatapp/dashboard.html', context)


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not username or not password or not password2:
            messages.error(request, "Please fill out all fields.")
            return render(request, 'chatapp/register.html')

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'chatapp/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'chatapp/register.html')

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Registration successful. You can now log in.")
        return redirect('login')

    return render(request, 'chatapp/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'chatapp/login1.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def chat_room(request, room_name):
    room = get_object_or_404(Room, room_name=room_name)

    if room.room_pin and not request.session.get(f'pin_verified_{room_name}'):
        messages.error(request, "Access denied. Join with correct PIN.")
        return redirect('dashboard')

    chats = Message.objects.filter(room=room).order_by('timestamp')

    return render(request, 'chatapp/chat_room.html', {
        'room_name': room.room_name,
        'username': request.user.username,
        'chats': chats,
    })


@login_required
def create_room_view(request):
    if request.method == 'POST':
        room_name = request.POST.get('room', '').strip()
        pin = request.POST.get('pin', '').strip()

        if not room_name:
            messages.error(request, "Room name is required.")
            return redirect('dashboard')

        try:
            room = Room.objects.get(room_name=room_name)

            if room.room_pin:
                if not pin:
                    messages.error(request, "Please enter the PIN for the existing room.")
                    return redirect('dashboard')

                if not room.check_pin(pin):
                    messages.error(request, "Incorrect PIN for the room.")
                    return redirect('dashboard')

            request.session[f'pin_verified_{room_name}'] = True
            messages.success(request, f"Joined room '{room_name}'.")
            return redirect('chat_room', room_name=room_name)

        except Room.DoesNotExist:
            new_room = Room(room_name=room_name, owner=request.user)
            if pin:
                new_room.set_pin(pin)
            new_room.save()

            request.session[f'pin_verified_{room_name}'] = True
            messages.success(request, f"Room '{room_name}' created successfully.")
            return redirect('chat_room', room_name=room_name)

    return render(request, 'chatapp/create_room1.html')


@login_required
def join_room_view(request):
    if request.method == 'POST':
        room_name = request.POST.get('room_name')
        pin = request.POST.get('pin')

        try:
            room = Room.objects.get(room_name=room_name)
            if room.check_pin(pin):
                request.session[f'pin_verified_{room_name}'] = True
                return redirect('chat_room', room_name=room_name)
            else:
                messages.error(request, "Incorrect PIN.")
        except Room.DoesNotExist:
            messages.error(request, "Room not found.")

    return redirect('dashboard')


@login_required
def save_message(request, room_name, username):
    if request.method == 'POST':
        room = get_object_or_404(Room, room_name=room_name)
        message_text = request.POST.get('message')
        message = Message(room=room, sender=username, message=message_text, message_hash="")  # Optional: add hash logic
        message.save()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"}, status=400)


@login_required
def clear_chat(request, room_name):
    if request.method == "POST":
        Message.objects.filter(room__room_name=room_name).delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"}, status=400)
