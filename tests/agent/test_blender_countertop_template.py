# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.blender_countertop import (
    BlenderConfig,
    build_blender,
    config_from_seed,
    resolve_config,
    run_blender_tests,
)
from sdk import TestContext as ArticraftTestContext


def _assert_strict_qc_passes(model) -> None:
    ctx = ArticraftTestContext(model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
    report = ctx.report()
    assert report.passed, report.failures


def test_seeded_configs_keep_good_parameterized_original_families() -> None:
    configs = [config_from_seed(seed) for seed in range(80)]

    assert {config.blender_layout for config in configs} == {
        "countertop_jug",
        "personal_cup",
        "vacuum_jug",
    }
    assert "commercial_hood" not in {config.blender_layout for config in configs}
    assert "bar_blender" not in {config.blender_layout for config in configs}
    assert {config.hood_enabled for config in configs} == {False}
    assert {config.safety_latch_enabled for config in configs} == {False}
    assert {config.control_style for config in configs} <= {"dial", "button_panel"}
    assert {config.cap_style for config in configs} <= {"none", "center_twist"}


def test_simple_families_resolve_to_their_original_body_shapes() -> None:
    countertop = resolve_config(BlenderConfig(blender_layout="countertop_jug"))
    personal = resolve_config(BlenderConfig(blender_layout="personal_cup"))
    vacuum = resolve_config(BlenderConfig(blender_layout="vacuum_jug"))

    assert countertop.base_shape == "rectangular"
    assert countertop.jar_shape == "square_pitcher"
    assert personal.blender_layout == "personal_cup"
    assert personal.base_shape == "rectangular"
    assert personal.jar_shape == "inverted_cup"
    assert personal.lid_style == "none"
    assert personal.handle_style == "none"
    assert vacuum.blender_layout == "vacuum_jug"
    assert vacuum.base_shape == "round_disc"
    assert vacuum.jar_shape == "cylindrical_jug"
    assert vacuum.lid_style in {"center_cap_lid", "vacuum_cap"}


def test_legacy_complex_hood_layouts_are_coerced_to_countertop_jug() -> None:
    for layout in ("commercial_hood", "bar_blender"):
        resolved = resolve_config(
            BlenderConfig(
                blender_layout=layout,
                hood_enabled=True,
                safety_latch_enabled=True,
                lid_style="hinged_shield",
                control_style="trigger",
                cap_style="vacuum_press",
            )
        )

        assert resolved.blender_layout == "countertop_jug"
        assert resolved.base_shape == "rectangular"
        assert resolved.jar_shape == "square_pitcher"
        assert resolved.lid_style == "center_cap_lid"
        assert resolved.control_style == "dial"
        assert not resolved.hood_enabled
        assert not resolved.safety_latch_enabled


def test_good_parameterized_families_pass_template_and_strict_qc() -> None:
    configs = [
        BlenderConfig(lid_style="center_cap_lid", control_style="dial"),
        BlenderConfig(blender_layout="personal_cup", control_style="button_panel"),
        BlenderConfig(
            blender_layout="vacuum_jug",
            lid_style="vacuum_cap",
            control_style="button_panel",
            jar_lock_motion="twist_lock",
        ),
    ]

    for config in configs:
        model = build_blender(config)
        report = run_blender_tests(model, config)
        assert report.passed, report.failures
        _assert_strict_qc_passes(model)


def test_rotary_controls_have_visible_asymmetric_markers() -> None:
    model = build_blender(BlenderConfig(lid_style="center_cap_lid", control_style="dial"))

    cap_visuals = {visual.name for visual in model.get_part("center_cap").visuals}
    dial_visuals = {visual.name for visual in model.get_part("dial_or_controls").visuals}

    assert "cap_twist_pointer" in cap_visuals
    assert "speed_dial_pointer" in dial_visuals


def test_seed_zero_to_eleven_pass_strict_qc() -> None:
    for seed in range(12):
        _assert_strict_qc_passes(build_blender(config_from_seed(seed)))
