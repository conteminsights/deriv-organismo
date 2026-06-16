import pytest

from deriv_organismo.config import Settings


def test_prod_requires_explicit_app_and_credential_secrets():
    with pytest.raises(ValueError, match='APP_SECRET_KEY'):
        Settings(
            app_env='prod',
            database_url='postgresql+asyncpg://user:pass@db:5432/deriv_organismo',
            redis_url='redis://cache:6379/0',
        )
