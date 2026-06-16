from deriv_organismo.domain.signals import SpecialistInput
from deriv_organismo.services.specialists.mean_reversion import MeanReversionSpecialist


def test_mean_reversion_specialist_requires_range_regime():
    specialist = MeanReversionSpecialist()
    payload = SpecialistInput(
        symbol="R_75",
        timeframe="5m",
        closes=[100, 99.8, 100.1, 99.9, 100.0, 99.7, 99.6],
        regime_label="range",
    )

    signal = specialist.evaluate(payload)

    assert signal.specialist_key == "mean_reversion"


def test_mean_reversion_specialist_goes_long_when_price_is_far_below_mean_in_range():
    specialist = MeanReversionSpecialist(zscore_threshold=1.0, window=5)
    payload = SpecialistInput(
        symbol="R_75",
        timeframe="5m",
        closes=[100.0, 100.1, 100.0, 99.9, 99.0],
        regime_label="range",
    )

    signal = specialist.evaluate(payload)

    assert signal.should_trade is True
    assert signal.direction == "long"
    assert signal.specialist_key == "mean_reversion"
