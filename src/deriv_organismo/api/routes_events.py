from fastapi import APIRouter

router = APIRouter()


@router.get("/events")
async def list_events() -> list[dict]:
    return [
        {
            "account_id": "acc_primary",
            "event_type": "trade_submitted",
            "payload": {"symbol": "R_100"},
        }
    ]


@router.get("/decisions/latest")
async def latest_decision() -> dict:
    return {
        "decision": "observe",
        "regime_label": "trend",
        "selected_specialist_key": "trend_follow",
        "contextual_score": 0.6,
        "risk_allowed": True,
    }
