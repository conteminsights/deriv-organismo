from deriv_organismo.domain.risk import RiskInput
from deriv_organismo.services.risk_engine import RiskEngine


def test_risk_engine_blocks_trade_when_account_hits_daily_loss_limit():
    engine = RiskEngine()

    result = engine.evaluate(
        RiskInput(
            account_id="acc_primary",
            symbol="R_100",
            daily_pnl=-101,
            daily_loss_limit=-100,
            recent_loss_streak=1,
            regime_label="trend",
            signal_confidence=0.8,
        )
    )

    assert result.allowed is False
