import pytest

from deriv_organismo.domain.deriv_account import DerivAccount
from deriv_organismo.services.deriv_realtime_data import DerivRealtimeDataService


class FakeAccountService:
    async def list_accounts_by_tenant(self, tenant_id: str):
        return [
            DerivAccount(
                account_id='acc_live_1',
                tenant_id=tenant_id,
                login_id='CR123456',
                account_type='demo',
                name='Conta Live',
            )
        ]

    async def get_plaintext_token(self, tenant_id: str, account_id: str) -> str:
        return 'token-live-1'


class FakeDerivGateway:
    async def fetch_authorize(self, token: str, login_id: str | None = None) -> dict:
        return {
            'loginid': login_id or 'CR123456',
            'balance': 1500.5,
            'is_virtual': 1,
            'currency': 'USD',
        }

    async def fetch_portfolio(self, token: str, login_id: str | None = None) -> list[dict]:
        return [
            {
                'contract_id': 9001,
                'symbol': 'R_100',
                'contract_type': 'CALL',
                'buy_price': 25.0,
                'current_spot': 128.9,
                'payout': 31.0,
            }
        ]

    async def fetch_balance(self, token: str) -> float:
        return 1500.5


@pytest.mark.asyncio
async def test_realtime_data_service_builds_live_operations_payload():
    service = DerivRealtimeDataService(FakeAccountService(), FakeDerivGateway())

    payload = await service.build_operations_payload('tenant_master')

    assert payload['data_source'] == 'deriv_live'
    assert payload['active_count'] == 1
    assert payload['operations'][0]['symbol'] == 'R_100'
    assert payload['account_summaries'][0]['connection_status'] == 'online'
