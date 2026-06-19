"""Live data routes for dashboard charts — ticks and decisions."""

from __future__ import annotations

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from deriv_organismo.services.live_buffer import decision_buffer, outcome_buffer, tick_buffer

router = APIRouter(tags=['live'])


async def recent_ticks(symbol: str = Query('R_100', description='Filter by symbol')) -> JSONResponse:
    """Return the most recent 100 ticks from the in-memory buffer."""
    ticks = tick_buffer.recent(count=100, symbol=symbol)
    return JSONResponse({
        'count': len(ticks),
        'ticks': ticks,
        'latest_price': tick_buffer.latest_price(symbol=symbol),
        'symbol': symbol,
    })


async def recent_decisions() -> JSONResponse:
    """Return the most recent 20 trading decisions."""
    decisions = decision_buffer.recent(count=20)
    return JSONResponse({
        'count': len(decisions),
        'decisions': decisions,
    })


async def trade_history() -> JSONResponse:
    """Return the most recent 20 trade outcomes (win/loss)."""
    outcomes = outcome_buffer.recent(count=20)
    return JSONResponse({
        'count': len(outcomes),
        'outcomes': outcomes,
        'stats': outcome_buffer.stats(),
    })


async def trade_stats() -> JSONResponse:
    """Return aggregate trade statistics."""
    return JSONResponse(outcome_buffer.stats())
