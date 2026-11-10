# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.turntable import (
    build_seeded_turntable,
    config_from_seed,
    run_turntable_tests,
)
from sdk import TestContext


@pytest.mark.parametrize("seed", [0, 1, 3, 5, 10, 14, 22, 33, 63])
def test_seeded_turntable_variants_pass_template_checks(seed: int) -> None:
    model = build_seeded_turntable(seed)
    report = run_turntable_tests(model, config_from_seed(seed))

    assert report.passed, report.failures


def test_seed_5_dust_cover_is_supported_and_clear_of_platter() -> None:
    model = build_seeded_turntable(5)
    ctx = TestContext(model)
    plinth = model.get_part("plinth")
    cover = model.get_part("dust_cover_guard")
    platter = model.get_part("platter")

    cover_visuals = {visual.name for visual in cover.visuals}
    assert {
        "rear_hinge_bar",
        "left_bottom_slide_foot",
        "right_bottom_slide_foot",
        "front_bottom_lip",
        "left_front_corner_post",
        "right_front_corner_post",
        "front_top_lip",
    } <= cover_visuals

    for elem in ("left_bottom_slide_foot", "right_bottom_slide_foot", "front_bottom_lip"):
        foot_aabb = ctx.part_element_world_aabb(cover, elem=elem)
        deck_aabb = ctx.part_element_world_aabb(plinth, elem="top_deck")
        assert foot_aabb is not None
        assert deck_aabb is not None
        assert foot_aabb[0][2] <= deck_aabb[1][2] + 0.004

    left_side = ctx.part_element_world_aabb(cover, elem="left_clear_side")
    right_side = ctx.part_element_world_aabb(cover, elem="right_clear_side")
    platter_disc = ctx.part_element_world_aabb(platter, elem="platter_disc")
    assert left_side is not None
    assert right_side is not None
    assert platter_disc is not None
    assert left_side[1][0] < platter_disc[0][0]
    assert right_side[0][0] > platter_disc[1][0]


def test_fixed_guard_frame_uses_deck_feet_and_low_ring() -> None:
    model = build_seeded_turntable(3)
    ctx = TestContext(model)
    plinth = model.get_part("plinth")
    guard = model.get_part("guard_frame")
    platter = model.get_part("platter")

    guard_visuals = {visual.name for visual in guard.visuals}
    assert {
        "fixed_guard_ring",
        "fixed_guard_foot_0",
        "fixed_guard_foot_1",
        "fixed_guard_foot_2",
    } <= guard_visuals

    deck_aabb = ctx.part_element_world_aabb(plinth, elem="top_deck")
    ring_aabb = ctx.part_element_world_aabb(guard, elem="fixed_guard_ring")
    mat_aabb = ctx.part_element_world_aabb(platter, elem="rubber_record_mat")
    assert deck_aabb is not None
    assert ring_aabb is not None
    assert mat_aabb is not None
    assert ring_aabb[0][2] > deck_aabb[1][2]
    assert ring_aabb[1][2] > mat_aabb[1][2]

    for index in range(3):
        foot_aabb = ctx.part_element_world_aabb(guard, elem=f"fixed_guard_foot_{index}")
        assert foot_aabb is not None
        assert foot_aabb[0][2] <= deck_aabb[1][2] + 0.004
