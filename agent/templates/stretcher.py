# SPDX-License-Identifier: Apache-2.0

"""Stretcher procedural template (modular).

Emergency-equipment stretcher family. Modular, parallel-children pattern with a
single ``deck_frame`` root; undercarriage / restraint / casters hang off it.

Slots (see specs_modular_v1/stretcher.md):
  A. deck        (③ Primary Form Family + patient surface, ROOT):
                 padded_cot / canvas_cot / basket_shell / spine_board
  B. undercarriage (② lift mechanism + base + N casters):
                 scissor_wheeled / foldleg_wheeled / telescoping_wheeled /
                 carry_poles / bare_feet
  C. restraint   (① side restraint):
                 folding_rails / strap_harness / immobilizer_blocks
  + caster_count multiplicity axis (N in {2,4,6}).

Sources adapted (rec:model.py:Lx-Ly):
  o1 rec_...stretcher_39031c58 — lower_carriage/scissor/height_slide/casters,
     backrest, folding side rails, segmented foam pads (box/cylinder tube frame).
  o2 rec_...stretcher_c7b79ba9 — deck_frame root, folding legs, casters, backrest.
  rec_stretcher_var_telescoping_legs — telescoping-leg PRISMATIC.
  rec_stretcher_var_pole_canvas — carry poles + folding spreaders REVOLUTE.
  rec_stretcher_var_basket_litter — Stokes basket clamshell fold REVOLUTE.
  rec_stretcher_var_spine_board — flat HDPE board + hinged immobilizer blocks.
  rec_stretcher_var_canvas_deck — tensioned canvas surface.
  rec_stretcher_var_strap_harness — cross-strap restraint replacing rails.
  rec_stretcher_var_casters_two / _six — caster multiplicity.

AUTHORING §A compliance:
  Rule 1: every non-articulating detail (pads, straps, seams, brake decals, rope
          handles, foot stubs) is a parent.visual(...), never a FIXED part.
  Rule 2: every non-FIXED joint here is a captured pin / sliding rail (hinge tube
          in socket, axle in hub, telescoping tube in sleeve) — mating omitted and
          grandfathered with element-scoped allow_overlap (matches the sources).
  Rule 3: structure derived from the declared 5-star sources; cheap Cylinder/Box
          tube frame + o1 cylinder casters keep the §7.5 compile budget; basket /
          board keep their Mesh primitives (never downgraded).
  Rule 5: run_tests calls fail_if_parts_overlap_in_sampled_poses + targeted
          ctx.pose(...) per mechanism.
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
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    MotionLimits,
    Origin,
    PerforatedPanelGeometry,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    superellipse_profile,
    tube_from_spline_points,
)

__modular__ = True

# --------------------------------------------------------------------------- #
# Slot enums + candidate tuples
# --------------------------------------------------------------------------- #
Deck = Literal["padded_cot", "canvas_cot", "basket_shell", "spine_board"]
Undercarriage = Literal[
    "scissor_wheeled",
    "foldleg_wheeled",
    "telescoping_wheeled",
    "carry_poles",
    "bare_feet",
]
Restraint = Literal["folding_rails", "strap_harness", "immobilizer_blocks"]
PaletteStyle = Literal[
    "safety_orange",
    "safety_yellow",
    "rescue_orange",
    "olive_drab",
    "ems_navy",
    "hi_vis_lime",
]

DECKS: tuple[Deck, ...] = ("padded_cot", "canvas_cot", "basket_shell", "spine_board")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "safety_orange",
    "safety_yellow",
    "rescue_orange",
    "olive_drab",
    "ems_navy",
    "hi_vis_lime",
)

# Compatibility gating (spec §9). Legal undercarriage / restraint per deck.
_UNDER_FOR_DECK: dict[str, tuple[str, ...]] = {
    "padded_cot": ("scissor_wheeled", "foldleg_wheeled", "telescoping_wheeled", "carry_poles"),
    "canvas_cot": ("scissor_wheeled", "foldleg_wheeled", "telescoping_wheeled", "carry_poles"),
    # a head-only basket deck cannot anchor head-to-foot legs/carriage; the
    # Stokes hull rests on the ground.
    "basket_shell": ("bare_feet",),
    "spine_board": ("bare_feet", "carry_poles"),
}
_RESTRAINT_FOR_DECK: dict[str, tuple[str, ...]] = {
    "padded_cot": ("folding_rails", "strap_harness"),
    "canvas_cot": ("folding_rails", "strap_harness"),
    "basket_shell": ("strap_harness",),
    "spine_board": ("immobilizer_blocks",),
}
_WHEELED = ("scissor_wheeled", "foldleg_wheeled", "telescoping_wheeled")
_CARRIAGE_WHEELED = ("scissor_wheeled", "telescoping_wheeled")
_HAS_BACKREST = ("padded_cot", "canvas_cot")

# caster multiplicity domain (spec §8): carriage undercarriages take N in {2,4,6};
# foldleg naturally takes 2 (foot leg) or 4 (both legs).
_CARRIAGE_N_CHOICES = (4, 6)
_CARRIAGE_N_WEIGHTS = (0.68, 0.32)
_FOLDLEG_N_CHOICES = (2, 4)
_FOLDLEG_N_WEIGHTS = (0.25, 0.75)

# --------------------------------------------------------------------------- #
# Palettes (6 colorways, spec §8.5 ⑥). Keys: frame / surface / strap / wheel /
# hub / release.
# --------------------------------------------------------------------------- #
PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "safety_orange": {
        "frame": (0.72, 0.74, 0.74, 1.0),
        "surface": (0.95, 0.22, 0.06, 1.0),
        "strap": (0.02, 0.02, 0.02, 1.0),
        "wheel": (0.02, 0.02, 0.02, 1.0),
        "hub": (0.50, 0.52, 0.52, 1.0),
        "release": (0.90, 0.02, 0.01, 1.0),
    },
    "safety_yellow": {
        "frame": (1.0, 0.74, 0.03, 1.0),
        "surface": (0.03, 0.03, 0.03, 1.0),
        "strap": (0.10, 0.10, 0.10, 1.0),
        "wheel": (0.05, 0.05, 0.05, 1.0),
        "hub": (0.65, 0.66, 0.62, 1.0),
        "release": (0.85, 0.02, 0.015, 1.0),
    },
    "rescue_orange": {
        "frame": (0.95, 0.35, 0.05, 1.0),
        "surface": (0.96, 0.42, 0.07, 1.0),
        "strap": (0.06, 0.06, 0.06, 1.0),
        "wheel": (0.10, 0.10, 0.10, 1.0),
        "hub": (0.55, 0.55, 0.55, 1.0),
        "release": (0.80, 0.10, 0.05, 1.0),
    },
    "olive_drab": {
        "frame": (0.06, 0.06, 0.05, 1.0),
        "surface": (0.42, 0.44, 0.24, 1.0),
        "strap": (0.25, 0.26, 0.15, 1.0),
        "wheel": (0.05, 0.05, 0.04, 1.0),
        "hub": (0.50, 0.50, 0.45, 1.0),
        "release": (0.70, 0.10, 0.05, 1.0),
    },
    "ems_navy": {
        "frame": (0.14, 0.18, 0.32, 1.0),
        "surface": (0.10, 0.11, 0.13, 1.0),
        "strap": (0.02, 0.02, 0.02, 1.0),
        "wheel": (0.03, 0.03, 0.03, 1.0),
        "hub": (0.50, 0.50, 0.52, 1.0),
        "release": (0.85, 0.02, 0.02, 1.0),
    },
    "hi_vis_lime": {
        "frame": (0.62, 0.80, 0.10, 1.0),
        "surface": (0.72, 0.86, 0.13, 1.0),
        "strap": (0.05, 0.05, 0.05, 1.0),
        "wheel": (0.08, 0.08, 0.08, 1.0),
        "hub": (0.55, 0.56, 0.58, 1.0),
        "release": (0.85, 0.02, 0.02, 1.0),
    },
}

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class StretcherConfig:
    deck: Deck | None = None
    undercarriage: Undercarriage | None = None
    restraint: Restraint | None = None
    caster_count: int | None = None
    palette_style: PaletteStyle = "safety_orange"
    deck_len_scale: float = 1.0
    deck_width_scale: float = 1.0
    deck_height_scale: float = 1.0
    backrest_angle_scale: float = 1.0
    fold_angle_scale: float = 1.0
    name: str = "stretcher"


@dataclass(frozen=True)
class ResolvedStretcherConfig:
    deck: Deck
    undercarriage: Undercarriage
    restraint: Restraint
    caster_count: int
    palette_style: PaletteStyle
    # Derived geometry (single-sourced, spec §7 / Contract 3c).
    deck_len: float
    deck_width: float
    base_z: float          # world z of the deck underside / lowest structure
    deck_thick: float      # deck slab / frame thickness
    top_z: float           # deck top surface world z
    backrest_hinge_x: float
    backrest_len: float
    backrest_upper: float
    fold_upper: float
    height_travel: float
    name: str

    @property
    def head_x(self) -> float:
        return -self.deck_len / 2.0

    @property
    def foot_x(self) -> float:
        return self.deck_len / 2.0

    @property
    def half_w(self) -> float:
        return self.deck_width / 2.0

    @property
    def has_backrest(self) -> bool:
        return self.deck in _HAS_BACKREST


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> StretcherConfig:
    rng = random.Random(seed)
    deck: Deck = rng.choice(DECKS)
    undercarriage: Undercarriage = rng.choice(_UNDER_FOR_DECK[deck])  # type: ignore[assignment]
    restraint: Restraint = rng.choice(_RESTRAINT_FOR_DECK[deck])  # type: ignore[assignment]

    if undercarriage in _CARRIAGE_WHEELED:
        caster_count = rng.choices(_CARRIAGE_N_CHOICES, weights=_CARRIAGE_N_WEIGHTS, k=1)[0]
    elif undercarriage == "foldleg_wheeled":
        caster_count = rng.choices(_FOLDLEG_N_CHOICES, weights=_FOLDLEG_N_WEIGHTS, k=1)[0]
    else:
        caster_count = 0

    return StretcherConfig(
        deck=deck,
        undercarriage=undercarriage,
        restraint=restraint,
        caster_count=caster_count,
        palette_style=rng.choice(PALETTE_STYLES),
        deck_len_scale=round(rng.uniform(0.92, 1.08), 4),
        deck_width_scale=round(rng.uniform(0.92, 1.08), 4),
        deck_height_scale=round(rng.uniform(0.90, 1.10), 4),
        backrest_angle_scale=round(rng.uniform(0.85, 1.12), 4),
        fold_angle_scale=round(rng.uniform(0.85, 1.12), 4),
        name=f"seeded_stretcher_{seed}",
    )


def resolve_config(config: StretcherConfig | None = None) -> ResolvedStretcherConfig:
    cfg = config or StretcherConfig()

    deck: Deck = _pick(cfg.deck, DECKS)  # type: ignore[assignment]
    under_choices = _UNDER_FOR_DECK[deck]
    restraint_choices = _RESTRAINT_FOR_DECK[deck]
    undercarriage: Undercarriage = _pick(cfg.undercarriage, under_choices)  # type: ignore[assignment]
    restraint: Restraint = _pick(cfg.restraint, restraint_choices)  # type: ignore[assignment]

    palette_style: PaletteStyle = _pick(cfg.palette_style, PALETTE_STYLES)  # type: ignore[assignment]

    # caster_count gating.
    if undercarriage in _CARRIAGE_WHEELED:
        n = int(cfg.caster_count) if cfg.caster_count else 4
        n = n if n in _CARRIAGE_N_CHOICES else (6 if n and n >= 5 else 4)
    elif undercarriage == "foldleg_wheeled":
        n = int(cfg.caster_count) if cfg.caster_count else 4
        n = n if n in _FOLDLEG_N_CHOICES else 4
    else:
        n = 0

    len_scale = _clamp(cfg.deck_len_scale, 0.92, 1.08)
    width_scale = _clamp(cfg.deck_width_scale, 0.92, 1.08)
    height_scale = _clamp(cfg.deck_height_scale, 0.90, 1.10)
    backrest_scale = _clamp(cfg.backrest_angle_scale, 0.85, 1.12)
    fold_scale = _clamp(cfg.fold_angle_scale, 0.85, 1.12)

    if deck == "spine_board":
        base_len, base_w, deck_thick = 1.83, 0.41, 0.05
    elif deck == "basket_shell":
        base_len, base_w, deck_thick = 2.00, 0.62, 0.24
    else:
        base_len, base_w, deck_thick = 1.90, 0.58, 0.05

    deck_len = base_len * len_scale
    deck_width = base_w * width_scale

    # base_z: world z of the deck underside, depends on the undercarriage.
    if undercarriage in _WHEELED:
        base_z = 0.72 * height_scale
    elif undercarriage == "carry_poles":
        base_z = 0.60
    else:  # bare_feet
        base_z = 0.045

    top_z = base_z + deck_thick

    backrest_len = 0.60 * len_scale
    backrest_hinge_x = -deck_len / 2.0 + backrest_len
    backrest_upper = _clamp(0.58 * backrest_scale, 0.30, 0.62)
    fold_upper = _clamp(1.30 * fold_scale, 0.90, 1.50)
    height_travel = _clamp(0.20 * height_scale, 0.12, 0.24)

    return ResolvedStretcherConfig(
        deck=deck,
        undercarriage=undercarriage,
        restraint=restraint,
        caster_count=n,
        palette_style=palette_style,
        deck_len=deck_len,
        deck_width=deck_width,
        base_z=base_z,
        deck_thick=deck_thick,
        top_z=top_z,
        backrest_hinge_x=backrest_hinge_x,
        backrest_len=backrest_len,
        backrest_upper=backrest_upper,
        fold_upper=fold_upper,
        height_travel=height_travel,
        name=cfg.name or "stretcher",
    )


def with_overrides(config: StretcherConfig, **kwargs: object) -> StretcherConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: StretcherConfig | ResolvedStretcherConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedStretcherConfig) else resolve_config(config)
    return (
        ("deck", r.deck),
        ("undercarriage", r.undercarriage),
        ("restraint", r.restraint),
        ("caster_count", f"n{r.caster_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Geometry helpers (adapted from the sources)
# --------------------------------------------------------------------------- #


def _tube_origin(p0, p1, *, extend: float = 0.002) -> tuple[Origin, float]:
    sx, sy, sz = p0
    ex, ey, ez = p1
    dx, dy, dz = ex - sx, ey - sy, ez - sz
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 1e-9:
        raise ValueError("tube endpoints must be separated")
    ux, uy, uz = dx / length, dy / length, dz / length
    sx -= ux * extend
    sy -= uy * extend
    sz -= uz * extend
    ex += ux * extend
    ey += uy * extend
    ez += uz * extend
    length += 2.0 * extend
    mx = (sx + ex) * 0.5
    my = (sy + ey) * 0.5
    mz = (sz + ez) * 0.5
    yaw = math.atan2(uy, ux)
    pitch = math.atan2(math.sqrt(ux * ux + uy * uy), uz)
    return Origin(xyz=(mx, my, mz), rpy=(0.0, pitch, yaw)), length


def _tube(part, p0, p1, radius: float, material, name: str, *, extend: float = 0.002) -> None:
    origin, length = _tube_origin(p0, p1, extend=extend)
    part.visual(Cylinder(radius=radius, length=length), origin=origin, material=material, name=name, material_class_id="metal.paint_coated")


def _box(part, name: str, size, xyz, material, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="fabric.upholstery_plain")


def _curved_tube(
    part, points, radius: float, material, name: str, *, sps: int = 8, rs: int = 12
) -> None:
    part.visual(
        mesh_from_geometry(
            tube_from_spline_points(
                points, radius=radius, samples_per_segment=sps, radial_segments=rs, cap_ends=True
            ),
            name,
        ),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _rounded_pad(width: float, length: float, thickness: float, radius: float, name: str):
    profile = rounded_rect_profile(length, width, radius, corner_segments=8)
    return mesh_from_geometry(ExtrudeGeometry.centered(profile, thickness), name)


# --------------------------------------------------------------------------- #
# Caster (cheap o1 cylinder wheel), shared by all wheeled undercarriages.
# --------------------------------------------------------------------------- #


def _add_caster(model, r, mats, *, name: str, parent, joint_name: str, origin_xyz) -> None:
    """One caster: tire + hub + spin marker, CONTINUOUS about y. (o1 L213-L227)."""
    wheel = model.part(name)
    wheel.visual(
        Cylinder(radius=0.062, length=0.058),
        origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["wheel"],
        name="tire", material_class_id="rubber.smooth_plain",
    )
    wheel.visual(
        Cylinder(radius=0.030, length=0.064),
        origin=Origin(rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material=mats["hub"],
        name="hub", material_class_id="metal.aluminum_bare",
    )
    _box(wheel, "spin_marker", (0.012, 0.046, 0.006), (0.037, 0.0, 0.0), mats["hub"])
    model.articulation(
        joint_name,
        ArticulationType.CONTINUOUS,
        parent=parent,
        child=wheel,
        origin=Origin(xyz=origin_xyz),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=12.0),
    )


def _caster_rows(r) -> list[tuple[float, float]]:
    """(x, y) caster axle world positions for carriage undercarriages by N."""
    cx = r.deck_len * 0.40
    cy = r.deck_width * 0.40
    if r.caster_count == 2:
        return [(cx, -cy), (cx, cy)]  # foot end pair
    if r.caster_count == 6:
        return [(x, y) for x in (-cx, 0.0, cx) for y in (-cy, cy)]
    return [(x, y) for x in (-cx, cx) for y in (-cy, cy)]  # N=4 default


# --------------------------------------------------------------------------- #
# Slot A — deck forms
# --------------------------------------------------------------------------- #


def _build_deck_sockets(deck, r, mats) -> None:
    """Perimeter under-frame + hinge/attach sockets shared by cot/canvas decks.
    The deck board itself covers the seat+foot section; the head section is the
    (movable) backrest, so the perimeter frame stops just short of the head."""
    hw = r.half_w
    hx, fx = r.head_x, r.foot_x
    tz = r.top_z
    front_x = r.backrest_hinge_x if r.has_backrest else hx
    # Full-length perimeter tube frame just under the top surface (the raised
    # backrest sits above the head third of this frame).
    _tube(deck, (hx, -hw, tz - 0.02), (fx, -hw, tz - 0.02), 0.015, mats["frame"], "side_frame_0")
    _tube(deck, (hx, hw, tz - 0.02), (fx, hw, tz - 0.02), 0.015, mats["frame"], "side_frame_1")
    _tube(deck, (hx, -hw, tz - 0.02), (hx, hw, tz - 0.02), 0.014, mats["frame"], "head_crossbar")
    _tube(deck, (fx, -hw, tz - 0.02), (fx, hw, tz - 0.02), 0.014, mats["frame"], "foot_crossbar")
    # Backrest hinge socket bridging the deck top up to the raised hinge line.
    if r.has_backrest:
        _tube(
            deck,
            (front_x, -hw - 0.005, tz + 0.008),
            (front_x, hw + 0.005, tz + 0.008),
            0.014,
            mats["frame"],
            "back_hinge_socket",
        )
    # Side-rail sockets along both edges, raised above the perimeter frame.
    _tube(deck, (front_x + 0.12, hw, tz + 0.010), (fx - 0.20, hw, tz + 0.010), 0.011, mats["strap"], "rail_socket_0")
    _tube(deck, (front_x + 0.12, -hw, tz + 0.010), (fx - 0.20, -hw, tz + 0.010), 0.011, mats["strap"], "rail_socket_1")


def _build_padded_cot(model, r, mats) -> str:
    """Segmented foam mattress deck + hinged backrest (o1 L78-L162 / o2 L386-L406)."""
    deck = model.part("deck_frame")
    _hx, fx = r.head_x, r.foot_x
    bz, tz = r.base_z, r.top_z
    seat_x0 = r.backrest_hinge_x
    # Full-length deck board (structural litter pan). Foam pads cover the seat +
    # foot; the raised backrest panel covers the head third above the board.
    _box(
        deck,
        "deck_board",
        (r.deck_len, r.deck_width, r.deck_thick),
        (0.0, 0.0, bz + r.deck_thick * 0.5),
        mats["strap"],
    )
    _build_deck_sockets(deck, r, mats)
    # Segmented foam pads over the seat + foot section (head section = backrest).
    seat_len = fx - seat_x0
    _box(
        deck,
        "foot_pad",
        (seat_len * 0.55, r.deck_width - 0.06, 0.07),
        (seat_x0 + seat_len * 0.72, 0.0, tz + 0.035),
        mats["surface"],
    )
    _box(
        deck,
        "seat_pad",
        (seat_len * 0.42, r.deck_width - 0.06, 0.07),
        (seat_x0 + seat_len * 0.25, 0.0, tz + 0.035),
        mats["surface"],
    )
    # Restraint straps + brake decal (④ decoration, host visuals).
    _box(deck, "seat_strap", (0.045, r.deck_width - 0.13, 0.010), (seat_x0 + seat_len * 0.45, 0.0, tz + 0.075), mats["strap"])
    _box(deck, "foot_strap", (0.045, r.deck_width - 0.13, 0.010), (seat_x0 + seat_len * 0.85, 0.0, tz + 0.075), mats["strap"])
    _build_backrest(model, r, mats)
    return "deck_frame"


def _build_canvas_cot(model, r, mats) -> str:
    """Tube frame + tensioned canvas surface + backrest (canvas_deck L100-L145)."""
    deck = model.part("deck_frame")
    hw = r.half_w
    _hx, fx = r.head_x, r.foot_x
    bz, tz = r.base_z, r.top_z
    seat_x0 = r.backrest_hinge_x
    # Full-length thin deck board / canvas support pan.
    _box(deck, "deck_board", (r.deck_len, r.deck_width, r.deck_thick), (0.0, 0.0, bz + r.deck_thick * 0.5), mats["frame"])
    _build_deck_sockets(deck, r, mats)
    canvas_x0 = seat_x0 + 0.06  # inset from the backrest hinge line.
    canvas_len = fx - canvas_x0
    canvas_cx = canvas_x0 + canvas_len * 0.5
    # Tensioned canvas panel resting on the deck board top (z=tz).
    _box(deck, "main_canvas", (canvas_len, r.deck_width - 0.06, 0.010), (canvas_cx, 0.0, tz + 0.004), mats["surface"])
    # Hem tubes along the canvas side edges.
    for i, ys in enumerate((-1.0, 1.0)):
        _tube(deck, (canvas_x0, ys * (hw - 0.03), tz + 0.004), (fx, ys * (hw - 0.03), tz + 0.004), 0.006, mats["surface"], f"canvas_hem_{i}")
    # Lace stubs (④ decoration).
    for i, xf in enumerate((0.2, 0.4, 0.6, 0.8)):
        xx = canvas_x0 + canvas_len * xf
        _box(deck, f"canvas_stitch_{i}", (0.007, r.deck_width - 0.10, 0.006), (xx, 0.0, tz + 0.010), mats["strap"])
    _box(deck, "seat_strap", (0.045, r.deck_width - 0.13, 0.010), (canvas_cx, 0.0, tz + 0.013), mats["strap"])
    _build_backrest(model, r, mats)
    return "deck_frame"


def _build_backrest(model, r, mats) -> None:
    """Hinged head/backrest section. Local origin at the hinge; extends toward -X.
    (o1 L118-L162 / o2 L517-L542)."""
    backrest = model.part("backrest")
    hw = r.half_w
    bl = r.backrest_len
    tz = r.top_z
    hinge_z = tz + 0.020
    # hinge bar (captured pin) at local origin, overlapping the deck socket.
    _tube(backrest, (0.0, -hw - 0.005, 0.0), (0.0, hw + 0.005, 0.0), 0.016, mats["frame"], "hinge_bar")
    # Side + head perimeter tubes extending toward the head end (-X local).
    _tube(backrest, (-bl, -hw + 0.02, 0.0), (0.0, -hw + 0.02, 0.0), 0.013, mats["frame"], "back_side_0")
    _tube(backrest, (-bl, hw - 0.02, 0.0), (0.0, hw - 0.02, 0.0), 0.013, mats["frame"], "back_side_1")
    _tube(backrest, (-bl, -hw + 0.02, 0.0), (-bl, hw - 0.02, 0.0), 0.012, mats["frame"], "head_end_tube")
    # Back pad + strap (④) resting on the perimeter tubes (local z=0).
    _box(backrest, "back_pad", (bl - 0.06, r.deck_width - 0.06, 0.065), (-bl * 0.5, 0.0, 0.030), mats["surface"])
    _box(backrest, "back_strap", (0.045, r.deck_width - 0.02, 0.010), (-bl * 0.42, 0.0, 0.066), mats["strap"])
    model.articulation(
        "deck_to_backrest",
        ArticulationType.REVOLUTE,
        parent=model.get_part("deck_frame"),
        child=backrest,
        # Reclines from flat (q=0) up to the seated angle; it never folds below
        # the deck plane (which would dive into the undercarriage at the head).
        origin=Origin(xyz=(r.backrest_hinge_x, 0.0, hinge_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=1.0, lower=0.0, upper=r.backrest_upper),
    )


def _build_spine_board(model, r, mats) -> str:
    """Flat rigid HDPE spine board with oval hand-hole cutouts + spider straps.
    (spine_board L88-L277). Static board; joint comes from immobilizer_blocks."""
    deck = model.part("deck_frame")
    hx, fx = r.head_x, r.foot_x
    hw = r.half_w
    bz = r.base_z
    board_thick = r.deck_thick
    # Board mesh with 5 pairs of oval hand holes.
    outer = rounded_rect_profile(r.deck_len, r.deck_width, 0.025, corner_segments=8)
    holes = []
    for hxx in (-0.58, -0.30, -0.02, 0.26, 0.54):
        for sy in (r.deck_width * 0.38, -r.deck_width * 0.38):
            hole = superellipse_profile(0.10, 0.030, exponent=2.0, segments=20)
            holes.append([(px * r.deck_len / 1.83 + hxx, py + sy) for px, py in hole])
    board = mesh_from_geometry(
        ExtrudeWithHolesGeometry(outer, holes, board_thick, center=True), "board"
    )
    deck.visual(board, origin=Origin(xyz=(0.0, 0.0, bz + board_thick * 0.5)), material=mats["surface"], name="board", material_class_id="plastic.opaque_glossy_molded")
    tz = bz + board_thick
    # Head bed pad (④).
    deck.visual(
        _rounded_pad(0.28, 0.30, 0.008, 0.04, "head_bed_pad"),
        origin=Origin(xyz=(hx + 0.11, 0.0, tz)),
        material=mats["strap"],
        name="head_bed_pad", material_class_id="fabric.flexible_foam",
    )
    # Spider strap set (④) resting on the board top (z=tz).
    for i, sx in enumerate((hx + 0.55, 0.05, fx - 0.55)):
        _box(deck, f"strap_{i}", (0.038, r.deck_width * 0.92, 0.006), (sx, 0.0, tz + 0.001), mats["strap"])
        _box(deck, f"buckle_{i}", (0.048, 0.038, 0.012), (sx, r.deck_width * 0.42, tz + 0.004), mats["release"])
    # Carry handles at head + foot ends.
    for tag, ex in (("head", hx + 0.04), ("foot", fx - 0.04)):
        pts = [
            (ex, -0.14, tz - 0.02),
            (ex - 0.04 if tag == "head" else ex + 0.04, -0.14, tz + 0.02),
            (ex - 0.04 if tag == "head" else ex + 0.04, 0.14, tz + 0.02),
            (ex, 0.14, tz - 0.02),
        ]
        _curved_tube(deck, pts, 0.008, mats["strap"], f"{tag}_handle", sps=6, rs=12)
    # Immobilizer sockets at the head (for immobilizer_blocks restraint).
    _tube(deck, (hx + 0.26, -hw - 0.01, tz + 0.006), (hx + 0.26, hw + 0.01, tz + 0.006), 0.010, mats["strap"], "block_socket")
    return "deck_frame"


def _basket_half_points(half_len, half_w, z_base, z_raise, *, n=12, footward=False):
    pts = []
    for i in range(n + 1):
        t = i / n
        theta = (-math.pi / 2.0 + t * math.pi) if footward else (math.pi / 2.0 + t * math.pi)
        x = half_len * math.cos(theta)
        y = half_w * math.sin(theta)
        z = z_base + z_raise * abs(x) / max(half_len, 1e-9)
        pts.append((x, y, z))
    return pts


def _add_basket_half(part, r, mats, *, footward: bool, base: float) -> None:
    """One Stokes basket half: oval rim + perforated floor pan + ribs + rope grabs
    + center-fold hinge hardware. (basket_litter L147-L262). ``base`` is the floor
    reference z in the PART's local frame (head half = world base_z, foot half = 0
    since it hangs off the fold hinge whose origin already carries base_z)."""
    sign = 1.0 if footward else -1.0
    half_len = r.deck_len * 0.50
    half_w = r.half_w
    rim_z = base + 0.20
    floor_z = base + 0.02
    raise_z = 0.06 if not footward else 0.0
    # perimeter rim tube (half oval)
    rim_pts = _basket_half_points(half_len, half_w, rim_z, raise_z, n=12, footward=footward)
    _curved_tube(part, rim_pts, 0.014, mats["surface"], "rim_tube", sps=8, rs=12)
    # perforated floor pan (coarse pitch to honor the §7.5 compile budget).
    floor_len = half_len * 0.84
    floor_w = half_w * 1.55
    floor_mesh = mesh_from_geometry(
        PerforatedPanelGeometry(
            (floor_len, floor_w),
            0.005,
            hole_diameter=0.024,
            pitch=(0.075, 0.075),
            frame=0.020,
            corner_radius=0.020,
            stagger=True,
        ),
        "floor_pan",
    )
    floor_cx = sign * half_len * 0.46
    part.visual(floor_mesh, origin=Origin(xyz=(floor_cx, 0.0, floor_z)), material=mats["wheel"], name="floor_pan", material_class_id="plastic.patterned_textured")
    # vertical rib uprights
    for i in range(5):
        t = (i + 0.5) / 5
        theta = (-math.pi / 2.0 + t * math.pi) if footward else (math.pi / 2.0 + t * math.pi)
        x = half_len * math.cos(theta)
        y = half_w * math.sin(theta)
        z_top = rim_z + (raise_z * abs(x) / max(half_len, 1e-9) if not footward else 0.0)
        _tube(part, (x, y, floor_z - 0.008), (x, y, z_top - 0.005), 0.008, mats["surface"], f"rib_{i}")
    # rope grab handles
    for i in range(3):
        t = (i + 0.5) / 3
        theta = (-math.pi / 2.0 + t * math.pi) if footward else (math.pi / 2.0 + t * math.pi)
        x = half_len * math.cos(theta)
        y = half_w * math.sin(theta)
        z_rim = rim_z + (raise_z * abs(x) / max(half_len, 1e-9) if not footward else 0.0)
        nx = math.cos(theta) / max(half_len, 1e-9)
        ny = math.sin(theta) / max(half_w, 1e-9)
        mag = math.hypot(nx, ny) or 1.0
        nx, ny = nx / mag, ny / mag
        along_x, along_y = -math.sin(theta) * 0.012, math.cos(theta) * 0.012
        pts = [
            (x + along_x, y + along_y, z_rim),
            (x + nx * 0.02, y + ny * 0.02, z_rim + 0.018),
            (x + nx * 0.05, y + ny * 0.05, z_rim + 0.036),
            (x + nx * 0.02, y + ny * 0.02, z_rim + 0.020),
            (x - along_x, y - along_y, z_rim),
        ]
        _curved_tube(part, pts, 0.005, mats["strap"], f"rope_handle_{i}", sps=5, rs=8)
    # center-fold hinge hardware
    hinge_half = 0.09 if not footward else 0.07
    hinge_r = 0.014 if not footward else 0.011
    _tube(part, (0.0, -hinge_half, floor_z), (0.0, hinge_half, floor_z), hinge_r, mats["surface"], "hinge_barrel")
    sx_s, sx_e = sign * 0.014, sign * 0.045
    _tube(part, (sx_s, -hinge_half, floor_z), (sx_e, -half_w, rim_z), 0.009, mats["surface"], "fold_stanchion_0")
    _tube(part, (sx_s, hinge_half, floor_z), (sx_e, half_w, rim_z), 0.009, mats["surface"], "fold_stanchion_1")
    _box(part, "hinge_plate", (0.040, hinge_half * 2.2, 0.006), (sign * 0.035, 0.0, floor_z), mats["surface"])


def _build_basket_shell(model, r, mats) -> str:
    """Stokes basket rescue litter: two halves + clamshell fold (basket_litter)."""
    head = model.part("deck_frame")
    _add_basket_half(head, r, mats, footward=False, base=r.base_z)
    foot = model.part("foot_basket")
    # foot half authored in local frame (floor at 0); the fold hinge origin
    # carries the world base_z offset.
    _add_basket_half(foot, r, mats, footward=True, base=0.0)
    model.articulation(
        "fold_hinge",
        ArticulationType.REVOLUTE,
        parent=head,
        child=foot,
        origin=Origin(xyz=(0.0, 0.0, r.base_z)),
        axis=(0.0, -1.0, 0.0),
        # Capped at ~vertical: beyond 90 deg the foot half folds bodily onto the
        # head half. The two halves share the fold-line seam (allowed below).
        motion_limits=MotionLimits(effort=30.0, velocity=1.0, lower=0.0, upper=1.45),
    )
    return "deck_frame"


_DECK_BUILDERS = {
    "padded_cot": _build_padded_cot,
    "canvas_cot": _build_canvas_cot,
    "basket_shell": _build_basket_shell,
    "spine_board": _build_spine_board,
}


# --------------------------------------------------------------------------- #
# Slot B — undercarriage
# --------------------------------------------------------------------------- #


def _build_carriage_wheeled(model, r, mats, *, scissor: bool) -> None:
    """Telescoping-slider lift: deck-fixed outer sleeves + carriage inner sliders +
    N casters. scissor=True adds decorative X-cross visuals (o1 scissor look).
    Height PRISMATIC retracts the carriage upward into the sleeves.
    (o1 L58-L227 / telescoping_legs L210-L256)."""
    deck = model.get_part("deck_frame")
    rows = _caster_rows(r)
    bz = r.base_z
    sleeve_bot = bz - 0.30
    # Deck-fixed outer sleeve tubes at each caster column (dedupe by x).
    col_xs = sorted({x for x, _ in rows})
    col_ys = sorted({y for _, y in rows})
    for ci, cx in enumerate(col_xs):
        for si, cy in enumerate(col_ys):
            _tube(deck, (cx, cy, bz), (cx, cy, sleeve_bot), 0.020, mats["frame"], f"leg_sleeve_{ci}_{si}")

    carriage = model.part("lower_carriage")
    # Inner slider tubes (top at sleeve_bot -> down to the frame, above the wheels).
    wheel_z = 0.065
    frame_z = wheel_z + 0.085  # lower frame sits clear above the wheel tops.
    for ci, cx in enumerate(col_xs):
        for si, cy in enumerate(col_ys):
            _tube(carriage, (cx, cy, sleeve_bot), (cx, cy, frame_z), 0.015, mats["frame"], f"inner_leg_{ci}_{si}")
    # Lower rail frame tying the sliders together.
    for cy in col_ys:
        _tube(carriage, (col_xs[0], cy, frame_z), (col_xs[-1], cy, frame_z), 0.012, mats["frame"], f"lower_rail_{cy:+.2f}")
    _tube(carriage, (col_xs[0], col_ys[0], frame_z), (col_xs[0], col_ys[-1], frame_z), 0.011, mats["frame"], "lower_cross_head")
    _tube(carriage, (col_xs[-1], col_ys[0], frame_z), (col_xs[-1], col_ys[-1], frame_z), 0.011, mats["frame"], "lower_cross_foot")
    if scissor:
        # Decorative scissor X crosses on each side (moves with carriage).
        for si, cy in enumerate(col_ys):
            _tube(carriage, (col_xs[0], cy, frame_z), (col_xs[-1], cy, sleeve_bot - 0.02), 0.011, mats["frame"], f"scissor_a_{si}")
            _tube(carriage, (col_xs[-1], cy, frame_z), (col_xs[0], cy, sleeve_bot - 0.02), 0.011, mats["frame"], f"scissor_b_{si}")
    # Short fork stubs bridging the frame down through each caster axle (so the
    # spin-joint origin sits on real fork hardware).
    for i, (cx, cy) in enumerate(rows):
        _tube(carriage, (cx, cy, frame_z), (cx, cy, wheel_z - 0.015), 0.014, mats["strap"], f"caster_fork_{i}")
    # Foot push hoop (② handle) on the carriage foot end.
    fx2 = col_xs[-1] + 0.14
    _tube(carriage, (fx2, -r.deck_width * 0.36, frame_z + 0.06), (fx2, r.deck_width * 0.36, frame_z + 0.06), 0.014, mats["frame"], "foot_push_crossbar")
    _tube(carriage, (col_xs[-1], -r.deck_width * 0.36, frame_z), (fx2, -r.deck_width * 0.36, frame_z + 0.06), 0.012, mats["frame"], "foot_push_side_0")
    _tube(carriage, (col_xs[-1], r.deck_width * 0.36, frame_z), (fx2, r.deck_width * 0.36, frame_z + 0.06), 0.012, mats["frame"], "foot_push_side_1")
    _box(carriage, "release_decal", (0.05, 0.02, 0.02), (fx2, -r.deck_width * 0.20, frame_z + 0.04), mats["release"])

    # Joint origin at world (0,0,0): carriage geometry is authored in world coords
    # so carriage-local == world. Prismatic origin is gauge-exempt.
    model.articulation(
        "height_slide",
        ArticulationType.PRISMATIC,
        parent=deck,
        child=carriage,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=250.0, velocity=0.18, lower=0.0, upper=r.height_travel),
    )
    # Casters on the carriage.
    for i, (cx, cy) in enumerate(rows):
        _add_caster(model, r, mats, name=f"caster_{i}", parent=carriage, joint_name=f"caster_spin_{i}", origin_xyz=(cx, cy, wheel_z))


def _build_scissor_wheeled(model, r, mats) -> None:
    _build_carriage_wheeled(model, r, mats, scissor=True)


def _build_telescoping_wheeled(model, r, mats) -> None:
    _build_carriage_wheeled(model, r, mats, scissor=False)


def _build_foldleg_wheeled(model, r, mats) -> None:
    """Folding straight-tube legs (REVOLUTE) + casters (o2 L549-L647, straight-tube
    idiom per o1 L58-L75; §7.5)."""
    deck = model.get_part("deck_frame")
    bz = r.base_z
    hw = r.half_w
    leg_x_head = r.head_x + 0.35
    leg_x_foot = r.foot_x - 0.35
    wheel_z = 0.065
    # Deck leg sockets (captured hinge tubes).
    _tube(deck, (leg_x_head, -hw, bz), (leg_x_head, hw, bz), 0.018, mats["frame"], "head_leg_socket")
    _tube(deck, (leg_x_foot, -hw, bz), (leg_x_foot, hw, bz), 0.018, mats["frame"], "foot_leg_socket")

    leg_cy = r.deck_width * 0.40
    specs = [("head_leg", leg_x_head, "deck_to_head_leg", -1.0), ("foot_leg", leg_x_foot, "deck_to_foot_leg", 1.0)]
    caster_idx = 0
    # N=2 -> only foot leg carries wheels.
    wheeled_legs = {"foot_leg"} if r.caster_count == 2 else {"head_leg", "foot_leg"}
    for leg_name, lx, joint_name, axis_sign in specs:
        leg = model.part(leg_name)
        # top hinge bar (captured pin) at local origin.
        _tube(leg, (0.0, -hw, 0.0), (0.0, hw, 0.0), 0.017, mats["frame"], "top_hinge")
        for si, ly in enumerate((-leg_cy, leg_cy)):
            # straight leg with a single outward bend (2 segments), foot to floor.
            splay = 0.06 * axis_sign
            _tube(leg, (0.0, ly, -0.010), (splay, ly, -(bz - wheel_z) * 0.5), 0.016, mats["frame"], f"upper_leg_{si}")
            _tube(leg, (splay, ly, -(bz - wheel_z) * 0.5), (splay, ly, -(bz - wheel_z) - 0.005), 0.016, mats["frame"], f"lower_leg_{si}")
            if leg_name in wheeled_legs:
                _box(leg, f"caster_mount_{si}", (0.06, 0.03, 0.03), (splay, ly, -(bz - wheel_z) - 0.02), mats["strap"])
                _tube(leg, (splay, ly - 0.058, -(bz - wheel_z) - 0.04), (splay, ly + 0.058, -(bz - wheel_z) - 0.04), 0.008, mats["strap"], f"wheel_axle_{si}")
        # cross tie between the two leg struts.
        _tube(leg, (splay, -leg_cy, -(bz - wheel_z) * 0.5), (splay, leg_cy, -(bz - wheel_z) * 0.5), 0.010, mats["frame"], "leg_crosstie")
        model.articulation(
            joint_name,
            ArticulationType.REVOLUTE,
            parent=deck,
            child=leg,
            origin=Origin(xyz=(lx, 0.0, bz)),
            # o2 convention: head leg axis (0,-1,0), foot leg (0,1,0) -> both fold
            # inward for storage; capped so head+foot wheel pairs never collide at
            # the center when both legs fold simultaneously.
            axis=(0.0, axis_sign, 0.0),
            motion_limits=MotionLimits(effort=70.0, velocity=1.0, lower=0.0, upper=min(r.fold_upper, 0.72)),
        )
        if leg_name in wheeled_legs:
            for si, ly in enumerate((-leg_cy, leg_cy)):
                _add_caster(
                    model, r, mats,
                    name=f"caster_{caster_idx}",
                    parent=leg,
                    joint_name=f"{leg_name}_to_caster_{si}",
                    origin_xyz=(splay, ly, -(bz - wheel_z)),
                )
                caster_idx += 1


def _build_carry_poles(model, r, mats) -> None:
    """Two carry poles (deck visuals) + folding head/foot spreaders (REVOLUTE)
    (pole_canvas L127-L209, L388-L407)."""
    deck = model.get_part("deck_frame")
    hx, fx = r.head_x, r.foot_x
    # poles run alongside the deck (cot/canvas) or underneath the shell/board.
    hw = r.half_w
    if r.deck in _HAS_BACKREST:
        pole_z = r.top_z - 0.04
        deck_attach_z = r.top_z - 0.01
    else:  # spine_board
        pole_z = r.base_z + 0.02
        deck_attach_z = r.base_z + r.deck_thick * 0.5
    pole_y = hw + 0.03
    for i, ys in enumerate((-1.0, 1.0)):
        y = ys * pole_y
        _tube(deck, (hx - 0.16, y, pole_z), (fx + 0.16, y, pole_z), 0.014, mats["frame"], f"pole_{i}")
        # rubber grip sleeves at both handle ends
        _tube(deck, (hx - 0.16, y, pole_z), (hx - 0.02, y, pole_z), 0.019, mats["strap"], f"grip_head_{i}", extend=0.0)
        _tube(deck, (fx + 0.02, y, pole_z), (fx + 0.16, y, pole_z), 0.019, mats["strap"], f"grip_foot_{i}", extend=0.0)
        deck.visual(Sphere(0.016), origin=Origin(xyz=(hx - 0.16, y, pole_z)), material=mats["frame"], name=f"end_cap_head_{i}", material_class_id="plastic.opaque_glossy_molded")
        deck.visual(Sphere(0.016), origin=Origin(xyz=(fx + 0.16, y, pole_z)), material=mats["frame"], name=f"end_cap_foot_{i}", material_class_id="plastic.opaque_glossy_molded")
        # connector struts tying each pole to the deck edge (connectivity).
        for j, xf in enumerate((0.20, 0.5, 0.80)):
            xx = hx + (fx - hx) * xf
            _tube(deck, (xx, y, pole_z), (xx, ys * (hw - 0.02), deck_attach_z), 0.009, mats["frame"], f"pole_strut_{i}_{j}")
    # spreader hinge line sits just below the poles, inside the mount brackets so
    # the joint axis lands on real hardware.
    spreader_z = pole_z - 0.05
    for tag, sx in (("head", hx + 0.30), ("foot", fx - 0.30)):
        for i, ys in enumerate((-1.0, 1.0)):
            _box(deck, f"{tag}_mount_{i}", (0.038, 0.032, 0.07), (sx, ys * pole_y, pole_z - 0.030), mats["strap"])

    for tag, sx in (("head", hx + 0.30), ("foot", fx - 0.30)):
        spreader = model.part(f"{tag}_spreader")
        # cross-bar tube from near pole across to far pole (local +Y).
        _tube(spreader, (0.0, -0.005, 0.0), (0.0, 2.0 * pole_y - 0.005, 0.0), 0.011, mats["frame"], "spreader_bar")
        spreader.visual(
            Cylinder(radius=0.016, length=0.018),
            origin=Origin(xyz=(0.0, pole_y, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["hub"],
            name="centre_brace", material_class_id="metal.aluminum_bare",
        )
        _box(spreader, "hinge_arm", (0.030, 0.032, 0.030), (0.0, 0.012, 0.015), mats["strap"])
        _box(spreader, "latch_arm", (0.030, 0.032, 0.030), (0.0, 2.0 * pole_y - 0.012, 0.015), mats["strap"])
        model.articulation(
            f"deck_to_{tag}_spreader",
            ArticulationType.REVOLUTE,
            parent=deck,
            child=spreader,
            origin=Origin(xyz=(sx, -pole_y, spreader_z)),
            # fold downward (-z), away from the deck/board that sits above the poles.
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=15.0, velocity=2.0, lower=0.0, upper=r.fold_upper),
        )


def _build_bare_feet(model, r, mats) -> None:
    """No undercarriage. A basket rests on its own hull; a flat board gets four
    short rubber foot stubs embedded into its underside.
    (spine_board 'No wheels or legs' / basket sits on ground)."""
    if r.deck == "basket_shell":
        return  # the Stokes hull rests on the ground; no separate feet.
    deck = model.get_part("deck_frame")
    bz = r.base_z
    stub_len = bz + 0.010  # from the floor up into the board underside
    for i, (sx, sy) in enumerate([(-0.42, -0.4), (-0.42, 0.4), (0.42, -0.4), (0.42, 0.4)]):
        deck.visual(
            Cylinder(radius=0.022, length=stub_len),
            origin=Origin(xyz=(sx * r.deck_len, sy * r.deck_width, stub_len * 0.5)),
            material=mats["strap"],
            name=f"foot_stub_{i}", material_class_id="rubber.smooth_plain",
        )


_UNDER_BUILDERS = {
    "scissor_wheeled": _build_scissor_wheeled,
    "foldleg_wheeled": _build_foldleg_wheeled,
    "telescoping_wheeled": _build_telescoping_wheeled,
    "carry_poles": _build_carry_poles,
    "bare_feet": _build_bare_feet,
}


# --------------------------------------------------------------------------- #
# Slot C — restraint
# --------------------------------------------------------------------------- #


def _build_folding_rails(model, r, mats) -> None:
    """Two folding tubular side rails (REVOLUTE, o1 L164-L180 / o2 L612-L629)."""
    deck = model.get_part("deck_frame")
    hw = r.half_w
    tz = r.top_z
    front_x = r.backrest_hinge_x if r.has_backrest else r.head_x
    rail_x0 = front_x + 0.12
    rail_x1 = r.foot_x - 0.20
    rail_len = rail_x1 - rail_x0
    rail_cx = 0.5 * (rail_x0 + rail_x1)
    for idx, ys in enumerate((1.0, -1.0)):
        rail = model.part(f"side_rail_{idx}")
        # local origin at the hinge line; lower tube runs along x (captured pin).
        _tube(rail, (-rail_len * 0.5, 0.0, 0.0), (rail_len * 0.5, 0.0, 0.0), 0.011, mats["frame"], "lower_tube")
        _tube(rail, (-rail_len * 0.5 + 0.04, 0.0, 0.185), (rail_len * 0.5 - 0.04, 0.0, 0.185), 0.012, mats["frame"], "top_guard_tube")
        for j, xf in enumerate((-0.42, 0.0, 0.42)):
            _tube(rail, (rail_len * xf, 0.0, 0.0), (rail_len * xf, 0.0, 0.185), 0.010, mats["frame"], f"upright_{j}")
        _box(rail, "release_tab", (0.055, 0.018, 0.018), (rail_len * 0.40, 0.0, 0.020), mats["release"])
        axis = (-1.0, 0.0, 0.0) if ys > 0 else (1.0, 0.0, 0.0)
        model.articulation(
            f"deck_to_side_rail_{idx}",
            ArticulationType.REVOLUTE,
            parent=deck,
            child=rail,
            origin=Origin(xyz=(rail_cx, ys * hw, tz + 0.010)),
            axis=axis,
            motion_limits=MotionLimits(effort=20.0, velocity=1.5, lower=0.0, upper=r.fold_upper),
        )


def _build_strap_harness(model, r, mats) -> None:
    """Cross-strap + shoulder harness restraint (deck visuals only, strap_harness)."""
    deck = model.get_part("deck_frame")
    hw = r.half_w
    if r.deck == "basket_shell":
        # cross straps lie on the head-half perforated floor pan (x < 0).
        half_len = r.deck_len * 0.50
        floor_cx = -half_len * 0.46
        floor_z = r.base_z + 0.02
        floor_w = hw * 1.55
        for tag, dx in (("chest", -0.22), ("waist", 0.20)):
            xx = floor_cx + dx * half_len
            _box(deck, f"{tag}_strap", (0.040, floor_w * 0.85, 0.008), (xx, 0.0, floor_z + 0.004), mats["strap"])
            for side, ys in (("l", -1.0), ("r", 1.0)):
                _box(deck, f"{tag}_buckle_{side}", (0.030, 0.024, 0.016), (xx, ys * floor_w * 0.40, floor_z + 0.010), mats["release"])
        return
    tz = r.top_z
    strap_w = r.deck_width + 0.02
    # straps span the seat/foot section only (clear of any raised backrest).
    seat_start = (r.backrest_hinge_x + 0.06) if r.has_backrest else (r.head_x + 0.10)
    seat_span = r.foot_x - 0.10 - seat_start
    for tag, frac in (("chest", 0.20), ("waist", 0.52), ("leg", 0.84)):
        xx = seat_start + seat_span * frac
        _box(deck, f"{tag}_strap", (0.040, strap_w, 0.010), (xx, 0.0, tz + 0.010), mats["strap"])
        for side, ys in (("l", -1.0), ("r", 1.0)):
            _box(deck, f"{tag}_buckle_{side}", (0.030, 0.024, 0.018), (xx, ys * (hw - 0.02), tz + 0.010), mats["release"])
    # Y-shaped shoulder harness near the chest end of the seat section.
    sx = seat_start + seat_span * 0.12
    _box(deck, "shoulder_stem", (0.10, 0.038, 0.010), (sx + 0.06, 0.0, tz + 0.010), mats["strap"])
    _tube(deck, (sx + 0.02, -0.02, tz + 0.013), (sx + 0.16, -hw * 0.7, tz + 0.013), 0.014, mats["strap"], "shoulder_left")
    _tube(deck, (sx + 0.02, 0.02, tz + 0.013), (sx + 0.16, hw * 0.7, tz + 0.013), 0.014, mats["strap"], "shoulder_right")


def _build_immobilizer_blocks(model, r, mats) -> None:
    """Two hinged head-immobilizer ear blocks (REVOLUTE, spine_board L118-L312)."""
    deck = model.get_part("deck_frame")
    hw = r.half_w
    tz = r.top_z
    head_x = r.head_x + 0.26
    edge_y = hw - 0.02
    for idx, ys in enumerate((1.0, -1.0)):
        block = model.part(f"imm_block_{idx}")
        inward_y = -0.028 * ys
        _box(block, "block_base", (0.12, 0.055, 0.10), (0.0, inward_y, 0.052), mats["surface"])
        block.visual(
            _rounded_pad(0.08, 0.12, 0.018, 0.012, "block_pad"),
            origin=Origin(xyz=(0.0, inward_y - 0.034 * ys, 0.050), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["strap"],
            name="block_pad", material_class_id="fabric.flexible_foam",
        )
        _box(block, "hinge_tab", (0.040, 0.014, 0.008), (0.0, 0.0, 0.004), mats["hub"])
        axis = (-1.0, 0.0, 0.0) if ys > 0 else (1.0, 0.0, 0.0)
        model.articulation(
            f"deck_to_block_{idx}",
            ArticulationType.REVOLUTE,
            parent=deck,
            child=block,
            origin=Origin(xyz=(head_x, ys * edge_y, tz + 0.006)),
            axis=axis,
            motion_limits=MotionLimits(effort=8.0, velocity=1.5, lower=0.0, upper=r.fold_upper),
        )


_RESTRAINT_BUILDERS = {
    "folding_rails": _build_folding_rails,
    "strap_harness": _build_strap_harness,
    "immobilizer_blocks": _build_immobilizer_blocks,
}


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #


def build_stretcher(
    config: StretcherConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"stretcher_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in pal.items()
    }

    _DECK_BUILDERS[r.deck](model, r, mats)
    _UNDER_BUILDERS[r.undercarriage](model, r, mats)
    _RESTRAINT_BUILDERS[r.restraint](model, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_stretcher(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_stretcher(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #


def _allow_captured_pins(ctx, model, r) -> None:
    """Element-scoped allowances for captured-pin hinges / sliding rails / axles."""
    deck = model.get_part("deck_frame")
    # backrest hinge weldment captured against the deck socket.
    if r.has_backrest:
        backrest = model.get_part("backrest")
        for elem in ("hinge_bar", "back_side_0", "back_side_1"):
            ctx.allow_overlap(backrest, deck, elem_a=elem, elem_b="back_hinge_socket",
                              reason="Backrest hinge weldment is captured against the deck hinge socket.")
    # basket fold barrels interleave.
    if r.deck == "basket_shell":
        foot = model.get_part("foot_basket")
        # The two basket halves meet along the fold-line seam (rims, floor pans,
        # corner ribs, and hinge hardware coincide at x=0, y=+-half_w).
        seam_elems = ("rim_tube", "floor_pan", "hinge_barrel", "hinge_plate",
                      "rib_0", "rib_4", "fold_stanchion_0", "fold_stanchion_1")
        for ea in seam_elems:
            for eb in seam_elems:
                ctx.allow_overlap(deck, foot, elem_a=ea, elem_b=eb,
                                  reason="Basket halves meet along the captured center-fold seam.")
    # carriage lift: inner sliders nest into deck sleeves; wheels pierced by axle.
    if r.undercarriage in _CARRIAGE_WHEELED:
        carriage = model.get_part("lower_carriage")
        col_xs_n = len({x for x, _ in _caster_rows(r)})
        col_ys_n = len({y for _, y in _caster_rows(r)})
        for ci in range(col_xs_n):
            for si in range(col_ys_n):
                ctx.allow_overlap(carriage, deck, elem_a=f"inner_leg_{ci}_{si}", elem_b=f"leg_sleeve_{ci}_{si}",
                                  reason="Telescoping inner slider nests inside the deck-fixed outer sleeve.")
        for i in range(r.caster_count):
            wheel = model.get_part(f"caster_{i}")
            for welem in ("tire", "hub", "spin_marker"):
                ctx.allow_overlap(wheel, carriage, elem_a=welem, elem_b=f"caster_fork_{i}",
                                  reason="Caster wheel is captured on its carriage fork stub.")
        # Scissor cross tubes tuck up between the deck-fixed sleeves as it retracts.
        if r.undercarriage == "scissor_wheeled":
            n_ci = len({x for x, _ in _caster_rows(r)})
            n_si = len({y for _, y in _caster_rows(r)})
            for si in range(n_si):
                for sc in (f"scissor_a_{si}", f"scissor_b_{si}"):
                    for ci in range(n_ci):
                        for sj in range(n_si):
                            ctx.allow_overlap(carriage, deck, elem_a=sc, elem_b=f"leg_sleeve_{ci}_{sj}",
                                              reason="Scissor cross tubes tuck between the deck sleeves during lift.")
    # foldleg hinges captured in sockets; caster hubs pierced by leg axles.
    if r.undercarriage == "foldleg_wheeled":
        model.get_part("head_leg")
        model.get_part("foot_leg")
        for leg_name, sock in (("head_leg", "head_leg_socket"), ("foot_leg", "foot_leg_socket")):
            leg = model.get_part(leg_name)
            for elem in ("top_hinge", "upper_leg_0", "upper_leg_1"):
                for deck_elem in (sock, "deck_board", "side_frame_0", "side_frame_1"):
                    ctx.allow_overlap(leg, deck, elem_a=elem, elem_b=deck_elem,
                                      reason="Folding-leg hinge weldment is captured under the deck / in its socket.")
        wheeled_legs = {"foot_leg"} if r.caster_count == 2 else {"head_leg", "foot_leg"}
        ci = 0
        for leg_name in ("head_leg", "foot_leg"):
            if leg_name not in wheeled_legs:
                continue
            leg = model.get_part(leg_name)
            for si in range(2):
                wheel = model.get_part(f"caster_{ci}")
                for welem in ("tire", "hub", "spin_marker"):
                    for lelem in (f"wheel_axle_{si}", f"lower_leg_{si}", f"caster_mount_{si}"):
                        ctx.allow_overlap(wheel, leg, elem_a=welem, elem_b=lelem,
                                          reason="Caster wheel is captured on the leg fork/axle.")
                ci += 1
    # carry-pole spreader hinges captured against the pole mount brackets.
    if r.undercarriage == "carry_poles":
        for tag in ("head", "foot"):
            sp = model.get_part(f"{tag}_spreader")
            for elem_a in ("hinge_arm", "latch_arm", "spreader_bar"):
                for i in range(2):
                    ctx.allow_overlap(sp, deck, elem_a=elem_a, elem_b=f"{tag}_mount_{i}",
                                      reason="Spreader hinge/latch arm is captured against its pole mount bracket.")
    # side rails captured in sockets.
    if r.restraint == "folding_rails":
        for idx in range(2):
            rail = model.get_part(f"side_rail_{idx}")
            for elem in ("lower_tube", "upright_0", "upright_1", "upright_2"):
                for deck_elem in (f"rail_socket_{idx}", "deck_board"):
                    ctx.allow_overlap(rail, deck, elem_a=elem, elem_b=deck_elem,
                                      reason="Side-rail hinge weldment is captured in its deck socket.")
    # immobilizer blocks captured against the head block socket.
    if r.restraint == "immobilizer_blocks":
        for idx in range(2):
            block = model.get_part(f"imm_block_{idx}")
            for elem_a in ("hinge_tab", "block_base"):
                ctx.allow_overlap(block, deck, elem_a=elem_a, elem_b="block_socket",
                                  reason="Immobilizer block hinge tab is captured against the head block socket.")


def _has_movable_joint(model) -> bool:
    for j in model.articulations:
        if j.articulation_type != ArticulationType.FIXED:
            return True
    return False


def run_stretcher_tests(object_model: ArticulatedObject, config: StretcherConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    _allow_captured_pins(ctx, object_model, r)
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # --- category identity ---
    deck = object_model.get_part("deck_frame")
    ctx.check("deck_frame root present", deck is not None)
    ctx.check(
        "stretcher keeps at least one non-fixed joint",
        _has_movable_joint(object_model),
    )
    deck_aabb = ctx.part_world_aabb(deck)
    if deck_aabb is not None and r.deck != "basket_shell":
        # (basket deck_frame is only the head half; the fold test covers it.)
        ext_x = deck_aabb[1][0] - deck_aabb[0][0]
        ctx.check(
            "deck length is stretcher-sized",
            1.5 < ext_x < 2.7,
            details=f"ext_x={ext_x:.3f}",
        )

    # --- caster count matches multiplicity axis ---
    n_caster = sum(1 for p in object_model.parts if p.name.startswith("caster_"))
    ctx.check(
        "caster count matches resolved multiplicity",
        n_caster == r.caster_count,
        details=f"found={n_caster}, expected={r.caster_count}",
    )

    # --- targeted motion per mechanism (Rule 5) ---
    if r.has_backrest:
        backrest = object_model.get_part("backrest")
        bj = object_model.get_articulation("deck_to_backrest")
        rest = ctx.part_world_aabb(backrest)
        with ctx.pose({bj: r.backrest_upper}):
            raised = ctx.part_world_aabb(backrest)
        if rest is not None and raised is not None:
            ctx.check(
                "backrest hinge raises the head section",
                raised[1][2] > rest[1][2] + 0.05,
                details=f"rest_top={rest[1][2]:.3f}, raised_top={raised[1][2]:.3f}",
            )

    if r.deck == "basket_shell":
        foot = object_model.get_part("foot_basket")
        fj = object_model.get_articulation("fold_hinge")
        deployed = ctx.part_world_aabb(foot)
        with ctx.pose({fj: 1.4}):
            folded = ctx.part_world_aabb(foot)
        if deployed is not None and folded is not None:
            ctx.check(
                "basket fold raises the foot half",
                folded[1][2] > deployed[1][2] + 0.10,
                details=f"deployed_top={deployed[1][2]:.3f}, folded_top={folded[1][2]:.3f}",
            )

    if r.undercarriage in _CARRIAGE_WHEELED:
        carriage = object_model.get_part("lower_carriage")
        hj = object_model.get_articulation("height_slide")
        rest = ctx.part_world_position(carriage)
        with ctx.pose({hj: r.height_travel}):
            raised = ctx.part_world_position(carriage)
        if rest is not None and raised is not None:
            ctx.check(
                "height slide retracts the carriage upward",
                raised[2] > rest[2] + 0.05,
                details=f"rest_z={rest[2]:.3f}, raised_z={raised[2]:.3f}",
            )

    if r.undercarriage == "foldleg_wheeled":
        foot_leg = object_model.get_part("foot_leg")
        fj = object_model.get_articulation("deck_to_foot_leg")
        rest = ctx.part_world_aabb(foot_leg)
        with ctx.pose({fj: fj.motion_limits.upper}):
            folded = ctx.part_world_aabb(foot_leg)
        if rest is not None and folded is not None:
            ctx.check(
                "folding leg swings inward when folded",
                0.5 * (folded[0][0] + folded[1][0]) < 0.5 * (rest[0][0] + rest[1][0]) - 0.05,
                details=f"rest_cx={0.5*(rest[0][0]+rest[1][0]):.3f}, folded_cx={0.5*(folded[0][0]+folded[1][0]):.3f}",
            )

    if r.undercarriage == "carry_poles":
        sp = object_model.get_part("head_spreader")
        sj = object_model.get_articulation("deck_to_head_spreader")
        rest = ctx.part_world_aabb(sp)
        with ctx.pose({sj: r.fold_upper}):
            folded = ctx.part_world_aabb(sp)
        if rest is not None and folded is not None:
            ctx.check(
                "carry-pole spreader folds",
                abs(folded[1][2] - rest[1][2]) > 0.02 or abs(folded[1][1] - rest[1][1]) > 0.02,
                details=f"rest={rest}, folded={folded}",
            )

    if r.restraint == "folding_rails":
        rail = object_model.get_part("side_rail_0")
        rj = object_model.get_articulation("deck_to_side_rail_0")
        up = ctx.part_world_aabb(rail)
        with ctx.pose({rj: r.fold_upper * 0.9}):
            down = ctx.part_world_aabb(rail)
        if up is not None and down is not None:
            ctx.check(
                "folding side rail drops outward",
                down[1][2] < up[1][2] - 0.05,
                details=f"up_top={up[1][2]:.3f}, down_top={down[1][2]:.3f}",
            )

    if r.restraint == "immobilizer_blocks":
        block = object_model.get_part("imm_block_0")
        bj = object_model.get_articulation("deck_to_block_0")
        up = ctx.part_world_aabb(block)
        with ctx.pose({bj: r.fold_upper * 0.9}):
            down = ctx.part_world_aabb(block)
        if up is not None and down is not None:
            ctx.check(
                "immobilizer block folds outward",
                down[1][1] > up[1][1] + 0.02 or down[0][1] < up[0][1] - 0.02,
                details=f"up={up}, down={down}",
            )

    # --- full sampled-pose collision sweep (Rule 5) ---
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    return ctx.report()


__all__ = [
    "Deck",
    "Undercarriage",
    "Restraint",
    "PaletteStyle",
    "StretcherConfig",
    "ResolvedStretcherConfig",
    "build_stretcher",
    "build_seeded_stretcher",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "slot_choices_for_config",
    "run_stretcher_tests",
]
