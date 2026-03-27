from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .models import Watchlist
from .serializers import WatchlistSerializer
from .permissions import IsOwnerOrReadOnly
from .openapi import WATCHLIST_SCHEMA


@WATCHLIST_SCHEMA
class WatchlistViewSet(viewsets.ModelViewSet):
    """
    API для управления списком просмотра.
    POST - добавить фильм
    GET - получить мой список
    """
    serializer_class = WatchlistSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['movie__title']
    ordering_fields = ['added_at', 'movie__title']
    ordering = ['-added_at']

    def get_queryset(self):
        user = self.request.user
        return Watchlist.objects.filter(user=user).select_related('movie')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)