from __future__ import annotations

from abc import ABC, abstractmethod

from deriv_organismo.domain.signals import (
    SpecialistDecisionReason,
    SpecialistInput,
    SpecialistSignal,
)


class BaseSpecialist(ABC):
    specialist_key: str

    @abstractmethod
    def evaluate(self, payload: SpecialistInput) -> SpecialistSignal:
        raise NotImplementedError


__all__ = [
    "BaseSpecialist",
    "SpecialistDecisionReason",
    "SpecialistInput",
    "SpecialistSignal",
]
