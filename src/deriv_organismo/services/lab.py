from __future__ import annotations

from pydantic import BaseModel, Field


class StrategyVariant(BaseModel):
    variant_key: str
    specialist_key: str
    parent_variant_key: str | None = None
    baseline_variant_key: str | None = None
    parameters: dict[str, float] = Field(default_factory=dict)
    quarantined: bool = True


class VariantLab:
    def clone_variant(
        self,
        *,
        specialist_key: str,
        parent_variant_key: str,
        parameter_adjustments: dict[str, float] | None = None,
    ) -> StrategyVariant:
        adjustments = parameter_adjustments or {}
        return StrategyVariant(
            variant_key=f"{parent_variant_key}_clone",
            specialist_key=specialist_key,
            parent_variant_key=parent_variant_key,
            baseline_variant_key=parent_variant_key,
            parameters=adjustments,
            quarantined=True,
        )
