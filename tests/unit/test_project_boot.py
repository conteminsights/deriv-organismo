from deriv_organismo.main import create_app


def test_create_app_exposes_health_route():
    app = create_app()
    routes = {route.path for route in app.routes}
    assert "/health" in routes
