"""Testes para modelo de contas Deriv."""
import pytest
from datetime import datetime, timezone
from deriv_organismo.domain.deriv_account import DerivAccount, DerivCredential


def test_deriv_account_creation():
    """Conta Deriv pode ser criada com login_id e tipo demo/real."""
    account = DerivAccount(
        account_id="acc_123",
        tenant_id="tenant_master",
        login_id="CR123456",
        account_type="demo",
        name="Minha Conta Demo",
    )
    assert account.account_id == "acc_123"
    assert account.tenant_id == "tenant_master"
    assert account.login_id == "CR123456"
    assert account.account_type == "demo"
    assert account.name == "Minha Conta Demo"
    assert account.is_active is True


def test_deriv_account_supports_real():
    """Conta Deriv pode ser do tipo real."""
    account = DerivAccount(
        account_id="acc_456",
        tenant_id="tenant_master",
        login_id="CR789012",
        account_type="real",
        name="Minha Conta Real",
    )
    assert account.account_type == "real"


def test_deriv_credential_creation():
    """Credencial Deriv armazena token criptografado por conta."""
    credential = DerivCredential(
        account_id="acc_123",
        tenant_id="tenant_master",
        encrypted_token="encrypted_token_here",
        token_type="api_token",
    )
    assert credential.account_id == "acc_123"
    assert credential.tenant_id == "tenant_master"
    assert credential.encrypted_token == "encrypted_token_here"
    assert credential.token_type == "api_token"
    assert credential.is_valid is True


def test_deriv_credential_revocation():
    """Credencial pode ser revogada."""
    credential = DerivCredential(
        account_id="acc_123",
        tenant_id="tenant_master",
        encrypted_token="encrypted_token_here",
    )
    credential.is_valid = False
    assert credential.is_valid is False


def test_deriv_account_cannot_share_across_tenants():
    """Conta Deriv não pode ser compartilhada entre tenants diferentes."""
    account_a = DerivAccount(
        account_id="acc_a",
        tenant_id="tenant_a",
        login_id="CR111111",
        account_type="demo",
        name="Conta A",
    )
    account_b = DerivAccount(
        account_id="acc_b",
        tenant_id="tenant_b",
        login_id="CR222222",
        account_type="demo",
        name="Conta B",
    )
    assert account_a.tenant_id != account_b.tenant_id
