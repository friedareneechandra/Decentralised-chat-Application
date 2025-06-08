import hashlib
from django.db import models
from django.utils import timezone

class ChatMessage(models.Model):
    username = models.CharField(max_length=100)  # Make sure this is defined
    room_name = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    message_hash = models.CharField(max_length=64, blank=True)
    previous_hash = models.CharField(max_length=64, blank=True)

    def save(self, *args, **kwargs):
        # Only generate hash on first save
        if not self.id:
            last = ChatMessage.objects.filter(room_name=self.room_name).order_by('-timestamp').first()
            self.previous_hash = last.message_hash if last else '0' * 64

            data = (
                self.username +
                self.room_name +
                self.message +
                str(self.timestamp) +
                self.previous_hash
            ).encode()

            self.message_hash = hashlib.sha256(data).hexdigest()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username}: {self.message[:30]}"

# class Room(models.Model):
#     room_name = models.CharField(max_length=255)

#     def __str__(self):
#         return self.room_name
    
#     def return_room_messages(self):

#         return Message.objects.filter(room=self)
    
#     def create_new_room_message(self, sender, message):

#         new_message = Message(room=self, sender=sender, message=message)
#         new_message.save()

class Room(models.Model):
    room_name = models.CharField(max_length=255, unique=True)
    room_pin = models.CharField(max_length=128, null=True, blank=True)  # Store hashed PIN

    def set_pin(self, raw_pin):
        self.room_pin = make_password(raw_pin)

    def check_pin(self, raw_pin):
        return check_password(raw_pin, self.room_pin)
        
class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.CharField(max_length=255)
    message = models.TextField()
    message_hash = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.room)










