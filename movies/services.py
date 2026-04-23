from .models import Movie


class MovieService:
    @staticmethod
    def get_top_rated():
        return Movie.objects.all().prefetch_related('genres').order_by('-rating')

    @staticmethod
    def get_new_releases():
        return Movie.objects.all().prefetch_related('genres').order_by('-release_year', '-rating')