from __future__ import annotations

from pydantic import BaseModel


class RiskInput(BaseModel):
    account_id: str
    symbol: str
    daily_pnl: float
    daily_loss_limit: float
    recent_loss_streak: int
    regime_label: str
    signal_confidence: float
    proposed_risk: float = 0.0
    max_risk_per_trade: float = 0.02
    max_loss_streak: int = 3
    cooldown_active: bool = False
    specialist_paused: bool = False
    variant_quarantined: bool = False


class RiskDecision(BaseModel):
    allowed: bool
    reason_code: str
    message: str
