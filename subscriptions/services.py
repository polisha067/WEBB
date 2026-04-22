from __future__ import annotations
from dataclasses import dataclass
from django.db import transaction
from django.utils import timezone
from core.exceptions import AlreadySubscribed, SubscriptionAlreadyCancelled
from .models import Subscription, UserSubscription

@dataclass(frozen=True, slots=True)
class ExpireResult:
    expired_count: int

class SubscriptionService:
    @staticmethod
    @transaction.atomic
    def activate(*, user, subscription: Subscription) -> UserSubscription:
        active_exists = (
            UserSubscription.objects.select_for_update()
            .filter(user=user, status="active", is_active=True)
            .exists()
        )
        if active_exists:
            raise AlreadySubscribed()

        user_subscription = UserSubscription.objects.create(
            user=user,
            subscription=subscription,
        )
        return user_subscription

    @staticmethod
    @transaction.atomic
    def cancel(*, user_subscription: UserSubscription) -> UserSubscription:
        if user_subscription.status != "active" or not user_subscription.is_active:
            raise SubscriptionAlreadyCancelled()

        user_subscription.status = "cancelled"
        user_subscription.is_active = False
        user_subscription.save(update_fields=["status", "is_active"])
        return user_subscription

    @staticmethod
    @transaction.atomic
    def check_expired(*, now=None) -> ExpireResult:
        now = now or timezone.now()

        qs = UserSubscription.objects.select_for_update().filter(
            status="active",
            is_active=True,
            expires_at__lt=now,
        )
        expired_count = qs.update(status="expired", is_active=False)
        return ExpireResult(expired_count=expired_count)