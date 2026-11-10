# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.coaxial_rotary_stack import (
    CoaxialRotaryStackConfig,
    build_coaxial_rotary_stack,
    build_seeded_coaxial_rotary_stack,
    config_from_seed,
    resolve_config,
    run_coaxial_rotary_stack_tests,
)
from sdk import TestContext as ArticraftTestContext


def _assert_strict_qc_passes(model) -> None:
    ctx = ArticraftTestContext(model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
    report = ctx.report()
    assert report.passed, report.failures


def test_seed_reproducibility() -> None:
    assert config_from_seed(21) == config_from_seed(21)
    assert config_from_seed(21) != config_from_seed(22)
    assert build_seeded_coaxial_rotary_stack(21).name == "seeded_coaxial_rotary_stack_21"


def test_seeded_configs_stay_on_upright_spindle_family() -> None:
    configs = [config_from_seed(seed) for seed in range(40)]
    assert {cfg.support_layout for cfg in configs} == {
        "upright_spindle",
        "saddle_body",
        "tower_post",
    }
    assert {cfg.stage_body_style for cfg in configs} <= {
        "solid_disk",
        "annular_ring",
        "spoked_ring",
    }
    assert {cfg.stage_radius_profile for cfg in configs} <= {"descending", "nested_equal_outer"}
    assert {cfg.bearing_style for cfg in configs} <= {
        "collar_stack",
        "thrust_washer",
        "bearing_land",
    }
    assert "drive_lugs" not in {cfg.index_marker_style for cfg in configs}


def test_validator_for_stable_core() -> None:
    configs = (
        CoaxialRotaryStackConfig(
            stage_count=2, support_layout="upright_spindle", stage_body_style="solid_disk"
        ),
        CoaxialRotaryStackConfig(
            stage_count=4,
            support_layout="upright_spindle",
            stage_body_style="annular_ring",
            rotation_range_mode="continuous",
        ),
        CoaxialRotaryStackConfig(
            stage_count=3,
            support_layout="saddle_body",
            stage_body_style="spoked_ring",
        ),
        CoaxialRotaryStackConfig(
            stage_count=3,
            support_layout="tower_post",
            stage_body_style="annular_ring",
        ),
    )
    for config in configs:
        model = build_coaxial_rotary_stack(config)
        report = run_coaxial_rotary_stack_tests(model, config)
        assert report.passed, report.failures


def test_legacy_complex_variants_are_coerced_to_stable_stack() -> None:
    resolved = resolve_config(
        CoaxialRotaryStackConfig(
            support_layout="underslung",
            stage_body_style="spoked_ring",
            stage_radius_profile="underslung_descending",
            bearing_style="hanger_collar",
            index_marker_style="drive_lugs",
        )
    )

    assert resolved.support_layout == "upright_spindle"
    assert resolved.stage_body_style == "spoked_ring"
    assert resolved.stage_radius_profile == "descending"
    assert resolved.bearing_style == "collar_stack"
    assert resolved.index_marker_style == "pointer_tabs"


def test_constraints_and_reject_cases() -> None:
    with pytest.raises(ValueError, match="stage_count"):
        resolve_config(CoaxialRotaryStackConfig(stage_count=1))
    with pytest.raises(ValueError, match="base_radius"):
        resolve_config(CoaxialRotaryStackConfig(base_radius=0.1))
    with pytest.raises(ValueError, match="stage_gap"):
        resolve_config(CoaxialRotaryStackConfig(stage_gap=0.2))


def test_seeded_variants_pass_strict_qc() -> None:
    for seed in (*range(3), 9):
        _assert_strict_qc_passes(build_coaxial_rotary_stack(config_from_seed(seed)))
