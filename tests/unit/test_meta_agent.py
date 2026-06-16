from deriv_organismo.services.meta_agent import MetaAgent


def test_meta_agent_prefers_trend_specialist_in_trend_regime():
    agent = MetaAgent()

    selected = agent.select_specialists(regime_label="trend", symbol="R_100")

    assert "trend_follow" in [item.specialist_key for item in selected]
