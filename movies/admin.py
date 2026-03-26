from django.contrib import admin
from .models import Genre, Movie

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_year', 'rating', 'duration', 'created_at']
    list_filter = ['release_year', 'genres', 'rating']
    search_fields = ['title', 'description']
    filter_horizontal = ['genres']  
    readonly_fields = ['created_at', 'updated_at']