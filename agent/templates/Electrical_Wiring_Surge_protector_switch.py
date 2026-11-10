# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template — surge_protector_switch (Electrical_Wiring / Surge protector switch).

Category identity: an extruded bar ``housing`` (ROOT) carrying a row of N NEMA
outlets + a row of independent red rocker switches (each its OWN REVOLUTE joint)
+ a captive swept-spline cord and plug. Optional green protection LED, push
reset/breaker button (PRISMATIC), USB block, wall-mount hardware.

Parallel-children + multiplicity (hand-rolled config dispatch, Container_Locker
/ circuit_breaker style — no SlotSpec assembler). All moving parts (K rockers,
optional reset button) parent directly to the single ``housing``.

Discrete slots:
- ③A ``housing_form``  : recessed_flat (S1, flush sockets/wells) / raised_bezel (S2, proud plates/bezels)
- ①B ``switch_scheme`` : per_outlet (N) / master_plus_individual (N+1) / single_master (1)
- ③C ``mount``         : flat_feet / wall_keyhole_guard
- ④D ``face_power``    : cord_plug / cord_plug_led / reset_breaker (+PRISMATIC) / usb_ports
- ①  ``outlet_count`` N ∈ [3,14] (weighted, anchors {4,6,8,12}); bar length + pitch derive from N
- ⑥  ``palette_style`` : 6 realistic surge-strip colorways

Rocker pivot axis is unified to +Y for EVERY rocker incl. master (S2 convention;
S1 used +X — one convention only). CadQuery housing / outlet plate / rocker /
bezel + swept-spline cord kept (TEMPLATE_DESIGN_RULES ③); S1's 64-box braid
greeble dropped. Each distinct sub-mesh is built ONCE and reused across N.

Sources: origins S1 `rec_electrical_wiring_gpt55_...sixrockers` (black recessed) +
S2 `rec_use-...d5decd1b` (yellow raised), forks four_outlet/twelve_outlet/
single_master_switch/reset_breaker_button/usb_ports.

Frame: X = bar length (cord exits +X), Y = width (outlet row +Y, switch row -Y),
Z = vertical (bottom z=0, top z=body_height). Body centered on x=0.

Canonical spec: articraft_template_authoring/specs_modular_v1/surge_protector_switch.md
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot vocabularies
# ---------------------------------------------------------------------------
HousingForm = Literal["recessed_flat", "raised_bezel"]
SwitchScheme = Literal["per_outlet", "master_plus_individual", "single_master"]
Mount = Literal["flat_feet", "wall_keyhole_guard"]
FacePower = Literal["cord_plug", "cord_plug_led", "reset_breaker", "usb_ports"]
PaletteStyle = Literal[
    "industrial_black",
    "safety_yellow",
    "office_white",
    "graphite_grey",
    "brushed_steel",
    "surge_blue",
]

HOUSING_FORMS: tuple[HousingForm, ...] = ("recessed_flat", "raised_bezel")
SWITCH_SCHEMES: tuple[SwitchScheme, ...] = (
    "per_outlet",
    "master_plus_individual",
    "single_master",
)
MOUNTS: tuple[Mount, ...] = ("flat_feet", "wall_keyhole_guard")
FACE_POWERS: tuple[FacePower, ...] = (
    "cord_plug",
    "cord_plug_led",
    "reset_breaker",
    "usb_ports",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "industrial_black",
    "safety_yellow",
    "office_white",
    "graphite_grey",
    "brushed_steel",
    "surge_blue",
)

# outlet_count weighted sampling (small N favored; spec Multiplicity table).
_OUTLET_COUNTS: tuple[int, ...] = (4, 6, 8, 10, 12, 14, 3, 5)
_OUTLET_WEIGHTS: tuple[float, ...] = (0.24, 0.22, 0.20, 0.12, 0.10, 0.05, 0.04, 0.03)

# ---------------------------------------------------------------------------
# Palettes: housing / rib / accent / endcap / label. Functional colors (red
# rocker lens, green LED, brass contacts, steel blades) stay CONSTANT across
# palettes. palette-only — never a slot choice.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "industrial_black": {
        "housing": (0.03, 0.03, 0.035, 1.0),
        "rib": (0.02, 0.02, 0.022, 1.0),
        "accent": (0.10, 0.10, 0.11, 1.0),
        "endcap": (0.02, 0.02, 0.022, 1.0),
        "label": (0.55, 0.55, 0.55, 1.0),
    },
    "safety_yellow": {
        "housing": (1.0, 0.77, 0.03, 1.0),
        "rib": (0.85, 0.66, 0.03, 1.0),
        "accent": (0.03, 0.03, 0.03, 1.0),
        "endcap": (0.02, 0.02, 0.022, 1.0),
        "label": (0.94, 0.94, 0.86, 1.0),
    },
    "office_white": {
        "housing": (0.90, 0.90, 0.88, 1.0),
        "rib": (0.80, 0.80, 0.78, 1.0),
        "accent": (0.30, 0.30, 0.32, 1.0),
        "endcap": (0.25, 0.25, 0.27, 1.0),
        "label": (0.20, 0.20, 0.22, 1.0),
    },
    "graphite_grey": {
        "housing": (0.28, 0.29, 0.31, 1.0),
        "rib": (0.20, 0.21, 0.22, 1.0),
        "accent": (0.12, 0.12, 0.13, 1.0),
        "endcap": (0.10, 0.10, 0.11, 1.0),
        "label": (0.75, 0.75, 0.77, 1.0),
    },
    "brushed_steel": {
        "housing": (0.66, 0.68, 0.70, 1.0),
        "rib": (0.55, 0.57, 0.59, 1.0),
        "accent": (0.40, 0.42, 0.44, 1.0),
        "endcap": (0.35, 0.36, 0.38, 1.0),
        "label": (0.20, 0.20, 0.22, 1.0),
    },
    "surge_blue": {
        "housing": (0.16, 0.32, 0.55, 1.0),
        "rib": (0.12, 0.25, 0.45, 1.0),
        "accent": (0.90, 0.90, 0.88, 1.0),
        "endcap": (0.06, 0.06, 0.08, 1.0),
        "label": (0.92, 0.92, 0.90, 1.0),
    },
}

_FUNCTIONAL_MATERIALS: dict[str, tuple[float, float, float, float]] = {
    "red_lens": (0.85, 0.05, 0.035, 0.92),
    "red_hi": (1.0, 0.22, 0.18, 0.90),
    "green_led": (0.05, 0.95, 0.28, 0.95),
    "brass": (0.88, 0.50, 0.16, 1.0),
    "steel": (0.72, 0.76, 0.76, 1.0),
    "rubber": (0.02, 0.02, 0.025, 1.0),
    "dark": (0.0, 0.0, 0.0, 1.0),
}

# ---------------------------------------------------------------------------
# Base geometry constants (meters), from the 5-star sources.
# ---------------------------------------------------------------------------
_OUTLET_HALF = 0.028  # half footprint of an outlet plate + margin (length axis)
_IND_HALF = 0.020  # half footprint of an individual switch bezel (length axis)
_MAS_HALF = 0.034  # half footprint of a master switch bezel (length axis)
_END_ZONE = 0.075  # free length beyond the outermost feature (face features + caps)
_FACE_INSET = 0.030  # face-feature x inside the +X end zone


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class SurgeProtectorSwitchConfig:
    housing_form: HousingForm = "raised_bezel"
    switch_scheme: SwitchScheme = "per_outlet"
    mount: Mount = "wall_keyhole_guard"
    face_power: FacePower = "cord_plug_led"
    outlet_count: int = 8
    palette_style: PaletteStyle = "safety_yellow"
    outlet_pitch: float = 0.080
    body_width: float = 0.086
    body_height: float = 0.031
    rocker_travel: float = 0.22
    reset_travel: float = 0.004
    name: str = "surge_protector_switch"


@dataclass(frozen=True)
class ResolvedSurgeProtectorSwitchConfig:
    housing_form: HousingForm
    switch_scheme: SwitchScheme
    mount: Mount
    face_power: FacePower
    outlet_count: int
    palette_style: PaletteStyle
    outlet_pitch: float
    body_width: float
    body_height: float
    rocker_travel: float
    reset_travel: float
    # derived
    body_length: float
    outlet_xs: tuple[float, ...]
    switch_specs: tuple[tuple[float, str], ...]
    outlet_y: float
    switch_y: float
    top_z: float
    face_zone_x: float
    name: str


def _compute_switch_specs(
    scheme: str, outlet_xs: tuple[float, ...], pitch: float
) -> tuple[tuple[float, str], ...]:
    """Single-sourced (x, kind) switch layout, read by BOTH housing_form (seat
    visuals) and switch_scheme (rocker parts). Contract 3c."""
    if scheme == "per_outlet":
        return tuple((x, "individual") for x in outlet_xs)
    if scheme == "master_plus_individual":
        master_x = outlet_xs[0] - pitch  # master at the -X end (opposite the +X cord)
        return ((master_x, "master"),) + tuple((x, "individual") for x in outlet_xs)
    # single_master
    return ((0.0, "master"),)


def config_from_seed(seed: int) -> SurgeProtectorSwitchConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    housing_form = rng.choice(HOUSING_FORMS)
    switch_scheme = rng.choice(SWITCH_SCHEMES)
    mount = rng.choice(MOUNTS)
    face_power = rng.choice(FACE_POWERS)
    outlet_count = rng.choices(_OUTLET_COUNTS, weights=_OUTLET_WEIGHTS, k=1)[0]
    palette = rng.choice(PALETTE_STYLES)
    return SurgeProtectorSwitchConfig(
        housing_form=housing_form,
        switch_scheme=switch_scheme,
        mount=mount,
        face_power=face_power,
        outlet_count=outlet_count,
        palette_style=palette,
        outlet_pitch=round(rng.uniform(0.070, 0.092), 4),
        body_width=round(rng.uniform(0.072, 0.120), 4),
        body_height=round(rng.uniform(0.028, 0.040), 4),
        rocker_travel=round(rng.uniform(0.18, 0.28), 4),
        reset_travel=round(rng.uniform(0.003, 0.006), 4),
        name=f"seeded_surge_protector_switch_{seed}",
    )


def resolve_config(
    config: SurgeProtectorSwitchConfig | None = None,
) -> ResolvedSurgeProtectorSwitchConfig:
    cfg = config or SurgeProtectorSwitchConfig()
    housing_form = _pick(cfg.housing_form, HOUSING_FORMS)
    switch_scheme = _pick(cfg.switch_scheme, SWITCH_SCHEMES)
    mount = _pick(cfg.mount, MOUNTS)
    face_power = _pick(cfg.face_power, FACE_POWERS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    n = int(_clamp(cfg.outlet_count, 3, 14))
    pitch = _clamp(cfg.outlet_pitch, 0.070, 0.092)
    width = _clamp(cfg.body_width, 0.072, 0.120)
    height = _clamp(cfg.body_height, 0.028, 0.040)
    travel = _clamp(cfg.rocker_travel, 0.18, 0.28)
    reset_travel = _clamp(cfg.reset_travel, 0.003, 0.006)

    outlet_xs = tuple((i - (n - 1) / 2.0) * pitch for i in range(n))
    switch_specs = _compute_switch_specs(switch_scheme, outlet_xs, pitch)

    # body_length is DERIVED (equation) to contain all outlets + switches + the
    # +X face-feature end zone. Symmetric about x=0.
    ext = max(abs(outlet_xs[0]) + _OUTLET_HALF, abs(outlet_xs[-1]) + _OUTLET_HALF)
    for x, kind in switch_specs:
        ext = max(ext, abs(x) + (_MAS_HALF if kind == "master" else _IND_HALF))
    body_length = 2.0 * (ext + _END_ZONE)

    outlet_y = 0.22 * width
    switch_y = -0.33 * width
    face_zone_x = ext + _FACE_INSET

    return ResolvedSurgeProtectorSwitchConfig(
        housing_form=housing_form,
        switch_scheme=switch_scheme,
        mount=mount,
        face_power=face_power,
        outlet_count=n,
        palette_style=palette,
        outlet_pitch=pitch,
        body_width=width,
        body_height=height,
        rocker_travel=travel,
        reset_travel=reset_travel,
        body_length=body_length,
        outlet_xs=outlet_xs,
        switch_specs=switch_specs,
        outlet_y=outlet_y,
        switch_y=switch_y,
        top_z=height,
        face_zone_x=face_zone_x,
        name=cfg.name or "surge_protector_switch",
    )


def with_overrides(
    config: SurgeProtectorSwitchConfig, **kwargs: object
) -> SurgeProtectorSwitchConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: SurgeProtectorSwitchConfig | ResolvedSurgeProtectorSwitchConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedSurgeProtectorSwitchConfig)
        else resolve_config(config)
    )
    return (
        ("housing_form", r.housing_form),
        ("switch_scheme", r.switch_scheme),
        ("mount", r.mount),
        ("face_power", r.face_power),
        ("outlet_count", f"outlets_{r.outlet_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Shared CadQuery shapes (each built ONCE per build, reused across N).
# ---------------------------------------------------------------------------
def _rounded_box(size: tuple[float, float, float], radius: float) -> cq.Workplane:
    shape = cq.Workplane("XY").box(size[0], size[1], size[2])
    if radius > 0.0:
        try:
            shape = shape.edges("|Z").fillet(radius)
        except Exception:
            pass
    return shape


def _outlet_plate_shape() -> cq.Workplane:
    """NEMA-style receptacle plate with real cut-through slots (S2 L52-67)."""
    sx, sy, sz = 0.044, 0.035, 0.0048
    plate = _rounded_box((sx, sy, sz), 0.004)
    cutters = [
        cq.Workplane("XY").box(0.0048, 0.014, sz * 5).translate((0.008, -0.007, 0.0)),
        cq.Workplane("XY").box(0.0048, 0.014, sz * 5).translate((0.008, 0.007, 0.0)),
        cq.Workplane("XY").box(0.0058, 0.010, sz * 5).translate((-0.010, 0.0, 0.0)),
        cq.Workplane("XY").circle(0.0046).extrude(sz * 5).translate((-0.015, 0.0, -sz * 2.5)),
    ]
    for cutter in cutters:
        plate = plate.cut(cutter)
    return plate


def _rocker_shape() -> cq.Workplane:
    """Small bevelled rectangular rocker cap (S2 L70-77)."""
    body = _rounded_box((0.027, 0.016, 0.006), 0.0022)
    rib = _rounded_box((0.019, 0.003, 0.0015), 0.0008).translate((0.0, 0.0, 0.0037))
    return body.union(rib)


def _master_rocker_shape() -> cq.Workplane:
    """Large bevelled master rocker cap (single_master fork L60-67)."""
    body = _rounded_box((0.052, 0.024, 0.008), 0.003)
    rib = _rounded_box((0.038, 0.004, 0.002), 0.001).translate((0.003, 0.0, 0.005))
    detent = _rounded_box((0.004, 0.018, 0.0015), 0.0005).translate((-0.022, 0.0, 0.0047))
    return body.union(rib).union(detent)


def _switch_bezel_shape() -> cq.Workplane:
    """Black raised switch well / bezel surrounding a rocker (S2 L79-85)."""
    sx, sy, sz = 0.036, 0.024, 0.006
    bezel = _rounded_box((sx, sy, sz), 0.0035)
    recess = cq.Workplane("XY").box(0.029, 0.017, sz * 3).translate((0.0, 0.0, 0.0015))
    return bezel.cut(recess)


def _master_bezel_shape() -> cq.Workplane:
    """Black raised bezel well for the single master rocker (single_master L70-75)."""
    sx, sy, sz = 0.064, 0.034, 0.007
    bezel = _rounded_box((sx, sy, sz), 0.004)
    recess = cq.Workplane("XY").box(0.054, 0.026, sz * 3).translate((0.0, 0.0, 0.002))
    return bezel.cut(recess)


def _mount_tab_shape() -> cq.Workplane:
    """Flat end mounting foot with a screw/keyhole opening (S2 L87-93)."""
    sx, sy, sz = 0.056, 0.078, 0.0045
    tab = _rounded_box((sx, sy, sz), 0.004)
    round_hole = cq.Workplane("XY").circle(0.006).extrude(sz * 5).translate((-0.010, 0.0, -sz * 2.5))
    slot_hole = cq.Workplane("XY").box(0.014, 0.006, sz * 5).translate((0.006, 0.0, 0.0))
    return tab.cut(round_hole).cut(slot_hole)


def _usb_block_shape() -> cq.Workplane:
    """Recessed USB charging panel with cut-through port cavities (usb fork L87-109)."""
    sx, sy, sz = 0.036, 0.026, 0.006
    block = _rounded_box((sx, sy, sz), 0.003)
    for offset_x in (-0.008, 0.008):
        port = cq.Workplane("XY").box(0.012, 0.005, sz * 5).translate((offset_x, 0.005, 0.0))
        block = block.cut(port)
    port_c = cq.Workplane("XY").box(0.009, 0.0035, sz * 5).translate((0.0, -0.006, 0.0))
    return block.cut(port_c)


def _reset_cap_solid() -> cq.Workplane:
    """Domed reset/circuit-breaker button cap (reset fork L246-254)."""
    r_cap, h_cap = 0.0055, 0.005
    profile = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(r_cap, 0.0)
        .lineTo(r_cap, h_cap * 0.65)
        .threePointArc((r_cap * 0.5, h_cap * 1.02), (0.0, h_cap))
        .close()
    )
    return profile.revolve(360, (0.0, 0.0, 0.0), (0.0, 1.0, 0.0))


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------
def _make_mats(model: ArticulatedObject, style: str) -> dict:
    pal = PALETTES[style]
    mats = {
        key: model.material(f"sp_{key}_{style}", rgba=rgba) for key, rgba in pal.items()
    }
    for key, rgba in _FUNCTIONAL_MATERIALS.items():
        mats[key] = model.material(f"sp_{key}", rgba=rgba)
    return mats


# ---------------------------------------------------------------------------
# Slot A: housing_form  (ROOT part + outlets + switch seats + ribs + label)
# ---------------------------------------------------------------------------
def _build_housing(model, r: ResolvedSurgeProtectorSwitchConfig, mats: dict, meshes: dict):
    housing = model.part("housing")
    L, W, H = r.body_length, r.body_width, r.body_height
    TOP = r.top_z
    raised = r.housing_form == "raised_bezel"

    housing.visual(
        meshes["shell"],
        origin=Origin(xyz=(0.0, 0.0, H / 2.0)),
        material=mats["housing"],
        name="main_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    housing.inertial = Inertial.from_geometry(
        Box((L, W, H)), mass=0.9, origin=Origin(xyz=(0.0, 0.0, H / 2.0))
    )

    # Long side protective ribs (both forms; raised bezel adds a center divider).
    rib_len = L * 0.90
    for y in (-W / 2.0 - 0.0006, W / 2.0 + 0.0006):
        for k in range(3):
            z = 0.006 + k * (H - 0.010) / 2.0
            housing.visual(
                Box((rib_len, 0.0028, 0.0026)),
                origin=Origin(xyz=(0.0, y, z)),
                material=mats["rib"],
                name=f"side_rib_{'p' if y > 0 else 'n'}_{k}", material_class_id="plastic.opaque_glossy_molded",
            )
    if raised:
        housing.visual(
            Box((L * 0.82, 0.006, 0.009)),
            origin=Origin(xyz=(0.0, (r.outlet_y + r.switch_y) / 2.0, TOP + 0.002)),
            material=mats["housing"],
            name="center_divider", material_class_id="plastic.opaque_glossy_molded",
        )
    # Rating label on the top face (host-conformal, always sits on TOP).
    housing.visual(
        Box((min(0.09, L * 0.20), 0.012, 0.0009)),
        origin=Origin(xyz=(-L * 0.18, (r.outlet_y + r.switch_y) / 2.0, TOP - 0.0003)),
        material=mats["label"],
        name="rating_label", appearance_only=AppearanceOnlySpec(kind="decal"),
    )

    # Outlets (multiplicity loop; single reused plate mesh).
    oy = r.outlet_y
    for i, x in enumerate(r.outlet_xs):
        if raised:
            housing.visual(
                Box((0.031, 0.026, 0.0018)),
                origin=Origin(xyz=(x, oy, TOP + 0.001)),
                material=mats["brass"],
                name=f"brass_contact_backing_{i}", material_class_id="metal.brass_polished",
            )
            housing.visual(
                Box((0.051, 0.042, 0.0015)),
                origin=Origin(xyz=(x, oy, TOP + 0.0004)),
                material=mats["dark"],
                name=f"outlet_recess_shadow_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
            housing.visual(
                meshes["outlet_plate"],
                origin=Origin(xyz=(x, oy, TOP + 0.0038)),
                material=mats["accent"],
                name=f"outlet_plate_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        else:
            # recessed_flat: sunk dark cavity + flush plate + brass in cavity.
            housing.visual(
                Box((0.048, 0.040, 0.008)),
                origin=Origin(xyz=(x, oy, TOP - 0.004)),
                material=mats["dark"],
                name=f"outlet_recess_shadow_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
            housing.visual(
                Box((0.031, 0.026, 0.0018)),
                origin=Origin(xyz=(x, oy, TOP - 0.005)),
                material=mats["brass"],
                name=f"brass_contact_backing_{i}", material_class_id="metal.brass_polished",
            )
            housing.visual(
                meshes["outlet_plate"],
                origin=Origin(xyz=(x, oy, TOP - 0.0016)),
                material=mats["accent"],
                name=f"outlet_plate_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        for yy in (-0.0145, 0.0145):
            housing.visual(
                Cylinder(radius=0.0022, length=0.0015),
                origin=Origin(xyz=(x + 0.017, oy + yy, TOP + (0.0062 if raised else -0.0002))),
                material=mats["dark"],
                name=f"outlet_screw_{i}_{'p' if yy > 0 else 'n'}", material_class_id="metal.blackened_gunmetal",
            )

    # Switch seats (bezel/well) at each switch position — read from switch_specs
    # so switch_scheme's rockers line up (Contract 3c). Reused bezel meshes.
    bezel_z = TOP + 0.003  # proud bezel both forms (see _pivot_z rationale)
    for i, (x, kind) in enumerate(r.switch_specs):
        mesh = meshes["master_bezel"] if kind == "master" else meshes["bezel"]
        housing.visual(
            mesh,
            origin=Origin(xyz=(x, r.switch_y, bezel_z)),
            material=mats["accent"] if raised else mats["dark"],
            name=f"switch_bezel_{i}", material_class_id="plastic.opaque_glossy_molded",
        )

    return housing


# ---------------------------------------------------------------------------
# Slot B: switch_scheme  (rocker parts + REVOLUTE joints, all axis +Y)
# ---------------------------------------------------------------------------
def _pivot_z(r: ResolvedSurgeProtectorSwitchConfig) -> float:
    # Unified proud switch seat (both forms) so the rocker clears the solid shell
    # top through full travel; the ③ recessed/raised distinction is carried by the
    # OUTLET treatment (flush-in-cavity vs proud-on-pedestal), not the switch.
    return r.top_z + 0.010


def _build_rocker_part(model, name, cap_mesh, is_master, mats):
    rocker = model.part(name)
    rocker.visual(
        cap_mesh,
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, -0.10, 0.0)),
        material=mats["red_lens"],
        name="rocker_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    if is_master:
        rocker.visual(
            Cylinder(radius=0.003, length=0.036),
            origin=Origin(xyz=(0.0, 0.0, -0.005), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["dark"],
            name="pivot_pin", material_class_id="metal.blackened_gunmetal",
        )
        rocker.visual(
            Box((0.016, 0.004, 0.004)),
            origin=Origin(xyz=(0.005, 0.0, 0.004)),
            material=mats["red_hi"],
            name="on_end_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        rocker.visual(
            Box((0.005, 0.016, 0.004)),
            origin=Origin(xyz=(-0.022, 0.0, 0.004)),
            material=mats["red_hi"],
            name="off_end_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        rocker.inertial = Inertial.from_geometry(
            Box((0.052, 0.024, 0.008)), mass=0.02, origin=Origin(xyz=(0.0, 0.0, 0.0))
        )
    else:
        rocker.visual(
            Cylinder(radius=0.0025, length=0.029),
            origin=Origin(xyz=(0.0, 0.0, -0.0040), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["dark"],
            name="pivot_pin", material_class_id="metal.blackened_gunmetal",
        )
        rocker.visual(
            Box((0.018, 0.0016, 0.001)),
            origin=Origin(xyz=(0.0045, 0.0, 0.0027), rpy=(0.0, -0.10, 0.0)),
            material=mats["red_hi"],
            name="on_end_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        rocker.visual(
            Box((0.008, 0.0016, 0.001)),
            origin=Origin(xyz=(-0.009, 0.0, 0.0027), rpy=(0.0, -0.10, 0.0)),
            material=mats["red_hi"],
            name="off_end_marker", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
        rocker.inertial = Inertial.from_geometry(
            Box((0.027, 0.016, 0.006)), mass=0.014, origin=Origin(xyz=(0.0, 0.0, 0.0))
        )
    return rocker


def _build_switch_scheme(model, housing, r: ResolvedSurgeProtectorSwitchConfig, mats, meshes):
    pivot_z = _pivot_z(r)
    for i, (x, kind) in enumerate(r.switch_specs):
        is_master = kind == "master"
        cap_mesh = meshes["master_rocker"] if is_master else meshes["rocker"]
        rocker = _build_rocker_part(model, f"rocker_{i}", cap_mesh, is_master, mats)
        upper = max(r.rocker_travel, 0.24) if is_master else r.rocker_travel
        model.articulation(
            f"housing_to_rocker_{i}",
            ArticulationType.REVOLUTE,
            parent=housing,
            child=rocker,
            origin=Origin(xyz=(x, r.switch_y, pivot_z)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=0.7, velocity=4.0, lower=-upper, upper=upper),
            meta={"mechanism": "detented rocker switch", "lower_label": "OFF", "upper_label": "ON"},
        )


# ---------------------------------------------------------------------------
# Slot C: mount  (fixed housing visuals, no joints)
# ---------------------------------------------------------------------------
def _apply_mount(housing, r: ResolvedSurgeProtectorSwitchConfig, mats, meshes):
    L, W, H = r.body_length, r.body_width, r.body_height
    TOP = r.top_z
    if r.mount == "flat_feet":
        fx = L / 2.0 - 0.030
        fy = W / 2.0 - 0.010
        for j, (sx, sy) in enumerate(((-fx, -fy), (fx, -fy), (-fx, fy), (fx, fy))):
            housing.visual(
                Box((0.022, 0.016, 0.008)),
                origin=Origin(xyz=(sx, sy, -0.003)),  # embeds 1mm into the shell bottom
                material=mats["rubber"],
                name=f"foot_{j}", material_class_id="rubber.smooth_plain",
            )
            housing.visual(
                Cylinder(radius=0.004, length=0.0016),
                origin=Origin(xyz=(sx, sy, TOP - 0.0006)),
                material=mats["dark"],
                name=f"corner_screw_{j}", material_class_id="metal.blackened_gunmetal",
            )
    else:  # wall_keyhole_guard (S2 L145-180)
        for sign, tag in ((-1.0, "front"), (1.0, "rear")):
            x_cap = sign * (L / 2.0 + 0.006)
            housing.visual(
                meshes["endcap"],
                origin=Origin(xyz=(x_cap, 0.0, H / 2.0)),
                material=mats["endcap"],
                name=f"endcap_{tag}", material_class_id="plastic.opaque_glossy_molded",
            )
            housing.visual(
                meshes["mount_tab"],
                origin=Origin(xyz=(sign * (L / 2.0 + 0.045), 0.0, 0.0025)),
                material=mats["endcap"],
                name=f"keyhole_{tag}", material_class_id="plastic.opaque_glossy_molded",
            )
            housing.visual(
                Box((0.012, W + 0.022, 0.010)),
                origin=Origin(xyz=(sign * (L / 2.0 + 0.055), 0.0, H + 0.016)),
                material=mats["housing"],
                name=f"guard_bar_{tag}", material_class_id="plastic.opaque_glossy_molded",
            )
            for y in (-W * 0.52, W * 0.52):
                housing.visual(
                    Box((0.070, 0.009, 0.017)),
                    origin=Origin(xyz=(sign * (L / 2.0 + 0.020), y, H + 0.009)),
                    material=mats["housing"],
                    name=f"guard_post_{tag}_{'p' if y > 0 else 'n'}", material_class_id="plastic.opaque_glossy_molded",
                )
            for y in (-0.032, 0.032):
                housing.visual(
                    Cylinder(radius=0.0045, length=0.002),
                    origin=Origin(xyz=(sign * (L / 2.0 + 0.006), y, H + 0.0018)),
                    material=mats["steel"],
                    name=f"endcap_screw_{tag}_{'p' if y > 0 else 'n'}", material_class_id="metal.steel_bare",
                )


# ---------------------------------------------------------------------------
# Slot D: face_power  (cord/plug always; optional LED / reset button / USB)
# ---------------------------------------------------------------------------
def _apply_face_power(model, housing, r: ResolvedSurgeProtectorSwitchConfig, mats, meshes):
    L, H = r.body_length, r.body_height
    TOP = r.top_z
    h = L / 2.0
    face = r.face_power
    fx = r.face_zone_x

    # --- cord + plug (all variants). Strain-relief boot overlaps the shell end
    #     so the cord connects regardless of mount hardware. Swept-spline tube. ---
    housing.visual(
        Cylinder(radius=0.012, length=0.044),
        origin=Origin(xyz=(h - 0.008, 0.0, 0.027), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["rubber"],
        name="strain_relief_boot", material_class_id="rubber.smooth_plain",
    )
    for j in range(4):
        housing.visual(
            Cylinder(radius=0.0125, length=0.0025),
            origin=Origin(xyz=(h + 0.006 + j * 0.006, 0.0, 0.027), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["rubber"],
            name=f"strain_relief_rib_{j}", material_class_id="rubber.smooth_plain",
        )
    cable_geom = tube_from_spline_points(
        [
            (h + 0.030, 0.0, 0.028),
            (h * 0.72, 0.05, 0.045),
            (h * 0.40, 0.23, 0.040),
            (-h * 0.03, 0.315, 0.033),
            (-h * 0.42, 0.27, 0.020),
        ],
        radius=0.006,
        samples_per_segment=14,
        radial_segments=16,
        cap_ends=True,
    )
    housing.visual(
        mesh_from_geometry(cable_geom, "power_cord"),
        material=mats["rubber"],
        name="power_cord", material_class_id="rubber.smooth_plain",
    )
    plug_x = -h * 0.44
    plug_y = 0.265
    housing.visual(
        Cylinder(radius=0.030, length=0.017),
        origin=Origin(xyz=(plug_x, plug_y, 0.010)),
        material=mats["rubber"],
        name="plug_body", material_class_id="rubber.smooth_plain",
    )
    housing.visual(
        Cylinder(radius=0.010, length=0.030),
        origin=Origin(xyz=(plug_x + 0.025, plug_y + 0.002, 0.016), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["rubber"],
        name="plug_grommet", material_class_id="rubber.smooth_plain",
    )
    for j, dx in enumerate((-0.009, 0.009)):
        housing.visual(
            Box((0.0045, 0.0025, 0.034)),
            origin=Origin(xyz=(plug_x + dx, plug_y - 0.015, 0.0355)),
            material=mats["steel"],
            name=f"plug_flat_blade_{j}", material_class_id="metal.steel_bare",
        )
    housing.visual(
        Cylinder(radius=0.0028, length=0.030),
        origin=Origin(xyz=(plug_x, plug_y + 0.017, 0.0335)),
        material=mats["steel"],
        name="plug_ground_pin", material_class_id="metal.steel_bare",
    )

    # --- green protection LED (all except the basic cord_plug) ---
    if face in ("cord_plug_led", "reset_breaker", "usb_ports"):
        housing.visual(
            Cylinder(radius=0.006, length=0.004),
            origin=Origin(xyz=(fx, 0.016, TOP + 0.001)),
            material=mats["green_led"],
            name="green_led", material_class_id="tech.emissive_surface",
        )

    # --- USB charging block (fixed visual, no joint) ---
    if face == "usb_ports":
        housing.visual(
            Box((0.031, 0.022, 0.0018)),
            origin=Origin(xyz=(fx, -0.018, TOP + 0.0004)),
            material=mats["brass"],
            name="usb_brass_backing", material_class_id="metal.brass_polished",
        )
        housing.visual(
            meshes["usb_block"],
            origin=Origin(xyz=(fx, -0.018, TOP + 0.0022)),
            material=mats["accent"],
            name="usb_charging_panel", material_class_id="plastic.opaque_glossy_molded",
        )
        housing.visual(
            Box((0.018, 0.004, 0.001)),
            origin=Origin(xyz=(fx, -0.036, TOP + 0.0005)),
            material=mats["label"],
            name="usb_label", appearance_only=AppearanceOnlySpec(kind="decal"),
        )

    # --- reset / circuit-breaker push button (PRISMATIC child) ---
    if face == "reset_breaker":
        reset = model.part("reset_breaker_button")
        reset.visual(
            meshes["reset_cap"],
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            material=mats["red_hi"],
            name="reset_cap", material_class_id="plastic.opaque_glossy_molded",
        )
        reset.visual(
            Cylinder(radius=0.003, length=r.reset_travel + 0.004),
            origin=Origin(xyz=(0.0, 0.0, -(r.reset_travel + 0.004) / 2.0)),
            material=mats["dark"],
            name="reset_stem", material_class_id="plastic.opaque_generic",
        )
        reset.inertial = Inertial.from_geometry(
            Cylinder(radius=0.0055, length=0.006), mass=0.005, origin=Origin(xyz=(0.0, 0.0, 0.0))
        )
        # bezel ring on the housing face so the button seats on real hardware.
        housing.visual(
            Cylinder(radius=0.008, length=0.0015),
            origin=Origin(xyz=(fx, -0.020, TOP - 0.0005)),
            material=mats["accent"],
            name="reset_bezel_ring", material_class_id="plastic.opaque_glossy_molded",
        )
        model.articulation(
            "housing_to_reset_breaker",
            ArticulationType.PRISMATIC,
            parent=housing,
            child=reset,
            origin=Origin(xyz=(fx, -0.020, TOP)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=8.0, velocity=0.5, lower=0.0, upper=r.reset_travel),
            meta={"mechanism": "reset/circuit-breaker push button"},
        )


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def _build_meshes(r: ResolvedSurgeProtectorSwitchConfig) -> dict:
    """Build each distinct sub-mesh ONCE; reuse across N (compile budget)."""
    meshes = {
        "shell": mesh_from_cadquery(
            _rounded_box((r.body_length, r.body_width, r.body_height), 0.010), "sp_shell"
        ),
        "outlet_plate": mesh_from_cadquery(_outlet_plate_shape(), "sp_outlet_plate"),
        "bezel": mesh_from_cadquery(_switch_bezel_shape(), "sp_bezel"),
        "rocker": mesh_from_cadquery(_rocker_shape(), "sp_rocker"),
    }
    kinds = {k for _, k in r.switch_specs}
    if "master" in kinds:
        meshes["master_bezel"] = mesh_from_cadquery(_master_bezel_shape(), "sp_master_bezel")
        meshes["master_rocker"] = mesh_from_cadquery(_master_rocker_shape(), "sp_master_rocker")
    if r.mount == "wall_keyhole_guard":
        meshes["endcap"] = mesh_from_cadquery(
            _rounded_box((0.052, r.body_width + 0.013, r.body_height + 0.004), 0.007), "sp_endcap"
        )
        meshes["mount_tab"] = mesh_from_cadquery(_mount_tab_shape(), "sp_mount_tab")
    if r.face_power == "usb_ports":
        meshes["usb_block"] = mesh_from_cadquery(_usb_block_shape(), "sp_usb_block")
    if r.face_power == "reset_breaker":
        meshes["reset_cap"] = mesh_from_cadquery(_reset_cap_solid(), "sp_reset_cap")
    return meshes


def build_surge_protector_switch(
    config: SurgeProtectorSwitchConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"category": "Electrical_Wiring", "small_class": "Surge protector switch"},
    )
    mats = _make_mats(model, r.palette_style)
    meshes = _build_meshes(r)

    housing = _build_housing(model, r, mats, meshes)
    _apply_mount(housing, r, mats, meshes)
    _apply_face_power(model, housing, r, mats, meshes)
    _build_switch_scheme(model, housing, r, mats, meshes)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_surge_protector_switch(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_surge_protector_switch(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_surge_protector_switch_tests(
    object_model: ArticulatedObject,
    config: SurgeProtectorSwitchConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    housing = object_model.get_part("housing")
    hvis = {v.name for v in housing.visuals}
    n = r.outlet_count
    k = len(r.switch_specs)

    # --- captured-pin overlaps (pin + seated cap in the bezel pocket). ---
    for i in range(k):
        rocker = object_model.get_part(f"rocker_{i}")
        ctx.allow_overlap(
            housing, rocker, elem_a=f"switch_bezel_{i}", elem_b="pivot_pin",
            reason="rocker pivot pin is captured in the bezel's molded trunnion pocket.",
        )
        ctx.allow_overlap(
            housing, rocker, elem_a=f"switch_bezel_{i}", elem_b="rocker_shell",
            reason="rocker cap is seated in the recessed bezel well (seated fit).",
        )
    if r.face_power == "reset_breaker":
        reset = object_model.get_part("reset_breaker_button")
        ctx.allow_overlap(
            housing, reset,
            reason="reset button stem is seated in the housing bore (captured push button).",
        )

    # --- identity ---
    ctx.check(
        "small class is Surge protector switch",
        object_model.meta.get("small_class") == "Surge protector switch",
        details=f"meta={object_model.meta}",
    )

    # --- N outlets ---
    ctx.check(
        f"{n} outlet plates present",
        sum(name.startswith("outlet_plate_") for name in hvis) == n,
        details=f"got {sum(name.startswith('outlet_plate_') for name in hvis)}",
    )

    # --- K rocker parts + REVOLUTE +Y joints ---
    rocker_joints = [
        j for j in object_model.articulations if j.name.startswith("housing_to_rocker_")
    ]
    ctx.check(
        f"{k} rocker REVOLUTE joints about +Y",
        len(rocker_joints) == k
        and all(j.articulation_type == ArticulationType.REVOLUTE for j in rocker_joints)
        and all(abs(j.axis[1]) > 0.99 for j in rocker_joints),
        details=f"joints={[(j.name, j.axis) for j in rocker_joints]}",
    )
    # switch_scheme => joint count
    expected_k = {
        "per_outlet": n,
        "master_plus_individual": n + 1,
        "single_master": 1,
    }[r.switch_scheme]
    ctx.check(
        f"switch_scheme {r.switch_scheme} yields {expected_k} rockers",
        k == expected_k,
        details=f"k={k}",
    )

    # --- cord + plug always present ---
    ctx.check(
        "swept-spline cord + three-prong plug present",
        {"power_cord", "plug_body", "plug_flat_blade_0", "plug_flat_blade_1", "plug_ground_pin"}
        <= hvis,
        details=f"missing={sorted({'power_cord','plug_body','plug_flat_blade_0','plug_flat_blade_1','plug_ground_pin'} - hvis)}",
    )
    ctx.check(
        "no chunky braided-box cord greeble",
        not any(name.startswith("braid_") for name in hvis),
        details="braid_* visuals must not exist (dropped S1 greeble)",
    )

    # --- face_power features ---
    if r.face_power in ("cord_plug_led", "reset_breaker", "usb_ports"):
        ctx.check("green protection LED present", "green_led" in hvis)
    if r.face_power == "usb_ports":
        ctx.check(
            "USB charging block present",
            {"usb_charging_panel", "usb_brass_backing"} <= hvis,
            details=f"missing={sorted({'usb_charging_panel','usb_brass_backing'} - hvis)}",
        )
    if r.face_power == "reset_breaker":
        reset_joint = object_model.get_articulation("housing_to_reset_breaker")
        ctx.check(
            "reset breaker joint is PRISMATIC about +Z",
            reset_joint.articulation_type == ArticulationType.PRISMATIC
            and abs(reset_joint.axis[2]) > 0.99,
            details=f"axis={reset_joint.axis}, type={reset_joint.articulation_type}",
        )

    # --- mount hardware ---
    if r.mount == "wall_keyhole_guard":
        ctx.check(
            "wall-mount end caps + keyholes present",
            {"endcap_front", "endcap_rear", "keyhole_front", "keyhole_rear"} <= hvis,
        )
    else:
        ctx.check(
            "flat mounting feet present",
            sum(name.startswith("foot_") for name in hvis) == 4,
        )

    # --- motion: rocker_0 rocks between ON/OFF detents (on_end_marker z shifts) ---
    joint0 = object_model.get_articulation("housing_to_rocker_0")
    lim = joint0.motion_limits
    with ctx.pose({joint0: lim.lower}):
        off_aabb = ctx.part_element_world_aabb(object_model.get_part("rocker_0"), elem="on_end_marker")
    with ctx.pose({joint0: lim.upper}):
        on_aabb = ctx.part_element_world_aabb(object_model.get_part("rocker_0"), elem="on_end_marker")
    off_z = None if off_aabb is None else (off_aabb[0][2] + off_aabb[1][2]) / 2.0
    on_z = None if on_aabb is None else (on_aabb[0][2] + on_aabb[1][2]) / 2.0
    ctx.check(
        "rocker_0 rocks between ON/OFF detent stops",
        off_z is not None and on_z is not None and abs(off_z - on_z) > 0.0015,
        details=f"off_z={off_z}, on_z={on_z}",
    )

    # --- motion: reset button presses in along Z ---
    if r.face_power == "reset_breaker":
        reset = object_model.get_part("reset_breaker_button")
        rj = object_model.get_articulation("housing_to_reset_breaker")
        with ctx.pose({rj: 0.0}):
            pressed = ctx.part_world_position(reset)
        with ctx.pose({rj: r.reset_travel}):
            popped = ctx.part_world_position(reset)
        ctx.check(
            "reset button travels along +Z when actuated",
            pressed is not None and popped is not None and popped[2] > pressed[2] + r.reset_travel * 0.5,
            details=f"pressed={pressed}, popped={popped}",
        )

    # --- slot_choices recorded ---
    ctx.check(
        "slot_choices recorded with all axes",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # --- at least one non-fixed joint ---
    non_fixed = [
        j for j in object_model.articulations if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check("at least one non-fixed joint", len(non_fixed) >= 1, details=f"n={len(non_fixed)}")

    # --- Rule 5: no through-travel 穿模 across the sampled rocker/reset poses. ---
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    return ctx.report()


__all__ = (
    "SurgeProtectorSwitchConfig",
    "ResolvedSurgeProtectorSwitchConfig",
    "build_surge_protector_switch",
    "build_seeded_surge_protector_switch",
    "config_from_seed",
    "resolve_config",
    "run_surge_protector_switch_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
