from .models import Movie


def get_top_rated():
    return Movie.objects.all().prefetch_related('genres').order_by('-rating')


def get_new_releases():
    return Movie.objects.all().prefetch_related('genres').order_by('-release_year', '-rating')
