from __future__ import annotations

from typing import Literal

from deriv_organismo.domain.signals import (
    SpecialistDecisionReason,
    SpecialistInput,
    SpecialistSignal,
)
from deriv_organismo.services.specialists.base import BaseSpecialist


class BreakoutSpecialist(BaseSpecialist):
    specialist_key = "breakout"

    def __init__(self, lookback: int = 4, breakout_threshold: float = 0.002) -> None:
        self.lookback = lookback
        self.breakout_threshold = breakout_threshold

    def evaluate(self, payload: SpecialistInput) -> SpecialistSignal:
        closes = payload.closes
        if payload.regime_label != "breakout" or len(closes) < self.lookback + 1:
            return SpecialistSignal(
                specialist_key=self.specialist_key,
                symbol=payload.symbol,
                timeframe=payload.timeframe,
                direction="flat",
                confidence=0.0,
                should_trade=False,
                reasons=[
                    SpecialistDecisionReason(
                        code="regime_or_data_block",
                        message="Breakout specialist requires breakout regime and enough candles.",
                    )
                ],
            )

        confirmation_window = closes[-(self.lookback + 1) : -1]
        last_close = closes[-1]
        recent_high = max(confirmation_window)
        recent_low = min(confirmation_window)

        upward_expansion = recent_high > 0 and last_close > recent_high * (1 + self.breakout_threshold)
        downward_expansion = recent_low > 0 and last_close < recent_low * (1 - self.breakout_threshold)
        should_trade = upward_expansion or downward_expansion
        direction: Literal["long", "short"] = "long" if upward_expansion else "short"
        expansion_reference = recent_high if upward_expansion else recent_low
        expansion_ratio = abs(last_close - expansion_reference) / expansion_reference if expansion_reference else 0.0
        confidence = min(expansion_ratio / max(self.breakout_threshold, 1e-6), 1.0)

        return SpecialistSignal(
            specialist_key=self.specialist_key,
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            direction=direction if should_trade else "flat",
            confidence=confidence if should_trade else 0.0,
            should_trade=should_trade,
            reasons=[
                SpecialistDecisionReason(
                    code="breakout_confirmation",
                    message=(
                        f"last_close={last_close:.4f} recent_high={recent_high:.4f} "
                        f"recent_low={recent_low:.4f} threshold={self.breakout_threshold:.4f}"
                    ),
                )
            ],
        )
