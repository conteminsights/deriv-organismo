from deriv_organismo.domain.symbols import V1_SYMBOLS


def test_v1_symbols_count_stays_between_three_and_five():
    assert 3 <= len(V1_SYMBOLS) <= 5
