# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.camera_lens import (
    CameraLensConfig,
    build_camera_lens,
    build_seeded_camera_lens,
    config_from_seed,
    resolve_config,
    run_camera_lens_tests,
)
from sdk import ArticulationType
from sdk import TestContext as ArticraftTestContext


def test_resolve_rejects_invalid_profile() -> None:
    with pytest.raises(ValueError, match="lens_profile"):
        resolve_config(CameraLensConfig(lens_profile="bad"))  # type: ignore[arg-type]


def test_builds_identity_and_required_focus_ring() -> None:
    config = CameraLensConfig()
    model = build_camera_lens(config)
    report = run_camera_lens_tests(model, config)

    assert report.passed, report.failures
    assert model.get_articulation("focus_ring_turn").axis == (1.0, 0.0, 0.0)
    barrel_visuals = {v.name for v in model.get_part("barrel").visuals if v.name}
    assert {"front_glass", "front_glass_retainer", "rear_glass", "mount_index_dot"}.issubset(
        barrel_visuals
    )


def test_ring_layout_creates_expected_control_joints() -> None:
    config = CameraLensConfig(
        ring_layout="zoom_iris_focus", zoom_ring_enabled=True, aperture_ring_enabled=True
    )
    model = build_camera_lens(config)

    assert model.get_articulation("zoom_ring_turn").articulation_type == ArticulationType.REVOLUTE
    assert model.get_articulation("aperture_ring_turn").axis == (1.0, 0.0, 0.0)
    assert model.get_articulation("focus_ring_turn").axis == (1.0, 0.0, 0.0)


def test_extension_is_suppressed_and_tripod_collar_turns() -> None:
    config = CameraLensConfig(extension_enabled=True, tripod_collar_enabled=True)
    model = build_camera_lens(config)
    joint_names = {joint.name for joint in model.articulations}

    assert "barrel_extension" not in joint_names
    assert model.get_articulation("tripod_collar_turn").axis == (1.0, 0.0, 0.0)
    collar_visuals = {v.name for v in model.get_part("tripod_collar").visuals if v.name}
    assert "ring_shell" in collar_visuals
    assert "collar_clamp_screw" not in collar_visuals


def test_hood_joint_without_extending_front_barrel() -> None:
    config = CameraLensConfig(
        lens_profile="manual_prime", extension_enabled=False, hood_enabled=True
    )
    model = build_camera_lens(config)

    assert model.get_articulation("hood_twist").axis == (1.0, 0.0, 0.0)


def test_tilt_shift_translation_chain_is_suppressed() -> None:
    config = CameraLensConfig(
        lens_profile="tilt_shift", tilt_shift_enabled=True, extension_enabled=False
    )
    model = build_camera_lens(config)
    joint_names = {joint.name for joint in model.articulations}

    assert "tilt_shift_rotate" not in joint_names
    assert "shift_slide" not in joint_names
    assert "tilt_axis" not in joint_names
    assert all(
        joint.articulation_type != ArticulationType.PRISMATIC for joint in model.articulations
    )


def test_tilt_shift_profile_resolves_to_rotation_only_lens() -> None:
    resolved = resolve_config(CameraLensConfig(lens_profile="tilt_shift"))

    assert not resolved.tilt_shift_enabled
    assert not resolved.extension_enabled
    assert not resolved.hood_enabled


def test_diversity_parameters_change_ring_surface() -> None:
    ribbed = build_camera_lens(CameraLensConfig(ring_style="rubber_ribbed"))
    smooth = build_camera_lens(CameraLensConfig(ring_style="smooth_marked"))
    ribbed_names = {v.name for v in ribbed.get_part("focus_ring").visuals if v.name}
    smooth_names = {v.name for v in smooth.get_part("focus_ring").visuals if v.name}

    assert "ring_shell" in ribbed_names
    assert "ring_shell" in smooth_names
    assert any(name.startswith("grip_rib_") for name in ribbed_names)
    assert not any(name.startswith("painted_scale_tick_") for name in ribbed_names)
    assert not any(name.startswith("ring_scale_tick_") for name in smooth_names)


def test_joint_metadata_includes_spec_fields() -> None:
    model = build_camera_lens(
        CameraLensConfig(
            ring_layout="unlock_zoom_focus",
            unlock_ring_enabled=True,
            extension_enabled=True,
            tripod_collar_enabled=True,
            hood_enabled=True,
            tilt_shift_enabled=True,
        )
    )

    for joint in model.articulations:
        if joint.articulation_type != ArticulationType.FIXED:
            assert {"type", "axis", "origin", "range"}.issubset(joint.meta)


def test_seed_config_reproducible_and_varied() -> None:
    assert config_from_seed(22) == config_from_seed(22)
    assert config_from_seed(22) != config_from_seed(23)
    configs = [config_from_seed(seed) for seed in range(50)]
    assert len({config.lens_profile for config in configs}) >= 3
    assert len({config.ring_style for config in configs}) >= 3


def test_run_camera_lens_tests_passes_for_variants() -> None:
    for config in (
        CameraLensConfig(),
        CameraLensConfig(lens_profile="telephoto_collar", tripod_collar_enabled=True),
        CameraLensConfig(lens_profile="tilt_shift", tilt_shift_enabled=True),
    ):
        report = run_camera_lens_tests(build_camera_lens(config), config)
        assert report.passed, report.failures


def test_seeded_models_pass_strict_geometry_qc() -> None:
    for seed in range(3):
        ctx = ArticraftTestContext(build_seeded_camera_lens(seed))
        ctx.check_model_valid()
        ctx.fail_if_isolated_parts()
        ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
        report = ctx.report()
        assert report.passed, report.failures


def test_named_profiles_pass_strict_geometry_qc() -> None:
    for config in (
        CameraLensConfig(lens_profile="standard_zoom"),
        CameraLensConfig(lens_profile="macro_extending"),
        CameraLensConfig(lens_profile="telephoto_collar", tripod_collar_enabled=True),
        CameraLensConfig(lens_profile="cine_zoom"),
        CameraLensConfig(lens_profile="tilt_shift", tilt_shift_enabled=True),
        CameraLensConfig(lens_profile="retractable_kit"),
        CameraLensConfig(lens_profile="manual_prime", hood_enabled=True),
    ):
        model = build_camera_lens(config)
        report = run_camera_lens_tests(model, config)
        assert report.passed, report.failures

        ctx = ArticraftTestContext(model)
        ctx.check_model_valid()
        ctx.fail_if_isolated_parts()
        ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
        qc_report = ctx.report()
        assert qc_report.passed, qc_report.failures
