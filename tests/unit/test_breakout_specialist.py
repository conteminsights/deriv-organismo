from deriv_organismo.domain.signals import SpecialistInput
from deriv_organismo.services.specialists.breakout import BreakoutSpecialist


def test_breakout_specialist_only_triggers_on_expansion_confirmation():
    specialist = BreakoutSpecialist(lookback=4, breakout_threshold=0.002)
    payload = SpecialistInput(
        symbol="R_100",
        timeframe="5m",
        closes=[100.0, 100.1, 100.2, 100.25, 100.8],
        regime_label="breakout",
    )

    signal = specialist.evaluate(payload)

    assert signal.specialist_key == "breakout"
    assert signal.should_trade is True
    assert signal.direction == "long"
