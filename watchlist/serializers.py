from rest_framework import serializers
from .models import Watchlist


class WatchlistSerializer(serializers.ModelSerializer):
    """сериализатор для списка просмотра"""
    movie_title = serializers.CharField(source='movie.title', read_only=True)

    class Meta:
        model = Watchlist
        fields = ['id', 'user', 'movie', 'movie_title', 'status', 'added_at']
        read_only_fields = ['id', 'user', 'added_at', 'movie_title']

    def validate(self, data):
        request = self.context.get('request')
        if not request:
            return data

        user = request.user
        movie = data.get('movie')

        if not movie:
            return data

        existing = Watchlist.objects.filter(user=user, movie=movie)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)

        if existing.exists():
            raise serializers.ValidationError(
                {'movie': 'этот фильм уже есть в вашем списке'}
            )

        return data