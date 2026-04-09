"""
Доменные исключения - бизнес-правила, выраженные как ошибки
Каждое исключение знает свой HTTP-статус и дефолтное сообщение
"""


class DomainException(Exception):
    """Базовое доменное исключение"""
    status_code = 500
    default_detail = 'Произошла ошибка'
    error_code = 'DOMAIN_ERROR'

    def __init__(self, detail=None):
        self.detail = detail or self.default_detail

    def __str__(self):
        return self.detail


# Accounts

class InvalidCredentials(DomainException):
    status_code = 401
    default_detail = 'Неверное имя пользователя или пароль'
    error_code = 'INVALID_CREDENTIALS'


class AccountDisabled(DomainException):
    status_code = 403
    default_detail = 'Аккаунт деактивирован'
    error_code = 'ACCOUNT_DISABLED'


class UsernameAlreadyExists(DomainException):
    status_code = 400
    default_detail = 'Пользователь с таким именем уже существует'
    error_code = 'USERNAME_ALREADY_EXISTS'


class PasswordsDoNotMatch(DomainException):
    status_code = 400
    default_detail = 'Пароли не совпадают'
    error_code = 'PASSWORDS_DO_NOT_MATCH'


# Subscriptions 

class AlreadySubscribed(DomainException):
    status_code = 400
    default_detail = 'У вас уже есть активная подписка'
    error_code = 'ALREADY_SUBSCRIBED'


class SubscriptionAlreadyCancelled(DomainException):
    status_code = 400
    default_detail = 'Подписка уже неактивна'
    error_code = 'SUBSCRIPTION_ALREADY_CANCELLED'


# Watchlist

class AlreadyInWatchlist(DomainException):
    status_code = 400
    default_detail = 'Этот фильм уже есть в вашем списке'
    error_code = 'ALREADY_IN_WATCHLIST'
