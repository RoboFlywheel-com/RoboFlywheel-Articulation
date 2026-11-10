# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math

import pytest

from agent.templates.box_fan_with_control_knob import (
    BoxFanWithControlKnobConfig,
    build_box_fan,
    build_seeded_box_fan,
    config_from_seed,
    resolve_config,
    run_box_fan_tests,
)
from sdk import ArticulationType
from sdk import TestContext as ArticraftTestContext


def test_resolve_rejects_invalid_rotor_count() -> None:
    with pytest.raises(ValueError, match="rotor_count"):
        resolve_config(BoxFanWithControlKnobConfig(rotor_count=3))


def test_blade_count_supports_three_to_eight() -> None:
    assert resolve_config(BoxFanWithControlKnobConfig(blade_count=3)).blade_count == 3
    assert resolve_config(BoxFanWithControlKnobConfig(blade_count=8)).blade_count == 8
    with pytest.raises(ValueError, match=r"\[3, 8\]"):
        resolve_config(BoxFanWithControlKnobConfig(blade_count=9))


def _assert_strict_seed_qc(model) -> None:
    ctx = ArticraftTestContext(model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
    report = ctx.report()
    assert report.passed, report.failures


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_seeded_box_fans_pass_strict_qc(seed: int) -> None:
    _assert_strict_seed_qc(build_seeded_box_fan(seed))


def test_wide_twin_requires_two_rotors() -> None:
    with pytest.raises(ValueError, match="wide_twin"):
        resolve_config(BoxFanWithControlKnobConfig(housing_profile="wide_twin", rotor_count=1))


def test_builds_required_identity_and_joints() -> None:
    config = BoxFanWithControlKnobConfig()
    model = build_box_fan(config)
    report = run_box_fan_tests(model, config)

    assert report.passed, report.failures
    assert model.get_part("housing") is not None
    assert model.get_part("speed_knob") is not None
    assert model.get_articulation("rotor_spin_0").articulation_type == ArticulationType.CONTINUOUS
    assert model.get_articulation("speed_knob_turn").articulation_type == ArticulationType.REVOLUTE


def test_twin_rotor_constraints() -> None:
    config = BoxFanWithControlKnobConfig(housing_profile="wide_twin", rotor_count=2)
    model = build_box_fan(config)

    assert model.get_articulation("rotor_spin_0").axis == (0.0, 1.0, 0.0)
    assert model.get_articulation("rotor_spin_1").axis == (0.0, 1.0, 0.0)
    assert len([p for p in model.parts if p.name.startswith("rotor_")]) == 2


def test_knob_mount_sets_axis_and_origin() -> None:
    top = build_box_fan(BoxFanWithControlKnobConfig(knob_mount="top_pod"))
    front = build_box_fan(BoxFanWithControlKnobConfig(knob_mount="front_corner"))

    assert top.get_articulation("speed_knob_turn").axis == (0.0, 0.0, 1.0)
    assert front.get_articulation("speed_knob_turn").axis == (0.0, 1.0, 0.0)
    assert top.get_articulation("speed_knob_turn").origin.xyz[2] > 0.2


def test_optional_support_and_panels_add_spec_joints() -> None:
    pedestal = build_box_fan(BoxFanWithControlKnobConfig(support_style="pedestal_column"))
    shuttered = build_box_fan(BoxFanWithControlKnobConfig(panel_layout="four_shutters"))

    assert (
        pedestal.get_articulation("column_extension").articulation_type
        == ArticulationType.PRISMATIC
    )
    assert pedestal.get_articulation("column_extension").axis == (0.0, 0.0, 1.0)
    panel_joints = [j for j in shuttered.articulations if j.name.startswith("panel_hinge_")]
    assert panel_joints
    assert all(j.articulation_type == ArticulationType.REVOLUTE for j in panel_joints)


def test_diversity_parameters_change_geometry() -> None:
    ribbed = build_box_fan(BoxFanWithControlKnobConfig(knob_style="ribbed_bakelite"))
    plain = build_box_fan(BoxFanWithControlKnobConfig(knob_style="plain_cylindrical"))
    ribbed_names = {v.name for v in ribbed.get_part("speed_knob").visuals if v.name}
    plain_names = {v.name for v in plain.get_part("speed_knob").visuals if v.name}

    # KnobGeometry path (cadquery available): produces "knob_mesh" with different grip styles.
    # Box-fallback path: produces "knob_rib_*" for ribbed, absent for plain.
    assert len(ribbed_names) >= 1
    assert len(plain_names) >= 1
    uses_knob_mesh = "knob_mesh" in ribbed_names
    has_ribs = any(name.startswith("knob_rib_") for name in ribbed_names)
    assert has_ribs or uses_knob_mesh, f"ribbed knob built neither ribs nor mesh: {ribbed_names}"
    assert not any(name.startswith("knob_rib_") for name in plain_names)


def test_blade_parameters_change_rotor_visuals() -> None:
    model = build_box_fan(
        BoxFanWithControlKnobConfig(
            blade_count=8,
            blade_shape="broad_rotor_geometry",
            blade_pitch_deg=9.0,
            blade_inner_radius_ratio=0.22,
            blade_outer_radius_ratio=0.94,
            blade_chord_ratio=0.17,
            blade_sweep_deg=15.0,
        )
    )
    rotor_visual_names = {
        visual.name for visual in model.get_part("rotor_0").visuals if visual.name
    }

    # FanRotorGeometry path (cadquery): single "fan_rotor_mesh_0" visual.
    # Box-fallback path: one "blade_0_*" + one "blade_swept_tip_0_*" per blade.
    if "fan_rotor_mesh_0" in rotor_visual_names:
        assert len(rotor_visual_names) >= 1
    else:
        assert sum(1 for name in rotor_visual_names if name.startswith("blade_0_")) == 8
        assert sum(1 for name in rotor_visual_names if name.startswith("blade_swept_tip_0_")) == 8


def test_joint_metadata_includes_spec_fields() -> None:
    model = build_box_fan(BoxFanWithControlKnobConfig(panel_layout="side_expansion_pair"))

    for joint in model.articulations:
        if joint.articulation_type != ArticulationType.FIXED:
            assert {"type", "axis", "origin", "range"}.issubset(joint.meta)


@pytest.mark.parametrize(
    "layout",
    [
        "classic_box",
        "window_twin",
        "industrial_exhaust",
        "pedestal_box",
        "shutter_exhaust",
        "portable_handle",
    ],
)
def test_layout_families_have_expected_joints_and_pass_qc(layout: str) -> None:
    config = BoxFanWithControlKnobConfig(layout=layout)
    resolved = resolve_config(config)
    model = build_box_fan(config)
    report = run_box_fan_tests(model, config)

    assert report.passed, report.failures
    _assert_strict_seed_qc(model)
    if layout == "window_twin":
        assert resolved.rotor_count == 2
        slide_joints = [j for j in model.articulations if j.name.endswith("_slide")]
        assert len(slide_joints) >= 2, (
            f"window_twin expects ≥2 prismatic slide joints, got {slide_joints}"
        )
        assert all(j.articulation_type == ArticulationType.PRISMATIC for j in slide_joints)
    if layout == "pedestal_box":
        assert (
            model.get_articulation("column_extension").articulation_type
            == ArticulationType.PRISMATIC
        )
    if layout == "shutter_exhaust":
        assert len([j for j in model.articulations if j.name.startswith("panel_hinge_")]) == 4
    if layout == "portable_handle":
        assert (
            model.get_articulation("carry_handle_fold").articulation_type
            == ArticulationType.REVOLUTE
        )


def test_seed_config_is_reproducible_and_varied() -> None:
    assert config_from_seed(8) == config_from_seed(8)
    assert config_from_seed(8) != config_from_seed(9)
    configs = [config_from_seed(seed) for seed in range(30)]
    assert len({config.layout for config in configs}) >= 4
    assert len({config.housing_profile for config in configs}) >= 2
    assert len({config.knob_style for config in configs}) >= 2


def test_run_box_fan_tests_passes_for_variants() -> None:
    configs = [
        BoxFanWithControlKnobConfig(),
        BoxFanWithControlKnobConfig(housing_profile="wide_twin", rotor_count=2),
        BoxFanWithControlKnobConfig(
            support_style="u_tilt_stand", panel_layout="side_expansion_pair"
        ),
        BoxFanWithControlKnobConfig(layout="portable_handle"),
    ]
    for config in configs:
        report = run_box_fan_tests(build_box_fan(config), config)
        assert report.passed, report.failures


def test_resolved_knob_range_maps_degrees_to_radians() -> None:
    resolved = resolve_config(BoxFanWithControlKnobConfig(knob_range_deg=180.0))

    assert resolved.knob_range_rad == pytest.approx(math.pi)
