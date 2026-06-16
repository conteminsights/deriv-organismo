from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryKey:
    account_id: str
    symbol: str
    specialist_key: str
    variant_key: str
    regime_label: str


class StrategyMemory:
    def __init__(self) -> None:
        self._store: dict[MemoryKey, dict[str, float]] = {}

    def remember(self, key: MemoryKey, metrics: dict[str, float]) -> None:
        self._store[key] = dict(metrics)

    def recall(self, key: MemoryKey) -> dict[str, float] | None:
        stored = self._store.get(key)
        return dict(stored) if stored is not None else None
