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


def build_ticks_subscribe_request(symbol: str) -> dict[str, str]:
    return {'ticks': symbol}


def build_forget_request(subscription_id: str) -> dict[str, str]:
    return {'forget': subscription_id}


def build_proposal_request(
    symbol: str,
    amount: float,
    contract_type: str = "CALL",
    duration: int = 5,
    duration_unit: str = "m",
    currency: str = "USD",
    basis: str = "stake",
) -> dict[str, str | int | float]:
    return {
        'proposal': 1,
        'symbol': symbol,
        'amount': amount,
        'basis': basis,
        'contract_type': contract_type,
        'currency': currency,
        'duration': duration,
        'duration_unit': duration_unit,
    }


def build_buy_request(proposal_id: str, price: float) -> dict[str, str | float]:
    return {'buy': proposal_id, 'price': price}


def build_proposal_open_contract_request(contract_id: int) -> dict[str, int]:
    return {'proposal_open_contract': 1, 'contract_id': contract_id}


def build_sell_request(contract_id: int) -> dict[str, int]:
    return {'sell': contract_id, 'price': 0}
