from deriv_organismo.observability.events import build_event


def test_event_builder_requires_account_and_event_type():
    event = build_event(account_id="acc_primary", event_type="risk_blocked", payload={})

    assert event["account_id"] == "acc_primary"
    assert event["event_type"] == "risk_blocked"


def test_event_builder_supports_required_audit_event_types():
    supported_types = [
        "regime_detected",
        "specialist_selected",
        "signal_generated",
        "risk_blocked",
        "trade_submitted",
        "trade_result",
        "variant_created",
        "promotion_decision",
    ]

    events = [build_event(account_id="acc_primary", event_type=event_type, payload={}) for event_type in supported_types]

    assert [event["event_type"] for event in events] == supported_types
