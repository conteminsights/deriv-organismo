import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from deriv_organismo.api.routes_accounts import list_accounts, list_symbols
from deriv_organismo.api.routes_admin import router as admin_router
from deriv_organismo.api.routes_auth import login, login_page, logout
from deriv_organismo.api.routes_dashboard import dashboard, dashboard_data
from deriv_organismo.api.routes_events import latest_decision, list_events
from deriv_organismo.api.routes_live import recent_decisions, recent_ticks
from deriv_organismo.api.routes_health import health, status
from deriv_organismo.api.routes_operations import operations_data, operations_page
from deriv_organismo.api.routes_performance import performance_data, performance_page
from deriv_organismo.config import DEFAULT_DEV_DATABASE_URL, Settings
from deriv_organismo.db.session import build_engine, build_session_factory, create_all_tables
from deriv_organismo.repositories.sql_account_repository import SqlAlchemyAccountRepository
from deriv_organismo.services.auth_service import AuthService
from deriv_organismo.services.credential_manager import CredentialManager
from deriv_organismo.services.deriv_account_service import DerivAccountService
from deriv_organismo.services.deriv_gateway import DerivRealtimeGateway
from deriv_organismo.services.deriv_realtime_data import DerivRealtimeDataService
from deriv_organismo.services.deriv_token_validator import DerivTokenValidator
from deriv_organismo.integrations.deriv.client import DerivClient
from deriv_organismo.integrations.deriv.trading import DerivTradingGateway
from deriv_organismo.services.live_buffer import tick_buffer, decision_buffer
from deriv_organismo.services.execution import ExecutionService
from deriv_organismo.workers.market_loop import ContinuousMarketWorker

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
DEFAULT_DATABASE_URL = DEFAULT_DEV_DATABASE_URL


def resolve_database_url(settings: Settings) -> str:
    database_url = settings.database_url
    if database_url is None:
        raise ValueError('DATABASE_URL could not be resolved from settings')
    return database_url


def build_auth_service(settings: Settings) -> AuthService:
    return AuthService(
        enabled=settings.auth_enabled,
        master_email=settings.master_email,
        master_password=settings.master_password,
        tenant_email=settings.tenant_email,
        tenant_password=settings.tenant_password,
        tenant_scope_id=settings.tenant_scope_id,
    )


def build_account_service(database_url: str, settings: Settings) -> tuple:
    engine = build_engine(database_url)
    session_factory = build_session_factory(engine)
    repository = SqlAlchemyAccountRepository(session_factory)
    credential_manager = CredentialManager(secret_key=settings.credential_secret_key)
    token_validator = DerivTokenValidator()
    service = DerivAccountService(repository, credential_manager, token_validator)
    return engine, service


def build_realtime_data_service(settings: Settings, account_service: DerivAccountService):
    if not settings.deriv_app_id:
        return None
    client = DerivClient(app_id=settings.deriv_app_id, base_ws_url=settings.deriv_api_base_ws)
    gateway = DerivRealtimeGateway(client)
    return DerivRealtimeDataService(account_service, gateway)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await create_all_tables(app.state.account_engine)

    # Start persistent WebSocket connection to Deriv
    realtime_service = getattr(app.state, 'realtime_data_service', None)
    market_worker = None
    if realtime_service is not None:
        gateway = realtime_service.gateway
        client = gateway.client
        try:
            # Connect and authorize the primary account
            accounts = await app.state.account_service.list_accounts_by_tenant('tenant_master')
            if accounts:
                account = accounts[0]
                token = await app.state.account_service.get_plaintext_token(
                    'tenant_master', account.account_id
                )
                await gateway.fetch_authorize(token, account.login_id)
                # Start heartbeat to keep connection alive
                await client.start_heartbeat(interval_seconds=30)

                # Start background market worker (same process = shared buffers)
                from deriv_organismo.domain.accounts import AccountContext
                account_ctx = AccountContext(
                    account_id=account.account_id,
                    tenant_id='tenant_master',
                    account_slug=account.name.lower().replace(' ', '_'),
                    mode=account.account_type,
                    deriv_login_id=account.login_id,
                )
                # Real trading gateway via persistent WebSocket
                trading_gateway = DerivTradingGateway(client)
                real_execution = ExecutionService(trading_gateway=trading_gateway)
                market_worker = ContinuousMarketWorker(
                    app_id=app.state.settings.deriv_app_id,
                    token=token,
                    account=account_ctx,
                    symbols=['R_100', 'R_75'],
                    candle_seconds=60,
                    cycle_sleep=15,
                    execution_service=real_execution,
                )
                await market_worker.start()
                app.state.market_worker = market_worker
        except Exception as exc:
            pass  # Non-critical; requests will create connections on demand

    try:
        yield
    finally:
        # Stop market worker
        if market_worker is not None:
            await market_worker.stop()
        # Cleanup WebSocket
        if realtime_service is not None:
            await realtime_service.gateway.disconnect()
        await app.state.account_engine.dispose()


def create_app(
    database_url: str | None = None,
    settings: Settings | None = None,
    *,
    run_migrations_on_create: bool = True,
) -> FastAPI:
    resolved_settings = settings or Settings()
    resolved_database_url = database_url or resolve_database_url(resolved_settings)

    app = FastAPI(title='Deriv Organismo', lifespan=app_lifespan)
    app.add_middleware(SessionMiddleware, secret_key=resolved_settings.app_secret_key)
    app.state.settings = resolved_settings
    app.state.auth_service = build_auth_service(resolved_settings)
    engine, account_service = build_account_service(resolved_database_url, resolved_settings)
    app.state.account_engine = engine
    app.state.account_service = account_service
    app.state.realtime_data_service = build_realtime_data_service(resolved_settings, account_service)

    if run_migrations_on_create:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(create_all_tables(engine))

    app.mount('/static', StaticFiles(directory=str(STATIC_DIR)), name='static')
    app.add_api_route('/health', health, methods=['GET'])
    app.add_api_route('/status', status, methods=['GET'])
    app.add_api_route('/accounts', list_accounts, methods=['GET'])
    app.add_api_route('/symbols', list_symbols, methods=['GET'])
    app.add_api_route('/events', list_events, methods=['GET'])
    app.add_api_route('/decisions/latest', latest_decision, methods=['GET'])
    app.add_api_route('/login', login_page, methods=['GET'])
    app.add_api_route('/login', login, methods=['POST'])
    app.add_api_route('/logout', logout, methods=['POST'])
    app.include_router(admin_router)
    app.add_api_route('/dashboard', dashboard, methods=['GET'])
    app.add_api_route('/dashboard/data', dashboard_data, methods=['GET'])
    app.add_api_route('/operations', operations_page, methods=['GET'])
    app.add_api_route('/operations/data', operations_data, methods=['GET'])
    app.add_api_route('/performance', performance_page, methods=['GET'])
    app.add_api_route('/performance/data', performance_data, methods=['GET'])
    app.add_api_route('/ticks/recent', recent_ticks, methods=['GET'])
    app.add_api_route('/decisions/recent', recent_decisions, methods=['GET'])
    return app


app = create_app(run_migrations_on_create=False)
