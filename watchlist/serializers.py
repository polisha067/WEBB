from rest_framework import serializers
from .models import Watchlist


class WatchlistSerializer(serializers.ModelSerializer):
    """сериализатор для списка просмотра"""
    movie_title = serializers.CharField(source='movie.title', read_only=True)

    class Meta:
        model = Watchlist
        fields = ['id', 'user', 'movie', 'movie_title', 'status', 'added_at']
        read_only_fields = ['id', 'user', 'added_at', 'movie_title']

