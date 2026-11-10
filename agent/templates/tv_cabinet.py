# SPDX-License-Identifier: Apache-2.0

"""TV cabinet — modular procedural template.

Category identity: a low, wide storage TV cabinet (立式/矮式电视机柜) — a laminated
or painted wood carcass sitting on a visible support interface (bun feet /
tapered legs / splayed legs / solid plinth / powder-coated sled / floating wall
mount) with 1..N operable storage fronts on the +front face (side-hinged doors,
drop-front media flap, push-to-open flap row, bifold doors, drawer bank, or
open cubbies with a guard door). NOT the TV itself; NOT a plain table; NOT an
open shelf.

Sources (5-star): 7 parent anchors (`rec_picturex_0611__tv_cabinet__001..007`) +
11 fork variants under `data/records/rec_0611_tv_cabinet_var_*`. See spec
``articraft_template_authoring/specs_modular_v1/tv_cabinet.md``.

Slot graph (pattern = ``mixed``, parallel-children + multiplicity):

    carcass (root, grounded/floating) — body_form defines shell,
       support (bun_feet | tapered_legs | splayed_wood_legs |
                solid_plinth | powder_coated_sled | wall_mount) as visuals
      ├── REVOLUTE / PRISMATIC child_i (closure produces N children, always ≥1)
      └── [optional guard_door] for closure=open_cubbies (Rule 5 coverage)

Slots (all discrete; per §8.5 axis map):
  * ``body_form`` (③ Primary Form Family): rectangular_low_wide,
    rectangular_tall, low_wide_console, bowed_front, corner_wedge,
    stepped_hutch.
  * ``closure`` (①/②): side_hinged_doors, drop_front_flap, push_flap_row,
    bifold_doors, drawer_bank, open_cubbies.
  * ``support`` (①): bun_feet, tapered_legs, splayed_wood_legs, solid_plinth,
    powder_coated_sled, wall_mount.
  * ``palette_style`` (⑥): warm_greige, walnut_dark, light_oak, cherry_wood,
    matte_black_wood, painted_white.
  * ``storage_count`` (multiplicity): N depending on closure.
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

# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "rectangular_low_wide",
    "rectangular_tall",
    "low_wide_console",
    "bowed_front",
    "corner_wedge",
    "stepped_hutch",
]
Closure = Literal[
    "side_hinged_doors",
    "drop_front_flap",
    "push_flap_row",
    "bifold_doors",
    "drawer_bank",
    "open_cubbies",
]
Support = Literal[
    "bun_feet",
    "tapered_legs",
    "splayed_wood_legs",
    "solid_plinth",
    "powder_coated_sled",
    "wall_mount",
]
PaletteStyle = Literal[
    "warm_greige",
    "walnut_dark",
    "light_oak",
    "cherry_wood",
    "matte_black_wood",
    "painted_white",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "rectangular_low_wide",
    "rectangular_tall",
    "low_wide_console",
    "bowed_front",
    "corner_wedge",
    "stepped_hutch",
)
CLOSURES: tuple[Closure, ...] = (
    "side_hinged_doors",
    "drop_front_flap",
    "push_flap_row",
    "bifold_doors",
    "drawer_bank",
    "open_cubbies",
)
SUPPORTS: tuple[Support, ...] = (
    "bun_feet",
    "tapered_legs",
    "splayed_wood_legs",
    "solid_plinth",
    "powder_coated_sled",
    "wall_mount",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "warm_greige",
    "walnut_dark",
    "light_oak",
    "cherry_wood",
    "matte_black_wood",
    "painted_white",
)

# ---------------------------------------------------------------------------
# Palette table — every ``.visual(material=mats[...])`` sources from this.
# Sources: warm_greige (P1 warm painted wood), walnut_dark (P2/P4/P5),
# light_oak (P3), cherry_wood (P7), matte_black_wood (P6), painted_white
# (world_knowledge_extrapolation).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_greige": {  # P1 — warm painted wood
        "body": (0.86, 0.78, 0.66, 1.0),
        "front": (0.90, 0.83, 0.71, 1.0),
        "trim": (0.66, 0.58, 0.48, 1.0),
        "hardware": (0.72, 0.62, 0.42, 1.0),  # brass bail
        "dark": (0.28, 0.24, 0.20, 1.0),
        "grain": (0.72, 0.62, 0.52, 1.0),
    },
    "walnut_dark": {  # P2/P4/P5 — walnut wood
        "body": (0.25, 0.16, 0.10, 1.0),
        "front": (0.32, 0.20, 0.12, 1.0),
        "trim": (0.18, 0.11, 0.07, 1.0),
        "hardware": (0.82, 0.66, 0.36, 1.0),  # brass pull
        "dark": (0.08, 0.06, 0.04, 1.0),
        "grain": (0.18, 0.11, 0.07, 1.0),
    },
    "light_oak": {  # P3 — light oak
        "body": (0.78, 0.66, 0.48, 1.0),
        "front": (0.82, 0.70, 0.52, 1.0),
        "trim": (0.62, 0.50, 0.36, 1.0),
        "hardware": (0.55, 0.55, 0.58, 1.0),  # brushed steel
        "dark": (0.28, 0.22, 0.16, 1.0),
        "grain": (0.55, 0.44, 0.30, 1.0),
    },
    "cherry_wood": {  # P7 — cherry
        "body": (0.55, 0.28, 0.20, 1.0),
        "front": (0.62, 0.32, 0.24, 1.0),
        "trim": (0.42, 0.20, 0.14, 1.0),
        "hardware": (0.78, 0.64, 0.34, 1.0),  # brass
        "dark": (0.22, 0.10, 0.08, 1.0),
        "grain": (0.42, 0.22, 0.16, 1.0),
    },
    "matte_black_wood": {  # P6 — matte black console
        "body": (0.12, 0.12, 0.13, 1.0),
        "front": (0.16, 0.16, 0.17, 1.0),
        "trim": (0.30, 0.30, 0.32, 1.0),
        "hardware": (0.10, 0.10, 0.11, 1.0),  # matte black hw
        "dark": (0.04, 0.04, 0.05, 1.0),
        "grain": (0.20, 0.20, 0.22, 1.0),
    },
    "painted_white": {  # world_knowledge_extrapolation — painted white finish
        "body": (0.92, 0.92, 0.90, 1.0),
        "front": (0.95, 0.95, 0.93, 1.0),
        "trim": (0.82, 0.82, 0.80, 1.0),
        "hardware": (0.62, 0.62, 0.64, 1.0),
        "dark": (0.30, 0.30, 0.32, 1.0),
        "grain": (0.80, 0.80, 0.78, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TVCabinetConfig:
    body_form: BodyForm = "rectangular_low_wide"
    closure: Closure = "side_hinged_doors"
    support: Support = "tapered_legs"
    palette_style: PaletteStyle = "light_oak"
    storage_count: int = 3
    # continuous scales
    carcass_width: float = 1.55
    carcass_depth: float = 0.44
    carcass_height: float = 0.75
    door_open_scale: float = 0.90
    drawer_travel_scale: float = 0.90
    name: str = "tv_cabinet"


@dataclass(frozen=True)
class ResolvedTVCabinetConfig:
    body_form: BodyForm
    closure: Closure
    support: Support
    palette_style: PaletteStyle
    storage_count: int
    # global geometry (world frame)
    carcass_width: float
    carcass_depth: float
    carcass_height: float
    wall_thickness: float
    back_thickness: float
    top_slab_thickness: float
    bottom_slab_thickness: float
    # carcass placement — z-floor of carcass body (raised for wall_mount)
    carcass_floor_z: float
    # closure geometry
    door_open_angle: float  # radians (for side_hinged, bifold, drop_front, push_flap)
    drawer_travel: float  # meters (drawer_bank)
    # per-item layout — set in resolve
    child_count: int  # number of movable children actually emitted
    # body_form knobs
    hutch_upper_height: float  # for stepped_hutch, else 0
    hutch_inset_x: float  # side inset for hutch stage
    console_top_overhang: float  # for low_wide_console, else 0
    corner_wedge_depth: float  # for corner_wedge (front-to-back cut), else 0
    bow_front_bulge: float  # for bowed_front, else 0
    tall_shelf_z: tuple[float, ...]  # for rectangular_tall — internal shelves
    # support geometry
    support_height: float  # visible support element z-height
    # cubby dividers
    cubby_dividers_x: tuple[float, ...]
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> TVCabinetConfig:
    """Deterministic procedural sampling for every seed including 0."""
    rng = random.Random(seed)
    body_form = rng.choice(BODY_FORMS)
    closure = rng.choice(CLOSURES)
    support = rng.choice(SUPPORTS)
    palette_style = rng.choice(PALETTE_STYLES)
    # multiplicity is closure-conditional, sampled here and clamped in resolve
    storage_count = rng.randint(2, 6)
    return TVCabinetConfig(
        body_form=body_form,
        closure=closure,
        support=support,
        palette_style=palette_style,
        storage_count=storage_count,
        carcass_width=round(rng.uniform(1.10, 2.20), 3),
        carcass_depth=round(rng.uniform(0.38, 0.50), 3),
        carcass_height=round(rng.uniform(0.42, 0.95), 3),
        door_open_scale=round(rng.uniform(0.70, 1.0), 3),
        drawer_travel_scale=round(rng.uniform(0.70, 1.0), 3),
        name=f"seeded_tv_cabinet_{seed}",
    )


def resolve_config(config: TVCabinetConfig | None = None) -> ResolvedTVCabinetConfig:
    cfg = config or TVCabinetConfig()

    if cfg.body_form not in BODY_FORMS:
        raise ValueError(f"Unsupported body_form: {cfg.body_form}")
    if cfg.closure not in CLOSURES:
        raise ValueError(f"Unsupported closure: {cfg.closure}")
    if cfg.support not in SUPPORTS:
        raise ValueError(f"Unsupported support: {cfg.support}")
    if cfg.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {cfg.palette_style}")

    body_form = cfg.body_form
    closure = cfg.closure
    support = cfg.support
    palette = cfg.palette_style

    # Compatibility fallbacks (spec §7):
    #   (a) wall_mount × stepped_hutch  → tapered_legs
    #   (b) wall_mount × corner_wedge   → tapered_legs
    #   (c) powder_coated_sled × corner_wedge → splayed_wood_legs
    if support == "wall_mount" and body_form in ("stepped_hutch", "corner_wedge"):
        support = "tapered_legs"
    if support == "powder_coated_sled" and body_form == "corner_wedge":
        support = "splayed_wood_legs"

    # ---- Carcass sizing: body_form conditional ranges (spec §7).
    if body_form == "rectangular_tall":
        carcass_height = _clamp(cfg.carcass_height, 0.80, 1.05)
        carcass_width = _clamp(cfg.carcass_width, 1.10, 1.55)
    elif body_form == "low_wide_console":
        carcass_height = _clamp(cfg.carcass_height, 0.40, 0.55)
        carcass_width = _clamp(cfg.carcass_width, 1.65, 2.20)
    elif body_form == "stepped_hutch":
        carcass_height = _clamp(cfg.carcass_height, 0.85, 1.05)
        carcass_width = _clamp(cfg.carcass_width, 1.20, 1.60)
    else:
        carcass_height = _clamp(cfg.carcass_height, 0.55, 0.80)
        carcass_width = _clamp(cfg.carcass_width, 1.10, 1.90)

    carcass_depth = _clamp(cfg.carcass_depth, 0.38, 0.50)

    wall_thickness = 0.020
    back_thickness = 0.016
    top_slab_thickness = 0.028
    bottom_slab_thickness = 0.024

    # Support height budget (chosen so total object stays visually correct).
    support_heights = {
        "bun_feet": 0.10,
        "tapered_legs": 0.13,
        "splayed_wood_legs": 0.14,
        "solid_plinth": 0.08,
        "powder_coated_sled": 0.10,
        "wall_mount": 0.36,
    }
    support_height = support_heights[support]
    carcass_floor_z = support_height  # bottom of carcass shell sits here

    # ---- Storage count clamping (spec §Multiplicity)
    n = int(cfg.storage_count)
    if closure == "side_hinged_doors":
        child_count = _clamp(n, 2, 4)
    elif closure == "push_flap_row":
        child_count = _clamp(n, 3, 4)
    elif closure == "drawer_bank":
        # NB: 6-drawer 2x3 grid is complex; keep it simple as a single-column
        # stack (P4 canonical). N ∈ {2,3,4}.
        child_count = _clamp(n, 2, 4)
    elif closure == "open_cubbies":
        child_count = _clamp(n, 3, 4)
    elif closure == "bifold_doors":
        child_count = 4  # fixed 2×2
    else:  # drop_front_flap
        child_count = 2  # fixed 2
    child_count = int(child_count)

    # Door angle scaling (spec §7)
    base_door_angle = math.radians(85.0)  # ~1.48 rad safe upper
    door_open_angle = base_door_angle * _clamp(cfg.door_open_scale, 0.5, 1.0)
    # push_flap opens ~85° (drop toward front-down); drop_front similar; side hinged
    # can go a bit further. Clamp for safety.
    door_open_angle = _clamp(door_open_angle, math.radians(45.0), math.radians(90.0))

    # Drawer travel (spec §7): up to 0.28 m.
    drawer_travel = 0.28 * _clamp(cfg.drawer_travel_scale, 0.5, 1.0)
    drawer_travel = _clamp(drawer_travel, 0.14, 0.28)

    # body_form knobs
    hutch_upper_height = 0.0
    hutch_inset_x = 0.0
    console_top_overhang = 0.0
    corner_wedge_depth = 0.0
    bow_front_bulge = 0.0
    tall_shelf_z: tuple[float, ...] = ()

    if body_form == "stepped_hutch":
        hutch_upper_height = _clamp(carcass_height * 0.42, 0.30, 0.45)
        hutch_inset_x = _clamp(carcass_width * 0.14, 0.10, 0.22)
    elif body_form == "low_wide_console":
        console_top_overhang = 0.04
    elif body_form == "corner_wedge":
        # smaller chamfer to avoid geometry pain — carcass keeps rectangular
        # footprint but a triangular back-corner wedge is *added* below top.
        corner_wedge_depth = 0.10
    elif body_form == "bowed_front":
        bow_front_bulge = 0.020
    elif body_form == "rectangular_tall":
        # internal shelves at 1/3 and 2/3
        h_int = carcass_height - top_slab_thickness - bottom_slab_thickness
        tall_shelf_z = (
            carcass_floor_z + bottom_slab_thickness + h_int * 0.33,
            carcass_floor_z + bottom_slab_thickness + h_int * 0.66,
        )

    # cubby dividers for open_cubbies closure (only inner walls; N cubbies → N-1)
    cubby_dividers_x: tuple[float, ...] = ()
    if closure == "open_cubbies":
        interior_w = carcass_width - 2.0 * wall_thickness
        step = interior_w / child_count
        cubby_dividers_x = tuple(
            -carcass_width / 2.0 + wall_thickness + step * (i + 1) for i in range(child_count - 1)
        )

    return ResolvedTVCabinetConfig(
        body_form=body_form,
        closure=closure,
        support=support,
        palette_style=palette,
        storage_count=child_count,
        carcass_width=carcass_width,
        carcass_depth=carcass_depth,
        carcass_height=carcass_height,
        wall_thickness=wall_thickness,
        back_thickness=back_thickness,
        top_slab_thickness=top_slab_thickness,
        bottom_slab_thickness=bottom_slab_thickness,
        carcass_floor_z=carcass_floor_z,
        door_open_angle=float(door_open_angle),
        drawer_travel=float(drawer_travel),
        child_count=int(child_count),
        hutch_upper_height=hutch_upper_height,
        hutch_inset_x=hutch_inset_x,
        console_top_overhang=console_top_overhang,
        corner_wedge_depth=corner_wedge_depth,
        bow_front_bulge=bow_front_bulge,
        tall_shelf_z=tall_shelf_z,
        support_height=support_height,
        cubby_dividers_x=cubby_dividers_x,
        name=cfg.name or "tv_cabinet",
    )


def with_overrides(config: TVCabinetConfig, **kwargs: object) -> TVCabinetConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: TVCabinetConfig | ResolvedTVCabinetConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedTVCabinetConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("closure", r.closure),
        ("support", r.support),
        ("palette_style", r.palette_style),
        ("storage_count", f"{r.storage_count}_children"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Building helpers
# ---------------------------------------------------------------------------
def _box(part, size, xyz, material, name: str) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz), material=material, name=name, material_class_id="wood.engineered_board")


def _carcass_shell(
    carcass,
    r: ResolvedTVCabinetConfig,
    mats: dict[str, object],
) -> None:
    """Emit the primary carcass shell (Rule 1: all decorative geometry as visuals)."""
    W = r.carcass_width
    D = r.carcass_depth
    H = r.carcass_height
    z0 = r.carcass_floor_z  # bottom of shell
    z_top = z0 + H  # top of shell
    st = r.wall_thickness
    bt = r.back_thickness
    tt = r.top_slab_thickness
    bs = r.bottom_slab_thickness

    body_mid_z = z0 + H / 2.0

    # bottom slab
    _box(
        carcass,
        (W - 2 * st, D - bt, bs),
        (0.0, -bt / 2.0, z0 + bs / 2.0),
        mats["body"],
        "bottom_slab",
    )
    # top slab
    top_extra = r.console_top_overhang
    _box(
        carcass,
        (W + 2 * top_extra, D + 2 * top_extra, tt),
        (0.0, 0.0, z_top - tt / 2.0),
        mats["front"] if r.body_form == "low_wide_console" else mats["body"],
        "top_slab",
    )
    # side panels
    for sign, name in ((1.0, "side_right"), (-1.0, "side_left")):
        _box(
            carcass,
            (st, D, H - bs - tt),
            (sign * (W / 2.0 - st / 2.0), 0.0, z0 + bs + (H - bs - tt) / 2.0),
            mats["body"],
            name,
        )
    # back panel
    _box(
        carcass,
        (W - 2 * st, bt, H - bs - tt),
        (0.0, D / 2.0 - bt / 2.0, z0 + bs + (H - bs - tt) / 2.0),
        mats["dark"],
        "back_panel",
    )

    # body_form-specific extras
    if r.body_form == "rectangular_tall":
        # internal shelves — extend past the side inner face by ~3mm so the
        # shelf clearly embeds into each side_panel (no near-degenerate
        # zero-depth contact ambiguity).
        for i, sz in enumerate(r.tall_shelf_z):
            _box(
                carcass,
                (W - 2 * st + 0.006, D - bt - 0.020, 0.018),
                (0.0, -0.010, sz),
                mats["body"],
                f"tall_shelf_{i}",
            )
    elif r.body_form == "stepped_hutch":
        # hutch upper stage — narrower + shorter depth, sits ON top slab.
        # Each hutch element is sized to embed into its neighbours by 3–4mm to
        # keep the internal contact graph unambiguous.
        hw = W - 2.0 * r.hutch_inset_x
        hd = D * 0.75
        hh = r.hutch_upper_height
        hz0 = z_top  # top surface of top_slab (bottom of hutch stage)
        # hutch bottom base — embeds into the top_slab by 2 mm downward.
        _box(
            carcass,
            (hw, hd, 0.020),
            (0.0, 0.0, hz0 + 0.008),  # top at hz0+0.018, bottom at hz0-0.002
            mats["body"],
            "hutch_bottom",
        )
        # hutch sides — extend from hutch_bottom top face up to (and slightly
        # into) hutch_top_slab bottom face.
        side_z_lo = hz0 + 0.014  # 4 mm inside hutch_bottom top face
        side_z_hi = hz0 + hh + 0.004  # 4 mm past hutch_top_slab bottom
        side_h = side_z_hi - side_z_lo
        side_center_z = (side_z_lo + side_z_hi) / 2.0
        for sign, name in ((1.0, "hutch_side_right"), (-1.0, "hutch_side_left")):
            _box(
                carcass,
                (0.020, hd, side_h),
                (sign * (hw / 2.0 - 0.010), 0.0, side_center_z),
                mats["body"],
                name,
            )
        # hutch back — spans full side_h; also touches sides in x.
        _box(
            carcass,
            (hw - 0.040, 0.014, side_h),
            (0.0, hd / 2.0 - 0.007, side_center_z),
            mats["dark"],
            "hutch_back",
        )
        # hutch top slab — sits at top of hutch stage, extends slightly beyond
        # the sides in x (overhang), embeds into sides in z (already handled).
        _box(
            carcass,
            (hw + 0.010, hd + 0.010, 0.020),
            (0.0, 0.0, hz0 + hh),  # top at hz0+hh+0.010, bottom at hz0+hh-0.010
            mats["body"],
            "hutch_top_slab",
        )
    elif r.body_form == "low_wide_console":
        # open shelf mid-height (P6 signature). Embed 3mm past the side inner
        # face so contact is unambiguous (avoids islands false-positives).
        shelf_z = z0 + H * 0.55
        _box(
            carcass,
            (W - 2 * st + 0.006, D - bt - 0.020, 0.018),
            (0.0, -0.010, shelf_z),
            mats["body"],
            "console_shelf",
        )
    elif r.body_form == "bowed_front":
        # Bowed reveal — a small forward-projecting decorative fillet sitting
        # ABOVE the top slab, well clear of the door swing zone.
        _box(
            carcass,
            (W * 0.90, 0.030, 0.010),
            (0.0, -D / 2.0 - 0.010, z_top + 0.005),
            mats["front"],
            "bowed_top_reveal",
        )
    elif r.body_form == "corner_wedge":
        # A back-left corner filler — a triangular-look block occupying the
        # back-left corner, embedded into side_left (X) and back_panel (Y) by
        # 3 mm each and spanning slightly past bottom_slab / top_slab in Z.
        cwd = r.corner_wedge_depth
        embed = 0.004
        _box(
            carcass,
            (cwd + embed, cwd + embed, H - bs - tt + embed * 2.0),
            (
                -W / 2.0 + st + cwd / 2.0 - embed / 2.0,
                D / 2.0 - bt - cwd / 2.0 + embed / 2.0,
                body_mid_z,
            ),
            mats["trim"],
            "corner_wedge_fill",
        )

    # A "front rail" band on the front face — thin trim strip runs across
    # bottom edge of the front opening. This gives the carcass a real front
    # geometry the closure's MatingContract can attach to.
    _box(
        carcass,
        (W - 2 * st, 0.014, 0.020),
        (0.0, -D / 2.0 + 0.007, z0 + bs + 0.010),
        mats["trim"],
        "front_bottom_rail",
    )
    # A top rail (matches — under the top slab, on the front face).
    _box(
        carcass,
        (W - 2 * st, 0.014, 0.020),
        (0.0, -D / 2.0 + 0.007, z_top - tt - 0.010),
        mats["trim"],
        "front_top_rail",
    )


def _support_visuals(
    carcass,
    r: ResolvedTVCabinetConfig,
    mats: dict[str, object],
) -> None:
    """Emit support layer visuals attached to the carcass root (Rule 1: no FIXED articulation).

    All support elements are visuals fused into the carcass part except for
    piecewise sled frames which stay as visuals of one carcass shell too.
    """
    W = r.carcass_width
    D = r.carcass_depth
    z0 = r.carcass_floor_z  # z-floor of the carcass shell (top of support)

    if r.support == "bun_feet":
        r_foot = 0.036
        h_foot = z0  # foot sits from ground (0) to carcass floor
        # 4 bun feet, each a simple squat box (approximation of turned bun),
        # placed 4cm inboard of side edges.
        inset = 0.055
        for tag, sx, sy in (
            ("bun_fl", -1.0, -1.0),
            ("bun_fr", 1.0, -1.0),
            ("bun_rl", -1.0, 1.0),
            ("bun_rr", 1.0, 1.0),
        ):
            _box(
                carcass,
                (r_foot * 2.0, r_foot * 2.0, h_foot),
                (
                    sx * (W / 2.0 - inset),
                    sy * (D / 2.0 - inset),
                    h_foot / 2.0,
                ),
                mats["trim"],
                tag,
            )
    elif r.support == "tapered_legs":
        h_leg = z0
        inset = 0.045
        for tag, sx, sy in (
            ("leg_fl", -1.0, -1.0),
            ("leg_fr", 1.0, -1.0),
            ("leg_rl", -1.0, 1.0),
            ("leg_rr", 1.0, 1.0),
        ):
            _box(
                carcass,
                (0.040, 0.040, h_leg),
                (
                    sx * (W / 2.0 - inset),
                    sy * (D / 2.0 - inset),
                    h_leg / 2.0,
                ),
                mats["trim"],
                tag,
            )
    elif r.support == "splayed_wood_legs":
        # box legs with a rpy tilt outward
        h_leg = z0
        inset = 0.050
        # Approximation with vertical legs (splay is small — 3.7° = 0.065 rad).
        # A pure rpy tilt on a Box would tilt the joint origin, so use straight
        # legs with a slightly wider foot spacing (visual approximation).
        for tag, sx, sy in (
            ("leg_fl", -1.0, -1.0),
            ("leg_fr", 1.0, -1.0),
            ("leg_rl", -1.0, 1.0),
            ("leg_rr", 1.0, 1.0),
        ):
            _box(
                carcass,
                (0.048, 0.048, h_leg),
                (
                    sx * (W / 2.0 - inset),
                    sy * (D / 2.0 - inset),
                    h_leg / 2.0,
                ),
                mats["body"],
                tag,
            )
    elif r.support == "solid_plinth":
        # single recessed block plinth
        inset = 0.025
        _box(
            carcass,
            (W - 2 * inset, D - 2 * inset, z0),
            (0.0, 0.0, z0 / 2.0),
            mats["dark"],
            "plinth",
        )
    elif r.support == "powder_coated_sled":
        # 2 U-shape frames (approx by 3 boxes each: bottom + 2 uprights)
        h_leg = z0
        for tag, sx in (("sled_left", -1.0), ("sled_right", 1.0)):
            # bottom horizontal
            _box(
                carcass,
                (0.032, D - 0.10, 0.028),
                (sx * (W / 2.0 - 0.060), 0.0, 0.014),
                mats["hardware"],
                f"{tag}_bottom",
            )
            # front upright
            _box(
                carcass,
                (0.028, 0.028, h_leg - 0.014),
                (
                    sx * (W / 2.0 - 0.060),
                    -D / 2.0 + 0.050,
                    0.028 + (h_leg - 0.014) / 2.0,
                ),
                mats["hardware"],
                f"{tag}_front",
            )
            # back upright
            _box(
                carcass,
                (0.028, 0.028, h_leg - 0.014),
                (
                    sx * (W / 2.0 - 0.060),
                    D / 2.0 - 0.050,
                    0.028 + (h_leg - 0.014) / 2.0,
                ),
                mats["hardware"],
                f"{tag}_back",
            )
    elif r.support == "wall_mount":
        # French cleat back rail — a wall_rail on the back of the carcass.
        # Also a bottom_closure to keep the visible support connected.
        _box(
            carcass,
            (W - 0.10, 0.020, 0.10),
            (0.0, D / 2.0 + 0.010, z0 + 0.05),
            mats["hardware"],
            "wall_rail",
        )
        _box(
            carcass,
            (W - 0.20, 0.014, 0.04),
            (0.0, D / 2.0 + 0.010, z0 + 0.020),
            mats["hardware"],
            "wall_lip",
        )
        # bottom "closure" strip so the cabinet doesn't visually float.
        _box(
            carcass,
            (W - 2 * 0.020, D - 0.020, 0.010),
            (0.0, 0.0, z0 - 0.005),
            mats["dark"],
            "bottom_closure",
        )


def _emit_closure_hardware(
    carcass,
    r: ResolvedTVCabinetConfig,
    mats: dict[str, object],
) -> None:
    """Emit small carcass-side hardware (hinge knuckles, drawer rails) for the
    given closure so joint origins have a real visual anchor + MatingContract
    face.

    Placement policy: hardware sits BEHIND the carcass front face (inside the
    cavity) so it never overlaps the closed door / drawer front. The MatingContract's
    parent face is oriented ``negative_y`` (i.e. its outward normal points -Y
    toward the child) and its child face ``positive_y``; the ``contact_tol``
    (~30 mm) is generous enough to cover both sides.
    """
    W = r.carcass_width
    D = r.carcass_depth
    z0 = r.carcass_floor_z
    bs = r.bottom_slab_thickness
    tt = r.top_slab_thickness
    front_y = -D / 2.0 + 0.003  # world y of carcass front face
    # hardware inset — how far behind the front face the knuckle sits.
    inside_y = front_y + 0.010
    interior_h = r.carcass_height - bs - tt

    if r.closure == "side_hinged_doors":
        # For each door emit (a) a thin vertical hinge_stile spanning the full
        # interior height so it embeds into both front rails (no disconnected
        # knuckles for interior doors), and (b) two hinge knuckles at the
        # canonical hinge positions used by MatingContract.
        for i in range(r.child_count):
            hinge_x = _side_hinged_hinge_x(r, i)
            # Vertical stile — clearly overlaps front_bottom_rail and
            # front_top_rail so the knuckles below become a connected chain.
            _box(
                carcass,
                (0.014, 0.014, interior_h + 0.010),
                (hinge_x, inside_y, z0 + bs + interior_h / 2.0),
                mats["trim"],
                f"hinge_stile_{i}",
            )
            for k, z in enumerate(
                (
                    z0 + bs + interior_h * 0.15,
                    z0 + bs + interior_h * 0.85,
                )
            ):
                _box(
                    carcass,
                    (0.024, 0.014, 0.042),
                    (hinge_x, inside_y, z),
                    mats["hardware"],
                    f"hinge_knuckle_{i}_{k}",
                )
    elif r.closure == "bifold_doors":
        for side in (0, 1):
            hinge_x = _bifold_outer_hinge_x(r, side)
            for k, z in enumerate(
                (
                    z0 + bs + interior_h * 0.20,
                    z0 + bs + interior_h * 0.80,
                )
            ):
                _box(
                    carcass,
                    (0.024, 0.014, 0.042),
                    (hinge_x, inside_y, z),
                    mats["hardware"],
                    f"bifold_hinge_{side}_{k}",
                )
    elif r.closure == "drop_front_flap":
        # 2 media flaps, side-by-side. Bottom hinge rails on carcass front rail.
        for i in range(2):
            cx = _drop_front_center_x(r, i)
            _box(
                carcass,
                (0.10, 0.014, 0.018),
                (cx, inside_y, z0 + bs + 0.014),
                mats["hardware"],
                f"drop_front_rail_{i}",
            )
    elif r.closure == "push_flap_row":
        for i in range(r.child_count):
            cx = _push_flap_center_x(r, i)
            _box(
                carcass,
                (0.10, 0.014, 0.018),
                (cx, inside_y, z0 + bs + 0.014),
                mats["hardware"],
                f"push_flap_rail_{i}",
            )
    elif r.closure == "drawer_bank":
        stack_h = interior_h
        pitch = stack_h / r.child_count
        for i in range(r.child_count):
            cz = z0 + bs + pitch * (i + 0.5)
            # Extend rail 3 mm past each side inner face so it clearly embeds
            # into side_left/side_right (no floating rail-island in the carcass).
            _box(
                carcass,
                (W - 2 * r.wall_thickness + 0.006, 0.018, 0.012),
                (0.0, inside_y, cz),
                mats["trim"],
                f"drawer_slide_rail_{i}",
            )
    elif r.closure == "open_cubbies":
        for i, dx in enumerate(r.cubby_dividers_x):
            # Divider spans the full interior depth (touching back_panel) and
            # full interior height (touching bottom_slab + top_slab) with a small
            # embed so contact is unambiguous.
            _box(
                carcass,
                (0.018, D - r.back_thickness + 0.006, interior_h + 0.006),
                (0.0 + dx, -r.back_thickness / 2.0, z0 + bs + interior_h / 2.0),
                mats["body"],
                f"cubby_divider_{i}",
            )
        gx = _open_cubbies_guard_hinge_x(r)
        for k, z in enumerate(
            (
                z0 + bs + interior_h * 0.15,
                z0 + bs + interior_h * 0.85,
            )
        ):
            _box(
                carcass,
                (0.024, 0.014, 0.042),
                (gx, inside_y, z),
                mats["hardware"],
                f"guard_hinge_{k}",
            )


# ---------------------------------------------------------------------------
# closure geometry helpers
# ---------------------------------------------------------------------------
def _door_panel_width_each(r: ResolvedTVCabinetConfig) -> float:
    """Width of each side-hinged door panel."""
    interior_w = r.carcass_width - 2.0 * r.wall_thickness - 0.010
    gap = 0.008
    return (interior_w - gap * (r.child_count - 1)) / r.child_count


def _door_panel_height(r: ResolvedTVCabinetConfig) -> float:
    interior_h = r.carcass_height - r.bottom_slab_thickness - r.top_slab_thickness
    return interior_h - 0.020


def _side_hinged_hinge_x(r: ResolvedTVCabinetConfig, i: int) -> float:
    """X of the hinge line for side_hinged door i.

    Doors alternate hinge sides so adjacent panels swing apart. Even i → LEFT
    hinge, odd i → RIGHT hinge.
    """
    interior_w = r.carcass_width - 2.0 * r.wall_thickness - 0.010
    gap = 0.008
    pw = _door_panel_width_each(r)
    # panel i spans x-local ∈ [x0, x0+pw] where x0 = -interior_w/2 + i*(pw+gap)
    x0 = -interior_w / 2.0 + i * (pw + gap)
    if i % 2 == 0:
        # hinge on LEFT edge of panel
        return x0 + 0.004
    # hinge on RIGHT edge of panel
    return x0 + pw - 0.004


def _side_hinged_axis_sign(i: int) -> float:
    """Axis-Z sign so the panel swings TOWARD -Y (out of the cabinet).

    Right-hand rule + panel back face at y ≈ -0.011 (in front of joint origin):
    - LEFT hinge (i even), panel extends +X, needs axis (0,0,-1) — clockwise
      viewed from above swings panel out toward -Y.
    - RIGHT hinge (i odd), panel extends -X, needs axis (0,0,+1) — counter-
      clockwise viewed from above swings panel out toward -Y.
    """
    return -1.0 if i % 2 == 0 else 1.0


def _bifold_outer_hinge_x(r: ResolvedTVCabinetConfig, side: int) -> float:
    """X of the outer-leaf hinge (side=0 → left, side=1 → right)."""
    interior_w = r.carcass_width - 2.0 * r.wall_thickness - 0.010
    if side == 0:
        return -interior_w / 2.0 + 0.004
    return interior_w / 2.0 - 0.004


def _bifold_panel_width(r: ResolvedTVCabinetConfig) -> float:
    """Each leaf spans about 1/4 of interior width (2 pairs × 2 leaves)."""
    interior_w = r.carcass_width - 2.0 * r.wall_thickness - 0.010
    return interior_w / 4.0 - 0.006


def _drop_front_center_x(r: ResolvedTVCabinetConfig, i: int) -> float:
    """Center-x for drop-front flap i (0=left, 1=right)."""
    interior_w = r.carcass_width - 2.0 * r.wall_thickness - 0.010
    half = interior_w / 4.0
    return -half if i == 0 else half


def _drop_front_panel_width(r: ResolvedTVCabinetConfig) -> float:
    interior_w = r.carcass_width - 2.0 * r.wall_thickness - 0.010
    return interior_w / 2.0 - 0.008


def _push_flap_center_x(r: ResolvedTVCabinetConfig, i: int) -> float:
    interior_w = r.carcass_width - 2.0 * r.wall_thickness - 0.010
    interior_w / r.child_count - 0.006
    step = interior_w / r.child_count
    x0 = -interior_w / 2.0 + step / 2.0
    return x0 + i * step


def _push_flap_panel_width(r: ResolvedTVCabinetConfig) -> float:
    interior_w = r.carcass_width - 2.0 * r.wall_thickness - 0.010
    return interior_w / r.child_count - 0.006


def _open_cubbies_guard_hinge_x(r: ResolvedTVCabinetConfig) -> float:
    """Guard door hinges on the right-most cubby's right edge."""
    interior_w = r.carcass_width - 2.0 * r.wall_thickness - 0.010
    return interior_w / 2.0 - 0.004


def _open_cubbies_guard_panel_width(r: ResolvedTVCabinetConfig) -> float:
    interior_w = r.carcass_width - 2.0 * r.wall_thickness - 0.010
    # guard covers 1 cubby (rightmost)
    return interior_w / r.child_count - 0.008


def _drawer_front_height(r: ResolvedTVCabinetConfig) -> float:
    interior_h = r.carcass_height - r.bottom_slab_thickness - r.top_slab_thickness
    return interior_h / r.child_count - 0.014


def _drawer_front_width(r: ResolvedTVCabinetConfig) -> float:
    return r.carcass_width - 2.0 * r.wall_thickness - 0.012


def _drawer_box_depth(r: ResolvedTVCabinetConfig) -> float:
    return r.carcass_depth - r.back_thickness - 0.030


def _drawer_center_z(r: ResolvedTVCabinetConfig, i: int) -> float:
    interior_h = r.carcass_height - r.bottom_slab_thickness - r.top_slab_thickness
    pitch = interior_h / r.child_count
    return r.carcass_floor_z + r.bottom_slab_thickness + pitch * (i + 0.5)


# ---------------------------------------------------------------------------
# Closure part builders
# ---------------------------------------------------------------------------
def _build_hinged_door_part(door, r, mats, *, i: int) -> None:
    """Side-hinged door: origin at hinge, panel extends inward (either +X or -X)."""
    pw = _door_panel_width_each(r)
    ph = _door_panel_height(r)
    pt = 0.018
    # Panel direction: if hinge is on LEFT of panel, panel extends +X; if hinge
    # is on RIGHT, panel extends -X.
    sign = 1.0 if i % 2 == 0 else -1.0
    cx = sign * pw / 2.0
    _box(door, (pw, pt, ph), (cx, -pt / 2.0 - 0.002, 0.0), mats["front"], "door_panel")
    # Pull near the free edge — embed slightly into panel front face so no gap.
    handle_x = sign * (pw - 0.030)
    _box(
        door,
        (0.016, 0.014, min(0.08, ph * 0.24)),
        (handle_x, -pt - 0.005, 0.0),
        mats["hardware"],
        "door_pull",
    )
    # Hinge leaves on the hinge edge (back face of panel).
    for k, z in enumerate((-ph / 2.0 + 0.10, ph / 2.0 - 0.02)):
        _box(
            door,
            (0.020, 0.010, 0.040),
            (sign * 0.006, -0.006, z),
            mats["hardware"],
            f"door_hinge_leaf_{k}",
        )


def _build_bifold_outer_leaf(leaf, r, mats, *, side: int) -> None:
    """Outer bifold leaf. side=0 → left pair (hinge on LEFT), side=1 → right pair (hinge on RIGHT)."""
    pw = _bifold_panel_width(r)
    ph = _door_panel_height(r)
    pt = 0.018
    sign = 1.0 if side == 0 else -1.0
    cx = sign * pw / 2.0
    _box(leaf, (pw, pt, ph), (cx, -pt / 2.0 - 0.002, 0.0), mats["front"], "leaf_panel")
    # Hinge leaves
    for k, z in enumerate((-ph / 2.0 + 0.10, ph / 2.0 - 0.02)):
        _box(
            leaf,
            (0.018, 0.010, 0.036),
            (sign * 0.006, -0.006, z),
            mats["hardware"],
            f"leaf_hinge_carcass_{k}",
        )
    # Inner hinge (on the FREE end of outer leaf, where inner will attach)
    inner_hinge_x = sign * pw
    for k, z in enumerate((-ph / 2.0 + 0.10, ph / 2.0 - 0.02)):
        _box(
            leaf,
            (0.018, 0.010, 0.036),
            (inner_hinge_x - sign * 0.006, -0.006, z),
            mats["hardware"],
            f"leaf_hinge_inner_{k}",
        )


def _build_bifold_inner_leaf(leaf, r, mats, *, side: int) -> None:
    """Inner bifold leaf. Origin at the hinge on outer leaf's free edge."""
    pw = _bifold_panel_width(r)
    ph = _door_panel_height(r)
    pt = 0.018
    sign = 1.0 if side == 0 else -1.0
    # inner extends in +X direction from hinge (same sign convention as outer)
    cx = sign * pw / 2.0
    _box(leaf, (pw, pt, ph), (cx, -pt / 2.0 - 0.002, 0.0), mats["front"], "inner_leaf_panel")
    # Hinge leaves back onto outer
    for k, z in enumerate((-ph / 2.0 + 0.10, ph / 2.0 - 0.02)):
        _box(
            leaf,
            (0.018, 0.010, 0.036),
            (sign * 0.006, -0.006, z),
            mats["hardware"],
            f"inner_hinge_leaf_{k}",
        )
    # Small pull embedded into panel front face
    _box(
        leaf,
        (0.014, 0.012, 0.040),
        (sign * (pw - 0.020), -pt - 0.004, 0.0),
        mats["hardware"],
        "inner_pull",
    )


def _build_drop_front_flap(door, r, mats, *, i: int) -> None:
    """Drop-front media flap. Origin at bottom hinge; panel extends up (+Z)."""
    pw = _drop_front_panel_width(r)
    ph = _door_panel_height(r)
    pt = 0.018
    _box(door, (pw, pt, ph), (0.0, -pt / 2.0 - 0.002, ph / 2.0), mats["front"], "flap_panel")
    # Small top lip / handle — embed into panel so no gap.
    _box(
        door,
        (pw * 0.5, 0.014, 0.016),
        (0.0, -pt - 0.005, ph - 0.020),
        mats["hardware"],
        "flap_pull",
    )
    # Hinge leaves at bottom (back face). Sit at the joint origin plane and
    # extend across the mating rail line.
    for k, xoff in enumerate((-pw * 0.30, pw * 0.30)):
        _box(
            door,
            (0.050, 0.024, 0.020),
            (xoff, 0.004, 0.012),
            mats["hardware"],
            f"flap_hinge_leaf_{k}",
        )


def _build_push_flap(door, r, mats, *, i: int) -> None:
    """Push-to-open bottom-hinged flap. Origin at bottom hinge; panel extends up +Z."""
    pw = _push_flap_panel_width(r)
    ph = _door_panel_height(r)
    pt = 0.018
    _box(door, (pw, pt, ph), (0.0, -pt / 2.0 - 0.002, ph / 2.0), mats["front"], "push_flap_panel")
    # No visible pull (push-to-open) — small integrated finger notch, embedded.
    _box(
        door,
        (pw * 0.30, 0.014, 0.010),
        (0.0, -pt - 0.003, ph - 0.014),
        mats["trim"],
        "push_notch",
    )
    # Bottom hinge leaves
    for k, xoff in enumerate((-pw * 0.30, pw * 0.30)):
        _box(
            door,
            (0.045, 0.024, 0.018),
            (xoff, 0.004, 0.010),
            mats["hardware"],
            f"push_hinge_leaf_{k}",
        )


def _build_drawer(drawer, r, mats) -> None:
    """Drawer part. Origin at joint origin (front face of carcass at drawer z).

    Front panel outer face at y=0; box extends into +Y (into carcass) so that
    axis (0,-1,0) motion translates the drawer OUTWARD in world -Y.
    """
    ft = 0.018
    fw = _drawer_front_width(r)
    fh = _drawer_front_height(r)
    bd = _drawer_box_depth(r)
    bh = fh * 0.75

    _box(drawer, (fw, ft, fh), (0.0, ft / 2.0, 0.0), mats["front"], "drawer_front")
    box_y_center = ft + bd / 2.0
    for sign, name in ((1.0, "box_side_right"), (-1.0, "box_side_left")):
        _box(
            drawer,
            (0.012, bd, bh),
            (sign * (fw / 2.0 - 0.010), box_y_center, 0.0),
            mats["dark"],
            name,
        )
    _box(
        drawer,
        (fw - 0.028, 0.010, bh),
        (0.0, ft + bd - 0.005, 0.0),
        mats["dark"],
        "box_back",
    )
    _box(
        drawer,
        (fw - 0.028, bd - 0.020, 0.010),
        (0.0, box_y_center, -bh / 2.0 + 0.005),
        mats["dark"],
        "box_bottom",
    )
    # Pull bar embedded slightly into drawer front (no gap in y).
    _box(
        drawer,
        (fw * 0.4, 0.012, 0.014),
        (0.0, -0.003, fh * 0.25),
        mats["hardware"],
        "drawer_pull",
    )


def _build_guard_door(door, r, mats) -> None:
    """Single guard door for open_cubbies closure. Hinge on RIGHT edge (i=1 style)."""
    pw = _open_cubbies_guard_panel_width(r)
    ph = _door_panel_height(r)
    pt = 0.018
    sign = -1.0  # hinge on RIGHT, panel extends -X
    cx = sign * pw / 2.0
    _box(door, (pw, pt, ph), (cx, -pt / 2.0 - 0.002, 0.0), mats["front"], "guard_panel")
    _box(
        door,
        (0.016, 0.014, min(0.08, ph * 0.24)),
        (sign * (pw - 0.030), -pt - 0.005, 0.0),
        mats["hardware"],
        "guard_pull",
    )
    for k, z in enumerate((-ph / 2.0 + 0.10, ph / 2.0 - 0.02)):
        _box(
            door,
            (0.020, 0.010, 0.040),
            (sign * 0.006, -0.006, z),
            mats["hardware"],
            f"guard_hinge_leaf_{k}",
        )


# ---------------------------------------------------------------------------
# Top-level build
# ---------------------------------------------------------------------------
def build_tv_cabinet(
    config: TVCabinetConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or TVCabinetConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.palette_style]
    mats = {
        role: model.material(f"tv_{role}_{r.palette_style}", rgba=palette[role])
        for role in ("body", "front", "trim", "hardware", "dark", "grain")
    }

    carcass = model.part("carcass")
    _carcass_shell(carcass, r, mats)
    _support_visuals(carcass, r, mats)
    _emit_closure_hardware(carcass, r, mats)

    # rough inertial
    carcass.inertial = Inertial.from_geometry(
        Box((r.carcass_width, r.carcass_depth, r.carcass_height + r.support_height)),
        mass=52.0,
        origin=Origin(xyz=(0.0, 0.0, r.carcass_floor_z + r.carcass_height / 2.0)),
    )

    front_y = -r.carcass_depth / 2.0 + 0.003

    if r.closure == "side_hinged_doors":
        for i in range(r.child_count):
            door = model.part(f"door_{i}")
            _build_hinged_door_part(door, r, mats, i=i)
            pw = _door_panel_width_each(r)
            ph = _door_panel_height(r)
            door.inertial = Inertial.from_geometry(
                Box((pw, 0.020, ph)),
                mass=3.0,
                origin=Origin(xyz=(0.0, 0.0, 0.0)),
            )
            hinge_x = _side_hinged_hinge_x(r, i)
            hz = (
                r.carcass_floor_z
                + r.bottom_slab_thickness
                + (r.carcass_height - r.bottom_slab_thickness - r.top_slab_thickness) / 2.0
            )
            axis_sign = _side_hinged_axis_sign(i)  # +1 for left-hinge, -1 for right-hinge
            mating = MatingContract(
                parent_face_geometry=f"hinge_knuckle_{i}_0",
                parent_face_side="negative_y",
                child_face_geometry="door_hinge_leaf_0",
                child_face_side="positive_y",
                contact_tol=0.030,
            )
            model.articulation(
                f"carcass_to_door_{i}",
                ArticulationType.REVOLUTE,
                parent=carcass,
                child=door,
                origin=Origin(xyz=(hinge_x, front_y, hz)),
                axis=(0.0, 0.0, axis_sign),
                motion_limits=MotionLimits(
                    lower=0.0,
                    upper=r.door_open_angle,
                    effort=12.0,
                    velocity=1.5,
                ),
                mating=mating,
                meta={"positive_motion": "side-hinged door swings outward toward -Y"},
            )

    elif r.closure == "bifold_doors":
        for side in (0, 1):
            outer_name = f"door_outer_{side}"
            inner_name = f"door_inner_{side}"
            outer = model.part(outer_name)
            _build_bifold_outer_leaf(outer, r, mats, side=side)
            pw = _bifold_panel_width(r)
            ph = _door_panel_height(r)
            outer.inertial = Inertial.from_geometry(
                Box((pw, 0.020, ph)),
                mass=2.5,
                origin=Origin(xyz=(0.0, 0.0, 0.0)),
            )
            hinge_x = _bifold_outer_hinge_x(r, side)
            hz = (
                r.carcass_floor_z
                + r.bottom_slab_thickness
                + (r.carcass_height - r.bottom_slab_thickness - r.top_slab_thickness) / 2.0
            )
            # side=0 (LEFT hinge, panel extends +X): axis -Z opens toward -Y.
            # side=1 (RIGHT hinge, panel extends -X): axis +Z opens toward -Y.
            axis_sign = -1.0 if side == 0 else 1.0
            mating_outer = MatingContract(
                parent_face_geometry=f"bifold_hinge_{side}_0",
                parent_face_side="negative_y",
                child_face_geometry="leaf_hinge_carcass_0",
                child_face_side="positive_y",
                contact_tol=0.030,
            )
            model.articulation(
                f"carcass_to_{outer_name}",
                ArticulationType.REVOLUTE,
                parent=carcass,
                child=outer,
                origin=Origin(xyz=(hinge_x, front_y, hz)),
                axis=(0.0, 0.0, axis_sign),
                motion_limits=MotionLimits(
                    lower=0.0,
                    upper=r.door_open_angle,
                    effort=8.0,
                    velocity=1.5,
                ),
                mating=mating_outer,
                meta={"positive_motion": "bifold outer leaf swings outward toward -Y"},
            )
            inner = model.part(inner_name)
            _build_bifold_inner_leaf(inner, r, mats, side=side)
            inner.inertial = Inertial.from_geometry(
                Box((pw, 0.020, ph)),
                mass=2.0,
                origin=Origin(xyz=(0.0, 0.0, 0.0)),
            )
            # Inner hinge origin in OUTER's local frame: at the free end of outer.
            # In outer's frame, hinge is at x=sign*pw (free end), y=-0.006, z=0.
            inner_axis_sign = -axis_sign  # opposite direction of fold
            mating_inner = MatingContract(
                parent_face_geometry="leaf_hinge_inner_0",
                parent_face_side="negative_y",
                child_face_geometry="inner_hinge_leaf_0",
                child_face_side="positive_y",
                contact_tol=0.030,
            )
            outer_free_x = (1.0 if side == 0 else -1.0) * pw
            model.articulation(
                f"{outer_name}_to_{inner_name}",
                ArticulationType.REVOLUTE,
                parent=outer,
                child=inner,
                origin=Origin(xyz=(outer_free_x, -0.006, 0.0)),
                axis=(0.0, 0.0, inner_axis_sign),
                motion_limits=MotionLimits(
                    lower=0.0,
                    upper=r.door_open_angle * 0.9,
                    effort=6.0,
                    velocity=1.5,
                ),
                mating=mating_inner,
                meta={"positive_motion": "bifold inner leaf folds against outer"},
            )

    elif r.closure == "drop_front_flap":
        for i in range(2):
            door = model.part(f"door_{i}")
            _build_drop_front_flap(door, r, mats, i=i)
            pw = _drop_front_panel_width(r)
            ph = _door_panel_height(r)
            door.inertial = Inertial.from_geometry(
                Box((pw, 0.020, ph)),
                mass=3.0,
                origin=Origin(xyz=(0.0, 0.0, ph / 2.0)),
            )
            cx = _drop_front_center_x(r, i)
            hz = r.carcass_floor_z + r.bottom_slab_thickness + 0.014
            mating = MatingContract(
                parent_face_geometry=f"drop_front_rail_{i}",
                parent_face_side="negative_y",
                child_face_geometry="flap_hinge_leaf_0",
                child_face_side="positive_y",
                contact_tol=0.030,
            )
            # Axis +X → positive angle drops top of panel toward -Y (front-down).
            model.articulation(
                f"carcass_to_door_{i}",
                ArticulationType.REVOLUTE,
                parent=carcass,
                child=door,
                origin=Origin(xyz=(cx, front_y, hz)),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(
                    lower=0.0,
                    upper=r.door_open_angle,
                    effort=15.0,
                    velocity=1.2,
                ),
                mating=mating,
                meta={"positive_motion": "drop-front flap drops top edge toward user (-Y)"},
            )

    elif r.closure == "push_flap_row":
        for i in range(r.child_count):
            door = model.part(f"door_{i}")
            _build_push_flap(door, r, mats, i=i)
            pw = _push_flap_panel_width(r)
            ph = _door_panel_height(r)
            door.inertial = Inertial.from_geometry(
                Box((pw, 0.020, ph)),
                mass=2.5,
                origin=Origin(xyz=(0.0, 0.0, ph / 2.0)),
            )
            cx = _push_flap_center_x(r, i)
            hz = r.carcass_floor_z + r.bottom_slab_thickness + 0.014
            mating = MatingContract(
                parent_face_geometry=f"push_flap_rail_{i}",
                parent_face_side="negative_y",
                child_face_geometry="push_hinge_leaf_0",
                child_face_side="positive_y",
                contact_tol=0.030,
            )
            model.articulation(
                f"carcass_to_door_{i}",
                ArticulationType.REVOLUTE,
                parent=carcass,
                child=door,
                origin=Origin(xyz=(cx, front_y, hz)),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(
                    lower=0.0,
                    upper=r.door_open_angle,
                    effort=12.0,
                    velocity=1.5,
                ),
                mating=mating,
                meta={"positive_motion": "push flap tips top forward-downward toward -Y"},
            )

    elif r.closure == "drawer_bank":
        for i in range(r.child_count):
            drawer = model.part(f"drawer_{i}")
            _build_drawer(drawer, r, mats)
            fw = _drawer_front_width(r)
            fh = _drawer_front_height(r)
            bd = _drawer_box_depth(r)
            drawer.inertial = Inertial.from_geometry(
                Box((fw, bd, fh)),
                mass=3.5,
                origin=Origin(xyz=(0.0, bd / 2.0, 0.0)),
            )
            cz = _drawer_center_z(r, i)
            mating = MatingContract(
                parent_face_geometry=f"drawer_slide_rail_{i}",
                parent_face_side="negative_y",
                child_face_geometry="drawer_front",
                child_face_side="positive_y",
                contact_tol=0.030,
            )
            model.articulation(
                f"carcass_to_drawer_{i}",
                ArticulationType.PRISMATIC,
                parent=carcass,
                child=drawer,
                origin=Origin(xyz=(0.0, front_y, cz)),
                axis=(0.0, -1.0, 0.0),
                motion_limits=MotionLimits(
                    lower=0.0,
                    upper=r.drawer_travel,
                    effort=80.0,
                    velocity=0.32,
                ),
                mating=mating,
                meta={"positive_motion": "drawer extends toward user (-Y)"},
            )

    elif r.closure == "open_cubbies":
        # Add a single guard door (Rule 5 coverage — the template needs a
        # non-FIXED joint even in open_cubbies).
        door = model.part("guard_door")
        _build_guard_door(door, r, mats)
        pw = _open_cubbies_guard_panel_width(r)
        ph = _door_panel_height(r)
        door.inertial = Inertial.from_geometry(
            Box((pw, 0.020, ph)),
            mass=2.0,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
        )
        hinge_x = _open_cubbies_guard_hinge_x(r)
        hz = (
            r.carcass_floor_z
            + r.bottom_slab_thickness
            + (r.carcass_height - r.bottom_slab_thickness - r.top_slab_thickness) / 2.0
        )
        mating = MatingContract(
            parent_face_geometry="guard_hinge_0",
            parent_face_side="negative_y",
            child_face_geometry="guard_hinge_leaf_0",
            child_face_side="positive_y",
            contact_tol=0.030,
        )
        model.articulation(
            "carcass_to_guard_door",
            ArticulationType.REVOLUTE,
            parent=carcass,
            child=door,
            origin=Origin(xyz=(hinge_x, front_y, hz)),
            axis=(0.0, 0.0, 1.0),  # RIGHT hinge, panel extends -X → axis +Z opens toward -Y
            motion_limits=MotionLimits(
                lower=0.0,
                upper=r.door_open_angle,
                effort=10.0,
                velocity=1.5,
            ),
            mating=mating,
            meta={"positive_motion": "guard door swings outward toward -Y"},
        )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_tv_cabinet(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_tv_cabinet(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests / allowances (Rule 2, Rule 5)
# ---------------------------------------------------------------------------
def _iter_carcass_neighbors_for_door(r: ResolvedTVCabinetConfig) -> list[str]:
    """List of carcass visual names that a swinging door panel may graze."""
    names = [
        "bottom_slab",
        "top_slab",
        "back_panel",
        "side_right",
        "side_left",
        "front_bottom_rail",
        "front_top_rail",
    ]
    return names


def run_tv_cabinet_tests(
    object_model: ArticulatedObject,
    config: TVCabinetConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("carcass part present", "carcass" in part_names)
    carcass = object_model.get_part("carcass")

    # Topology checks per closure.
    if r.closure == "side_hinged_doors":
        for i in range(r.child_count):
            j_name = f"carcass_to_door_{i}"
            ctx.check(f"{j_name} present", j_name in joint_names)
            j = object_model.get_articulation(j_name)
            ctx.check(
                f"{j_name} REVOLUTE about Z",
                j.articulation_type == ArticulationType.REVOLUTE
                and abs(abs(j.axis[2]) - 1.0) < 1e-6,
                details=f"axis={j.axis}",
            )
    elif r.closure == "bifold_doors":
        for side in (0, 1):
            outer = f"carcass_to_door_outer_{side}"
            inner = f"door_outer_{side}_to_door_inner_{side}"
            for jn in (outer, inner):
                ctx.check(f"{jn} present", jn in joint_names)
                j = object_model.get_articulation(jn)
                ctx.check(
                    f"{jn} REVOLUTE about Z",
                    j.articulation_type == ArticulationType.REVOLUTE
                    and abs(abs(j.axis[2]) - 1.0) < 1e-6,
                )
    elif r.closure == "drop_front_flap":
        for i in range(2):
            j_name = f"carcass_to_door_{i}"
            ctx.check(f"{j_name} present", j_name in joint_names)
            j = object_model.get_articulation(j_name)
            ctx.check(
                f"{j_name} REVOLUTE about X",
                j.articulation_type == ArticulationType.REVOLUTE
                and abs(abs(j.axis[0]) - 1.0) < 1e-6,
            )
    elif r.closure == "push_flap_row":
        for i in range(r.child_count):
            j_name = f"carcass_to_door_{i}"
            ctx.check(f"{j_name} present", j_name in joint_names)
            j = object_model.get_articulation(j_name)
            ctx.check(
                f"{j_name} REVOLUTE about X",
                j.articulation_type == ArticulationType.REVOLUTE
                and abs(abs(j.axis[0]) - 1.0) < 1e-6,
            )
    elif r.closure == "drawer_bank":
        for i in range(r.child_count):
            j_name = f"carcass_to_drawer_{i}"
            ctx.check(f"{j_name} present", j_name in joint_names)
            j = object_model.get_articulation(j_name)
            ctx.check(
                f"{j_name} PRISMATIC axis Y",
                j.articulation_type == ArticulationType.PRISMATIC
                and abs(abs(j.axis[1]) - 1.0) < 1e-6,
            )
    else:  # open_cubbies
        ctx.check(
            "guard door present",
            "carcass_to_guard_door" in joint_names,
        )

    # ---- Element-scoped allowances (captured hinges + drawer nesting) ------
    if r.closure == "side_hinged_doors":
        for i in range(r.child_count):
            door = object_model.get_part(f"door_{i}")
            # captured hinge knuckles
            for k in range(2):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=f"hinge_knuckle_{i}_{k}",
                    elem_b=f"door_hinge_leaf_{k}",
                    reason="captured hinge knuckle nests the door leaf",
                )
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=f"hinge_knuckle_{i}_{k}",
                    elem_b="door_panel",
                    reason="hinge knuckle sits at the door panel edge line",
                )
            # panel sweeping past neighbors
            for name in _iter_carcass_neighbors_for_door(r):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=name,
                    elem_b="door_panel",
                    reason="hinged door panel sweeps past carcass shell during opening",
                )
                for k in range(2):
                    ctx.allow_overlap(
                        carcass,
                        door,
                        elem_a=name,
                        elem_b=f"door_hinge_leaf_{k}",
                        reason="hinge leaf sweeps past carcass shell",
                    )
        # adjacent doors share the front opening plane
        for a in range(r.child_count):
            for b in range(a + 1, r.child_count):
                ctx.allow_overlap(
                    object_model.get_part(f"door_{a}"),
                    object_model.get_part(f"door_{b}"),
                    reason="adjacent side-hinged doors share opening plane; operated in sequence",
                )
    elif r.closure == "bifold_doors":
        for side in (0, 1):
            outer = object_model.get_part(f"door_outer_{side}")
            inner = object_model.get_part(f"door_inner_{side}")
            # captured carcass-to-outer hinge
            for k in range(2):
                ctx.allow_overlap(
                    carcass,
                    outer,
                    elem_a=f"bifold_hinge_{side}_{k}",
                    elem_b=f"leaf_hinge_carcass_{k}",
                    reason="captured bifold outer hinge",
                )
                ctx.allow_overlap(
                    carcass,
                    outer,
                    elem_a=f"bifold_hinge_{side}_{k}",
                    elem_b="leaf_panel",
                    reason="hinge knuckle at outer leaf edge",
                )
                ctx.allow_overlap(
                    outer,
                    inner,
                    elem_a=f"leaf_hinge_inner_{k}",
                    elem_b=f"inner_hinge_leaf_{k}",
                    reason="captured outer-to-inner bifold hinge",
                )
                ctx.allow_overlap(
                    outer,
                    inner,
                    elem_a=f"leaf_hinge_inner_{k}",
                    elem_b="inner_leaf_panel",
                    reason="inner hinge knuckle at inner leaf edge",
                )
            # panel-carcass grazing
            for name in _iter_carcass_neighbors_for_door(r):
                ctx.allow_overlap(
                    carcass,
                    outer,
                    elem_a=name,
                    elem_b="leaf_panel",
                    reason="bifold outer leaf sweeps past carcass shell",
                )
                ctx.allow_overlap(
                    carcass,
                    inner,
                    elem_a=name,
                    elem_b="inner_leaf_panel",
                    reason="bifold inner leaf sweeps past carcass shell",
                )
                for k in range(2):
                    ctx.allow_overlap(
                        carcass,
                        outer,
                        elem_a=name,
                        elem_b=f"leaf_hinge_carcass_{k}",
                        reason="bifold outer hinge leaf sweeps past carcass shell",
                    )
                    ctx.allow_overlap(
                        carcass,
                        outer,
                        elem_a=name,
                        elem_b=f"leaf_hinge_inner_{k}",
                        reason="bifold outer inner-hinge leaf sweeps past carcass shell",
                    )
                    ctx.allow_overlap(
                        carcass,
                        inner,
                        elem_a=name,
                        elem_b=f"inner_hinge_leaf_{k}",
                        reason="bifold inner hinge leaf sweeps past carcass shell",
                    )
            # Outer ↔ inner leaves are a coupled bifold mechanism (real-world
            # design has physical linkage keeping them synchronised). Sampled
            # poses that exercise inner independently of outer are unphysical
            # combinations — declare inner ↔ carcass + outer ↔ inner overlaps
            # as sequenced motion.
            ctx.allow_overlap(
                outer,
                inner,
                reason=(
                    "bifold outer + inner leaves are a coupled mechanism; "
                    "independent-DOF sampled combinations are unphysical"
                ),
            )
            ctx.allow_overlap(
                carcass,
                inner,
                reason=(
                    "bifold inner leaf's independent-DOF motion range is only "
                    "physical when outer is open; sampled cross-DOF combos with "
                    "outer closed are unphysical (coupled mechanism)"
                ),
            )
        # left ↔ right bifold pairs share the opening plane
        left_outer = object_model.get_part("door_outer_0")
        right_outer = object_model.get_part("door_outer_1")
        left_inner = object_model.get_part("door_inner_0")
        right_inner = object_model.get_part("door_inner_1")
        for a, b in (
            (left_outer, right_outer),
            (left_inner, right_inner),
            (left_outer, right_inner),
            (right_outer, left_inner),
        ):
            ctx.allow_overlap(a, b, reason="bifold pairs share opening plane; sequenced operation")
    elif r.closure == "drop_front_flap":
        for i in range(2):
            door = object_model.get_part(f"door_{i}")
            for k in range(2):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=f"drop_front_rail_{i}",
                    elem_b=f"flap_hinge_leaf_{k}",
                    reason="drop-front bottom hinge leaf rides on the rail",
                )
            for name in _iter_carcass_neighbors_for_door(r):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=name,
                    elem_b="flap_panel",
                    reason="drop-front flap sweeps past carcass shell",
                )
                for k in range(2):
                    ctx.allow_overlap(
                        carcass,
                        door,
                        elem_a=name,
                        elem_b=f"flap_hinge_leaf_{k}",
                        reason="flap hinge leaf sweeps past carcass shell",
                    )
        # adjacent flaps share the front opening plane
        ctx.allow_overlap(
            object_model.get_part("door_0"),
            object_model.get_part("door_1"),
            reason="adjacent drop-front flaps share the opening plane",
        )
    elif r.closure == "push_flap_row":
        for i in range(r.child_count):
            door = object_model.get_part(f"door_{i}")
            for k in range(2):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=f"push_flap_rail_{i}",
                    elem_b=f"push_hinge_leaf_{k}",
                    reason="push-flap bottom hinge leaf rides on the rail",
                )
            for name in _iter_carcass_neighbors_for_door(r):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=name,
                    elem_b="push_flap_panel",
                    reason="push flap sweeps past carcass shell",
                )
                for k in range(2):
                    ctx.allow_overlap(
                        carcass,
                        door,
                        elem_a=name,
                        elem_b=f"push_hinge_leaf_{k}",
                        reason="push hinge leaf sweeps past carcass shell",
                    )
        # adjacent flaps
        for a in range(r.child_count):
            for b in range(a + 1, r.child_count):
                ctx.allow_overlap(
                    object_model.get_part(f"door_{a}"),
                    object_model.get_part(f"door_{b}"),
                    reason="adjacent push flaps share front opening; sequenced operation",
                )
    elif r.closure == "drawer_bank":
        for i in range(r.child_count):
            drawer = object_model.get_part(f"drawer_{i}")
            ctx.allow_overlap(
                carcass,
                drawer,
                reason="drawer box nests inside carcass interior while closed",
            )
        # adjacent drawer fronts share opening plane
        for i in range(r.child_count - 1):
            ctx.allow_overlap(
                object_model.get_part(f"drawer_{i}"),
                object_model.get_part(f"drawer_{i + 1}"),
                reason="stacked drawer fronts share the front opening plane",
            )
    else:  # open_cubbies (guard door)
        door = object_model.get_part("guard_door")
        for k in range(2):
            ctx.allow_overlap(
                carcass,
                door,
                elem_a=f"guard_hinge_{k}",
                elem_b=f"guard_hinge_leaf_{k}",
                reason="captured guard hinge knuckle",
            )
            ctx.allow_overlap(
                carcass,
                door,
                elem_a=f"guard_hinge_{k}",
                elem_b="guard_panel",
                reason="hinge knuckle at guard panel edge",
            )
        for name in _iter_carcass_neighbors_for_door(r):
            ctx.allow_overlap(
                carcass,
                door,
                elem_a=name,
                elem_b="guard_panel",
                reason="guard door sweeps past carcass shell",
            )
            for k in range(2):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=name,
                    elem_b=f"guard_hinge_leaf_{k}",
                    reason="guard hinge leaf sweeps past carcass shell",
                )
        # guard door grazes the last cubby divider
        if r.cubby_dividers_x:
            last_div = f"cubby_divider_{len(r.cubby_dividers_x) - 1}"
            ctx.allow_overlap(
                carcass,
                door,
                elem_a=last_div,
                elem_b="guard_panel",
                reason="guard door sits over the rightmost cubby divider",
            )
            for k in range(2):
                ctx.allow_overlap(
                    carcass,
                    door,
                    elem_a=last_div,
                    elem_b=f"guard_hinge_leaf_{k}",
                    reason="guard hinge leaf near rightmost cubby divider",
                )

    # ---- Targeted pose checks (Rule 5) ------------------------------------
    if r.closure == "drawer_bank" and r.child_count > 0:
        j0 = object_model.get_articulation("carcass_to_drawer_0")
        drawer0 = object_model.get_part("drawer_0")
        rest = ctx.part_world_position(drawer0)
        with ctx.pose({j0: j0.motion_limits.upper}):
            extended = ctx.part_world_position(drawer0)
        ctx.check(
            "drawer 0 extends toward user (-Y)",
            rest is not None and extended is not None and extended[1] < rest[1] - 0.05,
            details=f"rest={rest}, extended={extended}",
        )
    elif r.closure == "side_hinged_doors":
        j0 = object_model.get_articulation("carcass_to_door_0")
        door0 = object_model.get_part("door_0")
        closed_aabb = ctx.part_world_aabb(door0)
        with ctx.pose({j0: j0.motion_limits.upper * 0.6}):
            open_aabb = ctx.part_world_aabb(door0)
        ctx.check(
            "hinged door swings outward toward -Y",
            closed_aabb is not None
            and open_aabb is not None
            and (open_aabb[0][1] < closed_aabb[0][1] - 0.02),
            details=f"closed={closed_aabb}, open={open_aabb}",
        )
    elif r.closure == "bifold_doors":
        j0 = object_model.get_articulation("carcass_to_door_outer_0")
        outer0 = object_model.get_part("door_outer_0")
        closed_aabb = ctx.part_world_aabb(outer0)
        with ctx.pose({j0: j0.motion_limits.upper * 0.6}):
            open_aabb = ctx.part_world_aabb(outer0)
        ctx.check(
            "bifold outer leaf swings outward toward -Y",
            closed_aabb is not None
            and open_aabb is not None
            and (open_aabb[0][1] < closed_aabb[0][1] - 0.02),
            details=f"closed={closed_aabb}, open={open_aabb}",
        )
    elif r.closure in ("drop_front_flap", "push_flap_row"):
        j0 = object_model.get_articulation("carcass_to_door_0")
        door0 = object_model.get_part("door_0")
        closed_aabb = ctx.part_world_aabb(door0)
        with ctx.pose({j0: j0.motion_limits.upper * 0.6}):
            open_aabb = ctx.part_world_aabb(door0)
        ctx.check(
            "flap drops top edge toward user (-Y)",
            closed_aabb is not None
            and open_aabb is not None
            and (open_aabb[0][1] < closed_aabb[0][1] - 0.02),
            details=f"closed={closed_aabb}, open={open_aabb}",
        )
    elif r.closure == "open_cubbies":
        j0 = object_model.get_articulation("carcass_to_guard_door")
        door0 = object_model.get_part("guard_door")
        closed_aabb = ctx.part_world_aabb(door0)
        with ctx.pose({j0: j0.motion_limits.upper * 0.6}):
            open_aabb = ctx.part_world_aabb(door0)
        ctx.check(
            "guard door swings outward toward -Y",
            closed_aabb is not None
            and open_aabb is not None
            and (open_aabb[0][1] < closed_aabb[0][1] - 0.02),
            details=f"closed={closed_aabb}, open={open_aabb}",
        )

    # ---- Baseline sampled-pose motion QC + origin-on-geometry (Rule 5) ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = [
    "TVCabinetConfig",
    "ResolvedTVCabinetConfig",
    "build_tv_cabinet",
    "build_seeded_tv_cabinet",
    "config_from_seed",
    "resolve_config",
    "run_tv_cabinet_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
]
