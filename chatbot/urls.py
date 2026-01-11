from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # JSON endpoint for both the mini-bot (base1) and full-bot
    path('query/', views.chatbot_query, name='chatbot_query'),
    
    # The dedicated full-screen page
    path('full-analysis/', views.full_chat_view, name='chat_home'),
]