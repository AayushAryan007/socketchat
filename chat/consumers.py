import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=4401)
            return

        try:
            self.room_id = int(self.scope['url_route']['kwargs']['room_id'])
        except (KeyError, ValueError):
            await self.close(code=4404)
            return

        self.room_group_name = f'chat_{self.room_id}'

        room = await self.get_room()
        if not room:
            await self.close(code=4404)
            return

        if not await self.is_member(room, user):
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        
        # Mark messages as read when user connects
        await self.mark_messages_read(user)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        message_text = (data.get('message') or '').strip()
        if not message_text:
            return

        user = self.scope["user"]
        msg = await self.save_message(user, message_text)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg.text,
                'sender': user.username,
                'sender_name': user.get_full_name() or user.username,
                'timestamp': msg.timestamp.isoformat()
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender': event['sender'],
            'sender_name': event['sender_name'],
            'timestamp': event['timestamp']
        }))

    @database_sync_to_async
    def get_room(self):
        try:
            return ChatRoom.objects.get(id=self.room_id)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def is_member(self, room, user):
        users = list(room.users.all())
        if len(users) != 2:
            return False
        other = users[0] if users[1] == user else users[1]
        return (user.profile.is_following(other) and 
                other.profile.is_following(user))

    @database_sync_to_async
    def save_message(self, sender, text):
        room = ChatRoom.objects.get(id=self.room_id)
        return Message.objects.create(room=room, sender=sender, text=text, is_read=False)
    
    @database_sync_to_async
    def mark_messages_read(self, user):
        """Mark all messages in this room as read for the user"""
        room = ChatRoom.objects.get(id=self.room_id)
        room.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)