def build_ping_request() -> dict[str, int]:
    return {'ping': 1}


def build_time_request() -> dict[str, int]:
    return {'time': 1}


def build_authorize_request(token: str) -> dict[str, str]:
    return {'authorize': token}


def build_portfolio_request() -> dict[str, int]:
    return {'portfolio': 1}


def build_balance_request() -> dict[str, int]:
    return {'balance': 1}


def build_active_symbols_request(product_type: str = 'basic') -> dict[str, str]:
    return {'active_symbols': product_type}


def build_ticks_history_request(
    *,
    symbol: str,
    count: int,
    style: str = 'candles',
    granularity: int = 300,
) -> dict[str, str | int]:
    return {
        'ticks_history': symbol,
        'count': count,
        'style': style,
        'granularity': granularity,
    }
