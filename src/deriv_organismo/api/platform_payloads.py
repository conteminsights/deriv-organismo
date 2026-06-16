from __future__ import annotations

from collections.abc import Iterable

from deriv_organismo.domain.deriv_account import DerivAccount


def seeded_accounts(accounts: Iterable[DerivAccount], tenant_id: str) -> list[dict]:
    rows = [
        {
            'account_id': acc.account_id,
            'tenant_id': acc.tenant_id,
            'login_id': acc.login_id,
            'account_type': acc.account_type,
            'name': acc.name,
            'is_active': acc.is_active,
            'connection_status': 'validada' if acc.is_active else 'pausada',
            'last_validated_at': 'agora',
            'last_sync': 'há 1 min',
            'mode_label': 'Conta real' if acc.account_type == 'real' else 'Conta demo',
        }
        for acc in accounts
    ]

    if rows:
        return rows

    return [
        {
            'account_id': 'preview_demo_01',
            'tenant_id': tenant_id,
            'login_id': 'CR900001',
            'account_type': 'demo',
            'name': 'Conta Demo Primária',
            'is_active': True,
            'connection_status': 'preview',
            'last_validated_at': 'pendente',
            'last_sync': 'aguardando primeira coleta',
            'mode_label': 'Conta demo',
        },
        {
            'account_id': 'preview_real_01',
            'tenant_id': tenant_id,
            'login_id': 'VR900002',
            'account_type': 'real',
            'name': 'Conta Real Observada',
            'is_active': False,
            'connection_status': 'bloqueada até promoção',
            'last_validated_at': 'pendente',
            'last_sync': 'sem sincronização',
            'mode_label': 'Conta real',
        },
    ]


def summarize_accounts(account_rows: list[dict]) -> dict:
    total = len(account_rows)
    active = sum(1 for item in account_rows if item['is_active'])
    demo = sum(1 for item in account_rows if item['account_type'] == 'demo')
    real = sum(1 for item in account_rows if item['account_type'] == 'real')
    validated = sum(1 for item in account_rows if item['connection_status'] in {'validada', 'preview'})
    return {
        'total_accounts': total,
        'active_accounts': active,
        'demo_accounts': demo,
        'real_accounts': real,
        'validated_accounts': validated,
    }


def operations_payload(account_rows: list[dict], tenant_id: str) -> dict:
    rows = account_rows[:3]
    operations = [
        {
            'operation_id': f'op_{index + 1:03d}',
            'tenant_id': tenant_id,
            'account_name': row['name'],
            'login_id': row['login_id'],
            'symbol': symbol,
            'side': side,
            'strategy': strategy,
            'status': status,
            'entry_price': entry,
            'current_price': current,
            'stake': stake,
            'pnl_float': pnl,
            'pnl_pct': pct,
            'opened_at': opened,
            'risk_state': risk_state,
        }
        for index, (row, symbol, side, strategy, status, entry, current, stake, pnl, pct, opened, risk_state) in enumerate(
            [
                (rows[0], 'R_100', 'CALL', 'trend_follow', 'aberta', 128.32, 129.14, 25.0, 3.18, 12.7, '09:12:04', 'estável'),
                (rows[min(1, len(rows)-1)], 'R_75', 'PUT', 'mean_reversion', 'monitorando saída', 94.20, 93.61, 18.0, 1.62, 9.0, '09:14:11', 'atenção'),
                (rows[min(2, len(rows)-1)], 'R_50', 'CALL', 'breakout_guarded', 'hedge passivo', 61.80, 61.32, 12.5, -0.94, -7.5, '09:15:48', 'bloqueio parcial'),
            ]
        )
    ]
    active_count = len(operations)
    profitable = sum(1 for item in operations if item['pnl_float'] > 0)
    losing = sum(1 for item in operations if item['pnl_float'] < 0)
    return {
        'tenant_id': tenant_id,
        'data_source': 'bootstrap_preview',
        'refresh_seconds': 5,
        'generated_at': 'agora',
        'active_count': active_count,
        'profitable_count': profitable,
        'losing_count': losing,
        'monitored_accounts': len({item['login_id'] for item in operations}),
        'account_summaries': [
            {
                'name': row['name'],
                'login_id': row['login_id'],
                'mode_label': row['mode_label'],
                'connection_status': row['connection_status'],
            }
            for row in account_rows
        ],
        'operations': operations,
    }


def performance_payload(account_rows: list[dict], tenant_id: str) -> dict:
    accounts = []
    base_rows = account_rows[:3]
    metrics_seed = [
        (1250.0, 1288.4, 92.1, 53.7, 38.4, 64.0, 4.8, 12),
        (980.0, 1001.8, 48.2, 26.4, 21.8, 58.0, 3.1, 9),
        (1500.0, 1476.3, 35.5, 59.2, -23.7, 44.0, 6.5, 7),
    ]
    for row, (start, current, gains, losses, net, win_rate, drawdown, trades) in zip(base_rows, metrics_seed):
        accounts.append(
            {
                'account_name': row['name'],
                'login_id': row['login_id'],
                'account_type': row['account_type'],
                'balance_start': start,
                'balance_current': current,
                'gains': gains,
                'losses': losses,
                'net_pnl': net,
                'win_rate': win_rate,
                'drawdown': drawdown,
                'trades': trades,
                'status': row['connection_status'],
            }
        )

    portfolio_start = round(sum(item['balance_start'] for item in accounts), 2)
    portfolio_current = round(sum(item['balance_current'] for item in accounts), 2)
    total_gains = round(sum(item['gains'] for item in accounts), 2)
    total_losses = round(sum(item['losses'] for item in accounts), 2)
    total_net = round(sum(item['net_pnl'] for item in accounts), 2)
    max_drawdown = max(item['drawdown'] for item in accounts)

    return {
        'tenant_id': tenant_id,
        'generated_at': 'agora',
        'portfolio': {
            'balance_start': portfolio_start,
            'balance_current': portfolio_current,
            'gains': total_gains,
            'losses': total_losses,
            'net_pnl': total_net,
            'drawdown': max_drawdown,
        },
        'accounts': accounts,
        'daily_series': [
            {'day': 'Seg', 'net_pnl': 12.4},
            {'day': 'Ter', 'net_pnl': -5.1},
            {'day': 'Qua', 'net_pnl': 8.7},
            {'day': 'Qui', 'net_pnl': 11.2},
            {'day': 'Sex', 'net_pnl': total_net},
        ],
        'strategy_breakdown': [
            {'strategy': 'trend_follow', 'share': 42},
            {'strategy': 'mean_reversion', 'share': 33},
            {'strategy': 'breakout_guarded', 'share': 25},
        ],
    }
