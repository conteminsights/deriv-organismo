from fastapi.testclient import TestClient

from deriv_organismo.main import create_app


def test_dashboard_route_exists():
    client = TestClient(create_app())

    response = client.get("/dashboard")

    assert response.status_code == 200
