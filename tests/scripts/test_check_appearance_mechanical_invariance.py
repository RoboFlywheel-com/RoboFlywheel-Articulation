# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import pytest

from scripts.check_appearance_mechanical_invariance import (
    MechanicalSnapshotError,
    compare_configs,
    compare_object_models,
    config_mechanical_fingerprint,
    config_mechanical_snapshot,
    object_model_mechanical_fingerprint,
    object_model_mechanical_snapshot,
)


@dataclass(frozen=True)
class Origin:
    xyz: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rpy: tuple[float, float, float] = (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class Box:
    size: tuple[float, float, float]


@dataclass(frozen=True)
class Inertia:
    ixx: float
    ixy: float
    ixz: float
    iyy: float
    iyz: float
    izz: float


@dataclass
class Inertial:
    mass: float
    inertia: Inertia
    origin: Origin = field(default_factory=Origin)


@dataclass
class Visual:
    geometry: Any
    origin: Origin = field(default_factory=Origin)
    material: Any = None
    name: str | None = None
    builder: str | None = None
    material_class_id: str | None = None


@dataclass
class Collision:
    geometry: Any
    origin: Origin = field(default_factory=Origin)
    name: str | None = None


@dataclass
class Part:
    name: str
    visuals: list[Visual]
    collisions: list[Collision]
    inertial: Inertial | None
    meta: dict[str, Any] = field(default_factory=dict)


class JointType(str, Enum):
    REVOLUTE = "revolute"


@dataclass
class Joint:
    name: str
    articulation_type: JointType
    parent: str
    child: str
    origin: Origin
    axis: tuple[float, float, float]
    motion_limits: dict[str, float]
    motion_properties: dict[str, float] | None = None
    mimic: dict[str, Any] | None = None
    mating: dict[str, Any] | None = None
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass
class Model:
    name: str
    parts: list[Part]
    articulations: list[Joint]
    materials: list[Any]


def _model() -> Model:
    base = Part(
        name="base",
        visuals=[
            Visual(
                Box((0.4, 0.3, 0.1)),
                Origin((0.0, 0.0, 0.05)),
                material={"name": "paint", "rgba": [1.0, 0.0, 0.0, 1.0]},
                name="base_shell",
                builder="_build_old_base",
                material_class_id="metal.generic_plain",
            )
        ],
        collisions=[Collision(Box((0.4, 0.3, 0.1)), Origin((0.0, 0.0, 0.05)), "base_collision")],
        inertial=Inertial(2.0, Inertia(1.0, 0.0, 0.0, 1.1, 0.0, 1.2)),
        meta={"structural": True},
    )
    door = Part(
        name="door",
        visuals=[
            Visual(
                Box((0.2, 0.02, 0.2)),
                Origin((0.1, 0.0, 0.15)),
                material="door_paint",
                name="door_leaf",
            )
        ],
        collisions=[],
        inertial=None,
    )
    joint = Joint(
        name="door_hinge",
        articulation_type=JointType.REVOLUTE,
        parent="base",
        child="door",
        origin=Origin((0.0, 0.0, 0.1)),
        axis=(0.0, 0.0, 1.0),
        motion_limits={"lower": 0.0, "upper": 1.2, "effort": 1.0, "velocity": 1.0},
        mating={"parent_face_geometry": "base_shell", "child_face_geometry": "door_leaf"},
    )
    return Model("sample", [base, door], [joint], materials=[{"name": "paint"}])


def test_material_registry_and_visual_material_class_are_excluded() -> None:
    before = _model()
    after = copy.deepcopy(before)
    after.materials = [{"name": "retrieved_pbr", "texture": "package.blend"}]
    after.parts[0].visuals[0].material = "retrieved_pbr"
    after.parts[0].visuals[0].material_class_id = "metal.paint_coated"
    after.parts[0].visuals[0].builder = "_build_renamed_base"

    result = compare_object_models(before, after)
    assert result.invariant is True
    assert result.before_sha256 == result.after_sha256
    assert result.differences == ()


@pytest.mark.parametrize(
    ("mutate", "path_fragment"),
    [
        (
            lambda snapshot: snapshot["parts"][0]["visuals"][0]["geometry"]["size"].__setitem__(
                0, 0.5
            ),
            "$.parts[0].visuals[0].geometry.size[0]",
        ),
        (
            lambda snapshot: snapshot["parts"][0]["visuals"][0]["origin"]["xyz"].__setitem__(
                2, 0.06
            ),
            "$.parts[0].visuals[0].origin.xyz[2]",
        ),
        (
            lambda snapshot: snapshot["parts"][0]["collisions"][0]["geometry"]["size"].__setitem__(
                1, 0.31
            ),
            "$.parts[0].collisions[0].geometry.size[1]",
        ),
        (
            lambda snapshot: snapshot["parts"][0]["inertial"].__setitem__("mass", 2.1),
            "$.parts[0].inertial.mass",
        ),
        (
            lambda snapshot: snapshot["joints"][0]["motion_limits"].__setitem__("upper", 1.3),
            "$.joints[0].motion_limits.upper",
        ),
    ],
)
def test_mechanical_changes_are_reported_with_paths(mutate: Any, path_fragment: str) -> None:
    before = object_model_mechanical_snapshot(_model())
    after = copy.deepcopy(before)
    mutate(after)

    result = compare_object_models(before, after)
    assert result.invariant is False
    assert result.before_sha256 != result.after_sha256
    assert any(path_fragment in difference for difference in result.differences)


def test_serialized_aliases_and_live_model_have_the_same_projection() -> None:
    live = _model()
    serialized = object_model_mechanical_snapshot(live)
    serialized["links"] = serialized.pop("parts")
    serialized["articulations"] = serialized.pop("joints")
    serialized["materials"] = [{"name": "ignored"}]
    for part in serialized["links"]:
        for visual in part["visuals"]:
            visual["material"] = {"name": "ignored"}
            visual["material_class_id"] = "metal.paint_coated"

    result = compare_object_models(live, serialized)
    assert result.invariant is True
    assert object_model_mechanical_fingerprint(live) == result.before_sha256


def test_part_and_visual_order_are_strict() -> None:
    before = _model()
    after = copy.deepcopy(before)
    after.parts.reverse()

    result = compare_object_models(before, after)
    assert result.invariant is False
    assert any("$.parts[0].name" in difference for difference in result.differences)


@dataclass(frozen=True)
class LegacyConfig:
    width: float
    panel_count: int
    material_style: str
    appearance: dict[str, Any]


def test_config_fingerprint_drops_only_explicit_appearance_fields() -> None:
    before = LegacyConfig(
        width=0.8,
        panel_count=3,
        material_style="painted_red",
        appearance={"colorway": "warm", "roughness": 0.4},
    )
    after = {"width": 0.8, "panel_count": 3, "appearance": {"roughness": 0.4}}
    fields_to_drop = ("material_style", "appearance.colorway")

    result = compare_configs(before, after, appearance_fields=fields_to_drop)
    assert result.invariant is True
    assert config_mechanical_fingerprint(
        before, appearance_fields=fields_to_drop
    ) == config_mechanical_fingerprint(after, appearance_fields=fields_to_drop)

    unfiltered = compare_configs(before, after)
    assert unfiltered.invariant is False


def test_config_mechanical_change_is_not_hidden_by_appearance_filter() -> None:
    before = {"width": 0.8, "panel_count": 3, "material_style": "red"}
    after = {"width": 0.9, "panel_count": 3}

    result = compare_configs(before, after, appearance_fields=("material_style",))
    assert result.invariant is False
    assert any("$.config.width" in difference for difference in result.differences)


def test_fingerprints_are_deterministic_and_reject_nonfinite_values() -> None:
    model = _model()
    assert object_model_mechanical_fingerprint(model) == object_model_mechanical_fingerprint(
        copy.deepcopy(model)
    )
    assert config_mechanical_snapshot(
        {"b": 2, "a": 1, "palette": "x"}, appearance_fields=("palette",)
    ) == config_mechanical_snapshot(
        {"palette": "y", "a": 1, "b": 2}, appearance_fields=("palette",)
    )

    model.parts[0].visuals[0].geometry = Box((float("nan"), 0.3, 0.1))
    with pytest.raises(MechanicalSnapshotError, match="non-finite"):
        object_model_mechanical_snapshot(model)
