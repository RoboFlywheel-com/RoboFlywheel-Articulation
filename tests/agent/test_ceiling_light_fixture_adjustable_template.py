# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.ceiling_light_fixture_adjustable import (
    MATERIAL_PALETTES,
    CeilingLightFixtureConfig,
    build_ceiling_light,
    config_from_seed,
    resolve_config,
    run_ceiling_light_tests,
)
from sdk import ArticulationType
from sdk import TestContext as ArticraftTestContext


def _visual_names(model, part_name: str) -> set[str]:
    return {visual.name for visual in model.get_part(part_name).visuals if visual.name}


def _assert_strict_qc_passes(model) -> None:
    ctx = ArticraftTestContext(model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
    report = ctx.report()
    assert report.passed, report.failures


def test_adjustable_fixture_variants_pass_template_tests_and_strict_qc() -> None:
    configs = [
        CeilingLightFixtureConfig(
            fixture_layout="track_spot",
            mount_style="rectangular_track",
            shade_style="cylindrical_spot",
            head_count=4,
            track_length=1.2,
        ),
        CeilingLightFixtureConfig(
            fixture_layout="branching_arm",
            mount_style="round_canopy",
            shade_style="bowl",
            arm_count=4,
        ),
        CeilingLightFixtureConfig(
            fixture_layout="pull_down_pendant",
            mount_style="canopy_cup",
            shade_style="drum",
            service_latch_style="side_button",
        ),
    ]

    for config in configs:
        model = build_ceiling_light(config)
        report = run_ceiling_light_tests(model, config)
        assert report.passed, report.failures
        _assert_strict_qc_passes(model)

    track_model = build_ceiling_light(configs[0])
    assert "round_junction_canopy" in _visual_names(track_model, "mount")
    assert "track_mounting_screw_0" in _visual_names(track_model, "mount")
    assert "rail_capture_plate" in _visual_names(track_model, "carriage_0")
    assert "left_pivot_screw" in _visual_names(track_model, "swivel_yoke_0")
    assert "cooling_fin_0" in _visual_names(track_model, "lamp_head_0")
    assert "rear_toggle_switch" in _visual_names(track_model, "lamp_head_0")

    branch_model = build_ceiling_light(configs[1])
    assert "canopy_mounting_screw_0" in _visual_names(branch_model, "mount")
    assert "tip_yoke_bridge" in _visual_names(branch_model, "arm_0")
    assert "shade_bezel_ring" in _visual_names(branch_model, "shade_0")

    pendant_model = build_ceiling_light(configs[2])
    assert "knurled_cord_grip" in _visual_names(pendant_model, "mount")
    assert "fixed_cord_guide_sleeve" in _visual_names(pendant_model, "mount")
    assert "fixed_hanging_cord" in _visual_names(pendant_model, "mount")
    assert "pull_chain_switch_boss" in _visual_names(pendant_model, "shade")
    assert "bead_chain" in _visual_names(pendant_model, "pull_chain")
    assert all(j.name != "cord_slide" for j in pendant_model.articulations)
    assert pendant_model.get_articulation("shade_spin").parent == "mount"
    assert (
        pendant_model.get_articulation("pull_chain_swing").articulation_type
        == ArticulationType.CONTINUOUS
    )


def test_track_spot_clamps_dense_heads_and_keeps_motion_contract() -> None:
    config = CeilingLightFixtureConfig(
        fixture_layout="track_spot",
        mount_style="rectangular_track",
        shade_style="cylindrical_spot",
        head_profile="deep_barrel",
        head_count=6,
        track_length=0.7,
    )
    resolved = resolve_config(config)
    model = build_ceiling_light(config)

    assert resolved.head_count == 2
    assert len([j for j in model.articulations if j.name.startswith("rail_slide_")]) == 2
    assert len([j for j in model.articulations if j.name.startswith("carriage_swivel_")]) == 2
    assert len([j for j in model.articulations if j.name.startswith("head_tilt_")]) == 2
    assert model.get_articulation("rail_slide_0").articulation_type == ArticulationType.PRISMATIC
    swivel = model.get_articulation("carriage_swivel_0")
    assert swivel.articulation_type == ArticulationType.REVOLUTE
    assert swivel.motion_limits is not None
    assert swivel.motion_limits.lower == -swivel.motion_limits.upper
    assert 0.0 < swivel.motion_limits.upper < 1.0
    assert model.get_articulation("head_tilt_0").articulation_type == ArticulationType.REVOLUTE
    _assert_strict_qc_passes(model)


def test_material_palette_is_applied_to_model_materials() -> None:
    brass = build_ceiling_light(CeilingLightFixtureConfig(material_style="warm_brass"))
    black = build_ceiling_light(CeilingLightFixtureConfig(material_style="matte_black"))

    brass_materials = {material.name: material.rgba for material in brass.materials}
    black_materials = {material.name: material.rgba for material in black.materials}

    assert brass_materials["ceiling_light_body"] == MATERIAL_PALETTES["warm_brass"]["body"]
    assert black_materials["ceiling_light_body"] == MATERIAL_PALETTES["matte_black"]["body"]
    assert brass_materials["ceiling_light_body"] != black_materials["ceiling_light_body"]


def test_seed_zero_to_eleven_pass_strict_qc() -> None:
    for seed in range(12):
        _assert_strict_qc_passes(build_ceiling_light(config_from_seed(seed)))
