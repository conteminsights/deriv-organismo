from typing import Literal

from pydantic import BaseModel, Field


class SpecialistDecisionReason(BaseModel):
    code: str
    message: str


class SpecialistInput(BaseModel):
    symbol: str
    timeframe: str
    closes: list[float] = Field(default_factory=list)
    regime_label: str


class SpecialistSignal(BaseModel):
    specialist_key: str
    symbol: str
    timeframe: str
    direction: Literal["long", "short", "flat"]
    confidence: float
    should_trade: bool
    reasons: list[SpecialistDecisionReason] = Field(default_factory=list)
