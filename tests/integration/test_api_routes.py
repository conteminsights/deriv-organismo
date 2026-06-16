from fastapi.testclient import TestClient

from deriv_organismo.main import create_app


client = TestClient(create_app())


def test_status_endpoint_exists():
    response = client.get("/status")

    assert response.status_code == 200


def test_operational_routes_exist():
    assert client.get("/health").status_code == 200
    assert client.get("/accounts").status_code == 200
    assert client.get("/symbols").status_code == 200
    assert client.get("/events").status_code == 200
    assert client.get("/decisions/latest").status_code == 200
