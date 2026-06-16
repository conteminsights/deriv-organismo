"""Rotas admin para gerenciamento de contas Deriv."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Literal

from deriv_organismo.repositories.account_repository import AccountRepository
from deriv_organismo.services.credential_manager import CredentialManager
from deriv_organismo.services.deriv_token_validator import DerivTokenValidator
from deriv_organismo.services.deriv_account_service import DerivAccountService


router = APIRouter(prefix="/admin", tags=["admin"])

# Instâncias globais (serão substituídas por DI no futuro)
account_repo = AccountRepository()
credential_manager = CredentialManager(secret_key="temp-secret-key-32-bytes-long!!")
token_validator = DerivTokenValidator()
account_service = DerivAccountService(account_repo, credential_manager, token_validator)


class RegisterAccountRequest(BaseModel):
    """Request para registrar nova conta."""
    tenant_id: str
    login_id: str
    token: str
    account_type: Literal["demo", "real"]
    name: str


class RegisterAccountResponse(BaseModel):
    """Response após registrar conta."""
    account_id: str
    login_id: str
    account_type: str
    name: str
    is_active: bool


@router.get("/accounts", response_model=list[RegisterAccountResponse])
async def list_accounts(tenant_id: str = "tenant_master"):
    """Lista todas as contas de um tenant."""
    accounts = account_service.list_accounts_by_tenant(tenant_id)
    return [
        RegisterAccountResponse(
            account_id=acc.account_id,
            login_id=acc.login_id,
            account_type=acc.account_type,
            name=acc.name,
            is_active=acc.is_active
        )
        for acc in accounts
    ]


@router.post("/accounts", response_model=RegisterAccountResponse, status_code=201)
async def register_account(request: RegisterAccountRequest):
    """Registra nova conta Deriv com validação de token."""
    try:
        account, credential = await account_service.register_account(
            tenant_id=request.tenant_id,
            login_id=request.login_id,
            token=request.token,
            account_type=request.account_type,
            name=request.name
        )
        
        return RegisterAccountResponse(
            account_id=account.account_id,
            login_id=account.login_id,
            account_type=account.account_type,
            name=account.name,
            is_active=account.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
