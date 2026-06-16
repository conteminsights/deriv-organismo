"""Serviço de gerenciamento de contas Deriv."""
import uuid
from typing import Literal

from deriv_organismo.domain.deriv_account import DerivAccount, DerivCredential
from deriv_organismo.services.credential_manager import CredentialManager
from deriv_organismo.services.deriv_token_validator import DerivTokenValidator


class DerivAccountService:
    """Serviço para gerenciar contas Deriv com validação e criptografia."""

    def __init__(self, account_repository, credential_manager: CredentialManager, token_validator: DerivTokenValidator):
        self.account_repository = account_repository
        self.credential_manager = credential_manager
        self.token_validator = token_validator

    async def register_account(
        self,
        tenant_id: str,
        login_id: str,
        token: str,
        account_type: Literal['demo', 'real'],
        name: str,
    ) -> tuple[DerivAccount, DerivCredential]:
        if not token:
            raise ValueError('token cannot be empty')
        if account_type not in ('demo', 'real'):
            raise ValueError("account_type must be 'demo' or 'real'")

        is_valid = await self.token_validator.validate_token(token, login_id)
        if not is_valid:
            raise ValueError('invalid token')

        account_id = f'acc_{uuid.uuid4().hex[:8]}'
        account = DerivAccount(
            account_id=account_id,
            tenant_id=tenant_id,
            login_id=login_id,
            account_type=account_type,
            name=name,
            is_active=True,
        )
        credential = DerivCredential(
            account_id=account_id,
            tenant_id=tenant_id,
            encrypted_token=self.credential_manager.encrypt_token(token),
            is_valid=True,
        )

        await self.account_repository.save(account)
        await self.account_repository.save_credential(credential)
        return account, credential

    async def list_accounts_by_tenant(self, tenant_id: str) -> list[DerivAccount]:
        return await self.account_repository.list_by_tenant(tenant_id)

    async def get_plaintext_token(self, tenant_id: str, account_id: str) -> str:
        account = await self.account_repository.get_by_tenant_and_id(tenant_id, account_id)
        if not account:
            raise ValueError('account not found')
        credential = await self.account_repository.get_credential(account_id)
        if not credential or credential.tenant_id != tenant_id:
            raise ValueError('credential not found')
        return self.credential_manager.decrypt_token(credential.encrypted_token)

    async def deactivate_account(self, account_id: str) -> DerivAccount:
        account = await self.account_repository.get_by_id(account_id)
        if not account:
            raise ValueError('account not found')

        account.is_active = False
        await self.account_repository.save(account)
        return account
