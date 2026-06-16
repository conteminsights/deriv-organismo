from __future__ import annotations

from typing import Any


class DerivRealtimeGateway:
    def __init__(self, client) -> None:
        self.client = client

    async def fetch_authorize(self, token: str) -> dict[str, Any]:
        return await self.client.authorize(token)

    async def fetch_portfolio(self, token: str) -> list[dict[str, Any]]:
        await self.client.authorize(token)
        return await self.client.portfolio()
