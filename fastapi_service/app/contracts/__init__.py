"""Контракты (DTO) внешних сервисов, с которыми работает BFF.

Схемы в `app/schemas` описывают API, которое BFF отдаёт фронту,
а здесь — то, что BFF получает от Django и UGC.
"""

from typing import Any, TypeVar

from pydantic import BaseModel, TypeAdapter, ValidationError

from app.core.exceptions import AppException

T = TypeVar("T")


def parse_contract(contract: type[T], data: Any, *, source: str) -> T:
    """Валидирует ответ внешнего сервиса по контракту, иначе 502"""
    try:
        if isinstance(contract, type) and issubclass(contract, BaseModel):
            return contract.model_validate(data)
        return TypeAdapter(contract).validate_python(data)
    except ValidationError as exc:
        raise AppException(
            code=f"{source.upper()}_CONTRACT_VIOLATION",
            message=f"Unexpected response format from {source}: {exc.error_count()} error(s)",
            status_code=502,
        ) from exc
