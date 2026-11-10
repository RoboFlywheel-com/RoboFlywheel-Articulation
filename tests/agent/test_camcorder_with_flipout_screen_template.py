# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.camcorder_with_flipout_screen import (
    CamcorderWithFlipoutScreenConfig,
    build_camcorder,
    build_seeded_camcorder,
    config_from_seed,
    resolve_config,
    run_camcorder_tests,
)
from sdk import ArticulationType
from sdk import TestContext as ArticraftTestContext


def test_resolve_rejects_invalid_screen_layout() -> None:
    with pytest.raises(ValueError, match="screen_layout"):
        resolve_config(CamcorderWithFlipoutScreenConfig(screen_layout="bad"))  # type: ignore[arg-type]


def test_builds_identity_and_required_screen_hinge() -> None:
    config = CamcorderWithFlipoutScreenConfig()
    model = build_camcorder(config)
    report = run_camcorder_tests(model, config)

    assert report.passed, report.failures
    assert model.get_articulation("screen_hinge").articulation_type == ArticulationType.REVOLUTE
    assert model.get_articulation("screen_hinge").axis == (0.0, 0.0, 1.0)


def test_supported_screen_layouts_and_legacy_armatures() -> None:
    swivel = build_camcorder(
        CamcorderWithFlipoutScreenConfig(screen_layout="door_with_inner_swivel")
    )
    assert (
        resolve_config(
            CamcorderWithFlipoutScreenConfig(screen_layout="door_with_inner_swivel")
        ).screen_layout
        == "door_with_inner_swivel"
    )
    assert "screen_swivel" in {joint.name for joint in swivel.articulations}

    resolved = resolve_config(CamcorderWithFlipoutScreenConfig(screen_layout="armature_two_link"))
    model = build_camcorder(CamcorderWithFlipoutScreenConfig(screen_layout="armature_two_link"))
    assert resolved.screen_layout == "single_door"
    assert "screen_arm" not in {part.name for part in model.parts}
    assert "screen_hinge" in {joint.name for joint in model.articulations}
    assert "screen_swivel" not in {joint.name for joint in model.articulations}


def test_lens_ring_and_buttons_follow_layout() -> None:
    config = CamcorderWithFlipoutScreenConfig(
        ring_style="zoom_ring", control_layout="buttons_and_dial", button_count=4
    )
    model = build_camcorder(config)

    assert model.get_articulation("lens_ring_spin").axis == (1.0, 0.0, 0.0)
    assert len([j for j in model.articulations if j.name.startswith("button_press_")]) == 4
    assert model.get_articulation("mode_dial_turn").articulation_type == ArticulationType.REVOLUTE


def test_legacy_top_handle_is_removed_from_geometry() -> None:
    config = CamcorderWithFlipoutScreenConfig(grip_style="top_handle")
    resolved = resolve_config(config)
    model = build_camcorder(config)

    assert resolved.grip_style == "hand_strap"
    assert "top_handle" not in {part.name for part in model.parts}
    assert "body_to_top_handle" not in {joint.name for joint in model.articulations}


def test_seed_config_reproducible_and_varied_without_complex_screens() -> None:
    assert config_from_seed(12) == config_from_seed(12)
    assert config_from_seed(12) != config_from_seed(13)
    configs = [config_from_seed(seed) for seed in range(30)]
    assert {config.screen_layout for config in configs} == {
        "single_door",
        "door_with_inner_swivel",
    }
    assert {config.grip_style for config in configs} <= {"none", "side_pad", "hand_strap"}
    assert len({config.body_profile for config in configs}) >= 2


def test_run_camcorder_tests_passes_for_stable_core() -> None:
    for config in (
        CamcorderWithFlipoutScreenConfig(),
        CamcorderWithFlipoutScreenConfig(ring_style="zoom_ring", control_layout="side_buttons"),
    ):
        report = run_camcorder_tests(build_camcorder(config), config)
        assert report.passed, report.failures


def test_seeded_models_pass_strict_geometry_qc() -> None:
    for seed in (0, 1, 2, 5, 16, 21):
        ctx = ArticraftTestContext(build_seeded_camcorder(seed))
        # Mirror the template's declared mechanism engagement: the control
        # ring's band rides concentrically on the lens barrel by design.
        ctx.allow_overlap(
            "lens",
            "lens_control_ring",
            elem_a="lens_barrel",
            elem_b="ring_band",
            reason="focus/zoom ring rotates concentrically on the lens barrel",
        )
        ctx.check_model_valid()
        ctx.fail_if_isolated_parts()
        ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
        report = ctx.report()
        assert report.passed, report.failures
