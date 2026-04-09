"""
Единый обработчик доменных исключений для DRF
Перехватывает DomainException и возвращает Response с правильным статусом
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response

from core.exceptions import DomainException


def custom_exception_handler(exc, context):
    """
    Если исключение — DomainException, возвращаем Response с
    detail и error_code. Иначе - стандартный обработчик DRF
    """
    if isinstance(exc, DomainException):
        return Response(
            {'detail': exc.detail, 'code': exc.error_code},
            status=exc.status_code,
        )

    return exception_handler(exc, context)
