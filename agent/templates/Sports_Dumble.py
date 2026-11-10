# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

# Modular adjustable dumbbell.
#
# Frame: handle axis along +X, midpoint at the origin (x=0 = bar center).
# Left side at -X, right side at +X. A mirrored stack of N weight plates per
# side stacks outward from the knurled grip, each stack retained by a knurled
# locking collar/nut threaded onto the exposed bar end just outboard of the
# plates.
#
# Slots:
#   A (plate shape)  : round_plate | hex_plate | dodecagonal_plate
#   B (collar lock)  : spinlock_nut | star_lock_collar | hex_jamnut_pair
#   C (grip form)    : straight_knurled_bar | contoured_ergonomic
#   multiplicity     : plates_per_side N (1..8), mirrored across x=0
#
# Articulation: exactly TWO locking collars, CONTINUOUS spin about +X (free
# spin). Plates are FIXED static visuals on the root body.
#
# Adapted from the 5-star dumbbell sources:
#   chrome parent (e0c0e76a) : round plate stack + spin-lock nut + straight grip
#   iron parent  (e9921a05)  : star-lock collar
#   var_hexplate / var_dodecaplate : faceted plate prisms
#   var_hexnut   : inner-fixed + outer-spinning hex jam-nut pair
#   var_contourgrip : lathe barrel grip
#   var_plates2/4/6 : N copy logic + thread_len growth with N

import math
import random
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    CylinderGeometry,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    Inertial,
    KnobGeometry,
    KnobGrip,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
)

__modular__ = True

PlateShape = Literal["round_plate", "hex_plate", "dodecagonal_plate"]
CollarLock = Literal["spinlock_nut", "star_lock_collar", "hex_jamnut_pair"]
GripForm = Literal["straight_knurled_bar", "contoured_ergonomic"]
PaletteStyle = Literal[
    "bright_chrome",
    "brushed_steel",
    "matte_black_iron",
    "zinc_plated",
    "gunmetal_cast",
    "polished_dumbbell",
]

PLATE_SHAPES: tuple[PlateShape, ...] = ("round_plate", "hex_plate", "dodecagonal_plate")
COLLAR_LOCKS: tuple[CollarLock, ...] = ("spinlock_nut", "star_lock_collar", "hex_jamnut_pair")
GRIP_FORMS: tuple[GripForm, ...] = ("straight_knurled_bar", "contoured_ergonomic")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "bright_chrome",
    "brushed_steel",
    "matte_black_iron",
    "zinc_plated",
    "gunmetal_cast",
    "polished_dumbbell",
)

N_MIN = 1
N_MAX = 8
# Small-N peak, long tail (real adjustable-dumbbell loadouts). N>=1.
N_WEIGHTS = (0.10, 0.20, 0.22, 0.18, 0.14, 0.08, 0.05, 0.03)

# ---- key dimensions (meters) ----
HANDLE_LEN = 0.150        # central grip section length (nominal)
HANDLE_R = 0.0150         # grip core radius
GRIP_KNURL_R = 0.0162     # knurled grip band radius

SLEEVE_R = 0.022          # shoulder collar between grip and plate stack
SLEEVE_LEN = 0.010

PLATE_R = 0.080           # plate radius (dia ~0.16 m)
PLATE_THICK = 0.012       # single plate thickness
PLATE_GAP = 0.0008        # tiny seam between plates
PLATE_HUB_R = 0.026       # raised center hub on each plate
BORE_R = 0.016            # plate center bore radius (slips over the bar)

THREAD_R = 0.0150         # threaded bar end core radius
THREAD_RIDGE_R = 0.0160   # outer radius of the thread ridges

COLLAR_DIA = 0.044        # spin-lock collar (knurled nut) outer diameter
COLLAR_LEN = 0.022        # collar length along the bar

# star-lock collar
STAR_POINTS = 6
STAR_LOBE_LEN = 0.018

# hex jam nut
HEX_FLAT = 0.040          # flat-to-flat distance across the hex nut
HEX_THICK = 0.011         # single hex-nut thickness along the bar axis
HEX_BORE_R = 0.0165       # hex-nut central bore radius

COLLAR_SEAT_OFFSET = 0.026  # spinlock/star collar seat from STACK_END (on thread)


# --------------------------------------------------------------------------- #
# Palettes
# --------------------------------------------------------------------------- #

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "bright_chrome": {
        "grip": (0.78, 0.80, 0.83, 1.0),
        "knurl": (0.52, 0.54, 0.57, 1.0),
        "sleeve": (0.66, 0.68, 0.71, 1.0),
        "plate": (0.86, 0.88, 0.90, 1.0),
        "thread": (0.66, 0.68, 0.71, 1.0),
        "collar": (0.66, 0.68, 0.71, 1.0),
        "marker": (0.92, 0.93, 0.95, 1.0),
    },
    "brushed_steel": {
        "grip": (0.66, 0.68, 0.71, 1.0),
        "knurl": (0.52, 0.54, 0.57, 1.0),
        "sleeve": (0.60, 0.62, 0.65, 1.0),
        "plate": (0.66, 0.68, 0.71, 1.0),
        "thread": (0.56, 0.58, 0.61, 1.0),
        "collar": (0.58, 0.60, 0.63, 1.0),
        "marker": (0.85, 0.86, 0.88, 1.0),
    },
    "matte_black_iron": {
        "grip": (0.62, 0.64, 0.67, 1.0),
        "knurl": (0.30, 0.31, 0.33, 1.0),
        "sleeve": (0.55, 0.57, 0.60, 1.0),
        "plate": (0.07, 0.07, 0.08, 1.0),
        "thread": (0.55, 0.57, 0.60, 1.0),
        "collar": (0.55, 0.57, 0.60, 1.0),
        "marker": (0.80, 0.12, 0.10, 1.0),
    },
    "zinc_plated": {
        "grip": (0.78, 0.80, 0.83, 1.0),
        "knurl": (0.52, 0.54, 0.57, 1.0),
        "sleeve": (0.66, 0.68, 0.71, 1.0),
        "plate": (0.86, 0.88, 0.90, 1.0),
        "thread": (0.66, 0.68, 0.71, 1.0),
        "collar": (0.72, 0.73, 0.70, 1.0),
        "marker": (0.90, 0.91, 0.86, 1.0),
    },
    "gunmetal_cast": {
        "grip": (0.40, 0.41, 0.44, 1.0),
        "knurl": (0.28, 0.29, 0.31, 1.0),
        "sleeve": (0.44, 0.45, 0.48, 1.0),
        "plate": (0.38, 0.39, 0.41, 1.0),
        "thread": (0.44, 0.45, 0.48, 1.0),
        "collar": (0.34, 0.35, 0.38, 1.0),
        "marker": (0.86, 0.60, 0.18, 1.0),
    },
    "polished_dumbbell": {
        "grip": (0.86, 0.88, 0.90, 1.0),
        "knurl": (0.62, 0.64, 0.67, 1.0),
        "sleeve": (0.82, 0.84, 0.87, 1.0),
        "plate": (0.90, 0.92, 0.94, 1.0),
        "thread": (0.78, 0.80, 0.83, 1.0),
        "collar": (0.84, 0.86, 0.89, 1.0),
        "marker": (0.96, 0.97, 0.99, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class DumbbellConfig:
    plate_shape: PlateShape = "round_plate"
    collar_lock: CollarLock = "spinlock_nut"
    grip_form: GripForm = "straight_knurled_bar"
    plates_per_side: int = 5
    palette_style: PaletteStyle = "bright_chrome"
    plate_radius_scale: float = 1.0
    plate_thick_scale: float = 1.0
    grip_len_scale: float = 1.0
    grip_mid_r_scale: float = 1.25
    name: str = "reference_dumbbell"


@dataclass(frozen=True)
class ResolvedDumbbellConfig:
    plate_shape: PlateShape
    collar_lock: CollarLock
    grip_form: GripForm
    plates_per_side: int
    palette_style: PaletteStyle
    plate_radius_scale: float
    plate_thick_scale: float
    grip_len_scale: float
    grip_mid_r_scale: float
    # derived geometry
    handle_len: float
    plate_r: float
    plate_thick: float
    grip_half: float
    sleeve_x: float
    stack_start: float
    stack_len: float
    stack_end: float
    thread_len: float
    thread_x: float
    collar_x: float
    inner_nut_center: float
    contact_face: float
    grip_mid_r: float
    name: str


def _pick(value, options):
    return value if value in options else options[0]


def config_from_seed(seed: int) -> DumbbellConfig:
    rng = random.Random(seed)
    n = rng.choices(range(N_MIN, N_MAX + 1), weights=N_WEIGHTS, k=1)[0]
    return DumbbellConfig(
        plate_shape=rng.choice(PLATE_SHAPES),
        collar_lock=rng.choice(COLLAR_LOCKS),
        grip_form=rng.choice(GRIP_FORMS),
        plates_per_side=n,
        palette_style=rng.choice(PALETTE_STYLES),
        plate_radius_scale=round(rng.uniform(0.85, 1.15), 3),
        plate_thick_scale=round(rng.uniform(0.85, 1.15), 3),
        grip_len_scale=round(rng.uniform(0.85, 1.20), 3),
        grip_mid_r_scale=round(rng.uniform(1.05, 1.45), 3),
        name=f"seeded_dumbbell_{seed}",
    )


def resolve_config(config: DumbbellConfig) -> ResolvedDumbbellConfig:
    plate_shape = _pick(config.plate_shape, PLATE_SHAPES)
    collar_lock = _pick(config.collar_lock, COLLAR_LOCKS)
    grip_form = _pick(config.grip_form, GRIP_FORMS)
    palette_style = _pick(config.palette_style, PALETTE_STYLES)

    n = int(config.plates_per_side)
    if n < N_MIN or n > N_MAX:
        raise ValueError(f"plates_per_side must be in [{N_MIN},{N_MAX}]")

    prs = min(1.15, max(0.85, config.plate_radius_scale))
    pts = min(1.15, max(0.85, config.plate_thick_scale))
    gls = min(1.20, max(0.85, config.grip_len_scale))
    gmrs = min(1.45, max(1.05, config.grip_mid_r_scale))

    handle_len = HANDLE_LEN * gls
    plate_r = PLATE_R * prs
    plate_thick = PLATE_THICK * pts

    grip_half = handle_len / 2.0
    sleeve_x = grip_half + SLEEVE_LEN / 2.0
    stack_start = grip_half + SLEEVE_LEN
    stack_len = n * plate_thick + (n - 1) * PLATE_GAP
    stack_end = stack_start + stack_len

    # Collar seat / contact face: where the lock seats just outboard of the stack.
    if collar_lock == "hex_jamnut_pair":
        inner_nut_center = stack_end + HEX_THICK / 2.0
        contact_face = stack_end + HEX_THICK
        # outer hex nut spans contact_face..contact_face+HEX_THICK
        collar_outboard = contact_face + HEX_THICK
        collar_x = contact_face  # joint origin (also used for thread length sizing)
        seat_half = HEX_THICK  # inner + outer span past stack_end
    else:
        inner_nut_center = 0.0
        contact_face = 0.0
        collar_x = stack_end + COLLAR_SEAT_OFFSET
        collar_outboard = collar_x + COLLAR_LEN / 2.0
        seat_half = COLLAR_SEAT_OFFSET + COLLAR_LEN / 2.0

    # thread_len grows with N so the collar/nuts still seat on exposed thread.
    # The exposed thread must reach at least to the outermost lock element plus
    # a small margin past the stack end (plates6 raised THREAD_LEN for N=6).
    thread_len = max(0.050, (collar_outboard - stack_end) + 0.006)
    thread_x = stack_end + thread_len / 2.0

    grip_mid_r = HANDLE_R * gmrs

    return ResolvedDumbbellConfig(
        plate_shape=plate_shape,
        collar_lock=collar_lock,
        grip_form=grip_form,
        plates_per_side=n,
        palette_style=palette_style,
        plate_radius_scale=prs,
        plate_thick_scale=pts,
        grip_len_scale=gls,
        grip_mid_r_scale=gmrs,
        handle_len=handle_len,
        plate_r=plate_r,
        plate_thick=plate_thick,
        grip_half=grip_half,
        sleeve_x=sleeve_x,
        stack_start=stack_start,
        stack_len=stack_len,
        stack_end=stack_end,
        thread_len=thread_len,
        thread_x=thread_x,
        collar_x=collar_x,
        inner_nut_center=inner_nut_center,
        contact_face=contact_face,
        grip_mid_r=grip_mid_r,
        name=config.name,
    )


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #


def _rot_x(geom):
    # CylinderGeometry / TorusGeometry / LatheGeometry built along local Z; rot to +X.
    return geom.rotate_y(math.pi / 2.0)


def _hex_profile(radius: float) -> list[tuple[float, float]]:
    # Regular hexagon inscribed in *radius*; vertices at 30,90,... so flat edges
    # land top/bottom after rotate_y → plate sits flat without rolling.
    return [
        (radius * math.cos(math.pi / 6.0 + i * math.pi / 3.0),
         radius * math.sin(math.pi / 6.0 + i * math.pi / 3.0))
        for i in range(6)
    ]


def _hex_flat_profile(flat_to_flat: float) -> list[tuple[float, float]]:
    r = flat_to_flat / (2.0 * math.cos(math.pi / 6.0))
    return [
        (r * math.cos(i * math.pi / 3.0), r * math.sin(i * math.pi / 3.0))
        for i in range(6)
    ]


def _dodecagon_profile(radius: float) -> list[tuple[float, float]]:
    n = 12
    return [
        (radius * math.cos(2.0 * math.pi * i / n), radius * math.sin(2.0 * math.pi * i / n))
        for i in range(n)
    ]


def _circle_profile(radius: float, segments: int = 36) -> list[tuple[float, float]]:
    return [
        (radius * math.cos(i * 2.0 * math.pi / segments),
         radius * math.sin(i * 2.0 * math.pi / segments))
        for i in range(segments)
    ]


def _single_plate_geom(r: ResolvedDumbbellConfig, radius: float, cx: float, sign: float):
    """One plate (round/hex/dodeca) with center bore-ish hub + embossed rim."""
    thickness = r.plate_thick
    shape = r.plate_shape
    if shape == "hex_plate":
        outer = _hex_profile(radius)
        bore = _circle_profile(BORE_R)
        plate = ExtrudeWithHolesGeometry(outer, [bore], thickness, cap=True, center=True)
        plate.rotate_y(math.pi / 2.0)
        plate.translate(cx, 0.0, 0.0)
        ring_segs = 6
    elif shape == "dodecagonal_plate":
        plate = ExtrudeGeometry(_dodecagon_profile(radius), thickness, cap=True, center=True)
        plate = plate.rotate_y(math.pi / 2.0)
        plate.translate(cx, 0.0, 0.0)
        ring_segs = 12
    else:  # round_plate
        plate = _rot_x(CylinderGeometry(radius, thickness, radial_segments=56))
        plate.translate(cx, 0.0, 0.0)
        ring_segs = 48

    # Raised embossed center hub on the outward face.
    hub = _rot_x(CylinderGeometry(PLATE_HUB_R, thickness * 0.5, radial_segments=40))
    hub.translate(cx + sign * (thickness * 0.25), 0.0, 0.0)
    plate.merge(hub)

    # Embossed raised rim ring.
    ring = _rot_x(
        TorusGeometry(radius * 0.62, 0.0022, radial_segments=10, tubular_segments=ring_segs)
    )
    ring.translate(cx + sign * (thickness * 0.5 - 0.001), 0.0, 0.0)
    plate.merge(ring)
    return plate


def _plate_stack_geom(r: ResolvedDumbbellConfig, sign: float):
    """One side's plate stack merged into a single mesh."""
    stack = None
    pitch = r.plate_thick + PLATE_GAP
    taper = min(0.004, r.plate_r * 0.05)
    for i in range(r.plates_per_side):
        radius = max(PLATE_HUB_R + 0.012, r.plate_r - taper * i)
        cx = sign * (r.stack_start + i * pitch + r.plate_thick / 2.0)
        plate = _single_plate_geom(r, radius, cx, sign)
        stack = plate if stack is None else stack.merge(plate)
    return stack


def _thread_geom(r: ResolvedDumbbellConfig, sign: float):
    cx = sign * r.thread_x
    core = _rot_x(CylinderGeometry(THREAD_R, r.thread_len, radial_segments=32))
    core.translate(cx, 0.0, 0.0)
    n_ridges = max(5, int(r.thread_len / 0.008))
    span = r.thread_len - 0.006
    start = r.thread_x - span / 2.0
    for j in range(n_ridges):
        rx = sign * (start + j * (span / (n_ridges - 1)))
        ridge = _rot_x(
            TorusGeometry(THREAD_R, THREAD_RIDGE_R - THREAD_R, radial_segments=8, tubular_segments=20)
        )
        ridge.translate(rx, 0.0, 0.0)
        core.merge(ridge)
    return core


def _grip_geom(r: ResolvedDumbbellConfig):
    """Return (core_geom, knurl_geom) for the grip slot."""
    if r.grip_form == "contoured_ergonomic":
        half = r.grip_half
        # barrel/hourglass core profile
        n_pts = 28
        profile = []
        for i in range(n_pts):
            t = i / (n_pts - 1)
            z = -half + t * 2.0 * half
            blend = 0.5 * (1.0 + math.cos(math.pi * abs(z) / half))
            rad = HANDLE_R + (r.grip_mid_r - HANDLE_R) * blend
            profile.append((rad, z))
        core = _rot_x(LatheGeometry(profile, segments=48))

        # corrugated knurl following the barrel
        n_bumps = 18
        knurl_span = r.handle_len * 0.78
        knurl_half = knurl_span / 2.0
        npk = n_bumps * 4 + 1
        kprofile = []
        for i in range(npk):
            t = i / (npk - 1)
            zx = -knurl_half + t * knurl_span
            blend = 0.5 * (1.0 + math.cos(math.pi * abs(zx) / half))
            base_r = HANDLE_R + (r.grip_mid_r - HANDLE_R) * blend
            bump = 0.00045 * (0.5 + 0.5 * math.sin(2.0 * math.pi * n_bumps * t))
            kprofile.append((base_r + bump, zx))
        knurl = _rot_x(LatheGeometry(kprofile, segments=48))
        return core, knurl

    # straight_knurled_bar
    core = _rot_x(CylinderGeometry(HANDLE_R, r.handle_len + 0.004, radial_segments=40))
    knurl = KnobGeometry(
        GRIP_KNURL_R * 2.0,
        r.handle_len * 0.62,
        body_style="cylindrical",
        grip=KnobGrip(style="knurled", count=44, depth=0.0009, helix_angle_deg=12.0),
        center=True,
    ).rotate_y(math.pi / 2.0)
    return core, knurl


def _spinlock_nut_geom():
    nut = KnobGeometry(
        COLLAR_DIA,
        COLLAR_LEN,
        body_style="cylindrical",
        grip=KnobGrip(style="knurled", count=30, depth=0.0010, helix_angle_deg=18.0),
        center=True,
    )
    return nut.rotate_y(math.pi / 2.0)


def _hex_nut_geom():
    outer = _hex_flat_profile(HEX_FLAT)
    bore = _circle_profile(HEX_BORE_R, 24)
    nut = ExtrudeWithHolesGeometry(outer, [bore], HEX_THICK, center=True)
    return nut.rotate_y(math.pi / 2.0)


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #


def build_dumbbell(
    config: DumbbellConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or DumbbellConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-dumbbell-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    mats = {k: model.material(f"dumbbell_{k}", rgba=v) for k, v in pal.items()}

    # ============ BODY (root) ============
    body = model.part("body")

    core, knurl = _grip_geom(r)
    body.visual(mesh_from_geometry(core, "grip_core"), material=mats["grip"], name="grip_core", material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome", "brushed_steel", "matte_black_iron", "zinc_plated", "polished_dumbbell"} else "metal.blackened_gunmetal"))
    body.visual(mesh_from_geometry(knurl, "grip_knurl"), material=mats["knurl"], name="grip_knurl", material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome", "brushed_steel", "matte_black_iron", "zinc_plated", "polished_dumbbell"} else "metal.blackened_gunmetal"))

    for sign in (-1.0, 1.0):
        side = "pos" if sign > 0 else "neg"

        sleeve = _rot_x(CylinderGeometry(SLEEVE_R, SLEEVE_LEN + 0.002, radial_segments=40))
        sleeve.translate(sign * r.sleeve_x, 0.0, 0.0)
        body.visual(
            mesh_from_geometry(sleeve, f"sleeve_{side}"),
            material=mats["sleeve"],
            name=f"sleeve_{side}", material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome", "brushed_steel", "matte_black_iron", "zinc_plated", "polished_dumbbell"} else "metal.blackened_gunmetal"),
        )

        stack = _plate_stack_geom(r, sign)
        body.visual(
            mesh_from_geometry(stack, f"plates_{side}"),
            material=mats["plate"],
            name=f"plates_{side}", material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome", "brushed_steel", "matte_black_iron", "zinc_plated", "polished_dumbbell"} else "metal.blackened_gunmetal"),
        )

        thread = _thread_geom(r, sign)
        body.visual(
            mesh_from_geometry(thread, f"thread_{side}"),
            material=mats["thread"],
            name=f"thread_{side}", material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome", "brushed_steel", "matte_black_iron", "zinc_plated", "polished_dumbbell"} else "metal.blackened_gunmetal"),
        )

        # hex_jamnut_pair adds a fixed inner nut body visual.
        if r.collar_lock == "hex_jamnut_pair":
            inner = _hex_nut_geom()
            inner.translate(sign * r.inner_nut_center, 0.0, 0.0)
            body.visual(
                mesh_from_geometry(inner, f"inner_hex_nut_{side}"),
                material=mats["collar"],
                name=f"inner_hex_nut_{side}", material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome", "brushed_steel", "matte_black_iron", "zinc_plated", "polished_dumbbell"} else "metal.blackened_gunmetal"),
            )

    body.inertial = Inertial.from_geometry(
        Box((2.0 * (r.thread_x + r.thread_len / 2.0), 2.0 * r.plate_r, 2.0 * r.plate_r)),
        mass=8.0,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )

    # ============ LOCKING COLLARS (CONTINUOUS spin about +X) ============
    for sign in (-1.0, 1.0):
        side = "pos" if sign > 0 else "neg"

        if r.collar_lock == "hex_jamnut_pair":
            part_name = f"collar_{side}"
            collar = model.part(part_name)
            # Outer hex nut, offset outward from the contact-face joint origin.
            # Seat it inward by JAM_SEAT so the outer nut's inboard face overlaps
            # the fixed inner nut by the required min_overlap (the two jam nuts
            # are tightened against each other at a shared face).
            JAM_SEAT = 0.0025
            nut_local_x = HEX_THICK / 2.0 - JAM_SEAT
            nut = _hex_nut_geom()
            nut.translate(sign * nut_local_x, 0.0, 0.0)
            collar.visual(
                mesh_from_geometry(nut, f"{part_name}_nut"),
                material=mats["collar"],
                name=f"{part_name}_nut", material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome", "brushed_steel", "matte_black_iron", "zinc_plated", "polished_dumbbell"} else "metal.blackened_gunmetal"),
            )
            collar.visual(
                Box((0.005, 0.006, 0.014)),
                origin=Origin(xyz=(sign * nut_local_x, HEX_FLAT / 2.0 + 0.001, 0.0)),
                material=mats["marker"],
                name=f"{part_name}_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
            collar.inertial = Inertial.from_geometry(
                Box((HEX_THICK, HEX_FLAT, HEX_FLAT)), mass=0.08
            )
            origin_x = sign * r.contact_face

        elif r.collar_lock == "star_lock_collar":
            part_name = f"collar_{side}"
            collar = model.part(part_name)
            nut = _spinlock_nut_geom()
            collar.visual(
                mesh_from_geometry(nut, f"{part_name}_nut"),
                material=mats["collar"],
                name=f"{part_name}_nut", material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome", "brushed_steel", "matte_black_iron", "zinc_plated", "polished_dumbbell"} else "metal.blackened_gunmetal"),
            )
            # radial star/lever finger lobes (Box fingers, like an indexer tab).
            # Seat each lobe so its inner end sinks ~3mm into the nut body so the
            # lobes are not floating islands but fused to the central nut.
            nut_surface_r = COLLAR_DIA / 2.0
            lobe_embed = 0.008
            lobe_r = nut_surface_r + STAR_LOBE_LEN / 2.0 - lobe_embed
            lobe_outer_r = lobe_r + STAR_LOBE_LEN / 2.0
            for k in range(STAR_POINTS):
                ang = 2.0 * math.pi * k / STAR_POINTS
                collar.visual(
                    Box((COLLAR_LEN * 0.55, 0.008, STAR_LOBE_LEN)),
                    origin=Origin(
                        xyz=(0.0, lobe_r * math.cos(ang), lobe_r * math.sin(ang)),
                        rpy=(ang, 0.0, 0.0),
                    ),
                    material=mats["collar"],
                    name=f"{part_name}_lobe_{k}", material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome", "brushed_steel", "matte_black_iron", "zinc_plated", "polished_dumbbell"} else "metal.blackened_gunmetal"),
                )
            # Index marker sits on the +Y (k=0) lobe's outer tip, overlapping it so
            # it stays connected to the lobe (which is in turn fused to the nut).
            marker_box = 0.006
            collar.visual(
                Box((marker_box, marker_box, marker_box)),
                origin=Origin(xyz=(0.0, lobe_outer_r - marker_box / 2.0 + 0.001, 0.0)),
                material=mats["marker"],
                name=f"{part_name}_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
            collar.inertial = Inertial.from_geometry(
                Box((COLLAR_LEN, 2.0 * lobe_r, 2.0 * lobe_r)), mass=0.12
            )
            origin_x = sign * r.collar_x

        else:  # spinlock_nut
            part_name = f"collar_{side}"
            collar = model.part(part_name)
            nut = _spinlock_nut_geom()
            collar.visual(
                mesh_from_geometry(nut, f"{part_name}_nut"),
                material=mats["collar"],
                name=f"{part_name}_nut", material_class_id=("metal.chrome_polished" if r.palette_style in {"bright_chrome", "brushed_steel", "matte_black_iron", "zinc_plated", "polished_dumbbell"} else "metal.blackened_gunmetal"),
            )
            collar.visual(
                Box((0.006, 0.006, 0.014)),
                origin=Origin(xyz=(0.0, COLLAR_DIA / 2.0 + 0.001, 0.0)),
                material=mats["marker"],
                name=f"{part_name}_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
            )
            collar.inertial = Inertial.from_geometry(
                Box((COLLAR_LEN, COLLAR_DIA, COLLAR_DIA)), mass=0.10
            )
            origin_x = sign * r.collar_x

        model.articulation(
            f"collar_spin_{side}",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=collar,
            origin=Origin(xyz=(origin_x, 0.0, 0.0)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=8.0),
        )

    return model


def build_seeded_dumbbell(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_dumbbell(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Slot choices
# --------------------------------------------------------------------------- #


def slot_choices_for_config(r: ResolvedDumbbellConfig) -> tuple[tuple[str, str], ...]:
    return (
        ("plate_shape", r.plate_shape),
        ("collar_lock", r.collar_lock),
        ("grip_form", r.grip_form),
        ("plates_per_side", str(r.plates_per_side)),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def _center(aabb):
    mn, mx = aabb
    return ((mn[0] + mx[0]) / 2.0, (mn[1] + mx[1]) / 2.0, (mn[2] + mx[2]) / 2.0)


def run_dumbbell_tests(object_model: ArticulatedObject, config: DumbbellConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    body = object_model.get_part("body")
    collar_pos = object_model.get_part("collar_pos")
    collar_neg = object_model.get_part("collar_neg")
    spin_pos = object_model.get_articulation("collar_spin_pos")
    spin_neg = object_model.get_articulation("collar_spin_neg")

    # ---- exactly two articulated collar parts, plates carry no joints ----
    collar_parts = [p for p in object_model.parts if p.name.startswith("collar_")]
    ctx.check(
        "exactly two articulated collar parts",
        len(collar_parts) == 2,
        details=f"collar_parts={[p.name for p in collar_parts]}",
    )
    ctx.check(
        "exactly two articulations",
        len(object_model.articulations) == 2,
        details=str([j.name for j in object_model.articulations]),
    )

    # ---- collar joints CONTINUOUS, axis +X, no limit ----
    for joint in (spin_pos, spin_neg):
        ctx.check(
            f"{joint.name} is CONTINUOUS",
            joint.articulation_type == ArticulationType.CONTINUOUS,
            details=str(joint.articulation_type),
        )
        ctx.check(
            f"{joint.name} axis is the bar axis (1,0,0)",
            tuple(joint.axis) == (1.0, 0.0, 0.0),
            details=str(joint.axis),
        )
        ctx.check(
            f"{joint.name} origin is on the bar axis (yz≈0)",
            abs(joint.origin.xyz[1]) < 1e-6 and abs(joint.origin.xyz[2]) < 1e-6,
            details=str(joint.origin.xyz),
        )

    # ---- plate stacks present, substantial, on both sides ----
    ext_pos = _ext(ctx.part_element_world_aabb(body, elem="plates_pos"))
    ext_neg = _ext(ctx.part_element_world_aabb(body, elem="plates_neg"))
    min_diam = 2.0 * (PLATE_HUB_R + 0.012) * 0.9
    for ext, tag in ((ext_pos, "pos"), (ext_neg, "neg")):
        ctx.check(
            f"{tag}-side plate stack present and substantial",
            ext[1] > min_diam and ext[2] > 0.10 and ext[0] > 0.004,
            details=f"plates_{tag} extents={ext}",
        )

    # ---- faceted plates read faceted (hex Z/Y ratio < round) ----
    if r.plate_shape == "hex_plate":
        for ext, tag in ((ext_pos, "pos"), (ext_neg, "neg")):
            ratio = ext[2] / ext[1] if ext[1] > 0 else 0.0
            ctx.check(
                f"{tag}-side hex plates are faceted (Z/Y < 0.95)",
                0.78 < ratio < 0.95,
                details=f"ratio={ratio:.3f} (Y={ext[1]:.4f} Z={ext[2]:.4f})",
            )

    # ---- left-right mirror symmetry ----
    cx_pos = _center(ctx.part_element_world_aabb(body, elem="plates_pos"))[0]
    cx_neg = _center(ctx.part_element_world_aabb(body, elem="plates_neg"))[0]
    ctx.check(
        "plate stacks mirror about the bar center",
        abs(cx_pos + cx_neg) < 0.002,
        details=f"cx_pos={cx_pos}, cx_neg={cx_neg}",
    )

    # ---- inner plate butts the grip shoulder sleeve (no floating stack) ----
    sleeve_pos_outer = ctx.part_element_world_aabb(body, elem="sleeve_pos")[1][0]
    plates_pos_inner = ctx.part_element_world_aabb(body, elem="plates_pos")[0][0]
    ctx.check(
        "positive plate stack butts the shoulder sleeve (no gap)",
        plates_pos_inner <= sleeve_pos_outer + 0.004,
        details=f"plates_inner={plates_pos_inner}, sleeve_outer={sleeve_pos_outer}",
    )

    # ---- collars outboard of the stacks ----
    plates_pos_outer = ctx.part_element_world_aabb(body, elem="plates_pos")[1][0]
    collar_pos_cx = ctx.part_world_position(collar_pos)[0]
    ctx.check(
        "positive collar is outboard of the positive plate stack",
        collar_pos_cx > plates_pos_outer - 0.004,
        details=f"collar_pos_x={collar_pos_cx}, plates_pos_outer={plates_pos_outer}",
    )
    plates_neg_outer = ctx.part_element_world_aabb(body, elem="plates_neg")[0][0]
    collar_neg_cx = ctx.part_world_position(collar_neg)[0]
    ctx.check(
        "negative collar is outboard of the negative plate stack",
        collar_neg_cx < plates_neg_outer + 0.004,
        details=f"collar_neg_x={collar_neg_cx}, plates_neg_outer={plates_neg_outer}",
    )

    # ---- collar seated on exposed thread, not overhanging the bar end ----
    for sign, side in ((1.0, "pos"), (-1.0, "neg")):
        thread_aabb = ctx.part_element_world_aabb(body, elem=f"thread_{side}")
        thread_outer = thread_aabb[1][0] if sign > 0 else thread_aabb[0][0]
        cpart = collar_pos if sign > 0 else collar_neg
        cnut = f"collar_{side}_nut"
        nut_outer = (
            ctx.part_element_world_aabb(cpart, elem=cnut)[1][0]
            if sign > 0
            else ctx.part_element_world_aabb(cpart, elem=cnut)[0][0]
        )
        if sign > 0:
            seated = nut_outer <= thread_outer + 0.001
        else:
            seated = nut_outer >= thread_outer - 0.001
        ctx.check(
            f"{side} collar nut stays on the exposed thread (no overhang)",
            seated,
            details=f"nut_outer={nut_outer}, thread_outer={thread_outer}",
        )

    # ---- collar↔seat overlap declared + expected (intentional thread seating) ----
    if r.collar_lock == "hex_jamnut_pair":
        for cpart, side in ((collar_pos, "pos"), (collar_neg, "neg")):
            ctx.allow_overlap(
                cpart, body,
                elem_a=f"collar_{side}_nut", elem_b=f"inner_hex_nut_{side}",
                reason="Outer jam nut spins against the fixed inner jam nut at the contact face.",
            )
            ctx.allow_overlap(
                cpart, body,
                elem_a=f"collar_{side}_nut", elem_b=f"thread_{side}",
                reason="Jam nut bore threads onto the bar end (intentional thread overlap).",
            )
            ctx.expect_overlap(
                cpart, body, axes="x", min_overlap=0.002,
                elem_a=f"collar_{side}_nut", elem_b=f"inner_hex_nut_{side}",
                name=f"{side} outer jam nut contacts the inner nut",
            )
    else:
        for cpart, side in ((collar_pos, "pos"), (collar_neg, "neg")):
            ctx.allow_overlap(
                cpart, body,
                elem_a=f"collar_{side}_nut", elem_b=f"thread_{side}",
                reason="Locking collar threads onto the bar end; nut bore intentionally overlaps the thread.",
            )
            ctx.expect_overlap(
                cpart, body, axes="x", min_overlap=0.004,
                elem_a=f"collar_{side}_nut", elem_b=f"thread_{side}",
                name=f"{side} collar seated on its thread",
            )

    # ---- both collars spin: marker swings off-axis from +Y toward +Z ----
    for collar, spin, tag in ((collar_pos, spin_pos, "pos"), (collar_neg, spin_neg, "neg")):
        m_elem = f"collar_{tag}_marker"
        rest_c = _center(ctx.part_element_world_aabb(collar, elem=m_elem))
        ctx.check(
            f"{tag} marker rests above the axis (+Y)",
            rest_c[1] > 0.015 and abs(rest_c[2]) < 0.012,
            details=f"{tag} rest marker center={rest_c}",
        )
        with ctx.pose({spin: math.pi / 2.0}):
            turn_c = _center(ctx.part_element_world_aabb(collar, elem=m_elem))
        ctx.check(
            f"{tag} collar spin swings marker from +Y toward +Z",
            turn_c[2] > 0.015 and abs(turn_c[1]) < 0.012,
            details=f"{tag} rest={rest_c}, quarter-turn={turn_c}",
        )

    return ctx.report()


__all__ = [
    "DumbbellConfig",
    "ResolvedDumbbellConfig",
    "config_from_seed",
    "resolve_config",
    "build_dumbbell",
    "build_seeded_dumbbell",
    "slot_choices_for_seed",
    "slot_choices_for_config",
    "run_dumbbell_tests",
    "__modular__",
]
