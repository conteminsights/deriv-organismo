from __future__ import annotations

from pydantic import BaseModel


class PromotionDecision(BaseModel):
    eligible: bool
    score: float
    reason_code: str


class PromotionScorer:
    def evaluate(
        self,
        *,
        trade_count: int,
        minimum_trade_count: int,
        net_return: float,
        drawdown: float,
        stability: float,
        regime_score: float,
    ) -> PromotionDecision:
        if trade_count < minimum_trade_count:
            return PromotionDecision(
                eligible=False,
                score=0.0,
                reason_code="insufficient_sample_size",
            )

        score = self._compose_score(
            net_return=net_return,
            drawdown=drawdown,
            stability=stability,
            regime_score=regime_score,
        )
        eligible = score >= 0.6
        return PromotionDecision(
            eligible=eligible,
            score=score,
            reason_code="eligible" if eligible else "score_below_threshold",
        )

    def _compose_score(
        self,
        *,
        net_return: float,
        drawdown: float,
        stability: float,
        regime_score: float,
    ) -> float:
        normalized_return = max(0.0, min(net_return, 0.30)) / 0.30
        drawdown_score = 1.0 - min(max(drawdown, 0.0), 0.20) / 0.20
        score = (
            normalized_return * 0.35
            + drawdown_score * 0.25
            + max(0.0, min(stability, 1.0)) * 0.20
            + max(0.0, min(regime_score, 1.0)) * 0.20
        )
        return round(score, 4)
