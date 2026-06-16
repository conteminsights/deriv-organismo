from pathlib import Path

import pytest

from deriv_organismo.db.session import build_engine, build_session_factory, create_all_tables
from deriv_organismo.repositories.sql_account_repository import SqlAlchemyAccountRepository
from deriv_organismo.services.credential_manager import CredentialManager
from deriv_organismo.services.deriv_account_service import DerivAccountService
from deriv_organismo.services.deriv_token_validator import DerivTokenValidator


@pytest.mark.asyncio
async def test_account_service_returns_decrypted_token_for_authorized_tenant(tmp_path: Path):
    db_path = tmp_path / 'secret-flow.db'
    engine = build_engine(f'sqlite+aiosqlite:///{db_path}')
    try:
        await create_all_tables(engine)
        repo = SqlAlchemyAccountRepository(build_session_factory(engine))
        service = DerivAccountService(
            repo,
            CredentialManager(secret_key='tenant-secret-key-32-bytes-long!!'),
            DerivTokenValidator(),
        )

        account, _credential = await service.register_account(
            tenant_id='tenant_a',
            login_id='CR123456',
            token='token-plain-a',
            account_type='demo',
            name='Conta A',
        )

        token = await service.get_plaintext_token('tenant_a', account.account_id)

        assert token == 'token-plain-a'
    finally:
        await engine.dispose()
