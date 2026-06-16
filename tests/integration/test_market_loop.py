from deriv_organismo.workers.market_loop import MarketLoop


def test_market_loop_exposes_single_cycle_runner():
    loop = MarketLoop()

    assert hasattr(loop, "run_cycle")
