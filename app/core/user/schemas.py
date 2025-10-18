from pydantic import BaseModel


class User(BaseModel):
    id: int
    email: str
    fullname: str


class CreateUser(BaseModel):
    email: str
    fullname: str
    password: str  # Plain password, will be hashed before storing
    confirmPassword: str
