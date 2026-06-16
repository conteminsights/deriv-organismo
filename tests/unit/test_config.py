from deriv_organismo.config import Settings


def test_settings_defaults_support_single_operator_and_future_multitenancy():
    settings = Settings(
        database_url="postgresql+asyncpg://localhost/test",
        redis_url="redis://localhost:6379/0",
    )
    assert settings.default_account_slug == "primary"
    assert settings.enable_multi_tenant is False
