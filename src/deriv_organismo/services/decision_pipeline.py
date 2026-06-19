from __future__ import annotations

from pydantic import BaseModel

from deriv_organismo.domain.risk import RiskInput
from deriv_organismo.domain.signals import SpecialistInput, SpecialistSignal
from deriv_organismo.services.candles import CandleBar, CandleFrameStore
from deriv_organismo.services.context_scorer import ContextScorer
from deriv_organismo.services.live_buffer import outcome_buffer as _global_outcome_buffer
from deriv_organismo.services.live_buffer import variant_lab as _global_variant_lab
from deriv_organismo.services.meta_agent import MetaAgent
from deriv_organismo.services.regime_detector import RegimeDetector
from deriv_organismo.services.risk_engine import RiskEngine
from deriv_organismo.services.specialists.breakout import BreakoutSpecialist
from deriv_organismo.services.specialists.mean_reversion import MeanReversionSpecialist
from deriv_organismo.services.specialists.no_trade import NoTradeSpecialist
from deriv_organismo.services.specialists.trend_follow import TrendFollowSpecialist


class DecisionArtifact(BaseModel):
    decision: str
    regime_label: str
    selected_specialist_key: str
    selected_variant_key: str = "baseline"
    contextual_score: float
    risk_allowed: bool


class DecisionPipeline:
    def __init__(
        self,
        frame_store: CandleFrameStore | None = None,
        regime_detector: RegimeDetector | None = None,
        meta_agent: MetaAgent | None = None,
        context_scorer: ContextScorer | None = None,
        risk_engine: RiskEngine | None = None,
    ) -> None:
        self.frame_store = frame_store or CandleFrameStore()
        self.regime_detector = regime_detector or RegimeDetector()
        self.meta_agent = meta_agent or MetaAgent(
            outcome_buffer=_global_outcome_buffer,
        )
        self.context_scorer = context_scorer or ContextScorer()
        self.risk_engine = risk_engine or RiskEngine()
        self.specialists = {
            "trend_follow": TrendFollowSpecialist(),
            "mean_reversion": MeanReversionSpecialist(),
            "breakout": BreakoutSpecialist(),
            "no_trade": NoTradeSpecialist(),
        }

    def run(self, symbol: str, timeframe: str, account_id: str = "acc_primary") -> DecisionArtifact:
        bars = self._load_market_frame(account_id=account_id, symbol=symbol, timeframe=timeframe)
        closes = [bar["close"] for bar in bars]
        atr_values = self._build_atr_values(bars)
        regime = self.regime_detector.classify(closes=closes, atr_values=atr_values)
        selected = self.meta_agent.select_specialists(regime_label=regime.label, symbol=symbol)
        signals = self._evaluate_specialists_via_lab(
            selected=selected, symbol=symbol, timeframe=timeframe, closes=closes,
            regime_label=regime.label,
        )

        if not signals:
            return DecisionArtifact(
                decision="observe", regime_label=regime.label,
                selected_specialist_key="no_trade",
                contextual_score=0.0, risk_allowed=True,
            )

        # Prefer variants with higher win rate, else higher confidence
        top = max(signals, key=lambda s: (
            _global_variant_lab.get_or_create_variant(s['variant_key']).win_rate,
            s['signal'].confidence,
        ))
        top_signal = top['signal']
        top_variant_key = top['variant_key']

        contextual_score = self.context_scorer.score(
            recent_win_rate=_global_variant_lab.get_or_create_variant(top_variant_key).win_rate,
            long_term_win_rate=0.55,
            regime_match_score=1.0 if top_signal.should_trade else 0.4,
        )
        risk = self.risk_engine.evaluate(
            RiskInput(
                account_id=account_id,
                symbol=symbol,
                daily_pnl=0.0,
                daily_loss_limit=-100.0,
                recent_loss_streak=0,
                regime_label=regime.label,
                signal_confidence=top_signal.confidence,
                proposed_risk=0.01,
            )
        )

        if not risk.allowed:
            decision = "blocked"
        elif top_signal.should_trade and contextual_score >= 0.6:
            decision = "approved"
        else:
            decision = "observe"

        return DecisionArtifact(
            decision=decision,
            regime_label=regime.label,
            selected_specialist_key=top_signal.specialist_key,
            selected_variant_key=top_variant_key,
            contextual_score=contextual_score,
            risk_allowed=risk.allowed,
        )

    def _load_market_frame(self, account_id: str, symbol: str, timeframe: str) -> list[CandleBar]:
        bars = self.frame_store.get_bars(account_id=account_id, symbol=symbol, timeframe=timeframe)
        if bars:
            return bars

        return [
            {"open": 100.0, "high": 100.3, "low": 99.9, "close": 100.2},
            {"open": 100.2, "high": 100.5, "low": 100.1, "close": 100.4},
            {"open": 100.4, "high": 100.7, "low": 100.3, "close": 100.6},
            {"open": 100.6, "high": 100.9, "low": 100.5, "close": 100.8},
            {"open": 100.8, "high": 101.1, "low": 100.7, "close": 101.0},
        ]

    def _build_atr_values(self, bars: list[CandleBar]) -> list[float]:
        return [bar["high"] - bar["low"] for bar in bars]

    def _evaluate_specialists_via_lab(
        self,
        selected: list,
        symbol: str,
        timeframe: str,
        closes: list[float],
        regime_label: str,
    ) -> list[dict]:
        """Evaluate all active lab variants for the selected specialists.

        Returns list of {'variant_key': str, 'signal': SpecialistSignal}.
        """
        results = []
        for sel in selected:
            sk = sel.specialist_key
            active = _global_variant_lab.get_active_variants(specialist_keys=[sk])
            if not active:
                # Fallback to baseline
                active = [_global_variant_lab.get_or_create_variant(f"{sk}_baseline")]

            for variant in active:
                specialist = _global_variant_lab.get_specialist_instance(variant.variant_key)
                payload = SpecialistInput(
                    symbol=symbol, timeframe=timeframe, closes=closes,
                    regime_label=regime_label,
                )
                signal = specialist.evaluate(payload)
                results.append({'variant_key': variant.variant_key, 'signal': signal})

        return results
