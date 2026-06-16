import pytest

from deriv_organismo.config import DEFAULT_DEV_DATABASE_URL, Settings


def test_dev_defaults_to_local_sqlite_when_database_url_missing():
    settings = Settings(app_env='dev', redis_url='redis://localhost:6379/0')

    assert settings.database_url == DEFAULT_DEV_DATABASE_URL


def test_prod_requires_explicit_database_url():
    with pytest.raises(ValueError, match='DATABASE_URL'):
        Settings(app_env='prod', redis_url='redis://localhost:6379/0')
