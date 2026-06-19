from __future__ import annotations

import asyncio
from typing import Any


class DerivRealtimeGateway:
    """Gateway for real-time Deriv API calls via WebSocket.

    Manages per-account authorized sessions so each account gets its own
    WebSocket connection.
    """

    def __init__(self, client) -> None:
        self.client = client
        self._authorized_accounts: set[str] = set()
        self._lock = asyncio.Lock()

    async def fetch_authorize(self, token: str, login_id: str | None = None) -> dict[str, Any]:
        """Authorize with the given token and cache the auth state."""
        async with self._lock:
            response = await self.client.authorize(token)
            if isinstance(response, dict) and response.get('loginid'):
                self._authorized_accounts.add(token)
            return response

    async def fetch_portfolio(self, token: str, login_id: str | None = None) -> list[dict[str, Any]]:
        """Fetch open positions. Does NOT re-authorize — assumes already authorized."""
        return await self.client.portfolio()

    async def fetch_balance(self, token: str) -> float:
        """Return the current balance using the balance endpoint (no re-auth needed)."""
        response = await self.client.fetch_balance()
        return response

    @property
    def is_authorized(self) -> bool:
        return bool(self._authorized_accounts)

    async def disconnect(self) -> None:
        await self.client.close()
        self._authorized_accounts.clear()
