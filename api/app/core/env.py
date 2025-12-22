import os

LOAD_FROM_DOTENV = (
    os.environ.get("LOAD_FROM_DOTENV", "True").lower() == "true"
)  # defaults to false in production
if LOAD_FROM_DOTENV:
    import dotenv

    dotenv.load_dotenv()

# Database Configuration
SQLALCHEMY_DATABASE_URL = os.environ.get(
    "SQLALCHEMY_DATABASE_URL", "sqlite:///./local.sql_app.db"
)

# Redis Configuration
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", None)
REDIS_DB = int(os.environ.get("REDIS_DB", "0"))
REDIS_DECODE_RESPONSES = True

# JWT Configuration
JWT_SECRET_KEY = os.environ.get(
    "JWT_SECRET_KEY", "your-secret-key-change-in-production"
)
JWT_ALGORITHM = os.environ.get("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.environ.get("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Session Configuration
SESSION_PREFIX = "session:"
SESSION_EXPIRE_SECONDS = ACCESS_TOKEN_EXPIRE_MINUTES * 60
