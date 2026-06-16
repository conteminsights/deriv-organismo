import pytest

from deriv_organismo.domain.accounts import AccountContext
from deriv_organismo.services.execution import ExecutionService, RealExecutionBlocked


def test_real_account_cannot_execute_unpromoted_variant():
    service = ExecutionService()
    account = AccountContext(
        account_id="acc_real",
        tenant_id="tenant_primary",
        account_slug="primary-real",
        mode="real",
    )

    with pytest.raises(RealExecutionBlocked):
        service.ensure_real_can_execute(is_promoted=False, account=account)


def test_real_account_requires_human_approval_when_flagged():
    service = ExecutionService()
    account = AccountContext(
        account_id="acc_real",
        tenant_id="tenant_primary",
        account_slug="primary-real",
        mode="real",
    )

    with pytest.raises(RealExecutionBlocked):
        service.ensure_real_can_execute(
            is_promoted=True,
            account=account,
            requires_human_approval=True,
            human_approval=False,
        )
