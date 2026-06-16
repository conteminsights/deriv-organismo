from deriv_organismo.db.models import TradeDecision


def test_trade_decision_model_has_account_id():
    columns = TradeDecision.__table__.columns.keys()
    assert "account_id" in columns
