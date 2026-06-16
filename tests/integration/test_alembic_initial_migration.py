from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def make_alembic_config(tmp_path: Path) -> tuple[Config, str]:
    db_path = tmp_path / 'alembic_migration.sqlite3'
    database_url = f'sqlite+aiosqlite:///{db_path}'

    config = Config('/home/alexandre/projetos/deriv-organismo/alembic.ini')
    config.set_main_option('script_location', '/home/alexandre/projetos/deriv-organismo/alembic')
    config.set_main_option('sqlalchemy.url', database_url)
    return config, str(db_path)


def test_upgrade_head_creates_multi_tenant_tables(tmp_path: Path):
    config, db_path = make_alembic_config(tmp_path)

    command.upgrade(config, 'head')

    inspector = inspect(create_engine(f'sqlite:///{db_path}'))
    table_names = set(inspector.get_table_names())

    assert 'tenants' in table_names
    assert 'deriv_accounts' in table_names
    assert 'deriv_credentials' in table_names


def test_downgrade_base_removes_multi_tenant_tables(tmp_path: Path):
    config, db_path = make_alembic_config(tmp_path)

    command.upgrade(config, 'head')
    command.downgrade(config, 'base')

    inspector = inspect(create_engine(f'sqlite:///{db_path}'))
    table_names = set(inspector.get_table_names())

    assert 'tenants' not in table_names
    assert 'deriv_accounts' not in table_names
    assert 'deriv_credentials' not in table_names
