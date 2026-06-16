from deriv_organismo.services.regime_detector import RegimeDetector


def test_regime_detector_returns_trend_or_range_labels():
    detector = RegimeDetector()
    regime = detector.classify(
        closes=[100, 101, 102, 103, 104, 105],
        atr_values=[1.0, 1.1, 1.2, 1.2, 1.3, 1.4],
    )
    assert regime.label in {"trend", "range", "high_vol", "high_noise", "no_trade"}
