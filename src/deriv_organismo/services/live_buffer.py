"""Simple in-memory ring buffer for real-time tick and decision data.

Shared between the web app and the market worker so the dashboard
can display live data without a database round-trip.
"""

from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from typing import Any

from deriv_organismo.services.lab import VariantLab


class TickBuffer:
    """Thread-safe-ish in-memory ring buffer for recent tick prices."""

    def __init__(self, maxlen: int = 500) -> None:
        self._ticks: deque[dict[str, Any]] = deque(maxlen=maxlen)

    def push(self, price: float, symbol: str, epoch: int | None = None) -> None:
        self._ticks.append({
            'price': price,
            'symbol': symbol,
            'epoch': epoch or int(datetime.now(timezone.utc).timestamp()),
            'ts': datetime.now(timezone.utc).isoformat(),
        })

    def recent(self, count: int = 100, symbol: str | None = None) -> list[dict[str, Any]]:
        items = list(self._ticks)
        if symbol:
            items = [t for t in items if t['symbol'] == symbol]
        return items[-count:]

    def latest_price(self, symbol: str | None = None) -> float | None:
        if not self._ticks:
            return None
        items = list(self._ticks)
        if symbol:
            items = [t for t in items if t['symbol'] == symbol]
        return items[-1]['price'] if items else None

    @property
    def count(self) -> int:
        return len(self._ticks)

    def clear(self) -> None:
        self._ticks.clear()


class DecisionBuffer:
    """In-memory buffer for recent trading decisions."""

    def __init__(self, maxlen: int = 200) -> None:
        self._decisions: deque[dict[str, Any]] = deque(maxlen=maxlen)

    def push(self, decision: dict[str, Any]) -> None:
        self._decisions.append(decision)

    def recent(self, count: int = 20) -> list[dict[str, Any]]:
        return list(self._decisions)[-count:]

    @property
    def count(self) -> int:
        return len(self._decisions)

    def last_decision(self) -> dict[str, Any] | None:
        return self._decisions[-1] if self._decisions else None

    def clear(self) -> None:
        self._decisions.clear()


class OutcomeBuffer:
    """In-memory buffer for trade outcomes (win/loss)."""

    def __init__(self, maxlen: int = 200) -> None:
        self._outcomes: deque[dict[str, Any]] = deque(maxlen=maxlen)

    def push(self, outcome: dict[str, Any]) -> None:
        self._outcomes.append(outcome)

    def recent(self, count: int = 20) -> list[dict[str, Any]]:
        return list(self._outcomes)[-count:]

    @property
    def count(self) -> int:
        return len(self._outcomes)

    def win_rate(self, specialist_key: str | None = None) -> float:
        """Calculate win rate, optionally filtered by specialist."""
        items = list(self._outcomes)
        if specialist_key:
            items = [o for o in items if o.get('specialist') == specialist_key]
        if not items:
            return 0.0
        wins = sum(1 for o in items if o.get('outcome') == 'won')
        return round(wins / len(items), 3)

    def total_stake(self) -> float:
        return sum(o.get('stake', 0) for o in self._outcomes)

    def total_profit(self) -> float:
        return sum(o.get('profit', 0) for o in self._outcomes)

    def stats(self) -> dict:
        total = self.count
        wins = sum(1 for o in self._outcomes if o.get('outcome') == 'won')
        losses = sum(1 for o in self._outcomes if o.get('outcome') == 'lost')
        return {
            'total': total,
            'wins': wins,
            'losses': losses,
            'win_rate': round(wins / total, 3) if total else 0.0,
            'total_stake': self.total_stake(),
            'total_profit': self.total_profit(),
        }


# Global singleton buffers
tick_buffer = TickBuffer()
decision_buffer = DecisionBuffer()
outcome_buffer = OutcomeBuffer()
variant_lab = VariantLab()
