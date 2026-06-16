from fastapi.testclient import TestClient

from deriv_organismo.main import create_app


client = TestClient(create_app())


def test_dashboard_uses_ferrari_static_css():
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "/static/css/ferrari-dark.css" in response.text
    assert "Painel Operacional" in response.text
    assert "Contêm Insights · Deriv Organismo" in response.text


def test_admin_accounts_page_is_human_friendly_html():
    response = client.get("/admin/accounts")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Administração de Contas" in response.text
    assert "Cadastrar nova conta Deriv" in response.text
    assert "tenant_id" in response.text


def test_admin_accounts_data_route_returns_json():
    response = client.get("/admin/accounts/data")

    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert isinstance(response.json(), list)


def test_login_page_exists():
    response = client.get("/login")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Acesso à Plataforma" in response.text
    assert "Ferrari" in response.text or "ferrari" in response.text.lower()
