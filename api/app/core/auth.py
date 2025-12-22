"""
Authentication Module
Módulo de autenticação com JWT e gerenciamento de sessão Redis
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core import env
from app.services.redis.session import session_manager
from app.core.utils.helper_functions import verify_hash
from app.core.utils.logging import log
from app.database import DatabaseSession
from app.database.models import User
from sqlmodel import select


# Configuração do Bearer Token
security = HTTPBearer()


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Cria um token JWT de acesso

    Args:
        data: Dados a serem incluídos no token
        expires_delta: Tempo de expiração customizado (opcional)

    Returns:
        str: Token JWT
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=env.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(to_encode, env.JWT_SECRET_KEY, algorithm=env.JWT_ALGORITHM)

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Cria um token JWT de refresh

    Args:
        data: Dados a serem incluídos no token

    Returns:
        str: Token JWT de refresh
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=env.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(to_encode, env.JWT_SECRET_KEY, algorithm=env.JWT_ALGORITHM)

    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verifica e decodifica um token JWT

    Args:
        token: Token JWT
        token_type: Tipo esperado do token ("access" ou "refresh")

    Returns:
        Dict com payload do token ou None se inválido
    """
    try:
        payload = jwt.decode(token, env.JWT_SECRET_KEY, algorithms=[env.JWT_ALGORITHM])

        # Verifica o tipo do token
        if payload.get("type") != token_type:
            log.warning(
                f"Token type mismatch. Expected: {token_type}, Got: {payload.get('type')}"
            )
            return None

        return payload

    except JWTError as e:
        log.warning(f"JWT verification failed: {e}")
        return None


def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Autentica um usuário verificando email e senha

    Args:
        email: Email do usuário
        password: Senha em texto plano

    Returns:
        User: Objeto do usuário se autenticado, None caso contrário
    """
    with DatabaseSession() as session:
        statement = select(User).where(User.email == email)
        user = session.exec(statement).first()

        if not user:
            log.warning(f"Login attempt with non-existent email: {email}")
            return None

        if not verify_hash(user.password, password):
            log.warning(f"Invalid password for user: {email}")
            return None

        log.info(f"User authenticated successfully: {email}")
        return user


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    Dependency para obter o usuário atual autenticado

    Args:
        credentials: Credenciais do Bearer token

    Returns:
        Dict: Dados do usuário da sessão

    Raises:
        HTTPException: Se o token for inválido ou a sessão não existir
    """
    token = credentials.credentials

    # Verifica o token
    payload = verify_token(token, token_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Obtém o session_id do token
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica se a sessão existe no Redis
    session_data = session_manager.get_session(session_id)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Renova o tempo da sessão a cada requisição
    session_manager.refresh_session(session_id)

    return session_data


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[Dict[str, Any]]:
    """
    Dependency opcional para obter o usuário atual (não lança exceção se não autenticado)

    Args:
        credentials: Credenciais do Bearer token (opcional)

    Returns:
        Dict: Dados do usuário ou None
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def login_user(user: User) -> Dict[str, Any]:
    """
    Realiza o login do usuário, criando sessão e tokens

    Args:
        user: Objeto do usuário

    Returns:
        Dict: Contém access_token, refresh_token e dados do usuário
    """
    # Cria sessão no Redis
    user_data = {
        "email": user.email,
        "fullname": user.fullname,
    }
    session_id = session_manager.create_session(user_id=user.id, user_data=user_data)

    # Cria tokens JWT
    token_data = {
        "sub": str(user.id),
        "session_id": session_id,
        "email": user.email,
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    log.info(f"User logged in: {user.email}")

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "fullname": user.fullname,
        },
    }


def logout_user(session_id: str) -> bool:
    """
    Realiza o logout do usuário removendo a sessão

    Args:
        session_id: ID da sessão

    Returns:
        bool: True se logout bem sucedido
    """
    result = session_manager.delete_session(session_id)
    if result:
        log.info(f"User logged out, session deleted: {session_id}")
    return result


def refresh_access_token(refresh_token: str) -> Optional[Dict[str, Any]]:
    """
    Cria um novo access_token usando um refresh_token válido

    Args:
        refresh_token: Token de refresh

    Returns:
        Dict: Novo access_token ou None se inválido
    """
    # Verifica o refresh token
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        return None

    # Verifica se a sessão ainda existe
    session_id = payload.get("session_id")
    if not session_id:
        return None

    session_data = session_manager.get_session(session_id)
    if not session_data:
        return None

    # Cria novo access token
    token_data = {
        "sub": payload.get("sub"),
        "session_id": session_id,
        "email": payload.get("email"),
    }

    new_access_token = create_access_token(token_data)

    log.info(f"Access token refreshed for session: {session_id}")

    return {"access_token": new_access_token, "token_type": "bearer"}


__all__ = [
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "authenticate_user",
    "get_current_user",
    "get_current_user_optional",
    "login_user",
    "logout_user",
    "refresh_access_token",
]
