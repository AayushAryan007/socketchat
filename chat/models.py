from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    users = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return " & ".join([u.username for u in self.users.all()])

    @staticmethod
    def get_or_create_room(user1, user2):
        # Find existing room with both users
        rooms = ChatRoom.objects.filter(users=user1).filter(users=user2)
        if rooms.exists():
            return rooms.first()
        # Create new room
        room = ChatRoom.objects.create()
        room.users.add(user1, user2)
        return room

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.text[:30]}"
