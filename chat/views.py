from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import ChatRoom, Message

@login_required
def chat_list(request):
    # Get all friends with their chat rooms and unread counts
    friends_data = []
    for user in User.objects.exclude(id=request.user.id):
        if (request.user.profile.is_following(user) and 
            user.profile.is_following(request.user)):
            # Get or create room to check unread count
            room = ChatRoom.get_or_create_room(request.user, user)
            unread = room.unread_count_for_user(request.user)
            friends_data.append({
                'user': user,
                'room': room,
                'unread_count': unread
            })
    
    return render(request, 'chat/chat_list.html', {'friends_data': friends_data})

@login_required
def chat_room(request, username):
    friend = get_object_or_404(User, username=username)
    
    # Check if they are friends
    if not (request.user.profile.is_following(friend) and 
            friend.profile.is_following(request.user)):
        return render(request, 'chat/not_friend.html', {'friend': friend})
    
    # Get or create chat room
    room = ChatRoom.get_or_create_room(request.user, friend)
    
    # Mark all messages in this room as read for current user
    room.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
    
    messages = room.messages.all()
    
    return render(request, 'chat/chat_room.html', {
        'room': room,
        'friend': friend,
        'messages': messages
    })

@login_required
def unread_count(request):
    """API endpoint to get total unread message count"""
    total_unread = 0
    for room in request.user.chat_rooms.all():
        total_unread += room.unread_count_for_user(request.user)
    
    return JsonResponse({'count': total_unread})
