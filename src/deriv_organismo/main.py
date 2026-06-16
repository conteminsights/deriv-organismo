from fastapi import FastAPI

from deriv_organismo.api.routes_accounts import list_accounts, list_symbols
from deriv_organismo.api.routes_dashboard import dashboard, dashboard_data
from deriv_organismo.api.routes_admin import router as admin_router
from deriv_organismo.api.routes_events import latest_decision, list_events
from deriv_organismo.api.routes_health import health, status


def create_app() -> FastAPI:
    app = FastAPI(title="Deriv Organismo")
    app.add_api_route("/health", health, methods=["GET"])
    app.add_api_route("/status", status, methods=["GET"])
    app.add_api_route("/accounts", list_accounts, methods=["GET"])
    app.add_api_route("/symbols", list_symbols, methods=["GET"])
    app.add_api_route("/events", list_events, methods=["GET"])
    app.add_api_route("/decisions/latest", latest_decision, methods=["GET"])
    app.include_router(admin_router)
    app.add_api_route("/dashboard", dashboard, methods=["GET"])
    app.add_api_route("/dashboard/data", dashboard_data, methods=["GET"])
    return app


app = create_app()
