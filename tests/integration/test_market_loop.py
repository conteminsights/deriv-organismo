from deriv_organismo.workers.market_loop import ContinuousMarketWorker


def test_continuous_market_worker_exposes_start_stop():
    worker = ContinuousMarketWorker(
        app_id='1089',
        token='fake',
        account=None,  # type: ignore[arg-type]
    )
    assert hasattr(worker, 'start')
    assert hasattr(worker, 'stop')
    assert hasattr(worker, 'summary')
    assert not worker._running
