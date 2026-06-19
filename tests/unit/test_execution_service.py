import pytest

from deriv_organismo.domain.accounts import AccountContext
from deriv_organismo.services.execution import ExecutionService


class StubTradingGateway:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    async def request_proposal(self, payload: dict) -> dict:
        self.calls.append(("proposal", payload))
        return {"proposal": {"id": "proposal_demo_1"}}

    async def submit_buy(self, payload: dict) -> dict:
        self.calls.append(("buy", payload))
        return {"buy": {"contract_id": "contract_demo_1", "status": "open"}}


def build_account(mode: str = "demo") -> AccountContext:
    return AccountContext(
        account_id="acc_primary",
        tenant_id="tenant_primary",
        account_slug="primary",
        mode=mode,
    )


def test_execution_service_requires_account_context_for_trade_submission():
    service = ExecutionService()

    payload = service.build_trade_request(account=build_account(), symbol="R_100", amount=10)

    assert payload.account_id == "acc_primary"


@pytest.mark.asyncio
async def test_execution_service_requests_proposal_and_buy_for_demo_account():
    gateway = StubTradingGateway()
    service = ExecutionService(trading_gateway=gateway)

    result = await service.execute_trade(
        account=build_account(mode="demo"),
        symbol="R_100",
        amount=10,
        strategy_key="trend_follow",
    )

    assert result.status == "submitted"
    assert [name for name, _ in gateway.calls] == ["proposal", "buy"]
    assert result.events[0].event_type == "trade_intent_recorded"
    assert result.events[-1].event_type == "trade_submitted"


@pytest.mark.asyncio
async def test_execution_service_blocks_real_trade_when_strategy_is_not_promoted():
    gateway = StubTradingGateway()
    service = ExecutionService(trading_gateway=gateway, promoted_strategies={"mean_reversion"})

    result = await service.execute_trade(
        account=build_account(mode="real"),
        symbol="R_100",
        amount=10,
        strategy_key="trend_follow",
    )

    assert result.status == "blocked"
    assert result.reason_code == "real_mode_requires_promotion"
    assert gateway.calls == []
    assert result.events[-1].event_type == "trade_blocked"
