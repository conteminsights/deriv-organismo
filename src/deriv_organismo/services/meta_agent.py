from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SelectedSpecialist:
    specialist_key: str
    weight: float
    paused: bool = False


class MetaAgent:
    def __init__(self, paused_specialists: set[str] | None = None) -> None:
        self.paused_specialists = set(paused_specialists or set())
        self._regime_map: dict[str, list[tuple[str, float]]] = {
            "trend": [("trend_follow", 1.0), ("breakout", 0.6)],
            "range": [("mean_reversion", 1.0)],
            "breakout": [("breakout", 1.0), ("trend_follow", 0.5)],
            "high_noise": [("no_trade", 1.0)],
            "no_trade": [("no_trade", 1.0)],
        }

    def pause_specialist(self, specialist_key: str) -> None:
        self.paused_specialists.add(specialist_key)

    def reactivate_specialist(self, specialist_key: str) -> None:
        self.paused_specialists.discard(specialist_key)

    def select_specialists(self, regime_label: str, symbol: str) -> list[SelectedSpecialist]:
        del symbol
        configured = self._regime_map.get(regime_label, [("no_trade", 1.0)])
        selected: list[SelectedSpecialist] = []

        for specialist_key, weight in configured:
            if specialist_key in self.paused_specialists:
                continue
            selected.append(SelectedSpecialist(specialist_key=specialist_key, weight=weight))

        if selected:
            return selected

        return [SelectedSpecialist(specialist_key="no_trade", weight=1.0, paused=False)]
