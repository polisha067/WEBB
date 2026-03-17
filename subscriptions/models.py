from django.db import models

class Subscription(models.Model):
    """
    Подписка - тарифный план кинотеатра
    Содержит информацию о цене, длительности и возможностях
    """
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
        indexes = [
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return f'{self.name} - {self.price}₽'