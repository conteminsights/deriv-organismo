from deriv_organismo.services.specialists.base import SpecialistSignal


def test_specialist_signal_contains_risk_relevant_fields():
    signal = SpecialistSignal(
        specialist_key="trend_follow",
        symbol="R_100",
        timeframe="5m",
        direction="long",
        confidence=0.7,
        should_trade=True,
    )
    assert signal.should_trade is True
