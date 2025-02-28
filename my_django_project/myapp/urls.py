from django.urls import path
from .views import ChatmessageView

urlpatterns = [
    path('chat/', ChatmessageView.as_view(), name='chat'),
    path('chat/new_topic/', ChatmessageView.as_view(), name='new_topic'),
]
