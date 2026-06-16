from fastapi import Request
from fastapi.responses import JSONResponse

from deriv_organismo.api.platform_payloads import operations_payload, seeded_accounts
from deriv_organismo.api.routes_admin import get_account_service
from deriv_organismo.api.routes_auth import require_api_auth, require_page_auth, resolve_tenant_id
from deriv_organismo.api.templating import templates


def get_realtime_data_service(request: Request):
    return getattr(request.app.state, 'realtime_data_service', None)


async def operations_data_payload(tenant_id: str, request: Request) -> dict:
    realtime_service = get_realtime_data_service(request)
    if realtime_service is not None:
        return await realtime_service.build_operations_payload(tenant_id)
    domain_accounts = await get_account_service(request).list_accounts_by_tenant(tenant_id)
    accounts = seeded_accounts(domain_accounts, tenant_id)
    return operations_payload(accounts, tenant_id)


async def operations_page(request: Request, tenant_id: str = 'tenant_master'):
    auth_response = require_page_auth(request)
    if auth_response is not None:
        return auth_response
    effective_tenant_id = resolve_tenant_id(request, tenant_id)
    payload = await operations_data_payload(effective_tenant_id, request)
    return templates.TemplateResponse(
        request=request,
        name='operations.html',
        context={
            'active_page': 'operations',
            'tenant_id': effective_tenant_id,
            'payload': payload,
        },
    )


async def operations_data(request: Request, tenant_id: str = 'tenant_master'):
    require_api_auth(request)
    effective_tenant_id = resolve_tenant_id(request, tenant_id)
    return JSONResponse(await operations_data_payload(effective_tenant_id, request))
