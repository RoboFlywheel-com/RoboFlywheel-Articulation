# SPDX-License-Identifier: Apache-2.0

"""Pose-aware render helpers for specific-editing paper figures.

Blender/Cycles is the publication backend.  A deterministic PIL software
renderer remains available for fast tests, but is not intended for final
figures.  Neither backend starts a simulator.

The public entry points intentionally accept an SDK ``ArticulatedObject`` by
duck typing.  This keeps the visualization pipeline independent from compiler
or physics internals while preserving the SDK's URDF-style joint semantics.
"""

from __future__ import annotations

import json
import math
import os
import re
import subprocess
import tempfile
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
import trimesh
from PIL import Image, ImageChops, ImageDraw, ImageFont

from specific_editing.pbr_materials import blender_pbr_spec, curated_material_id
from specific_editing.selectors import matches_surface, surface_key

RendererName = Literal["blender", "software"]
RGBA = tuple[float, float, float, float]
Vec3 = tuple[float, float, float]

_DEFAULT_BACKGROUND = (255, 255, 255)
_DEFAULT_COLOR: RGBA = (0.62, 0.66, 0.70, 1.0)
_DEFAULT_BLENDER = Path("/tmp/blender-4.2.21-linux-x64/blender")
_DEFAULT_EGL_VENDOR = Path("/tmp/egl/10_nvidia.json")
_SHADOW_STRENGTH = 1.0
_CAMERA_SENSOR_HEIGHT_MM = 32.0
_CAMERA_FILL_FRACTION = 0.92
_SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9_.-]+")


class RenderError(RuntimeError):
    """Raised when a model cannot be converted into a usable image."""


class RenderBackendUnavailable(RenderError):
    """Raised when the requested renderer cannot run in the current environment."""


@dataclass(frozen=True, slots=True)
class RenderQuality:
    """Small, JSON-friendly health summary for one generated image."""

    width: int
    height: int
    file_bytes: int
    foreground_fraction: float
    mean_luminance: float
    contrast_span: float

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SceneFrame:
    """A shared world-space frame used to compare poses or variants at scale."""

    center: Vec3
    radius: float
    half_extents: Vec3 | None = None

    def __post_init__(self) -> None:
        center = tuple(float(value) for value in self.center)
        if len(center) != 3 or not all(math.isfinite(value) for value in center):
            raise ValueError("SceneFrame.center must contain three finite values")
        radius = float(self.radius)
        if not math.isfinite(radius) or radius <= 0.0:
            raise ValueError("SceneFrame.radius must be positive and finite")
        raw_half_extents = self.half_extents or (radius, radius, radius)
        half_extents = tuple(float(value) for value in raw_half_extents)
        if len(half_extents) != 3 or not all(
            math.isfinite(value) and value > 0.0 for value in half_extents
        ):
            raise ValueError("SceneFrame.half_extents must contain three positive finite values")
        object.__setattr__(self, "center", center)
        object.__setattr__(self, "radius", radius)
        object.__setattr__(self, "half_extents", half_extents)


@dataclass(frozen=True, slots=True)
class VisualMesh:
    """One SDK visual converted to a posed world-space triangle mesh."""

    part_name: str
    visual_name: str
    mesh: trimesh.Trimesh
    rgba: RGBA
    metallic: float = 0.0
    roughness: float = 0.56
    transmission: float = 0.0
    ior: float = 1.45
    material_name: str = ""
    material_class_id: str = ""
    pbr_material_id: str | None = None
    targeted: bool = False

    @property
    def key(self) -> str:
        return f"{self.part_name}/{self.visual_name}"


@dataclass(frozen=True, slots=True)
class RenderRecord:
    path: Path
    view: str
    pose: str
    renderer: str
    quality: RenderQuality
    target_matches: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "view": self.view,
            "pose": self.pose,
            "renderer": self.renderer,
            "quality": self.quality.to_dict(),
            "target_matches": list(self.target_matches),
        }


@dataclass(frozen=True, slots=True)
class ContactSheetRecord:
    path: Path
    image_paths: tuple[Path, ...]
    quality: RenderQuality

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": str(self.path),
            "image_paths": [str(path) for path in self.image_paths],
            "quality": self.quality.to_dict(),
        }


def _safe_name(value: object, *, fallback: str) -> str:
    name = _SAFE_NAME_RE.sub("-", str(value).strip()).strip("-._")
    return (name or fallback)[:96]


def _joint_type(joint: object) -> str:
    value = getattr(joint, "articulation_type", getattr(joint, "joint_type", "fixed"))
    value = getattr(value, "value", value)
    return str(value).rsplit(".", 1)[-1].lower()


def _origin_matrix(origin: object | None) -> np.ndarray:
    if origin is None:
        return np.eye(4, dtype=float)
    if isinstance(origin, Mapping):
        xyz = origin.get("xyz", (0.0, 0.0, 0.0))
        rpy = origin.get("rpy", (0.0, 0.0, 0.0))
    else:
        xyz = getattr(origin, "xyz", (0.0, 0.0, 0.0))
        rpy = getattr(origin, "rpy", (0.0, 0.0, 0.0))
    x, y, z = (float(value) for value in xyz)
    roll, pitch, yaw = (float(value) for value in rpy)
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    rotation = np.array(
        [
            [cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
            [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
            [-sp, cp * sr, cp * cr],
        ],
        dtype=float,
    )
    transform = np.eye(4, dtype=float)
    transform[:3, :3] = rotation
    transform[:3, 3] = (x, y, z)
    return transform


def _axis_angle_matrix(axis: Sequence[float], angle: float) -> np.ndarray:
    vector = np.asarray(tuple(float(value) for value in axis), dtype=float)
    length = float(np.linalg.norm(vector))
    if length <= 1e-12:
        return np.eye(4, dtype=float)
    x, y, z = vector / length
    c = math.cos(float(angle))
    s = math.sin(float(angle))
    one_minus_c = 1.0 - c
    rotation = np.array(
        [
            [c + x * x * one_minus_c, x * y * one_minus_c - z * s, x * z * one_minus_c + y * s],
            [y * x * one_minus_c + z * s, c + y * y * one_minus_c, y * z * one_minus_c - x * s],
            [z * x * one_minus_c - y * s, z * y * one_minus_c + x * s, c + z * z * one_minus_c],
        ],
        dtype=float,
    )
    transform = np.eye(4, dtype=float)
    transform[:3, :3] = rotation
    return transform


def _joint_limits(joint: object) -> tuple[float | None, float | None]:
    limits = getattr(joint, "motion_limits", getattr(joint, "limit", None))
    lower = getattr(limits, "lower", None) if limits is not None else None
    upper = getattr(limits, "upper", None) if limits is not None else None
    lower_value = float(lower) if isinstance(lower, (int, float)) and math.isfinite(lower) else None
    upper_value = float(upper) if isinstance(upper, (int, float)) and math.isfinite(upper) else None
    return lower_value, upper_value


def _rest_position(joint: object) -> float:
    lower, upper = _joint_limits(joint)
    value = 0.0
    if lower is not None:
        value = max(value, lower)
    if upper is not None:
        value = min(value, upper)
    return value


def _open_position(joint: object, rest: float) -> float:
    metadata = getattr(joint, "meta", None)
    if isinstance(metadata, Mapping):
        authored = metadata.get("opening_endpoint", metadata.get("open_position"))
        if isinstance(authored, (int, float)) and math.isfinite(float(authored)):
            return float(authored)
        if isinstance(authored, str):
            lower, upper = _joint_limits(joint)
            if authored.lower() == "lower" and lower is not None:
                return lower
            if authored.lower() == "upper" and upper is not None:
                return upper

    joint_type = _joint_type(joint)
    if joint_type == "continuous":
        return rest + math.pi / 2.0
    lower, upper = _joint_limits(joint)
    candidates = [value for value in (lower, upper) if value is not None]
    if not candidates:
        return rest
    # Mirrored parts often use [-limit, 0] and [0, +limit].  Choosing the
    # endpoint furthest from the zero/rest pose opens both sides correctly.
    return max(candidates, key=lambda value: (abs(value - rest), value))


def pose_values(
    model: object,
    pose: str | Mapping[str, float] = "rest",
) -> dict[str, float]:
    """Resolve ``rest``, ``mid`` or ``open`` into independent joint values.

    ``rest`` is zero clamped to the declared range.  ``open`` is the finite
    endpoint furthest from rest (or +90 degrees for continuous joints), which
    naturally handles mirrored negative-limit hinges.  Mimic joints are left
    to forward kinematics and must not be set directly.
    """

    if isinstance(pose, Mapping):
        return {str(name): float(value) for name, value in pose.items()}
    pose_name = str(pose).strip().lower()
    aliases = {"closed": "rest", "neutral": "rest", "half": "mid", "max": "open"}
    pose_name = aliases.get(pose_name, pose_name)
    if pose_name not in {"rest", "mid", "open"}:
        raise ValueError(f"Unknown pose {pose!r}; expected rest, mid, open, or a joint mapping")

    values: dict[str, float] = {}
    joints = getattr(model, "articulations", getattr(model, "joints", ())) or ()
    for joint in joints:
        joint_type = _joint_type(joint)
        if joint_type in {"fixed", "floating"} or getattr(joint, "mimic", None) is not None:
            continue
        name = str(getattr(joint, "name", "")).strip()
        if not name:
            continue
        rest = _rest_position(joint)
        opened = _open_position(joint, rest)
        values[name] = {
            "rest": rest,
            "mid": rest + 0.5 * (opened - rest),
            "open": opened,
        }[pose_name]
    return values


def _resolved_joint_values(model: object, supplied: Mapping[str, float]) -> dict[str, Any]:
    joints = getattr(model, "articulations", getattr(model, "joints", ())) or ()
    by_name = {
        str(getattr(joint, "name")): joint
        for joint in joints
        if str(getattr(joint, "name", "")).strip()
    }
    resolved: dict[str, Any] = {}
    active: list[str] = []

    def resolve(name: str) -> Any:
        if name in resolved:
            return resolved[name]
        joint = by_name[name]
        if name in active:
            cycle = " -> ".join((*active[active.index(name) :], name))
            raise RenderError(f"Mimic articulation cycle: {cycle}")
        active.append(name)
        mimic = getattr(joint, "mimic", None)
        if mimic is not None:
            source = str(getattr(mimic, "joint", "")).strip()
            if source not in by_name:
                raise RenderError(f"Articulation {name!r} mimics missing joint {source!r}")
            value = float(resolve(source)) * float(getattr(mimic, "multiplier", 1.0)) + float(
                getattr(mimic, "offset", 0.0)
            )
        elif _joint_type(joint) == "floating":
            # The articulation origin is already applied by FK; the neutral
            # floating motion itself is identity rather than that origin again.
            value = supplied.get(name, None)
        else:
            value = float(supplied.get(name, _rest_position(joint)))
        active.pop()
        resolved[name] = value
        return value

    for joint_name in by_name:
        resolve(joint_name)
    return resolved


def compute_world_transforms(
    model: object,
    joint_positions: Mapping[str, float] | None = None,
) -> dict[str, np.ndarray]:
    """Compute URDF-style part transforms without importing simulator code."""

    parts = list(getattr(model, "parts", getattr(model, "links", ())) or ())
    joints = list(getattr(model, "articulations", getattr(model, "joints", ())) or ())
    names = [str(getattr(part, "name", "")).strip() for part in parts]
    if not names or any(not name for name in names):
        raise RenderError("Model must contain named parts")
    if len(names) != len(set(names)):
        raise RenderError("Model part names must be unique")

    part_names = set(names)
    children: set[str] = set()
    outgoing: dict[str, list[object]] = {name: [] for name in names}
    for joint in joints:
        parent = str(getattr(joint, "parent", ""))
        child = str(getattr(joint, "child", ""))
        if parent not in part_names or child not in part_names:
            raise RenderError(f"Articulation references missing parts: {parent!r} -> {child!r}")
        if child in children:
            raise RenderError(f"Part {child!r} has more than one parent articulation")
        children.add(child)
        outgoing[parent].append(joint)

    roots = [name for name in names if name not in children]
    if not roots:
        raise RenderError("Articulation graph has no root part")
    resolved = _resolved_joint_values(model, dict(joint_positions or {}))
    world: dict[str, np.ndarray] = {name: np.eye(4, dtype=float) for name in roots}
    queue = list(roots)
    visited: set[str] = set()
    while queue:
        parent = queue.pop(0)
        if parent in visited:
            continue
        visited.add(parent)
        for joint in outgoing[parent]:
            child = str(getattr(joint, "child"))
            joint_type = _joint_type(joint)
            origin = _origin_matrix(getattr(joint, "origin", None))
            value = resolved.get(str(getattr(joint, "name", "")), 0.0)
            motion = np.eye(4, dtype=float)
            if joint_type in {"revolute", "continuous"}:
                motion = _axis_angle_matrix(getattr(joint, "axis", (0.0, 0.0, 1.0)), float(value))
            elif joint_type == "prismatic":
                axis = np.asarray(getattr(joint, "axis", (0.0, 0.0, 1.0)), dtype=float)
                norm = float(np.linalg.norm(axis))
                if norm > 1e-12:
                    motion[:3, 3] = axis / norm * float(value)
            elif joint_type == "floating":
                motion = _origin_matrix(value)
            world[child] = world[parent] @ origin @ motion
            queue.append(child)

    missing = part_names - set(world)
    if missing:
        raise RenderError(f"Unreachable parts in articulation graph: {sorted(missing)}")
    return world


def _primitive_mesh(geometry: object) -> trimesh.Trimesh | None:
    class_name = type(geometry).__name__.lower()
    if class_name == "box" or (hasattr(geometry, "size") and not hasattr(geometry, "filename")):
        size = tuple(float(value) for value in getattr(geometry, "size"))
        if len(size) == 3:
            return trimesh.creation.box(extents=size)
    if class_name == "cylinder" or (hasattr(geometry, "radius") and hasattr(geometry, "length")):
        return trimesh.creation.cylinder(
            radius=float(getattr(geometry, "radius")),
            height=float(getattr(geometry, "length")),
            sections=32,
        )
    if class_name == "sphere" or (
        hasattr(geometry, "radius")
        and not hasattr(geometry, "length")
        and not hasattr(geometry, "filename")
    ):
        return trimesh.creation.icosphere(subdivisions=2, radius=float(getattr(geometry, "radius")))
    return None


def _resolve_mesh_path(geometry: object, assets: object | None) -> Path | None:
    materialized = getattr(geometry, "materialized_path", None)
    if materialized:
        path = Path(os.fspath(materialized)).expanduser()
        if path.exists():
            return path.resolve()
    filename = getattr(geometry, "filename", None)
    if not filename:
        return None
    path = Path(os.fspath(filename)).expanduser()
    if path.is_absolute():
        return path.resolve()
    if assets is not None:
        mesh_path = getattr(assets, "mesh_path", None)
        if callable(mesh_path):
            try:
                candidate = Path(mesh_path(path, ensure_dir=False))
            except TypeError:
                candidate = Path(mesh_path(path))
            if candidate.exists():
                return candidate.resolve()
        root = getattr(assets, "asset_root", getattr(assets, "root", None))
        if root is not None:
            candidate = Path(root) / path
            if candidate.exists():
                return candidate.resolve()
    if path.exists():
        return path.resolve()
    return None


def _load_mesh_geometry(geometry: object, assets: object | None) -> trimesh.Trimesh:
    source = getattr(geometry, "source_geometry", None)
    if source is not None:
        mesh = _primitive_mesh(source)
        if mesh is None:
            raise RenderError(f"Unsupported mesh source geometry: {type(source).__name__}")
        source_transform = getattr(geometry, "source_transform", None)
        if source_transform is not None:
            mesh.apply_transform(np.asarray(source_transform, dtype=float))
    else:
        mesh = _primitive_mesh(geometry)
        if mesh is None:
            path = _resolve_mesh_path(geometry, assets)
            if path is None or not path.is_file():
                filename = getattr(geometry, "filename", None)
                raise RenderError(f"Visual mesh file cannot be resolved: {filename!r}")
            loaded = trimesh.load_mesh(path, force="mesh", process=True)
            if isinstance(loaded, trimesh.Scene):
                geometries = tuple(loaded.geometry.values())
                if not geometries:
                    raise RenderError(f"Visual mesh contains no geometry: {path}")
                mesh = trimesh.util.concatenate(geometries)
            elif isinstance(loaded, trimesh.Trimesh):
                mesh = loaded
            else:
                raise RenderError(f"Unsupported mesh payload in {path}: {type(loaded).__name__}")

    scale = getattr(geometry, "scale", None)
    if scale is not None:
        scale_values = tuple(float(value) for value in scale)
        scale_matrix = np.eye(4, dtype=float)
        scale_matrix[0, 0], scale_matrix[1, 1], scale_matrix[2, 2] = scale_values
        mesh.apply_transform(scale_matrix)
    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        raise RenderError("Visual mesh contains no renderable triangles")
    return mesh


def _rgba(value: object, material_lookup: Mapping[str, object]) -> RGBA:
    material = material_lookup.get(value, value) if isinstance(value, str) else value
    rgba = getattr(material, "rgba", None)
    if isinstance(rgba, Sequence) and not isinstance(rgba, (str, bytes)) and len(rgba) >= 3:
        values = [float(channel) for channel in rgba[:4]]
        if len(values) == 3:
            values.append(1.0)
        # SDK colors are normally 0..1, but accepting byte colors makes this
        # helper useful for small hand-authored examples as well.
        if max(values[:3], default=0.0) > 1.0:
            values[:3] = [channel / 255.0 for channel in values[:3]]
        return tuple(float(np.clip(channel, 0.0, 1.0)) for channel in values)  # type: ignore[return-value]
    return _DEFAULT_COLOR


def _visual_appearance(
    model: object,
    *,
    part_name: str,
    visual_name: str,
    visual: object,
    material_lookup: Mapping[str, object],
) -> tuple[RGBA, float, float, float, float, str, str, str | None]:
    raw_material = getattr(visual, "material", None)
    resolved_material = (
        material_lookup.get(raw_material, raw_material)
        if isinstance(raw_material, str)
        else raw_material
    )
    material_name = str(
        getattr(resolved_material, "name", raw_material if isinstance(raw_material, str) else "")
        or ""
    )
    rgba = _rgba(raw_material, material_lookup)
    material_class = str(getattr(visual, "material_class_id", "") or "")
    metallic, roughness, transmission, ior = 0.0, 0.56, 0.0, 1.45
    if material_class.startswith("metal."):
        metallic, roughness = 0.78, 0.32
    elif material_class.startswith(("glass.", "optical.")):
        roughness, transmission = 0.12, 0.78
    elif material_class.startswith(("rubber.", "fabric.")):
        roughness = 0.88

    key = surface_key(part_name, visual_name)
    metadata = getattr(model, "meta", {}) or {}
    override_material_id: str | None = None
    for override in metadata.get("specific_editing_material_overrides", ()):
        surfaces = override.get("surfaces", ())
        if key not in surfaces and (surfaces or part_name not in override.get("parts", ())):
            continue
        values = override.get("rgba", rgba)
        rgba = tuple(float(value) for value in values)  # type: ignore[assignment]
        metallic = float(override.get("metallic", metallic))
        roughness = float(override.get("roughness", roughness))
        transmission = float(override.get("transmission", transmission))
        ior = float(override.get("ior", ior))
        override_id = override.get("material_id")
        if isinstance(override_id, str) and override_id:
            override_material_id = override_id
        break
    generator_id = str(metadata.get("specific_editing_generator_id", ""))
    pbr_material_id = override_material_id or curated_material_id(generator_id, material_name)
    return (
        rgba,
        metallic,
        roughness,
        transmission,
        ior,
        material_name,
        material_class,
        pbr_material_id,
    )


def extract_visual_meshes(
    model: object,
    *,
    pose: str | Mapping[str, float] = "rest",
    target_patterns: Sequence[str] | str = (),
) -> tuple[VisualMesh, ...]:
    """Extract every visual as a colored, posed world-space triangle mesh."""

    positions = pose_values(model, pose)
    world = compute_world_transforms(model, positions)
    materials = {
        str(getattr(material, "name", "")): material
        for material in (getattr(model, "materials", ()) or ())
    }
    output: list[VisualMesh] = []
    parts = getattr(model, "parts", getattr(model, "links", ())) or ()
    for part in parts:
        part_name = str(getattr(part, "name", "part"))
        assets = getattr(part, "assets", None) or getattr(model, "assets", None)
        for index, visual in enumerate(getattr(part, "visuals", ()) or ()):
            visual_name = str(getattr(visual, "name", None) or f"visual_{index:03d}")
            try:
                mesh = _load_mesh_geometry(getattr(visual, "geometry"), assets).copy()
            except Exception as exc:
                if isinstance(exc, RenderError):
                    raise RenderError(f"{part_name}/{visual_name}: {exc}") from exc
                raise RenderError(f"Cannot load visual {part_name}/{visual_name}: {exc}") from exc
            mesh.apply_transform(_origin_matrix(getattr(visual, "origin", None)))
            mesh.apply_transform(world[part_name])
            (
                rgba,
                metallic,
                roughness,
                transmission,
                ior,
                material_name,
                material_class_id,
                pbr_material_id,
            ) = _visual_appearance(
                model,
                part_name=part_name,
                visual_name=visual_name,
                visual=visual,
                material_lookup=materials,
            )
            output.append(
                VisualMesh(
                    part_name=part_name,
                    visual_name=visual_name,
                    mesh=mesh,
                    rgba=rgba,
                    metallic=metallic,
                    roughness=roughness,
                    transmission=transmission,
                    ior=ior,
                    material_name=material_name,
                    material_class_id=material_class_id,
                    pbr_material_id=pbr_material_id,
                    targeted=matches_surface(
                        target_patterns,
                        part_name=part_name,
                        visual_name=visual_name,
                        visual=visual,
                    ),
                )
            )
    if not output:
        raise RenderError("ArticulatedObject contains no renderable visuals")
    return tuple(output)


def frame_visual_meshes(
    mesh_groups: Iterable[Iterable[VisualMesh]],
    *,
    padding: float = 1.10,
) -> SceneFrame:
    """Build one scale-preserving frame around one or more poses/variants."""

    bounds: list[np.ndarray] = []
    for meshes in mesh_groups:
        bounds.extend(np.asarray(item.mesh.bounds, dtype=float) for item in meshes)
    if not bounds:
        raise RenderError("Cannot frame an empty visual collection")
    lower = np.min(np.stack([bound[0] for bound in bounds]), axis=0)
    upper = np.max(np.stack([bound[1] for bound in bounds]), axis=0)
    center = (lower + upper) * 0.5
    half_extents = np.maximum((upper - lower) * 0.5 * float(padding), 1e-6)
    radius = max(float(np.linalg.norm(half_extents)), 1e-6)
    return SceneFrame(
        center=tuple(float(value) for value in center),
        radius=radius,
        half_extents=tuple(float(value) for value in half_extents),
    )


def merge_frames(
    frames: Iterable[SceneFrame],
    *,
    padding: float = 1.10,
) -> SceneFrame:
    """Merge unpadded per-model frames without retaining their source models."""

    lower: np.ndarray | None = None
    upper: np.ndarray | None = None
    for frame in frames:
        center = np.asarray(frame.center, dtype=float)
        half_extents = np.asarray(frame.half_extents, dtype=float)
        frame_lower = center - half_extents
        frame_upper = center + half_extents
        lower = frame_lower if lower is None else np.minimum(lower, frame_lower)
        upper = frame_upper if upper is None else np.maximum(upper, frame_upper)
    if lower is None or upper is None:
        raise RenderError("Cannot merge an empty frame collection")
    center = (lower + upper) * 0.5
    half_extents = np.maximum((upper - lower) * 0.5 * float(padding), 1e-6)
    radius = max(float(np.linalg.norm(half_extents)), 1e-6)
    return SceneFrame(
        center=tuple(float(value) for value in center),
        radius=radius,
        half_extents=tuple(float(value) for value in half_extents),
    )


def shared_frame(
    models: Sequence[object],
    *,
    poses: Sequence[str | Mapping[str, float]] | str | Mapping[str, float] = ("closed",),
    front_axis: str = "-y",
    size: tuple[int, int] = (800, 640),
    padding: float = 1.10,
) -> SceneFrame:
    """Compute one world-space frame shared by every model, pose and view.

    The frame stores a padded AABB and its enclosing radius.  Blender projects
    that same AABB for each requested semantic view, keeping all variants at a
    fixed scale while avoiding excessive whitespace for long, thin objects.
    """

    model_list = tuple(models)
    if not model_list:
        raise ValueError("models must contain at least one ArticulatedObject")
    if isinstance(poses, (str, Mapping)):
        pose_list: tuple[str | Mapping[str, float], ...] = (poses,)
    else:
        pose_list = tuple(poses)
    if not pose_list:
        raise ValueError("poses must contain at least one pose")
    _axis_vector(front_axis)
    width, height = (int(value) for value in size)
    if width < 16 or height < 16:
        raise ValueError("size dimensions must be at least 16 pixels")
    groups = (extract_visual_meshes(model, pose=pose) for model in model_list for pose in pose_list)
    return frame_visual_meshes(groups, padding=padding)


def _axis_vector(axis: str) -> np.ndarray:
    key = str(axis).strip().lower().replace(" ", "")
    vectors = {
        "+x": (1.0, 0.0, 0.0),
        "x": (1.0, 0.0, 0.0),
        "-x": (-1.0, 0.0, 0.0),
        "+y": (0.0, 1.0, 0.0),
        "y": (0.0, 1.0, 0.0),
        "-y": (0.0, -1.0, 0.0),
        "+z": (0.0, 0.0, 1.0),
        "z": (0.0, 0.0, 1.0),
        "-z": (0.0, 0.0, -1.0),
    }
    if key not in vectors:
        raise ValueError(f"Unknown front_axis {axis!r}; expected +/-x, +/-y, or +/-z")
    return np.asarray(vectors[key], dtype=float)


def _view_direction(view: str, front_axis: str) -> tuple[np.ndarray, np.ndarray]:
    front = _axis_vector(front_axis)
    world_up = np.array([0.0, 0.0, 1.0], dtype=float)
    if abs(float(np.dot(front, world_up))) > 0.95:
        world_up = np.array([0.0, 1.0, 0.0], dtype=float)
    side = np.cross(world_up, front)
    side /= np.linalg.norm(side)
    key = str(view).strip().lower().replace("-", "_")
    directions = {
        "front": front + 0.16 * world_up,
        "rear": -front + 0.16 * world_up,
        "side": side + 0.20 * world_up,
        "left": -side + 0.20 * world_up,
        "top": world_up + 0.06 * front,
        "iso": front + 0.82 * side + 0.62 * world_up,
        "front_iso": front - 0.82 * side + 0.62 * world_up,
        "rear_iso": -front - 0.72 * side + 0.58 * world_up,
    }
    if key not in directions:
        raise ValueError(
            f"Unknown view {view!r}; expected front, side, left, rear, top, iso, "
            "front_iso, or rear_iso"
        )
    direction = directions[key]
    direction /= np.linalg.norm(direction)
    return direction, world_up


def _camera_basis(direction: np.ndarray, world_up: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    forward = -direction
    right = np.cross(forward, world_up)
    if float(np.linalg.norm(right)) <= 1e-8:
        right = np.array([1.0, 0.0, 0.0], dtype=float)
    right /= np.linalg.norm(right)
    up = np.cross(right, forward)
    up /= np.linalg.norm(up)
    return right, up


def _camera_pose(
    center: np.ndarray, direction: np.ndarray, world_up: np.ndarray, distance: float
) -> np.ndarray:
    right, up = _camera_basis(direction, world_up)
    forward = -direction
    transform = np.eye(4, dtype=float)
    transform[:3, :3] = np.stack((right, up, -forward), axis=1)
    transform[:3, 3] = center + direction * distance
    return transform


def _perspective_camera_distance(
    frame: SceneFrame,
    direction: np.ndarray,
    world_up: np.ndarray,
    *,
    image_size: tuple[int, int],
    focal_length_mm: float,
) -> float:
    """Fit the shared padded AABB into a perspective view at a stable margin."""

    right, up = _camera_basis(direction, world_up)
    half_extents = np.asarray(frame.half_extents, dtype=float)
    width, height = image_size
    vertical_tangent = _CAMERA_SENSOR_HEIGHT_MM / (2.0 * float(focal_length_mm))
    horizontal_tangent = vertical_tangent * float(width) / float(height)
    corners = (
        np.asarray((x, y, z), dtype=float) * half_extents
        for x in (-1.0, 1.0)
        for y in (-1.0, 1.0)
        for z in (-1.0, 1.0)
    )
    required_distance = max(
        max(
            float(corner @ direction)
            + abs(float(corner @ right)) / (horizontal_tangent * _CAMERA_FILL_FRACTION),
            float(corner @ direction)
            + abs(float(corner @ up)) / (vertical_tangent * _CAMERA_FILL_FRACTION),
        )
        for corner in corners
    )
    return max(required_distance, 1e-3)


def _effective_colors(meshes: Sequence[VisualMesh], background: tuple[int, int, int]) -> list[RGBA]:
    has_target = any(item.targeted for item in meshes)
    background_rgb = np.asarray(background, dtype=float) / 255.0
    colors: list[RGBA] = []
    for item in meshes:
        rgba = np.asarray(item.rgba, dtype=float)
        if has_target and not item.targeted:
            rgba[:3] = rgba[:3] * 0.70 + background_rgb * 0.30
        colors.append(tuple(float(value) for value in rgba))  # type: ignore[arg-type]
    return colors


def _render_software(
    meshes: Sequence[VisualMesh],
    output: Path,
    *,
    direction: np.ndarray,
    world_up: np.ndarray,
    frame: SceneFrame,
    image_size: tuple[int, int],
    supersample: int,
    background: tuple[int, int, int],
) -> None:
    width, height = image_size
    factor = max(1, int(supersample))
    render_width, render_height = width * factor, height * factor
    right, up = _camera_basis(direction, world_up)
    forward = -direction
    center = np.asarray(frame.center, dtype=float)
    center_xy = np.array((float(center @ right), float(center @ up)), dtype=float)
    scale = min(render_width, render_height) * 0.5 / frame.radius
    colors = _effective_colors(meshes, background)

    polygons: list[tuple[float, list[tuple[float, float]], tuple[int, int, int], bool]] = []
    # A camera-relative key light gives stable, readable shading for any view.
    light = direction + 0.35 * right + 0.65 * world_up
    light /= np.linalg.norm(light)
    half_vector = light + direction
    half_vector /= np.linalg.norm(half_vector)
    for item, rgba in zip(meshes, colors, strict=True):
        vertices = np.asarray(item.mesh.vertices, dtype=float)
        xy = np.column_stack((vertices @ right, vertices @ up))
        screen = (xy - center_xy) * scale
        screen[:, 0] += render_width * 0.5
        screen[:, 1] = render_height * 0.5 - screen[:, 1]
        depth = vertices @ forward
        base = np.asarray(rgba[:3], dtype=float) * 255.0
        alpha = float(np.clip(rgba[3] * (1.0 - 0.35 * item.transmission), 0.0, 1.0))
        roughness = float(np.clip(item.roughness, 0.0, 1.0))
        metallic = float(np.clip(item.metallic, 0.0, 1.0))
        for face, normal in zip(
            np.asarray(item.mesh.faces, dtype=np.int64),
            np.asarray(item.mesh.face_normals, dtype=float),
            strict=False,
        ):
            facing = float(np.dot(normal, direction))
            if facing <= 1e-8:
                continue
            points = [(float(screen[index, 0]), float(screen[index, 1])) for index in face]
            diffuse = max(0.0, float(np.dot(normal, light)))
            shade = 0.44 + (0.54 - 0.16 * metallic) * diffuse
            specular_power = 4.0 + 72.0 * (1.0 - roughness) ** 2
            specular = max(0.0, float(np.dot(normal, half_vector))) ** specular_power
            specular_strength = (0.08 + 0.66 * metallic) * (1.0 - 0.45 * roughness)
            specular_color = base if metallic > 0.5 else np.full(3, 255.0)
            rgb_float = np.clip(
                base * shade + specular_color * specular * specular_strength,
                15.0,
                250.0,
            )
            if alpha < 0.999:
                rgb_float = rgb_float * alpha + np.asarray(background, dtype=float) * (1.0 - alpha)
            rgb = tuple(int(value) for value in rgb_float)
            polygons.append((float(np.mean(depth[face])), points, rgb, item.targeted))

    if not polygons:
        raise RenderError("Software renderer found no camera-facing triangles")
    image = Image.new("RGB", (render_width, render_height), background)
    draw = ImageDraw.Draw(image)
    # Larger forward-depth values are farther from a camera on +direction.
    for _depth, points, rgb, _targeted in sorted(polygons, key=lambda row: row[0], reverse=True):
        # Do not outline individual triangles: tessellation diagonals are an
        # implementation detail and make flat panels look wireframed in paper
        # figures.  Face shading and target muting provide sufficient shape
        # separation without exposing the mesh topology.
        draw.polygon(points, fill=rgb)
    if factor > 1:
        image = image.resize((width, height), Image.Resampling.LANCZOS)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def _blender_executable() -> Path:
    configured = os.environ.get("SPECIFIC_EDITING_BLENDER")
    executable = Path(configured).expanduser() if configured else _DEFAULT_BLENDER
    if not executable.is_file() or not os.access(executable, os.X_OK):
        source = "SPECIFIC_EDITING_BLENDER" if configured else "the documented default path"
        raise RenderBackendUnavailable(
            f"Blender executable is unavailable at {executable} ({source})"
        )
    return executable.resolve()


def _shadow_pass_paths(output: Path) -> tuple[Path, Path]:
    return (
        output.with_name(f"{output.stem}__shadow_with_0001.png"),
        output.with_name(f"{output.stem}__shadow_clean.png"),
    )


def _composite_cycles_render(
    foreground: Image.Image,
    *,
    shadow_with_path: Path,
    shadow_clean_path: Path,
    background: tuple[int, int, int],
    shadow_strength: float = _SHADOW_STRENGTH,
    transparent: bool = False,
) -> Image.Image:
    try:
        with Image.open(shadow_with_path) as source:
            shadow_with = np.asarray(source.convert("RGB"), dtype=np.float32) / 255.0
        with Image.open(shadow_clean_path) as source:
            shadow_clean = np.asarray(source.convert("RGB"), dtype=np.float32) / 255.0
    except Exception as exc:
        raise RenderError(f"Cannot read Cycles shadow-catcher passes: {exc}") from exc
    if shadow_with.shape != shadow_clean.shape or shadow_with.shape[:2] != (
        foreground.height,
        foreground.width,
    ):
        raise RenderError("Cycles shadow-catcher passes disagree with the foreground size")

    ratio = np.clip(shadow_with / np.maximum(shadow_clean, 1.0 / 255.0), 0.0, 1.0)
    deficit = 1.0 - ratio
    deficit[deficit < 0.015] = 0.0
    multiplier = 1.0 - float(shadow_strength) * deficit
    if transparent:
        # Keep the film alpha and encode the ground shadow as semi-transparent
        # black, so compositing over any backdrop matches the opaque render.
        foreground_rgba = np.asarray(foreground.convert("RGBA"), dtype=np.float32) / 255.0
        foreground_alpha = foreground_rgba[..., 3:4]
        shadow_alpha = np.clip(1.0 - multiplier, 0.0, 1.0).mean(axis=2, keepdims=True)
        out_alpha = foreground_alpha + shadow_alpha * (1.0 - foreground_alpha)
        safe_alpha = np.maximum(out_alpha, 1.0 / 255.0)
        out_rgb = foreground_rgba[..., :3] * foreground_alpha / safe_alpha
        rgba = np.concatenate((out_rgb, out_alpha), axis=-1)
        return Image.fromarray(np.uint8(np.clip(rgba * 255.0 + 0.5, 0.0, 255.0)), mode="RGBA")
    background_rgb = np.asarray(background, dtype=np.float32).reshape((1, 1, 3))
    shadowed = np.uint8(np.clip(multiplier * background_rgb + 0.5, 0.0, 255.0))
    canvas = Image.fromarray(shadowed, mode="RGB").convert("RGBA")
    canvas.alpha_composite(foreground.convert("RGBA"))
    return canvas.convert("RGB")


def _export_blender_input(
    meshes: Sequence[VisualMesh],
    path: Path,
    *,
    background: tuple[int, int, int],
) -> dict[str, dict[str, Any]]:
    """Write posed surfaces to a temporary GLB and return exact PBR overrides."""

    scene = trimesh.Scene(base_frame="world")
    materials: dict[str, dict[str, Any]] = {}
    # trimesh writes Z-up coordinates directly into a Y-up glTF. Blender's
    # importer applies this conversion, so pre-rotate by its inverse to retain
    # the SDK's Z-up world coordinates and keep camera matrices unchanged.
    blender_import = np.array(((1.0, 0.0, 0.0), (0.0, 0.0, -1.0), (0.0, 1.0, 0.0)), dtype=float)
    pre_rotate = np.eye(4, dtype=float)
    pre_rotate[:3, :3] = blender_import.T

    for index, (item, rgba) in enumerate(
        zip(meshes, _effective_colors(meshes, background), strict=True)
    ):
        mesh = item.mesh.copy()
        mesh.apply_transform(pre_rotate)
        material_name = f"specific_editing_surface_{index:04d}"
        rgba_values = [float(np.clip(value, 0.0, 1.0)) for value in rgba]
        mesh.visual = trimesh.visual.TextureVisuals(
            material=trimesh.visual.material.PBRMaterial(
                name=material_name,
                baseColorFactor=np.rint(np.asarray(rgba_values) * 255.0).astype(np.uint8),
                metallicFactor=float(np.clip(item.metallic, 0.0, 1.0)),
                roughnessFactor=float(np.clip(item.roughness, 0.0, 1.0)),
                alphaMode="BLEND" if rgba_values[3] < 0.999 else "OPAQUE",
                doubleSided=True,
            )
        )
        scene.add_geometry(
            mesh,
            node_name=f"surface_{index:04d}",
            geom_name=f"surface_{index:04d}",
        )
        materials[material_name] = {
            "rgba": rgba_values,
            "metallic": float(np.clip(item.metallic, 0.0, 1.0)),
            "roughness": float(np.clip(item.roughness, 0.0, 1.0)),
            "transmission": float(np.clip(item.transmission, 0.0, 1.0)),
            "ior": float(np.clip(item.ior, 1.0, 3.0)),
        }
        if item.pbr_material_id is not None:
            materials[material_name]["pbr"] = blender_pbr_spec(item.pbr_material_id)

    if not materials:
        raise RenderError("Cannot send an empty scene to Blender")
    path.write_bytes(scene.export(file_type="glb"))
    return materials


def _render_blender_batch(
    meshes: Sequence[VisualMesh],
    outputs: Sequence[tuple[str, Path]],
    *,
    front_axis: str,
    frame: SceneFrame,
    image_size: tuple[int, int],
    supersample: int,
    background: tuple[int, int, int],
    shadow_strength: float,
    additional_shadow_outputs: Mapping[float, Sequence[Path]] | None = None,
    transparent: bool = False,
) -> str:
    """Render all semantic views for one posed model in one Blender process."""

    executable = _blender_executable()
    worker = Path(__file__).with_name("blender_worker.py")
    if not worker.is_file():
        raise RenderBackendUnavailable(f"Blender worker is missing: {worker}")

    width, height = image_size
    factor = max(1, int(supersample))
    extra_outputs = dict(additional_shadow_outputs or {})
    for strength, destinations in extra_outputs.items():
        if not math.isfinite(float(strength)) or not 0.0 <= float(strength) <= 1.0:
            raise ValueError("additional shadow strengths must be in [0, 1]")
        if len(destinations) != len(outputs):
            raise ValueError("each additional shadow output set must match the view count")
    center = np.asarray(frame.center, dtype=float)
    frame_scale = 2.0 * frame.radius * max(1.0, height / width)
    focal_length_mm = 60.0
    for _view, output in outputs:
        output.parent.mkdir(parents=True, exist_ok=True)
    for destinations in extra_outputs.values():
        for output in destinations:
            output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="specific-editing-blender-", dir="/tmp") as temp_text:
        temp_root = Path(temp_text)
        input_glb = temp_root / "posed_scene.glb"
        materials = _export_blender_input(meshes, input_glb, background=background)
        jobs: list[dict[str, Any]] = []
        temporary_outputs: list[Path] = []
        for index, (view, _output) in enumerate(outputs):
            direction, world_up = _view_direction(view, front_axis)
            distance = _perspective_camera_distance(
                frame,
                direction,
                world_up,
                image_size=image_size,
                focal_length_mm=focal_length_mm,
            )
            temporary_output = temp_root / f"render_{index:03d}.png"
            temporary_outputs.append(temporary_output)
            jobs.append(
                {
                    "output": str(temporary_output),
                    "camera_matrix": _camera_pose(center, direction, world_up, distance).tolist(),
                    "frame_center": center.tolist(),
                    "frame_scale": frame_scale,
                    "focal_length_mm": focal_length_mm,
                }
            )
        config_path = temp_root / "job.json"
        config_path.write_text(
            json.dumps(
                {
                    "input_glb": str(input_glb),
                    "background": [value / 255.0 for value in background],
                    "image_size": [width * factor, height * factor],
                    "samples": 64,
                    "materials": materials,
                    "jobs": jobs,
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        command = [
            str(executable),
            "--background",
            "--factory-startup",
            "--disable-autoexec",
            "--python",
            str(worker),
            "--",
            "--config",
            str(config_path),
        ]
        environment = os.environ.copy()
        if "__EGL_VENDOR_LIBRARY_FILENAMES" not in environment and _DEFAULT_EGL_VENDOR.is_file():
            environment["__EGL_VENDOR_LIBRARY_FILENAMES"] = str(_DEFAULT_EGL_VENDOR)
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
                env=environment,
            )
        except subprocess.TimeoutExpired as exc:
            raise RenderBackendUnavailable("Blender rendering timed out after 300 seconds") from exc
        if completed.returncode != 0:
            details = "\n".join((completed.stdout + completed.stderr).splitlines()[-24:])
            raise RenderBackendUnavailable(
                f"Blender rendering failed with exit code {completed.returncode}:\n{details}"
            )
        for output_index, (temporary_output, (_view, output)) in enumerate(
            zip(temporary_outputs, outputs, strict=True)
        ):
            if not temporary_output.is_file() or temporary_output.stat().st_size <= 0:
                raise RenderError(f"Blender did not create a usable image: {temporary_output}")
            try:
                with Image.open(temporary_output) as rendered:
                    foreground = rendered.convert("RGBA")
                    if foreground.size != (width * factor, height * factor):
                        raise RenderError(
                            f"Blender returned {foreground.size}, expected "
                            f"{(width * factor, height * factor)}"
                        )
                    shadow_with, shadow_clean = _shadow_pass_paths(temporary_output)
                    destinations = [(shadow_strength, output)]
                    destinations.extend(
                        (strength, paths[output_index])
                        for strength, paths in extra_outputs.items()
                    )
                    for strength, destination in destinations:
                        image = _composite_cycles_render(
                            foreground,
                            shadow_with_path=shadow_with,
                            shadow_clean_path=shadow_clean,
                            background=background,
                            shadow_strength=strength,
                            transparent=transparent,
                        )
                        if factor > 1:
                            resized = image.resize((width, height), Image.Resampling.LANCZOS)
                            image.close()
                            image = resized
                        image.save(destination)
                        image.close()
            except RenderError:
                raise
            except Exception as exc:
                raise RenderError(f"Cannot read Blender output {temporary_output}: {exc}") from exc
    return "blender"


def analyze_image(
    path: str | Path,
    *,
    background: tuple[int, int, int] = _DEFAULT_BACKGROUND,
) -> RenderQuality:
    """Read a generated image and report lightweight, backend-neutral stats."""

    image_path = Path(path)
    if not image_path.is_file() or image_path.stat().st_size <= 0:
        raise RenderError(f"Rendered image is missing or empty: {image_path}")
    try:
        with Image.open(image_path) as image:
            rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)
    except Exception as exc:
        raise RenderError(f"Rendered image is unreadable: {image_path}: {exc}") from exc
    delta = np.max(np.abs(rgb.astype(np.int16) - np.asarray(background, dtype=np.int16)), axis=2)
    foreground_fraction = float(np.count_nonzero(delta > 8) / delta.size)
    luminance = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]
    if foreground_fraction <= 0.0005:
        raise RenderError(f"Rendered image appears blank: {image_path}")
    foreground_luminance = luminance[delta > 8]
    p05, p95 = (float(value) for value in np.percentile(foreground_luminance, (5.0, 95.0)))
    return RenderQuality(
        width=int(rgb.shape[1]),
        height=int(rgb.shape[0]),
        file_bytes=int(image_path.stat().st_size),
        foreground_fraction=foreground_fraction,
        mean_luminance=float(luminance.mean()),
        contrast_span=p95 - p05,
    )


def _render_meshes(
    meshes: Sequence[VisualMesh],
    output: Path,
    *,
    view: str,
    renderer: RendererName | str,
    front_axis: str,
    frame: SceneFrame,
    image_size: tuple[int, int],
    supersample: int,
    background: tuple[int, int, int],
) -> str:
    direction, world_up = _view_direction(view, front_axis)
    requested = str(renderer).strip().lower()
    if requested != "software":
        raise ValueError("single-view rendering is only used by the software backend")
    _render_software(
        meshes,
        output,
        direction=direction,
        world_up=world_up,
        frame=frame,
        image_size=image_size,
        supersample=supersample,
        background=background,
    )
    return "software"


def _pose_label(pose: str | Mapping[str, float]) -> str:
    return str(pose) if isinstance(pose, str) else "custom"


def render_model(
    model: object,
    output_dir: str | Path,
    views: Sequence[str] | str = ("front", "side"),
    pose: str | Mapping[str, float] = "rest",
    renderer: RendererName | str = "blender",
    front_axis: str = "-y",
    target_patterns: Sequence[str] | str = (),
    *,
    image_size: tuple[int, int] = (800, 640),
    supersample: int = 2,
    frame: SceneFrame | None = None,
    filename_prefix: str | None = None,
    background: tuple[int, int, int] = _DEFAULT_BACKGROUND,
    shadow_strength: float = _SHADOW_STRENGTH,
) -> list[RenderRecord]:
    """Render one model pose from one or more semantic camera views.

    The return value contains image paths, the backend actually used, target
    matches, and basic quality statistics suitable for a JSON manifest.
    ``target_patterns`` are case-insensitive glob/substring matches against
    part, visual, builder and material-class names.  Matched visuals keep their
    authored colors while the rest of the object is gently muted.
    """

    if isinstance(views, str):
        views = (views,)
    views = tuple(str(view) for view in views)
    if not views:
        raise ValueError("views must contain at least one view")
    width, height = (int(value) for value in image_size)
    if width < 16 or height < 16:
        raise ValueError("image_size dimensions must be at least 16 pixels")
    if not math.isfinite(float(shadow_strength)) or not 0.0 <= float(shadow_strength) <= 1.0:
        raise ValueError("shadow_strength must be in [0, 1]")
    output_root = Path(output_dir).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    meshes = extract_visual_meshes(model, pose=pose, target_patterns=target_patterns)
    resolved_frame = frame or frame_visual_meshes((meshes,))
    pose_label = _pose_label(pose)
    prefix = _safe_name(filename_prefix, fallback="render") + "__" if filename_prefix else ""
    target_matches = tuple(sorted({item.key for item in meshes if item.targeted}))
    requested_renderer = str(renderer).strip().lower()
    if requested_renderer not in {"blender", "software"}:
        raise ValueError("renderer must be blender or software")

    outputs = [
        (
            view,
            output_root
            / (
                f"{prefix}{_safe_name(pose_label, fallback='pose')}__"
                f"{_safe_name(view, fallback='view')}.png"
            ),
        )
        for view in views
    ]
    if requested_renderer == "blender":
        actual_backend = _render_blender_batch(
            meshes,
            outputs,
            front_axis=front_axis,
            frame=resolved_frame,
            image_size=(width, height),
            supersample=supersample,
            background=background,
            shadow_strength=shadow_strength,
        )

    records: list[RenderRecord] = []
    for view, output in outputs:
        if requested_renderer == "software":
            actual_backend = _render_meshes(
                meshes,
                output,
                view=view,
                renderer=requested_renderer,
                front_axis=front_axis,
                frame=resolved_frame,
                image_size=(width, height),
                supersample=supersample,
                background=background,
            )
        records.append(
            RenderRecord(
                path=output,
                view=view,
                pose=pose_label,
                renderer=actual_backend,
                quality=analyze_image(output, background=background),
                target_matches=target_matches,
            )
        )
    return records


def render_variant_records(
    model: object,
    output_dir: str | Path,
    *,
    poses: Sequence[str | Mapping[str, float]] = ("rest", "mid", "open"),
    views: Sequence[str] | str = ("front_iso",),
    renderer: RendererName | str = "blender",
    front_axis: str = "-y",
    target_patterns: Sequence[str] | str = (),
    image_size: tuple[int, int] = (800, 640),
    supersample: int = 2,
    filename_prefix: str | None = None,
    background: tuple[int, int, int] = _DEFAULT_BACKGROUND,
    frame: SceneFrame | None = None,
    shadow_strength: float = _SHADOW_STRENGTH,
) -> list[RenderRecord]:
    """Render rest/mid/open views with a shared frame for honest comparison."""

    if isinstance(poses, (str, Mapping)):
        pose_list = (poses,)
    else:
        pose_list = tuple(poses)
    if not pose_list:
        raise ValueError("poses must contain at least one pose")
    mesh_groups = [
        extract_visual_meshes(model, pose=pose, target_patterns=target_patterns)
        for pose in pose_list
    ]
    shared_frame = frame or frame_visual_meshes(mesh_groups)
    records: list[RenderRecord] = []
    for pose in pose_list:
        records.extend(
            render_model(
                model,
                output_dir,
                views=views,
                pose=pose,
                renderer=renderer,
                front_axis=front_axis,
                target_patterns=target_patterns,
                image_size=image_size,
                supersample=supersample,
                frame=shared_frame,
                filename_prefix=filename_prefix,
                background=background,
                shadow_strength=shadow_strength,
            )
        )
    return records


def render_variant(
    model: object,
    output_dir: str | Path,
    views: Sequence[str] | str = ("front_iso",),
    poses: Sequence[str | Mapping[str, float]] = ("closed",),
    front_axis: str = "-y",
    size: tuple[int, int] = (800, 640),
    backend: RendererName | str = "blender",
    highlight_parts: Sequence[str] | str = (),
    *,
    supersample: int = 2,
    filename_prefix: str | None = None,
    background: tuple[int, int, int] = _DEFAULT_BACKGROUND,
    frame: SceneFrame | None = None,
    shadow_strength: float = _SHADOW_STRENGTH,
) -> dict[str, Path]:
    """Pipeline compatibility API returning ``pose__view -> image path``.

    ``highlight_parts`` accepts scoped surface selectors, substrings, or glob
    patterns.  The structured records and quality statistics remain available through
    :func:`render_variant_records` (and :func:`analyze_image` for any returned
    path).
    """

    if isinstance(views, str):
        view_list = (views,)
    else:
        view_list = tuple(views)
    records = render_variant_records(
        model,
        output_dir,
        poses=poses,
        views=view_list,
        renderer=backend,
        front_axis=front_axis,
        target_patterns=highlight_parts,
        image_size=size,
        supersample=supersample,
        filename_prefix=filename_prefix,
        background=background,
        frame=frame,
        shadow_strength=shadow_strength,
    )
    return {
        f"{_safe_name(record.pose, fallback='pose')}__{_safe_name(record.view, fallback='view')}": record.path
        for record in records
    }


def _record_path(item: str | Path | RenderRecord) -> Path:
    return item.path if isinstance(item, RenderRecord) else Path(item)


def _load_font(size: int) -> ImageFont.ImageFont:
    candidates = (
        Path("/usr/share/fonts/google-droid/DroidSans.ttf"),
        Path(__file__).resolve().parents[1] / "agent" / "templates" / "fonts" / "DroidSans.ttf",
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    *,
    preferred_size: int,
    max_width: int,
) -> ImageFont.ImageFont:
    size = max(14, int(preferred_size))
    while size > 14:
        font = _load_font(size)
        bounds = draw.textbbox((0, 0), text, font=font)
        if bounds[2] - bounds[0] <= max_width:
            return font
        size -= 2
    return _load_font(14)


def _foreground_bbox(
    image: Image.Image,
    *,
    background: tuple[int, int, int],
    threshold: int = 3,
    margin: int = 10,
) -> tuple[int, int, int, int]:
    """Return a padded box around rendered geometry and its real shadow."""

    backdrop = Image.new("RGB", image.size, background)
    difference = ImageChops.difference(image.convert("RGB"), backdrop).convert("L")
    mask = difference.point(lambda value: 255 if value > threshold else 0)
    bounds = mask.getbbox()
    if bounds is None:
        return (0, 0, image.width, image.height)
    left, top, right, bottom = bounds
    return (
        max(0, left - margin),
        max(0, top - margin),
        min(image.width, right + margin),
        min(image.height, bottom + margin),
    )


def _compose_compact_foreground_sheet(
    images: Sequence[Image.Image],
    labels: Sequence[str],
    *,
    columns: int,
    reference_cell_size: tuple[int, int],
    title: str | None,
    padding: int,
    background: tuple[int, int, int],
    normalize_foreground: bool,
) -> Image.Image:
    """Pack foreground crops around centered paper labels.

    The default keeps a common pixel scale for honest geometry comparisons.
    ``normalize_foreground`` is for presentation sheets where each crop should
    use the available cell more fully, such as a count axis spanning very
    different chain lengths.
    """

    reference_width, reference_height = reference_cell_size
    source_width = max(image.width for image in images)
    source_height = max(image.height for image in images)
    scale = min(1.0, reference_width / source_width, reference_height / source_height)
    label_font_size = max(18, min(30, reference_width // 16))
    label_font = _load_font(label_font_size)
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1), background))
    prepared: list[Image.Image] = []
    label_bounds: list[tuple[int, int, int, int]] = []
    try:
        for image, label in zip(images, labels, strict=True):
            crop = image.crop(_foreground_bbox(image, background=background))
            crop_scale = scale
            if normalize_foreground:
                crop_scale = min(
                    0.92 * reference_width / max(crop.width, 1),
                    0.92 * reference_height / max(crop.height, 1),
                )
            scaled_size = (
                max(1, round(crop.width * crop_scale)),
                max(1, round(crop.height * crop_scale)),
            )
            prepared.append(crop.resize(scaled_size, Image.Resampling.LANCZOS))
            crop.close()
            label_bounds.append(measure.textbbox((0, 0), str(label), font=label_font))

        row_count = math.ceil(len(prepared) / columns)
        column_widths = [96] * columns
        row_asset_heights = [1] * row_count
        for index, (image, bounds) in enumerate(zip(prepared, label_bounds, strict=True)):
            row, column = divmod(index, columns)
            text_width = bounds[2] - bounds[0]
            column_widths[column] = max(column_widths[column], image.width + 20, text_width + 16)
            row_asset_heights[row] = max(row_asset_heights[row], image.height + 18)

        label_height = label_font_size + 16
        title_font_size = label_font_size + 6
        title_height = title_font_size + 20 if title else 0
        sheet_width = padding + sum(width + padding for width in column_widths)
        sheet_height = title_height + padding + sum(
            height + label_height + padding for height in row_asset_heights
        )
        sheet = Image.new("RGB", (sheet_width, sheet_height), background)
        draw = ImageDraw.Draw(sheet)
        if title:
            draw.text((padding, 9), str(title), fill=(34, 39, 46), font=_load_font(title_font_size))

        column_lefts: list[int] = []
        cursor = padding
        for width in column_widths:
            column_lefts.append(cursor)
            cursor += width + padding
        row_tops: list[int] = []
        cursor = title_height + padding
        for height in row_asset_heights:
            row_tops.append(cursor)
            cursor += height + label_height + padding

        for index, (image, label, bounds) in enumerate(
            zip(prepared, labels, label_bounds, strict=True)
        ):
            row, column = divmod(index, columns)
            left = column_lefts[column]
            top = row_tops[row]
            column_width = column_widths[column]
            asset_height = row_asset_heights[row]
            paste_x = left + (column_width - image.width) // 2
            paste_y = top + asset_height - image.height - 8
            sheet.paste(image, (paste_x, paste_y))
            text_width = bounds[2] - bounds[0]
            draw.text(
                (
                    left + (column_width - text_width) // 2 - bounds[0],
                    top + asset_height + 6 - bounds[1],
                ),
                str(label),
                fill=(44, 49, 57),
                font=label_font,
            )
        return sheet
    finally:
        for image in prepared:
            image.close()


def make_contact_sheet(
    image_paths: Sequence[str | Path | RenderRecord],
    output_path: str | Path,
    *,
    labels: Sequence[str] | None = None,
    columns: int | None = None,
    cell_size: tuple[int, int] | None = None,
    title: str | None = None,
    padding: int = 14,
    background: tuple[int, int, int] = _DEFAULT_BACKGROUND,
    compact_foreground: bool = False,
    normalize_foreground: bool = False,
) -> ContactSheetRecord:
    """Arrange rendered images into a paper-ready labeled contact sheet."""

    paths = tuple(_record_path(item).expanduser().resolve() for item in image_paths)
    if not paths:
        raise ValueError("image_paths must contain at least one image")
    if labels is None:
        labels = tuple(path.stem for path in paths)
    if len(labels) != len(paths):
        raise ValueError("labels must have the same length as image_paths")
    opened: list[Image.Image] = []
    try:
        for path in paths:
            with Image.open(path) as source:
                opened.append(source.convert("RGB").copy())
        if cell_size is None:
            cell_width = max(image.width for image in opened)
            cell_height = max(image.height for image in opened)
        else:
            cell_width, cell_height = (int(value) for value in cell_size)
        if cell_width <= 0 or cell_height <= 0:
            raise ValueError("cell_size dimensions must be positive")
        column_count = int(columns or math.ceil(math.sqrt(len(opened))))
        if column_count <= 0:
            raise ValueError("columns must be positive")
        padding = max(0, int(padding))
        if compact_foreground:
            sheet = _compose_compact_foreground_sheet(
                opened,
                tuple(str(label) for label in labels),
                columns=column_count,
                reference_cell_size=(cell_width, cell_height),
                title=title,
                padding=padding,
                background=background,
                normalize_foreground=normalize_foreground,
            )
        else:
            row_count = math.ceil(len(opened) / column_count)
            label_font_size = max(18, min(36, cell_width // 14))
            label_height = label_font_size + 16
            title_font_size = label_font_size + 6
            title_height = title_font_size + 20 if title else 0
            sheet_width = padding + column_count * (cell_width + padding)
            sheet_height = title_height + padding + row_count * (
                cell_height + label_height + padding
            )
            sheet = Image.new("RGB", (sheet_width, sheet_height), background)
            draw = ImageDraw.Draw(sheet)
            title_font = _load_font(title_font_size)
            if title:
                draw.text((padding, 9), str(title), fill=(34, 39, 46), font=title_font)

            for index, (image, label) in enumerate(zip(opened, labels, strict=True)):
                row, column = divmod(index, column_count)
                left = padding + column * (cell_width + padding)
                top = title_height + padding + row * (cell_height + label_height + padding)
                fitted = image.copy()
                fitted.thumbnail((cell_width, cell_height), Image.Resampling.LANCZOS)
                paste_x = left + (cell_width - fitted.width) // 2
                paste_y = top + (cell_height - fitted.height) // 2
                sheet.paste(fitted, (paste_x, paste_y))
                fitted.close()
                text = str(label)
                label_font = _fit_font(
                    draw,
                    text,
                    preferred_size=label_font_size,
                    max_width=max(cell_width - 16, 24),
                )
                bbox = draw.textbbox((0, 0), text, font=label_font)
                text_width = bbox[2] - bbox[0]
                draw.text(
                    (
                        left + max(0, (cell_width - text_width) // 2) - bbox[0],
                        top + cell_height + 8 - bbox[1],
                    ),
                    text,
                    fill=(44, 49, 57),
                    font=label_font,
                )
        destination = Path(output_path).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        sheet.save(destination)
    finally:
        for image in opened:
            image.close()
    return ContactSheetRecord(
        path=destination,
        image_paths=paths,
        quality=analyze_image(destination, background=background),
    )


def render_contact_sheet(
    image_paths: Sequence[str | Path | RenderRecord],
    output_path: str | Path,
    **kwargs: Any,
) -> ContactSheetRecord:
    """Compatibility alias with an explicit rendering-oriented name."""

    return make_contact_sheet(image_paths, output_path, **kwargs)


def make_comparison_sheets(
    base_label: str,
    base_images: Mapping[str, str | Path | RenderRecord],
    variants: Sequence[tuple[str, Mapping[str, str | Path | RenderRecord]]],
    output_dir: str | Path,
    size: tuple[int, int] = (800, 640),
    *,
    columns: int | None = None,
    padding: int = 14,
    background: tuple[int, int, int] = _DEFAULT_BACKGROUND,
    compact_foreground: bool = False,
    normalize_foreground: bool = False,
) -> dict[str, Path]:
    """Create one aligned base-vs-edit sheet for every pose/view key."""

    if not base_images:
        raise ValueError("base_images must contain at least one pose/view image")
    output_root = Path(output_dir).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    sheets: dict[str, Path] = {}
    for key, base_image in base_images.items():
        images: list[str | Path | RenderRecord] = [base_image]
        labels = [str(base_label)]
        for label, variant_images in variants:
            if key not in variant_images:
                raise RenderError(f"Variant {label!r} has no render matching {key!r}")
            images.append(variant_images[key])
            labels.append(str(label))
        destination = output_root / f"{_safe_name(key, fallback='comparison')}.png"
        sheet = make_contact_sheet(
            images,
            destination,
            labels=labels,
            columns=columns or min(len(images), 4),
            cell_size=size,
            padding=padding,
            background=background,
            compact_foreground=compact_foreground,
            normalize_foreground=normalize_foreground,
        )
        sheets[str(key)] = sheet.path
    return sheets


__all__ = [
    "ContactSheetRecord",
    "RenderBackendUnavailable",
    "RenderError",
    "RenderQuality",
    "RenderRecord",
    "SceneFrame",
    "VisualMesh",
    "analyze_image",
    "compute_world_transforms",
    "extract_visual_meshes",
    "frame_visual_meshes",
    "make_comparison_sheets",
    "make_contact_sheet",
    "merge_frames",
    "pose_values",
    "render_contact_sheet",
    "render_model",
    "render_variant",
    "render_variant_records",
    "shared_frame",
]
