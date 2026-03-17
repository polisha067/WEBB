from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Subscription(models.Model):
    """Тарифный план - что можно купить"""
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(help_text='в днях')
    features = models.TextField(help_text='что входит')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['price']

    def __str__(self):
        return f'{self.name} - {self.price}₽'


class UserSubscription(models.Model):
    """
    Активная подписка пользователя
    Связывает пользователя с тарифом и хранит сроки действия
    """
    STATUS_CHOICES = [
        ('active', 'Активна'),
        ('expired', 'Истекла'),
        ('cancelled', 'Отменена'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.CASCADE,
        related_name='user_subscriptions'
    )
    purchased_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(help_text='Когда истекает')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Подписка пользователя'
        verbose_name_plural = 'Подписки пользователей'
        ordering = ['-purchased_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.subscription.name}'

    def save(self, *args, **kwargs):
        """Автоматически рассчитываем дату истечения"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=self.subscription.duration_days)

        if self.expires_at < timezone.now():
            self.status = 'expired'
            self.is_active = False

        super().save(*args, **kwargs)