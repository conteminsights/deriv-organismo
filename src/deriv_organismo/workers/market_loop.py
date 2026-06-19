"""Continuous market worker — runs real-time trading cycles using live Deriv data."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from deriv_organismo.domain.accounts import AccountContext
from deriv_organismo.integrations.deriv.stream import TickStream
from deriv_organismo.services.candles import CandleFrameStore, RealTimeCandleBuilder
from deriv_organismo.services.decision_pipeline import DecisionPipeline
from deriv_organismo.services.execution import ExecutionService
from deriv_organismo.services.live_buffer import decision_buffer, outcome_buffer, tick_buffer

logger = logging.getLogger(__name__)

# Default symbols for demo trading
DEFAULT_SYMBOLS = ['R_100', 'R_75', 'R_50']
CANDLE_SECONDS = 60  # 1-minute candles
CYCLE_SLEEP = 5  # seconds between decision cycles


class ContinuousMarketWorker:
    """Async worker that streams real-time ticks, builds candles, runs decisions,
    and executes demo trades in a continuous loop.

    For each symbol:
        1. Subscribe to tick stream
        2. Aggregate ticks into 1-min candles
        3. Feed candles into decision pipeline
        4. If decision is 'approved', execute a demo trade
        5. Log results and continue
    """

    def __init__(
        self,
        app_id: str,
        token: str,
        account: AccountContext,
        symbols: list[str] | None = None,
        candle_seconds: int = CANDLE_SECONDS,
        cycle_sleep: int = CYCLE_SLEEP,
        base_ws_url: str = 'wss://ws.derivws.com/websockets/v3',
        decision_pipeline: DecisionPipeline | None = None,
        execution_service: ExecutionService | None = None,
        frame_store: CandleFrameStore | None = None,
    ) -> None:
        self.app_id = app_id
        self.token = token
        self.account = account
        self.symbols = symbols or DEFAULT_SYMBOLS
        self.candle_seconds = candle_seconds
        self.cycle_sleep = cycle_sleep
        self.base_ws_url = base_ws_url

        self.decision_pipeline = decision_pipeline or DecisionPipeline()
        self.execution_service = execution_service or ExecutionService()
        self.frame_store = frame_store or CandleFrameStore()

        # One tick stream per symbol
        self._streams: dict[str, TickStream] = {}
        self._builders: dict[str, RealTimeCandleBuilder] = {}

        self._running = False
        self._task: asyncio.Task | None = None

        # Cycle counters
        self.cycle_count = 0
        self.decisions: list[dict[str, Any]] = []
        self.trades: list[dict[str, Any]] = []

    async def start(self) -> None:
        """Start the continuous market loop in the background."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop())
        logger.info('market_worker_started', extra={
            'symbols': self.symbols,
            'account_id': self.account.account_id,
            'mode': self.account.mode,
        })

    async def stop(self) -> None:
        """Stop the market loop and disconnect all streams."""
        self._running = False
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

        # Disconnect all tick streams
        for symbol, stream in self._streams.items():
            await stream.disconnect()
        self._streams.clear()
        self._builders.clear()
        logger.info('market_worker_stopped')

    async def _run_loop(self) -> None:
        """Main loop: process each symbol in round-robin style."""
        # Subscribe to all symbols first
        for symbol in self.symbols:
            await self._ensure_stream(symbol)

        while self._running:
            self.cycle_count += 1
            logger.info('market_cycle_start', extra={'cycle': self.cycle_count})

            for symbol in self.symbols:
                try:
                    await self._process_symbol(symbol)
                except Exception as e:
                    logger.error('market_cycle_symbol_error', extra={
                        'symbol': symbol,
                        'error': str(e),
                    })

            # Summary
            total_ticks = sum(
                b.tick_count for b in self._builders.values()
            )
            logger.info('market_cycle_end', extra={
                'cycle': self.cycle_count,
                'total_ticks': total_ticks,
                'decisions_this_cycle': len(self.decisions),
            })

            await asyncio.sleep(self.cycle_sleep)

    async def _ensure_stream(self, symbol: str) -> TickStream:
        """Connect, authorize, and subscribe to a symbol's tick stream."""
        if symbol in self._streams and self._streams[symbol].is_connected:
            return self._streams[symbol]

        stream = TickStream(app_id=self.app_id, base_ws_url=self.base_ws_url)
        await stream.connect()
        await stream.authorize(self.token)
        sub_id = await stream.subscribe(symbol)

        if sub_id:
            self._streams[symbol] = stream
            self._builders[symbol] = RealTimeCandleBuilder(
                symbol=symbol,
                candle_seconds=self.candle_seconds,
            )
            logger.info('market_stream_subscribed', extra={'symbol': symbol, 'id': sub_id})
        else:
            logger.warning('market_stream_subscribe_failed', extra={'symbol': symbol})

        return stream

    async def _process_symbol(self, symbol: str) -> None:
        """Drain buffered ticks for a symbol, build candles, and run decisions."""
        stream = self._streams.get(symbol)
        builder = self._builders.get(symbol)

        if stream is None or builder is None:
            return

        # Drain available ticks without blocking
        for _ in range(50):  # max 50 ticks per cycle per symbol
            if not await self._read_one_tick(stream, builder, timeout=0.01):
                break

        # Check if we have completed candles
        while builder.tick_count > 0:
            candles = builder.force_close()
            if not candles:
                break

            for candle in candles:
                # Store in frame store
                self.frame_store.add_bar(
                    account_id=self.account.account_id,
                    symbol=symbol,
                    timeframe=f'{self.candle_seconds}s',
                    bar=candle,
                )

                # Run decision pipeline
                decision = self.decision_pipeline.run(
                    symbol=symbol,
                    timeframe=f'{self.candle_seconds}s',
                    account_id=self.account.account_id,
                )

                decision_record = {
                    'symbol': symbol,
                    'decision': decision.decision,
                    'regime': decision.regime_label,
                    'specialist': decision.selected_specialist_key,
                    'score': decision.contextual_score,
                    'risk_allowed': decision.risk_allowed,
                    'candle': candle,
                    'cycle': self.cycle_count,
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                }
                self.decisions.append(decision_record)
                decision_buffer.push(decision_record)
                logger.info('market_decision', extra=decision_record)

                # Execute if approved
                if decision.decision == 'approved' and self.account.mode == 'demo':
                    try:
                        result = await self.execution_service.execute_trade(
                            account=self.account,
                            symbol=symbol,
                            amount=1.0,  # small demo amount
                            strategy_key=decision.selected_specialist_key,
                        )
                        trade_record = {
                            'symbol': symbol,
                            'status': result.status,
                            'reason': result.reason_code,
                            'cycle': self.cycle_count,
                            'timestamp': datetime.now(timezone.utc).isoformat(),
                        }
                        self.trades.append(trade_record)
                        logger.info('market_trade_executed', extra=trade_record)

                        # Track outcome — poll contract settlement
                        gateway = getattr(self.execution_service, 'trading_gateway', None)
                        if gateway and hasattr(gateway, 'last_contract_id') and gateway.last_contract_id:
                            await self._track_outcome(
                                gateway=gateway,
                                contract_id=gateway.last_contract_id,
                                symbol=symbol,
                                specialist=decision.selected_specialist_key,
                                amount=1.0,
                            )
                    except Exception as e:
                        logger.error('market_trade_error', extra={
                            'symbol': symbol,
                            'error': str(e),
                        })

    async def _track_outcome(self, gateway, contract_id: int, symbol: str,
                              specialist: str, amount: float) -> None:
        """Poll contract settlement and record win/loss outcome."""
        for attempt in range(15):  # poll up to ~30s for tick contracts
            try:
                await asyncio.sleep(2)
                resp = await gateway.check_contract(contract_id)
                poc = resp.get('proposal_open_contract', {})
                status = poc.get('status', 'open')
                profit = float(poc.get('profit', 0))

                if status in ('won', 'lost'):
                    outcome_buffer.push({
                        'contract_id': contract_id,
                        'symbol': symbol,
                        'specialist': specialist,
                        'outcome': status,  # 'won' or 'lost'
                        'profit': profit,
                        'stake': amount,
                        'cycle': self.cycle_count,
                        'timestamp': datetime.now(timezone.utc).isoformat(),
                    })
                    logger.info('market_outcome', extra={
                        'contract_id': contract_id,
                        'symbol': symbol,
                        'outcome': status,
                        'profit': profit,
                    })
                    return
            except Exception:
                pass

        logger.warning('market_outcome_timeout', extra={'contract_id': contract_id})

    async def _read_one_tick(
        self,
        stream: TickStream,
        builder: RealTimeCandleBuilder,
        timeout: float = 0.01,
    ) -> bool:
        """Try to read one tick from the stream. Returns True if a tick was processed."""
        tick_msg = await stream.read_tick(timeout=timeout)
        if tick_msg is None:
            return False

        price = RealTimeCandleBuilder.extract_tick_price(tick_msg)
        epoch = RealTimeCandleBuilder.extract_tick_epoch(tick_msg)
        if price is not None:
            builder.add_tick(price, epoch)
            # Push to live buffer for dashboard
            tick_buffer.push(price, symbol=builder.symbol, epoch=epoch)
            return True
        return False

    @property
    def summary(self) -> dict[str, Any]:
        return {
            'running': self._running,
            'cycle_count': self.cycle_count,
            'symbols': list(self._streams.keys()),
            'subscribed': sum(1 for s in self._streams.values() if s.is_connected),
            'total_decisions': len(self.decisions),
            'total_trades': len(self.trades),
            'last_decision': self.decisions[-1] if self.decisions else None,
            'last_trade': self.trades[-1] if self.trades else None,
        }
