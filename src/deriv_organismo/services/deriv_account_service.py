"""Serviço de gerenciamento de contas Deriv."""
import uuid
from datetime import datetime, timezone
from typing import Literal

from deriv_organismo.domain.deriv_account import DerivAccount, DerivCredential
from deriv_organismo.repositories.account_repository import AccountRepository
from deriv_organismo.services.credential_manager import CredentialManager
from deriv_organismo.services.deriv_token_validator import DerivTokenValidator


class DerivAccountService:
    """Serviço para gerenciar contas Deriv com validação e criptografia."""
    
    def __init__(
        self,
        account_repository: AccountRepository,
        credential_manager: CredentialManager,
        token_validator: DerivTokenValidator
    ):
        """
        Inicializa o serviço.
        
        Args:
            account_repository: Repositório de contas.
            credential_manager: Gerenciador de credenciais criptografadas.
            token_validator: Validador de tokens Deriv.
        """
        self.account_repository = account_repository
        self.credential_manager = credential_manager
        self.token_validator = token_validator
    
    async def register_account(
        self,
        tenant_id: str,
        login_id: str,
        token: str,
        account_type: Literal["demo", "real"],
        name: str
    ) -> tuple[DerivAccount, DerivCredential]:
        """
        Registra uma nova conta Deriv com validação de token.
        
        Args:
            tenant_id: ID do tenant.
            login_id: Login ID da conta Deriv.
            token: Token da API Deriv.
            account_type: Tipo da conta ("demo" ou "real").
            name: Nome amigável da conta.
            
        Returns:
            Tupla (conta, credencial) criadas.
            
        Raises:
            ValueError: Se token for inválido, vazio, ou account_type inválido.
        """
        if not token:
            raise ValueError("token cannot be empty")
        
        if account_type not in ("demo", "real"):
            raise ValueError("account_type must be 'demo' or 'real'")
        
        # Valida token
        is_valid = await self.token_validator.validate_token(token, login_id)
        if not is_valid:
            raise ValueError("invalid token")
        
        # Cria conta
        account_id = f"acc_{uuid.uuid4().hex[:8]}"
        account = DerivAccount(
            account_id=account_id,
            tenant_id=tenant_id,
            login_id=login_id,
            account_type=account_type,
            name=name,
            is_active=True
        )
        
        # Criptografa token
        encrypted_token = self.credential_manager.encrypt_token(token)
        
        # Cria credencial
        credential = DerivCredential(
            account_id=account_id,
            tenant_id=tenant_id,
            encrypted_token=encrypted_token,
            is_valid=True
        )
        
        # Salva conta
        self.account_repository.save(account)
        
        return account, credential
    
    def list_accounts_by_tenant(self, tenant_id: str) -> list[DerivAccount]:
        """
        Lista todas as contas de um tenant.
        
        Args:
            tenant_id: ID do tenant.
            
        Returns:
            Lista de contas do tenant.
        """
        return self.account_repository.list_by_tenant(tenant_id)
    
    def deactivate_account(self, account_id: str) -> DerivAccount:
        """
        Desativa uma conta (marca como inativa).
        
        Args:
            account_id: ID da conta.
            
        Returns:
            Conta desativada.
            
        Raises:
            ValueError: Se conta não existir.
        """
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise ValueError("account not found")
        
        account.is_active = False
        self.account_repository.save(account)
        
        return account
