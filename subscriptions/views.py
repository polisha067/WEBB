from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from drf_spectacular.utils import extend_schema
from .models import Subscription, UserSubscription
from .serializers import SubscriptionSerializer, UserSubscriptionSerializer
from .openapi import SUBSCRIPTION_SCHEMA, USER_SUBSCRIPTION_SCHEMA
from .services import SubscriptionService


@SUBSCRIPTION_SCHEMA
class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    """API для тарифных планов"""
    queryset = Subscription.objects.filter(is_active=True)
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.AllowAny]
    search_fields = ['name', 'features']
    ordering_fields = ['price', 'duration_days']


@USER_SUBSCRIPTION_SCHEMA
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_subscription = SubscriptionService.activate(
            user=request.user,
            subscription=serializer.validated_data["subscription"],
        )
        out = self.get_serializer(user_subscription)
        return Response(out.data, status=201)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Отмена подписки"""
        user_subscription = self.get_object()
        user_subscription = SubscriptionService.cancel(user_subscription=user_subscription)
        return Response(self.get_serializer(user_subscription).data)