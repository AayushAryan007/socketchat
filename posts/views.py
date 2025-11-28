from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import Post, PostMedia, Comment
from .forms import PostCreateForm, CommentForm

@login_required
def feed_view(request):
    posts = Post.objects.all().select_related('author', 'author__profile').prefetch_related('media', 'likes', 'comments')
    context = {
        'posts': posts,
    }
    return render(request, 'posts/feed.html', context)

@login_required
def create_post_view(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST)
        files = request.FILES.getlist('media_files')
        
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            # Handle multiple file uploads
            for file in files:
                # Determine media type based on file extension
                file_extension = file.name.split('.')[-1].lower()
                if file_extension in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    media_type = 'image'
                elif file_extension in ['mp4', 'avi', 'mov', 'wmv', 'webm']:
                    media_type = 'video'
                else:
                    continue
                
                PostMedia.objects.create(
                    post=post,
                    file=file,
                    media_type=media_type
                )
            
            messages.success(request, 'Post created successfully!')
            return redirect('feed')
    else:
        form = PostCreateForm()
    
    return render(request, 'posts/create_post.html', {'form': form})

@login_required
def post_detail_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all().select_related('author', 'author__profile')
    
    if request.method == 'POST':
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                
                # Get avatar URL
                avatar_url = request.user.profile.avatar.url if request.user.profile.avatar else 'https://via.placeholder.com/40'
                
                return JsonResponse({
                    'success': True,
                    'comment': {
                        'id': comment.pk,
                        'text': comment.text,
                        'author_name': request.user.get_full_name(),
                        'author_username': request.user.username,
                        'author_avatar': avatar_url,
                    }
                })
            else:
                return JsonResponse({'success': False, 'errors': comment_form.errors})
        else:
            # Regular form submission (fallback)
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.post = post
                comment.author = request.user
                comment.save()
                messages.success(request, 'Comment added!')
                return redirect('post_detail', pk=pk)
    else:
        comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'posts/post_detail.html', context)

@login_required
def user_posts_view(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=user).select_related('author', 'author__profile').prefetch_related('media', 'likes', 'comments')
    
    context = {
        'profile_user': user,
        'posts': posts,
    }
    return render(request, 'posts/user_posts.html', context)

@login_required
@require_POST
def like_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'total_likes': post.total_likes
        })
    
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

@login_required
def delete_post_view(request, pk):
    post = get_object_or_404(Post, pk=pk)
    
    if post.author == request.user:
        post.delete()
        messages.success(request, 'Post deleted successfully!')
    else:
        messages.error(request, 'You can only delete your own posts.')
    
    return redirect(request.META.get('HTTP_REFERER', 'feed'))

@login_required
def delete_comment_view(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    
    if comment.author == request.user or comment.post.author == request.user:
        # Check if it's an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            comment.delete()
            return JsonResponse({'success': True})
        else:
            comment.delete()
            messages.success(request, 'Comment deleted successfully!')
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Permission denied'})
        else:
            messages.error(request, 'You can only delete your own comments.')
    
    return redirect('post_detail', pk=post_pk)
