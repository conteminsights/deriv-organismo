from fastapi import Request
from fastapi.responses import JSONResponse

from deriv_organismo.api.platform_payloads import operations_payload, performance_payload, seeded_accounts, summarize_accounts
from deriv_organismo.api.routes_admin import account_service
from deriv_organismo.api.templating import templates


def dashboard_payload(tenant_id: str = 'tenant_master') -> dict:
    accounts = seeded_accounts(account_service.list_accounts_by_tenant(tenant_id), tenant_id)
    operations = operations_payload(accounts, tenant_id)
    performance = performance_payload(accounts, tenant_id)
    summary = summarize_accounts(accounts)
    return {
        'app_status': 'running',
        'tenant_id': tenant_id,
        'accounts': accounts,
        'summary': summary,
        'operations': operations,
        'performance': performance,
        'last_decisions': [
            {
                'decision': 'observe',
                'symbol': operations['operations'][0]['symbol'],
                'specialist_key': operations['operations'][0]['strategy'],
            }
        ],
        'last_risk_blocks': [
            {'reason': 'breakout_guarded em hedge passivo'}
        ] if operations['losing_count'] else [],
        'last_promotions': [],
    }


def dashboard_data(tenant_id: str = 'tenant_master') -> JSONResponse:
    return JSONResponse(dashboard_payload(tenant_id))


async def dashboard(request: Request, tenant_id: str = 'tenant_master'):
    payload = dashboard_payload(tenant_id)
    account = payload['accounts'][0]
    decision = payload['last_decisions'][0]
    return templates.TemplateResponse(
        request=request,
        name='dashboard.html',
        context={
            'active_page': 'dashboard',
            'payload': payload,
            'account': account,
            'decision': decision,
            'risk_block_count': len(payload['last_risk_blocks']),
            'promotion_count': len(payload['last_promotions']),
        },
    )
