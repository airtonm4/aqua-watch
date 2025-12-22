"""
Utility Functions para SQLModel
Funções auxiliares simplificadas para trabalhar com models
"""
import datetime
import random
import string
from typing import Optional


def datetime_now() -> datetime.datetime:
    """Retorna datetime atual em UTC"""
    return datetime.datetime.now(tz=datetime.timezone.utc)


__all__ = [
    "datetime_now",
]
