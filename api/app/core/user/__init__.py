from typing import Optional
from sqlmodel import select
from app.database import DatabaseSession
from app.database.models import User
from . import schemas, error
from app.core.utils import helper_functions


def get_user_by_email(email: str) -> Optional[User]:
    """
    Busca um usuário pelo email
    
    Args:
        email: Email do usuário
        
    Returns:
        User ou None se não encontrado
    """
    with DatabaseSession() as session:
        user = session.exec(select(User).where(User.email == email)).first()
        return user


def get_user_by_id(user_id: int) -> Optional[User]:
    """
    Busca um usuário pelo ID
    
    Args:
        user_id: ID do usuário
        
    Returns:
        User ou None se não encontrado
    """
    with DatabaseSession() as session:
        user = session.get(User, user_id)
        return user


def create_user(data: schemas.CreateUser) -> User:
    """
    Cria um novo usuário no sistema
    
    Args:
        data: Dados do usuário (CreateUser schema)
        
    Returns:
        User criado
        
    Raises:
        UnmatchedPasswordError: Se as senhas não coincidirem
        error.EmailAlreadyExistsError: Se o email já estiver registrado
    """
    if data.password != data.confirmPassword:
        raise error.UnmatchedPasswordError("Passwords do not match")
    
    if len(data.password) < 6:
        raise error.PasswordTooShortError("Password must be at least 6 characters long")

    with DatabaseSession() as session:
        # Verifica se email já existe
        existing_user = session.exec(
            select(User).where(User.email == data.email)
        ).first()
        
        if existing_user:
            raise error.EmailAlreadyExistsError("Email already registered")

        hashed_password = helper_functions.hash_password(data.password)

        user = User(
            email=data.email,
            fullname=data.fullname,
            password=hashed_password,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
