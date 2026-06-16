from fastapi import Request
from fastapi.responses import JSONResponse

from deriv_organismo.api.platform_payloads import operations_payload, seeded_accounts
from deriv_organismo.api.routes_admin import get_account_service
from deriv_organismo.api.templating import templates


async def operations_data_payload(tenant_id: str, request: Request) -> dict:
    domain_accounts = await get_account_service(request).list_accounts_by_tenant(tenant_id)
    accounts = seeded_accounts(domain_accounts, tenant_id)
    return operations_payload(accounts, tenant_id)


async def operations_page(request: Request, tenant_id: str = 'tenant_master'):
    payload = await operations_data_payload(tenant_id, request)
    return templates.TemplateResponse(
        request=request,
        name='operations.html',
        context={
            'active_page': 'operations',
            'tenant_id': tenant_id,
            'payload': payload,
        },
    )


async def operations_data(request: Request, tenant_id: str = 'tenant_master'):
    return JSONResponse(await operations_data_payload(tenant_id, request))
