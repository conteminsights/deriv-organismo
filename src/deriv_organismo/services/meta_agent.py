"""Meta-agent — selects specialists based on market regime and historical performance."""

from __future__ import annotations

from dataclasses import dataclass

# Minimum trades before we consider a specialist's win rate for pausing
MIN_WIN_RATE_SAMPLES = 3
# Win rate below this pauses the specialist
PAUSE_WIN_RATE_THRESHOLD = 0.40
# Win rate above this reactivates a paused specialist
REACTIVATE_WIN_RATE_THRESHOLD = 0.50


@dataclass(frozen=True)
class SelectedSpecialist:
    specialist_key: str
    weight: float
    paused: bool = False


class MetaAgent:
    """Selects specialists using the regime map, plus real-time win rate feedback.

    If a specialist's win rate drops below the threshold, it is auto-paused.
    Paused specialists are reactivated when their win rate recovers.
    """

    def __init__(
        self,
        paused_specialists: set[str] | None = None,
        outcome_buffer=None,
    ) -> None:
        self.paused_specialists = set(paused_specialists or set())
        self._outcome_buffer = outcome_buffer  # Optional feedback source
        self._auto_paused: set[str] = set()    # Track which were paused by the system

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
        self._apply_feedback()  # Auto-pause/reactivate based on win rates

        configured = self._regime_map.get(regime_label, [("no_trade", 1.0)])
        selected: list[SelectedSpecialist] = []

        for specialist_key, weight in configured:
            if specialist_key in self.paused_specialists:
                continue
            selected.append(SelectedSpecialist(specialist_key=specialist_key, weight=weight))

        if selected:
            return selected

        return [SelectedSpecialist(specialist_key="no_trade", weight=1.0, paused=False)]

    def _apply_feedback(self) -> None:
        """Evaluate specialist win rates and auto-pause/reactivate."""
        if self._outcome_buffer is None:
            return

        for specialist_key in self._regime_specialists():
            wr = self._outcome_buffer.win_rate(specialist_key=specialist_key)
            total = sum(
                1 for o in self._outcome_buffer._outcomes
                if o.get('specialist') == specialist_key
            )

            if total < MIN_WIN_RATE_SAMPLES:
                continue  # Not enough data to judge

            if wr < PAUSE_WIN_RATE_THRESHOLD and specialist_key not in self.paused_specialists:
                self.paused_specialists.add(specialist_key)
                self._auto_paused.add(specialist_key)

            elif wr >= REACTIVATE_WIN_RATE_THRESHOLD and specialist_key in self._auto_paused:
                self.paused_specialists.discard(specialist_key)
                self._auto_paused.discard(specialist_key)

    def _regime_specialists(self) -> set[str]:
        """Return the set of all specialists referenced in the regime map."""
        result: set[str] = set()
        for candidates in self._regime_map.values():
            for key, _ in candidates:
                result.add(key)
        return result

    @property
    def feedback_stats(self) -> dict:
        """Return feedback state for debugging."""
        stats = {}
        for key in self._regime_specialists():
            if self._outcome_buffer:
                stats[key] = {
                    'win_rate': self._outcome_buffer.win_rate(specialist_key=key),
                    'paused': key in self.paused_specialists,
                    'auto_paused': key in self._auto_paused,
                }
        return stats
