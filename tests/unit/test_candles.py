from deriv_organismo.services.candles import CandleAggregator


def test_candle_aggregator_rolls_one_minute_candles_into_five_minute_bar():
    aggregator = CandleAggregator()
    candles = [
        {"open": 100, "high": 101, "low": 99, "close": 100.5},
        {"open": 100.5, "high": 102, "low": 100, "close": 101},
        {"open": 101, "high": 103, "low": 100.8, "close": 102},
        {"open": 102, "high": 102.5, "low": 101.2, "close": 101.8},
        {"open": 101.8, "high": 104, "low": 101.5, "close": 103},
    ]
    bar = aggregator.rollup(candles)
    assert bar["open"] == 100
    assert bar["close"] == 103
    assert bar["high"] == 104
    assert bar["low"] == 99
