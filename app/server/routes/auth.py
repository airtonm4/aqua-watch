"""
Authentication Routes
Rotas de autenticação: login, logout, refresh token, registro
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr

from app.core.auth import (
    authenticate_user,
    login_user,
    logout_user,
    refresh_access_token,
    get_current_user,
)
from app.core.user import schemas as user_schemas
from app.core.user import error as user_error
from app.core import user as user_service


router = APIRouter(prefix="/auth", tags=["Authentication"])


# ==================== Schemas ====================


class LoginRequest(BaseModel):
    """Schema para requisição de login"""

    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Schema para requisição de registro"""

    email: EmailStr
    fullname: str
    password: str
    confirmPassword: str


class RefreshTokenRequest(BaseModel):
    """Schema para refresh token"""

    refresh_token: str


class TokenResponse(BaseModel):
    """Schema de resposta com tokens"""

    access_token: str
    refresh_token: str
    token_type: str


class LoginResponse(TokenResponse):
    """Schema de resposta completa do login"""

    user: user_schemas.UserResponse


# ==================== Endpoints ====================


@router.post(
    "/register", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
def register(data: RegisterRequest):
    """
    Registra um novo usuário

    - **email**: Email único do usuário
    - **fullname**: Nome completo
    - **password**: Senha (mínimo 6 caracteres)
    - **confirmPassword**: Confirmação da senha
    """
    try:
        # Cria o schema CreateUser com os dados da requisição
        create_user_data = user_schemas.CreateUser(
            email=data.email,
            fullname=data.fullname,
            password=data.password,
            confirmPassword=data.confirmPassword
        )
        
        # Chama o serviço de usuário para criar o usuário
        user = user_service.create_user(create_user_data)
        
        return user_schemas.UserResponse(
            id=user.id, 
            email=user.email, 
            fullname=user.fullname
        )
        
    except user_error.UnmatchedPasswordError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )
    except user_error.PasswordTooShortError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except user_error.EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    """
    Realiza login e retorna tokens de acesso

    - **email**: Email do usuário
    - **password**: Senha do usuário

    Retorna:
    - **access_token**: Token para autenticar requisições (expira em 30min)
    - **refresh_token**: Token para renovar o access_token (expira em 7 dias)
    - **user**: Dados básicos do usuário
    """
    # Autentica usuário
    user = authenticate_user(data.email, data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Realiza login (cria sessão e tokens)
    login_data = login_user(user)

    return LoginResponse(**login_data)


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Realiza logout invalidando a sessão atual

    Requer autenticação (Bearer token no header)
    """
    session_id = current_user.get("session_id")

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session"
        )

    success = logout_user(session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to logout"
        )

    return {"message": "Logged out successfully"}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(data: RefreshTokenRequest):
    """
    Renova o access_token usando um refresh_token válido

    - **refresh_token**: Token de refresh obtido no login

    Retorna um novo access_token
    """
    result = refresh_access_token(data.refresh_token)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return result


@router.get("/me", response_model=user_schemas.UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Retorna informações do usuário autenticado

    Requer autenticação (Bearer token no header)
    """
    return user_schemas.UserResponse(
        id=current_user["user_id"],
        email=current_user["email"],
        fullname=current_user["fullname"],
    )


@router.get("/sessions")
async def list_user_sessions(current_user: dict = Depends(get_current_user)):
    """
    Lista todas as sessões ativas do usuário

    Requer autenticação (Bearer token no header)
    """
    from app.services.redis.session import session_manager

    user_id = current_user["user_id"]
    sessions = session_manager.get_user_sessions(user_id)

    return {"total": len(sessions), "sessions": sessions}


@router.delete("/sessions/all")
async def logout_all_sessions(current_user: dict = Depends(get_current_user)):
    """
    Remove todas as sessões do usuário (logout em todos os dispositivos)

    Requer autenticação (Bearer token no header)
    """
    from app.services.redis.session import session_manager

    user_id = current_user["user_id"]
    count = session_manager.delete_user_sessions(user_id)

    return {"message": f"Logged out from {count} sessions", "sessions_deleted": count}
