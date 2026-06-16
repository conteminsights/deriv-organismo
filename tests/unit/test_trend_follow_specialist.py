from deriv_organismo.domain.signals import SpecialistInput
from deriv_organismo.services.specialists.trend_follow import TrendFollowSpecialist


def test_trend_follow_specialist_trades_when_fast_ma_is_above_slow_ma():
    specialist = TrendFollowSpecialist()
    payload = SpecialistInput(
        symbol="R_100",
        timeframe="5m",
        closes=[100, 101, 102, 103, 104, 105, 106],
        regime_label="trend",
    )
    signal = specialist.evaluate(payload)
    assert signal.specialist_key == "trend_follow"
