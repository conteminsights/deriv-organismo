from deriv_organismo.services.lab import VariantLab


def test_variant_lab_clones_specialist_with_parent_reference():
    lab = VariantLab()

    variant = lab.clone_variant(
        specialist_key="trend_follow",
        parent_variant_key="trend_follow_v1",
    )

    assert variant.parent_variant_key == "trend_follow_v1"


def test_variant_lab_clones_are_quarantined_by_default():
    lab = VariantLab()

    variant = lab.clone_variant(
        specialist_key="mean_reversion",
        parent_variant_key="mean_reversion_v1",
    )

    assert variant.quarantined is True
