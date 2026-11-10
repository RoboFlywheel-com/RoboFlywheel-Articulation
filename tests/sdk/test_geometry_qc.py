# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math
import sys
import types
from pathlib import Path

import pytest

from sdk import ArticulatedObject, ArticulationType, Box, Mesh, Mimic, MotionLimits, Origin
from sdk._core.v0 import geometry_qc


def _write_disconnected_boxes_obj(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    centers = ((0.0, 0.0, 0.0), (0.45, 0.0, 0.0))
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    cube_faces = (
        (0, 1, 2),
        (0, 2, 3),
        (4, 6, 5),
        (4, 7, 6),
        (0, 4, 5),
        (0, 5, 1),
        (1, 5, 6),
        (1, 6, 2),
        (2, 6, 7),
        (2, 7, 3),
        (3, 7, 4),
        (3, 4, 0),
    )
    for center_x, center_y, center_z in centers:
        base_index = len(vertices) + 1
        vertices.extend(
            [
                (center_x - 0.05, center_y - 0.05, center_z - 0.05),
                (center_x + 0.05, center_y - 0.05, center_z - 0.05),
                (center_x + 0.05, center_y + 0.05, center_z - 0.05),
                (center_x - 0.05, center_y + 0.05, center_z - 0.05),
                (center_x - 0.05, center_y - 0.05, center_z + 0.05),
                (center_x + 0.05, center_y - 0.05, center_z + 0.05),
                (center_x + 0.05, center_y + 0.05, center_z + 0.05),
                (center_x - 0.05, center_y + 0.05, center_z + 0.05),
            ]
        )
        faces.extend(tuple(base_index + idx for idx in face) for face in cube_faces)
    lines = [f"v {x} {y} {z}" for x, y, z in vertices]
    lines.extend(f"f {a} {b} {c}" for a, b, c in faces)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_single_box_obj(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    vertices = [
        (-0.05, -0.05, -0.05),
        (0.05, -0.05, -0.05),
        (0.05, 0.05, -0.05),
        (-0.05, 0.05, -0.05),
        (-0.05, -0.05, 0.05),
        (0.05, -0.05, 0.05),
        (0.05, 0.05, 0.05),
        (-0.05, 0.05, 0.05),
    ]
    faces = (
        (1, 2, 3),
        (1, 3, 4),
        (5, 7, 6),
        (5, 8, 7),
        (1, 5, 6),
        (1, 6, 2),
        (2, 6, 7),
        (2, 7, 3),
        (3, 7, 8),
        (3, 8, 4),
        (4, 8, 5),
        (4, 5, 1),
    )
    lines = [f"v {x} {y} {z}" for x, y, z in vertices]
    lines.extend(f"f {a} {b} {c}" for a, b, c in faces)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_nonmanifold_box_obj(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    vertices = [
        (-0.05, -0.05, -0.05),
        (0.05, -0.05, -0.05),
        (0.05, 0.05, -0.05),
        (-0.05, 0.05, -0.05),
        (-0.05, -0.05, 0.05),
        (0.05, -0.05, 0.05),
        (0.05, 0.05, 0.05),
        (-0.05, 0.05, 0.05),
    ]
    # Deliberately omit the +Z face.
    faces = (
        (1, 2, 3),
        (1, 3, 4),
        (1, 5, 6),
        (1, 6, 2),
        (2, 6, 7),
        (2, 7, 3),
        (3, 7, 8),
        (3, 8, 4),
        (4, 8, 5),
        (4, 5, 1),
    )
    lines = [f"v {x} {y} {z}" for x, y, z in vertices]
    lines.extend(f"f {a} {b} {c}" for a, b, c in faces)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _build_box_pair_model(
    *,
    penetration: float,
    angle: float = 0.0,
) -> ArticulatedObject:
    model = ArticulatedObject(name=f"box_pair_{penetration:g}_{angle:g}")
    root = model.part("root")
    left = model.part("left")
    left.visual(Box((0.1, 0.1, 0.1)), origin=Origin(rpy=(0.0, 0.0, angle)))
    right = model.part("right")
    right.visual(Box((0.1, 0.1, 0.1)), origin=Origin(rpy=(0.0, 0.0, angle)))
    model.articulation(
        "root_to_left",
        ArticulationType.FIXED,
        parent=root,
        child=left,
        origin=Origin(),
    )
    separation = 0.1 - float(penetration)
    model.articulation(
        "root_to_right",
        ArticulationType.FIXED,
        parent=root,
        child=right,
        origin=Origin(
            xyz=(
                separation * math.cos(angle),
                separation * math.sin(angle),
                0.0,
            )
        ),
    )
    return model


def _build_support_gap_model(gap: float) -> ArticulatedObject:
    model = ArticulatedObject(name=f"support_gap_{gap:g}")
    base = model.part("base")
    base.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.0, 0.0, 0.05)))
    child = model.part("child")
    child.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.0, 0.0, 0.05)))
    model.articulation(
        "base_to_child",
        ArticulationType.FIXED,
        parent=base,
        child=child,
        origin=Origin(xyz=(0.0, 0.0, 0.1 + float(gap))),
    )
    return model


def _build_disjoint_collision_model() -> ArticulatedObject:
    model = ArticulatedObject(name="disjoint_collision_parts")
    root = model.part("root")

    left = model.part("left")
    left.visual(
        Box((0.1, 0.1, 0.1)),
        origin=Origin(xyz=(0.0, 0.0, 0.05)),
        name="left_box",
    )

    right = model.part("right")
    right.visual(
        Box((0.1, 0.1, 0.1)),
        origin=Origin(xyz=(1.0, 0.0, 0.05)),
        name="right_box",
    )
    model.articulation(
        "root_to_left",
        ArticulationType.FIXED,
        parent=root,
        child=left,
        origin=Origin(),
    )
    model.articulation(
        "root_to_right",
        ArticulationType.FIXED,
        parent=root,
        child=right,
        origin=Origin(),
    )

    return model


def test_collision_overlap_qc_prunes_disjoint_aabbs_before_fcl(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {"collide": 0}

    class FakeCollisionRequest:
        pass

    class FakeCollisionResult:
        pass

    def fake_collide(*_args: object, **_kwargs: object) -> int:
        calls["collide"] += 1
        raise AssertionError("fcl.collide should not run when AABB overlap thresholds fail")

    fake_fcl = types.SimpleNamespace(
        CollisionRequest=FakeCollisionRequest,
        CollisionResult=FakeCollisionResult,
        collide=fake_collide,
    )

    monkeypatch.setitem(sys.modules, "fcl", fake_fcl)
    monkeypatch.setattr(
        geometry_qc,
        "_fcl_shape_from_primitive",
        lambda geometry: object(),
    )
    monkeypatch.setattr(
        geometry_qc,
        "_collision_object_from_shape",
        lambda shape, **kwargs: object(),
    )

    overlaps = geometry_qc.find_geometry_overlaps(
        _build_disjoint_collision_model(),
        max_pose_samples=1,
        overlap_tol=1e-3,
        overlap_volume_tol=0.0,
    )

    assert overlaps == []
    assert calls["collide"] == 0


def test_load_fcl_mesh_rejects_obj_without_triangles(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mesh_path = tmp_path / "empty_faces.obj"
    mesh_path.write_text(
        "\n".join(
            [
                "v 0 0 0",
                "v 1 0 0",
                "v 0 1 0",
                "",
            ]
        ),
        encoding="utf-8",
    )

    fake_fcl = types.SimpleNamespace(BVHModel=lambda: object())
    monkeypatch.setitem(sys.modules, "fcl", fake_fcl)

    class FakeTrimesh:
        def __init__(self) -> None:
            self.vertices = types.SimpleNamespace(size=9)
            self.faces = types.SimpleNamespace(size=0)

    fake_trimesh = types.SimpleNamespace(
        Trimesh=FakeTrimesh,
        load_mesh=lambda path, force="mesh": FakeTrimesh(),
    )
    monkeypatch.setitem(sys.modules, "trimesh", fake_trimesh)

    with pytest.raises(geometry_qc.ValidationError, match="no triangles"):
        geometry_qc._load_fcl_mesh(mesh_path, cache={}, scale=None)


def test_collision_object_from_geometry_supports_scaled_meshes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mesh_relpath = "assets/meshes/scaled.obj"
    mesh_path = tmp_path / mesh_relpath
    mesh_path.parent.mkdir(parents=True, exist_ok=True)
    mesh_path.write_text("# placeholder\n", encoding="utf-8")

    applied_scales: list[tuple[float, float, float]] = []

    class FakeArray:
        def __init__(self, values: list[tuple[float, float, float]]) -> None:
            self._values = values
            self.size = len(values) * 3

        def __len__(self) -> int:
            return len(self._values)

    class FakeTrimesh:
        def __init__(self) -> None:
            self.vertices = FakeArray([(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)])
            self.faces = FakeArray([(0, 1, 2)])

        def copy(self) -> "FakeTrimesh":
            return FakeTrimesh()

        def apply_scale(self, scale: tuple[float, float, float]) -> None:
            applied_scales.append(tuple(float(v) for v in scale))

    class FakeBVHModel:
        def beginModel(self, *_args: object) -> None:
            return None

        def addSubModel(self, *_args: object) -> None:
            return None

        def endModel(self) -> None:
            return None

    class FakeTransform:
        def __init__(self, rot: object, trans: object) -> None:
            self.rot = rot
            self.trans = trans

    class FakeCollisionObject:
        def __init__(self, shape: object, transform: object) -> None:
            self.shape = shape
            self.transform = transform

    fake_fcl = types.SimpleNamespace(
        BVHModel=FakeBVHModel,
        CollisionObject=FakeCollisionObject,
        Transform=FakeTransform,
    )
    fake_trimesh = types.SimpleNamespace(
        Trimesh=FakeTrimesh,
        load_mesh=lambda path, force="mesh": FakeTrimesh(),
    )

    monkeypatch.setitem(sys.modules, "fcl", fake_fcl)
    monkeypatch.setitem(sys.modules, "trimesh", fake_trimesh)

    collision_object = geometry_qc._collision_object_from_geometry(
        Mesh(filename=mesh_relpath, scale=(2.0, 3.0, 4.0)),
        elem_tf=(
            (1.0, 0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0, 0.0),
            (0.0, 0.0, 1.0, 0.0),
            (0.0, 0.0, 0.0, 1.0),
        ),
        asset_root=tmp_path,
        mesh_cache={},
    )

    assert isinstance(collision_object, FakeCollisionObject)
    assert applied_scales == [(2.0, 3.0, 4.0)]


def test_find_part_geometry_connectivity_findings_splits_mesh_components(tmp_path: Path) -> None:
    mesh_path = tmp_path / "assets" / "meshes" / "frame.obj"
    _write_disconnected_boxes_obj(mesh_path)

    model = ArticulatedObject(name="mesh_connectivity")
    frame = model.part("frame")
    frame.visual(Mesh(filename=mesh_path.as_posix()), origin=Origin(), name="frame_body")

    findings = geometry_qc.find_part_geometry_connectivity_findings(model)

    assert len(findings) == 1
    finding = findings[0]
    assert finding.part == "frame"
    assert finding.connected == 1
    assert finding.total == 2
    assert len(finding.disconnected) == 1
    assert finding.disconnected[0].startswith("frame_body__component_002:Mesh")
    # Repair hint appended: nearest connected element + gap direction.
    assert "nearest=" in finding.disconnected[0]


def test_find_geometry_overlaps_reports_mesh_component_name(tmp_path: Path) -> None:
    mesh_path = tmp_path / "assets" / "meshes" / "frame.obj"
    _write_disconnected_boxes_obj(mesh_path)

    model = ArticulatedObject(name="mesh_overlap")
    root = model.part("root")
    frame = model.part("frame")
    frame.visual(Mesh(filename=mesh_path.as_posix()), origin=Origin(), name="frame_body")

    blocker = model.part("blocker")
    blocker.visual(
        Box((0.12, 0.12, 0.12)),
        origin=Origin(xyz=(0.45, 0.0, 0.0)),
        name="blocker_box",
    )
    model.articulation(
        "root_to_frame",
        ArticulationType.FIXED,
        parent=root,
        child=frame,
        origin=Origin(),
    )
    model.articulation(
        "root_to_blocker",
        ArticulationType.FIXED,
        parent=root,
        child=blocker,
        origin=Origin(),
    )

    overlaps = geometry_qc.find_geometry_overlaps(
        model,
        max_pose_samples=1,
        overlap_tol=0.001,
        overlap_volume_tol=0.0,
    )

    assert len(overlaps) == 1
    overlap = overlaps[0]
    assert overlap.link_a == "blocker"
    assert overlap.link_b == "frame"
    assert overlap.elem_a_name == "blocker_box"
    assert overlap.elem_b_name == "frame_body__component_002"


def test_default_overlap_volume_tol_from_env_uses_small_nonzero_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OBJECT_GEOMETRY_OVERLAP_VOLUME_TOL", raising=False)
    monkeypatch.delenv("URDF_GEOMETRY_OVERLAP_VOLUME_TOL", raising=False)

    assert geometry_qc.default_overlap_volume_tol_from_env() == pytest.approx(5e-7)


@pytest.mark.parametrize(
    ("penetration", "expected_count"),
    ((0.0, 0), (0.001, 0), (0.005, 0), (0.006, 1)),
)
@pytest.mark.parametrize("angle", (0.0, math.pi / 4.0))
def test_primitive_overlap_uses_inclusive_five_mm_penetration_limit(
    penetration: float,
    expected_count: int,
    angle: float,
) -> None:
    overlaps = geometry_qc.find_geometry_overlaps_in_poses(
        _build_box_pair_model(penetration=penetration, angle=angle),
        poses=[{}],
    )

    assert len(overlaps) == expected_count
    if overlaps:
        assert overlaps[0].penetration_depth == pytest.approx(penetration)
        assert overlaps[0].intersection_volume is not None
        assert overlaps[0].narrow_phase == "fcl_primitive_penetration+manifold_volume"


@pytest.mark.parametrize(("penetration", "expected_count"), ((0.001, 0), (0.006, 1)))
def test_watertight_mesh_overlap_uses_manifold_intersection(
    tmp_path: Path,
    penetration: float,
    expected_count: int,
) -> None:
    mesh_path = tmp_path / "box.obj"
    _write_single_box_obj(mesh_path)
    model = ArticulatedObject(name=f"mesh_pair_{penetration:g}")
    root = model.part("root")
    mesh_part = model.part("mesh_part")
    mesh_part.visual(Mesh(filename=mesh_path.as_posix()), name="mesh")
    primitive_part = model.part("primitive_part")
    primitive_part.visual(Box((0.1, 0.1, 0.1)), name="primitive")
    model.articulation(
        "root_to_mesh",
        ArticulationType.FIXED,
        parent=root,
        child=mesh_part,
    )
    model.articulation(
        "root_to_primitive",
        ArticulationType.FIXED,
        parent=root,
        child=primitive_part,
        origin=Origin(xyz=(0.1 - penetration, 0.0, 0.0)),
    )

    overlaps = geometry_qc.find_geometry_overlaps_in_poses(model, poses=[{}])

    assert len(overlaps) == expected_count
    if overlaps:
        assert overlaps[0].penetration_depth == pytest.approx(penetration, abs=1e-7)
        assert overlaps[0].intersection_volume == pytest.approx(
            penetration * 0.1 * 0.1,
            rel=1e-5,
        )
        assert overlaps[0].narrow_phase == "manifold_intersection"


def test_nonmanifold_mesh_uses_explicit_conservative_fcl_fallback(
    tmp_path: Path,
) -> None:
    mesh_path = tmp_path / "open_box.obj"
    _write_nonmanifold_box_obj(mesh_path)
    model = ArticulatedObject(name="nonmanifold_overlap")
    root = model.part("root")
    mesh_part = model.part("mesh_part")
    mesh_part.visual(Mesh(filename=mesh_path.as_posix()), name="open_box")
    blocker = model.part("blocker")
    blocker.visual(Box((0.1, 0.1, 0.1)), name="blocker")
    model.articulation(
        "root_to_mesh",
        ArticulationType.FIXED,
        parent=root,
        child=mesh_part,
    )
    model.articulation(
        "root_to_blocker",
        ArticulationType.FIXED,
        parent=root,
        child=blocker,
        origin=Origin(xyz=(0.094, 0.0, 0.0)),
    )

    overlaps = geometry_qc.find_geometry_overlaps_in_poses(model, poses=[{}])

    assert len(overlaps) == 1
    assert overlaps[0].narrow_phase == "fcl_conservative_nonmanifold"
    assert overlaps[0].penetration_depth is None
    assert overlaps[0].intersection_volume is None
    assert overlaps[0].overlap_volume > 0.0


@pytest.mark.parametrize(
    ("gap", "unsupported"),
    ((0.0, False), (0.0005, False), (0.001, False), (0.0011, True)),
)
def test_part_support_default_accepts_up_to_one_mm_gap(
    gap: float,
    unsupported: bool,
) -> None:
    findings = geometry_qc.find_unsupported_parts(
        _build_support_gap_model(gap),
        max_pose_samples=1,
    )

    assert bool(findings) is unsupported


def test_collision_scene_reuses_mesh_load_across_checks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mesh_path = tmp_path / "box.obj"
    _write_single_box_obj(mesh_path)
    model = ArticulatedObject(name="shared_collision_scene")
    base = model.part("base")
    base.visual(Box((0.1, 0.1, 0.1)))
    child = model.part("child")
    child.visual(Mesh(filename=mesh_path.as_posix()), name="mesh")
    model.articulation(
        "base_to_child",
        ArticulationType.FIXED,
        parent=base,
        child=child,
        origin=Origin(xyz=(0.2, 0.0, 0.0)),
    )

    original = geometry_qc._load_fcl_mesh_components
    calls = 0

    def counted_load(*args: object, **kwargs: object):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(geometry_qc, "_load_fcl_mesh_components", counted_load)

    geometry_qc.find_unsupported_parts(model, max_pose_samples=1)
    geometry_qc.find_geometry_overlaps(model, max_pose_samples=1)
    geometry_qc.find_part_geometry_connectivity_findings(model)

    assert calls == 1


def test_primitive_provenance_mesh_does_not_load_obj(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    mesh_path = tmp_path / "provenance.obj"
    _write_single_box_obj(mesh_path)
    identity = (
        (1.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )
    model = ArticulatedObject(name="primitive_provenance")
    root = model.part("root")
    derived = model.part("derived")
    derived.visual(
        Mesh(
            filename=mesh_path.as_posix(),
            source_geometry=Box((0.1, 0.1, 0.1)),
            source_transform=identity,
        )
    )
    blocker = model.part("blocker")
    blocker.visual(Box((0.1, 0.1, 0.1)))
    model.articulation(
        "root_to_derived",
        ArticulationType.FIXED,
        parent=root,
        child=derived,
    )
    model.articulation(
        "root_to_blocker",
        ArticulationType.FIXED,
        parent=root,
        child=blocker,
        origin=Origin(xyz=(0.094, 0.0, 0.0)),
    )
    monkeypatch.setattr(
        geometry_qc,
        "_load_fcl_mesh_components",
        lambda *args, **kwargs: pytest.fail("primitive provenance should bypass OBJ loading"),
    )

    overlaps = geometry_qc.find_geometry_overlaps_in_poses(model, poses=[{}])

    assert len(overlaps) == 1
    assert overlaps[0].narrow_phase == "fcl_primitive_penetration+manifold_volume"


def test_collision_scene_cache_is_bounded_and_invalidates_on_inputs(
    tmp_path: Path,
) -> None:
    model = ArticulatedObject(name="scene_cache")
    base = model.part("base")
    base.visual(Box((0.1, 0.1, 0.1)))
    slider = model.part("slider")
    slider.visual(Box((0.1, 0.1, 0.1)))
    model.articulation(
        "slide",
        ArticulationType.PRISMATIC,
        parent=base,
        child=slider,
        origin=Origin(xyz=(0.2, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=1.0,
            velocity=1.0,
            lower=0.0,
            upper=0.01,
        ),
    )
    compiled = geometry_qc.compile_object_model_with_exact_collisions(model)
    scene = geometry_qc._collision_scene_for_model(compiled, asset_root=None)
    for index in range(10):
        scene.pose_view({"slide": index * 0.001})
    assert len(scene._pose_cache) == geometry_qc._COLLISION_POSE_CACHE_SIZE
    other_root_scene = geometry_qc._collision_scene_for_model(
        compiled,
        asset_root=tmp_path,
    )
    assert other_root_scene is not scene

    slider.visual(Box((0.01, 0.01, 0.01)), name="new_detail")
    changed_compiled = geometry_qc.compile_object_model_with_exact_collisions(model)
    changed_scene = geometry_qc._collision_scene_for_model(
        changed_compiled,
        asset_root=None,
    )
    assert changed_compiled is not compiled
    assert changed_scene is not scene


def test_static_and_motion_poses_share_overlap_threshold_semantics() -> None:
    model = ArticulatedObject(name="pose_overlap_semantics")
    base = model.part("base")
    base.visual(Box((0.1, 0.1, 0.1)))
    slider = model.part("slider")
    slider.visual(Box((0.1, 0.1, 0.1)))
    model.articulation(
        "slide",
        ArticulationType.PRISMATIC,
        parent=base,
        child=slider,
        origin=Origin(xyz=(0.095, 0.0, 0.0)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=1.0,
            velocity=1.0,
            lower=0.0,
            upper=0.001,
        ),
    )

    overlaps = geometry_qc.find_geometry_overlaps_in_poses(
        model,
        poses=[{"slide": 0.0}, {"slide": 0.001}],
    )

    assert len(overlaps) == 1
    assert overlaps[0].pose_index == 1
    assert overlaps[0].penetration_depth == pytest.approx(0.006)


def test_default_contact_tol_from_env_is_one_mm(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OBJECT_GEOMETRY_CONTACT_TOL", raising=False)
    monkeypatch.delenv("URDF_GEOMETRY_CONTACT_TOL", raising=False)

    assert geometry_qc.default_contact_tol_from_env() == pytest.approx(0.001)


def test_find_unsupported_parts_keeps_single_mesh_behavior(tmp_path: Path) -> None:
    mesh_path = tmp_path / "assets" / "meshes" / "child.obj"
    _write_single_box_obj(mesh_path)

    model = ArticulatedObject(name="single_mesh_isolated_part")
    base = model.part("base")
    base.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.0, 0.0, 0.05)))

    child = model.part("child")
    child.visual(Mesh(filename=mesh_path.as_posix()), origin=Origin(), name="child_mesh")

    model.articulation(
        "base_to_child",
        ArticulationType.FIXED,
        parent=base,
        child=child,
        origin=Origin(xyz=(0.7, 0.0, 0.0)),
    )

    findings = geometry_qc.find_unsupported_parts(model, max_pose_samples=1)

    assert len(findings) == 1
    assert findings[0].part == "child"


def test_compute_part_world_transforms_applies_floating_origin_pose() -> None:
    model = ArticulatedObject(name="floating_pose_world_tf")

    base = model.part("base")
    base.visual(Box((0.2, 0.2, 0.2)), origin=Origin(xyz=(0.0, 0.0, 0.1)))

    payload = model.part("payload")
    payload.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.0, 0.0, 0.05)))

    free_joint = model.articulation(
        "base_to_payload",
        ArticulationType.FLOATING,
        parent=base,
        child=payload,
        origin=Origin(xyz=(1.0, 0.0, 0.0)),
    )

    world = geometry_qc.compute_part_world_transforms(
        model,
        {free_joint.name: Origin(xyz=(0.25, -0.5, 0.75))},
    )

    payload_tf = world["payload"]
    assert payload_tf[0][3] == pytest.approx(1.25)
    assert payload_tf[1][3] == pytest.approx(-0.5)
    assert payload_tf[2][3] == pytest.approx(0.75)


def test_compute_part_world_transforms_rejects_multiple_root_parts() -> None:
    model = ArticulatedObject(name="multiple_roots_world_tf")

    base = model.part("base")
    base.visual(Box((0.2, 0.2, 0.2)), origin=Origin(xyz=(0.0, 0.0, 0.1)))

    rogue = model.part("rogue")
    rogue.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.0, 0.0, 0.05)))

    with pytest.raises(geometry_qc.ValidationError, match="exactly one root part"):
        geometry_qc.compute_part_world_transforms(model, {})


def test_compute_part_world_transforms_uses_urdf_rpy_order() -> None:
    model = ArticulatedObject(name="fixed_joint_rpy_order")

    base = model.part("base")
    child = model.part("child")
    model.articulation(
        "base_to_child",
        ArticulationType.FIXED,
        parent=base,
        child=child,
        origin=Origin(rpy=(math.pi / 2.0, 0.0, math.pi / 2.0)),
    )

    child_tf = geometry_qc.compute_part_world_transforms(model, {})["child"]

    child_x = tuple(float(child_tf[row][0]) for row in range(3))
    child_y = tuple(float(child_tf[row][1]) for row in range(3))
    child_z = tuple(float(child_tf[row][2]) for row in range(3))
    assert child_x == pytest.approx((0.0, 1.0, 0.0), abs=1e-9)
    assert child_y == pytest.approx((0.0, 0.0, 1.0), abs=1e-9)
    assert child_z == pytest.approx((1.0, 0.0, 0.0), abs=1e-9)


def test_generate_pose_samples_keeps_floating_origin_values() -> None:
    model = ArticulatedObject(name="floating_pose_samples")
    base = model.part("base")
    payload = model.part("payload")
    joint = model.articulation(
        "base_to_payload",
        ArticulationType.FLOATING,
        parent=base,
        child=payload,
        meta={"qc_samples": [Origin(xyz=(0.1, 0.2, 0.3)), Origin(rpy=(0.0, 0.0, 0.4))]},
    )

    poses = geometry_qc.generate_pose_samples(model, max_samples=8, seed=0)

    assert poses[0][joint.name] == Origin()
    assert any(pose[joint.name] == Origin(xyz=(0.1, 0.2, 0.3)) for pose in poses)
    assert any(pose[joint.name] == Origin(rpy=(0.0, 0.0, 0.4)) for pose in poses)


def test_motion_pose_plan_never_truncates_required_continuous_edges() -> None:
    model = ArticulatedObject(name="continuous_edge_coverage")
    parent = model.part("root")
    joint_names: list[str] = []
    for index in range(8):
        child = model.part(f"link_{index}")
        joint = model.articulation(
            f"spin_{index}",
            ArticulationType.CONTINUOUS,
            parent=parent,
            child=child,
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=1.0, velocity=1.0),
        )
        joint_names.append(joint.name)
        parent = child

    plan = geometry_qc.generate_motion_pose_plan(model, max_samples=5, seed=0)
    report = geometry_qc.motion_pose_execution_report(
        plan,
        executed_pose_ids=(case.pose_id for case in plan.cases),
        collision_free=True,
    )

    # Global neutral + three extra representatives per continuous joint.  The
    # five-pose optional budget must not truncate these 25 required poses.
    assert len(plan.cases) == 1 + 3 * len(joint_names)
    assert len(plan.cases) > plan.max_samples
    assert report["status"] == "pass"
    assert report["missing_edges"] == []
    rows = {row["joint"]: row for row in report["joints"]}
    for name in joint_names:
        assert rows[name]["covered_edges"] == [
            "half_turn",
            "negative_quarter",
            "nominal",
            "positive_quarter",
        ]


def test_motion_pose_coverage_only_counts_executed_cases() -> None:
    model = ArticulatedObject(name="bounded_edge_coverage")
    base = model.part("base")
    arm = model.part("arm")
    model.articulation(
        "hinge",
        ArticulationType.REVOLUTE,
        parent=base,
        child=arm,
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=-0.5, upper=0.75),
    )
    plan = geometry_qc.generate_motion_pose_plan(model, max_samples=8, seed=0)

    report = geometry_qc.motion_pose_execution_report(
        plan,
        executed_pose_ids=("neutral", "hinge:lower"),
        collision_free=True,
    )

    assert report["status"] == "fail"
    assert report["missing_pose_ids"] == ["hinge:upper"]
    assert report["missing_edges"] == [
        {
            "joint": "hinge",
            "joint_type": "revolute",
            "edge": "upper",
            "position": 0.75,
        }
    ]


def _bounded_revolute_chain(count: int) -> tuple[ArticulatedObject, list[str]]:
    model = ArticulatedObject(name=f"bounded_chain_{count}")
    parent = model.part("root")
    names: list[str] = []
    for index in range(count):
        child = model.part(f"link_{index}")
        joint = model.articulation(
            f"hinge_{index}",
            ArticulationType.REVOLUTE,
            parent=parent,
            child=child,
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=1.0,
                velocity=1.0,
                lower=-0.5 - 0.1 * index,
                upper=0.75 + 0.1 * index,
            ),
        )
        names.append(joint.name)
        parent = child
    return model, names


def test_motion_pose_plan_caps_automatic_pairs_and_random_poses() -> None:
    model, _ = _bounded_revolute_chain(4)

    plan = geometry_qc.generate_motion_pose_plan(
        model,
        max_samples=100,
        seed=7,
        automatic_pair_pose_cap=8,
        random_pose_cap=2,
    )
    repeated = geometry_qc.generate_motion_pose_plan(
        model,
        max_samples=100,
        seed=7,
        automatic_pair_pose_cap=8,
        random_pose_cap=2,
    )
    next_seed = geometry_qc.generate_motion_pose_plan(
        model,
        max_samples=100,
        seed=8,
        automatic_pair_pose_cap=8,
        random_pose_cap=2,
    )
    kinds = [case.kind for case in plan.cases]

    assert sum(kind == "neutral" for kind in kinds) == 1
    assert sum(kind == "single_joint_edge" for kind in kinds) == 8
    assert sum(kind == "automatic_pair" for kind in kinds) <= 6
    assert sum(kind == "random" for kind in kinds) <= 2
    assert len(plan.cases) <= 17
    assert [case.to_dict() for case in repeated.cases] == [case.to_dict() for case in plan.cases]
    assert [case.pose for case in next_seed.cases if case.kind == "automatic_pair"] != [
        case.pose for case in plan.cases if case.kind == "automatic_pair"
    ]


def test_motion_pose_plan_samples_explicit_homogeneous_repeat_group() -> None:
    model = ArticulatedObject(name="repeated_keys")
    keybed = model.part("keybed")
    names: list[str] = []
    for index in range(20):
        key = model.part(f"key_{index}")
        joint = model.articulation(
            f"key_press_{index}",
            ArticulationType.PRISMATIC,
            parent=keybed,
            child=key,
            origin=Origin(xyz=(float(index % 5), float(index // 5), 0.0)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(
                effort=1.0,
                velocity=1.0,
                lower=0.0,
                upper=0.004,
            ),
            meta={"motion_qc_repeat_group": "key_press"},
        )
        names.append(joint.name)
    knob = model.part("knob")
    model.articulation(
        "knob_turn",
        ArticulationType.REVOLUTE,
        parent=keybed,
        child=knob,
        motion_limits=MotionLimits(
            effort=1.0,
            velocity=1.0,
            lower=-0.5,
            upper=0.5,
        ),
    )

    plan = geometry_qc.generate_motion_pose_plan(
        model,
        max_samples=64,
        seed=3,
        automatic_pair_pose_cap=0,
        random_pose_cap=0,
    )
    next_seed = geometry_qc.generate_motion_pose_plan(
        model,
        max_samples=64,
        seed=4,
        automatic_pair_pose_cap=0,
        random_pose_cap=0,
    )

    assert len(plan.repeat_groups) == 1
    group = plan.repeat_groups[0]
    assert group["member_count"] == 20
    assert group["sampled_count"] == 12
    assert set(group["sampled_joints"]).issubset(names)
    assert group["sampled_joints"] != next_seed.repeat_groups[0]["sampled_joints"]
    required_joints = {edge["joint"] for edge in plan.required_edges}
    assert required_joints == set(group["sampled_joints"]) | {"knob_turn"}
    assert len(plan.required_edges) == 2 * (12 + 1)


def test_motion_pose_plan_rejects_heterogeneous_repeat_group() -> None:
    model = ArticulatedObject(name="invalid_repeated_controls")
    base = model.part("base")
    for index, axis in enumerate(((0.0, 0.0, -1.0), (1.0, 0.0, 0.0))):
        child = model.part(f"control_{index}")
        model.articulation(
            f"control_joint_{index}",
            ArticulationType.PRISMATIC,
            parent=base,
            child=child,
            axis=axis,
            motion_limits=MotionLimits(
                effort=1.0,
                velocity=1.0,
                lower=0.0,
                upper=0.004,
            ),
            meta={"motion_qc_repeat_group": "controls"},
        )

    with pytest.raises(geometry_qc.ValidationError, match="homogeneous"):
        geometry_qc.generate_motion_pose_plan(model, seed=0)


def test_motion_pose_plan_projects_declared_interlocks_without_losing_edges() -> None:
    model = ArticulatedObject(name="door_before_slide")
    body = model.part("body")
    door = model.part("door")
    rack = model.part("rack")
    door_joint = model.articulation(
        "door_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=-1.5, upper=0.0),
    )
    rack_joint = model.articulation(
        "rack_slide",
        ArticulationType.PRISMATIC,
        parent=body,
        child=rack,
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=1.0, lower=0.0, upper=0.4),
    )
    model.meta["motion_interlocks"] = [
        {
            "controller_joint": door_joint.name,
            "controller_required_position": 0.0,
            "dependent_joints": [rack_joint.name],
        }
    ]

    plan = geometry_qc.generate_motion_pose_plan(
        model,
        max_samples=32,
        seed=3,
        automatic_pair_pose_cap=8,
        random_pose_cap=2,
    )

    for case in plan.cases:
        if case.pose[rack_joint.name] != 0.0:
            assert case.pose[door_joint.name] == 0.0
    assert any(
        case.pose[door_joint.name] == -1.5 and case.pose[rack_joint.name] == 0.0
        for case in plan.cases
    )
    assert any(
        case.pose[rack_joint.name] == 0.4 and case.pose[door_joint.name] == 0.0
        for case in plan.cases
    )


def test_motion_pose_plan_keeps_authored_risk_and_explicit_coupling_required() -> None:
    model, names = _bounded_revolute_chain(4)
    model.meta["risk_poses"] = [{names[0]: 0.2, names[3]: 0.3}]
    model.meta["coupled_joint_pairs"] = [(names[0], names[2])]

    plan = geometry_qc.generate_motion_pose_plan(
        model,
        max_samples=1,
        seed=0,
        automatic_pair_pose_cap=0,
        random_pose_cap=0,
    )
    report = geometry_qc.motion_pose_execution_report(
        plan,
        executed_pose_ids=(case.pose_id for case in plan.cases),
        collision_free=True,
    )
    kinds = [case.kind for case in plan.cases]

    assert sum(kind == "authored_risk" for kind in kinds) == 1
    assert sum(kind == "explicit_coupled" for kind in kinds) == 4
    assert all(case.required for case in plan.cases)
    assert len(plan.cases) > plan.max_samples
    assert report["schema_version"] == 2
    assert report["required_pose_kind_counts"] == {
        "authored_risk": 1,
        "explicit_coupled": 4,
        "neutral": 1,
        "single_joint_edge": 8,
    }
    assert report["executed_pose_kind_counts"] == report["required_pose_kind_counts"]


def test_compute_part_world_transforms_applies_mimic_pose() -> None:
    model = ArticulatedObject(name="mimic_pose_world_tf")

    base = model.part("base")
    base.visual(Box((0.2, 0.2, 0.2)), origin=Origin(xyz=(0.0, 0.0, 0.1)))

    carriage = model.part("carriage")
    carriage.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.0, 0.0, 0.05)))

    tool = model.part("tool")
    tool.visual(Box((0.08, 0.08, 0.08)), origin=Origin(xyz=(0.0, 0.0, 0.04)))

    driver = model.articulation(
        "base_to_carriage",
        ArticulationType.PRISMATIC,
        parent=base,
        child=carriage,
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=0.0, upper=0.4),
    )
    model.articulation(
        "carriage_to_tool",
        ArticulationType.PRISMATIC,
        parent=carriage,
        child=tool,
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=0.0, upper=0.4),
        mimic=Mimic(joint=driver.name, multiplier=0.5, offset=0.05),
    )

    world = geometry_qc.compute_part_world_transforms(model, {driver.name: 0.2})

    carriage_tf = world["carriage"]
    tool_tf = world["tool"]
    assert carriage_tf[0][3] == pytest.approx(0.2)
    assert tool_tf[0][3] == pytest.approx(0.35)


def test_compute_part_world_transforms_rejects_direct_mimic_pose() -> None:
    model = ArticulatedObject(name="mimic_direct_pose_rejected")
    base = model.part("base")
    carriage = model.part("carriage")
    tool = model.part("tool")
    driver = model.articulation(
        "base_to_carriage",
        ArticulationType.PRISMATIC,
        parent=base,
        child=carriage,
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=0.0, upper=0.4),
    )
    follower = model.articulation(
        "carriage_to_tool",
        ArticulationType.PRISMATIC,
        parent=carriage,
        child=tool,
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=0.0, upper=0.4),
        mimic=Mimic(joint=driver.name),
    )

    with pytest.raises(geometry_qc.ValidationError, match="cannot be posed directly"):
        geometry_qc.compute_part_world_transforms(model, {follower.name: 0.1})
