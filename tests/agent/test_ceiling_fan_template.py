# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.ceiling_fan import (
    CeilingFanConfig,
    build_ceiling_fan,
    build_seeded_ceiling_fan,
    config_from_seed,
    resolve_config,
    run_ceiling_fan_tests,
)
from sdk import ArticulationType
from sdk import TestContext as ArticraftTestContext


def _visual_names(model, part_name: str) -> set[str]:
    return {visual.name for visual in model.get_part(part_name).visuals if visual.name}


def _assert_strict_seed_qc(model) -> None:
    ctx = ArticraftTestContext(model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
    report = ctx.report()
    assert report.passed, report.failures


def test_seed_config_is_reproducible() -> None:
    assert config_from_seed(41) == config_from_seed(41)
    assert config_from_seed(41) != config_from_seed(42)


@pytest.mark.parametrize("seed", [0, 1, 2, 4, 7, 11, 20, 28, 32, 47, 88, 135])
def test_seeded_ceiling_fans_pass_strict_qc(seed: int) -> None:
    _assert_strict_seed_qc(build_seeded_ceiling_fan(seed))


def test_reject_cases_invalid_enums_and_blade_count() -> None:
    with pytest.raises(ValueError, match="Unsupported fan_layout"):
        resolve_config(CeilingFanConfig(fan_layout="desk_fan"))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="blade_count"):
        resolve_config(CeilingFanConfig(blade_count=2))


def test_five_star_style_fan_matches_validator() -> None:
    config = CeilingFanConfig(
        fan_layout="rod_canopy",
        blade_count=5,
        blade_shape="tapered_paddle",
        housing_style="vented_band",
        mount_style="bell_canopy",
        light_kit_style="finial",
    )
    model = build_ceiling_fan(config)
    report = run_ceiling_fan_tests(model, config)
    assert report.passed, report.failures
    assert model.get_articulation("fan_spin").articulation_type == ArticulationType.CONTINUOUS
    assert model.get_articulation("fan_spin").axis == (0.0, 0.0, 1.0)
    assert "bell_canopy" in _visual_names(model, "ceiling_mount")
    assert "vent_window_0" in _visual_names(model, "motor_housing")
    assert "rotor_hub" in _visual_names(model, "blade_assembly")
    assert "blade_0_root_clamp" in _visual_names(model, "blade_assembly")
    assert "blade_surface_0" in _visual_names(model, "blade_assembly")
    assert "decorative_bottom_finial" in _visual_names(model, "blade_assembly")


def test_legacy_configs_coerce_to_new_five_star_families() -> None:
    assert (
        resolve_config(CeilingFanConfig(fan_layout="standard_downrod")).fan_layout == "rod_canopy"
    )  # type: ignore[arg-type]
    assert (
        resolve_config(CeilingFanConfig(fan_layout="hugger_low_profile")).fan_layout
        == "flush_plate"
    )  # type: ignore[arg-type]
    assert (
        resolve_config(CeilingFanConfig(blade_shape="curved_airfoil")).blade_shape
        == "rounded_airfoil"
    )  # type: ignore[arg-type]


def test_seeded_diversity_stays_inside_new_families() -> None:
    configs = [config_from_seed(seed) for seed in range(120)]
    assert {cfg.fan_layout for cfg in configs} <= {
        "rod_canopy",
        "flush_plate",
        "showroom_downrod",
    }
    assert {cfg.blade_variant for cfg in configs} == {"rigid_fixed"}
    assert {cfg.mount_style for cfg in configs} <= {
        "bell_canopy",
        "flat_plate",
        "wide_ceiling_plate",
    }
    assert {cfg.blade_shape for cfg in configs} <= {
        "straight_plank",
        "tapered_paddle",
        "rounded_airfoil",
        "long_rectangular",
    }
    assert {cfg.housing_style for cfg in configs} <= {
        "smooth_drum",
        "tiered_drum",
        "vented_band",
        "rounded_stack",
    }


def test_build_seeded_ceiling_fan_runs_template_tests() -> None:
    model = build_seeded_ceiling_fan(17)
    report = run_ceiling_fan_tests(model, config_from_seed(17))
    assert report.passed, report.failures
