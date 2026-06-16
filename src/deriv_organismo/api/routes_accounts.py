from fastapi import APIRouter

router = APIRouter()


@router.get("/accounts")
async def list_accounts() -> list[dict[str, str]]:
    return [
        {
            "account_id": "acc_primary",
            "tenant_id": "tenant_primary",
            "account_slug": "primary",
            "mode": "demo",
        }
    ]


@router.get("/symbols")
async def list_symbols() -> list[dict[str, str]]:
    return [
        {"symbol": "R_100", "market": "synthetic"},
        {"symbol": "R_75", "market": "synthetic"},
    ]
