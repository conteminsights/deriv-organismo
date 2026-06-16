from __future__ import annotations

from deriv_organismo.domain.accounts import AccountContext
from deriv_organismo.observability.events import build_event
from deriv_organismo.services.decision_pipeline import DecisionPipeline
from deriv_organismo.services.execution import ExecutionService


class MarketLoop:
    def __init__(
        self,
        decision_pipeline: DecisionPipeline | None = None,
        execution_service: ExecutionService | None = None,
    ) -> None:
        self.decision_pipeline = decision_pipeline or DecisionPipeline()
        self.execution_service = execution_service or ExecutionService()

    def run_cycle(
        self,
        *,
        symbol: str = "R_100",
        timeframe: str = "5m",
        account: AccountContext | None = None,
    ) -> dict:
        active_account = account or AccountContext(
            account_id="acc_primary",
            tenant_id="tenant_primary",
            account_slug="primary",
            mode="demo",
        )
        decision = self.decision_pipeline.run(
            symbol=symbol,
            timeframe=timeframe,
            account_id=active_account.account_id,
        )
        execution = None
        if decision.decision == "approved":
            execution = self.execution_service.execute_trade(
                account=active_account,
                symbol=symbol,
                amount=10,
                strategy_key=decision.selected_specialist_key,
            )

        event = build_event(
            account_id=active_account.account_id,
            event_type="trade_submitted" if execution else "signal_generated",
            payload={
                "symbol": symbol,
                "timeframe": timeframe,
                "decision": decision.decision,
            },
        )
        return {
            "decision": decision,
            "execution": execution,
            "event": event,
        }
