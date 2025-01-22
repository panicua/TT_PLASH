from decouple import config
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from todo.models import Todo
from todo.serializers import TodoSerializer


class TodoViewSet(viewsets.ModelViewSet):
    queryset = Todo.objects.all()
    serializer_class = TodoSerializer
    permission_classes = [AllowAny]

    def initialize_request(self, request, *args, **kwargs):
        self.secret = request.headers.get('X-Telegram-Secret')
        if self.secret == config('TELEGRAM_SECRET_HEADER_TOKEN'):
            return super().initialize_request(request, *args, **kwargs)
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        todo = self.get_object()
        serializer = self.get_serializer(todo, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        todo = self.get_object()
        todo.delete()
        return Response({"message": "Todo deleted successfully"}, status=status.HTTP_200_OK)
