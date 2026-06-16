from __future__ import annotations

from deriv_organismo.domain.risk import RiskDecision, RiskInput


class RiskEngine:
    def evaluate(self, payload: RiskInput) -> RiskDecision:
        if payload.proposed_risk > payload.max_risk_per_trade:
            return RiskDecision(
                allowed=False,
                reason_code="max_risk_per_trade_block",
                message="Proposed trade risk exceeds maximum risk per trade.",
            )

        if payload.daily_pnl <= payload.daily_loss_limit:
            return RiskDecision(
                allowed=False,
                reason_code="daily_loss_limit_block",
                message="Account hit the daily loss limit.",
            )

        if payload.recent_loss_streak >= payload.max_loss_streak:
            return RiskDecision(
                allowed=False,
                reason_code="loss_streak_block",
                message="Recent loss streak reached the configured maximum.",
            )

        if payload.regime_label in {"high_noise", "no_trade"}:
            return RiskDecision(
                allowed=False,
                reason_code="regime_block",
                message="Current regime is blocked for trading.",
            )

        if payload.cooldown_active:
            return RiskDecision(
                allowed=False,
                reason_code="cooldown_block",
                message="Cooldown is active for this account or symbol.",
            )

        if payload.specialist_paused:
            return RiskDecision(
                allowed=False,
                reason_code="specialist_paused_block",
                message="Selected specialist is paused.",
            )

        if payload.variant_quarantined:
            return RiskDecision(
                allowed=False,
                reason_code="variant_quarantine_block",
                message="Selected strategy variant is quarantined.",
            )

        return RiskDecision(
            allowed=True,
            reason_code="allowed",
            message="Risk checks passed.",
        )
