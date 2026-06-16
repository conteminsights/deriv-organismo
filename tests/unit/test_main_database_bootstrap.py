import pytest

from deriv_organismo.config import DEFAULT_DEV_DATABASE_URL, DEFAULT_REDIS_URL, Settings
from deriv_organismo.main import resolve_database_url


def test_resolve_database_url_uses_settings_default_for_dev():
    settings = Settings(app_env='dev')

    assert resolve_database_url(settings) == DEFAULT_DEV_DATABASE_URL


def test_settings_dev_also_defaults_redis_locally():
    settings = Settings(app_env='dev')

    assert settings.redis_url == DEFAULT_REDIS_URL


def test_resolve_database_url_prefers_explicit_value():
    explicit_url = 'postgresql+asyncpg://user:pass@db:5432/deriv_organismo'
    settings = Settings(
        app_env='prod',
        database_url=explicit_url,
        redis_url='redis://cache:6379/0',
    )

    assert resolve_database_url(settings) == explicit_url


def test_prod_still_requires_explicit_database_url():
    with pytest.raises(ValueError, match='DATABASE_URL'):
        Settings(app_env='prod', redis_url='redis://cache:6379/0')
