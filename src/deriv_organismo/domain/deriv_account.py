"""Modelos de contas Deriv e credenciais."""
from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, Field


class DerivAccount(BaseModel):
    """Conta Deriv associada a um tenant."""
    account_id: str
    tenant_id: str
    login_id: str
    account_type: Literal["demo", "real"]
    name: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict = Field(default_factory=dict)


class DerivCredential(BaseModel):
    """Credencial Deriv (token) criptografada e associada a uma conta."""
    account_id: str
    tenant_id: str
    encrypted_token: str
    token_type: str = "api_token"
    is_valid: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_validated_at: datetime | None = None
