from deriv_organismo.main import create_app


def test_create_app_exposes_health_route():
    app = create_app()
    routes = {route.path for route in app.routes if hasattr(route, "path")}
    assert "/health" in routes


def test_create_app_uses_lifespan_instead_of_legacy_startup_shutdown_hooks():
    app = create_app()

    assert app.router.on_startup == []
    assert app.router.on_shutdown == []


def test_create_app_can_skip_eager_table_bootstrap_for_module_level_app():
    app = create_app(run_migrations_on_create=False)

    assert app.state.account_engine is not None
