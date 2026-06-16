from __future__ import annotations


class ContextScorer:
    def __init__(
        self,
        recent_weight: float = 0.5,
        long_term_weight: float = 0.3,
        regime_weight: float = 0.2,
    ) -> None:
        self.recent_weight = recent_weight
        self.long_term_weight = long_term_weight
        self.regime_weight = regime_weight

    def score(
        self,
        recent_win_rate: float,
        long_term_win_rate: float,
        regime_match_score: float,
    ) -> float:
        weighted_score = (
            recent_win_rate * self.recent_weight
            + long_term_win_rate * self.long_term_weight
            + regime_match_score * self.regime_weight
        )
        return min(max(weighted_score, 0.0), 1.0)
