from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from core.exceptions import AlreadySubscribed, SubscriptionAlreadyCancelled
from subscriptions.models import Subscription, UserSubscription
from subscriptions.services import SubscriptionService


class SubscriptionServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pass123456")
        self.plan = Subscription.objects.create(
            name="Basic",
            price="100.00",
            duration_days=30,
            features="Feature 1",
            is_active=True,
        )

    def test_activate_creates_user_subscription(self):
        us = SubscriptionService.activate(user=self.user, subscription=self.plan)
        self.assertEqual(us.user, self.user)
        self.assertEqual(us.subscription, self.plan)
        self.assertEqual(us.status, "active")
        self.assertTrue(us.is_active)
        self.assertIsNotNone(us.expires_at)

    def test_activate_duplicate_raises(self):
        SubscriptionService.activate(user=self.user, subscription=self.plan)
        with self.assertRaises(AlreadySubscribed):
            SubscriptionService.activate(user=self.user, subscription=self.plan)

    def test_cancel_active_subscription(self):
        us = SubscriptionService.activate(user=self.user, subscription=self.plan)
        us = SubscriptionService.cancel(user_subscription=us)
        us.refresh_from_db()
        self.assertEqual(us.status, "cancelled")
        self.assertFalse(us.is_active)

    def test_cancel_already_cancelled_raises(self):
        us = SubscriptionService.activate(user=self.user, subscription=self.plan)
        SubscriptionService.cancel(user_subscription=us)
        us.refresh_from_db()
        with self.assertRaises(SubscriptionAlreadyCancelled):
            SubscriptionService.cancel(user_subscription=us)

    def test_check_expired_marks_expired(self):
        us = SubscriptionService.activate(user=self.user, subscription=self.plan)

        past = timezone.now() - timedelta(days=1)
        UserSubscription.objects.filter(pk=us.pk).update(
            expires_at=past,
            status="active",
            is_active=True,
        )

        result = SubscriptionService.check_expired(now=timezone.now())
        self.assertEqual(result.expired_count, 1)

        us.refresh_from_db()
        self.assertEqual(us.status, "expired")
        self.assertFalse(us.is_active)

