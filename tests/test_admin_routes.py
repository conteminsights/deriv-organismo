"""Testes para rotas admin de contas Deriv."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from deriv_organismo.main import create_app


@pytest.fixture
def client():
    """Fixture para client FastAPI."""
    return TestClient(create_app())


def test_admin_accounts_route_exists(client):
    """Rota /admin/accounts existe."""
    response = client.get("/admin/accounts")
    assert response.status_code == 200


def test_admin_accounts_returns_list(client):
    """Rota /admin/accounts retorna lista de contas."""
    response = client.get("/admin/accounts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_register_account_route_exists(client):
    """Rota POST /admin/accounts existe."""
    response = client.post(
        "/admin/accounts",
        json={
            "tenant_id": "tenant_master",
            "login_id": "CR123456",
            "token": "valid_token",
            "account_type": "demo",
            "name": "Conta Demo"
        }
    )
    # Status 201 ou 200 indica que a rota existe
    assert response.status_code in (200, 201)
