# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.cantilever_articulated_arm import (
    CantileverArticulatedArmConfig,
    build_cantilever_arm,
    build_seeded_cantilever_arm,
    config_from_seed,
    resolve_config,
    run_cantilever_arm_tests,
)
from sdk import ArticulationType
from sdk import TestContext as ArticraftTestContext


def _assert_strict_qc_passes(model) -> None:
    ctx = ArticraftTestContext(model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
    report = ctx.report()
    assert report.passed, report.failures


def test_seed_config_is_reproducible() -> None:
    assert config_from_seed(21) == config_from_seed(21)
    assert config_from_seed(21) != config_from_seed(22)


def test_reject_cases_invalid_enums_and_link_count() -> None:
    with pytest.raises(ValueError, match="Unsupported arm_layout"):
        resolve_config(CantileverArticulatedArmConfig(arm_layout="static_beam"))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="link_count"):
        resolve_config(CantileverArticulatedArmConfig(link_count=1))


def test_default_arm_matches_validator() -> None:
    config = CantileverArticulatedArmConfig()
    model = build_cantilever_arm(config)
    report = run_cantilever_arm_tests(model, config)
    assert report.passed, report.failures
    assert model.get_articulation("shoulder_joint").articulation_type == ArticulationType.REVOLUTE
    assert model.get_articulation("elbow_joint").origin.xyz[0] == pytest.approx(
        resolve_config(config).shoulder_link_length
    )
    base_visuals = {visual.name for visual in model.get_part("base_support").visuals}
    shoulder_visuals = {visual.name for visual in model.get_part("shoulder_link").visuals}
    wrist_visuals = {visual.name for visual in model.get_part("wrist_or_end_effector").visuals}
    assert {"anchor_bolt_0", "front_column_rib"}.issubset(base_visuals)
    assert {"shoulder_root_bushed_pin", "shoulder_elbow_cheek_bridge"}.issubset(shoulder_visuals)
    assert {"wrist_contact_bridge", "wrist_bushed_pin", "end_plate"}.issubset(wrist_visuals)


def test_horizontal_and_yaw_constraints() -> None:
    horizontal = CantileverArticulatedArmConfig(arm_layout="horizontal_swing_chain")
    horizontal_model = build_cantilever_arm(horizontal)
    assert run_cantilever_arm_tests(horizontal_model, horizontal).passed
    assert horizontal_model.get_articulation("shoulder_joint").axis == (0.0, 0.0, 1.0)

    yaw = CantileverArticulatedArmConfig(
        arm_layout="pedestal_yaw_pitch_chain",
        base_mount_style="column_turret",
    )
    yaw_model = build_cantilever_arm(yaw)
    assert run_cantilever_arm_tests(yaw_model, yaw).passed
    assert yaw_model.get_articulation("base_yaw").axis == (0.0, 0.0, 1.0)


def test_diversity_parameters_are_observable() -> None:
    configs = [config_from_seed(seed) for seed in range(80)]
    assert len({cfg.arm_layout for cfg in configs}) == 4
    assert len({cfg.base_mount_style for cfg in configs}) == 4
    assert len({cfg.link_profile for cfg in configs}) == 4
    assert len({cfg.wrist_style for cfg in configs}) == 4


def test_build_seeded_cantilever_arm_runs_template_tests() -> None:
    model = build_seeded_cantilever_arm(9)
    report = run_cantilever_arm_tests(model, config_from_seed(9))
    assert report.passed, report.failures


def test_representative_seeds_pass_strict_qc() -> None:
    for seed in (0, 1, 2, 6):
        _assert_strict_qc_passes(build_cantilever_arm(config_from_seed(seed)))
