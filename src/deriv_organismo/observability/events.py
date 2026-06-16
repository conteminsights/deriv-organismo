from __future__ import annotations

from datetime import UTC, datetime

SUPPORTED_EVENT_TYPES = {
    "regime_detected",
    "specialist_selected",
    "signal_generated",
    "risk_blocked",
    "trade_submitted",
    "trade_result",
    "variant_created",
    "promotion_decision",
}


def build_event(*, account_id: str, event_type: str, payload: dict) -> dict:
    if event_type not in SUPPORTED_EVENT_TYPES:
        raise ValueError(f"unsupported event_type: {event_type}")

    return {
        "account_id": account_id,
        "event_type": event_type,
        "payload": payload,
        "created_at": datetime.now(UTC).isoformat(),
    }
