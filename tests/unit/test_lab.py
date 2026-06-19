from deriv_organismo.services.lab import VariantLab


def test_variant_lab_creates_baselines_on_init():
    lab = VariantLab()

    baselines = lab.get_active_variants()
    assert len(baselines) >= 3  # trend_follow, mean_reversion, breakout

    trend = lab.get_or_create_variant("trend_follow_baseline")
    assert trend.specialist_key == "trend_follow"
    assert trend.quarantined is False
    assert trend.generation == 0
    assert "fast_window" in trend.parameters


def test_variant_lab_records_outcome_and_updates_win_rate():
    lab = VariantLab()

    lab.record_outcome("trend_follow_baseline", "won", 1.0)
    lab.record_outcome("trend_follow_baseline", "lost", -0.5)

    variant = lab.get_or_create_variant("trend_follow_baseline")
    assert variant.total_trades == 2
    assert variant.wins == 1
    assert variant.losses == 1
    assert variant.win_rate == 0.5


def test_variant_lab_unquarantines_after_3_trades():
    lab = VariantLab()

    v = lab.get_or_create_variant("mean_reversion_baseline")
    assert v.quarantined is False  # baselines start un-quarantined

    # Create a new variant that starts quarantined and un-quarantine it
    kv = "mean_reversion_test_001"
    from deriv_organismo.services.lab import StrategyVariant
    lab._variants[kv] = StrategyVariant(
        variant_key=kv, specialist_key="mean_reversion", quarantined=True,
    )

    for _ in range(3):
        lab.record_outcome(kv, "won", 1.0)

    v2 = lab.get_or_create_variant(kv)
    assert v2.quarantined is False
    assert v2.total_trades == 3


def test_variant_lab_creates_specialist_instance_with_custom_params():
    lab = VariantLab()

    specialist = lab.get_specialist_instance("trend_follow_baseline")
    assert specialist.specialist_key == "trend_follow"
    assert hasattr(specialist, "fast_window")
    assert specialist.fast_window == 3  # baseline value
