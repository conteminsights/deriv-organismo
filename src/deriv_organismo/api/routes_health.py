from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/status")
async def status() -> dict[str, str]:
    return {"service": "deriv-organismo", "status": "running"}


async def worker_debug(request: Request) -> dict:
    """Debug endpoint to inspect market worker state."""
    worker = getattr(request.app.state, 'market_worker', None)
    if worker is None:
        return {"worker": "not_running"}

    exec_service = getattr(worker, 'execution_service', None)
    gateway = getattr(exec_service, 'trading_gateway', None) if exec_service else None

    return {
        "worker_running": worker._running,
        "cycle_count": worker.cycle_count,
        "subscribed": worker.summary.get('subscribed', 0),
        "symbols": worker.symbols,
        "trades": len(worker.trades),
        "decisions": len(worker.decisions),
        "gateway_has_client": gateway is not None and not getattr(gateway, '_stub_mode', True),
        "last_contract_id": gateway.last_contract_id if gateway else None,
        "last_proposal_id": gateway.last_proposal_id if gateway else None,
        "last_proposal": str(gateway._last_proposal)[:200] if gateway and gateway._last_proposal else None,
        "last_buy": str(gateway._last_buy)[:200] if gateway and gateway._last_buy else None,
    }
