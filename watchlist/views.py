from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Watchlist
from .serializers import WatchlistSerializer
from .permissions import IsOwnerOrReadOnly
from .services import WatchlistService
from django.core.exceptions import ValidationError


class WatchlistViewSet(viewsets.ModelViewSet):
    """API для управления списком просмотра"""
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            WatchlistService.add(
                user=self.request.user,
                movie=serializer.validated_data['movie'],
                status=serializer.validated_data.get('status', 'want_to_watch'),
            )
        except ValidationError as e:
            raise ValidationError({'movie': str(e)})

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