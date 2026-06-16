from pathlib import Path

from fastapi.testclient import TestClient

from deriv_organismo.main import create_app


def test_register_account_persists_and_appears_in_followup_list(tmp_path: Path):
    db_path = tmp_path / 'admin-flow.db'
    app = create_app(database_url=f'sqlite+aiosqlite:///{db_path}')

    with TestClient(app) as client:
        created = client.post(
            '/admin/accounts',
            json={
                'tenant_id': 'tenant_master',
                'login_id': 'CR123456',
                'token': 'valid_token',
                'account_type': 'demo',
                'name': 'Conta Persistida',
            },
        )
        assert created.status_code == 201

        listed = client.get('/admin/accounts/data', params={'tenant_id': 'tenant_master'})
        assert listed.status_code == 200
        data = listed.json()
        assert any(item['name'] == 'Conta Persistida' for item in data)
