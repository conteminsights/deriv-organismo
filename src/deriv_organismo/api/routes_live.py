"""Live data routes for dashboard charts — ticks and decisions."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from deriv_organismo.services.live_buffer import decision_buffer, tick_buffer

router = APIRouter(tags=['live'])


async def recent_ticks() -> JSONResponse:
    """Return the most recent 100 ticks from the in-memory buffer."""
    ticks = tick_buffer.recent(count=100)
    return JSONResponse({
        'count': len(ticks),
        'ticks': ticks,
        'latest_price': tick_buffer.latest_price(),
    })


async def recent_decisions() -> JSONResponse:
    """Return the most recent 20 trading decisions."""
    decisions = decision_buffer.recent(count=20)
    return JSONResponse({
        'count': len(decisions),
        'decisions': decisions,
    })
