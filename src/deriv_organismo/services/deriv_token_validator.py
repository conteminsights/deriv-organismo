"""Validador de token Deriv."""
import logging
from typing import Optional


logger = logging.getLogger(__name__)


class DerivTokenValidator:
    """Valida tokens da API Deriv via websocket."""
    
    async def validate_token(self, token: str, login_id: str) -> bool:
        """
        Valida se o token é válido para o login_id especificado.
        
        Args:
            token: Token da API Deriv.
            login_id: Login ID da conta Deriv (ex: CR123456).
            
        Returns:
            True se o token for válido, False caso contrário.
            
        Raises:
            ValueError: Se token ou login_id estiverem vazios.
        """
        if not token:
            raise ValueError("token cannot be empty")
        if not login_id:
            raise ValueError("login_id cannot be empty")
        
        try:
            return await self._validate_with_deriv(token, login_id)
        except Exception as e:
            logger.error(f"Token validation failed for {login_id}: {e}")
            return False
    
    async def _validate_with_deriv(self, token: str, login_id: str) -> bool:
        """
        Valida o token fazendo uma chamada à API Deriv.
        
        Implementação real com websocket virá na próxima fase.
        Por enquanto, retorna True para tokens não-vazios (mock).
        
        Args:
            token: Token da API Deriv.
            login_id: Login ID da conta.
            
        Returns:
            True se válido, False caso contrário.
        """
        # TODO: Implementar validação real via websocket Deriv
        # Por enquanto, aceita qualquer token não-vazio como válido
        return bool(token and login_id)
