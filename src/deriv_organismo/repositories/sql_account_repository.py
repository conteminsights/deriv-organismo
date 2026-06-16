from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from deriv_organismo.db.models import DerivAccountRecord, DerivCredentialRecord, TenantRecord
from deriv_organismo.domain.deriv_account import DerivAccount, DerivCredential


class SqlAlchemyAccountRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def save(self, account: DerivAccount) -> None:
        async with self.session_factory() as session:
            await self._ensure_tenant(session, account.tenant_id)
            existing = await session.get(DerivAccountRecord, account.account_id)
            if existing is None:
                session.add(self._to_account_record(account))
            else:
                existing.tenant_id = account.tenant_id
                existing.login_id = account.login_id
                existing.account_type = account.account_type
                existing.name = account.name
                existing.is_active = account.is_active
                existing.metadata_json = dict(account.metadata)
            await session.commit()

    async def save_credential(self, credential: DerivCredential) -> None:
        async with self.session_factory() as session:
            await self._ensure_tenant(session, credential.tenant_id)
            existing = await session.get(DerivCredentialRecord, credential.account_id)
            if existing is None:
                session.add(self._to_credential_record(credential))
            else:
                existing.tenant_id = credential.tenant_id
                existing.encrypted_token = credential.encrypted_token
                existing.token_type = credential.token_type
                existing.is_valid = credential.is_valid
                existing.last_validated_at = credential.last_validated_at
            await session.commit()

    async def get_by_id(self, account_id: str) -> DerivAccount | None:
        async with self.session_factory() as session:
            record = await session.get(DerivAccountRecord, account_id)
            return None if record is None else self._to_account_domain(record)

    async def get_by_tenant_and_id(self, tenant_id: str, account_id: str) -> DerivAccount | None:
        async with self.session_factory() as session:
            stmt = select(DerivAccountRecord).where(
                DerivAccountRecord.account_id == account_id,
                DerivAccountRecord.tenant_id == tenant_id,
            )
            record = (await session.execute(stmt)).scalar_one_or_none()
            return None if record is None else self._to_account_domain(record)

    async def list_by_tenant(self, tenant_id: str) -> list[DerivAccount]:
        async with self.session_factory() as session:
            stmt = select(DerivAccountRecord).where(DerivAccountRecord.tenant_id == tenant_id)
            rows = (await session.execute(stmt)).scalars().all()
            return [self._to_account_domain(row) for row in rows]

    async def get_credential(self, account_id: str) -> DerivCredential | None:
        async with self.session_factory() as session:
            record = await session.get(DerivCredentialRecord, account_id)
            return None if record is None else self._to_credential_domain(record)

    async def delete(self, account_id: str) -> None:
        async with self.session_factory() as session:
            credential = await session.get(DerivCredentialRecord, account_id)
            if credential is not None:
                await session.delete(credential)
            record = await session.get(DerivAccountRecord, account_id)
            if record is not None:
                await session.delete(record)
            await session.commit()

    async def _ensure_tenant(self, session: AsyncSession, tenant_id: str) -> None:
        tenant = await session.get(TenantRecord, tenant_id)
        if tenant is None:
            session.add(TenantRecord(tenant_id=tenant_id, name=tenant_id))
            await session.flush()

    @staticmethod
    def _to_account_record(account: DerivAccount) -> DerivAccountRecord:
        return DerivAccountRecord(
            account_id=account.account_id,
            tenant_id=account.tenant_id,
            login_id=account.login_id,
            account_type=account.account_type,
            name=account.name,
            is_active=account.is_active,
            metadata_json=dict(account.metadata),
            created_at=account.created_at,
        )

    @staticmethod
    def _to_credential_record(credential: DerivCredential) -> DerivCredentialRecord:
        return DerivCredentialRecord(
            account_id=credential.account_id,
            tenant_id=credential.tenant_id,
            encrypted_token=credential.encrypted_token,
            token_type=credential.token_type,
            is_valid=credential.is_valid,
            created_at=credential.created_at,
            last_validated_at=credential.last_validated_at,
        )

    @staticmethod
    def _to_account_domain(record: DerivAccountRecord) -> DerivAccount:
        return DerivAccount(
            account_id=record.account_id,
            tenant_id=record.tenant_id,
            login_id=record.login_id,
            account_type=record.account_type,
            name=record.name,
            is_active=record.is_active,
            created_at=record.created_at,
            metadata=record.metadata_json,
        )

    @staticmethod
    def _to_credential_domain(record: DerivCredentialRecord) -> DerivCredential:
        return DerivCredential(
            account_id=record.account_id,
            tenant_id=record.tenant_id,
            encrypted_token=record.encrypted_token,
            token_type=record.token_type,
            is_valid=record.is_valid,
            created_at=record.created_at,
            last_validated_at=record.last_validated_at,
        )
