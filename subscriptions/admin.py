from django.contrib import admin
from .models import Subscription, UserSubscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_days', 'is_active', 'created_at']
    list_filter = ['is_active', 'duration_days']
    search_fields = ['name', 'features']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'subscription', 'purchased_at', 'expires_at', 'status', 'is_active']
    list_filter = ['status', 'is_active', 'purchased_at']
    search_fields = ['user__username', 'subscription__name']
    readonly_fields = ['purchased_at', 'expires_at']