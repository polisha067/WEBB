from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Watchlist
from .serializers import WatchlistSerializer
from .permissions import IsOwnerOrReadOnly
from .services import WatchlistService
from django.core.exceptions import ValidationError


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

        try:
            WatchlistService.remove(user=self.request.user, movie=instance.movie)
        except ValidationError as e:
            raise serializers.ValidationError({'movie': str(e)})


    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        try:
            new_status = request.data.get('status', instance.status)
            watchlist_item = WatchlistService.change_status(
                user=request.user,
                movie=instance.movie,
                new_status=new_status
            )
            serializer = self.get_serializer(watchlist_item)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'movie': str(e)}, status=status.HTTP_400_BAD_REQUEST)