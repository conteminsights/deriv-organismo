from __future__ import annotations

from typing import Literal

from deriv_organismo.domain.signals import (
    SpecialistDecisionReason,
    SpecialistInput,
    SpecialistSignal,
)
from deriv_organismo.services.specialists.base import BaseSpecialist


class TrendFollowSpecialist(BaseSpecialist):
    specialist_key = "trend_follow"

    def __init__(
        self,
        fast_window: int = 3,
        slow_window: int = 5,
        min_trend_strength: float = 0.001,
    ) -> None:
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.min_trend_strength = min_trend_strength

    def evaluate(self, payload: SpecialistInput) -> SpecialistSignal:
        closes = payload.closes
        if payload.regime_label != "trend" or len(closes) < self.slow_window:
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
                        message="Trend specialist requires trend regime and enough candles.",
                    )
                ],
            )

        fast_ma = sum(closes[-self.fast_window :]) / self.fast_window
        slow_ma = sum(closes[-self.slow_window :]) / self.slow_window
        trend_strength = (fast_ma - slow_ma) / slow_ma if slow_ma else 0.0

        direction: Literal["long", "short"] = "long" if fast_ma > slow_ma else "short"
        should_trade = abs(trend_strength) >= self.min_trend_strength and fast_ma != slow_ma
        confidence = min(abs(trend_strength) * 100, 1.0)

        return SpecialistSignal(
            specialist_key=self.specialist_key,
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            direction=direction if should_trade else "flat",
            confidence=confidence,
            should_trade=should_trade,
            reasons=[
                SpecialistDecisionReason(
                    code="ma_alignment",
                    message=f"fast_ma={fast_ma:.4f} slow_ma={slow_ma:.4f} trend_strength={trend_strength:.4f}",
                )
            ],
        )
