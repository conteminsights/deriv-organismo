from alembic import op
import sqlalchemy as sa

revision = "20260615_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("account_slug", sa.String(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("deriv_login_id", sa.String(), nullable=True),
    )
    op.create_index("ix_accounts_tenant_id", "accounts", ["tenant_id"])
    op.create_unique_constraint("uq_accounts_account_slug", "accounts", ["account_slug"])

    for table_name in [
        "market_candles",
        "specialists",
        "specialist_variants",
        "risk_events",
        "learning_events",
    ]:
        op.create_table(
            table_name,
            sa.Column("id", sa.String(), primary_key=True),
            sa.Column("account_id", sa.String(), nullable=False),
        )
        op.create_index(f"ix_{table_name}_account_id", table_name, ["account_id"])

    op.create_table(
        "trade_decisions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("account_id", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("timeframe", sa.String(), nullable=False),
        sa.Column("specialist_key", sa.String(), nullable=False),
        sa.Column("variant_key", sa.String(), nullable=False),
        sa.Column("regime", sa.String(), nullable=False),
        sa.Column("decision", sa.String(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("risk_status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_trade_decisions_account_id", "trade_decisions", ["account_id"])


def downgrade() -> None:
    op.drop_index("ix_trade_decisions_account_id", table_name="trade_decisions")
    op.drop_table("trade_decisions")

    for table_name in [
        "learning_events",
        "risk_events",
        "specialist_variants",
        "specialists",
        "market_candles",
    ]:
        op.drop_index(f"ix_{table_name}_account_id", table_name=table_name)
        op.drop_table(table_name)

    op.drop_constraint("uq_accounts_account_slug", "accounts", type_="unique")
    op.drop_index("ix_accounts_tenant_id", table_name="accounts")
    op.drop_table("accounts")
