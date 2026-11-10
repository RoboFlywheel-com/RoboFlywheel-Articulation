# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math
import os
import random
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from ._mesh_provenance import decompose_mesh_primitive_provenance
from .assets import resolve_asset_root, resolve_mesh_path
from .errors import ValidationError
from .exact_collisions import compile_object_model_with_exact_collisions
from .types import ArticulationType, Box, Cylinder, Mesh, Origin, Part, Sphere

Vec3 = Tuple[float, float, float]
AABB = Tuple[Vec3, Vec3]
Mat3 = Tuple[Vec3, Vec3, Vec3]
Mat4 = Tuple[Tuple[float, float, float, float], ...]

_EPS = 1e-9
_COLLISION_SCENE_CACHE_ATTR = "_sdk_geometry_qc_collision_scenes"
_COLLISION_POSE_CACHE_SIZE = 4


def _dot(a: Vec3, b: Vec3) -> float:
    return float(a[0] * b[0] + a[1] * b[1] + a[2] * b[2])


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _aabb_center(aabb: AABB) -> Vec3:
    (mn, mx) = aabb
    return ((mn[0] + mx[0]) * 0.5, (mn[1] + mx[1]) * 0.5, (mn[2] + mx[2]) * 0.5)


def _aabb_size(aabb: AABB) -> Vec3:
    (mn, mx) = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


@dataclass(frozen=True)
class _OBB:
    center: Vec3
    axes: Mat3  # orthonormal axes in world coordinates
    half_extents: Vec3


def _mat4_axes(mat: Mat4) -> Mat3:
    # Columns of the rotation part represent the world direction of the local basis axes.
    ax = (mat[0][0], mat[1][0], mat[2][0])
    ay = (mat[0][1], mat[1][1], mat[2][1])
    az = (mat[0][2], mat[1][2], mat[2][2])
    return (_normalize(ax), _normalize(ay), _normalize(az))


def _obb_from_local_aabb_and_tf(local_aabb: AABB, tf: Mat4) -> _OBB:
    (mn, mx) = local_aabb
    center_local = ((mn[0] + mx[0]) * 0.5, (mn[1] + mx[1]) * 0.5, (mn[2] + mx[2]) * 0.5)
    half = ((mx[0] - mn[0]) * 0.5, (mx[1] - mn[1]) * 0.5, (mx[2] - mn[2]) * 0.5)
    return _OBB(center=_mat4_vec3(tf, center_local), axes=_mat4_axes(tf), half_extents=half)


def _obb_overlaps(a: _OBB, b: _OBB) -> bool:
    """
    Separating Axis Theorem OBB-vs-OBB overlap test.

    This is still conservative with respect to the true underlying geometry (especially meshes),
    but substantially less conservative than using world-axis AABBs for rotated parts.
    """

    # Rotation matrix expressing B in A's frame: R[i][j] = Ai dot Bj.
    r = [[_dot(a.axes[i], b.axes[j]) for j in range(3)] for i in range(3)]
    abs_r = [[abs(r[i][j]) + _EPS for j in range(3)] for i in range(3)]

    # Translation in A's frame.
    t_world = _sub(b.center, a.center)
    t = [_dot(t_world, a.axes[i]) for i in range(3)]

    a_e = a.half_extents
    b_e = b.half_extents

    # Test axes L = A0, A1, A2
    for i in range(3):
        ra = a_e[i]
        rb = b_e[0] * abs_r[i][0] + b_e[1] * abs_r[i][1] + b_e[2] * abs_r[i][2]
        if abs(t[i]) > ra + rb:
            return False

    # Test axes L = B0, B1, B2
    for j in range(3):
        ra = a_e[0] * abs_r[0][j] + a_e[1] * abs_r[1][j] + a_e[2] * abs_r[2][j]
        rb = b_e[j]
        tj = t[0] * r[0][j] + t[1] * r[1][j] + t[2] * r[2][j]
        if abs(tj) > ra + rb:
            return False

    # Test axis L = Ai x Bj
    for i in range(3):
        i1 = (i + 1) % 3
        i2 = (i + 2) % 3
        for j in range(3):
            j1 = (j + 1) % 3
            j2 = (j + 2) % 3
            ra = a_e[i1] * abs_r[i2][j] + a_e[i2] * abs_r[i1][j]
            rb = b_e[j1] * abs_r[i][j2] + b_e[j2] * abs_r[i][j1]
            t_ij = abs(t[i2] * r[i1][j] - t[i1] * r[i2][j])
            if t_ij > ra + rb:
                return False

    return True


def _rpy_matrix(roll: float, pitch: float, yaw: float) -> Mat3:
    cr = math.cos(roll)
    sr = math.sin(roll)
    cp = math.cos(pitch)
    sp = math.sin(pitch)
    cy = math.cos(yaw)
    sy = math.sin(yaw)

    # R = Rz(yaw) * Ry(pitch) * Rx(roll)
    return (
        (cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr),
        (sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr),
        (-sp, cp * sr, cp * cr),
    )


def _mat3_vec3(mat: Mat3, vec: Vec3) -> Vec3:
    x, y, z = vec
    return (
        mat[0][0] * x + mat[0][1] * y + mat[0][2] * z,
        mat[1][0] * x + mat[1][1] * y + mat[1][2] * z,
        mat[2][0] * x + mat[2][1] * y + mat[2][2] * z,
    )


def _mat4_mul(a: Mat4, b: Mat4) -> Mat4:
    out: list[list[float]] = [[0.0] * 4 for _ in range(4)]
    for i in range(4):
        for j in range(4):
            out[i][j] = (
                a[i][0] * b[0][j] + a[i][1] * b[1][j] + a[i][2] * b[2][j] + a[i][3] * b[3][j]
            )
    return tuple(tuple(row) for row in out)  # type: ignore[return-value]


def _mat4_vec3(mat: Mat4, vec: Vec3) -> Vec3:
    x, y, z = vec
    tx = mat[0][0] * x + mat[0][1] * y + mat[0][2] * z + mat[0][3]
    ty = mat[1][0] * x + mat[1][1] * y + mat[1][2] * z + mat[1][3]
    tz = mat[2][0] * x + mat[2][1] * y + mat[2][2] * z + mat[2][3]
    return (tx, ty, tz)


def _identity4() -> Mat4:
    return (
        (1.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0),
        (0.0, 0.0, 0.0, 1.0),
    )


def _origin_to_mat4(origin: Origin) -> Mat4:
    ox, oy, oz = origin.xyz
    rr, rp, ry = origin.rpy
    r = _rpy_matrix(float(rr), float(rp), float(ry))
    return (
        (r[0][0], r[0][1], r[0][2], float(ox)),
        (r[1][0], r[1][1], r[1][2], float(oy)),
        (r[2][0], r[2][1], r[2][2], float(oz)),
        (0.0, 0.0, 0.0, 1.0),
    )


def _norm(v: Vec3) -> float:
    x, y, z = float(v[0]), float(v[1]), float(v[2])
    return math.sqrt(x * x + y * y + z * z)


def _normalize(v: Vec3) -> Vec3:
    x, y, z = float(v[0]), float(v[1]), float(v[2])
    n = math.sqrt(x * x + y * y + z * z)
    if n <= 0:
        return (0.0, 0.0, 0.0)
    return (x / n, y / n, z / n)


def _axis_angle_matrix(axis: Vec3, angle: float) -> Mat3:
    ax = _normalize(axis)
    if abs(ax[0]) <= _EPS and abs(ax[1]) <= _EPS and abs(ax[2]) <= _EPS:
        raise ValidationError("Articulation axis must be non-zero")
    x, y, z = ax
    c = math.cos(angle)
    s = math.sin(angle)
    t = 1.0 - c
    return (
        (t * x * x + c, t * x * y - s * z, t * x * z + s * y),
        (t * x * y + s * z, t * y * y + c, t * y * z - s * x),
        (t * x * z - s * y, t * y * z + s * x, t * z * z + c),
    )


def _mat3_to_mat4(rot: Mat3, *, translation: Vec3 = (0.0, 0.0, 0.0)) -> Mat4:
    tx, ty, tz = translation
    return (
        (rot[0][0], rot[0][1], rot[0][2], float(tx)),
        (rot[1][0], rot[1][1], rot[1][2], float(ty)),
        (rot[2][0], rot[2][1], rot[2][2], float(tz)),
        (0.0, 0.0, 0.0, 1.0),
    )


def _aabb_intersection_depth(a: AABB, b: AABB) -> Vec3:
    (amin_x, amin_y, amin_z), (amax_x, amax_y, amax_z) = a
    (bmin_x, bmin_y, bmin_z), (bmax_x, bmax_y, bmax_z) = b
    dx = min(amax_x, bmax_x) - max(amin_x, bmin_x)
    dy = min(amax_y, bmax_y) - max(amin_y, bmin_y)
    dz = min(amax_z, bmax_z) - max(amin_z, bmin_z)
    return (dx, dy, dz)


def _aabb_intersection_volume(a: AABB, b: AABB) -> float:
    dx, dy, dz = _aabb_intersection_depth(a, b)
    if dx <= 0 or dy <= 0 or dz <= 0:
        return 0.0
    return float(dx * dy * dz)


def _aabb_min_distance(a: AABB, b: AABB) -> float:
    """Lower bound of the true distance between the shapes inside two AABBs.

    Per-axis gap is 0 when the intervals overlap; the Euclidean norm of the
    gaps never exceeds the exact FCL distance, so `gap > tol` proves the exact
    query would also exceed `tol` — the broad-phase cull that keeps the O(N^2)
    pairwise QC loops from drowning in far-pair narrow-phase queries on
    high-multiplicity templates (chains, fences, blinds)."""
    (amin_x, amin_y, amin_z), (amax_x, amax_y, amax_z) = a
    (bmin_x, bmin_y, bmin_z), (bmax_x, bmax_y, bmax_z) = b
    gx = max(bmin_x - amax_x, amin_x - bmax_x, 0.0)
    gy = max(bmin_y - amax_y, amin_y - bmax_y, 0.0)
    gz = max(bmin_z - amax_z, amin_z - bmax_z, 0.0)
    return math.sqrt(gx * gx + gy * gy + gz * gz)


# Pairs whose AABB gap exceeds this skip exact distance queries entirely (the
# AABB lower bound is recorded instead — accurate enough for "disconnected,
# nearest ~X" reporting); pairs closer than this keep exact narrow-phase
# accuracy for near-miss reporting.
_FAR_PAIR_CULL_DISTANCE = 0.05


def _aabbs_touch_or_overlap(a: AABB, b: AABB, *, tol: float) -> bool:
    (amin_x, amin_y, amin_z), (amax_x, amax_y, amax_z) = a
    (bmin_x, bmin_y, bmin_z), (bmax_x, bmax_y, bmax_z) = b
    return not (
        (amax_x < bmin_x - tol)
        or (bmax_x < amin_x - tol)
        or (amax_y < bmin_y - tol)
        or (bmax_y < amin_y - tol)
        or (amax_z < bmin_z - tol)
        or (bmax_z < amin_z - tol)
    )


def _aabb_separation_distance(a: AABB, b: AABB) -> float:
    (amin_x, amin_y, amin_z), (amax_x, amax_y, amax_z) = a
    (bmin_x, bmin_y, bmin_z), (bmax_x, bmax_y, bmax_z) = b
    dx = max(0.0, bmin_x - amax_x, amin_x - bmax_x)
    dy = max(0.0, bmin_y - amax_y, amin_y - bmax_y)
    dz = max(0.0, bmin_z - amax_z, amin_z - bmax_z)
    return float(math.sqrt(dx * dx + dy * dy + dz * dz))


def _obj_aabb(path: Path) -> AABB:
    min_x = min_y = min_z = float("inf")
    max_x = max_y = max_z = float("-inf")
    found = False
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if not line.startswith("v "):
            continue
        parts = line.split()
        if len(parts) < 4:
            continue
        try:
            x = float(parts[1])
            y = float(parts[2])
            z = float(parts[3])
        except ValueError:
            continue
        found = True
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        min_z = min(min_z, z)
        max_x = max(max_x, x)
        max_y = max(max_y, y)
        max_z = max(max_z, z)

    if not found:
        raise ValidationError(f"OBJ contains no vertices: {path} (is this a valid .obj file?)")
    return (min_x, min_y, min_z), (max_x, max_y, max_z)


@dataclass(frozen=True)
class GeometryOverlap:
    pose_index: int
    pose: Dict[str, float]
    link_a: str
    link_b: str
    elem_a: int
    elem_b: int
    overlap_depth: Vec3
    overlap_volume: float
    aabb_a: AABB
    aabb_b: AABB
    elem_a_name: Optional[str] = None
    elem_b_name: Optional[str] = None
    elem_a_origin: Optional[Origin] = None
    elem_b_origin: Optional[Origin] = None
    elem_a_geometry: Optional[str] = None
    elem_b_geometry: Optional[str] = None
    penetration_depth: Optional[float] = None
    intersection_volume: Optional[float] = None
    narrow_phase: str = "fcl_conservative"


@dataclass(frozen=True)
class UnsupportedPartFinding:
    pose_index: int
    pose: Dict[str, float]
    part: str
    nearest_part: Optional[str]
    min_distance: Optional[float]
    contact_tol: float
    backend: str
    parts: Tuple[str, ...] = ()
    root_parts: Tuple[str, ...] = ()


@dataclass(frozen=True)
class JointOriginDistanceFinding:
    joint: str
    parent: str
    child: str
    parent_distance: float
    child_distance: float
    tol: float
    # Anchor semantics actually applied (see find_joint_origin_distance_findings):
    # "axis" for revolute/continuous (distances are axis-segment distances),
    # "point" for fixed. Center distances are the axis-to-part-AABB-center
    # perpendicular distances (the symmetry-centerline clause); inf for "point".
    joint_type: str = ""
    metric: str = "point"
    parent_center_distance: float = float("inf")
    child_center_distance: float = float("inf")


@dataclass(frozen=True)
class PartGeometryConnectivityFinding:
    part: str
    connected: int
    total: int
    disconnected: Tuple[str, ...]
    contact_tol: float


@dataclass(frozen=True)
class JointMatingGapFinding:
    """One articulation whose MatingContract resolves to two face centers that
    are farther apart in world coordinates than the declared contact_tol."""

    joint: str
    parent: str
    child: str
    parent_face_geometry: str
    parent_face_side: str
    child_face_geometry: str
    child_face_side: str
    parent_face_world: Vec3
    child_face_world: Vec3
    distance: float
    contact_tol: float
    reason: str = ""
    # "fail" (default) or "warn" — dry-run tangential findings are warnings:
    # surfaced in reports, never gate generation.
    severity: str = "fail"


@dataclass(frozen=True)
class _MeshComponentCollision:
    local_aabb: AABB
    shape: object
    index: int
    total: int
    manifold: object | None = None


@dataclass(frozen=True)
class _CompiledCollisionEntry:
    item: object
    collision_obj: object
    aabb: AABB
    name: Optional[str]
    geometry_name: str
    origin: Origin
    entry_id: str = ""
    elem_tf: Optional[Mat4] = None
    local_manifold: object | None = None
    exact_primitive: bool = False


@dataclass(frozen=True)
class _LocalCollisionEntry:
    item: object
    shape: object
    local_aabb: AABB
    elem_local_tf: Mat4
    name: Optional[str]
    geometry_name: str
    origin: Origin
    entry_id: str
    local_manifold: object | None
    exact_primitive: bool


@dataclass
class _CollisionPairMetrics:
    collided: bool
    distance: Optional[float]
    penetration_depth: Optional[float]
    contact_normals: Tuple[Vec3, ...]


@dataclass
class _CollisionPoseView:
    entries_by_part: Dict[str, List[_CompiledCollisionEntry]]
    pair_metrics: Dict[Tuple[str, str], _CollisionPairMetrics]


def _rotation_is_identityish(tf: Mat4, *, tol: float = 1e-6) -> bool:
    """True when the transform's 3x3 rotation block is (numerically) identity."""
    for r in range(3):
        for c in range(3):
            expected = 1.0 if r == c else 0.0
            if abs(tf[r][c] - expected) > tol:
                return False
    return True


def _rpy_is_zeroish(origin: object, *, tol: float = 1e-9) -> bool:
    rpy = getattr(origin, "rpy", (0.0, 0.0, 0.0))
    return all(abs(float(v)) <= tol for v in rpy)


def _transform_aabb(aabb: AABB, tf: Mat4) -> AABB:
    (min_x, min_y, min_z), (max_x, max_y, max_z) = aabb
    corners = [(x, y, z) for x in (min_x, max_x) for y in (min_y, max_y) for z in (min_z, max_z)]
    tx0 = ty0 = tz0 = float("inf")
    tx1 = ty1 = tz1 = float("-inf")
    for c in corners:
        x, y, z = _mat4_vec3(tf, c)
        tx0 = min(tx0, x)
        ty0 = min(ty0, y)
        tz0 = min(tz0, z)
        tx1 = max(tx1, x)
        ty1 = max(ty1, y)
        tz1 = max(tz1, z)
    return (tx0, ty0, tz0), (tx1, ty1, tz1)


def _geometry_local_aabb(
    geometry: object,
    *,
    asset_root: Optional[Path],
    _obj_cache: Dict[Path, AABB],
) -> AABB:

    if isinstance(geometry, Box):
        sx, sy, sz = geometry.size
        return (-sx / 2.0, -sy / 2.0, -sz / 2.0), (sx / 2.0, sy / 2.0, sz / 2.0)
    if isinstance(geometry, Cylinder):
        r = float(geometry.radius)
        length = float(geometry.length)
        return (-r, -r, -length / 2.0), (r, r, length / 2.0)
    if isinstance(geometry, Sphere):
        r = float(geometry.radius)
        return (-r, -r, -r), (r, r, r)
    if isinstance(geometry, Mesh):
        filename = geometry.filename
        if not isinstance(filename, (str, os.PathLike)):
            raise ValidationError("Mesh geometry filename is missing")
        filename = os.fspath(filename)
        if not filename:
            raise ValidationError("Mesh geometry filename is missing")

        mesh_path = resolve_mesh_path(filename, assets=asset_root)
        if not mesh_path.exists():
            raise ValidationError(f"Mesh file not found: {mesh_path}")
        if mesh_path.suffix.lower() != ".obj":
            raise ValidationError(
                f"Only OBJ meshes are supported for geometry QC (got: {mesh_path.name!r}). "
                "Convert the mesh to .obj or disable the overlap check."
            )

        aabb = _obj_cache.get(mesh_path)
        if aabb is None:
            aabb = _obj_aabb(mesh_path)
            _obj_cache[mesh_path] = aabb

        local_min, local_max = aabb
        if geometry.scale:
            sx, sy, sz = geometry.scale
            local_min = (local_min[0] * sx, local_min[1] * sy, local_min[2] * sz)
            local_max = (local_max[0] * sx, local_max[1] * sy, local_max[2] * sz)
        return local_min, local_max

    raise ValidationError(f"Unsupported geometry type: {type(geometry).__name__}")


def part_local_aabbs(
    part: Part,
    *,
    asset_root: Optional[Path] = None,
    prefer_collisions: bool = True,
    _obj_cache: Optional[Dict[Path, AABB]] = None,
) -> List[AABB]:
    obj_cache: Dict[Path, AABB] = _obj_cache if _obj_cache is not None else {}
    geoms: list[object] = []
    if prefer_collisions and part.collisions:
        geoms = list(part.collisions)
    else:
        geoms = list(part.visuals)

    aabbs: list[AABB] = []
    for item in geoms:
        origin = getattr(item, "origin", Origin())
        geometry = getattr(item, "geometry", None)
        if geometry is None:
            continue
        local_aabb = _geometry_local_aabb(geometry, asset_root=asset_root, _obj_cache=obj_cache)
        aabbs.append(_transform_aabb(local_aabb, _origin_to_mat4(origin)))
    return aabbs


def link_local_aabbs(
    link: Part,
    *,
    asset_root: Optional[Path] = None,
    prefer_collisions: bool = True,
    _obj_cache: Optional[Dict[Path, AABB]] = None,
) -> List[AABB]:
    return part_local_aabbs(
        link,
        asset_root=asset_root,
        prefer_collisions=prefer_collisions,
        _obj_cache=_obj_cache,
    )


def part_world_aabb(
    part: Part,
    link_world_tf: Mat4,
    *,
    asset_root: Optional[Path] = None,
    prefer_collisions: bool = True,
    _obj_cache: Optional[Dict[Path, AABB]] = None,
) -> Optional[AABB]:
    local = part_local_aabbs(
        part,
        asset_root=asset_root,
        prefer_collisions=prefer_collisions,
        _obj_cache=_obj_cache,
    )
    if not local:
        return None

    mins = [float("inf"), float("inf"), float("inf")]
    maxs = [float("-inf"), float("-inf"), float("-inf")]
    for aabb in local:
        waabb = _transform_aabb(aabb, link_world_tf)
        (mn, mx) = waabb
        for i in range(3):
            mins[i] = min(mins[i], mn[i])
            maxs[i] = max(maxs[i], mx[i])
    return (mins[0], mins[1], mins[2]), (maxs[0], maxs[1], maxs[2])


def link_world_aabb(
    link: Part,
    link_world_tf: Mat4,
    *,
    asset_root: Optional[Path] = None,
    prefer_collisions: bool = True,
    _obj_cache: Optional[Dict[Path, AABB]] = None,
) -> Optional[AABB]:
    return part_world_aabb(
        link,
        link_world_tf,
        asset_root=asset_root,
        prefer_collisions=prefer_collisions,
        _obj_cache=_obj_cache,
    )


def _mat4_rotation_translation(
    mat: Mat4,
) -> tuple[tuple[tuple[float, float, float], ...], tuple[float, float, float]]:
    rot = (
        (float(mat[0][0]), float(mat[0][1]), float(mat[0][2])),
        (float(mat[1][0]), float(mat[1][1]), float(mat[1][2])),
        (float(mat[2][0]), float(mat[2][1]), float(mat[2][2])),
    )
    trans = (float(mat[0][3]), float(mat[1][3]), float(mat[2][3]))
    return rot, trans


def _load_fcl_mesh(
    mesh_path: Path,
    *,
    cache: Dict[tuple[Path, Optional[Vec3]], object],
    scale: Optional[Vec3] = None,
) -> object:
    cache_key = (mesh_path, None if scale is None else tuple(float(v) for v in scale))
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    import fcl
    import trimesh

    loaded = trimesh.load_mesh(mesh_path, force="mesh")
    if not isinstance(loaded, trimesh.Trimesh):
        raise ValidationError(f"Expected mesh geometry at {mesh_path}, got {type(loaded).__name__}")
    if loaded.vertices.size == 0:
        raise ValidationError(f"OBJ contains no vertices: {mesh_path}")
    if loaded.faces.size == 0:
        raise ValidationError(f"OBJ contains no triangles: {mesh_path}")
    if scale is not None:
        loaded = loaded.copy()
        loaded.apply_scale(scale)
    model = fcl.BVHModel()
    model.beginModel(len(loaded.vertices), len(loaded.faces))
    model.addSubModel(loaded.vertices, loaded.faces)
    model.endModel()
    cache[cache_key] = model
    return model


def _mesh_component_suffix(index: int) -> str:
    return f"__component_{index + 1:03d}"


def _mesh_component_name(name: object, *, index: int, total: int) -> Optional[str]:
    base_name = str(name).strip() if isinstance(name, str) and str(name).strip() else None
    if total <= 1:
        return base_name
    if base_name is None:
        return f"mesh{_mesh_component_suffix(index)}"
    return f"{base_name}{_mesh_component_suffix(index)}"


def _mesh_local_aabb(mesh: object) -> AABB:
    bounds = getattr(mesh, "bounds", None)
    if bounds is None:
        raise ValidationError("Mesh component is missing bounds")
    return (
        (float(bounds[0][0]), float(bounds[0][1]), float(bounds[0][2])),
        (float(bounds[1][0]), float(bounds[1][1]), float(bounds[1][2])),
    )


def _build_fcl_bvh_model(mesh: object) -> object:
    import fcl

    vertices = getattr(mesh, "vertices", None)
    faces = getattr(mesh, "faces", None)
    if vertices is None or getattr(vertices, "size", 0) == 0:
        raise ValidationError("Mesh component contains no vertices")
    if faces is None or getattr(faces, "size", 0) == 0:
        raise ValidationError("Mesh component contains no triangles")
    model = fcl.BVHModel()
    model.beginModel(len(vertices), len(faces))
    model.addSubModel(vertices, faces)
    model.endModel()
    return model


def _manifold_from_trimesh(mesh: object) -> object | None:
    """Best-effort solid representation used only after FCL reports a collision."""

    try:
        import manifold3d as m3d
        import numpy as np

        if not bool(getattr(mesh, "is_watertight", False)):
            return None
        solid_mesh = mesh.copy()
        signed_volume = float(getattr(solid_mesh, "volume", 0.0))
        if abs(signed_volume) <= _EPS:
            return None
        if signed_volume < 0.0:
            solid_mesh.invert()
        vertices = np.asarray(getattr(solid_mesh, "vertices"), dtype=np.float32)
        faces = np.asarray(getattr(solid_mesh, "faces"), dtype=np.uint32)
        manifold = m3d.Manifold(m3d.Mesh(vertices, faces))
        if (
            manifold.status() != m3d.Error.NoError
            or manifold.is_empty()
            or float(manifold.volume()) <= _EPS
        ):
            return None
        return manifold
    except Exception:
        return None


def _primitive_manifold(geometry: object) -> object | None:
    try:
        import manifold3d as m3d

        if isinstance(geometry, Box):
            return m3d.Manifold.cube(tuple(float(v) for v in geometry.size), center=True)
        if isinstance(geometry, Cylinder):
            return m3d.Manifold.cylinder(
                float(geometry.length),
                float(geometry.radius),
                center=True,
            )
        if isinstance(geometry, Sphere):
            return m3d.Manifold.sphere(float(geometry.radius))
    except Exception:
        return None
    return None


def _load_fcl_mesh_components(
    mesh_path: Path,
    *,
    cache: Dict[tuple[Path, Optional[Vec3]], object],
    scale: Optional[Vec3] = None,
) -> tuple[_MeshComponentCollision, ...]:
    cache_key = (
        "components",
        mesh_path,
        None if scale is None else tuple(float(v) for v in scale),
    )
    cached = cache.get(cache_key)
    if isinstance(cached, tuple):
        return cached

    import trimesh

    loaded = trimesh.load_mesh(mesh_path, force="mesh")
    if not isinstance(loaded, trimesh.Trimesh):
        raise ValidationError(f"Expected mesh geometry at {mesh_path}, got {type(loaded).__name__}")
    if loaded.vertices.size == 0:
        raise ValidationError(f"OBJ contains no vertices: {mesh_path}")
    if loaded.faces.size == 0:
        raise ValidationError(f"OBJ contains no triangles: {mesh_path}")
    if scale is not None:
        loaded = loaded.copy()
        loaded.apply_scale(scale)

    # Do not let trimesh silently close small holes while splitting. FCL can
    # still use an open component, but exact solid intersection must retain
    # the fact that the authored mesh was non-manifold.
    raw_components = list(loaded.split(only_watertight=False, repair=False))
    components = [
        component
        for component in raw_components
        if getattr(component, "vertices", None) is not None
        and getattr(component.vertices, "size", 0) > 0
        and getattr(component, "faces", None) is not None
        and getattr(component.faces, "size", 0) > 0
    ]
    if not components:
        components = [loaded]

    total = len(components)
    resolved = tuple(
        _MeshComponentCollision(
            local_aabb=_mesh_local_aabb(component),
            shape=_build_fcl_bvh_model(component),
            index=index,
            total=total,
            manifold=_manifold_from_trimesh(component),
        )
        for index, component in enumerate(components)
    )
    cache[cache_key] = resolved
    return resolved


def _collision_object_from_shape(shape: object, *, elem_tf: Mat4) -> object:
    import fcl

    rot, trans = _mat4_rotation_translation(elem_tf)
    return fcl.CollisionObject(shape, fcl.Transform(rot, trans))


def _collision_object_from_geometry(
    geometry: object,
    *,
    elem_tf: Mat4,
    asset_root: Optional[Path],
    mesh_cache: Dict[tuple[Path, Optional[Vec3]], object],
) -> object:
    import fcl

    if isinstance(geometry, Box):
        shape = fcl.Box(*[float(v) for v in geometry.size])
    elif isinstance(geometry, Cylinder):
        shape = fcl.Cylinder(float(geometry.radius), float(geometry.length))
    elif isinstance(geometry, Sphere):
        shape = fcl.Sphere(float(geometry.radius))
    elif isinstance(geometry, Mesh):
        filename = os.fspath(geometry.filename)
        mesh_path = resolve_mesh_path(filename, assets=asset_root)
        if mesh_path.suffix.lower() != ".obj":
            raise ValidationError(
                f"Only OBJ meshes are supported for geometry QC (got: {mesh_path.name!r})."
            )
        scale = None
        if geometry.scale is not None:
            scale = tuple(float(v) for v in geometry.scale)
        shape = _load_fcl_mesh(mesh_path, cache=mesh_cache, scale=scale)
    else:
        raise ValidationError(f"Unsupported geometry type: {type(geometry).__name__}")

    return _collision_object_from_shape(shape, elem_tf=elem_tf)


def _point_collision_object(point: Vec3, *, radius: float = 1e-9) -> object:
    import fcl

    rot = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    return fcl.CollisionObject(
        fcl.Sphere(float(radius)),
        fcl.Transform(rot, (float(point[0]), float(point[1]), float(point[2]))),
    )


def _collision_pair_metrics(obj_a: object, obj_b: object) -> tuple[bool, float]:
    import fcl

    collision_request = fcl.CollisionRequest()
    collision_result = fcl.CollisionResult()
    if int(fcl.collide(obj_a, obj_b, collision_request, collision_result)) > 0:
        return True, 0.0

    distance_request = fcl.DistanceRequest()
    distance_result = fcl.DistanceResult()
    return False, float(fcl.distance(obj_a, obj_b, distance_request, distance_result))


def _compiled_part_collision_entries(
    part: Part,
    *,
    asset_root: Optional[Path],
    mesh_cache: Dict[tuple[Path, Optional[Vec3]], object],
    part_tf: Optional[Mat4] = None,
) -> list[_CompiledCollisionEntry]:
    resolved_part_tf = _identity4() if part_tf is None else part_tf
    obj_cache: Dict[Path, AABB] = {}
    entries: list[_CompiledCollisionEntry] = []
    for item in list(getattr(part, "collisions", []) or []):
        geometry = getattr(item, "geometry", None)
        if geometry is None:
            continue
        origin = getattr(item, "origin", Origin())
        elem_tf = _mat4_mul(resolved_part_tf, _origin_to_mat4(origin))
        geometry_name = type(geometry).__name__
        if isinstance(geometry, Mesh):
            filename = os.fspath(geometry.filename)
            mesh_path = resolve_mesh_path(filename, assets=asset_root)
            scale = None
            if geometry.scale is not None:
                scale = tuple(float(v) for v in geometry.scale)
            for component in _load_fcl_mesh_components(
                mesh_path,
                cache=mesh_cache,
                scale=scale,
            ):
                entries.append(
                    _CompiledCollisionEntry(
                        item=item,
                        collision_obj=_collision_object_from_shape(
                            component.shape, elem_tf=elem_tf
                        ),
                        aabb=_transform_aabb(component.local_aabb, elem_tf),
                        name=_mesh_component_name(
                            getattr(item, "name", None),
                            index=component.index,
                            total=component.total,
                        ),
                        geometry_name=geometry_name,
                        origin=origin,
                    )
                )
            continue

        local_aabb = _geometry_local_aabb(
            geometry,
            asset_root=asset_root,
            _obj_cache=obj_cache,
        )
        entries.append(
            _CompiledCollisionEntry(
                item=item,
                collision_obj=_collision_object_from_geometry(
                    geometry,
                    elem_tf=elem_tf,
                    asset_root=asset_root,
                    mesh_cache=mesh_cache,
                ),
                aabb=_transform_aabb(local_aabb, elem_tf),
                name=getattr(item, "name", None),
                geometry_name=geometry_name,
                origin=origin,
            )
        )
    return entries


def _fcl_shape_from_primitive(geometry: object) -> object:
    import fcl

    if isinstance(geometry, Box):
        return fcl.Box(*[float(v) for v in geometry.size])
    if isinstance(geometry, Cylinder):
        return fcl.Cylinder(float(geometry.radius), float(geometry.length))
    if isinstance(geometry, Sphere):
        return fcl.Sphere(float(geometry.radius))
    raise ValidationError(f"Unsupported primitive collision geometry: {type(geometry).__name__}")


def _build_local_part_collision_entries(
    part: Part,
    *,
    asset_root: Optional[Path],
    mesh_cache: Dict[tuple[object, ...], object],
) -> list[_LocalCollisionEntry]:
    obj_cache: Dict[Path, AABB] = {}
    entries: list[_LocalCollisionEntry] = []
    part_name = str(getattr(part, "name", "part"))
    for item_index, item in enumerate(list(getattr(part, "collisions", []) or [])):
        geometry = getattr(item, "geometry", None)
        if geometry is None:
            continue
        origin = getattr(item, "origin", Origin())
        item_tf = _origin_to_mat4(origin)
        geometry_name = type(geometry).__name__

        if isinstance(geometry, Mesh):
            decomposed = decompose_mesh_primitive_provenance(geometry)
            if decomposed is not None:
                primitive, source_tf = decomposed
                elem_tf = _mat4_mul(item_tf, source_tf)
                entries.append(
                    _LocalCollisionEntry(
                        item=item,
                        shape=_fcl_shape_from_primitive(primitive),
                        local_aabb=_geometry_local_aabb(
                            primitive,
                            asset_root=asset_root,
                            _obj_cache=obj_cache,
                        ),
                        elem_local_tf=elem_tf,
                        name=getattr(item, "name", None),
                        geometry_name=geometry_name,
                        origin=origin,
                        entry_id=f"{part_name}:{item_index}:0",
                        local_manifold=_primitive_manifold(primitive),
                        exact_primitive=True,
                    )
                )
                continue

            filename = os.fspath(geometry.filename)
            mesh_path = resolve_mesh_path(filename, assets=asset_root)
            scale = (
                None
                if geometry.scale is None
                else tuple(float(v) for v in geometry.scale)
            )
            for component in _load_fcl_mesh_components(
                mesh_path,
                cache=mesh_cache,  # type: ignore[arg-type]
                scale=scale,
            ):
                entries.append(
                    _LocalCollisionEntry(
                        item=item,
                        shape=component.shape,
                        local_aabb=component.local_aabb,
                        elem_local_tf=item_tf,
                        name=_mesh_component_name(
                            getattr(item, "name", None),
                            index=component.index,
                            total=component.total,
                        ),
                        geometry_name=geometry_name,
                        origin=origin,
                        entry_id=f"{part_name}:{item_index}:{component.index}",
                        local_manifold=component.manifold,
                        exact_primitive=False,
                    )
                )
            continue

        if isinstance(geometry, (Box, Cylinder, Sphere)):
            entries.append(
                _LocalCollisionEntry(
                    item=item,
                    shape=_fcl_shape_from_primitive(geometry),
                    local_aabb=_geometry_local_aabb(
                        geometry,
                        asset_root=asset_root,
                        _obj_cache=obj_cache,
                    ),
                    elem_local_tf=item_tf,
                    name=getattr(item, "name", None),
                    geometry_name=geometry_name,
                    origin=origin,
                    entry_id=f"{part_name}:{item_index}:0",
                    local_manifold=_primitive_manifold(geometry),
                    exact_primitive=True,
                )
            )
            continue
        raise ValidationError(f"Unsupported geometry type: {type(geometry).__name__}")
    return entries


def _collision_pose_key(pose: Dict[str, object]) -> tuple[tuple[str, str], ...]:
    return tuple(sorted((str(name), repr(value)) for name, value in pose.items()))


class _CollisionScene:
    """Compiled local collision shapes plus a small cache of world-pose views."""

    def __init__(self, model: object, *, asset_root: Optional[Path]) -> None:
        self.model = model
        self.asset_root = asset_root
        links = getattr(model, "parts", None)
        if not isinstance(links, list):
            raise ValidationError("model must expose a .parts list")
        self._mesh_cache: Dict[tuple[object, ...], object] = {}
        self._local_by_part: Dict[str, list[_LocalCollisionEntry]] = {}
        for link in links:
            name = getattr(link, "name", None)
            if not isinstance(name, str):
                continue
            self._local_by_part[name] = _build_local_part_collision_entries(
                link,
                asset_root=asset_root,
                mesh_cache=self._mesh_cache,
            )
        self._pose_cache: OrderedDict[
            tuple[tuple[str, str], ...], _CollisionPoseView
        ] = OrderedDict()

    def pose_view(self, pose: Dict[str, object]) -> _CollisionPoseView:
        key = _collision_pose_key(pose)
        cached = self._pose_cache.get(key)
        if cached is not None:
            self._pose_cache.move_to_end(key)
            return cached

        transforms = compute_part_world_transforms(self.model, pose)
        entries_by_part: Dict[str, List[_CompiledCollisionEntry]] = {}
        for part_name, local_entries in self._local_by_part.items():
            part_tf = transforms.get(part_name, _identity4())
            world_entries: list[_CompiledCollisionEntry] = []
            for local in local_entries:
                elem_tf = _mat4_mul(part_tf, local.elem_local_tf)
                world_entries.append(
                    _CompiledCollisionEntry(
                        item=local.item,
                        collision_obj=_collision_object_from_shape(
                            local.shape,
                            elem_tf=elem_tf,
                        ),
                        aabb=_transform_aabb(local.local_aabb, elem_tf),
                        name=local.name,
                        geometry_name=local.geometry_name,
                        origin=local.origin,
                        entry_id=local.entry_id,
                        elem_tf=elem_tf,
                        local_manifold=local.local_manifold,
                        exact_primitive=local.exact_primitive,
                    )
                )
            if world_entries:
                entries_by_part[part_name] = world_entries

        view = _CollisionPoseView(entries_by_part=entries_by_part, pair_metrics={})
        self._pose_cache[key] = view
        self._pose_cache.move_to_end(key)
        while len(self._pose_cache) > _COLLISION_POSE_CACHE_SIZE:
            self._pose_cache.popitem(last=False)
        return view

    def pair_metrics(
        self,
        view: _CollisionPoseView,
        entry_a: _CompiledCollisionEntry,
        entry_b: _CompiledCollisionEntry,
        *,
        need_distance: bool,
    ) -> _CollisionPairMetrics:
        key = tuple(sorted((entry_a.entry_id, entry_b.entry_id)))
        cached = view.pair_metrics.get(key)
        if cached is None:
            import fcl

            request = fcl.CollisionRequest(num_max_contacts=64, enable_contact=True)
            result = fcl.CollisionResult()
            collided = int(
                fcl.collide(
                    entry_a.collision_obj,
                    entry_b.collision_obj,
                    request,
                    result,
                )
            ) > 0
            depths: list[float] = []
            normals: list[Vec3] = []
            for contact in list(getattr(result, "contacts", ()) or ()):
                depth = getattr(contact, "penetration_depth", None)
                if isinstance(depth, (int, float)) and math.isfinite(float(depth)):
                    depths.append(max(0.0, float(depth)))
                normal = getattr(contact, "normal", None)
                if normal is not None and len(normal) >= 3:
                    candidate = (float(normal[0]), float(normal[1]), float(normal[2]))
                    if _norm(candidate) > _EPS:
                        normals.append(_normalize(candidate))
            cached = _CollisionPairMetrics(
                collided=collided,
                distance=0.0 if collided else None,
                penetration_depth=max(depths) if depths else (0.0 if collided else None),
                contact_normals=tuple(normals),
            )
            view.pair_metrics[key] = cached

        if need_distance and not cached.collided and cached.distance is None:
            import fcl

            request = fcl.DistanceRequest()
            result = fcl.DistanceResult()
            cached.distance = float(
                fcl.distance(
                    entry_a.collision_obj,
                    entry_b.collision_obj,
                    request,
                    result,
                )
            )
        return cached


def _collision_scene_for_model(
    compiled_model: object,
    *,
    asset_root: Optional[Path],
) -> _CollisionScene:
    root_key = "" if asset_root is None else str(Path(asset_root).resolve())
    cache = getattr(compiled_model, _COLLISION_SCENE_CACHE_ATTR, None)
    if not isinstance(cache, dict):
        cache = {}
        setattr(compiled_model, _COLLISION_SCENE_CACHE_ATTR, cache)
    scene = cache.get(root_key)
    if not isinstance(scene, _CollisionScene):
        scene = _CollisionScene(compiled_model, asset_root=asset_root)
        cache[root_key] = scene
    return scene


def compute_part_world_transforms(
    model: object,
    joint_positions: Dict[str, object],
) -> Dict[str, Mat4]:
    links = getattr(model, "parts", None)
    if not isinstance(links, list):
        links = getattr(model, "links", None)
    joints = getattr(model, "articulations", None)
    if not isinstance(joints, list):
        joints = getattr(model, "joints", None)
    if not isinstance(links, list) or not isinstance(joints, list):
        raise ValidationError("model must have .parts and .articulations lists")

    link_names = [getattr(link, "name", None) for link in links]
    if not all(isinstance(n, str) for n in link_names):
        raise ValidationError("model.parts must have string names")
    if len(set(link_names)) != len(link_names):
        raise ValidationError("model.parts must have unique names")
    link_name_set = set(link_names)  # type: ignore[arg-type]

    child_set: set[str] = set()
    parent_to_children: Dict[str, List[object]] = {name: [] for name in link_name_set}  # type: ignore[arg-type]
    for j in joints:
        parent = getattr(j, "parent", None)
        child = getattr(j, "child", None)
        if not isinstance(parent, str) or not isinstance(child, str):
            raise ValidationError("articulations must have string parent/child names")
        if parent not in link_name_set:
            raise ValidationError(f"Articulation references missing parent part {parent!r}")
        if child not in link_name_set:
            raise ValidationError(f"Articulation references missing child part {child!r}")
        if child in child_set:
            raise ValidationError(f"Part {child!r} has multiple parent articulations")
        parent_to_children.setdefault(parent, []).append(j)
        child_set.add(child)

    roots = sorted(link_name_set - child_set)
    if not roots:
        raise ValidationError(
            "Articulated object has no root part (cycle or every part is a child)"
        )
    if len(roots) > 1:
        raise ValidationError(
            "Articulated object must have exactly one root part for world-frame "
            f"computations; found multiple root parts: {roots}"
        )

    root = roots[0]
    world: Dict[str, Mat4] = {root: _identity4()}
    resolved_joint_positions = _resolve_joint_positions(model, joint_positions)
    visited: set[str] = set()
    queue: List[str] = [root]

    while queue:
        parent_link = queue.pop(0)
        if parent_link in visited:
            continue
        visited.add(parent_link)
        parent_tf = world[parent_link]
        for joint in parent_to_children.get(parent_link, []):
            child = getattr(joint, "child", None)
            if not isinstance(child, str):
                continue
            joint_origin = getattr(joint, "origin", Origin())
            joint_tf = _origin_to_mat4(joint_origin)

            motion_tf = _identity4()
            joint_type = getattr(joint, "articulation_type", None)
            axis = getattr(joint, "axis", (0.0, 0.0, 1.0))
            pose_value = resolved_joint_positions.get(
                getattr(joint, "name", ""), _joint_zero_pose_value(joint)
            )

            if joint_type in (ArticulationType.REVOLUTE, ArticulationType.CONTINUOUS):
                q = float(pose_value)
                rot = _axis_angle_matrix(_normalize(axis), q)
                motion_tf = _mat3_to_mat4(rot)
            elif joint_type == ArticulationType.PRISMATIC:
                q = float(pose_value)
                ax = _normalize(axis)
                motion_tf = _mat3_to_mat4(
                    ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
                    translation=(ax[0] * q, ax[1] * q, ax[2] * q),
                )
            elif joint_type == ArticulationType.FLOATING:
                motion_tf = _origin_to_mat4(pose_value)
            elif joint_type == ArticulationType.FIXED:
                motion_tf = _identity4()
            else:
                motion_tf = _identity4()

            child_tf = _mat4_mul(_mat4_mul(parent_tf, joint_tf), motion_tf)
            if child in world:
                raise ValidationError(f"Part {child!r} was reached multiple times")
            world[child] = child_tf
            queue.append(child)

    if visited != link_name_set:
        missing = sorted(link_name_set - visited)
        raise ValidationError(
            "Articulated object contains unreachable parts (cycle or broken articulations): "
            f"{missing}"
        )
    return world


def _coerce_origin_pose_value(value: object, *, joint_name: str) -> Origin:
    if isinstance(value, Origin):
        return value
    xyz = getattr(value, "xyz", None)
    rpy = getattr(value, "rpy", None)
    if xyz is not None and rpy is not None:
        try:
            return Origin(xyz=xyz, rpy=rpy)
        except Exception as exc:  # pragma: no cover - defensive conversion guard
            raise ValidationError(
                f"Articulation {joint_name!r} expects an Origin pose value"
            ) from exc
    raise ValidationError(f"Articulation {joint_name!r} expects an Origin pose value")


def _joint_zero_pose_value(joint: object) -> object:
    if getattr(joint, "articulation_type", None) == ArticulationType.FLOATING:
        return Origin()
    return 0.0


def _resolve_joint_positions(
    model: object, joint_positions: Dict[str, object]
) -> Dict[str, object]:
    joints = getattr(model, "articulations", None)
    if not isinstance(joints, list):
        joints = getattr(model, "joints", None)
    if not isinstance(joints, list):
        raise ValidationError("model must have an .articulations list")

    joint_lookup = {
        name: joint for joint in joints if isinstance((name := getattr(joint, "name", None)), str)
    }
    resolved: Dict[str, object] = {}
    resolving: list[str] = []

    def resolve_joint(name: str) -> object:
        if name in resolved:
            return resolved[name]
        joint = joint_lookup.get(name)
        if joint is None:
            raise ValidationError(f"Unknown articulation: {name!r}")
        if name in resolving:
            cycle_start = resolving.index(name)
            cycle = resolving[cycle_start:] + [name]
            raise ValidationError(f"Mimic cycle detected: {' -> '.join(cycle)}")

        resolving.append(name)
        mimic = getattr(joint, "mimic", None)
        if mimic is not None:
            if name in joint_positions:
                raise ValidationError(
                    f"Articulation {name!r} is mimic-driven and cannot be posed directly"
                )
            source_name = str(getattr(mimic, "joint", "")).strip()
            source_value = resolve_joint(source_name)
            if isinstance(source_value, Origin):
                raise ValidationError(
                    f"Articulation {name!r} mimic source {source_name!r} must use scalar poses"
                )
            value = float(source_value) * float(getattr(mimic, "multiplier", 1.0)) + float(
                getattr(mimic, "offset", 0.0)
            )
        else:
            value = _coerce_joint_pose_value(
                joint,
                joint_positions.get(name, _joint_zero_pose_value(joint)),
            )
        resolving.pop()
        resolved[name] = value
        return value

    for name in joint_lookup:
        resolve_joint(name)
    return resolved


def _coerce_joint_pose_value(joint: object, value: object) -> object:
    joint_name = str(getattr(joint, "name", ""))
    joint_type = getattr(joint, "articulation_type", None)
    if joint_type == ArticulationType.FLOATING:
        return _coerce_origin_pose_value(value, joint_name=joint_name)
    if isinstance(value, Origin) or (hasattr(value, "xyz") and hasattr(value, "rpy")):
        raise ValidationError(
            f"Articulation {joint_name!r} expects a scalar pose value, not Origin(...)"
        )
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(f"Articulation {joint_name!r} expects a scalar pose value") from exc


def _pose_value_key(value: object) -> object:
    if isinstance(value, Origin):
        return ("origin", value.xyz, value.rpy)
    return float(value)


def _pose_value_is_zero(value: object) -> bool:
    if isinstance(value, Origin):
        return all(abs(float(v)) <= 1e-12 for v in (*value.xyz, *value.rpy))
    return abs(float(value)) <= 1e-12


def compute_link_world_transforms(
    model: object,
    joint_positions: Dict[str, object],
) -> Dict[str, Mat4]:
    return compute_part_world_transforms(model, joint_positions)


def _joint_sample_values(joint: object) -> List[object]:
    joint_type = getattr(joint, "articulation_type", None)
    motion_limits = getattr(joint, "motion_limits", None)
    if joint_type == ArticulationType.FIXED:
        return [0.0]

    meta = getattr(joint, "meta", None)
    raw = meta.get("qc_samples", meta.get("qc_sample_values")) if isinstance(meta, dict) else None

    if joint_type == ArticulationType.FLOATING:
        values: list[Origin] = [Origin()]
        if isinstance(raw, (list, tuple)) and raw:
            for v in raw[:32]:
                try:
                    pose_value = _coerce_joint_pose_value(joint, v)
                except ValidationError:
                    continue
                if isinstance(pose_value, Origin) and pose_value not in values:
                    values.append(pose_value)
        return list(values)

    if isinstance(raw, (list, tuple)) and raw:
        values: list[float] = [0.0]
        for v in raw[:32]:
            if isinstance(v, (int, float)):
                values.append(float(v))
        out: list[float] = []
        for v in values:
            if not any(abs(v - u) <= 1e-9 for u in out):
                out.append(v)
        return list(out)

    if joint_type == ArticulationType.CONTINUOUS:
        return [0.0, -math.pi / 2.0, math.pi / 2.0, math.pi]

    lower = getattr(motion_limits, "lower", None) if motion_limits is not None else None
    upper = getattr(motion_limits, "upper", None) if motion_limits is not None else None
    values: list[float] = [0.0]
    if isinstance(lower, (int, float)):
        values.append(float(lower))
    if isinstance(upper, (int, float)):
        values.append(float(upper))
    if isinstance(lower, (int, float)) and isinstance(upper, (int, float)):
        values.append(0.5 * (float(lower) + float(upper)))
    out: list[float] = []
    for v in values:
        if not any(abs(v - u) <= 1e-9 for u in out):
            out.append(v)
    return list(out)


@dataclass(frozen=True)
class MotionPoseCase:
    """One concrete pose executed by motion QC."""

    pose_id: str
    kind: str
    required: bool
    pose: Dict[str, object]
    covers: Tuple[Dict[str, object], ...] = ()

    def to_dict(self) -> Dict[str, object]:
        return {
            "pose_id": self.pose_id,
            "kind": self.kind,
            "required": self.required,
            "pose": dict(self.pose),
            "covers": [dict(item) for item in self.covers],
        }


@dataclass(frozen=True)
class MotionPosePlan:
    """Required joint edges plus budgeted multi-joint exploration poses."""

    cases: Tuple[MotionPoseCase, ...]
    required_edges: Tuple[Dict[str, object], ...]
    max_samples: int
    repeat_groups: Tuple[Dict[str, object], ...] = ()

    @property
    def poses(self) -> List[Dict[str, object]]:
        return [dict(case.pose) for case in self.cases]

    @property
    def required_pose_ids(self) -> Tuple[str, ...]:
        return tuple(case.pose_id for case in self.cases if case.required)


def motion_pose_execution_report(
    plan: MotionPosePlan,
    *,
    executed_pose_ids: Iterable[str],
    collision_free: bool,
) -> Dict[str, object]:
    """Build coverage exclusively from pose IDs the collision gate executed."""

    executed = tuple(dict.fromkeys(str(item) for item in executed_pose_ids))
    executed_set = set(executed)
    required_pose_ids = plan.required_pose_ids
    missing_pose_ids = tuple(item for item in required_pose_ids if item not in executed_set)
    covered_edges: dict[tuple[str, str], Dict[str, object]] = {}
    for case in plan.cases:
        if case.pose_id not in executed_set:
            continue
        for edge in case.covers:
            key = (str(edge.get("joint") or ""), str(edge.get("edge") or ""))
            covered_edges[key] = dict(edge)
    required_edges = {
        (str(edge.get("joint") or ""), str(edge.get("edge") or "")): dict(edge)
        for edge in plan.required_edges
    }
    missing_edges = [
        required_edges[key] for key in sorted(required_edges) if key not in covered_edges
    ]
    joint_rows: dict[tuple[str, str], dict[str, object]] = {}
    for edge in plan.required_edges:
        key = (str(edge.get("joint") or ""), str(edge.get("joint_type") or ""))
        row = joint_rows.setdefault(
            key,
            {
                "joint": key[0],
                "joint_type": key[1],
                "required_edges": [],
                "covered_edges": [],
            },
        )
        row["required_edges"].append(str(edge.get("edge") or ""))  # type: ignore[union-attr]
    for edge in covered_edges.values():
        key = (str(edge.get("joint") or ""), str(edge.get("joint_type") or ""))
        row = joint_rows.get(key)
        if row is not None:
            row["covered_edges"].append(str(edge.get("edge") or ""))  # type: ignore[union-attr]
    for row in joint_rows.values():
        row["required_edges"] = sorted(set(row["required_edges"]))  # type: ignore[arg-type]
        row["covered_edges"] = sorted(set(row["covered_edges"]))  # type: ignore[arg-type]
    executed_kind_counts: dict[str, int] = {}
    required_kind_counts: dict[str, int] = {}
    for case in plan.cases:
        if case.required:
            required_kind_counts[case.kind] = required_kind_counts.get(case.kind, 0) + 1
        if case.pose_id in executed_set:
            executed_kind_counts[case.kind] = executed_kind_counts.get(case.kind, 0) + 1
    coverage_complete = not missing_pose_ids and not missing_edges
    return {
        "schema_version": 2,
        "status": "pass" if collision_free and coverage_complete else "fail",
        "collision_free": bool(collision_free),
        "required_pose_ids": list(required_pose_ids),
        "executed_pose_ids": list(executed),
        "missing_pose_ids": list(missing_pose_ids),
        "required_edges": [dict(edge) for edge in plan.required_edges],
        "covered_edges": [covered_edges[key] for key in sorted(covered_edges)],
        "missing_edges": missing_edges,
        "joints": [joint_rows[key] for key in sorted(joint_rows)],
        "required_pose_kind_counts": dict(sorted(required_kind_counts.items())),
        "executed_pose_kind_counts": dict(sorted(executed_kind_counts.items())),
        "repeat_groups": [dict(group) for group in plan.repeat_groups],
        "poses": [case.to_dict() for case in plan.cases],
    }


def _joint_type_text(joint: object) -> str:
    joint_type = getattr(joint, "articulation_type", None)
    return str(getattr(joint_type, "value", joint_type or "")).lower()


def _legal_neutral_value(joint: object) -> object:
    if getattr(joint, "articulation_type", None) == ArticulationType.FLOATING:
        return Origin()
    joint_type = _joint_type_text(joint)
    if joint_type not in {"revolute", "prismatic"}:
        return 0.0
    limits = getattr(joint, "motion_limits", None)
    lower = getattr(limits, "lower", None) if limits is not None else None
    upper = getattr(limits, "upper", None) if limits is not None else None
    if isinstance(lower, (int, float)) and 0.0 < float(lower):
        return float(lower)
    if isinstance(upper, (int, float)) and 0.0 > float(upper):
        return float(upper)
    return 0.0


def _motion_interlocks(
    model: object,
    joint_names: Sequence[str],
) -> Tuple[Tuple[int, float, Tuple[int, ...]], ...]:
    """Resolve simple controller-before-dependent motion requirements.

    A template may declare ``model.meta["motion_interlocks"]`` entries with a
    controller joint, the controller position required for operation, and one
    or more dependent joints.  Whenever a sampled dependent leaves its legal
    neutral position, the controller is projected to that required position.
    This keeps endpoint coverage while avoiding impossible operation orders,
    such as pulling a dishwasher rack through a closed door.
    """

    meta = getattr(model, "meta", {})
    raw_specs = meta.get("motion_interlocks", ()) if isinstance(meta, dict) else ()
    if raw_specs in (None, ()):
        return ()
    if not isinstance(raw_specs, (list, tuple)):
        raise ValidationError("motion_interlocks must be a list of mappings")

    name_to_index = {name: index for index, name in enumerate(joint_names)}
    resolved: list[Tuple[int, float, Tuple[int, ...]]] = []
    for spec_index, raw_spec in enumerate(raw_specs):
        if not isinstance(raw_spec, dict):
            raise ValidationError(f"motion_interlocks[{spec_index}] must be a mapping")
        controller_name = raw_spec.get("controller_joint")
        required_position = raw_spec.get("controller_required_position")
        dependent_names = raw_spec.get("dependent_joints")
        if not isinstance(controller_name, str) or controller_name not in name_to_index:
            raise ValidationError(
                f"motion_interlocks[{spec_index}].controller_joint must name an independent joint"
            )
        if not isinstance(required_position, (int, float)):
            raise ValidationError(
                f"motion_interlocks[{spec_index}].controller_required_position must be scalar"
            )
        if not isinstance(dependent_names, (list, tuple)) or not dependent_names:
            raise ValidationError(
                f"motion_interlocks[{spec_index}].dependent_joints must be a non-empty list"
            )
        dependent_indices: list[int] = []
        for dependent_name in dependent_names:
            if not isinstance(dependent_name, str) or dependent_name not in name_to_index:
                raise ValidationError(
                    f"motion_interlocks[{spec_index}] names an unknown dependent joint"
                )
            dependent_index = name_to_index[dependent_name]
            if dependent_index == name_to_index[controller_name]:
                raise ValidationError(
                    f"motion_interlocks[{spec_index}] cannot depend on its controller"
                )
            if dependent_index not in dependent_indices:
                dependent_indices.append(dependent_index)
        resolved.append(
            (
                name_to_index[controller_name],
                float(required_position),
                tuple(dependent_indices),
            )
        )
    return tuple(resolved)


def _apply_motion_interlocks(
    values: Sequence[object],
    neutral_values: Sequence[object],
    interlocks: Sequence[Tuple[int, float, Tuple[int, ...]]],
) -> list[object]:
    projected = list(values)
    for controller_index, required_position, dependent_indices in interlocks:
        if any(
            _pose_value_key(projected[index]) != _pose_value_key(neutral_values[index])
            for index in dependent_indices
        ):
            projected[controller_index] = required_position
    return projected


def _motion_edge(
    joint: object,
    *,
    edge: str,
    position: float,
) -> Dict[str, object]:
    return {
        "joint": str(getattr(joint, "name", "")),
        "joint_type": _joint_type_text(joint),
        "edge": edge,
        "position": float(position),
    }


_MOTION_QC_REPEAT_GROUP_KEY = "motion_qc_repeat_group"
_MOTION_QC_REPEAT_GROUP_SAMPLE_CAP = 12


def _repeat_group_joint_indexes(
    independent_joints: Sequence[object],
    *,
    seed: int,
) -> tuple[set[int], tuple[Dict[str, object], ...]]:
    """Select collision-QC representatives from explicitly tagged repeat groups.

    The tag is an opt-in contract for a homogeneous sibling mechanism family,
    such as independently articulated keys.  Every untagged joint remains
    exhaustive.  Representatives preserve spatial extremes and center, then
    rotate the remaining sample across seeds.
    """

    grouped: dict[str, list[int]] = {}
    for index, joint in enumerate(independent_joints):
        meta = getattr(joint, "meta", None)
        raw_group = meta.get(_MOTION_QC_REPEAT_GROUP_KEY) if isinstance(meta, dict) else None
        if raw_group is None:
            continue
        if not isinstance(raw_group, str) or not raw_group.strip():
            raise ValidationError(
                f"joint {getattr(joint, 'name', '?')!r} has an invalid "
                f"{_MOTION_QC_REPEAT_GROUP_KEY}; expected a non-empty string"
            )
        grouped.setdefault(raw_group.strip(), []).append(index)

    sampled_indexes: set[int] = set(range(len(independent_joints)))
    reports: list[Dict[str, object]] = []
    for group_name in sorted(grouped):
        indexes = grouped[group_name]
        first = independent_joints[indexes[0]]
        expected = (
            _joint_type_text(first),
            str(getattr(first, "parent", "")),
            tuple(round(float(value), 9) for value in getattr(first, "axis", ())),
            (
                getattr(getattr(first, "motion_limits", None), "lower", None),
                getattr(getattr(first, "motion_limits", None), "upper", None),
            ),
        )
        children: set[str] = set()
        points: dict[int, tuple[float, float, float]] = {}
        for index in indexes:
            joint = independent_joints[index]
            actual = (
                _joint_type_text(joint),
                str(getattr(joint, "parent", "")),
                tuple(round(float(value), 9) for value in getattr(joint, "axis", ())),
                (
                    getattr(getattr(joint, "motion_limits", None), "lower", None),
                    getattr(getattr(joint, "motion_limits", None), "upper", None),
                ),
            )
            if actual != expected or actual[0] not in {"revolute", "prismatic"}:
                raise ValidationError(
                    f"motion QC repeat group {group_name!r} must contain homogeneous "
                    "bounded revolute or prismatic sibling joints"
                )
            child = str(getattr(joint, "child", ""))
            if not child or child in children:
                raise ValidationError(
                    f"motion QC repeat group {group_name!r} must use one distinct child per joint"
                )
            children.add(child)
            xyz = getattr(getattr(joint, "origin", None), "xyz", (0.0, 0.0, 0.0))
            points[index] = tuple(float(value) for value in xyz)

        cap = min(_MOTION_QC_REPEAT_GROUP_SAMPLE_CAP, len(indexes))
        selected: list[int] = []

        def select(index: int) -> None:
            if index not in selected and len(selected) < cap:
                selected.append(index)

        if len(indexes) <= cap:
            selected.extend(indexes)
        else:
            # Preserve the six axis extremes and representatives nearest to and
            # farthest from the group centroid before filling by seeded rotation.
            for axis in range(3):
                select(min(indexes, key=lambda item: (points[item][axis], item)))
                select(max(indexes, key=lambda item: (points[item][axis], -item)))
            centroid = tuple(
                sum(points[index][axis] for index in indexes) / len(indexes) for axis in range(3)
            )

            def distance_sq(index: int) -> float:
                return sum((points[index][axis] - centroid[axis]) ** 2 for axis in range(3))

            select(min(indexes, key=lambda item: (distance_sq(item), item)))
            select(max(indexes, key=lambda item: (distance_sq(item), -item)))
            remaining = [index for index in indexes if index not in selected]
            if remaining:
                offset = int(seed) % len(remaining)
                ordered = remaining[offset:] + remaining[:offset]
                slots = cap - len(selected)
                for slot in range(slots):
                    select(ordered[(slot * len(ordered)) // slots])

        selected_set = set(selected)
        sampled_indexes.difference_update(indexes)
        sampled_indexes.update(selected_set)
        reports.append(
            {
                "group": group_name,
                "member_count": len(indexes),
                "sample_cap": _MOTION_QC_REPEAT_GROUP_SAMPLE_CAP,
                "sampled_count": len(selected),
                "sampled_joints": [
                    str(getattr(independent_joints[index], "name", "")) for index in selected
                ],
                "selection": "spatial_extremes_center_seeded_rotation",
            }
        )
    return sampled_indexes, tuple(reports)


def generate_motion_pose_plan(
    model: object,
    *,
    max_samples: int = 256,
    seed: int = 0,
    automatic_pair_pose_cap: int = 8,
    random_pose_cap: int = 2,
) -> MotionPosePlan:
    """Plan required motion edges plus a small deterministic exploration layer.

    Neutral, single-joint edges, authored risk poses, and explicitly coupled
    joint boundaries are required and can exceed ``max_samples``.  Inferred
    adjacent-pair and random poses are optional, capped separately, and also
    respect the remaining ``max_samples`` budget.
    """

    max_samples = int(max_samples)
    if max_samples <= 0:
        raise ValidationError("max_samples must be positive")
    automatic_pair_pose_cap = int(automatic_pair_pose_cap)
    random_pose_cap = int(random_pose_cap)
    if automatic_pair_pose_cap < 0:
        raise ValidationError("automatic_pair_pose_cap must be non-negative")
    if random_pose_cap < 0:
        raise ValidationError("random_pose_cap must be non-negative")

    joints = getattr(model, "articulations", None)
    if not isinstance(joints, list):
        joints = getattr(model, "joints", None)
    if not isinstance(joints, list):
        raise ValidationError("model must have an .articulations list")

    independent_joints: list[object] = []
    joint_names: list[str] = []
    per_joint: list[list[object]] = []
    for j in joints:
        name = getattr(j, "name", None)
        if not isinstance(name, str):
            continue
        if getattr(j, "mimic", None) is not None:
            continue
        independent_joints.append(j)
        joint_names.append(name)
        per_joint.append(_joint_sample_values(j))

    if not joint_names:
        neutral = MotionPoseCase("neutral", "neutral", True, {}, ())
        return MotionPosePlan((neutral,), (), max_samples)

    edge_sample_indexes, repeat_group_reports = _repeat_group_joint_indexes(
        independent_joints,
        seed=seed,
    )
    neutral_values = [_legal_neutral_value(joint) for joint in independent_joints]
    interlocks = _motion_interlocks(model, joint_names)
    builders: list[dict[str, object]] = []
    seen: dict[tuple[object, ...], int] = {}
    required_edges: dict[tuple[str, str], Dict[str, object]] = {}

    def add_pose(
        pose_id: str,
        kind: str,
        values: Sequence[object],
        *,
        required: bool,
        covers: Sequence[Dict[str, object]] = (),
        optional_limit: int | None = None,
    ) -> bool:
        values = _apply_motion_interlocks(values, neutral_values, interlocks)
        key = tuple(_pose_value_key(values[i]) for i in range(len(joint_names)))
        existing_index = seen.get(key)
        if existing_index is not None:
            builder = builders[existing_index]
            builder["required"] = bool(builder["required"]) or required
            existing_covers = builder["covers"]
            assert isinstance(existing_covers, list)
            for cover in covers:
                if cover not in existing_covers:
                    existing_covers.append(dict(cover))
            return True
        if not required and optional_limit is not None and len(builders) >= optional_limit:
            return False
        seen[key] = len(builders)
        builders.append(
            {
                "pose_id": pose_id,
                "kind": kind,
                "required": required,
                "pose": {joint_names[i]: values[i] for i in range(len(joint_names))},
                "covers": [dict(cover) for cover in covers],
            }
        )
        return True

    neutral_covers: list[Dict[str, object]] = []
    for joint in independent_joints:
        if _joint_type_text(joint) == "continuous":
            cover = _motion_edge(joint, edge="nominal", position=0.0)
            neutral_covers.append(cover)
            required_edges[(str(cover["joint"]), str(cover["edge"]))] = cover
    add_pose("neutral", "neutral", neutral_values, required=True, covers=neutral_covers)

    # Required layer: every ungrouped joint is exhaustive.  Explicit homogeneous
    # repeat groups use deterministic representatives for the expensive
    # collision sweep while template-level checks still validate every member.
    for index, joint in enumerate(independent_joints):
        if index not in edge_sample_indexes:
            continue
        name = joint_names[index]
        joint_type = _joint_type_text(joint)
        edge_values: list[tuple[str, float]] = []
        if joint_type in {"revolute", "prismatic"}:
            limits = getattr(joint, "motion_limits", None)
            lower = getattr(limits, "lower", None) if limits is not None else None
            upper = getattr(limits, "upper", None) if limits is not None else None
            if isinstance(lower, (int, float)):
                edge_values.append(("lower", float(lower)))
            if isinstance(upper, (int, float)):
                edge_values.append(("upper", float(upper)))
        elif joint_type == "continuous":
            edge_values.extend(
                (
                    ("negative_quarter", -math.pi / 2.0),
                    ("positive_quarter", math.pi / 2.0),
                    ("half_turn", math.pi),
                )
            )
        for edge, position in edge_values:
            cover = _motion_edge(joint, edge=edge, position=position)
            required_edges[(name, edge)] = cover
            values = list(neutral_values)
            values[index] = position
            add_pose(
                f"{name}:{edge}",
                (
                    "continuous_representative"
                    if joint_type == "continuous"
                    else "single_joint_edge"
                ),
                values,
                required=True,
                covers=(cover,),
            )

    # Authored risk poses express category knowledge and are required regardless
    # of the automatic exploration budget.
    meta = getattr(model, "meta", {})
    raw_risk_poses = meta.get("risk_poses", ()) if isinstance(meta, dict) else ()
    if isinstance(raw_risk_poses, (list, tuple)):
        for risk_index, raw_pose in enumerate(raw_risk_poses):
            if not isinstance(raw_pose, dict):
                continue
            values = list(neutral_values)
            for name, value in raw_pose.items():
                if name in joint_names:
                    values[joint_names.index(name)] = value
            add_pose(
                f"risk:{risk_index}",
                "authored_risk",
                values,
                required=True,
            )

    endpoints = [_joint_endpoint_values(joint) for joint in independent_joints]
    explicit_pairs, adjacent_pairs = _joint_pair_groups(model, joints, joint_names)

    # Explicit coupling is authored mechanism semantics, so all endpoint
    # combinations are required.  Merely sharing a part is weaker evidence and
    # is handled by the bounded automatic layer below.
    for left, right in explicit_pairs:
        for left_value in endpoints[left]:
            for right_value in endpoints[right]:
                pair = list(neutral_values)
                pair[left] = left_value
                pair[right] = right_value
                add_pose(
                    f"coupled:{joint_names[left]}:{joint_names[right]}:{len(builders)}",
                    "explicit_coupled",
                    pair,
                    required=True,
                )

    optional_limit = max(max_samples, len(builders))

    # Give each inferred adjacent pair roughly two endpoint combinations per
    # build, rotate both pair and endpoint order by seed, and cap the whole
    # automatic pair layer.  Across cumulative seeds this spreads coverage
    # without repeating every Cartesian pair at every configuration.
    automatic_pair_target = min(automatic_pair_pose_cap, 2 * len(adjacent_pairs))
    automatic_pair_added = 0
    if adjacent_pairs and automatic_pair_target > 0:
        pair_shift = int(seed) % len(adjacent_pairs)
        ordered_pairs = adjacent_pairs[pair_shift:] + adjacent_pairs[:pair_shift]
        pair_candidates: list[tuple[int, int, object, object]] = []
        max_combinations = max(
            (len(endpoints[left]) * len(endpoints[right]) for left, right in ordered_pairs),
            default=0,
        )
        for round_index in range(max_combinations):
            for pair_index, (left, right) in enumerate(ordered_pairs):
                combinations = [
                    (left_value, right_value)
                    for left_value in endpoints[left]
                    for right_value in endpoints[right]
                ]
                if not combinations:
                    continue
                combination_index = (int(seed) + pair_index + round_index) % len(combinations)
                left_value, right_value = combinations[combination_index]
                pair_candidates.append((left, right, left_value, right_value))

        for candidate_index, (left, right, left_value, right_value) in enumerate(pair_candidates):
            if automatic_pair_added >= automatic_pair_target or len(builders) >= optional_limit:
                break
            pair = list(neutral_values)
            pair[left] = left_value
            pair[right] = right_value
            before = len(builders)
            add_pose(
                f"auto_pair:{joint_names[left]}:{joint_names[right]}:{candidate_index}",
                "automatic_pair",
                pair,
                required=False,
                optional_limit=optional_limit,
            )
            automatic_pair_added += len(builders) - before

    # A very small seeded robustness layer fills gaps that endpoint pairwise
    # poses cannot express.  It is bounded independently from joint count.
    rng = random.Random(int(seed))
    random_target = min(optional_limit, len(builders) + random_pose_cap)
    max_stall = max(64, 16 * max(1, random_pose_cap))
    stall = 0
    while len(builders) < random_target and stall < max_stall:
        sample = [rng.choice(vals) for vals in per_joint]
        before = len(seen)
        add_pose(
            f"random:{len(builders)}",
            "random",
            sample,
            required=False,
            optional_limit=optional_limit,
        )
        stall = 0 if len(seen) > before else stall + 1
    cases = tuple(
        MotionPoseCase(
            pose_id=str(builder["pose_id"]),
            kind=str(builder["kind"]),
            required=bool(builder["required"]),
            pose=dict(builder["pose"]),  # type: ignore[arg-type]
            covers=tuple(dict(item) for item in builder["covers"]),  # type: ignore[arg-type]
        )
        for builder in builders
    )
    return MotionPosePlan(
        cases=cases,
        required_edges=tuple(required_edges[key] for key in sorted(required_edges)),
        max_samples=max_samples,
        repeat_groups=repeat_group_reports,
    )


def generate_pose_samples(
    model: object,
    *,
    max_samples: int = 256,
    seed: int = 0,
) -> List[Dict[str, object]]:
    return generate_motion_pose_plan(model, max_samples=max_samples, seed=seed).poses


def _joint_endpoint_values(joint: object) -> list[object]:
    joint_type = _joint_type_text(joint)
    if joint_type == "continuous":
        return [-math.pi / 2.0, math.pi]
    if joint_type in {"revolute", "prismatic"}:
        limits = getattr(joint, "motion_limits", None)
        values = [
            value
            for value in (
                getattr(limits, "lower", None) if limits is not None else None,
                getattr(limits, "upper", None) if limits is not None else None,
            )
            if isinstance(value, (int, float))
        ]
        return list(dict.fromkeys(float(value) for value in values))
    return [value for value in _joint_sample_values(joint) if value != _legal_neutral_value(joint)][
        :2
    ]


def _joint_pair_groups(
    model: object,
    joints: Sequence[object],
    joint_names: Sequence[str],
) -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    by_name = {name: index for index, name in enumerate(joint_names)}
    independent = [joint for joint in joints if getattr(joint, "name", None) in by_name]
    adjacent_pairs: set[tuple[int, int]] = set()
    for left_index, left_joint in enumerate(independent):
        left_name = str(getattr(left_joint, "name"))
        left_parts = {
            str(value)
            for value in (getattr(left_joint, "parent", None), getattr(left_joint, "child", None))
            if isinstance(value, str)
        }
        for right_joint in independent[left_index + 1 :]:
            right_name = str(getattr(right_joint, "name"))
            right_parts = {
                str(value)
                for value in (
                    getattr(right_joint, "parent", None),
                    getattr(right_joint, "child", None),
                )
                if isinstance(value, str)
            }
            if left_parts.intersection(right_parts):
                pair = tuple(sorted((by_name[left_name], by_name[right_name])))
                adjacent_pairs.add(pair)

    meta = getattr(model, "meta", {})
    raw_pairs = meta.get("coupled_joint_pairs", ()) if isinstance(meta, dict) else ()
    explicit_pairs: set[tuple[int, int]] = set()
    if isinstance(raw_pairs, (list, tuple)):
        for raw_pair in raw_pairs:
            if (
                isinstance(raw_pair, (list, tuple))
                and len(raw_pair) == 2
                and raw_pair[0] in by_name
                and raw_pair[1] in by_name
            ):
                explicit_pairs.add(
                    tuple(sorted((by_name[str(raw_pair[0])], by_name[str(raw_pair[1])])))
                )
    return sorted(explicit_pairs), sorted(adjacent_pairs - explicit_pairs)


def _adjacent_or_coupled_joint_pairs(
    model: object,
    joints: Sequence[object],
    joint_names: Sequence[str],
) -> list[tuple[int, int]]:
    """Compatibility wrapper for the former combined private helper."""

    explicit, adjacent = _joint_pair_groups(model, joints, joint_names)
    return sorted(set(explicit).union(adjacent))


def refine_pose_samples(
    model: object,
    failed_poses: Sequence[Dict[str, object]],
    *,
    max_samples: int,
    seed: int = 0,
) -> List[Dict[str, object]]:
    """Locally densify around failed poses without expanding the global grid."""

    if max_samples <= 0:
        return []
    joints = getattr(model, "articulations", None)
    if not isinstance(joints, list):
        joints = getattr(model, "joints", None)
    if not isinstance(joints, list):
        return []
    lookup = {
        str(joint.name): joint for joint in joints if isinstance(getattr(joint, "name", None), str)
    }
    refined: list[dict[str, object]] = []
    seen: set[tuple[tuple[str, object], ...]] = set()

    def add(pose: dict[str, object]) -> None:
        if len(refined) >= max_samples:
            return
        key = tuple(sorted((name, _pose_value_key(value)) for name, value in pose.items()))
        if key not in seen:
            seen.add(key)
            refined.append(pose)

    rng = random.Random(int(seed))
    for failed in failed_poses:
        for joint_name in sorted(failed):
            value = failed[joint_name]
            joint = lookup.get(joint_name)
            if joint is None or not isinstance(value, (int, float)):
                continue
            limits = getattr(joint, "motion_limits", None)
            lower = getattr(limits, "lower", None) if limits is not None else None
            upper = getattr(limits, "upper", None) if limits is not None else None
            if isinstance(lower, (int, float)) and isinstance(upper, (int, float)):
                span = max(abs(float(upper) - float(lower)), 1e-3)
            else:
                span = math.tau
            delta = max(0.01 * span, 1e-4)
            for sign in (-1.0, 1.0):
                candidate = float(value) + sign * delta * rng.uniform(0.75, 1.25)
                if isinstance(lower, (int, float)):
                    candidate = max(candidate, float(lower))
                if isinstance(upper, (int, float)):
                    candidate = min(candidate, float(upper))
                pose = dict(failed)
                pose[joint_name] = candidate
                add(pose)
                if len(refined) >= max_samples:
                    return refined
    return refined


def _world_manifold(entry: _CompiledCollisionEntry) -> object | None:
    manifold = entry.local_manifold
    tf = entry.elem_tf
    if manifold is None or tf is None:
        return None
    try:
        transform = tuple(
            tuple(float(tf[row][col]) for col in range(4))
            for row in range(3)
        )
        return manifold.transform(transform)
    except Exception:
        return None


def _intersection_projection_depth(
    intersection: object,
    *,
    entry_a: _CompiledCollisionEntry,
    entry_b: _CompiledCollisionEntry,
    contact_normals: Sequence[Vec3],
) -> Optional[float]:
    try:
        import numpy as np

        mesh = intersection.to_mesh()
        vertices = np.asarray(mesh.vert_properties, dtype=float)
        if vertices.size == 0:
            return 0.0
        points = vertices[:, :3]
    except Exception:
        return None

    axes: list[Vec3] = [
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
    ]
    if entry_a.elem_tf is not None:
        axes.extend(_mat4_axes(entry_a.elem_tf))
    if entry_b.elem_tf is not None:
        axes.extend(_mat4_axes(entry_b.elem_tf))
    axes.extend(contact_normals)

    spans: list[float] = []
    seen: set[tuple[int, int, int]] = set()
    for raw_axis in axes:
        if _norm(raw_axis) <= _EPS:
            continue
        axis = _normalize(raw_axis)
        canonical = axis
        if (
            canonical[0] < -_EPS
            or (
                abs(canonical[0]) <= _EPS
                and (
                    canonical[1] < -_EPS
                    or (abs(canonical[1]) <= _EPS and canonical[2] < 0.0)
                )
            )
        ):
            canonical = (-canonical[0], -canonical[1], -canonical[2])
        key = tuple(int(round(component * 1_000_000.0)) for component in canonical)
        if key in seen:
            continue
        seen.add(key)
        projected = points @ np.asarray(axis, dtype=float)
        spans.append(float(projected.max() - projected.min()))
    return min(spans) if spans else None


def _strictly_exceeds(value: float, tolerance: float) -> bool:
    """Strict threshold comparison that keeps an exactly-authored boundary inclusive."""

    value_f = float(value)
    tolerance_f = float(tolerance)
    return value_f > tolerance_f and not math.isclose(
        value_f,
        tolerance_f,
        rel_tol=1e-12,
        abs_tol=1e-15,
    )


def _within_tolerance(value: float, tolerance: float) -> bool:
    value_f = float(value)
    tolerance_f = float(tolerance)
    return value_f <= tolerance_f or math.isclose(
        value_f,
        tolerance_f,
        rel_tol=1e-12,
        abs_tol=1e-15,
    )


def _classify_narrow_phase_overlap(
    entry_a: _CompiledCollisionEntry,
    entry_b: _CompiledCollisionEntry,
    metrics: _CollisionPairMetrics,
    *,
    overlap_tol: float,
    overlap_volume_tol: float,
    broad_volume: float,
) -> tuple[bool, Optional[float], Optional[float], str]:
    if entry_a.exact_primitive and entry_b.exact_primitive:
        penetration = metrics.penetration_depth
        if penetration is None:
            return True, None, None, "fcl_conservative_primitive"
        manifold_a = _world_manifold(entry_a)
        manifold_b = _world_manifold(entry_b)
        if manifold_a is None or manifold_b is None:
            return (
                _strictly_exceeds(penetration, overlap_tol)
                and _strictly_exceeds(broad_volume, overlap_volume_tol),
                penetration,
                None,
                "fcl_conservative_primitive",
            )
        try:
            intersection = manifold_a ^ manifold_b
            volume = (
                0.0
                if intersection.is_empty()
                else max(0.0, float(intersection.volume()))
            )
        except Exception:
            return (
                _strictly_exceeds(penetration, overlap_tol)
                and _strictly_exceeds(broad_volume, overlap_volume_tol),
                penetration,
                None,
                "fcl_conservative_primitive",
            )
        return (
            _strictly_exceeds(penetration, overlap_tol)
            and _strictly_exceeds(volume, overlap_volume_tol),
            penetration,
            volume,
            "fcl_primitive_penetration+manifold_volume",
        )

    manifold_a = _world_manifold(entry_a)
    manifold_b = _world_manifold(entry_b)
    if manifold_a is None or manifold_b is None:
        return True, None, None, "fcl_conservative_nonmanifold"

    try:
        intersection = manifold_a ^ manifold_b
        if intersection.is_empty():
            return False, 0.0, 0.0, "manifold_intersection"
        volume = max(0.0, float(intersection.volume()))
        penetration = _intersection_projection_depth(
            intersection,
            entry_a=entry_a,
            entry_b=entry_b,
            contact_normals=metrics.contact_normals,
        )
    except Exception:
        return True, None, None, "fcl_conservative_nonmanifold"

    if penetration is None:
        return True, None, volume, "fcl_conservative_nonmanifold"
    return (
        _strictly_exceeds(penetration, overlap_tol)
        and _strictly_exceeds(volume, overlap_volume_tol),
        penetration,
        volume,
        "manifold_intersection",
    )


def _find_collision_overlaps_fcl_for_poses(
    compiled_model: object,
    *,
    asset_root: Optional[Path],
    source_model: Optional[object] = None,
    poses: Sequence[Dict[str, float]],
    overlap_tol: float,
    overlap_volume_tol: float,
    allowed_pairs: Optional[Iterable[Tuple[str, str]]],
) -> List[GeometryOverlap]:
    resolved_asset_root = resolve_asset_root(
        asset_root,
        compiled_model,
        source_model if source_model is not None else compiled_model,
    )
    links = getattr(compiled_model, "parts", None)
    joints = getattr(compiled_model, "articulations", None)
    if not isinstance(links, list) or not isinstance(joints, list):
        raise ValidationError("model must have .parts and .articulations lists")

    allowed: set[tuple[str, str]] = set()
    if allowed_pairs:
        for a, b in allowed_pairs:
            allowed.add((a, b))
            allowed.add((b, a))

    overlaps: list[GeometryOverlap] = []
    scene = _collision_scene_for_model(
        compiled_model,
        asset_root=resolved_asset_root,
    )

    for pose_index, pose in enumerate(poses):
        view = scene.pose_view(dict(pose))
        names = sorted(view.entries_by_part.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a = names[i]
                b = names[j]
                if (a, b) in allowed:
                    continue
                for ia, item_a in enumerate(view.entries_by_part[a]):
                    for ib, item_b in enumerate(view.entries_by_part[b]):
                        aabb_a = item_a.aabb
                        aabb_b = item_b.aabb
                        depth = _aabb_intersection_depth(aabb_a, aabb_b)
                        volume = _aabb_intersection_volume(aabb_a, aabb_b)
                        if not (
                            _strictly_exceeds(depth[0], overlap_tol)
                            and _strictly_exceeds(depth[1], overlap_tol)
                            and _strictly_exceeds(depth[2], overlap_tol)
                        ):
                            continue
                        if not _strictly_exceeds(volume, overlap_volume_tol):
                            continue
                        metrics = scene.pair_metrics(
                            view,
                            item_a,
                            item_b,
                            need_distance=False,
                        )
                        if not metrics.collided:
                            continue
                        report, penetration, intersection_volume, narrow_phase = (
                            _classify_narrow_phase_overlap(
                                item_a,
                                item_b,
                                metrics,
                                overlap_tol=overlap_tol,
                                overlap_volume_tol=overlap_volume_tol,
                                broad_volume=volume,
                            )
                        )
                        if not report:
                            continue
                        overlaps.append(
                            GeometryOverlap(
                                pose_index=pose_index,
                                pose=dict(pose),
                                link_a=a,
                                link_b=b,
                                elem_a=ia,
                                elem_b=ib,
                                overlap_depth=depth,
                                overlap_volume=volume,
                                aabb_a=aabb_a,
                                aabb_b=aabb_b,
                                elem_a_name=item_a.name,
                                elem_b_name=item_b.name,
                                elem_a_origin=item_a.origin,
                                elem_b_origin=item_b.origin,
                                elem_a_geometry=item_a.geometry_name,
                                elem_b_geometry=item_b.geometry_name,
                                penetration_depth=penetration,
                                intersection_volume=intersection_volume,
                                narrow_phase=narrow_phase,
                            )
                        )
    return overlaps


def _find_collision_overlaps_fcl(
    model: object,
    *,
    asset_root: Optional[Path],
    max_pose_samples: int,
    overlap_tol: float,
    overlap_volume_tol: float,
    allowed_pairs: Optional[Iterable[Tuple[str, str]]],
    seed: int,
    validate_model: bool = True,
) -> List[GeometryOverlap]:
    compiled_model = compile_object_model_with_exact_collisions(
        model,  # type: ignore[arg-type]
        asset_root=asset_root,
        validate=validate_model,
    )
    initial_budget = (
        max(1, int(max_pose_samples * 0.8)) if max_pose_samples > 4 else max_pose_samples
    )
    poses = generate_pose_samples(compiled_model, max_samples=initial_budget, seed=int(seed))
    overlaps = _find_collision_overlaps_fcl_for_poses(
        compiled_model,
        asset_root=asset_root,
        source_model=model,
        poses=poses,
        overlap_tol=overlap_tol,
        overlap_volume_tol=overlap_volume_tol,
        allowed_pairs=allowed_pairs,
    )
    remaining = max(0, max_pose_samples - len(poses))
    if not overlaps or remaining == 0:
        return overlaps
    failed_poses = [dict(finding.pose) for finding in overlaps]
    refined = refine_pose_samples(
        compiled_model,
        failed_poses,
        max_samples=remaining,
        seed=int(seed) + 1,
    )
    if refined:
        overlaps.extend(
            _find_collision_overlaps_fcl_for_poses(
                compiled_model,
                asset_root=asset_root,
                source_model=model,
                poses=refined,
                overlap_tol=overlap_tol,
                overlap_volume_tol=overlap_volume_tol,
                allowed_pairs=allowed_pairs,
            )
        )
    return overlaps


def _resolve_model_links_and_joints(model: object) -> tuple[list[object], list[object]]:
    links = getattr(model, "parts", None)
    if not isinstance(links, list):
        links = getattr(model, "links", None)
    joints = getattr(model, "articulations", None)
    if not isinstance(joints, list):
        joints = getattr(model, "joints", None)
    if not isinstance(links, list) or not isinstance(joints, list):
        raise ValidationError("model must have .parts and .articulations lists")
    return links, joints


def _pair_key(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a <= b else (b, a)


def _root_part_names(names: Sequence[str], joints: Sequence[object]) -> Tuple[str, ...]:
    name_set = {str(name) for name in names}
    child_names = {
        str(child)
        for joint in joints
        if isinstance((child := getattr(joint, "child", None)), str) and child in name_set
    }
    roots = tuple(sorted(name for name in name_set if name not in child_names))
    if roots:
        return roots
    if not name_set:
        return ()
    return (sorted(name_set)[0],)


def _connected_components(
    names: Sequence[str],
    adjacency: Dict[str, set[str]],
) -> List[Tuple[str, ...]]:
    remaining = set(names)
    components: list[tuple[str, ...]] = []
    while remaining:
        start = min(remaining)
        stack = [start]
        component: list[str] = []
        remaining.remove(start)
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in sorted(adjacency.get(current, set())):
                if neighbor not in remaining:
                    continue
                remaining.remove(neighbor)
                stack.append(neighbor)
        components.append(tuple(sorted(component)))
    return components


def _unsupported_component_findings(
    names: Sequence[str],
    *,
    root_parts: Sequence[str],
    support_pairs: Iterable[Tuple[str, str]],
    pair_min_distances: Dict[Tuple[str, str], float],
    pose_index: int,
    pose: Dict[str, float],
    contact_tol: float,
    backend: str,
) -> List[UnsupportedPartFinding]:
    unique_names = tuple(sorted({str(name) for name in names}))
    if len(unique_names) <= 1:
        return []

    adjacency: Dict[str, set[str]] = {name: set() for name in unique_names}
    for raw_a, raw_b in support_pairs:
        a, b = _pair_key(str(raw_a), str(raw_b))
        if a == b or a not in adjacency or b not in adjacency:
            continue
        adjacency[a].add(b)
        adjacency[b].add(a)

    components = _connected_components(unique_names, adjacency)
    root_set = {str(name) for name in root_parts}
    grounded_parts: set[str] = set()
    for component in components:
        if any(name in root_set for name in component):
            grounded_parts.update(component)
    if not grounded_parts and unique_names:
        grounded_parts.add(unique_names[0])

    findings: list[UnsupportedPartFinding] = []
    for component in components:
        if any(name in grounded_parts for name in component):
            continue

        nearest_part: Optional[str] = None
        min_distance: Optional[float] = None
        for name in component:
            for grounded_name in grounded_parts:
                if name == grounded_name:
                    continue
                distance = pair_min_distances.get(_pair_key(name, grounded_name))
                if distance is None:
                    continue
                if (
                    min_distance is None
                    or distance < float(min_distance)
                    or (
                        math.isclose(distance, float(min_distance), abs_tol=_EPS)
                        and isinstance(nearest_part, str)
                        and grounded_name < nearest_part
                    )
                    or (nearest_part is None and math.isfinite(distance))
                ):
                    min_distance = float(distance)
                    nearest_part = grounded_name

        findings.append(
            UnsupportedPartFinding(
                pose_index=pose_index,
                pose=dict(pose),
                part=component[0],
                nearest_part=nearest_part,
                min_distance=min_distance,
                contact_tol=float(contact_tol),
                backend=backend,
                parts=component,
                root_parts=tuple(sorted(root_set)),
            )
        )

    return findings


def _unsupported_parts_from_world_aabbs(
    part_aabbs: Dict[str, AABB],
    *,
    pose_index: int,
    pose: Dict[str, float],
    contact_tol: float,
    backend: str,
    root_parts: Sequence[str] = (),
) -> List[UnsupportedPartFinding]:
    names = sorted(part_aabbs.keys())
    if len(names) <= 1:
        return []

    support_pairs: set[tuple[str, str]] = set()
    pair_min_distances: dict[tuple[str, str], float] = {}

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = names[i]
            b = names[j]
            aabb_a = part_aabbs[a]
            aabb_b = part_aabbs[b]
            if _aabbs_touch_or_overlap(aabb_a, aabb_b, tol=contact_tol):
                support_pairs.add((a, b))
                dist = 0.0
            else:
                dist = _aabb_separation_distance(aabb_a, aabb_b)
            pair_min_distances[_pair_key(a, b)] = float(dist)

    return _unsupported_component_findings(
        names,
        root_parts=tuple(root_parts) if root_parts else _root_part_names(names, ()),
        support_pairs=support_pairs,
        pair_min_distances=pair_min_distances,
        pose_index=pose_index,
        pose=pose,
        contact_tol=float(contact_tol),
        backend=backend,
    )


def _find_unsupported_parts_physical(
    model: object,
    *,
    asset_root: Optional[Path],
    max_pose_samples: int,
    contact_tol: float,
    seed: int,
    validate_model: bool = True,
) -> List[UnsupportedPartFinding]:
    compiled_model = compile_object_model_with_exact_collisions(
        model,  # type: ignore[arg-type]
        asset_root=asset_root,
        validate=validate_model,
    )
    resolved_asset_root = resolve_asset_root(asset_root, compiled_model, model)
    links, joints = _resolve_model_links_and_joints(compiled_model)
    if len(links) <= 1:
        return []

    try:
        import fcl  # type: ignore[import-not-found]
    except Exception as exc:
        raise ValidationError(
            "find_unsupported_parts(...) requires FCL support for contact queries."
        ) from exc

    poses = generate_pose_samples(compiled_model, max_samples=max_pose_samples, seed=int(seed))
    findings: list[UnsupportedPartFinding] = []

    if not all(hasattr(fcl, attr) for attr in ("distance", "DistanceRequest", "DistanceResult")):
        raise ValidationError(
            "find_unsupported_parts(...) requires FCL distance queries "
            "(`distance`, `DistanceRequest`, `DistanceResult`)."
        )
    scene = _collision_scene_for_model(
        compiled_model,
        asset_root=resolved_asset_root,
    )

    for pose_index, pose in enumerate(poses):
        view = scene.pose_view(dict(pose))
        names = sorted(view.entries_by_part.keys())
        if len(names) <= 1:
            continue

        root_parts = _root_part_names(names, joints)
        support_pairs: set[tuple[str, str]] = set()
        pair_min_distances: dict[tuple[str, str], float] = {}

        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a = names[i]
                b = names[j]
                pair_supported = False
                pair_min_distance: Optional[float] = None
                for entry_a in view.entries_by_part[a]:
                    for entry_b in view.entries_by_part[b]:
                        # Broad-phase cull: the AABB gap lower-bounds the exact
                        # distance, so a far pair can neither collide nor sit
                        # within contact_tol — skip both narrow-phase queries.
                        aabb_gap = _aabb_min_distance(entry_a.aabb, entry_b.aabb)
                        if aabb_gap > _FAR_PAIR_CULL_DISTANCE and aabb_gap > contact_tol:
                            if pair_min_distance is None or aabb_gap < pair_min_distance:
                                pair_min_distance = aabb_gap
                            continue
                        metrics = scene.pair_metrics(
                            view,
                            entry_a,
                            entry_b,
                            need_distance=True,
                        )
                        if metrics.collided:
                            pair_supported = True
                            pair_min_distance = 0.0
                            break

                        dist = float(
                            metrics.distance
                            if metrics.distance is not None
                            else float("inf")
                        )
                        if pair_min_distance is None or dist < pair_min_distance:
                            pair_min_distance = dist
                        if _within_tolerance(dist, contact_tol):
                            pair_supported = True
                            pair_min_distance = dist
                            break
                    if pair_supported:
                        break

                if pair_supported:
                    support_pairs.add((a, b))

                if pair_min_distance is not None:
                    pair_min_distances[_pair_key(a, b)] = float(pair_min_distance)

        findings.extend(
            _unsupported_component_findings(
                names,
                root_parts=root_parts,
                support_pairs=support_pairs,
                pair_min_distances=pair_min_distances,
                pose_index=pose_index,
                pose=pose,
                contact_tol=float(contact_tol),
                backend="fcl",
            )
        )

    return findings


def _point_to_line_perp_distance(point: Vec3, line_point: Vec3, direction: Vec3) -> float:
    """Perpendicular distance from a point to the infinite line through
    ``line_point`` along ``direction`` (axial offset is deliberately ignored:
    for a symmetry axis the along-axis component carries no information)."""
    d = _normalize(direction)
    v = (point[0] - line_point[0], point[1] - line_point[1], point[2] - line_point[2])
    t = v[0] * d[0] + v[1] * d[1] + v[2] * d[2]
    perp = (v[0] - t * d[0], v[1] - t * d[1], v[2] - t * d[2])
    return math.sqrt(perp[0] ** 2 + perp[1] ** 2 + perp[2] ** 2)


def find_joint_origin_distance_findings(
    model: object,
    *,
    asset_root: Optional[Path] = None,
    tol: float = 0.015,
    bbox_relative: float = 0.0,
    validate_model: bool = True,
) -> List[JointOriginDistanceFinding]:
    """Anchor-honesty gate: every joint's frame must sit on real hardware.

    Per-type semantics (each physically derived; ONE flat ``tol``, no
    bbox-relative loosening — ``bbox_relative`` is accepted for backward
    compatibility and ignored):

    - REVOLUTE/CONTINUOUS: the rotation axis is a physically unique line. Each
      side (parent, child) passes if EITHER (a) the axis SEGMENT passes within
      ``tol`` of that side's geometry (pin/knuckle/axle), or (b) the axis line
      passes within ``tol`` of that side's AABB center — the axis is the
      part's symmetry centerline (ring bearings: domes, lens rings, caps,
      wheel hubs, revolving panels). A mid-air phantom pivot fails both.
      Segment bounds follow ``measure_joint_axis_distances``.
    - PRISMATIC/FLOATING: no positional check. Translation has no distinguished
      axis line — origin position is pure gauge freedom (moving it while
      compensating mesh offsets yields the identical motion). Engagement is
      the mating/overlap/connectivity gates' job.
    - FIXED (or zero axis): origin POINT within ``tol`` of both parts — a weld
      belongs at the interface it welds.
    """
    del bbox_relative  # legacy parameter: relative loosening retired
    compiled_model = compile_object_model_with_exact_collisions(
        model,  # type: ignore[arg-type]
        asset_root=asset_root,
        validate=validate_model,
    )
    resolved_asset_root = resolve_asset_root(asset_root, compiled_model, model)
    links, joints = _resolve_model_links_and_joints(compiled_model)
    if not links or not joints:
        return []

    links_by_name = {
        name: link for link in links if isinstance((name := getattr(link, "name", None)), str)
    }
    mesh_cache: Dict[tuple[Path, Optional[Vec3]], object] = {}
    entries_cache: Dict[str, list[_CompiledCollisionEntry]] = {}

    def _entries_for(part_name: str, part: Part) -> list[_CompiledCollisionEntry]:
        cached = entries_cache.get(part_name)
        if cached is None:
            cached = _compiled_part_collision_entries(
                part,
                asset_root=resolved_asset_root,
                mesh_cache=mesh_cache,
            )
            entries_cache[part_name] = cached
        return cached

    point_radius = 1e-9
    flat_tol = float(tol)
    findings: list[JointOriginDistanceFinding] = []

    for joint in joints:
        joint_name = getattr(joint, "name", None)
        parent_name = getattr(joint, "parent", None)
        child_name = getattr(joint, "child", None)
        if (
            not isinstance(joint_name, str)
            or not isinstance(parent_name, str)
            or not isinstance(child_name, str)
        ):
            continue
        parent_part = links_by_name.get(parent_name)
        child_part = links_by_name.get(child_name)
        if parent_part is None or child_part is None:
            continue

        joint_type = getattr(joint, "articulation_type", None)
        joint_type_str = str(getattr(joint_type, "value", joint_type or "")).lower()
        if joint_type_str in ("prismatic", "floating"):
            continue

        parent_entries = _entries_for(parent_name, parent_part)
        child_entries = _entries_for(child_name, child_part)
        if not parent_entries or not child_entries:
            continue

        origin = getattr(joint, "origin", Origin())
        parent_point = (
            float(origin.xyz[0]),
            float(origin.xyz[1]),
            float(origin.xyz[2]),
        )
        child_point = (0.0, 0.0, 0.0)

        axis = _normalize(getattr(joint, "axis", (0.0, 0.0, 1.0)))
        axis_is_zero = abs(axis[0]) <= _EPS and abs(axis[1]) <= _EPS and abs(axis[2]) <= _EPS
        rotational = joint_type_str in ("revolute", "continuous") and not axis_is_zero

        if not rotational:
            # FIXED (or degenerate axis): flat point-proximity on both sides.
            parent_probe = _point_collision_object(parent_point, radius=point_radius)
            child_probe = _point_collision_object(child_point, radius=point_radius)
            parent_distance = min(
                _collision_pair_metrics(parent_probe, entry.collision_obj)[1]
                for entry in parent_entries
            )
            child_distance = min(
                _collision_pair_metrics(child_probe, entry.collision_obj)[1]
                for entry in child_entries
            )
            if parent_distance > flat_tol or child_distance > flat_tol:
                findings.append(
                    JointOriginDistanceFinding(
                        joint=joint_name,
                        parent=parent_name,
                        child=child_name,
                        parent_distance=float(parent_distance),
                        child_distance=float(child_distance),
                        tol=flat_tol,
                        joint_type=joint_type_str,
                        metric="point",
                    )
                )
            continue

        parent_aabb = _entries_union_aabb(parent_entries)
        child_aabb = _entries_union_aabb(child_entries)
        rpy = getattr(origin, "rpy", (0.0, 0.0, 0.0))
        rot = _rpy_matrix(float(rpy[0]), float(rpy[1]), float(rpy[2]))
        parent_dir = _normalize(
            (
                rot[0][0] * axis[0] + rot[0][1] * axis[1] + rot[0][2] * axis[2],
                rot[1][0] * axis[0] + rot[1][1] * axis[1] + rot[1][2] * axis[2],
                rot[2][0] * axis[0] + rot[2][1] * axis[1] + rot[2][2] * axis[2],
            )
        )
        child_dir = axis
        half_length = max(
            _AXIS_MIN_HALF_LENGTH,
            0.5
            * max(
                _aabb_extent_along(parent_aabb, parent_dir),
                _aabb_extent_along(child_aabb, child_dir),
            ),
        )

        def _side(
            point: Vec3,
            direction: Vec3,
            entries: Sequence[_CompiledCollisionEntry],
            union_aabb: AABB,
        ) -> tuple[float, float, bool]:
            axis_dist = _min_segment_distance_to_entries(point, direction, half_length, entries)
            center = tuple(0.5 * (union_aabb[0][i] + union_aabb[1][i]) for i in range(3))
            center_dist = _point_to_line_perp_distance(center, point, direction)
            return axis_dist, center_dist, (axis_dist <= flat_tol or center_dist <= flat_tol)

        p_axis, p_center, p_ok = _side(parent_point, parent_dir, parent_entries, parent_aabb)
        c_axis, c_center, c_ok = _side(child_point, child_dir, child_entries, child_aabb)
        if not (p_ok and c_ok):
            findings.append(
                JointOriginDistanceFinding(
                    joint=joint_name,
                    parent=parent_name,
                    child=child_name,
                    parent_distance=float(p_axis),
                    child_distance=float(c_axis),
                    tol=flat_tol,
                    joint_type=joint_type_str,
                    metric="axis",
                    parent_center_distance=float(p_center),
                    child_center_distance=float(c_center),
                )
            )
    return findings


@dataclass(frozen=True)
class JointAxisDistanceMeasurement:
    """Shadow-metric measurement for one joint (report-only, not a gate).

    Records both the legacy origin-POINT proximity (what
    ``find_joint_origin_distance_findings`` gates on today, including its
    bbox-relative effective tol) and the proposed axis-LINE-SEGMENT proximity
    for the same joint, so the two verdicts can be diffed offline.
    """

    joint: str
    parent: str
    child: str
    joint_type: str
    # Legacy point metric (same semantics as find_joint_origin_distance_findings).
    parent_point_distance: float
    child_point_distance: float
    point_tol: float
    # Shadow axis metric. For FIXED/FLOATING joints (no meaningful axis) these
    # duplicate the point distances and axis_based is False.
    parent_axis_distance: float
    child_axis_distance: float
    axis_half_length: float
    axis_based: bool


@dataclass(frozen=True)
class JointAxisDistanceFinding:
    joint: str
    parent: str
    child: str
    joint_type: str
    parent_distance: float
    child_distance: float
    tol: float
    axis_based: bool
    axis_half_length: float


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


_AXIS_PROBE_RADIUS = 1e-6
_AXIS_MIN_HALF_LENGTH = 1e-3


def _segment_collision_object(
    center: Vec3,
    direction: Vec3,
    half_length: float,
    *,
    radius: float = _AXIS_PROBE_RADIUS,
) -> object:
    """A thin fcl.Capsule spanning ``center ± half_length·direction``.

    FCL capsules are aligned with local +Z and centered on their transform, so
    the rotation maps local Z onto ``direction``. The tiny radius makes the
    reported distance the segment-to-geometry distance minus ``radius``
    (negligible at 1e-6 m).
    """
    import fcl

    d = _normalize(direction)
    ref = (0.0, 0.0, 1.0) if abs(d[2]) < 0.9 else (1.0, 0.0, 0.0)
    x = _normalize(_cross(ref, d))
    y = _cross(d, x)
    rot = (
        (x[0], y[0], d[0]),
        (x[1], y[1], d[1]),
        (x[2], y[2], d[2]),
    )
    return fcl.CollisionObject(
        fcl.Capsule(float(radius), float(2.0 * half_length)),
        fcl.Transform(rot, (float(center[0]), float(center[1]), float(center[2]))),
    )


def _segment_aabb(center: Vec3, direction: Vec3, half_length: float, *, radius: float) -> AABB:
    d = _normalize(direction)
    p0 = (
        center[0] - d[0] * half_length,
        center[1] - d[1] * half_length,
        center[2] - d[2] * half_length,
    )
    p1 = (
        center[0] + d[0] * half_length,
        center[1] + d[1] * half_length,
        center[2] + d[2] * half_length,
    )
    lo = (min(p0[0], p1[0]) - radius, min(p0[1], p1[1]) - radius, min(p0[2], p1[2]) - radius)
    hi = (max(p0[0], p1[0]) + radius, max(p0[1], p1[1]) + radius, max(p0[2], p1[2]) + radius)
    return lo, hi


def _is_bvh_collision_object(obj: object) -> bool:
    import fcl

    try:
        return isinstance(obj.collision_geometry, fcl.BVHModel)
    except Exception:
        return False


def _min_segment_distance_to_entry(
    center: Vec3,
    direction: Vec3,
    half_length: float,
    entry: _CompiledCollisionEntry,
) -> float:
    """Min distance from a segment to one collision entry.

    python-fcl's Capsule narrow phase is only trustworthy against BVH meshes
    (capsule-vs-primitive returns wrong nearest pairs — verified: capsule/Box
    reports 0.187 where the true distance is 0.150, while capsule/BVH and
    sphere/anything are exact). BVH entries therefore use one capsule query;
    primitive entries fall back to sphere point-probes sampled along the
    segment with golden-section refinement around the best coarse sample.
    """
    if _is_bvh_collision_object(entry.collision_obj):
        probe = _segment_collision_object(center, direction, half_length)
        _, dist = _collision_pair_metrics(probe, entry.collision_obj)
        return dist

    d = _normalize(direction)

    def _dist_at(t: float) -> float:
        point = (center[0] + d[0] * t, center[1] + d[1] * t, center[2] + d[2] * t)
        probe = _point_collision_object(point, radius=1e-9)
        _, dist = _collision_pair_metrics(probe, entry.collision_obj)
        return dist

    n = 17
    ts = [(-half_length + (2.0 * half_length) * i / (n - 1)) for i in range(n)]
    dists = [_dist_at(t) for t in ts]
    best_i = min(range(n), key=lambda i: dists[i])
    lo = ts[max(0, best_i - 1)]
    hi = ts[min(n - 1, best_i + 1)]
    # Golden-section refinement: the along-segment distance profile is
    # piecewise smooth; the coarse grid brackets the basin, refinement
    # converges to ~1e-4 of the segment length in ~25 evaluations.
    inv_phi = 0.6180339887498949
    a, b = lo, hi
    c = b - (b - a) * inv_phi
    e = a + (b - a) * inv_phi
    fc, fe = _dist_at(c), _dist_at(e)
    for _ in range(25):
        if fc < fe:
            b, e, fe = e, c, fc
            c = b - (b - a) * inv_phi
            fc = _dist_at(c)
        else:
            a, c, fc = c, e, fe
            e = a + (b - a) * inv_phi
            fe = _dist_at(e)
    return min(min(dists), fc, fe)


def _min_segment_distance_to_entries(
    center: Vec3,
    direction: Vec3,
    half_length: float,
    entries: Sequence[_CompiledCollisionEntry],
) -> float:
    """Segment→part distance with the AABB lower-bound cull ordering."""
    seg_aabb = _segment_aabb(center, direction, half_length, radius=_AXIS_PROBE_RADIUS)
    best = float("inf")
    order = sorted(entries, key=lambda e: _aabb_min_distance(seg_aabb, e.aabb))
    for entry in order:
        if _aabb_min_distance(seg_aabb, entry.aabb) >= best:
            break
        dist = _min_segment_distance_to_entry(center, direction, half_length, entry)
        if dist < best:
            best = dist
        if best <= 0.0:
            break
    return best


def _min_distance_to_entries(
    probe_obj: object,
    probe_aabb: AABB,
    entries: Sequence[_CompiledCollisionEntry],
) -> float:
    """Min FCL distance from a probe object to a part's collision entries.

    Entries are visited in ascending order of the AABB lower bound
    (``_aabb_min_distance`` never exceeds the exact distance), so the loop can
    stop as soon as the next lower bound already exceeds the best exact
    distance found.
    """
    best = float("inf")
    order = sorted(entries, key=lambda e: _aabb_min_distance(probe_aabb, e.aabb))
    for entry in order:
        if _aabb_min_distance(probe_aabb, entry.aabb) >= best:
            break
        _, dist = _collision_pair_metrics(probe_obj, entry.collision_obj)
        if dist < best:
            best = dist
        if best <= 0.0:
            break
    return best


def _entries_union_aabb(entries: Sequence[_CompiledCollisionEntry]) -> AABB:
    lo = tuple(min(e.aabb[0][i] for e in entries) for i in range(3))
    hi = tuple(max(e.aabb[1][i] for e in entries) for i in range(3))
    return lo, hi  # type: ignore[return-value]


def _aabb_extent_along(aabb: AABB, direction: Vec3) -> float:
    """Projection width of an AABB onto a (normalized) direction."""
    d = _normalize(direction)
    size = _aabb_size(aabb)
    return abs(d[0]) * size[0] + abs(d[1]) * size[1] + abs(d[2]) * size[2]


def measure_joint_axis_distances(
    model: object,
    *,
    asset_root: Optional[Path] = None,
    point_tol: float = 0.015,
    point_bbox_relative: float = 0.05,
    validate_model: bool = True,
) -> List[JointAxisDistanceMeasurement]:
    """SHADOW metric (report-only): joint AXIS-line proximity per joint.

    For every joint this returns both the legacy origin-point distances (the
    exact quantities ``find_joint_origin_distance_findings`` gates on,
    including its bbox-relative effective tol) and the proposed axis-segment
    distances. Nothing here is wired into any gate; the existing point gate is
    unchanged.

    Axis-segment semantics (non-FIXED joints):

    - In the CHILD frame the axis line passes through ``(0, 0, 0)`` along
      ``joint.axis``; in the PARENT frame it passes through ``origin.xyz``
      along ``R(origin.rpy) @ joint.axis``. Both probes describe the same
      physical line, expressed in the frame each part's collision entries
      already live in (``_compiled_part_collision_entries`` with no part_tf).
    - The probe is a bounded SEGMENT, not an infinite line: an infinite line
      would spuriously graze unrelated geometry far along the axis and make
      the metric meaningless on large assemblies. The segment is centered at
      the joint origin and extends ``± half_length`` where ``half_length`` is
      half the larger of the two parts' AABB projection widths onto the axis
      (floored at ``_AXIS_MIN_HALF_LENGTH``). This makes an axial offset up to
      the part pair's own size legal (prismatic slide origins, axles through
      wheels) while a mid-air phantom pivot — whose axis passes through
      neither part anywhere near the origin — still reads as far. The check
      stays per parent/child part, which further limits accidental grazing of
      unrelated geometry.
    - The segment is realized as a thin ``fcl.Capsule`` (radius 1e-6), one
      narrow-phase query per collision entry, with the ``_aabb_min_distance``
      lower-bound cull to skip far entries.

    FIXED and FLOATING joints have no axis semantics; their "axis" distances
    duplicate the point distances and ``axis_based`` is False.
    """
    compiled_model = compile_object_model_with_exact_collisions(
        model,  # type: ignore[arg-type]
        asset_root=asset_root,
        validate=validate_model,
    )
    resolved_asset_root = resolve_asset_root(asset_root, compiled_model, model)
    links, joints = _resolve_model_links_and_joints(compiled_model)
    if not links or not joints:
        return []

    links_by_name = {
        name: link for link in links if isinstance((name := getattr(link, "name", None)), str)
    }
    mesh_cache: Dict[tuple[Path, Optional[Vec3]], object] = {}
    entries_cache: Dict[str, list[_CompiledCollisionEntry]] = {}

    def _entries_for(part_name: str, part: Part) -> list[_CompiledCollisionEntry]:
        cached = entries_cache.get(part_name)
        if cached is None:
            cached = _compiled_part_collision_entries(
                part,
                asset_root=resolved_asset_root,
                mesh_cache=mesh_cache,
            )
            entries_cache[part_name] = cached
        return cached

    point_radius = 1e-9
    measurements: list[JointAxisDistanceMeasurement] = []

    for joint in joints:
        joint_name = getattr(joint, "name", None)
        parent_name = getattr(joint, "parent", None)
        child_name = getattr(joint, "child", None)
        if (
            not isinstance(joint_name, str)
            or not isinstance(parent_name, str)
            or not isinstance(child_name, str)
        ):
            continue
        parent_part = links_by_name.get(parent_name)
        child_part = links_by_name.get(child_name)
        if parent_part is None or child_part is None:
            continue
        parent_entries = _entries_for(parent_name, parent_part)
        child_entries = _entries_for(child_name, child_part)
        if not parent_entries or not child_entries:
            # Same skip as the legacy gate: nothing to measure against.
            continue

        origin = getattr(joint, "origin", Origin())
        parent_point = (
            float(origin.xyz[0]),
            float(origin.xyz[1]),
            float(origin.xyz[2]),
        )
        child_point = (0.0, 0.0, 0.0)

        # --- legacy point metric (identical semantics to the live gate) ---
        parent_aabb = _entries_union_aabb(parent_entries)
        child_aabb = _entries_union_aabb(child_entries)
        effective_point_tol = float(point_tol)
        if point_bbox_relative > 0.0:
            p_diag = math.sqrt(sum((parent_aabb[1][i] - parent_aabb[0][i]) ** 2 for i in range(3)))
            c_diag = math.sqrt(sum((child_aabb[1][i] - child_aabb[0][i]) ** 2 for i in range(3)))
            effective_point_tol = max(
                effective_point_tol, float(point_bbox_relative) * max(p_diag, c_diag)
            )
        parent_point_probe = _point_collision_object(parent_point, radius=point_radius)
        child_point_probe = _point_collision_object(child_point, radius=point_radius)
        parent_point_aabb = (
            (
                parent_point[0] - point_radius,
                parent_point[1] - point_radius,
                parent_point[2] - point_radius,
            ),
            (
                parent_point[0] + point_radius,
                parent_point[1] + point_radius,
                parent_point[2] + point_radius,
            ),
        )
        child_point_aabb = (
            (-point_radius, -point_radius, -point_radius),
            (point_radius, point_radius, point_radius),
        )
        parent_point_distance = _min_distance_to_entries(
            parent_point_probe, parent_point_aabb, parent_entries
        )
        child_point_distance = _min_distance_to_entries(
            child_point_probe, child_point_aabb, child_entries
        )

        # --- shadow axis metric ---
        joint_type = getattr(joint, "articulation_type", None)
        joint_type_str = str(getattr(joint_type, "value", joint_type or "")).lower()
        axis = _normalize(getattr(joint, "axis", (0.0, 0.0, 1.0)))
        axis_is_zero = abs(axis[0]) <= _EPS and abs(axis[1]) <= _EPS and abs(axis[2]) <= _EPS
        axis_based = joint_type_str not in ("fixed", "floating") and not axis_is_zero

        if axis_based:
            rpy = getattr(origin, "rpy", (0.0, 0.0, 0.0))
            rot = _rpy_matrix(float(rpy[0]), float(rpy[1]), float(rpy[2]))
            parent_dir = _normalize(
                (
                    rot[0][0] * axis[0] + rot[0][1] * axis[1] + rot[0][2] * axis[2],
                    rot[1][0] * axis[0] + rot[1][1] * axis[1] + rot[1][2] * axis[2],
                    rot[2][0] * axis[0] + rot[2][1] * axis[1] + rot[2][2] * axis[2],
                )
            )
            child_dir = axis
            half_length = max(
                _AXIS_MIN_HALF_LENGTH,
                0.5
                * max(
                    _aabb_extent_along(parent_aabb, parent_dir),
                    _aabb_extent_along(child_aabb, child_dir),
                ),
            )
            parent_axis_distance = _min_segment_distance_to_entries(
                parent_point, parent_dir, half_length, parent_entries
            )
            child_axis_distance = _min_segment_distance_to_entries(
                child_point, child_dir, half_length, child_entries
            )
        else:
            half_length = 0.0
            parent_axis_distance = parent_point_distance
            child_axis_distance = child_point_distance

        measurements.append(
            JointAxisDistanceMeasurement(
                joint=joint_name,
                parent=parent_name,
                child=child_name,
                joint_type=joint_type_str,
                parent_point_distance=float(parent_point_distance),
                child_point_distance=float(child_point_distance),
                point_tol=float(effective_point_tol),
                parent_axis_distance=float(parent_axis_distance),
                child_axis_distance=float(child_axis_distance),
                axis_half_length=float(half_length),
                axis_based=axis_based,
            )
        )
    return measurements


def find_joint_axis_distance_findings(
    model: object,
    *,
    asset_root: Optional[Path] = None,
    tol: float = 0.015,
    validate_model: bool = True,
) -> List[JointAxisDistanceFinding]:
    """SHADOW companion to ``find_joint_origin_distance_findings`` (report-only).

    Flags joints whose axis LINE SEGMENT (see ``measure_joint_axis_distances``
    for the exact segment design) is farther than a FLAT ``tol`` from the
    parent's or the child's collision geometry. There is deliberately no
    bbox-relative term: the axis-line semantics already legalize the
    axial-offset cases the relative fudge existed to forgive. FIXED/FLOATING
    joints fall back to the legacy origin-point distance.

    NOT wired into any gate — evidence-gathering only.
    """
    findings: list[JointAxisDistanceFinding] = []
    for m in measure_joint_axis_distances(
        model,
        asset_root=asset_root,
        validate_model=validate_model,
    ):
        if m.parent_axis_distance > tol or m.child_axis_distance > tol:
            findings.append(
                JointAxisDistanceFinding(
                    joint=m.joint,
                    parent=m.parent,
                    child=m.child,
                    joint_type=m.joint_type,
                    parent_distance=m.parent_axis_distance,
                    child_distance=m.child_axis_distance,
                    tol=float(tol),
                    axis_based=m.axis_based,
                    axis_half_length=m.axis_half_length,
                )
            )
    return findings


_FACE_SIDE_TO_AXIS = {
    "positive_x": (0, +1),
    "negative_x": (0, -1),
    "positive_y": (1, +1),
    "negative_y": (1, -1),
    "positive_z": (2, +1),
    "negative_z": (2, -1),
}


def _face_center_in_geom_frame(local_aabb: AABB, face_side: str) -> Vec3:
    """Return the (x, y, z) center of the named axis-aligned face of an AABB,
    in the geometry's local frame."""
    (min_x, min_y, min_z), (max_x, max_y, max_z) = local_aabb
    cx = 0.5 * (min_x + max_x)
    cy = 0.5 * (min_y + max_y)
    cz = 0.5 * (min_z + max_z)
    axis_idx, sign = _FACE_SIDE_TO_AXIS[face_side]
    point = [cx, cy, cz]
    point[axis_idx] = (
        (max_x, max_y, max_z)[axis_idx] if sign > 0 else (min_x, min_y, min_z)[axis_idx]
    )
    return (float(point[0]), float(point[1]), float(point[2]))


def _find_visual_by_name(part: object, visual_name: str) -> Optional[object]:
    for visual in getattr(part, "visuals", []) or []:
        if getattr(visual, "name", None) == visual_name:
            return visual
    return None


def find_joint_mating_findings(
    model: object,
    *,
    asset_root: Optional[Path] = None,
    validate_model: bool = True,
) -> List[JointMatingGapFinding]:
    """Resolve every articulation's MatingContract (if declared) to a pair of
    world-frame face centers and report ones whose distance exceeds the
    contract's contact_tol. Joints without a mating field are skipped
    (grandfathered).
    """
    compiled_model = compile_object_model_with_exact_collisions(
        model,  # type: ignore[arg-type]
        asset_root=asset_root,
        validate=validate_model,
    )
    resolved_asset_root = resolve_asset_root(asset_root, compiled_model, model)
    links, joints = _resolve_model_links_and_joints(compiled_model)
    if not links or not joints:
        return []

    links_by_name = {
        name: link for link in links if isinstance((name := getattr(link, "name", None)), str)
    }

    try:
        part_world = compute_part_world_transforms(compiled_model, {})
    except Exception:
        return []

    findings: list[JointMatingGapFinding] = []
    obj_cache: Dict[Path, AABB] = {}

    for joint in joints:
        mating = getattr(joint, "mating", None)
        if mating is None:
            continue
        joint_name = getattr(joint, "name", None) or "<unnamed>"
        parent_name = getattr(joint, "parent", None)
        child_name = getattr(joint, "child", None)
        if not isinstance(parent_name, str) or not isinstance(child_name, str):
            continue
        parent_part = links_by_name.get(parent_name)
        child_part = links_by_name.get(child_name)
        if parent_part is None or child_part is None:
            continue

        parent_visual = _find_visual_by_name(parent_part, mating.parent_face_geometry)
        child_visual = _find_visual_by_name(child_part, mating.child_face_geometry)
        if parent_visual is None:
            findings.append(
                JointMatingGapFinding(
                    joint=joint_name,
                    parent=parent_name,
                    child=child_name,
                    parent_face_geometry=mating.parent_face_geometry,
                    parent_face_side=mating.parent_face_side,
                    child_face_geometry=mating.child_face_geometry,
                    child_face_side=mating.child_face_side,
                    parent_face_world=(0.0, 0.0, 0.0),
                    child_face_world=(0.0, 0.0, 0.0),
                    distance=float("inf"),
                    contact_tol=float(mating.contact_tol),
                    reason=(
                        f"parent visual {mating.parent_face_geometry!r} not found on part "
                        f"{parent_name!r}"
                    ),
                )
            )
            continue
        if child_visual is None:
            findings.append(
                JointMatingGapFinding(
                    joint=joint_name,
                    parent=parent_name,
                    child=child_name,
                    parent_face_geometry=mating.parent_face_geometry,
                    parent_face_side=mating.parent_face_side,
                    child_face_geometry=mating.child_face_geometry,
                    child_face_side=mating.child_face_side,
                    parent_face_world=(0.0, 0.0, 0.0),
                    child_face_world=(0.0, 0.0, 0.0),
                    distance=float("inf"),
                    contact_tol=float(mating.contact_tol),
                    reason=(
                        f"child visual {mating.child_face_geometry!r} not found on part "
                        f"{child_name!r}"
                    ),
                )
            )
            continue

        try:
            parent_geom = getattr(parent_visual, "geometry", None)
            child_geom = getattr(child_visual, "geometry", None)
            if parent_geom is None or child_geom is None:
                continue
            parent_aabb = _geometry_local_aabb(
                parent_geom, asset_root=resolved_asset_root, _obj_cache=obj_cache
            )
            child_aabb = _geometry_local_aabb(
                child_geom, asset_root=resolved_asset_root, _obj_cache=obj_cache
            )
        except Exception as exc:  # noqa: BLE001 — record as a finding so the agent can fix
            findings.append(
                JointMatingGapFinding(
                    joint=joint_name,
                    parent=parent_name,
                    child=child_name,
                    parent_face_geometry=mating.parent_face_geometry,
                    parent_face_side=mating.parent_face_side,
                    child_face_geometry=mating.child_face_geometry,
                    child_face_side=mating.child_face_side,
                    parent_face_world=(0.0, 0.0, 0.0),
                    child_face_world=(0.0, 0.0, 0.0),
                    distance=float("inf"),
                    contact_tol=float(mating.contact_tol),
                    reason=f"could not compute geometry AABB: {type(exc).__name__}: {exc}",
                )
            )
            continue

        parent_visual_origin = getattr(parent_visual, "origin", Origin())
        child_visual_origin = getattr(child_visual, "origin", Origin())

        # Compute each visual's AABB *in its part's local frame* (i.e., after
        # applying the visual's origin transform incl. rpy). This way
        # parent_face_side / child_face_side are interpreted in the part's
        # axes — what an author writing the MatingContract naturally means
        # when they say "the top face of `blade_plate`" — rather than in
        # the (possibly rotated) geometry frame.
        parent_visual_origin_tf = _origin_to_mat4(parent_visual_origin)
        child_visual_origin_tf = _origin_to_mat4(child_visual_origin)
        parent_aabb_part = _transform_aabb(parent_aabb, parent_visual_origin_tf)
        child_aabb_part = _transform_aabb(child_aabb, child_visual_origin_tf)

        parent_face_part = _face_center_in_geom_frame(parent_aabb_part, mating.parent_face_side)
        child_face_part = _face_center_in_geom_frame(child_aabb_part, mating.child_face_side)

        parent_face_world = _mat4_vec3(part_world.get(parent_name, _identity4()), parent_face_part)
        child_face_world = _mat4_vec3(part_world.get(child_name, _identity4()), child_face_part)

        # Distance is measured ONLY along the parent face's outward normal.
        # This is the correct semantics for "mating face contact": for a
        # sliding-rail joint the parent's bottom face is naturally much
        # longer than the child's rail shoe, but they should still touch
        # in the direction PERPENDICULAR to the slide axis. Computing 3D
        # Euclidean distance would spuriously fail on every prismatic mate.
        # We assume axis-aligned visuals (no rpy on parent visual); under
        # rpy != identity the axis would need to be rotated through the
        # parent visual's transform; we leave that as a follow-up.
        axis_idx, _ = _FACE_SIDE_TO_AXIS[mating.parent_face_side]
        distance = abs(parent_face_world[axis_idx] - child_face_world[axis_idx])

        if distance > float(mating.contact_tol):
            findings.append(
                JointMatingGapFinding(
                    joint=joint_name,
                    parent=parent_name,
                    child=child_name,
                    parent_face_geometry=mating.parent_face_geometry,
                    parent_face_side=mating.parent_face_side,
                    child_face_geometry=mating.child_face_geometry,
                    child_face_side=mating.child_face_side,
                    parent_face_world=parent_face_world,
                    child_face_world=child_face_world,
                    distance=float(distance),
                    contact_tol=float(mating.contact_tol),
                )
            )

        # Opt-in mount-footprint containment (legacy field name: tangential):
        # the child face's extent in the two axes tangent to the parent face
        # must lie within the parent face's extent (+ tangential_tol). Catches
        # "touching but hanging half off" placement bugs (e.g. a centered tray
        # mounted by a corner-post origin) that normal distance and joint-origin
        # proximity are both structurally blind to. Rotational axis realization
        # is a separate AxisInterface contract.
        # Same axis-aligned assumption as the normal check above.
        opt_in = bool(getattr(mating, "tangential_containment", False))
        dry_run = bool(getattr(mating, "tangential_dry_run", False)) and not opt_in
        if opt_in or dry_run:
            severity = "fail" if opt_in else "warn"

            def _tangential_finding(distance: float, tol: float, reason: str):
                return JointMatingGapFinding(
                    joint=joint_name,
                    parent=parent_name,
                    child=child_name,
                    parent_face_geometry=mating.parent_face_geometry,
                    parent_face_side=mating.parent_face_side,
                    child_face_geometry=mating.child_face_geometry,
                    child_face_side=mating.child_face_side,
                    parent_face_world=parent_face_world,
                    child_face_world=child_face_world,
                    distance=distance,
                    contact_tol=tol,
                    reason=reason,
                    severity=severity,
                )

            tangential_tol = float(getattr(mating, "tangential_tol", 0.005))
            if dry_run and not (
                _rotation_is_identityish(part_world.get(parent_name, _identity4()))
                and _rotation_is_identityish(part_world.get(child_name, _identity4()))
                and _rpy_is_zeroish(parent_visual_origin)
                and _rpy_is_zeroish(child_visual_origin)
            ):
                # The footprint comparison is AABB-based (axis-aligned
                # assumption); a rotated mating face inflates the AABB and
                # can produce false verdicts. Dry-run mode SKIPS instead of
                # judging — surfaced so coverage gaps stay visible.
                findings.append(
                    _tangential_finding(
                        0.0,
                        tangential_tol,
                        "tangential dry-run SKIPPED: rotated mating face/part "
                        "(rpy != 0 or non-identity part rotation); the AABB "
                        "footprint comparison is unreliable under rotation.",
                    )
                )
            else:
                parent_aabb_world = _transform_aabb(
                    parent_aabb_part, part_world.get(parent_name, _identity4())
                )
                child_aabb_world = _transform_aabb(
                    child_aabb_part, part_world.get(child_name, _identity4())
                )
                for t_axis in (0, 1, 2):
                    if t_axis == axis_idx:
                        continue
                    overhang = max(
                        parent_aabb_world[0][t_axis] - child_aabb_world[0][t_axis],
                        child_aabb_world[1][t_axis] - parent_aabb_world[1][t_axis],
                    )
                    if overhang > tangential_tol:
                        findings.append(
                            _tangential_finding(
                                float(overhang),
                                tangential_tol,
                                f"mount-footprint containment violated on "
                                f"{'xyz'[t_axis]} tangent axis: "
                                f"child face extends {overhang:.4g}m past the parent face "
                                f"(tangential_tol={tangential_tol:.4g}). The child is "
                                f"mis-placed relative to its mount, not merely gapped."
                                + (" [dry-run: warning only]" if dry_run else ""),
                            )
                        )

    return findings


def find_part_geometry_connectivity_findings(
    model: object,
    *,
    asset_root: Optional[Path] = None,
    contact_tol: float = 1e-6,
    validate_model: bool = True,
) -> List[PartGeometryConnectivityFinding]:
    compiled_model = compile_object_model_with_exact_collisions(
        model,  # type: ignore[arg-type]
        asset_root=asset_root,
        validate=validate_model,
    )
    resolved_asset_root = resolve_asset_root(asset_root, compiled_model, model)
    links, _joints = _resolve_model_links_and_joints(compiled_model)
    if not links:
        return []

    scene = _collision_scene_for_model(
        compiled_model,
        asset_root=resolved_asset_root,
    )
    neutral_view = scene.pose_view({})
    findings: list[PartGeometryConnectivityFinding] = []

    for link in links:
        part_name = getattr(link, "name", None)
        if not isinstance(part_name, str):
            continue
        entries = list(neutral_view.entries_by_part.get(part_name, ()))
        if len(entries) <= 1:
            continue

        remaining = set(range(len(entries)))
        connected_groups: list[set[int]] = []
        while remaining:
            current_group = {next(iter(remaining))}
            queue = list(current_group)
            while queue:
                current = queue.pop()
                current_aabb = entries[current].aabb
                for idx, candidate in enumerate(entries):
                    if idx in current_group:
                        continue
                    # Broad-phase cull: AABB gap lower-bounds the exact
                    # distance, so a separated pair can't be touching.
                    if _aabb_min_distance(current_aabb, candidate.aabb) > float(contact_tol):
                        continue
                    metrics = scene.pair_metrics(
                        neutral_view,
                        entries[current],
                        candidate,
                        need_distance=True,
                    )
                    distance = (
                        0.0
                        if metrics.collided
                        else float(
                            metrics.distance
                            if metrics.distance is not None
                            else float("inf")
                        )
                    )
                    if metrics.collided or distance <= float(contact_tol):
                        current_group.add(idx)
                        queue.append(idx)
            connected_groups.append(current_group)
            remaining.difference_update(current_group)

        largest_group = max(connected_groups, key=lambda group: (len(group), -min(group)))
        if len(largest_group) == len(entries):
            continue

        builder_by_name: Dict[str, str] = {}
        for visual in getattr(link, "visuals", []) or []:
            v_name = getattr(visual, "name", None)
            v_builder = getattr(visual, "builder", None)
            if isinstance(v_name, str) and v_name and isinstance(v_builder, str) and v_builder:
                builder_by_name[v_name] = v_builder

        disconnected: list[str] = []
        for idx, entry in enumerate(entries):
            if idx in largest_group:
                continue
            item_name = entry.name
            geometry_name = entry.geometry_name
            if isinstance(item_name, str) and item_name:
                label = f"{item_name}:{geometry_name}"
            else:
                label = f"#{idx}:{geometry_name}"

            # Repair hint: nearest connected element, its distance, and the
            # AABB separation axes — tells the author which way (and how far)
            # to move/extend the floating piece without reading the code.
            best_dist = math.inf
            best_idx: Optional[int] = None
            # Cheap AABB pass orders candidates and prunes ones whose lower
            # bound already exceeds the best exact distance found so far.
            ranked = sorted(
                largest_group,
                key=lambda cidx: _aabb_min_distance(entry.aabb, entries[cidx].aabb),
            )
            for cidx in ranked:
                if _aabb_min_distance(entry.aabb, entries[cidx].aabb) >= best_dist:
                    break
                metrics = scene.pair_metrics(
                    neutral_view,
                    entry,
                    entries[cidx],
                    need_distance=True,
                )
                dist = (
                    0.0
                    if metrics.collided
                    else float(
                        metrics.distance
                        if metrics.distance is not None
                        else float("inf")
                    )
                )
                if dist < best_dist:
                    best_dist = dist
                    best_idx = cidx
            if best_idx is not None and math.isfinite(best_dist):
                near = entries[best_idx]
                near_label = (
                    near.name if isinstance(near.name, str) and near.name else f"#{best_idx}"
                )
                moves: list[str] = []
                for ax in range(3):
                    lo_f, hi_f = entry.aabb[0][ax], entry.aabb[1][ax]
                    lo_n, hi_n = near.aabb[0][ax], near.aabb[1][ax]
                    if lo_f > hi_n:
                        moves.append(f"-{'xyz'[ax]} {lo_f - hi_n:.4g}m")
                    elif lo_n > hi_f:
                        moves.append(f"+{'xyz'[ax]} {lo_n - hi_f:.4g}m")
                hint = f" (nearest={near_label} dist={best_dist:.4g}m"
                if moves:
                    hint += f"; close the gap by moving {', '.join(moves)}"
                builder = builder_by_name.get(item_name) if isinstance(item_name, str) else None
                if builder:
                    hint += f"; built_by={builder}"
                hint += ")"
                label += hint
            disconnected.append(label)
        findings.append(
            PartGeometryConnectivityFinding(
                part=part_name,
                connected=len(largest_group),
                total=len(entries),
                disconnected=tuple(disconnected),
                contact_tol=float(contact_tol),
            )
        )
    return findings


def find_unsupported_parts(
    model: object,
    *,
    asset_root: Optional[Path] = None,
    max_pose_samples: int = 1,
    contact_tol: float = 0.001,
    seed: int = 0,
    validate_model: bool = True,
) -> List[UnsupportedPartFinding]:
    """
    Find support-disconnected floating components across sampled poses.

    Parts are grouped by exact physical contact / near-contact into connected
    components. Any component that has no path to a rooted body part is
    reported, so a floating multi-part island such as `lid + top_vent` is
    flagged even when those parts still touch each other.
    """
    return _find_unsupported_parts_physical(
        model,
        asset_root=asset_root,
        max_pose_samples=max_pose_samples,
        contact_tol=float(contact_tol),
        seed=int(seed),
        validate_model=validate_model,
    )


def find_geometry_overlaps(
    model: object,
    *,
    asset_root: Optional[Path] = None,
    max_pose_samples: int = 256,
    overlap_tol: float = 0.005,
    overlap_volume_tol: float = 5e-7,
    allowed_pairs: Optional[Iterable[Tuple[str, str]]] = None,
    seed: int = 0,
    validate_model: bool = True,
) -> List[GeometryOverlap]:
    return _find_collision_overlaps_fcl(
        model,
        asset_root=asset_root,
        max_pose_samples=max_pose_samples,
        overlap_tol=overlap_tol,
        overlap_volume_tol=overlap_volume_tol,
        allowed_pairs=allowed_pairs,
        seed=seed,
        validate_model=validate_model,
    )


def find_geometry_overlaps_in_poses(
    model: object,
    *,
    poses: Sequence[Dict[str, float]],
    asset_root: Optional[Path] = None,
    overlap_tol: float = 0.005,
    overlap_volume_tol: float = 5e-7,
    allowed_pairs: Optional[Iterable[Tuple[str, str]]] = None,
    validate_model: bool = True,
) -> List[GeometryOverlap]:
    if not poses:
        return []
    compiled_model = compile_object_model_with_exact_collisions(
        model,  # type: ignore[arg-type]
        asset_root=asset_root,
        validate=validate_model,
    )
    return _find_collision_overlaps_fcl_for_poses(
        compiled_model,
        asset_root=asset_root,
        source_model=model,
        poses=poses,
        overlap_tol=overlap_tol,
        overlap_volume_tol=overlap_volume_tol,
        allowed_pairs=allowed_pairs,
    )


def validate_no_geometry_overlaps(
    model: object,
    *,
    asset_root: Optional[Path] = None,
    max_pose_samples: int = 256,
    overlap_tol: float = 0.005,
    overlap_volume_tol: float = 5e-7,
    allowed_pairs: Optional[Iterable[Tuple[str, str]]] = None,
    seed: int = 0,
    validate_model: bool = True,
) -> None:
    overlaps = find_geometry_overlaps(
        model,
        asset_root=asset_root,
        max_pose_samples=max_pose_samples,
        overlap_tol=overlap_tol,
        overlap_volume_tol=overlap_volume_tol,
        allowed_pairs=allowed_pairs,
        seed=int(seed),
        validate_model=validate_model,
    )
    if not overlaps:
        return

    worst = max(
        overlaps,
        key=lambda o: (
            float(o.penetration_depth)
            if o.penetration_depth is not None
            else min(o.overlap_depth[0], o.overlap_depth[1], o.overlap_depth[2]),
            float(o.intersection_volume)
            if o.intersection_volume is not None
            else float(o.overlap_volume),
        ),
    )
    min_depth = min(worst.overlap_depth[0], worst.overlap_depth[1], worst.overlap_depth[2])
    actual_penetration = (
        "unknown"
        if worst.penetration_depth is None
        else f"{worst.penetration_depth:.4g}m"
    )
    actual_volume = (
        "unknown"
        if worst.intersection_volume is None
        else f"{worst.intersection_volume:.4g}m^3"
    )
    pose_preview = ", ".join(f"{k}={v:.4g}" for k, v in sorted(worst.pose.items()))

    # Heuristic "what to move" hint: separate world-axis AABBs along the least-overlapping axis.
    a_ctr = _aabb_center(worst.aabb_a)
    b_ctr = _aabb_center(worst.aabb_b)
    dx, dy, dz = worst.overlap_depth
    axis = "x"
    overlap_amt = float(dx)
    if float(dy) < overlap_amt:
        axis, overlap_amt = "y", float(dy)
    if float(dz) < overlap_amt:
        axis, overlap_amt = "z", float(dz)

    sign = 1.0
    if axis == "x" and b_ctr[0] < a_ctr[0]:
        sign = -1.0
    if axis == "y" and b_ctr[1] < a_ctr[1]:
        sign = -1.0
    if axis == "z" and b_ctr[2] < a_ctr[2]:
        sign = -1.0
    suggested_move = sign * (overlap_amt + overlap_tol)
    conservative_note = (
        " The mesh could not be converted to a watertight solid, so this result "
        "uses the conservative FCL collision fallback."
        if worst.narrow_phase == "fcl_conservative_nonmanifold"
        else ""
    )
    raise ValidationError(
        "Geometry overlap check failed: parts interpenetrate beyond the configured tolerance "
        "at a sampled articulation pose. "
        f"worst_pair=({worst.link_a!r}[{worst.elem_a}], {worst.link_b!r}[{worst.elem_b}]) "
        f"penetration={actual_penetration} intersection_volume={actual_volume} "
        f"backend={worst.narrow_phase} "
        f"aabb_min_depth={min_depth:.4g}m aabb_volume={worst.overlap_volume:.4g}m^3 "
        f"pose_index={worst.pose_index} pose=({pose_preview}). "
        f"elem_a=(name={worst.elem_a_name!r} origin_xyz={getattr(worst.elem_a_origin, 'xyz', None)} "
        f"origin_rpy={getattr(worst.elem_a_origin, 'rpy', None)} geom={worst.elem_a_geometry}) "
        f"elem_b=(name={worst.elem_b_name!r} origin_xyz={getattr(worst.elem_b_origin, 'xyz', None)} "
        f"origin_rpy={getattr(worst.elem_b_origin, 'rpy', None)} geom={worst.elem_b_geometry}). "
        f"hint: the AABB broad phase suggests moving {worst.link_b!r} by "
        f"~{suggested_move:.4g}m along world {axis} "
        "(or adjust the responsible articulation origin/limits or element origins). "
        "Fix by adjusting articulation origins/limits and/or visual element origins so parts do not interpenetrate "
        "in the rest pose or across the articulated range."
        f"{conservative_note}"
    )


def default_overlap_tol_from_env() -> float:
    raw = os.environ.get(
        "OBJECT_GEOMETRY_OVERLAP_TOL", os.environ.get("URDF_GEOMETRY_OVERLAP_TOL", "0.005")
    )
    try:
        return float(raw)
    except ValueError:
        return 0.005


def default_overlap_volume_tol_from_env() -> float:
    raw = os.environ.get(
        "OBJECT_GEOMETRY_OVERLAP_VOLUME_TOL",
        os.environ.get("URDF_GEOMETRY_OVERLAP_VOLUME_TOL", "5e-7"),
    )
    try:
        return float(raw)
    except ValueError:
        return 5e-7


def default_contact_tol_from_env() -> float:
    raw = os.environ.get(
        "OBJECT_GEOMETRY_CONTACT_TOL",
        os.environ.get("URDF_GEOMETRY_CONTACT_TOL", "0.001"),
    )
    try:
        return float(raw)
    except ValueError:
        return 0.001
