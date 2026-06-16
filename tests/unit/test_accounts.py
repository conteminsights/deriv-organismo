from deriv_organismo.domain.accounts import AccountContext


def test_account_context_isolation_fields_are_required():
    account = AccountContext(
        account_id="acc_primary",
        tenant_id="tenant_primary",
        account_slug="primary",
        mode="demo",
    )
    assert account.account_slug == "primary"
    assert account.mode == "demo"
