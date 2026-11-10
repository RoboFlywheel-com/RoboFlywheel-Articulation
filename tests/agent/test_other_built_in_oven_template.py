# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import cadquery as cq
import pytest

from agent.templates.Other_Built_in_oven import (
    BuiltInOvenConfig,
    _body_shell,
    build_built_in_oven,
    config_from_seed,
    resolve_config,
    run_built_in_oven_tests,
)
from sdk import TestContext as ArticraftTestContext


def _center(aabb):
    mins, maxs = aabb
    return tuple((lo + hi) * 0.5 for lo, hi in zip(mins, maxs))


def test_rack_geometry_is_derived_from_the_slide_origin_without_double_offset() -> None:
    config = BuiltInOvenConfig(
        door_mechanism="drop_down_bottom_hinge",
        door_count=1,
        rack_count=3,
        body_depth_scale=1.10,
        rack_travel_scale=1.05,
    )
    resolved = resolve_config(config)
    model = build_built_in_oven(config)
    ctx = ArticraftTestContext(model)

    for rack_index in range(resolved.rack_count):
        rack = model.get_part(f"rack_0_{rack_index}")
        aabb = ctx.part_world_aabb(rack)
        center = _center(aabb)

        assert abs(center[0]) < 0.02
        assert aabb[0][0] > -resolved.open_w / 2.0
        assert aabb[1][0] < resolved.open_w / 2.0
        assert aabb[0][1] >= 0.010
        assert aabb[1][1] <= min(0.480, resolved.body_d) + 0.005
        assert center[1] == pytest.approx(resolved.rack_rest_y, abs=0.010)


def test_rack_travel_preserves_retained_insertion_at_full_extension() -> None:
    config = BuiltInOvenConfig(
        rack_count=2,
        body_depth_scale=1.10,
        rack_travel_scale=1.05,
    )
    resolved = resolve_config(config)
    model = build_built_in_oven(config)
    ctx = ArticraftTestContext(model)
    rack = model.get_part("rack_0_0")
    slide = model.get_articulation("body_to_rack_0_0")

    # Sequenced mechanism: the rack keeps its FULL designed travel (no
    # clearance-solver clamp trimming it back to the CLOSED-door plane). The
    # "door shut + rack out" combo is whitelisted via the rack↔door allowance.
    assert slide.motion_limits.upper == pytest.approx(resolved.rack_travel, abs=1e-9)
    assert resolved.rack_travel <= 0.36 + 1e-9

    with ctx.pose({slide: resolved.rack_travel}):
        open_aabb = ctx.part_world_aabb(rack)
    retained = max(
        0.0, min(open_aabb[1][1], min(0.480, resolved.body_d)) - max(open_aabb[0][1], 0.0)
    )

    assert retained >= 0.035


def test_rack_closed_position_is_derived_from_cavity_depth_for_shallow_bodies() -> None:
    config = BuiltInOvenConfig(
        door_count=3,
        rack_count=4,
        body_depth_scale=0.92,
        rack_travel_scale=1.05,
    )
    resolved = resolve_config(config)
    model = build_built_in_oven(config)
    ctx = ArticraftTestContext(model)

    assert resolved.rack_rest_y + 0.200 <= resolved.body_d - 0.015

    for cavity_index in range(resolved.door_count):
        for rack_index in range(resolved.rack_count):
            rack = model.get_part(f"rack_{cavity_index}_{rack_index}")
            aabb = ctx.part_world_aabb(rack)

            assert aabb[0][1] >= 0.010
            assert aabb[1][1] <= resolved.body_d - 0.010


def test_deep_body_shell_cavity_cut_opens_through_front_face() -> None:
    configs = [
        config_from_seed(188398),
        BuiltInOvenConfig(door_count=3, body_depth_scale=1.10, cavity_height_scale=1.12),
    ]

    for config in configs:
        resolved = resolve_config(config)
        shell = _body_shell(resolved)

        for hinge_z in resolved.hinge_zs:
            probe = (
                cq.Workplane("XY")
                .box(0.12, 0.008, 0.12)
                .translate((0.0, 0.004, hinge_z + resolved.open_h / 2.0))
            )
            intersection = shell.intersect(probe)
            try:
                volume = intersection.val().Volume()
            except ValueError:
                volume = 0.0

            assert volume <= 1e-9


def test_run_built_in_oven_tests_passes_for_rack_heavy_seeded_cases() -> None:
    configs = [
        BuiltInOvenConfig(door_count=2, rack_count=4, knob_count=4),
        BuiltInOvenConfig(
            door_mechanism="french_double_door",
            door_count=2,
            rack_count=3,
            knob_count=2,
        ),
        config_from_seed(5),
    ]

    for config in configs:
        report = run_built_in_oven_tests(build_built_in_oven(config), config)
        assert report.passed, report.failures
