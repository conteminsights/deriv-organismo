"""Testes para serviço de gerenciamento de contas Deriv."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from deriv_organismo.services.deriv_account_service import DerivAccountService
from deriv_organismo.domain.deriv_account import DerivAccount, DerivCredential


@pytest.fixture
def service():
    """Fixture para DerivAccountService com mocks."""
    mock_repo = MagicMock()
    mock_credential_manager = MagicMock()
    mock_validator = AsyncMock()
    
    # Configura comportamento padrão
    mock_validator.validate_token = AsyncMock(return_value=True)
    mock_credential_manager.encrypt_token = MagicMock(return_value="encrypted_token_xyz")
    
    return DerivAccountService(
        account_repository=mock_repo,
        credential_manager=mock_credential_manager,
        token_validator=mock_validator
    )


@pytest.mark.asyncio
async def test_register_account_creates_account_with_valid_token(service):
    """register_account cria conta quando token é válido."""
    service.token_validator.validate_token = AsyncMock(return_value=True)
    service.account_repository.save = MagicMock()
    service.account_repository.get_by_id = MagicMock(return_value=None)
    
    account, credential = await service.register_account(
        tenant_id="tenant_master",
        login_id="CR123456",
        token="valid_token_abc",
        account_type="demo",
        name="Conta Demo"
    )
    
    assert account is not None
    assert account.tenant_id == "tenant_master"
    assert account.login_id == "CR123456"
    assert account.account_type == "demo"
    assert credential is not None
    assert credential.encrypted_token == "encrypted_token_xyz"
    service.account_repository.save.assert_called_once()


@pytest.mark.asyncio
async def test_register_account_fails_with_invalid_token(service):
    """register_account falha quando token é inválido."""
    service.token_validator.validate_token = AsyncMock(return_value=False)
    
    with pytest.raises(ValueError, match="invalid token"):
        await service.register_account(
            tenant_id="tenant_master",
            login_id="CR123456",
            token="invalid_token",
            account_type="demo",
            name="Conta Demo"
        )


@pytest.mark.asyncio
async def test_register_account_rejects_empty_token(service):
    """register_account rejeita token vazio."""
    with pytest.raises(ValueError, match="token cannot be empty"):
        await service.register_account(
            tenant_id="tenant_master",
            login_id="CR123456",
            token="",
            account_type="demo",
            name="Conta Demo"
        )


@pytest.mark.asyncio
async def test_register_account_rejects_invalid_account_type(service):
    """register_account rejeita account_type inválido."""
    service.token_validator.validate_token = AsyncMock(return_value=True)
    
    with pytest.raises(ValueError, match="account_type must be 'demo' or 'real'"):
        await service.register_account(
            tenant_id="tenant_master",
            login_id="CR123456",
            token="valid_token",
            account_type="invalid",
            name="Conta"
        )


@pytest.mark.asyncio
async def test_list_accounts_by_tenant(service):
    """list_accounts_by_tenant retorna contas filtradas."""
    mock_accounts = [
        DerivAccount(
            account_id="acc_1",
            tenant_id="tenant_a",
            login_id="CR111",
            account_type="demo",
            name="Conta 1"
        )
    ]
    service.account_repository.list_by_tenant = MagicMock(return_value=mock_accounts)
    
    result = service.list_accounts_by_tenant("tenant_a")
    
    assert len(result) == 1
    assert result[0].tenant_id == "tenant_a"
    service.account_repository.list_by_tenant.assert_called_once_with("tenant_a")


@pytest.mark.asyncio
async def test_deactivate_account_sets_is_active_false(service):
    """deactivate_account marca conta como inativa."""
    account = DerivAccount(
        account_id="acc_123",
        tenant_id="tenant_master",
        login_id="CR123456",
        account_type="demo",
        name="Conta Ativa",
        is_active=True
    )
    service.account_repository.get_by_id = MagicMock(return_value=account)
    service.account_repository.save = MagicMock()
    
    result = service.deactivate_account("acc_123")
    
    assert result.is_active is False
    service.account_repository.save.assert_called_once()


@pytest.mark.asyncio
async def test_deactivate_account_fails_if_not_found(service):
    """deactivate_account falha se conta não existir."""
    service.account_repository.get_by_id = MagicMock(return_value=None)
    
    with pytest.raises(ValueError, match="account not found"):
        service.deactivate_account("nonexistent")
