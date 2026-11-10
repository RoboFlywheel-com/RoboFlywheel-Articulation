# SPDX-License-Identifier: Apache-2.0

"""Agricultural / Greenhouse vent roof — modular parametric template.

A glazed greenhouse ROOF SECTION (an architectural roof bay, NOT a whole
building and NOT a wall window): a pitched aluminium/timber ``roof_frame``
carrying a glazing field, with a mid-slope operable ventilation opening driven
by one of four mechanisms. Every seed keeps at least one real opening joint.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/greenhouse_vent_roof.md`` and the
10 synced 5-star records (1 origin + 9 slot-fork variants) under ``data/records/``.

Structure (pattern = ``mixed``): a single root ``roof_frame`` part (its rake /
eave / ridge geometry chosen by ``roof_geometry``, its fixed glazing field by
``glazing``, its bar cross-section + material by ``frame_member``), with the
operable mechanism (chosen by ``vent_mechanism``) parented to it:

  * ``roof_geometry`` (3): mono_pitch (single ``_plane_xyz`` slope) / even_span
    (horizontal ridge cap + mirrored left slope) / curved_eave (arched rafters
    via ``sweep_profile_along_spline`` mesh + lower-field arch purlins). All
    three keep the glazing / curb / hinge / mechanism in the SAME primary-slope
    ``_plane_xyz`` frame, so roof_geometry is orthogonal to the mechanism.
  * ``vent_mechanism`` (4): top_hinged_prop (N sashes, each a top-hinged
    REVOLUTE + folding stay + latch) / louvre_bank (N blades, each REVOLUTE) /
    sliding_panel (1 panel, PRISMATIC down-slope + latch) / ridge_flap (1 long
    ridge flap, REVOLUTE + stay + latch).
  * ``glazing`` (2): multi_pane_grid (3x2 pane grid + transom_mid/mullions) /
    single_pane (2 large rafter-to-rafter sheets).
  * ``frame_member`` (2): aluminium_box (thin metal box bars) / timber_bar
    (thicker timber sections + host-conformal putty glazing beads).
  * ``sash_count`` (N in [1,3], top_hinged only) / ``louvre_count``
    (N in [4,8], louvre only): two mutually-exclusive multiplicity axes,
    each encoded into the slot_choice tuple as ``("*_count", f"n{N}")``.

All hinge pins / axles / slider shoes / mount tabs are captured-pin/slide
geometry, so those joints omit ``MatingContract`` (grandfathered) and are
guarded by the flat articulation-origin baseline + element-scoped
``allow_overlap`` (mirroring each source record's run_tests allow_overlap block).

Compatibility gating (resolve_config, spec 9):
  * timber_bar frame_member <=> natural_timber palette (putty emitted);
    aluminium_box <=> one of the 5 metal/painted palettes.
  * sash_count active only for top_hinged; louvre_count active only for louvre;
    the inactive axis is pinned to a sentinel.
  * curved_eave arch purlins are placed only in the lower field (u > vent band)
    so an opening sash/flap never sweeps into them.
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
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    sweep_profile_along_spline,
)

__modular__ = True

RoofGeometry = Literal["mono_pitch", "even_span", "curved_eave"]
VentMechanism = Literal["top_hinged_prop", "louvre_bank", "sliding_panel", "ridge_flap"]
Glazing = Literal["multi_pane_grid", "single_pane"]
FrameMember = Literal["aluminium_box", "timber_bar"]
PaletteStyle = Literal[
    "mill_aluminium",
    "white_painted",
    "green_painted",
    "natural_timber",
    "galvanized_steel",
    "anthracite_tinted",
]

ROOF_GEOMETRIES: tuple[RoofGeometry, ...] = ("mono_pitch", "even_span", "curved_eave")
VENT_MECHANISMS: tuple[VentMechanism, ...] = (
    "top_hinged_prop",
    "louvre_bank",
    "sliding_panel",
    "ridge_flap",
)
GLAZINGS: tuple[Glazing, ...] = ("multi_pane_grid", "single_pane")
FRAME_MEMBERS: tuple[FrameMember, ...] = ("aluminium_box", "timber_bar")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "mill_aluminium",
    "white_painted",
    "green_painted",
    "natural_timber",
    "galvanized_steel",
    "anthracite_tinted",
)
# timber_bar frame <=> the timber palette; aluminium_box <=> the 5 metal/painted.
_TIMBER_PALETTE: PaletteStyle = "natural_timber"
_ALU_PALETTES: tuple[PaletteStyle, ...] = (
    "mill_aluminium",
    "white_painted",
    "green_painted",
    "galvanized_steel",
    "anthracite_tinted",
)

SASH_N_MIN, SASH_N_MAX = 1, 3
SASH_N_WEIGHTS = (0.5, 0.3, 0.2)  # spec 8: 1 high-freq, 2 common, 3 tail
LOUVRE_N_MIN, LOUVRE_N_MAX = 4, 8
LOUVRE_N_WEIGHTS = (0.28, 0.26, 0.22, 0.14, 0.10)

# --- Fixed real-world geometry (meters), from the origin/source records. -----
HALF_W = 0.72  # half width across the slope (world Y)
EAVE_U = 2.60  # down-slope run from ridge to eave
VENT_U0, VENT_U1 = 0.07, 1.28  # sash/louvre/sliding opening band along slope
VENT_HALF = 0.46  # sash/louvre/sliding opening half-width across
FLAP_U0, FLAP_U1 = 0.06, 1.16  # ridge-flap opening band
FLAP_HALF = 0.62  # ridge-flap half-width (wider than a sash)
RIDGE_HEIGHT_BASE = 2.18
ARCH_RISE = 0.20  # curved_eave arch bow above the straight pitch line
TRANSOM_MID_U = 1.52  # lower-field mid transom (kept clear of the sliding panel)

# Shared hardware colours (constant across palettes; only frame + glass vary).
_SHARED_RGBA: dict[str, tuple[float, float, float, float]] = {
    "hardware": (0.55, 0.57, 0.52, 1.0),
    "rubber": (0.02, 0.02, 0.02, 1.0),
    "black_steel": (0.04, 0.04, 0.045, 1.0),
    "bolt": (0.03, 0.03, 0.03, 1.0),
    "jute": (0.42, 0.34, 0.22, 1.0),
    "wire": (0.62, 0.60, 0.55, 1.0),
    "putty": (0.88, 0.84, 0.72, 1.0),
}
_FRAME_RGBA: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "mill_aluminium": {
        "frame": (0.76, 0.77, 0.74, 1.0),
        "frame_accent": (0.55, 0.56, 0.53, 1.0),
        "glass": (0.60, 0.80, 0.95, 0.26),
    },
    "white_painted": {
        "frame": (0.92, 0.92, 0.90, 1.0),
        "frame_accent": (0.80, 0.80, 0.78, 1.0),
        "glass": (0.62, 0.82, 0.95, 0.24),
    },
    "green_painted": {
        "frame": (0.20, 0.42, 0.24, 1.0),
        "frame_accent": (0.14, 0.30, 0.17, 1.0),
        "glass": (0.62, 0.85, 0.90, 0.26),
    },
    "natural_timber": {
        "frame": (0.58, 0.40, 0.22, 1.0),
        "frame_accent": (0.44, 0.32, 0.19, 1.0),
        "glass": (0.60, 0.80, 0.95, 0.26),
    },
    "galvanized_steel": {
        "frame": (0.62, 0.63, 0.60, 1.0),
        "frame_accent": (0.48, 0.49, 0.47, 1.0),
        "glass": (0.60, 0.80, 0.95, 0.26),
    },
    "anthracite_tinted": {
        "frame": (0.18, 0.19, 0.20, 1.0),
        "frame_accent": (0.10, 0.11, 0.12, 1.0),
        "glass": (0.32, 0.42, 0.40, 0.42),
    },
}


def _palette_rgba(style: PaletteStyle) -> dict[str, tuple[float, float, float, float]]:
    return {**_SHARED_RGBA, **_FRAME_RGBA[style]}


@dataclass(frozen=True)
class GreenhouseVentRoofConfig:
    roof_geometry: RoofGeometry | None = None
    vent_mechanism: VentMechanism | None = None
    glazing: Glazing | None = None
    frame_member: FrameMember | None = None
    sash_count: int | None = None
    louvre_count: int | None = None
    palette_style: PaletteStyle | None = None
    pitch: float = 0.42
    ridge_height_scale: float = 1.0
    open_travel_scale: float = 1.0
    name: str = "greenhouse_vent_roof"


@dataclass(frozen=True)
class ResolvedGreenhouseVentRoofConfig:
    roof_geometry: RoofGeometry
    vent_mechanism: VentMechanism
    glazing: Glazing
    frame_member: FrameMember
    sash_count: int
    louvre_count: int
    palette_style: PaletteStyle
    # slope frame
    pitch: float
    cos_p: float
    sin_p: float
    ridge_height: float
    frame_thick: float  # bar cross-section factor (1.0 alu, >1 timber)
    emit_putty: bool
    # opening geometry (mechanism-dependent)
    vent_half_eff: float
    side_mullion_v: float
    emit_side_glass: bool
    # motion envelopes
    sash_open: float
    louvre_open: float
    slide_travel: float
    flap_open: float
    stay_open: float
    latch_open: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices, default):
    return value if value in choices else default


def config_from_seed(seed: int) -> GreenhouseVentRoofConfig:
    rng = random.Random(seed)
    frame_member = rng.choices(FRAME_MEMBERS, weights=(0.68, 0.32), k=1)[0]
    if frame_member == "timber_bar":
        palette = _TIMBER_PALETTE
    else:
        palette = rng.choice(_ALU_PALETTES)
    return GreenhouseVentRoofConfig(
        roof_geometry=rng.choice(ROOF_GEOMETRIES),
        vent_mechanism=rng.choice(VENT_MECHANISMS),
        glazing=rng.choice(GLAZINGS),
        frame_member=frame_member,
        sash_count=rng.choices((1, 2, 3), weights=SASH_N_WEIGHTS, k=1)[0],
        louvre_count=rng.choices(
            tuple(range(LOUVRE_N_MIN, LOUVRE_N_MAX + 1)), weights=LOUVRE_N_WEIGHTS, k=1
        )[0],
        palette_style=palette,
        pitch=round(rng.uniform(0.32, 0.50), 4),
        ridge_height_scale=round(rng.uniform(0.90, 1.12), 4),
        open_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_greenhouse_vent_roof_{seed}",
    )


def resolve_config(
    config: GreenhouseVentRoofConfig | None = None,
) -> ResolvedGreenhouseVentRoofConfig:
    cfg = config or GreenhouseVentRoofConfig()

    roof_geometry = _pick(cfg.roof_geometry, ROOF_GEOMETRIES, "mono_pitch")
    vent_mechanism = _pick(cfg.vent_mechanism, VENT_MECHANISMS, "top_hinged_prop")
    glazing = _pick(cfg.glazing, GLAZINGS, "multi_pane_grid")
    frame_member = _pick(cfg.frame_member, FRAME_MEMBERS, "aluminium_box")

    # --- Compatibility gating (spec 9): frame_member <-> palette. ---
    palette = _pick(cfg.palette_style, PALETTE_STYLES, "mill_aluminium")
    if frame_member == "timber_bar":
        palette = _TIMBER_PALETTE
    elif palette == _TIMBER_PALETTE:  # aluminium_box cannot wear the timber palette
        palette = "mill_aluminium"
    emit_putty = frame_member == "timber_bar"
    frame_thick = 1.16 if frame_member == "timber_bar" else 1.0

    # --- Multiplicity axes are active only for their mechanism. ---
    sash_count = int(cfg.sash_count) if cfg.sash_count is not None else 1
    sash_count = int(_clamp(sash_count, SASH_N_MIN, SASH_N_MAX))
    louvre_count = int(cfg.louvre_count) if cfg.louvre_count is not None else 6
    louvre_count = int(_clamp(louvre_count, LOUVRE_N_MIN, LOUVRE_N_MAX))
    if vent_mechanism != "top_hinged_prop":
        sash_count = 1  # sentinel (inactive axis)
    if vent_mechanism != "louvre_bank":
        louvre_count = 0  # sentinel (inactive axis)

    pitch = _clamp(cfg.pitch, 0.32, 0.50)
    ridge_height = RIDGE_HEIGHT_BASE * _clamp(cfg.ridge_height_scale, 0.90, 1.12)
    open_scale = _clamp(cfg.open_travel_scale, 0.85, 1.10)

    # opening geometry
    vent_half_eff = FLAP_HALF if vent_mechanism == "ridge_flap" else VENT_HALF
    side_mullion_v = min(vent_half_eff + 0.14, HALF_W - 0.06)
    emit_side_glass = vent_mechanism != "ridge_flap"

    return ResolvedGreenhouseVentRoofConfig(
        roof_geometry=roof_geometry,
        vent_mechanism=vent_mechanism,
        glazing=glazing,
        frame_member=frame_member,
        sash_count=sash_count,
        louvre_count=louvre_count,
        palette_style=palette,
        pitch=pitch,
        cos_p=math.cos(pitch),
        sin_p=math.sin(pitch),
        ridge_height=ridge_height,
        frame_thick=frame_thick,
        emit_putty=emit_putty,
        vent_half_eff=vent_half_eff,
        side_mullion_v=side_mullion_v,
        emit_side_glass=emit_side_glass,
        sash_open=_clamp(1.05 * open_scale, 0.70, 1.15),
        louvre_open=_clamp(0.70 * open_scale, 0.45, 0.85),
        slide_travel=_clamp(0.16 * open_scale, 0.12, 0.20),
        flap_open=_clamp(1.05 * open_scale, 0.70, 1.15),
        stay_open=_clamp(0.32 * open_scale, 0.20, 0.40),
        latch_open=0.40,
        name=cfg.name or "greenhouse_vent_roof",
    )


def with_overrides(
    config: GreenhouseVentRoofConfig, **kwargs: object
) -> GreenhouseVentRoofConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: GreenhouseVentRoofConfig | ResolvedGreenhouseVentRoofConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedGreenhouseVentRoofConfig)
        else resolve_config(config)
    )
    return (
        ("roof_geometry", r.roof_geometry),
        ("vent_mechanism", r.vent_mechanism),
        ("glazing", r.glazing),
        ("frame_member", r.frame_member),
        ("sash_count", f"n{r.sash_count}"),
        ("louvre_count", f"n{r.louvre_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Primary-slope coordinate helpers (all take the resolved config r for pitch).
# ---------------------------------------------------------------------------
def _plane_xyz(
    r: ResolvedGreenhouseVentRoofConfig, u: float, v: float, w: float
) -> tuple[float, float, float]:
    """Map primary-slope coords (u=down-slope, v=across=Y, w=out-of-plane) to xyz."""
    x = u * r.cos_p + w * r.sin_p
    y = v
    z = r.ridge_height - u * r.sin_p + w * r.cos_p
    return (x, y, z)


def _left_xyz(
    r: ResolvedGreenhouseVentRoofConfig, u: float, v: float, w: float
) -> tuple[float, float, float]:
    """Mirrored left slope (even_span only)."""
    x = -(u * r.cos_p) - w * r.sin_p
    y = v
    z = r.ridge_height - u * r.sin_p + w * r.cos_p
    return (x, y, z)


def _plane_box(part, name, size, r, u, v, w, material):
    part.visual(
        Box(size),
        origin=Origin(xyz=_plane_xyz(r, u, v, w), rpy=(0.0, r.pitch, 0.0)),
        material=material,
        name=name, material_class_id=("metal.paint_coated" if r.palette_style in {"mill_aluminium", "white_painted", "green_painted", "galvanized_steel", "anthracite_tinted"} else "wood.natural_generic"),
    )


def _left_box(part, name, size, r, u, v, w, material):
    part.visual(
        Box(size),
        origin=Origin(xyz=_left_xyz(r, u, v, w), rpy=(0.0, -r.pitch, 0.0)),
        material=material,
        name=name, material_class_id=("metal.paint_coated" if r.palette_style in {"mill_aluminium", "white_painted", "green_painted", "galvanized_steel", "anthracite_tinted"} else "wood.natural_generic"),
    )


def _plane_cyl_y(part, name, radius, length, r, u, v, w, material):
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=_plane_xyz(r, u, v, w), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.steel_galvanized",
    )


def _plane_screw(part, name, r, u, v, w, radius, length, material):
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=_plane_xyz(r, u, v, w), rpy=(0.0, r.pitch, 0.0)),
        material=material,
        name=name, material_class_id="metal.blackened_gunmetal",
    )


# Local-frame helpers (sash / latch / stay / panel / blade authored flat).
def _add_box(part, name, size, xyz, material, rpy=(0.0, 0.0, 0.0)):
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _add_cyl_y(part, name, radius, length, xyz, material):
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.steel_galvanized",
    )


def _tk(x: float, r: ResolvedGreenhouseVentRoofConfig) -> float:
    """Timber bars are visibly beefier: scale a cross-section dim by frame_thick."""
    return x * r.frame_thick


# ---------------------------------------------------------------------------
# Curved eave (Rule 3: keep the swept-mesh rafter, never a Box placeholder).
# ---------------------------------------------------------------------------
def _arch_path(r: ResolvedGreenhouseVentRoofConfig, v: float, n: int = 14):
    pts: list[tuple[float, float, float]] = []
    for k in range(n + 1):
        u = EAVE_U * k / n
        straight_x = u * r.cos_p
        straight_z = r.ridge_height - u * r.sin_p
        arch_z = ARCH_RISE * math.sin(math.pi * u / EAVE_U)
        pts.append((straight_x, v, straight_z + arch_z))
    return pts


def _build_arched_rake(r: ResolvedGreenhouseVentRoofConfig, v: float):
    path = _arch_path(r, v, n=14)
    profile = rounded_rect_profile(_tk(0.055, r), _tk(0.048, r), radius=0.006)
    return sweep_profile_along_spline(
        path,
        profile=profile,
        samples_per_segment=10,
        spline="catmull_rom",
        alpha=0.5,
        cap_profile=True,
        up_hint=(0.0, 0.0, 1.0),
    )


# ---------------------------------------------------------------------------
# roof_frame: geometry (A) + glazing field (C) + shared framing/decor + putty.
# ---------------------------------------------------------------------------
def _build_roof(model, r, mats):
    roof = model.part("roof_frame")
    frame = mats["frame"]
    accent = mats["frame_accent"]
    glass = mats["glass"]

    # --- ridge_rail (peak): even_span uses a horizontal cap, else pitched. ---
    if r.roof_geometry == "even_span":
        _add_box(
            roof,
            "ridge_rail",
            (_tk(0.085, r), 2 * HALF_W + 0.06, _tk(0.060, r)),
            (0.0, 0.0, r.ridge_height + 0.030),
            frame,
        )
    else:
        _plane_box(
            roof, "ridge_rail", (_tk(0.085, r), 2 * HALF_W + 0.06, _tk(0.060, r)),
            r, 0.0, 0.0, 0.028, frame,
        )
    _plane_box(
        roof, "eave_rail", (_tk(0.060, r), 2 * HALF_W + 0.06, _tk(0.050, r)),
        r, EAVE_U, 0.0, 0.022, frame,
    )

    # --- rakes / rafters (A) ---
    if r.roof_geometry == "curved_eave":
        for idx, (v_sign, mat) in enumerate(((-1.0, frame), (1.0, accent))):
            arch_mesh = _build_arched_rake(r, v_sign * HALF_W)
            roof.visual(
                mesh_from_geometry(arch_mesh, f"rake_arch_{idx}"),
                origin=Origin(xyz=(0.0, 0.0, 0.0)),
                material=mat,
                name=f"rake_arch_{idx}", material_class_id=("metal.paint_coated" if r.palette_style in {"mill_aluminium", "white_painted", "green_painted", "galvanized_steel", "anthracite_tinted"} else "wood.natural_generic"),
            )
        # Purlins only in the lower field (u > vent band) so an opening
        # sash/flap never sweeps into them.
        for pi_, u_station in enumerate((1.75, 2.25)):
            arch_z = ARCH_RISE * math.sin(math.pi * u_station / EAVE_U)
            mid = _plane_xyz(r, u_station, 0.0, 0.022)
            roof.visual(
                Box((_tk(0.042, r), 2 * HALF_W, _tk(0.038, r))),
                origin=Origin(xyz=(mid[0], 0.0, mid[2] + arch_z)),
                material=frame if pi_ % 2 == 0 else accent,
                name=f"arch_purlin_{pi_}", material_class_id=("metal.paint_coated" if r.palette_style in {"mill_aluminium", "white_painted", "green_painted", "galvanized_steel", "anthracite_tinted"} else "wood.natural_generic"),
            )
    else:
        _plane_box(
            roof, "rake_rail_0", (EAVE_U + 0.06, _tk(0.055, r), _tk(0.050, r)),
            r, EAVE_U / 2.0, -HALF_W, 0.022, frame,
        )
        _plane_box(
            roof, "rake_rail_1", (EAVE_U + 0.06, _tk(0.055, r), _tk(0.050, r)),
            r, EAVE_U / 2.0, HALF_W, 0.022, accent,
        )

    # --- even_span mirrored left slope (satisfies the two-slope identity) ---
    if r.roof_geometry == "even_span":
        _left_box(
            roof, "eave_rail_left", (_tk(0.060, r), 2 * HALF_W + 0.06, _tk(0.050, r)),
            r, EAVE_U, 0.0, 0.022, frame,
        )
        _left_box(
            roof, "rake_rail_left_0", (EAVE_U + 0.06, _tk(0.055, r), _tk(0.050, r)),
            r, EAVE_U / 2.0, -HALF_W, 0.022, frame,
        )
        _left_box(
            roof, "rake_rail_left_1", (EAVE_U + 0.06, _tk(0.055, r), _tk(0.050, r)),
            r, EAVE_U / 2.0, HALF_W, 0.022, accent,
        )
        for i, u in enumerate((0.70, 1.42, 2.02)):
            _left_box(
                roof, f"transom_left_{i}", (_tk(0.050, r), 2 * HALF_W, _tk(0.044, r)),
                r, u, 0.0, 0.024, accent if i < 2 else frame,
            )
        for i, v in enumerate((-0.24, 0.24)):
            _left_box(
                roof, f"mullion_left_{i}", (EAVE_U - 0.12, _tk(0.042, r), _tk(0.040, r)),
                r, EAVE_U / 2.0, v, 0.026, frame,
            )
        for ci, v in enumerate((-0.46, 0.0, 0.46)):
            for ri, u in enumerate((0.36, 1.06, 1.72, 2.31)):
                _left_box(
                    roof, f"glass_left_{ci}_{ri}", (0.50, 0.44, 0.006),
                    r, u, v, 0.045, glass,
                )

    # --- side mullions flanking the vent opening (right/primary slope) ---
    for i, v in enumerate((-r.side_mullion_v, r.side_mullion_v)):
        _plane_box(
            roof, f"mullion_side_{i}", (1.40, _tk(0.042, r), _tk(0.040, r)),
            r, 0.71, v, 0.026, accent,
        )

    # --- glazing field (C) in the lower slope region ---
    _build_glazing_field(roof, r, mats)

    # --- a few glazing-clip screws seated on transom_low (always present) ---
    for sx, v in enumerate((-0.40, 0.0, 0.40)):
        _plane_screw(roof, f"roof_screw_{sx}", r, 2.02, v, 0.040, 0.009, 0.010, mats["bolt"])

    # --- timber putty glazing beads (host-conformal, embedded on the bars) ---
    if r.emit_putty:
        _plane_box(roof, "putty_transom_low", (0.012, 2 * HALF_W - 0.08, 0.008), r, 2.02, 0.0, 0.048, mats["putty"])
        _plane_box(roof, "putty_eave", (0.012, 2 * HALF_W - 0.08, 0.008), r, EAVE_U - 0.03, 0.0, 0.048, mats["putty"])

    return roof


def _build_glazing_field(roof, r, mats):
    """Fixed glazing in the lower slope field (below the vent band)."""
    glass = mats["glass"]
    frame = mats["frame"]
    accent = mats["frame_accent"]

    _plane_box(
        roof, "transom_low", (_tk(0.050, r), 2 * HALF_W, _tk(0.044, r)),
        r, 2.02, 0.0, 0.024, frame,
    )
    if r.glazing == "multi_pane_grid":
        _plane_box(
            roof, "transom_mid", (_tk(0.050, r), 2 * HALF_W, _tk(0.044, r)),
            r, TRANSOM_MID_U, 0.0, 0.024, accent,
        )
        # kept clear of the sliding panel's travel zone (starts at u ~1.58)
        for i, v in enumerate((-0.24, 0.24)):
            _plane_box(
                roof, f"mullion_lower_{i}", (0.98, _tk(0.042, r), _tk(0.040, r)),
                r, 2.07, v, 0.026, frame,
            )
        for ci, v in enumerate((-0.46, 0.0, 0.46)):
            for ri, u in enumerate((1.72, 2.31)):
                _plane_box(
                    roof, f"glass_lower_{ci}_{ri}", (0.55, 0.44, 0.006),
                    r, u, v, 0.045, glass,
                )
    else:  # single_pane: two large rafter-to-rafter sheets
        # The upper sheet must start below the sliding panel's travel zone.
        top_u = 1.56 if r.vent_mechanism == "sliding_panel" else VENT_U1
        upper_u = (top_u + 2.00) / 2.0
        upper_len = 2.00 - top_u
        lower_u = (2.04 + EAVE_U - 0.02) / 2.0
        lower_len = (EAVE_U - 0.02) - 2.04
        sheet_w = 2.0 * 0.58
        _plane_box(roof, "glass_sheet_0", (upper_len, sheet_w, 0.010), r, upper_u, 0.0, 0.041, glass)
        _plane_box(roof, "glass_sheet_1", (lower_len, sheet_w, 0.010), r, lower_u, 0.0, 0.041, glass)

    if r.emit_side_glass:
        side_v = r.side_mullion_v + 0.01
        for i, v in enumerate((-side_v, side_v)):
            _plane_box(roof, f"glass_side_{i}", (1.18, 0.18, 0.006), r, 0.71, v, 0.045, glass)


# ---------------------------------------------------------------------------
# Mechanism B1: top_hinged_prop (N sashes; each _build_vent_sash).
# ---------------------------------------------------------------------------
def _bay_v_center(bay_idx: int, n: int, bay_half: float) -> float:
    return (2 * bay_idx - (n - 1)) * bay_half


def _build_vent_sash(model, roof, r, mats, *, bay_idx, n, bay_half, v_center):
    """One top-hinged vent bay: sash + latch + folding stay + 3 REVOLUTE joints.

    Local frame: +X down-slope from the ridge hinge, +Z out of the roof plane.
    """
    frame = mats["frame"]
    accent = mats["frame_accent"]
    galv = mats["hardware"]
    glass = mats["glass"]
    rubber = mats["rubber"]
    black = mats["black_steel"]
    bolt = mats["bolt"]

    sash_len = VENT_U1 - VENT_U0
    midx = sash_len / 2.0
    # Inset the sash inside its bay so adjacent bays leave a real gap for the
    # divider mullion and never collide edge-to-edge (matters for N=3 timber).
    sh = bay_half - 0.010
    hinge_dv = min(0.08, sh - 0.05)
    prefix = f"vent_sash_{bay_idx}"
    vent = model.part(prefix)

    _add_box(vent, "vent_glass", (sash_len - 0.10, 2 * sh - 0.08, 0.007), (midx, 0.0, -0.002), glass)
    _add_box(vent, "sash_top_rail", (0.060, 2 * sh, _tk(0.038, r)), (0.030, 0.0, 0.0), frame)
    _add_box(vent, "sash_bottom_rail", (0.080, 2 * sh, _tk(0.038, r)), (sash_len - 0.030, 0.0, 0.0), frame)
    _add_box(vent, "sash_stile_0", (sash_len, _tk(0.052, r), _tk(0.038, r)), (midx, -sh + 0.026, 0.0), frame)
    _add_box(vent, "sash_stile_1", (sash_len, _tk(0.052, r), _tk(0.038, r)), (midx, sh - 0.026, 0.0), accent)
    _add_box(vent, "sash_glazing_bar", (_tk(0.038, r), 2 * sh - 0.08, 0.028), (midx, 0.0, 0.010), frame)
    _add_box(vent, "sash_drip_lip", (0.030, 2 * sh - 0.06, 0.022), (sash_len - 0.060, 0.0, -0.024), frame)

    _add_box(vent, "sash_gasket_0", (sash_len - 0.10, 0.016, 0.012), (midx, -sh + 0.012, -0.018), rubber)
    _add_box(vent, "sash_gasket_1", (sash_len - 0.10, 0.016, 0.012), (midx, sh - 0.012, -0.018), rubber)
    _add_box(vent, "sash_gasket_bottom", (0.018, 2 * sh - 0.06, 0.012), (sash_len - 0.020, 0.0, -0.010), rubber)

    if r.emit_putty:
        _add_box(vent, "sash_putty_top", (0.012, 2 * sh - 0.10, 0.008), (0.072, 0.0, 0.014), mats["putty"])
        _add_box(vent, "sash_putty_bottom", (0.012, 2 * sh - 0.10, 0.008), (sash_len - 0.088, 0.0, 0.014), mats["putty"])

    for j, dv in enumerate((-hinge_dv, hinge_dv)):
        _add_box(vent, f"sash_hinge_leaf_{j}", (0.060, 0.100, 0.006), (0.020, dv, 0.012), galv)
        _add_cyl_y(vent, f"sash_hinge_knuckle_{j}", 0.011, 0.100, (0.004, dv, 0.006), galv)

    # Stay lug near the low-Y bay edge (clears the centred latch in narrow bays).
    stay_v = -sh + 0.05
    _add_box(vent, "stay_mount_tab", (0.060, 0.080, 0.110), (sash_len - 0.01, stay_v, -0.045), galv)
    cp = max(0.03, sh - 0.06)
    for j, (x, dv) in enumerate(
        ((0.10, -cp), (0.10, cp), (sash_len - 0.06, -cp), (sash_len - 0.06, cp))
    ):
        _add_box(vent, f"sash_corner_plate_{j}", (0.075, 0.045, 0.006), (x, dv, 0.016), galv)

    # --- latch ---
    latch = model.part(f"latch_{bay_idx}")
    _add_cyl_y(latch, "latch_pivot_pin", 0.015, 0.075, (0.0, 0.0, 0.0), bolt)
    _add_box(latch, "latch_back_plate", (0.065, 0.085, 0.010), (0.0, 0.0, -0.006), galv)
    _add_box(latch, "latch_hook_tongue", (0.115, 0.024, 0.012), (0.090, 0.0, -0.078), black)
    _add_box(latch, "latch_hook_drop", (0.018, 0.024, 0.072), (0.034, 0.0, -0.044), black)
    _add_box(latch, "pull_handle_stem", (0.020, 0.028, 0.140), (-0.012, 0.0, -0.080), black)
    _add_box(latch, "rubber_grip", (0.038, 0.110, 0.024), (-0.012, 0.0, -0.150), rubber)

    # --- folding stay ---
    stay = model.part(f"stay_arm_{bay_idx}")
    _add_cyl_y(stay, "stay_top_pin", 0.010, 0.040, (0.0, 0.0, 0.0), bolt)
    _add_box(stay, "stay_pivot_plate", (0.050, 0.050, 0.010), (0.0, 0.0, -0.006), galv)
    _add_box(stay, "stay_upper_arm", (0.020, 0.020, 0.240), (0.0, 0.0, -0.125), black)
    _add_cyl_y(stay, "stay_knuckle", 0.014, 0.026, (0.0, 0.0, -0.245), bolt)
    _add_box(stay, "stay_elbow_jog", (0.140, 0.020, 0.020), (0.060, 0.0, -0.245), black)
    _add_box(stay, "stay_lower_arm", (0.020, 0.020, 0.200), (0.120, 0.0, -0.345), black)
    _add_box(stay, "stay_end_shoe", (0.052, 0.030, 0.018), (0.120, 0.0, -0.445), galv)

    # --- joints ---
    hinge_origin = _plane_xyz(r, 0.0, v_center, 0.064)
    hinge = model.articulation(
        f"roof_to_vent_sash_{bay_idx}",
        ArticulationType.REVOLUTE,
        parent=roof,
        child=vent,
        origin=Origin(xyz=hinge_origin, rpy=(0.0, r.pitch, 0.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.4, lower=0.0, upper=r.sash_open),
    )
    hinge.meta["role"] = f"bay {bay_idx} top-hinged roof vent opening"
    model.articulation(
        f"sash_{bay_idx}_to_latch_{bay_idx}",
        ArticulationType.REVOLUTE,
        parent=vent,
        child=latch,
        origin=Origin(xyz=(sash_len - 0.06, 0.0, -0.030)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=-r.latch_open, upper=r.latch_open),
    )
    model.articulation(
        f"sash_{bay_idx}_to_stay_arm_{bay_idx}",
        ArticulationType.REVOLUTE,
        parent=vent,
        child=stay,
        origin=Origin(xyz=(sash_len - 0.01, stay_v, -0.090)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=14.0, velocity=1.0, lower=-0.05, upper=r.stay_open),
    )
    return vent


def _build_top_hinged(model, roof, r, mats):
    frame = mats["frame"]
    galv = mats["hardware"]
    rubber = mats["rubber"]
    bolt = mats["bolt"]
    n = r.sash_count
    bay_half = VENT_HALF / n

    # roof-side fixed opening framing
    _plane_box(
        roof, "vent_curb_sill", (0.065, 2 * VENT_HALF + 0.12, _tk(0.048, r)),
        r, VENT_U1, 0.0, 0.024, frame,
    )
    if n > 1:
        for k in range(n - 1):
            v_div = _bay_v_center(k, n, bay_half) + bay_half
            _plane_box(
                roof, f"vent_center_mullion_{k}", (VENT_U1 - VENT_U0, _tk(0.045, r), _tk(0.046, r)),
                r, (VENT_U0 + VENT_U1) / 2.0, v_div, 0.024, frame,
            )
    for i in range(n):
        v_center = _bay_v_center(i, n, bay_half)
        # outer curb jamb
        jv = (v_center - bay_half - 0.02) if i == 0 else (v_center + bay_half + 0.02) if i == n - 1 else None
        if jv is not None:
            _plane_box(
                roof, f"vent_curb_jamb_{i}", (VENT_U1 - VENT_U0, _tk(0.045, r), _tk(0.046, r)),
                r, (VENT_U0 + VENT_U1) / 2.0, jv, 0.024, frame,
            )
        # fixed hinge leaves + knuckles per bay (near the sash hinge knuckles)
        fixed_dv = min(0.08, bay_half - 0.05)
        for j, dv in enumerate((-fixed_dv, fixed_dv)):
            hv = v_center + dv
            _plane_box(roof, f"fixed_hinge_leaf_{i}_{j}", (0.060, 0.100, 0.006), r, -0.05, hv, 0.046, galv)
            _plane_cyl_y(roof, f"fixed_hinge_knuckle_{i}_{j}", 0.012, 0.100, r, 0.020, hv, 0.064, galv)
        _plane_box(roof, f"ridge_weather_seal_{i}", (0.024, 2 * bay_half, 0.014), r, 0.020, v_center, 0.044, rubber)
        _plane_box(roof, f"sill_weather_seal_{i}", (0.024, 2 * bay_half, 0.014), r, VENT_U1 - 0.02, v_center, 0.046, rubber)

    # two hinge pins at the OUTER edges of the whole opening (not per interior bay)
    for k, pin_v in enumerate((-VENT_HALF - 0.02, VENT_HALF + 0.02)):
        _plane_cyl_y(roof, f"hinge_pin_{k}", 0.007, 0.040, r, 0.020, pin_v, 0.064, bolt)

    for i in range(n):
        _build_vent_sash(
            model, roof, r, mats,
            bay_idx=i, n=n, bay_half=bay_half, v_center=_bay_v_center(i, n, bay_half),
        )


# ---------------------------------------------------------------------------
# Mechanism B2: louvre_bank (N blades; each _build_louvre_blade).
# ---------------------------------------------------------------------------
def _build_louvre_blade(model, roof, r, mats, *, i, n):
    galv = mats["hardware"]
    frame = mats["frame"]
    rubber = mats["rubber"]
    bolt = mats["bolt"]

    span = VENT_U1 - VENT_U0
    pitch_u = span / n
    blade_len = pitch_u - 0.014  # leave a real gap clear of the next blade axle
    blade_w = 2.0 * VENT_HALF - 0.08
    blade_pivot_w = 0.058

    blade = model.part(f"louvre_blade_{i}")
    _add_box(blade, "panel", (blade_len, blade_w, 0.006), (blade_len / 2.0, 0.0, 0.0), frame)
    axle_len = 2.0 * (VENT_HALF + 0.02)
    _add_cyl_y(blade, "axle", 0.006, axle_len, (0.0, 0.0, 0.0), galv)
    for s, side in enumerate((-1, 1)):
        _add_box(blade, f"bracket_{s}", (0.035, 0.028, 0.018), (0.018, side * (blade_w / 2.0 - 0.014), 0.0), galv)
    # trailing-edge seal embedded into the panel top surface (no floating island)
    _add_box(blade, "edge_seal", (0.010, blade_w - 0.04, 0.005), (blade_len - 0.006, 0.0, 0.002), rubber)
    for s, side in enumerate((-1, 1)):
        blade.visual(
            Cylinder(radius=0.005, length=0.006),
            origin=Origin(xyz=(0.018, side * (blade_w / 2.0 - 0.014), 0.010)),
            material=bolt,
            name=f"bolt_{s}", material_class_id="metal.blackened_gunmetal",
        )

    u_pivot = VENT_U0 + (i + 0.5) * pitch_u
    pivot_xyz = _plane_xyz(r, u_pivot, 0.0, blade_pivot_w)
    joint = model.articulation(
        f"frame_to_louvre_blade_{i}",
        ArticulationType.REVOLUTE,
        parent=roof,
        child=blade,
        origin=Origin(xyz=pivot_xyz, rpy=(0.0, r.pitch, 0.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=1.0, lower=0.0, upper=r.louvre_open),
    )
    joint.meta["role"] = f"louvre blade {i} jalousie pivot"
    return blade


def _build_louvre(model, roof, r, mats):
    frame = mats["frame"]
    galv = mats["hardware"]
    rubber = mats["rubber"]
    n = r.louvre_count
    span = VENT_U1 - VENT_U0
    pitch_u = span / n
    blade_pivot_w = 0.058

    _plane_box(roof, "vent_curb_sill", (0.065, 2 * VENT_HALF + 0.12, _tk(0.048, r)), r, VENT_U1, 0.0, 0.024, frame)
    for i, v in enumerate((-VENT_HALF - 0.04, VENT_HALF + 0.04)):
        _plane_box(roof, f"vent_curb_jamb_{i}", (VENT_U1 - VENT_U0, _tk(0.045, r), _tk(0.046, r)), r, (VENT_U0 + VENT_U1) / 2.0, v, 0.024, frame)
    _plane_box(roof, "louvre_head_rail", (_tk(0.055, r), 2 * VENT_HALF + 0.10, _tk(0.040, r)), r, VENT_U0 + 0.025, 0.0, 0.042, frame)
    _plane_box(roof, "sill_weather_seal", (0.024, 2 * VENT_HALF, 0.014), r, VENT_U1 - 0.02, 0.0, 0.046, rubber)

    for i in range(n):
        u_pivot = VENT_U0 + (i + 0.5) * pitch_u
        for s, v in enumerate((-VENT_HALF - 0.02, VENT_HALF + 0.02)):
            _plane_box(roof, f"blade_bearing_{i}_{s}", (0.032, 0.040, 0.030), r, u_pivot, v, blade_pivot_w, galv)
        _plane_box(roof, f"linkage_tab_{i}", (0.020, 0.024, 0.020), r, u_pivot, -VENT_HALF - 0.04, blade_pivot_w, galv)
    _plane_box(roof, "louvre_linkage_bar", (span + 0.06, 0.018, 0.014), r, (VENT_U0 + VENT_U1) / 2.0, -VENT_HALF - 0.06, blade_pivot_w - 0.014, galv)

    for i in range(n):
        _build_louvre_blade(model, roof, r, mats, i=i, n=n)


# ---------------------------------------------------------------------------
# Mechanism B3: sliding_panel (1 panel, PRISMATIC down-slope + latch).
# ---------------------------------------------------------------------------
def _build_sliding(model, roof, r, mats):
    frame = mats["frame"]
    accent = mats["frame_accent"]
    galv = mats["hardware"]
    glass = mats["glass"]
    rubber = mats["rubber"]
    black = mats["black_steel"]
    bolt = mats["bolt"]

    travel = r.slide_travel
    panel_w = 0.060
    rail_u0 = VENT_U0 - 0.02
    rail_u1 = VENT_U1 + travel + 0.02
    rail_len = rail_u1 - rail_u0
    rail_mid = (rail_u0 + rail_u1) / 2.0

    _plane_box(roof, "vent_curb_sill", (0.065, 2 * VENT_HALF + 0.12, _tk(0.048, r)), r, VENT_U1 + travel, 0.0, 0.024, frame)
    for i, v in enumerate((-VENT_HALF - 0.04, VENT_HALF + 0.04)):
        _plane_box(roof, f"vent_curb_jamb_{i}", (rail_len, _tk(0.045, r), _tk(0.046, r)), r, rail_mid, v, 0.024, frame)
    _plane_box(roof, "vent_header", (_tk(0.055, r), 2 * VENT_HALF + 0.10, _tk(0.046, r)), r, VENT_U0, 0.0, 0.024, frame)
    _plane_box(roof, "header_weather_seal", (0.022, 2 * VENT_HALF, 0.014), r, VENT_U0 + 0.02, 0.0, 0.048, rubber)
    _plane_box(roof, "sill_weather_seal", (0.024, 2 * VENT_HALF, 0.014), r, VENT_U1 + travel - 0.02, 0.0, 0.046, rubber)

    for i, v in enumerate((-VENT_HALF - 0.025, VENT_HALF + 0.025)):
        _plane_box(roof, f"vent_rail_{i}", (rail_len, 0.042, 0.015), r, rail_mid, v, 0.048, frame)
        lip_offset = 0.017 * (1 if i == 0 else -1)
        _plane_box(roof, f"vent_rail_lip_{i}", (rail_len, 0.008, 0.024), r, rail_mid, v + lip_offset, 0.058, frame)
        _plane_box(roof, f"vent_rail_stop_top_{i}", (0.022, 0.044, 0.032), r, rail_u0 + 0.012, v, 0.058, galv)
        _plane_box(roof, f"vent_rail_stop_bot_{i}", (0.022, 0.044, 0.032), r, rail_u1 - 0.012, v, 0.058, galv)

    # --- sliding vent panel (q=0 frame = the header seating plane) ---
    panel = model.part("sliding_vent_panel")
    sash_len = VENT_U1 - VENT_U0
    sash_half = VENT_HALF
    midx = sash_len / 2.0
    frame_z = 0.014
    _add_box(panel, "vent_glass", (sash_len - 0.10, 2 * sash_half - 0.08, 0.007), (midx, 0.0, 0.004), glass)
    _add_box(panel, "sash_top_rail", (0.060, 2 * sash_half, _tk(0.038, r)), (0.030, 0.0, frame_z), frame)
    _add_box(panel, "sash_bottom_rail", (0.080, 2 * sash_half, _tk(0.038, r)), (sash_len - 0.030, 0.0, frame_z), frame)
    _add_box(panel, "sash_stile_0", (sash_len, _tk(0.052, r), _tk(0.038, r)), (midx, -sash_half + 0.026, frame_z), frame)
    _add_box(panel, "sash_stile_1", (sash_len, _tk(0.052, r), _tk(0.038, r)), (midx, sash_half - 0.026, frame_z), accent)
    _add_box(panel, "sash_glazing_bar", (_tk(0.038, r), 2 * sash_half - 0.08, 0.028), (midx, 0.0, 0.024), frame)
    _add_box(panel, "sash_drip_lip", (0.030, 2 * sash_half - 0.06, 0.022), (sash_len - 0.060, 0.0, -0.016), frame)
    _add_box(panel, "sash_gasket_0", (sash_len - 0.10, 0.016, 0.012), (midx, -sash_half + 0.012, -0.008), rubber)
    _add_box(panel, "sash_gasket_1", (sash_len - 0.10, 0.016, 0.012), (midx, sash_half - 0.012, -0.008), rubber)
    _add_box(panel, "sash_gasket_bottom", (0.018, 2 * sash_half - 0.06, 0.012), (sash_len - 0.020, 0.0, 0.000), rubber)
    _add_box(panel, "sash_gasket_top", (0.018, 2 * sash_half - 0.06, 0.012), (0.020, 0.0, 0.000), rubber)
    for side_idx, yv in enumerate((-sash_half - 0.003, sash_half + 0.003)):
        for end_idx, xu in enumerate((0.10, sash_len - 0.10)):
            _add_box(panel, f"slider_shoe_{side_idx}_{end_idx}", (0.060, 0.032, 0.020), (xu, yv, -0.005), galv)
    for i, (x, v) in enumerate(((0.10, -0.40), (0.10, 0.40), (sash_len - 0.06, -0.40), (sash_len - 0.06, 0.40))):
        _add_box(panel, f"sash_corner_plate_{i}", (0.075, 0.045, 0.006), (x, v, 0.030), galv)
    _add_box(panel, "slide_pull_handle", (0.120, 0.030, 0.024), (sash_len - 0.10, 0.0, 0.035), black)
    _add_box(panel, "slide_pull_grip", (0.100, 0.042, 0.016), (sash_len - 0.10, 0.0, 0.050), rubber)

    # --- compact latch on the panel bottom rail ---
    latch = model.part("latch_handle")
    _add_cyl_y(latch, "latch_pivot_pin", 0.012, 0.065, (0.0, 0.0, 0.0), bolt)
    _add_box(latch, "latch_back_plate", (0.055, 0.075, 0.010), (0.0, 0.0, 0.008), galv)
    _add_box(latch, "latch_hook_tongue", (0.075, 0.024, 0.012), (0.055, 0.0, -0.018), black)
    _add_box(latch, "latch_hook_drop", (0.018, 0.024, 0.030), (0.022, 0.0, -0.012), black)
    _add_box(latch, "pull_handle_stem", (0.020, 0.028, 0.055), (-0.012, 0.0, 0.036), black)
    _add_box(latch, "rubber_grip", (0.038, 0.100, 0.024), (-0.012, 0.0, 0.066), rubber)

    slide_origin = _plane_xyz(r, VENT_U0, 0.0, panel_w)
    slide = model.articulation(
        "roof_to_sliding_vent",
        ArticulationType.PRISMATIC,
        parent=roof,
        child=panel,
        origin=Origin(xyz=slide_origin, rpy=(0.0, r.pitch, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=0.15, lower=0.0, upper=travel),
    )
    slide.meta["role"] = "primary sliding vent panel on roof guide rails"
    model.articulation(
        "panel_to_latch",
        ArticulationType.REVOLUTE,
        parent=panel,
        child=latch,
        origin=Origin(xyz=(sash_len - 0.03, 0.25, 0.050)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=-r.latch_open, upper=r.latch_open),
    )


# ---------------------------------------------------------------------------
# Mechanism B4: ridge_flap (1 long ridge flap, REVOLUTE + stay + latch).
# ---------------------------------------------------------------------------
def _build_ridge_flap(model, roof, r, mats):
    frame = mats["frame"]
    accent = mats["frame_accent"]
    galv = mats["hardware"]
    glass = mats["glass"]
    rubber = mats["rubber"]
    black = mats["black_steel"]
    bolt = mats["bolt"]

    flap_len = FLAP_U1 - FLAP_U0
    midx = flap_len / 2.0

    # roof-side framing
    _plane_box(roof, "flap_curb_sill", (0.065, 2 * FLAP_HALF + 0.12, _tk(0.048, r)), r, FLAP_U1, 0.0, 0.024, frame)
    for i, v in enumerate((-FLAP_HALF - 0.04, FLAP_HALF + 0.04)):
        _plane_box(roof, f"flap_curb_jamb_{i}", (FLAP_U1 - FLAP_U0, _tk(0.045, r), _tk(0.046, r)), r, (FLAP_U0 + FLAP_U1) / 2.0, v, 0.024, frame)
    _plane_box(roof, "ridge_weather_seal", (0.024, 2 * FLAP_HALF, 0.014), r, 0.020, 0.0, 0.044, rubber)
    _plane_box(roof, "sill_weather_seal", (0.024, 2 * FLAP_HALF, 0.014), r, FLAP_U1 - 0.02, 0.0, 0.046, rubber)
    for i, v in enumerate((-0.42, -0.14, 0.14, 0.42)):
        _plane_box(roof, f"fixed_hinge_leaf_{i}", (0.060, 0.130, 0.006), r, -0.05, v, 0.046, galv)
        _plane_cyl_y(roof, f"fixed_hinge_knuckle_{i}", 0.012, 0.130, r, 0.020, v, 0.064, galv)
    _plane_cyl_y(roof, "hinge_pin_left", 0.007, 0.040, r, 0.020, -0.56, 0.064, bolt)
    _plane_cyl_y(roof, "hinge_pin_right", 0.007, 0.040, r, 0.020, 0.56, 0.064, bolt)

    # --- ridge vent flap ---
    flap = model.part("ridge_vent_flap")
    _add_box(flap, "flap_glass", (flap_len - 0.10, 2 * FLAP_HALF - 0.08, 0.007), (midx, 0.0, -0.002), glass)
    _add_box(flap, "flap_top_rail", (0.060, 2 * FLAP_HALF, _tk(0.038, r)), (0.030, 0.0, 0.0), frame)
    _add_box(flap, "flap_bottom_rail", (0.080, 2 * FLAP_HALF, _tk(0.038, r)), (flap_len - 0.030, 0.0, 0.0), frame)
    _add_box(flap, "flap_stile_0", (flap_len, _tk(0.052, r), _tk(0.038, r)), (midx, -FLAP_HALF + 0.026, 0.0), frame)
    _add_box(flap, "flap_stile_1", (flap_len, _tk(0.052, r), _tk(0.038, r)), (midx, FLAP_HALF - 0.026, 0.0), accent)
    _add_box(flap, "flap_glazing_bar", (_tk(0.038, r), 2 * FLAP_HALF - 0.08, 0.028), (midx, 0.0, 0.010), frame)
    _add_box(flap, "flap_drip_lip", (0.030, 2 * FLAP_HALF - 0.06, 0.022), (flap_len - 0.060, 0.0, -0.024), frame)
    _add_box(flap, "flap_gasket_0", (flap_len - 0.10, 0.016, 0.012), (midx, -FLAP_HALF + 0.012, -0.018), rubber)
    _add_box(flap, "flap_gasket_1", (flap_len - 0.10, 0.016, 0.012), (midx, FLAP_HALF - 0.012, -0.018), rubber)
    _add_box(flap, "flap_gasket_bottom", (0.018, 2 * FLAP_HALF - 0.06, 0.012), (flap_len - 0.020, 0.0, -0.010), rubber)
    for i, v in enumerate((-0.28, 0.0, 0.28)):
        _add_box(flap, f"flap_hinge_leaf_{i}", (0.060, 0.125, 0.006), (0.020, v, 0.012), galv)
        _add_cyl_y(flap, f"flap_hinge_knuckle_{i}", 0.011, 0.125, (0.004, v, 0.006), galv)
    _add_box(flap, "stay_mount_tab", (0.060, 0.080, 0.110), (flap_len - 0.01, -0.30, -0.045), galv)
    stile_y = FLAP_HALF - 0.026
    for i, (x, sy) in enumerate(((0.04, -stile_y), (0.04, stile_y), (flap_len - 0.04, -stile_y), (flap_len - 0.04, stile_y))):
        _add_box(flap, f"flap_corner_plate_{i}", (0.075, 0.052, 0.006), (x, sy, 0.020), galv)

    # --- latch + folding stay ---
    latch = model.part("latch_handle")
    _add_cyl_y(latch, "latch_pivot_pin", 0.015, 0.075, (0.0, 0.0, 0.0), bolt)
    _add_box(latch, "latch_back_plate", (0.065, 0.085, 0.010), (0.0, 0.0, -0.006), galv)
    _add_box(latch, "latch_hook_tongue", (0.115, 0.024, 0.012), (0.090, 0.0, -0.078), black)
    _add_box(latch, "latch_hook_drop", (0.018, 0.024, 0.072), (0.034, 0.0, -0.044), black)
    _add_box(latch, "pull_handle_stem", (0.020, 0.028, 0.140), (-0.012, 0.0, -0.080), black)
    _add_box(latch, "rubber_grip", (0.038, 0.110, 0.024), (-0.012, 0.0, -0.150), rubber)

    stay = model.part("stay_arm")
    _add_cyl_y(stay, "stay_top_pin", 0.010, 0.040, (0.0, 0.0, 0.0), bolt)
    _add_box(stay, "stay_pivot_plate", (0.050, 0.050, 0.010), (0.0, 0.0, -0.006), galv)
    _add_box(stay, "stay_upper_arm", (0.020, 0.020, 0.240), (0.0, 0.0, -0.125), black)
    _add_cyl_y(stay, "stay_knuckle", 0.014, 0.026, (0.0, 0.0, -0.245), bolt)
    _add_box(stay, "stay_elbow_jog", (0.140, 0.020, 0.020), (0.060, 0.0, -0.245), black)
    _add_box(stay, "stay_lower_arm", (0.020, 0.020, 0.200), (0.120, 0.0, -0.345), black)
    _add_box(stay, "stay_end_shoe", (0.052, 0.030, 0.018), (0.120, 0.0, -0.445), galv)

    hinge_origin = _plane_xyz(r, 0.0, 0.0, 0.064)
    flap_joint = model.articulation(
        "roof_to_ridge_flap",
        ArticulationType.REVOLUTE,
        parent=roof,
        child=flap,
        origin=Origin(xyz=hinge_origin, rpy=(0.0, r.pitch, 0.0)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.4, lower=0.0, upper=r.flap_open),
    )
    flap_joint.meta["role"] = "primary ridge vent flap opening along ridge_rail"
    model.articulation(
        "ridge_flap_to_latch",
        ArticulationType.REVOLUTE,
        parent=flap,
        child=latch,
        origin=Origin(xyz=(flap_len - 0.06, 0.0, -0.030)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=-r.latch_open, upper=r.latch_open),
    )
    model.articulation(
        "ridge_flap_to_stay_arm",
        ArticulationType.REVOLUTE,
        parent=flap,
        child=stay,
        origin=Origin(xyz=(flap_len - 0.01, -0.30, -0.090)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=14.0, velocity=1.0, lower=-0.05, upper=r.stay_open),
    )


_MECHANISM_BUILDERS = {
    "top_hinged_prop": _build_top_hinged,
    "louvre_bank": _build_louvre,
    "sliding_panel": _build_sliding,
    "ridge_flap": _build_ridge_flap,
}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_greenhouse_vent_roof(
    config: GreenhouseVentRoofConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "class": "Agricultural/Greenhouse vent roof",
            "description": (
                "A glazed greenhouse roof section: a pitched frame carrying a "
                "glazing field with a mid-slope operable ventilation opening."
            ),
        },
    )
    mats = {
        role: model.material(f"ghvent_{role}_{r.palette_style}", rgba=rgba)
        for role, rgba in _palette_rgba(r.palette_style).items()
    }

    roof = _build_roof(model, r, mats)
    _MECHANISM_BUILDERS[r.vent_mechanism](model, roof, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_greenhouse_vent_roof(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_greenhouse_vent_roof(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _allow_top_hinged(ctx, model, r):
    n = r.sash_count
    sash_members = ("sash_top_rail", "sash_bottom_rail", "sash_stile_0", "sash_stile_1",
                    "sash_gasket_0", "sash_gasket_1", "sash_gasket_bottom", "sash_drip_lip")
    hinge_line = ("sash_top_rail", "sash_stile_0", "sash_stile_1",
                  "sash_hinge_leaf_0", "sash_hinge_leaf_1",
                  "sash_hinge_knuckle_0", "sash_hinge_knuckle_1")
    for i in range(n):
        vname = f"vent_sash_{i}"
        lname = f"latch_{i}"
        sname = f"stay_arm_{i}"
        # closed sash beds onto / hinges against the fixed ridge rail
        for member in hinge_line:
            ctx.allow_overlap(vname, "roof_frame", elem_a=member, elem_b="ridge_rail",
                              reason="Closed sash frame + hinge hardware beds onto the ridge rail at the hinge line.")
        # inner edges + stay lug seat against the flanking mullions / curb jambs
        seat_edges = sash_members + ("stay_mount_tab", "sash_glazing_bar")
        for m in (i - 1, i):
            if 0 <= m <= n - 2:
                for elem in seat_edges:
                    ctx.allow_overlap(vname, "roof_frame", elem_a=elem, elem_b=f"vent_center_mullion_{m}",
                                      reason=f"Bay {i} inner edge / stay lug seats against the divider mullion.")
        if f"vent_curb_jamb_{i}" in {v.name for v in model.get_part('roof_frame').visuals}:
            for elem in seat_edges:
                ctx.allow_overlap(vname, "roof_frame", elem_a=elem, elem_b=f"vent_curb_jamb_{i}",
                                  reason=f"Bay {i} outer edge / stay lug seats against the curb jamb.")
        # stay + latch hardware clustered on the bottom rail (captured pins)
        for elem in ("stay_pivot_plate", "stay_top_pin", "stay_upper_arm"):
            for member in ("stay_mount_tab", "sash_bottom_rail", "sash_stile_0", "sash_drip_lip"):
                ctx.allow_overlap(sname, vname, elem_a=elem, elem_b=member,
                                  reason="Folding stay is captured on the sash mount lug / bottom rail at the revolute pin.")
        for latch_elem in ("latch_pivot_pin", "latch_back_plate", "latch_hook_drop", "latch_hook_tongue", "pull_handle_stem"):
            for member in ("sash_bottom_rail", "sash_drip_lip", "stay_mount_tab", "sash_glazing_bar"):
                ctx.allow_overlap(lname, vname, elem_a=latch_elem, elem_b=member,
                                  reason="Latch hardware is captured on / swings against the crowded sash bottom rail.")
        # latch hook engages the curb sill keeper below the sash
        for latch_elem in ("latch_hook_tongue", "latch_hook_drop"):
            ctx.allow_overlap(lname, "roof_frame", elem_a=latch_elem, elem_b="vent_curb_sill",
                              reason="Latch hook engages the fixed curb sill keeper when swung.")
        # folding stay foot bears against the curb sill when propped open
        for elem in ("stay_end_shoe", "stay_lower_arm"):
            ctx.allow_overlap(sname, "roof_frame", elem_a=elem, elem_b="vent_curb_sill",
                              reason="Folding stay foot bears against the curb sill when the sash is propped open.")
        # ridge hinge pins + fixed knuckles interleave with the sash frame
        for k in range(2):
            for member in hinge_line:
                ctx.allow_overlap("roof_frame", vname, elem_a=f"hinge_pin_{k}", elem_b=member,
                                  reason="Ridge hinge pin end runs through the sash frame at the hinge line.")
        for jk in range(2):
            for member in hinge_line:
                ctx.allow_overlap("roof_frame", vname, elem_a=f"fixed_hinge_knuckle_{i}_{jk}", elem_b=member,
                                  reason="Fixed ridge hinge knuckle interleaves with the sash frame at the hinge line.")
                ctx.allow_overlap("roof_frame", vname, elem_a=f"fixed_hinge_leaf_{i}_{jk}", elem_b=member,
                                  reason="Fixed ridge hinge leaf interleaves with the sash frame at the hinge line.")
        # EPDM seals bedded by the closed sash
        for seal in (f"ridge_weather_seal_{i}", f"sill_weather_seal_{i}"):
            for member in sash_members:
                ctx.allow_overlap("roof_frame", vname, elem_a=seal, elem_b=member,
                                  reason="Closed sash frame beds and compresses the fixed EPDM weather seal.")
    # adjacent bays share the divider line: allow their inner stiles / gaskets to meet
    for i in range(n - 1):
        a, b = f"vent_sash_{i}", f"vent_sash_{i + 1}"
        for ea in ("sash_stile_1", "sash_gasket_1", "sash_top_rail", "sash_bottom_rail"):
            for eb in ("sash_stile_0", "sash_gasket_0", "sash_top_rail", "sash_bottom_rail"):
                ctx.allow_overlap(a, b, elem_a=ea, elem_b=eb,
                                  reason="Adjacent vent bays meet at the shared divider mullion line.")


def _allow_louvre(ctx, model, r):
    n = r.louvre_count
    for i in range(n):
        for s in (0, 1):
            ctx.allow_overlap(f"louvre_blade_{i}", "roof_frame", elem_a="axle", elem_b=f"blade_bearing_{i}_{s}",
                              reason="Blade pivot axle is captured in the jamb bearing block it rotates in.")
        ctx.allow_overlap(f"louvre_blade_{i}", "roof_frame", elem_a="axle", elem_b=f"linkage_tab_{i}",
                          reason="Linkage tab visually couples to the blade axle end for simultaneous operation.")
        ctx.allow_overlap(f"louvre_blade_{i}", "roof_frame", elem_a="axle", elem_b="louvre_head_rail",
                          reason="Top blade axle runs just under the louvre head rail at the opening head.")
    # adjacent jalousie blades imbricate along the pivot line
    for i in range(n - 1):
        for ea, eb in (("panel", "axle"), ("panel", "panel"), ("edge_seal", "axle"), ("edge_seal", "panel")):
            ctx.allow_overlap(f"louvre_blade_{i}", f"louvre_blade_{i + 1}", elem_a=ea, elem_b=eb,
                              reason="Adjacent jalousie blades imbricate along the shared pivot line.")


def _allow_sliding(ctx, model, r):
    for side_idx in range(2):
        for end_idx in range(2):
            shoe = f"slider_shoe_{side_idx}_{end_idx}"
            for target in (f"vent_rail_{side_idx}", f"vent_rail_lip_{side_idx}",
                           f"vent_rail_stop_top_{side_idx}", f"vent_rail_stop_bot_{side_idx}",
                           "vent_curb_jamb_0", "vent_curb_jamb_1"):
                ctx.allow_overlap("sliding_vent_panel", "roof_frame", elem_a=shoe, elem_b=target,
                                  reason="Slider shoe rides inside the vent rail C-channel track alongside the curb jamb.")
    for stile in ("sash_stile_0", "sash_stile_1"):
        ctx.allow_overlap("sliding_vent_panel", "roof_frame", elem_a=stile, elem_b="vent_header",
                          reason="Closed panel leading edge seats against the vent header bar.")
    ctx.allow_overlap("sliding_vent_panel", "roof_frame", elem_a="sash_bottom_rail", elem_b="vent_curb_sill",
                      reason="Closed panel trailing edge seats onto the curb sill.")
    for seal, members in (
        ("header_weather_seal", ("sash_top_rail", "sash_gasket_top", "sash_stile_0", "sash_stile_1")),
        ("sill_weather_seal", ("sash_bottom_rail", "sash_gasket_bottom", "sash_stile_0", "sash_stile_1")),
    ):
        for member in members:
            ctx.allow_overlap("roof_frame", "sliding_vent_panel", elem_a=seal, elem_b=member,
                              reason="Closed panel frame beds and compresses the fixed EPDM weather seal.")
    for latch_elem in ("latch_pivot_pin", "latch_back_plate", "latch_hook_drop", "latch_hook_tongue", "pull_handle_stem"):
        for member in ("sash_bottom_rail", "sash_drip_lip", "sash_stile_1", "slide_pull_handle"):
            ctx.allow_overlap("latch_handle", "sliding_vent_panel", elem_a=latch_elem, elem_b=member,
                              reason="Latch hardware is captured on / swings against the panel bottom rail it mounts to.")
    for latch_elem in ("latch_hook_tongue", "latch_hook_drop"):
        ctx.allow_overlap("latch_handle", "roof_frame", elem_a=latch_elem, elem_b="vent_curb_sill",
                          reason="Latch hook engages the fixed curb sill keeper when swung.")
    ctx.allow_overlap("sliding_vent_panel", "sliding_vent_panel", elem_a="slide_pull_handle", elem_b="sash_bottom_rail",
                      reason="Pull handle is surface-mounted on top of the panel bottom rail.")


def _allow_ridge_flap(ctx, model, r):
    for member in ("flap_stile_0", "flap_stile_1", "flap_top_rail",
                   "flap_hinge_leaf_0", "flap_hinge_leaf_1", "flap_hinge_leaf_2",
                   "flap_hinge_knuckle_0", "flap_hinge_knuckle_1", "flap_hinge_knuckle_2"):
        ctx.allow_overlap("ridge_vent_flap", "roof_frame", elem_a=member, elem_b="ridge_rail",
                          reason="Closed ridge flap frame + hinge hardware beds onto the ridge rail at the hinge line.")
    for elem in ("stay_pivot_plate", "stay_top_pin", "stay_upper_arm"):
        ctx.allow_overlap("stay_arm", "ridge_vent_flap", elem_a=elem, elem_b="stay_mount_tab",
                          reason="Stay pivot is captured on the flap mount lug at the revolute pin.")
    for elem in ("stay_end_shoe", "stay_lower_arm"):
        ctx.allow_overlap("stay_arm", "roof_frame", elem_a=elem, elem_b="flap_curb_sill",
                          reason="Folding stay foot bears against the curb sill when the flap is propped open.")
    for latch_elem in ("latch_pivot_pin", "latch_back_plate", "latch_hook_drop", "latch_hook_tongue", "pull_handle_stem"):
        for member in ("flap_bottom_rail", "flap_drip_lip", "flap_glazing_bar"):
            ctx.allow_overlap("latch_handle", "ridge_vent_flap", elem_a=latch_elem, elem_b=member,
                              reason="Latch hardware is captured on / swings against the flap bottom rail / drip lip.")
    for latch_elem in ("latch_hook_tongue", "latch_hook_drop"):
        ctx.allow_overlap("latch_handle", "roof_frame", elem_a=latch_elem, elem_b="flap_curb_sill",
                          reason="Latch hook engages the fixed curb sill keeper when swung.")
    for side, stile, fknuckle in (
        ("hinge_pin_left", "flap_stile_0", "flap_hinge_knuckle_0"),
        ("hinge_pin_right", "flap_stile_1", "flap_hinge_knuckle_2"),
    ):
        for member in ("flap_top_rail", stile, fknuckle):
            ctx.allow_overlap("roof_frame", "ridge_vent_flap", elem_a=side, elem_b=member,
                              reason="Ridge hinge pin end runs through the flap frame at the hinge line.")
    for i in range(4):
        for member in ("flap_top_rail", "flap_hinge_leaf_0", "flap_hinge_leaf_1", "flap_hinge_leaf_2",
                       "flap_hinge_knuckle_0", "flap_hinge_knuckle_1", "flap_hinge_knuckle_2"):
            ctx.allow_overlap("roof_frame", "ridge_vent_flap", elem_a=f"fixed_hinge_knuckle_{i}", elem_b=member,
                              reason="Fixed ridge hinge knuckle interleaves with the flap frame at the hinge line.")
    for seal, members in (
        ("ridge_weather_seal", ("flap_top_rail", "flap_stile_0", "flap_stile_1", "flap_gasket_0", "flap_gasket_1")),
        ("sill_weather_seal", ("flap_bottom_rail", "flap_stile_0", "flap_stile_1", "flap_gasket_0",
                               "flap_gasket_1", "flap_gasket_bottom")),
    ):
        for member in members:
            ctx.allow_overlap("roof_frame", "ridge_vent_flap", elem_a=seal, elem_b=member,
                              reason="Closed flap frame beds and compresses the fixed EPDM weather seal.")


def run_greenhouse_vent_roof_tests(
    object_model: ArticulatedObject,
    config: GreenhouseVentRoofConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    roof = object_model.get_part("roof_frame")

    # ---- captured-pin/slide + seating allowances (element-scoped). ----
    if r.vent_mechanism == "top_hinged_prop":
        _allow_top_hinged(ctx, object_model, r)
    elif r.vent_mechanism == "louvre_bank":
        _allow_louvre(ctx, object_model, r)
    elif r.vent_mechanism == "sliding_panel":
        _allow_sliding(ctx, object_model, r)
    else:
        _allow_ridge_flap(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ---- identity ----
    ctx.check(
        "classified as greenhouse vent roof",
        object_model.meta.get("class") == "Agricultural/Greenhouse vent roof" and roof is not None,
        details=f"class={object_model.meta.get('class')}",
    )
    part_names = {p.name for p in object_model.parts}
    ctx.check(
        "single grounded roof_frame is the root",
        "roof_frame" in part_names,
        details=str(sorted(part_names)),
    )

    # ---- every seed has at least one real opening joint ----
    movable = [
        j
        for j in object_model.articulations
        if j.articulation_type in (ArticulationType.REVOLUTE, ArticulationType.PRISMATIC)
    ]
    ctx.check(
        "has at least one operable (non-fixed) vent joint",
        len(movable) >= 1,
        details=f"movable joints={[j.name for j in movable]}",
    )

    # ---- mechanism-specific structure + motion ----
    if r.vent_mechanism == "top_hinged_prop":
        n = r.sash_count
        vents = [object_model.get_part(f"vent_sash_{i}") for i in range(n)]
        hinges = [object_model.get_articulation(f"roof_to_vent_sash_{i}") for i in range(n)]
        ctx.check(
            f"top_hinged: {n} sash bays with hinges",
            all(v is not None for v in vents) and all(h is not None for h in hinges),
            details=f"n={n}",
        )
        h0 = hinges[0]
        ctx.check(
            "sash hinge is REVOLUTE about -Y (top-hinged, lifts up)",
            h0.articulation_type == ArticulationType.REVOLUTE and abs(h0.axis[1]) > 0.9,
            details=f"type={h0.articulation_type} axis={tuple(h0.axis)}",
        )
        closed = ctx.part_world_aabb(vents[0])
        with ctx.pose({h0: r.sash_open * 0.9}):
            opened = ctx.part_world_aabb(vents[0])
        if closed is not None and opened is not None:
            ctx.check(
                "top-hinged sash opens upward",
                opened[1][2] > closed[1][2] + 0.20,
                details=f"closed_top={closed[1][2]:.3f} open_top={opened[1][2]:.3f}",
            )
    elif r.vent_mechanism == "louvre_bank":
        n = r.louvre_count
        blades = [object_model.get_part(f"louvre_blade_{i}") for i in range(n)]
        joints = [object_model.get_articulation(f"frame_to_louvre_blade_{i}") for i in range(n)]
        ctx.check(
            f"louvre: {n} blades each with a REVOLUTE pivot",
            all(b is not None for b in blades) and all(j is not None for j in joints),
            details=f"n={n}",
        )
        j0 = joints[0]
        closed = ctx.part_world_aabb(blades[0])
        with ctx.pose({j0: r.louvre_open}):
            opened = ctx.part_world_aabb(blades[0])
        if closed is not None and opened is not None:
            ctx.check(
                "louvre blade tilts open (trailing edge lifts)",
                opened[1][2] > closed[1][2] + 0.008,
                details=f"closed_top={closed[1][2]:.4f} open_top={opened[1][2]:.4f}",
            )
    elif r.vent_mechanism == "sliding_panel":
        panel = object_model.get_part("sliding_vent_panel")
        slide = object_model.get_articulation("roof_to_sliding_vent")
        ctx.check(
            "sliding: panel + PRISMATIC joint present",
            panel is not None and slide is not None
            and slide.articulation_type == ArticulationType.PRISMATIC
            and abs(slide.axis[0]) > 0.9,
            details=f"type={getattr(slide, 'articulation_type', None)}",
        )
        p0 = ctx.part_world_position(panel)
        with ctx.pose({slide: r.slide_travel}):
            p1 = ctx.part_world_position(panel)
        if p0 is not None and p1 is not None:
            ctx.check(
                "sliding panel translates down-slope (+x)",
                p1[0] > p0[0] + 0.08,
                details=f"closed_x={p0[0]:.3f} open_x={p1[0]:.3f}",
            )
    else:  # ridge_flap
        flap = object_model.get_part("ridge_vent_flap")
        fj = object_model.get_articulation("roof_to_ridge_flap")
        ctx.check(
            "ridge_flap: flap + REVOLUTE about -Y present",
            flap is not None and fj is not None
            and fj.articulation_type == ArticulationType.REVOLUTE and abs(fj.axis[1]) > 0.9,
            details=f"type={getattr(fj, 'articulation_type', None)}",
        )
        flap_aabb = ctx.part_world_aabb(flap)
        ctx.check(
            "ridge flap spans wide along the ridge (Y > 1.0 m)",
            flap_aabb is not None and (flap_aabb[1][1] - flap_aabb[0][1]) > 1.0,
            details=f"aabb={flap_aabb}",
        )
        closed = ctx.part_world_aabb(flap)
        with ctx.pose({fj: r.flap_open * 0.9}):
            opened = ctx.part_world_aabb(flap)
        if closed is not None and opened is not None:
            ctx.check(
                "ridge flap opens upward",
                opened[1][2] > closed[1][2] + 0.20,
                details=f"closed_top={closed[1][2]:.3f} open_top={opened[1][2]:.3f}",
            )

    # ---- curved_eave keeps the swept-mesh rafter (Rule 3). ----
    if r.roof_geometry == "curved_eave":
        arch_visuals = [v for v in roof.visuals if v.name.startswith("rake_arch_")]
        ctx.check(
            "curved_eave rafters are swept meshes (not box placeholders)",
            len(arch_visuals) >= 2,
            details=f"rake_arch visuals={[v.name for v in arch_visuals]}",
        )

    # ---- glazing field present. ----
    glass_names = [v.name for v in roof.visuals if v.name.startswith(("glass_lower", "glass_sheet"))]
    ctx.check(
        "fixed glazing field present on the roof",
        len(glass_names) >= 2,
        details=f"glass={glass_names[:6]}",
    )

    # ---- timber_bar emits host-conformal putty beads. ----
    if r.frame_member == "timber_bar":
        putty_names = [v.name for v in roof.visuals if v.name.startswith("putty_")]
        ctx.check(
            "timber_bar emits putty glazing beads (host-conformal)",
            len(putty_names) >= 1,
            details=f"putty={putty_names}",
        )

    # ---- Rule 5: sampled-pose collision across all opening joints. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices recorded with multiplicity encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "GreenhouseVentRoofConfig",
    "ResolvedGreenhouseVentRoofConfig",
    "build_greenhouse_vent_roof",
    "build_seeded_greenhouse_vent_roof",
    "config_from_seed",
    "resolve_config",
    "run_greenhouse_vent_roof_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
