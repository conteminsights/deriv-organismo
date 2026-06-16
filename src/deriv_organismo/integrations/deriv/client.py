from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection

from deriv_organismo.domain.accounts import AccountContext
from deriv_organismo.integrations.deriv.messages import (
    build_active_symbols_request,
    build_ping_request,
    build_ticks_history_request,
    build_time_request,
)

logger = logging.getLogger(__name__)


class DerivClient:
    def __init__(self, app_id: str, base_ws_url: str = "wss://ws.derivws.com/websockets/v3") -> None:
        self.app_id = app_id
        self.base_ws_url = base_ws_url
        self._connection: ClientConnection | None = None

    def build_ping_request(self) -> dict[str, int]:
        return build_ping_request()

    def build_time_request(self) -> dict[str, int]:
        return build_time_request()

    def build_active_symbols_request(self, product_type: str = "basic") -> dict[str, str]:
        return build_active_symbols_request(product_type=product_type)

    def build_ticks_history_request(
        self,
        *,
        account: AccountContext,
        symbol: str,
        count: int,
        style: str = "candles",
        granularity: int = 300,
    ) -> dict[str, str | int]:
        payload = build_ticks_history_request(
            symbol=symbol,
            count=count,
            style=style,
            granularity=granularity,
        )
        logger.info(
            "deriv_request_built",
            extra={
                "account_id": account.account_id,
                "tenant_id": account.tenant_id,
                "account_slug": account.account_slug,
                "mode": account.mode,
                "request_type": "ticks_history",
                "symbol": symbol,
            },
        )
        return payload

    @property
    def websocket_url(self) -> str:
        return f"{self.base_ws_url}?app_id={self.app_id}"

    async def connect(self) -> ClientConnection:
        self._connection = await websockets.connect(self.websocket_url)
        return self._connection

    async def ensure_connection(self) -> ClientConnection:
        if self._connection is None or self._connection.state.name != "OPEN":
            return await self.connect()
        return self._connection

    async def send(self, payload: dict[str, Any]) -> None:
        connection = await self.ensure_connection()
        await connection.send(json.dumps(payload))
        logger.info("deriv_request_sent", extra={"request_keys": sorted(payload.keys())})

    async def recv(self) -> dict[str, Any]:
        connection = await self.ensure_connection()
        raw = await connection.recv()
        message = json.loads(raw)
        logger.info("deriv_response_received", extra={"response_keys": sorted(message.keys())})
        return message

    async def ping(self) -> None:
        await self.send(self.build_ping_request())

    async def heartbeat(self, interval_seconds: int = 30) -> None:
        while True:
            try:
                await self.ping()
            except Exception:
                logger.warning("deriv_ping_failed_reconnecting")
                await self.reconnect()
            await asyncio.sleep(interval_seconds)

    async def reconnect(self) -> ClientConnection:
        await self.close()
        return await self.connect()

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None
