from __future__ import annotations

from deriv_organismo.domain.signals import (
    SpecialistDecisionReason,
    SpecialistInput,
    SpecialistSignal,
)
from deriv_organismo.services.specialists.base import BaseSpecialist


class NoTradeSpecialist(BaseSpecialist):
    specialist_key = "no_trade"

    def evaluate(self, payload: SpecialistInput) -> SpecialistSignal:
        reason_code = {
            "high_noise": "high_noise_veto",
            "no_trade": "no_trade_veto",
        }.get(payload.regime_label, "regime_pass")

        should_trade = False
        reason_message = {
            "high_noise_veto": "Trading vetoed because market regime is high noise.",
            "no_trade_veto": "Trading vetoed because market regime is explicitly no_trade.",
            "regime_pass": "No-trade specialist did not detect a veto regime.",
        }[reason_code]

        return SpecialistSignal(
            specialist_key=self.specialist_key,
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            direction="flat",
            confidence=1.0 if reason_code != "regime_pass" else 0.0,
            should_trade=should_trade,
            reasons=[
                SpecialistDecisionReason(
                    code=reason_code,
                    message=reason_message,
                )
            ],
        )
