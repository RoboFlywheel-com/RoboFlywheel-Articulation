# SPDX-License-Identifier: Apache-2.0

"""pictureX / 0611 / drafting_table_with_adjustable_tilt_surface (modular).

Spec: articraft_template_authoring/specs_modular_v1/
      pictureX_0611_drafting_table_with_adjustable_tilt_surface.md

Identity = a wide drawing board carried on a grounded support that has BOTH a real
PRISMATIC height stage AND a real REVOLUTE tilt hinge with visible angle-hold
hardware. The tilt joint is the point of the subcategory: a fixed-top table is out
of category, so every seed emits ``board_tilt`` with a usable (>= 0.50 rad) range.

Sources (all 8 five-star records read in full; 5 origins + 3 user-confirmed forks):
  O1 rec_..._001  portable tabletop A-frame board  (parallel rule + clamp knobs)
  O2 rec_..._002  four-leg shelf drafting table    (telescoping legs, organizer)
  O3 rec_..._003  twin-post trestle                (center pivot, curved stays)
  O4 rec_..._004  pale slatted-top adjustable      (twin pedestals, slat board)
  O5 rec_..._005  split-wing / maple trestle       (sleeve+post carriage)
  F_split  rec_picturex0611_drafting_table_fork_split_top_dual_surface_20260714
  F_spring rec_picturex0611_drafting_table_fork_counterbalance_spring_tilt_20260714
  F_column rec_picturex0611_drafting_table_fork_single_pedestal_column_20260714

Pattern = mixed: a grounded root carries a PRISMATIC height stage whose moving
member is the ``mount``; the mount then carries the REVOLUTE board (parallel
children), and the board carries the angle-hold stays + optional parallel rule.

Slots: support_base (5, (1) skeleton) / board_top (4, (3) primary form) /
tilt_stay (4, (2) mechanism) / board_accessory (2).

Rules:
  Rule 1 - non-articulating hardware (rails, sleeves, organizer, slats, grain,
    ledges, split-top shelf, feet) is a host ``.visual(...)``. Real parts are only
    the height members, the board, the stays/lever, the rule and the knobs.
  Rule 2 - every non-FIXED joint here is a captured pin/trunnion/sleeve fit
    (barrel-around-pin, tube-in-sleeve, shaft-in-socket). ``MatingContract``
    assumes two axis-aligned faces in contact, which none of these are (the board
    subtree carries the authored pre-tilt at closed pose), so they take the
    documented grandfather route (omit ``mating=``) and are kept honest with
    element-scoped ``allow_overlap`` + ``expect_contact/expect_overlap`` mirroring
    the sources. The one genuine axis-aligned face pair -- the height clamp knob
    stem end against the flat sleeve/boss face -- DOES declare a MatingContract.
  Rule 3 - part tree / joint topology / primitive family derive from the declared
    sources; meshes stay meshes (ExtrudeGeometry board, ExtrudeWithHolesGeometry
    sleeve, tube_from_spline_points brace, KnobGeometry knob).
  Rule 5 - ``fail_if_parts_overlap_in_sampled_poses`` + one targeted ``ctx.pose``
    per mechanism (tilt / height / stay coupling / rule / knob).
  Rule 7 - every allowance names an exact element pair; zero whole-part scope.

Clearance invariant (this is why the template is collision-free by construction,
not by sweep-tuning):
  Every board-local point has ``z_local >= -Z_UNDER``. The board rotates about
  ``+x`` through total angle ``a in [0, tilt_sign*theta_max]``, so the lowest world
  z any board point can reach is ``hinge_z - (drop_arm*sin(theta_max) + Z_UNDER)``
  == ``hinge_z - front_drop``. Since ``hinge_z = mount_top_z + tilt_gap`` and
  ``tilt_gap = max(front_drop, MIN_TILT_GAP) + CLEAR``, the board never descends
  below ``mount_top_z + CLEAR``. All inboard mount structure is capped at
  ``mount_top_z``; everything the mount puts above it is either ON the hinge axis
  (captured by the board barrel) or outboard of the board width.
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
    KnobGeometry,
    KnobGrip,
    MatingContract,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot value spaces
# ---------------------------------------------------------------------------
SupportBase = Literal[
    "four_leg_downleg",
    "sleeve_post_carriage",
    "twin_post_trestle",
    "twin_pedestal_lift",
    "single_pedestal_column",
]
BoardTop = Literal[
    "rounded_laminate_panel",
    "slatted_wood_board",
    "framed_batten_board",
    "split_top_side_shelf",
]
TiltStay = Literal[
    "curved_spline_braces",
    "counterbalance_spring_arms",
    "folding_bar_stays",
    "lever_angle_lock",
]
BoardAccessory = Literal["parallel_rule", "plain_surface"]
PaletteStyle = Literal[
    "school_white_blue",
    "crimson_wood_black",
    "honey_beech_gray",
    "pale_maple_black",
    "cool_white_graphite",
]

SUPPORT_BASES: tuple[SupportBase, ...] = (
    "four_leg_downleg",
    "sleeve_post_carriage",
    "twin_post_trestle",
    "twin_pedestal_lift",
    "single_pedestal_column",
)
BOARD_TOPS: tuple[BoardTop, ...] = (
    "rounded_laminate_panel",
    "slatted_wood_board",
    "framed_batten_board",
    "split_top_side_shelf",
)
TILT_STAYS: tuple[TiltStay, ...] = (
    "curved_spline_braces",
    "counterbalance_spring_arms",
    "folding_bar_stays",
    "lever_angle_lock",
)
BOARD_ACCESSORIES: tuple[BoardAccessory, ...] = ("parallel_rule", "plain_surface")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "school_white_blue",
    "crimson_wood_black",
    "honey_beech_gray",
    "pale_maple_black",
    "cool_white_graphite",
)

# Gate G1 (spec Compatibility Gates): the split top's fixed side shelf needs a
# mount with a wide transverse member to carry its brackets. The two centre-pivot
# skeletons have no such member -> the shelf would float.
SHELF_OK: frozenset[SupportBase] = frozenset(
    {"four_leg_downleg", "sleeve_post_carriage", "twin_pedestal_lift"}
)
# Centre-pivot skeletons (O3, F_column): the board straddles the pivot line, so a
# larger total tilt stays mechanically honest (gate G3).
CENTER_PIVOT: frozenset[SupportBase] = frozenset(
    {"twin_post_trestle", "single_pedestal_column"}
)
# Wood-framed skeleton (O3): the base structure itself is stained timber.
WOOD_FRAMED: frozenset[SupportBase] = frozenset({"twin_post_trestle"})

# Fraction of board depth that sits IN FRONT of the tilt axis. Read off each
# source's board box vs its tilt-joint origin:
#   O5 board y in [0, 0.56] about a front-edge pivot            -> ~0.08
#   O3 board y in [-0.34, +0.34] about a centre pivot           -> 0.50
#   F_column board y in [-0.60, -0.03] about a rear pivot       -> ~0.70
#   O4 board y in [-0.60, -0.03] about a rear pivot             -> 0.70
#   O2 board y in [-0.44, +0.11] about a rear-of-centre pivot   -> ~0.72
PIVOT_FRAC: dict[SupportBase, float] = {
    "four_leg_downleg": 0.72,
    "sleeve_post_carriage": 0.08,
    "twin_post_trestle": 0.50,
    "twin_pedestal_lift": 0.70,
    "single_pedestal_column": 0.50,
}

# ---------------------------------------------------------------------------
# Palettes -- one realistic colorway per source record's observed finish.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    # O2: cool gray laminate board, white powder-coated steel, blue-gray organizer.
    "school_white_blue": {
        "board": (0.78, 0.84, 0.86, 1.0),
        "board_edge": (0.57, 0.66, 0.69, 1.0),
        "grain": (0.66, 0.74, 0.78, 1.0),
        "frame": (0.88, 0.89, 0.88, 1.0),
        "frame_edge": (0.72, 0.74, 0.73, 1.0),
        "accent": (0.31, 0.47, 0.55, 1.0),
    },
    # O3: reddish-brown stained wood board and frame, blackened steel hardware.
    "crimson_wood_black": {
        "board": (0.48, 0.155, 0.095, 1.0),
        "board_edge": (0.245, 0.070, 0.040, 1.0),
        "grain": (0.36, 0.105, 0.060, 1.0),
        "frame": (0.36, 0.105, 0.060, 1.0),
        "frame_edge": (0.245, 0.070, 0.040, 1.0),
        "accent": (0.075, 0.067, 0.060, 1.0),
    },
    # O4: honey-beech slatted board, warm gray steel frame, black polymer.
    "honey_beech_gray": {
        "board": (0.78, 0.54, 0.29, 1.0),
        "board_edge": (0.65, 0.43, 0.23, 1.0),
        "grain": (0.70, 0.45, 0.23, 1.0),
        "frame": (0.60, 0.61, 0.58, 1.0),
        "frame_edge": (0.43, 0.45, 0.44, 1.0),
        "accent": (0.08, 0.085, 0.08, 1.0),
    },
    # O5: pale maple board, powder-black frame, zinc/graphite hardware.
    "pale_maple_black": {
        "board": (0.83, 0.70, 0.49, 1.0),
        "board_edge": (0.74, 0.59, 0.39, 1.0),
        "grain": (0.68, 0.54, 0.35, 1.0),
        "frame": (0.055, 0.060, 0.065, 1.0),
        "frame_edge": (0.12, 0.13, 0.14, 1.0),
        "accent": (0.58, 0.61, 0.64, 1.0),
    },
    # O1: cool white laminate board with black edge band, black stand, aluminum.
    "cool_white_graphite": {
        "board": (0.91, 0.94, 0.94, 1.0),
        "board_edge": (0.035, 0.040, 0.042, 1.0),
        "grain": (0.80, 0.84, 0.85, 1.0),
        "frame": (0.045, 0.050, 0.052, 1.0),
        "frame_edge": (0.10, 0.11, 0.11, 1.0),
        "accent": (0.72, 0.75, 0.76, 1.0),
    },
}
# Near-constant hardware finishes (present in every source).
_HARDWARE: dict[str, tuple[float, float, float, float]] = {
    "hardware": (0.56, 0.59, 0.59, 1.0),
    "rubber": (0.025, 0.027, 0.030, 1.0),
    "bright": (0.76, 0.77, 0.73, 1.0),
    "brass": (0.72, 0.55, 0.18, 1.0),
}

# ---------------------------------------------------------------------------
# Single-sourced geometry constants (world metres). +Y = back, -Y = front (user
# side), X = width, Z = up. Each carries its observational basis (Contract 3e).
# ---------------------------------------------------------------------------
BOARD_W = 1.02        # nominal board width; sources span 0.82 (O1) .. 1.22 (O3).
BOARD_D = 0.60        # nominal board depth; sources span 0.55 (O2/O5) .. 0.68 (O3).
BOARD_T = 0.026       # panel thickness; O2 0.018, O5 0.023, O4 0.028, O3 0.032.
MOUNT_TOP_Z = 0.62    # frame-top height at rest; O2 rails 0.655, O5 sleeve top 0.57.
BASE_Y_HALF = 0.30    # base footprint half-depth; O3 feet 0.60 long, O5 0.50.
TUBE = 0.035          # frame tube cross-section; O2 0.030-0.034, O5 0.040.
CLEAR = 0.030         # board-to-frame swept clearance floor.
MIN_TILT_GAP = 0.200  # min hinge-above-frame gap giving the angle-hold stay a real
                      # envelope; O3 seats its pivot 0.28 above the sleeve top.
Z_UNDER = 0.030       # deepest board hardware below the pivot plane (barrel r=0.021).
PIN_R = 0.012         # hinge pin radius; O5 0.010, drafting_table 0.012.
BARREL_R = 0.021      # board hinge barrel radius; O5 0.015, O3 0.022.
PANEL_BOTTOM = 0.014  # panel underside above the axis so the mount pin (r=PIN_R)
                      # clears it by 2 mm while the barrel still captures the pin.
SLAT_H = 0.004        # O4 slat veneer thickness (L297-L313).

# Telescoping fit (single-sourced: every sleeve/post pair in the template uses it).
# A stretcher meeting a sleeve must die INSIDE the tube wall -- past the outer face
# so it connects, short of the cavity so it never spears the sliding post.
SLEEVE_OUTER = 0.052  # O5 L140-L151 outer square tube across flats.
SLEEVE_INNER = 0.036  # cavity across flats.
POST_W = 0.030        # inner telescoping member across flats.
STRETCHER_STOP = 0.022  # distance from sleeve centre: inside wall (0.026), clear of post (0.015).

# Sleeve/post stack planes. These are the ONLY statements of where the collar and
# the guide block sit inside the telescoping fit; both the emitters and the travel
# solver read them, so the pair can never drift apart (Contract 3c).
COLLAR_H = 0.024          # sleeve collar ring height.
COLLAR_DROP = 0.010       # collar centre below the sleeve top.
COLLAR_BELOW_TOP = COLLAR_DROP + COLLAR_H * 0.5   # collar underside below sleeve top.
GUIDE_H = 0.026           # polymer guide block height.
GUIDE_RISE = 0.040        # guide-block centre above the post foot.
GUIDE_ABOVE_FOOT = GUIDE_RISE + GUIDE_H * 0.5     # guide-block top above the post foot.
TELESCOPE_STOP_CLEAR = 0.006  # air the guide block keeps below the collar at full lift.
POST_LEN = 0.30           # twin-post inner member length (O5 L186-L192).
LEG_LEN = 0.34            # four-leg down-leg length (O2 L206-L226).
TWIN_SLEEVE_DROP = 0.10   # twin sleeve top below the frame top (O5 L140-L151).
LEG_SLEEVE_BOT = 0.34     # four-leg sleeve foot height (O2 L118-L123).
LEG_ENGAGE = 0.090        # down-leg head inside its sleeve at full extension.
FOOT_RAIL_H = 0.040       # twin-base foot rail height (O5 L128-L139).
WELD_EMBED = 0.004        # how far a welded member sinks into the face it lands on.
CROSS_RAIL_H = 0.050      # moving cross rail section (O4 L185-L190).
CROSS_RAIL_CLEAR = 0.008  # air the moving rail keeps above the static sleeve collar.
RAIL_POST_WELD = 0.010    # rail end inside the DRIVING post's tube (same part: a weld).
RAIL_POST_CLEAR = 0.007   # air the rail keeps from the DRIVEN post's tube (other part).

# Single pedestal column stack (F_column L120-L180).
COLUMN_OUTER = 0.082      # hollow outer column across flats.
COLUMN_INNER = 0.062      # cavity across flats.
COLUMN_DROP = 0.12        # outer column top below the frame top.
COLUMN_COLLAR_H = 0.030
COLUMN_COLLAR_DROP = 0.014
COLUMN_LEN = 0.40         # inner lift column length.
COLUMN_GUIDE_RISE = 0.040
COLUMN_GUIDE_H = 0.026

# Height clamp knob (O4 L406-L441). The boss face is a DATUM: the joint origin, the
# stem and the MatingContract all derive from it instead of restating it.
KNOB_BOSS_T = 0.020       # boss thickness along the outward axis.
# Boss centre outboard of the host face it grows from. MUST stay < KNOB_BOSS_T/2 so
# the boss's inner face lands INSIDE that face and the boss is really welded to it;
# at the old 0.012 the boss started 2 mm proud of the sleeve and floated.
KNOB_BOSS_INSET = 0.008
KNOB_STEM_LEN = 0.026     # stem length proud of the boss face.
KNOB_STEM_EMBED = 0.001   # stem seats this far INTO the boss: real contact, not air.

# Angle-lock lever pivot (O4 L376-L404).
LOCK_BRACKET_FACE = 0.050  # bracket outer face outboard of |x|=outboard_x.
LEVER_PIN_R = 0.009
LEVER_PIN_LEN = 0.040
LEVER_HUB_LEN = 0.030
LEVER_HUB_CLEAR = 0.003    # air between the swinging hub and the static bracket face.

# Parallel rule stack (O1 L210-L310). RULE_PAD_BED is the ONE intentional contact
# with the board face; every other rule element stands off the deck plane.
RULE_PAD_T = 0.003
RULE_PAD_BED = 0.001
RULE_CARRIAGE_H = 0.020
RULE_SHAFT_CLEAR = 0.002   # air the knob shaft keeps above the end carriage.
STAY_PANEL_CLEAR = 0.002   # air the swinging stay bracket keeps below the panel.
STAY_PIN_R = 0.014         # board-mounted stay pin radius (O3 brace_pin L196-L205).

SIDES: tuple[tuple[str, float], ...] = (("0", -1.0), ("1", 1.0))


# ---------------------------------------------------------------------------
# Datums (Contract 3c/3e). Each is the single statement of a plane that more than
# one element depends on. Consumers derive from these; they never restate them.
# ---------------------------------------------------------------------------
def _mount_top_underside_z(r) -> float:
    """THE underside of the rigid frame-top rectangle.

    ``_emit_mount_top`` lays every top rail centred at ``mount_top_z - TUBE/2``, so
    the rectangle spans ``[mount_top_z - TUBE, mount_top_z]`` and its underside is
    the plane every column that CARRIES the mount top must stop at. Restating this
    as ``mount_top_z - 0.020`` is what drove the frame rails 15 mm (TUBE - 0.020)
    through the second post on every twin-post seed.
    """
    return r.mount_top_z - TUBE


def _sleeve_collar_bottom_z(sleeve_top: float) -> float:
    """Underside of the sleeve collar -- the hard stop the guide block rises toward."""
    return sleeve_top - COLLAR_BELOW_TOP


def _guide_block_top_z(post_top: float, post_len: float) -> float:
    """Top of the polymer guide block riding inside the sleeve."""
    return post_top - post_len + GUIDE_ABOVE_FOOT


def _sleeve_collar_top_z(sleeve_top: float) -> float:
    return sleeve_top - COLLAR_DROP + COLLAR_H * 0.5


def _cross_rail_z(r) -> float:
    """Centre height of the twin-post moving cross rail and its receiving socket.

    The rail rides on the MOVING posts while the sleeve collar is STATIC, so its
    height is derived from that collar's top face plus a real clearance -- it is the
    lowest the rail may sit and still sweep the whole height travel without
    striking the collar. It must also stay under the frame-top underside it hangs
    below (asserted in run_tests).
    """
    return _sleeve_collar_top_z(_twin_sleeve_top_z(r)) + CROSS_RAIL_CLEAR + CROSS_RAIL_H * 0.5


def _twin_sleeve_top_z(r) -> float:
    """Top of a twin-post outer sleeve (O5 L140-L151): the post stands proud of it."""
    return r.mount_top_z - TWIN_SLEEVE_DROP


def _leg_top_z(r) -> float:
    """Top of a four-leg down-leg at full extension. It stays LEG_ENGAGE inside its
    sleeve, which is what bounds the retraction travel (see _max_height_travel)."""
    return LEG_SLEEVE_BOT + LEG_ENGAGE


def _max_height_travel(r) -> float:
    """Travel the realized telescoping stack can actually accept (Contract 3e).

    The height stage is bounded by real hardware, not by taste: a twin post rises
    until its guide block reaches the sleeve collar, and a four-leg down-leg
    retracts until its head reaches the frame-top underside. Freezing the domain at
    0.18 m instead of solving it is what rammed the guide block 17 mm into the
    collar on every seed that sampled a long travel.
    """
    if r.support_base == "four_leg_downleg":
        return _mount_top_underside_z(r) - _leg_top_z(r) - TELESCOPE_STOP_CLEAR
    if r.support_base == "single_pedestal_column":
        guide_top = _column_guide_top_z(r)
        return _column_collar_bottom_z(r) - guide_top - TELESCOPE_STOP_CLEAR
    return (
        _sleeve_collar_bottom_z(_twin_sleeve_top_z(r))
        - _guide_block_top_z(_mount_top_underside_z(r), POST_LEN)
        - TELESCOPE_STOP_CLEAR
    )


def _column_top_z(r) -> float:
    """Top of the single pedestal's hollow outer column (F_column L120-L140)."""
    return r.mount_top_z - COLUMN_DROP


def _column_collar_bottom_z(r) -> float:
    return _column_top_z(r) - COLUMN_COLLAR_DROP - COLUMN_COLLAR_H * 0.5


def _column_guide_top_z(r) -> float:
    return _mount_top_underside_z(r) - COLUMN_LEN + COLUMN_GUIDE_RISE + COLUMN_GUIDE_H * 0.5


def _lever_pivot_x(r) -> float:
    """THE angle-lock lever's pivot axis.

    Derived from the bracket's outer face so the swinging hub always clears the
    static bracket AND the bracket arm behind it: the hub's inboard end sits
    LEVER_HUB_CLEAR outboard of that face. Frozen at ``outboard_x + 0.052`` the hub
    reached back to ``outboard_x + 0.017`` and sliced through the bracket arm.
    """
    return r.outboard_x + LOCK_BRACKET_FACE + LEVER_HUB_CLEAR + LEVER_HUB_LEN * 0.5


def _lever_pin_center_x(r) -> float:
    """The pivot pin spans from inside the bracket out to the lever hub it carries."""
    return _lever_pivot_x(r) - LEVER_HUB_LEN * 0.5 - LEVER_HUB_CLEAR + LEVER_PIN_LEN * 0.5 - 0.012


def _rule_deck_z() -> float:
    """Rule-local z of the plane the rule body stands on: the top of its runner pads.

    The rule registers to the board's working surface (rule-local z=0). Only the pads
    may touch that surface -- every other rule element derives its height from this
    deck, because on a TILTED board the overlap prefilter is useless (the AABBs are
    all inflated by the tilt) and any resting contact becomes a real FCL hit.
    """
    return RULE_PAD_T - RULE_PAD_BED


def _knob_boss_face_x(x: float, outward: float) -> float:
    """THE outward face of a height-knob boss -- the plane the knob stem seats on.

    The boss is centred ``KNOB_BOSS_INSET`` outboard of ``x`` and is ``KNOB_BOSS_T``
    thick. Hand-writing the joint origin at ``x + outward*0.026`` instead of reading
    this face is what left every knob stem exactly 4 mm off its boss -- both a
    mating gap and a disconnected part.
    """
    return x + outward * (KNOB_BOSS_INSET + KNOB_BOSS_T * 0.5)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Geometry helpers (adapted from O2 `_add_beam` L40-L47 and O3 `_add_box` L25-L31)
# ---------------------------------------------------------------------------
def _beam_pose(p0, p1) -> tuple[Origin, float]:
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length <= 1e-9:
        raise ValueError("beam endpoints must be distinct")
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(math.sqrt(dx * dx + dy * dy), dz)
    center = ((p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5, (p0[2] + p1[2]) * 0.5)
    return Origin(xyz=center, rpy=(0.0, pitch, yaw)), length


def _beam(part, p0, p1, size, material, name, overshoot: float = 0.018) -> None:
    origin, length = _beam_pose(p0, p1)
    part.visual(
        Box((size, size, length + overshoot)), origin=origin, material=material, name=name, material_class_id="metal.generic_plain"
    )


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.generic_plain")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _square_tube_mesh(outer: float, inner: float, height: float, name: str):
    """Hollow square sleeve. Mesh family preserved from O5 `_rectangular_tube_mesh`
    (L55-L70): ExtrudeWithHolesGeometry over rounded rect profiles, never a Box."""
    geometry = ExtrudeWithHolesGeometry(
        rounded_rect_profile(outer, outer, 0.004, corner_segments=4),
        [rounded_rect_profile(inner, inner, 0.002, corner_segments=4)],
        height,
        cap=True,
        center=True,
    )
    return mesh_from_geometry(geometry, name)


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class DraftingTiltTableConfig:
    support_base: SupportBase | None = None
    board_top: BoardTop | None = None
    tilt_stay: TiltStay | None = None
    board_accessory: BoardAccessory | None = None
    palette_style: PaletteStyle = "pale_maple_black"
    board_width_scale: float = 1.0
    board_depth_scale: float = 1.0
    frame_height_scale: float = 1.0
    height_travel: float = 0.14
    tilt_total_max: float = 0.87
    authored_tilt: float = 0.21
    slat_count: int = 9
    name: str = "pictureX_0611_drafting_table_with_adjustable_tilt_surface"


@dataclass(frozen=True)
class ResolvedDraftingTiltTableConfig:
    support_base: SupportBase
    board_top: BoardTop
    tilt_stay: TiltStay
    board_accessory: BoardAccessory
    palette_style: PaletteStyle
    board_width_scale: float
    board_depth_scale: float
    frame_height_scale: float
    height_travel: float
    tilt_total_max: float
    authored_tilt: float
    slat_count: int
    name: str

    # -- single-sourced derived geometry (Contract 3c) --------------------
    @property
    def half_width(self) -> float:
        return 0.5 * BOARD_W * self.board_width_scale

    @property
    def board_depth(self) -> float:
        return BOARD_D * self.board_depth_scale

    @property
    def mount_top_z(self) -> float:
        return MOUNT_TOP_Z * self.frame_height_scale

    @property
    def pivot_frac(self) -> float:
        return PIVOT_FRAC[self.support_base]

    @property
    def y_front(self) -> float:
        return self.pivot_frac * self.board_depth

    @property
    def y_back(self) -> float:
        return (1.0 - self.pivot_frac) * self.board_depth

    @property
    def hinge_y(self) -> float:
        """Board is centred over the base footprint, so the axis shifts with pivot_frac."""
        return 0.5 * (self.y_front - self.y_back)

    @property
    def tilt_sign(self) -> float:
        """The longer half of the board is the half that rises (O4/F_column tilt the
        front up about a rear pivot; O5/O3 tilt the rear up about a front/centre one)."""
        return 1.0 if self.pivot_frac <= 0.5 else -1.0

    @property
    def drop_arm(self) -> float:
        """Board half that descends while tilting."""
        return self.y_front if self.tilt_sign > 0 else self.y_back

    @property
    def rise_arm(self) -> float:
        return self.y_back if self.tilt_sign > 0 else self.y_front

    @property
    def front_drop(self) -> float:
        return self.drop_arm * math.sin(self.tilt_total_max) + Z_UNDER

    @property
    def tilt_gap(self) -> float:
        return max(self.front_drop, MIN_TILT_GAP) + CLEAR

    @property
    def hinge_z(self) -> float:
        return self.mount_top_z + self.tilt_gap

    @property
    def outboard_x(self) -> float:
        """All mount structure above mount_top_z lives at/outside this |x|."""
        return self.half_width + 0.025

    @property
    def authored_angle(self) -> float:
        return self.tilt_sign * self.authored_tilt

    @property
    def tilt_lower(self) -> float:
        if self.tilt_sign > 0:
            return -self.authored_tilt
        return -(self.tilt_total_max - self.authored_tilt)

    @property
    def tilt_upper(self) -> float:
        if self.tilt_sign > 0:
            return self.tilt_total_max - self.authored_tilt
        return self.authored_tilt

    @property
    def flat_q(self) -> float:
        """Joint value putting the board horizontal (total angle a = 0). With a rear
        pivot the board tilts negative, so flat sits at the UPPER limit."""
        return self.tilt_lower if self.tilt_sign > 0 else self.tilt_upper

    @property
    def steep_q(self) -> float:
        """Joint value at the steepest drawing angle (|a| = tilt_total_max)."""
        return self.tilt_upper if self.tilt_sign > 0 else self.tilt_lower

    @property
    def has_shelf(self) -> bool:
        return self.board_top == "split_top_side_shelf"

    @property
    def shelf_span(self) -> float:
        return 0.26 * 2.0 * self.half_width if self.has_shelf else 0.0

    @property
    def panel_x_max(self) -> float:
        """Right edge of the tilting panel (the split top yields it to the shelf)."""
        return self.half_width - (self.shelf_span + 0.015 if self.has_shelf else 0.0)

    @property
    def panel_width(self) -> float:
        return self.panel_x_max + self.half_width

    @property
    def panel_x_center(self) -> float:
        return 0.5 * (self.panel_x_max - self.half_width)

    @property
    def board_surface_z(self) -> float:
        """Board-local z of the working surface everything on top registers to."""
        return PANEL_BOTTOM + BOARD_T + (SLAT_H if self.board_top == "slatted_wood_board" else 0.0)

    @property
    def stay_y(self) -> float:
        """Stay hangs off the rising half so its attach point never descends."""
        return self.tilt_sign * min(0.5 * self.rise_arm, 0.18)

    @property
    def stay_len(self) -> float:
        """Hanging stay length -- bounded so its foot stays CLEAR above the frame top."""
        return self.tilt_gap - 0.060

    @property
    def stay_x(self) -> float:
        return self.panel_x_max - 0.10 if self.has_shelf else self.half_width - 0.10

    @property
    def rule_y_lo(self) -> float:
        return -self.y_front + 0.09

    @property
    def rule_travel(self) -> float:
        return max(0.06, (self.y_back - 0.06) - self.rule_y_lo)

    @property
    def is_root_mount(self) -> bool:
        """four_leg_downleg keeps O2's semantics: the frame IS the root and the
        telescoping legs move under it."""
        return self.support_base == "four_leg_downleg"

    @property
    def root_part_name(self) -> str:
        return "frame" if self.is_root_mount else "base"

    @property
    def mount_part_name(self) -> str:
        if self.is_root_mount:
            return "frame"
        if self.support_base == "single_pedestal_column":
            return "lift_column"
        return "height_post_0"

    @property
    def height_driver_name(self) -> str:
        if self.is_root_mount:
            return "height_leg_0"
        if self.support_base == "single_pedestal_column":
            return "height_column"
        return "height_post_0"


def config_from_seed(seed: int) -> DraftingTiltTableConfig:
    """Deterministic procedural sampling across the whole slot domain. seed 0 is not
    special; there are no curated/regression overrides."""
    rng = random.Random(seed)
    base = rng.choice(SUPPORT_BASES)
    top = rng.choice(BOARD_TOPS)
    stay = rng.choice(TILT_STAYS)
    accessory = rng.choice(BOARD_ACCESSORIES)
    return DraftingTiltTableConfig(
        support_base=base,
        board_top=top,
        tilt_stay=stay,
        board_accessory=accessory,
        palette_style=rng.choice(PALETTE_STYLES),
        board_width_scale=round(rng.uniform(0.92, 1.10), 4),
        board_depth_scale=round(rng.uniform(0.94, 1.06), 4),
        frame_height_scale=round(rng.uniform(0.95, 1.08), 4),
        height_travel=round(rng.uniform(0.10, 0.18), 4),
        tilt_total_max=round(rng.uniform(0.70, 1.05), 4),
        authored_tilt=round(rng.uniform(0.17, 0.26), 4),
        slat_count=rng.randint(7, 10),
        name=f"seeded_drafting_tilt_table_{seed}",
    )


def resolve_config(
    config: DraftingTiltTableConfig | None = None,
) -> ResolvedDraftingTiltTableConfig:
    """All compatibility gates + equation/inequality/conditional constraints are
    solved here so the builder can never fail (spec section 7 / Compatibility Gates)."""
    cfg = config or DraftingTiltTableConfig()
    base = _pick(cfg.support_base, SUPPORT_BASES)
    top = _pick(cfg.board_top, BOARD_TOPS)
    stay = _pick(cfg.tilt_stay, TILT_STAYS)
    accessory = _pick(cfg.board_accessory, BOARD_ACCESSORIES)

    # G1: the split top needs a mount with a wide transverse member for its shelf.
    if top == "split_top_side_shelf" and base not in SHELF_OK:
        top = "rounded_laminate_panel"

    # G5: a parallel rule registers off a CONTINUOUS flat working surface. The
    # slatted veneer stands SLAT_H proud of its core with open seams between the
    # slats, so the rule's runner pads have no continuous bearing plane to ride --
    # real boards fitted with a parallel rule use a smooth laminate/framed panel.
    # Gated at config time (never a build-time failure); the rule stays reachable on
    # the other three board tops.
    if top == "slatted_wood_board" and accessory == "parallel_rule":
        accessory = "plain_surface"

    width_scale = _clamp(cfg.board_width_scale, 0.92, 1.10)
    # G2: the single-column yoke cannot honestly cantilever the widest board.
    if base == "single_pedestal_column":
        width_scale = min(width_scale, 1.02)

    # G3 (conditional): only centre-pivot skeletons carry the steepest total tilt.
    tilt_cap = 1.05 if base in CENTER_PIVOT else 0.87
    tilt_max = _clamp(cfg.tilt_total_max, 0.70, tilt_cap)
    authored = _clamp(cfg.authored_tilt, 0.17, 0.26)
    # The authored closed pose must sit strictly inside the travel.
    authored = min(authored, tilt_max - 0.30)

    resolved = ResolvedDraftingTiltTableConfig(
        support_base=base,
        board_top=top,
        tilt_stay=stay,
        board_accessory=accessory,
        palette_style=_pick(cfg.palette_style, PALETTE_STYLES),
        board_width_scale=width_scale,
        board_depth_scale=_clamp(cfg.board_depth_scale, 0.94, 1.06),
        frame_height_scale=_clamp(cfg.frame_height_scale, 0.95, 1.08),
        height_travel=_clamp(cfg.height_travel, 0.10, 0.18),
        tilt_total_max=tilt_max,
        authored_tilt=authored,
        slat_count=int(_clamp(cfg.slat_count, 7, 10)),
        name=cfg.name or "pictureX_0611_drafting_table_with_adjustable_tilt_surface",
    )
    # G6: the height travel is SOLVED against the realized telescoping stack rather
    # than frozen -- the hardware, not the sampler, decides how far the stage rises.
    feasible = _max_height_travel(resolved)
    if resolved.height_travel > feasible:
        resolved = replace(resolved, height_travel=max(0.06, feasible))
    return resolved


def slot_choices_for_config(config) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedDraftingTiltTableConfig)
        else resolve_config(config)
    )
    return (
        ("support_base", r.support_base),
        ("board_top", r.board_top),
        ("tilt_stay", r.tilt_stay),
        ("board_accessory", r.board_accessory),
        ("palette_style", r.palette_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Shared upper interface -- emitted by every support_base on its mount part.
# ===========================================================================
def _emit_mount_top(mount, r, mats) -> None:
    """The rigid frame-top rectangle at ``mount_top_z``. This is the highest inboard
    mount structure; the clearance invariant is stated against it."""
    metal = mats["frame"]
    z = r.mount_top_z - TUBE * 0.5
    for idx, sx in SIDES:
        _box(
            mount,
            (TUBE, 2.0 * BASE_Y_HALF, TUBE),
            (sx * r.outboard_x, 0.0, z),
            metal,
            f"top_side_rail_{idx}",
        )
    # Cross rail directly under the hinge line -- carries both hinge risers.
    _box(
        mount,
        (2.0 * r.outboard_x, TUBE, TUBE),
        (0.0, r.hinge_y, z),
        metal,
        "hinge_cross_rail",
    )
    for tag, sy in (("front", -1.0), ("rear", 1.0)):
        _box(
            mount,
            (2.0 * r.outboard_x, 0.030, 0.030),
            (0.0, sy * (BASE_Y_HALF - 0.020), z),
            metal,
            f"{tag}_top_rail",
        )


def _emit_hinge_interface(mount, r, mats) -> None:
    """Outboard risers + the captured hinge pin (O5 pivot_cheek/pivot_pin L243-L266).
    The risers are the ONLY mount structure above ``mount_top_z`` inside the board's
    y-band, and they sit outside the board's x-span."""
    metal = mats["frame"]
    grey = mats["hardware"]
    riser_h = r.tilt_gap + 0.050
    riser_z = r.mount_top_z - 0.020 + riser_h * 0.5
    for idx, sx in SIDES:
        _box(
            mount,
            (0.038, 0.055, riser_h),
            (sx * r.outboard_x, r.hinge_y, riser_z),
            metal,
            f"pivot_cheek_{idx}",
        )
    # Pin spans the full width and embeds into both cheeks -> one connected cluster.
    _cyl(
        mount,
        PIN_R,
        2.0 * r.outboard_x - 0.008,
        (0.0, r.hinge_y, r.hinge_z),
        grey,
        "hinge_pin",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )


def _emit_shelf(mount, r, mats) -> None:
    """F_split L168-L218: fixed side shelf as mount host visuals (Rule 1 -- it does
    not articulate). Shelf and main panel derive from the one board profile."""
    if not r.has_shelf:
        return
    surface = mats["board"]
    edge = mats["board_edge"]
    metal = mats["frame"]
    cx = r.half_width - r.shelf_span * 0.5
    shelf_top = r.hinge_z + r.board_surface_z
    shelf_z = shelf_top - 0.009
    depth = 0.68 * r.board_depth
    _box(mount, (r.shelf_span, depth, 0.018), (cx, r.hinge_y, shelf_z), surface, "shelf_panel")
    _box(
        mount,
        (r.shelf_span, 0.014, 0.026),
        (cx, r.hinge_y - depth * 0.5 - 0.005, shelf_z + 0.004),
        edge,
        "shelf_front_lip",
    )
    _box(
        mount,
        (0.014, depth, 0.026),
        (r.half_width - 0.005, r.hinge_y, shelf_z + 0.004),
        edge,
        "shelf_side_lip",
    )
    for bindex, sy in enumerate((-1.0, 1.0)):
        by = r.hinge_y + sy * depth * 0.30
        _beam(
            mount,
            (cx, by, r.mount_top_z - 0.02),
            (cx, by, shelf_z - 0.009),
            0.024,
            metal,
            f"shelf_bracket_{bindex}",
        )
    _beam(
        mount,
        (cx, r.hinge_y - depth * 0.30, shelf_z - 0.022),
        (cx, r.hinge_y + depth * 0.30, shelf_z - 0.022),
        0.020,
        metal,
        "shelf_under_rail",
    )


# ===========================================================================
# Slot A: support_base
# ===========================================================================
def _emit_sleeve_column(part, r, mats, x, y, top_z, bot_z, tag):
    """Hollow square sleeve from bot_z to top_z (O5 L140-L151 / O2 L118-L123)."""
    height = top_z - bot_z
    part.visual(
        _square_tube_mesh(0.052, 0.036, height, f"sleeve_tube_{tag}"),
        origin=Origin(xyz=(x, y, (top_z + bot_z) * 0.5)),
        material=mats["frame"],
        name=f"outer_sleeve_{tag}", material_class_id=("metal.paint_coated" if r.support_base in {"four_leg_downleg", "sleeve_post_carriage", "twin_pedestal_lift", "single_pedestal_column"} else "wood.polished_varnished"),
    )
    _box(part, (0.060, 0.060, COLLAR_H), (x, y, top_z - COLLAR_DROP), mats["frame_edge"], f"sleeve_collar_{tag}")


def _emit_inner_post(part, r, mats, x, y, top_z, length, tag, *, guide_at_head: bool = False):
    """Inner telescoping member + polymer guide block (O2 L206-L226 / O5 L186-L192).

    The guide block must sit on whichever END of the member rides INSIDE the sleeve:
    a twin post stands up out of its sleeve (foot captured), while a four-leg
    down-leg hangs down out of its sleeve (head captured). Placing it off the foot in
    both cases left the four-leg's guide 0.2 m below the sleeve, guiding nothing.
    """
    _box(part, (POST_W, POST_W, length), (x, y, top_z - length * 0.5), mats["bright"], f"inner_post_{tag}")
    guide_z = top_z - GUIDE_RISE if guide_at_head else top_z - length + GUIDE_RISE
    _box(
        part,
        (0.036, 0.036, GUIDE_H),
        (x, y, guide_z),
        mats["accent"],
        f"guide_block_{tag}",
    )


def _emit_height_knob(model, parent, r, mats, x, y, z, outward, tag) -> str:
    """Hand-tightened height clamp (O4 L406-L441 / F_column L325-L359). The knob stem's
    flat end face against the flat boss face is the ONE axis-aligned mating pair in
    this template, so it declares a real MatingContract (Rule 2)."""
    _box(
        parent,
        (KNOB_BOSS_T, 0.034, 0.034),
        (x + outward * KNOB_BOSS_INSET, y, z),
        mats["frame_edge"],
        f"knob_boss_{tag}",
    )
    knob = model.part(f"height_knob_{tag}")
    # Stem spans local outward [-KNOB_STEM_EMBED, +KNOB_STEM_LEN]: it seats INTO the
    # boss so the pair really touches (the isolated-parts check needs contact within
    # 1 um) while staying far under the overlap tolerance.
    _cyl(
        knob,
        0.007,
        KNOB_STEM_LEN + KNOB_STEM_EMBED,
        (outward * (KNOB_STEM_LEN - KNOB_STEM_EMBED) * 0.5, 0.0, 0.0),
        mats["frame_edge"],
        "knob_stem",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    _cyl(
        knob,
        0.022,
        0.018,
        (outward * (KNOB_STEM_LEN + 0.009), 0.0, 0.0),
        mats["accent"],
        "knob_cap",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    model.articulation(
        f"height_knob_joint_{tag}",
        ArticulationType.REVOLUTE,
        parent=parent,
        child=knob,
        origin=Origin(xyz=(_knob_boss_face_x(x, outward), y, z)),
        axis=(outward, 0.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=4.0, lower=-math.pi, upper=math.pi),
        mating=MatingContract(
            parent_face_geometry=f"knob_boss_{tag}",
            parent_face_side="positive_x" if outward > 0 else "negative_x",
            child_face_geometry="knob_stem",
            child_face_side="negative_x" if outward > 0 else "positive_x",
            contact_tol=0.002,
        ),
    )
    return f"height_knob_{tag}"


def _base_four_leg_downleg(model, r, mats):
    """O2 L97-L237: welded four-leg trestle root carrying four telescoping down-legs
    plus the fixed blue-gray rear organizer. The frame is the root AND the mount."""
    frame = model.part("frame")
    _emit_mount_top(frame, r, mats)
    _emit_hinge_interface(frame, r, mats)
    _emit_shelf(frame, r, mats)

    sleeve_top = _mount_top_underside_z(r)
    sleeve_bot = LEG_SLEEVE_BOT
    leg_top = _leg_top_z(r)
    legs: list[str] = []
    for i, (sx, sy) in enumerate(((-1.0, -1.0), (1.0, -1.0), (-1.0, 1.0), (1.0, 1.0))):
        x = sx * r.outboard_x
        y = sy * (BASE_Y_HALF - 0.045)
        _emit_sleeve_column(frame, r, mats, x, y, sleeve_top, sleeve_bot, str(i))
        leg = model.part(f"leg_{i}")
        _emit_inner_post(leg, r, mats, x, y, leg_top, LEG_LEN, str(i), guide_at_head=True)
        _box(leg, (0.040, 0.036, 0.024), (x, y, leg_top - LEG_LEN + 0.012), mats["rubber"], f"foot_cap_{i}")
        model.articulation(
            f"height_leg_{i}",
            ArticulationType.PRISMATIC,
            parent=frame,
            child=leg,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=350.0, velocity=0.08, lower=0.0, upper=r.height_travel),
            mimic=None if i == 0 else Mimic(joint="height_leg_0", multiplier=1.0),
            meta={"positive_motion": "retracts the telescoping foot up into its sleeve"},
        )
        legs.append(f"leg_{i}")

    # Welded stabilizers joining the sleeves (O2 L127-L130). Both die inside the
    # sleeve walls at STRETCHER_STOP so the sliding legs stay clear of them.
    leg_y = BASE_Y_HALF - 0.045
    for tag, sy in (("front", -1.0), ("rear", 1.0)):
        _box(
            frame,
            (2.0 * (r.outboard_x - STRETCHER_STOP), 0.026, 0.026),
            (0.0, sy * leg_y, 0.40),
            mats["frame"],
            f"{tag}_stretcher",
        )
    for idx, sx in SIDES:
        _box(
            frame,
            (0.025, 2.0 * (leg_y - STRETCHER_STOP), 0.025),
            (sx * r.outboard_x, 0.0, 0.42),
            mats["frame"],
            f"side_stretcher_{idx}",
        )

    # Fixed rear organizer (O2 L133-L158) -- (4) decoration, host visuals. Kept
    # behind the board's rearmost reach (y = hinge_y + y_back) so it never sweeps.
    org_y = max(BASE_Y_HALF + 0.02, r.hinge_y + r.y_back + 0.03)
    org_z = r.mount_top_z + 0.02
    _box(frame, (2.0 * r.outboard_x - 0.06, 0.19, 0.018), (0.0, org_y + 0.095, org_z), mats["accent"], "organizer_shelf")
    _box(frame, (2.0 * r.outboard_x - 0.06, 0.018, 0.19), (0.0, org_y + 0.185, org_z + 0.095), mats["accent"], "organizer_back")
    for idx, sx in SIDES:
        _box(
            frame,
            (0.018, 0.19, 0.19),
            (sx * (r.outboard_x - 0.04), org_y + 0.095, org_z + 0.095),
            mats["accent"],
            f"organizer_cheek_{idx}",
        )
        _beam(
            frame,
            (sx * (r.outboard_x - 0.02), BASE_Y_HALF - 0.02, r.mount_top_z - 0.02),
            (sx * (r.outboard_x - 0.02), org_y + 0.06, org_z - 0.006),
            0.026,
            mats["frame"],
            f"organizer_riser_{idx}",
        )
    return frame, legs


def _emit_twin_post_base(model, r, mats, *, wood: bool, locks: str | None):
    """Shared twin-sleeve + twin-post skeleton (O5 L128-L218, O3 L59-L171,
    O4 L64-L287): a grounded ``base`` of hollow sleeves and two synchronized
    PRISMATIC inner posts. ``height_post_0`` is the mount."""
    base = model.part("base")
    metal = mats["frame"] if not wood else mats["frame"]
    sleeve_top = _twin_sleeve_top_z(r)
    # The sleeve STANDS ON its foot rail: its foot is derived from the rail's top
    # face (and sinks WELD_EMBED into it). Frozen at 0.070 it floated 30 mm above
    # the rail -- a disconnected island in every twin-post seed.
    sleeve_bot = FOOT_RAIL_H - WELD_EMBED

    for idx, sx in SIDES:
        x = sx * r.outboard_x
        _box(base, (0.070, 2.0 * BASE_Y_HALF, FOOT_RAIL_H), (x, 0.0, FOOT_RAIL_H * 0.5), metal, f"foot_rail_{idx}")
        for cap, sy in (("front", -1.0), ("rear", 1.0)):
            _box(
                base,
                (0.062, 0.030, 0.018),
                (x, sy * (BASE_Y_HALF - 0.020), 0.009),
                mats["rubber"],
                f"{cap}_foot_cap_{idx}",
            )
        _emit_sleeve_column(base, r, mats, x, 0.0, sleeve_top, sleeve_bot, idx)
    # Ends die inside the sleeve walls (the posts never reach this height, but the
    # stop keeps the connection honest across every frame_height_scale).
    _box(
        base,
        (2.0 * (r.outboard_x - STRETCHER_STOP), 0.046, 0.055),
        (0.0, 0.0, 0.22),
        metal,
        "lower_stretcher",
    )

    posts: list[str] = []
    post_len = POST_LEN
    mount = None
    for idx, sx in SIDES:
        x = sx * r.outboard_x
        post = model.part(f"height_post_{idx}")
        # The post CARRIES the frame-top rectangle: its top face is that rectangle's
        # underside, derived (never restated) so the rails rest on the post instead
        # of running through it.
        _emit_inner_post(post, r, mats, x, 0.0, _mount_top_underside_z(r), post_len, idx)
        if idx == "0":
            _emit_mount_top(post, r, mats)
            _emit_hinge_interface(post, r, mats)
            _emit_shelf(post, r, mats)
            # Moving cross rail carried by the driving post (O4 L185-L190). It lives
            # in the posts' OWN y-plane so it really welds to the driving post; at
            # y=-0.20 it floated clear of both posts. Its far end dies inside post 1's
            # socket but stops RAIL_POST_CLEAR short of that post's own tube.
            rail_x0 = -r.outboard_x + POST_W * 0.5 - RAIL_POST_WELD
            rail_x1 = r.outboard_x - POST_W * 0.5 - RAIL_POST_CLEAR
            _box(
                post,
                (rail_x1 - rail_x0, 0.050, CROSS_RAIL_H),
                (0.5 * (rail_x0 + rail_x1), 0.0, _cross_rail_z(r)),
                mats["bright"],
                "moving_cross_rail",
            )
            mount = post
        else:
            # Socket receiving the moving rail (O4 L242-L247) -- keeps the second
            # visible slider an independent part without fusing the two.
            _box(
                post,
                (0.046, 0.070, CROSS_RAIL_H),
                (x - sx * 0.024, 0.0, _cross_rail_z(r)),
                mats["frame_edge"],
                "rail_socket",
            )
        model.articulation(
            f"height_post_{idx}",
            ArticulationType.PRISMATIC,
            parent=base,
            child=post,
            origin=Origin(xyz=(0.0, 0.0, 0.0)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=350.0, velocity=0.08, lower=0.0, upper=r.height_travel),
            mimic=None if idx == "0" else Mimic(joint="height_post_0", multiplier=1.0),
            meta={"positive_motion": "raises the carriage and the drawing board"},
        )
        posts.append(f"height_post_{idx}")

    extras: list[str] = []
    if locks == "wood_levers":
        # O3 L315-L345: two stacked hand levers on the outer face of the right sleeve.
        for i, dz in enumerate((-0.09, 0.0)):
            lock = model.part(f"height_lock_{i}")
            _cyl(lock, 0.007, 0.030, (0.015, 0.0, 0.0), mats["hardware"], "clamp_stem", rpy=(0.0, math.pi / 2.0, 0.0))
            _cyl(lock, 0.020, 0.018, (0.038, 0.0, 0.0), mats["accent"], "clamp_knob", rpy=(0.0, math.pi / 2.0, 0.0))
            _box(lock, (0.018, 0.016, 0.056), (0.050, 0.0, -0.020), mats["accent"], "clamp_lever")
            _box(
                base,
                (0.018, 0.034, 0.034),
                (r.outboard_x + 0.032, 0.0, sleeve_top - 0.06 + dz),
                mats["frame_edge"],
                f"lock_boss_{i}",
            )
            model.articulation(
                f"height_lock_joint_{i}",
                ArticulationType.REVOLUTE,
                parent=base,
                child=lock,
                origin=Origin(xyz=(r.outboard_x + 0.041, 0.0, sleeve_top - 0.06 + dz)),
                axis=(1.0, 0.0, 0.0),
                motion_limits=MotionLimits(
                    effort=3.0, velocity=2.5, lower=math.radians(-70.0), upper=math.radians(70.0)
                ),
            )
            extras.append(f"height_lock_{i}")
    elif locks == "knobs":
        # O4 L406-L441: one clamp knob on each pedestal sleeve.
        for idx, sx in SIDES:
            extras.append(
                _emit_height_knob(
                    model, base, r, mats, sx * (r.outboard_x + 0.026), 0.0, sleeve_top - 0.09, sx, idx
                )
            )
    return base, mount, posts, extras


def _base_sleeve_post_carriage(model, r, mats):
    """O5: black steel sleeve base + twin inner posts + welded upper carriage."""
    return _emit_twin_post_base(model, r, mats, wood=False, locks=None)


def _base_twin_post_trestle(model, r, mats):
    """O3: stained-wood twin-post trestle with two stacked height levers."""
    return _emit_twin_post_base(model, r, mats, wood=True, locks="wood_levers")


def _base_twin_pedestal_lift(model, r, mats):
    """O4: gray steel twin pedestals, moving cross rail, two height clamp knobs."""
    return _emit_twin_post_base(model, r, mats, wood=False, locks="knobs")


def _base_single_pedestal_column(model, r, mats):
    """F_column L75-L230: T-foot + hollow central column + one PRISMATIC lift column
    whose yoke reaches out to the outboard hinge risers."""
    base = model.part("base")
    metal = mats["frame"]
    _box(base, (0.070, 2.0 * BASE_Y_HALF, 0.030), (0.0, 0.0, 0.015), metal, "t_foot_long")
    _box(base, (0.56, 0.070, 0.030), (0.0, -BASE_Y_HALF + 0.045, 0.015), metal, "t_foot_cross")
    for cap, (cx, cy) in (
        ("rear", (0.0, BASE_Y_HALF - 0.020)),
        ("left", (-0.25, -BASE_Y_HALF + 0.045)),
        ("right", (0.25, -BASE_Y_HALF + 0.045)),
    ):
        _box(base, (0.062, 0.062, 0.008), (cx, cy, 0.004), mats["rubber"], f"foot_cap_{cap}")
    _box(base, (0.10, 0.10, 0.050), (0.0, 0.0, 0.055), mats["frame_edge"], "column_gusset")

    col_top = _column_top_z(r)
    base.visual(
        _square_tube_mesh(COLUMN_OUTER, COLUMN_INNER, col_top - 0.060, "outer_column_tube"),
        origin=Origin(xyz=(0.0, 0.0, (col_top + 0.060) * 0.5)),
        material=metal,
        name="outer_column", material_class_id="metal.paint_coated",
    )
    _cyl(
        base,
        0.050,
        COLUMN_COLLAR_H,
        (0.0, 0.0, col_top - COLUMN_COLLAR_DROP),
        mats["frame_edge"],
        "column_collar",
    )
    # The knob boss grows from the column's own outer face -- derived, so it welds to
    # the tube instead of hanging in the air beside it.
    knob = _emit_height_knob(
        model, base, r, mats, COLUMN_OUTER * 0.5, 0.0, col_top - 0.16, 1.0, "c"
    )

    lift = model.part("lift_column")
    # The lift column CARRIES the frame top: its head is that rectangle's underside.
    col_head = _mount_top_underside_z(r)
    _box(lift, (0.056, 0.056, COLUMN_LEN), (0.0, 0.0, col_head - COLUMN_LEN * 0.5), mats["bright"], "inner_column")
    _box(
        lift,
        (COLUMN_INNER, COLUMN_INNER, COLUMN_GUIDE_H),
        (0.0, 0.0, col_head - COLUMN_LEN + COLUMN_GUIDE_RISE),
        mats["accent"],
        "column_guide",
    )
    _emit_mount_top(lift, r, mats)
    _emit_hinge_interface(lift, r, mats)
    _emit_shelf(lift, r, mats)
    # Yoke: bridge + arms reaching the outboard cheeks (F_column L163-L180, arms
    # lengthened so the bearings sit outside the board's swept x-span).
    _box(lift, (0.10, 0.070, 0.040), (0.0, r.hinge_y, r.mount_top_z - 0.055), mats["bright"], "yoke_bridge")
    for idx, sx in SIDES:
        _beam(
            lift,
            (0.0, r.hinge_y, r.mount_top_z - 0.055),
            (sx * r.outboard_x, r.hinge_y, r.mount_top_z - 0.055),
            0.038,
            mats["bright"],
            f"yoke_arm_{idx}",
        )
    model.articulation(
        "height_column",
        ArticulationType.PRISMATIC,
        parent=base,
        child=lift,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=450.0, velocity=0.08, lower=0.0, upper=r.height_travel),
        meta={"positive_motion": "raises the yoke and the drawing board"},
    )
    return base, lift, [], [knob]


def _build_support_base(model, r, mats):
    """Returns (root, mount, height_members, extra_parts)."""
    if r.support_base == "four_leg_downleg":
        frame, legs = _base_four_leg_downleg(model, r, mats)
        return frame, frame, legs, []
    builder = {
        "sleeve_post_carriage": _base_sleeve_post_carriage,
        "twin_post_trestle": _base_twin_post_trestle,
        "twin_pedestal_lift": _base_twin_pedestal_lift,
        "single_pedestal_column": _base_single_pedestal_column,
    }[r.support_base]
    return builder(model, r, mats)


# ===========================================================================
# Slot B: board_top -- the (3) primary form family, plus the constant tilt hinge.
# ===========================================================================
def _emit_under_rails(board, r, mats, xs) -> None:
    """Underside stiffeners (O2 L265-L272, O3 center_batten L182). They stop short of
    the pivot barrel so nothing but the barrel ever reaches the mount hinge pin."""
    for i, x in enumerate(xs):
        for tag, (y0, y1) in (
            ("rear", (BARREL_R + 0.024, r.y_back - 0.020)),
            ("front", (-r.y_front + 0.020, -(BARREL_R + 0.024))),
        ):
            if y1 - y0 < 0.06:
                continue
            _box(
                board,
                (0.034, y1 - y0, 0.022),
                (x, (y0 + y1) * 0.5, PANEL_BOTTOM - 0.011),
                mats["hardware"],
                f"under_rail_{tag}_{i}",
            )


def _emit_ledges(board, r, mats) -> None:
    """Front paper ledge + fence, present in every source (O1 L161-L166, O3 L180-L181,
    O4 L328-L341, O5 L309-L320). Derived from the realized panel width/front edge."""
    top = r.board_surface_z
    _box(
        board,
        (r.panel_width + 0.02, 0.045, 0.012),
        (r.panel_x_center, -r.y_front + 0.012, top + 0.006),
        mats["accent"],
        "paper_ledge_shelf",
    )
    _box(
        board,
        (r.panel_width + 0.02, 0.012, 0.038),
        (r.panel_x_center, -r.y_front - 0.006, top + 0.019),
        mats["accent"],
        "ledge_fence",
    )


def _emit_hinge_barrel(board, r, mats) -> None:
    """The board's captured hinge barrel around the mount pin (O5 pivot_barrel L321-L329,
    O3 pivot_shaft L183-L188). Stops short of the split top's shelf."""
    _cyl(
        board,
        BARREL_R,
        r.panel_width - 0.020,
        (r.panel_x_center, 0.0, 0.0),
        mats["hardware"],
        "pivot_barrel",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    for idx, sx in SIDES:
        x = -r.half_width + 0.012 if sx < 0 else r.panel_x_max - 0.012
        _cyl(board, 0.030, 0.022, (x, 0.0, 0.0), mats["frame_edge"], f"pivot_cap_{idx}", rpy=(0.0, math.pi / 2.0, 0.0))


def _emit_board(model, mount, r, mats):
    """Board authored FLAT in its own frame: pivot line at y=0, panel underside at
    z=PANEL_BOTTOM. The whole authored tilt lives in the joint's rpy, so q=lower is
    exactly horizontal and q=0 reproduces the source records' working angle."""
    board = model.part("board")
    top = r.board_surface_z

    if r.board_top == "slatted_wood_board":
        # O4 L289-L341: plywood core + slatted veneer (Macro Surface Construction).
        _box(
            board,
            (r.panel_width, r.board_depth, BOARD_T),
            (r.panel_x_center, (r.y_back - r.y_front) * 0.5, PANEL_BOTTOM + BOARD_T * 0.5),
            mats["board_edge"],
            "board_core",
        )
        span = r.board_depth - 0.10
        pitch = span / r.slat_count
        for i in range(r.slat_count):
            y = -r.y_front + 0.05 + (i + 0.5) * pitch
            _box(
                board,
                (r.panel_width - 0.022, pitch * 0.86, SLAT_H),
                (r.panel_x_center, y, PANEL_BOTTOM + BOARD_T + SLAT_H * 0.5),
                mats["board"] if i % 3 else mats["grain"],
                f"wood_slat_{i}",
            )
            if i < r.slat_count - 1:
                _box(
                    board,
                    (r.panel_width - 0.020, pitch * 0.10, SLAT_H * 0.5),
                    (r.panel_x_center, y + pitch * 0.5, PANEL_BOTTOM + BOARD_T + SLAT_H * 0.75),
                    mats["grain"],
                    f"slat_seam_{i}",
                )
        for idx, sx in SIDES:
            x = -r.half_width + 0.008 if sx < 0 else r.panel_x_max - 0.008
            _box(
                board,
                (0.016, r.board_depth, BOARD_T + SLAT_H),
                (x, (r.y_back - r.y_front) * 0.5, PANEL_BOTTOM + (BOARD_T + SLAT_H) * 0.5),
                mats["grain"],
                f"side_band_{idx}",
            )
        _emit_under_rails(board, r, mats, (r.panel_x_center - r.panel_width * 0.28, r.panel_x_center + r.panel_width * 0.28))

    elif r.board_top == "framed_batten_board":
        # O3 L175-L205: framed panel + seams + a full-length centre batten
        # (Volumetric Envelope Form -- the underside build-up reads as the form).
        _box(
            board,
            (r.panel_width, r.board_depth, BOARD_T),
            (r.panel_x_center, (r.y_back - r.y_front) * 0.5, PANEL_BOTTOM + BOARD_T * 0.5),
            mats["board"],
            "board_core",
        )
        for idx, sx in SIDES:
            _box(
                board,
                (0.006, r.board_depth - 0.010, 0.003),
                (r.panel_x_center + sx * r.panel_width * 0.32, (r.y_back - r.y_front) * 0.5, PANEL_BOTTOM + BOARD_T),
                mats["grain"],
                f"panel_seam_{idx}",
            )
        _box(
            board,
            (r.panel_width + 0.006, 0.030, BOARD_T + 0.006),
            (r.panel_x_center, r.y_back - 0.014, PANEL_BOTTOM + BOARD_T * 0.5),
            mats["board_edge"],
            "rear_edge",
        )
        _emit_under_rails(board, r, mats, (r.panel_x_center,))

    else:
        # O5 L73-L80 + L288-L337 (and O2 L244-L263): one rounded-corner laminate
        # panel (Planar Boundary Form). Mesh family preserved -- never a Box.
        panel = ExtrudeGeometry(
            rounded_rect_profile(r.panel_width, r.board_depth, 0.018, corner_segments=6),
            BOARD_T,
            cap=True,
            center=True,
        )
        board.visual(
            mesh_from_geometry(panel, "laminate_panel"),
            origin=Origin(
                xyz=(r.panel_x_center, (r.y_back - r.y_front) * 0.5, PANEL_BOTTOM + BOARD_T * 0.5)
            ),
            material=mats["board"],
            name="board_core", material_class_id="plastic.opaque_glossy_molded",
        )
        _box(
            board,
            (r.panel_width - 0.02, 0.014, 0.006),
            (r.panel_x_center, r.y_back - 0.012, PANEL_BOTTOM + BOARD_T),
            mats["board_edge"],
            "rear_lamination",
        )
        _emit_under_rails(board, r, mats, (r.panel_x_center - r.panel_width * 0.26, r.panel_x_center + r.panel_width * 0.26))

    _emit_ledges(board, r, mats)
    _emit_hinge_barrel(board, r, mats)

    # Stay mounting pins under the rising half (O3 brace_pin L196-L205,
    # F_spring spring_pivot L197-L208).
    for idx, sx in SIDES:
        _cyl(
            board,
            STAY_PIN_R,
            0.048,
            (sx * abs(r.stay_x), r.stay_y, PANEL_BOTTOM - STAY_PIN_R),
            mats["hardware"],
            f"stay_pin_{idx}",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )

    model.articulation(
        "board_tilt",
        ArticulationType.REVOLUTE,
        parent=mount,
        child=board,
        origin=Origin(xyz=(0.0, r.hinge_y, r.hinge_z), rpy=(r.authored_angle, 0.0, 0.0)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=90.0, velocity=0.55, lower=r.tilt_lower, upper=r.tilt_upper
        ),
        meta={
            "mechanism": "adjustable drawing-surface tilt",
            "zero_pose": "source-record working angle",
            "total_tilt_range_rad": (0.0, r.tilt_total_max),
        },
    )
    return board


# ===========================================================================
# Slot C: tilt_stay -- (2) the angle-hold mechanism.
# ===========================================================================
def _stay_joint(model, board, r, stay, idx, sx) -> None:
    """Stay hangs off the board's stay pin. Mimic(-1) against ``board_tilt`` plus the
    joint's -authored_angle rpy makes the strut hold a constant WORLD orientation
    through the whole arc -- it stays coupled to the board and never floats."""
    model.articulation(
        f"stay_fold_{idx}",
        ArticulationType.REVOLUTE,
        parent=board,
        child=stay,
        origin=Origin(
            xyz=(sx * abs(r.stay_x), r.stay_y, PANEL_BOTTOM - 0.014),
            rpy=(-r.authored_angle, 0.0, 0.0),
        ),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=35.0, velocity=1.0, lower=-r.tilt_upper, upper=-r.tilt_lower
        ),
        mimic=Mimic(joint="board_tilt", multiplier=-1.0),
        meta={"mechanism": "board angle-hold stay coupled to the tilt joint"},
    )


def _stay_bracket_y_half(r) -> float:
    """Half-depth of the stay's upper bracket -- SOLVED, not frozen (Contract 3e).

    The bracket hangs off the board's stay pin and counter-rotates against the board
    through the whole tilt arc (|relative angle| <= tilt_total_max). Its top corners
    sweep UP by ``y_half * sin(theta)``, so the widest it may be is set by how much
    room the panel underside leaves. Frozen at 0.019 it climbed into the panel on
    every seed that sampled a steep tilt.
    """
    reach = max(math.sin(r.tilt_total_max), 1e-6)
    return min(0.019, (PANEL_BOTTOM - STAY_PANEL_CLEAR) / reach)


def _emit_stay_hub(stay, r, mats) -> None:
    # The hub is COAXIAL with the stay's rotation axis, so its 2 mm bite into the
    # panel is rotation-invariant and is the one declared captured fit (see
    # _allow_captured_fits). The bracket is not coaxial, so it is sized to clear.
    _cyl(stay, 0.016, 0.052, (0.0, 0.0, 0.0), mats["hardware"], "upper_hub", rpy=(0.0, math.pi / 2.0, 0.0))
    y_half = _stay_bracket_y_half(r)
    _box(stay, (0.046, 2.0 * y_half, 0.034), (0.0, 0.0, -0.017), mats["hardware"], "upper_bracket")


def _emit_curved_spline_braces(model, board, r, mats) -> list[str]:
    """O3 L226-L313: curved steel stays built with tube_from_spline_points (mesh
    family preserved), plus the independent tilt-lock handle on the right stay."""
    parts: list[str] = []
    length = r.stay_len
    stays = []
    for idx, sx in SIDES:
        stay = model.part(f"tilt_stay_{idx}")
        _emit_stay_hub(stay, r, mats)
        path = tube_from_spline_points(
            [
                (0.0, 0.0, -0.030),
                (0.0, -0.020 * length, -0.34 * length),
                (0.0, -0.070 * length, -0.70 * length),
                (0.0, -0.130 * length, -length),
            ],
            radius=0.010,
            samples_per_segment=10,
            radial_segments=12,
            cap_ends=True,
        )
        stay.visual(mesh_from_geometry(path, f"brace_rod_{idx}"), material=mats["accent"], name="brace_rod", material_class_id="metal.blackened_gunmetal")
        _cyl(
            stay,
            0.022,
            0.048,
            (0.0, -0.130 * length, -length),
            mats["frame_edge"],
            "lower_hub",
            rpy=(0.0, math.pi / 2.0, 0.0),
        )
        _stay_joint(model, board, r, stay, idx, sx)
        parts.append(f"tilt_stay_{idx}")
        stays.append(stay)

    # Independent tilt-lock handle on the right stay's lower hub (O3 L279-L313).
    lock = model.part("tilt_lock")
    _cyl(lock, 0.008, 0.034, (0.026, 0.0, 0.0), mats["hardware"], "lock_shaft", rpy=(0.0, math.pi / 2.0, 0.0))
    _box(lock, (0.020, 0.018, 0.075), (0.046, 0.0, -0.030), mats["accent"], "lock_handle")
    _cyl(lock, 0.016, 0.024, (0.058, 0.0, -0.062), mats["frame_edge"], "lock_grip", rpy=(math.pi / 2.0, 0.0, 0.0))
    model.articulation(
        "stay_to_tilt_lock",
        ArticulationType.REVOLUTE,
        parent=stays[1],
        child=lock,
        origin=Origin(xyz=(0.0, -0.130 * length, -length)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=4.0, velocity=2.0, lower=math.radians(-35.0), upper=math.radians(55.0)
        ),
    )
    parts.append("tilt_lock")
    return parts


def _emit_counterbalance_spring_arms(model, board, r, mats) -> list[str]:
    """F_spring L234-L327: spring cylinder + exposed coil rings + piston rod. The
    mimic keeps the strut world-vertical, so it tracks the board through its arc."""
    parts: list[str] = []
    length = r.stay_len
    for idx, sx in SIDES:
        arm = model.part(f"tilt_stay_{idx}")
        _emit_stay_hub(arm, r, mats)
        _cyl(arm, 0.010, 0.056, (0.0, 0.0, -0.010), mats["brass"], "upper_pivot_pin", rpy=(0.0, math.pi / 2.0, 0.0))
        # The link plate carries the spring body up to the pinned bracket. Its head is
        # derived from the board stay pin it swings around so it stops CLEAR of that
        # pin (it stays welded to upper_bracket, which is what actually holds it).
        # Frozen at -0.035*length it always landed inside the pin, because stay_len is
        # bounded well below the 0.40 m that literal silently assumed.
        plate_top = -(STAY_PIN_R + STAY_PANEL_CLEAR)
        plate_bot = -0.335 * length
        _box(
            arm,
            (0.032, 0.028, plate_top - plate_bot),
            (0.0, 0.0, 0.5 * (plate_top + plate_bot)),
            mats["hardware"],
            "link_plate",
        )
        _box(arm, (0.036, 0.036, 0.50 * length), (0.0, 0.0, -0.50 * length), mats["hardware"], "spring_cylinder")
        _cyl(arm, 0.020, 0.012, (0.0, 0.0, -0.255 * length), mats["frame_edge"], "cylinder_cap")
        for ring, frac in enumerate((0.34, 0.50, 0.66)):
            _cyl(arm, 0.024, 0.010, (0.0, 0.0, -frac * length), mats["brass"], f"coil_ring_{ring}")
        _cyl(arm, 0.008, 0.30 * length, (0.0, 0.0, -0.85 * length), mats["hardware"], "piston_rod")
        _box(arm, (0.042, 0.040, 0.024), (0.0, 0.0, -length), mats["hardware"], "lower_bracket")
        _cyl(arm, 0.010, 0.050, (0.0, 0.0, -length), mats["brass"], "lower_pivot_pin", rpy=(0.0, math.pi / 2.0, 0.0))
        _stay_joint(model, board, r, arm, idx, sx)
        parts.append(f"tilt_stay_{idx}")
    return parts


def _emit_folding_bar_stays(model, board, r, mats) -> list[str]:
    """O2 L289-L325 / O5 L359-L443: straight folding bars with a rubber shoe, each
    carrying a CONTINUOUS hand-tightened clamp knob (O5 L415-L443)."""
    parts: list[str] = []
    length = r.stay_len
    knob_mesh = mesh_from_geometry(
        KnobGeometry(
            0.038,
            0.020,
            body_style="lobed",
            base_diameter=0.026,
            top_diameter=0.034,
            crown_radius=0.0015,
            grip=KnobGrip(style="ribbed", count=9, depth=0.0008, width=0.0016),
            center=False,
        ),
        "stay_clamp_knob",
    )
    for idx, sx in SIDES:
        stay = model.part(f"tilt_stay_{idx}")
        _emit_stay_hub(stay, r, mats)
        _box(stay, (0.022, 0.016, length - 0.030), (0.0, 0.0, -0.030 - (length - 0.030) * 0.5), mats["frame"], "support_bar")
        _box(stay, (0.030, 0.024, 0.008), (0.0, 0.0, -length + 0.004), mats["rubber"], "support_pad")
        _cyl(stay, 0.013, 0.030, (0.0, 0.0, -0.34 * length), mats["hardware"], "support_rivet", rpy=(0.0, math.pi / 2.0, 0.0))
        _stay_joint(model, board, r, stay, idx, sx)
        parts.append(f"tilt_stay_{idx}")

        knob = model.part(f"stay_knob_{idx}")
        knob.visual(
            knob_mesh,
            origin=Origin(rpy=(0.0, sx * math.pi / 2.0, 0.0)),
            material=mats["accent"],
            name="lobed_knob", material_class_id="plastic.opaque_glossy_molded",
        )
        _cyl(knob, 0.005, 0.016, (-sx * 0.008, 0.0, 0.0), mats["hardware"], "clamp_stem", rpy=(0.0, math.pi / 2.0, 0.0))
        model.articulation(
            f"stay_knob_joint_{idx}",
            ArticulationType.CONTINUOUS,
            parent=stay,
            child=knob,
            origin=Origin(xyz=(sx * 0.016, 0.0, -0.34 * length)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=12.0, velocity=2.5),
            meta={"mechanism": "hand-tightened angle-lock clamp"},
        )
        parts.append(f"stay_knob_{idx}")
    return parts


def _emit_lever_angle_lock(model, mount, r, mats) -> list[str]:
    """O4 L376-L404: a single swinging angle-lock lever. Replanted outboard of the
    board's x-span (the outboard-control precedent of O2 L340-L361 / O3 L315-L345 /
    O4 L407-L441) so its swing can never enter the board's swept wedge."""
    y = r.hinge_y - 0.085
    z = r.mount_top_z + r.tilt_gap * 0.45
    _box(mount, (0.060, 0.040, 0.026), (r.outboard_x + 0.020, y, z), mats["frame_edge"], "lock_bracket")
    _beam(
        mount,
        (r.outboard_x, r.hinge_y, z),
        (r.outboard_x + 0.030, y, z),
        0.024,
        mats["frame"],
        "lock_bracket_arm",
    )
    # The lever turns on a real pivot pin carried by the bracket, planted OUTBOARD of
    # the bracket's own face so the hub wraps the pin (axle<->hub) instead of being
    # rammed through the structural bracket arm that carries it.
    _cyl(
        mount,
        LEVER_PIN_R,
        LEVER_PIN_LEN,
        (_lever_pin_center_x(r), y, z),
        mats["hardware"],
        "lock_pivot_pin",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    x = _lever_pivot_x(r)
    lever = model.part("angle_lever")
    _cyl(lever, 0.020, LEVER_HUB_LEN, (0.0, 0.0, 0.0), mats["accent"], "lever_hub", rpy=(0.0, math.pi / 2.0, 0.0))
    _box(lever, (0.026, 0.024, 0.090), (0.0, -0.005, -0.055), mats["accent"], "lever_arm")
    _cyl(lever, 0.016, 0.046, (0.0, -0.010, -0.100), mats["accent"], "lever_grip", rpy=(0.0, math.pi / 2.0, 0.0))
    model.articulation(
        "mount_to_angle_lever",
        ArticulationType.REVOLUTE,
        parent=mount,
        child=lever,
        origin=Origin(xyz=(x, y, z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=-0.45, upper=0.65),
        meta={"mechanism": "board angle-lock lever"},
    )
    return ["angle_lever"]


def _emit_tilt_stay(model, mount, board, r, mats) -> list[str]:
    if r.tilt_stay == "curved_spline_braces":
        return _emit_curved_spline_braces(model, board, r, mats)
    if r.tilt_stay == "counterbalance_spring_arms":
        return _emit_counterbalance_spring_arms(model, board, r, mats)
    if r.tilt_stay == "folding_bar_stays":
        return _emit_folding_bar_stays(model, board, r, mats)
    return _emit_lever_angle_lock(model, mount, r, mats)


# ===========================================================================
# Slot D: board_accessory
# ===========================================================================
def _emit_parallel_rule(model, board, r, mats) -> list[str]:
    """O1 L210-L310: parallel rule sliding along the board face on runner pads, with
    two rotating clamp knobs (KnobGeometry mesh family preserved)."""
    top = r.board_surface_z
    bar_w = r.panel_width - 0.055
    deck = _rule_deck_z()
    rule = model.part("parallel_rule")
    _box(rule, (bar_w, 0.034, 0.014), (0.0, 0.0, deck + 0.024), mats["bright"], "aluminum_bar")
    _box(rule, (bar_w - 0.05, 0.012, 0.012), (0.0, -0.023, deck + 0.018), mats["board_edge"], "black_guide")
    knob_x = bar_w * 0.5 - 0.012
    for idx, sx in SIDES:
        _box(
            rule,
            (0.048, 0.050, RULE_CARRIAGE_H),
            (sx * (bar_w * 0.5 - 0.028), 0.0, deck + RULE_CARRIAGE_H * 0.5),
            mats["frame"],
            f"end_carriage_{idx}",
        )
        # The pad is the ONLY rule element that meets the board face; it beds
        # RULE_PAD_BED into it so the sliding contact is real, not a razor gap.
        _box(
            rule,
            (0.030, 0.030, RULE_PAD_T),
            (sx * (bar_w * 0.5 - 0.028), 0.0, RULE_PAD_T * 0.5 - RULE_PAD_BED),
            mats["rubber"],
            f"runner_pad_{idx}",
        )
        _cyl(rule, 0.006, 0.022, (sx * knob_x, 0.0, deck + 0.019), mats["hardware"], f"knob_bushing_{idx}")
    model.articulation(
        "board_to_rule",
        ArticulationType.PRISMATIC,
        parent=board,
        child=rule,
        origin=Origin(xyz=(r.panel_x_center, r.rule_y_lo, top)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=18.0, velocity=0.16, lower=0.0, upper=r.rule_travel),
        meta={"positive_motion": "slides the parallel rule up the inclined board face"},
    )
    parts = ["parallel_rule"]
    knob_z = deck + 0.030
    # The clamp shaft runs down the bar's bore (lined by knob_bushing) but stops
    # RULE_SHAFT_CLEAR above the end carriage, so the only contact it declares is the
    # bore it actually passes through.
    shaft_len = 0.020
    shaft_bottom = deck + RULE_CARRIAGE_H + RULE_SHAFT_CLEAR
    for idx, sx in SIDES:
        knob = model.part(f"rule_knob_{idx}")
        _cyl(
            knob,
            0.0045,
            shaft_len,
            (0.0, 0.0, shaft_bottom + shaft_len * 0.5 - knob_z),
            mats["hardware"],
            "shaft",
        )
        _cyl(knob, 0.017, 0.014, (0.0, 0.0, 0.010), mats["accent"], "knob_cap")
        _box(knob, (0.020, 0.008, 0.006), (0.014, 0.0, 0.017), mats["accent"], "clamp_wing")
        model.articulation(
            f"rule_to_knob_{idx}",
            ArticulationType.REVOLUTE,
            parent=rule,
            child=knob,
            origin=Origin(xyz=(sx * knob_x, 0.0, knob_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=1.8, velocity=3.0, lower=-1.2, upper=1.2),
        )
        parts.append(f"rule_knob_{idx}")
    return parts


# ===========================================================================
# Assembly
# ===========================================================================
def build_pictureX_0611_drafting_table_with_adjustable_tilt_surface(
    config: DraftingTiltTableConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={"category": "pictureX/0611/drafting_table_with_adjustable_tilt_surface"},
    )
    rgba = dict(PALETTES[r.palette_style])
    rgba.update(_HARDWARE)
    mats = {k: model.material(f"dtt_{k}_{r.palette_style}", rgba=v) for k, v in rgba.items()}

    root, mount, height_members, extras = _build_support_base(model, r, mats)
    board = _emit_board(model, mount, r, mats)
    _emit_tilt_stay(model, mount, board, r, mats)
    if r.board_accessory == "parallel_rule":
        _emit_parallel_rule(model, board, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    model.meta["height_members"] = list(height_members)
    model.meta["extra_parts"] = list(extras)
    return model


def build_seeded_pictureX_0611_drafting_table_with_adjustable_tilt_surface(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_pictureX_0611_drafting_table_with_adjustable_tilt_surface(
        config_from_seed(seed), assets=assets
    )


# ===========================================================================
# Tests
# ===========================================================================
def _allow_captured_fits(ctx, model, r) -> None:
    """Every allowance names an EXACT element pair with a physical reason (Rule 7).
    All of these mirror an allowance already declared by the source records."""
    board = model.get_part("board")
    mount = model.get_part(r.mount_part_name)
    root = model.get_part(r.root_part_name)

    # Board hinge barrel captured around the mount's hinge pin (O5 L584-L591).
    ctx.allow_overlap(
        mount,
        board,
        elem_a="hinge_pin",
        elem_b="pivot_barrel",
        reason="The board hinge barrel is intentionally captured around the frame hinge pin.",
    )
    # The same pin runs on through the board's coaxial pivot end caps (O3 pivot_cap
    # L189-L195 sits on the same shaft line).
    for idx, sx in SIDES:
        ctx.allow_overlap(
            mount,
            board,
            elem_a="hinge_pin",
            elem_b=f"pivot_cap_{idx}",
            reason="The frame hinge pin runs coaxially through the board's pivot end cap.",
        )

    # Telescoping members retained inside their hollow sleeves (O5 L475-L485).
    if r.is_root_mount:
        for i in range(4):
            leg = model.get_part(f"leg_{i}")
            ctx.allow_overlap(
                root,
                leg,
                elem_a=f"outer_sleeve_{i}",
                elem_b=f"inner_post_{i}",
                reason="The telescoping inner leg is intentionally retained inside its hollow sleeve.",
            )
            ctx.allow_overlap(
                root,
                leg,
                elem_a=f"outer_sleeve_{i}",
                elem_b=f"guide_block_{i}",
                reason="The close-fitting polymer guide is intentionally captured inside the sleeve.",
            )
            ctx.allow_overlap(
                root,
                leg,
                elem_a=f"sleeve_collar_{i}",
                elem_b=f"inner_post_{i}",
                reason="The sleeve collar wraps the inner leg as a visible clamp ring.",
            )
    elif r.support_base == "single_pedestal_column":
        lift = model.get_part("lift_column")
        ctx.allow_overlap(
            root,
            lift,
            elem_a="outer_column",
            elem_b="inner_column",
            reason="The inner column is intentionally retained inside the hollow outer column.",
        )
        ctx.allow_overlap(
            root,
            lift,
            elem_a="outer_column",
            elem_b="column_guide",
            reason="The close-fitting column guide is intentionally captured inside the outer column.",
        )
        ctx.allow_overlap(
            root,
            lift,
            elem_a="column_collar",
            elem_b="inner_column",
            reason="The inner column passes through the column collar lip as it telescopes.",
        )
    else:
        for idx, sx in SIDES:
            post = model.get_part(f"height_post_{idx}")
            ctx.allow_overlap(
                root,
                post,
                elem_a=f"outer_sleeve_{idx}",
                elem_b=f"inner_post_{idx}",
                reason="The telescoping inner post is intentionally retained inside its hollow sleeve.",
            )
            ctx.allow_overlap(
                root,
                post,
                elem_a=f"outer_sleeve_{idx}",
                elem_b=f"guide_block_{idx}",
                reason="The close-fitting polymer guide is intentionally captured inside the sleeve.",
            )
            ctx.allow_overlap(
                root,
                post,
                elem_a=f"sleeve_collar_{idx}",
                elem_b=f"inner_post_{idx}",
                reason="The sleeve collar wraps the inner post as a visible clamp ring.",
            )
        # The synchronized second post is captured by the driving post's moving rail
        # socket (O4 rail_socket L242-L247).
        post_1 = model.get_part("height_post_1")
        ctx.allow_overlap(
            mount,
            post_1,
            elem_a="moving_cross_rail",
            elem_b="rail_socket",
            reason="The moving cross rail is intentionally received by the second post's rail socket.",
        )

    # Stay hubs captured on the board's stay pins (O3 L440-L468, F_spring L479-L507).
    if r.tilt_stay != "lever_angle_lock":
        for idx, sx in SIDES:
            stay = model.get_part(f"tilt_stay_{idx}")
            ctx.allow_overlap(
                board,
                stay,
                elem_a=f"stay_pin_{idx}",
                elem_b="upper_hub",
                reason="The stay's upper hub is captured on its board-mounted pivot pin.",
            )
            ctx.allow_overlap(
                board,
                stay,
                elem_a=f"stay_pin_{idx}",
                elem_b="upper_bracket",
                reason="The stay bracket is seated around the same captured board pivot pin.",
            )
            # The stay pin is recessed into the board underside, so the hub that
            # wraps it grazes the panel -- exactly O3's board_core<->pivot_bushing
            # allowance (L410-L423).
            ctx.allow_overlap(
                board,
                stay,
                elem_a="board_core",
                elem_b="upper_hub",
                reason="The stay hub wraps a pivot pin locally recessed into the board underside.",
            )
            if r.tilt_stay == "counterbalance_spring_arms":
                ctx.allow_overlap(
                    board,
                    stay,
                    elem_a=f"stay_pin_{idx}",
                    elem_b="upper_pivot_pin",
                    reason="The counterbalance arm's pivot pin is coaxial with the board's stay pin.",
                )
        if r.tilt_stay == "curved_spline_braces":
            stay_1 = model.get_part("tilt_stay_1")
            lock = model.get_part("tilt_lock")
            ctx.allow_overlap(
                stay_1,
                lock,
                elem_a="lower_hub",
                elem_b="lock_shaft",
                reason="The tilt-lock shaft is intentionally inserted into the brace's lower hub.",
            )
        if r.tilt_stay == "folding_bar_stays":
            for idx, sx in SIDES:
                stay = model.get_part(f"tilt_stay_{idx}")
                knob = model.get_part(f"stay_knob_{idx}")
                ctx.allow_overlap(
                    stay,
                    knob,
                    elem_a="support_rivet",
                    elem_b="clamp_stem",
                    reason="The clamp knob stem is intentionally captured inside the stay rivet.",
                )
                ctx.allow_overlap(
                    stay,
                    knob,
                    elem_a="support_bar",
                    elem_b="clamp_stem",
                    reason="The same stem runs through the support bar's bore that the rivet lines.",
                )
    else:
        lever = model.get_part("angle_lever")
        ctx.allow_overlap(
            mount,
            lever,
            elem_a="lock_pivot_pin",
            elem_b="lever_hub",
            reason="The angle-lock lever's hub turns on the bracket's pivot pin (axle in hub).",
        )

    # Parallel-rule clamp shafts captured in the rule's bushings (O1 L440-L446).
    if r.board_accessory == "parallel_rule":
        rule = model.get_part("parallel_rule")
        board_panel = model.get_part("board")
        for idx, sx in SIDES:
            # The rule rides the board on its runner pads: the one intentional
            # contact between the rule and the working surface, and what carries it.
            ctx.allow_overlap(
                board_panel,
                rule,
                elem_a="board_core",
                elem_b=f"runner_pad_{idx}",
                reason="The rule's runner pad beds onto the board face as its sliding bearing.",
            )
            knob = model.get_part(f"rule_knob_{idx}")
            ctx.allow_overlap(
                rule,
                knob,
                elem_a=f"knob_bushing_{idx}",
                elem_b="shaft",
                reason="The clamp shaft is intentionally captured inside the ruler bushing.",
            )
            ctx.allow_overlap(
                rule,
                knob,
                elem_a="aluminum_bar",
                elem_b="shaft",
                reason="The clamp shaft runs through the bar's bore that knob_bushing lines.",
            )


def run_pictureX_0611_drafting_table_with_adjustable_tilt_surface_tests(
    object_model: ArticulatedObject, config: DraftingTiltTableConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_captured_fits(ctx, object_model, r)

    board = object_model.get_part("board")
    mount = object_model.get_part(r.mount_part_name)
    tilt = object_model.get_articulation("board_tilt")
    driver = object_model.get_articulation(r.height_driver_name)

    # ---- Category identity: BOTH a height stage and a real tilt hinge. ----
    ctx.check(
        "board tilt is a REVOLUTE hinge with a usable adjustment range",
        tilt.articulation_type == ArticulationType.REVOLUTE
        and abs(tilt.axis[0]) > 0.99
        and tilt.motion_limits is not None
        and tilt.motion_limits.lower is not None
        and tilt.motion_limits.upper is not None
        and (tilt.motion_limits.upper - tilt.motion_limits.lower) >= 0.50,
        details=f"axis={tilt.axis}, limits={tilt.motion_limits}",
    )
    ctx.check(
        "a real PRISMATIC height stage exists with usable travel",
        driver.articulation_type == ArticulationType.PRISMATIC
        and abs(driver.axis[2]) > 0.99
        and driver.motion_limits is not None
        and (driver.motion_limits.upper - driver.motion_limits.lower) >= 0.06,
        details=f"axis={driver.axis}, limits={driver.motion_limits}",
    )
    ctx.check(
        "the drawing board is carried across the mount width",
        ctx.part_element_world_aabb(board, elem="pivot_barrel") is not None,
        details="pivot_barrel missing",
    )

    # ---- The clearance invariant this template is built on. ----
    lo = ctx.part_world_aabb(board)
    ctx.check(
        "board clears the frame top at the closed pose",
        lo is not None and lo[0][2] > r.mount_top_z,
        details=f"board_aabb={lo}, mount_top_z={r.mount_top_z}",
    )
    with ctx.pose({tilt: r.flat_q}):
        flat = ctx.part_world_aabb(board)
        flat_ledge = ctx.part_element_world_aabb(board, elem="paper_ledge_shelf")
    with ctx.pose({tilt: r.steep_q}):
        steep = ctx.part_world_aabb(board)
    ctx.check(
        "board sweeps the full tilt range without dropping onto the frame",
        flat is not None
        and steep is not None
        and flat[0][2] > r.mount_top_z
        and steep[0][2] > r.mount_top_z,
        details=f"flat={flat}, steep={steep}, mount_top_z={r.mount_top_z}",
    )

    # ---- Targeted mechanism poses (Rule 5). ----
    # 1. Tilt: the flat limit really is horizontal and the steep limit really lifts.
    ctx.check(
        "tilting the board from flat to the steep limit raises it visibly",
        flat is not None and steep is not None and steep[1][2] > flat[1][2] + 0.08,
        details=f"flat={flat}, steep={steep}",
    )
    ledge_center = (
        None if flat_ledge is None else 0.5 * (flat_ledge[0][2] + flat_ledge[1][2])
    )
    ctx.check(
        "the flat tilt limit is the horizontal drawing pose",
        ledge_center is not None
        and abs(ledge_center - (r.hinge_z + r.board_surface_z + 0.006)) < 0.05,
        details=f"ledge_center={ledge_center}, expected={r.hinge_z + r.board_surface_z + 0.006}",
    )

    # 2. Height: the driving member really travels along +z.
    if r.is_root_mount:
        moving = object_model.get_part("leg_0")
    else:
        moving = object_model.get_part(r.mount_part_name)
    rest_pos = ctx.part_world_position(moving)
    with ctx.pose({driver: driver.motion_limits.upper}):
        raised_pos = ctx.part_world_position(moving)
    ctx.check(
        "the height stage translates the full declared travel",
        rest_pos is not None
        and raised_pos is not None
        and abs((raised_pos[2] - rest_pos[2]) - r.height_travel) < 0.004,
        details=f"rest={rest_pos}, raised={raised_pos}, travel={r.height_travel}",
    )
    # Telescoping members stay inserted at the extreme (O3 L583-L600 semantics).
    if not r.is_root_mount and r.support_base != "single_pedestal_column":
        with ctx.pose({driver: driver.motion_limits.upper}):
            for idx, sx in SIDES:
                ctx.expect_overlap(
                    object_model.get_part(f"height_post_{idx}"),
                    object_model.get_part("base"),
                    axes="z",
                    elem_a=f"inner_post_{idx}",
                    elem_b=f"outer_sleeve_{idx}",
                    min_overlap=0.04,
                    name=f"height post {idx} stays inserted at maximum height",
                )
        ctx.check(
            "the second visible post is synchronized to the driver",
            object_model.get_articulation("height_post_1").mimic is not None
            and object_model.get_articulation("height_post_1").mimic.joint == "height_post_0",
            details=f"mimic={object_model.get_articulation('height_post_1').mimic}",
        )

    # 3. Stays stay coupled to the board through the arc (never float free).
    if r.tilt_stay != "lever_angle_lock":
        for idx, sx in SIDES:
            stay_joint = object_model.get_articulation(f"stay_fold_{idx}")
            ctx.check(
                f"stay {idx} is mimic-coupled to the board tilt",
                stay_joint.mimic is not None
                and stay_joint.mimic.joint == "board_tilt"
                and abs(stay_joint.mimic.multiplier + 1.0) < 1e-9,
                details=f"mimic={stay_joint.mimic}",
            )
        stay = object_model.get_part("tilt_stay_0")
        with ctx.pose({tilt: r.flat_q}):
            rest_stay = ctx.part_world_aabb(stay)
        with ctx.pose({tilt: r.steep_q}):
            moved_stay = ctx.part_world_aabb(stay)
        ctx.check(
            "the coupled stay travels with the board rather than staying put",
            rest_stay is not None
            and moved_stay is not None
            and max(abs(moved_stay[0][k] - rest_stay[0][k]) for k in (1, 2)) > 0.01,
            details=f"rest={rest_stay}, moved={moved_stay}",
        )
    else:
        lever = object_model.get_part("angle_lever")
        lj = object_model.get_articulation("mount_to_angle_lever")
        with ctx.pose({lj: lj.motion_limits.lower}):
            a = ctx.part_element_world_aabb(lever, elem="lever_grip")
        with ctx.pose({lj: lj.motion_limits.upper}):
            b = ctx.part_element_world_aabb(lever, elem="lever_grip")
        ctx.check(
            "the angle-lock lever has an independent usable swing",
            a is not None and b is not None and abs(b[0][1] - a[0][1]) > 0.05,
            details=f"released={a}, clamped={b}",
        )

    # 4. Parallel rule slides along the board face.
    if r.board_accessory == "parallel_rule":
        rule = object_model.get_part("parallel_rule")
        rj = object_model.get_articulation("board_to_rule")
        before = ctx.part_world_position(rule)
        with ctx.pose({rj: r.rule_travel}):
            after = ctx.part_world_position(rule)
        ctx.check(
            "the parallel rule slides up the board face",
            before is not None
            and after is not None
            and math.dist(before, after) > 0.05,
            details=f"before={before}, after={after}",
        )
        ctx.expect_within(
            rule,
            board,
            axes="x",
            inner_elem="aluminum_bar",
            outer_elem="board_core",
            margin=0.0,
            name="parallel rule spans within the board width",
        )

    # 5. Rotary controls really turn.
    # NOTE: a revolute child's part origin sits ON its own axis, so
    # part_world_position CANNOT move under it -- asserting "it did not move" there
    # would pass unconditionally and prove nothing. Assert instead that each control
    # carrying an OFF-AXIS feature really sweeps that feature through the pose.
    for name, elem in (
        ("rule_knob_0", "clamp_wing"),
        ("rule_knob_1", "clamp_wing"),
        ("height_lock_0", "clamp_lever"),
        ("height_lock_1", "clamp_lever"),
    ):
        try:
            part = object_model.get_part(name)
        except Exception:
            continue
        joint = next((j for j in object_model.articulations if j.child == name), None)
        if joint is None:
            continue
        before = ctx.part_element_world_aabb(part, elem=elem)
        with ctx.pose({joint: 0.8}):
            after = ctx.part_element_world_aabb(part, elem=elem)
        swept = (
            None
            if before is None or after is None
            else max(
                abs(0.5 * (after[0][k] + after[1][k]) - 0.5 * (before[0][k] + before[1][k]))
                for k in range(3)
            )
        )
        ctx.check(
            f"{name} really turns: its off-axis {elem} sweeps to a new place",
            swept is not None and swept > 0.002,
            details=f"before={before}, after={after}, swept={swept}",
        )

    # The purely axisymmetric clamp knobs (height_knob_*, stay_knob_*) cannot show
    # rotation through geometry at all, so their semantics are asserted on the joint.
    for name in ("height_knob_0", "height_knob_c", "stay_knob_0"):
        joint = next((j for j in object_model.articulations if j.child == name), None)
        if joint is None:
            continue
        ctx.check(
            f"{name} is a real hand-turned control with a full working turn",
            joint.articulation_type
            in (ArticulationType.REVOLUTE, ArticulationType.CONTINUOUS)
            and (
                joint.articulation_type == ArticulationType.CONTINUOUS
                or (joint.motion_limits.upper - joint.motion_limits.lower) >= 1.5
            ),
            details=f"type={joint.articulation_type}, limits={joint.motion_limits}",
        )

    # ---- Rule 5: full-travel collision sweep. ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=40, ignore_fixed=True)

    # ---- Compiler-owned baseline. ----
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    return ctx.report()


__all__ = [
    "SupportBase",
    "BoardTop",
    "TiltStay",
    "BoardAccessory",
    "PaletteStyle",
    "DraftingTiltTableConfig",
    "ResolvedDraftingTiltTableConfig",
    "build_pictureX_0611_drafting_table_with_adjustable_tilt_surface",
    "build_seeded_pictureX_0611_drafting_table_with_adjustable_tilt_surface",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_seed",
    "run_pictureX_0611_drafting_table_with_adjustable_tilt_surface_tests",
]
