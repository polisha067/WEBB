from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Watchlist


class WatchlistService:
    """Сервис для управления списком просмотра"""

    @staticmethod
    @transaction.atomic
    def add(user, movie, status='want_to_watch'):
        """Добавить фильм в список"""
        if Watchlist.objects.filter(user=user, movie=movie).exists():
            raise ValidationError('Этот фильм уже есть в вашем списке')
        
        return Watchlist.objects.create(user=user, movie=movie, status=status)

    @staticmethod
    @transaction.atomic
    def remove(user, movie):
        """Удалить фильм из списка"""
        watchlist_item = Watchlist.objects.filter(user=user, movie=movie).first()
        
        if not watchlist_item:
            raise ValidationError('Фильм не найден в вашем списке')
        
        watchlist_item.delete()
        return True

    @staticmethod
    @transaction.atomic
    def change_status(user, movie, new_status):
        """Изменить статус просмотра"""
        watchlist_item = Watchlist.objects.filter(user=user, movie=movie).first()
        
        if not watchlist_item:
            raise ValidationError('Фильм не найден в вашем списке')
        
        watchlist_item.status = new_status
        watchlist_item.save()
        return watchlist_item

    @staticmethod
    def get_user_watchlist(user):
        """Получить список пользователя"""
        return Watchlist.objects.filter(user=user).select_related('movie')