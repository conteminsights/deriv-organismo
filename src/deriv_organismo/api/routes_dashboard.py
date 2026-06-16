from fastapi import Request
from fastapi.responses import JSONResponse

from deriv_organismo.api.platform_payloads import operations_payload, performance_payload, seeded_accounts, summarize_accounts
from deriv_organismo.api.routes_admin import get_account_service
from deriv_organismo.api.templating import templates


async def dashboard_payload(tenant_id: str, request: Request) -> dict:
    domain_accounts = await get_account_service(request).list_accounts_by_tenant(tenant_id)
    accounts = seeded_accounts(domain_accounts, tenant_id)
    operations = operations_payload(accounts, tenant_id)
    performance = performance_payload(accounts, tenant_id)
    return {
        'app_status': 'running',
        'tenant_id': tenant_id,
        'summary': summarize_accounts(accounts),
        'accounts': accounts,
        'operations': operations,
        'performance': performance,
    }


async def dashboard(request: Request, tenant_id: str = 'tenant_master'):
    payload = await dashboard_payload(tenant_id, request)
    operations = payload['operations']['operations']
    decision = operations[0] if operations else {
        'decision': 'aguardando coleta',
        'symbol': '-',
        'specialist_key': 'bootstrap_preview',
    }
    risk_block_count = sum(1 for item in operations if item['risk_state'] != 'estável')
    return templates.TemplateResponse(
        request=request,
        name='dashboard.html',
        context={
            'active_page': 'dashboard',
            'tenant_id': tenant_id,
            'payload': payload,
            'account': payload['accounts'][0] if payload['accounts'] else None,
            'operations': operations,
            'performance_accounts': payload['performance']['accounts'],
            'decision': decision,
            'risk_block_count': risk_block_count,
        },
    )


async def dashboard_data(request: Request, tenant_id: str = 'tenant_master'):
    return JSONResponse(await dashboard_payload(tenant_id, request))
