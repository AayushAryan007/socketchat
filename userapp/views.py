from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm
from .models import UserProfile
from posts.models import Notification

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            login(request, user)
            return redirect('profile', username=user.username)
    else:
        form = SignUpForm()
    return render(request, 'userapp/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('profile', username=request.user.username)
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('profile', username=user.username)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'userapp/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required
def profile_view(request, username=None):
    user = get_object_or_404(User, username=username) if username else request.user
    profile = user.profile
    is_own_profile = (request.user == user)
    is_following = False

    if request.user.is_authenticated and not is_own_profile:
        is_following = profile.is_following(request.user)

    context = {
        'profile_user': user,
        'profile': profile,
        'is_own_profile': is_own_profile,
        'is_following': is_following,
    }
    return render(request, 'userapp/profile.html', context)

@login_required
def edit_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    
    if request.user != user:
        messages.error(request, 'You can only edit your own profile.')
        return redirect('profile', username=username)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile', username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'userapp/edit_profile.html', context)

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your password was successfully updated!')
            login(request, user)
            return redirect('profile', username=request.user.username)
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'userapp/change_password.html', {'form': form})

@login_required
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    
    if user_to_follow != request.user:
        profile = user_to_follow.profile
        if profile.is_following(request.user):
            # Unfollow
            profile.followers.remove(request.user)
            messages.success(request, f'You unfollowed {username}.')
            # Delete follow notification
            Notification.objects.filter(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='follow'
            ).delete()
            # Delete friend notification if exists
            Notification.objects.filter(
                recipient=request.user,
                sender=user_to_follow,
                notification_type='friend'
            ).delete()
            Notification.objects.filter(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='friend'
            ).delete()
        else:
            # Follow
            profile.followers.add(request.user)
            messages.success(request, f'You are now following {username}.')
            
            # Create follow notification
            Notification.objects.create(
                recipient=user_to_follow,
                sender=request.user,
                notification_type='follow'
            )
            
            # Check if they're now friends (both following each other)
            if request.user.profile.is_following(user_to_follow):
                # Create friend notifications for both users
                Notification.objects.get_or_create(
                    recipient=request.user,
                    sender=user_to_follow,
                    notification_type='friend'
                )
                Notification.objects.get_or_create(
                    recipient=user_to_follow,
                    sender=request.user,
                    notification_type='friend'
                )
    
    return redirect('profile', username=username)

@login_required
def followers_list(request, username):
    user = get_object_or_404(User, username=username)
    followers = user.profile.followers.all()
    return render(request, 'userapp/followers_list.html', {'profile_user': user, 'followers': followers})

@login_required
def following_list(request, username):
    user = get_object_or_404(User, username=username)
    following = User.objects.filter(profile__followers=user)
    return render(request, 'userapp/following_list.html', {'profile_user': user, 'following': following})
