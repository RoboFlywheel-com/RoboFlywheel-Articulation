# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template — Technology / Graphics_Card.

Dominant axis = MULTIPLICITY: N∈{1,2,3,4} axial cooling fans, each a homogeneous
copy `fan_{i}` on its own CONTINUOUS spin joint (axis = card thickness (0,0,1)).
A fold-out anti-sag `support_foot` adds a REVOLUTE joint. All non-moving structure
(heatsink, shroud, bracket, backplate, power block, brand/RGB/accent decorations)
is fused into the single grounded `card_body` part as named visuals (Rule 1).

Derived from the 8 rating-5 sources (see specs_modular_v1/Technology_Graphics_Card.md):
  MSI Trio (e43c8fd4) / Gigabyte (c9301248) / Founders (ccf04675) / Zotac (b4e75c5b)
  + var_blower / var_power_triple_8pin / var_power_12vhpwr / var_support_bracket.

Frame: card_body centered at origin. +X = length (I/O bracket at -X end),
+Y = height (PCIe fingers below -Y, power connector on +Y top edge),
+Z = thickness (fans face +Z, PCB near z=0, backplate at -Z).
"""

from __future__ import annotations

import math
import tempfile
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    FanRotorBlade,
    FanRotorGeometry,
    FanRotorHub,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

ShroudForm = Literal[
    "open_axial_gaming",
    "compact_itx_open_axial",
    "flow_through_founders",
    "blower_radial",
    "vapor_chamber_full_cover",
]
Backplate = Literal["absent", "present_with_cutout", "present_solid"]
PowerConnector = Literal["single_8pin", "row_8pin", "12vhpwr_16pin", "absent"]
SupportBracket = Literal["fans_only", "foldout_support_foot"]
PaletteStyle = Literal[
    "all_black_gaming",
    "gunmetal_gray",
    "black_rgb",
    "zotac_copper",
    "founders_silver",
    "white_rgb",
]

# --------------------------------------------------------------------------- #
# Palettes (⑥ 涂装) — every .visual material key resolves through here.
# --------------------------------------------------------------------------- #
PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "all_black_gaming": {
        "pcb": (0.04, 0.04, 0.05, 1.0), "shroud": (0.09, 0.09, 0.10, 1.0),
        "fan": (0.07, 0.07, 0.08, 1.0), "fin": (0.55, 0.56, 0.58, 1.0),
        "copper": (0.86, 0.46, 0.16, 1.0), "gold": (0.84, 0.66, 0.20, 1.0),
        "metal": (0.60, 0.61, 0.64, 1.0), "port": (0.10, 0.10, 0.12, 1.0),
        "accent": (0.22, 0.23, 0.26, 1.0), "backplate": (0.11, 0.12, 0.13, 1.0),
        "rgb": (0.30, 0.55, 0.95, 0.85), "badge": (0.90, 0.16, 0.14, 1.0),
    },
    "gunmetal_gray": {
        "pcb": (0.05, 0.06, 0.06, 1.0), "shroud": (0.38, 0.39, 0.42, 1.0),
        "fan": (0.12, 0.12, 0.13, 1.0), "fin": (0.72, 0.73, 0.75, 1.0),
        "copper": (0.84, 0.44, 0.14, 1.0), "gold": (0.83, 0.66, 0.20, 1.0),
        "metal": (0.68, 0.70, 0.72, 1.0), "port": (0.14, 0.14, 0.16, 1.0),
        "accent": (0.18, 0.19, 0.22, 1.0), "backplate": (0.30, 0.31, 0.34, 1.0),
        "rgb": (0.85, 0.85, 0.88, 0.85), "badge": (0.90, 0.90, 0.92, 1.0),
    },
    "black_rgb": {
        "pcb": (0.03, 0.03, 0.04, 1.0), "shroud": (0.06, 0.06, 0.07, 1.0),
        "fan": (0.05, 0.05, 0.06, 1.0), "fin": (0.50, 0.52, 0.54, 1.0),
        "copper": (0.88, 0.48, 0.18, 1.0), "gold": (0.85, 0.68, 0.22, 1.0),
        "metal": (0.55, 0.56, 0.60, 1.0), "port": (0.08, 0.08, 0.10, 1.0),
        "accent": (0.14, 0.60, 0.85, 1.0), "backplate": (0.08, 0.09, 0.10, 1.0),
        "rgb": (0.20, 0.85, 0.55, 0.85), "badge": (0.20, 0.80, 0.95, 1.0),
    },
    "zotac_copper": {
        "pcb": (0.05, 0.10, 0.08, 1.0), "shroud": (0.135, 0.14, 0.155, 1.0),
        "fan": (0.05, 0.05, 0.06, 1.0), "fin": (0.62, 0.64, 0.67, 1.0),
        "copper": (0.82, 0.51, 0.20, 1.0), "gold": (0.83, 0.66, 0.20, 1.0),
        "metal": (0.58, 0.60, 0.63, 1.0), "port": (0.12, 0.12, 0.13, 1.0),
        "accent": (0.82, 0.51, 0.20, 1.0), "backplate": (0.10, 0.11, 0.12, 1.0),
        "rgb": (0.94, 0.94, 0.95, 0.85), "badge": (0.94, 0.94, 0.95, 1.0),
    },
    "founders_silver": {
        "pcb": (0.06, 0.07, 0.07, 1.0), "shroud": (0.70, 0.71, 0.73, 1.0),
        "fan": (0.14, 0.14, 0.15, 1.0), "fin": (0.76, 0.77, 0.79, 1.0),
        "copper": (0.84, 0.44, 0.14, 1.0), "gold": (0.83, 0.66, 0.20, 1.0),
        "metal": (0.80, 0.81, 0.83, 1.0), "port": (0.16, 0.16, 0.18, 1.0),
        "accent": (0.34, 0.35, 0.38, 1.0), "backplate": (0.62, 0.63, 0.65, 1.0),
        "rgb": (0.88, 0.88, 0.90, 0.85), "badge": (0.30, 0.31, 0.34, 1.0),
    },
    "white_rgb": {
        "pcb": (0.06, 0.08, 0.075, 1.0), "shroud": (0.90, 0.90, 0.87, 1.0),
        "fan": (0.14, 0.15, 0.16, 1.0), "fin": (0.68, 0.70, 0.72, 1.0),
        "copper": (0.86, 0.47, 0.18, 1.0), "gold": (0.86, 0.70, 0.24, 1.0),
        "metal": (0.78, 0.79, 0.80, 1.0), "port": (0.14, 0.14, 0.16, 1.0),
        "accent": (0.55, 0.75, 0.90, 1.0), "backplate": (0.86, 0.86, 0.83, 1.0),
        "rgb": (0.30, 0.85, 0.60, 0.85), "badge": (0.20, 0.75, 0.90, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class GraphicsCardConfig:
    cooler_shroud_form: ShroudForm = "open_axial_gaming"
    fan_count: int = 3
    backplate: Backplate = "absent"
    power_connector: PowerConnector = "single_8pin"
    n_8pin: int = 2
    support_bracket: SupportBracket = "fans_only"
    palette_style: PaletteStyle = "all_black_gaming"
    card_length: float | None = None
    card_height: float | None = None
    pcb_thickness: float | None = None
    cooler_thickness: float | None = None
    fan_radius: float | None = None
    blade_count: int | None = None
    fin_count: int | None = None
    name: str = "parametric_graphics_card"


@dataclass(frozen=True)
class ResolvedGraphicsCardConfig:
    cooler_shroud_form: ShroudForm
    fan_count: int
    backplate: Backplate
    power_connector: PowerConnector
    n_8pin: int
    support_bracket: SupportBracket
    palette_style: PaletteStyle
    card_length: float
    card_height: float
    pcb_thickness: float
    cooler_thickness: float
    fan_radius: float
    blade_count: int
    fin_count: int
    fan_centers_x: tuple[float, ...]
    hole_radius: float
    # derived z-layout
    z_pcb_top: float
    base_t: float
    fin_h: float
    z_fin_top: float
    rotor_t: float
    fan_z: float
    boss_z0: float
    face_z: float
    face_t: float
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# --------------------------------------------------------------------------- #
# Seed sampling
# --------------------------------------------------------------------------- #
def config_from_seed(seed: int) -> GraphicsCardConfig:
    import random

    rng = random.Random(seed)

    form: ShroudForm = rng.choices(
        (
            "open_axial_gaming",
            "compact_itx_open_axial",
            "flow_through_founders",
            "blower_radial",
            "vapor_chamber_full_cover",
        ),
        weights=(0.42, 0.16, 0.18, 0.12, 0.12),
        k=1,
    )[0]

    # blower / compact are single-fan forms.
    if form in ("blower_radial", "compact_itx_open_axial"):
        fan_count = 1
    else:
        fan_count = rng.choices((1, 2, 3, 4), weights=(0.14, 0.36, 0.42, 0.08), k=1)[0]

    height = round(rng.uniform(0.100, 0.135), 3)
    cooler_t = round(rng.uniform(0.030, 0.058), 3)
    pcb_t = round(rng.uniform(0.0016, 0.0024), 4)
    fin_count = rng.randint(14, 37)
    blade_count = rng.choice((9, 11, 11, 13, 14))

    # length lower bound rises with N (fan pitch); add slack then clamp.
    l_min = 0.150 + 0.058 * fan_count
    length = round(rng.uniform(l_min, l_min + 0.055), 3)

    backplate: Backplate = rng.choices(
        ("absent", "present_with_cutout", "present_solid"),
        weights=(0.45, 0.35, 0.20),
        k=1,
    )[0]

    # power gated by length.
    if length >= 0.24:
        power: PowerConnector = rng.choices(
            ("single_8pin", "row_8pin", "12vhpwr_16pin", "absent"),
            weights=(0.40, 0.24, 0.24, 0.12),
            k=1,
        )[0]
    else:
        power = rng.choices(("single_8pin", "absent"), weights=(0.55, 0.45), k=1)[0]
    n_8pin = rng.choice((2, 3)) if power == "row_8pin" else 2

    support: SupportBracket = rng.choices(
        ("fans_only", "foldout_support_foot"), weights=(0.62, 0.38), k=1
    )[0]

    palette: PaletteStyle = rng.choice(
        (
            "all_black_gaming",
            "gunmetal_gray",
            "black_rgb",
            "zotac_copper",
            "founders_silver",
            "white_rgb",
        )
    )

    return GraphicsCardConfig(
        cooler_shroud_form=form,
        fan_count=fan_count,
        backplate=backplate,
        power_connector=power,
        n_8pin=n_8pin,
        support_bracket=support,
        palette_style=palette,
        card_length=length,
        card_height=height,
        pcb_thickness=pcb_t,
        cooler_thickness=cooler_t,
        blade_count=blade_count,
        fin_count=fin_count,
        name=f"seeded_graphics_card_{seed}",
    )


def resolve_config(config: GraphicsCardConfig) -> ResolvedGraphicsCardConfig:
    form = config.cooler_shroud_form
    if form not in PALETTES.keys() and form not in (
        "open_axial_gaming",
        "compact_itx_open_axial",
        "flow_through_founders",
        "blower_radial",
        "vapor_chamber_full_cover",
    ):
        raise ValueError(f"bad shroud form {form}")
    palette = config.palette_style
    if palette not in PALETTES:
        raise ValueError(f"bad palette {palette}")

    fan_count = int(config.fan_count)
    # form gates.
    if form in ("blower_radial", "compact_itx_open_axial"):
        fan_count = 1
    fan_count = max(1, min(4, fan_count))

    height = _clamp(config.card_height if config.card_height is not None else 0.120, 0.100, 0.135)
    pcb_t = _clamp(
        config.pcb_thickness if config.pcb_thickness is not None else 0.0018, 0.0016, 0.0024
    )
    cooler_t = _clamp(
        config.cooler_thickness if config.cooler_thickness is not None else 0.045, 0.030, 0.058
    )
    fin_count = max(14, min(37, int(config.fin_count if config.fin_count is not None else 24)))
    blade_count = max(7, min(15, int(config.blade_count if config.blade_count is not None else 11)))

    l_min = 0.150 + 0.058 * fan_count
    length = _clamp(
        config.card_length if config.card_length is not None else l_min + 0.02, l_min, 0.420
    )

    # power gating (defensive; sampler already gates).
    power = config.power_connector
    if length < 0.24 and power in ("row_8pin", "12vhpwr_16pin"):
        power = "single_8pin"
    n_8pin = max(2, min(3, int(config.n_8pin))) if power == "row_8pin" else 2

    # fan centers along +X: inset from the card ends by (max_radius + clearance)
    # so the outermost rotor tip clears the +X/-X shroud end walls in every pose.
    r_from_h = height * 0.5 - 0.007
    end_clear = r_from_h + 0.016
    x0 = -length * 0.5 + end_clear
    x1 = length * 0.5 - end_clear
    if fan_count == 1:
        centers = [0.0]
        pitch = x1 - x0
    else:
        step = (x1 - x0) / (fan_count - 1)
        centers = [x0 + i * step for i in range(fan_count)]
        pitch = step

    # fan radius: bounded by height and pitch; end clearance uses r_from_h so any
    # fan_radius <= r_from_h keeps >= 0.0075 m from the end walls.
    r_from_pitch = (pitch * 0.5 - 0.004) if fan_count > 1 else r_from_h
    requested = config.fan_radius if config.fan_radius is not None else 0.045
    fan_radius = _clamp(requested, 0.026, max(0.028, min(r_from_h, r_from_pitch, 0.048)))
    hole_radius = fan_radius + 0.004

    # z-layout (all derived from pcb_t + cooler_t) — single-sourced.
    z_pcb_top = pcb_t * 0.5
    base_t = 0.005
    fin_h = _clamp(cooler_t * 0.45, 0.012, 0.026)
    z_fin_top = z_pcb_top + base_t + fin_h
    rotor_t = _clamp(cooler_t * 0.26, 0.008, 0.013)
    fan_z = z_fin_top + 0.0015 + rotor_t * 0.5
    boss_z0 = z_fin_top - 0.004
    face_z0 = fan_z + rotor_t * 0.5 + 0.0025
    face_t = 0.005
    face_z = face_z0 + face_t * 0.5

    return ResolvedGraphicsCardConfig(
        cooler_shroud_form=form,
        fan_count=fan_count,
        backplate=config.backplate,
        power_connector=power,
        n_8pin=n_8pin,
        support_bracket=config.support_bracket,
        palette_style=palette,
        card_length=length,
        card_height=height,
        pcb_thickness=pcb_t,
        cooler_thickness=cooler_t,
        fan_radius=fan_radius,
        blade_count=blade_count,
        fin_count=fin_count,
        fan_centers_x=tuple(centers),
        hole_radius=hole_radius,
        z_pcb_top=z_pcb_top,
        base_t=base_t,
        fin_h=fin_h,
        z_fin_top=z_fin_top,
        rotor_t=rotor_t,
        fan_z=fan_z,
        boss_z0=boss_z0,
        face_z=face_z,
        face_t=face_t,
        name=config.name,
    )


def with_overrides(config: GraphicsCardConfig, **kw) -> GraphicsCardConfig:
    return replace(config, **kw)


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    n = r.fan_count
    band = f"N={n}" if n <= 3 else "N=4"
    return [
        ("cooler_shroud_form", r.cooler_shroud_form),
        ("fan_count", band),
        ("backplate", r.backplate),
        ("power_connector", r.power_connector),
        ("support_bracket", r.support_bracket),
    ]


# --------------------------------------------------------------------------- #
# Geometry helpers
# --------------------------------------------------------------------------- #
def _mat(model, r: ResolvedGraphicsCardConfig, key: str):
    return model.material(f"gpu_{key}", rgba=PALETTES[r.palette_style][key])


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)):
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)):
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _rounded_plate_mesh(
    assets, tag, x0, x1, y0, y1, thickness, holes, corner=0.006, extra_rect_cut=None
):
    """A rectangular (optionally rounded) plate in XY, +Z thickness, with circular
    fan holes and an optional rectangular cutout. Returns a Mesh."""
    w = x1 - x0
    h = y1 - y0
    cx = (x0 + x1) * 0.5
    cy = (y0 + y1) * 0.5
    wp = cq.Workplane("XY").center(cx, cy)
    if corner > 0.0:
        plate = wp.rect(w, h).extrude(thickness)
        plate = plate.edges("|Z").fillet(min(corner, 0.4 * min(w, h)))
    else:
        plate = wp.rect(w, h).extrude(thickness)
    for (hx, hy, hr) in holes:
        plate = plate.cut(
            cq.Workplane("XY").workplane(offset=-0.001).center(hx, hy).circle(hr).extrude(
                thickness + 0.002
            )
        )
    if extra_rect_cut is not None:
        rx, ry, rw, rh = extra_rect_cut
        plate = plate.cut(
            cq.Workplane("XY").workplane(offset=-0.001).center(rx, ry).rect(rw, rh).extrude(
                thickness + 0.002
            )
        )
    return mesh_from_cadquery(plate, assets.mesh_path(f"{tag}.obj"), tolerance=0.0004)


# --------------------------------------------------------------------------- #
# card_body: fused non-moving structure
# --------------------------------------------------------------------------- #
def _build_pcb_and_heatsink(body, r, assets, mats):
    L, H, T = r.card_length, r.card_height, r.pcb_thickness
    _box(body, (L, H, T), (0.0, 0.0, 0.0), mats["pcb"], "pcb")

    # Gold PCIe x16 edge connector hanging below the -Y edge (S_MSI L185-197).
    conn_len = min(L * 0.55, 0.170)
    conn_cx = -L * 0.5 + 0.070
    _box(
        body,
        (conn_len, 0.012, 0.0016),
        (conn_cx, -H * 0.5 - 0.006, 0.0),
        mats["gold"],
        "pcie_contact_bar",
    )
    n_fingers = 16 if L > 0.24 else 10
    fstep = conn_len / n_fingers
    for i in range(n_fingers):
        fx = conn_cx - conn_len * 0.5 + (i + 0.5) * fstep
        _box(
            body,
            (fstep * 0.55, 0.007, 0.0018),
            (fx, -H * 0.5 - 0.011, 0.0),
            mats["gold"],
            f"pcie_finger_{i}",
        )

    # Heatsink baseplate + dense fin stack (S_MSI L199-218 / S_GB L250-268).
    span_x = L * 0.72
    base_cx = 0.006
    _box(
        body,
        (span_x, H * 0.80, r.base_t),
        (base_cx, 0.0, r.z_pcb_top + r.base_t * 0.5),
        mats["fin"],
        "heatsink_base",
    )
    fin_z0 = r.z_pcb_top + r.base_t
    fin_cz = fin_z0 + r.fin_h * 0.5
    x_first = base_cx - span_x * 0.5 + 0.006
    fstep2 = (span_x - 0.012) / max(1, r.fin_count)
    for i in range(r.fin_count):
        fx = x_first + (i + 0.5) * fstep2
        _box(
            body,
            (max(0.0012, fstep2 * 0.34), H * 0.70, r.fin_h),
            (fx, 0.0, fin_cz),
            mats["fin"],
            f"cooling_fin_{i}",
        )
    # heatpipes peeking along the lower fin edge (S_MSI L221-227).
    for k, yy in enumerate((-H * 0.20, 0.0, H * 0.20)):
        _cyl(
            body,
            0.0030,
            span_x * 0.92,
            (base_cx, yy, fin_z0 + 0.004),
            mats["copper"],
            f"heatpipe_{k}",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )

    # motor bosses under each fan hub (S_MSI L230-236).
    boss_len = r.fan_z - r.boss_z0 + r.rotor_t * 0.4
    for i, fx in enumerate(r.fan_centers_x):
        _cyl(
            body,
            max(0.010, r.fan_radius * 0.28),
            boss_len,
            (fx, 0.0, r.boss_z0 + boss_len * 0.5),
            mats["port"],
            f"motor_boss_{i}",
        )


def _build_io_bracket(body, r, mats):
    L, H = r.card_length, r.card_height
    xf = -L * 0.5 - 0.003
    bracket_h = H * (1.10 if H > 0.11 else 1.02)
    _box(body, (0.006, bracket_h, 0.062), (xf, 0.0, 0.026), mats["metal"], "io_bracket_plate")
    # foot lapping onto the PCB edge (contact / support).
    _box(body, (0.010, H * 0.86, 0.008), (-L * 0.5 + 0.004, 0.0, 0.0), mats["metal"], "io_bracket_foot")
    # display ports behind the bracket openings (S_MSI L269-281).
    for i, yc in enumerate((-0.030, 0.000, 0.030)):
        _box(body, (0.012, 0.016, 0.010), (-L * 0.5 + 0.004, yc, 0.020), mats["port"], f"display_port_{i}")
    _box(body, (0.012, 0.014, 0.010), (-L * 0.5 + 0.004, 0.058, 0.020), mats["port"], "hdmi_port")
    # bracket vents.
    for i in range(4):
        _box(
            body,
            (0.004, 0.006, 0.0025),
            (xf, -H * 0.30 + i * H * 0.16, 0.050),
            mats["port"],
            f"bracket_vent_{i}",
        )


def _build_power_connector(body, r, mats):
    if r.power_connector == "absent":
        return
    L, H = r.card_length, r.card_height
    yt = H * 0.5
    # block bottom dips ~2.5 mm into the PCB top so it seats (no float).
    z = r.z_pcb_top + 0.003
    xc = min(L * 0.10, L * 0.5 - 0.035)  # keep the block on the board
    if r.power_connector == "single_8pin":
        _box(body, (0.040, 0.011, 0.011), (xc, yt - 0.005, z), mats["port"], "power_connector_8pin_0")
    elif r.power_connector == "row_8pin":
        pitch = 0.050
        n = r.n_8pin
        for i in range(n):
            cx = xc + (i - (n - 1) * 0.5) * pitch
            cx = max(-L * 0.5 + 0.030, min(L * 0.5 - 0.030, cx))
            _box(body, (0.040, 0.011, 0.011), (cx, yt - 0.005, z), mats["port"], f"power_connector_8pin_{i}")
    else:  # 12vhpwr_16pin
        _box(body, (0.044, 0.013, 0.0125), (xc, yt - 0.006, z), mats["port"], "power_connector_12vhpwr")
        _box(body, (0.012, 0.010, 0.0105), (min(L * 0.5 - 0.020, xc + 0.028), yt - 0.005, z), mats["port"], "power_connector_sense_band")


def _build_backplate(body, r, assets, mats):
    if r.backplate == "absent":
        return
    L, H, T = r.card_length, r.card_height, r.pcb_thickness
    back_t = 0.003
    z_center = -T * 0.5 - back_t * 0.5 + 0.0006  # slight embed onto rear face
    x0, x1 = -L * 0.5 + 0.006, L * 0.5 - 0.006
    y0, y1 = -H * 0.5 + 0.004, H * 0.5 - 0.004
    if r.backplate == "present_with_cutout":
        mesh = _rounded_plate_mesh(
            assets,
            "backplate_plate",
            x0,
            x1,
            y0,
            y1,
            back_t,
            holes=(),
            corner=0.006,
            extra_rect_cut=(L * 0.30, 0.0, 0.030, H * 0.42),
        )
        body.visual(
            mesh,
            origin=Origin(xyz=(0.0, 0.0, z_center - back_t * 0.5)),
            material=mats["backplate"],
            name="backplate_plate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"all_black_gaming", "gunmetal_gray", "black_rgb", "zotac_copper", "white_rgb"} else "metal.aluminum_bare"),
        )
    else:  # present_solid
        _box(body, (x1 - x0, y1 - y0, back_t), ((x0 + x1) * 0.5, 0.0, z_center), mats["backplate"], "backplate_plate")
    # brand strip + screw dots (decoration, S_GB L182-196).
    _box(body, (L * 0.30, back_t * 0.6, 0.012), (0.0, 0.0, z_center - back_t * 0.5), mats["metal"], "backplate_brand")
    for i, (sx, sy) in enumerate(((x0 + 0.02, y0 + 0.01), (x0 + 0.02, y1 - 0.01), (x1 - 0.02, y0 + 0.01), (x1 - 0.02, y1 - 0.01))):
        _cyl(body, 0.0024, back_t * 0.5, (sx, sy, z_center - back_t * 0.5), mats["metal"], f"backplate_screw_{i}", rpy=(0.0, 0.0, 0.0))


# --- Slot A shroud forms (VISUALS on card_body) ---------------------------- #
def _shroud_holes(r):
    return [(fx, 0.0, r.hole_radius) for fx in r.fan_centers_x]


def _build_shroud(body, r, assets, mats):
    L, H = r.card_length, r.card_height
    form = r.cooler_shroud_form
    x0, x1 = -L * 0.5 + 0.006, L * 0.5 - 0.006
    y0, y1 = -H * 0.5 + 0.004, H * 0.5 - 0.004
    fz = r.face_z
    ft = r.face_t

    if form == "flow_through_founders":
        # faceplate stops after the last fan, leaving an open finned tail duct.
        last_fx = max(r.fan_centers_x)
        plate_x1 = min(x1, last_fx + r.hole_radius + 0.010)
        holes = _shroud_holes(r)
        mesh = _rounded_plate_mesh(assets, "shroud_faceplate", x0, plate_x1, y0, y1, ft, holes, corner=0.005)
        body.visual(mesh, origin=Origin(xyz=(0.0, 0.0, fz - ft * 0.5)), material=mats["shroud"], name="shroud_faceplate", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"all_black_gaming", "gunmetal_gray", "black_rgb", "zotac_copper", "white_rgb"} else "metal.aluminum_bare"))
        # open tail: chevron trim seated on the plate tail edge (overlaps the plate).
        _box(body, (0.010, H * 0.7, 0.005), (plate_x1 - 0.003, 0.0, fz + ft * 0.5), mats["accent"], "founders_chevron")
    elif form == "blower_radial":
        # fully enclosed plate: only a small hub vent, top intake grille + exhaust louvers.
        fx = r.fan_centers_x[0]
        holes = [(fx, 0.0, r.fan_radius * 0.34)]
        mesh = _rounded_plate_mesh(
            assets, "shroud_faceplate", x0, x1, y0, y1, ft, holes, corner=0.006,
        )
        body.visual(mesh, origin=Origin(xyz=(0.0, 0.0, fz - ft * 0.5)), material=mats["shroud"], name="shroud_faceplate", material_class_id="plastic.opaque_glossy_molded")
        for i in range(6):
            _box(body, (0.007, 0.010, 0.004), (fx - 0.03 + i * 0.012, y1 - 0.010, fz + ft * 0.5), mats["accent"], f"intake_grille_bar_{i}")
        for i in range(4):
            _box(body, (0.004, H * 0.5, 0.010), (x0 + 0.006 + i * 0.006, -H * 0.10, fz - 0.002), mats["accent"], f"exhaust_louver_{i}", rpy=(0.30, 0.0, 0.0))
    else:
        # open_axial_gaming / compact_itx_open_axial / vapor_chamber_full_cover
        holes = _shroud_holes(r)
        corner = 0.010 if form == "compact_itx_open_axial" else 0.005
        mesh = _rounded_plate_mesh(assets, "shroud_faceplate", x0, x1, y0, y1, ft, holes, corner=corner)
        body.visual(mesh, origin=Origin(xyz=(0.0, 0.0, fz - ft * 0.5)), material=mats["shroud"], name="shroud_faceplate", material_class_id="plastic.opaque_glossy_molded")

    # perimeter skirt walls down to the PCB (all forms; supports the plate).
    wall_h = fz - r.z_pcb_top
    wall_cz = r.z_pcb_top + wall_h * 0.5
    _box(body, (L * 0.94, 0.005, wall_h), (0.0, y1, wall_cz), mats["shroud"], "skirt_wall_top")
    _box(body, (L * 0.94, 0.005, wall_h), (0.0, y0, wall_cz), mats["shroud"], "skirt_wall_bottom")
    _box(body, (0.005, H * 0.92, wall_h), (x0, 0.0, wall_cz), mats["shroud"], "skirt_wall_head")
    _box(body, (0.005, H * 0.92, wall_h), (x1, 0.0, wall_cz), mats["shroud"], "skirt_wall_tail")

    # ---- form-specific decoration (④, host-conformal on the face plane) ----
    if form == "open_axial_gaming":
        for i, xx in enumerate((-L * 0.18, L * 0.06, L * 0.24)):
            _box(body, (0.012, H * 0.82, 0.003), (xx, 0.0, fz + 0.002), mats["accent"], f"accent_strap_{i}", rpy=(0.0, 0.0, 0.22))
        for i, (xx, yy) in enumerate(((x0 + 0.03, y1 - 0.02), (x1 - 0.03, y0 + 0.02))):
            _box(body, (0.03, 0.006, 0.003), (xx, yy, fz + 0.002), mats["accent"], f"accent_wedge_{i}", rpy=(0.0, 0.0, 0.4))
        # RGB diffuser strip along the top edge (decoration).
        _box(body, (L * 0.80, 0.008, 0.003), (0.0, y1 - 0.002, fz + 0.0015), mats["rgb"], "rgb_diffuser_strip")
    elif form == "compact_itx_open_axial":
        fx = r.fan_centers_x[0]
        for i, side in enumerate((-1, 1)):
            _box(body, (0.004, H * 0.8, 0.004), (fx + side * (r.hole_radius + 0.006), 0.0, fz + 0.001), mats["copper"], f"copper_strip_{i}")
        # diagonal slat vent flanks.
        for i in range(4):
            _box(body, (0.03, 0.004, 0.004), (x1 - 0.012, -H * 0.18 + i * H * 0.12, fz - 0.001), mats["accent"], f"slat_vent_{i}", rpy=(0.0, 0.0, -math.pi / 4))
        _box(body, (0.03, 0.004, 0.002), (x0 + 0.02, y1 - 0.004, fz + 0.002), mats["copper"], "logo_strip")
    elif form == "vapor_chamber_full_cover":
        _box(body, (L * 0.86, 0.006, 0.002), (0.0, 0.0, fz + 0.002), mats["accent"], "vapor_seam")


# --------------------------------------------------------------------------- #
# Slot B: fan rotor (shared mesh helper)
# --------------------------------------------------------------------------- #
def _rotor_mesh(assets, r):
    geom = FanRotorGeometry(
        outer_radius=r.fan_radius,
        hub_radius=max(0.006, r.fan_radius * 0.30),
        blade_count=r.blade_count,
        thickness=r.rotor_t,
        blade_pitch_deg=32.0,
        blade_sweep_deg=30.0,
        blade=FanRotorBlade(shape="scimitar", camber=0.18, tip_clearance=0.0015),
        hub=FanRotorHub(style="flat"),
    )
    return mesh_from_geometry(geom, assets.mesh_path("fan_rotor.obj"))


def _add_fan(model, r, index, rotor_mesh, mats):
    fan = model.part(f"fan_{index}")
    fan.visual(rotor_mesh, origin=Origin(xyz=(0.0, 0.0, 0.0)), material=mats["fan"], name="rotor_blades", material_class_id="plastic.opaque_glossy_molded")
    hub_r = max(0.006, r.fan_radius * 0.30)
    # Hub stack straddles the rotor mid-plane so every element overlaps the rotor
    # mesh hub (concentric radial contact) and the next element -- no islands.
    _cyl(fan, hub_r * 1.02, r.rotor_t + 0.0020, (0.0, 0.0, 0.0), mats["badge"], "hub_ring")
    _cyl(fan, hub_r * 0.64, r.rotor_t + 0.0040, (0.0, 0.0, 0.0), mats["fan"], "hub_cap")
    # off-axis badge chip so spin is observable (overlaps the proud hub_cap top).
    _box(fan, (0.009, 0.005, 0.0016), (hub_r * 0.40, 0.0, r.rotor_t * 0.5 + 0.0010), mats["badge"], "hub_badge")
    return fan


# --------------------------------------------------------------------------- #
# Slot E: fold-out support foot (REVOLUTE)
# --------------------------------------------------------------------------- #
def _add_support_foot(model, r, body, mats):
    L, H = r.card_length, r.card_height
    lug_x = L * 0.5 - 0.012
    lug_y = -H * 0.5 + 0.006
    lug_z = 0.0
    # hinge lug barrel on the card body (visual).
    _cyl(body, 0.004, 0.014, (lug_x, lug_y, lug_z), mats["metal"], "support_foot_hinge_lug", rpy=(0.0, math.pi / 2.0, 0.0))

    foot = model.part("support_foot")
    # strut extends along -Y when stowed (q=0); pivot bore captured on the lug.
    foot.visual(Box((0.006, 0.045, 0.004)), origin=Origin(xyz=(0.0, -0.0225, 0.0)), material=mats["metal"], name="foot_strut", material_class_id=("metal.blackened_gunmetal" if r.palette_style in {"all_black_gaming", "gunmetal_gray", "black_rgb", "zotac_copper", "white_rgb"} else "metal.aluminum_bare"))
    foot.visual(Box((0.018, 0.008, 0.005)), origin=Origin(xyz=(0.0, -0.049, 0.0)), material=mats["fan"], name="foot_pad", material_class_id="rubber.smooth_plain")

    origin = (lug_x, lug_y, lug_z)
    model.articulation(
        "support_foot_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=foot,
        origin=Origin(xyz=origin),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=1.5, lower=0.0, upper=math.pi / 2.0),
        meta={"type": "revolute", "axis": (1.0, 0.0, 0.0), "origin": origin, "range": (0.0, math.pi / 2.0), "source_id": "S_SB"},
    )


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_graphics_card(
    config: GraphicsCardConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or GraphicsCardConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-gpu-")))
    model = ArticulatedObject(name=r.name, assets=assets)

    mats = {k: _mat(model, r, k) for k in PALETTES[r.palette_style].keys()}

    body = model.part("card_body")
    _build_pcb_and_heatsink(body, r, assets, mats)
    _build_io_bracket(body, r, mats)
    _build_backplate(body, r, assets, mats)
    _build_power_connector(body, r, mats)
    _build_shroud(body, r, assets, mats)

    # N cooling fans — homogeneous copies on CONTINUOUS spin joints (dominant axis).
    rotor_mesh = _rotor_mesh(assets, r)
    for i, fx in enumerate(r.fan_centers_x):
        _add_fan(model, r, i, rotor_mesh, mats)
        origin = (fx, 0.0, r.fan_z)
        model.articulation(
            f"fan_{i}_spin",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=f"fan_{i}",
            origin=Origin(xyz=origin),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=0.4, velocity=120.0),
            meta={"type": "continuous", "axis": (0.0, 0.0, 1.0), "origin": origin, "range": "unbounded", "source_id": "S_MSI"},
        )

    if r.support_bracket == "foldout_support_foot":
        _add_support_foot(model, r, body, mats)

    return model


def build_seeded_graphics_card(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_graphics_card(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def run_graphics_card_tests(
    object_model: ArticulatedObject | None = None, config: GraphicsCardConfig | None = None
) -> TestReport:
    config = config or GraphicsCardConfig()
    model = object_model or build_graphics_card(config)
    r = resolve_config(config)
    ctx = TestContext(model)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()

    body = model.get_part("card_body")

    # Rotor hubs are seated onto the motor bosses (captured-pin, grandfathered).
    for i in range(r.fan_count):
        for elem in ("rotor_blades", "hub_ring", "hub_cap"):
            ctx.allow_overlap(
                "card_body",
                f"fan_{i}",
                elem_a=f"motor_boss_{i}",
                elem_b=elem,
                reason="Rotor hub (blades + hub cylinders) is seated onto the axisymmetric motor boss bearing (captured spin seat).",
            )
        ctx.expect_contact(
            f"fan_{i}", "card_body", elem_a="rotor_blades", elem_b=f"motor_boss_{i}",
            name=f"fan_{i}_hub_seats_on_motor_boss",
        )
    if r.support_bracket == "foldout_support_foot":
        ctx.allow_overlap(
            "card_body", "support_foot", elem_a="support_foot_hinge_lug", elem_b="foot_strut",
            reason="Hinge lug barrel captures the foot strut pivot bore (captured-pin hinge).",
        )

    ctx.fail_if_isolated_parts()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=96, ignore_fixed=True)

    # ---- N fans, each a CONTINUOUS spin about (0,0,1) ----
    fan_joints = [j for j in model.articulations if j.name.startswith("fan_") and j.name.endswith("_spin")]
    ctx.check("fan_joint_count", len(fan_joints) == r.fan_count, f"got {len(fan_joints)} want {r.fan_count}")
    fan_parts = [p for p in model.parts if p.name.startswith("fan_")]
    ctx.check("fan_part_count", len(fan_parts) == r.fan_count, f"got {len(fan_parts)}")
    for j in fan_joints:
        ctx.check(f"{j.name}_continuous", j.articulation_type == ArticulationType.CONTINUOUS, f"type={j.articulation_type}")
        ctx.check(f"{j.name}_axis_z", tuple(j.axis) == (0.0, 0.0, 1.0), f"axis={j.axis}")

    # each fan spins in place: off-axis badge displaces, origin stays fixed.
    for i in range(r.fan_count):
        fan = model.get_part(f"fan_{i}")
        rest_pos = ctx.part_world_position(fan)
        rest = ctx.part_element_world_aabb(fan, elem="hub_badge")
        if rest is None:
            ctx.check(f"fan_{i}_badge_present", False, "missing hub_badge")
            continue
        rc = [(rest[0][k] + rest[1][k]) * 0.5 for k in range(3)]
        with ctx.pose({f"fan_{i}_spin": math.pi}):
            posed_pos = ctx.part_world_position(fan)
            posed = ctx.part_element_world_aabb(fan, elem="hub_badge")
            pc = [(posed[0][k] + posed[1][k]) * 0.5 for k in range(3)]
            ctx.check(f"fan_{i}_spin_displaces_badge", math.dist(rc, pc) > 0.004, f"disp={math.dist(rc, pc):.4f}")
            ctx.check(f"fan_{i}_spins_in_place", math.dist(rest_pos, posed_pos) < 1e-9, f"rest={rest_pos} posed={posed_pos}")

    # ---- identity checks ----
    names = {v.name for v in body.visuals}
    ctx.check("has_pcb", "pcb" in names, "pcb missing")
    ctx.check("has_pcie_fingers", any(n.startswith("pcie_finger_") for n in names), "pcie fingers missing")
    ctx.check("has_io_bracket", "io_bracket_plate" in names, "io bracket missing")
    ctx.check("has_shroud_faceplate", "shroud_faceplate" in names, "shroud faceplate missing")
    ctx.check("has_fins", any(n.startswith("cooling_fin_") for n in names), "fins missing")

    # gold edge connector below the PCB bottom edge.
    pcb_aabb = ctx.part_element_world_aabb(body, elem="pcb")
    conn_aabb = ctx.part_element_world_aabb(body, elem="pcie_contact_bar")
    ctx.check(
        "connector_below_pcb",
        conn_aabb is not None and pcb_aabb is not None and conn_aabb[0][1] < pcb_aabb[0][1] - 0.002,
        f"pcb={pcb_aabb} conn={conn_aabb}",
    )

    # fans fit within the card height.
    for i, fx in enumerate(r.fan_centers_x):
        ctx.check(f"fan_{i}_fits_height", r.fan_radius < r.card_height * 0.5 - 0.002, f"r={r.fan_radius} H={r.card_height}")

    # ---- support foot (Slot E) ----
    if r.support_bracket == "foldout_support_foot":
        foot_hinge = model.get_articulation("support_foot_hinge")
        ctx.check("support_hinge_revolute", foot_hinge.articulation_type == ArticulationType.REVOLUTE, f"type={foot_hinge.articulation_type}")
        ctx.check("support_hinge_axis_x", tuple(foot_hinge.axis) == (1.0, 0.0, 0.0), f"axis={foot_hinge.axis}")
        foot = model.get_part("support_foot")
        stow = ctx.part_element_world_aabb(foot, elem="foot_pad")
        stow_c = [(stow[0][k] + stow[1][k]) * 0.5 for k in range(3)]
        with ctx.pose({"support_foot_hinge": math.pi / 2.0}):
            depl = ctx.part_element_world_aabb(foot, elem="foot_pad")
            depl_c = [(depl[0][k] + depl[1][k]) * 0.5 for k in range(3)]
            ctx.check("support_foot_deploys", math.dist(stow_c, depl_c) > 0.02, f"disp={math.dist(stow_c, depl_c):.4f}")

    return ctx.report()
