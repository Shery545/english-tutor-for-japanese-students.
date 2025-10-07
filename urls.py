from django.urls import path
from .views import conversation_view, api_start_conversation, api_process_response

urlpatterns = [
    path('', conversation_view, name='home'),
    path('api/conversation/start/', api_start_conversation, name='start-conversation'),
    path('api/conversation/respond/', api_process_response, name='process-response'),
]