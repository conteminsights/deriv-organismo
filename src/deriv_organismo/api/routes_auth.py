from fastapi import Request
from fastapi.responses import HTMLResponse

from deriv_organismo.api.templating import templates


async def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={'active_page': 'login'},
    )
