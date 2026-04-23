from django.test import TestCase

from movies.models import Movie
from movies.services import MovieService


class MovieServiceTest(TestCase):
    def test_get_top_rated_returns_movies_ordered_by_rating_desc(self):
        movie_low = Movie.objects.create(
            title='Movie Low',
            description='Low rating movie',
            duration=90,
            rating=7.1,
            release_year=2022,
            poster=''
        )
        movie_high = Movie.objects.create(
            title='Movie High',
            description='High rating movie',
            duration=100,
            rating=9.3,
            release_year=2021,
            poster=''
        )

        result = list(MovieService.get_top_rated())

        self.assertEqual(result, [movie_high, movie_low])

    def test_get_new_releases_returns_movies_ordered_by_release_year_desc_then_rating_desc(self):
        movie_old = Movie.objects.create(
            title='Movie Old',
            description='Old movie',
            duration=95,
            rating=9.5,
            release_year=2020,
            poster=''
        )
        movie_new_lower_rating = Movie.objects.create(
            title='Movie New Lower',
            description='New movie lower rating',
            duration=110,
            rating=8.0,
            release_year=2024,
            poster=''
        )
        movie_new_higher_rating = Movie.objects.create(
            title='Movie New Higher',
            description='New movie higher rating',
            duration=115,
            rating=9.0,
            release_year=2024,
            poster=''
        )

        result = list(MovieService.get_new_releases())

        self.assertEqual(
            result,
            [movie_new_higher_rating, movie_new_lower_rating, movie_old]
        )