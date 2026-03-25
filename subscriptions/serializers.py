from rest_framework import serializers
from .models import Subscription, UserSubscription


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для тарифных планов"""
    class Meta:
        model = Subscription
        fields = ['id', 'name', 'price', 'duration_days', 'features', 'is_active', 'created_at', 'updated_at']


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор для подписок пользователей"""
    subscription_name = serializers.CharField(
        source='subscription.name', read_only=True
    )

    class Meta:
        model = UserSubscription
        fields = ['id', 'user', 'subscription', 'subscription_name',
            'purchased_at', 'expires_at', 'status', 'is_active']
        read_only_fields = ['user', 'purchased_at', 'expires_at', 'status', 'is_active']