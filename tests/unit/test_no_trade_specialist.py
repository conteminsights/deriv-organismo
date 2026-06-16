from deriv_organismo.domain.signals import SpecialistInput
from deriv_organismo.services.specialists.no_trade import NoTradeSpecialist


def test_no_trade_specialist_vetoes_high_noise_regime():
    specialist = NoTradeSpecialist()
    payload = SpecialistInput(
        symbol="R_50",
        timeframe="5m",
        closes=[100.0, 100.4, 99.7, 100.3, 99.8],
        regime_label="high_noise",
    )

    signal = specialist.evaluate(payload)

    assert signal.specialist_key == "no_trade"
    assert signal.should_trade is False
    assert signal.reasons[0].code == "high_noise_veto"


def test_no_trade_specialist_vetoes_no_trade_regime():
    specialist = NoTradeSpecialist()
    payload = SpecialistInput(
        symbol="R_50",
        timeframe="5m",
        closes=[100.0, 100.0, 100.0, 100.0, 100.0],
        regime_label="no_trade",
    )

    signal = specialist.evaluate(payload)

    assert signal.specialist_key == "no_trade"
    assert signal.should_trade is False
    assert signal.reasons[0].code == "no_trade_veto"
