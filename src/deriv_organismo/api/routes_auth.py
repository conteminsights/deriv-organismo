from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel

from deriv_organismo.api.templating import templates
from deriv_organismo.services.auth_service import AuthService


class LoginRequest(BaseModel):
    email: str
    password: str


def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


def get_session_auth(request: Request) -> dict | None:
    return request.session.get('auth')


def resolve_tenant_id(request: Request, requested_tenant_id: str) -> str:
    return get_auth_service(request).resolve_tenant(get_session_auth(request), requested_tenant_id)


def require_page_auth(request: Request):
    auth_service = get_auth_service(request)
    if auth_service.is_authenticated(get_session_auth(request)):
        return None
    return RedirectResponse(url='/login', status_code=307)


def require_api_auth(request: Request) -> None:
    auth_service = get_auth_service(request)
    if auth_service.is_authenticated(get_session_auth(request)):
        return
    raise HTTPException(status_code=401, detail='authentication required')


async def login_page(request: Request):
    auth_service = get_auth_service(request)
    if auth_service.enabled and auth_service.is_authenticated(get_session_auth(request)):
        return RedirectResponse(url='/dashboard', status_code=307)
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={'active_page': 'login'},
    )


async def login(request: Request, payload: LoginRequest) -> JSONResponse:
    session_auth = get_auth_service(request).authenticate(payload.email, payload.password)
    request.session['auth'] = session_auth
    return JSONResponse({'authenticated': True, 'role': session_auth['role'], 'tenant_id': session_auth['tenant_id']})


async def logout(request: Request) -> JSONResponse:
    request.session.clear()
    return JSONResponse({'authenticated': False})
