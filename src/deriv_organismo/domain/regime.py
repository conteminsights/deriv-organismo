from pydantic import BaseModel


class RegimeSnapshot(BaseModel):
    label: str
    trend_score: float
    volatility_score: float
    noise_score: float
