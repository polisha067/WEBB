"""
Тесты сервисного слоя аккаунтов 
"""
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.test import TestCase

from accounts.services import AccountService
from core.exceptions import (
    InvalidCredentials,
    AccountDisabled,
    UsernameAlreadyExists,
    PasswordsDoNotMatch,
)


class AccountServiceRegisterTest(TestCase):
    def test_register_creates_user_and_token(self):
        user, token = AccountService.register(
            username='alice',
            email='alice@test.com',
            password='strongpassword123',
            password_confirm='strongpassword123',
        )
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, 'alice')
        self.assertTrue(Token.objects.filter(user=user).exists())

    def test_register_raises_on_password_mismatch(self):
        with self.assertRaises(PasswordsDoNotMatch):
            AccountService.register(
                username='bob',
                email='',
                password='password1',
                password_confirm='password2',
            )

    def test_register_raises_on_duplicate_username(self):
        AccountService.register(
            username='charlie',
            email='',
            password='password123',
            password_confirm='password123',
        )
        with self.assertRaises(UsernameAlreadyExists):
            AccountService.register(
                username='charlie',
                email='other@test.com',
                password='password456',
                password_confirm='password456',
            )


class AccountServiceLoginTest(TestCase):
    def setUp(self):
        AccountService.register(
            username='dave',
            email='dave@test.com',
            password='password123',
            password_confirm='password123',
        )

    def test_login_returns_user_and_token(self):
        user, token = AccountService.login('dave', 'password123')
        self.assertEqual(user.username, 'dave')
        self.assertIsNotNone(token.key)

    def test_login_raises_on_wrong_password(self):
        with self.assertRaises(InvalidCredentials):
            AccountService.login('dave', 'wrongpassword')

    def test_login_raises_on_nonexistent_user(self):
        with self.assertRaises(InvalidCredentials):
            AccountService.login('nobody', 'password123')

    def test_login_raises_on_disabled_account(self):
        user = User.objects.get(username='dave')
        user.is_active = False
        user.save()
        with self.assertRaises(AccountDisabled):
            AccountService.login('dave', 'password123')


class AccountServiceLogoutTest(TestCase):
    def test_logout_deletes_token(self):
        user, _ = AccountService.register(
            username='eve',
            email='',
            password='password123',
            password_confirm='password123',
        )
        self.assertTrue(Token.objects.filter(user=user).exists())
        AccountService.logout(user)
        self.assertFalse(Token.objects.filter(user=user).exists())
