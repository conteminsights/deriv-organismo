from deriv_organismo.services.promotion import PromotionScorer


def test_promotion_scorer_blocks_candidate_without_sample_size():
    scorer = PromotionScorer()

    result = scorer.evaluate(
        trade_count=8,
        minimum_trade_count=30,
        net_return=0.12,
        drawdown=0.03,
        stability=0.70,
        regime_score=0.75,
    )

    assert result.eligible is False


def test_promotion_scorer_allows_candidate_with_enough_sample_and_quality():
    scorer = PromotionScorer()

    result = scorer.evaluate(
        trade_count=40,
        minimum_trade_count=30,
        net_return=0.15,
        drawdown=0.02,
        stability=0.82,
        regime_score=0.80,
    )

    assert result.eligible is True
