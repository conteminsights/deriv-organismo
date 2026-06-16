"""Rotas admin para gerenciamento de contas Deriv."""
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from deriv_organismo.api.platform_payloads import seeded_accounts, summarize_accounts
from deriv_organismo.api.templating import templates
from deriv_organismo.repositories.account_repository import AccountRepository
from deriv_organismo.services.credential_manager import CredentialManager
from deriv_organismo.services.deriv_account_service import DerivAccountService
from deriv_organismo.services.deriv_token_validator import DerivTokenValidator

router = APIRouter(prefix='/admin', tags=['admin'])

account_repo = AccountRepository()
credential_manager = CredentialManager(secret_key='temp-secret-key-32-bytes-long!!')
token_validator = DerivTokenValidator()
account_service = DerivAccountService(account_repo, credential_manager, token_validator)


class RegisterAccountRequest(BaseModel):
    tenant_id: str
    login_id: str
    token: str
    account_type: Literal['demo', 'real']
    name: str


class RegisterAccountResponse(BaseModel):
    account_id: str
    tenant_id: str
    login_id: str
    account_type: str
    name: str
    is_active: bool


def serialize_accounts(tenant_id: str) -> list[dict]:
    return seeded_accounts(account_service.list_accounts_by_tenant(tenant_id), tenant_id)


@router.get('/accounts')
async def admin_accounts_page(request: Request, tenant_id: str = 'tenant_master'):
    accounts = serialize_accounts(tenant_id)
    return templates.TemplateResponse(
        request=request,
        name='admin_accounts.html',
        context={
            'active_page': 'admin_accounts',
            'accounts': accounts,
            'tenant_id': tenant_id,
            'summary': summarize_accounts(accounts),
        },
    )


@router.get('/accounts/data', response_model=list[RegisterAccountResponse])
async def list_accounts_data(tenant_id: str = 'tenant_master'):
    rows = serialize_accounts(tenant_id)
    return [
        RegisterAccountResponse(
            account_id=item['account_id'],
            tenant_id=item['tenant_id'],
            login_id=item['login_id'],
            account_type=item['account_type'],
            name=item['name'],
            is_active=item['is_active'],
        )
        for item in rows
    ]


@router.post('/accounts', response_model=RegisterAccountResponse, status_code=201)
async def register_account(request: RegisterAccountRequest):
    try:
        account, _credential = await account_service.register_account(
            tenant_id=request.tenant_id,
            login_id=request.login_id,
            token=request.token,
            account_type=request.account_type,
            name=request.name,
        )
        return RegisterAccountResponse(
            account_id=account.account_id,
            tenant_id=account.tenant_id,
            login_id=account.login_id,
            account_type=account.account_type,
            name=account.name,
            is_active=account.is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
