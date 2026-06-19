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
    build_authorize_request,
    build_balance_request,
    build_buy_request,
    build_ping_request,
    build_portfolio_request,
    build_proposal_open_contract_request,
    build_proposal_request,
    build_ticks_history_request,
    build_time_request,
)

logger = logging.getLogger(__name__)


class DerivClient:
    def __init__(self, app_id: str, base_ws_url: str = 'wss://ws.derivws.com/websockets/v3') -> None:
        self.app_id = app_id
        self.base_ws_url = base_ws_url
        self._connection: ClientConnection | None = None
        self._authorized_token: str | None = None
        self._authorized_response: dict[str, Any] | None = None
        self._heartbeat_task: asyncio.Task | None = None
        self._heartbeat_running = False

    def build_ping_request(self) -> dict[str, int]:
        return build_ping_request()

    def build_time_request(self) -> dict[str, int]:
        return build_time_request()

    def build_authorize_request(self, token: str) -> dict[str, str]:
        return build_authorize_request(token)

    def build_portfolio_request(self) -> dict[str, int]:
        return build_portfolio_request()

    def build_active_symbols_request(self, product_type: str = 'basic') -> dict[str, str]:
        return build_active_symbols_request(product_type=product_type)

    def build_ticks_history_request(
        self,
        *,
        account: AccountContext,
        symbol: str,
        count: int,
        style: str = 'candles',
        granularity: int = 300,
    ) -> dict[str, str | int]:
        payload = build_ticks_history_request(
            symbol=symbol,
            count=count,
            style=style,
            granularity=granularity,
        )
        logger.info(
            'deriv_request_built',
            extra={
                'account_id': account.account_id,
                'tenant_id': account.tenant_id,
                'account_slug': account.account_slug,
                'mode': account.mode,
                'request_type': 'ticks_history',
                'symbol': symbol,
            },
        )
        return payload

    @property
    def websocket_url(self) -> str:
        return f'{self.base_ws_url}?app_id={self.app_id}'

    @property
    def is_connected(self) -> bool:
        return self._connection is not None and self._connection.state.name == 'OPEN'

    @property
    def is_authorized(self) -> bool:
        return self._authorized_token is not None

    async def connect(self) -> ClientConnection:
        if self.is_connected and self._connection is not None:
            return self._connection
        self._connection = await websockets.connect(self.websocket_url)
        logger.info('deriv_ws_connected')
        return self._connection

    async def ensure_connection(self) -> ClientConnection:
        if not self.is_connected or self._connection is None:
            return await self.connect()
        return self._connection

    async def send(self, payload: dict[str, Any]) -> None:
        connection = await self.ensure_connection()
        await connection.send(json.dumps(payload))
        logger.info('deriv_request_sent', extra={'request_keys': sorted(payload.keys())})

    async def recv(self) -> dict[str, Any]:
        connection = await self.ensure_connection()
        raw = await connection.recv()
        message = json.loads(raw)
        logger.info('deriv_response_received', extra={'response_keys': sorted(message.keys())})
        return message

    async def request(self, payload: dict[str, Any]) -> dict[str, Any]:
        await self.send(payload)
        return await self.recv()

    async def authorize(self, token: str) -> dict[str, Any]:
        """Authorize and cache the token. Reconnects if already authorized with a different token.

        Returns the authorize response (which includes loginid, balance, etc.).
        If already authorized with the same token, returns the cached authorize response.
        """
        if self._authorized_token == token and self.is_connected and self._authorized_response is not None:
            return self._authorized_response

        if self._authorized_token is not None:
            # Already authorized with a different token — reconnect first
            await self.reconnect()

        response = await self.request(self.build_authorize_request(token))
        result = response.get('authorize', response)
        if isinstance(result, dict) and result.get('loginid'):
            self._authorized_token = token
            self._authorized_response = result
            logger.info('deriv_authorized', extra={'loginid': result.get('loginid')})
        return result

    async def portfolio(self) -> list[dict[str, Any]]:
        response = await self.request(self.build_portfolio_request())
        portfolio = response.get('portfolio', {})
        return portfolio.get('contracts', [])

    async def fetch_balance(self) -> float:
        """Fetch current balance from Deriv API. Requires authorized connection."""
        response = await self.request(build_balance_request())
        balance = response.get('balance', {})
        return float(balance.get('balance', 0.0))

    async def request_proposal(
        self,
        symbol: str,
        amount: float,
        contract_type: str = "CALL",
        duration: int = 5,
        duration_unit: str = "m",
        currency: str = "USD",
        basis: str = "stake",
    ) -> dict:
        """Request a trading proposal (quote) from Deriv."""
        payload = build_proposal_request(
            symbol=symbol, amount=amount, contract_type=contract_type,
            duration=duration, duration_unit=duration_unit,
            currency=currency, basis=basis,
        )
        response = await self.request(payload)
        return response

    async def buy_contract(self, proposal_id: str, price: float) -> dict:
        """Buy a contract at the proposed price."""
        response = await self.request(build_buy_request(proposal_id, price))
        return response

    async def check_contract(self, contract_id: int) -> dict:
        """Check the status/outcome of a contract."""
        response = await self.request(build_proposal_open_contract_request(contract_id))
        return response

    async def ping(self) -> None:
        if self.is_connected:
            await self.send(self.build_ping_request())

    async def _send_and_drain_ping(self) -> None:
        """Send a ping and immediately read the response to keep the buffer clean."""
        await self.send(self.build_ping_request())
        try:
            # Read the ping response to keep the buffer clean
            response = await asyncio.wait_for(self.recv(), timeout=5)
            if response.get('msg_type') != 'ping':
                logger.warning('heartbeat_got_unexpected_message', extra={'msg_type': response.get('msg_type')})
        except asyncio.TimeoutError:
            logger.warning('heartbeat_ping_timeout')
        except Exception:
            logger.warning('heartbeat_ping_read_failed')

    async def start_heartbeat(self, interval_seconds: int = 30) -> None:
        """Start a background heartbeat loop to keep the connection alive."""
        if self._heartbeat_running:
            return
        self._heartbeat_running = True

        async def _heartbeat_loop():
            # Wait a few seconds before first ping to let startup complete
            await asyncio.sleep(5)
            while self._heartbeat_running:
                try:
                    await self._send_and_drain_ping()
                    logger.debug('deriv_heartbeat_ping')
                except Exception:
                    logger.warning('deriv_heartbeat_failed_reconnecting')
                    await self.reconnect()
                await asyncio.sleep(interval_seconds)

        self._heartbeat_task = asyncio.create_task(_heartbeat_loop())
        logger.info('deriv_heartbeat_started')

    async def stop_heartbeat(self) -> None:
        self._heartbeat_running = False
        if self._heartbeat_task is not None:
            self._heartbeat_task.cancel()
            try:
                await self._heartbeat_task
            except asyncio.CancelledError:
                pass
            self._heartbeat_task = None

    async def reconnect(self) -> ClientConnection:
        await self.close()
        conn = await self.connect()
        self._authorized_token = None
        self._authorized_response = None
        return conn

    async def close(self) -> None:
        await self.stop_heartbeat()
        if self._connection is not None:
            try:
                await self._connection.close()
            except Exception:
                pass
            self._connection = None
            self._authorized_token = None
            self._authorized_response = None
            logger.info('deriv_ws_disconnected')
