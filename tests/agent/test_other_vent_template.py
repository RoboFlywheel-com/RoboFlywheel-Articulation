# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.Other_Vent import (
    VentConfig,
    build_vent,
    resolve_config,
    run_vent_tests,
)
from sdk import TestContext as ArticraftTestContext


def _aabb_center(aabb):
    mins, maxs = aabb
    return tuple((lo + hi) * 0.5 for lo, hi in zip(mins, maxs))


@pytest.mark.parametrize(
    ("grille_style", "housing_form", "part_name", "joint_name"),
    [
        ("woven_square_mesh", "round_through_wall", "mesh_grille", "housing_to_grille"),
        ("wire_guard_cage", "inline_duct_cylinder", "front_guard", "housing_to_guard"),
        ("louvered_front_grille", "round_flange", "louver_grille", "housing_to_louver_grille"),
        ("perforated_plate", "square_wall", "perforated_plate", "housing_to_plate"),
    ],
)
def test_independent_grilles_rebase_from_rim_joint_to_duct_center(
    grille_style: str,
    housing_form: str,
    part_name: str,
    joint_name: str,
) -> None:
    config = VentConfig(
        housing_form=housing_form,
        grille_style=grille_style,
        backdraft_shutter="none",
        guard_ring_count=5,
    )
    resolved = resolve_config(config)
    model = build_vent(config)
    report = run_vent_tests(model, config)
    assert report.passed, report.failures

    joint = model.get_articulation(joint_name)
    assert joint.origin.xyz[2] == pytest.approx(resolved.bore_r - 0.004)

    grille = model.get_part(part_name)
    center = _aabb_center(ArticraftTestContext(model).part_world_aabb(grille))
    assert center[1] == pytest.approx(0.0, abs=0.002)
    assert center[2] == pytest.approx(0.0, abs=0.002)


def test_louver_shutter_pitch_is_clamped_and_centered_in_frame() -> None:
    config = VentConfig(
        housing_form="round_flange",
        grille_style="louvered_front_grille",
        backdraft_shutter="multi_blade_louver_shutter",
        shutter_flap_count=4,
        louver_pitch_scale=1.1,
    )
    resolved = resolve_config(config)
    model = build_vent(config)
    report = run_vent_tests(model, config)
    assert report.passed, report.failures
    assert resolved.louver_pitch_scale == pytest.approx(1.0)

    slot_h = (2.0 * (resolved.bore_r - 0.006) / resolved.shutter_flap_count) * (
        resolved.louver_pitch_scale
    )
    hinge_zs = [
        model.get_articulation(f"shutter_blade_{i}_hinge").origin.xyz[2]
        for i in range(resolved.shutter_flap_count)
    ]
    occupied_min = hinge_zs[-1] - slot_h
    occupied_max = hinge_zs[0]
    assert (occupied_min + occupied_max) * 0.5 == pytest.approx(0.0, abs=1e-6)
    assert occupied_max <= resolved.bore_r
    assert occupied_min >= -resolved.bore_r
