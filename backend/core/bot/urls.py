# urls.py
from django.urls import path
from .views import ChatView, ChatMessageView, chat_page

urlpatterns = [
    path('chats/', ChatView.as_view(), name='chats'),
    path('chats/<int:chat_id>/messages/', ChatMessageView.as_view(), name='chat_messages'),
    path('chat/', chat_page, name='chat_page'),
]