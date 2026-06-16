"""Testes para validação de token Deriv."""
import pytest
from unittest.mock import AsyncMock, patch
from deriv_organismo.services.deriv_token_validator import DerivTokenValidator


@pytest.mark.asyncio
async def test_deriv_token_validator_returns_true_for_valid_token():
    """Validator retorna True quando token é válido."""
    validator = DerivTokenValidator()
    
    with patch.object(validator, '_validate_with_deriv', new_callable=AsyncMock) as mock_validate:
        mock_validate.return_value = True
        
        result = await validator.validate_token(
            token="valid_token_abc123",
            login_id="CR123456"
        )
        
        assert result is True


@pytest.mark.asyncio
async def test_deriv_token_validator_returns_false_for_invalid_token():
    """Validator retorna False quando token é inválido."""
    validator = DerivTokenValidator()
    
    with patch.object(validator, '_validate_with_deriv', new_callable=AsyncMock) as mock_validate:
        mock_validate.return_value = False
        
        result = await validator.validate_token(
            token="invalid_token_xyz",
            login_id="CR999999"
        )
        
        assert result is False


@pytest.mark.asyncio
async def test_deriv_token_validator_rejects_empty_token():
    """Validator rejeita token vazio."""
    validator = DerivTokenValidator()
    
    with pytest.raises(ValueError, match="token cannot be empty"):
        await validator.validate_token(token="", login_id="CR123456")


@pytest.mark.asyncio
async def test_deriv_token_validator_rejects_empty_login_id():
    """Validator rejeita login_id vazio."""
    validator = DerivTokenValidator()
    
    with pytest.raises(ValueError, match="login_id cannot be empty"):
        await validator.validate_token(token="valid_token", login_id="")


@pytest.mark.asyncio
async def test_deriv_token_validator_handles_network_error():
    """Validator trata erros de rede gracefully."""
    validator = DerivTokenValidator()
    
    with patch.object(validator, '_validate_with_deriv', new_callable=AsyncMock) as mock_validate:
        mock_validate.side_effect = Exception("Network error")
        
        result = await validator.validate_token(
            token="valid_token",
            login_id="CR123456"
        )
        
        assert result is False
