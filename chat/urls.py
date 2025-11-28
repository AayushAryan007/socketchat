from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<str:username>/', views.chat_room, name='chat_room'),
    path('unread-count/', views.unread_count, name='chat_unread_count'),
]