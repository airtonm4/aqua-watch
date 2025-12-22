from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    email: str
    fullname: str


class CreateUser(BaseModel):
    email: EmailStr
    fullname: str
    password: str  # Plain password, will be hashed before storing
    confirmPassword: str


class UserResponse(BaseModel):
    """Schema de resposta com dados do usuário"""
    id: int
    email: str
    fullname: str
