from django.conf import settings
from django.db import models
from movies.models import Movie


class Watchlist(models.Model):
    """
    Список просмотра пользователя
    Связывает пользователя с фильмом и хранит статус просмотра
    """
    STATUS_CHOICES = [
        ('want_to_watch', 'Хочу посмотреть'),
        ('watching', 'Смотрю'),
        ('watched', 'Посмотрел'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='watchlists'
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='watchlists'
    )
    added_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='want_to_watch'
    )

    class Meta:
        verbose_name = 'Список просмотра'
        verbose_name_plural = 'Списки просмотра'
        ordering = ['-added_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'movie'],
                name='unique_user_movie'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.movie.title}'