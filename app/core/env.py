import os

LOAD_FROM_DOTENV = (
    os.environ.get("LOAD_FROM_DOTENV", "True").lower() == "true"
)  # defaults to false in production
if LOAD_FROM_DOTENV:
    import dotenv

    dotenv.load_dotenv()

SQLALCHEMY_DATABASE_URL = os.environ.get(
    "SQLALCHEMY_DATABASE_URL", "sqlite:///./local.sql_app.db"
)
