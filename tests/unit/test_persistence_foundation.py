from deriv_organismo.config import Settings
from deriv_organismo.db.base import Base


def test_settings_builds_safe_sqlite_url_for_local_bootstrap():
    settings = Settings(
        database_url='sqlite+aiosqlite:///./deriv-organismo.db',
        redis_url='redis://localhost:6379/0',
    )

    assert settings.database_url.startswith('sqlite+aiosqlite://')


def test_metadata_contains_persistent_multi_tenant_tables():
    table_names = set(Base.metadata.tables.keys())

    assert 'tenants' in table_names
    assert 'deriv_accounts' in table_names
    assert 'deriv_credentials' in table_names


def test_deriv_account_table_has_expected_columns():
    deriv_accounts = Base.metadata.tables['deriv_accounts']

    expected = {
        'account_id',
        'tenant_id',
        'login_id',
        'account_type',
        'name',
        'is_active',
        'created_at',
        'updated_at',
    }
    assert expected.issubset(set(deriv_accounts.columns.keys()))


def test_deriv_credential_table_has_expected_columns():
    deriv_credentials = Base.metadata.tables['deriv_credentials']

    expected = {
        'account_id',
        'tenant_id',
        'encrypted_token',
        'is_valid',
        'created_at',
        'updated_at',
    }
    assert expected.issubset(set(deriv_credentials.columns.keys()))
