from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any

import websockets
from websockets.asyncio.client import ClientConnection

from deriv_organismo.integrations.deriv.messages import (
    build_authorize_request,
    build_forget_request,
    build_ticks_subscribe_request,
)

logger = logging.getLogger(__name__)


class TickStream:
    """Dedicated streaming connection to Deriv for real-time tick data.

    Manages its own WebSocket connection separate from the request/response
    client used for authorize/balance/portfolio calls.

    Usage:
        stream = TickStream(app_id='1089')
        await stream.connect()
        await stream.authorize('your_token')
        await stream.subscribe('R_100')

        async for tick_msg in stream.iter_ticks(timeout=60):
            price = TickStream.extract_price(tick_msg)
            # process tick...

        await stream.disconnect()
    """

    def __init__(self, app_id: str, base_ws_url: str = 'wss://ws.derivws.com/websockets/v3') -> None:
        self.app_id = app_id
        self.base_ws_url = base_ws_url
        self._connection: ClientConnection | None = None
        self._subscription_id: str | None = None
        self._symbol: str | None = None
        self._authorized = False
        self._running = False

    @property
    def websocket_url(self) -> str:
        return f'{self.base_ws_url}?app_id={self.app_id}'

    @property
    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.state.name == 'OPEN'

    @property
    def subscribed_symbol(self) -> str | None:
        return self._symbol

    async def connect(self) -> None:
        if self.is_connected:
            return
        self._connection = await websockets.connect(self.websocket_url)
        logger.info('tick_stream_connected')

    async def authorize(self, token: str) -> dict[str, Any]:
        """Authorize this streaming connection."""
        await self.connect()
        if self._connection is None:
            return {'error': 'not connected'}
        await self._connection.send(json.dumps(build_authorize_request(token)))
        raw = await asyncio.wait_for(self._connection.recv(), timeout=10)
        response = json.loads(raw)
        result = response.get('authorize', response)
        if isinstance(result, dict) and result.get('loginid'):
            self._authorized = True
            logger.info('tick_stream_authorized', extra={'loginid': result.get('loginid')})
        return result

    async def subscribe(self, symbol: str) -> str | None:
        """Subscribe to ticks for a given symbol.

        Returns the subscription_id if successful, None otherwise.
        """
        self._symbol = symbol
        await self.connect()
        if self._connection is None:
            return None
        await self._connection.send(json.dumps(build_ticks_subscribe_request(symbol)))

        # Read the subscription response
        raw = await asyncio.wait_for(self._connection.recv(), timeout=10)
        response = json.loads(raw)

        # The first message after subscribe is the subscription confirmation
        if response.get('msg_type') == 'tick':
            # First tick already arrived with subscription info
            tick = response.get('tick', {})
            self._subscription_id = tick.get('id')
            logger.info('tick_stream_subscribed', extra={'symbol': symbol, 'id': self._subscription_id})
            return self._subscription_id

        # It might be a different message type (subscribe confirmation)
        subscription = response.get('subscription', {})
        if isinstance(subscription, dict):
            self._subscription_id = subscription.get('id')
            if self._subscription_id:
                logger.info('tick_stream_subscribed', extra={'symbol': symbol, 'id': self._subscription_id})
                return self._subscription_id

        logger.warning('tick_stream_subscribe_unexpected', extra={'msg_type': response.get('msg_type')})
        return None

    async def unsubscribe(self) -> None:
        """Unsubscribe from the current tick stream."""
        if self._subscription_id and self.is_connected and self._connection is not None:
            await self._connection.send(json.dumps(build_forget_request(self._subscription_id)))
            # Read the forget response
            try:
                raw = await asyncio.wait_for(self._connection.recv(), timeout=5)
                if isinstance(raw, str):
                    response = json.loads(raw)
                    if response.get('msg_type') == 'forget':
                        logger.info('tick_stream_unsubscribed', extra={'id': self._subscription_id})
            except asyncio.TimeoutError:
                pass
        self._subscription_id = None
        self._symbol = None

    async def iter_ticks(self, timeout: float | None = None) -> AsyncIterator[dict[str, Any]]:
        """Async generator that yields tick messages from the stream.

        Yields each tick message as a dict. Stops when timeout expires
        or disconnect() is called.
        """
        self._running = True
        while self._running and self.is_connected and self._connection is not None:
            try:
                raw = await asyncio.wait_for(self._connection.recv(), timeout=timeout)
                message = json.loads(raw)
                msg_type = message.get('msg_type')
                if msg_type == 'tick':
                    yield message
                elif msg_type == 'error':
                    logger.error('tick_stream_error', extra={'error': message})
                    break
            except asyncio.TimeoutError:
                # No tick received within timeout — yield None so caller can tick
                yield {'_timeout': True, 'symbol': self._symbol}
            except websockets.ConnectionClosed:
                logger.warning('tick_stream_connection_closed')
                break

    async def disconnect(self) -> None:
        """Close the streaming connection."""
        self._running = False
        await self.unsubscribe()
        if self._connection is not None:
            try:
                await self._connection.close()
            except Exception:
                pass
            self._connection = None
            self._authorized = False
            logger.info('tick_stream_disconnected')

    async def read_tick(self, timeout: float = 0.01) -> dict[str, Any] | None:
        """Non-blocking read of one tick message.

        Returns the tick message dict, or None if no tick is available
        within the timeout.
        """
        if not self.is_connected or self._connection is None:
            return None
        try:
            raw = await asyncio.wait_for(self._connection.recv(), timeout=timeout)
            if isinstance(raw, str):
                message = json.loads(raw)
                if message.get('msg_type') == 'tick':
                    return message
            return None
        except asyncio.TimeoutError:
            return None
        except Exception:
            return None

    @staticmethod
    def extract_price(tick_message: dict[str, Any]) -> float | None:
        """Extract the quote (mid) price from a tick message."""
        tick = tick_message.get('tick')
        if not tick:
            return None
        return float(tick.get('quote', 0.0))

    @staticmethod
    def extract_epoch(tick_message: dict[str, Any]) -> int | None:
        """Extract the epoch timestamp from a tick message."""
        tick = tick_message.get('tick')
        if not tick:
            return None
        epoch = tick.get('epoch')
        return int(epoch) if epoch is not None else None
