"""
Database Session Management com SQLModel
Gerenciamento de conexões e sessões do banco de dados
"""
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional, Generator

from sqlmodel import create_engine, Session, SQLModel

from app.core import env


# Engine de conexão com o banco
if env.SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        env.SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,  # True para debug SQL
    )
else:
    engine = create_engine(
        env.SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,  # Verifica conexões antes de usar
        pool_size=5,
        max_overflow=10,
        echo=False,  # True para debug SQL
    )

# Context var para armazenar a sessão atual
database_session = ContextVar[Session]("database_session")


@contextmanager
def DatabaseSession(custom_session: Optional[Session] = None) -> Generator[Session, None, None]:
    """
    Context manager para gerenciar sessões do banco de dados.
    
    Uso:
        with DatabaseSession() as session:
            # usar session aqui
            booking = session.get(Booking, booking_id)
    
    Args:
        custom_session: Sessão customizada (útil para testes)
    
    Yields:
        Session: Sessão do SQLModel/SQLAlchemy
    """
    if custom_session is not None:
        _session = custom_session
    else:
        _session = Session(engine, expire_on_commit=False)

    context_token = database_session.set(_session)
    
    try:
        yield _session
        # Commit automático se não houver exceção
        _session.commit()
    except Exception as e:
        # Rollback em caso de erro
        _session.rollback()
        raise
    finally:
        _session.close()
        database_session.reset(context_token)


def get_session() -> Session:
    """
    Retorna a sessão atual do context var.
    Útil para usar como dependency no FastAPI.
    
    Usage:
        @app.get("/users")
        def get_users():
            session = get_session()
            return session.exec(select(User)).all()
    """
    return database_session.get()


def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas.
    Use apenas em desenvolvimento ou para testes.
    Em produção, use Alembic para migrations.
    """
    SQLModel.metadata.create_all(engine)


def drop_db():
    """
    Remove todas as tabelas do banco de dados.
    CUIDADO: Use apenas em desenvolvimento/testes!
    """
    SQLModel.metadata.drop_all(engine)


# Importar todos os models para que o SQLModel os registre
# Isso é necessário para o Alembic detectar os models
from . import models

__all__ = [
    "engine",
    "DatabaseSession",
    "get_session",
    "database_session",
    "init_db",
    "drop_db",
    "SQLModel",
    "Session",
]
