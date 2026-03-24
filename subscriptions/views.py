from rest_framework import viewsets, permissions
from rest_framework.response import Response
from .models import Subscription, UserSubscription
from .serializers import SubscriptionSerializer, UserSubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    """API для тарифных планов"""
    queryset = Subscription.objects.filter(is_active=True)
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ['name', 'features']
    ordering_fields = ['price', 'duration_days'] 


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """API для подписок пользователей"""
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserSubscription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)