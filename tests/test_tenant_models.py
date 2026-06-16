"""Testes para modelos base do multi-tenant."""
import pytest
from datetime import datetime, timezone
from deriv_organismo.domain.tenant import Tenant, User, TenantUser


def test_tenant_creation():
    """Tenant pode ser criado com nome e metadata."""
    tenant = Tenant(
        tenant_id="tenant_master",
        name="Master Tenant",
        created_at=datetime.now(timezone.utc),
    )
    assert tenant.tenant_id == "tenant_master"
    assert tenant.name == "Master Tenant"
    assert tenant.is_active is True


def test_user_creation():
    """User pode ser criado com email e senha hash."""
    user = User(
        user_id="user_master",
        email="master@conteminsights.com",
        password_hash="hashed_password_here",
        is_superadmin=True,
    )
    assert user.user_id == "user_master"
    assert user.email == "master@conteminsights.com"
    assert user.is_superadmin is True


def test_tenant_user_association():
    """User pode ser associado a um tenant com role específico."""
    association = TenantUser(
        tenant_id="tenant_master",
        user_id="user_master",
        role="admin",
    )
    assert association.tenant_id == "tenant_master"
    assert association.user_id == "user_master"
    assert association.role == "admin"


def test_tenant_isolation():
    """Tenants diferentes não compartilham dados."""
    tenant_a = Tenant(tenant_id="tenant_a", name="Tenant A")
    tenant_b = Tenant(tenant_id="tenant_b", name="Tenant B")
    assert tenant_a.tenant_id != tenant_b.tenant_id
