from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    users = models.ManyToManyField(User, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return " & ".join([u.username for u in self.users.all()])

    @staticmethod
    def get_or_create_room(user1, user2):
        rooms = ChatRoom.objects.filter(users=user1).filter(users=user2)
        if rooms.exists():
            return rooms.first()
        room = ChatRoom.objects.create()
        room.users.add(user1, user2)
        return room
    
    def get_other_user(self, current_user):
        """Get the other user in this chat room"""
        users = self.users.exclude(id=current_user.id)
        return users.first() if users.exists() else None
    
    def unread_count_for_user(self, user):
        """Get unread message count for a specific user"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.username}: {self.text[:30]}"
