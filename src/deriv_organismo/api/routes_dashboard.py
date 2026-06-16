from fastapi import Request
from fastapi.responses import JSONResponse

from deriv_organismo.api.templating import templates


def dashboard_payload() -> dict:
    return {
        'app_status': 'running',
        'accounts': [
            {
                'account_id': 'acc_primary',
                'account_slug': 'primary',
                'mode': 'demo',
            }
        ],
        'last_decisions': [
            {
                'decision': 'observe',
                'symbol': 'R_100',
                'specialist_key': 'trend_follow',
            }
        ],
        'last_risk_blocks': [],
        'last_promotions': [],
    }


def dashboard_data() -> JSONResponse:
    return JSONResponse(dashboard_payload())


async def dashboard(request: Request):
    payload = dashboard_payload()
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
