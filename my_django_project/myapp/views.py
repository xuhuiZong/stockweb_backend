from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from openai import OpenAI
from django.conf import settings
from .models import ChatMessage
from .serializers import ChatmessageSerializer
from django.shortcuts import get_object_or_404

class ChatmessageView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def __init__(self):
        super().__init__()
        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.API_BASE
        )
    
    def get(self, request, *args, **kwargs):
        messages = ChatMessage.objects.all().order_by('-message_time')
        serializer = ChatmessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    # 添加新建话题的方法
    def new_topic(self, request):
        new_topic = ChatMessage.objects.create(
            message_name=f"新话题 {ChatMessage.objects.count() + 1}",
            message_content=[]
        )
        serializer = ChatmessageSerializer(new_topic)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        # 处理新建话题的请求
        if request.path.endswith('/new_topic/'):
            return self.new_topic(request)
            
        try:
            user_message = request.data.get("message", "")
            topic_id = request.data.get("topic_id")
            
            # 获取指定话题的消息记录
            chat_message = get_object_or_404(ChatMessage, id=topic_id)
            conversation_history = chat_message.message_content
            
            # 添加新的用户消息
            conversation_history.append({"role": "user", "content": user_message})
            
            # 调用模型 API
            response = self.client.chat.completions.create(
                model=settings.MODEL_SERVICE_ID,
                messages=conversation_history,
                stream=True,
                temperature=0.7,
                max_tokens=4096,
                extra_headers={"lora_id": "0"},
                stream_options={"include_usage": True}
            )

            full_response = ""
            for chunk in response:
                if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content is not None:
                    full_response += chunk.choices[0].delta.reasoning_content
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content

            # 更新对话记录
            conversation_history.append({"role": "assistant", "content": full_response})
            chat_message.message_content = conversation_history
            chat_message.save()
            
            serializer = ChatmessageSerializer(chat_message)
            return Response({
                "message": serializer.data,
                "response": full_response
            })

        except Exception as e:
            return Response({"error": str(e)}, status=400)
    