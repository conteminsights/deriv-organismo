"""Modelos base do multi-tenant."""
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class Tenant(BaseModel):
    """Tenant representa uma organização/cliente na plataforma."""
    tenant_id: str
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
    metadata: dict = Field(default_factory=dict)


class User(BaseModel):
    """User representa um usuário do sistema (pode pertencer a múltiplos tenants)."""
    user_id: str
    email: str
    password_hash: str
    is_superadmin: bool = False
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TenantUser(BaseModel):
    """Associação entre User e Tenant com role específico."""
    tenant_id: str
    user_id: str
    role: str  # "admin", "operator", "viewer"
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
