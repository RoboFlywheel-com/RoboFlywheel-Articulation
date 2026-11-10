# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import dataclasses
import math
from pathlib import Path

import pytest

from controlled_morphology.generators import kitchen_cabinet_access as kitchen_access
from controlled_morphology.generators import multi_door_cabinet as multi_door
from controlled_morphology.generators import multi_drawer_cabinet as multi_drawer
from controlled_morphology.generators import single_door_cabinet as door
from controlled_morphology.generators import single_drawer_cabinet as drawer
from controlled_morphology.pipeline import validate_spec
from controlled_morphology.registry import get_generator

ROOT = Path(__file__).resolve().parents[1]


def _moving_joints(model):
    return [joint for joint in model.articulations if joint.articulation_type.value != "fixed"]


def _geometry_signature(geometry):
    if dataclasses.is_dataclass(geometry):
        payload = dataclasses.asdict(geometry)
    else:
        payload = repr(geometry)
    return type(geometry).__name__, payload


def _visual_signatures(model, *, ignored_token: str):
    signatures = []
    for part in model.parts:
        for visual in part.visuals:
            name = str(visual.name)
            if ignored_token in name:
                continue
            signatures.append(
                (
                    part.name,
                    name,
                    _geometry_signature(visual.geometry),
                    tuple(visual.origin.xyz),
                    tuple(visual.origin.rpy),
                )
            )
    return signatures


@pytest.mark.parametrize(
    ("hinge_side", "expected_limits", "expected_sign"),
    [
        ("left", (-1.7, 0.0), -1.0),
        ("right", (0.0, 1.7), 1.0),
    ],
)
def test_single_door_handedness_matches_joint_and_metadata(
    hinge_side, expected_limits, expected_sign
):
    config = door.Config(hinge_side=hinge_side)
    model = door.build_single_door_cabinet(config)
    resolved = door.resolve_config(config)
    metadata = door.benchmark_metadata(config)
    joints = _moving_joints(model)

    assert len(joints) == 1
    joint = joints[0]
    assert joint.axis == (0.0, 0.0, 1.0)
    assert (joint.motion_limits.lower, joint.motion_limits.upper) == expected_limits
    assert metadata["opening_sign"] == expected_sign
    assert metadata["opening_endpoint"] == expected_sign * resolved.door_swing_rad
    assert metadata["target_joint"] == joint.name
    assert metadata["target_link"] == joint.child


def test_door_handle_orientation_changes_only_handle_geometry():
    horizontal = door.build_single_door_cabinet(door.Config(handle_orientation_rad=0.0))
    vertical = door.build_single_door_cabinet(door.Config(handle_orientation_rad=math.pi / 2.0))

    assert _visual_signatures(horizontal, ignored_token="__handle_") == _visual_signatures(
        vertical, ignored_token="__handle_"
    )


def test_door_handle_metadata_matches_grip_visual():
    config = door.Config(
        hinge_side="right",
        handle_orientation_rad=math.pi / 3.0,
        handle_hinge_distance_ratio=0.70,
        handle_vertical_position_ratio=0.43,
    )
    model = door.build_single_door_cabinet(config)
    metadata = door.benchmark_metadata(config)
    target = next(part for part in model.parts if part.name == metadata["target_link"])
    grip = next(visual for visual in target.visuals if "__handle_grip" in str(visual.name))

    assert list(grip.origin.xyz) == pytest.approx(metadata["handle_frame"]["xyz"])
    assert list(grip.origin.rpy) == pytest.approx(metadata["handle_frame"]["rpy"])


@pytest.mark.parametrize(
    ("module", "builder"),
    [
        (door, door.build_single_door_cabinet),
        (multi_door, multi_door.build_multi_door_cabinet),
    ],
)
def test_door_knob_and_stem_use_visible_proportions(module, builder):
    model = builder(module.Config(handle_type="knob", handle_thickness_m=0.014))
    knob = next(
        visual
        for part in model.parts
        for visual in part.visuals
        if "handle_knob" in str(visual.name)
    )
    stem = next(
        visual
        for part in model.parts
        for visual in part.visuals
        if str(visual.name).endswith("handle_post")
    )

    assert knob.geometry.radius == pytest.approx(0.014 * 1.15)
    assert stem.geometry.radius == pytest.approx(0.014 * 0.50)


def test_door_metadata_records_deterministic_morphology_descendants():
    config = door.Config(carcass_width_m=1.18, carcass_height_m=1.50)
    resolved = door.resolve_config(config)
    morphology = door.benchmark_metadata(config)["morphology"]
    panel = morphology["target_panel"]

    assert panel["width_m"] == pytest.approx(resolved.leaf_w_m)
    assert panel["height_m"] == pytest.approx(resolved.leaf_h_m)
    assert panel["thickness_m"] == pytest.approx(resolved.leaf_t_m)
    assert panel["aspect_ratio_height_over_width"] == pytest.approx(
        resolved.leaf_h_m / resolved.leaf_w_m
    )
    assert morphology["motion"]["hinge_to_free_edge_m"] > resolved.leaf_w_m


@pytest.mark.parametrize("handle_type", ["bar", "knob"])
def test_single_drawer_has_one_forward_prismatic_joint(handle_type):
    config = drawer.Config(handle_type=handle_type)
    model = drawer.build_single_drawer_cabinet(config)
    metadata = drawer.benchmark_metadata(config)
    joints = _moving_joints(model)

    assert len(joints) == 1
    joint = joints[0]
    assert joint.axis == (0.0, -1.0, 0.0)
    assert joint.motion_limits.lower == 0.0
    assert joint.motion_limits.upper > 0.0
    assert metadata["opening_endpoint"] == joint.motion_limits.upper
    assert metadata["target_joint"] == joint.name
    assert metadata["target_link"] == joint.child


def test_task_builders_reject_multi_joint_configs():
    with pytest.raises(ValueError, match="single-door"):
        door.build_single_door_cabinet(door.Config(door_count=2))
    with pytest.raises(ValueError, match="single-drawer"):
        drawer.build_single_drawer_cabinet(drawer.Config(access_count=2))


def test_drawer_handle_orientation_changes_only_handle_geometry():
    horizontal = drawer.build_single_drawer_cabinet(drawer.Config(handle_orientation_rad=0.0))
    vertical = drawer.build_single_drawer_cabinet(
        drawer.Config(handle_orientation_rad=math.pi / 2.0)
    )

    assert _visual_signatures(horizontal, ignored_token="__pull_") == _visual_signatures(
        vertical, ignored_token="__pull_"
    )


def test_drawer_handle_metadata_matches_grip_visual():
    config = drawer.Config(
        handle_orientation_rad=math.pi / 4.0,
        handle_horizontal_position_ratio=0.42,
        handle_vertical_position_ratio=0.61,
    )
    model = drawer.build_single_drawer_cabinet(config)
    metadata = drawer.benchmark_metadata(config)
    target = next(part for part in model.parts if part.name == metadata["target_link"])
    grip = next(visual for visual in target.visuals if "__pull_bar" in str(visual.name))
    frame = metadata["handle_frame"]

    assert list(grip.origin.xyz) == pytest.approx(frame["origin_xyz"])
    assert list(grip.origin.rpy) == pytest.approx(frame["orientation_rpy"])


@pytest.mark.parametrize(
    ("module", "builder"),
    [
        (drawer, drawer.build_single_drawer_cabinet),
        (kitchen_access, kitchen_access.build_kitchen_cabinet_access),
    ],
)
def test_kitchen_family_knob_and_stem_use_visible_proportions(module, builder):
    model = builder(module.Config(handle_type="knob", handle_thickness_m=0.014))
    knob = next(
        visual for part in model.parts for visual in part.visuals if "pull_knob" in str(visual.name)
    )
    stem = next(
        visual
        for part in model.parts
        for visual in part.visuals
        if str(visual.name).endswith("pull_mount_0")
    )

    assert knob.geometry.radius == pytest.approx(0.014 * 1.15)
    assert stem.geometry.radius == pytest.approx(0.014 * 0.50)


def test_drawer_metadata_records_panel_tray_and_effective_motion():
    config = drawer.Config(
        carcass_width_m=0.70,
        carcass_depth_m=0.60,
        carcass_height_m=0.78,
        drawer_travel_ratio=0.60,
    )
    metadata = drawer.benchmark_metadata(config)
    morphology = metadata["morphology"]

    assert morphology["target_panel"]["width_m"] == pytest.approx(0.66)
    assert morphology["target_panel"]["height_m"] == pytest.approx(0.732)
    assert morphology["drawer_tray"]["depth_m"] == pytest.approx(0.544)
    assert morphology["motion"]["effective_travel_ratio"] == pytest.approx(0.60)
    assert morphology["motion"]["joint_travel_m"] == pytest.approx(metadata["opening_endpoint"])


def test_drawer_travel_ratio_has_no_silent_saturated_tail():
    assert (
        drawer.resolve_config(drawer.Config(drawer_travel_ratio=0.60)).drawer_travel_ratio == 0.60
    )
    assert (
        drawer.resolve_config(drawer.Config(drawer_travel_ratio=0.62)).drawer_travel_ratio == 0.60
    )


@pytest.mark.parametrize(
    "generator_id",
    [
        "single_door_cabinet",
        "single_drawer_cabinet",
        "multi_door_cabinet",
        "multi_drawer_cabinet",
        "kitchen_cabinet_access",
    ],
)
def test_registered_generators_publish_machine_readable_variable_space(generator_id):
    registration = get_generator(generator_id)
    space = registration.variable_space()

    assert space["schema_version"] == 1
    assert space["generator"] == generator_id
    assert space["variables"]
    assert all("control" in descriptor for descriptor in space["variables"].values())
    assert space["provenance"]["task_variant"] == generator_id
    assert space["provenance"]["upstream_generator_id"] == registration.upstream_generator_id
    assert registration.upstream_template_path.is_file()


@pytest.mark.parametrize("door_count", [1, 2, 3, 4])
def test_multi_door_metadata_declares_every_moving_joint(door_count):
    config = multi_door.Config(door_count=door_count)
    model = multi_door.build_multi_door_cabinet(config)
    metadata = multi_door.benchmark_metadata(config)
    joints = _moving_joints(model)

    assert len(joints) == door_count
    assert len(metadata["articulations"]) == door_count
    assert {item["target_joint"] for item in metadata["articulations"]} == {
        joint.name for joint in joints
    }
    assert all(tuple(item["axis"]) == (0.0, 0.0, 1.0) for item in metadata["articulations"])


@pytest.mark.parametrize("drawer_count", [1, 2, 3, 4, 5, 6])
def test_multi_drawer_metadata_declares_every_moving_joint(drawer_count):
    config = multi_drawer.Config(drawer_count=drawer_count)
    model = multi_drawer.build_multi_drawer_cabinet(config)
    metadata = multi_drawer.benchmark_metadata(config)
    joints = _moving_joints(model)

    assert len(joints) == drawer_count
    assert len(metadata["articulations"]) == drawer_count
    assert {item["target_joint"] for item in metadata["articulations"]} == {
        joint.name for joint in joints
    }
    assert all(tuple(item["axis"]) == (0.0, -1.0, 0.0) for item in metadata["articulations"])


@pytest.mark.parametrize(
    ("access_module", "expected_axis"),
    [
        ("hinged_doors", (0.0, 0.0, 1.0)),
        ("lift_up_flap", (1.0, 0.0, 0.0)),
    ],
)
def test_kitchen_access_is_a_matched_single_revolute_pair(access_module, expected_axis):
    config = kitchen_access.Config(access_module=access_module)
    model = kitchen_access.build_kitchen_cabinet_access(config)
    metadata = kitchen_access.benchmark_metadata(config)
    joints = _moving_joints(model)

    assert len(joints) == 1
    assert joints[0].axis == expected_axis
    assert tuple(metadata["axis"]) == expected_axis
    assert metadata["opening_endpoint"] == pytest.approx(-1.4)
    assert metadata["target_joint"] == joints[0].name
    assert metadata["target_link"] == joints[0].child


def test_kitchen_access_rejects_drawers_and_multiple_panels():
    with pytest.raises(ValueError, match="kitchen-access"):
        kitchen_access.build_kitchen_cabinet_access(
            kitchen_access.Config(access_module="drawer_stack")
        )
    with pytest.raises(ValueError, match="kitchen-access"):
        kitchen_access.build_kitchen_cabinet_access(kitchen_access.Config(access_count=2))


@pytest.mark.parametrize(
    ("filename", "axis_count", "asset_count"),
    [
        ("door_p0_space.json", 10, 28),
        ("drawer_control_space.json", 11, 32),
    ],
)
def test_control_space_specs_are_valid(filename, axis_count, asset_count):
    spec, plans = validate_spec(ROOT / "specs" / filename)

    assert len(spec.axes) == axis_count
    assert len(spec.nuisance_blocks) == 1
    assert len(plans) == asset_count


@pytest.mark.parametrize(
    ("filename", "generator_id", "asset_count"),
    [
        ("door_p1_part_count.json", "multi_door_cabinet", 4),
        ("drawer_p1_part_count.json", "multi_drawer_cabinet", 6),
        ("drawer_p1_layout.json", "multi_drawer_cabinet", 3),
        ("cabinet_p1_hinge_axis.json", "kitchen_cabinet_access", 2),
    ],
)
def test_structural_p1_specs_use_independent_generators(filename, generator_id, asset_count):
    spec, plans = validate_spec(ROOT / "specs" / filename)

    assert spec.generator_id == generator_id
    assert len(plans) == asset_count
