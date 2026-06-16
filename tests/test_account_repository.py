"""Testes para repositório de contas Deriv."""
import pytest
from deriv_organismo.repositories.account_repository import AccountRepository
from deriv_organismo.domain.deriv_account import DerivAccount


def test_account_repository_saves_and_retrieves_account():
    """Repository salva e recupera conta por account_id."""
    repo = AccountRepository()
    
    account = DerivAccount(
        account_id="acc_123",
        tenant_id="tenant_master",
        login_id="CR123456",
        account_type="demo",
        name="Conta Demo Principal"
    )
    
    repo.save(account)
    retrieved = repo.get_by_id("acc_123")
    
    assert retrieved is not None
    assert retrieved.account_id == "acc_123"
    assert retrieved.tenant_id == "tenant_master"
    assert retrieved.login_id == "CR123456"


def test_account_repository_returns_none_for_nonexistent_account():
    """Repository retorna None para conta inexistente."""
    repo = AccountRepository()
    
    result = repo.get_by_id("nonexistent")
    
    assert result is None


def test_account_repository_lists_accounts_by_tenant():
    """Repository lista contas filtradas por tenant_id."""
    repo = AccountRepository()
    
    account_a1 = DerivAccount(
        account_id="acc_a1",
        tenant_id="tenant_a",
        login_id="CR111111",
        account_type="demo",
        name="Conta A1"
    )
    account_a2 = DerivAccount(
        account_id="acc_a2",
        tenant_id="tenant_a",
        login_id="CR222222",
        account_type="real",
        name="Conta A2"
    )
    account_b = DerivAccount(
        account_id="acc_b",
        tenant_id="tenant_b",
        login_id="CR333333",
        account_type="demo",
        name="Conta B"
    )
    
    repo.save(account_a1)
    repo.save(account_a2)
    repo.save(account_b)
    
    tenant_a_accounts = repo.list_by_tenant("tenant_a")
    tenant_b_accounts = repo.list_by_tenant("tenant_b")
    
    assert len(tenant_a_accounts) == 2
    assert len(tenant_b_accounts) == 1
    assert all(acc.tenant_id == "tenant_a" for acc in tenant_a_accounts)
    assert all(acc.tenant_id == "tenant_b" for acc in tenant_b_accounts)


def test_account_repository_updates_account():
    """Repository atualiza conta existente."""
    repo = AccountRepository()
    
    account = DerivAccount(
        account_id="acc_123",
        tenant_id="tenant_master",
        login_id="CR123456",
        account_type="demo",
        name="Conta Original"
    )
    repo.save(account)
    
    account.name = "Conta Atualizada"
    repo.save(account)
    
    retrieved = repo.get_by_id("acc_123")
    assert retrieved.name == "Conta Atualizada"


def test_account_repository_deletes_account():
    """Repository deleta conta por account_id."""
    repo = AccountRepository()
    
    account = DerivAccount(
        account_id="acc_123",
        tenant_id="tenant_master",
        login_id="CR123456",
        account_type="demo",
        name="Conta para Deletar"
    )
    repo.save(account)
    
    repo.delete("acc_123")
    
    assert repo.get_by_id("acc_123") is None


def test_account_repository_prevents_cross_tenant_access():
    """Repository impede que tenant veja contas de outro tenant."""
    repo = AccountRepository()
    
    account = DerivAccount(
        account_id="acc_private",
        tenant_id="tenant_a",
        login_id="CR123456",
        account_type="demo",
        name="Conta Privada"
    )
    repo.save(account)
    
    # Tentar recuperar com tenant_id errado deve retornar None
    result = repo.get_by_tenant_and_id("tenant_b", "acc_private")
    
    assert result is None
