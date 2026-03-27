from rest_framework import serializers
from .models import Watchlist


class WatchlistSerializer(serializers.ModelSerializer):
    """сериализатор для списка просмотра"""
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    movie_poster = serializers.CharField(source='movie.poster', read_only=True)
    movie_release_year = serializers.IntegerField(source='movie.release_year', read_only=True)
    movie_duration = serializers.IntegerField(source='movie.duration', read_only=True)
    movie_rating = serializers.DecimalField(source='movie.rating', max_digits=3, decimal_places=1, read_only=True)

    class Meta:
        model = Watchlist
        fields = ['id', 'user', 'movie', 'movie_title', 'movie_poster', 'movie_release_year', 'movie_duration', 'movie_rating', 'status', 'added_at']
        read_only_fields = ['id', 'user', 'added_at', 'movie_title', 'movie_poster', 'movie_release_year', 'movie_duration', 'movie_rating']

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