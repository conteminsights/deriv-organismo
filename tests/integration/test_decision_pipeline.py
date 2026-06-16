from deriv_organismo.services.decision_pipeline import DecisionPipeline


def test_decision_pipeline_returns_blocked_or_approved_trade_decision():
    pipeline = DecisionPipeline()

    result = pipeline.run(symbol="R_100", timeframe="5m")

    assert result.decision in {"approved", "blocked", "observe"}
