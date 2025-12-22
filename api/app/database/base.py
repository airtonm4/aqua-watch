"""
SQLModel Base Configuration
Novo arquivo base usando SQLModel ao invés de SQLAlchemy puro
"""
from sqlmodel import SQLModel, Field, Session, create_engine
from typing import Optional
from datetime import datetime
import uuid

# SQLModel já combina SQLAlchemy + Pydantic
# Não precisa mais de declarative_base, tudo vem do SQLModel

# Re-exportar tipos comuns para facilitar imports
from sqlalchemy import (
    BigInteger,
    SmallInteger,
    Text,
    func,
    select,
    and_,
    or_,
    case,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY
from sqlalchemy.ext.hybrid import hybrid_property

# Custom types que ainda precisamos (os mais complexos)
from .custom_types import (
    Timestamp,
)

__all__ = [
    "SQLModel",
    "Field",
    "Session",
    "create_engine",
    "BigInteger",
    "SmallInteger",
    "Text",
    "JSONB",
    "UUID",
    "ARRAY",
    "Timestamp",
    "func",
    "select",
    "and_",
    "or_",
    "case",
    "hybrid_property",
]
