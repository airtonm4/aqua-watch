"""
Redis Client Configuration
Gerenciamento de conexão com Redis
"""

import redis
from typing import Optional
from app.core import env
from app.core.utils.logging import log


class RedisClient:
    """Cliente singleton para Redis"""

    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_instance(cls) -> redis.Redis:
        """
        Retorna a instância singleton do Redis client

        Returns:
            redis.Redis: Cliente Redis configurado
        """
        if cls._instance is None:
            try:
                cls._instance = redis.Redis(
                    host=env.REDIS_HOST,
                    port=env.REDIS_PORT,
                    password=env.REDIS_PASSWORD,
                    db=env.REDIS_DB,
                    decode_responses=env.REDIS_DECODE_RESPONSES,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )

                # Testa a conexão
                cls._instance.ping()
                log.info("Redis connection established successfully")

            except redis.ConnectionError as e:
                log.error(f"Failed to connect to Redis: {e}")
                raise
            except Exception as e:
                log.error(f"Unexpected error connecting to Redis: {e}")
                raise

        return cls._instance

    @classmethod
    def close(cls):
        """Fecha a conexão com Redis"""
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None
            log.info("Redis connection closed")


def get_redis() -> redis.Redis:
    """
    Função helper para obter o cliente Redis

    Usage:
        redis_client = get_redis()
        redis_client.set("key", "value")

    Returns:
        redis.Redis: Cliente Redis
    """
    return RedisClient.get_instance()


__all__ = [
    "RedisClient",
    "get_redis",
]
