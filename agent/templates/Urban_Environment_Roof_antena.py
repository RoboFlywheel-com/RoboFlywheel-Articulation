# SPDX-License-Identifier: Apache-2.0

"""Rooftop TV / comm antenna modular template.

Identity: a tall weathered metal **mast** standing on the roof at ``z=0``
(root, static), with an **azimuth** rotation head (collar/hub) at the mast top
(the DEFINING joint: REVOLUTE about +Z), carrying a pitch-adjustable **array**
that elevation-tilts (REVOLUTE about ±Y). The mature default domain is a
rooftop yagi TV antenna: mast + azimuth head + single boom + N director
elements arrayed along the boom + rear reflector grid + flat-base mount.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Urban_Environment_Roof_antena.md`` (1 parent
baseline + 9 single-axis converged 5-star variants).

Structure (pattern = ``mixed``): a linear chain ``mast -> antenna_head ->
array`` stringing two REVOLUTE joints (azimuth +Z defining + elevation Y
secondary), with the array's director/dipole elements loop-emitted as inline
boom visuals (multiplicity axis), and the roof mount folded into the static
root ``mast`` part's visual layer (parallel mount layer, no joint).

Slot axes:
  * ``antenna_type`` (Slot A, 4): yagi_director_array / dish_reflector /
    dipole_whip / panel -- the array head shape (azimuth + elevation REVOLUTE
    preserved in all).
  * ``element_count_N`` (Slot B, multiplicity N in [5,14]): director/dipole
    rods loop-emitted ``element_{i}`` along the boom +X, FIXED riding the boom
    (Rule 1 inline visuals). Conditional: only exposed when
    antenna_type in {yagi, dipole_whip}.
  * ``mast_mount`` (Slot C, 4): flat_base / tripod_feet / chimney_strap /
    wall_bracket -- folded into the static mast part's visuals. chimney_strap
    offsets the mast pole to ``mast_x`` AND shifts the azimuth joint origin to
    ``mast_x`` (gotcha).
  * ``boom_config`` (Slot D, 2): single_boom / X_dual_boom -- conditional, only
    active when antenna_type=yagi; otherwise forced single.

3 HARD RULES honored:
  * Decorations ride as ``parent.visual(...)`` (Rule 1): mount geometry, boom
    elements, reflector grid, dish struts, dipole loop are inline visuals.
  * Every non-FIXED joint (azimuth, elevation) declares a ``MatingContract``
    (Rule 2).
  * Boom elements ride the boom (FIXED inline ``element_{i}``, contacting the
    boom spine -- no floating islands).

Compatibility gating (resolve_config, spec compatibility matrix):
  * X_dual_boom only valid for yagi; non-yagi forces single_boom.
  * element_count_N only exposed for {yagi, dipole_whip}; dish/panel collapse N
    to a fixed grid (N not a multiplicity axis there).
  * chimney_strap offsets mast_x and shifts the azimuth joint origin to match.
  * collar_inner_r derives from mast_radius_scale to avoid pierce/detach.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    LatheGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True

AntennaType = Literal["yagi_director_array", "dish_reflector", "dipole_whip", "panel"]
MastMount = Literal["flat_base", "tripod_feet", "chimney_strap", "wall_bracket"]
BoomConfig = Literal["single_boom", "X_dual_boom"]
PaletteStyle = Literal[
    "aluminium", "galvanized", "black", "weathered", "white_painted", "bronze"
]

ANTENNA_TYPES: tuple[AntennaType, ...] = (
    "yagi_director_array",
    "dish_reflector",
    "dipole_whip",
    "panel",
)
MAST_MOUNTS: tuple[MastMount, ...] = (
    "flat_base",
    "tripod_feet",
    "chimney_strap",
    "wall_bracket",
)
BOOM_CONFIGS: tuple[BoomConfig, ...] = ("single_boom", "X_dual_boom")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "aluminium",
    "galvanized",
    "black",
    "weathered",
    "white_painted",
    "bronze",
)

# Types that expose the element-count multiplicity axis (row-type heads).
ROW_TYPES: tuple[AntennaType, ...] = ("yagi_director_array", "dipole_whip")

N_MIN = 5
N_MAX = 14
# element-count sampling weights: small N high-frequency, large N rare tail.
# Indices map to N = 5..14.
_N_WEIGHTS = (0.16, 0.16, 0.15, 0.13, 0.11, 0.09, 0.07, 0.05, 0.05, 0.03)

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "aluminium": {
        "mast": (0.74, 0.76, 0.78, 1.0),
        "metal": (0.66, 0.68, 0.70, 1.0),
        "dark": (0.20, 0.21, 0.22, 1.0),
        "accent": (0.86, 0.87, 0.88, 1.0),
    },
    "galvanized": {
        "mast": (0.60, 0.62, 0.64, 1.0),
        "metal": (0.52, 0.54, 0.56, 1.0),
        "dark": (0.16, 0.17, 0.18, 1.0),
        "accent": (0.72, 0.74, 0.76, 1.0),
    },
    "black": {
        "mast": (0.07, 0.075, 0.08, 1.0),
        "metal": (0.10, 0.105, 0.11, 1.0),
        "dark": (0.02, 0.02, 0.02, 1.0),
        "accent": (0.30, 0.31, 0.32, 1.0),
    },
    "weathered": {
        "mast": (0.46, 0.43, 0.38, 1.0),
        "metal": (0.40, 0.37, 0.33, 1.0),
        "dark": (0.18, 0.16, 0.13, 1.0),
        "accent": (0.58, 0.50, 0.40, 1.0),
    },
    "white_painted": {
        "mast": (0.88, 0.88, 0.86, 1.0),
        "metal": (0.80, 0.80, 0.78, 1.0),
        "dark": (0.24, 0.24, 0.24, 1.0),
        "accent": (0.94, 0.94, 0.92, 1.0),
    },
    "bronze": {
        "mast": (0.52, 0.38, 0.22, 1.0),
        "metal": (0.60, 0.45, 0.26, 1.0),
        "dark": (0.22, 0.16, 0.10, 1.0),
        "accent": (0.74, 0.56, 0.32, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). The parent baseline drives the mast +
# head + articulation skeleton; per-type heads adapt the source array.
# ---------------------------------------------------------------------------
_MAST_LEN = 3.40  # nominal mast length (scaled by mast_height_scale)
_MAST_R = 0.016  # nominal mast radius (scaled by mast_radius_scale)
_HEAD_GAP = 0.05  # collar sits this far below the mast top
_COLLAR_LEN = 0.060
_ELEV_POST_Z = 0.12  # elevation pivot height above the collar top
_BOOM_LEN = 1.55  # nominal yagi boom length
_BOOM_SIDE = 0.018  # square boom spine half-extent-ish
_AZIMUTH_RANGE = math.pi
_ELEV_RANGE = 0.35


@dataclass(frozen=True)
class RoofAntennaConfig:
    antenna_type: AntennaType | None = None
    mast_mount: MastMount | None = None
    boom_config: BoomConfig | None = None
    element_count_N: int | None = None
    palette_style: PaletteStyle = "aluminium"
    mast_height_scale: float = 1.0
    mast_radius_scale: float = 1.0
    boom_len_scale: float = 1.0
    dish_radius_scale: float = 1.0
    boom_splay_deg: float = 14.0
    name: str = "roof_antenna"


@dataclass(frozen=True)
class ResolvedRoofAntennaConfig:
    antenna_type: AntennaType
    mast_mount: MastMount
    boom_config: BoomConfig
    element_count_N: int
    palette_style: PaletteStyle
    # Concrete geometry (scaled / derived).
    mast_len: float
    mast_r: float
    mast_x: float  # mast pole X offset (nonzero only for chimney_strap)
    head_z: float  # azimuth joint Z (= mast_len - gap)
    collar_inner_r: float
    collar_len: float
    elev_post_z: float
    boom_len: float
    boom_side: float
    dish_radius: float
    boom_splay: float  # radians
    name: str

    @property
    def exposes_elements(self) -> bool:
        return self.antenna_type in ROW_TYPES


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> RoofAntennaConfig:
    rng = random.Random(seed)
    antenna_type: AntennaType = rng.choice(ANTENNA_TYPES)
    # boom_config only meaningful for yagi.
    if antenna_type == "yagi_director_array":
        boom_config: BoomConfig = rng.choices(
            ("single_boom", "X_dual_boom"), weights=(0.62, 0.38), k=1
        )[0]
    else:
        boom_config = "single_boom"
    # element_count only for row-type heads; sample weighted toward small N.
    if antenna_type in ROW_TYPES:
        n = rng.choices(range(N_MIN, N_MAX + 1), weights=_N_WEIGHTS, k=1)[0]
    else:
        n = 9  # placeholder; not exposed / not used for dish/panel.
    return RoofAntennaConfig(
        antenna_type=antenna_type,
        mast_mount=rng.choice(MAST_MOUNTS),
        boom_config=boom_config,
        element_count_N=n,
        palette_style=rng.choice(PALETTE_STYLES),
        mast_height_scale=round(rng.uniform(0.90, 1.20), 4),
        mast_radius_scale=round(rng.uniform(0.85, 1.30), 4),
        boom_len_scale=round(rng.uniform(0.85, 1.25), 4),
        dish_radius_scale=round(rng.uniform(0.85, 1.20), 4),
        boom_splay_deg=round(rng.uniform(10.0, 18.0), 3),
        name=f"seeded_roof_antenna_{seed}",
    )


def resolve_config(config: RoofAntennaConfig | None = None) -> ResolvedRoofAntennaConfig:
    cfg = config or RoofAntennaConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    antenna_type = _pick(cfg.antenna_type, ANTENNA_TYPES)
    mast_mount = _pick(cfg.mast_mount, MAST_MOUNTS)
    boom_config = _pick(cfg.boom_config, BOOM_CONFIGS)

    # --- Compatibility gating. ---
    # (1) X_dual only for yagi.
    if antenna_type != "yagi_director_array":
        boom_config = "single_boom"
    # (2) element_count only for row-type heads; else collapse to fixed grid N.
    n = int(cfg.element_count_N) if cfg.element_count_N is not None else 9
    if antenna_type in ROW_TYPES:
        n = int(_clamp(n, N_MIN, N_MAX))
    else:
        n = 9  # not exposed; dish/panel use type-fixed grid geometry.

    # --- Scales (clamp). ---
    h_scale = _clamp(cfg.mast_height_scale, 0.90, 1.20)
    r_scale = _clamp(cfg.mast_radius_scale, 0.85, 1.30)
    boom_scale = _clamp(cfg.boom_len_scale, 0.85, 1.25)
    dish_scale = _clamp(cfg.dish_radius_scale, 0.85, 1.20)
    splay_deg = _clamp(cfg.boom_splay_deg, 10.0, 18.0)

    mast_len = _MAST_LEN * h_scale
    # head_z = mast top; the azimuth joint sits at the mast top and the collar
    # seats on it. Ensure head world z > 3.0 (rooftop identity).
    if mast_len <= 3.04:
        mast_len = 3.04
    head_z = mast_len

    mast_r = _MAST_R * r_scale
    # collar_inner_r derives from mast_radius_scale: snug around the mast pole
    # (ε in [0.010, 0.016]) so it neither pierces (too small) nor detaches.
    eps = _clamp(0.013 * r_scale, 0.010, 0.016)
    collar_inner_r = mast_r + eps

    # chimney_strap offsets the mast pole to mast_x; azimuth origin follows.
    mast_x = 0.0
    if mast_mount == "chimney_strap":
        mast_x = 0.14 + mast_r  # mast pole hugs the +X chimney face

    boom_len = _BOOM_LEN * boom_scale
    dish_radius = 0.26 * dish_scale

    return ResolvedRoofAntennaConfig(
        antenna_type=antenna_type,
        mast_mount=mast_mount,
        boom_config=boom_config,
        element_count_N=n,
        palette_style=palette_style,
        mast_len=mast_len,
        mast_r=mast_r,
        mast_x=mast_x,
        head_z=head_z,
        collar_inner_r=collar_inner_r,
        collar_len=_COLLAR_LEN,
        elev_post_z=_ELEV_POST_Z,
        boom_len=boom_len,
        boom_side=_BOOM_SIDE,
        dish_radius=dish_radius,
        boom_splay=math.radians(splay_deg),
        name=cfg.name or "roof_antenna",
    )


def with_overrides(config: RoofAntennaConfig, **kwargs: object) -> RoofAntennaConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: RoofAntennaConfig | ResolvedRoofAntennaConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedRoofAntennaConfig) else resolve_config(config)
    choices: list[tuple[str, str]] = [
        ("antenna_type", r.antenna_type),
        ("mast_mount", r.mast_mount),
        ("boom_config", r.boom_config),
    ]
    if r.exposes_elements:
        choices.append(("element_count_N", f"n{r.element_count_N}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared helpers.
# ---------------------------------------------------------------------------
def _rpy_from_z_axis(direction: tuple[float, float, float]) -> tuple[float, float, float]:
    """rpy that points a +Z cylinder along `direction` (matches the SDK helper)."""
    dx, dy, dz = direction
    n = math.sqrt(dx * dx + dy * dy + dz * dz)
    if n < 1e-12:
        return (0.0, 0.0, 0.0)
    dx, dy, dz = dx / n, dy / n, dz / n
    return (0.0, math.atan2(math.sqrt(dx * dx + dy * dy), dz), math.atan2(dy, dx))


def _rod(part, *, length: float, radius: float, origin: Origin, material, name: str) -> None:
    """A thin cylindrical rod (default along +Z; rotate via origin.rpy)."""
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=origin,
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _parabolic_dish_shell(radius: float, depth: float):
    """LatheGeometry parabolic dish shell (concave +X-facing bowl).

    Profile in (r, z_local) about the dish's local axis (axis = +Z of the
    lathe, later rotated to face +X). Source: dish var _parabolic_dish_shell.
    """
    pts: list[tuple[float, float]] = []
    steps = 10
    for i in range(steps + 1):
        rr = radius * i / steps
        z = depth * (rr / radius) ** 2 if radius > 0 else 0.0
        pts.append((rr, z))
    # return along the front rim with a small shell thickness offset.
    th = 0.010
    for i in range(steps, -1, -1):
        rr = radius * i / steps
        z = depth * (rr / radius) ** 2 if radius > 0 else 0.0
        pts.append((max(0.0, rr - th), z + th))
    return LatheGeometry(pts, segments=48, closed=True)


# ===========================================================================
# Mast (root, static) + Slot C mount geometry folded in as visuals (Rule 1).
# ===========================================================================
def _build_mast(model: ArticulatedObject, r: ResolvedRoofAntennaConfig, mats):
    mast = model.part("mast")
    mx = r.mast_x
    # Mast pole (root spine), standing at z=0.
    mast.visual(
        Cylinder(radius=r.mast_r, length=r.mast_len),
        origin=Origin(xyz=(mx, 0.0, r.mast_len / 2.0)),
        material=mats["mast"],
        name="mast_pole", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
    )
    # A couple of weld collars on the pole (decorative, real visuals).
    for i, frac in enumerate((0.30, 0.66)):
        mast.visual(
            Cylinder(radius=r.mast_r + 0.006, length=0.030),
            origin=Origin(xyz=(mx, 0.0, r.mast_len * frac)),
            material=mats["dark"],
            name=f"mast_collar_{i}", material_class_id="metal.blackened_gunmetal",
        )
    mast.inertial = Inertial.from_geometry(
        Cylinder(radius=r.mast_r, length=r.mast_len),
        mass=3.0,
        origin=Origin(xyz=(mx, 0.0, r.mast_len / 2.0)),
    )

    if r.mast_mount == "flat_base":
        _emit_flat_base(mast, r, mats)
    elif r.mast_mount == "tripod_feet":
        _emit_tripod(mast, r, mats)
    elif r.mast_mount == "chimney_strap":
        _emit_chimney_strap(mast, r, mats)
    else:  # wall_bracket
        _emit_wall_bracket(mast, r, mats)
    return mast


def _emit_flat_base(mast, r: ResolvedRoofAntennaConfig, mats):
    mast.visual(
        Cylinder(radius=0.085, length=0.014),
        origin=Origin(xyz=(0.0, 0.0, 0.007)),
        material=mats["metal"],
        name="foot_plate", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
    )
    for i, ang in enumerate((0.5, math.pi - 0.5)):
        x = 0.075 * math.cos(ang)
        y = 0.075 * math.sin(ang)
        mast.visual(
            Box((0.026, 0.018, 0.040)),
            origin=Origin(xyz=(x, y, 0.020)),
            material=mats["dark"],
            name=f"standoff_bracket_{i}", material_class_id="metal.blackened_gunmetal",
        )
        mast.visual(
            Box((0.030, 0.030, 0.006)),
            origin=Origin(xyz=(x, y, 0.003)),
            material=mats["dark"],
            name=f"standoff_pad_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _emit_tripod(mast, r: ResolvedRoofAntennaConfig, mats):
    mast.visual(
        Cylinder(radius=r.mast_r + 0.014, length=0.050),
        origin=Origin(xyz=(0.0, 0.0, 0.060)),
        material=mats["metal"],
        name="tripod_hub", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
    )
    hub_z = 0.060
    foot_r = 0.22  # foot pad radial distance
    # Leg runs from near the hub axis (top) out+down to the foot pad on z=0.
    leg_len = math.hypot(foot_r, hub_z)
    for i in range(3):
        ang = i * 2.0 * math.pi / 3.0
        fx, fy = foot_r * math.cos(ang), foot_r * math.sin(ang)
        # leg from hub-axis-top (0,0,hub_z) down+out to the foot (fx,fy,0).
        dvec = (fx, fy, -hub_z)
        mx, my, mz = 0.5 * fx, 0.5 * fy, 0.5 * hub_z
        _rod(
            mast,
            length=leg_len,
            radius=0.012,
            origin=Origin(
                xyz=(mx, my, mz),
                rpy=_rpy_from_z_axis(dvec),
            ),
            material=mats["metal"],
            name=f"leg_{i}",
        )
        mast.visual(
            Cylinder(radius=0.026, length=0.012),
            origin=Origin(xyz=(foot_r * math.cos(ang), foot_r * math.sin(ang), 0.006)),
            material=mats["dark"],
            name=f"foot_pad_{i}", material_class_id="metal.blackened_gunmetal",
        )


def _emit_chimney_strap(mast, r: ResolvedRoofAntennaConfig, mats):
    # Brick chimney stub at the origin; mast pole is offset to its +X face.
    chimney_h = 0.50
    mast.visual(
        Box((0.24, 0.24, chimney_h)),
        origin=Origin(xyz=(0.0, 0.0, chimney_h / 2.0)),
        material=mats["dark"],
        name="chimney_block", material_class_id="ceramic.terracotta_earthenware",
    )
    mast.visual(
        Box((0.28, 0.28, 0.030)),
        origin=Origin(xyz=(0.0, 0.0, chimney_h + 0.015)),
        material=mats["metal"],
        name="chimney_cap", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
    )
    # 3 hose straps wrapping the chimney + mast (span from chimney face to mast).
    for i, sz in enumerate((0.12, 0.26, 0.40)):
        mast.visual(
            Box((0.30, 0.040, 0.012)),
            origin=Origin(xyz=(0.07, 0.0, sz)),
            material=mats["metal"],
            name=f"strap_{i}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
        )


def _emit_wall_bracket(mast, r: ResolvedRoofAntennaConfig, mats):
    # Standing wall plate behind the mast (x ~ -0.20).
    mast.visual(
        Box((0.018, 0.18, 0.30)),
        origin=Origin(xyz=(-0.20, 0.0, 0.18)),
        material=mats["metal"],
        name="wall_plate", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
    )
    for i in range(4):
        dy = 0.07 if i % 2 else -0.07
        dz = 0.05 if i < 2 else 0.28
        mast.visual(
            Cylinder(radius=0.007, length=0.010),
            origin=Origin(xyz=(-0.192, dy, dz), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["dark"],
            name=f"wall_bolt_{i}", material_class_id="metal.blackened_gunmetal",
        )
    # 2 standoff arms reaching from the plate to the mast.
    for i, dz in enumerate((0.08, 0.26)):
        mast.visual(
            Box((0.20, 0.030, 0.030)),
            origin=Origin(xyz=(-0.10, 0.0, dz)),
            material=mats["metal"],
            name=f"arm_{i}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
        )
        mast.visual(
            Cylinder(radius=r.mast_r + 0.012, length=0.040),
            origin=Origin(xyz=(0.0, 0.0, dz)),
            material=mats["dark"],
            name=f"arm_clamp_{i}", material_class_id="metal.blackened_gunmetal",
        )


# ===========================================================================
# Antenna head (azimuth collar). Child of mast via azimuth REVOLUTE (+Z).
# ===========================================================================
def _build_antenna_head(model: ArticulatedObject, mast, r: ResolvedRoofAntennaConfig, mats):
    head = model.part("antenna_head")
    # Head authored in its own frame: the azimuth joint origin (= mast top) is at
    # local (0,0,0). The collar seats on the mast top -> its bottom face is at
    # z=0 (center at +collar_len/2) so the collar negative_z mates the mast top.
    collar_cz = r.collar_len / 2.0
    head.visual(
        Cylinder(radius=r.collar_inner_r + 0.012, length=r.collar_len),
        origin=Origin(xyz=(0.0, 0.0, collar_cz)),
        material=mats["metal"],
        name="azimuth_collar", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
    )
    # Clamp blocks extend DOWN past z=0 to grip the mast pole (intentional
    # overlap with mast_pole) -> no floating + a real anchoring fit.
    clamp_len = r.collar_len + 0.060
    for i, ang in enumerate((0.0, math.pi)):
        head.visual(
            Box((0.024, 0.018, clamp_len)),
            origin=Origin(
                xyz=((r.collar_inner_r + 0.004) * math.cos(ang),
                     (r.collar_inner_r + 0.004) * math.sin(ang),
                     collar_cz - 0.030)
            ),
            material=mats["dark"],
            name=f"clamp_block_{i}", material_class_id="metal.blackened_gunmetal",
        )
    # Elevation post boss on top of the collar (top face anchors the array).
    post_len = r.elev_post_z + 0.010
    post_top = r.collar_len + post_len  # local-z of the elevation_post top face
    head.visual(
        Cylinder(radius=0.020, length=post_len),
        origin=Origin(xyz=(0.0, 0.0, r.collar_len + post_len / 2.0)),
        material=mats["metal"],
        name="elevation_post", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
    )
    head.inertial = Inertial.from_geometry(
        Cylinder(radius=r.collar_inner_r + 0.012, length=r.collar_len),
        mass=0.25,
        origin=Origin(xyz=(0.0, 0.0, collar_cz)),
    )
    # Azimuth REVOLUTE about +Z (DEFINING). Origin at mast top (mast_x, 0, head_z).
    model.articulation(
        "azimuth_joint",
        ArticulationType.REVOLUTE,
        parent=mast,
        child=head,
        origin=Origin(xyz=(r.mast_x, 0.0, r.head_z)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=12.0, velocity=1.0, lower=-_AZIMUTH_RANGE, upper=_AZIMUTH_RANGE
        ),
        mating=MatingContract(
            parent_face_geometry="mast_pole",
            parent_face_side="positive_z",
            child_face_geometry="azimuth_collar",
            child_face_side="negative_z",
            contact_tol=0.006,
        ),
    )
    return head, post_top


# ===========================================================================
# Array heads (Slot A). Child of head via elevation REVOLUTE (±Y).
# ===========================================================================
def _attach_elevation(model, head, array, r, post_top, *, pivot_geom):
    """Elevation REVOLUTE about -Y, origin on the elevation_post top."""
    model.articulation(
        "elevation_joint",
        ArticulationType.REVOLUTE,
        parent=head,
        child=array,
        origin=Origin(xyz=(0.0, 0.0, post_top)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=8.0, velocity=1.0, lower=-_ELEV_RANGE, upper=_ELEV_RANGE
        ),
        mating=MatingContract(
            parent_face_geometry="elevation_post",
            parent_face_side="positive_z",
            child_face_geometry=pivot_geom,
            child_face_side="negative_z",
            contact_tol=0.050,
        ),
    )


def _emit_boom_elements(part, r: ResolvedRoofAntennaConfig, mats, *, prefix: str,
                        x0_off: float = 0.0, y0_off: float = 0.0):
    """Loop-emit N director rods along the boom +X, front-tapered, riding the
    boom spine (FIXED inline visuals, Rule 1 / no floating islands).

    Returns list of element visual names emitted.
    """
    n = r.element_count_N
    boom_len = r.boom_len
    start = -boom_len * 0.42
    end = boom_len * 0.42
    max_len = 0.34  # rear (driven) element half-span * 2
    min_len = 0.16  # front director
    names: list[str] = []
    for i in range(n):
        frac = i / (n - 1) if n > 1 else 0.0
        x = start + frac * (end - start)
        elen = max_len - frac * (max_len - min_len)
        name = f"{prefix}{i}"
        # Element rod crosses ±Y (rotate the +Z cylinder about +X by 90deg).
        _rod(
            part,
            length=elen,
            radius=0.005,
            origin=Origin(xyz=(x0_off + x, y0_off, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"],
            name=name,
        )
        names.append(name)
    return names


def _emit_reflector_grid(part, r: ResolvedRoofAntennaConfig, mats, *, x_pos: float, y0_off: float = 0.0):
    """Rear reflector grid: 17 horizontal rods between 2 vertical stiles, plus a
    bridging strut joining the grid to the boom (no floating island)."""
    refl_half_w = 0.40
    refl_half_h = 0.34
    # 2 vertical stiles.
    for i, sx in enumerate((-1.0, 1.0)):
        _rod(
            part,
            length=2.0 * refl_half_h,
            radius=0.005,
            origin=Origin(xyz=(x_pos, y0_off + sx * refl_half_w, 0.0),
                          rpy=(0.0, 0.0, 0.0)),
            material=mats["metal"],
            name=f"reflector_stile_{i}",
        )
    # 17 horizontal rods.
    for g in range(17):
        zz = -refl_half_h + 2.0 * refl_half_h * g / 16.0
        _rod(
            part,
            length=2.0 * refl_half_w,
            radius=0.004,
            origin=Origin(xyz=(x_pos, y0_off, zz), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["metal"],
            name=f"reflector_grid_{g:02d}",
        )
    # Bridging strut from the boom to the grid center (anchors the grid).
    _rod(
        part,
        length=abs(x_pos) + 0.04,
        radius=0.008,
        origin=Origin(xyz=(x_pos / 2.0, y0_off, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["dark"],
        name=f"reflector_strut_{'c' if y0_off == 0 else int(y0_off * 1000)}",
    )


def _emit_yagi(model, head, r: ResolvedRoofAntennaConfig, mats, post_top):
    array = model.part("yagi_boom")
    boom_len = r.boom_len
    rear_x = -boom_len * 0.46

    if r.boom_config == "single_boom":
        # Central boom spine along +X. Pivot boss = boom_spine (-Z face mates).
        array.visual(
            Box((boom_len, 2.0 * r.boom_side, 2.0 * r.boom_side)),
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["metal"],
            name="boom_spine", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
        )
        # Balun box rear + junction box front.
        array.visual(
            Box((0.05, 0.05, 0.05)),
            origin=Origin(xyz=(rear_x + 0.05, 0.0, 0.0)),
            material=mats["dark"],
            name="balun_box_rear", material_class_id="metal.blackened_gunmetal",
        )
        array.visual(
            Box((0.04, 0.04, 0.04)),
            origin=Origin(xyz=(boom_len * 0.42, 0.0, 0.0)),
            material=mats["dark"],
            name="junction_box_front", material_class_id="metal.blackened_gunmetal",
        )
        _emit_boom_elements(array, r, mats, prefix="element_")
        _emit_reflector_grid(array, r, mats, x_pos=rear_x)
        pivot_geom = "boom_spine"
    else:
        # X_dual: central hub + 2 splay booms, each with its own element row.
        array.visual(
            Cylinder(radius=0.030, length=2.0 * r.boom_side),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["metal"],
            name="hub", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
        )
        for b, sign in ((0, 1.0), (1, -1.0)):
            ang = sign * r.boom_splay
            # boom spine rotated by splay about +Z.
            array.visual(
                Box((boom_len, 2.0 * r.boom_side, 2.0 * r.boom_side)),
                origin=Origin(
                    xyz=(boom_len * 0.5 * math.cos(ang), boom_len * 0.5 * math.sin(ang), 0.0),
                    rpy=(0.0, 0.0, ang),
                ),
                material=mats["metal"],
                name=f"boom_spine_{b}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
            )
            # Elements along each boom: place along the rotated axis.
            n = r.element_count_N
            start_f = 0.06
            end_f = 0.92
            max_len = 0.32
            min_len = 0.16
            for i in range(n):
                frac = i / (n - 1) if n > 1 else 0.0
                t = (start_f + frac * (end_f - start_f)) * boom_len
                ex = t * math.cos(ang)
                ey = t * math.sin(ang)
                elen = max_len - frac * (max_len - min_len)
                _rod(
                    array,
                    length=elen,
                    radius=0.005,
                    origin=Origin(xyz=(ex, ey, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material=mats["accent"],
                    name=f"element_{b}_{i}",
                )
            array.visual(
                Box((0.05, 0.05, 0.05)),
                origin=Origin(xyz=(0.06 * math.cos(ang), 0.06 * math.sin(ang), 0.0)),
                material=mats["dark"],
                name=f"balun_box_{b}", material_class_id="metal.blackened_gunmetal",
            )
        # Shared centered reflector grid behind the hub.
        _emit_reflector_grid(array, r, mats, x_pos=rear_x)
        # Center strut tying hub to reflector already added; add per-boom struts.
        for b in (0, 1):
            _rod(
                array,
                length=0.10,
                radius=0.006,
                origin=Origin(xyz=(rear_x * 0.5, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
                material=mats["dark"],
                name=f"reflector_center_strut_{b}",
            )
        pivot_geom = "hub"

    array.inertial = Inertial.from_geometry(
        Box((boom_len, 0.7, 0.7)),
        mass=0.5,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    _attach_elevation(model, head, array, r, post_top, pivot_geom=pivot_geom)
    return array


def _emit_dish(model, head, r: ResolvedRoofAntennaConfig, mats, post_top):
    array = model.part("dish_assembly")
    rad = r.dish_radius
    depth = rad * 0.34
    vertex_x = 0.10  # dish vertex (bowl bottom) X
    rim_x = vertex_x + depth
    # stub_arm (pivot_geom): bridges from below the elevation post up through the
    # dish vertex so the whole assembly is one connected body.
    array.visual(
        Box((vertex_x + 0.05, 0.05, 0.05)),
        origin=Origin(xyz=((vertex_x - 0.025) / 1.0, 0.0, 0.0)),
        material=mats["dark"],
        name="stub_arm", material_class_id="metal.blackened_gunmetal",
    )
    array.visual(
        Box((0.05, 0.07, 0.06)),
        origin=Origin(xyz=(0.03, 0.0, 0.0)),
        material=mats["dark"],
        name="pivot_bracket", material_class_id="metal.blackened_gunmetal",
    )
    # Parabolic dish shell, faces +X. Lathe axis +Z -> rotate +90deg about +Y so
    # the bowl opens toward +X with its vertex at vertex_x.
    array.visual(
        mesh_from_geometry(_parabolic_dish_shell(rad, depth), "dish_reflector"),
        origin=Origin(xyz=(vertex_x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["accent"],
        name="dish_reflector", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
    )
    # Rim torus at the dish mouth (x = rim_x).
    array.visual(
        mesh_from_geometry(
            TorusGeometry(rad, 0.010, radial_segments=16, tubular_segments=40), "dish_rim"
        ),
        origin=Origin(xyz=(rim_x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["metal"],
        name="dish_rim", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
    )
    # Feed horn at the focus + 3 support struts from the rim to the horn.
    focus_x = rim_x + 0.05
    horn_len = 0.09
    array.visual(
        Cylinder(radius=0.022, length=horn_len),
        origin=Origin(xyz=(focus_x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["dark"],
        name="feed_horn", material_class_id="metal.blackened_gunmetal",
    )
    # struts converge to a point well inside the horn body so they overlap it.
    horn_back = focus_x
    for i in range(3):
        ang = i * 2.0 * math.pi / 3.0
        ry = rad * math.cos(ang)
        rz = rad * math.sin(ang)
        # strut from rim point (rim_x, ry, rz) to horn center (horn_back, 0, 0).
        dvec = (horn_back - rim_x, -ry, -rz)
        strut_len = math.sqrt(sum(c * c for c in dvec))
        _rod(
            array,
            length=strut_len,
            radius=0.005,
            origin=Origin(
                xyz=((rim_x + horn_back) / 2.0, ry / 2.0, rz / 2.0),
                rpy=_rpy_from_z_axis(dvec),
            ),
            material=mats["metal"],
            name=f"support_strut_{i}",
        )
    array.visual(
        Box((0.05, 0.05, 0.05)),
        origin=Origin(xyz=(0.0, 0.0, -0.045)),
        material=mats["dark"],
        name="junction_box", material_class_id="metal.blackened_gunmetal",
    )
    array.inertial = Inertial.from_geometry(
        Box((2.0 * rad, 2.0 * rad, 2.0 * rad)),
        mass=0.6,
        origin=Origin(xyz=(vertex_x, 0.0, 0.0)),
    )
    _attach_elevation(model, head, array, r, post_top, pivot_geom="stub_arm")
    return array


def _emit_dipole(model, head, r: ResolvedRoofAntennaConfig, mats, post_top):
    array = model.part("dipole_assembly")
    # center_hub (pivot_geom) + crossbar + vertical whip + balun.
    array.visual(
        Box((0.05, 0.05, 0.05)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["dark"],
        name="center_hub", material_class_id="metal.blackened_gunmetal",
    )
    # Horizontal dipole crossbar + N elements along it (row type).
    array.visual(
        Box((r.boom_len, 2.0 * r.boom_side, 2.0 * r.boom_side)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["metal"],
        name="dipole_crossbar", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
    )
    _emit_boom_elements(array, r, mats, prefix="element_")
    # Vertical whip rising from the hub.
    _rod(
        array,
        length=0.60,
        radius=0.004,
        origin=Origin(xyz=(0.0, 0.0, 0.30)),
        material=mats["accent"],
        name="vertical_whip",
    )
    array.visual(
        Box((0.04, 0.04, 0.04)),
        origin=Origin(xyz=(-r.boom_len * 0.4, 0.0, 0.0)),
        material=mats["dark"],
        name="balun_box", material_class_id="metal.blackened_gunmetal",
    )
    # 8-segment loop ring (octagon in the y-z plane at x=cx) + 4 spokes
    # (type-fixed grid, NOT a multiplicity axis). The ring rods are proper chords
    # between octagon vertices on radius loop_r; the spokes run radially from the
    # crossbar/center axis OUT THROUGH the ring vertices so the whole ring fuses
    # into one connected solid (no floating loop island). tol 1e-6 needs real
    # mesh overlap, so spokes pierce the ring radius rather than tip-touch it.
    loop_r = 0.12
    cx = r.boom_len * 0.46
    for i in range(8):
        a0 = i * 2.0 * math.pi / 8.0
        a1 = (i + 1) * 2.0 * math.pi / 8.0
        # Octagon vertices on radius loop_r; rod is the chord between them.
        y0, z0 = loop_r * math.cos(a0), loop_r * math.sin(a0)
        y1, z1 = loop_r * math.cos(a1), loop_r * math.sin(a1)
        my, mz = 0.5 * (y0 + y1), 0.5 * (z0 + z1)  # chord midpoint
        dy, dz = y1 - y0, z1 - z0  # chord direction (y-z plane)
        seg_len = math.hypot(dy, dz)
        # +Z cylinder -> axis (0,-sin rx, cos rx); want axis along (dy,dz).
        rx = math.atan2(-dy, dz)
        _rod(
            array,
            length=seg_len * 1.06,  # slight overlap so adjacent chords fuse
            radius=0.004,
            origin=Origin(xyz=(cx, my, mz), rpy=(rx, 0.0, 0.0)),
            material=mats["accent"],
            name=f"loop_rod_{i}",
        )
    # Radial spokes: span from past the axis (overlapping the crossbar) out PAST
    # the ring radius (piercing the loop_rod vertices) so ring<->spokes<->crossbar
    # all fuse. Spoke angles 0/90/180/270 land on octagon vertices shared by two
    # adjacent loop_rods, so all 8 ring rods attach.
    sp_inner = -0.012  # crosses the axis -> overlaps crossbar + opposite spoke
    sp_outer = loop_r + 0.014  # pierces the ring rod endpoints at the vertices
    sp_len = sp_outer - sp_inner
    sp_mid = 0.5 * (sp_inner + sp_outer)  # radial midpoint
    for k in range(4):
        a = k * math.pi / 2.0
        dy, dz = math.cos(a), math.sin(a)  # outward radial direction (y-z plane)
        rx = math.atan2(-dy, dz)
        _rod(
            array,
            length=sp_len,
            radius=0.005,
            origin=Origin(xyz=(cx, sp_mid * dy, sp_mid * dz), rpy=(rx, 0.0, 0.0)),
            material=mats["metal"],
            name=f"loop_support_{k}",
        )
    array.inertial = Inertial.from_geometry(
        Box((r.boom_len, 0.5, 0.7)),
        mass=0.4,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    _attach_elevation(model, head, array, r, post_top, pivot_geom="center_hub")
    return array


def _emit_panel(model, head, r: ResolvedRoofAntennaConfig, mats, post_top):
    array = model.part("panel")
    # stub_bracket (pivot_geom) + riser + flat radome panel + 4x6 patch grid.
    array.visual(
        Box((0.05, 0.05, 0.05)),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["dark"],
        name="stub_bracket", material_class_id="metal.blackened_gunmetal",
    )
    pw, ph, pt = 0.34, 0.50, 0.020
    panel_x = 0.07
    # Riser spans from the stub_bracket (x~0) up to the panel back face
    # (x = panel_x - pt/2 = 0.06) so both ends overlap their neighbors.
    array.visual(
        Box((0.075, 0.05, 0.10)),
        origin=Origin(xyz=(0.030, 0.0, 0.06)),
        material=mats["dark"],
        name="panel_mount_riser", material_class_id="metal.blackened_gunmetal",
    )
    array.visual(
        Box((pt, pw, ph)),
        origin=Origin(xyz=(panel_x, 0.0, 0.10)),
        material=mats["accent"],
        name="radome_panel", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
    )
    # 4x6 = 24 patches embedded into the +X face of the panel.
    idx = 0
    for cy in range(4):
        for cz in range(6):
            yy = -pw * 0.36 + pw * 0.72 * cy / 3.0
            zz = 0.10 - ph * 0.36 + ph * 0.72 * cz / 5.0
            array.visual(
                Box((0.006, 0.040, 0.040)),
                origin=Origin(xyz=(panel_x + pt / 2.0, yy, zz)),
                material=mats["metal"],
                name=f"patch_{idx}", material_class_id=("metal.aluminum_bare" if r.palette_style in {"aluminium", "galvanized", "black", "white_painted", "bronze"} else "rust.oxidized_metal"),
            )
            idx += 1
    array.visual(
        Box((0.05, 0.05, 0.04)),
        origin=Origin(xyz=(0.0, 0.0, -0.04)),
        material=mats["dark"],
        name="junction_box", material_class_id="metal.blackened_gunmetal",
    )
    array.inertial = Inertial.from_geometry(
        Box((0.06, pw, ph)),
        mass=0.4,
        origin=Origin(xyz=(panel_x, 0.0, 0.10)),
    )
    _attach_elevation(model, head, array, r, post_top, pivot_geom="stub_bracket")
    return array


_ARRAY_BUILDERS = {
    "yagi_director_array": _emit_yagi,
    "dish_reflector": _emit_dish,
    "dipole_whip": _emit_dipole,
    "panel": _emit_panel,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_roof_antenna(
    config: RoofAntennaConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"roof_antenna_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    mast = _build_mast(model, r, mats)
    head, post_top = _build_antenna_head(model, mast, r, mats)
    _ARRAY_BUILDERS[r.antenna_type](model, head, r, mats, post_top)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_roof_antenna(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_roof_antenna(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_roof_antenna_tests(
    object_model: ArticulatedObject,
    config: RoofAntennaConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    mast = object_model.get_part("mast")
    head = object_model.get_part("antenna_head")

    # ---- Intentional overlaps (element-scoped). ----
    # Collar + clamp blocks grip the mast pole.
    ctx.allow_overlap(
        head, mast, elem_a="azimuth_collar", elem_b="mast_pole",
        reason="azimuth collar wraps the mast top (captured rotation fit).",
    )
    for i in range(2):
        ctx.allow_overlap(
            head, mast, elem_a=f"clamp_block_{i}", elem_b="mast_pole",
            reason=f"clamp block {i} grips the mast pole inside the collar.",
        )
    if r.mast_mount == "wall_bracket":
        for i in range(2):
            ctx.allow_overlap(
                mast, mast, elem_a=f"arm_clamp_{i}", elem_b="mast_pole",
                reason="wall-bracket arm clamp grips the mast pole.",
            )
    if r.mast_mount == "chimney_strap":
        for i in range(3):
            ctx.allow_overlap(
                mast, mast, elem_a=f"strap_{i}", elem_b="mast_pole",
                reason="hose strap wraps the chimney and the mast pole.",
            )
            ctx.allow_overlap(
                mast, mast, elem_a=f"strap_{i}", elem_b="chimney_block",
                reason="hose strap wraps the chimney block.",
            )

    # Array pivot overlaps the elevation_post.
    array_name = {
        "yagi_director_array": "yagi_boom",
        "dish_reflector": "dish_assembly",
        "dipole_whip": "dipole_assembly",
        "panel": "panel",
    }[r.antenna_type]
    array = object_model.get_part(array_name)
    ctx.allow_overlap(
        array, head, reason="array pivot boss seats over the elevation post.",
    )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- Structure / identity. ----
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "mast + antenna_head + array parts present",
        {"mast", "antenna_head", array_name}.issubset(part_names),
        details=str(sorted(part_names)),
    )

    # ---- Mast lands on roof z=0 and is tall (>3m head). ----
    aabb = ctx.part_world_aabb(mast)
    if aabb is not None:
        (axmn, aymn, azmn), (axmx, aymx, azmx) = aabb
        ctx.check("mast foot on the roof (z=0)", azmn < 0.02, details=f"z_min={azmn:.4f}")
        ctx.check("mast is tall (>3m)", azmx > 3.0, details=f"z_max={azmx:.4f}")

    # ---- Head world z > 3.0. ----
    ctx.check("azimuth head above 3m", r.head_z > 3.0, details=f"head_z={r.head_z:.4f}")

    # ---- Azimuth (DEFINING) REVOLUTE +Z. ----
    az = object_model.get_articulation("azimuth_joint")
    ctx.check(
        "azimuth is DEFINING REVOLUTE about +Z",
        az.articulation_type == ArticulationType.REVOLUTE and abs(az.axis[2]) > 0.99,
        details=f"type={az.articulation_type} axis={tuple(az.axis)}",
    )
    ctx.check(
        "azimuth origin tracks mast_x",
        abs(az.origin.xyz[0] - r.mast_x) < 1e-6,
        details=f"origin_x={az.origin.xyz[0]:.4f} mast_x={r.mast_x:.4f}",
    )

    # ---- Elevation REVOLUTE about ±Y. ----
    ev = object_model.get_articulation("elevation_joint")
    ctx.check(
        "elevation is REVOLUTE about ±Y",
        ev.articulation_type == ArticulationType.REVOLUTE and abs(ev.axis[1]) > 0.99,
        details=f"type={ev.articulation_type} axis={tuple(ev.axis)}",
    )

    # ---- Azimuth actuation rotates the head/array in plan. ----
    closed = ctx.part_world_aabb(array)
    with ctx.pose({az: math.pi / 2.0}):
        rotated = ctx.part_world_aabb(array)
    if closed is not None and rotated is not None:
        moved = (
            abs(rotated[0][0] - closed[0][0]) + abs(rotated[1][0] - closed[1][0])
            + abs(rotated[0][1] - closed[0][1]) + abs(rotated[1][1] - closed[1][1])
        )
        ctx.check(
            "azimuth rotates the array head",
            moved > 0.05,
            details=f"plan shift={moved:.4f}",
        )

    # ---- Element multiplicity (row types only). ----
    if r.exposes_elements:
        if r.boom_config == "X_dual_boom":
            elem_names = [v.name for v in array.visuals if v.name.startswith("element_0_")]
            ctx.check(
                "X_dual boom 0 has N elements",
                len(elem_names) == r.element_count_N,
                details=f"count={len(elem_names)} N={r.element_count_N}",
            )
            elem1 = [v.name for v in array.visuals if v.name.startswith("element_1_")]
            ctx.check(
                "X_dual boom 1 has N elements",
                len(elem1) == r.element_count_N,
                details=f"count={len(elem1)} N={r.element_count_N}",
            )
        else:
            elem_names = [
                v.name for v in array.visuals
                if v.name.startswith("element_") and v.name[len("element_"):].isdigit()
            ]
            ctx.check(
                "boom has N director elements (loop-emitted)",
                len(elem_names) == r.element_count_N,
                details=f"count={len(elem_names)} N={r.element_count_N}",
            )
        ctx.check(
            "element_count_N within [5,14]",
            N_MIN <= r.element_count_N <= N_MAX,
            details=f"N={r.element_count_N}",
        )

    # ---- Conditional gating. ----
    if r.antenna_type != "yagi_director_array":
        ctx.check(
            "non-yagi forces single_boom",
            r.boom_config == "single_boom",
            details=f"boom_config={r.boom_config}",
        )
    if r.antenna_type not in ROW_TYPES:
        ctx.check(
            "dish/panel do not expose elements in slot_choices",
            all(s[0] != "element_count_N" for s in slot_choices_for_config(r)),
            details=str(slot_choices_for_config(r)),
        )

    # ---- collar_inner_r derives from mast_radius_scale (snug fit). ----
    ctx.check(
        "collar_inner_r snug around mast (no pierce/detach)",
        r.mast_r < r.collar_inner_r <= r.mast_r + 0.017,
        details=f"mast_r={r.mast_r:.4f} collar_inner_r={r.collar_inner_r:.4f}",
    )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "RoofAntennaConfig",
    "ResolvedRoofAntennaConfig",
    "build_roof_antenna",
    "build_seeded_roof_antenna",
    "config_from_seed",
    "resolve_config",
    "run_roof_antenna_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
