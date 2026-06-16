from __future__ import annotations

from statistics import fmean, pstdev
from typing import Literal

from deriv_organismo.domain.signals import (
    SpecialistDecisionReason,
    SpecialistInput,
    SpecialistSignal,
)
from deriv_organismo.services.specialists.base import BaseSpecialist


class MeanReversionSpecialist(BaseSpecialist):
    specialist_key = "mean_reversion"

    def __init__(self, window: int = 5, zscore_threshold: float = 1.0) -> None:
        self.window = window
        self.zscore_threshold = zscore_threshold

    def evaluate(self, payload: SpecialistInput) -> SpecialistSignal:
        closes = payload.closes
        if payload.regime_label != "range" or len(closes) < self.window:
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
                        message="Mean reversion specialist requires range regime and enough candles.",
                    )
                ],
            )

        window_closes = closes[-self.window :]
        mean_price = fmean(window_closes)
        std_dev = pstdev(window_closes)

        if std_dev == 0:
            return SpecialistSignal(
                specialist_key=self.specialist_key,
                symbol=payload.symbol,
                timeframe=payload.timeframe,
                direction="flat",
                confidence=0.0,
                should_trade=False,
                reasons=[
                    SpecialistDecisionReason(
                        code="zero_volatility",
                        message="Mean reversion specialist requires price dispersion to compute z-score.",
                    )
                ],
            )

        last_close = window_closes[-1]
        zscore = (last_close - mean_price) / std_dev
        should_trade = abs(zscore) >= self.zscore_threshold
        direction: Literal["long", "short"] = "long" if zscore < 0 else "short"
        confidence = min(abs(zscore) / max(self.zscore_threshold, 1e-6), 1.0)

        return SpecialistSignal(
            specialist_key=self.specialist_key,
            symbol=payload.symbol,
            timeframe=payload.timeframe,
            direction=direction if should_trade else "flat",
            confidence=confidence if should_trade else 0.0,
            should_trade=should_trade,
            reasons=[
                SpecialistDecisionReason(
                    code="zscore_reversion",
                    message=(
                        f"last_close={last_close:.4f} mean={mean_price:.4f} "
                        f"std={std_dev:.4f} zscore={zscore:.4f}"
                    ),
                )
            ],
        )
