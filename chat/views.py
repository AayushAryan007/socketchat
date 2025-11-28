from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import ChatRoom, Message

@login_required
def chat_list(request):
    # Get all friends (users who mutually follow each other)
    friends = []
    for user in User.objects.exclude(id=request.user.id):
        if (request.user.profile.is_following(user) and 
            user.profile.is_following(request.user)):
            friends.append(user)
    
    return render(request, 'chat/chat_list.html', {'friends': friends})

@login_required
def chat_room(request, username):
    friend = get_object_or_404(User, username=username)
    
    # Check if they are friends
    if not (request.user.profile.is_following(friend) and 
            friend.profile.is_following(request.user)):
        return render(request, 'chat/not_friend.html', {'friend': friend})
    
    # Get or create chat room
    room = ChatRoom.get_or_create_room(request.user, friend)
    messages = room.messages.all()
    
    # Don't use Django messages for chat
    return render(request, 'chat/chat_room.html', {
        'room': room,
        'friend': friend,
        'messages': messages
    })
