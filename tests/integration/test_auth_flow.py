from fastapi.testclient import TestClient

from deriv_organismo.config import Settings
from deriv_organismo.main import create_app


def make_auth_client() -> TestClient:
    settings = Settings(
        app_env='dev',
        auth_enabled=True,
        master_email='master@conteminsights.com',
        master_password='master-secret',
        tenant_email='tenant@conteminsights.com',
        tenant_password='tenant-secret',
        tenant_scope_id='tenant_demo',
    )
    return TestClient(create_app(settings=settings))


def test_protected_route_redirects_to_login_when_auth_enabled():
    client = make_auth_client()

    response = client.get('/admin/accounts', follow_redirects=False)

    assert response.status_code == 307
    assert response.headers['location'].startswith('/login')


def test_master_login_allows_access_to_admin_and_requested_tenant():
    client = make_auth_client()

    login = client.post(
        '/login',
        json={'email': 'master@conteminsights.com', 'password': 'master-secret'},
    )
    assert login.status_code == 200

    response = client.get('/admin/accounts/data?tenant_id=tenant_master')

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_tenant_login_is_scoped_to_own_tenant():
    client = make_auth_client()

    login = client.post(
        '/login',
        json={'email': 'tenant@conteminsights.com', 'password': 'tenant-secret'},
    )
    assert login.status_code == 200

    response = client.get('/admin/accounts/data?tenant_id=tenant_other')

    assert response.status_code == 200
    rows = response.json()
    assert isinstance(rows, list)
    assert all(item['tenant_id'] == 'tenant_demo' for item in rows)
