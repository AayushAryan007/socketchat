from django.contrib import admin
from .models import Post, PostMedia, Comment, Notification

class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 1

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['author', 'description', 'created_at', 'total_likes', 'total_comments']
    list_filter = ['created_at']
    search_fields = ['description', 'author__username']
    inlines = [PostMediaInline]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'text', 'created_at']
    list_filter = ['created_at']
    search_fields = ['text', 'author__username']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'sender__username']
