from fastapi import Request
from fastapi.responses import JSONResponse

from deriv_organismo.api.platform_payloads import performance_payload, seeded_accounts
from deriv_organismo.api.routes_admin import get_account_service
from deriv_organismo.api.templating import templates


async def performance_data_payload(tenant_id: str, request: Request) -> dict:
    domain_accounts = await get_account_service(request).list_accounts_by_tenant(tenant_id)
    accounts = seeded_accounts(domain_accounts, tenant_id)
    return performance_payload(accounts, tenant_id)


async def performance_page(request: Request, tenant_id: str = 'tenant_master'):
    payload = await performance_data_payload(tenant_id, request)
    return templates.TemplateResponse(
        request=request,
        name='performance.html',
        context={
            'active_page': 'performance',
            'tenant_id': tenant_id,
            'payload': payload,
        },
    )


async def performance_data(request: Request, tenant_id: str = 'tenant_master'):
    return JSONResponse(await performance_data_payload(tenant_id, request))
