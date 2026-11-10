# SPDX-License-Identifier: Apache-2.0

"""Water / beverage dispenser modular procedural template.

Implements ``articraft_template_authoring/specs_modular_v1/Other_Water_dispenser.md``.

A grounded dispensing machine: one stable body (Slot B ``body_form``) carries
``1..N`` front/peripheral faucets (multiplicity axis), each operated by a moving
valve mechanism (Slot A ``tap_type``).  Below the body sits a drip tray; the
grounding / reservoir behaviour is set by Slot C ``base_reservoir``.

Slot graph (mixed parallel-children + multiplicity, explicit slot dispatch — no
auto-assembler, all moving children parent directly to the grounded body tree):

* Slot B ``body_form``  : rectangular_box | bottled_cooler_cabinet | cylindrical_urn
                          — emits the main shell + decides each faucet's mount
                          parent and layout (front row / radial fan / alcove).
* Slot A ``tap_type``   : push_lever (REVOLUTE) | push_button (PRISMATIC)
                          | twist_spigot (REVOLUTE about +X flow axis)
                          | paddle (REVOLUTE about Y, bottled_cooler only).
* Slot C ``base_reservoir`` : countertop (drip_tray root, no extra joint)
                          | floor_standing_pedestal (cabinet root, FIXED stack)
                          | removable_drip_tray (PRISMATIC pull/lift)
                          | inverted_top_bottle (FIXED top reservoir).
* faucet_count N        : copy ``faucet_{i}`` + its tap_type child N times.

Adopted 5-star source mapping (all under ``data/records/``, rating 5):
S1 …single…_b6696ffc       push_lever + rectangular_box + countertop (N=1).
S2 …triple…_acfaa2cf       push_lever + flared column + countertop (N=3 fan).
S3 …four-tap…_3f3a9da3     push_lever + T-header + countertop (N=4 copy loop).
S4 …cooler…_6fffaa2f       paddle + bottled_cooler_cabinet + +Z removable tray
                           + inverted_top_bottle (4 same-source modules).
S5 …push-button…_1a8f4bb6  push_button (PRISMATIC -Z, stem captured in bonnet).
S6 …twist-spigot…_ffb293c3 twist_spigot (REVOLUTE +X knob) + faucet copy loop.
S7 …cylindrical-urn…_b7793c5c lathe base + urn, radial faucet fan.
S8 …floor-pedestal…_9a1aa34a pedestal_cabinet root, FIXED tray stack.
S9 …removable-drip-tray…_7e820f42 drip_tray PRISMATIC -Y pull-out.
S10 …inverted-top-bottle…_870bb3bc water_bottle lathe FIXED into top collar.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    CylinderGeometry,
    Inertial,
    KnobGeometry,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True


# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
TapType = Literal["push_lever", "push_button", "twist_spigot", "paddle"]
BodyForm = Literal["rectangular_box", "bottled_cooler_cabinet", "cylindrical_urn"]
BaseReservoir = Literal[
    "countertop",
    "floor_standing_pedestal",
    "removable_drip_tray",
    "inverted_top_bottle",
]
PaletteStyle = Literal[
    "brushed_steel",
    "matte_black_chrome",
    "white_cooler",
    "copper_urn",
    "pastel_dispenser",
]

TAP_TYPES: tuple[TapType, ...] = (
    "push_lever",
    "push_button",
    "twist_spigot",
    "paddle",
)
BODY_FORMS: tuple[BodyForm, ...] = (
    "rectangular_box",
    "bottled_cooler_cabinet",
    "cylindrical_urn",
)
BASE_RESERVOIRS: tuple[BaseReservoir, ...] = (
    "countertop",
    "floor_standing_pedestal",
    "removable_drip_tray",
    "inverted_top_bottle",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "brushed_steel",
    "matte_black_chrome",
    "white_cooler",
    "copper_urn",
    "pastel_dispenser",
)

N_MIN = 1
N_MAX = 4
# Spec §8: small N high-frequency, N=4 long tail.
N_WEIGHTS = (0.40, 0.30, 0.20, 0.10)


# ---------------------------------------------------------------------------
# Compatibility (spec §9)
# ---------------------------------------------------------------------------
# paddle hangs from a bottled-cooler alcove ceiling only.
def _legal_tap_types(body: BodyForm) -> tuple[TapType, ...]:
    if body == "bottled_cooler_cabinet":
        return ("push_lever", "push_button", "twist_spigot", "paddle")
    return ("push_lever", "push_button", "twist_spigot")


# inverted_top_bottle needs a top collar/socket — urn top is a lid, no collar.
def _legal_base_reservoirs(body: BodyForm) -> tuple[BaseReservoir, ...]:
    if body == "cylindrical_urn":
        return ("countertop", "floor_standing_pedestal", "removable_drip_tray")
    return BASE_RESERVOIRS


def _n_upper(body: BodyForm, tap: TapType) -> int:
    if body == "cylindrical_urn":
        return 3  # small barrel circumference
    if body == "bottled_cooler_cabinet" and tap == "paddle":
        return 2  # hot/cold paddle pair
    return N_MAX


# ---------------------------------------------------------------------------
# Palettes (spec colorways; every .visual material is keyed here)
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "brushed_steel": {
        "body": (0.66, 0.67, 0.69, 1.0),
        "body_dark": (0.16, 0.16, 0.17, 1.0),
        "trim": (0.80, 0.81, 0.84, 1.0),
        "metal": (0.85, 0.87, 0.90, 1.0),
        "grip": (0.05, 0.05, 0.06, 1.0),
        "accent": (0.78, 0.20, 0.18, 1.0),
        "water": (0.55, 0.78, 0.95, 0.55),
    },
    "matte_black_chrome": {
        "body": (0.13, 0.13, 0.14, 1.0),
        "body_dark": (0.045, 0.045, 0.05, 1.0),
        "trim": (0.80, 0.81, 0.84, 1.0),
        "metal": (0.85, 0.87, 0.90, 1.0),
        "grip": (0.03, 0.03, 0.035, 1.0),
        "accent": (0.72, 0.72, 0.74, 1.0),
        "water": (0.50, 0.74, 0.92, 0.55),
    },
    "white_cooler": {
        "body": (0.92, 0.93, 0.93, 1.0),
        "body_dark": (0.55, 0.57, 0.58, 1.0),
        "trim": (0.78, 0.80, 0.82, 1.0),
        "metal": (0.85, 0.87, 0.90, 1.0),
        "grip": (0.10, 0.11, 0.12, 1.0),
        "accent": (0.85, 0.18, 0.16, 1.0),
        "water": (0.40, 0.62, 0.92, 0.55),
    },
    "copper_urn": {
        "body": (0.21, 0.18, 0.17, 1.0),
        "body_dark": (0.10, 0.085, 0.08, 1.0),
        "trim": (0.78, 0.50, 0.30, 1.0),
        "metal": (0.85, 0.58, 0.36, 1.0),
        "grip": (0.05, 0.05, 0.06, 1.0),
        "accent": (0.80, 0.52, 0.30, 1.0),
        "water": (0.55, 0.74, 0.90, 0.55),
    },
    "pastel_dispenser": {
        "body": (0.86, 0.90, 0.92, 1.0),
        "body_dark": (0.52, 0.62, 0.68, 1.0),
        "trim": (0.80, 0.84, 0.88, 1.0),
        "metal": (0.85, 0.87, 0.90, 1.0),
        "grip": (0.36, 0.58, 0.70, 1.0),
        "accent": (0.92, 0.62, 0.50, 1.0),
        "water": (0.58, 0.82, 0.95, 0.55),
    },
}


# ---------------------------------------------------------------------------
# Base dimensions (meters), from S1/S3/S4/S7.  Long faucet row along X (+X front).
# ---------------------------------------------------------------------------
_TRAY_X = 0.30  # drip tray depth (X, front-back)
_TRAY_Y = 0.40  # drip tray width (Y, left-right) — faucet row runs along Y
_TRAY_H = 0.030
_PLATE_T = 0.004
_PLATE_TOP_Z = 0.026

_COL_R = 0.0375  # tower column radius
_COL_TOP = 0.35  # tower column total height (countertop frame)
_FAUCET_Z = 0.315  # faucet axis height above tray top

# faucet unit (local frame: shank along +X from body face, spout drops at front).
_BODY_R = 0.013
_SHANK_X0 = -0.018  # shank starts inside the body wall
_SHANK_X1 = 0.082  # shank forward extent
_BONNET_X = 0.066  # bonnet (valve top) X
_PIVOT_Z = 0.030  # lever / button pivot height above faucet axis

# urn lathe profile
_URN_R_BELLY = 0.105
_URN_R_BOTTOM = 0.088
_URN_R_TOP = 0.082
_URN_H = 0.30

# cabinet (bottled cooler)
_CAB_X = 0.30
_CAB_Y = 0.30
_CAB_H = 0.46
_COOLER_ALCOVE_W_FRAC = 0.64
_COOLER_ALCOVE_BOTTOM_FRAC = 0.11
_COOLER_ALCOVE_CEIL_FRAC = 0.42

# pedestal cabinet
_PED_X = 0.34
_PED_Y = 0.40
_PED_H = 0.46

_TRAY_SLIDE = 0.18  # removable tray pull-out / lift travel
_BUTTON_TRAVEL = 0.010
_LEVER_OPEN = 0.62  # ~36 deg
_SPIGOT_OPEN = math.radians(90.0)
# Cooler alcove paddles start tilted outward, then press back toward vertical.
# This gives the button real travel while keeping the pressed pose inside the
# alcove instead of sweeping through the cabinet face.
_PADDLE_OPEN = 0.30
_PADDLE_REST_TILT = 0.30


# ---------------------------------------------------------------------------
# Config dataclasses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class WaterDispenserConfig:
    tap_type: TapType | None = None
    body_form: BodyForm | None = None
    base_reservoir: BaseReservoir | None = None
    faucet_count: int | None = None
    palette_style: PaletteStyle = "brushed_steel"
    body_height_scale: float = 1.0
    body_footprint_scale: float = 1.0
    faucet_spacing_scale: float = 1.0
    tap_travel_scale: float = 1.0
    tray_travel_scale: float = 1.0
    name: str = "water_dispenser"


@dataclass(frozen=True)
class ResolvedWaterDispenserConfig:
    tap_type: TapType
    body_form: BodyForm
    base_reservoir: BaseReservoir
    faucet_count: int
    palette_style: PaletteStyle
    body_height_scale: float
    body_footprint_scale: float
    faucet_spacing_scale: float
    tap_travel_scale: float
    tray_travel_scale: float
    # derived geometry
    tray_x: float
    tray_y: float
    base_z: float  # top surface the body sits on (z of tray seat), 0 for countertop
    faucet_z: float  # world Z of faucet axis
    faucet_local_z: float  # body-local Z of faucet axis (excludes base_z)
    body_top_local_z: float  # body-local Z of body top (excludes base_z)
    faucet_ys: tuple[float, ...]  # absolute Y positions of faucets (rect/cooler)
    faucet_angles: tuple[float, ...]  # radial angles (urn)
    mount_radius: float  # urn belly radius at faucet height
    body_top_z: float  # collar / top-bottle seat Z
    lever_open: float
    button_travel: float
    spigot_open: float
    paddle_open: float
    tray_travel: float
    name: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(round(value))))


def _pick(value, choices, fallback):
    return value if value in choices else fallback


def _cyl_x() -> tuple[float, float, float]:
    return (0.0, math.pi / 2.0, 0.0)


def _cyl_y() -> tuple[float, float, float]:
    return (math.pi / 2.0, 0.0, 0.0)


def _cyl_z() -> tuple[float, float, float]:
    return (0.0, 0.0, 0.0)


def _box(part, name, size, xyz, material, rpy=(0.0, 0.0, 0.0)):
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="plastic.opaque_generic")


def _cyl(part, name, radius, length, xyz, material, rpy=(0.0, 0.0, 0.0)):
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _spout_geometry(length_scale: float = 1.0) -> MeshGeometry:
    """Downward-curving tapered spout (manual ring loft, outward winding).

    Adapted verbatim from S1/S5 ``_spout_geometry`` so the mesh source is not
    downgraded to a box.  Built in faucet-local XZ with the bend center near
    the spout start; the user can rescale the drop with ``length_scale``.
    """
    n_pts = 18
    n_bend = 9
    bend_r = 0.020
    start_x = 0.078
    cx, cz = start_x, -bend_r
    specs: list[tuple[float, float, float, float]] = []
    for i in range(n_bend + 1):
        t = (math.pi / 2.0) * i / n_bend
        r = 0.0105 + (0.0080 - 0.0105) * (i / n_bend)
        specs.append((t, cx + bend_r * math.sin(t), cz + bend_r * math.cos(t), r))
    drop = 0.014 * length_scale
    specs.append((math.pi / 2.0, cx + bend_r, cz - 0.6 * drop, 0.0074))
    specs.append((math.pi / 2.0, cx + bend_r, cz - drop, 0.0068))

    geom = MeshGeometry()
    ring_ids: list[list[int]] = []
    for t, rcx, rcz, r in specs:
        wx, wz = math.sin(t), math.cos(t)
        ids: list[int] = []
        for j in range(n_pts):
            a = 2.0 * math.pi * j / n_pts
            px = rcx + r * math.sin(a) * wx
            py = r * math.cos(a)
            pz = rcz + r * math.sin(a) * wz
            ids.append(geom.add_vertex(px, py, pz))
        ring_ids.append(ids)
    for i in range(len(ring_ids) - 1):
        ra, rb = ring_ids[i], ring_ids[i + 1]
        for j in range(n_pts):
            j2 = (j + 1) % n_pts
            geom.add_face(ra[j], ra[j2], rb[j2])
            geom.add_face(ra[j], rb[j2], rb[j])
    c0x, c0z = specs[0][1], specs[0][2]
    sc = geom.add_vertex(c0x, 0.0, c0z)
    for j in range(n_pts):
        j2 = (j + 1) % n_pts
        geom.add_face(sc, ring_ids[0][j2], ring_ids[0][j])
    cnx, cnz = specs[-1][1], specs[-1][2]
    ec = geom.add_vertex(cnx, 0.0, cnz)
    last = ring_ids[-1]
    for j in range(n_pts):
        j2 = (j + 1) % n_pts
        geom.add_face(ec, last[j], last[j2])
    return geom


def _urn_shell_geometry(r: ResolvedWaterDispenserConfig) -> LatheGeometry:
    fs = r.body_footprint_scale
    hs = r.body_height_scale
    h = _URN_H * hs
    return LatheGeometry(
        [
            (0.001, 0.0),  # bottom center cap (solid axis)
            (_URN_R_BOTTOM * fs * 0.85, 0.0),
            (_URN_R_BOTTOM * fs, 0.005 * hs),
            (_URN_R_BELLY * fs, 0.055 * hs),
            (_URN_R_BELLY * fs, 0.55 * h),
            (_URN_R_TOP * fs, 0.78 * h),
            (_URN_R_TOP * fs + 0.003, h),
            (0.001, h),  # top center cap (solid axis)
        ],
        segments=40,
    )


def _urn_base_geometry(r: ResolvedWaterDispenserConfig) -> LatheGeometry:
    fs = r.body_footprint_scale
    return LatheGeometry(
        [
            (0.001, 0.0),  # bottom center cap (solid axis)
            (_URN_R_BELLY * fs * 1.02, 0.0),
            (_URN_R_BELLY * fs * 1.02, 0.012),
            (_URN_R_BOTTOM * fs, 0.024),
            (_URN_R_BOTTOM * fs * 0.9, 0.028),
            (0.001, 0.028),  # top center cap (solid axis)
        ],
        segments=40,
    )


def _bottle_geometry() -> LatheGeometry:
    """Inverted 19 L bottle: neck at z=0 (seats into collar), belly above.

    True-scale ~19 L jug (belly Ø ≈ 0.27 m, height ≈ 0.49 m).  The neck profile
    (z=0..0.018, r≈0.026-0.030) is unchanged so it still seats in the collar bore.
    """
    return LatheGeometry(
        [
            (0.001, 0.0),  # neck center cap
            (0.026, 0.0),  # neck (seats into collar)
            (0.030, 0.018),  # neck shoulder
            (0.070, 0.055),  # shoulder flare
            (0.120, 0.110),
            (0.135, 0.230),  # belly max radius 0.135 (Ø 0.27)
            (0.135, 0.360),
            (0.120, 0.440),
            (0.075, 0.480),
            (0.0, 0.490),  # base center cap (total height 0.49)
        ],
        segments=40,
    )


def _knob_geometry() -> MeshGeometry:
    knob = KnobGeometry(
        diameter=0.040,
        height=0.026,
        body_style="lobed",
    )
    # KnobGeometry is itself a MeshGeometry built on +Z; rotate so twist axis is +X.
    return knob.rotate_y(math.pi / 2.0)


# ---------------------------------------------------------------------------
# resolve_config — the only legalization / derivation entry point
# ---------------------------------------------------------------------------
def resolve_config(config: WaterDispenserConfig) -> ResolvedWaterDispenserConfig:
    body_form: BodyForm = _pick(config.body_form, BODY_FORMS, "rectangular_box")  # type: ignore
    legal_taps = _legal_tap_types(body_form)
    tap_type: TapType = _pick(config.tap_type, legal_taps, legal_taps[0])  # type: ignore
    legal_bases = _legal_base_reservoirs(body_form)
    base_reservoir: BaseReservoir = _pick(config.base_reservoir, legal_bases, legal_bases[0])  # type: ignore
    palette_style: PaletteStyle = _pick(config.palette_style, PALETTE_STYLES, "brushed_steel")  # type: ignore

    n_hi = _n_upper(body_form, tap_type)
    n_req = config.faucet_count if config.faucet_count is not None else 1
    faucet_count = _clamp_int(n_req, N_MIN, n_hi)

    body_height_scale = _clamp(config.body_height_scale, 0.88, 1.18)
    body_footprint_scale = _clamp(config.body_footprint_scale, 0.90, 1.12)
    faucet_spacing_scale = (
        _clamp(config.faucet_spacing_scale, 0.90, 1.10) if faucet_count >= 2 else 1.0
    )
    tap_travel_scale = _clamp(config.tap_travel_scale, 0.85, 1.10)
    tray_travel_scale = (
        _clamp(config.tray_travel_scale, 0.85, 1.10)
        if base_reservoir == "removable_drip_tray"
        else 1.0
    )

    fs = body_footprint_scale
    hs = body_height_scale
    tray_x = _TRAY_X * fs
    tray_y = _TRAY_Y * fs

    # base_z: top of the support the body tree sits on.
    if base_reservoir == "floor_standing_pedestal":
        base_z = _PED_H * hs
    else:
        base_z = 0.0

    # faucet axis height — BODY-LOCAL (z measured from the body tree's own
    # authoring origin z0, NOT including base_z; the pedestal stack is a FIXED
    # joint so the body tree keeps its own local frame).
    if body_form == "cylindrical_urn":
        faucet_local_z = 0.55 * _URN_H * hs
        body_top_local_z = _URN_H * hs
    elif body_form == "bottled_cooler_cabinet":
        faucet_local_z = 0.40 * _CAB_H * hs
        body_top_local_z = _CAB_H * hs
    else:  # rectangular_box
        faucet_local_z = _PLATE_TOP_Z + (_FAUCET_Z * hs)
        body_top_local_z = _PLATE_TOP_Z + (_COL_TOP * hs)
    faucet_z = base_z + faucet_local_z
    body_top_z = base_z + body_top_local_z

    # faucet layout: absolute, center-symmetric so the row is N-invariant.
    faucet_ys: tuple[float, ...] = ()
    faucet_angles: tuple[float, ...] = ()
    mount_radius = 0.0
    if body_form == "cylindrical_urn":
        mount_radius = _URN_R_BELLY * fs
        # radial fan over the front 150 deg
        if faucet_count == 1:
            faucet_angles = (0.0,)
        else:
            fan = math.radians(120.0) * faucet_spacing_scale
            fan = min(fan, math.radians(150.0))
            faucet_angles = tuple(
                (i - (faucet_count - 1) / 2.0) * (fan / max(1, faucet_count - 1))
                for i in range(faucet_count)
            )
    else:
        # front face faucet row along Y.  Front span = tray width minus margins.
        if body_form == "bottled_cooler_cabinet":
            # Cooler paddles hang inside the recessed alcove, not across the
            # whole cabinet width.  Keeping the row inside the alcove prevents
            # two-tap seeds from looking like side-mounted boxes.
            front_span = _CAB_Y * fs * _COOLER_ALCOVE_W_FRAC
        else:
            front_span = tray_y - 0.06
        faucet_w = 0.05
        margin = 0.5 * faucet_w
        usable = front_span - 2.0 * margin
        if faucet_count == 1:
            faucet_ys = (0.0,)
        else:
            gap = usable / (faucet_count - 1)
            gap *= faucet_spacing_scale
            # clearance inequality (spec §7): row must fit within the FULL front
            # span (not the margin-reduced ``usable``), so spacing_scale>1.0 can
            # actually widen the row instead of being a no-op.
            max_gap = front_span / (faucet_count - 1)
            gap = min(gap, max_gap)
            faucet_ys = tuple((i - (faucet_count - 1) / 2.0) * gap for i in range(faucet_count))

    tray_travel = _TRAY_SLIDE * tray_travel_scale

    return ResolvedWaterDispenserConfig(
        tap_type=tap_type,
        body_form=body_form,
        base_reservoir=base_reservoir,
        faucet_count=faucet_count,
        palette_style=palette_style,
        body_height_scale=body_height_scale,
        body_footprint_scale=body_footprint_scale,
        faucet_spacing_scale=faucet_spacing_scale,
        tap_travel_scale=tap_travel_scale,
        tray_travel_scale=tray_travel_scale,
        tray_x=tray_x,
        tray_y=tray_y,
        base_z=base_z,
        faucet_z=faucet_z,
        faucet_local_z=faucet_local_z,
        body_top_local_z=body_top_local_z,
        faucet_ys=faucet_ys,
        faucet_angles=faucet_angles,
        mount_radius=mount_radius,
        body_top_z=body_top_z,
        lever_open=_LEVER_OPEN * tap_travel_scale,
        button_travel=_BUTTON_TRAVEL * tap_travel_scale,
        spigot_open=_SPIGOT_OPEN * tap_travel_scale,
        paddle_open=_PADDLE_OPEN * tap_travel_scale,
        tray_travel=tray_travel,
        name=str(config.name or "water_dispenser"),
    )


# ---------------------------------------------------------------------------
# Seed sampling
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> WaterDispenserConfig:
    rng = random.Random(seed)
    body_form = rng.choice(BODY_FORMS)
    tap_type = rng.choice(_legal_tap_types(body_form))
    base_reservoir = rng.choice(_legal_base_reservoirs(body_form))
    n_hi = _n_upper(body_form, tap_type)
    weights = N_WEIGHTS[:n_hi]
    faucet_count = rng.choices(tuple(range(1, n_hi + 1)), weights=weights, k=1)[0]
    return WaterDispenserConfig(
        tap_type=tap_type,
        body_form=body_form,
        base_reservoir=base_reservoir,
        faucet_count=faucet_count,
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=rng.uniform(0.90, 1.16),
        body_footprint_scale=rng.uniform(0.92, 1.10),
        faucet_spacing_scale=rng.uniform(0.92, 1.08),
        tap_travel_scale=rng.uniform(0.88, 1.08),
        tray_travel_scale=rng.uniform(0.88, 1.08),
        name=f"seeded_water_dispenser_{seed}",
    )


def slot_choices_for_config(config: WaterDispenserConfig) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("body_form", r.body_form),
        ("tap_type", r.tap_type),
        ("base_reservoir", r.base_reservoir),
        ("faucet_count", f"n{r.faucet_count}"),
        ("palette_style", r.palette_style),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


def _register_materials(model: ArticulatedObject, style: PaletteStyle) -> dict[str, object]:
    return {name: model.material(f"wd_{name}", rgba=rgba) for name, rgba in PALETTES[style].items()}


# ---------------------------------------------------------------------------
# Body anchors descriptor
# ---------------------------------------------------------------------------
@dataclass
class BodyAnchors:
    root: Part  # grounded root part
    mount_parent: Part  # part faucets parent to
    mount_parent_name: str
    # per-faucet mount frame: (xyz, yaw) in mount_parent local frame
    faucet_mounts: list[tuple[tuple[float, float, float], float]]
    collar_seat: tuple[float, float, float] | None  # for inverted_top_bottle
    collar_parent: Part | None  # part the bottle is FIXED to (where the collar lives)
    tray_part: Part | None  # drip tray (for removable)
    tray_seat: tuple[float, float, float]
    alcove_tap_bodies: list[str]  # paddle tap_body visual names on mount parent


# ---------------------------------------------------------------------------
# Slot B: body_form
# ---------------------------------------------------------------------------
def _build_drip_tray(
    part: Part, r: ResolvedWaterDispenserConfig, mats, *, z0: float, basin: bool = True
) -> None:
    """Perforated drip tray basin (box rim + perforated plate via cylinders).

    When ``basin`` is False (removable_drip_tray mode) the fixed root is instead
    a plain base plinth reaching the same top height (``_PLATE_TOP_Z``) that seats
    the column — the single catch basin then becomes the removable pull-out, so
    the dispenser never shows two stacked trays.
    """
    tx, ty = r.tray_x, r.tray_y
    if not basin:
        _box(
            part,
            "tray_floor",
            (tx, ty, _PLATE_TOP_Z),
            (0.0, 0.0, z0 + _PLATE_TOP_Z / 2.0),
            mats["body"],
        )
        return
    # rim ring (4 walls) + floor
    _box(part, "tray_floor", (tx, ty, 0.008), (0.0, 0.0, z0 + 0.004), mats["body"])
    wall_h = _TRAY_H - 0.006
    _box(
        part,
        "tray_wall_front",
        (0.010, ty, wall_h),
        (tx / 2 - 0.005, 0.0, z0 + 0.006 + wall_h / 2),
        mats["body"],
    )
    _box(
        part,
        "tray_wall_back",
        (0.010, ty, wall_h),
        (-tx / 2 + 0.005, 0.0, z0 + 0.006 + wall_h / 2),
        mats["body"],
    )
    _box(
        part,
        "tray_wall_left",
        (tx, 0.010, wall_h),
        (0.0, ty / 2 - 0.005, z0 + 0.006 + wall_h / 2),
        mats["body"],
    )
    _box(
        part,
        "tray_wall_right",
        (tx, 0.010, wall_h),
        (0.0, -ty / 2 + 0.005, z0 + 0.006 + wall_h / 2),
        mats["body"],
    )
    # perforated top plate (recessed): a thin plate with drain hole grid as cylinders
    _box(
        part,
        "tray_perforated_plate",
        (tx - 0.020, ty - 0.020, _PLATE_T),
        (0.0, 0.0, z0 + _PLATE_TOP_Z - _PLATE_T / 2),
        mats["trim"],
    )


def _build_rectangular_box(model, r, mats, anchors_root: Part, *, z0: float) -> BodyAnchors:
    """drip tray + stainless tower column (+ optional T header for N>=3)."""
    tray = anchors_root  # tray is the root (or stacked onto pedestal)
    # removable_drip_tray => the single catch basin is the pull-out; the root is
    # just a base plinth (no second static basin).
    _build_drip_tray(
        tray, r, mats, z0=z0, basin=(r.base_reservoir != "removable_drip_tray")
    )

    hs = r.body_height_scale
    col_h = _COL_TOP * hs
    col_x = -r.tray_x * 0.27  # column toward rear edge
    # column part (FIXED on tray)
    column = model.part("tower_column")
    _cyl(column, "base_skirt", _COL_R * 1.45, 0.024, (0.0, 0.0, 0.012), mats["body_dark"], _cyl_z())
    _cyl(
        column,
        "column_shell",
        _COL_R,
        col_h - 0.024,
        (0.0, 0.0, 0.012 + (col_h - 0.024) / 2),
        mats["body"],
        _cyl_z(),
    )
    _cyl(
        column, "cap_band", _COL_R + 0.002, 0.012, (0.0, 0.0, col_h - 0.006), mats["trim"], _cyl_z()
    )
    _cyl(
        column, "top_cap", _COL_R + 0.003, 0.008, (0.0, 0.0, col_h + 0.004), mats["metal"], _cyl_z()
    )
    model.articulation(
        "tray_to_column",
        ArticulationType.FIXED,
        parent=tray,
        child=column,
        origin=Origin(xyz=(col_x, 0.0, z0 + _PLATE_TOP_Z)),
    )

    mount_parent = column
    mount_parent_name = "tower_column"
    faucet_mounts: list[tuple[tuple[float, float, float], float]] = []
    # Multiple faucets need a wide header bar to mount on (a thin column can
    # only support a single centered faucet); single faucet mounts on the column.
    use_header = r.faucet_count >= 2
    if use_header:
        # T-style header box across the front of the column (S3).
        header = model.part("header_box")
        head_y = r.tray_y * 0.92
        _box(header, "header_shell", (0.10, head_y, 0.10), (0.0, 0.0, 0.0), mats["body"])
        model.articulation(
            "column_to_header",
            ArticulationType.FIXED,
            parent=column,
            child=header,
            origin=Origin(xyz=(0.0, 0.0, col_h - 0.05)),
        )
        mount_parent = header
        mount_parent_name = "header_box"
        # faucets mount on the header front face (-X? front is +X) -> +X face
        fz = 0.0  # header-local
        for y in r.faucet_ys:
            faucet_mounts.append(((0.05, y, fz), 0.0))
    else:
        # faucets mount on the column front, faucet axis at faucet_local_z.
        # column-local z = body-local faucet z minus the column joint z (z0+plate_top).
        fz = r.faucet_local_z - _PLATE_TOP_Z
        for y in r.faucet_ys:
            faucet_mounts.append(((_COL_R - 0.004, y, fz), 0.0))

    # top collar (for inverted_top_bottle); collar_seat is column-local.
    collar_seat = None
    if r.base_reservoir == "inverted_top_bottle":
        _cyl(
            column, "bottle_collar", 0.030, 0.024, (0.0, 0.0, col_h + 0.018), mats["trim"], _cyl_z()
        )
        # bottle neck (z=0..0.018) seats just inside the collar bore.
        collar_seat = (0.0, 0.0, col_h + 0.014)

    column.inertial = Inertial.from_geometry(
        Cylinder(radius=_COL_R, length=col_h), mass=3.0, origin=Origin(xyz=(0.0, 0.0, col_h / 2))
    )
    tray.inertial = Inertial.from_geometry(
        Box((r.tray_x, r.tray_y, _TRAY_H)),
        mass=2.0,
        origin=Origin(xyz=(0.0, 0.0, z0 + _TRAY_H / 2)),
    )
    return BodyAnchors(
        root=tray,
        mount_parent=mount_parent,
        mount_parent_name=mount_parent_name,
        faucet_mounts=faucet_mounts,
        collar_seat=collar_seat,
        collar_parent=column,
        tray_part=tray,
        tray_seat=(0.0, 0.0, z0),
        alcove_tap_bodies=[],
    )


def _build_bottled_cooler_cabinet(model, r, mats, anchors_root: Part, *, z0: float) -> BodyAnchors:
    """Solid cabinet shell with front alcove; faucets hang from alcove ceiling."""
    cab = anchors_root
    fs = r.body_footprint_scale
    hs = r.body_height_scale
    cx, cy, ch = _CAB_X * fs, _CAB_Y * fs, _CAB_H * hs
    # main shell (4 walls + floor + ceiling around a front alcove)
    _box(cab, "cabinet_floor", (cx, cy, 0.02), (0.0, 0.0, z0 + 0.01), mats["body"])
    _box(cab, "cabinet_back", (0.04, cy, ch), (-cx / 2 + 0.02, 0.0, z0 + ch / 2), mats["body"])
    _box(cab, "cabinet_left", (cx, 0.03, ch), (0.0, cy / 2 - 0.015, z0 + ch / 2), mats["body"])
    _box(cab, "cabinet_right", (cx, 0.03, ch), (0.0, -cy / 2 + 0.015, z0 + ch / 2), mats["body"])
    _box(cab, "cabinet_top", (cx, cy, 0.03), (0.0, 0.0, z0 + ch - 0.015), mats["body"])
    # Front fascia frames the dispenser alcove so the cooler reads as a closed
    # cabinet with one recessed opening instead of a large hollow box.
    alcove_w = cy * _COOLER_ALCOVE_W_FRAC
    alcove_bottom_z = z0 + _COOLER_ALCOVE_BOTTOM_FRAC * ch
    alcove_ceil_z = z0 + _COOLER_ALCOVE_CEIL_FRAC * ch
    front_t = 0.012
    front_x = cx / 2 - front_t / 2
    side_w = max(0.012, (cy - alcove_w) / 2.0)
    _box(
        cab,
        "front_lower_panel",
        (front_t, cy, alcove_bottom_z - z0),
        (front_x, 0.0, z0 + (alcove_bottom_z - z0) / 2.0),
        mats["body"],
    )
    _box(
        cab,
        "front_upper_panel",
        (front_t, cy, z0 + ch - alcove_ceil_z),
        (front_x, 0.0, alcove_ceil_z + (z0 + ch - alcove_ceil_z) / 2.0),
        mats["body"],
    )
    _box(
        cab,
        "front_left_jamb",
        (front_t, side_w, alcove_ceil_z - alcove_bottom_z),
        (front_x, alcove_w / 2.0 + side_w / 2.0, (alcove_bottom_z + alcove_ceil_z) / 2.0),
        mats["body"],
    )
    _box(
        cab,
        "front_right_jamb",
        (front_t, side_w, alcove_ceil_z - alcove_bottom_z),
        (front_x, -alcove_w / 2.0 - side_w / 2.0, (alcove_bottom_z + alcove_ceil_z) / 2.0),
        mats["body"],
    )
    _box(
        cab,
        "front_control_panel",
        (0.006, alcove_w * 0.44, 0.038),
        (cx / 2 + 0.003, 0.0, alcove_ceil_z + 0.065),
        mats["body_dark"],
    )
    _box(
        cab,
        "front_status_light",
        (0.008, alcove_w * 0.15, 0.014),
        (cx / 2 + 0.007, -alcove_w * 0.16, alcove_ceil_z + 0.065),
        mats["accent"],
    )
    for k in range(2):
        _box(
            cab,
            f"front_round_button_{k}",
            (0.008, 0.014, 0.014),
            (cx / 2 + 0.007, alcove_w * (0.09 + 0.12 * k), alcove_ceil_z + 0.065),
            mats["trim"],
        )
    # alcove ceiling block (front upper) — faucets hang from its underside.
    # Spans from the back wall to the front so it connects to the shell.
    alcove_len = cx * 0.98
    _box(
        cab,
        "alcove_ceiling",
        (alcove_len, alcove_w, 0.05),
        (cx / 2 - alcove_len / 2, 0.0, alcove_ceil_z + 0.025),
        mats["body"],
    )
    # control panel + LED readout above the alcove (rest on the alcove ceiling top).
    _box(
        cab,
        "control_panel",
        (cx * 0.5, cy * 0.5, 0.03),
        (cx * 0.18, 0.0, alcove_ceil_z + 0.05 + 0.014),
        mats["body_dark"],
    )
    _box(
        cab,
        "led_readout",
        (cx * 0.2, cy * 0.18, 0.012),
        (cx * 0.18, 0.0, alcove_ceil_z + 0.05 + 0.028),
        mats["accent"],
    )
    for k in range(4):
        _box(
            cab,
            f"side_vent_{k}",
            (cx * 0.4, 0.004, 0.006),
            (-cx * 0.05, cy / 2 - 0.002, z0 + ch * 0.30 + k * 0.02),
            mats["body_dark"],
        )

    # Built-in alcove tray.  Even when the slot choice is removable_drip_tray,
    # cooler seeds keep the tray inside the cabinet with no tray joint.
    gx, gy = cx * 0.40, cy * 0.62
    grille_x = cx * 0.28  # under the alcove spouts
    _box(
        cab,
        "drip_grille_pan",
        (gx, gy, 0.012),
        (grille_x, 0.0, z0 + 0.024),
        mats["body_dark"],
    )
    _box(
        cab,
        "drip_grille_plate",
        (gx - 0.02, gy - 0.02, 0.006),
        (grille_x, 0.0, z0 + 0.030),
        mats["trim"],
    )

    # bottle collar on top
    collar_seat = None
    if r.base_reservoir == "inverted_top_bottle":
        collar_geom = LatheGeometry(
            [(0.040, 0.0), (0.044, 0.006), (0.030, 0.022), (0.027, 0.030)], segments=40
        )
        cab.visual(
            mesh_from_geometry(collar_geom, "bottle_collar"),
            origin=Origin(xyz=(cx * 0.0, 0.0, z0 + ch)),
            material=mats["trim"],
            name="bottle_collar", material_class_id=("metal.chrome_polished" if r.palette_style in {"matte_black_chrome", "white_cooler", "copper_urn", "pastel_dispenser"} else "metal.brushed_silver"),
        )
        collar_seat = (0.0, 0.0, z0 + ch + 0.010)

    cab.inertial = Inertial.from_geometry(
        Box((cx, cy, ch)), mass=14.0, origin=Origin(xyz=(0.0, 0.0, z0 + ch / 2))
    )

    # faucet mounts: alcove ceiling underside, paddle taps centered around Y.
    faucet_mounts: list[tuple[tuple[float, float, float], float]] = []
    alcove_tap_bodies: list[str] = []
    # cabinet-local faucet z (cabinet authored from z0).
    fz = z0 + r.faucet_local_z
    for i, y in enumerate(r.faucet_ys):
        faucet_mounts.append(((cx * 0.30, y, fz), 0.0))
    return BodyAnchors(
        root=cab,
        mount_parent=cab,
        mount_parent_name="cabinet",
        faucet_mounts=faucet_mounts,
        collar_seat=collar_seat,
        collar_parent=cab,
        tray_part=None,
        tray_seat=(cx * 0.20, 0.0, z0 + 0.06),
        alcove_tap_bodies=alcove_tap_bodies,
    )


def _build_cylindrical_urn(model, r, mats, anchors_root: Part, *, z0: float) -> BodyAnchors:
    """Lathe base platform (root) + lathe urn barrel (FIXED), radial faucets."""
    base = anchors_root
    base.visual(
        mesh_from_geometry(_urn_base_geometry(r), "urn_base"),
        origin=Origin(xyz=(0.0, 0.0, z0)),
        material=mats["body_dark"],
        name="urn_base", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"brushed_steel", "matte_black_chrome", "copper_urn"} else "plastic.opaque_glossy_molded"),
    )
    fs = r.body_footprint_scale
    hs = r.body_height_scale
    urn_h = _URN_H * hs
    urn = model.part("urn")
    urn.visual(
        mesh_from_geometry(_urn_shell_geometry(r), "urn_shell"),
        material=mats["body"],
        name="urn_shell", material_class_id=("plastic.opaque_glossy_molded" if r.palette_style in {"white_cooler", "pastel_dispenser"} else "metal.blackened_gunmetal"),
    )
    # band, lid, knob (parent visuals)
    _cyl(
        urn,
        "urn_band",
        _URN_R_BELLY * fs + 0.004,
        0.014,
        (0.0, 0.0, urn_h * 0.45),
        mats["trim"],
        _cyl_z(),
    )
    _cyl(
        urn,
        "urn_lid",
        _URN_R_TOP * fs + 0.002,
        0.010,
        (0.0, 0.0, urn_h + 0.005),
        mats["trim"],
        _cyl_z(),
    )
    _cyl(urn, "urn_knob", 0.012, 0.018, (0.0, 0.0, urn_h + 0.018), mats["metal"], _cyl_z())
    model.articulation(
        "base_to_urn",
        ArticulationType.FIXED,
        parent=base,
        child=urn,
        origin=Origin(xyz=(0.0, 0.0, z0 + 0.024)),
    )

    base.inertial = Inertial.from_geometry(
        Cylinder(radius=_URN_R_BELLY * fs, length=0.028),
        mass=2.0,
        origin=Origin(xyz=(0.0, 0.0, z0)),
    )
    urn.inertial = Inertial.from_geometry(
        Cylinder(radius=_URN_R_BELLY * fs, length=urn_h),
        mass=8.0,
        origin=Origin(xyz=(0.0, 0.0, urn_h / 2)),
    )

    # radial faucet mounts on the belly (urn-local frame, base offset 0.024).
    fz_urn = r.faucet_local_z - 0.024
    mount_r = r.mount_radius
    faucet_mounts: list[tuple[tuple[float, float, float], float]] = []
    for angle in r.faucet_angles:
        mx = mount_r * math.cos(angle)
        my = mount_r * math.sin(angle)
        faucet_mounts.append(((mx, my, fz_urn), angle))
    return BodyAnchors(
        root=base,
        mount_parent=urn,
        mount_parent_name="urn",
        faucet_mounts=faucet_mounts,
        collar_seat=None,
        collar_parent=None,
        tray_part=None,
        tray_seat=(0.0, 0.0, z0),
        alcove_tap_bodies=[],
    )


# ---------------------------------------------------------------------------
# Faucet + tap_type (multiplicity copy)
# ---------------------------------------------------------------------------
def _emit_faucet_body(part: Part, r, mats) -> None:
    """Shared faucet body mesh: shank cylinder + flange + bonnet + curved spout."""
    body = (
        CylinderGeometry(_BODY_R, _SHANK_X1 - _SHANK_X0, radial_segments=24)
        .rotate_y(math.pi / 2.0)
        .translate((_SHANK_X0 + _SHANK_X1) / 2.0, 0.0, 0.0)
    )
    flange = (
        CylinderGeometry(0.0165, 0.012, radial_segments=24)
        .rotate_y(math.pi / 2.0)
        .translate(0.004, 0.0, 0.0)
    )
    body.merge(flange)
    part.visual(mesh_from_geometry(body, "faucet_body"), material=mats["metal"], name="faucet_body", material_class_id=("metal.chrome_polished" if r.palette_style in {"matte_black_chrome", "white_cooler", "copper_urn", "pastel_dispenser"} else "metal.brushed_silver"))
    bonnet = CylinderGeometry(0.012, 0.019, radial_segments=24).translate(_BONNET_X, 0.0, 0.0175)
    bonnet.merge(
        CylinderGeometry(0.0145, 0.005, radial_segments=24).translate(_BONNET_X, 0.0, 0.0105)
    )
    part.visual(
        mesh_from_geometry(bonnet, "faucet_bonnet"), material=mats["metal"], name="faucet_bonnet", material_class_id=("metal.chrome_polished" if r.palette_style in {"matte_black_chrome", "white_cooler", "copper_urn", "pastel_dispenser"} else "metal.brushed_silver")
    )
    spout = _spout_geometry()
    part.visual(
        mesh_from_geometry(spout, "faucet_spout"), material=mats["metal"], name="faucet_spout", material_class_id=("metal.chrome_polished" if r.palette_style in {"matte_black_chrome", "white_cooler", "copper_urn", "pastel_dispenser"} else "metal.brushed_silver")
    )


def _build_faucets(model, r, mats, anchors: BodyAnchors) -> None:
    parent = anchors.mount_parent
    n = r.faucet_count
    for i in range(n):
        (mx, my, mz), yaw = anchors.faucet_mounts[i]
        suffix = "" if n == 1 else f"_{i}"
        faucet = model.part(f"faucet{suffix}")
        if r.tap_type == "paddle":
            # alcove tap body that the paddle hinge captures; no horizontal faucet shank.
            _cyl(faucet, "tap_body", 0.016, 0.05, (0.0, 0.0, -0.025), mats["metal"], _cyl_z())
            _cyl(faucet, "tap_ring", 0.020, 0.008, (0.0, 0.0, 0.004), mats["trim"], _cyl_z())
            # short downward spout nozzle, overlapping the tap_body bottom for connection.
            _cyl(faucet, "tap_spout", 0.007, 0.024, (0.0, 0.0, -0.050), mats["metal"], _cyl_z())
        else:
            _emit_faucet_body(faucet, r, mats)
        model.articulation(
            f"body_to_faucet{suffix}",
            ArticulationType.FIXED,
            parent=parent,
            child=faucet,
            origin=Origin(xyz=(mx, my, mz), rpy=(0.0, 0.0, yaw)),
        )
        faucet.inertial = Inertial.from_geometry(
            Cylinder(radius=_BODY_R, length=_SHANK_X1 - _SHANK_X0),
            mass=0.30,
            origin=Origin(xyz=(0.03, 0.0, 0.0), rpy=_cyl_x()),
        )
        _build_tap_mechanism(model, r, mats, faucet, suffix)


def _build_tap_mechanism(model, r, mats, faucet: Part, suffix: str) -> None:
    if r.tap_type == "push_lever":
        handle = model.part(f"tap_handle{suffix}")
        _cyl(handle, "lever_collar", 0.013, 0.020, (0.0, 0.0, 0.0), mats["metal"], _cyl_z())
        _box(handle, "lever_grip", (0.012, 0.018, 0.070), (0.0, 0.0, 0.040), mats["grip"])
        model.articulation(
            f"faucet_lever{suffix}",
            ArticulationType.REVOLUTE,
            parent=faucet,
            child=handle,
            origin=Origin(xyz=(_BONNET_X, 0.0, _PIVOT_Z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=3.0, lower=0.0, upper=r.lever_open),
        )
        handle.inertial = Inertial.from_geometry(
            Box((0.012, 0.018, 0.070)), mass=0.05, origin=Origin(xyz=(0.0, 0.0, 0.04))
        )
    elif r.tap_type == "push_button":
        bonnet_top_z = 0.0175 + 0.019 / 2.0
        # bezel trim on faucet (parent visual)
        bezel = LatheGeometry(
            [
                (0.010, -0.002),
                (0.018, -0.001),
                (0.018, 0.005),
                (0.010, 0.006),
            ],
            segments=32,
        ).translate(_BONNET_X, 0.0, bonnet_top_z)
        faucet.visual(
            mesh_from_geometry(bezel, "button_bezel"), material=mats["metal"], name="button_bezel", material_class_id=("metal.chrome_polished" if r.palette_style in {"matte_black_chrome", "white_cooler", "copper_urn", "pastel_dispenser"} else "metal.brushed_silver")
        )
        button = model.part(f"push_button{suffix}")
        stem = CylinderGeometry(0.009, 0.022, radial_segments=24).translate(0.0, 0.0, -0.010)
        button.visual(
            mesh_from_geometry(stem, "button_stem"), material=mats["metal"], name="button_stem", material_class_id=("metal.chrome_polished" if r.palette_style in {"matte_black_chrome", "white_cooler", "copper_urn", "pastel_dispenser"} else "metal.brushed_silver")
        )
        cap = LatheGeometry(
            [(0.0, 0.016), (0.010, 0.014), (0.014, 0.010), (0.0145, 0.0), (0.0, 0.0)],
            segments=32,
        )
        button.visual(
            mesh_from_geometry(cap, "button_cap"), material=mats["grip"], name="button_cap", material_class_id="rubber.smooth_plain"
        )
        model.articulation(
            f"faucet_button{suffix}",
            ArticulationType.PRISMATIC,
            parent=faucet,
            child=button,
            origin=Origin(xyz=(_BONNET_X, 0.0, bonnet_top_z + 0.006)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=8.0, velocity=0.5, lower=0.0, upper=r.button_travel),
        )
        button.inertial = Inertial.from_geometry(
            Cylinder(radius=0.014, length=0.024), mass=0.03, origin=Origin(xyz=(0.0, 0.0, 0.0))
        )
    elif r.tap_type == "twist_spigot":
        spigot = model.part(f"spigot_knob{suffix}")
        # stem collar capturing bonnet + lobed knob (KnobGeometry mesh, +X axis)
        stem = (
            CylinderGeometry(0.010, 0.030, radial_segments=24)
            .rotate_y(math.pi / 2.0)
            .translate(0.015, 0.0, 0.0)
        )
        spigot.visual(
            mesh_from_geometry(stem, "spigot_stem"), material=mats["metal"], name="spigot_stem", material_class_id=("metal.chrome_polished" if r.palette_style in {"matte_black_chrome", "white_cooler", "copper_urn", "pastel_dispenser"} else "metal.brushed_silver")
        )
        knob = _knob_geometry().translate(0.040, 0.0, 0.0)
        spigot.visual(
            mesh_from_geometry(knob, "spigot_knob"), material=mats["grip"], name="spigot_knob", material_class_id="rubber.smooth_plain"
        )
        model.articulation(
            f"faucet_spigot{suffix}",
            ArticulationType.REVOLUTE,
            parent=faucet,
            child=spigot,
            origin=Origin(xyz=(_BONNET_X, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=3.0, velocity=4.0, lower=0.0, upper=r.spigot_open),
        )
        spigot.inertial = Inertial.from_geometry(
            Cylinder(radius=0.020, length=0.040),
            mass=0.04,
            origin=Origin(xyz=(0.03, 0.0, 0.0), rpy=_cyl_x()),
        )
    elif r.tap_type == "paddle":
        paddle = model.part(f"paddle{suffix}")
        # hinge barrel along Y captured in the tap_body; paddle plate hangs down.
        _cyl(paddle, "hinge_barrel", 0.010, 0.040, (0.0, 0.0, 0.0), mats["metal"], _cyl_y())
        _box(paddle, "paddle_plate", (0.022, 0.034, 0.060), (0.012, 0.0, -0.032), mats["grip"])
        model.articulation(
            f"paddle_hinge{suffix}",
            ArticulationType.REVOLUTE,
            parent=faucet,
            child=paddle,
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, -_PADDLE_REST_TILT, 0.0)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=r.paddle_open),
        )
        paddle.inertial = Inertial.from_geometry(
            Box((0.022, 0.034, 0.060)), mass=0.04, origin=Origin(xyz=(0.012, 0.0, -0.032))
        )


# ---------------------------------------------------------------------------
# Slot C: base_reservoir extras (floor pedestal, removable tray, top bottle)
# ---------------------------------------------------------------------------
def _build_pedestal(model, r, mats) -> Part:
    """Floor-standing pedestal cabinet (new root); body tree stacks FIXED on top."""
    ped = model.part("pedestal_cabinet")
    fs = r.body_footprint_scale
    hs = r.body_height_scale
    px, py, ph = _PED_X * fs, _PED_Y * fs, _PED_H * hs
    toe = 0.05
    _box(ped, "toe_kick", (px * 0.9, py * 0.9, toe), (0.0, 0.0, toe / 2), mats["body_dark"])
    _box(ped, "pedestal_shell", (px, py, ph - toe), (0.0, 0.0, toe + (ph - toe) / 2), mats["body"])
    _box(ped, "top_plate", (px, py, 0.02), (0.0, 0.0, ph - 0.01), mats["trim"])
    _box(
        ped,
        "front_door_panel",
        (0.006, py * 0.7, ph * 0.55),
        (px / 2 - 0.003, 0.0, toe + (ph - toe) * 0.5),
        mats["body_dark"],
    )
    _box(
        ped,
        "door_handle",
        (0.012, 0.04, 0.012),
        (px / 2 + 0.006, py * 0.22, toe + (ph - toe) * 0.55),
        mats["metal"],
    )
    ped.inertial = Inertial.from_geometry(
        Box((px, py, ph)), mass=18.0, origin=Origin(xyz=(0.0, 0.0, ph / 2))
    )
    return ped


def _build_removable_tray(model, r, mats, anchors: BodyAnchors) -> Part:
    """Drip tray as a horizontal PRISMATIC pull-out that slides straight OUT (+X)
    toward the user — a real catch tray never rises into the faucet/ceiling.

    * rectangular_box: this pull-out *is* the single catch basin, sized to span
      the footprint front and centered under the spout drip line (the root is a
      plain plinth, so there is no second basin).
    * cooler / urn: a compact catch grille seated at the alcove / base front.
    """
    tray = model.part("pullout_tray")

    if r.body_form == "rectangular_box":
        # Single full catch basin, centered under the spouts and forward of the
        # rear column so it clears it through its whole travel.
        col_front = -r.tray_x * 0.27 + _COL_R * 1.45  # front-most column geometry (root frame)
        region_rear = col_front + 0.012
        region_front = r.tray_x / 2.0 - 0.006
        tx = region_front - region_rear
        ty = r.tray_y * 0.86
        front_x = 0.5 * (region_rear + region_front)
        root_top = _PLATE_TOP_Z  # base plinth top
        seat_z = root_top - 0.002  # rim rests on the solid plinth top (2 mm embed)
    elif r.body_form == "cylindrical_urn":
        tx = 0.10
        ty = 0.20 * 0.65
        front_x = r.mount_radius * 0.55
        root_top = 0.028 * r.body_height_scale
        seat_z = root_top - 0.004 - 0.002  # tray floor embeds 2 mm into the base top
    else:  # bottled_cooler_cabinet
        cx = _CAB_X * r.body_footprint_scale
        tx = 0.10
        ty = 0.13
        front_x = cx * 0.30  # under the alcove spouts
        root_top = 0.020  # cabinet floor top surface
        seat_z = root_top - 0.004 - 0.002

    _box(tray, "tray_rim", (tx, ty, 0.018), (0.0, 0.0, 0.009), mats["body"])
    _box(tray, "tray_floor", (tx - 0.02, ty - 0.02, 0.006), (0.0, 0.0, 0.004), mats["body_dark"])
    _box(
        tray,
        "tray_perforated_plate",
        (tx - 0.03, ty - 0.03, 0.004),
        (0.0, 0.0, 0.016),
        mats["trim"],
    )

    # Horizontal pull-out toward the front: slides +X only, never rises.
    model.articulation(
        "tray_slide",
        ArticulationType.PRISMATIC,
        parent=anchors.root,
        child=tray,
        origin=Origin(xyz=(front_x, 0.0, seat_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=25.0, velocity=0.4, lower=0.0, upper=r.tray_travel),
    )
    tray.inertial = Inertial.from_geometry(
        Box((tx, ty, 0.02)), mass=0.5, origin=Origin(xyz=(0.0, 0.0, 0.01))
    )
    return tray


def _build_top_bottle(model, r, mats, anchors: BodyAnchors) -> Part:
    bottle = model.part("water_bottle")
    bottle.visual(
        mesh_from_geometry(_bottle_geometry(), "bottle_shell"),
        material=mats["water"],
        name="bottle_shell", material_class_id="plastic.clear_rigid",
    )
    # collar_seat is in the collar_parent's local frame; bottle is FIXED to it
    # so the neck (z=0..0.018) seats into the collar bore.
    collar_parent = anchors.collar_parent or anchors.mount_parent
    seat = anchors.collar_seat or (0.0, 0.0, r.body_top_local_z)
    model.articulation(
        "body_to_bottle",
        ArticulationType.FIXED,
        parent=collar_parent,
        child=bottle,
        origin=Origin(xyz=seat),
    )
    bottle.inertial = Inertial.from_geometry(
        Cylinder(radius=0.135, length=0.49), mass=4.0, origin=Origin(xyz=(0.0, 0.0, 0.245))
    )
    return bottle


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------
def build_water_dispenser(
    config: WaterDispenserConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or WaterDispenserConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = _register_materials(model, r.palette_style)

    # root part: pedestal cabinet, else the body_form's own root.
    pedestal: Part | None = None
    if r.base_reservoir == "floor_standing_pedestal":
        pedestal = _build_pedestal(model, r, mats)

    # body_form root part name differs; create it then stack on pedestal if needed.
    if r.body_form == "cylindrical_urn":
        root = model.part("base")
    elif r.body_form == "bottled_cooler_cabinet":
        root = model.part("cabinet")
    else:
        root = model.part("drip_tray")

    z0 = 0.0  # body tree authored from z0; pedestal stack handled via FIXED joint below
    if r.body_form == "rectangular_box":
        anchors = _build_rectangular_box(model, r, mats, root, z0=z0)
    elif r.body_form == "bottled_cooler_cabinet":
        anchors = _build_bottled_cooler_cabinet(model, r, mats, root, z0=z0)
    else:
        anchors = _build_cylindrical_urn(model, r, mats, root, z0=z0)

    # If on a pedestal, stack the body root onto the pedestal top.
    if pedestal is not None:
        model.articulation(
            "pedestal_to_body",
            ArticulationType.FIXED,
            parent=pedestal,
            child=anchors.root,
            origin=Origin(xyz=(0.0, 0.0, r.base_z)),
        )

    _build_faucets(model, r, mats, anchors)

    if r.base_reservoir == "removable_drip_tray" and r.body_form != "bottled_cooler_cabinet":
        _build_removable_tray(model, r, mats, anchors)
    elif r.base_reservoir == "inverted_top_bottle":
        _build_top_bottle(model, r, mats, anchors)

    return model


def build_seeded_water_dispenser(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_water_dispenser(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _allow(ctx, a, b, ea, eb, reason):
    try:
        ctx.allow_overlap(a, b, elem_a=ea, elem_b=eb, reason=reason)
    except Exception:
        pass


_FAUCET_ELEMS = (
    "faucet_body",
    "faucet_bonnet",
    "faucet_spout",
    "button_bezel",
    "tap_body",
    "tap_ring",
    "tap_spout",
)
_MOUNT_ELEMS = (
    "column_shell",
    "cap_band",
    "top_cap",
    "base_skirt",
    "header_shell",
    "alcove_ceiling",
    "cabinet_top",
    "cabinet_back",
    "cabinet_left",
    "cabinet_right",
    "cabinet_floor",
    "urn_shell",
    "urn_band",
    "urn_lid",
    "bottle_collar",
)


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject, r) -> None:
    parts = {p.name for p in model.parts}
    n = r.faucet_count

    def part(name):
        return model.get_part(name) if name in parts else None

    # mount parent = the part the faucets are FIXED to (header preferred over
    # column for rect N>=3; cabinet / urn otherwise).  Allow the faucet shank to
    # pass into ANY present body part it might brush.
    mount_names = ("header_box", "cabinet", "urn", "tower_column")
    mount_candidates = [part(m) for m in mount_names if part(m)]

    # header box FIXED-stacked on the column (captured seat).
    column = part("tower_column")
    header = part("header_box")
    if column is not None and header is not None:
        for he in ("header_shell",):
            for ce in ("column_shell", "cap_band", "top_cap"):
                _allow(ctx, header, column, he, ce, "T-header box seats over the column top")

    for i in range(n):
        suffix = "" if n == 1 else f"_{i}"
        faucet = part(f"faucet{suffix}")
        if faucet is None:
            continue
        # faucet shank passes into the mount parent wall (captured pass-through).
        for mc in mount_candidates:
            for fe in _FAUCET_ELEMS:
                for me in _MOUNT_ELEMS:
                    _allow(ctx, faucet, mc, fe, me, "faucet shank seated into the body wall")
        # tap mechanism children captured on the faucet bonnet / tap body.
        for child_name, child_elems in (
            (f"tap_handle{suffix}", ("lever_collar", "lever_grip")),
            (f"push_button{suffix}", ("button_stem", "button_cap")),
            (f"spigot_knob{suffix}", ("spigot_stem", "spigot_knob")),
            (f"paddle{suffix}", ("hinge_barrel", "paddle_plate")),
        ):
            child = part(child_name)
            if child is None:
                continue
            for fe in (
                "faucet_bonnet",
                "faucet_body",
                "faucet_spout",
                "button_bezel",
                "tap_body",
                "tap_ring",
                "tap_spout",
            ):
                for ce in child_elems:
                    _allow(
                        ctx, child, faucet, ce, fe, "tap mechanism captured on the faucet bonnet"
                    )
            # tap mechanism may also brush the body it hangs from (e.g. a button
            # cap poking up into the cabinet alcove ceiling).
            for mc in mount_candidates:
                for me in _MOUNT_ELEMS:
                    for ce in child_elems:
                        _allow(ctx, child, mc, ce, me, "tap mechanism sits against the body wall")

    # inverted bottle neck captured in collar (on the column / cabinet top).
    bottle = part("water_bottle")
    if bottle is not None:
        for host_name in ("tower_column", "cabinet"):
            host = part(host_name)
            if host is None:
                continue
            for me in ("bottle_collar", "cabinet_top", "top_cap", "cap_band", "column_shell"):
                _allow(
                    ctx,
                    bottle,
                    host,
                    "bottle_shell",
                    me,
                    "inverted bottle neck seats in the collar bore",
                )

    # removable pull-out tray rests on / slides into the body base.
    tray = part("pullout_tray")
    if tray is not None:
        tray_elems = ("tray_rim", "tray_floor", "tray_perforated_plate")
        root_elems = (
            "tray_floor",
            "tray_perforated_plate",
            "tray_wall_front",
            "cabinet_floor",
            "cabinet_back",
            "urn_base",
            "urn_shell",
            "urn_band",
        )
        for root_name in ("drip_tray", "base", "cabinet", "urn"):
            root = part(root_name)
            if root is None:
                continue
            for te in tray_elems:
                for re_ in root_elems:
                    _allow(
                        ctx,
                        tray,
                        root,
                        te,
                        re_,
                        "removable tray rests on and slides into the body base",
                    )


def run_water_dispenser_tests(
    object_model: ArticulatedObject,
    config: WaterDispenserConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model, r)
    if "pullout_tray" in {p.name for p in object_model.parts}:
        ctx.allow_isolated_part(
            object_model.get_part("pullout_tray"),
            reason="pull-out tray slides clear of the dispenser body and loses contact",
        )
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()

    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.joints}

    # identity: a grounded body + at least one faucet + tap mechanism.
    if not any(n in part_names for n in ("drip_tray", "base", "cabinet", "pedestal_cabinet")):
        ctx.fail("identity_body", "water dispenser must have a grounded body/tray/cabinet")
    faucet_parts = [n for n in part_names if n == "faucet" or n.startswith("faucet_")]
    paddle_parts = [n for n in part_names if n == "tap_body" or n.startswith("paddle")]
    if not faucet_parts and not paddle_parts:
        ctx.fail("identity_faucet", "water dispenser must expose at least one faucet")

    # tap mechanism articulation present per faucet.
    tap_joint_prefix = {
        "push_lever": "faucet_lever",
        "push_button": "faucet_button",
        "twist_spigot": "faucet_spigot",
        "paddle": "paddle_hinge",
    }[r.tap_type]
    tap_joints = [j for j in object_model.joints if j.name.startswith(tap_joint_prefix)]
    if len(tap_joints) != r.faucet_count:
        ctx.fail(
            "tap_count",
            f"expected {r.faucet_count} {r.tap_type} joints, got {len(tap_joints)}",
        )
    for j in tap_joints:
        if r.tap_type == "push_button":
            if j.articulation_type != ArticulationType.PRISMATIC:
                ctx.fail("tap_joint_type", f"{j.name} must be PRISMATIC")
        else:
            if j.articulation_type != ArticulationType.REVOLUTE:
                ctx.fail("tap_joint_type", f"{j.name} must be REVOLUTE")

    # base_reservoir specific joints.
    if r.base_reservoir == "removable_drip_tray":
        if r.body_form == "bottled_cooler_cabinet":
            if any(n in joint_names for n in ("tray_slide", "drip_tray_lift")):
                ctx.fail("tray_joint", "cooler alcove tray must remain static inside the cabinet")
            if "pullout_tray" in part_names:
                ctx.fail("tray_part", "cooler alcove tray should be a cabinet visual, not a moving part")
        elif not any(n in joint_names for n in ("tray_slide", "drip_tray_lift")):
            ctx.fail("tray_joint", "removable drip tray must have a PRISMATIC joint")
    if r.base_reservoir == "inverted_top_bottle":
        if "body_to_bottle" not in joint_names:
            ctx.fail("bottle_joint", "inverted top bottle must be FIXED to the body")
    if r.base_reservoir == "floor_standing_pedestal":
        if "pedestal_to_body" not in joint_names:
            ctx.fail("pedestal_joint", "floor pedestal must stack the body FIXED on top")

    # lock-in: the removable drip tray pulls straight OUT horizontally and never
    # rises into the faucet (regression guard against the old +Z-lift bug).
    if (
        r.base_reservoir == "removable_drip_tray"
        and r.body_form != "bottled_cooler_cabinet"
        and "pullout_tray" in part_names
    ):
        slide = next((j for j in object_model.joints if j.name == "tray_slide"), None)
        ctx.check(
            "removable tray slides on a horizontal (+X) axis",
            slide is not None and abs(slide.axis[0]) > 0.99 and abs(slide.axis[2]) < 1e-6,
            details=f"axis={getattr(slide, 'axis', None)}",
        )
        tray = object_model.get_part("pullout_tray")
        rest = ctx.part_world_aabb(tray)
        with ctx.pose({"tray_slide": r.tray_travel}):
            out = ctx.part_world_aabb(tray)
        if rest is not None and out is not None:
            dx = (out[0][0] + out[1][0]) / 2.0 - (rest[0][0] + rest[1][0]) / 2.0
            dz = (out[0][2] + out[1][2]) / 2.0 - (rest[0][2] + rest[1][2]) / 2.0
            ctx.check(
                "tray pull-out advances +X without rising",
                dx > 0.05 and abs(dz) < 0.005,
                details=f"dx={dx:.4f}, dz={dz:.4f}",
            )
            faucet_bottoms = [
                ab[0][2]
                for fn in part_names
                if fn == "faucet" or fn.startswith("faucet_")
                for ab in (ctx.part_world_aabb(object_model.get_part(fn)),)
                if ab is not None
            ]
            if faucet_bottoms:
                ctx.check(
                    "extended tray stays below the faucet (no ramming)",
                    out[1][2] < min(faucet_bottoms),
                    details=f"tray_top={out[1][2]:.4f}, faucet_bottom={min(faucet_bottoms):.4f}",
                )

    return ctx.report()


__all__ = [
    "WaterDispenserConfig",
    "ResolvedWaterDispenserConfig",
    "build_water_dispenser",
    "build_seeded_water_dispenser",
    "config_from_seed",
    "resolve_config",
    "run_water_dispenser_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
