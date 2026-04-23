from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from movies.models import Movie
from ..services import WatchlistService
from ..models import Watchlist


class WatchlistServiceTest(TestCase):
    """Тесты для WatchlistService"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.movie = Movie.objects.create(
            title='Тестовый фильм',
            description='Описание',
            duration=120,
            rating=7.5,
            release_year=2024
        )

    def test_add_movie_to_watchlist(self):
        """Тест 1: Добавление фильма"""
        result = WatchlistService.add(self.user, self.movie, 'want_to_watch')
        
        self.assertIsNotNone(result.id)
        self.assertEqual(result.user, self.user)
        self.assertEqual(result.movie, self.movie)
        self.assertTrue(Watchlist.objects.filter(user=self.user, movie=self.movie).exists())

    def test_add_duplicate_movie(self):
        """Тест 2: Попытка добавить дубликат"""
        WatchlistService.add(self.user, self.movie, 'want_to_watch')
        
        with self.assertRaises(ValidationError):
            WatchlistService.add(self.user, self.movie, 'watching')

    def test_remove_movie_from_watchlist(self):
        """Тест 3: Удаление фильма"""
        WatchlistService.add(self.user, self.movie, 'want_to_watch')
        
        result = WatchlistService.remove(self.user, self.movie)
        
        self.assertTrue(result)
        self.assertFalse(Watchlist.objects.filter(user=self.user, movie=self.movie).exists())

    def test_change_status(self):
        """Тест 4: Изменение статуса"""
        WatchlistService.add(self.user, self.movie, 'want_to_watch')
        
        result = WatchlistService.change_status(self.user, self.movie, 'watched')
        
        self.assertEqual(result.status, 'watched')