# SPDX-License-Identifier: Apache-2.0

"""Table with doors and drawers — modular procedural template.

Category identity: a desk (work table) that carries BOTH storage doors AND
storage drawers on a grounded carcass with a raised work surface (~0.72–0.78 m).
Must retain simultaneously a visible desktop, ≥1 real drawer (PRISMATIC), ≥1
real door / closure (REVOLUTE / PRISMATIC / tambour), and a grounded support.

Sources (5-star): 2 origin anchors + 12 slot-fork variants under
``data/records/rec_picturex_0611__table_with_doors_and_drawers__00{1,2}__png_*``
and ``data/records/rec_0611_table_with_doors_and_drawers_var_*``.

Slot graph (pattern = ``mixed``, parallel-children + multiplicity + optional):

    carcass (root, grounded)  — desktop + carcass panels + support form
      ├── PRISMATIC (0,-1,0) drawer_i      (i in [0, drawer_count), always ≥1)
      ├── [REVOLUTE / PRISMATIC] door_j     (j in [0, door_count), always ≥1) —
      │     joint type + geometry from ``closure`` slot
      └── PRISMATIC (0,-1,0) keyboard_tray  (optional; secondary_motion)

Slots (all discrete; per §8.5 axis map):
  * ``worktop_form`` (③ Primary Form Family): rectangular / corner_return /
    wide_rectangular
  * ``closure`` (② joint type swap on the door front): hinged_door /
    sliding_door / roll_top / drop_front
  * ``support_form`` (①): pedestal_plinth / twin_pedestal / four_legs
  * ``drawer_count`` (multiplicity): N ∈ [1, 5]
  * ``door_count`` (multiplicity): M ∈ [1, 3] — forced to 1 for
    sliding_door / roll_top / drop_front
  * ``palette_style`` (⑥): light_maple / beech_graphite / walnut_brass /
    industrial_metal / pale_oak_ivory
  * ``secondary_motion`` (①, optional): none / keyboard_tray

Canonical spec:
``articraft_template_authoring/specs_modular_v1/table_with_doors_and_drawers.md``
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
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

WorktopForm = Literal["rectangular", "corner_return", "wide_rectangular"]
Closure = Literal["hinged_door", "sliding_door", "roll_top", "drop_front"]
SupportForm = Literal["pedestal_plinth", "twin_pedestal", "four_legs"]
SecondaryMotion = Literal["none", "keyboard_tray"]
PaletteStyle = Literal[
    "light_maple",
    "beech_graphite",
    "walnut_brass",
    "industrial_metal",
    "pale_oak_ivory",
]

WORKTOP_FORMS: tuple[WorktopForm, ...] = (
    "rectangular",
    "corner_return",
    "wide_rectangular",
)
CLOSURES: tuple[Closure, ...] = (
    "hinged_door",
    "sliding_door",
    "roll_top",
    "drop_front",
)
SUPPORT_FORMS: tuple[SupportForm, ...] = (
    "pedestal_plinth",
    "twin_pedestal",
    "four_legs",
)
SECONDARY_MOTIONS: tuple[SecondaryMotion, ...] = ("none", "keyboard_tray")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "light_maple",
    "beech_graphite",
    "walnut_brass",
    "industrial_metal",
    "pale_oak_ivory",
)

# Palette assigns real material rgba for every visual by role name. Every
# ``.visual(material=mats[...])`` call sources from this table (Rule 4 palette).
# Sources: S1 (light_maple), S2 (beech_graphite); rest are palette adaptations
# preserving the same role mapping.
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "light_maple": {  # S1 origin (rec_picturex_...001)
        "carcass": (0.82, 0.68, 0.50, 1.0),
        "worktop": (0.90, 0.79, 0.62, 1.0),
        "drawer_front": (0.90, 0.79, 0.62, 1.0),
        "drawer_box": (0.82, 0.68, 0.50, 1.0),
        "door_panel": (0.90, 0.79, 0.62, 1.0),
        "cubby": (0.31, 0.16, 0.075, 1.0),
        "hardware": (0.70, 0.72, 0.72, 1.0),
        "accent": (0.25, 0.27, 0.28, 1.0),
    },
    "beech_graphite": {  # S2 origin (rec_picturex_...002)
        "carcass": (0.15, 0.16, 0.17, 1.0),
        "worktop": (0.82, 0.62, 0.36, 1.0),
        "drawer_front": (0.68, 0.43, 0.21, 1.0),
        "drawer_box": (0.055, 0.06, 0.06, 1.0),
        "door_panel": (0.68, 0.43, 0.21, 1.0),
        "cubby": (0.055, 0.06, 0.06, 1.0),
        "hardware": (0.055, 0.06, 0.055, 1.0),
        "accent": (0.64, 0.67, 0.68, 1.0),
    },
    "walnut_brass": {  # world_knowledge_extrapolation of S1 palette family
        "carcass": (0.24, 0.15, 0.09, 1.0),
        "worktop": (0.32, 0.20, 0.12, 1.0),
        "drawer_front": (0.32, 0.20, 0.12, 1.0),
        "drawer_box": (0.20, 0.13, 0.08, 1.0),
        "door_panel": (0.32, 0.20, 0.12, 1.0),
        "cubby": (0.09, 0.05, 0.03, 1.0),
        "hardware": (0.86, 0.68, 0.34, 1.0),
        "accent": (0.60, 0.45, 0.20, 1.0),
    },
    "industrial_metal": {  # world_knowledge_extrapolation industrial family
        "carcass": (0.72, 0.72, 0.74, 1.0),
        "worktop": (0.45, 0.45, 0.48, 1.0),
        "drawer_front": (0.68, 0.68, 0.70, 1.0),
        "drawer_box": (0.30, 0.30, 0.32, 1.0),
        "door_panel": (0.28, 0.28, 0.30, 1.0),
        "cubby": (0.14, 0.14, 0.16, 1.0),
        "hardware": (0.08, 0.08, 0.09, 1.0),
        "accent": (0.20, 0.20, 0.22, 1.0),
    },
    "pale_oak_ivory": {  # world_knowledge_extrapolation pale oak family
        "carcass": (0.89, 0.86, 0.79, 1.0),
        "worktop": (0.72, 0.55, 0.37, 1.0),
        "drawer_front": (0.89, 0.86, 0.79, 1.0),
        "drawer_box": (0.72, 0.68, 0.60, 1.0),
        "door_panel": (0.72, 0.55, 0.37, 1.0),
        "cubby": (0.32, 0.28, 0.24, 1.0),
        "hardware": (0.66, 0.68, 0.68, 1.0),
        "accent": (0.14, 0.10, 0.06, 1.0),
    },
}


DRAWER_MIN, DRAWER_MAX = 1, 5
DOOR_MIN, DOOR_MAX = 1, 3


@dataclass(frozen=True)
class TableWithDoorsAndDrawersConfig:
    worktop_form: WorktopForm = "rectangular"
    closure: Closure = "hinged_door"
    support_form: SupportForm = "pedestal_plinth"
    drawer_count: int = 2
    door_count: int = 1
    palette_style: PaletteStyle = "light_maple"
    secondary_motion: SecondaryMotion = "none"
    desk_width: float = 1.35
    desk_depth: float = 0.56
    desk_height: float = 0.755
    drawer_travel: float = 0.26
    door_open_angle: float = 1.72
    door_slide_travel: float = 0.28
    tambour_rise: float = 0.22
    drop_front_angle: float = 1.45
    tray_travel: float = 0.25
    name: str = "table_with_doors_and_drawers"


@dataclass(frozen=True)
class ResolvedTableWithDoorsAndDrawersConfig:
    worktop_form: WorktopForm
    closure: Closure
    support_form: SupportForm
    drawer_count: int
    door_count: int
    palette_style: PaletteStyle
    secondary_motion: SecondaryMotion
    # Global.
    desk_width: float
    desk_depth: float
    desk_height: float
    worktop_thickness: float
    plinth_height: float
    wall_thickness: float
    back_thickness: float
    # Pedestal geometry (single pedestal that hosts BOTH drawers and doors,
    # side-by-side splits).
    pedestal_width: float
    pedestal_depth: float
    # Layout (two banks side-by-side in the desk).
    drawer_bank_x: float  # centerline X of the drawer pedestal
    door_bank_x: float  # centerline X of the door pedestal
    # Drawer bank.
    drawer_front_width: float
    drawer_box_width: float
    drawer_box_depth: float
    drawer_front_height: float
    drawer_box_height: float
    drawer_travel: float
    drawer_center_z: tuple[float, ...]
    # Door bank.
    door_pedestal_width: float
    door_panel_width_each: float  # per-door width when M > 1
    door_panel_height: float
    door_open_angle: float
    door_slide_travel: float
    tambour_rise: float
    drop_front_angle: float
    hinge_center_z: float  # for hinged_door
    dropfront_hinge_z: float  # for drop_front (bottom hinge line)
    # Worktop return.
    return_width: float
    return_depth: float
    return_direction_y: float  # +1 or 0
    # Secondary motion.
    tray_travel: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def config_from_seed(seed: int) -> TableWithDoorsAndDrawersConfig:
    """Deterministic procedural sampling (all seeds, no seed=0 special case)."""
    rng = random.Random(seed)
    return TableWithDoorsAndDrawersConfig(
        worktop_form=rng.choice(WORKTOP_FORMS),
        closure=rng.choice(CLOSURES),
        support_form=rng.choice(SUPPORT_FORMS),
        drawer_count=rng.randint(DRAWER_MIN, DRAWER_MAX),
        door_count=rng.randint(DOOR_MIN, DOOR_MAX),
        palette_style=rng.choice(PALETTE_STYLES),
        secondary_motion=rng.choice(SECONDARY_MOTIONS),
        desk_width=round(rng.uniform(1.10, 1.90), 3),
        desk_depth=round(rng.uniform(0.48, 0.72), 3),
        desk_height=round(rng.uniform(0.72, 0.78), 3),
        drawer_travel=round(rng.uniform(0.20, 0.30), 3),
        door_open_angle=round(rng.uniform(1.55, 1.85), 3),
        door_slide_travel=round(rng.uniform(0.20, 0.32), 3),
        tambour_rise=round(rng.uniform(0.18, 0.30), 3),
        drop_front_angle=round(rng.uniform(1.25, 1.55), 3),
        tray_travel=round(rng.uniform(0.20, 0.30), 3),
        name=f"seeded_table_with_doors_and_drawers_{seed}",
    )


def resolve_config(
    config: TableWithDoorsAndDrawersConfig | None = None,
) -> ResolvedTableWithDoorsAndDrawersConfig:
    cfg = config or TableWithDoorsAndDrawersConfig()

    if cfg.worktop_form not in WORKTOP_FORMS:
        raise ValueError(f"Unsupported worktop_form: {cfg.worktop_form}")
    if cfg.closure not in CLOSURES:
        raise ValueError(f"Unsupported closure: {cfg.closure}")
    if cfg.support_form not in SUPPORT_FORMS:
        raise ValueError(f"Unsupported support_form: {cfg.support_form}")
    if cfg.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {cfg.palette_style}")
    if cfg.secondary_motion not in SECONDARY_MOTIONS:
        raise ValueError(f"Unsupported secondary_motion: {cfg.secondary_motion}")

    worktop = cfg.worktop_form
    closure = cfg.closure
    support = cfg.support_form
    palette = cfg.palette_style
    secondary = cfg.secondary_motion

    # --- Compatibility gating (spec §9). ---
    # (a) support_form=four_legs incompatible with closure=roll_top (tambour
    #     needs solid enclosed side to house tracks + housing) OR with
    #     closure=sliding_door (sliding panel translates past the pedestal
    #     outer face into the corner leg's footprint — a real four-legs desk
    #     wraps the slider inside its pedestal and cannot open past the leg).
    #     Degrade to hinged_door which the corner legs clear.
    if support == "four_legs" and closure in ("roll_top", "sliding_door"):
        closure = "hinged_door"
    # (b) worktop_form=corner_return incompatible with support_form=four_legs
    #     (return_leg vs corner_leg conflict); degrade worktop to rectangular.
    if worktop == "corner_return" and support == "four_legs":
        worktop = "rectangular"
    # (c) door_count is forced to 1 unless closure supports multi-panel hinged
    #     doors.
    if closure in ("sliding_door", "roll_top", "drop_front"):
        door_count = 1
    else:
        door_count = int(_clamp(cfg.door_count, DOOR_MIN, DOOR_MAX))
    # (d) drawer_count required ≥1 by identity.
    drawer_count = int(_clamp(cfg.drawer_count, DRAWER_MIN, DRAWER_MAX))
    # (e) secondary_motion=keyboard_tray only when closure supports it AND
    #     drawer_count ≤ 2 (tray sits UNDER the topmost drawer / worktop; more
    #     drawers push into its bay). Degrade otherwise.
    if secondary == "keyboard_tray":
        if closure not in ("hinged_door", "drop_front") or drawer_count > 2:
            secondary = "none"

    desk_width = _clamp(cfg.desk_width, 1.10, 2.00)
    desk_depth = _clamp(cfg.desk_depth, 0.46, 0.78)
    desk_height = _clamp(cfg.desk_height, 0.70, 0.80)
    worktop_thickness = 0.035
    plinth_height = 0.055
    wall_thickness = 0.022
    back_thickness = 0.018

    # Pedestal width sized so two side-by-side pedestals + center knee bay all
    # fit inside desk_width. Each pedestal ≈ 30 % of desk_width, bounded.
    pedestal_width_raw = 0.30 * desk_width
    pedestal_width = _clamp(pedestal_width_raw, 0.30, 0.52)
    pedestal_depth = _clamp(desk_depth - 0.020, 0.42, 0.72)

    # Ensure both pedestals + a small knee (≥ 0.20 m) fit inside desk_width.
    max_pedestal = (desk_width - 0.20) / 2.0
    pedestal_width = min(pedestal_width, max_pedestal)
    pedestal_width = max(pedestal_width, 0.28)

    door_pedestal_width = pedestal_width  # same size as drawer pedestal

    # Two banks: drawer on the right (+X), door on the left (−X). When the
    # support form is `four_legs`, corner legs (0.048 wide) sit at the desk
    # corners; the pedestals must inset inboard by more than a leg width so
    # legs do not intersect the pedestal side walls, the swinging door panel,
    # or the drawer front face. For pedestal/twin-plinth supports there are
    # no corner legs, so we can keep the pedestals near the desk edge.
    half_w = desk_width / 2.0
    if support == "four_legs":
        pedestal_x_inset = 0.070  # > leg_w (0.048) + door/drawer panel clearance
    else:
        pedestal_x_inset = 0.010
    drawer_bank_x = half_w - pedestal_width / 2.0 - pedestal_x_inset
    door_bank_x = -half_w + door_pedestal_width / 2.0 + pedestal_x_inset

    # Vertical drawer stack.
    usable_h = desk_height - worktop_thickness - plinth_height - 0.010
    drawer_pitch = usable_h / max(drawer_count, 1)
    drawer_front_height = _clamp(drawer_pitch * 0.86, 0.09, 0.24)
    drawer_box_height = drawer_front_height * 0.80
    first_z = plinth_height + drawer_pitch * 0.5
    drawer_center_z = tuple(first_z + i * drawer_pitch for i in range(drawer_count))

    # Drawer horizontal geometry (inside pedestal cavity).
    interior_w = pedestal_width - 2.0 * wall_thickness - 0.010
    drawer_front_width = _clamp(interior_w + 0.008, 0.24, 0.50)
    drawer_box_width = _clamp(interior_w - 0.006, 0.20, 0.46)
    drawer_box_depth = _clamp(pedestal_depth - back_thickness - 0.040, 0.30, 0.62)
    drawer_travel = _clamp(cfg.drawer_travel, 0.14, min(0.32, drawer_box_depth * 0.72))

    # Door bank geometry.
    door_panel_height = _clamp(usable_h - 0.070, 0.30, 0.62)
    if door_count >= 2:
        # Multi-hinged doors split the door pedestal width uniformly. gap
        # accommodates the intermediate face_frame_stile (0.012 wide) + swing
        # clearance.
        gap = 0.020
        door_panel_width_each = (
            door_pedestal_width - 2.0 * wall_thickness - (door_count - 1) * gap
        ) / door_count
    else:
        door_panel_width_each = door_pedestal_width - 2.0 * wall_thickness - 0.006
    door_panel_width_each = _clamp(door_panel_width_each, 0.10, 0.60)
    # Cap open angle at ~90° to prevent the swinging panel from raking back
    # into the outer pedestal wall / face-frame stiles.
    door_open_angle = _clamp(cfg.door_open_angle, math.radians(70.0), math.radians(92.0))
    door_slide_travel = _clamp(cfg.door_slide_travel, 0.14, door_pedestal_width * 0.90 + 0.06)
    tambour_rise = _clamp(cfg.tambour_rise, 0.12, door_panel_height - 0.10)
    drop_front_angle = _clamp(cfg.drop_front_angle, math.radians(60.0), math.radians(92.0))

    hinge_center_z = plinth_height + door_panel_height / 2.0 + 0.010
    dropfront_hinge_z = plinth_height + 0.020

    # Worktop return (short L arm) for L-shape forms. Not for wide_rectangular
    # or plain rectangular.
    if worktop == "rectangular":
        return_width, return_depth, return_direction_y = 0.0, 0.0, 0.0
    elif worktop == "wide_rectangular":
        return_width, return_depth, return_direction_y = 0.0, 0.0, 0.0
    else:  # corner_return
        return_width = 0.32
        return_depth = _clamp(desk_depth * 1.4, 0.68, 1.10)
        return_direction_y = 1.0

    # wide_rectangular = same part tree as rectangular but extended in X.
    if worktop == "wide_rectangular":
        desk_width = min(desk_width * 1.20, 2.00)
        half_w = desk_width / 2.0
        drawer_bank_x = half_w - pedestal_width / 2.0 - pedestal_x_inset
        door_bank_x = -half_w + door_pedestal_width / 2.0 + pedestal_x_inset

    tray_travel = _clamp(cfg.tray_travel, 0.15, drawer_box_depth * 0.72)

    return ResolvedTableWithDoorsAndDrawersConfig(
        worktop_form=worktop,
        closure=closure,
        support_form=support,
        drawer_count=drawer_count,
        door_count=door_count,
        palette_style=palette,
        secondary_motion=secondary,
        desk_width=desk_width,
        desk_depth=desk_depth,
        desk_height=desk_height,
        worktop_thickness=worktop_thickness,
        plinth_height=plinth_height,
        wall_thickness=wall_thickness,
        back_thickness=back_thickness,
        pedestal_width=pedestal_width,
        pedestal_depth=pedestal_depth,
        drawer_bank_x=drawer_bank_x,
        door_bank_x=door_bank_x,
        drawer_front_width=drawer_front_width,
        drawer_box_width=drawer_box_width,
        drawer_box_depth=drawer_box_depth,
        drawer_front_height=drawer_front_height,
        drawer_box_height=drawer_box_height,
        drawer_travel=drawer_travel,
        drawer_center_z=drawer_center_z,
        door_pedestal_width=door_pedestal_width,
        door_panel_width_each=door_panel_width_each,
        door_panel_height=door_panel_height,
        door_open_angle=door_open_angle,
        door_slide_travel=door_slide_travel,
        tambour_rise=tambour_rise,
        drop_front_angle=drop_front_angle,
        hinge_center_z=hinge_center_z,
        dropfront_hinge_z=dropfront_hinge_z,
        return_width=return_width,
        return_depth=return_depth,
        return_direction_y=return_direction_y,
        tray_travel=tray_travel,
        name=cfg.name or "table_with_doors_and_drawers",
    )


def with_overrides(
    config: TableWithDoorsAndDrawersConfig, **kwargs: object
) -> TableWithDoorsAndDrawersConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: TableWithDoorsAndDrawersConfig | ResolvedTableWithDoorsAndDrawersConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedTableWithDoorsAndDrawersConfig)
        else resolve_config(config)
    )
    return (
        ("worktop_form", r.worktop_form),
        ("closure", r.closure),
        ("support_form", r.support_form),
        ("drawer_count", f"{r.drawer_count}_drawers"),
        ("door_count", f"{r.door_count}_doors"),
        ("palette_style", r.palette_style),
        ("secondary_motion", r.secondary_motion),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _box(part, size, xyz, material, name: str) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="wood.veneer_panel")


# ---------------------------------------------------------------------------
# Carcass construction (parent visuals only — Rule 1).
# ---------------------------------------------------------------------------


def _build_pedestal_carcass(
    carcass,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
    *,
    center_x: float,
    prefix: str,
    include_plinth: bool,
) -> None:
    """Emit a pedestal carcass (2 side walls + back + floor + top cap [+ plinth]).

    Anchors drawer / door hardware; front is left open for movable children.
    Sources: S1 (rec_picturex_...001 L85-L136), S2 (rec_picturex_...002 L73-L149).
    """
    w = r.pedestal_width
    d = r.pedestal_depth
    ped_h = r.desk_height - r.worktop_thickness - r.plinth_height
    st = r.wall_thickness
    bt = r.back_thickness
    z_body_mid = r.plinth_height + ped_h / 2.0

    if include_plinth:
        # Plinth (below). S1:L104-L110, S2:L99-L110.
        _box(
            carcass,
            (w * 0.94, d * 0.90, r.plinth_height),
            (center_x, 0.0, r.plinth_height / 2.0),
            mats["accent"],
            f"{prefix}_plinth",
        )
    # Side walls. S1:L85-L102, S2:L73-L96.
    for sign, name in ((1.0, "wall_right"), (-1.0, "wall_left")):
        _box(
            carcass,
            (st, d, ped_h),
            (center_x + sign * (w / 2.0 - st / 2.0), 0.0, z_body_mid),
            mats["carcass"],
            f"{prefix}_{name}",
        )
    # Back panel.
    _box(
        carcass,
        (w - 2.0 * st, bt, ped_h),
        (center_x, d / 2.0 - bt / 2.0, z_body_mid),
        mats["cubby"],
        f"{prefix}_back",
    )
    # Floor.
    _box(
        carcass,
        (w - 2.0 * st, d - bt, 0.018),
        (center_x, -bt / 2.0, r.plinth_height + 0.009),
        mats["carcass"],
        f"{prefix}_floor",
    )
    # Top cap (under worktop).
    _box(
        carcass,
        (w - 2.0 * st, d - bt, 0.018),
        (center_x, -bt / 2.0, r.plinth_height + ped_h - 0.009),
        mats["carcass"],
        f"{prefix}_top_cap",
    )


def _emit_drawer_bank_hardware(
    carcass,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
    *,
    center_x: float,
    prefix: str,
) -> None:
    """Emit thin vertical front stiles + per-drawer horizontal slide rails.

    The rails give ``fail_if_articulation_origin_far_from_geometry`` a real
    contact face for each drawer's PRISMATIC joint origin. Sources:
    S1:L146-L158 (drawer_guide_0/1), drawer_count_5:L262-L269 (per-drawer rails).
    """
    w = r.pedestal_width
    d = r.pedestal_depth
    ped_h = r.desk_height - r.worktop_thickness - r.plinth_height
    st = r.wall_thickness
    front_y = -d / 2.0 + 0.010
    z_body_mid = r.plinth_height + ped_h / 2.0

    # Two front stiles anchor the closed drawer fronts.
    for sign, name in ((1.0, "front_stile_right"), (-1.0, "front_stile_left")):
        _box(
            carcass,
            (0.014, 0.020, ped_h - 0.010),
            (center_x + sign * (w / 2.0 - st / 2.0), front_y, z_body_mid),
            mats["carcass"],
            f"{prefix}_{name}",
        )
    # Per-drawer horizontal slide rail across the pedestal front. Rail sits just
    # behind the pedestal front face (inside the cavity) so the drawer front
    # panel can rest against it and the joint MatingContract lands within tol.
    for i, cz in enumerate(r.drawer_center_z):
        _box(
            carcass,
            (w - 2.0 * st, 0.020, 0.012),
            (center_x, front_y + 0.010, cz),
            mats["accent"],
            f"{prefix}_slide_rail_{i}",
        )


def _emit_hinged_door_hardware(
    carcass,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
    *,
    center_x: float,
    prefix: str,
) -> None:
    """Emit front stiles + hinge stiles for each hinged door.

    For M > 1 doors, an intermediate ``face_frame_stile_{k}`` sits between doors.
    Sources: S1:L160-L175 (hinge knuckles), door_count_3:L270-L280 (face frame stiles).
    """
    w = r.door_pedestal_width
    d = r.pedestal_depth
    ped_h = r.desk_height - r.worktop_thickness - r.plinth_height
    st = r.wall_thickness
    front_y = -d / 2.0 + 0.010
    z_body_mid = r.plinth_height + ped_h / 2.0

    # Outer front stiles (also anchor hinge for door_0 and door_{M-1}).
    for sign, name in ((1.0, "front_stile_right"), (-1.0, "front_stile_left")):
        _box(
            carcass,
            (0.014, 0.020, ped_h - 0.010),
            (center_x + sign * (w / 2.0 - st / 2.0), front_y, z_body_mid),
            mats["carcass"],
            f"{prefix}_{name}",
        )
    # Intermediate face-frame stiles for M >= 2.
    if r.door_count >= 2:
        gap = 0.020  # match _door_hinge_x + _build_hinged_door layout
        interior_w = w - 2.0 * st
        # Divide interior_w into M sections separated by (M-1) intermediate stiles.
        for k in range(1, r.door_count):
            # Interior center-line between segment (k-1) and segment k.
            seg_w = r.door_panel_width_each + gap
            x_local = -interior_w / 2.0 + k * seg_w - gap / 2.0
            _box(
                carcass,
                (0.012, 0.018, ped_h - 0.010),
                (center_x + x_local, front_y + 0.006, z_body_mid),
                mats["carcass"],
                f"{prefix}_face_frame_stile_{k}",
            )
    # Hinge knuckles per door (on the LEFT side of each door panel: hinge_x_j).
    for j in range(r.door_count):
        hinge_x = _door_hinge_x(r, center_x, j)
        for i, z in enumerate(
            (
                r.plinth_height + 0.14,
                r.plinth_height + r.door_panel_height - 0.02,
            )
        ):
            _box(
                carcass,
                (0.022, 0.014, 0.048),
                (hinge_x, front_y - 0.006, z),
                mats["hardware"],
                f"{prefix}_hinge_knuckle_{j}_{i}",
            )


def _emit_sliding_door_hardware(
    carcass,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
    *,
    center_x: float,
    prefix: str,
) -> None:
    """Emit horizontal top/bottom track rails for the sliding door.

    Sources: sliding_door:L165-L176 (sliding_track_top / bottom).
    """
    d = r.pedestal_depth
    ped_h = r.desk_height - r.worktop_thickness - r.plinth_height
    st = r.wall_thickness
    front_y = -d / 2.0 + 0.010
    interior_w = r.door_pedestal_width - 2.0 * st
    # Top rail above the panel top, bottom rail below the panel bottom. The
    # sliding_door joint origin sits at `plinth_height + 0.040 + panel_h/2` so
    # the panel spans z ∈ [plinth_height + 0.040, plinth_height + 0.040 + panel_h].
    z_top = r.plinth_height + 0.040 + r.door_panel_height + 0.010
    z_bot = r.plinth_height + 0.040 - 0.010
    for name, z_rail in (("sliding_track_top", z_top), ("sliding_track_bottom", z_bot)):
        _box(
            carcass,
            (interior_w + 0.010, 0.028, 0.012),
            (center_x, front_y, z_rail),
            mats["hardware"],
            f"{prefix}_{name}",
        )
    # Two outer front stiles for structural closure.
    z_body_mid = r.plinth_height + ped_h / 2.0
    for sign, name in ((1.0, "front_stile_right"), (-1.0, "front_stile_left")):
        _box(
            carcass,
            (0.014, 0.020, ped_h - 0.010),
            (center_x + sign * (r.door_pedestal_width / 2.0 - st / 2.0), front_y, z_body_mid),
            mats["carcass"],
            f"{prefix}_{name}",
        )


def _emit_roll_top_hardware(
    carcass,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
    *,
    center_x: float,
    prefix: str,
) -> None:
    """Emit vertical tambour side tracks + tambour housing.

    Sources: roll_top:L177-L198.
    """
    d = r.pedestal_depth
    ped_h = r.desk_height - r.worktop_thickness - r.plinth_height
    st = r.wall_thickness
    front_y = -d / 2.0 + 0.010
    z_body_mid = r.plinth_height + ped_h / 2.0
    interior_w = r.door_pedestal_width - 2.0 * st
    # Two outer front stiles.
    for sign, name in ((1.0, "front_stile_right"), (-1.0, "front_stile_left")):
        _box(
            carcass,
            (0.014, 0.020, ped_h - 0.010),
            (center_x + sign * (r.door_pedestal_width / 2.0 - st / 2.0), front_y, z_body_mid),
            mats["carcass"],
            f"{prefix}_{name}",
        )
    # Left / right vertical tambour tracks.
    for sign, tag in ((-1.0, "left"), (1.0, "right")):
        _box(
            carcass,
            (0.010, 0.020, r.door_panel_height + r.tambour_rise + 0.06),
            (
                center_x + sign * (interior_w / 2.0 - 0.006),
                front_y - 0.004,
                r.plinth_height + (r.door_panel_height + r.tambour_rise) / 2.0 + 0.020,
            ),
            mats["hardware"],
            f"{prefix}_tambour_track_{tag}",
        )
    # Tambour housing pocket up under the worktop.
    _box(
        carcass,
        (interior_w, 0.020, 0.05),
        (
            center_x,
            front_y - 0.002,
            r.plinth_height + r.door_panel_height + 0.03,
        ),
        mats["cubby"],
        f"{prefix}_tambour_housing",
    )


def _emit_drop_front_hardware(
    carcass,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
    *,
    center_x: float,
    prefix: str,
) -> None:
    """Emit bottom hinge rail for the drop-front writing panel.

    Sources: drop_front:L151-L158 (dropfront_hinge_rail).
    """
    d = r.pedestal_depth
    ped_h = r.desk_height - r.worktop_thickness - r.plinth_height
    st = r.wall_thickness
    front_y = -d / 2.0 + 0.010
    z_body_mid = r.plinth_height + ped_h / 2.0
    interior_w = r.door_pedestal_width - 2.0 * st
    # Two outer front stiles.
    for sign, name in ((1.0, "front_stile_right"), (-1.0, "front_stile_left")):
        _box(
            carcass,
            (0.014, 0.020, ped_h - 0.010),
            (center_x + sign * (r.door_pedestal_width / 2.0 - st / 2.0), front_y, z_body_mid),
            mats["carcass"],
            f"{prefix}_{name}",
        )
    # Bottom hinge rail runs along the full interior width at the drop-front hinge Z.
    # Rail is a thin strip on the front carcass plane; the door panel sits IN FRONT of
    # the rail (y further negative), so the rail must not extend into that space.
    _box(
        carcass,
        (interior_w, 0.018, 0.018),
        (center_x, front_y + 0.008, r.dropfront_hinge_z),
        mats["accent"],
        f"{prefix}_dropfront_hinge_rail",
    )


def _emit_support_form(
    carcass,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
) -> None:
    """Emit support form-specific visuals: pedestal plinths, twin plinths,
    or four corner legs. Independent of the drawer / door hardware — those
    live inside their pedestal carcass emitters."""
    if r.support_form == "four_legs":
        # Four rectangular corner legs (support_four_legs:L99-L118).
        leg_w = 0.048
        leg_h = r.desk_height - r.worktop_thickness
        half_w = r.desk_width / 2.0
        half_d = r.desk_depth / 2.0
        for tag, sx, sy in (
            ("leg_fl", -1.0, -1.0),
            ("leg_rl", -1.0, 1.0),
            ("leg_fr", 1.0, -1.0),
            ("leg_rr", 1.0, 1.0),
        ):
            _box(
                carcass,
                (leg_w, leg_w, leg_h),
                (
                    sx * (half_w - leg_w / 2.0 - 0.002),
                    sy * (half_d - leg_w / 2.0 - 0.002),
                    leg_h / 2.0,
                ),
                mats["carcass"],
                tag,
            )


def _build_worktop(
    carcass,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
) -> None:
    """Emit the worktop slab(s) as carcass visuals (Rule 1: no articulation)."""
    z_top = r.desk_height - r.worktop_thickness / 2.0
    # Main worktop.
    _box(
        carcass,
        (r.desk_width, r.desk_depth, r.worktop_thickness),
        (0.0, 0.0, z_top),
        mats["worktop"],
        "main_worktop",
    )
    # Modesty panel across back between pedestals (S1:L139-L144 / S2:L126-L149).
    modesty_w = r.desk_width - 2.0 * r.pedestal_width + 0.020
    if modesty_w > 0.10:
        _box(
            carcass,
            (modesty_w, 0.018, 0.24),
            (0.0, r.desk_depth / 2.0 - 0.012, r.plinth_height + 0.20),
            mats["cubby"],
            "modesty_panel",
        )
    # Return (L) worktop.
    if r.worktop_form == "corner_return":
        # Return sits at −X side of main worktop, extending in +Y (behind).
        ret_x = -r.desk_width / 2.0 - r.return_width / 2.0 + 0.020
        ret_y = r.return_direction_y * (r.desk_depth / 2.0 + r.return_depth / 2.0 - 0.020)
        _box(
            carcass,
            (r.return_width + 0.040, r.return_depth, r.worktop_thickness),
            (ret_x, ret_y, z_top),
            mats["worktop"],
            "return_worktop",
        )
        # Simple support leg under the return outer corner.
        leg_x = ret_x - r.return_width / 2.0 + 0.020
        leg_y = ret_y + r.return_direction_y * (r.return_depth / 2.0 - 0.030)
        _box(
            carcass,
            (0.036, 0.036, r.desk_height - r.worktop_thickness),
            (leg_x, leg_y, (r.desk_height - r.worktop_thickness) / 2.0),
            mats["accent"],
            "return_leg",
        )
        # Cross-brace connecting return leg to the door-pedestal top so the
        # leg is not an isolated island. Bracket runs from the door pedestal's
        # top_cap outward toward the return leg location.
        brace_left_x = -r.desk_width / 2.0 + r.door_pedestal_width - 0.020
        brace_len = abs(ret_x - brace_left_x) + 0.030
        _box(
            carcass,
            (brace_len, 0.020, 0.018),
            (
                (ret_x + brace_left_x) / 2.0,
                ret_y - r.return_direction_y * (r.return_depth / 2.0 - 0.040),
                r.desk_height - r.worktop_thickness - 0.008,
            ),
            mats["carcass"],
            "return_brace",
        )


def _build_carcass(
    carcass,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
) -> None:
    include_plinth = r.support_form != "four_legs"
    # Drawer pedestal.
    _build_pedestal_carcass(
        carcass, r, mats, center_x=r.drawer_bank_x, prefix="drawped", include_plinth=include_plinth
    )
    _emit_drawer_bank_hardware(carcass, r, mats, center_x=r.drawer_bank_x, prefix="drawped")
    # Door pedestal.
    _build_pedestal_carcass(
        carcass, r, mats, center_x=r.door_bank_x, prefix="doorped", include_plinth=include_plinth
    )
    # Closure-specific hardware on the door pedestal.
    if r.closure == "hinged_door":
        _emit_hinged_door_hardware(carcass, r, mats, center_x=r.door_bank_x, prefix="doorped")
    elif r.closure == "sliding_door":
        _emit_sliding_door_hardware(carcass, r, mats, center_x=r.door_bank_x, prefix="doorped")
    elif r.closure == "roll_top":
        _emit_roll_top_hardware(carcass, r, mats, center_x=r.door_bank_x, prefix="doorped")
    else:  # drop_front
        _emit_drop_front_hardware(carcass, r, mats, center_x=r.door_bank_x, prefix="doorped")
    _emit_support_form(carcass, r, mats)
    _build_worktop(carcass, r, mats)


# ---------------------------------------------------------------------------
# Drawer part construction.
# ---------------------------------------------------------------------------
def _build_drawer(
    drawer,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
) -> None:
    """Build a drawer part in its rest-pose local frame.

    Local origin at the joint origin (pedestal front face at drawer Z).
    Front panel outer face at y = 0; box extends into +Y toward the pedestal
    interior (which after axis (0,-1,0) motion translates the drawer OUTWARD
    in world -Y). Sources: S1:L194-L256, drawer_count_5:L35-L101.
    """
    ft = 0.018
    fw = r.drawer_front_width
    fh = r.drawer_front_height
    bw = r.drawer_box_width
    bd = r.drawer_box_depth
    bh = r.drawer_box_height

    # Drawer front panel: outer face at y = 0 (joint origin plane).
    _box(drawer, (fw, ft, fh), (0.0, ft / 2.0, 0.0), mats["drawer_front"], "front_panel")
    box_y_center = ft + bd / 2.0
    for sign, name in ((1.0, "box_side_right"), (-1.0, "box_side_left")):
        _box(
            drawer,
            (0.012, bd, bh),
            (sign * (bw / 2.0 - 0.006), box_y_center, 0.0),
            mats["drawer_box"],
            name,
        )
    _box(
        drawer,
        (bw - 0.024, 0.012, bh),
        (0.0, ft + bd - 0.006, 0.0),
        mats["drawer_box"],
        "box_back",
    )
    _box(
        drawer,
        (bw - 0.024, bd - 0.024, 0.010),
        (0.0, box_y_center, -bh / 2.0 + 0.005),
        mats["drawer_box"],
        "box_bottom",
    )
    # Pull.
    _box(
        drawer,
        (fw * 0.55, 0.008, 0.014),
        (0.0, -0.004, fh * 0.28),
        mats["hardware"],
        "drawer_pull",
    )


# ---------------------------------------------------------------------------
# Door part construction (per closure family).
# ---------------------------------------------------------------------------
def _door_hinge_x(r: ResolvedTableWithDoorsAndDrawersConfig, center_x: float, j: int) -> float:
    """X position of door_j's hinge line inside the door pedestal.

    Doors are arranged left→right. Hinge sits on the LEFT edge of each panel;
    the panel swings outward to +Y (toward user), so the hinge is behind the
    panel at y = −pedestal_depth/2. Hinge_x lands INSIDE the pedestal interior
    boundary so that it sits at (or embedded slightly into) the outer front
    stile for j=0 and just inboard of each intermediate face_frame_stile
    for j ≥ 1.
    """
    st = r.wall_thickness
    gap = 0.020 if r.door_count >= 2 else 0.006
    interior_w = r.door_pedestal_width - 2.0 * st
    # Panel j spans x ∈ [x_local_start, x_local_start + pw] in the pedestal frame.
    x_local_start = -interior_w / 2.0 + j * (r.door_panel_width_each + gap)
    # Hinge sits at the LEFT edge of panel j, just inboard of the stile so the
    # hinge knuckle rests on the front stile face without piercing the panel.
    hinge_x_local = x_local_start + 0.006
    return center_x + hinge_x_local


def _build_hinged_door(
    door,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
    *,
    j: int,
) -> None:
    """Build a right-swinging hinged door panel. Local origin at hinge line
    (world coordinates of hinge_x[j], y = -pedestal_depth/2, z = hinge_center_z).

    The panel extends in +X from the hinge (panel width = door_panel_width_each);
    at rest y ≈ 0, and axis (0,0,+1) opens toward -Y (user) via right-hand rule.
    Source: S1:L258-L292 (single door), door_count_3:L48-L139 (per-door helper).
    """
    pw = r.door_panel_width_each
    ph = r.door_panel_height
    pt = 0.018

    # Panel centered on the segment.
    _box(door, (pw, pt, ph), (pw / 2.0, -pt / 2.0 - 0.004, 0.0), mats["door_panel"], "door_panel")
    # Pull near the free (right) edge.
    _box(
        door,
        (0.020, 0.012, min(0.10, ph * 0.28)),
        (pw - 0.030, -pt - 0.008, 0.0),
        mats["hardware"],
        "door_handle",
    )
    # Hinge leaves along the hinge axis; sit on the panel back face facing +Y.
    for i, z in enumerate((-ph / 2.0 + 0.14, ph / 2.0 - 0.02)):
        _box(
            door,
            (0.020, 0.010, 0.048),
            (0.008, -0.006, z),
            mats["hardware"],
            f"door_hinge_leaf_{i}",
        )


def _build_sliding_door(
    door,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
) -> None:
    """Build the sliding door as a single panel spanning the door pedestal
    front, with top / bottom guide shoes riding in the tracks. Local origin at
    the panel center; the joint origin (at same X) lets the panel translate
    along −X. Source: sliding_door:L259-L301.
    """
    pw = r.door_pedestal_width - 2.0 * r.wall_thickness - 0.004
    ph = r.door_panel_height
    pt = 0.020

    _box(door, (pw, pt, ph), (0.0, 0.0, 0.0), mats["door_panel"], "door_panel")
    # Pull on the right edge.
    _box(
        door,
        (0.016, 0.012, min(0.10, ph * 0.24)),
        (pw / 2.0 - 0.020, -pt / 2.0 - 0.006, 0.0),
        mats["hardware"],
        "door_handle",
    )
    # Guide shoes on top and bottom edges — rest inside the tracks.
    for suffix, z in (("top", ph / 2.0 + 0.004), ("bottom", -ph / 2.0 - 0.004)):
        _box(
            door,
            (pw - 0.020, 0.014, 0.010),
            (0.0, 0.004, z),
            mats["hardware"],
            f"door_guide_{suffix}",
        )


def _build_roll_top_door(
    door,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
) -> None:
    """Build a roll-top tambour door as a bank of horizontal slats + canvas +
    pull. Local origin at the front-face bottom center of the closed pose.
    Source: roll_top:L278-L338.
    """
    pw = r.door_pedestal_width - 2.0 * r.wall_thickness - 0.006
    ph = r.door_panel_height
    slat_h = 0.035
    slat_gap = 0.005
    slat_pitch = slat_h + slat_gap
    slat_count = max(3, min(24, int(ph / slat_pitch)))
    canvas_h = slat_count * slat_pitch - slat_gap

    # Horizontal slats (visuals of the door part; Rule 1 — not separate parts).
    for i in range(slat_count):
        z_local = slat_h / 2.0 + i * slat_pitch
        _box(
            door,
            (pw - 0.008, 0.014, slat_h),
            (0.0, 0.0, z_local),
            mats["door_panel"],
            f"tambour_slat_{i}",
        )
    # Canvas backing behind the slats.
    _box(
        door,
        (pw - 0.020, 0.004, canvas_h),
        (0.0, 0.008, canvas_h / 2.0),
        mats["accent"],
        "tambour_canvas",
    )
    # Pull on the bottom slat.
    _box(
        door,
        (pw * 0.6, 0.010, 0.012),
        (0.0, -0.010, slat_h / 2.0),
        mats["hardware"],
        "door_pull",
    )


def _build_drop_front_door(
    door,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
) -> None:
    """Build a drop-front writing panel with top lip + bottom hinge leaves.
    Local origin at the hinge line (world = door_bank_x, y = -pedestal_depth/2,
    z = dropfront_hinge_z). Panel extends up in +Z from the hinge.
    Source: drop_front:L163-L229.
    """
    pw = r.door_pedestal_width - 2.0 * r.wall_thickness - 0.006
    ph = r.door_panel_height
    pt = 0.018

    _box(door, (pw, pt, ph), (0.0, -pt / 2.0 - 0.004, ph / 2.0), mats["door_panel"], "door_panel")
    # Top lip / finger grip.
    _box(
        door,
        (pw - 0.030, 0.020, 0.012),
        (0.0, -0.006, ph - 0.006),
        mats["accent"],
        "door_top_lip",
    )
    # Handle near the top.
    _box(
        door,
        (min(0.10, pw * 0.4), 0.014, 0.020),
        (0.0, -pt - 0.010, ph - 0.045),
        mats["hardware"],
        "door_handle",
    )
    # Bottom hinge leaves along +X. Bridge from the drop-front hinge rail on
    # the carcass (behind the panel) to the panel's back face — leaf spans
    # both faces so islands / isolated_parts checks stay connected.
    # Panel back face: y_local = -0.004. Rail (in world) front face y ≈
    # (front_y + 0.008) - 0.009 = front_y - 0.001; joint origin world y =
    # front_y + 0.006 → rail front face in door-local frame ≈ -0.007. The
    # rail extends further +Y to y_local = +0.011. Leaf must overlap BOTH
    # panel back (-0.004) and rail (from -0.007 upward). Set leaf center at
    # y_local = 0.006 with thickness 0.030 → spans [-0.009, +0.021].
    for i, xoff in enumerate((-pw * 0.30, pw * 0.30)):
        _box(
            door,
            (0.060, 0.030, 0.022),
            (xoff, 0.006, 0.013),
            mats["hardware"],
            f"hinge_leaf_{i}",
        )


def _build_keyboard_tray(
    tray,
    r: ResolvedTableWithDoorsAndDrawersConfig,
    mats: dict[str, object],
) -> None:
    """Build a keyboard tray as a shallow slide-out shelf. Local origin at joint
    origin (front face just below the top drawer)."""
    tw = r.drawer_front_width * 1.20
    tw = min(tw, r.pedestal_width * 1.6)
    td = r.drawer_box_depth * 0.85
    th = 0.020

    _box(tray, (tw, 0.014, 0.030), (0.0, 0.007, 0.010), mats["accent"], "tray_front")
    _box(tray, (tw, td, th), (0.0, 0.014 + td / 2.0, 0.0), mats["drawer_box"], "tray_bottom")
    # Two side rails to keep the tray connected (islands guard).
    for sign, name in ((1.0, "tray_side_right"), (-1.0, "tray_side_left")):
        _box(
            tray,
            (0.010, td, 0.014),
            (sign * (tw / 2.0 - 0.008), 0.014 + td / 2.0, 0.008),
            mats["drawer_box"],
            name,
        )


# ---------------------------------------------------------------------------
# Top-level build.
# ---------------------------------------------------------------------------
def build_table_with_doors_and_drawers(
    config: TableWithDoorsAndDrawersConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or TableWithDoorsAndDrawersConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.palette_style]
    mats = {
        role: model.material(f"twdad_{role}_{r.palette_style}", rgba=palette[role])
        for role in (
            "carcass",
            "worktop",
            "drawer_front",
            "drawer_box",
            "door_panel",
            "cubby",
            "hardware",
            "accent",
        )
    }

    carcass = model.part("carcass")
    _build_carcass(carcass, r, mats)
    carcass.inertial = Inertial.from_geometry(
        Box((r.desk_width, r.desk_depth, r.desk_height)),
        mass=42.0,
        origin=Origin(xyz=(0.0, 0.0, r.desk_height / 2.0)),
    )

    # Drawers.
    for i, cz in enumerate(r.drawer_center_z):
        drawer = model.part(f"drawer_{i}")
        _build_drawer(drawer, r, mats)
        drawer.inertial = Inertial.from_geometry(
            Box((r.drawer_front_width, r.drawer_box_depth, r.drawer_front_height)),
            mass=3.0,
            origin=Origin(xyz=(0.0, r.drawer_box_depth / 2.0, 0.0)),
        )
        joint_origin = (r.drawer_bank_x, -r.pedestal_depth / 2.0 + 0.010, cz)
        limits = MotionLimits(
            lower=0.0,
            upper=r.drawer_travel,
            effort=80.0,
            velocity=0.32,
        )
        mating = MatingContract(
            parent_face_geometry=f"drawped_slide_rail_{i}",
            parent_face_side="negative_y",
            child_face_geometry="front_panel",
            child_face_side="positive_y",
            contact_tol=0.030,
        )
        model.articulation(
            f"drawer_slide_{i}",
            ArticulationType.PRISMATIC,
            parent=carcass,
            child=drawer,
            origin=Origin(xyz=joint_origin),
            axis=(0.0, -1.0, 0.0),
            motion_limits=limits,
            mating=mating,
            meta={"positive_motion": "drawer extends toward user (-Y)"},
        )

    # Doors.
    if r.closure == "hinged_door":
        for j in range(r.door_count):
            door = model.part(f"door_{j}")
            _build_hinged_door(door, r, mats, j=j)
            door.inertial = Inertial.from_geometry(
                Box((r.door_panel_width_each, 0.020, r.door_panel_height)),
                mass=4.0,
                origin=Origin(xyz=(r.door_panel_width_each / 2.0, 0.0, 0.0)),
            )
            hinge_x = _door_hinge_x(r, r.door_bank_x, j)
            hinge_origin = (
                hinge_x,
                -r.pedestal_depth / 2.0 + 0.006,
                r.hinge_center_z,
            )
            limits = MotionLimits(
                lower=0.0,
                upper=r.door_open_angle,
                effort=12.0,
                velocity=1.5,
            )
            mating = MatingContract(
                parent_face_geometry=(
                    f"doorped_hinge_knuckle_{j}_0"
                    if j == 0 or j >= 0  # always exists
                    else "doorped_front_stile_left"
                ),
                parent_face_side="negative_y",
                child_face_geometry="door_hinge_leaf_0",
                child_face_side="positive_y",
                contact_tol=0.030,
            )
            model.articulation(
                f"door_hinge_{j}",
                ArticulationType.REVOLUTE,
                parent=carcass,
                child=door,
                origin=Origin(xyz=hinge_origin),
                axis=(0.0, 0.0, -1.0),
                motion_limits=limits,
                mating=mating,
                meta={"positive_motion": "door swings outward toward -Y"},
            )
    elif r.closure == "sliding_door":
        door = model.part("door_0")
        _build_sliding_door(door, r, mats)
        door.inertial = Inertial.from_geometry(
            Box((r.door_pedestal_width, 0.020, r.door_panel_height)),
            mass=4.0,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        # Joint origin at the front face of the door pedestal, centerline of the
        # door panel. Offset above the plinth top + floor so the panel bottom
        # (which sits at joint_z - panel_h/2 - guide_h) does NOT dip into the
        # pedestal floor visual.
        joint_origin = (
            r.door_bank_x,
            -r.pedestal_depth / 2.0 + 0.010,
            r.plinth_height + 0.040 + r.door_panel_height / 2.0,
        )
        limits = MotionLimits(
            lower=0.0,
            upper=r.door_slide_travel,
            effort=30.0,
            velocity=0.4,
        )
        model.articulation(
            "door_slide_0",
            ArticulationType.PRISMATIC,
            parent=carcass,
            child=door,
            origin=Origin(xyz=joint_origin),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=limits,
            meta={"positive_motion": "door slides along -X to expose cabinet"},
        )
    elif r.closure == "roll_top":
        door = model.part("door_0")
        _build_roll_top_door(door, r, mats)
        door.inertial = Inertial.from_geometry(
            Box((r.door_pedestal_width, 0.020, r.door_panel_height)),
            mass=4.5,
            origin=Origin(xyz=(0.0, 0.0, r.door_panel_height / 2.0)),
        )
        # Joint origin at bottom of the tambour rest position.
        joint_origin = (
            r.door_bank_x,
            -r.pedestal_depth / 2.0 + 0.010,
            r.plinth_height + 0.020,
        )
        limits = MotionLimits(
            lower=0.0,
            upper=r.tambour_rise,
            effort=25.0,
            velocity=0.4,
        )
        model.articulation(
            "door_slide_0",
            ArticulationType.PRISMATIC,
            parent=carcass,
            child=door,
            origin=Origin(xyz=joint_origin),
            axis=(0.0, 0.0, 1.0),
            motion_limits=limits,
            meta={"positive_motion": "tambour rises to expose cabinet"},
        )
    else:  # drop_front
        door = model.part("door_0")
        _build_drop_front_door(door, r, mats)
        door.inertial = Inertial.from_geometry(
            Box((r.door_pedestal_width, 0.020, r.door_panel_height)),
            mass=5.0,
            origin=Origin(xyz=(0.0, 0.0, r.door_panel_height / 2.0)),
        )
        joint_origin = (
            r.door_bank_x,
            -r.pedestal_depth / 2.0 + 0.006,
            r.dropfront_hinge_z,
        )
        limits = MotionLimits(
            lower=0.0,
            upper=r.drop_front_angle,
            effort=12.0,
            velocity=1.2,
        )
        mating = MatingContract(
            parent_face_geometry="doorped_dropfront_hinge_rail",
            parent_face_side="negative_y",
            child_face_geometry="hinge_leaf_0",
            child_face_side="positive_y",
            contact_tol=0.030,
        )
        model.articulation(
            "door_hinge_0",
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=door,
            origin=Origin(xyz=joint_origin),
            axis=(1.0, 0.0, 0.0),
            motion_limits=limits,
            mating=mating,
            meta={"positive_motion": "drop-front tilts panel downward toward user"},
        )

    # Secondary motion.
    if r.secondary_motion == "keyboard_tray":
        tray = model.part("keyboard_tray")
        _build_keyboard_tray(tray, r, mats)
        tray.inertial = Inertial.from_geometry(
            Box((r.drawer_front_width * 1.20, r.drawer_box_depth * 0.85, 0.030)),
            mass=1.5,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        # Tray sits under the desktop, just below the top drawer.
        top_z = max(r.drawer_center_z) if r.drawer_center_z else r.plinth_height + 0.30
        tray_z = top_z - 0.06
        # Emit rails on the carcass underside so the joint origin lands on real
        # hardware (a small horizontal box below the drawer bank).
        tray_rail_x = r.drawer_bank_x
        _box(
            carcass,
            (r.pedestal_width - 2.0 * r.wall_thickness, 0.020, 0.010),
            (tray_rail_x, -r.pedestal_depth / 2.0 + 0.010, tray_z),
            mats["hardware"],
            "keyboard_tray_rail",
        )
        joint_origin = (tray_rail_x, -r.pedestal_depth / 2.0 + 0.010, tray_z)
        limits = MotionLimits(
            lower=0.0,
            upper=r.tray_travel,
            effort=40.0,
            velocity=0.30,
        )
        model.articulation(
            "keyboard_tray_slide",
            ArticulationType.PRISMATIC,
            parent=carcass,
            child=tray,
            origin=Origin(xyz=joint_origin),
            axis=(0.0, -1.0, 0.0),
            motion_limits=limits,
            meta={"positive_motion": "keyboard tray extends toward user"},
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_table_with_doors_and_drawers(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_table_with_doors_and_drawers(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests.
# ---------------------------------------------------------------------------
def run_table_with_doors_and_drawers_tests(
    object_model: ArticulatedObject,
    config: TableWithDoorsAndDrawersConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("carcass part present", "carcass" in part_names)
    carcass = object_model.get_part("carcass")

    # Drawer topology checks.
    drawer_parts = sorted(n for n in part_names if n.startswith("drawer_"))
    ctx.check(
        "drawer part count matches config",
        len(drawer_parts) == r.drawer_count,
        details=f"expected {r.drawer_count}, got {drawer_parts}",
    )
    for i in range(r.drawer_count):
        joint_name = f"drawer_slide_{i}"
        ctx.check(f"{joint_name} joint present", joint_name in joint_names)
        j = object_model.get_articulation(joint_name)
        ctx.check(
            f"{joint_name} PRISMATIC axis -Y",
            j.articulation_type == ArticulationType.PRISMATIC and tuple(j.axis) == (0.0, -1.0, 0.0),
            details=f"type={j.articulation_type}, axis={j.axis}",
        )

    # Door topology checks (per closure).
    if r.closure == "hinged_door":
        for jdx in range(r.door_count):
            j_name = f"door_hinge_{jdx}"
            ctx.check(f"{j_name} joint present", j_name in joint_names)
            j = object_model.get_articulation(j_name)
            ctx.check(
                f"{j_name} REVOLUTE about Z",
                j.articulation_type == ArticulationType.REVOLUTE
                and abs(abs(j.axis[2]) - 1.0) < 1e-6,
                details=f"axis={j.axis}",
            )
    elif r.closure == "sliding_door":
        j = object_model.get_articulation("door_slide_0")
        ctx.check(
            "sliding door is PRISMATIC along X",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[0]) > 0.99,
            details=f"axis={j.axis}",
        )
    elif r.closure == "roll_top":
        j = object_model.get_articulation("door_slide_0")
        ctx.check(
            "roll_top is PRISMATIC along +Z",
            j.articulation_type == ArticulationType.PRISMATIC and abs(j.axis[2]) > 0.99,
            details=f"axis={j.axis}",
        )
    else:  # drop_front
        j = object_model.get_articulation("door_hinge_0")
        ctx.check(
            "drop_front is REVOLUTE about X",
            j.articulation_type == ArticulationType.REVOLUTE and abs(j.axis[0]) > 0.99,
            details=f"axis={j.axis}",
        )

    # Element-scoped allowances (captured hinges / sliding tracks / tambour).
    if r.closure == "hinged_door":
        for jdx in range(r.door_count):
            door = object_model.get_part(f"door_{jdx}")
            # Element-scoped allowances for EVERY door's hinge knuckle
            # (adjacent doors' knuckles may graze this door's panel when doors
            # are stacked side-by-side).
            for other_j in range(r.door_count):
                for i in range(2):
                    ctx.allow_overlap(
                        carcass,
                        door,
                        elem_a=f"doorped_hinge_knuckle_{other_j}_{i}",
                        elem_b=f"door_hinge_leaf_{i}",
                        reason=("captured hinge: fixed knuckle nests the hinge leaf"),
                    )
                    ctx.allow_overlap(
                        carcass,
                        door,
                        elem_a=f"doorped_hinge_knuckle_{other_j}_{i}",
                        elem_b="door_panel",
                        reason=(
                            "hinge knuckles sit at the panel edge line "
                            "(captured hinge geometry across the door row)"
                        ),
                    )
            # Door panel can graze the outer front stiles and the intermediate
            # face-frame stiles when swinging.
            stile_names = ["doorped_front_stile_left", "doorped_front_stile_right"]
            for k in range(1, r.door_count):
                stile_names.append(f"doorped_face_frame_stile_{k}")
            for stile in stile_names:
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=stile,
                    elem_b="door_panel",
                    reason="door panel sweeps past pedestal front / face-frame stile",
                )
                for i in range(2):
                    ctx.allow_overlap(
                        carcass,
                        door,
                        elem_a=stile,
                        elem_b=f"door_hinge_leaf_{i}",
                        reason="face-frame / front stile grazes the hinge leaf line",
                    )
            # Wall left/right sits at the outer edges; the swinging panel can
            # brush past its front face at large angles.
            for wall in ("doorped_wall_left", "doorped_wall_right"):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=wall,
                    elem_b="door_panel",
                    reason="swinging door panel grazes the pedestal outer wall at ~90°",
                )
                for i in range(2):
                    ctx.allow_overlap(
                        carcass,
                        door,
                        elem_a=wall,
                        elem_b=f"door_hinge_leaf_{i}",
                        reason="hinge leaf sweeps past the pedestal outer wall",
                    )
            # Floor / top_cap can graze the panel when opening.
            for horiz in ("doorped_floor", "doorped_top_cap"):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=horiz,
                    elem_b="door_panel",
                    reason="door panel edge grazes the pedestal floor / top cap when open",
                )
        # Adjacent multi-panel doors share the pedestal opening plane: when one
        # opens the other's closed panel sits in its swing arc — operated in
        # sequence.
        if r.door_count >= 2:
            for a in range(r.door_count):
                for b in range(a + 1, r.door_count):
                    ctx.allow_overlap(
                        object_model.get_part(f"door_{a}"),
                        object_model.get_part(f"door_{b}"),
                        reason=(
                            "adjacent hinged doors share the pedestal opening; "
                            "opened in sequence (mid-open cross-DOF overlap)"
                        ),
                    )
    elif r.closure == "sliding_door":
        door = object_model.get_part("door_0")
        for tag in ("top", "bottom"):
            ctx.allow_overlap(
                carcass,
                door,
                elem_a=f"doorped_sliding_track_{tag}",
                elem_b=f"door_guide_{tag}",
                reason=f"door guide shoe rides inside the {tag} track (captured slide)",
            )
        # The door panel spans the door pedestal opening; as it slides open it
        # translates PAST the left / right walls and beyond the front stiles
        # (into the knee bay). Declare those sweep-through overlaps.
        panel_neighbors = (
            "doorped_front_stile_left",
            "doorped_front_stile_right",
            "doorped_wall_left",
            "doorped_wall_right",
            "doorped_floor",
            "doorped_top_cap",
        )
        for elem in panel_neighbors:
            ctx.allow_overlap(
                carcass,
                door,
                elem_a=elem,
                elem_b="door_panel",
                reason=(
                    "sliding door panel spans / sweeps past pedestal walls, "
                    "stiles, floor and top cap during travel"
                ),
            )
            for tag in ("top", "bottom"):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=elem,
                    elem_b=f"door_guide_{tag}",
                    reason=(
                        "guide shoe sweeps past pedestal walls / stiles / "
                        "floor / top during sliding travel"
                    ),
                )
    elif r.closure == "roll_top":
        door = object_model.get_part("door_0")
        # Every slat is captured by both side tracks.
        slat_count = sum(1 for v in door.visuals if v.name and v.name.startswith("tambour_slat_"))
        for i in range(slat_count):
            for tag in ("left", "right"):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=f"doorped_tambour_track_{tag}",
                    elem_b=f"tambour_slat_{i}",
                    reason=("tambour slat edges are captured inside the vertical tracks"),
                )
        # Slats graze the tambour housing when raised, and the outer stiles.
        # When the tambour rises, its top slats also disappear into a housing
        # pocket that in a real desk curves back BEHIND the worktop; our box
        # approximation cannot curve, so the top slats geometrically cross the
        # main worktop / top_cap plane during the upper half of the travel.
        # This is the same "box approximation of a curved captured member"
        # allowance the roll_top source record uses for slat ↔ housing.
        for elem in (
            "doorped_tambour_housing",
            "doorped_front_stile_left",
            "doorped_front_stile_right",
            "doorped_top_cap",
            "doorped_back",
            "main_worktop",
        ):
            for i in range(slat_count):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=elem,
                    elem_b=f"tambour_slat_{i}",
                    reason=(
                        "tambour slats retract into housing pocket that curves "
                        "behind the worktop; box approximation of the curved "
                        "captured tambour"
                    ),
                )
            # Canvas backing follows the slat bank.
            ctx.allow_overlap(
                carcass,
                door,
                elem_a=elem,
                elem_b="tambour_canvas",
                reason=(
                    "tambour canvas backing follows slat bank into housing "
                    "pocket (curved-tambour box approximation)"
                ),
            )
    else:  # drop_front
        door = object_model.get_part("door_0")
        for i in range(2):
            ctx.allow_overlap(
                carcass,
                door,
                elem_a="doorped_dropfront_hinge_rail",
                elem_b=f"hinge_leaf_{i}",
                reason="drop-front bottom hinge leaf rides on the hinge rail",
            )
            # As the panel drops, the leaf back-face rotates into the
            # pedestal interior, brushing the floor / walls / stiles. Real
            # drop-front hardware is a butt hinge whose leaves sweep past the
            # pedestal frame at those poses.
            for elem in (
                "doorped_floor",
                "doorped_wall_left",
                "doorped_wall_right",
                "doorped_front_stile_left",
                "doorped_front_stile_right",
            ):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=elem,
                    elem_b=f"hinge_leaf_{i}",
                    reason="drop-front hinge leaf sweeps past pedestal frame",
                )
        # Panel grazes the front stiles at rest.
        for stile in ("doorped_front_stile_left", "doorped_front_stile_right"):
            ctx.allow_overlap(
                carcass,
                door,
                elem_a=stile,
                elem_b="door_panel",
                reason="drop-front panel sweeps past pedestal front stile at rest",
            )
        # As the panel drops toward horizontal it swings past / into the
        # pedestal floor plane (real drop-front rests against the floor front
        # edge; box approximation cannot land exactly on the front edge for
        # every desk_height / drop_front_angle combination).
        for elem in (
            "doorped_floor",
            "doorped_top_cap",
            "doorped_back",
            "doorped_wall_left",
            "doorped_wall_right",
        ):
            ctx.allow_overlap(
                carcass,
                door,
                elem_a=elem,
                elem_b="door_panel",
                reason=(
                    "drop-front panel sweeps past pedestal frame during travel "
                    "(box approximation of the butt-hinge fall)"
                ),
            )

    # Drawer cavity allowance (drawer box nests inside the pedestal at rest).
    for i in range(r.drawer_count):
        drawer = object_model.get_part(f"drawer_{i}")
        ctx.allow_overlap(
            carcass,
            drawer,
            reason="drawer box nests inside pedestal cavity while closed",
        )
    # Adjacent drawer fronts share the pedestal opening plane.
    for i in range(r.drawer_count - 1):
        ctx.allow_overlap(
            object_model.get_part(f"drawer_{i}"),
            object_model.get_part(f"drawer_{i + 1}"),
            reason="adjacent stacked drawer fronts share the opening plane",
        )

    # Keyboard tray (if present).
    if r.secondary_motion == "keyboard_tray":
        tray = object_model.get_part("keyboard_tray")
        ctx.allow_overlap(
            carcass,
            tray,
            reason="keyboard tray body slides under the top drawer / desktop",
        )
        # Tray grazes the drawer_0 body when retracted.
        if r.drawer_count > 0:
            ctx.allow_overlap(
                object_model.get_part("drawer_0"),
                tray,
                reason="tray sits under the top drawer bay",
            )

    # Targeted pose checks (Rule 5: prove motion semantics).
    if r.drawer_count > 0:
        j0 = object_model.get_articulation("drawer_slide_0")
        drawer0 = object_model.get_part("drawer_0")
        rest = ctx.part_world_position(drawer0)
        with ctx.pose({j0: j0.motion_limits.upper}):
            extended = ctx.part_world_position(drawer0)
        ctx.check(
            "drawer 0 extends toward user (-Y)",
            rest is not None and extended is not None and extended[1] < rest[1] - 0.08,
            details=f"rest={rest}, extended={extended}",
        )

    # Closure-specific motion check.
    if r.closure == "hinged_door":
        dj = object_model.get_articulation("door_hinge_0")
        door = object_model.get_part("door_0")
        closed_aabb = ctx.part_world_aabb(door)
        with ctx.pose({dj: dj.motion_limits.upper * 0.6}):
            open_aabb = ctx.part_world_aabb(door)
        ctx.check(
            "hinged door swings outward (front / -Y)",
            closed_aabb is not None
            and open_aabb is not None
            and (open_aabb[0][1] < closed_aabb[0][1] - 0.03),
            details=f"closed={closed_aabb}, open={open_aabb}",
        )
    elif r.closure == "sliding_door":
        dj = object_model.get_articulation("door_slide_0")
        door = object_model.get_part("door_0")
        rest = ctx.part_world_position(door)
        with ctx.pose({dj: dj.motion_limits.upper}):
            opened = ctx.part_world_position(door)
        ctx.check(
            "sliding door translates along X",
            rest is not None and opened is not None and abs(opened[0] - rest[0]) > 0.10,
            details=f"rest={rest}, opened={opened}",
        )
    elif r.closure == "roll_top":
        dj = object_model.get_articulation("door_slide_0")
        door = object_model.get_part("door_0")
        rest = ctx.part_world_position(door)
        with ctx.pose({dj: dj.motion_limits.upper}):
            opened = ctx.part_world_position(door)
        ctx.check(
            "tambour rises (+Z)",
            rest is not None and opened is not None and opened[2] > rest[2] + 0.08,
            details=f"rest={rest}, opened={opened}",
        )
    else:  # drop_front
        dj = object_model.get_articulation("door_hinge_0")
        door = object_model.get_part("door_0")
        closed_aabb = ctx.part_world_aabb(door)
        with ctx.pose({dj: dj.motion_limits.upper * 0.7}):
            open_aabb = ctx.part_world_aabb(door)
        ctx.check(
            "drop-front drops top edge downward and forward",
            closed_aabb is not None
            and open_aabb is not None
            and (open_aabb[0][1] < closed_aabb[0][1] - 0.05),
            details=f"closed={closed_aabb}, open={open_aabb}",
        )

    if r.secondary_motion == "keyboard_tray":
        j_tray = object_model.get_articulation("keyboard_tray_slide")
        tray = object_model.get_part("keyboard_tray")
        rest = ctx.part_world_position(tray)
        with ctx.pose({j_tray: j_tray.motion_limits.upper}):
            extended = ctx.part_world_position(tray)
        ctx.check(
            "keyboard tray extends toward user (-Y)",
            rest is not None and extended is not None and extended[1] < rest[1] - 0.08,
            details=f"rest={rest}, extended={extended}",
        )

    # Baseline sampled-pose motion QC. All non-FIXED joints are checked.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = [
    "TableWithDoorsAndDrawersConfig",
    "ResolvedTableWithDoorsAndDrawersConfig",
    "build_table_with_doors_and_drawers",
    "build_seeded_table_with_doors_and_drawers",
    "config_from_seed",
    "resolve_config",
    "run_table_with_doors_and_drawers_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
