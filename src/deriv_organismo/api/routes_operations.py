from fastapi import Request
from fastapi.responses import JSONResponse

from deriv_organismo.api.platform_payloads import operations_payload, seeded_accounts
from deriv_organismo.api.routes_admin import account_service
from deriv_organismo.api.templating import templates


def operations_data_payload(tenant_id: str = 'tenant_master') -> dict:
    accounts = seeded_accounts(account_service.list_accounts_by_tenant(tenant_id), tenant_id)
    return operations_payload(accounts, tenant_id)


def operations_data(tenant_id: str = 'tenant_master') -> JSONResponse:
    return JSONResponse(operations_data_payload(tenant_id))


async def operations_page(request: Request, tenant_id: str = 'tenant_master'):
    payload = operations_data_payload(tenant_id)
    return templates.TemplateResponse(
        request=request,
        name='operations.html',
        context={
            'active_page': 'operations',
            'payload': payload,
        },
    )
