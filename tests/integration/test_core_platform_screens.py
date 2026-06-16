from fastapi.testclient import TestClient

from deriv_organismo.main import create_app


client = TestClient(create_app())


def test_operations_page_exists_with_live_review_language():
    response = client.get('/operations')

    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert 'Operações em Tempo Real' in response.text
    assert '/operations/data' in response.text
    assert 'Atualização automática' in response.text


def test_operations_data_route_returns_json_contract():
    response = client.get('/operations/data')

    assert response.status_code == 200
    assert 'application/json' in response.headers['content-type']
    payload = response.json()
    assert 'operations' in payload
    assert 'account_summaries' in payload
    assert 'refresh_seconds' in payload
    assert isinstance(payload['operations'], list)


def test_performance_page_exists_with_account_metrics():
    response = client.get('/performance')

    assert response.status_code == 200
    assert 'text/html' in response.headers['content-type']
    assert 'Relatório de Performance' in response.text
    assert 'Saldo consolidado' in response.text
    assert '/performance/data' in response.text


def test_performance_data_route_returns_json_contract():
    response = client.get('/performance/data')

    assert response.status_code == 200
    assert 'application/json' in response.headers['content-type']
    payload = response.json()
    assert 'accounts' in payload
    assert 'portfolio' in payload
    assert 'daily_series' in payload
    assert isinstance(payload['accounts'], list)
