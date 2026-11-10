# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import math
import os
import re
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Sequence, Tuple, Union

from .assets import AssetContext, coerce_asset_context
from .errors import ValidationError

Vec3 = Tuple[float, float, float]
Mat4 = Tuple[Tuple[float, float, float, float], ...]


def _as_vec3(values: Sequence[float], *, name: str) -> Vec3:
    if len(values) != 3:
        raise ValidationError(f"{name} must have 3 elements")
    return (float(values[0]), float(values[1]), float(values[2]))


def _as_mat4(values: Sequence[Sequence[float]], *, name: str) -> Mat4:
    if len(values) != 4:
        raise ValidationError(f"{name} must have 4 rows")
    rows: list[tuple[float, float, float, float]] = []
    for idx, row in enumerate(values):
        if len(row) != 4:
            raise ValidationError(f"{name}[{idx}] must have 4 elements")
        rows.append((float(row[0]), float(row[1]), float(row[2]), float(row[3])))
    return (rows[0], rows[1], rows[2], rows[3])


@dataclass(frozen=True)
class Origin:
    xyz: Vec3 = (0.0, 0.0, 0.0)
    rpy: Vec3 = (0.0, 0.0, 0.0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "xyz", _as_vec3(self.xyz, name="origin.xyz"))
        object.__setattr__(self, "rpy", _as_vec3(self.rpy, name="origin.rpy"))


@dataclass(frozen=True)
class Box:
    size: Vec3


@dataclass(frozen=True, init=False)
class Cylinder:
    radius: float
    length: float

    def __init__(
        self,
        radius: float,
        length: float | None = None,
        *,
        height: float | None = None,
    ) -> None:
        if length is not None and height is not None:
            raise TypeError("Cylinder() accepts only one of 'length' or alias 'height'")
        resolved_length = height if length is None else length
        if resolved_length is None:
            raise TypeError("Cylinder() missing required argument: 'length'")
        object.__setattr__(self, "radius", float(radius))
        object.__setattr__(self, "length", float(resolved_length))

    @property
    def height(self) -> float:
        return self.length


@dataclass(frozen=True)
class Sphere:
    radius: float


PrimitiveGeometry = Union[Box, Cylinder, Sphere]


@dataclass(frozen=True)
class Mesh:
    filename: Union[str, os.PathLike[str], None] = None
    name: Optional[str] = None
    scale: Optional[Vec3] = None
    source_geometry: Optional[PrimitiveGeometry] = None
    source_transform: Optional[Mat4] = None
    # Exact CadQuery source retained for downstream physical-property
    # derivation.  The OBJ remains the portable/renderable representation;
    # these fields are provenance and are deliberately optional for ordinary
    # imported meshes.
    source_brep_path: Optional[str] = field(default=None, compare=False, repr=False)
    source_brep_sha256: Optional[str] = None
    source_brep_unit_scale: float = 1.0
    source_brep_materialized_path: Optional[str] = field(default=None, compare=False, repr=False)
    materialized_path: Optional[str] = field(default=None, compare=False, repr=False)

    def __post_init__(self) -> None:
        filename_value = self.filename
        filename = os.fspath(filename_value) if filename_value is not None else ""
        logical_name = None if self.name is None else str(self.name).strip()
        if not filename and not logical_name:
            raise ValidationError("mesh.filename or mesh.name is required")
        if filename:
            object.__setattr__(self, "filename", filename)
        else:
            object.__setattr__(self, "filename", None)
        if logical_name is not None:
            if not logical_name:
                raise ValidationError("mesh.name must be non-empty when provided")
            object.__setattr__(self, "name", logical_name)
        if self.scale is not None:
            object.__setattr__(self, "scale", _as_vec3(self.scale, name="mesh.scale"))
        if self.source_geometry is not None and not isinstance(
            self.source_geometry, (Box, Cylinder, Sphere)
        ):
            raise ValidationError("mesh.source_geometry must be a Box, Cylinder, Sphere, or None")
        if self.source_transform is not None:
            if self.source_geometry is None:
                raise ValidationError("mesh.source_transform requires mesh.source_geometry")
            object.__setattr__(
                self,
                "source_transform",
                _as_mat4(self.source_transform, name="mesh.source_transform"),
            )
        if self.materialized_path is not None:
            object.__setattr__(self, "materialized_path", os.fspath(self.materialized_path))
        if self.source_brep_path is not None:
            object.__setattr__(self, "source_brep_path", os.fspath(self.source_brep_path))
        if self.source_brep_materialized_path is not None:
            object.__setattr__(
                self,
                "source_brep_materialized_path",
                os.fspath(self.source_brep_materialized_path),
            )
        if self.source_brep_sha256 is not None:
            digest = str(self.source_brep_sha256).strip().lower()
            if re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise ValidationError("mesh.source_brep_sha256 must be a lowercase SHA-256 hex")
            if self.source_brep_path is None:
                raise ValidationError("mesh.source_brep_sha256 requires mesh.source_brep_path")
            object.__setattr__(self, "source_brep_sha256", digest)
        unit_scale = float(self.source_brep_unit_scale)
        if not (unit_scale > 0.0):
            raise ValidationError("mesh.source_brep_unit_scale must be positive")
        object.__setattr__(self, "source_brep_unit_scale", unit_scale)


Geometry = Union[Box, Cylinder, Sphere, Mesh]


def _normalize_material_rgba(
    rgba: Optional[Sequence[float]],
    *,
    field_name: str = "material.rgba",
) -> Optional[Tuple[float, float, float, float]]:
    if rgba is None:
        return None
    normalized = tuple(float(v) for v in rgba)
    if len(normalized) not in (3, 4):
        raise ValidationError(f"{field_name} must have 3 or 4 values")
    if len(normalized) == 3:
        normalized = normalized + (1.0,)
    return normalized


@dataclass(init=False)
class Material:
    name: str
    rgba: Optional[Tuple[float, float, float, float]] = None
    texture: Optional[str] = None

    def __init__(
        self,
        name: str,
        rgba: Optional[Sequence[float]] = None,
        texture: Optional[str] = None,
        *,
        color: Optional[Sequence[float]] = None,
    ) -> None:
        if rgba is not None and color is not None:
            raise ValidationError("Material cannot set both rgba and color")
        self.name = str(name)
        self.rgba = _normalize_material_rgba(rgba if rgba is not None else color)
        self.texture = texture
        self.__post_init__()

    def __post_init__(self) -> None:
        self.name = str(self.name)
        if not self.name:
            raise ValidationError("material.name is required")
        self.rgba = _normalize_material_rgba(self.rgba)


MaterialRef = Union[Material, str]


class AppearanceOnlyKind(str, Enum):
    """Semantic role for a visual that is not a physical material surface."""

    OVERLAY = "overlay"
    EMISSION = "emission"
    TEXT = "text"
    DECAL = "decal"
    SCREEN = "screen"


_APPEARANCE_ALPHA_MODES = frozenset({"auto", "opaque", "mask", "blend"})


def _finite_float(value: object, *, field_name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValidationError(f"{field_name} must be finite")
    return result


def _as_vec2(values: Sequence[float], *, field_name: str) -> Tuple[float, float]:
    if len(values) != 2:
        raise ValidationError(f"{field_name} must have 2 elements")
    return (
        _finite_float(values[0], field_name=f"{field_name}[0]"),
        _finite_float(values[1], field_name=f"{field_name}[1]"),
    )


@dataclass(frozen=True)
class AppearanceOnlySpec:
    """Renderer-facing payload for labels, overlays, emission, text and screens.

    The visual's existing :class:`Material` remains the source of its material
    name, RGBA and optional texture.  This payload adds only semantics that a
    plain URDF material cannot express.
    """

    kind: AppearanceOnlyKind | str
    alpha_mode: str = "auto"
    alpha_cutoff: Optional[float] = None
    emission_color: Optional[Vec3] = None
    emission_strength: Optional[float] = None
    text: Optional[str] = None
    uv_offset: Tuple[float, float] = (0.0, 0.0)
    uv_scale: Tuple[float, float] = (1.0, 1.0)
    uv_rotation_rad: float = 0.0

    def __post_init__(self) -> None:
        try:
            kind = (
                self.kind
                if isinstance(self.kind, AppearanceOnlyKind)
                else AppearanceOnlyKind(str(self.kind))
            )
        except ValueError as exc:
            raise ValidationError(
                "appearance_only.kind must be overlay, emission, text, decal, or screen"
            ) from exc

        alpha_mode = str(self.alpha_mode).strip().lower()
        if alpha_mode not in _APPEARANCE_ALPHA_MODES:
            raise ValidationError("appearance_only.alpha_mode must be auto, opaque, mask, or blend")
        alpha_cutoff = self.alpha_cutoff
        if alpha_cutoff is not None:
            alpha_cutoff = _finite_float(
                alpha_cutoff,
                field_name="appearance_only.alpha_cutoff",
            )
            if not 0.0 <= alpha_cutoff <= 1.0:
                raise ValidationError("appearance_only.alpha_cutoff must be in [0, 1]")
            if alpha_mode != "mask":
                raise ValidationError(
                    "appearance_only.alpha_cutoff is only valid when alpha_mode='mask'"
                )

        emission_color = self.emission_color
        if emission_color is not None:
            emission_color = _as_vec3(
                emission_color,
                name="appearance_only.emission_color",
            )
            if any(not math.isfinite(value) or value < 0.0 for value in emission_color):
                raise ValidationError(
                    "appearance_only.emission_color values must be finite and non-negative"
                )
        emission_strength = self.emission_strength
        if emission_strength is not None:
            emission_strength = _finite_float(
                emission_strength,
                field_name="appearance_only.emission_strength",
            )
            if emission_strength < 0.0:
                raise ValidationError("appearance_only.emission_strength must be non-negative")
        if (emission_color is not None or emission_strength is not None) and kind not in {
            AppearanceOnlyKind.EMISSION,
            AppearanceOnlyKind.SCREEN,
        }:
            raise ValidationError(
                "appearance_only emission fields are only valid for emission or screen"
            )

        text = None if self.text is None else str(self.text)
        if text is not None and not text:
            raise ValidationError("appearance_only.text must be non-empty when provided")
        if kind == AppearanceOnlyKind.TEXT and text is None:
            raise ValidationError("appearance_only kind='text' requires text")
        if text is not None and kind not in {AppearanceOnlyKind.TEXT, AppearanceOnlyKind.SCREEN}:
            raise ValidationError("appearance_only.text is only valid for text or screen")

        uv_offset = _as_vec2(self.uv_offset, field_name="appearance_only.uv_offset")
        uv_scale = _as_vec2(self.uv_scale, field_name="appearance_only.uv_scale")
        if uv_scale[0] == 0.0 or uv_scale[1] == 0.0:
            raise ValidationError("appearance_only.uv_scale components must be non-zero")
        uv_rotation_rad = _finite_float(
            self.uv_rotation_rad,
            field_name="appearance_only.uv_rotation_rad",
        )

        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "alpha_mode", alpha_mode)
        object.__setattr__(self, "alpha_cutoff", alpha_cutoff)
        object.__setattr__(self, "emission_color", emission_color)
        object.__setattr__(self, "emission_strength", emission_strength)
        object.__setattr__(self, "text", text)
        object.__setattr__(self, "uv_offset", uv_offset)
        object.__setattr__(self, "uv_scale", uv_scale)
        object.__setattr__(self, "uv_rotation_rad", uv_rotation_rad)


BLENDERKIT_MATERIAL_CATEGORIES = frozenset(
    {
        "animal-material",
        "asphalt",
        "bricks",
        "ceramic",
        "concrete",
        "dirt",
        "fabric",
        "floor",
        "food-material",
        "fx",
        "glass",
        "grass",
        "ground-material",
        "human",
        "ice",
        "leather",
        "liquid",
        "marble",
        "metal",
        "organic",
        "ornaments",
        "paper",
        "paving",
        "plaster",
        "plastic",
        "rock",
        "roofing",
        "rubber",
        "rust",
        "sand",
        "soil",
        "stone",
        "tech",
        "tiles",
        "wood",
    }
)

_MATERIAL_CLASS_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$")


def _nonempty_text(value: object, *, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{field_name} must be a non-empty string")
    return value.strip()


def _optional_material_class_id(value: object, *, field_name: str) -> Optional[str]:
    if value is None:
        return None
    identifier = _nonempty_text(value, field_name=field_name)
    if _MATERIAL_CLASS_ID_RE.fullmatch(identifier) is None:
        raise ValidationError(
            f"{field_name} must be a lowercase dotted identifier such as 'metal.brushed_steel'"
        )
    parent_category = identifier.split(".", 1)[0]
    if parent_category not in BLENDERKIT_MATERIAL_CATEGORIES:
        raise ValidationError(
            f"{field_name} must start with an official BlenderKit top-level "
            f"material slug (got {parent_category!r})"
        )
    return identifier


def _coerce_visual_material_ref(
    *,
    material: Optional[MaterialRef],
    color: object,
) -> Optional[MaterialRef]:
    if material is not None and color is not None:
        raise TypeError("Part.visual() accepts only one of 'material' or alias 'color'")
    if color is None:
        return material
    if isinstance(color, (Material, str)):
        return color
    if isinstance(color, Sequence) and not isinstance(color, (str, bytes)):
        return Material(name="inline_color", rgba=tuple(float(v) for v in color))
    raise TypeError(
        "Part.visual() alias 'color' must be a material name, Material, or 3/4-value color tuple"
    )


@dataclass
class Visual:
    geometry: Geometry
    origin: Origin = field(default_factory=Origin)
    material: Optional[MaterialRef] = None
    name: Optional[str] = None
    # Auto-captured name of the function that emitted this visual (best-effort,
    # via Part.visual()). Lets QC failure messages point at the code to edit
    # ("built_by=_build_lattice_blade") instead of leaving the author to grep
    # element-name conventions.
    builder: Optional[str] = None
    # Exact PBR pool selector. A visual without it keeps its ordinary material.
    material_class_id: Optional[str] = None
    # Typed rendering-only payload. Mechanical compilation deliberately ignores
    # this metadata; the post-mechanical appearance exporter enforces whether a
    # visual uses this payload or a physical material class.
    appearance_only: Optional[AppearanceOnlySpec] = None

    def __post_init__(self) -> None:
        if self.appearance_only is not None and not isinstance(
            self.appearance_only, AppearanceOnlySpec
        ):
            raise ValidationError("visual.appearance_only must be an AppearanceOnlySpec or None")


@dataclass
class Collision:
    geometry: Geometry
    origin: Origin = field(default_factory=Origin)
    name: Optional[str] = None


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

    @staticmethod
    def from_geometry(
        geometry: Geometry, mass: float, *, origin: Optional[Origin] = None
    ) -> "Inertial":
        mass = float(mass)
        if mass <= 0:
            raise ValidationError("Mass must be positive")

        if isinstance(geometry, Box):
            x, y, z = _as_vec3(geometry.size, name="box.size")
            ixx = (1.0 / 12.0) * mass * (y * y + z * z)
            iyy = (1.0 / 12.0) * mass * (x * x + z * z)
            izz = (1.0 / 12.0) * mass * (x * x + y * y)
        elif isinstance(geometry, Cylinder):
            r = float(geometry.radius)
            length = float(geometry.length)
            ixx = (1.0 / 12.0) * mass * (3 * r * r + length * length)
            iyy = ixx
            izz = 0.5 * mass * r * r
        elif isinstance(geometry, Sphere):
            r = float(geometry.radius)
            ixx = (2.0 / 5.0) * mass * r * r
            iyy = ixx
            izz = ixx
        else:
            raise ValidationError("Cannot derive inertia for mesh geometry")

        inertia = Inertia(ixx=ixx, ixy=0.0, ixz=0.0, iyy=iyy, iyz=0.0, izz=izz)
        return Inertial(mass=mass, inertia=inertia, origin=origin or Origin())


class ArticulationType(str, Enum):
    REVOLUTE = "revolute"
    CONTINUOUS = "continuous"
    PRISMATIC = "prismatic"
    FIXED = "fixed"
    FLOATING = "floating"


def _coerce_articulation_type(
    value: Union["ArticulationType", str],
) -> ArticulationType:
    try:
        return value if isinstance(value, ArticulationType) else ArticulationType(str(value))
    except ValueError as exc:
        raise ValidationError(f"Unknown articulation type: {value}") from exc


@dataclass(frozen=True)
class MotionLimits:
    effort: float = 1.0
    velocity: float = 1.0
    lower: Optional[float] = None
    upper: Optional[float] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "effort", float(self.effort))
        object.__setattr__(self, "velocity", float(self.velocity))
        if self.lower is not None:
            object.__setattr__(self, "lower", float(self.lower))
        if self.upper is not None:
            object.__setattr__(self, "upper", float(self.upper))


@dataclass(frozen=True)
class MotionProperties:
    damping: Optional[float] = None
    friction: Optional[float] = None


@dataclass(frozen=True)
class Mimic:
    joint: str
    multiplier: float = 1.0
    offset: float = 0.0

    def __post_init__(self) -> None:
        joint_name = str(self.joint).strip()
        if not joint_name:
            raise ValidationError("mimic.joint is required")
        object.__setattr__(self, "joint", joint_name)
        object.__setattr__(self, "multiplier", float(self.multiplier))
        object.__setattr__(self, "offset", float(self.offset))


def _capture_builder_name() -> Optional[str]:
    """Best-effort name of the model-code function emitting a visual.

    Walks a few frames up looking for a ``_build*``-named caller (the modular
    template convention); falls back to the nearest non-infrastructure caller.
    Purely diagnostic — never raises.
    """
    try:
        frame = sys._getframe(2)
    except Exception:  # noqa: BLE001 - diagnostics must never break model builds
        return None
    fallback: Optional[str] = None
    depth = 0
    while frame is not None and depth < 16:
        name = frame.f_code.co_name
        if name.startswith("_build") or name.startswith("build_"):
            return name
        if fallback is None and name not in {"visual", "collision", "<module>"}:
            fallback = name
        frame = frame.f_back
        depth += 1
    return fallback


@dataclass
class Part:
    name: str
    visuals: List[Visual] = field(default_factory=list)
    collisions: List[Collision] = field(default_factory=list)
    inertial: Optional[Inertial] = None
    meta: Dict[str, object] = field(default_factory=dict)
    assets: Optional[AssetContext] = None

    def __post_init__(self) -> None:
        self.assets = coerce_asset_context(self.assets)

    def visual(
        self,
        geometry: Geometry,
        *,
        origin: Optional[Origin] = None,
        material: Optional[MaterialRef] = None,
        material_class_id: Optional[str] = None,
        appearance_only: Optional[AppearanceOnlySpec] = None,
        color: object = None,
        name: Optional[str] = None,
    ) -> Visual:
        resolved_material_class_id = _optional_material_class_id(
            material_class_id,
            field_name="visual.material_class_id",
        )
        visual = Visual(
            geometry=geometry,
            origin=origin or Origin(),
            material=_coerce_visual_material_ref(material=material, color=color),
            material_class_id=resolved_material_class_id,
            appearance_only=appearance_only,
            name=name,
            builder=_capture_builder_name(),
        )
        self.visuals.append(visual)
        return visual

    def get_visual(self, name: str) -> Visual:
        key = str(name).strip()
        if not key:
            raise ValidationError("visual name is required")
        for visual in self.visuals:
            if visual.name == key:
                return visual
        raise ValidationError(f"Unknown visual on part {self.name!r}: {name!r}")


_FACE_SIDES = frozenset(
    {
        "positive_x",
        "negative_x",
        "positive_y",
        "negative_y",
        "positive_z",
        "negative_z",
    }
)


@dataclass(frozen=True)
class MatingContract:
    """Declares which surfaces of a joint's parent and child parts should kiss.

    Goes one level finer than `fail_if_articulation_origin_far_from_geometry`:
    not just "joint origin is near both parts' geometry" but "the specific
    mating face on the parent visual and the specific mating face on the child
    visual are within `contact_tol` of each other in world coordinates at the
    closed pose".

    `parent_face_geometry` / `child_face_geometry` are visual names assigned
    via `part.visual(..., name="...")`. `parent_face_side` / `child_face_side`
    pick which axis-aligned face of that visual is the mating surface, one of:
    {positive_x, negative_x, positive_y, negative_y, positive_z, negative_z}.

    Templates should declare a MatingContract on every joint they intend to
    have "tight" contact; the compiler-owned baseline then verifies the
    contract via `fail_if_joint_mating_has_gap`. Joints without a mating
    contract are grandfathered (the check is skipped for that joint).
    """

    parent_face_geometry: str
    parent_face_side: str
    child_face_geometry: str
    child_face_side: str
    contact_tol: float = 0.001
    # Opt-in mount-footprint containment (legacy API name: tangential): besides
    # the faces kissing along the parent face's normal, the child face's extent
    # in the two surface-tangent axes must lie within the parent face's extent
    # (expanded by tangential_tol). Use for stacked/nested mounts (a shelf or
    # oven tray on its real support region) where "touching but hanging half
    # off" is a placement bug the normal-only check cannot see. This is not the
    # rotational-axis contract; AxisInterface/register_interface_mate owns that.
    tangential_containment: bool = False
    tangential_tol: float = 0.005
    # Dry-run variant (set automatically by the modular assembler when both
    # interfaces declare reliable face extents): the same tangential check
    # runs but violations are reported as WARNINGS, never failures — a
    # calibration channel before any hard-fail promotion. Ignored when
    # tangential_containment (the opt-in hard path) is already True.
    tangential_dry_run: bool = False

    def __post_init__(self) -> None:
        pfg = str(self.parent_face_geometry).strip()
        cfg = str(self.child_face_geometry).strip()
        if not pfg:
            raise ValidationError("MatingContract.parent_face_geometry is required")
        if not cfg:
            raise ValidationError("MatingContract.child_face_geometry is required")
        pfs = str(self.parent_face_side).strip().lower()
        cfs = str(self.child_face_side).strip().lower()
        if pfs not in _FACE_SIDES:
            raise ValidationError(
                f"MatingContract.parent_face_side must be one of {sorted(_FACE_SIDES)}, got {pfs!r}"
            )
        if cfs not in _FACE_SIDES:
            raise ValidationError(
                f"MatingContract.child_face_side must be one of {sorted(_FACE_SIDES)}, got {cfs!r}"
            )
        tol = float(self.contact_tol)
        if not (tol >= 0.0):
            raise ValidationError(
                f"MatingContract.contact_tol must be >= 0 (got {self.contact_tol!r})"
            )
        tangential_tol = float(self.tangential_tol)
        if not (tangential_tol >= 0.0):
            raise ValidationError(
                f"MatingContract.tangential_tol must be >= 0 (got {self.tangential_tol!r})"
            )
        object.__setattr__(self, "parent_face_geometry", pfg)
        object.__setattr__(self, "parent_face_side", pfs)
        object.__setattr__(self, "child_face_geometry", cfg)
        object.__setattr__(self, "child_face_side", cfs)
        object.__setattr__(self, "contact_tol", tol)
        object.__setattr__(self, "tangential_containment", bool(self.tangential_containment))
        object.__setattr__(self, "tangential_tol", tangential_tol)


@dataclass(eq=False)
class Articulation:
    name: str
    articulation_type: Union[ArticulationType, str]
    parent: str
    child: str
    origin: Origin = field(default_factory=Origin)
    axis: Vec3 = (0.0, 0.0, 1.0)
    motion_limits: Optional[MotionLimits] = None
    motion_properties: Optional[MotionProperties] = None
    mimic: Optional[Mimic] = None
    mating: Optional[MatingContract] = None
    meta: Dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.articulation_type = _coerce_articulation_type(self.articulation_type)
        self.axis = _as_vec3(self.axis, name="articulation.axis")
        if self.mimic is not None and not isinstance(self.mimic, Mimic):
            if isinstance(self.mimic, str):
                self.mimic = Mimic(joint=self.mimic)
            else:
                joint = getattr(self.mimic, "joint", None)
                if joint is None:
                    raise ValidationError("articulation.mimic must be a Mimic or mimic-like object")
                self.mimic = Mimic(
                    joint=joint,
                    multiplier=getattr(self.mimic, "multiplier", 1.0),
                    offset=getattr(self.mimic, "offset", 0.0),
                )

    @property
    def joint_type(self) -> ArticulationType:
        return self.articulation_type

    @joint_type.setter
    def joint_type(self, value: Union[ArticulationType, str]) -> None:
        self.articulation_type = _coerce_articulation_type(value)

    @property
    def limit(self) -> Optional[MotionLimits]:
        return self.motion_limits

    @limit.setter
    def limit(self, value: Optional[MotionLimits]) -> None:
        self.motion_limits = value

    @property
    def dynamics(self) -> Optional[MotionProperties]:
        return self.motion_properties

    @dynamics.setter
    def dynamics(self, value: Optional[MotionProperties]) -> None:
        self.motion_properties = value
