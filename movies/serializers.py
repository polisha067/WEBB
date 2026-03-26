from rest_framework import serializers
from .models import Genre, Movie


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    genre_ids = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(),
        source='genres',
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'description', 'duration', 'rating',
            'release_year', 'genres', 'genre_ids', 'poster',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        genres = validated_data.pop('genres', [])
        movie = Movie.objects.create(**validated_data)
        movie.genres.set(genres)
        return movie

    def update(self, instance, validated_data):
        genres = validated_data.pop('genres', None)
        if genres is not None:
            instance.genres.set(genres)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance