from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Watchlist
from .serializers import WatchlistSerializer
from .permissions import IsOwnerOrReadOnly


class WatchlistViewSet(viewsets.ModelViewSet):
    """
    API для управления списком просмотра.
    POST - добавить фильм
    GET - получить мой список
    """
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        
        user = self.request.user
        return Watchlist.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)