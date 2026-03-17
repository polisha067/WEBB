from django.db import models

class Genre(models.Model):
    """
    Жанр фильма - категория для группировки фильмов.
    Один жанр может быть у множества фильмов
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class Movie(models.Model):
    """
    Фильм - основная сущность кинотеатра
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField(help_text='в минутах')
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    release_year = models.IntegerField()
    genres = models.ManyToManyField(Genre, related_name='movies')
    poster = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Фильм'
        verbose_name_plural = 'Фильмы'
        ordering = ['-release_year', '-rating']  
        indexes = [
            models.Index(fields=['release_year']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return self.title