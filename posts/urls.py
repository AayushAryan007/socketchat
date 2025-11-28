from django.urls import path
from . import views

urlpatterns = [
    path('feed/', views.feed_view, name='feed'),
    path('create/', views.create_post_view, name='create_post'),
    path('post/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('post/<int:pk>/like/', views.like_post_view, name='like_post'),
    path('post/<int:pk>/delete/', views.delete_post_view, name='delete_post'),
    path('user/<str:username>/posts/', views.user_posts_view, name='user_posts'),
    path('comment/<int:pk>/delete/', views.delete_comment_view, name='delete_comment'),
]