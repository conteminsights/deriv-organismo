"""Evolutionary lab — creates, evaluates, and evolves specialist variants.

Each variant is a specialist with custom parameters. Variants compete on win rate.
Top performers spawn mutated children; bottom performers are retired.
"""

from __future__ import annotations

import random
from typing import Any

from pydantic import BaseModel, Field

# Default parameter spaces for each specialist
PARAMETER_SPACES: dict[str, dict[str, tuple[float, float]]] = {
    "trend_follow": {
        "fast_window": (2, 8),
        "slow_window": (5, 20),
        "min_trend_strength": (0.0005, 0.005),
    },
    "mean_reversion": {
        "window": (3, 15),
        "zscore_threshold": (0.5, 3.0),
    },
    "breakout": {
        "lookback": (2, 10),
        "breakout_threshold": (0.001, 0.01),
    },
}

# Baseline (default) parameters for each specialist
BASELINE_PARAMETERS: dict[str, dict[str, float]] = {
    "trend_follow": {"fast_window": 3, "slow_window": 5, "min_trend_strength": 0.001},
    "mean_reversion": {"window": 5, "zscore_threshold": 1.0},
    "breakout": {"lookback": 4, "breakout_threshold": 0.002},
}


class StrategyVariant(BaseModel):
    """A variant of a specialist with specific parameter values."""

    variant_key: str
    specialist_key: str
    parent_variant_key: str | None = None
    parameters: dict[str, float] = Field(default_factory=dict)
    quarantined: bool = True  # Starts quarantined until proven
    generation: int = 0
    wins: int = 0
    losses: int = 0
    total_trades: int = 0

    @property
    def win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.0
        return round(self.wins / self.total_trades, 3)

    def record_outcome(self, outcome: str, profit: float) -> None:
        self.total_trades += 1
        if outcome == "won":
            self.wins += 1
        elif outcome == "lost":
            self.losses += 1
        # Un-quarantine after enough trades
        if self.total_trades >= 3 and self.quarantined:
            self.quarantined = False


class VariantLab:
    """Evolutionary lab that manages specialist variants.

    Creates baseline variants, spawns mutated children from top performers,
    and retires bottom performers.
    """

    def __init__(
        self,
        min_trades_for_evolution: int = 10,
        max_variants_per_specialist: int = 5,
        mutation_rate: float = 0.2,
        retention_ratio: float = 0.6,
    ) -> None:
        self.min_trades_for_evolution = min_trades_for_evolution
        self.max_variants_per_specialist = max_variants_per_specialist
        self.mutation_rate = mutation_rate
        self.retention_ratio = retention_ratio
        self._variants: dict[str, StrategyVariant] = {}
        self._evolution_count = 0
        self._setup_baselines()

    def _setup_baselines(self) -> None:
        """Create baseline variants for all specialists."""
        for specialist_key, params in BASELINE_PARAMETERS.items():
            vk = f"{specialist_key}_baseline"
            self._variants[vk] = StrategyVariant(
                variant_key=vk,
                specialist_key=specialist_key,
                parameters=dict(params),
                quarantined=False,  # baseline starts un-quarantined
                generation=0,
            )

    def get_or_create_variant(self, variant_key: str) -> StrategyVariant:
        """Get existing variant or create baseline on the fly."""
        if variant_key not in self._variants:
            # Try to infer specialist_key from variant_key
            for sk in BASELINE_PARAMETERS:
                if variant_key.startswith(sk):
                    self._variants[variant_key] = StrategyVariant(
                        variant_key=variant_key,
                        specialist_key=sk,
                        parameters=dict(BASELINE_PARAMETERS[sk]),
                        generation=0,
                    )
                    break
        return self._variants.get(variant_key, StrategyVariant(
            variant_key=variant_key, specialist_key="no_trade",
        ))

    def get_active_variants(
        self, specialist_keys: list[str] | None = None,
    ) -> list[StrategyVariant]:
        """Get all non-quarantined variants, optionally filtered by specialist."""
        result = [
            v for v in self._variants.values()
            if not v.quarantined
        ]
        if specialist_keys:
            result = [v for v in result if v.specialist_key in specialist_keys]
        return result

    def record_outcome(
        self, variant_key: str, outcome: str, profit: float,
    ) -> None:
        """Record a trade outcome for a variant."""
        variant = self.get_or_create_variant(variant_key)
        variant.record_outcome(outcome, profit)
        self._check_evolution()

    def _check_evolution(self) -> None:
        """Trigger evolution cycle if enough trades have accumulated."""
        total = sum(v.total_trades for v in self._variants.values())
        if total >= self.min_trades_for_evolution * (self._evolution_count + 1):
            self._evolve()

    def _evolve(self) -> None:
        """Run one evolution cycle: evaluate, select, mutate, retire."""
        self._evolution_count += 1

        for specialist_key in PARAMETER_SPACES:
            variants = [
                v for v in self._variants.values()
                if v.specialist_key == specialist_key and not v.quarantined
                and v.total_trades >= 2
            ]
            if len(variants) < 2:
                continue  # Need at least 2 to compare

            # Sort by win rate descending
            variants.sort(key=lambda v: v.win_rate, reverse=True)

            # Keep top N, retire bottom
            keep_count = max(1, int(len(variants) * self.retention_ratio))
            keep = variants[:keep_count]
            retire = variants[keep_count:]

            for v in retire:
                self._variants[v.variant_key].quarantined = True

            # Spawn new variants from top performers
            for parent in keep[:2]:  # Top 2 get to reproduce
                if len([v for v in self._variants.values()
                        if v.specialist_key == specialist_key
                        and not v.quarantined]) >= self.max_variants_per_specialist:
                    break

                child = self._mutate(parent)
                self._variants[child.variant_key] = child

    def _mutate(self, parent: StrategyVariant) -> StrategyVariant:
        """Create a mutated child from a parent variant."""
        child_params = dict(parent.parameters)
        space = PARAMETER_SPACES.get(parent.specialist_key, {})

        for param_name in child_params:
            if random.random() < self.mutation_rate:
                lo, hi = space.get(param_name, (0, 1))
                current = child_params[param_name]
                # Jitter: move by 10-30% in a random direction
                jitter = current * random.uniform(0.1, 0.3) * random.choice([-1, 1])
                child_params[param_name] = round(max(lo, min(hi, current + jitter)), 4)

        child_key = f"{parent.specialist_key}_gen{self._evolution_count}_{random.randint(100, 999)}"
        return StrategyVariant(
            variant_key=child_key,
            specialist_key=parent.specialist_key,
            parent_variant_key=parent.variant_key,
            parameters=child_params,
            quarantined=True,
            generation=self._evolution_count,
        )

    def get_specialist_instance(self, variant_key: str):
        """Create a specialist instance with the variant's parameters."""
        from deriv_organismo.services.specialists.trend_follow import TrendFollowSpecialist
        from deriv_organismo.services.specialists.mean_reversion import MeanReversionSpecialist
        from deriv_organismo.services.specialists.breakout import BreakoutSpecialist
        from deriv_organismo.services.specialists.no_trade import NoTradeSpecialist

        variant = self.get_or_create_variant(variant_key)
        mapping = {
            "trend_follow": TrendFollowSpecialist,
            "mean_reversion": MeanReversionSpecialist,
            "breakout": BreakoutSpecialist,
            "no_trade": NoTradeSpecialist,
        }
        cls = mapping.get(variant.specialist_key)
        if cls is None:
            return NoTradeSpecialist()
        return cls(**{k: int(v) if k.endswith("_window") or k == "lookback" or k == "window"
                      else v for k, v in variant.parameters.items()})

    def status(self) -> dict[str, Any]:
        """Return lab status for debugging/API."""
        active = self.get_active_variants()
        quarantined = [v for v in self._variants.values() if v.quarantined]
        by_specialist: dict[str, list[dict]] = {}
        for v in active:
            by_specialist.setdefault(v.specialist_key, []).append({
                "variant_key": v.variant_key,
                "gen": v.generation,
                "win_rate": v.win_rate,
                "trades": v.total_trades,
                "params": v.parameters,
                "quarantined": v.quarantined,
            })
        return {
            "evolution_cycles": self._evolution_count,
            "total_variants": len(self._variants),
            "active_variants": len(active),
            "quarantined_variants": len(quarantined),
            "by_specialist": by_specialist,
        }
