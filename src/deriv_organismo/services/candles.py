from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, TypedDict


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


class RealTimeCandleBuilder:
    """Aggregates real-time ticks from Deriv into CandleBar objects.

    Ticks arrive at ~1-4 per second for volatility indices.
    This builder accumulates ticks over a time window and produces a CandleBar.
    """

    def __init__(self, symbol: str, candle_seconds: int = 60) -> None:
        self.symbol = symbol
        self.candle_seconds = candle_seconds
        self._ticks: list[float] = []
        self._candle_start: float | None = None

    def add_tick(self, tick_price: float, epoch: int | None = None) -> list[CandleBar] | None:
        """Add a tick from the Deriv stream.

        Returns a completed CandleBar if the candle window has elapsed,
        otherwise None.
        """
        now = epoch if epoch is not None else int(datetime.now(timezone.utc).timestamp())

        if self._candle_start is None:
            self._candle_start = now

        elapsed = now - self._candle_start
        self._ticks.append(tick_price)

        if elapsed >= self.candle_seconds:
            return self._close_candle()

        return None

    def _close_candle(self) -> list[CandleBar]:
        if not self._ticks:
            return []

        bar: CandleBar = {
            "open": self._ticks[0],
            "high": max(self._ticks),
            "low": min(self._ticks),
            "close": self._ticks[-1],
        }

        # Reset for next candle
        self._ticks = []
        self._candle_start = None

        return [bar]

    def force_close(self) -> list[CandleBar]:
        """Force-close the current candle (e.g., on shutdown)."""
        return self._close_candle()

    @property
    def tick_count(self) -> int:
        return len(self._ticks)

    @property
    def current_price(self) -> float | None:
        return self._ticks[-1] if self._ticks else None

    @staticmethod
    def extract_tick_price(tick_message: dict[str, Any]) -> float | None:
        """Extract the mid/quote price from a Deriv tick WebSocket message."""
        tick = tick_message.get("tick")
        if not tick:
            return None
        return float(tick.get("quote", 0.0))

    @staticmethod
    def extract_tick_epoch(tick_message: dict[str, Any]) -> int | None:
        """Extract the epoch from a Deriv tick message."""
        tick = tick_message.get("tick")
        if not tick:
            return None
        epoch = tick.get("epoch")
        return int(epoch) if epoch is not None else None
