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

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'


def create_app() -> FastAPI:
    app = FastAPI(title='Deriv Organismo')
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
