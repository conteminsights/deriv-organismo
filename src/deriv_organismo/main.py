import asyncio
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from deriv_organismo.api.routes_accounts import list_accounts, list_symbols
from deriv_organismo.api.routes_admin import router as admin_router
from deriv_organismo.api.routes_auth import login_page
from deriv_organismo.api.routes_dashboard import dashboard, dashboard_data
from deriv_organismo.api.routes_events import latest_decision, list_events
from deriv_organismo.api.routes_health import health, status
from deriv_organismo.api.routes_operations import operations_data, operations_page
from deriv_organismo.api.routes_performance import performance_data, performance_page
from deriv_organismo.config import DEFAULT_DEV_DATABASE_URL, Settings
from deriv_organismo.db.session import build_engine, build_session_factory, create_all_tables
from deriv_organismo.repositories.sql_account_repository import SqlAlchemyAccountRepository
from deriv_organismo.services.credential_manager import CredentialManager
from deriv_organismo.services.deriv_account_service import DerivAccountService
from deriv_organismo.services.deriv_token_validator import DerivTokenValidator

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
DEFAULT_DATABASE_URL = DEFAULT_DEV_DATABASE_URL


def resolve_database_url(settings: Settings) -> str:
    database_url = settings.database_url
    if database_url is None:
        raise ValueError('DATABASE_URL could not be resolved from settings')
    return database_url


def build_account_service(database_url: str) -> tuple:
    engine = build_engine(database_url)
    session_factory = build_session_factory(engine)
    repository = SqlAlchemyAccountRepository(session_factory)
    credential_manager = CredentialManager(secret_key='temp-secret-key-32-bytes-long!!')
    token_validator = DerivTokenValidator()
    service = DerivAccountService(repository, credential_manager, token_validator)
    return engine, service


def create_app(database_url: str | None = None, settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or Settings()
    resolved_database_url = database_url or resolve_database_url(resolved_settings)

    app = FastAPI(title='Deriv Organismo')
    engine, account_service = build_account_service(resolved_database_url)
    app.state.settings = resolved_settings
    app.state.account_engine = engine
    app.state.account_service = account_service

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        asyncio.run(create_all_tables(engine))

    @app.on_event('startup')
    async def startup() -> None:
        await create_all_tables(engine)

    @app.on_event('shutdown')
    async def shutdown() -> None:
        await engine.dispose()

    app.mount('/static', StaticFiles(directory=str(STATIC_DIR)), name='static')
    app.add_api_route('/health', health, methods=['GET'])
    app.add_api_route('/status', status, methods=['GET'])
    app.add_api_route('/accounts', list_accounts, methods=['GET'])
    app.add_api_route('/symbols', list_symbols, methods=['GET'])
    app.add_api_route('/events', list_events, methods=['GET'])
    app.add_api_route('/decisions/latest', latest_decision, methods=['GET'])
    app.add_api_route('/login', login_page, methods=['GET'])
    app.include_router(admin_router)
    app.add_api_route('/dashboard', dashboard, methods=['GET'])
    app.add_api_route('/dashboard/data', dashboard_data, methods=['GET'])
    app.add_api_route('/operations', operations_page, methods=['GET'])
    app.add_api_route('/operations/data', operations_data, methods=['GET'])
    app.add_api_route('/performance', performance_page, methods=['GET'])
    app.add_api_route('/performance/data', performance_data, methods=['GET'])
    return app


app = create_app()
