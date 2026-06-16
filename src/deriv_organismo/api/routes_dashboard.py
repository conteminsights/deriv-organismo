from fastapi import Request
from fastapi.responses import JSONResponse

from deriv_organismo.api.platform_payloads import operations_payload, performance_payload, seeded_accounts, summarize_accounts
from deriv_organismo.api.routes_admin import get_account_service
from deriv_organismo.api.routes_auth import require_api_auth, require_page_auth, resolve_tenant_id
from deriv_organismo.api.templating import templates


def get_realtime_data_service(request: Request):
    return getattr(request.app.state, 'realtime_data_service', None)


async def dashboard_payload(tenant_id: str, request: Request) -> dict:
    realtime_service = get_realtime_data_service(request)
    if realtime_service is not None:
        operations = await realtime_service.build_operations_payload(tenant_id)
        performance = await realtime_service.build_performance_payload(tenant_id)
        accounts = operations['account_summaries']
        return {
            'app_status': 'running',
            'tenant_id': tenant_id,
            'summary': {
                'total_accounts': len(accounts),
                'active_accounts': len(accounts),
                'demo_accounts': sum(1 for item in performance['accounts'] if item['account_type'] == 'demo'),
                'real_accounts': sum(1 for item in performance['accounts'] if item['account_type'] == 'real'),
                'validated_accounts': len(accounts),
            },
            'accounts': accounts,
            'operations': operations,
            'performance': performance,
        }
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
    auth_response = require_page_auth(request)
    if auth_response is not None:
        return auth_response
    effective_tenant_id = resolve_tenant_id(request, tenant_id)
    payload = await dashboard_payload(effective_tenant_id, request)
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
            'tenant_id': effective_tenant_id,
            'payload': payload,
            'account': payload['accounts'][0] if payload['accounts'] else None,
            'operations': operations,
            'performance_accounts': payload['performance']['accounts'],
            'decision': decision,
            'risk_block_count': risk_block_count,
        },
    )


async def dashboard_data(request: Request, tenant_id: str = 'tenant_master'):
    require_api_auth(request)
    effective_tenant_id = resolve_tenant_id(request, tenant_id)
    return JSONResponse(await dashboard_payload(effective_tenant_id, request))
