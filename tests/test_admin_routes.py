"""Testes para rotas admin de contas Deriv."""
import pytest
from fastapi.testclient import TestClient

from deriv_organismo.main import create_app


@pytest.fixture
def client():
    return TestClient(create_app())


def test_admin_accounts_route_exists(client):
    response = client.get('/admin/accounts')
    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']


def test_admin_accounts_data_returns_list(client):
    response = client.get('/admin/accounts/data')
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_register_account_route_exists(client):
    response = client.post(
        '/admin/accounts',
        json={
            'tenant_id': 'tenant_master',
            'login_id': 'CR123456',
            'token': 'valid_token',
            'account_type': 'demo',
            'name': 'Conta Demo',
        },
    )
    assert response.status_code in (200, 201)
