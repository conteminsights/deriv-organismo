from deriv_organismo.services.context_scorer import ContextScorer


def test_context_scorer_weights_recent_and_long_term_performance():
    scorer = ContextScorer()

    score = scorer.score(
        recent_win_rate=0.70,
        long_term_win_rate=0.55,
        regime_match_score=0.80,
    )

    assert 0 <= score <= 1
