# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import pytest

from agent.templates.louvered_shutter_assembly import (
    LouveredShutterConfig,
    build_louvered_shutter,
    build_seeded_louvered_shutter,
    config_from_seed,
    resolve_config,
    run_louvered_shutter_tests,
)
from sdk import ArticulationType
from sdk._core.v0.testing import TestContext as SDKTestContext


def _assert_template_qc_passes(config: LouveredShutterConfig) -> None:
    model = build_louvered_shutter(config)
    report = run_louvered_shutter_tests(model, config)
    assert report.passed, report.failures


def test_template_line_floor() -> None:
    template_path = Path("agent/templates/louvered_shutter_assembly.py")
    assert len(template_path.read_text().splitlines()) >= 1000


def test_seed_reproducibility() -> None:
    assert config_from_seed(9) == config_from_seed(9)
    assert config_from_seed(9) != config_from_seed(10)
    assert build_seeded_louvered_shutter(9).name == "seeded_louvered_shutter_assembly_9"


def test_default_seed_domain_stays_plantation_core() -> None:
    layouts = {config_from_seed(seed).panel_layout for seed in range(60)}
    assert layouts <= {"single_panel", "double_plantation", "fixed_frame_only"}


def test_double_plantation_derives_two_leaves_and_slats() -> None:
    config = LouveredShutterConfig(panel_layout="double_plantation", slat_count=10)
    resolved = resolve_config(config)
    model = build_louvered_shutter(config)
    slat_joints = [joint for joint in model.articulations if joint.name.startswith("louver_pivot_")]
    panel_hinges = [joint for joint in model.articulations if joint.name.startswith("panel_hinge_")]

    assert resolved.leaf_count == 2
    assert len(slat_joints) == resolved.slat_count * 2
    assert len(panel_hinges) == 2


def test_louver_pivots_use_slat_long_axis() -> None:
    config = LouveredShutterConfig(panel_layout="single_panel", slat_count=8)
    model = build_louvered_shutter(config)
    slat_joints = [joint for joint in model.articulations if joint.name.startswith("louver_pivot_")]

    assert slat_joints
    assert all(joint.articulation_type == ArticulationType.REVOLUTE for joint in slat_joints)
    assert all(tuple(joint.axis) == (1.0, 0.0, 0.0) for joint in slat_joints)


def test_tilt_rod_slide_is_vertical_when_enabled() -> None:
    config = LouveredShutterConfig(panel_layout="single_panel", control_style="tilt_rod_mimic")
    model = build_louvered_shutter(config)
    rod = model.get_articulation("tilt_rod_slide_0")

    assert rod.articulation_type == ArticulationType.PRISMATIC
    assert tuple(rod.axis) == (0.0, 0.0, 1.0)


def test_review_gated_layout_downgrades_in_default_domain() -> None:
    resolved = resolve_config(
        LouveredShutterConfig(
            panel_layout="bifold_pair",
            seed_domain="plantation_louver_core",
        )
    )
    assert resolved.panel_layout == "double_plantation"


def test_fixed_frame_has_no_panel_hinges() -> None:
    model = build_louvered_shutter(LouveredShutterConfig(panel_layout="fixed_frame_only"))
    panel_hinges = [joint for joint in model.articulations if joint.name.startswith("panel_hinge_")]
    assert panel_hinges == []


@pytest.mark.parametrize("seed", range(12))
def test_seeded_configs_pass_template_qc(seed: int) -> None:
    _assert_template_qc_passes(config_from_seed(seed))


def test_strict_current_pose_overlap_seed_zero() -> None:
    model = build_louvered_shutter(config_from_seed(0))
    ctx = SDKTestContext(model)
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
    assert ctx.report().passed
