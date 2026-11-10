# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math

import pytest

from agent.templates.bicycle_crankset_and_pedal_assembly import (
    ADOPTED_SOURCES,
    FIVE_STAR_SOURCE_RECORDS,
    BicycleCranksetAndPedalAssemblyConfig,
    build_bicycle_crankset,
    build_seeded_bicycle_crankset,
    config_from_seed,
    resolve_config,
    run_bicycle_crankset_tests,
)
from sdk import ArticulationType
from sdk import TestContext as ArticraftTestContext


def test_adopted_sources_are_recorded() -> None:
    assert set(ADOPTED_SOURCES) == {"S1", "S2", "S3", "S4", "S5"}
    assert len(FIVE_STAR_SOURCE_RECORDS) == 36
    assert all(
        record_id.startswith("rec_bicycle_crankset_and_pedal_assembly_")
        for record_id in FIVE_STAR_SOURCE_RECORDS
    )


@pytest.mark.parametrize("layout", ["combined_crankset", "modular_three_piece"])
def test_layouts_build_crank_spin_chainring_and_two_pedals(layout: str) -> None:
    config = BicycleCranksetAndPedalAssemblyConfig(assembly_layout=layout)  # type: ignore[arg-type]
    model = build_bicycle_crankset(config)
    report = run_bicycle_crankset_tests(model, config)

    assert report.passed, report.failures
    assert (
        model.get_articulation("bb_to_crank_spin").articulation_type == ArticulationType.CONTINUOUS
    )
    assert model.get_part("right_pedal") is not None
    assert model.get_part("left_pedal") is not None


def test_pedal_spin_axes_parallel_crank_axis() -> None:
    config = BicycleCranksetAndPedalAssemblyConfig(spindle_axis="x", pedal_motion_mode="spin")
    model = build_bicycle_crankset(config)

    crank = model.get_articulation("bb_to_crank_spin")
    right = model.get_articulation("right_pedal_spin")
    left = model.get_articulation("left_pedal_spin")
    assert crank.axis == right.axis == left.axis == (1.0, 0.0, 0.0)


def test_bottom_bracket_stays_focused_on_crankset_shell() -> None:
    model = build_bicycle_crankset(BicycleCranksetAndPedalAssemblyConfig(spindle_axis="x"))
    shell = model.get_part("bottom_bracket_shell")

    visual_names = {visual.name for visual in shell.visuals}
    assert "frame_stub" not in visual_names
    assert "seat_tube_stub" not in visual_names
    assert {
        "shell_upper_shell",
        "drive_cup_upper_shell",
        "non_drive_cup_upper_shell",
    } <= visual_names

    drive_cup = shell.get_visual("drive_cup_upper_shell")
    non_drive_cup = shell.get_visual("non_drive_cup_upper_shell")
    assert drive_cup.origin.xyz[0] > 0.0
    assert non_drive_cup.origin.xyz[0] < 0.0


def test_chainring_spider_uses_short_bolt_circle_supports() -> None:
    config = BicycleCranksetAndPedalAssemblyConfig(
        chainring_profile="round_single",
        spider_style="five_arm",
    )
    r = resolve_config(config)
    model = build_bicycle_crankset(config)
    crankset = model.get_part("crankset_combined")

    spider = crankset.get_visual("spider_arm_0")
    spider_center_radius = math.hypot(spider.origin.xyz[1], spider.origin.xyz[2])
    spider_outer_radius = spider_center_radius + spider.geometry.size[2] * 0.5

    assert spider.geometry.size[2] < 0.045
    assert spider_outer_radius <= min(r.ring_radii) * 0.72
    assert crankset.get_visual("chainring_bolt_0").origin.xyz[2] == pytest.approx(
        min(r.ring_radii) * 0.68
    )


def test_modular_layout_uses_child_local_arm_and_pedal_coordinates() -> None:
    config = BicycleCranksetAndPedalAssemblyConfig(
        assembly_layout="modular_three_piece",
        spindle_axis="x",
        pedal_motion_mode="spin",
    )
    model = build_bicycle_crankset(config)

    right_pedal = model.get_articulation("right_pedal_spin")
    left_pedal = model.get_articulation("left_pedal_spin")
    assert right_pedal.origin.xyz[0] == pytest.approx(0.0)
    assert left_pedal.origin.xyz[0] == pytest.approx(0.0)
    assert right_pedal.origin.xyz[2] < 0.0
    assert left_pedal.origin.xyz[2] < 0.0

    right_boss = model.get_part("right_crank").get_visual("right_boss")
    left_boss = model.get_part("left_crank").get_visual("left_boss")
    assert right_boss.origin.xyz == pytest.approx((0.0, 0.0, 0.0))
    assert left_boss.origin.xyz == pytest.approx((0.0, 0.0, 0.0))


def test_pedal_bodies_extend_outward_from_each_crank_side() -> None:
    combined = build_bicycle_crankset(
        BicycleCranksetAndPedalAssemblyConfig(
            assembly_layout="combined_crankset",
            spindle_axis="x",
            pedal_style="platform",
        )
    )
    modular = build_bicycle_crankset(
        BicycleCranksetAndPedalAssemblyConfig(
            assembly_layout="modular_three_piece",
            spindle_axis="x",
            pedal_style="platform",
        )
    )
    folding_modular = build_bicycle_crankset(
        BicycleCranksetAndPedalAssemblyConfig(
            assembly_layout="modular_three_piece",
            spindle_axis="x",
            pedal_style="folding_cage",
            pedal_motion_mode="spin_and_fold",
        )
    )

    assert combined.get_part("right_pedal").get_visual("right_pedal_body").origin.xyz[0] > 0.0
    assert combined.get_part("left_pedal").get_visual("left_pedal_body").origin.xyz[0] < 0.0
    assert modular.get_part("right_pedal").get_visual("right_pedal_body").origin.xyz[0] > 0.0
    assert modular.get_part("left_pedal").get_visual("left_pedal_body").origin.xyz[0] < 0.0
    assert modular.get_articulation("left_pedal_spin").origin.rpy == pytest.approx(
        (0.0, math.pi, 0.0)
    )
    assert (
        folding_modular.get_part("left_pedal_knuckle").get_visual("left_fold_knuckle").origin.xyz[0]
        < 0.0
    )
    assert folding_modular.get_articulation("left_pedal_fold").origin.rpy == pytest.approx(
        (0.0, math.pi, 0.0)
    )


def test_folding_pedals_use_revolute_pi_over_two_range() -> None:
    config = BicycleCranksetAndPedalAssemblyConfig(
        pedal_style="folding_cage",
        pedal_motion_mode="fold",
    )
    model = build_bicycle_crankset(config)

    for name in ("right_pedal_fold", "left_pedal_fold"):
        joint = model.get_articulation(name)
        assert joint.articulation_type == ArticulationType.REVOLUTE
        assert joint.motion_limits.upper == pytest.approx(math.pi / 2.0)


def test_cage_pedal_uses_connected_rail_and_deck_construction() -> None:
    config = BicycleCranksetAndPedalAssemblyConfig(pedal_style="cage", spindle_axis="x")
    model = build_bicycle_crankset(config)
    pedal = model.get_part("right_pedal")
    visual_names = {visual.name for visual in pedal.visuals}

    assert not any("_cage_rail_" in name for name in visual_names)
    assert {
        "right_inner_rail",
        "right_outer_rail",
        "right_front_rail",
        "right_rear_rail",
        "right_pedal_deck",
    } <= visual_names

    deck = pedal.get_visual("right_pedal_deck")
    front = pedal.get_visual("right_front_rail")
    rear = pedal.get_visual("right_rear_rail")
    inner = pedal.get_visual("right_inner_rail")
    outer = pedal.get_visual("right_outer_rail")

    assert abs(front.origin.xyz[2] - deck.origin.xyz[2]) < 0.010
    assert abs(rear.origin.xyz[2] - deck.origin.xyz[2]) < 0.010
    assert inner.origin.xyz[0] - inner.geometry.size[0] * 0.5 <= deck.origin.xyz[0]
    assert outer.origin.xyz[0] + outer.geometry.size[0] * 0.5 >= deck.origin.xyz[0]


def test_rejects_nonfolding_fold_motion() -> None:
    with pytest.raises(ValueError, match="non-folding"):
        resolve_config(BicycleCranksetAndPedalAssemblyConfig(pedal_motion_mode="fold"))


def test_diversity_parameters_vary_across_seeds() -> None:
    configs = [config_from_seed(seed) for seed in range(120)]
    assert {c.assembly_layout for c in configs} == {"combined_crankset", "modular_three_piece"}
    assert {c.spindle_axis for c in configs} == {"x"}
    assert len({c.crank_arm_profile for c in configs}) >= 4
    assert len({c.chainring_profile for c in configs}) >= 9
    assert len({c.pedal_style for c in configs}) >= 8
    assert len({c.bb_shell_style for c in configs}) >= 11
    assert len({c.material_style for c in configs}) >= 7


def test_chainring_profiles_cover_single_double_and_triple_variants() -> None:
    single = resolve_config(BicycleCranksetAndPedalAssemblyConfig(chainring_profile="oval_one_by"))
    inferred_double = resolve_config(
        BicycleCranksetAndPedalAssemblyConfig(chainring_profile="road_double")
    )
    double = resolve_config(
        BicycleCranksetAndPedalAssemblyConfig(chainring_profile="road_double", chainring_count=2)
    )
    compact = resolve_config(
        BicycleCranksetAndPedalAssemblyConfig(chainring_profile="compact_double", chainring_count=2)
    )
    triple = resolve_config(
        BicycleCranksetAndPedalAssemblyConfig(chainring_profile="road_triple", chainring_count=3)
    )
    track = resolve_config(
        BicycleCranksetAndPedalAssemblyConfig(
            chainring_profile="track_solid", spider_style="five_arm"
        )
    )

    assert len(single.ring_radii) == 1
    assert inferred_double.chainring_count == 2
    assert len(inferred_double.ring_radii) == inferred_double.chainring_count
    assert len(double.ring_radii) == 2
    assert len(compact.ring_radii) == 2
    assert len(triple.ring_radii) == 3
    assert triple.ring_radii[0] > triple.ring_radii[1] > triple.ring_radii[2]
    assert track.spider_arm_count == 0


def test_sampled_pedal_and_bottom_bracket_variants_have_visible_features() -> None:
    rat_trap = build_bicycle_crankset(
        BicycleCranksetAndPedalAssemblyConfig(pedal_style="rat_trap", spindle_axis="x")
    )
    road_clipless = build_bicycle_crankset(
        BicycleCranksetAndPedalAssemblyConfig(pedal_style="road_clipless", spindle_axis="x")
    )
    square_taper = build_bicycle_crankset(
        BicycleCranksetAndPedalAssemblyConfig(bb_shell_style="square_taper", spindle_axis="x")
    )
    torque_sensor = build_bicycle_crankset(
        BicycleCranksetAndPedalAssemblyConfig(
            bb_shell_style="torque_sensor_ebike", spindle_axis="x"
        )
    )

    rat_trap_names = {visual.name for visual in rat_trap.get_part("right_pedal").visuals}
    road_clipless_names = {visual.name for visual in road_clipless.get_part("right_pedal").visuals}
    square_taper_names = {
        visual.name for visual in square_taper.get_part("crankset_combined").visuals
    }
    torque_sensor_names = {
        visual.name for visual in torque_sensor.get_part("bottom_bracket_shell").visuals
    }

    assert "right_cage_grip_pin_0_0" in rat_trap_names
    assert "right_front_binding" in road_clipless_names
    assert "right_square_taper_flat" in square_taper_names
    assert "torque_sensor_module" in torque_sensor_names


def test_seed_reproducibility() -> None:
    assert config_from_seed(7) == config_from_seed(7)
    assert config_from_seed(7) != config_from_seed(8)
    assert build_seeded_bicycle_crankset(2).name == build_seeded_bicycle_crankset(2).name


def test_run_bicycle_crankset_tests_passes_default() -> None:
    config = BicycleCranksetAndPedalAssemblyConfig()
    report = run_bicycle_crankset_tests(build_bicycle_crankset(config), config)
    assert report.passed, report.failures


def test_seed_0_to_2_pass_strict_contact_qc() -> None:
    for seed in range(3):
        ctx = ArticraftTestContext(build_seeded_bicycle_crankset(seed))
        ctx.check_model_valid()
        ctx.fail_if_isolated_parts()
        ctx.fail_if_parts_overlap_in_current_pose(
            overlap_tol=0.003,
            overlap_volume_tol=1e-7,
        )
        report = ctx.report()
        assert report.passed, report.failures
