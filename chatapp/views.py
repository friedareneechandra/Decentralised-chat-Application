from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.http import JsonResponse
from .models import *
from .utils import get_online_users



def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('login')

@login_required(login_url='login')
def dashboard(request):
    rooms = Room.objects.all()
    return render(request, 'chatapp/dashboard.html', {
        'user': request.user,
        'rooms': rooms,
    })


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not username or not password or not password2:
            messages.error(request, "Please fill out all fields.")
            return render(request, 'chatapp/register1.html')

        if password != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'chatapp/register1.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, 'chatapp/register1.html')

        User.objects.create_user(username=username, password=password)
        messages.success(request, "Registration successful. You can now log in.")
        return redirect('login')

    return render(request, 'chatapp/register1.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'chatapp/login1.html')

    return render(request, 'chatapp/login1.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# @login_required(login_url='login')
# def chat_room(request,room_name):
#     # room = Room.objects.get(room_name=room_name)
#     # chats = Message.objects.filter(room=room).order_by('timestamp')
#     # return render(request, 'chatapp/chat_room1.html', {
#     #     'room_name': room_name,
#     #     'chats': chats,
#     #     'username': request.user.username
#     # })
#     room, created = Room.objects.get_or_create(room_name=room_name)
    
#     chats = room.return_room_messages()
    
#     return render(request, 'chatapp/chat_room1.html', {
#         'room_name': room.room_name,
#         'username': request.user.username,
#         'chats': chats,
#     })
#     return render(request, 'chatapp/chat_room1.html', context)

@login_required(login_url='login')
def chat_room(request, room_name):
    room = get_object_or_404(Room, room_name=room_name)

    if room.room_pin and not request.session.get(f'pin_verified_{room_name}'):
        messages.error(request, "Access denied. Join with correct PIN.")
        return redirect('dashboard')

    chats = room.return_room_messages()
    
    return render(request, 'chatapp/chat_room1.html', {
        'room_name': room.room_name,
        'username': request.user.username,
        'chats': chats,
    })



def save_message(username, room_name, message):
    chat = Message(username=username, room_name=room_name, message=message)
    chat.save()
    return chat.message_hash

@login_required
def CreateRoom(request):

    if request.method == 'POST':
        username = request.POST['username']
        room = request.POST['room']

        try:
            get_room = Room.objects.get(room_name=room)
            return redirect('room', room_name=room, username=username)

        except Room.DoesNotExist:
            new_room = Room(room_name = room)
            new_room.save()
            return redirect('room', room_name=room, username=username)

    return render(request, 'chat_room1.html')

@login_required
def CreateRoom(request):
    if request.method == 'POST':
        room = request.POST['room']
        pin = request.POST['pin']

        if Room.objects.filter(room_name=room).exists():
            messages.error(request, "Room already exists.")
            return redirect('dashboard')

        new_room = Room(room_name=room)
        if pin:
            new_room.set_pin(pin)
        new_room.save()

        return redirect('chat_room', room_name=room)
    
    return render(request, 'create_room1.html')

@login_required
def join_room_view(request):
    if request.method == 'POST':
        room_name = request.POST.get('room')
        pin = request.POST.get('pin')

        try:
            room = Room.objects.get(room_name=room_name)
            if room.check_pin(pin):
                return redirect('chat_room', room_name=room_name)
            else:
                messages.error(request, "Incorrect PIN.")
                return redirect('dashboard')
        except Room.DoesNotExist:
            messages.error(request, "Room not found.")
            return redirect('dashboard')
    
    return redirect('dashboard')


def MessageView(request, room_name, username):

    get_room = Room.objects.get(room_name=room_name)

    if request.method == 'POST':
        message = request.POST['message']

        print(message)

        new_message = Message(room=get_room, sender=username, message=message)
        new_message.save()

    get_messages= Message.objects.filter(room=get_room)
    
    context = {
        "messages": get_messages,
        "user": username,
        "room_name": room_name,
    }
    return render(request, 'chat_room1.html', context)

def dashboard(request):  # or your relevant view
    rooms = Room.objects.all()
    users = User.objects.all()

    # Fetch currently logged in users via session
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []
    for session in sessions:
        data = session.get_decoded()
        uid = data.get('_auth_user_id')
        if uid:
            uid_list.append(uid)

    online_users = User.objects.filter(id__in=uid_list)
    online_usernames = [user.username for user in online_users]

    return render(request, 'chatapp/dashboard.html', {
        'rooms': rooms,
        'users': users,
        'request_user': request.user,
        'online_usernames': online_usernames,
    })
    
def clear_chat(request, room_name):
    if request.method == "POST":
        Message.objects.filter(room__room_name=room_name).delete()
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "failed"}, status=400)

