from fastapi import APIRouter

router = APIRouter()


@router.get("/dashboard")
async def dashboard() -> dict:
    return {
        "app_status": "running",
        "accounts": [
            {
                "account_id": "acc_primary",
                "account_slug": "primary",
                "mode": "demo",
            }
        ],
        "last_decisions": [
            {
                "decision": "observe",
                "symbol": "R_100",
                "specialist_key": "trend_follow",
            }
        ],
        "last_risk_blocks": [],
        "last_promotions": [],
    }
