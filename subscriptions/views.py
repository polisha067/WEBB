from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from .models import Subscription, UserSubscription
from .serializers import SubscriptionSerializer, UserSubscriptionSerializer


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """API для тарифных планов"""
    queryset = Subscription.objects.filter(is_active=True)
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ['name', 'features']
    ordering_fields = ['price', 'duration_days']


class UserSubscriptionViewSet(ListModelMixin,
                              RetrieveModelMixin,
                              CreateModelMixin,
                              viewsets.GenericViewSet):
    """API для подписок пользователей (list/retrieve/create + cancel)"""
    serializer_class = UserSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']

    def get_queryset(self):
        return UserSubscription.objects.filter(
            user=self.request.user
        ).select_related('subscription')

    def perform_create(self, serializer):
        active_exists = UserSubscription.objects.filter(
            user=self.request.user,
            status='active',
            is_active=True,
        ).exists()
        if active_exists:
            raise serializers.ValidationError(
                'У вас уже есть активная подписка'
            )
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отмена подписки"""
        subscription = self.get_object()
        if subscription.status != 'active':
            return Response(
                {'detail': 'Подписка уже неактивна'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.status = 'cancelled'
        subscription.is_active = False
        subscription.save()
        return Response(UserSubscriptionSerializer(subscription).data)