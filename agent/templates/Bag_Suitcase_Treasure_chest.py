# SPDX-License-Identifier: Apache-2.0

"""Treasure chest (medieval banded wooden chest) — modular procedural template.

Category identity: a single rectangular plank-sided wooden chest body
(``chest_body``) closed by **one curved / peaked / flat lid** hinged at the rear
seam (the category headline axis ``lid_profile``), wrapped in iron banding
(``banding``) and closed by a front lock mechanism (``lock_mechanism``).  The lid
must keep its **curved / peaked identity** — domed_barrel is a true lathe
half-cylinder (``_barrel_band``), gabled_peaked is a triangular-ridge prism
(``_gabled_panel``); neither degrades to a flat box.  ``band_count`` is the one
multiplicity axis: N horizontal lid straps (``lid_strap_{i}``) wrapping the lid,
geometry following the lid profile.

Pattern: ``mixed`` — three named slots (lid_profile + lock_mechanism + banding)
hang off the shared ``chest_body`` root, plus the ``band_count`` multiplicity
axis copying ``lid_strap_{i}`` visuals onto ``chest_lid``.  The only active main
axis is ``lid_hinge`` (REVOLUTE -X at the rear seam); front_hasp adds a REVOLUTE
parented to the **lid**; padlock_loop adds a FIXED padlock body + a REVOLUTE
shackle parented to the **padlock body**.

Sources (synced under ``data/records/``): parent ``…_6febc2df`` (domed lathe lid
+ front hasp + iron straps), ``rec_chest_var_flatlid`` (flat plank lid),
``rec_chest_var_gabled`` (gabled mesh lid), ``rec_chest_var_padlock`` (padlock +
shackle), ``rec_chest_var_corners`` (8 corner L-brackets).  See spec
``articraft_template_authoring/specs_modular_v1/Bag_Suitcase_Treasure_chest.md``.

slot_choices_for_seed returns the 4-tuple
``(lid_profile, lock_mechanism, banding, ("band_count", f"n{N}"))`` consumed by
the ``module_topology_diversity`` gate.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    BoxGeometry,
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

LidProfile = Literal["domed_barrel", "flat_plank", "gabled_peaked"]
LockMechanism = Literal["front_hasp", "padlock_loop"]
Banding = Literal["iron_straps", "corner_brackets"]
PaletteStyle = Literal[
    "aged_oak_iron",
    "dark_walnut_blackiron",
    "weathered_pine_iron",
    "mahogany_brass",
    "ebony_brass",
]

LID_PROFILES: tuple[LidProfile, ...] = ("domed_barrel", "flat_plank", "gabled_peaked")
LOCK_MECHANISMS: tuple[LockMechanism, ...] = ("front_hasp", "padlock_loop")
BANDINGS: tuple[Banding, ...] = ("iron_straps", "corner_brackets")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "aged_oak_iron",
    "dark_walnut_blackiron",
    "weathered_pine_iron",
    "mahogany_brass",
    "ebony_brass",
)

N_MIN = 2
N_MAX = 6
# band_count sampling weights (spec §8: 3-4 high-frequency, 5-6 long tail).
BAND_COUNT_VALUES = (2, 3, 4, 5, 6)
BAND_COUNT_WEIGHTS = (0.16, 0.30, 0.28, 0.16, 0.10)

# Each palette gives a wood-stain trio plus an iron/blackened band colour and a
# bright (brass / accent) colour used for the lock body + rivet highlights.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "aged_oak_iron": {
        "wood": (0.42, 0.30, 0.20, 1.0),
        "wood_dark": (0.30, 0.21, 0.14, 1.0),
        "wood_light": (0.48, 0.35, 0.23, 1.0),
        "iron": (0.20, 0.21, 0.24, 1.0),
        "iron_dark": (0.16, 0.17, 0.20, 1.0),
        "bright": (0.52, 0.46, 0.30, 1.0),
    },
    "dark_walnut_blackiron": {
        "wood": (0.26, 0.17, 0.11, 1.0),
        "wood_dark": (0.18, 0.12, 0.08, 1.0),
        "wood_light": (0.34, 0.24, 0.16, 1.0),
        "iron": (0.16, 0.17, 0.20, 1.0),
        "iron_dark": (0.12, 0.13, 0.16, 1.0),
        "bright": (0.40, 0.40, 0.42, 1.0),
    },
    "weathered_pine_iron": {
        "wood": (0.55, 0.45, 0.34, 1.0),
        "wood_dark": (0.42, 0.34, 0.25, 1.0),
        "wood_light": (0.62, 0.52, 0.40, 1.0),
        "iron": (0.20, 0.21, 0.24, 1.0),
        "iron_dark": (0.16, 0.17, 0.20, 1.0),
        "bright": (0.50, 0.50, 0.52, 1.0),
    },
    "mahogany_brass": {
        "wood": (0.36, 0.18, 0.13, 1.0),
        "wood_dark": (0.26, 0.13, 0.09, 1.0),
        "wood_light": (0.44, 0.24, 0.18, 1.0),
        "iron": (0.20, 0.21, 0.24, 1.0),
        "iron_dark": (0.16, 0.17, 0.20, 1.0),
        "bright": (0.60, 0.50, 0.22, 1.0),
    },
    "ebony_brass": {
        "wood": (0.16, 0.13, 0.11, 1.0),
        "wood_dark": (0.10, 0.08, 0.07, 1.0),
        "wood_light": (0.24, 0.20, 0.17, 1.0),
        "iron": (0.16, 0.17, 0.20, 1.0),
        "iron_dark": (0.13, 0.13, 0.16, 1.0),
        "bright": (0.60, 0.50, 0.22, 1.0),
    },
}

BRACKET_ARM = 0.07  # corner bracket arm length from corner
BRACKET_T = 0.005  # corner bracket plate thickness


@dataclass(frozen=True)
class TreasureChestConfig:
    lid_profile: LidProfile = "domed_barrel"
    lock_mechanism: LockMechanism = "front_hasp"
    banding: Banding = "iron_straps"
    band_count: int = 5
    palette_style: PaletteStyle = "aged_oak_iron"
    box_w: float = 0.46
    box_d: float = 0.30
    box_h: float = 0.18
    lid_open_scale: float = 1.0
    lock_open_scale: float = 1.0
    strap_spacing_scale: float = 1.0
    name: str = "reference_treasure_chest"


@dataclass(frozen=True)
class ResolvedTreasureChestConfig:
    lid_profile: LidProfile
    lock_mechanism: LockMechanism
    banding: Banding
    band_count: int
    palette_style: PaletteStyle
    box_w: float
    box_d: float
    box_h: float
    wall_t: float
    lid_t: float
    barrel_r: float
    gable_peak: float
    lid_open_scale: float
    lock_open_scale: float
    strap_spacing_scale: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _max_band_count(box_w: float, strap_w: float, margin: float) -> int:
    """Largest N whose absolute-spaced straps stay within the lid width.

    Constraint: N*strap_w + (N-1)*min_gap <= W - 2*margin.
    """
    usable = box_w - 2.0 * margin
    min_gap = 0.010
    n = N_MAX
    while n > N_MIN:
        if n * strap_w + (n - 1) * min_gap <= usable:
            break
        n -= 1
    return max(N_MIN, n)


def config_from_seed(seed: int) -> TreasureChestConfig:
    rng = random.Random(seed)
    lid_profile = rng.choice(LID_PROFILES)
    lock_mechanism = rng.choice(LOCK_MECHANISMS)
    banding = rng.choice(BANDINGS)
    band_count = rng.choices(BAND_COUNT_VALUES, weights=BAND_COUNT_WEIGHTS, k=1)[0]
    palette_style = rng.choice(PALETTE_STYLES)

    box_w = round(rng.uniform(0.34, 0.60), 3)
    box_d = round(rng.uniform(0.24, 0.38), 3)
    box_h = round(rng.uniform(0.14, 0.24), 3)

    return TreasureChestConfig(
        lid_profile=lid_profile,
        lock_mechanism=lock_mechanism,
        banding=banding,
        band_count=band_count,
        palette_style=palette_style,
        box_w=box_w,
        box_d=box_d,
        box_h=box_h,
        lid_open_scale=round(rng.uniform(0.85, 1.05), 4),
        lock_open_scale=round(rng.uniform(0.85, 1.05), 4),
        strap_spacing_scale=round(rng.uniform(0.90, 1.10), 4),
        name=f"seeded_treasure_chest_{seed}",
    )


def resolve_config(config: TreasureChestConfig | None = None) -> ResolvedTreasureChestConfig:
    cfg = config or TreasureChestConfig()
    lid_profile = _pick(cfg.lid_profile, LID_PROFILES)
    lock_mechanism = _pick(cfg.lock_mechanism, LOCK_MECHANISMS)
    banding = _pick(cfg.banding, BANDINGS)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    box_w = _clamp(cfg.box_w, 0.34, 0.60)
    box_d = _clamp(cfg.box_d, 0.24, 0.38)
    box_h = _clamp(cfg.box_h, 0.14, 0.24)

    wall_t = _clamp(0.018 * (box_w / 0.46), 0.014, 0.020)
    lid_t = 0.022
    barrel_r = box_d / 2.0
    gable_peak = _clamp(0.5 * box_d, 0.06, 0.13)

    # band_count clamped to [2,6] then narrowed by the lid-width inequality.
    strap_w = 0.028
    margin = 0.016
    n = int(_clamp(float(cfg.band_count), N_MIN, N_MAX))
    n = min(n, _max_band_count(box_w, strap_w, margin))

    return ResolvedTreasureChestConfig(
        lid_profile=lid_profile,
        lock_mechanism=lock_mechanism,
        banding=banding,
        band_count=n,
        palette_style=palette_style,
        box_w=box_w,
        box_d=box_d,
        box_h=box_h,
        wall_t=wall_t,
        lid_t=lid_t,
        barrel_r=barrel_r,
        gable_peak=gable_peak,
        lid_open_scale=_clamp(cfg.lid_open_scale, 0.85, 1.05),
        lock_open_scale=_clamp(cfg.lock_open_scale, 0.85, 1.05),
        strap_spacing_scale=_clamp(cfg.strap_spacing_scale, 0.90, 1.10),
        name=cfg.name or "treasure_chest",
    )


def with_overrides(config: TreasureChestConfig, **kwargs: object) -> TreasureChestConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: TreasureChestConfig | ResolvedTreasureChestConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedTreasureChestConfig) else resolve_config(config)
    return (
        ("lid_profile", r.lid_profile),
        ("lock_mechanism", r.lock_mechanism),
        ("banding", r.banding),
        ("band_count", f"n{r.band_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _joint_meta(joint_type, axis, origin, limits) -> dict[str, object]:
    return {
        "type": joint_type.value,
        "axis": axis,
        "origin": origin,
        "range": None if limits is None else (limits.lower, limits.upper),
    }


def _box(part, size, xyz, material, name: str, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="wood.plank_floor")


def _half_disk_profile(r, segs=26):
    pts = []
    for i in range(segs + 1):
        a = math.pi * i / segs
        pts.append((r * math.cos(a), r * math.sin(a)))
    return pts


def _barrel_band(r, depth, x0, xw):
    """Solid half-cylinder band of radius r, width xw centered at x0, authored
    in the lid-local frame (hinge at the rear seam: local y in [-depth, 0])."""
    geo = ExtrudeGeometry.from_z0(_half_disk_profile(r), xw, cap=True)
    geo.rotate_z(math.pi / 2.0)
    geo.rotate_y(math.pi / 2.0)
    geo.translate(x0 - xw / 2.0, -depth / 2.0, 0.0)
    return geo


def _gabled_profile(depth, peak_h):
    half = depth / 2.0
    return [(half, 0.0), (-half, 0.0), (0.0, peak_h)]


def _gabled_panel(depth, peak_h, width, x_center=0.0):
    """Solid gabled triangular prism, authored in the lid-local frame."""
    profile = _gabled_profile(depth, peak_h)
    geo = ExtrudeGeometry.from_z0(profile, width, cap=True)
    geo.rotate_z(math.pi / 2.0)
    geo.rotate_y(math.pi / 2.0)
    geo.translate(x_center - width / 2.0, -depth / 2.0, 0.0)
    return geo


def _gabled_strap(depth, peak_h, width, x_center=0.0, proud=0.004):
    """Iron strap wrapping over the gabled surface (slightly proud)."""
    half = depth / 2.0
    profile = [
        (half + proud, -proud),
        (-(half + proud), -proud),
        (0.0, peak_h + proud),
    ]
    geo = ExtrudeGeometry.from_z0(profile, width, cap=True)
    geo.rotate_z(math.pi / 2.0)
    geo.rotate_y(math.pi / 2.0)
    geo.translate(x_center - width / 2.0, -depth / 2.0, 0.0)
    return geo


def _u_bar(w, h, t, depth):
    """U-shaped bar profile opening downward, extruded along -Y after rotation."""
    profile = [
        (-w / 2.0, 0.0),
        (-w / 2.0, h),
        (w / 2.0, h),
        (w / 2.0, 0.0),
        (w / 2.0 - t, 0.0),
        (w / 2.0 - t, h - t),
        (-(w / 2.0 - t), h - t),
        (-(w / 2.0 - t), 0.0),
    ]
    geo = ExtrudeGeometry.from_z0(profile, depth, cap=True)
    geo.rotate_x(math.pi / 2.0)
    return geo


def _corner_bracket_mesh(cx, cy, cz, sx, sy, is_top):
    """Single connected L-shaped corner bracket mesh wrapping a box corner."""
    arm = BRACKET_ARM
    t = BRACKET_T
    dx = -float(sx)
    dy = -float(sy)
    dz = -1.0 if is_top else 1.0
    plate_len = arm + t
    half_t = t / 2.0

    plate_z = BoxGeometry((plate_len, plate_len, t))
    plate_z.translate(
        cx + dx * (plate_len / 2.0 - t),
        cy + dy * (plate_len / 2.0 - t),
        cz - dz * half_t,
    )
    plate_y = BoxGeometry((plate_len, t, plate_len))
    plate_y.translate(
        cx + dx * (plate_len / 2.0 - t),
        cy - dy * half_t,
        cz + dz * (plate_len / 2.0 - t),
    )
    plate_x = BoxGeometry((t, plate_len, plate_len))
    plate_x.translate(
        cx - dx * half_t,
        cy + dy * (plate_len / 2.0 - t),
        cz + dz * (plate_len / 2.0 - t),
    )
    plate_z.merge(plate_y)
    plate_z.merge(plate_x)

    rs = 0.008
    rh = 0.004
    rpos = arm * 0.55
    rv_z = BoxGeometry((rs, rs, rh))
    rv_z.translate(cx + dx * rpos, cy + dy * rpos, cz - dz * (half_t + rh / 2.0))
    plate_z.merge(rv_z)
    rv_y = BoxGeometry((rs, rh, rs))
    rv_y.translate(cx + dx * rpos, cy - dy * (half_t + rh / 2.0), cz + dz * rpos)
    plate_z.merge(rv_y)
    rv_x = BoxGeometry((rh, rs, rs))
    rv_x.translate(cx - dx * (half_t + rh / 2.0), cy + dy * rpos, cz + dz * rpos)
    plate_z.merge(rv_x)
    return plate_z


def _strap_x_positions(r: ResolvedTreasureChestConfig) -> list[float]:
    """Absolute, symmetric X positions of the N lid straps (end straps near
    the lid edges).  N-invariant: each x is solved from N and lid width."""
    w = r.box_w
    n = r.band_count
    margin = 0.016
    usable = (w - 2.0 * margin) * r.strap_spacing_scale
    usable = min(usable, w - 2.0 * margin)
    if n == 1:
        return [0.0]
    step = usable / (n - 1)
    return [-usable / 2.0 + i * step for i in range(n)]


# ---------------------------------------------------------------------------
# Body chassis (root) + banding.
# Coordinates: floor inside-base at z=0; walls rise to z=box_h. Front=-Y, back=+Y.
# ---------------------------------------------------------------------------
def _build_chassis(body, r: ResolvedTreasureChestConfig, mats: dict) -> None:
    w, d, hb, t = r.box_w, r.box_d, r.box_h, r.wall_t
    cz = hb / 2.0
    wood = mats["wood"]
    wood_dark = mats["wood_dark"]

    _box(body, (w, d, t), (0.0, 0.0, t / 2.0), wood_dark, "floor_panel")
    _box(body, (w, t, hb), (0.0, -(d / 2.0 - t / 2.0), cz), wood, "wall_front")
    _box(body, (w, t, hb), (0.0, (d / 2.0 - t / 2.0), cz), wood, "wall_back")
    _box(body, (t, d, hb), (-(w / 2.0 - t / 2.0), 0.0, cz), wood, "wall_left")
    _box(body, (t, d, hb), ((w / 2.0 - t / 2.0), 0.0, cz), wood, "wall_right")

    _build_banding(body, r, mats)


def _build_banding(body, r: ResolvedTreasureChestConfig, mats: dict) -> None:
    w, d, hb = r.box_w, r.box_d, r.box_h
    cz = hb / 2.0
    iron = mats["iron"]

    if r.banding == "iron_straps":
        bk = 0.034
        idx = 0
        for sx in (-1.0, 1.0):
            for sy in (-1.0, 1.0):
                _box(
                    body,
                    (bk, bk, hb),
                    (sx * (w / 2.0 - bk / 2.0 + 0.003), sy * (d / 2.0 - bk / 2.0 + 0.003), cz),
                    iron,
                    f"corner_post_{idx}",
                )
                idx += 1
        for sx in (-w * 0.26, w * 0.26):
            tag = "l" if sx < 0 else "r"
            _box(body, (0.03, d + 0.004, 0.006), (sx, 0.0, cz), iron, f"body_band_{tag}")
    else:  # corner_brackets
        _corners = [
            (-w / 2.0, -d / 2.0, 0.0, -1, -1, False),
            (w / 2.0, -d / 2.0, 0.0, 1, -1, False),
            (-w / 2.0, d / 2.0, 0.0, -1, 1, False),
            (w / 2.0, d / 2.0, 0.0, 1, 1, False),
            (-w / 2.0, -d / 2.0, hb, -1, -1, True),
            (w / 2.0, -d / 2.0, hb, 1, -1, True),
            (-w / 2.0, d / 2.0, hb, -1, 1, True),
            (w / 2.0, d / 2.0, hb, 1, 1, True),
        ]
        for i in range(8):
            cx, cy, cz_val, sx, sy, is_top = _corners[i]
            bracket = _corner_bracket_mesh(cx, cy, cz_val, sx, sy, is_top)
            body.visual(
                mesh_from_geometry(bracket, f"corner_bracket_{i}"),
                material=iron,
                name=f"corner_bracket_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "dark_walnut_blackiron" else "metal.cast_iron_bare"),
            )


# ---------------------------------------------------------------------------
# Lid closures.  Each emits ``chest_lid`` + N lid straps + ``hasp_mount`` and the
# ``lid_hinge`` REVOLUTE at the rear seam, and returns the front-edge Y where the
# hasp hinge attaches (lid-local) plus its Z.
# ---------------------------------------------------------------------------
def _build_lid(model, body, r: ResolvedTreasureChestConfig, mats: dict) -> tuple[float, float]:
    w, d, hb = r.box_w, r.box_d, r.box_h
    scale = r.lid_open_scale
    wood = mats["wood"]
    wood_light = mats["wood_light"]
    wood_dark = mats["wood_dark"]
    iron = mats["iron"]
    rim_z = hb

    lid = model.part("chest_lid")
    strap_xs = _strap_x_positions(r)
    strap_w = 0.028

    if r.lid_profile == "domed_barrel":
        rr = r.barrel_r
        dome = _barrel_band(rr, d, 0.0, w)
        lid.visual(mesh_from_geometry(dome, "lid_dome"), material=wood, name="lid_dome", material_class_id=("wood.oak" if r.palette_style in {"aged_oak_iron", "weathered_pine_iron", "mahogany_brass"} else "wood.walnut_dark"))
        for i, x0 in enumerate(strap_xs):
            strap = _barrel_band(rr + 0.004, d, x0, strap_w)
            lid.visual(
                mesh_from_geometry(strap, f"lid_strap_{i}"), material=iron, name=f"lid_strap_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "dark_walnut_blackiron" else "metal.cast_iron_bare")
            )
        # forward hasp mount tab (reaches over the front face).
        hasp_y = -d + 0.003
        hasp_z = rr * 0.30
        lid.visual(
            Box((0.05, 0.020, 0.022)),
            origin=Origin(xyz=(0.0, hasp_y, hasp_z)),
            material=iron,
            name="hasp_mount", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "dark_walnut_blackiron" else "metal.cast_iron_bare"),
        )

    elif r.lid_profile == "flat_plank":
        lt = r.lid_t
        # Continuous base panel keeps the flat lid a single connected part; the
        # plank look comes from alternating proud plank strips on top + grooves.
        lid.visual(
            Box((w + 0.02, d + 0.02, lt)),
            origin=Origin(xyz=(0.0, -d / 2.0, lt / 2.0)),
            material=wood,
            name="lid_plank_0", material_class_id=("wood.oak" if r.palette_style in {"aged_oak_iron", "weathered_pine_iron", "mahogany_brass"} else "wood.walnut_dark"),
        )
        n_planks = 4
        plank_gap = 0.003
        plank_w = (w - (n_planks - 1) * plank_gap) / n_planks
        for i in range(1, n_planks):
            mat = wood if i % 2 == 0 else wood_light
            px = -w / 2.0 + plank_w / 2.0 + i * (plank_w + plank_gap)
            # proud strips overlap into the base panel (top embed) so they stay
            # connected to the single lid part.
            lid.visual(
                Box((plank_w - 0.004, d, 0.004)),
                origin=Origin(xyz=(px, -d / 2.0, lt + 0.002 - 0.002)),
                material=mat,
                name=f"lid_plank_{i}", material_class_id=("wood.oak" if r.palette_style in {"aged_oak_iron", "weathered_pine_iron", "mahogany_brass"} else "wood.walnut_dark"),
            )
        # flat iron straps across width (band_count copies); each strap is wide
        # enough in depth to bridge over the proud strips and embed into the base.
        for i, x0 in enumerate(strap_xs):
            lid.visual(
                Box((strap_w, d + 0.004, 0.006)),
                origin=Origin(xyz=(x0, -d / 2.0, lt + 0.006 / 2.0 - 0.003)),
                material=iron,
                name=f"lid_strap_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "dark_walnut_blackiron" else "metal.cast_iron_bare"),
            )
        hasp_y = -d - 0.006
        hasp_z = lt * 0.4
        lid.visual(
            Box((0.05, 0.012, 0.04)),
            origin=Origin(xyz=(0.0, hasp_y, hasp_z)),
            material=iron,
            name="hasp_mount", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "dark_walnut_blackiron" else "metal.cast_iron_bare"),
        )

    else:  # gabled_peaked
        peak = r.gable_peak
        lid_panel = _gabled_panel(d, peak, w)
        lid.visual(mesh_from_geometry(lid_panel, "lid_panel"), material=wood, name="lid_panel", material_class_id=("wood.oak" if r.palette_style in {"aged_oak_iron", "weathered_pine_iron", "mahogany_brass"} else "wood.walnut_dark"))
        for i, x0 in enumerate(strap_xs):
            strap = _gabled_strap(d, peak, strap_w, x_center=x0, proud=0.004)
            lid.visual(
                mesh_from_geometry(strap, f"lid_strap_{i}"), material=iron, name=f"lid_strap_{i}", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "dark_walnut_blackiron" else "metal.cast_iron_bare")
            )
        lid.visual(
            Box((w - 0.02, 0.032, 0.006)),
            origin=Origin(xyz=(0.0, -d / 2.0, peak + 0.003)),
            material=iron,
            name="ridge_cap", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "dark_walnut_blackiron" else "metal.cast_iron_bare"),
        )
        lid.visual(
            Box((w - 0.02, 0.008, 0.04)),
            origin=Origin(xyz=(0.0, -d - 0.005, -0.02)),
            material=wood_dark,
            name="lid_front_skirt", material_class_id=("wood.oak" if r.palette_style in {"aged_oak_iron", "weathered_pine_iron", "mahogany_brass"} else "wood.walnut_dark"),
        )
        hasp_y = -d - 0.008
        hasp_z = -0.015
        lid.visual(
            Box((0.05, 0.012, 0.025)),
            origin=Origin(xyz=(0.0, hasp_y, hasp_z)),
            material=iron,
            name="hasp_mount", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "dark_walnut_blackiron" else "metal.cast_iron_bare"),
        )

    limits = MotionLimits(
        effort=18.0, velocity=2.0, lower=0.0, upper=_clamp(1.9 * scale, 0.0, math.pi * 0.62)
    )
    origin = (0.0, d / 2.0, rim_z)
    model.articulation(
        "lid_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=origin),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=limits,
        meta=_joint_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), origin, limits),
    )
    # hasp hinge attach point: just below/forward of the hasp_mount tab.
    return hasp_y - 0.006, hasp_z


# ---------------------------------------------------------------------------
# Lock mechanism.
# front_hasp: lock_keeper on body front + lock_hasp part REVOLUTE on the LID.
# padlock_loop: staple_loop on body front + padlock_body FIXED + shackle REVOLUTE
#               parented to the padlock body.
# ---------------------------------------------------------------------------
def _build_lock(
    model, body, r: ResolvedTreasureChestConfig, mats: dict, hasp_y: float, hasp_z: float
) -> None:
    d, hb = r.box_d, r.box_h
    scale = r.lock_open_scale
    iron = mats["iron"]
    iron_dark = mats["iron_dark"]
    bright = mats["bright"]
    lid = model.get_part("chest_lid")

    if r.lock_mechanism == "front_hasp":
        # body keeper staple that receives the hasp eye.
        _box(body, (0.05, 0.012, 0.035), (0.0, -(d / 2.0) - 0.006, hb * 0.55), iron, "lock_keeper")
        hasp = model.part("lock_hasp")
        hasp.visual(
            Box((0.05, 0.010, 0.11)),
            origin=Origin(xyz=(0.0, 0.0, -0.055)),
            material=iron,
            name="hasp_arm", material_class_id=("metal.blackened_gunmetal" if r.palette_style == "dark_walnut_blackiron" else "metal.cast_iron_bare"),
        )
        hasp.visual(
            Box((0.026, 0.016, 0.02)),
            origin=Origin(xyz=(0.0, -0.005, -0.10)),
            material=bright,
            name="hasp_eye", material_class_id=("metal.brass_aged" if r.palette_style in {"aged_oak_iron", "mahogany_brass", "ebony_brass"} else "metal.brushed_silver"),
        )
        limits = MotionLimits(effort=3.0, velocity=3.0, lower=0.0, upper=1.4 * scale)
        origin = (0.0, hasp_y, hasp_z)
        # Axis -X so the hasp arm lifts FORWARD (-Y) off the body keeper as it
        # opens; +X would swing the arm backward into wall_front (穿模).
        model.articulation(
            "hasp_hinge",
            ArticulationType.REVOLUTE,
            parent=lid,
            child=hasp,
            origin=Origin(xyz=origin),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=limits,
            meta=_joint_meta(ArticulationType.REVOLUTE, (-1.0, 0.0, 0.0), origin, limits),
        )
        return

    # padlock_loop
    staple_w = 0.044
    staple_h = 0.038
    staple_t = 0.008
    staple_d = 0.020
    staple_z_top = hb * 0.62
    staple_geo = _u_bar(staple_w, staple_h, staple_t, staple_d)
    staple_geo.translate(0.0, -d / 2.0, staple_z_top - staple_h)
    body.visual(
        mesh_from_geometry(staple_geo, "staple_loop"), material=iron_dark, name="staple_loop", material_class_id="metal.blackened_gunmetal"
    )
    _box(
        body,
        (staple_w + 0.012, 0.006, staple_h + 0.010),
        (0.0, -(d / 2.0 - 0.003), staple_z_top - staple_h / 2.0),
        iron,
        "staple_plate",
    )

    padlock_w = 0.042
    padlock_d = 0.020
    padlock_h = 0.050
    padlock_body_top_z = staple_z_top - staple_h - 0.003
    padlock_body_cz = padlock_body_top_z - padlock_h / 2.0
    padlock_body_cy = -d / 2.0 - staple_d / 2.0

    padlock = model.part("padlock_body")
    padlock_shape = (
        cq.Workplane("XY")
        .box(padlock_w, padlock_d, padlock_h)
        .edges("|Z")
        .fillet(0.005)
        .edges("#Z")
        .fillet(0.003)
    )
    padlock.visual(
        mesh_from_cadquery(padlock_shape, "padlock_case"),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=bright,
        name="padlock_case", material_class_id=("metal.brass_aged" if r.palette_style in {"aged_oak_iron", "mahogany_brass", "ebony_brass"} else "metal.brushed_silver"),
    )
    padlock.visual(
        Box((0.012, 0.003, 0.016)),
        origin=Origin(xyz=(0.0, -padlock_d / 2.0 - 0.001, -0.006)),
        material=iron_dark,
        name="keyhole_plate", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        "body_to_padlock",
        ArticulationType.FIXED,
        parent=body,
        child=padlock,
        origin=Origin(xyz=(0.0, padlock_body_cy, padlock_body_cz)),
        meta=_joint_meta(
            ArticulationType.FIXED, (0.0, 0.0, 1.0), (0.0, padlock_body_cy, padlock_body_cz), None
        ),
    )

    shackle_w = 0.030
    shackle_h = 0.042
    shackle_t = 0.006
    shackle_d = 0.014
    shackle = model.part("padlock_shackle")
    pivot_x = -shackle_w / 2.0 + shackle_t / 2.0
    shackle_geo = _u_bar(shackle_w, shackle_h, shackle_t, shackle_d)
    shackle_geo.translate(shackle_w / 2.0 - shackle_t / 2.0, shackle_d / 2.0, 0.0)
    shackle.visual(
        mesh_from_geometry(shackle_geo, "shackle_bow"), material=iron_dark, name="shackle_bow", material_class_id="metal.blackened_gunmetal"
    )
    leg_insert = 0.014
    shackle.visual(
        Cylinder(shackle_t / 2.0, leg_insert),
        origin=Origin(xyz=(0.0, 0.0, -leg_insert / 2.0)),
        material=iron_dark,
        name="shackle_leg_fixed", material_class_id="metal.blackened_gunmetal",
    )
    shackle.visual(
        Cylinder(shackle_t / 2.0, leg_insert),
        origin=Origin(xyz=(shackle_w - shackle_t, 0.0, -leg_insert / 2.0)),
        material=iron_dark,
        name="shackle_leg_free", material_class_id="metal.blackened_gunmetal",
    )
    limits = MotionLimits(effort=3.0, velocity=3.0, lower=0.0, upper=2.4 * scale)
    origin = (pivot_x, 0.0, padlock_h / 2.0)
    # Axis -Z so the free leg + bow swing FORWARD/outward (-Y, away from the
    # chest) about the captive fixed leg; +Z carried the bow into wall_front
    # (穿模) mid-swing. Pivot sits at the fixed leg so the staple stays captive.
    model.articulation(
        "shackle_hinge",
        ArticulationType.REVOLUTE,
        parent=padlock,
        child=shackle,
        origin=Origin(xyz=origin),
        axis=(0.0, 0.0, -1.0),
        motion_limits=limits,
        meta=_joint_meta(ArticulationType.REVOLUTE, (0.0, 0.0, -1.0), origin, limits),
    )


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------
def build_treasure_chest(
    config: TreasureChestConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"tc_{key}_{r.palette_style}", rgba=palette[key])
        for key in ("wood", "wood_dark", "wood_light", "iron", "iron_dark", "bright")
    }

    body = model.part("chest_body")
    _build_chassis(body, r, mats)
    body.inertial = Inertial.from_geometry(
        Box((r.box_w, r.box_d, r.box_h)),
        mass=5.0 + r.box_w * r.box_d * 30.0,
        origin=Origin(xyz=(0.0, 0.0, r.box_h / 2.0)),
    )

    hasp_y, hasp_z = _build_lid(model, body, r, mats)
    _build_lock(model, body, r, mats, hasp_y, hasp_z)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_treasure_chest(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_treasure_chest(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / allowances
# ---------------------------------------------------------------------------
def run_treasure_chest_tests(
    object_model: ArticulatedObject,
    config: TreasureChestConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("chest_body")
    lid = object_model.get_part("chest_lid")
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("chest_body present", "chest_body" in part_names)
    ctx.check("chest_lid present", "chest_lid" in part_names)
    ctx.check("lid_hinge present", "lid_hinge" in joint_names)
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # Closed lid seats on the body rim.
    ctx.allow_overlap(body, lid, reason="closed lid seats on the body rim (0-6 mm gap)")

    # --- Lid profile identity (curved / peaked must not degrade to a flat box). ---
    hb = r.box_h
    if r.lid_profile == "domed_barrel":
        dome_aabb = ctx.part_element_world_aabb(lid, elem="lid_dome")
        ctx.check(
            "lid is a raised dome above the seam",
            dome_aabb is not None and dome_aabb[1][2] > hb + r.barrel_r * 0.7,
            details=f"dome_aabb={dome_aabb}",
        )
    elif r.lid_profile == "gabled_peaked":
        ridge_aabb = ctx.part_element_world_aabb(lid, elem="ridge_cap")
        skirt_aabb = ctx.part_element_world_aabb(lid, elem="lid_front_skirt")
        ctx.check(
            "ridge peak rises above the seam by gable height",
            ridge_aabb is not None and ridge_aabb[1][2] > hb + r.gable_peak * 0.8,
            details=f"ridge_cap_aabb={ridge_aabb}",
        )
        ctx.check(
            "gabled peak rises above front edge (two-slope profile)",
            ridge_aabb is not None
            and skirt_aabb is not None
            and ridge_aabb[1][2] > skirt_aabb[1][2] + 0.04,
            details=f"ridge_top={ridge_aabb[1][2] if ridge_aabb else None}, "
            f"skirt_top={skirt_aabb[1][2] if skirt_aabb else None}",
        )
    else:  # flat_plank — reverse-guard against an accidental dome.
        with ctx.pose({object_model.get_articulation("lid_hinge"): 0.0}):
            closed_lid = ctx.part_world_aabb(lid)
        max_flat_z = hb + r.lid_t + 0.005 + 0.012
        ctx.check(
            "lid is a flat plank profile (not domed)",
            closed_lid is not None and closed_lid[1][2] < max_flat_z,
            details=f"lid_top_z={closed_lid[1][2] if closed_lid else None}, expected < {max_flat_z:.3f}",
        )

    # band_count straps present.
    ctx.check(
        f"all {r.band_count} lid straps present",
        all(f"lid_strap_{i}" in {v.name for v in lid.visuals} for i in range(r.band_count)),
    )

    # --- Lock mechanism. ---
    if r.lock_mechanism == "front_hasp":
        ctx.check("hasp_hinge present (parent=chest_lid)", "hasp_hinge" in joint_names)
        hasp_hinge = object_model.get_articulation("hasp_hinge")
        ctx.check(
            "hasp_hinge is parented to the lid",
            hasp_hinge.parent == "chest_lid",
            details=f"parent={hasp_hinge.parent}",
        )
        hasp = object_model.get_part("lock_hasp")
        ctx.allow_overlap(
            lid,
            hasp,
            elem_a="hasp_mount",
            elem_b="hasp_arm",
            reason="hasp arm hangs from and overlaps the lid hasp mount tab",
        )
        ctx.allow_overlap(
            body,
            hasp,
            elem_a="lock_keeper",
            elem_b="hasp_arm",
            reason="closed hasp arm hangs in front of the body keeper staple",
        )
        ctx.allow_overlap(
            body,
            hasp,
            elem_a="lock_keeper",
            elem_b="hasp_eye",
            reason="closed hasp eye wraps around the body keeper staple",
        )
        ctx.allow_overlap(lid, hasp, reason="closed hasp lies against the lid front edge")
        # Guard: open hasp must swing FORWARD off the keeper, never back into
        # wall_front. At the upper limit the whole hasp stays ahead of the
        # front wall face (-Y).
        front_face = -r.box_d / 2.0
        with ctx.pose({hasp_hinge: hasp_hinge.motion_limits.upper}):
            hasp_open = ctx.part_world_aabb(hasp)
        ctx.check(
            "open hasp clears the front wall (swings forward, no 穿模)",
            hasp_open is not None and hasp_open[1][1] <= front_face + 0.004,
            details=f"hasp_open_max_y={hasp_open[1][1] if hasp_open else None}, "
            f"front_face={front_face:.3f}",
        )
    else:  # padlock_loop
        ctx.check("body_to_padlock FIXED present", "body_to_padlock" in joint_names)
        ctx.check("shackle_hinge present (parent=padlock_body)", "shackle_hinge" in joint_names)
        shackle_hinge = object_model.get_articulation("shackle_hinge")
        padlock = object_model.get_part("padlock_body")
        ctx.check(
            "shackle_hinge is parented to the padlock body",
            shackle_hinge.parent == "padlock_body",
            details=f"parent={shackle_hinge.parent}",
        )
        ctx.check(
            "body_to_padlock is FIXED",
            object_model.get_articulation("body_to_padlock").articulation_type
            == ArticulationType.FIXED,
        )
        shackle = object_model.get_part("padlock_shackle")
        ctx.allow_overlap(
            body,
            shackle,
            elem_a="staple_loop",
            elem_b="shackle_bow",
            reason="the shackle passes through the body staple loop",
        )
        ctx.allow_overlap(
            padlock,
            shackle,
            elem_a="padlock_case",
            elem_b="shackle_leg_fixed",
            reason="the fixed shackle leg inserts into the padlock body",
        )
        ctx.allow_overlap(
            padlock,
            shackle,
            elem_a="padlock_case",
            elem_b="shackle_leg_free",
            reason="the free shackle leg inserts into the padlock body when closed",
        )
        # Guard: open shackle must swing FORWARD/outward (-Y), never back into
        # wall_front. At the upper limit the whole shackle stays ahead of the
        # front wall face (-Y).
        front_face = -r.box_d / 2.0
        with ctx.pose({shackle_hinge: shackle_hinge.motion_limits.upper}):
            shackle_open = ctx.part_world_aabb(shackle)
        ctx.check(
            "open shackle clears the front wall (swings outward, no 穿模)",
            shackle_open is not None and shackle_open[1][1] <= front_face + 0.004,
            details=f"shackle_open_max_y={shackle_open[1][1] if shackle_open else None}, "
            f"front_face={front_face:.3f}",
        )

    # --- Banding: top corner brackets sandwich with the lid edge at z=HB. ---
    if r.banding == "corner_brackets":
        for i in range(4, 8):
            ctx.allow_overlap(
                body,
                lid,
                elem_a=f"corner_bracket_{i}",
                elem_b="lid_dome"
                if r.lid_profile == "domed_barrel"
                else ("lid_panel" if r.lid_profile == "gabled_peaked" else "lid_plank_0"),
                reason="top corner bracket sits flush on the body top face where the lid edge seats at z=HB",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = (
    "TreasureChestConfig",
    "ResolvedTreasureChestConfig",
    "build_treasure_chest",
    "build_seeded_treasure_chest",
    "config_from_seed",
    "resolve_config",
    "run_treasure_chest_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
