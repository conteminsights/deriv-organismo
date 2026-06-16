from __future__ import annotations

from typing import Any


class AuthService:
    def __init__(
        self,
        *,
        enabled: bool,
        master_email: str | None = None,
        master_password: str | None = None,
        tenant_email: str | None = None,
        tenant_password: str | None = None,
        tenant_scope_id: str | None = None,
    ) -> None:
        self.enabled = enabled
        self.master_email = master_email
        self.master_password = master_password
        self.tenant_email = tenant_email
        self.tenant_password = tenant_password
        self.tenant_scope_id = tenant_scope_id

    def authenticate(self, email: str, password: str) -> dict[str, Any]:
        if not self.enabled:
            return {'role': 'master', 'email': 'dev-local', 'tenant_id': None}
        if email == self.master_email and password == self.master_password:
            return {'role': 'master', 'email': email, 'tenant_id': None}
        if (
            email == self.tenant_email
            and password == self.tenant_password
            and self.tenant_scope_id
        ):
            return {'role': 'tenant', 'email': email, 'tenant_id': self.tenant_scope_id}
        raise ValueError('invalid credentials')

    def resolve_tenant(self, session_auth: dict[str, Any] | None, requested_tenant_id: str) -> str:
        if not self.enabled or session_auth is None:
            return requested_tenant_id
        if session_auth.get('role') == 'master':
            return requested_tenant_id
        return str(session_auth.get('tenant_id') or requested_tenant_id)

    def is_authenticated(self, session_auth: dict[str, Any] | None) -> bool:
        if not self.enabled:
            return True
        return session_auth is not None and bool(session_auth.get('email'))
