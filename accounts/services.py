"""
Сервисный слой для аккаунтов: регистрация, вход, выход.
Бизнес-логика вынесена из views и serializers.
"""
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from core.exceptions import (
    InvalidCredentials,
    AccountDisabled,
    UsernameAlreadyExists,
    PasswordsDoNotMatch,
)


class AccountService:

    @staticmethod
    def register(username: str, email: str, password: str, password_confirm: str):
        """
        Зарегистрировать пользователя и создать токен.
        Бросает PasswordsDoNotMatch / UsernameAlreadyExists.
        """
        if password != password_confirm:
            raise PasswordsDoNotMatch()

        if User.objects.filter(username=username).exists():
            raise UsernameAlreadyExists()

        user = User.objects.create_user(
            username=username,
            email=email or '',
            password=password,
        )
        token = Token.objects.create(user=user)
        return user, token

    @staticmethod
    def login(username: str, password: str):
        """
        Аутентифицировать пользователя и вернуть токен.
        Бросает InvalidCredentials / AccountDisabled.
        """
        user = authenticate(username=username, password=password)

        if user is None:
            raise InvalidCredentials()

        if not user.is_active:
            raise AccountDisabled()

        token, _ = Token.objects.get_or_create(user=user)
        return user, token

    @staticmethod
    def logout(user):
        """Удалить токен пользователя."""
        user.auth_token.delete()
