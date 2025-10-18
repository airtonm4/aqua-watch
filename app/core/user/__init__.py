from app.database import DatabaseSession
from . import schemas, error
from database import models
from app.core.utils import helper_functions


def create_user(data: schemas.CreateUser):
    if data.password != data.confirmPassword:
        raise error.UnmatchedPasswordError("Passwords do not match")

    with DatabaseSession() as session:

        hashed_password = helper_functions.hash_password(data.password)

        user = models.User(
            email=data.email,
            fullname=data.fullname,
            password=hashed_password,  # Lembre-se de hashear a senha em produção
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
