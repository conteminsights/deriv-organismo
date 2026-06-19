from __future__ import annotations

from pydantic import BaseModel, Field

from deriv_organismo.domain.accounts import AccountContext
from deriv_organismo.integrations.deriv.trading import DerivTradingGateway


class RealExecutionBlocked(Exception):
    pass


class TradeRequest(BaseModel):
    account_id: str
    tenant_id: str
    account_slug: str
    mode: str
    symbol: str
    amount: float
    strategy_key: str = "trend_follow"


class ExecutionEvent(BaseModel):
    account_id: str
    event_type: str
    payload: dict = Field(default_factory=dict)


class ExecutionResult(BaseModel):
    status: str
    reason_code: str
    events: list[ExecutionEvent] = Field(default_factory=list)
    proposal_request: dict | None = None
    buy_request: dict | None = None


class ExecutionService:
    def __init__(
        self,
        trading_gateway: DerivTradingGateway | None = None,
        promoted_strategies: set[str] | None = None,
    ) -> None:
        self.trading_gateway = trading_gateway or DerivTradingGateway()
        self.promoted_strategies = promoted_strategies or set()
        self.events: list[ExecutionEvent] = []

    def build_trade_request(
        self,
        *,
        account: AccountContext,
        symbol: str,
        amount: float,
        strategy_key: str = "trend_follow",
    ) -> TradeRequest:
        return TradeRequest(
            account_id=account.account_id,
            tenant_id=account.tenant_id,
            account_slug=account.account_slug,
            mode=account.mode,
            symbol=symbol,
            amount=amount,
            strategy_key=strategy_key,
        )

    async def execute_trade(
        self,
        *,
        account: AccountContext,
        symbol: str,
        amount: float,
        strategy_key: str,
        requires_human_approval: bool = False,
        human_approval: bool = False,
    ) -> ExecutionResult:
        request = self.build_trade_request(
            account=account,
            symbol=symbol,
            amount=amount,
            strategy_key=strategy_key,
        )
        events = [
            self._record_event(
                account_id=request.account_id,
                event_type="trade_intent_recorded",
                payload={
                    "symbol": request.symbol,
                    "amount": request.amount,
                    "strategy_key": request.strategy_key,
                    "mode": request.mode,
                },
            )
        ]

        try:
            self.ensure_real_can_execute(
                is_promoted=request.strategy_key in self.promoted_strategies,
                account=account,
                requires_human_approval=requires_human_approval,
                human_approval=human_approval,
            )
        except RealExecutionBlocked as exc:
            events.append(
                self._record_event(
                    account_id=request.account_id,
                    event_type="trade_blocked",
                    payload={"reason_code": str(exc)},
                )
            )
            return ExecutionResult(
                status="blocked",
                reason_code=str(exc),
                events=events,
            )

        proposal_request = (
            self.trading_gateway.build_proposal_request(
                account=account,
                symbol=request.symbol,
                amount=request.amount,
            )
            if hasattr(self.trading_gateway, "build_proposal_request")
            else {
                "proposal": 1,
                "symbol": request.symbol,
                "amount": request.amount,
                "passthrough": {
                    "account_id": account.account_id,
                    "tenant_id": account.tenant_id,
                    "account_slug": account.account_slug,
                    "mode": account.mode,
                },
            }
        )
        proposal_response = await self.trading_gateway.request_proposal(proposal_request)
        proposal_id = proposal_response["proposal"]["id"]
        buy_request = (
            self.trading_gateway.build_buy_request(proposal_id=proposal_id, amount=request.amount)
            if hasattr(self.trading_gateway, "build_buy_request")
            else {"buy": proposal_id, "price": request.amount}
        )
        buy_response = await self.trading_gateway.submit_buy(buy_request)
        events.append(
            self._record_event(
                account_id=request.account_id,
                event_type="trade_submitted",
                payload={
                    "proposal_id": proposal_id,
                    "buy_response": buy_response,
                },
            )
        )
        return ExecutionResult(
            status="submitted",
            reason_code="submitted",
            events=events,
            proposal_request=proposal_request,
            buy_request=buy_request,
        )

    def ensure_real_can_execute(
        self,
        *,
        is_promoted: bool,
        account: AccountContext,
        requires_human_approval: bool = False,
        human_approval: bool = False,
    ) -> None:
        if account.mode != "real":
            return

        if not is_promoted:
            raise RealExecutionBlocked("real_mode_requires_promotion")

        if requires_human_approval and not human_approval:
            raise RealExecutionBlocked("real_mode_requires_human_approval")

    def _record_event(self, *, account_id: str, event_type: str, payload: dict) -> ExecutionEvent:
        event = ExecutionEvent(account_id=account_id, event_type=event_type, payload=payload)
        self.events.append(event)
        return event
