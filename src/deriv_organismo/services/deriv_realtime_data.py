from __future__ import annotations

from typing import Any

from deriv_organismo.domain.deriv_account import DerivAccount


class DerivRealtimeDataService:
    def __init__(self, account_service, gateway) -> None:
        self.account_service = account_service
        self.gateway = gateway

    async def build_operations_payload(self, tenant_id: str) -> dict[str, Any]:
        accounts = await self.account_service.list_accounts_by_tenant(tenant_id)
        summaries: list[dict[str, Any]] = []
        operations: list[dict[str, Any]] = []

        for account in accounts:
            token = await self.account_service.get_plaintext_token(tenant_id, account.account_id)
            authorize = await self.gateway.fetch_authorize(token)
            contracts = await self.gateway.fetch_portfolio(token)
            summaries.append(self._build_account_summary(account, authorize))
            for index, contract in enumerate(contracts, start=1):
                operations.append(self._build_operation_row(account, tenant_id, contract, index))

        return {
            'tenant_id': tenant_id,
            'data_source': 'deriv_live',
            'refresh_seconds': 5,
            'generated_at': 'agora',
            'active_count': len(operations),
            'profitable_count': sum(1 for item in operations if item['pnl_float'] > 0),
            'losing_count': sum(1 for item in operations if item['pnl_float'] < 0),
            'monitored_accounts': len(summaries),
            'account_summaries': summaries,
            'operations': operations,
        }

    async def build_performance_payload(self, tenant_id: str) -> dict[str, Any]:
        accounts = await self.account_service.list_accounts_by_tenant(tenant_id)
        rows: list[dict[str, Any]] = []
        for account in accounts:
            token = await self.account_service.get_plaintext_token(tenant_id, account.account_id)
            authorize = await self.gateway.fetch_authorize(token)
            balance_current = float(authorize.get('balance', 0.0))
            rows.append(
                {
                    'account_name': account.name,
                    'login_id': account.login_id,
                    'account_type': account.account_type,
                    'balance_start': balance_current,
                    'balance_current': balance_current,
                    'gains': 0.0,
                    'losses': 0.0,
                    'net_pnl': 0.0,
                    'win_rate': 0.0,
                    'drawdown': 0.0,
                    'trades': 0,
                    'status': 'online',
                }
            )

        total_balance = round(sum(item['balance_current'] for item in rows), 2)
        return {
            'tenant_id': tenant_id,
            'generated_at': 'agora',
            'data_source': 'deriv_live',
            'portfolio': {
                'balance_start': total_balance,
                'balance_current': total_balance,
                'gains': 0.0,
                'losses': 0.0,
                'net_pnl': 0.0,
                'drawdown': 0.0,
            },
            'accounts': rows,
            'daily_series': [],
            'strategy_breakdown': [],
        }

    @staticmethod
    def _build_account_summary(account: DerivAccount, authorize: dict[str, Any]) -> dict[str, Any]:
        is_virtual = bool(authorize.get('is_virtual', account.account_type == 'demo'))
        return {
            'name': account.name,
            'login_id': authorize.get('loginid', account.login_id),
            'mode_label': 'Conta demo' if is_virtual else 'Conta real',
            'connection_status': 'online',
        }

    @staticmethod
    def _build_operation_row(account: DerivAccount, tenant_id: str, contract: dict[str, Any], index: int) -> dict[str, Any]:
        stake = float(contract.get('buy_price', 0.0))
        current_price = float(contract.get('payout', stake))
        pnl_float = round(current_price - stake, 2)
        pnl_pct = round((pnl_float / stake) * 100, 2) if stake else 0.0
        return {
            'operation_id': f"op_live_{contract.get('contract_id', index)}",
            'tenant_id': tenant_id,
            'account_name': account.name,
            'login_id': account.login_id,
            'symbol': contract.get('symbol', '-'),
            'side': contract.get('contract_type', 'UNKNOWN'),
            'strategy': 'deriv_live',
            'status': 'aberta',
            'entry_price': stake,
            'current_price': current_price,
            'stake': stake,
            'pnl_float': pnl_float,
            'pnl_pct': pnl_pct,
            'opened_at': 'live',
            'risk_state': 'estável',
        }
