from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/status")
async def status() -> dict[str, str]:
    return {"service": "deriv-organismo", "status": "running"}
