from typing import Literal

from pydantic import BaseModel


class AccountContext(BaseModel):
    account_id: str
    tenant_id: str
    account_slug: str
    mode: Literal["demo", "real"]
    deriv_login_id: str | None = None
