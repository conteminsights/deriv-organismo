from collections import defaultdict
from typing import TypedDict


class CandleBar(TypedDict):
    open: float
    high: float
    low: float
    close: float


class CandleAggregator:
    def rollup(self, candles: list[CandleBar]) -> CandleBar:
        if not candles:
            raise ValueError("candles cannot be empty")

        return {
            "open": candles[0]["open"],
            "high": max(candle["high"] for candle in candles),
            "low": min(candle["low"] for candle in candles),
            "close": candles[-1]["close"],
        }


class CandleFrameStore:
    def __init__(self) -> None:
        self._bars: dict[tuple[str, str, str], list[CandleBar]] = defaultdict(list)

    def add_bar(self, account_id: str, symbol: str, timeframe: str, bar: CandleBar) -> None:
        self._bars[(account_id, symbol, timeframe)].append(bar)

    def get_bars(self, account_id: str, symbol: str, timeframe: str) -> list[CandleBar]:
        return list(self._bars[(account_id, symbol, timeframe)])
