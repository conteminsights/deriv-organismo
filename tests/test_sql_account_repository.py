from pathlib import Path

import pytest

from deriv_organismo.domain.deriv_account import DerivAccount, DerivCredential
from deriv_organismo.repositories.sql_account_repository import SqlAlchemyAccountRepository
from deriv_organismo.db.session import build_engine, build_session_factory, create_all_tables


@pytest.mark.asyncio
async def test_sql_repository_persists_account_and_credential(tmp_path: Path):
    db_path = tmp_path / 'repo.db'
    engine = build_engine(f'sqlite+aiosqlite:///{db_path}')
    try:
        await create_all_tables(engine)
        session_factory = build_session_factory(engine)
        repo = SqlAlchemyAccountRepository(session_factory)

        account = DerivAccount(
            account_id='acc_sql_1',
            tenant_id='tenant_master',
            login_id='CR999999',
            account_type='demo',
            name='Conta SQL',
        )
        credential = DerivCredential(
            account_id='acc_sql_1',
            tenant_id='tenant_master',
            encrypted_token='enc-token',
            is_valid=True,
        )

        await repo.save(account)
        await repo.save_credential(credential)

        stored = await repo.get_by_id('acc_sql_1')
        tenant_accounts = await repo.list_by_tenant('tenant_master')
        stored_credential = await repo.get_credential('acc_sql_1')

        assert stored is not None
        assert stored.name == 'Conta SQL'
        assert len(tenant_accounts) == 1
        assert tenant_accounts[0].login_id == 'CR999999'
        assert stored_credential is not None
        assert stored_credential.encrypted_token == 'enc-token'
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_sql_repository_prevents_cross_tenant_access(tmp_path: Path):
    db_path = tmp_path / 'repo-cross-tenant.db'
    engine = build_engine(f'sqlite+aiosqlite:///{db_path}')
    try:
        await create_all_tables(engine)
        session_factory = build_session_factory(engine)
        repo = SqlAlchemyAccountRepository(session_factory)

        account = DerivAccount(
            account_id='acc_private',
            tenant_id='tenant_a',
            login_id='CR111111',
            account_type='real',
            name='Conta Privada',
        )
        await repo.save(account)

        visible = await repo.get_by_tenant_and_id('tenant_a', 'acc_private')
        blocked = await repo.get_by_tenant_and_id('tenant_b', 'acc_private')

        assert visible is not None
        assert blocked is None
    finally:
        await engine.dispose()
