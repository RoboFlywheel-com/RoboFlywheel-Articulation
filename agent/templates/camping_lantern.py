# SPDX-License-Identifier: Apache-2.0

"""Camping lantern modular template (battery/LED portable area light).

A grounded ``lower_base`` (canister / ground-stake / magnetic-disc / fold-out
tripod) carries a light-chamber ``upper_lantern`` (the ③ Primary Form Family:
clear cylinder chamber / wire-cage diffuser / barn globe / orb globe / box panel
fixture / flat puck / slim tube), seated or telescoped on the base, plus one
swinging ``carry_handle`` grip (fold-up bail / top J-hook / side loop). Two
optional multiplicity axes: N fold-out legs (tripod) and N cage guard bars
(cage_diffuser).

pattern = ``mixed``: base→body seat/slide chain + parallel-children grip + leg /
cage-bar multiplicity — cushion.py / Light_Latern.py style (no assemble() chain,
manual joints with MatingContract on the seat and grandfathered captured-pin
grip/leg pivots).

Non-FIXED joints (motion identity):
  * ``base_to_lantern`` PRISMATIC z when base=canister_telescope (else FIXED seat);
  * ``lantern_to_grip`` REVOLUTE (bail x / hook y / side-loop x), captured-pin;
  * ``base_to_leg_i`` REVOLUTE (tripod only), captured-pin.

Sourced from ``articraft_template_authoring/specs_modular_v1/camping_lantern.md``
and the 16-record 5-star pool (2 origin anchors 9f7633a6 + c2bd28cb, 14 forks).
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
    Cylinder,
    Inertial,
    LatheGeometry,
    MatingContract,
    MeshGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

TAU = 2.0 * math.pi

BaseStyle = Literal[
    "canister_telescope", "canister_seat", "ground_stake", "magnetic_disc", "tripod"
]
BodyStyle = Literal[
    "cylinder_chamber",
    "cage_diffuser",
    "barn_globe",
    "orb_globe",
    "box_panel",
    "puck_disc",
    "slim_tube",
]
GripStyle = Literal["fold_bail", "top_hook", "side_loop"]
PaletteStyle = Literal[
    "graphite_black",
    "olive_steel",
    "vintage_brass",
    "frosted_white",
    "sand_tan",
    "anodized_orange",
]

BASE_STYLES: tuple[BaseStyle, ...] = (
    "canister_telescope",
    "canister_seat",
    "ground_stake",
    "magnetic_disc",
    "tripod",
)
BODY_STYLES: tuple[BodyStyle, ...] = (
    "cylinder_chamber",
    "cage_diffuser",
    "barn_globe",
    "orb_globe",
    "box_panel",
    "puck_disc",
    "slim_tube",
)
GRIP_STYLES: tuple[GripStyle, ...] = ("fold_bail", "top_hook", "side_loop")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "graphite_black",
    "olive_steel",
    "vintage_brass",
    "frosted_white",
    "sand_tan",
    "anodized_orange",
)

LEG_N_CHOICES = (3, 4)
LEG_N_WEIGHTS = (0.72, 0.28)
CAGE_N_CHOICES = (8, 10, 12, 14, 16)
CAGE_N_WEIGHTS = (0.30, 0.24, 0.22, 0.14, 0.10)
LEG_MIN, LEG_MAX = 3, 4
CAGE_MIN, CAGE_MAX = 8, 16

# Realistic camping-lantern colorways drawn across the 5-star pool. Every
# `.visual(material=...)` is driven off one of these (mats[...]). `diffuser` is
# always translucent (alpha < 0.5) so the glowing chamber reads through.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "graphite_black": {  # 9f7633a6 canister origin
        "shell": (0.02, 0.02, 0.02, 1.0),
        "dark": (0.05, 0.05, 0.05, 1.0),
        "accent": (0.82, 0.86, 0.86, 1.0),
        "diffuser": (0.70, 0.92, 1.0, 0.32),
        "led": (1.0, 0.86, 0.42, 1.0),
        "fastener": (0.72, 0.74, 0.72, 1.0),
    },
    "olive_steel": {  # c2bd28cb tripod origin
        "shell": (0.30, 0.35, 0.31, 1.0),
        "dark": (0.05, 0.06, 0.05, 1.0),
        "accent": (0.10, 0.11, 0.10, 1.0),
        "diffuser": (1.0, 0.54, 0.08, 0.34),
        "led": (1.0, 0.73, 0.20, 0.92),
        "fastener": (0.90, 0.90, 0.85, 1.0),
    },
    "vintage_brass": {  # barn globe fork
        "shell": (0.62, 0.45, 0.14, 1.0),
        "dark": (0.42, 0.31, 0.15, 1.0),
        "accent": (0.55, 0.36, 0.16, 1.0),
        "diffuser": (1.0, 0.60, 0.14, 0.34),
        "led": (1.0, 0.73, 0.20, 0.92),
        "fastener": (0.86, 0.80, 0.55, 1.0),
    },
    "frosted_white": {  # orb globe fork
        "shell": (0.88, 0.88, 0.86, 1.0),
        "dark": (0.30, 0.30, 0.32, 1.0),
        "accent": (0.78, 0.80, 0.82, 1.0),
        "diffuser": (0.92, 0.90, 0.85, 0.46),
        "led": (1.0, 0.88, 0.50, 1.0),
        "fastener": (0.72, 0.74, 0.72, 1.0),
    },
    "sand_tan": {  # box fixture fork
        "shell": (0.76, 0.70, 0.55, 1.0),
        "dark": (0.45, 0.40, 0.32, 1.0),
        "accent": (0.24, 0.23, 0.20, 1.0),
        "diffuser": (1.0, 0.82, 0.45, 0.40),
        "led": (1.0, 0.73, 0.20, 0.92),
        "fastener": (0.90, 0.90, 0.85, 1.0),
    },
    "anodized_orange": {  # hook / magnetic-clip fork accent
        "shell": (0.13, 0.13, 0.14, 1.0),
        "dark": (0.04, 0.04, 0.04, 1.0),
        "accent": (0.93, 0.39, 0.07, 1.0),
        "diffuser": (0.70, 0.92, 1.0, 0.34),
        "led": (1.0, 0.86, 0.42, 1.0),
        "fastener": (0.72, 0.74, 0.72, 1.0),
    },
}

SEG = 64  # revolved-shell tessellation (compile budget §7.5)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(v, choices):
    return v if v in choices else choices[0]


# --------------------------------------------------------------- body nominals
# Per-body seat-relative datums (before scale). Seat plane = z 0, body extends +z.
#   cap_apex: highest solid cap point (grip mounts just above it so a folding
#     bail/hook always clears the body) ; seat_r: seat ring radius ;
#   max_r: widest radius ; side_wall/side_z: side_loop sidewall (true wall
#   radius + mount height) ; box: flat (planar) sidewall rather than round.
_BODY_NOMINAL: dict[BodyStyle, dict[str, float]] = {
    "cylinder_chamber": {"cap_apex": 0.165, "seat_r": 0.052, "max_r": 0.062, "side_wall": 0.052, "side_z": 0.090, "box": 0.0},
    "cage_diffuser": {"cap_apex": 0.187, "seat_r": 0.044, "max_r": 0.055, "side_wall": 0.032, "side_z": 0.090, "box": 0.0},
    "barn_globe": {"cap_apex": 0.187, "seat_r": 0.044, "max_r": 0.064, "side_wall": 0.060, "side_z": 0.098, "box": 0.0},
    "orb_globe": {"cap_apex": 0.165, "seat_r": 0.052, "max_r": 0.058, "side_wall": 0.056, "side_z": 0.076, "box": 0.0},
    "box_panel": {"cap_apex": 0.180, "seat_r": 0.050, "max_r": 0.060, "side_wall": 0.036, "side_z": 0.075, "box": 1.0},
    "puck_disc": {"cap_apex": 0.040, "seat_r": 0.078, "max_r": 0.082, "side_wall": 0.082, "side_z": 0.015, "box": 0.0},
    "slim_tube": {"cap_apex": 0.266, "seat_r": 0.024, "max_r": 0.028, "side_wall": 0.021, "side_z": 0.120, "box": 0.0},
}

# Per-base nominal top-seat height (before base_height_scale).
_BASE_TOP_NOMINAL: dict[BaseStyle, float] = {
    "canister_telescope": 0.105,
    "canister_seat": 0.105,
    "ground_stake": 0.038,
    "magnetic_disc": 0.020,
    "tripod": 0.052,
}

# Per-base seat-rim radius: sized to reliably overlap the base shell so the rim
# (the mating face) is not an island. Independent of the body seat radius.
_BASE_RIM_R: dict[BaseStyle, float] = {
    "canister_telescope": 0.056,
    "canister_seat": 0.056,
    "ground_stake": 0.030,
    "magnetic_disc": 0.052,
    "tripod": 0.030,
}


# =================================================================== config
@dataclass(frozen=True)
class CampingLanternConfig:
    base_style: BaseStyle | None = None
    body_style: BodyStyle | None = None
    grip_style: GripStyle | None = None
    palette_style: PaletteStyle = "graphite_black"
    leg_count: int | None = None
    cage_bar_count: int | None = None
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    base_height_scale: float = 1.0
    name: str = "camping_lantern"


@dataclass(frozen=True)
class ResolvedCampingLanternConfig:
    base_style: BaseStyle
    body_style: BodyStyle
    grip_style: GripStyle
    palette_style: PaletteStyle
    leg_count: int  # 0 == no legs
    cage_bar_count: int  # 0 == no cage bars
    body_height_scale: float
    body_radius_scale: float
    base_height_scale: float
    # derived, single-sourced datums (Contract 3c)
    base_top_z: float
    body_top_z: float
    body_seat_r: float
    body_max_r: float
    body_side_wall: float
    body_side_z: float
    body_is_box: bool
    prismatic: bool
    name: str


def config_from_seed(seed: int) -> CampingLanternConfig:
    rng = random.Random(seed)
    return CampingLanternConfig(
        base_style=rng.choice(BASE_STYLES),
        body_style=rng.choice(BODY_STYLES),
        grip_style=rng.choice(GRIP_STYLES),
        palette_style=rng.choice(PALETTE_STYLES),
        leg_count=rng.choices(LEG_N_CHOICES, weights=LEG_N_WEIGHTS, k=1)[0],
        cage_bar_count=rng.choices(CAGE_N_CHOICES, weights=CAGE_N_WEIGHTS, k=1)[0],
        body_height_scale=round(rng.uniform(0.88, 1.15), 4),
        body_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        base_height_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_camping_lantern_{seed}",
    )


def resolve_config(
    config: CampingLanternConfig | None = None,
) -> ResolvedCampingLanternConfig:
    cfg = config or CampingLanternConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)
    base_style = _pick(cfg.base_style, BASE_STYLES)
    body_style = _pick(cfg.body_style, BODY_STYLES)
    grip_style = _pick(cfg.grip_style, GRIP_STYLES)

    hs = _clamp(cfg.body_height_scale, 0.88, 1.15)
    rs = _clamp(cfg.body_radius_scale, 0.90, 1.12)
    bhs = _clamp(cfg.base_height_scale, 0.85, 1.15)

    # --- Compatibility gating (spec §9) ---
    # Square box body cannot slide a round canister bore -> demote to seat.
    if base_style == "canister_telescope" and body_style == "box_panel":
        base_style = "canister_seat"
    # Side loop needs a solid continuous sidewall: flat puck has none, and the
    # wire cage's gapped bars give no reliable boss seat -> use the top bail.
    if grip_style == "side_loop" and body_style in ("puck_disc", "cage_diffuser"):
        grip_style = "fold_bail"

    leg_count = 0
    if base_style == "tripod":
        raw = int(cfg.leg_count) if cfg.leg_count is not None else 3
        leg_count = int(_clamp(raw, LEG_MIN, LEG_MAX))
    cage_bar_count = 0
    if body_style == "cage_diffuser":
        raw = int(cfg.cage_bar_count) if cfg.cage_bar_count is not None else 8
        cage_bar_count = int(_clamp(raw, CAGE_MIN, CAGE_MAX))

    nom = _BODY_NOMINAL[body_style]
    # The magnetic disc is a fixed standardized puck (unscaled height); every
    # other base scales its height by base_height_scale.
    base_top_z = (
        _BASE_TOP_NOMINAL[base_style]
        if base_style == "magnetic_disc"
        else _BASE_TOP_NOMINAL[base_style] * bhs
    )

    return ResolvedCampingLanternConfig(
        base_style=base_style,
        body_style=body_style,
        grip_style=grip_style,
        palette_style=palette_style,
        leg_count=leg_count,
        cage_bar_count=cage_bar_count,
        body_height_scale=hs,
        body_radius_scale=rs,
        base_height_scale=bhs,
        base_top_z=base_top_z,
        body_top_z=nom["cap_apex"] * hs + 0.004,
        body_seat_r=nom["seat_r"] * rs,
        body_max_r=nom["max_r"] * rs,
        body_side_wall=nom["side_wall"] * rs,
        body_side_z=nom["side_z"] * hs,
        body_is_box=bool(nom["box"]),
        prismatic=(base_style == "canister_telescope"),
        name=cfg.name or "camping_lantern",
    )


def with_overrides(config: CampingLanternConfig, **kw: object) -> CampingLanternConfig:
    return replace(config, **kw)


def slot_choices_for_config(
    config: CampingLanternConfig | ResolvedCampingLanternConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCampingLanternConfig) else resolve_config(config)
    out: list[tuple[str, str]] = [
        ("base", r.base_style),
        ("body", r.body_style),
        ("grip", r.grip_style),
    ]
    if r.leg_count:
        out.append(("legs", f"n{r.leg_count}"))
    if r.cage_bar_count:
        out.append(("cage_bars", f"n{r.cage_bar_count}"))
    return tuple(out)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# =================================================================== mesh helpers
def _shell(name: str, outer, inner, *, segments: int = SEG):
    """Thin-walled revolved shell with visible lips/ridges (source _ring_profile_mesh)."""
    return mesh_from_geometry(
        LatheGeometry.from_shell_profiles(
            outer, inner, segments=segments, start_cap="flat", end_cap="flat", lip_samples=4
        ),
        name,
    )


def _solid(name: str, profile, *, segments: int = SEG):
    return mesh_from_geometry(LatheGeometry(profile, segments=segments, closed=True), name)


def _cage_mesh(n_bars: int, radius: float, z_breaks: list[float]) -> MeshGeometry:
    """Connected cylindrical guard lattice (c2bd28cb _lantern_cage_mesh), N bars."""
    cage = MeshGeometry()
    n = 72
    verts: dict[tuple[int, int], int] = {}
    n_z = len(z_breaks)

    def vid(ai: int, zi: int) -> int:
        key = (ai % n, zi)
        if key not in verts:
            a = TAU * (ai % n) / n
            verts[key] = cage.add_vertex(radius * math.cos(a), radius * math.sin(a), z_breaks[zi])
        return verts[key]

    def in_bar(ai: int) -> bool:
        for bar in range(n_bars):
            center = int(round(n * bar / n_bars))
            delta = min((ai - center) % n, (center - ai) % n)
            if delta <= 1:
                return True
        return False

    band_zi = {0, n_z // 2 - 1, n_z - 2}

    for ai in range(n):
        for zi in range(n_z - 1):
            if zi in band_zi or in_bar(ai):
                a0, a1 = vid(ai, zi), vid(ai + 1, zi)
                b0, b1 = vid(ai, zi + 1), vid(ai + 1, zi + 1)
                cage.add_face(a0, a1, b1)
                cage.add_face(a0, b1, b0)
    return cage


def _bail_wire(span: float, rise: float) -> MeshGeometry:
    p = [
        (-span, 0.0, 0.000),
        (-span * 0.98, 0.0, rise * 0.34),
        (-span * 0.79, 0.0, rise * 0.77),
        (-span * 0.36, 0.0, rise * 0.97),
        (0.000, 0.0, rise),
        (span * 0.36, 0.0, rise * 0.97),
        (span * 0.79, 0.0, rise * 0.77),
        (span * 0.98, 0.0, rise * 0.34),
        (span, 0.0, 0.000),
    ]
    return tube_from_spline_points(
        p, radius=0.0022, samples_per_segment=10, radial_segments=14, cap_ends=True
    )


def _hook_wire() -> MeshGeometry:
    p = [
        (0.000, 0.0, 0.000),
        (0.000, 0.0, 0.016),
        (0.001, 0.0, 0.034),
        (0.005, 0.0, 0.048),
        (0.012, 0.0, 0.053),
        (0.019, 0.0, 0.048),
        (0.022, 0.0, 0.036),
        (0.021, 0.0, 0.026),
    ]
    return tube_from_spline_points(
        p, radius=0.0025, samples_per_segment=12, radial_segments=14, cap_ends=True
    )


def _side_loop_wire(y: float, drop: float) -> MeshGeometry:
    p = [
        (-0.020, 0.000, 0.000),
        (-0.023, y * 0.44, -drop * 0.35),
        (-0.022, y * 0.79, -drop * 0.72),
        (-0.015, y * 0.94, -drop * 0.91),
        (0.000, y, -drop),
        (0.015, y * 0.94, -drop * 0.91),
        (0.022, y * 0.79, -drop * 0.72),
        (0.023, y * 0.44, -drop * 0.35),
        (0.020, 0.000, 0.000),
    ]
    return tube_from_spline_points(
        p, radius=0.0022, samples_per_segment=12, radial_segments=14, cap_ends=True
    )


def _leg_mesh() -> MeshGeometry:
    leg = tube_from_spline_points(
        [
            (0.004, 0.0, -0.002),
            (0.018, 0.0, -0.056),
            (0.039, 0.0, -0.111),
            (0.059, 0.0, -0.153),
        ],
        radius=0.0022,
        samples_per_segment=10,
        radial_segments=12,
        cap_ends=True,
    )
    return leg


# =================================================================== base modules
def _emit_base(model, r: ResolvedCampingLanternConfig, mats) -> object:
    """Slot A: grounded lower_base + (tripod) fold-out legs. Emits `body_seat_rim`."""
    base = model.part("lower_base")
    bhs = r.base_height_scale
    top_z = r.base_top_z

    if r.base_style in ("canister_telescope", "canister_seat"):
        _emit_canister(base, bhs, mats)
    elif r.base_style == "ground_stake":
        _emit_stake(base, bhs, mats)
    elif r.base_style == "magnetic_disc":
        _emit_magnetic_disc(base, mats)
    else:  # tripod
        _emit_tripod_hub(base, bhs, mats)

    # Shared mating rim: flat disc whose +z face sits exactly at base_top_z; it
    # extends downward into the base shell so it is anchored (not an island).
    base.visual(
        Cylinder(radius=_BASE_RIM_R[r.base_style], length=0.014),
        origin=Origin(xyz=(0.0, 0.0, top_z - 0.007)),
        material=mats["dark"],
        name="body_seat_rim", material_class_id="metal.paint_coated",
    )

    base.inertial = Inertial.from_geometry(
        Cylinder(radius=0.06, length=max(0.04, top_z)),
        mass=0.35,
        origin=Origin(xyz=(0.0, 0.0, top_z * 0.5)),
    )

    if r.base_style == "tripod":
        _emit_legs(model, base, r, mats)
    return base


def _emit_canister(base, bhs: float, mats) -> None:
    """Ribbed sitting canister (9f7633a6 L67-L120), height scaled by bhs."""
    outer = [(x, z * bhs) for (x, z) in [
        (0.056, 0.000), (0.064, 0.006), (0.064, 0.017), (0.059, 0.023),
        (0.059, 0.035), (0.062, 0.039), (0.062, 0.045), (0.058, 0.049),
        (0.058, 0.085), (0.062, 0.090), (0.062, 0.100), (0.058, 0.105),
    ]]
    inner = [(x, z * bhs) for (x, z) in [
        (0.047, 0.006), (0.052, 0.014), (0.054, 0.095), (0.054, 0.105),
    ]]
    base.visual(_shell("ribbed_base_shell", outer, inner), material=mats["shell"], name="base_shell", material_class_id="metal.paint_coated")
    for i in range(18):
        ang = TAU * i / 18
        base.visual(
            Box((0.006, 0.010, 0.047 * bhs)),
            origin=Origin(xyz=(0.0625 * math.cos(ang), 0.0625 * math.sin(ang), 0.054 * bhs), rpy=(0.0, 0.0, ang)),
            material=mats["dark"],
            name=f"base_rib_{i}", material_class_id="metal.paint_coated",
        )
    for i in range(18):
        ang = TAU * (i + 0.5) / 18
        base.visual(
            Box((0.007, 0.014, 0.015)),
            origin=Origin(xyz=(0.062 * math.cos(ang), 0.062 * math.sin(ang), 0.008), rpy=(0.0, 0.0, ang)),
            material=mats["dark"],
            name=f"foot_lug_{i}", material_class_id="rubber.smooth_plain",
        )


def _emit_stake(base, bhs: float, mats) -> None:
    """Ground-stake spike + hub + seating flange (ground_stake fork L77-L101)."""
    spike_len = 0.180
    hub_h = 0.038 * bhs
    base.visual(
        _solid("ground_stake_spike", [
            (0.001, -spike_len), (0.003, -spike_len + 0.012), (0.006, -spike_len + 0.040),
            (0.009, -spike_len + 0.080), (0.012, -spike_len + 0.120), (0.015, -0.040),
            (0.019, -0.020), (0.023, -0.006), (0.023, hub_h - 0.010),
            (0.040, hub_h - 0.005), (0.040, hub_h), (0.000, hub_h),
        ]),
        material=mats["accent"],
        name="base_shell", material_class_id="metal.steel_galvanized",
    )


def _emit_magnetic_disc(base, mats) -> None:
    """Thin magnetic puck disc + contact ring + anti-slip pad (magnetic fork L76-L134)."""
    dh, dr = 0.020, 0.054
    base.visual(
        _solid("magnetic_puck_disc", [
            (0.000, 0.000), (dr, 0.000), (dr + 0.002, 0.003), (dr + 0.002, 0.017),
            (dr, dh), (0.050, dh), (0.050, 0.006), (0.000, 0.006),
        ]),
        material=mats["shell"],
        name="base_shell", material_class_id="metal.paint_coated",
    )
    base.visual(
        _solid("magnetic_contact_ring", [
            (0.012, -0.001), (0.044, -0.001), (0.044, 0.000), (0.012, 0.000)
        ], segments=48),
        material=mats["fastener"],
        name="magnet_ring", material_class_id="metal.stainless_matte",
    )
    for i in range(24):
        ang = TAU * i / 24
        base.visual(
            Box((0.004, 0.006, 0.010)),
            origin=Origin(xyz=((dr + 0.0025) * math.cos(ang), (dr + 0.0025) * math.sin(ang), 0.010), rpy=(0.0, 0.0, ang)),
            material=mats["dark"],
            name=f"disc_grip_{i}", material_class_id="rubber.pebbled",
        )


def _emit_tripod_hub(base, bhs: float, mats) -> None:
    """Slim vented hub the body seats on; legs fold from OUTSIDE it (c2bd28cb hub).

    Kept narrow (max r ~0.033) so the fold-out leg wires at socket radius ~0.036
    clear the hub shell instead of piercing it.
    """
    hub_top = 0.052 * bhs
    base.visual(
        _solid("vented_hub", [
            (0.000, 0.000), (0.030, 0.000), (0.033, 0.008 * bhs), (0.031, 0.024 * bhs),
            (0.026, 0.040 * bhs), (0.018, hub_top - 0.004), (0.012, hub_top), (0.000, hub_top),
        ]),
        material=mats["shell"],
        name="base_shell", material_class_id="metal.paint_coated",
    )


def _emit_legs(model, base, r: ResolvedCampingLanternConfig, mats) -> None:
    """Leg multiplicity axis: N fold-out wire legs, REVOLUTE children of the hub."""
    n = r.leg_count
    socket_r = 0.036
    hinge_z = 0.020 * r.base_height_scale
    leg_mesh = _leg_mesh()
    for i in range(n):
        ang = TAU * i / n + math.pi / 6.0
        x, y = socket_r * math.cos(ang), socket_r * math.sin(ang)
        base.visual(
            Box((0.016, 0.010, 0.010)),
            origin=Origin(xyz=(x, y, hinge_z), rpy=(0.0, 0.0, ang)),
            material=mats["accent"],
            name=f"leg_socket_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"graphite_black", "vintage_brass", "frosted_white", "anodized_orange"} else "metal.blackened_gunmetal"),
        )
        leg = model.part(f"leg_{i}")
        leg.visual(
            mesh_from_geometry(leg_mesh.copy(), f"foldout_leg_{i}"),
            material=mats["accent"],
            name="leg_wire", material_class_id=("metal.stainless_matte" if r.palette_style in {"graphite_black", "vintage_brass", "frosted_white", "anodized_orange"} else "metal.blackened_gunmetal"),
        )
        leg.visual(
            Cylinder(radius=0.004, length=0.017),
            origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"],
            name="hinge_pin", material_class_id=("metal.stainless_matte" if r.palette_style in {"graphite_black", "vintage_brass", "frosted_white", "anodized_orange"} else "metal.blackened_gunmetal"),
        )
        leg.inertial = Inertial.from_geometry(
            Box((0.06, 0.02, 0.16)), mass=0.03, origin=Origin(xyz=(0.03, 0.0, -0.08))
        )
        model.articulation(
            f"base_to_leg_{i}",
            ArticulationType.REVOLUTE,
            parent=base,
            child=leg,
            origin=Origin(xyz=(x, y, hinge_z), rpy=(0.0, 0.0, ang)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=1.25),
        )


# =================================================================== body modules
def _emit_led_core(part, r, mats, *, z_top: float) -> None:
    """Warm LED strip on a central spine anchored to the `body_seat` disc.

    Spans z 0.002 (overlapping the solid body_seat) up to ``z_top`` (into the cap
    region) so the assembly is never a floating island. Lens dots embed in the
    board's front face.
    """
    z0 = 0.002
    span = z_top - z0
    cz = (z0 + z_top) / 2.0
    part.visual(
        Box((0.030 * r.body_radius_scale, 0.010, span)),
        origin=Origin(xyz=(0.0, -0.010, cz)),
        material=mats["fastener"],
        name="led_board", material_class_id="tech.circuit_board",
    )
    part.visual(
        Box((0.020 * r.body_radius_scale, 0.012, span)),
        origin=Origin(xyz=(0.0, -0.002, cz)),
        material=mats["led"],
        name="inner_reflector", material_class_id="tech.emissive_surface",
    )
    rows = max(3, int(round(span / 0.024)))
    for row in range(rows):
        z = z0 + 0.008 + row * (span - 0.016) / max(1, rows - 1)
        for col, x in enumerate((-0.008, 0.008)):
            part.visual(
                Cylinder(radius=0.0038, length=0.0025),
                origin=Origin(xyz=(x, -0.012, z), rpy=(math.pi / 2, 0.0, 0.0)),
                material=mats["led"],
                name=f"led_lens_{row}_{col}", material_class_id="tech.emissive_surface",
            )


def _emit_body(model, r: ResolvedCampingLanternConfig, mats) -> object:
    body = model.part("upper_lantern")

    # Shared seat disc: -z face at part z=0 -> world base_top_z (MatingContract
    # child). Radius is generous so it catches every body's lower collar / base
    # rim AND the central LED spine, giving one solid anchor for the whole part.
    body.visual(
        Cylinder(radius=r.body_max_r + 0.006, length=0.004),
        origin=Origin(xyz=(0.0, 0.0, 0.002)),
        material=mats["dark"],
        name="body_seat", material_class_id="metal.paint_coated",
    )

    bs = r.body_style
    if bs == "cylinder_chamber":
        _body_cylinder(body, r, mats)
    elif bs == "cage_diffuser":
        _body_cage(body, r, mats)
    elif bs == "barn_globe":
        _body_barn(body, r, mats)
    elif bs == "orb_globe":
        _body_orb(body, r, mats)
    elif bs == "box_panel":
        _body_box(body, r, mats)
    elif bs == "puck_disc":
        _body_puck(body, r, mats)
    else:  # slim_tube
        _body_slim(body, r, mats)

    body.inertial = Inertial.from_geometry(
        Cylinder(radius=max(0.03, r.body_max_r), length=max(0.04, r.body_top_z)),
        mass=0.30,
        origin=Origin(xyz=(0.0, 0.0, r.body_top_z * 0.5)),
    )
    return body


def _cap_tabs(body, r, mats, *, z: float, radius: float) -> None:
    """Host-conformal cap tabs hugging the cap radius (④, derived from ③/⑤ surface)."""
    for i in range(6):
        ang = TAU * i / 6
        body.visual(
            Box((0.020, 0.024, 0.016)),
            origin=Origin(xyz=(radius * math.cos(ang), radius * math.sin(ang), z), rpy=(0.0, 0.0, ang)),
            material=mats["dark"],
            name=f"cap_tab_{i}", material_class_id="metal.paint_coated",
        )


def _body_cylinder(body, r, mats) -> None:
    hs, rs = r.body_height_scale, r.body_radius_scale
    def s(x, z):
        return (x * rs, z * hs)
    body.visual(
        _shell("lower_collar", [s(0.051, 0.000), s(0.060, 0.004), s(0.060, 0.015), s(0.052, 0.019)],
               [s(0.042, 0.000), s(0.045, 0.019)]),
        material=mats["shell"], name="lower_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        _solid("clear_chamber_tube", [s(0.052, 0.015), s(0.052, 0.137), s(0.049, 0.137), s(0.049, 0.015)]),
        material=mats["diffuser"], name="clear_chamber", material_class_id="plastic.frosted_translucent",
    )
    for i in range(4):
        ang = TAU * i / 4 + math.pi / 4
        body.visual(
            Box((0.006, 0.004, 0.118 * hs)),
            origin=Origin(xyz=(0.0525 * rs * math.cos(ang), 0.0525 * rs * math.sin(ang), 0.077 * hs), rpy=(0.0, 0.0, ang)),
            material=mats["diffuser"], name=f"clear_post_{i}", material_class_id="plastic.frosted_translucent",
        )
    _emit_led_core(body, r, mats, z_top=max(0.134 * hs, r.body_top_z))
    body.visual(
        _shell("top_cap", [s(0.052, 0.132), s(0.061, 0.138), s(0.061, 0.154), s(0.057, 0.160), s(0.048, 0.165)],
               [s(0.020, 0.132), s(0.020, 0.162), s(0.000, 0.165)]),
        material=mats["shell"], name="top_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    _cap_tabs(body, r, mats, z=0.149 * hs, radius=0.057 * rs)


def _body_orb(body, r, mats) -> None:
    hs, rs = r.body_height_scale, r.body_radius_scale
    def s(x, z):
        return (x * rs, z * hs)
    orb_r = 0.058 * min(rs, hs)
    orb_cz = 0.076 * hs
    body.visual(
        _shell("lower_collar", [s(0.056, 0.000), s(0.060, 0.004), s(0.060, 0.015), s(0.052, 0.019), s(0.052, 0.032)],
               [s(0.050, 0.000), s(0.045, 0.019), s(0.036, 0.032)]),
        material=mats["shell"], name="lower_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        Sphere(radius=orb_r), origin=Origin(xyz=(0.0, 0.0, orb_cz)),
        material=mats["diffuser"], name="clear_chamber", material_class_id="plastic.frosted_translucent",
    )
    _emit_led_core(body, r, mats, z_top=max(0.124 * hs, r.body_top_z))
    body.visual(
        _shell("top_cap", [s(0.052, 0.120), s(0.052, 0.132), s(0.061, 0.138), s(0.061, 0.154), s(0.057, 0.160), s(0.048, 0.165)],
               [s(0.036, 0.120), s(0.020, 0.132), s(0.020, 0.162), s(0.000, 0.165)]),
        material=mats["shell"], name="top_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    _cap_tabs(body, r, mats, z=0.149 * hs, radius=0.058 * rs)


def _body_slim(body, r, mats) -> None:
    hs, rs = r.body_height_scale, r.body_radius_scale
    def s(x, z):
        return (x * rs, z * hs)
    body.visual(
        _shell("lower_collar", [s(0.023, 0.000), s(0.028, 0.004), s(0.028, 0.012), s(0.024, 0.016)],
               [s(0.019, 0.000), s(0.020, 0.016)]),
        material=mats["shell"], name="lower_collar", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        _solid("slim_tube_chamber", [s(0.022, 0.016), s(0.022, 0.236), s(0.019, 0.236), s(0.019, 0.016)]),
        material=mats["diffuser"], name="clear_chamber", material_class_id="plastic.frosted_translucent",
    )
    # Carrier spine from body_seat (z~0) to the cap so the LED strip is anchored.
    body.visual(
        Box((0.032 * rs, 0.006, 0.244 * hs)),
        origin=Origin(xyz=(0.0, 0.0, 0.122 * hs)),
        material=mats["fastener"], name="carrier_spine", material_class_id="metal.aluminum_bare",
    )
    for row in range(8):
        z = (0.028 + row * 0.026) * hs
        for col, x in enumerate((-0.004, 0.004)):
            body.visual(
                Cylinder(radius=0.0030, length=0.002),
                origin=Origin(xyz=(x * rs, -0.004, z), rpy=(math.pi / 2, 0.0, 0.0)),
                material=mats["led"], name=f"led_lens_{row}_{col}", material_class_id="tech.emissive_surface",
            )
    body.visual(
        _shell("top_cap", [s(0.022, 0.236), s(0.027, 0.241), s(0.027, 0.256), s(0.024, 0.262), s(0.018, 0.266)],
               [s(0.010, 0.236), s(0.010, 0.263), s(0.000, 0.266)]),
        material=mats["shell"], name="top_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    _cap_tabs(body, r, mats, z=0.249 * hs, radius=0.025 * rs)


def _body_puck(body, r, mats) -> None:
    hs, rs = r.body_height_scale, r.body_radius_scale
    def s(x, z):
        return (x * rs, z * hs)
    body.visual(
        _shell("puck_shell", [s(0.076, 0.000), s(0.082, 0.004), s(0.082, 0.020), s(0.076, 0.030)],
               [s(0.070, 0.004), s(0.070, 0.020), s(0.020, 0.030)]),
        material=mats["shell"], name="puck_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        _solid("diffuser_disc", [s(0.010, 0.001), s(0.070, 0.001), s(0.070, 0.006), s(0.010, 0.006)]),
        material=mats["diffuser"], name="clear_chamber", material_class_id="plastic.frosted_translucent",
    )
    body.visual(
        Cylinder(radius=0.058 * rs, length=0.002),
        origin=Origin(xyz=(0.0, 0.0, 0.004 * hs)),
        material=mats["led"], name="cob_phosphor", material_class_id="tech.emissive_surface",
    )
    body.visual(
        Cylinder(radius=0.070 * rs, length=0.003),
        origin=Origin(xyz=(0.0, 0.0, 0.009 * hs)),
        material=mats["fastener"], name="led_board", material_class_id="tech.circuit_board",
    )
    body.visual(
        _shell("top_cap", [s(0.048, 0.025), s(0.055, 0.028), s(0.055, 0.032), s(0.050, 0.035), s(0.042, 0.038)],
               [s(0.018, 0.025), s(0.018, 0.035), s(0.000, 0.038)]),
        material=mats["shell"], name="top_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )


def _body_barn(body, r, mats) -> None:
    hs, rs = r.body_height_scale, r.body_radius_scale
    def s(x, z):
        return (x * rs, z * hs)
    # Vented base fused to the body (bottom seat region).
    body.visual(
        _solid("vented_base", [s(0.000, 0.000), s(0.044, 0.000), s(0.052, 0.006), s(0.050, 0.016),
                               s(0.037, 0.024), s(0.032, 0.029), s(0.021, 0.032), s(0.000, 0.032)]),
        material=mats["shell"], name="vented_base", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    # Bulged barn/hurricane glass globe (barn fork _barn_globe_mesh, re-origined -0.02).
    body.visual(
        _solid("barn_globe", [
            s(0.000, 0.032), s(0.028, 0.032), s(0.034, 0.040), s(0.044, 0.054), s(0.054, 0.072),
            s(0.061, 0.088), s(0.064, 0.098), s(0.063, 0.112), s(0.056, 0.128), s(0.046, 0.142),
            s(0.036, 0.152), s(0.028, 0.156), s(0.000, 0.156),
        ]),
        material=mats["diffuser"], name="clear_chamber", material_class_id="plastic.frosted_translucent",
    )
    # Warm LED core from body_seat (z~0) up to the grip mount (no island).
    body.visual(
        Cylinder(radius=0.020 * rs, length=0.174 * hs),
        origin=Origin(xyz=(0.0, 0.0, 0.089 * hs)),
        material=mats["led"], name="led_column", material_class_id="tech.emissive_surface",
    )
    body.visual(
        _solid("top_vent_cap", [s(0.000, 0.156), s(0.053, 0.156), s(0.063, 0.161), s(0.062, 0.170),
                               s(0.053, 0.175), s(0.026, 0.175), s(0.018, 0.178), s(0.018, 0.183),
                               s(0.013, 0.187), s(0.000, 0.187)]),
        material=mats["shell"], name="top_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    # Control block on the cap shoulder, kept below the grip mount.
    body.visual(
        Box((0.068 * rs, 0.030, 0.014)),
        origin=Origin(xyz=(0.0, -0.004, 0.166 * hs)),
        material=mats["shell"], name="top_control_block", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        Box((0.047 * rs, 0.004, 0.0012)),
        origin=Origin(xyz=(0.0, -0.020, 0.1735 * hs)),
        material=mats["fastener"], name="brand_stroke", material_class_id="metal.paint_coated",
    )


def _body_cage(body, r, mats) -> None:
    hs, rs = r.body_height_scale, r.body_radius_scale
    def s(x, z):
        return (x * rs, z * hs)
    body.visual(
        _solid("vented_base", [s(0.000, 0.000), s(0.044, 0.000), s(0.052, 0.006), s(0.050, 0.016),
                               s(0.037, 0.024), s(0.032, 0.029), s(0.021, 0.032), s(0.000, 0.032)]),
        material=mats["shell"], name="vented_base", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    # Solid diffuser + LED core, both spanning from the body_seat disc up to the
    # grip mount so the cage body is a single connected part (no island).
    body.visual(
        Cylinder(radius=0.032 * rs, length=0.163 * hs),
        origin=Origin(xyz=(0.0, 0.0, 0.0815 * hs)),
        material=mats["diffuser"], name="clear_chamber", material_class_id="plastic.frosted_translucent",
    )
    body.visual(
        Cylinder(radius=0.020 * rs, length=0.174 * hs),
        origin=Origin(xyz=(0.0, 0.0, 0.089 * hs)),
        material=mats["led"], name="led_column", material_class_id="tech.emissive_surface",
    )
    z_breaks = [z * hs for z in (0.018, 0.024, 0.030, 0.087, 0.097, 0.151, 0.161, 0.167)]
    body.visual(
        mesh_from_geometry(_cage_mesh(r.cage_bar_count, 0.055 * rs, z_breaks), "cage_lattice"),
        material=mats["accent"], name="cage_lattice", material_class_id=("metal.stainless_matte" if r.palette_style in {"graphite_black", "vintage_brass", "frosted_white", "anodized_orange"} else "metal.blackened_gunmetal"),
    )
    body.visual(
        _solid("top_vent_cap", [s(0.000, 0.156), s(0.053, 0.156), s(0.063, 0.161), s(0.062, 0.170),
                               s(0.053, 0.175), s(0.026, 0.175), s(0.018, 0.178), s(0.018, 0.183),
                               s(0.013, 0.187), s(0.000, 0.187)]),
        material=mats["shell"], name="top_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    # Control block on the cap shoulder, kept below the grip mount.
    body.visual(
        Box((0.068 * rs, 0.030, 0.014)),
        origin=Origin(xyz=(0.0, -0.004, 0.166 * hs)),
        material=mats["shell"], name="top_control_block", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        Box((0.025, 0.016, 0.004)),
        origin=Origin(xyz=(0.025 * rs, 0.025 * rs, 0.160 * hs)),
        material=mats["dark"], name="top_switch", material_class_id="plastic.opaque_glossy_molded",
    )


def _box_housing_shape(hw: float, hd: float, hh: float) -> cq.Workplane:
    """Rectangular box housing frame: plates + 4 corner posts (box fork L44-L94)."""
    t, bar = 0.005, 0.008
    frame = (
        cq.Workplane("XY").transformed(offset=(0.0, 0.0, -hh / 2.0 + t / 2.0)).box(hw, hd, t)
    )
    frame = frame.union(
        cq.Workplane("XY").transformed(offset=(0.0, 0.0, hh / 2.0 - t / 2.0)).box(hw, hd, t)
    )
    for sx in (-1, 1):
        for sy in (-1, 1):
            frame = frame.union(
                cq.Workplane("XY")
                .transformed(offset=(sx * (hw / 2.0 - bar / 2.0), sy * (hd / 2.0 - bar / 2.0), 0.0))
                .box(bar, bar, hh)
            )
    return frame


def _body_box(body, r, mats) -> None:
    rs = r.body_radius_scale
    hs = r.body_height_scale
    hw, hd, hh = 0.100 * rs, 0.080 * rs, 0.120 * hs
    bar, plate_t = 0.008, 0.005
    hz = 0.028 + hh / 2.0  # housing center z (base ~0.028 tall)
    # Squared vented base.
    body.visual(
        Box((0.120 * rs, 0.100 * rs, 0.028)),
        origin=Origin(xyz=(0.0, 0.0, 0.014)),
        material=mats["shell"], name="vented_base", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        mesh_from_cadquery(_box_housing_shape(hw, hd, hh), "housing_frame", tolerance=0.0004),
        origin=Origin(xyz=(0.0, 0.0, hz)),
        material=mats["shell"], name="housing_frame", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    panel_h = hh - 2.0 * plate_t - 0.004
    pf = hw - 2.0 * bar
    ps = hd - 2.0 * bar
    specs = [
        ("diffuser_panel_0", (pf, 0.003, panel_h), (0.0, hd / 2.0 - bar / 2.0, hz)),
        ("diffuser_panel_1", (pf, 0.003, panel_h), (0.0, -(hd / 2.0 - bar / 2.0), hz)),
        ("diffuser_panel_2", (0.003, ps, panel_h), (hw / 2.0 - bar / 2.0, 0.0, hz)),
        ("diffuser_panel_3", (0.003, ps, panel_h), (-(hw / 2.0 - bar / 2.0), 0.0, hz)),
    ]
    for name, dims, xyz in specs:
        body.visual(Box(dims), origin=Origin(xyz=xyz), material=mats["diffuser"], name=name, material_class_id="plastic.frosted_translucent")
    # LED column + tall pedestal bridging the base plate to the column (no gap).
    body.visual(
        Cylinder(radius=0.016 * rs, length=0.028 + hh * 0.5),
        origin=Origin(xyz=(0.0, 0.0, 0.014 + (0.028 + hh * 0.5) * 0.5)),
        material=mats["dark"], name="led_mount", material_class_id="metal.paint_coated",
    )
    body.visual(
        Cylinder(radius=0.018 * rs, length=0.098 * hs),
        origin=Origin(xyz=(0.0, 0.0, hz)),
        material=mats["led"], name="led_column", material_class_id="tech.emissive_surface",
    )
    body.visual(
        Box((0.112 * rs, 0.092 * rs, 0.022)),
        origin=Origin(xyz=(0.0, 0.0, 0.028 + hh + 0.011)),
        material=mats["shell"], name="top_cap", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    body.visual(
        Box((0.068 * rs, 0.030, 0.016)),
        origin=Origin(xyz=(0.0, -0.004, 0.028 + hh + 0.024)),
        material=mats["shell"], name="top_control_block", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )


# =================================================================== grip modules
def _emit_grip(model, body, r: ResolvedCampingLanternConfig, mats) -> str:
    """Slot C: one swinging carry handle. Body-side bosses are inline visuals;
    handle is a REVOLUTE captured-pin child (grandfathered)."""
    gs = r.grip_style
    top_z = r.body_top_z  # sits just above the body's cap apex (bail clears cap)
    boss_x = min(0.052, r.body_max_r + 0.0015)

    if gs in ("fold_bail", "top_hook"):
        # A thin crown disc at the top, anchored by overlapping the cap below it,
        # gives every top-mounted grip a solid seat regardless of body form.
        crown_r = boss_x + 0.004
        body.visual(
            Cylinder(radius=crown_r, length=0.018),
            origin=Origin(xyz=(0.0, 0.0, top_z - 0.008)),
            material=mats["shell"], name="grip_crown", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
        )

    if gs == "fold_bail":
        for side, xs in enumerate((-1.0, 1.0)):
            body.visual(
                Cylinder(radius=0.006, length=0.012),
                origin=Origin(xyz=(xs * boss_x, 0.0, top_z), rpy=(0.0, math.pi / 2, 0.0)),
                material=mats["accent"], name=f"bail_ear_{side}", material_class_id=("metal.stainless_matte" if r.palette_style in {"graphite_black", "vintage_brass", "frosted_white", "anodized_orange"} else "metal.blackened_gunmetal"),
            )
        handle = model.part("carry_handle")
        rise = 0.132 * r.body_height_scale
        handle.visual(
            mesh_from_geometry(_bail_wire(boss_x - 0.002, rise), "bail_wire"),
            material=mats["accent"], name="wire_bail", material_class_id=("metal.stainless_matte" if r.palette_style in {"graphite_black", "vintage_brass", "frosted_white", "anodized_orange"} else "metal.blackened_gunmetal"),
        )
        handle.inertial = Inertial.from_geometry(
            Box((2.0 * boss_x, 0.01, rise)), mass=0.03, origin=Origin(xyz=(0.0, 0.0, rise / 2.0))
        )
        model.articulation(
            "lantern_to_grip", ArticulationType.REVOLUTE, parent=body, child=handle,
            origin=Origin(xyz=(0.0, 0.0, top_z)), axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=-1.45, upper=0.20),
        )
        return "carry_handle"

    if gs == "top_hook":
        # Central pivot boss on the crown; pivot sits at its top.
        body.visual(
            Cylinder(radius=0.006, length=0.014),
            origin=Origin(xyz=(0.0, 0.0, top_z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["accent"], name="hook_pivot_boss", material_class_id=("metal.stainless_matte" if r.palette_style in {"graphite_black", "vintage_brass", "frosted_white", "anodized_orange"} else "metal.blackened_gunmetal"),
        )
        handle = model.part("carry_handle")
        handle.visual(
            mesh_from_geometry(_hook_wire(), "hook_wire"),
            material=mats["accent"], name="wire_bail", material_class_id=("metal.stainless_matte" if r.palette_style in {"graphite_black", "vintage_brass", "frosted_white", "anodized_orange"} else "metal.blackened_gunmetal"),
        )
        handle.inertial = Inertial.from_geometry(
            Box((0.04, 0.01, 0.06)), mass=0.02, origin=Origin(xyz=(0.01, 0.0, 0.03))
        )
        model.articulation(
            "lantern_to_grip", ArticulationType.REVOLUTE, parent=body, child=handle,
            origin=Origin(xyz=(0.0, 0.0, top_z + 0.004)), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=1.0, velocity=2.5, lower=0.0, upper=1.50),
        )
        return "carry_handle"

    # side_loop: a flat saddle plate flush to the +Y wall (touches it at least
    # along its centre line, whatever the wall curvature) carries the two pivot
    # ears; the loop's pivot ends are captured on the ears and the loop body
    # hangs clear outside the wall.
    sz = r.body_side_z
    wall = r.body_side_wall
    body.visual(
        Box((0.046, 0.018, 0.018)),
        origin=Origin(xyz=(0.0, wall - 0.006, sz)),
        material=mats["shell"], name="loop_saddle", material_class_id=("metal.paint_coated" if r.palette_style in {"graphite_black", "olive_steel", "vintage_brass", "anodized_orange"} else "plastic.opaque_glossy_molded"),
    )
    y_ear = wall + 0.006
    for side, xs in enumerate((-1.0, 1.0)):
        body.visual(
            Cylinder(radius=0.005, length=0.014),
            origin=Origin(xyz=(xs * 0.018, y_ear, sz), rpy=(0.0, math.pi / 2, 0.0)),
            material=mats["accent"], name=f"bail_ear_{side}", material_class_id=("metal.stainless_matte" if r.palette_style in {"graphite_black", "vintage_brass", "frosted_white", "anodized_orange"} else "metal.blackened_gunmetal"),
        )
    handle = model.part("carry_handle")
    handle.visual(
        mesh_from_geometry(_side_loop_wire(0.060, 0.064), "side_loop_wire"),
        material=mats["accent"], name="wire_bail", material_class_id=("metal.stainless_matte" if r.palette_style in {"graphite_black", "vintage_brass", "frosted_white", "anodized_orange"} else "metal.blackened_gunmetal"),
    )
    handle.visual(
        Cylinder(radius=0.0058, length=0.030),
        origin=Origin(xyz=(0.0, 0.060, -0.064), rpy=(0.0, math.pi / 2, 0.0)),
        material=mats["dark"], name="grip_sleeve", material_class_id="rubber.smooth_plain",
    )
    handle.inertial = Inertial.from_geometry(
        Box((0.05, 0.13, 0.07)), mass=0.03, origin=Origin(xyz=(0.0, 0.03, -0.03))
    )
    model.articulation(
        "lantern_to_grip", ArticulationType.REVOLUTE, parent=body, child=handle,
        origin=Origin(xyz=(0.0, y_ear, sz)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=0.0, upper=1.40),
    )
    return "carry_handle"


# =================================================================== assembly
def build_camping_lantern(
    config: CampingLanternConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"lantern_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }

    base = _emit_base(model, r, mats)
    body = _emit_body(model, r, mats)

    # base -> body seat/slide chain (the sole MatingContract joint).
    seat_mating = MatingContract(
        parent_face_geometry="body_seat_rim",
        parent_face_side="positive_z",
        child_face_geometry="body_seat",
        child_face_side="negative_z",
        contact_tol=0.0025,
    )
    if r.prismatic:
        model.articulation(
            "base_to_lantern", ArticulationType.PRISMATIC, parent=base, child=body,
            origin=Origin(xyz=(0.0, 0.0, r.base_top_z)), axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=60.0, velocity=0.18, lower=0.0, upper=0.070),
            mating=seat_mating,
        )
    else:
        model.articulation(
            "base_to_lantern", ArticulationType.FIXED, parent=base, child=body,
            origin=Origin(xyz=(0.0, 0.0, r.base_top_z)), mating=seat_mating,
        )

    _emit_grip(model, body, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_camping_lantern(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_camping_lantern(config_from_seed(seed), assets=assets)


# =================================================================== tests
def run_camping_lantern_tests(
    object_model: ArticulatedObject,
    config: CampingLanternConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    base = object_model.get_part("lower_base")
    body = object_model.get_part("upper_lantern")
    grip = object_model.get_part("carry_handle")
    grip_joint = object_model.get_articulation("lantern_to_grip")

    # ---- Captured-pin allowances (element-scoped, mirror the 5-star sources). ----
    if r.grip_style == "top_hook":
        ctx.allow_overlap(
            grip, body, elem_a="wire_bail", elem_b="hook_pivot_boss",
            reason="J-hook wire pivots on the captured cap-center boss pin.",
        )
    else:  # fold_bail / side_loop use ear bosses
        ctx.allow_overlap(
            grip, body, elem_a="wire_bail", elem_b="bail_ear_0",
            reason="bail/loop pivot pin seated through the +side ear boss.",
        )
        ctx.allow_overlap(
            grip, body, elem_a="wire_bail", elem_b="bail_ear_1",
            reason="bail/loop pivot pin seated through the -side ear boss.",
        )
    for i in range(r.leg_count):
        leg = object_model.get_part(f"leg_{i}")
        ctx.allow_overlap(
            leg, base, elem_a="hinge_pin", elem_b=f"leg_socket_{i}",
            reason="slim leg hinge pin is captured inside its base socket block.",
        )
        ctx.allow_overlap(
            leg, base, elem_a="leg_wire", elem_b=f"leg_socket_{i}",
            reason="the leg wire root sweeps past its own hinge socket block through the fold.",
        )

    # ---- Baseline geometry / connectivity gates. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()
    # Rule 5: no 穿模 across the full joint travel.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=96, ignore_fixed=True)

    # ---- Identity: diffuser translucent, body seated on base. ----
    diff_name = {
        "cage_diffuser": "clear_chamber",
        "box_panel": "diffuser_panel_0",
    }.get(r.body_style, "clear_chamber")
    diff = body.get_visual(diff_name)
    diff_rgba = diff.material.rgba if diff and diff.material else None
    ctx.check(
        "light diffuser is translucent",
        diff_rgba is not None and diff_rgba[3] < 0.5,
        details=f"{diff_name} rgba={diff_rgba}",
    )
    seat_bb = ctx.part_element_world_aabb(body, elem="body_seat")
    rim_bb = ctx.part_element_world_aabb(base, elem="body_seat_rim")
    ctx.check(
        "body seats on base rim (z contact)",
        seat_bb is not None and rim_bb is not None and abs(seat_bb[0][2] - rim_bb[1][2]) < 0.006,
        details=f"seat={seat_bb}, rim={rim_bb}",
    )

    # ---- Slot realization counts. ----
    if r.leg_count:
        n_legs = sum(1 for p in object_model.parts if (p.name or "").startswith("leg_"))
        ctx.check(
            "tripod leg count matches leg_count",
            n_legs == r.leg_count,
            details=f"legs={n_legs} expected={r.leg_count}",
        )
    if r.cage_bar_count:
        ctx.check(
            "cage lattice present for cage_diffuser",
            body.get_visual("cage_lattice") is not None,
            details=f"cage_bar_count={r.cage_bar_count}",
        )

    # ---- Motion identity: grip REVOLUTE actually swings. ----
    ctx.check(
        "grip joint is REVOLUTE",
        grip_joint.articulation_type == ArticulationType.REVOLUTE,
        details=f"type={grip_joint.articulation_type}",
    )
    closed = ctx.part_world_aabb(grip)
    swing_q = {"fold_bail": -1.2, "top_hook": 1.0, "side_loop": 1.2}[r.grip_style]
    with ctx.pose({grip_joint: swing_q}):
        swung = ctx.part_world_aabb(grip)
    if closed is not None and swung is not None:
        moved = max(abs(swung[0][k] - closed[0][k]) + abs(swung[1][k] - closed[1][k]) for k in range(3))
        ctx.check("grip swings on its REVOLUTE", moved > 0.02, details=f"closed={closed} swung={swung}")

    # ---- base->body motion: telescope lifts / seat is FIXED. ----
    base_joint = object_model.get_articulation("base_to_lantern")
    if r.prismatic:
        rest = ctx.part_world_position(body)
        with ctx.pose({base_joint: 0.070}):
            lifted = ctx.part_world_position(body)
        ctx.check(
            "telescope slide lifts the body upward",
            rest is not None and lifted is not None and lifted[2] > rest[2] + 0.05,
            details=f"rest={rest}, lifted={lifted}",
        )
    else:
        ctx.check(
            "non-telescope base uses a FIXED seat",
            base_joint.articulation_type == ArticulationType.FIXED,
            details=f"type={base_joint.articulation_type}",
        )

    # ---- Legs fold up about their base hinge (tripod). ----
    for i in range(r.leg_count):
        leg = object_model.get_part(f"leg_{i}")
        joint = object_model.get_articulation(f"base_to_leg_{i}")
        rest_bb = ctx.part_element_world_aabb(leg, elem="leg_wire")
        with ctx.pose({joint: 1.0}):
            fold_bb = ctx.part_element_world_aabb(leg, elem="leg_wire")
        if rest_bb is not None and fold_bb is not None:
            ctx.check(
                f"leg_{i} folds up about its hinge",
                fold_bb[0][2] > rest_bb[0][2] + 0.04,
                details=f"rest={rest_bb}, fold={fold_bb}",
            )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )
    return ctx.report()


__all__ = (
    "CampingLanternConfig",
    "ResolvedCampingLanternConfig",
    "build_camping_lantern",
    "build_seeded_camping_lantern",
    "config_from_seed",
    "resolve_config",
    "run_camping_lantern_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
