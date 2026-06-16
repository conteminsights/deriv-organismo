from __future__ import annotations

from deriv_organismo.domain.regime import RegimeSnapshot


class RegimeDetector:
    def classify(self, closes: list[float], atr_values: list[float]) -> RegimeSnapshot:
        if not closes or not atr_values:
            return RegimeSnapshot(
                label="no_trade",
                trend_score=0.0,
                volatility_score=0.0,
                noise_score=1.0,
            )

        trend_score = self._trend_score(closes)
        volatility_score = sum(atr_values) / len(atr_values)
        noise_score = self._noise_score(closes)

        if noise_score >= 0.6:
            label = "high_noise"
        elif volatility_score >= 2.0:
            label = "high_vol"
        elif trend_score >= 0.7:
            label = "trend"
        else:
            label = "range"

        return RegimeSnapshot(
            label=label,
            trend_score=trend_score,
            volatility_score=volatility_score,
            noise_score=noise_score,
        )

    def _trend_score(self, closes: list[float]) -> float:
        if len(closes) < 2:
            return 0.0

        moves = [curr - prev for prev, curr in zip(closes, closes[1:])]
        directional_consistency = sum(1 for move in moves if move > 0 or move < 0) / len(moves)
        aligned_direction = max(
            sum(1 for move in moves if move > 0),
            sum(1 for move in moves if move < 0),
        ) / len(moves)
        return round((directional_consistency + aligned_direction) / 2, 4)

    def _noise_score(self, closes: list[float]) -> float:
        if len(closes) < 3:
            return 0.0

        moves = [curr - prev for prev, curr in zip(closes, closes[1:])]
        direction_flips = sum(
            1
            for prev, curr in zip(moves, moves[1:])
            if (prev > 0 > curr) or (prev < 0 < curr)
        )
        return round(direction_flips / max(len(moves) - 1, 1), 4)
