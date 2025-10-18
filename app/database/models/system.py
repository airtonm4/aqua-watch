from typing import Optional
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """
    Tabela de Autenticação da Plataforma.

    """

    __tablename__: str = "user"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    email: EmailStr = Field(index=True, unique=True)
    fullname: str
    password: str  # Hash da senha
