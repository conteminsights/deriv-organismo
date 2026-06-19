#!/usr/bin/env python
"""Run the continuous market loop with live Deriv data.

Usage:
    uv run python scripts/run_market_loop.py           # single symbol (R_100)
    uv run python scripts/run_market_loop.py --symbols R_100,R_75
    uv run python scripts/run_market_loop.py --candle 60 --cycles 5
"""

import argparse
import asyncio
import logging
import sys

from deriv_organismo.config import Settings
from deriv_organismo.db.session import build_engine, build_session_factory
from deriv_organismo.repositories.sql_account_repository import SqlAlchemyAccountRepository
from deriv_organismo.services.credential_manager import CredentialManager
from deriv_organismo.services.deriv_account_service import DerivAccountService
from deriv_organismo.services.deriv_token_validator import DerivTokenValidator
from deriv_organismo.workers.market_loop import (
    CANDLE_SECONDS,
    CYCLE_SLEEP,
    DEFAULT_SYMBOLS,
    ContinuousMarketWorker,
    AccountContext,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout,
)
logger = logging.getLogger('market_loop_script')


async def main():
    parser = argparse.ArgumentParser(description='Deriv Organismo — Continuous Market Loop')
    parser.add_argument('--symbols', type=str, default=','.join(DEFAULT_SYMBOLS),
                        help='Comma-separated symbols (default: R_100,R_75,R_50)')
    parser.add_argument('--candle', type=int, default=CANDLE_SECONDS,
                        help=f'Candle window in seconds (default: {CANDLE_SECONDS})')
    parser.add_argument('--sleep', type=int, default=CYCLE_SLEEP,
                        help=f'Sleep between cycles in seconds (default: {CYCLE_SLEEP})')
    parser.add_argument('--cycles', type=int, default=0,
                        help='Number of cycles to run (0 = infinite)')
    parser.add_argument('--amount', type=float, default=5.0,
                        help='Trade amount in USD (default: 5.0)')
    parser.add_argument('--account-id', type=str, default=None,
                        help='Account ID to use (default: first account from DB)')
    parser.add_argument('--no-trade', action='store_true',
                        help='Dry-run mode — no trades executed')
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(',') if s.strip()]

    # Load settings
    settings = Settings()
    if not settings.deriv_app_id:
        logger.error('DERIV_APP_ID not configured in .env')
        sys.exit(1)

    # Load account from DB
    logger.info('Connecting to database...')
    db_url = settings.database_url or 'sqlite+aiosqlite:///./deriv-organismo.db'
    engine = build_engine(db_url)
    factory = build_session_factory(engine)
    repository = SqlAlchemyAccountRepository(factory)
    credential_manager = CredentialManager(secret_key=settings.credential_secret_key)
    token_validator = DerivTokenValidator()
    account_service = DerivAccountService(repository, credential_manager, token_validator)

    accounts = await account_service.list_accounts_by_tenant('tenant_master')
    if not accounts:
        logger.error('No accounts found in database. Register an account first via POST /admin/accounts.')
        await engine.dispose()
        sys.exit(1)

    # Filter by account_id if specified
    target_account = accounts[0]
    if args.account_id:
        match = [a for a in accounts if a.account_id == args.account_id]
        if not match:
            logger.error(f'Account {args.account_id} not found')
            await engine.dispose()
            sys.exit(1)
        target_account = match[0]

    # Get plaintext token
    token = await account_service.get_plaintext_token('tenant_master', target_account.account_id)
    logger.info(f'Using account: {target_account.name} ({target_account.login_id}) [mode={target_account.account_type}]')

    # Build AccountContext for the worker
    account_ctx = AccountContext(
        account_id=target_account.account_id,
        tenant_id='tenant_master',
        account_slug=target_account.name.lower().replace(' ', '_'),
        mode=target_account.account_type,
        deriv_login_id=target_account.login_id,
    )

    # Create the worker
    worker = ContinuousMarketWorker(
        app_id=settings.deriv_app_id,
        token=token,
        account=account_ctx,
        symbols=symbols,
        candle_seconds=args.candle,
        cycle_sleep=args.sleep,
        base_ws_url=settings.deriv_api_base_ws,
    )

    # Start the worker
    logger.info(f'Starting market loop: {symbols} | candle={args.candle}s | cycle_sleep={args.sleep}s')
    if args.no_trade:
        logger.info('DRY-RUN mode: no trades will be executed')
    logger.info('Press Ctrl+C to stop')
    print('─' * 60)

    await worker.start()

    # Wait and report
    try:
        if args.cycles > 0:
            for _ in range(args.cycles):
                await asyncio.sleep(args.sleep)
                s = worker.summary
                print(f'  Cycle {s["cycle_count"]}: {s["subscribed"]}/{len(symbols)} streams | '
                      f'{s["total_decisions"]} decisions | {s["total_trades"]} trades')
        else:
            while True:
                await asyncio.sleep(10)
                s = worker.summary
                print(f'  [{s["cycle_count"]}] Streams: {s["subscribed"]}/{len(symbols)} | '
                      f'Decisions: {s["total_decisions"]} | Trades: {s["total_trades"]}')
    except KeyboardInterrupt:
        logger.info('Stopping market loop...')
    finally:
        await worker.stop()
        await engine.dispose()
        logger.info('Market loop stopped. Bye!')
        print('─' * 60)

        # Final summary
        s = worker.summary
        print(f'\nSummary:')
        print(f'  Cycles: {s["cycle_count"]}')
        print(f'  Decisions: {s["total_decisions"]}')
        print(f'  Trades: {s["total_trades"]}')
        if worker.decisions:
            last = worker.decisions[-1]
            print(f'  Last decision: {last["decision"]} ({last["specialist"]}) on {last["symbol"]}')
        if worker.trades:
            last_trade = worker.trades[-1]
            print(f'  Last trade: {last_trade["status"]} on {last_trade["symbol"]}')


if __name__ == '__main__':
    asyncio.run(main())
