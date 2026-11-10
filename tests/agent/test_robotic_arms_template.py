# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import itertools

import pytest

from agent.templates.robotic_arms import (
    BASE_MODULES,
    EFFECTOR_MODULES,
    GRIPPER_MODULES,
    LINK_MODULES,
    WRIST_MODULES,
    RoboticArmsConfig,
    build_robotic_arms,
    config_from_seed,
    run_robotic_arms_tests,
    slot_choices_for_seed,
)
from sdk import TestContext as ArticraftTestContext


def _assert_no_disconnected_visual_islands(model) -> None:
    ctx = ArticraftTestContext(model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_part_contains_disconnected_geometry_islands()
    report = ctx.report()
    assert report.passed, report.failures


def test_seed_zero_is_anchor_combination_and_connected() -> None:
    assert slot_choices_for_seed(0) == [
        ("base_yaw_root", "combined_shoulder_base"),
        ("shoulder_elbow_link", "box_beam_link"),
        ("wrist_module", "wrist_1dof_roll"),
        ("end_effector", "fixed_flange"),
    ]
    model = build_robotic_arms(config_from_seed(0))
    _assert_no_disconnected_visual_islands(model)


@pytest.mark.parametrize(
    "base_module,link_module,wrist_module,effector_module",
    itertools.product(BASE_MODULES, LINK_MODULES, WRIST_MODULES, EFFECTOR_MODULES),
)
def test_all_module_combinations_build_and_are_connected(
    base_module, link_module, wrist_module, effector_module
) -> None:
    config = RoboticArmsConfig(
        base_yaw_root_module=base_module,
        shoulder_elbow_link_module=link_module,
        wrist_module=wrist_module,
        end_effector_module=effector_module,
    )
    model = build_robotic_arms(config)
    report = run_robotic_arms_tests(model, config)
    assert report.passed, report.failures
    _assert_no_disconnected_visual_islands(model)


def test_parallel_gripper_subtypes_build_and_are_connected() -> None:
    for gripper_module in GRIPPER_MODULES:
        config = RoboticArmsConfig(
            base_yaw_root_module="combined_shoulder_base",
            shoulder_elbow_link_module="box_beam_link",
            wrist_module="wrist_1dof_roll",
            end_effector_module="parallel_gripper",
            gripper_module=gripper_module,
            finger_count=3 if gripper_module in {"parallel_slide", "concentric_3jaw_chuck"} else 2,
            detail_level="industrial",
        )
        model = build_robotic_arms(config)
        report = run_robotic_arms_tests(model, config)
        assert report.passed, (gripper_module, report.failures)
        _assert_no_disconnected_visual_islands(model)
