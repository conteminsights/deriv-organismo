"""Repositório de contas Deriv (implementação in-memory)."""
from typing import Optional
from deriv_organismo.domain.deriv_account import DerivAccount


class AccountRepository:
    """Repositório para gerenciamento de contas Deriv."""
    
    def __init__(self):
        """Inicializa o repositório com storage em memória."""
        self._accounts: dict[str, DerivAccount] = {}
    
    def save(self, account: DerivAccount) -> None:
        """
        Salva ou atualiza uma conta.
        
        Args:
            account: Conta Deriv a ser salva.
        """
        self._accounts[account.account_id] = account
    
    def get_by_id(self, account_id: str) -> Optional[DerivAccount]:
        """
        Recupera uma conta por account_id.
        
        Args:
            account_id: ID único da conta.
            
        Returns:
            Conta se encontrada, None caso contrário.
        """
        return self._accounts.get(account_id)
    
    def get_by_tenant_and_id(self, tenant_id: str, account_id: str) -> Optional[DerivAccount]:
        """
        Recupera uma conta filtrada por tenant_id e account_id.
        
        Impede acesso cross-tenant.
        
        Args:
            tenant_id: ID do tenant.
            account_id: ID da conta.
            
        Returns:
            Conta se encontrada e pertencer ao tenant, None caso contrário.
        """
        account = self._accounts.get(account_id)
        if account and account.tenant_id == tenant_id:
            return account
        return None
    
    def list_by_tenant(self, tenant_id: str) -> list[DerivAccount]:
        """
        Lista todas as contas de um tenant específico.
        
        Args:
            tenant_id: ID do tenant.
            
        Returns:
            Lista de contas do tenant.
        """
        return [
            acc for acc in self._accounts.values()
            if acc.tenant_id == tenant_id
        ]
    
    def delete(self, account_id: str) -> None:
        """
        Deleta uma conta por account_id.
        
        Args:
            account_id: ID único da conta.
        """
        self._accounts.pop(account_id, None)
    
    def clear(self) -> None:
        """Limpa todas as contas (útil para testes)."""
        self._accounts.clear()
