# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.crane_tower import (
    CraneTowerConfig,
    build_crane_tower,
    build_seeded_crane_tower,
    config_from_seed,
    resolve_config,
    run_crane_tower_tests,
)
from sdk import ArticulationType
from sdk import TestContext as ArticraftTestContext


def test_resolve_rejects_invalid_mast_height() -> None:
    with pytest.raises(ValueError, match="mast_height"):
        resolve_config(CraneTowerConfig(mast_height=4.0))


def test_supported_tower_variants_and_legacy_coercion() -> None:
    for variant in ("hammerhead", "luffing_jib", "derrick_pedestal"):
        resolved = resolve_config(CraneTowerConfig(crane_variant=variant))
        assert resolved.crane_variant == variant
        assert resolved.mast_profile in {"square_lattice", "round_pedestal"}
        assert resolved.base_style in {"fixed_foundation", "pedestal_base", "pedestal_flange"}
        assert resolved.extension_travel == 0.0

    for variant in ("self_erecting", "knuckle_boom", "gantry_bridge"):
        resolved = resolve_config(CraneTowerConfig(crane_variant=variant))
        assert resolved.crane_variant == "hammerhead"
        assert resolved.mast_profile == "square_lattice"
        assert resolved.base_style == "fixed_foundation"
        assert resolved.jib_layout == "horizontal_jib_counterjib"
        assert resolved.trolley_mode == "jib_trolley"
        assert resolved.extension_travel == 0.0


def test_continuous_slew_uses_unbounded_motion_limits() -> None:
    model = build_crane_tower(CraneTowerConfig(slew_range="continuous"))
    slew = model.get_articulation("slew_joint")

    assert slew.articulation_type == ArticulationType.CONTINUOUS
    assert slew.motion_limits.lower is None
    assert slew.motion_limits.upper is None
    assert slew.meta["range"] == "continuous"


def test_lattice_mast_and_horizontal_jib_include_diagonal_bracing() -> None:
    model = build_crane_tower(CraneTowerConfig(crane_variant="hammerhead"))
    base_visuals = {visual.name for visual in model.get_part("base").visuals}
    upper_visuals = {visual.name for visual in model.get_part("upperworks").visuals}

    assert any(name.startswith("mast_diag_front") for name in base_visuals)
    assert any(name.startswith("jib_left_diag") for name in upper_visuals)


def test_seed_config_is_reproducible_and_hammerhead_only() -> None:
    assert config_from_seed(8) == config_from_seed(8)
    assert config_from_seed(8) != config_from_seed(9)
    assert {config_from_seed(seed).crane_variant for seed in range(100)} == {
        "hammerhead",
        "luffing_jib",
        "derrick_pedestal",
    }


def test_run_crane_tower_tests_passes() -> None:
    config = CraneTowerConfig()
    report = run_crane_tower_tests(build_crane_tower(config), config)

    assert report.passed, report.failures


def test_seed_0_to_2_pass_strict_contact_qc() -> None:
    for seed in range(3):
        ctx = ArticraftTestContext(build_seeded_crane_tower(seed))
        ctx.check_model_valid()
        ctx.fail_if_isolated_parts()
        ctx.fail_if_parts_overlap_in_current_pose(
            overlap_tol=0.003,
            overlap_volume_tol=1e-7,
        )
        report = ctx.report()
        assert report.passed, report.failures
