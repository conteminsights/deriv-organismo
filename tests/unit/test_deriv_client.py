from deriv_organismo.domain.accounts import AccountContext
from deriv_organismo.integrations.deriv.client import DerivClient


def test_deriv_client_builds_account_aware_request_payload():
    account = AccountContext(
        account_id="acc_primary",
        tenant_id="tenant_primary",
        account_slug="primary",
        mode="demo",
    )
    client = DerivClient(app_id="1234")
    payload = client.build_ticks_history_request(account=account, symbol="R_100", count=10)
    assert payload["ticks_history"] == "R_100"
