"""
Session Management with Redis
Gerenciamento de sessões de usuário usando Redis
"""
import json
import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from . import get_redis
from app.core import env
from app.core.utils.logging import log


class SessionManager:
    """Gerenciador de sessões com Redis"""
    
    def __init__(self):
        self.redis = get_redis()
        self.prefix = env.SESSION_PREFIX
        self.expire_seconds = env.SESSION_EXPIRE_SECONDS
    
    def _make_key(self, session_id: str) -> str:
        """Cria a chave completa da sessão"""
        return f"{self.prefix}{session_id}"
    
    def create_session(
        self,
        user_id: int,
        user_data: Dict[str, Any],
        expire_seconds: Optional[int] = None
    ) -> str:
        """
        Cria uma nova sessão para o usuário
        
        Args:
            user_id: ID do usuário
            user_data: Dados adicionais do usuário (email, fullname, etc)
            expire_seconds: Tempo de expiração customizado (opcional)
        
        Returns:
            str: ID da sessão criada
        """
        session_id = str(uuid.uuid4())
        key = self._make_key(session_id)
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            **user_data
        }
        
        expire = expire_seconds or self.expire_seconds
        
        try:
            self.redis.setex(
                key,
                expire,
                json.dumps(session_data)
            )
            log.info(f"Session created for user {user_id}: {session_id}")
            return session_id
        
        except Exception as e:
            log.error(f"Error creating session for user {user_id}: {e}")
            raise
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Obtém os dados da sessão
        
        Args:
            session_id: ID da sessão
        
        Returns:
            Dict com dados da sessão ou None se não existir
        """
        key = self._make_key(session_id)
        
        try:
            data = self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        
        except Exception as e:
            log.error(f"Error getting session {session_id}: {e}")
            return None
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Atualiza os dados da sessão mantendo o TTL
        
        Args:
            session_id: ID da sessão
            data: Novos dados para atualizar
        
        Returns:
            bool: True se atualizado com sucesso
        """
        key = self._make_key(session_id)
        
        try:
            # Obtém dados atuais
            current_data = self.get_session(session_id)
            if not current_data:
                return False
            
            # Atualiza com novos dados
            current_data.update(data)
            current_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Obtém o TTL atual
            ttl = self.redis.ttl(key)
            if ttl < 0:
                ttl = self.expire_seconds
            
            # Salva com o TTL original
            self.redis.setex(
                key,
                ttl,
                json.dumps(current_data)
            )
            
            log.info(f"Session updated: {session_id}")
            return True
        
        except Exception as e:
            log.error(f"Error updating session {session_id}: {e}")
            return False
    
    def refresh_session(self, session_id: str) -> bool:
        """
        Renova o tempo de expiração da sessão
        
        Args:
            session_id: ID da sessão
        
        Returns:
            bool: True se renovado com sucesso
        """
        key = self._make_key(session_id)
        
        try:
            if self.redis.exists(key):
                self.redis.expire(key, self.expire_seconds)
                log.info(f"Session refreshed: {session_id}")
                return True
            return False
        
        except Exception as e:
            log.error(f"Error refreshing session {session_id}: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Remove a sessão (logout)
        
        Args:
            session_id: ID da sessão
        
        Returns:
            bool: True se removido com sucesso
        """
        key = self._make_key(session_id)
        
        try:
            result = self.redis.delete(key)
            if result:
                log.info(f"Session deleted: {session_id}")
            return bool(result)
        
        except Exception as e:
            log.error(f"Error deleting session {session_id}: {e}")
            return False
    
    def delete_user_sessions(self, user_id: int) -> int:
        """
        Remove todas as sessões de um usuário
        
        Args:
            user_id: ID do usuário
        
        Returns:
            int: Número de sessões removidas
        """
        try:
            # Busca todas as chaves de sessão
            pattern = f"{self.prefix}*"
            count = 0
            
            for key in self.redis.scan_iter(match=pattern):
                data = self.redis.get(key)
                if data:
                    session_data = json.loads(data)
                    if session_data.get("user_id") == user_id:
                        self.redis.delete(key)
                        count += 1
            
            log.info(f"Deleted {count} sessions for user {user_id}")
            return count
        
        except Exception as e:
            log.error(f"Error deleting user sessions for user {user_id}: {e}")
            return 0
    
    def get_user_sessions(self, user_id: int) -> list[Dict[str, Any]]:
        """
        Lista todas as sessões ativas de um usuário
        
        Args:
            user_id: ID do usuário
        
        Returns:
            Lista de sessões ativas
        """
        try:
            pattern = f"{self.prefix}*"
            sessions = []
            
            for key in self.redis.scan_iter(match=pattern):
                data = self.redis.get(key)
                if data:
                    session_data = json.loads(data)
                    if session_data.get("user_id") == user_id:
                        session_id = key.replace(self.prefix, "")
                        sessions.append({
                            "session_id": session_id,
                            **session_data
                        })
            
            return sessions
        
        except Exception as e:
            log.error(f"Error getting user sessions for user {user_id}: {e}")
            return []


# Instância global do gerenciador de sessão
session_manager = SessionManager()


__all__ = [
    "SessionManager",
    "session_manager",
]
