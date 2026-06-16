from fastapi.testclient import TestClient

from deriv_organismo.main import create_app


class FakeRealtimeDataService:
    async def build_operations_payload(self, tenant_id: str) -> dict:
        return {
            'tenant_id': tenant_id,
            'data_source': 'deriv_live',
            'refresh_seconds': 5,
            'generated_at': 'agora',
            'active_count': 1,
            'profitable_count': 1,
            'losing_count': 0,
            'monitored_accounts': 1,
            'account_summaries': [{'name': 'Conta Live', 'login_id': 'CR123456', 'mode_label': 'Conta demo', 'connection_status': 'online'}],
            'operations': [{'operation_id': 'op_live_1', 'tenant_id': tenant_id, 'account_name': 'Conta Live', 'login_id': 'CR123456', 'symbol': 'R_100', 'side': 'CALL', 'strategy': 'deriv_live', 'status': 'aberta', 'entry_price': 25.0, 'current_price': 31.0, 'stake': 25.0, 'pnl_float': 6.0, 'pnl_pct': 24.0, 'opened_at': 'live', 'risk_state': 'estável'}],
        }


def test_operations_route_prefers_live_realtime_service_when_present():
    app = create_app()
    app.state.realtime_data_service = FakeRealtimeDataService()
    client = TestClient(app)

    response = client.get('/operations/data')

    assert response.status_code == 200
    assert response.json()['data_source'] == 'deriv_live'
