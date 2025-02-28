# myapp/serializers.py
from rest_framework import serializers
from .models import ChatMessage

class ChatmessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'message_name', 'message_content', 'message_time']
        # 也可以只读：
        # extra_kwargs = {
        #     'custom_folder': {'read_only': True}
        # }
