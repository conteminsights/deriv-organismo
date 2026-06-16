from pathlib import Path

from sqlalchemy import inspect

from deriv_organismo.db.session import build_engine, build_session_factory, create_all_tables


def test_build_engine_uses_configured_url():
    engine = build_engine('sqlite+aiosqlite:///./test-persistence.db')

    assert str(engine.url) == 'sqlite+aiosqlite:///./test-persistence.db'



def test_build_session_factory_binds_to_engine():
    engine = build_engine('sqlite+aiosqlite:///./test-session.db')
    factory = build_session_factory(engine)

    assert factory.kw['bind'] is engine


async def test_create_all_tables_materializes_expected_schema(tmp_path: Path):
    db_path = tmp_path / 'integration.db'
    database_url = f'sqlite+aiosqlite:///{db_path}'
    engine = build_engine(database_url)

    try:
        await create_all_tables(engine)
        async with engine.begin() as conn:
            tables = await conn.run_sync(lambda sync_conn: set(inspect(sync_conn).get_table_names()))
        assert 'tenants' in tables
        assert 'deriv_accounts' in tables
        assert 'deriv_credentials' in tables
    finally:
        await engine.dispose()
