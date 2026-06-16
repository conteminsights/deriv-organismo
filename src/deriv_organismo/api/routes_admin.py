"""Rotas admin para gerenciamento de contas Deriv."""
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from deriv_organismo.api.platform_payloads import seeded_accounts, summarize_accounts
from deriv_organismo.api.templating import templates
from deriv_organismo.services.deriv_account_service import DerivAccountService

router = APIRouter(prefix='/admin', tags=['admin'])


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


def get_account_service(request: Request) -> DerivAccountService:
    return request.app.state.account_service


async def serialize_accounts(request: Request, tenant_id: str) -> list[dict]:
    accounts = await get_account_service(request).list_accounts_by_tenant(tenant_id)
    return seeded_accounts(accounts, tenant_id)


@router.get('/accounts')
async def admin_accounts_page(request: Request, tenant_id: str = 'tenant_master'):
    accounts = await serialize_accounts(request, tenant_id)
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
async def list_accounts_data(request: Request, tenant_id: str = 'tenant_master'):
    rows = await serialize_accounts(request, tenant_id)
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
async def register_account(request: Request, payload: RegisterAccountRequest):
    try:
        account, _credential = await get_account_service(request).register_account(
            tenant_id=payload.tenant_id,
            login_id=payload.login_id,
            token=payload.token,
            account_type=payload.account_type,
            name=payload.name,
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
        raise HTTPException(status_code=400, detail=str(e)) from e
