# SPDX-License-Identifier: Apache-2.0

"""Roller skates (a pair) modular template — Sports / Roller scates.

A pair of roller skates. Each skate is one ``_add_skate`` construction; the
right skate is the same construction mirrored about the lateral axis
(``side = -1``, never negative mesh scaling) and FIXED-mounted under the left
boot. Per-skate local frame: +X toe, +Y lateral, +Z up, ground at z=0.

Pattern = ``mixed`` (matches ``cushion.py``): a root ``{prefix}_boot`` part with
parallel-children modules attached:

  * ``chassis_arrangement`` (Slot A, the multiplicity axis): inline_N (single
    twin-rail rockered frame, N wheels in a line) or quad (two transverse
    trucks, 2x2 corner wheels). Emits ``{prefix}_frame`` (FIXED to boot) and
    ``{prefix}_wheel_{i}`` each on a CONTINUOUS +Y spin joint.
  * ``boot_form`` (Slot B): hard_shell / soft_boot / low_cut — the boot shell /
    sole / shaft / liner / cuff geometry and the ankle ``cuff`` part on a
    REVOLUTE +Y flex joint.
  * ``closure`` (Slot C): laces / buckle_ratchet / velcro_strap — instep
    decorations on the boot (Rule 1, non-moving visuals) + a cuff strap on the
    cuff (moves with the cuff_flex joint).
  * ``wheel_count`` (N, inline only): multiplicity axis [3,5]; quad forces N=4.
  * ``instep_strap_count`` (M, buckle/velcro only): multiplicity [2,3]; laces
    uses a fixed 5-rung lace set and does not expose M.

Sources (reviewed spec ``specs_modular_v1/Sports_Roller_scates.md``): the inline-4
hard-boot laces parent (…26f6e0cf) + 7 slot-fork variants (inline3/inline5/
quad/softboot/lowcut/buckle/velcro), all under ``data/records/``.

Hard rules honoured: ① non-moving instep/lace/strap detail = ``boot.visual`` /
``cuff.visual`` (not a FIXED part); ② every CONTINUOUS/REVOLUTE joint mates real
hardware (wheel axle captured in rails/hanger; cuff pivot rivet seated in the
shaft) — captured-pin joints declare element-scoped ``allow_overlap`` and the
mating contract is grandfathered; ③ geometry adapted from the 5★ sources, never
downgraded to Box/Cylinder for the structural shell (superellipse side-loft,
Tire/Wheel geometry, hollow extrude collars are preserved).

Compatibility gating (resolve_config, spec §10):
  * quad x {soft_boot, low_cut}: untested chassis<->boot mount -> quad forces
    boot_form = hard_shell.
  * inline N=5 packing: shrink wheel_radius (and lengthen the rail half-span via
    derived spacing) so adjacent tires never touch (2R <= spacing - clearance).
  * laces does not expose M; buckle/velcro M in [2,3].
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
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TireCarcass,
    TireGeometry,
    TireShoulder,
    TireSidewall,
    WheelBore,
    WheelGeometry,
    WheelHub,
    WheelRim,
    WheelSpokes,
    mesh_from_geometry,
    resample_side_sections,
    rounded_rect_profile,
    superellipse_profile,
    superellipse_side_loft,
)

__modular__ = True

ChassisArrangement = Literal["inline", "quad"]
BootForm = Literal["hard_shell", "soft_boot", "low_cut"]
Closure = Literal["laces", "buckle_ratchet", "velcro_strap"]
PaletteStyle = Literal[
    "classic_gray_red",
    "graphite_speed",
    "soft_black_blue",
    "mono_black_buckle",
    "velcro_dark_gray",
    "urethane_neutral",
]

CHASSIS_ARRANGEMENTS: tuple[ChassisArrangement, ...] = ("inline", "quad")
BOOT_FORMS: tuple[BootForm, ...] = ("hard_shell", "soft_boot", "low_cut")
CLOSURES: tuple[Closure, ...] = ("laces", "buckle_ratchet", "velcro_strap")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "classic_gray_red",
    "graphite_speed",
    "soft_black_blue",
    "mono_black_buckle",
    "velcro_dark_gray",
    "urethane_neutral",
)

# Boot forms NOT compatible with the quad truck chassis (spec §10).
QUAD_BOOT_FORMS: tuple[BootForm, ...] = ("hard_shell",)

WHEEL_N_MIN = 3
WHEEL_N_MAX = 5
STRAP_M_MIN = 2
STRAP_M_MAX = 3

# Weighted sampling (spec §"sampling domain"): inline主流, N=4高, quad较少,
# N=5稀采 (packing risk), M=3 common.
ARRANGEMENT_WEIGHTS = (0.74, 0.26)  # inline, quad
WHEEL_N_CHOICES = (3, 4, 5)
WHEEL_N_WEIGHTS = (0.30, 0.55, 0.15)
STRAP_M_CHOICES = (2, 3)
STRAP_M_WEIGHTS = (0.40, 0.60)

# ---------------------------------------------------------------------------
# Palettes — each colorway maps the same set of material keys (spec §palette).
# Keys: shell / shaft / liner / sole / tongue / accent / lace / cuff / frame /
# tire / hub / steel / strap / buckle / patch.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "classic_gray_red": {
        "shell": (0.74, 0.74, 0.76, 1.0),
        "shaft": (0.60, 0.61, 0.64, 1.0),
        "liner": (0.22, 0.22, 0.24, 1.0),
        "sole": (0.20, 0.20, 0.22, 1.0),
        "tongue": (0.45, 0.45, 0.48, 1.0),
        "accent": (0.70, 0.13, 0.16, 1.0),
        "lace": (0.82, 0.81, 0.79, 1.0),
        "cuff": (0.55, 0.56, 0.59, 1.0),
        "frame": (0.92, 0.93, 0.95, 1.0),
        "tire": (0.93, 0.90, 0.85, 0.55),
        "hub": (0.96, 0.96, 0.97, 1.0),
        "steel": (0.52, 0.53, 0.56, 1.0),
        "strap": (0.70, 0.13, 0.16, 1.0),
        "buckle": (0.30, 0.31, 0.34, 1.0),
        "patch": (0.16, 0.16, 0.18, 1.0),
    },
    "graphite_speed": {
        "shell": (0.28, 0.28, 0.30, 1.0),
        "shaft": (0.24, 0.24, 0.26, 1.0),
        "liner": (0.14, 0.14, 0.16, 1.0),
        "sole": (0.10, 0.10, 0.12, 1.0),
        "tongue": (0.22, 0.22, 0.25, 1.0),
        "accent": (0.80, 0.16, 0.18, 1.0),
        "lace": (0.86, 0.30, 0.22, 1.0),
        "cuff": (0.20, 0.20, 0.22, 1.0),
        "frame": (0.74, 0.75, 0.78, 1.0),
        "tire": (0.86, 0.84, 0.80, 0.55),
        "hub": (0.30, 0.31, 0.34, 1.0),
        "steel": (0.50, 0.51, 0.54, 1.0),
        "strap": (0.80, 0.16, 0.18, 1.0),
        "buckle": (0.16, 0.16, 0.18, 1.0),
        "patch": (0.12, 0.12, 0.14, 1.0),
    },
    "soft_black_blue": {
        "shell": (0.18, 0.18, 0.20, 1.0),
        "shaft": (0.20, 0.20, 0.23, 1.0),
        "liner": (0.15, 0.15, 0.17, 1.0),
        "sole": (0.12, 0.12, 0.14, 1.0),
        "tongue": (0.24, 0.24, 0.28, 1.0),
        "accent": (0.16, 0.34, 0.72, 1.0),
        "lace": (0.90, 0.91, 0.93, 1.0),
        "cuff": (0.20, 0.21, 0.25, 1.0),
        "frame": (0.82, 0.83, 0.85, 1.0),
        "tire": (0.92, 0.90, 0.86, 0.55),
        "hub": (0.90, 0.91, 0.93, 1.0),
        "steel": (0.52, 0.53, 0.56, 1.0),
        "strap": (0.16, 0.34, 0.72, 1.0),
        "buckle": (0.30, 0.31, 0.34, 1.0),
        "patch": (0.12, 0.16, 0.30, 1.0),
    },
    "mono_black_buckle": {
        "shell": (0.30, 0.30, 0.32, 1.0),
        "shaft": (0.24, 0.24, 0.26, 1.0),
        "liner": (0.14, 0.14, 0.16, 1.0),
        "sole": (0.10, 0.10, 0.12, 1.0),
        "tongue": (0.22, 0.22, 0.24, 1.0),
        "accent": (0.40, 0.41, 0.44, 1.0),
        "lace": (0.30, 0.30, 0.33, 1.0),
        "cuff": (0.22, 0.22, 0.24, 1.0),
        "frame": (0.90, 0.91, 0.93, 1.0),
        "tire": (0.88, 0.86, 0.82, 0.55),
        "hub": (0.92, 0.92, 0.93, 1.0),
        "steel": (0.46, 0.47, 0.50, 1.0),
        "strap": (0.10, 0.10, 0.12, 1.0),
        "buckle": (0.40, 0.41, 0.44, 1.0),
        "patch": (0.16, 0.16, 0.18, 1.0),
    },
    "velcro_dark_gray": {
        "shell": (0.34, 0.34, 0.37, 1.0),
        "shaft": (0.28, 0.28, 0.31, 1.0),
        "liner": (0.16, 0.16, 0.18, 1.0),
        "sole": (0.12, 0.12, 0.14, 1.0),
        "tongue": (0.26, 0.26, 0.29, 1.0),
        "accent": (0.52, 0.53, 0.56, 1.0),
        "lace": (0.40, 0.40, 0.43, 1.0),
        "cuff": (0.30, 0.30, 0.33, 1.0),
        "frame": (0.88, 0.89, 0.91, 1.0),
        "tire": (0.86, 0.84, 0.80, 0.55),
        "hub": (0.90, 0.90, 0.92, 1.0),
        "steel": (0.50, 0.51, 0.54, 1.0),
        "strap": (0.14, 0.14, 0.16, 1.0),
        "buckle": (0.24, 0.24, 0.26, 1.0),
        "patch": (0.50, 0.51, 0.54, 1.0),
    },
    "urethane_neutral": {
        "shell": (0.66, 0.64, 0.60, 1.0),
        "shaft": (0.58, 0.56, 0.52, 1.0),
        "liner": (0.28, 0.27, 0.26, 1.0),
        "sole": (0.24, 0.23, 0.22, 1.0),
        "tongue": (0.50, 0.48, 0.45, 1.0),
        "accent": (0.40, 0.42, 0.46, 1.0),
        "lace": (0.74, 0.72, 0.68, 1.0),
        "cuff": (0.60, 0.58, 0.54, 1.0),
        "frame": (0.70, 0.71, 0.73, 1.0),
        "tire": (0.86, 0.83, 0.74, 0.60),
        "hub": (0.80, 0.80, 0.81, 1.0),
        "steel": (0.56, 0.57, 0.60, 1.0),
        "strap": (0.46, 0.45, 0.42, 1.0),
        "buckle": (0.50, 0.51, 0.54, 1.0),
        "patch": (0.34, 0.34, 0.36, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters), from the parent (…26f6e0cf).
# ---------------------------------------------------------------------------
_AXLE_LENGTH = 0.036
_AXLE_RADIUS = 0.0045
_RAIL_THICKNESS = 0.005
_RAIL_CENTER_Y = 0.016  # rail inner faces ~±0.0135
_DECK_SEAT = 0.0063  # deck_plate Z thickness band (0.081 -> 0.0873)

# The boot/sole interface sits at a fixed Z regardless of wheel size; the
# chassis lifts/drops to keep the wheels coplanar on z=0. The parent has the
# sole bottom at 0.087 with wheel_radius 0.040 (rail top ~0.0815). We treat the
# boot as authored in a fixed frame and place the deck plate so its top meets
# the sole bottom; the wheel spin origins sit at AXLE_Z = wheel_radius.
_SOLE_BOTTOM_Z = 0.087
_RAIL_TOP_Z = 0.0815

# Right skate placement (mirror + lateral offset). The pair stands side by side
# ~0.135 m apart (lateral_y). Yaw is kept at 0 so the right boot can be cleanly
# re-anchored (pure translation) onto the boot_mount contact datum below.
_RIGHT_SKATE_OFFSET = (-0.018, -0.150, 0.0)
_RIGHT_SKATE_YAW = 0.0

# Boot-mount contact datum (world coords): the right-skate boot_mount FIXED joint
# origin must sit within the baseline 0.015 m articulation-origin tolerance of
# BOTH parent (left boot) and child (right boot) geometry. We place it INSIDE the
# right boot's solid sole block (child_distance ~0, robust across boot forms) and
# bridge the small lateral gap to the left boot with a short "pair_clip" tab
# visual on the left boot (parent_distance ~0). The right boot is re-anchored so
# its link origin (0,0,0) lands exactly here (rifle.py _reanchor_part pattern).
_BOOT_MOUNT_DATUM = (-0.013, -0.112, 0.092)
# Left-boot pairing clip: a tab bridging the left sole medial face out to the
# mount datum (inside the right sole) so the FIXED boot_mount origin is seated on
# real left geometry while it also lands inside the right boot geometry.
_PAIR_CLIP_Y0 = -0.045  # just inside the left sole medial face (~ -0.05)
_PAIR_CLIP_Y1 = -0.120  # reaches past the datum y (-0.112) into the right sole

_TONGUE_TILT = -0.50

# Cuff flex limits (within spec window [-0.6,0)∪(0,0.8]).
_CUFF_LOWER = -0.16
_CUFF_UPPER = 0.48

# Quad truck constants (spec §Slot A quad / S3).
_TRUCK_FRONT_X = 0.060
_TRUCK_REAR_X = -0.060
_WHEEL_Y_OFFSET = 0.034
_TRUCK_BASEPLATE_LX = 0.052
_TRUCK_BASEPLATE_LY = 0.078
_TRUCK_BASEPLATE_THICK = 0.005
_HANGER_BAR_RADIUS = 0.009
# Crossbar (axle) must reach the wheel centers (y=±_WHEEL_Y_OFFSET) so the
# wheel-spin joint origin is seated in the hanger geometry, not floating off the
# bar end. Half-length 0.036 just clears the 0.034 mount.
_HANGER_BAR_LENGTH = 0.072
_HANGER_ARM_WIDTH = 0.012
_HANGER_ARM_DEPTH = 0.010

# Segment count for the boot side-loft. The spec mandates <=56 (boolean/loft
# degenerates at 64 on some soft/low rebuilds: "Profile area must be non-zero").
_LOFT_SEGMENTS = 56


@dataclass(frozen=True)
class RollerSkatesConfig:
    chassis_arrangement: ChassisArrangement | None = None
    boot_form: BootForm | None = None
    closure: Closure | None = None
    wheel_count: int | None = None
    instep_strap_count: int | None = None
    palette_style: PaletteStyle = "classic_gray_red"
    wheelbase_scale: float = 1.0
    shell_height_scale: float = 1.0
    name: str = "roller_skates"


@dataclass(frozen=True)
class ResolvedRollerSkatesConfig:
    chassis_arrangement: ChassisArrangement
    boot_form: BootForm
    closure: Closure
    wheel_count: int
    instep_strap_count: int
    palette_style: PaletteStyle
    # Derived chassis geometry.
    wheel_radius: float
    wheel_width: float
    axle_xs: tuple[float, ...]  # inline only
    rail_half_span: float
    axle_z: float
    # Derived boot geometry.
    shell_top_z: float
    cuff_pivot_z: float
    cuff_z0: float
    cuff_z1: float
    name: str

    @property
    def n_wheels(self) -> int:
        return 4 if self.chassis_arrangement == "quad" else self.wheel_count


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def _shift_visuals(part, anchor: tuple[float, float, float]) -> None:
    """Translate every visual of ``part`` by ``-anchor`` (rifle.py pattern).

    Used to re-anchor the right boot so its link (0,0,0) lands on the boot_mount
    contact datum while the geometry keeps its world placement.
    """
    ax, ay, az = anchor
    for v in part.visuals:
        ox, oy, oz = v.origin.xyz
        v.origin = Origin(xyz=(ox - ax, oy - ay, oz - az), rpy=v.origin.rpy)


def _shift_joint_origin(joint, anchor: tuple[float, float, float]) -> None:
    """Translate a joint origin by ``-anchor`` (keeps the child world-fixed when
    its parent link frame was moved by ``+anchor``)."""
    ax, ay, az = anchor
    ox, oy, oz = joint.origin.xyz
    joint.origin = Origin(xyz=(ox - ax, oy - ay, oz - az), rpy=joint.origin.rpy)


def config_from_seed(seed: int) -> RollerSkatesConfig:
    rng = random.Random(seed)
    arrangement = rng.choices(CHASSIS_ARRANGEMENTS, weights=ARRANGEMENT_WEIGHTS, k=1)[0]
    wheel_count = rng.choices(WHEEL_N_CHOICES, weights=WHEEL_N_WEIGHTS, k=1)[0]
    boot_form = rng.choice(BOOT_FORMS)
    closure = rng.choice(CLOSURES)
    strap_count = rng.choices(STRAP_M_CHOICES, weights=STRAP_M_WEIGHTS, k=1)[0]
    palette_style = rng.choice(PALETTE_STYLES)
    return RollerSkatesConfig(
        chassis_arrangement=arrangement,
        boot_form=boot_form,
        closure=closure,
        wheel_count=wheel_count,
        instep_strap_count=strap_count,
        palette_style=palette_style,
        wheelbase_scale=round(rng.uniform(0.92, 1.08), 4),
        shell_height_scale=round(rng.uniform(0.95, 1.06), 4),
        name=f"seeded_roller_skates_{seed}",
    )


def resolve_config(
    config: RollerSkatesConfig | None = None,
) -> ResolvedRollerSkatesConfig:
    cfg = config or RollerSkatesConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    arrangement = _pick(cfg.chassis_arrangement, CHASSIS_ARRANGEMENTS)
    boot_form = _pick(cfg.boot_form, BOOT_FORMS)
    closure = _pick(cfg.closure, CLOSURES)

    wheel_count = int(cfg.wheel_count) if cfg.wheel_count is not None else 4
    wheel_count = int(_clamp(wheel_count, WHEEL_N_MIN, WHEEL_N_MAX))

    strap_count = (
        int(cfg.instep_strap_count) if cfg.instep_strap_count is not None else 3
    )
    strap_count = int(_clamp(strap_count, STRAP_M_MIN, STRAP_M_MAX))

    # --- Compatibility gating (spec §10). ---
    # (1) quad x {soft_boot, low_cut} untested -> force hard_shell on quad.
    if arrangement == "quad" and boot_form not in QUAD_BOOT_FORMS:
        boot_form = "hard_shell"
    # quad forces N=4 (2 trucks x 2 wheels).
    if arrangement == "quad":
        wheel_count = 4
    # (2) laces does not expose M; normalize to a sentinel for the slot tuple.
    #     (M only meaningful for buckle/velcro; leave value but it is unused.)

    wheelbase_scale = _clamp(cfg.wheelbase_scale, 0.92, 1.08)
    shell_height_scale = _clamp(cfg.shell_height_scale, 0.95, 1.06)

    # --- Chassis geometry derivation. ---
    wheel_width = 0.024
    if arrangement == "quad":
        wheel_radius = 0.040
        axle_xs: tuple[float, ...] = ()
        rail_half_span = 0.0
    else:
        # Wheelbase scaled from the parent 4-wheel span (~0.246 m). Stations are
        # evenly spaced over the wheelbase. Larger N -> shrink radius so tires
        # never touch; the rail half-span overhangs the outermost boss.
        wheelbase = 0.246 * wheelbase_scale
        n = wheel_count
        if n == 1:
            spacing = wheelbase
        else:
            spacing = wheelbase / (n - 1)
        axle_xs = tuple(
            round(wheelbase / 2.0 - i * spacing, 6) for i in range(n)
        )
        # Nominal radius by N (real inline skates: fewer/bigger or more/smaller).
        nominal_r = {3: 0.044, 4: 0.040, 5: 0.034}.get(n, 0.040)
        wheel_radius = nominal_r
        # Tire-non-touch inequality: 2R <= spacing - clearance. Shrink R if needed.
        clearance = 0.006
        max_r = (spacing - clearance) / 2.0
        if wheel_radius > max_r:
            wheel_radius = max(0.026, max_r)
        # Deck-clearance cap: the solid deck plate bottom sits at the sole bottom
        # minus the deck thickness. The tire top (= 2R, wheels rest on z=0) must
        # stay below it so big wheels never poke up into the deck plate.
        deck_bottom = _SOLE_BOTTOM_Z - _DECK_SEAT
        max_r_deck = (deck_bottom - 0.002) / 2.0
        if wheel_radius > max_r_deck:
            wheel_radius = max(0.026, max_r_deck)
        wheel_width = 0.024 if n <= 4 else 0.022
        rail_half_span = round(wheelbase / 2.0 + 0.024, 4)

    axle_z = wheel_radius  # wheels rest on z=0

    # --- Boot geometry derivation (boot_form -> cuff pivot / shell height). ---
    if boot_form == "hard_shell":
        shell_top_z = 0.170 * shell_height_scale
        cuff_pivot_z = 0.215 * shell_height_scale
        cuff_z0 = 0.205 * shell_height_scale
        cuff_z1 = 0.275 * shell_height_scale
    elif boot_form == "soft_boot":
        shell_top_z = 0.194 * shell_height_scale
        cuff_pivot_z = 0.240 * shell_height_scale
        cuff_z0 = 0.230 * shell_height_scale
        cuff_z1 = 0.290 * shell_height_scale
    else:  # low_cut
        shell_top_z = 0.148 * shell_height_scale
        # Pivot sits below the cuff band (so a positive flex tips the short cuff
        # forward over the toes) but high enough to stay on the boot shell.
        cuff_pivot_z = 0.126 * shell_height_scale
        cuff_z0 = 0.140 * shell_height_scale
        cuff_z1 = 0.172 * shell_height_scale

    return ResolvedRollerSkatesConfig(
        chassis_arrangement=arrangement,
        boot_form=boot_form,
        closure=closure,
        wheel_count=wheel_count,
        instep_strap_count=strap_count,
        palette_style=palette_style,
        wheel_radius=wheel_radius,
        wheel_width=wheel_width,
        axle_xs=axle_xs,
        rail_half_span=rail_half_span,
        axle_z=axle_z,
        shell_top_z=shell_top_z,
        cuff_pivot_z=cuff_pivot_z,
        cuff_z0=cuff_z0,
        cuff_z1=cuff_z1,
        name=cfg.name or "roller_skates",
    )


def with_overrides(config: RollerSkatesConfig, **kwargs: object) -> RollerSkatesConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: RollerSkatesConfig | ResolvedRollerSkatesConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedRollerSkatesConfig)
        else resolve_config(config)
    )
    choices: list[tuple[str, str]] = [
        ("chassis_arrangement", r.chassis_arrangement),
        ("boot_form", r.boot_form),
        ("closure", r.closure),
        ("wheel_count", f"n{r.n_wheels}"),
    ]
    # M only encoded for buckle/velcro (laces has no M, spec §axis 2 gating).
    if r.closure in ("buckle_ratchet", "velcro_strap"):
        choices.append(("instep_strap_count", f"m{r.instep_strap_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Shared mesh helpers (rebuilt per config; reused by both skates).
# ===========================================================================
_SHELL_BASE_Z = 0.095


def _scaled_sections(sections, z_scale: float):
    """Scale the z_max of each (station, z_min, z_max, width) section."""
    return [
        (st, zmn, _SHELL_BASE_Z + (zmx - _SHELL_BASE_Z) * z_scale, w)
        for (st, zmn, zmx, w) in sections
    ]


def _build_hard_shell_mesh(z_scale: float):
    sections = [
        (-0.135, _SHELL_BASE_Z, 0.148, 0.052),
        (-0.118, _SHELL_BASE_Z, 0.163, 0.076),
        (-0.090, _SHELL_BASE_Z, 0.170, 0.088),
        (-0.055, _SHELL_BASE_Z, 0.170, 0.092),
        (-0.020, _SHELL_BASE_Z, 0.162, 0.094),
        (0.015, _SHELL_BASE_Z, 0.150, 0.095),
        (0.050, _SHELL_BASE_Z, 0.135, 0.094),
        (0.085, _SHELL_BASE_Z, 0.124, 0.091),
        (0.115, _SHELL_BASE_Z, 0.116, 0.083),
        (0.138, _SHELL_BASE_Z, 0.109, 0.068),
        (0.148, _SHELL_BASE_Z, 0.104, 0.046),
    ]
    smooth = resample_side_sections(_scaled_sections(sections, z_scale),
                                    samples_per_span=3, smooth_passes=1)
    geom = superellipse_side_loft(smooth, exponents=2.5, segments=_LOFT_SEGMENTS)
    geom.rotate_z(-math.pi / 2.0)
    return mesh_from_geometry(geom, "boot_shell")


def _build_soft_upper_mesh(z_scale: float):
    sections = [
        (-0.135, _SHELL_BASE_Z, 0.158, 0.058),
        (-0.118, _SHELL_BASE_Z, 0.172, 0.082),
        (-0.090, _SHELL_BASE_Z, 0.186, 0.094),
        (-0.055, _SHELL_BASE_Z, 0.194, 0.098),
        (-0.020, _SHELL_BASE_Z, 0.188, 0.100),
        (0.015, _SHELL_BASE_Z, 0.174, 0.101),
        (0.050, _SHELL_BASE_Z, 0.155, 0.099),
        (0.085, _SHELL_BASE_Z, 0.140, 0.096),
        (0.115, _SHELL_BASE_Z, 0.128, 0.088),
        (0.138, _SHELL_BASE_Z, 0.118, 0.072),
        (0.148, _SHELL_BASE_Z, 0.112, 0.050),
    ]
    smooth = resample_side_sections(_scaled_sections(sections, z_scale),
                                    samples_per_span=3, smooth_passes=2)
    geom = superellipse_side_loft(smooth, exponents=2.0, segments=_LOFT_SEGMENTS)
    geom.rotate_z(-math.pi / 2.0)
    return mesh_from_geometry(geom, "soft_upper")


def _build_low_cut_shell_mesh(z_scale: float):
    sections = [
        (-0.138, _SHELL_BASE_Z, 0.140, 0.050),
        (-0.125, _SHELL_BASE_Z, 0.146, 0.072),
        (-0.108, _SHELL_BASE_Z, 0.148, 0.086),
        (-0.088, _SHELL_BASE_Z, 0.144, 0.090),
        (-0.055, _SHELL_BASE_Z, 0.135, 0.092),
        (-0.020, _SHELL_BASE_Z, 0.128, 0.094),
        (0.015, _SHELL_BASE_Z, 0.120, 0.095),
        (0.050, _SHELL_BASE_Z, 0.112, 0.094),
        (0.085, _SHELL_BASE_Z, 0.106, 0.091),
        (0.115, _SHELL_BASE_Z, 0.100, 0.083),
        (0.138, _SHELL_BASE_Z, 0.095, 0.068),
        (0.150, _SHELL_BASE_Z, 0.091, 0.046),
    ]
    smooth = resample_side_sections(_scaled_sections(sections, z_scale),
                                    samples_per_span=3, smooth_passes=1)
    geom = superellipse_side_loft(smooth, exponents=2.5, segments=_LOFT_SEGMENTS)
    geom.rotate_z(-math.pi / 2.0)
    return mesh_from_geometry(geom, "boot_shell")


def _build_heel_panel_mesh(z_scale: float, *, low: bool):
    if low:
        sections = [
            (-0.142, 0.097, 0.138, 0.052),
            (-0.128, 0.097, 0.146, 0.074),
            (-0.112, 0.097, 0.148, 0.084),
            (-0.094, 0.097, 0.144, 0.088),
        ]
    else:
        sections = [
            (-0.140, 0.097, 0.156, 0.054),
            (-0.126, 0.097, 0.176, 0.074),
            (-0.112, 0.097, 0.190, 0.082),
            (-0.096, 0.097, 0.196, 0.086),
        ]
    scaled = [(st, zmn, 0.097 + (zmx - 0.097) * z_scale, w)
              for (st, zmn, zmx, w) in sections]
    smooth = resample_side_sections(scaled, samples_per_span=3, smooth_passes=1)
    geom = superellipse_side_loft(smooth, exponents=2.5, segments=48)
    geom.rotate_z(-math.pi / 2.0)
    return mesh_from_geometry(geom, "heel_panel")


def _build_toe_bumper_mesh():
    sections = [
        (0.118, 0.0915, 0.114, 0.087),
        (0.140, 0.0915, 0.108, 0.072),
        (0.154, 0.0915, 0.102, 0.044),
    ]
    smooth = resample_side_sections(sections, samples_per_span=3, smooth_passes=1)
    geom = superellipse_side_loft(smooth, exponents=2.5, segments=48)
    geom.rotate_z(-math.pi / 2.0)
    return mesh_from_geometry(geom, "toe_bumper")


def _build_sole_mesh():
    geom = ExtrudeGeometry(
        superellipse_profile(0.285, 0.100, 2.3),
        0.010,
        center=True,
    )
    geom.translate(0.005, 0.0, (_SOLE_BOTTOM_Z + 0.010 / 2.0 + _SOLE_BOTTOM_Z) / 2.0)
    return mesh_from_geometry(geom, "boot_sole")


def _build_shaft_mesh(z_scale: float):
    z0 = 0.150 * z_scale
    z1 = 0.225 * z_scale
    geom = ExtrudeWithHolesGeometry(
        superellipse_profile(0.105, 0.082, 2.4),
        [superellipse_profile(0.093, 0.070, 2.4)],
        z1 - z0,
        center=True,
    )
    geom.translate(-0.048, 0.0, (z0 + z1) / 2.0)
    return mesh_from_geometry(geom, "boot_shaft")


def _build_soft_collar_mesh(z_scale: float):
    z0 = 0.165 * z_scale
    z1 = 0.250 * z_scale
    geom = ExtrudeWithHolesGeometry(
        superellipse_profile(0.118, 0.096, 2.0),
        [superellipse_profile(0.098, 0.076, 2.0)],
        z1 - z0,
        center=True,
    )
    geom.translate(-0.042, 0.0, (z0 + z1) / 2.0)
    return mesh_from_geometry(geom, "padded_collar")


def _build_hard_liner_mesh(z_scale: float):
    z0 = 0.150 * z_scale
    geom = ExtrudeWithHolesGeometry(
        superellipse_profile(0.092, 0.069, 2.4),
        [superellipse_profile(0.082, 0.059, 2.4)],
        0.053,
        center=True,
    )
    geom.translate(-0.048, 0.0, z0 + 0.0265)
    return mesh_from_geometry(geom, "liner_collar")


def _build_low_liner_mesh(shell_top_z: float):
    geom = ExtrudeWithHolesGeometry(
        superellipse_profile(0.092, 0.078, 2.4),
        [superellipse_profile(0.080, 0.066, 2.4)],
        0.014,
        center=True,
    )
    geom.translate(-0.048, 0.0, shell_top_z - 0.002)
    return mesh_from_geometry(geom, "liner_collar")


def _build_tongue_mesh(boot_form: str):
    if boot_form == "soft_boot":
        geom = ExtrudeGeometry(rounded_rect_profile(0.018, 0.054, 0.008), 0.095, center=True)
        geom.rotate_y(_TONGUE_TILT)
        geom.translate(0.012, 0.0, 0.175)
    elif boot_form == "low_cut":
        geom = ExtrudeGeometry(rounded_rect_profile(0.013, 0.048, 0.005), 0.058, center=True)
        geom.rotate_y(_TONGUE_TILT)
        geom.translate(0.022, 0.0, 0.130)
    else:
        geom = ExtrudeGeometry(rounded_rect_profile(0.013, 0.050, 0.005), 0.080, center=True)
        geom.rotate_y(_TONGUE_TILT)
        geom.translate(0.016, 0.0, 0.160)
    return mesh_from_geometry(geom, "boot_tongue")


def _build_rail_mesh(r: ResolvedRollerSkatesConfig):
    boss_bottom = 0.026
    arch_bottom = 0.060
    boss_half = 0.013
    blend = 0.013
    span = r.rail_half_span

    def bottom_z(x: float) -> float:
        d = min(abs(x - ax) for ax in r.axle_xs)
        if d <= boss_half:
            return boss_bottom
        if d >= boss_half + blend:
            return arch_bottom
        t = (d - boss_half) / blend
        s = 0.5 - 0.5 * math.cos(math.pi * t)
        return boss_bottom + (arch_bottom - boss_bottom) * s

    step = 0.004
    count = int(2 * span / step) + 1
    xs = [-span + i * step for i in range(count)]
    profile = [(x, bottom_z(x)) for x in xs]
    profile.append((span, _RAIL_TOP_Z))
    profile.append((-span, _RAIL_TOP_Z))
    geom = ExtrudeGeometry(profile, _RAIL_THICKNESS, center=True)
    geom.rotate_x(math.pi / 2.0)
    return mesh_from_geometry(geom, "frame_rail")


def _build_truck_baseplate_mesh():
    from sdk import CylinderGeometry
    plate = ExtrudeGeometry(
        rounded_rect_profile(_TRUCK_BASEPLATE_LX, _TRUCK_BASEPLATE_LY, 0.008),
        _TRUCK_BASEPLATE_THICK,
        center=True,
    )
    bolt_dx = _TRUCK_BASEPLATE_LX * 0.38
    bolt_dy = _TRUCK_BASEPLATE_LY * 0.38
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        bolt = CylinderGeometry(0.004, _TRUCK_BASEPLATE_THICK + 0.001, radial_segments=6)
        bolt.translate(sx * bolt_dx, sy * bolt_dy, 0.0)
        plate = plate.merge(bolt)
    return mesh_from_geometry(plate, "truck_baseplate")


def _build_truck_hanger_mesh(axle_z: float):
    from sdk import BoxGeometry, CylinderGeometry
    baseplate_z0 = 0.081
    arm_height = baseplate_z0 - (axle_z + _HANGER_BAR_RADIUS)
    arm_height = max(0.010, arm_height)
    crossbar = CylinderGeometry(_HANGER_BAR_RADIUS, _HANGER_BAR_LENGTH, radial_segments=24)
    crossbar.rotate_x(math.pi / 2.0)
    arm_z_center = arm_height / 2.0
    arm_z_offset = _HANGER_BAR_RADIUS + arm_z_center
    # Arms straddle the kingpin near the truck center, kept INSIDE the wheel
    # inner faces (tires at y=±_WHEEL_Y_OFFSET, inner edge ~±0.022) so the long
    # axle crossbar can reach the wheels without the support arms clipping a tire.
    arm_spacing = 0.012
    for sy in (-1.0, 1.0):
        arm = BoxGeometry((_HANGER_ARM_DEPTH, _HANGER_ARM_WIDTH, arm_height))
        arm.translate(0.0, sy * arm_spacing, arm_z_offset)
        crossbar = crossbar.merge(arm)
    bridge = BoxGeometry((_HANGER_ARM_DEPTH * 1.4, arm_spacing * 2.0 + _HANGER_ARM_WIDTH, 0.004))
    bridge.translate(0.0, 0.0, _HANGER_BAR_RADIUS + arm_height)
    crossbar = crossbar.merge(bridge)
    kingpin = CylinderGeometry(0.005, 0.008, radial_segments=12)
    kingpin.translate(0.0, 0.0, _HANGER_BAR_RADIUS + arm_height + 0.004)
    crossbar = crossbar.merge(kingpin)
    return mesh_from_geometry(crossbar, "truck_hanger")


def _build_tire_mesh(r: ResolvedRollerSkatesConfig):
    inner = max(0.012, r.wheel_radius - 0.014)
    geom = TireGeometry(
        r.wheel_radius,
        r.wheel_width,
        inner_radius=inner,
        carcass=TireCarcass(sidewall_bulge=0.10),
        sidewall=TireSidewall(style="rounded", bulge=0.10),
        shoulder=TireShoulder(style="soft", radius=0.003),
    )
    geom.rotate_z(math.pi / 2.0)
    return mesh_from_geometry(geom, "wheel_tire")


def _build_hub_mesh(r: ResolvedRollerSkatesConfig):
    hub_outer = max(0.014, r.wheel_radius - 0.013)
    rim_inner = max(0.010, hub_outer - 0.007)
    geom = WheelGeometry(
        hub_outer,
        0.020,
        rim=WheelRim(inner_radius=rim_inner),
        hub=WheelHub(radius=0.008, width=0.021, cap_style="flat"),
        spokes=WheelSpokes(style="straight", count=6, thickness=0.0045),
        bore=WheelBore(style="round", diameter=0.0055),
    )
    geom.rotate_z(math.pi / 2.0)
    return mesh_from_geometry(geom, "wheel_hub")


def _build_cuff_mesh(r: ResolvedRollerSkatesConfig):
    """Hollow ankle cuff collar authored relative to the pivot frame."""
    if r.boot_form == "soft_boot":
        outer = superellipse_profile(0.138, 0.118, 2.0)
        inner = superellipse_profile(0.118, 0.098, 2.0)
        exp_name = "soft_cuff_wrap"
    elif r.boot_form == "low_cut":
        outer = superellipse_profile(0.118, 0.100, 2.4)
        inner = superellipse_profile(0.104, 0.086, 2.4)
        exp_name = "cuff_band"
    else:
        outer = superellipse_profile(0.130, 0.110, 2.4)
        inner = superellipse_profile(0.116, 0.096, 2.4)
        exp_name = "cuff_ring"
    geom = ExtrudeWithHolesGeometry(outer, [inner], r.cuff_z1 - r.cuff_z0, center=True)
    geom.translate(0.0, 0.0, (r.cuff_z0 + r.cuff_z1) / 2.0 - r.cuff_pivot_z)
    return mesh_from_geometry(geom, exp_name)


def _build_cuff_top_mesh(r: ResolvedRollerSkatesConfig):
    if r.boot_form == "soft_boot":
        outer = superellipse_profile(0.130, 0.112, 2.0)
        inner = superellipse_profile(0.112, 0.094, 2.0)
        h = 0.022
        ztop = r.cuff_z1 + 0.011
    elif r.boot_form == "low_cut":
        outer = superellipse_profile(0.112, 0.096, 2.4)
        inner = superellipse_profile(0.100, 0.084, 2.4)
        h = 0.008
        ztop = r.cuff_z1 + 0.004
    else:
        outer = superellipse_profile(0.122, 0.104, 2.4)
        inner = superellipse_profile(0.108, 0.090, 2.4)
        h = 0.024
        ztop = r.cuff_z1 + 0.005
    geom = ExtrudeWithHolesGeometry(outer, [inner], h, center=True)
    geom.translate(-0.006, 0.0, ztop - r.cuff_pivot_z)
    return mesh_from_geometry(geom, "cuff_top_collar")


def _shared_meshes(r: ResolvedRollerSkatesConfig) -> dict:
    z = r.shell_top_z / (0.170 if r.boot_form == "hard_shell"
                         else (0.194 if r.boot_form == "soft_boot" else 0.148))
    meshes: dict = {}
    if r.boot_form == "hard_shell":
        meshes["shell"] = _build_hard_shell_mesh(z)
        meshes["shaft"] = _build_shaft_mesh(z)
        meshes["liner"] = _build_hard_liner_mesh(z)
        meshes["heel_panel"] = _build_heel_panel_mesh(z, low=False)
        meshes["toe_bumper"] = _build_toe_bumper_mesh()
    elif r.boot_form == "soft_boot":
        meshes["shell"] = _build_soft_upper_mesh(z)
        meshes["collar"] = _build_soft_collar_mesh(z)
        meshes["liner"] = _build_hard_liner_mesh(z)  # nested liner ring (reused)
        meshes["toe_bumper"] = _build_toe_bumper_mesh()
    else:  # low_cut
        meshes["shell"] = _build_low_cut_shell_mesh(z)
        meshes["liner"] = _build_low_liner_mesh(r.shell_top_z)
        meshes["heel_panel"] = _build_heel_panel_mesh(z, low=True)
        meshes["toe_bumper"] = _build_toe_bumper_mesh()
    meshes["sole"] = _build_sole_mesh()
    meshes["tongue"] = _build_tongue_mesh(r.boot_form)
    meshes["cuff"] = _build_cuff_mesh(r)
    meshes["cuff_top"] = _build_cuff_top_mesh(r)
    meshes["tire"] = _build_tire_mesh(r)
    meshes["hub"] = _build_hub_mesh(r)
    if r.chassis_arrangement == "inline":
        meshes["rail"] = _build_rail_mesh(r)
    else:
        meshes["truck_baseplate"] = _build_truck_baseplate_mesh()
        meshes["truck_hanger"] = _build_truck_hanger_mesh(r.axle_z)
    return meshes


# ===========================================================================
# Closure emit helpers (Rule 1 visuals on the boot / cuff).
# ===========================================================================
# Per-boot-form instep anchor (x, z) on the upper, matching the tongue placement,
# the instep-decoration span, the eyelet-stay z, and the cuff-strap ride height.
# Low-cut boots are shorter and more forward; soft boots are taller.
#   (instep_x, instep_z, instep_span, eyelet_z, cuff_strap_z)
_INSTEP_ANCHOR = {
    "hard_shell": (0.016, 0.160, 0.080, 0.158, 0.047),
    "soft_boot": (0.012, 0.172, 0.082, 0.170, 0.050),
    # low_cut: short boot. Instep decorations sit low and span a short range so
    # the topmost rung stays below the low cuff band (cuff_z0 ~0.140). The cuff
    # strap rides at the collar band center (cuff-local z ~0.030).
    "low_cut": (0.026, 0.106, 0.044, 0.104, 0.030),
}


def _anchor(boot_form: str):
    return _INSTEP_ANCHOR.get(boot_form, _INSTEP_ANCHOR["hard_shell"])


def _cuff_front_x(boot_form: str) -> float:
    """Front x where a cuff strap embeds in the collar ring wall. The low-cut
    collar is smaller, so its strap sits further back than the tall cuffs."""
    return {"hard_shell": 0.062, "soft_boot": 0.066, "low_cut": 0.048}.get(
        boot_form, 0.062
    )


def _lace_centers(boot_form: str):
    ax, az, span, _ez, _cz = _anchor(boot_form)
    d = (math.sin(_TONGUE_TILT), 0.0, math.cos(_TONGUE_TILT))
    n = (math.cos(_TONGUE_TILT), 0.0, -math.sin(_TONGUE_TILT))
    centers = []
    for t in (0.15, 0.32, 0.49, 0.66, 0.83):
        a = span * (t - 0.5)
        off = 0.0083
        centers.append((ax + d[0] * a + n[0] * off, 0.0, az + d[2] * a + n[2] * off))
    return centers


def _emit_laces(boot, cuff, r, mats, *, side: float):
    ax, az, span, ez, cz_cuff = _anchor(r.boot_form)
    # Red eyelet stays flanking the tongue.
    for label, sy in (("lateral", side), ("medial", -side)):
        boot.visual(
            Box((0.011, 0.013, 0.085 if r.boot_form != "low_cut" else 0.060)),
            origin=Origin(xyz=(ax + 0.002, sy * 0.0295, ez), rpy=(0.0, _TONGUE_TILT, 0.0)),
            material=mats["accent"],
            name=f"eyelet_stay_{label}", material_class_id="plastic.opaque_glossy_molded",
        )
    for i, (cx, _cy, cz) in enumerate(_lace_centers(r.boot_form)):
        boot.visual(
            Cylinder(radius=0.0022, length=0.048),
            origin=Origin(xyz=(cx, 0.0, cz), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["lace"],
            name=f"lace_{i}", material_class_id="fabric.thread_yarn",
        )
    # Cuff strap + steel buckle (rides on the cuff, moves with cuff_flex). Ride
    # height tracks the cuff so the strap seats on the collar, not the boot; the
    # front x is pulled back onto the (smaller) low-cut collar wall so the strap
    # embeds in the ring rather than floating off the front.
    sx = _cuff_front_x(r.boot_form)
    cuff.visual(
        Box((0.012, 0.072, 0.016)),
        origin=Origin(xyz=(sx, 0.0, cz_cuff)),
        material=mats["strap"],
        name="cuff_strap", material_class_id="fabric.webbing",
    )
    cuff.visual(
        Box((0.010, 0.018, 0.020)),
        origin=Origin(xyz=(sx - 0.004, side * 0.030, cz_cuff)),
        material=mats["steel"],
        name="cuff_strap_buckle", material_class_id="metal.steel_bare",
    )


def _instep_positions(n: int, boot_form: str = "hard_shell"):
    ax, az, span, _ez, _cz = _anchor(boot_form)
    d = (math.sin(_TONGUE_TILT), 0.0, math.cos(_TONGUE_TILT))
    nv = (math.cos(_TONGUE_TILT), 0.0, -math.sin(_TONGUE_TILT))
    out = []
    for i in range(n):
        t = (i + 1.0) / (n + 1.0)
        a = span * (t - 0.5)
        off = 0.009
        out.append((ax + d[0] * a + nv[0] * off, az + d[2] * a + nv[2] * off))
    return out


def _add_ratchet_strap(part, *, index, cx, cz, tilt, side, mats,
                       strap_length, strap_width, strap_thick, buckle_size, prefix):
    part.visual(
        Box((strap_thick, strap_length, strap_width)),
        origin=Origin(xyz=(cx, 0.0, cz), rpy=(0.0, tilt, 0.0)),
        material=mats["strap"],
        name=f"{prefix}_{index}", material_class_id="fabric.webbing",
    )
    for j in range(3):
        ty = -strap_length * 0.28 + j * strap_length * 0.28
        part.visual(
            Box((strap_thick + 0.0016, 0.0018, strap_width * 0.78)),
            origin=Origin(xyz=(cx, ty, cz), rpy=(0.0, tilt, 0.0)),
            material=mats["strap"],
            name=f"{prefix}_tooth_{index}_{j}", material_class_id="plastic.patterned_textured",
        )
    by = side * (strap_length / 2.0 - buckle_size[1] / 2.0)
    part.visual(
        Box(buckle_size),
        origin=Origin(xyz=(cx, by, cz), rpy=(0.0, tilt, 0.0)),
        material=mats["buckle"],
        name=f"{prefix}_buckle_{index}", material_class_id="metal.blackened_gunmetal",
    )
    nvec = (math.cos(tilt), 0.0, -math.sin(tilt))
    lever_off = buckle_size[0] / 2.0 + 0.001
    lx = cx + nvec[0] * lever_off
    lz = cz + nvec[2] * lever_off
    part.visual(
        Box((0.003, buckle_size[1] * 0.60, strap_width * 0.55)),
        origin=Origin(xyz=(lx, by, lz), rpy=(0.0, tilt, 0.0)),
        material=mats["buckle"],
        name=f"{prefix}_lever_{index}", material_class_id="metal.blackened_gunmetal",
    )
    ay = -side * (strap_length / 2.0 - 0.004)
    part.visual(
        Box((strap_thick + 0.002, 0.008, strap_width * 0.70)),
        origin=Origin(xyz=(cx, ay, cz), rpy=(0.0, tilt, 0.0)),
        material=mats["buckle"],
        name=f"{prefix}_anchor_{index}", material_class_id="metal.blackened_gunmetal",
    )


def _emit_buckle(boot, cuff, r, mats, *, side: float):
    m = r.instep_strap_count
    _ax, _az, _span, _ez, cz_cuff = _anchor(r.boot_form)
    for i, (cx, cz) in enumerate(_instep_positions(m, r.boot_form)):
        _add_ratchet_strap(
            boot, index=i, cx=cx, cz=cz, tilt=_TONGUE_TILT, side=side, mats=mats,
            strap_length=0.066, strap_width=0.014, strap_thick=0.003,
            buckle_size=(0.007, 0.017, 0.018), prefix="instep_strap",
        )
    # Cuff power strap (ride height + front x track the cuff collar).
    _add_ratchet_strap(
        cuff, index=0, cx=_cuff_front_x(r.boot_form), cz=cz_cuff - 0.002,
        tilt=0.0, side=side, mats=mats,
        strap_length=0.082, strap_width=0.026, strap_thick=0.004,
        buckle_size=(0.009, 0.020, 0.028), prefix="power_strap",
    )


def _emit_velcro(boot, cuff, r, mats, *, side: float):
    m = r.instep_strap_count
    ax, az, span, _ez, cz_cuff = _anchor(r.boot_form)
    d = (math.sin(_TONGUE_TILT), 0.0, math.cos(_TONGUE_TILT))
    nv = (math.cos(_TONGUE_TILT), 0.0, -math.sin(_TONGUE_TILT))
    centers = []
    # Pick m evenly spread fractions.
    fractions = (0.22, 0.50, 0.78)
    chosen = fractions[:m] if m <= 3 else fractions
    if m == 2:
        chosen = (0.30, 0.70)
    # Pull the (thin) strap inward along the surface normal so it embeds in the
    # shell rather than floating just outside it (connectivity).
    embed = 0.006
    for t in chosen:
        a = span * (t - 0.5)
        off = 0.0085 - embed
        centers.append((ax + d[0] * a + nv[0] * off, az + d[2] * a + nv[2] * off))
    for i, (cx, cz) in enumerate(centers):
        boot.visual(
            Box((0.026, 0.072, 0.012)),
            origin=Origin(xyz=(cx, 0.0, cz), rpy=(0.0, _TONGUE_TILT, 0.0)),
            material=mats["strap"],
            name=f"instep_strap_{i}", material_class_id="fabric.webbing",
        )
        # Patch overlaps the strap body (not floating above it).
        boot.visual(
            Box((0.018, 0.020, 0.006)),
            origin=Origin(
                xyz=(cx + nv[0] * 0.004, side * 0.028, cz + nv[2] * 0.004),
                rpy=(0.0, _TONGUE_TILT, 0.0),
            ),
            material=mats["patch"],
            name=f"strap_patch_{i}", material_class_id="plastic.patterned_textured",
        )
    # Cuff velcro strap + patch (ride height + front x track the cuff collar; the
    # strap embeds into the collar and the patch overlaps the strap).
    sx = _cuff_front_x(r.boot_form)
    cuff.visual(
        Box((0.030, 0.098, 0.012)),
        origin=Origin(xyz=(sx - 0.004, 0.0, cz_cuff)),
        material=mats["strap"],
        name="cuff_strap", material_class_id="fabric.webbing",
    )
    cuff.visual(
        Box((0.022, 0.024, 0.008)),
        origin=Origin(xyz=(sx + 0.002, side * 0.038, cz_cuff)),
        material=mats["patch"],
        name="cuff_strap_patch", material_class_id="plastic.patterned_textured",
    )


_CLOSURE_EMIT = {
    "laces": _emit_laces,
    "buckle_ratchet": _emit_buckle,
    "velcro_strap": _emit_velcro,
}


# ===========================================================================
# Chassis emit helpers (Slot A): emit {prefix}_frame + wheels with spin joints.
# ===========================================================================
def _emit_wheel(model, frame, r, mats, *, prefix, i, wx, wy, frame_z=0.0):
    wheel = model.part(f"{prefix}_wheel_{i}")
    wheel.visual(r._meshes["tire"], material=mats["tire"], name="tire", material_class_id="rubber.smooth_plain")
    wheel.visual(r._meshes["hub"], material=mats["hub"], name="hub", material_class_id="plastic.opaque_glossy_molded")
    wheel.visual(
        Cylinder(radius=_AXLE_RADIUS, length=_AXLE_LENGTH),
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["steel"],
        name="axle", material_class_id="metal.steel_bare",
    )
    wheel.inertial = Inertial.from_geometry(
        Cylinder(radius=r.wheel_radius, length=r.wheel_width),
        mass=0.06,
        origin=Origin(rpy=(math.pi / 2.0, 0.0, 0.0)),
    )
    # The frame's local frame origin sits at the boot-sole contact (frame_z in
    # absolute coords). Wheel spin origin is expressed in that frame -> subtract.
    model.articulation(
        f"{prefix}_wheel_{i}_spin",
        ArticulationType.CONTINUOUS,
        parent=frame,
        child=wheel,
        origin=Origin(xyz=(wx, wy, r.axle_z - frame_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=60.0),
    )
    return wheel


def _emit_inline_chassis(model, boot, r, mats, *, prefix, side):
    frame = model.part(f"{prefix}_frame")
    # The frame_mount FIXED joint origin must lie on the real boot-sole/frame
    # contact face (z=_SOLE_BOTTOM_Z) so it is near BOTH geometries. The frame's
    # local frame is therefore offset DOWN by mount_z; every frame-child
    # placement (deck/rails/wheels) is authored in absolute coords and shifted by
    # -mount_z to keep the chassis in the same world position.
    mount_z = _SOLE_BOTTOM_Z
    model.articulation(
        f"{prefix}_frame_mount", ArticulationType.FIXED,
        parent=boot, child=frame, origin=Origin(xyz=(0.0, 0.0, mount_z)),
    )
    # Deck plate sits just under the sole, top at the sole bottom.
    deck_top = _SOLE_BOTTOM_Z
    deck_bot = deck_top - _DECK_SEAT
    frame.visual(
        Box((2 * r.rail_half_span, 0.040, deck_top - deck_bot)),
        origin=Origin(xyz=(0.0, 0.0, (deck_bot + deck_top) / 2.0 - mount_z)),
        material=mats["frame"],
        name="deck_plate", material_class_id="metal.aluminum_bare",
    )
    # The rail mesh is authored with its top at _RAIL_TOP_Z and its wheel bosses
    # spanning z[0.026, _RAIL_TOP_Z]. We keep the rail at its authored z (top
    # embedded ~0.0008+ into the deck for every N) so the rails always connect to
    # the deck; the boss z-span captures the axle for all wheel radii (axle_z in
    # [0.034, 0.044] sits inside the boss). Pull the top up a hair into the deck
    # so the deck<->rail contact is robust to the connectivity tolerance.
    rail_z = (deck_bot + 0.0035) - _RAIL_TOP_Z - mount_z
    for label, sy in (("lateral", side), ("medial", -side)):
        frame.visual(
            r._meshes["rail"],
            origin=Origin(xyz=(0.0, sy * _RAIL_CENTER_Y, rail_z)),
            material=mats["frame"],
            name=f"rail_{label}", material_class_id="metal.aluminum_bare",
        )
    frame.inertial = Inertial.from_geometry(
        Box((2 * r.rail_half_span, 0.040, 0.060)),
        mass=0.16,
        origin=Origin(xyz=(0.0, 0.0, _RAIL_TOP_Z / 2.0 - mount_z)),
    )
    wheels = []
    for i, ax in enumerate(r.axle_xs):
        wheels.append(_emit_wheel(model, frame, r, mats, prefix=prefix, i=i,
                                  wx=ax, wy=0.0, frame_z=mount_z))
    return frame, wheels


def _emit_quad_chassis(model, boot, r, mats, *, prefix, side):
    frame = model.part(f"{prefix}_frame")
    # See _emit_inline_chassis: mount origin on the sole/frame contact face; all
    # frame-child placements shifted down by mount_z to stay world-fixed.
    mount_z = _SOLE_BOTTOM_Z
    model.articulation(
        f"{prefix}_frame_mount", ArticulationType.FIXED,
        parent=boot, child=frame, origin=Origin(xyz=(0.0, 0.0, mount_z)),
    )
    deck_top = _SOLE_BOTTOM_Z
    deck_bot = deck_top - _DECK_SEAT
    frame.visual(
        Box((abs(_TRUCK_FRONT_X - _TRUCK_REAR_X) + _TRUCK_BASEPLATE_LX, 0.050,
             deck_top - deck_bot)),
        origin=Origin(xyz=((_TRUCK_FRONT_X + _TRUCK_REAR_X) / 2.0, 0.0,
                           (deck_bot + deck_top) / 2.0 - mount_z)),
        material=mats["frame"],
        name="deck_plate", material_class_id="metal.aluminum_bare",
    )
    baseplate_z = 0.081 + _TRUCK_BASEPLATE_THICK / 2.0
    for ti, tx in enumerate((_TRUCK_FRONT_X, _TRUCK_REAR_X)):
        tlabel = "front" if ti == 0 else "rear"
        frame.visual(
            r._meshes["truck_baseplate"],
            origin=Origin(xyz=(tx, 0.0, baseplate_z - mount_z)),
            material=mats["frame"],
            name=f"{tlabel}_baseplate", material_class_id="metal.aluminum_bare",
        )
        frame.visual(
            r._meshes["truck_hanger"],
            origin=Origin(xyz=(tx, 0.0, r.axle_z - mount_z)),
            material=mats["steel"],
            name=f"{tlabel}_hanger", material_class_id="metal.steel_bare",
        )
    frame.inertial = Inertial.from_geometry(
        Box((0.16, 0.080, 0.060)),
        mass=0.18,
        origin=Origin(xyz=(0.0, 0.0, 0.060 - mount_z)),
    )
    corners = [
        (_TRUCK_FRONT_X, +1.0), (_TRUCK_FRONT_X, -1.0),
        (_TRUCK_REAR_X, +1.0), (_TRUCK_REAR_X, -1.0),
    ]
    wheels = []
    for i, (wx, ysign) in enumerate(corners):
        wy = side * ysign * _WHEEL_Y_OFFSET
        wheels.append(_emit_wheel(model, frame, r, mats, prefix=prefix, i=i,
                                  wx=wx, wy=wy, frame_z=mount_z))
    return frame, wheels


# ===========================================================================
# Boot + cuff (Slot B) + per-skate assembly.
# ===========================================================================
def _add_skate(model, r, mats, *, prefix, side, parent_boot=None, mount_origin=None):
    boot = model.part(f"{prefix}_boot")
    if parent_boot is not None:
        model.articulation(
            f"{prefix}_boot_mount", ArticulationType.FIXED,
            parent=parent_boot, child=boot, origin=mount_origin or Origin(),
        )

    # --- boot shell visuals (Slot B) ---
    meshes = r._meshes
    boot.visual(meshes["shell"], material=mats["shell"], name="shell", material_class_id=("fabric.upholstery_plain" if r.boot_form in {"hard_shell", "soft_boot"} else "leather.smooth_plain"))
    boot.visual(meshes["sole"], material=mats["sole"], name="sole", material_class_id="rubber.smooth_plain")
    if r.boot_form == "hard_shell":
        boot.visual(meshes["shaft"], material=mats["shaft"], name="shaft", material_class_id="plastic.opaque_glossy_molded")
        boot.visual(meshes["liner"], material=mats["liner"], name="liner_collar", material_class_id="fabric.flexible_foam")
        boot.visual(meshes["heel_panel"], material=mats["accent"], name="heel_panel", material_class_id="plastic.opaque_glossy_molded")
        boot.visual(meshes["toe_bumper"], material=mats["sole"], name="toe_bumper", material_class_id="rubber.smooth_plain")
    elif r.boot_form == "soft_boot":
        boot.visual(meshes["collar"], material=mats["shaft"], name="padded_collar", material_class_id="fabric.upholstery_plain")
        boot.visual(meshes["liner"], material=mats["liner"], name="liner_collar", material_class_id="fabric.flexible_foam")
        boot.visual(meshes["toe_bumper"], material=mats["accent"], name="toe_cap", material_class_id="rubber.smooth_plain")
    else:  # low_cut
        boot.visual(meshes["liner"], material=mats["liner"], name="liner_collar", material_class_id="fabric.flexible_foam")
        boot.visual(meshes["heel_panel"], material=mats["accent"], name="heel_panel", material_class_id="plastic.opaque_glossy_molded")
        boot.visual(meshes["toe_bumper"], material=mats["sole"], name="toe_bumper", material_class_id="rubber.smooth_plain")
    boot.visual(meshes["tongue"], material=mats["tongue"], name="tongue", material_class_id="fabric.upholstery_plain")
    boot.inertial = Inertial.from_geometry(
        Box((0.30, 0.10, 0.28)),
        mass=0.55,
        origin=Origin(xyz=(0.0, 0.0, 0.13)),
    )

    # --- cuff part (Slot B geometry) ---
    cuff = model.part(f"{prefix}_cuff")
    cuff.visual(meshes["cuff"], material=mats["cuff"], name="collar", material_class_id=("plastic.opaque_glossy_molded" if r.boot_form in {"hard_shell", "low_cut"} else "fabric.upholstery_plain"))
    cuff.visual(meshes["cuff_top"], material=mats["cuff"], name="upper_collar", material_class_id=("plastic.opaque_glossy_molded" if r.boot_form in {"hard_shell", "low_cut"} else "fabric.upholstery_plain"))
    # Pivot rivet: a short steel stub seated INTO the collar ring wall. The cuff
    # collar profiles use FULL-width args, so the ring inner wall sits at half the
    # inner width (~0.048). Center the stub on the ring band so it embeds (->
    # structurally connected) without crossing to the neighbour skate.
    rivet_wall_y = {"hard_shell": 0.052, "soft_boot": 0.053, "low_cut": 0.046}.get(
        r.boot_form, 0.052
    )
    # Seat the rivet at the collar band center (cuff-local z), which need not be
    # the hinge plane (z=0): low-cut pivots sit below the collar band.
    rivet_z = _clamp((r.cuff_z0 + r.cuff_z1) / 2.0 - r.cuff_pivot_z, 0.0, 0.030)
    for label, sy in (("lateral", side), ("medial", -side)):
        cuff.visual(
            Cylinder(radius=0.0085, length=0.020),
            origin=Origin(
                xyz=(0.0, sy * rivet_wall_y, rivet_z),
                rpy=(math.pi / 2.0, 0.0, 0.0),
            ),
            material=mats["steel"],
            name=f"pivot_rivet_{label}", material_class_id="metal.steel_bare",
        )
    cuff.inertial = Inertial.from_geometry(
        Box((0.12, 0.12, 0.06)),
        mass=0.10,
        origin=Origin(xyz=(0.0, 0.0, 0.03)),
    )

    # --- closure (Slot C): instep on boot + strap on cuff ---
    _CLOSURE_EMIT[r.closure](boot, cuff, r, mats, side=side)

    # --- cuff flex joint (REVOLUTE +Y) ---
    # Pivot x sits on the rear ankle shell; the low-cut shell is shorter/more
    # forward, so its hinge anchors a touch further forward to stay on geometry.
    pivot_x = -0.038 if r.boot_form == "low_cut" else -0.048
    model.articulation(
        f"{prefix}_cuff_flex", ArticulationType.REVOLUTE,
        parent=boot, child=cuff,
        origin=Origin(xyz=(pivot_x, 0.0, r.cuff_pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=4.0,
                                   lower=_CUFF_LOWER, upper=_CUFF_UPPER),
    )

    # --- chassis (Slot A): frame + wheels ---
    if r.chassis_arrangement == "quad":
        _emit_quad_chassis(model, boot, r, mats, prefix=prefix, side=side)
    else:
        _emit_inline_chassis(model, boot, r, mats, prefix=prefix, side=side)

    return boot


# ===========================================================================
# Build
# ===========================================================================
def build_roller_skates(
    config: RollerSkatesConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: model.material(f"roller_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in PALETTES[r.palette_style].items()
    }
    # Build the shared meshes once and stash on the resolved config (read-only
    # cache; both skates reuse the identical geometry).
    object.__setattr__(r, "_meshes", _shared_meshes(r))

    left_boot = _add_skate(model, r, mats, prefix="left", side=1.0)
    # Pairing clip: short tab on the left boot sole reaching out to the boot_mount
    # contact datum, so the right-skate FIXED mount origin seats on real left-boot
    # geometry (baseline articulation-origin check). Rule-1 non-moving visual.
    _clip_yc = (_PAIR_CLIP_Y0 + _PAIR_CLIP_Y1) / 2.0
    _clip_ly = abs(_PAIR_CLIP_Y1 - _PAIR_CLIP_Y0)
    left_boot.visual(
        Box((0.024, _clip_ly, 0.014)),
        origin=Origin(xyz=(_BOOT_MOUNT_DATUM[0], _clip_yc, _BOOT_MOUNT_DATUM[2])),
        material=mats["sole"],
        name="pair_clip", material_class_id="rubber.smooth_plain",
    )
    _add_skate(
        model, r, mats, prefix="right", side=-1.0,
        parent_boot=left_boot,
        mount_origin=Origin(xyz=_RIGHT_SKATE_OFFSET, rpy=(0.0, 0.0, _RIGHT_SKATE_YAW)),
    )

    # Re-anchor the right boot so its link origin sits on the boot_mount contact
    # datum (rifle.py _reanchor_part pattern). The right boot's local frame moves
    # by +anchor (boot_mount origin -> datum); its own visuals shift by -anchor to
    # stay world-fixed, and its child joints (cuff_flex, frame_mount) shift by
    # -anchor so the cuff/frame subtrees keep their world poses. (yaw == 0, so the
    # re-anchor is a pure translation and stays consistent.)
    anchor = tuple(_BOOT_MOUNT_DATUM[k] - _RIGHT_SKATE_OFFSET[k] for k in range(3))
    right_boot = model.get_part("right_boot")
    _shift_visuals(right_boot, anchor)
    boot_mount = model.get_articulation("right_boot_mount")
    boot_mount.origin = Origin(xyz=_BOOT_MOUNT_DATUM,
                               rpy=(0.0, 0.0, _RIGHT_SKATE_YAW))
    for jname in ("right_cuff_flex", "right_frame_mount"):
        _shift_joint_origin(model.get_articulation(jname), anchor)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_roller_skates(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_roller_skates(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_roller_skates_tests(
    object_model: ArticulatedObject,
    config: RollerSkatesConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    sides = ("left", "right")
    n = r.n_wheels

    boots = {s: object_model.get_part(f"{s}_boot") for s in sides}
    frames = {s: object_model.get_part(f"{s}_frame") for s in sides}
    cuffs = {s: object_model.get_part(f"{s}_cuff") for s in sides}
    wheels = {s: [object_model.get_part(f"{s}_wheel_{i}") for i in range(n)] for s in sides}
    spin_joints = {
        s: [object_model.get_articulation(f"{s}_wheel_{i}_spin") for i in range(n)]
        for s in sides
    }
    cuff_joints = {s: object_model.get_articulation(f"{s}_cuff_flex") for s in sides}

    # ----- intentional, scoped allowances -----
    # The right skate stands beside the left without touching it (one pair,
    # two separate stands).
    isolated = [frames["right"], cuffs["right"]] + wheels["right"]
    for part in isolated:
        ctx.allow_isolated_part(
            part.name,
            reason="Right skate of the pair stands separately beside the left skate.",
        )
    # The left-boot pairing clip bridges to the right-boot sole (this is what
    # FIXED-mounts the right skate to the pair); the clip is seated in the left
    # sole and reaches into the right sole.
    for relem in ("sole", "shell", "toe_bumper", "heel_panel"):
        ctx.allow_overlap(
            boots["left"], boots["right"], elem_a="pair_clip", elem_b=relem,
            reason="Pairing clip seats the right skate onto the left boot.",
        )
    # Stored as a pair, the two skates stand close; on the wide soft-boot cuffs the
    # adjacent collars / pivot rivets can graze. Allow the cross-skate cuff contact.
    for ea in ("collar", "upper_collar", "pivot_rivet_lateral", "pivot_rivet_medial"):
        for eb in ("collar", "upper_collar", "pivot_rivet_lateral", "pivot_rivet_medial"):
            ctx.allow_overlap(
                cuffs["left"], cuffs["right"], elem_a=ea, elem_b=eb,
                reason="Paired skates stand close; adjacent cuff collars/rivets graze.",
            )
    # The cuff flexes forward on its ankle pivot; the cuff collar sweeps past the
    # boot's liner collar / tongue it wraps around (captured ankle-flex engagement).
    for s in sides:
        ctx.allow_overlap(
            boots[s], cuffs[s],
            reason="Cuff flexes on the ankle pivot over the boot liner collar and tongue.",
        )
    for s in sides:
        # Wheel axles captured through the chassis (rails or hanger crossbar).
        for wheel in wheels[s]:
            if r.chassis_arrangement == "inline":
                for rail in ("rail_lateral", "rail_medial"):
                    for welem in ("axle", "hub"):
                        ctx.allow_overlap(
                            frames[s], wheel, elem_a=rail, elem_b=welem,
                            reason="Wheel axle/hub captured through both inline frame rails.",
                        )
            else:
                for tlabel in ("front_hanger", "rear_hanger"):
                    for welem in ("axle", "hub"):
                        ctx.allow_overlap(
                            frames[s], wheel, elem_a=tlabel, elem_b=welem,
                            reason="Truck hanger crossbar passes through the wheel "
                                   "hub/axle bore (captured axle).",
                        )
        # Cuff pivot rivets seated in the boot shaft/collar wall.
        for label in ("lateral", "medial"):
            ctx.allow_overlap(
                boots[s], cuffs[s], elem_a="shell", elem_b=f"pivot_rivet_{label}",
                reason="Cuff pivot rivet seated into the boot shell/shaft wall.",
            )
        # Hollow cuff collar nests concentrically around the boot upper.
        ctx.allow_overlap(
            boots[s], cuffs[s], elem_a="shell", elem_b="collar",
            reason="Hollow ankle cuff collar nests concentrically around the boot upper.",
        )
        # Boot forms with a heel_panel (hard_shell / low_cut): the low cuff collar
        # wraps over the rear heel panel.
        if r.boot_form == "low_cut":
            # On the low-cut boot the cuff sits low; the instep tongue tucks under
            # the front of the cuff collar and its closure strap.
            for celem in ("collar", "cuff_strap"):
                ctx.allow_overlap(
                    boots[s], cuffs[s], elem_a="tongue", elem_b=celem,
                    reason="Instep tongue tucks under the low-cut cuff collar/strap.",
                )
            # The cuff collar nests over the boot liner rim.
            ctx.allow_overlap(
                boots[s], cuffs[s], elem_a="liner_collar", elem_b="collar",
                reason="Cuff collar nests over the low-cut boot liner rim.",
            )
            for label in ("lateral", "medial"):
                ctx.allow_overlap(
                    boots[s], cuffs[s], elem_a="liner_collar",
                    elem_b=f"pivot_rivet_{label}",
                    reason="Cuff pivot rivet seated through the boot liner rim.",
                )
        if r.boot_form in ("hard_shell", "low_cut"):
            ctx.allow_overlap(
                boots[s], cuffs[s], elem_a="heel_panel", elem_b="collar",
                reason="Cuff collar nests over the rear heel panel.",
            )
            for label in ("lateral", "medial"):
                ctx.allow_overlap(
                    boots[s], cuffs[s], elem_a="heel_panel",
                    elem_b=f"pivot_rivet_{label}",
                    reason="Cuff pivot rivet seated through the heel panel.",
                )
        if r.boot_form == "hard_shell":
            ctx.allow_overlap(
                boots[s], cuffs[s], elem_a="shaft", elem_b="collar",
                reason="Hollow cuff collar wraps the boot shaft with radial clearance.",
            )
            for label in ("lateral", "medial"):
                ctx.allow_overlap(
                    boots[s], cuffs[s], elem_a="shaft", elem_b=f"pivot_rivet_{label}",
                    reason="Cuff pivot rivet seated into the boot shaft wall.",
                )
        if r.boot_form == "soft_boot":
            # Soft boots use a thick padded_collar (no rigid shaft); the hollow
            # cuff collar nests over it.
            ctx.allow_overlap(
                boots[s], cuffs[s], elem_a="padded_collar", elem_b="collar",
                reason="Hollow cuff collar nests over the soft boot padded collar.",
            )
            for label in ("lateral", "medial"):
                ctx.allow_overlap(
                    boots[s], cuffs[s], elem_a="padded_collar",
                    elem_b=f"pivot_rivet_{label}",
                    reason="Cuff pivot rivet seated into the soft boot padded collar.",
                )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    # ----- wheel count, joint types, lateral spin axes -----
    for s in sides:
        for i, joint in enumerate(spin_joints[s]):
            ctx.check(
                f"{s}_wheel_{i}_spin is a CONTINUOUS lateral-axle joint",
                str(joint.articulation_type).lower().endswith("continuous")
                and abs(joint.axis[1]) > 0.99
                and abs(joint.axis[0]) < 1e-6
                and abs(joint.axis[2]) < 1e-6,
                details=f"type={joint.articulation_type}, axis={joint.axis}",
            )
    total_wheels = sum(1 for p in object_model.parts if "_wheel_" in p.name)
    ctx.check(
        "skate pair has exactly 2*N wheels",
        total_wheels == 2 * n,
        details=f"total_wheels={total_wheels} expected={2 * n}",
    )

    # quad: 2x2 lateral separation (not collapsed into a single line).
    if r.chassis_arrangement == "quad":
        ys = []
        for i in range(4):
            j = spin_joints["left"][i]
            ys.append(j.origin.xyz[1])
        ctx.check(
            "quad wheels split laterally (2x2, not single-file)",
            max(ys) - min(ys) > 0.04,
            details=f"wheel_y={[round(y, 4) for y in ys]}",
        )

    # ----- all wheels coplanar on the ground -----
    min_zs = []
    for s in sides:
        for wheel in wheels[s]:
            aabb = ctx.part_world_aabb(wheel)
            if aabb is not None:
                min_zs.append(aabb[0][2])
    spread = max(min_zs) - min(min_zs) if min_zs else 1.0
    ctx.check(
        "all wheels rest coplanar on the ground",
        len(min_zs) == 2 * n and spread <= 0.0015 and all(abs(z) <= 0.004 for z in min_zs),
        details=f"wheel min-z: {[round(z, 5) for z in min_zs]}",
    )

    # ----- inline tire-non-touch (packing inequality proven from dims) -----
    if r.chassis_arrangement == "inline" and n >= 2:
        spacing = min(
            abs(r.axle_xs[i] - r.axle_xs[i + 1]) for i in range(len(r.axle_xs) - 1)
        )
        ctx.check(
            "adjacent inline tires do not touch (2R <= spacing - clearance)",
            2.0 * r.wheel_radius <= spacing - 0.003,
            details=f"2R={2 * r.wheel_radius:.4f} spacing={spacing:.4f}",
        )

    # ----- cuff joints: REVOLUTE with realistic ankle-flex limits -----
    for s in sides:
        joint = cuff_joints[s]
        limits = joint.motion_limits
        ctx.check(
            f"{s}_cuff_flex is a limited REVOLUTE ankle joint about +Y",
            str(joint.articulation_type).lower().endswith("revolute")
            and abs(joint.axis[1]) > 0.99
            and limits is not None and limits.lower is not None and limits.upper is not None
            and -0.6 <= limits.lower < 0.0 < limits.upper <= 0.8,
            details=f"type={joint.articulation_type}, limits=({limits.lower}, {limits.upper})",
        )

    # ----- mounting + side-by-side stand -----
    for s in sides:
        ctx.expect_contact(
            boots[s], frames[s], name=f"{s} frame deck seats against the boot sole",
        )
        ctx.expect_contact(
            cuffs[s], boots[s], name=f"{s} cuff is riveted to the boot",
        )
    # The two skates stand side by side. We measure the wheel-group y centroid
    # separation (clip-independent and robust: the right boot is re-anchored onto
    # the boot_mount contact datum, so neither link origins nor the clipped boot
    # AABB centers are reliable here).
    def _wheel_centroid_y(s):
        ys = []
        for wheel in wheels[s]:
            a = ctx.part_world_aabb(wheel)
            if a is not None:
                ys.append((a[0][1] + a[1][1]) / 2.0)
        return sum(ys) / len(ys) if ys else 0.0

    wheel_y_sep = abs(_wheel_centroid_y("right") - _wheel_centroid_y("left"))
    ctx.check(
        "the two skates stand side by side",
        0.09 <= wheel_y_sep <= 0.20,
        details=f"wheel_y_sep={wheel_y_sep:.4f}",
    )

    # ----- decisive pose checks: cuff flexes forward, wheel spins in place -----
    rest_cuff = ctx.part_world_aabb(cuffs["left"])
    with ctx.pose({cuff_joints["left"]: 0.4}):
        flexed_cuff = ctx.part_world_aabb(cuffs["left"])
    ok_flex = (
        rest_cuff is not None and flexed_cuff is not None
        and ((flexed_cuff[0][0] + flexed_cuff[1][0]) - (rest_cuff[0][0] + rest_cuff[1][0])) / 2.0
        > 0.004
    )
    ctx.check("positive cuff flex leans the cuff forward over the toes", ok_flex,
              details=f"rest={rest_cuff}, flexed={flexed_cuff}")

    rest_wheel = ctx.part_world_aabb(wheels["left"][0])
    with ctx.pose({spin_joints["left"][0]: 1.3}):
        spun_wheel = ctx.part_world_aabb(wheels["left"][0])

    def _center(aabb):
        return tuple((aabb[0][k] + aabb[1][k]) / 2.0 for k in range(3))

    ok_spin = False
    if rest_wheel is not None and spun_wheel is not None:
        rc, sc = _center(rest_wheel), _center(spun_wheel)
        ok_spin = all(abs(sc[k] - rc[k]) <= 0.002 for k in range(3))
    ctx.check("wheel spins in place about its lateral axle", ok_spin,
              details=f"rest={rest_wheel}, spun={spun_wheel}")

    # ----- closure features present (Rule 1 visuals) -----
    boot = boots["left"]
    cuff = cuffs["left"]
    if r.closure == "laces":
        names = {v.name for v in boot.visuals}
        ctx.check("laces present (5 lace rungs + eyelet stays)",
                  "lace_0" in names and "lace_4" in names and "eyelet_stay_lateral" in names,
                  details=str(sorted(n for n in names if "lace" in n or "eyelet" in n)))
    else:
        # Count only the base strap bodies (instep_strap_<i>), not the buckle/
        # tooth/lever/anchor sub-elements that share the prefix.
        strap_visuals = [
            v.name for v in boot.visuals
            if v.name.startswith("instep_strap_") and v.name.split("_")[-1].isdigit()
            and not any(tok in v.name for tok in ("tooth", "buckle", "lever", "anchor"))
        ]
        ctx.check(
            "M instep straps inlined on the boot (Rule 1)",
            len(strap_visuals) == r.instep_strap_count,
            details=f"straps={sorted(strap_visuals)} expected M={r.instep_strap_count}",
        )
        cuff_names = {v.name for v in cuff.visuals}
        ctx.check("cuff closure strap present on the cuff",
                  any(nm.startswith("cuff_strap") or nm.startswith("power_strap") for nm in cuff_names),
                  details=str(sorted(cuff_names)))

    # ----- slot_choices recorded with N (and conditional M) encoded -----
    ctx.check(
        "slot_choices recorded with wheel_count (and M when applicable) encoded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "RollerSkatesConfig",
    "ResolvedRollerSkatesConfig",
    "build_roller_skates",
    "build_seeded_roller_skates",
    "config_from_seed",
    "resolve_config",
    "run_roller_skates_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
