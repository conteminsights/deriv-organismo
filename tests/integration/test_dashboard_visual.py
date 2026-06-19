from fastapi.testclient import TestClient

from deriv_organismo.main import create_app


def test_dashboard_returns_human_friendly_html():
    client = TestClient(create_app())

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Painel Operacional" in response.text
    assert "Saldo" in response.text
    assert "tickChart" in response.text
    assert "decisions-list" in response.text
