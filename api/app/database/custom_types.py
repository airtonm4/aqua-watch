"""
Custom Types Simplificados para SQLModel
Mantém apenas os types customizados mais complexos que não têm equivalente direto no Pydantic
"""
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.types import TypeDecorator
from sqlalchemy import DateTime


class Timestamp(TypeDecorator):
    """
    Armazena datetime sempre em UTC no banco.
    Converte automaticamente para UTC ao salvar e ao recuperar.
    """
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(
        self, value: Optional[datetime], dialect: Dialect
    ) -> Optional[datetime]:
        """Converte para UTC antes de salvar no banco"""
        if value is None:
            return None

        if value.tzinfo is None:
            raise ValueError("Cannot save a naive datetime object. Use timezone-aware datetime.")

        return value.astimezone(timezone.utc)

    def process_result_value(
        self, value: Optional[datetime], dialect: Dialect
    ) -> Optional[datetime]:
        """Garante que o valor retornado está em UTC"""
        if value is None:
            return None

        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)


__all__ = [
    "Timestamp",
]
