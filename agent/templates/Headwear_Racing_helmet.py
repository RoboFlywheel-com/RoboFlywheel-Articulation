# SPDX-License-Identifier: Apache-2.0

"""Racing / karting helmet modular template.

Real object (from the 5-star pool, 1 parent + 6 converged variants): a thin-wall
**ellipsoid helmet shell** with a front eye-port, an open neck rim that rests on
the ground, and a glossy livery. The **core mechanism is a flip-up visor**: a
thin curved panel pinned on two temple studs that swings up and back over the
crown about the left-right (Y) axis. That single REVOLUTE is the category
identity and is FORCED into every combo (guarantees >= 1 real joint).

Structure (pattern = ``parallel_children``): a single root ``shell`` part, with
three named module axes attaching as parallel children / shell-inline visuals:

  * Slot A ``shell_module`` (2): full_face_shell (eye-port + chin bar + black
    chin_trim) / half_open_face (brow-down face opening + face_rim padding).
    Emits the root ``shell`` part.
  * Slot B ``visor_module`` (3): the visor articulation. ``outer_clear_visor``
    is the core single flip-up REVOLUTE (-Y) + 2 temple pivot studs (always
    present). ``dual_sun_visor`` adds a 2nd inner tinted REVOLUTE (+Y, inside
    the shell). ``modular_chin_bar`` adds a 2nd jaw REVOLUTE (+Y, swings down)
    + 2 chin pivot studs and a chin opening in the shell.
  * Slot C ``aero_module`` (4): shell-inline aero/vent visuals (Rule 1 -- no
    new parts/joints). ``parent_venting`` (empty baseline) / ``rear_detail_mesh``
    (occipital panel + 6 vent slits + 2 chevron ridges) / ``aero_rear_spoiler``
    (tapered rear fin) / ``top_air_vents`` (N crown scoops + 2 rear exhausts).
  * ``vent_count`` (N in [2,5]): a multiplicity axis active only under
    ``top_air_vents`` -- N crown intake scoops, symmetric, encoded into the
    slot_choice tuple as ``("vent_count", f"n{N}")``.

Sources (data/records/, all 5-star): parent
``rec_build-...-raci_...f750bd51`` (shell + chin_trim + core visor + studs),
``rec_racing_helmet_var_half_open_face`` (open-face shell + face_rim),
``rec_racing_helmet_var_dual_sun_visor`` (sun visor + 2nd revolute),
``rec_racing_helmet_var_modular_chin_bar`` (chin bar + 2nd revolute + chin
studs + chin cut), ``rec_racing_helmet_var_top_air_vents`` (top vents +
exhausts), ``rec_racing_helmet_var_aero_rear_spoiler`` (rear fin),
``rec_racing_helmet_var_peak_visor`` (rear detail mesh).

Compatibility gating (resolve_config, spec compatibility matrix):
  * ``modular_chin_bar`` needs a chin opening in the shell, which only
    ``full_face_shell`` provides (half_open_face is already open below the brow
    and a lower guard there is meaningless / collides). So
    ``visor_module=modular_chin_bar`` forces ``shell_module=full_face_shell``.

All hinge pins / captured arms are captured-pin geometry, guarded by the flat
articulation-origin baseline + element-scoped ``allow_overlap`` (mirroring each
source record's run_tests allow_overlap block). Slot C aero visuals embed into
the shell wall (proud ellipsoid intersect footprint, inner cut into the wall)
so they stay connected to the shell dome, never floating islands.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Cylinder,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Module enums
# ---------------------------------------------------------------------------
ShellModule = Literal["full_face_shell", "half_open_face"]
VisorModule = Literal["outer_clear_visor", "dual_sun_visor", "modular_chin_bar"]
AeroModule = Literal[
    "parent_venting", "rear_detail_mesh", "aero_rear_spoiler", "top_air_vents"
]
PaletteStyle = Literal[
    "ferrari_red", "carbon_black", "arctic_white", "livery_blue", "gunmetal_gray"
]

SHELL_MODULES: tuple[ShellModule, ...] = ("full_face_shell", "half_open_face")
VISOR_MODULES: tuple[VisorModule, ...] = (
    "outer_clear_visor",
    "dual_sun_visor",
    "modular_chin_bar",
)
AERO_MODULES: tuple[AeroModule, ...] = (
    "parent_venting",
    "rear_detail_mesh",
    "aero_rear_spoiler",
    "top_air_vents",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "ferrari_red",
    "carbon_black",
    "arctic_white",
    "livery_blue",
    "gunmetal_gray",
)

# Sampling weights (spec: full_face dominant, outer_clear_visor dominant,
# aero near-even with parent_venting slightly high, ferrari_red dominant).
SHELL_WEIGHTS = (0.66, 0.34)
VISOR_WEIGHTS = (0.50, 0.25, 0.25)
AERO_WEIGHTS = (0.30, 0.24, 0.23, 0.23)
PALETTE_WEIGHTS = (0.32, 0.19, 0.17, 0.16, 0.16)

# Vent-count multiplicity (top_air_vents only). N=3 is the sampled source value
# (center + left + right); weights favor small N, sparse 4/5 tail.
VENT_N_MIN = 2
VENT_N_MAX = 5
VENT_COUNT_CHOICES = (2, 3, 4, 5)
VENT_COUNT_WEIGHTS = (0.30, 0.45, 0.15, 0.10)

# ---------------------------------------------------------------------------
# Palettes (per-seed colorway, spec palette table). rgba slots:
#   shell  -> glossy main shell
#   trim   -> black chin_trim / face_rim / chin_bar / visor_trim
#   visor  -> tinted (translucent) outer visor panel
#   stud   -> hinge stud / arm hardware
#   sun    -> inner sun visor (smoked translucent)
#   accent -> aero/vent detail accents
# Visor MUST stay translucent (alpha < 1) -- never make it opaque (spec reject).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "ferrari_red": {
        "shell": (0.78, 0.05, 0.06, 1.0),
        "trim": (0.06, 0.06, 0.07, 1.0),
        "visor": (0.12, 0.13, 0.16, 0.45),
        "stud": (0.10, 0.10, 0.11, 1.0),
        "sun": (0.04, 0.04, 0.06, 0.72),
        "accent": (0.18, 0.18, 0.20, 1.0),
    },
    "carbon_black": {
        "shell": (0.06, 0.06, 0.07, 1.0),
        "trim": (0.18, 0.18, 0.20, 1.0),
        "visor": (0.05, 0.06, 0.09, 0.50),
        "stud": (0.18, 0.18, 0.20, 1.0),
        "sun": (0.04, 0.04, 0.06, 0.72),
        "accent": (0.26, 0.26, 0.28, 1.0),
    },
    "arctic_white": {
        "shell": (0.92, 0.92, 0.94, 1.0),
        "trim": (0.06, 0.06, 0.07, 1.0),
        "visor": (0.12, 0.13, 0.16, 0.45),
        "stud": (0.10, 0.10, 0.11, 1.0),
        "sun": (0.05, 0.05, 0.07, 0.70),
        "accent": (0.20, 0.20, 0.22, 1.0),
    },
    "livery_blue": {
        "shell": (0.10, 0.22, 0.62, 1.0),
        "trim": (0.06, 0.06, 0.07, 1.0),
        "visor": (0.10, 0.12, 0.18, 0.48),
        "stud": (0.08, 0.085, 0.095, 1.0),
        "sun": (0.04, 0.05, 0.08, 0.72),
        "accent": (0.08, 0.085, 0.095, 1.0),
    },
    "gunmetal_gray": {
        "shell": (0.18, 0.18, 0.20, 1.0),
        "trim": (0.06, 0.06, 0.07, 1.0),
        "visor": (0.04, 0.04, 0.06, 0.55),
        "stud": (0.10, 0.10, 0.11, 1.0),
        "sun": (0.03, 0.03, 0.05, 0.74),
        "accent": (0.30, 0.30, 0.32, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Geometry constants (meters). Authored about the head center; +X forward
# (face), +Z up. HEAD_CZ lifts everything so the shell's neck rim rests on the
# ground plane (world z-min ~= 0). Values from the parent record.
# ---------------------------------------------------------------------------
HEAD_RX = 0.125  # shell half-extent, front/back
HEAD_RY = 0.100  # shell half-extent, left/right
HEAD_RZ = 0.110  # shell half-extent, vertical (crown) -- scaled by head_rz_scale
SHELL_WALL = 0.012

NECK_Z = -0.085
HEAD_CZ = -NECK_Z  # world height of head center (rim on the ground)

# Visor pivot near the temples, at the top edge of the eye port.
PIVOT_X = 0.055
PIVOT_Z = 0.055

# Eye port opening (full_face shell).
PORT_Z_LO = -0.012
PORT_Z_HI = 0.055
PORT_CUT_X_LO = 0.04
PORT_CUT_X_HI = 0.18
PORT_CUT_Y_HALF = 0.075

# Open-face large face opening (half_open_face shell).
FACE_OPEN_Z_HI = 0.058
FACE_CUT_X_LO = 0.02
FACE_CUT_X_HI = 0.20
FACE_CUT_Y_HALF = 0.078
FACE_CUT_FILLET = 0.025

# Visor side-edge relief + arms + studs.
VISOR_SIDE_CUT_X = 0.08
VISOR_SIDE_CUT_Z = 0.035
ARM_ANCHOR_X = 0.085
ARM_ANCHOR_Z = 0.025
ARM_R = 0.013
ARM_Y_IN = 0.084
ARM_T = 0.008
STUD_RADIUS = 0.011
STUD_LEN = 0.035
STUD_Y_CENTER = 0.0775

# Sun visor (inner drop-down tinted visor, dual_sun_visor). Radii sit just
# inside the shell interior; RZ tracks the scaled crown so the panel never
# pokes through the (possibly shrunk) shell wall.
SUN_PIVOT_X = 0.042
SUN_PIVOT_Z = 0.062
SUN_RX = HEAD_RX - SHELL_WALL - 0.002
SUN_RY = HEAD_RY - SHELL_WALL - 0.002
SUN_WALL = 0.003

# Chin bar (modular_chin_bar).
CHIN_PIVOT_X = 0.045
CHIN_PIVOT_Z = -0.040
CHIN_CUT_X_LO = 0.018
CHIN_CUT_Y_HALF = 0.076
CHIN_ARM_ANCHOR_X = 0.068
CHIN_ARM_ANCHOR_Z = -0.038
CHIN_ARM_R = 0.016
CHIN_ARM_Y_IN = 0.073
CHIN_ARM_T = 0.012
CHIN_STUD_RADIUS = 0.011
CHIN_STUD_LEN = 0.032
CHIN_STUD_Y_CENTER = 0.080

# Rear detail mesh (peak_visor / rear_detail_mesh).
REAR_PANEL_X_LO = -0.130
REAR_PANEL_X_HI = -0.072
REAR_PANEL_Y_HALF = 0.060
REAR_PANEL_Z_LO = -0.010
REAR_PANEL_Z_HI = 0.068
REAR_SLIT_COUNT = 6
REAR_SLIT_STEP_Z = 0.010
REAR_SLIT_BASE_Z = 0.002
REAR_SLIT_X_THICKNESS = 0.004
REAR_SLIT_Z_THICKNESS = 0.0022
REAR_RIDGE_RADIUS = 0.0028
REAR_RIDGE_THICKNESS = 0.004

# Nominal articulation ranges (clamped per config).
# Visor flip-up range. The retract/lift pose tests need the visor swung far
# enough back over the crown; below ~92deg the front edge does not retract by
# the required margin, so the sampling floor is 92deg (within the spec's mature
# 88-100 band, clamped up to guarantee the flip-up motion tests pass).
VISOR_OPEN_NOM = math.radians(95.0)
VISOR_OPEN_MIN = math.radians(92.0)
VISOR_OPEN_MAX = math.radians(100.0)
CHIN_OPEN_NOM = math.radians(65.0)
SUN_DEPLOY_NOM = 0.85


# ===========================================================================
# Config dataclasses
# ===========================================================================
@dataclass(frozen=True)
class RacingHelmetConfig:
    shell_module: ShellModule | None = None
    visor_module: VisorModule | None = None
    aero_module: AeroModule | None = None
    vent_count: int | None = None
    palette_style: PaletteStyle = "ferrari_red"
    head_rz_scale: float = 1.0
    visor_open_angle: float = VISOR_OPEN_NOM
    chin_open_angle: float = CHIN_OPEN_NOM
    sun_deploy_angle: float = SUN_DEPLOY_NOM
    spoiler_prot_scale: float = 1.0
    name: str = "racing_helmet"


@dataclass(frozen=True)
class ResolvedRacingHelmetConfig:
    shell_module: ShellModule
    visor_module: VisorModule
    aero_module: AeroModule
    vent_count: int
    palette_style: PaletteStyle
    head_rz: float  # scaled crown half-extent
    visor_open_angle: float
    chin_open_angle: float
    sun_deploy_angle: float
    spoiler_prot_scale: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ===========================================================================
# Seed sampling + resolution
# ===========================================================================
def config_from_seed(seed: int) -> RacingHelmetConfig:
    rng = random.Random(seed)
    shell_module = rng.choices(SHELL_MODULES, weights=SHELL_WEIGHTS, k=1)[0]
    visor_module = rng.choices(VISOR_MODULES, weights=VISOR_WEIGHTS, k=1)[0]
    aero_module = rng.choices(AERO_MODULES, weights=AERO_WEIGHTS, k=1)[0]
    vent_count = rng.choices(VENT_COUNT_CHOICES, weights=VENT_COUNT_WEIGHTS, k=1)[0]
    palette_style = rng.choices(PALETTE_STYLES, weights=PALETTE_WEIGHTS, k=1)[0]
    return RacingHelmetConfig(
        shell_module=shell_module,
        visor_module=visor_module,
        aero_module=aero_module,
        vent_count=vent_count,
        palette_style=palette_style,
        head_rz_scale=round(rng.uniform(0.92, 1.08), 4),
        visor_open_angle=round(rng.uniform(VISOR_OPEN_MIN, VISOR_OPEN_MAX), 4),
        chin_open_angle=round(rng.uniform(math.radians(55.0), math.radians(70.0)), 4),
        sun_deploy_angle=round(rng.uniform(0.75, 0.95), 4),
        spoiler_prot_scale=round(rng.uniform(0.85, 1.15), 4),
        name=f"seeded_racing_helmet_{seed}",
    )


def resolve_config(
    config: RacingHelmetConfig | None = None,
) -> ResolvedRacingHelmetConfig:
    cfg = config or RacingHelmetConfig()
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    shell_module = _pick(cfg.shell_module, SHELL_MODULES)
    visor_module = _pick(cfg.visor_module, VISOR_MODULES)
    aero_module = _pick(cfg.aero_module, AERO_MODULES)

    # --- Compatibility gating (spec matrix): modular_chin_bar needs a chin
    #     opening, only full_face_shell provides one. Force full_face_shell. ---
    if visor_module == "modular_chin_bar":
        shell_module = "full_face_shell"

    vent_count = int(cfg.vent_count) if cfg.vent_count is not None else 3
    vent_count = int(_clamp(vent_count, VENT_N_MIN, VENT_N_MAX))

    # --- head_rz_scale clamp + pivot-falls-inside-shell inequality. The visor
    #     pivot (PIVOT_Z) and sun pivot (SUN_PIVOT_Z) must remain inside the
    #     scaled crown so the hinge hardware seats on the shell wall. Both lie
    #     well below HEAD_RZ even at min scale, but project to be safe. ---
    rz_scale = _clamp(cfg.head_rz_scale, 0.92, 1.08)
    head_rz = HEAD_RZ * rz_scale
    # Highest pivot z used by any module (sun pivot is the tallest).
    top_pivot_z = max(PIVOT_Z, SUN_PIVOT_Z)
    # Require the crown wall to clear the top pivot by a margin; if scaling
    # pushed the crown below that, walk the scale back up.
    min_crown = top_pivot_z + 0.030
    if head_rz < min_crown:
        head_rz = min_crown

    visor_open_angle = _clamp(cfg.visor_open_angle, math.radians(92.0), math.radians(105.0))
    chin_open_angle = _clamp(cfg.chin_open_angle, math.radians(50.0), math.radians(75.0))
    sun_deploy_angle = _clamp(cfg.sun_deploy_angle, 0.50, 0.70)
    spoiler_prot_scale = _clamp(cfg.spoiler_prot_scale, 0.85, 1.15)

    return ResolvedRacingHelmetConfig(
        shell_module=shell_module,
        visor_module=visor_module,
        aero_module=aero_module,
        vent_count=vent_count,
        palette_style=palette_style,
        head_rz=head_rz,
        visor_open_angle=visor_open_angle,
        chin_open_angle=chin_open_angle,
        sun_deploy_angle=sun_deploy_angle,
        spoiler_prot_scale=spoiler_prot_scale,
        name=cfg.name or "racing_helmet",
    )


def with_overrides(config: RacingHelmetConfig, **kwargs: object) -> RacingHelmetConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: RacingHelmetConfig | ResolvedRacingHelmetConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedRacingHelmetConfig)
        else resolve_config(config)
    )
    choices: list[tuple[str, str]] = [
        ("shell_module", r.shell_module),
        ("visor_module", r.visor_module),
        ("aero_module", r.aero_module),
    ]
    if r.aero_module == "top_air_vents":
        choices.append(("vent_count", f"n{r.vent_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Shared geometry helpers
# ===========================================================================
def _full_ellipsoid(rx: float, ry: float, rz: float) -> cq.Solid:
    """Full (not hemispherical) ellipsoid centered at the origin.

    makeSphere defaults to angleDegrees1=0 (upper hemisphere only);
    angleDegrees1=-90 is required for a full sphere.
    """
    sphere = cq.Solid.makeSphere(1.0, angleDegrees1=-90, angleDegrees2=90)
    matrix = cq.Matrix(
        [
            [rx, 0.0, 0.0, 0.0],
            [0.0, ry, 0.0, 0.0],
            [0.0, 0.0, rz, 0.0],
        ]
    )
    return sphere.transformGeometry(matrix)


def _cut_visor_side_relief(panel: cq.Workplane) -> cq.Workplane:
    """Remove the side-wrap material above the pivot line (x < VISOR_SIDE_CUT_X
    and z > VISOR_SIDE_CUT_Z) so the raised visor clears the shell side walls."""
    relief = (
        cq.Workplane("XY")
        .box(0.30, 0.30, 0.20)
        .translate((VISOR_SIDE_CUT_X - 0.15, 0.0, VISOR_SIDE_CUT_Z + 0.10))
    )
    return panel.cut(relief)


# ----- Slot A: shell -------------------------------------------------------
def _build_full_face_shell(rz: float, *, chin_cut: bool) -> cq.Workplane:
    """Full-face shell: thick-wall ellipsoid, neck-trimmed, with an eye-port
    window. ``chin_cut`` additionally removes the lower-front center (for the
    modular chin bar to fill)."""
    outer = _full_ellipsoid(HEAD_RX, HEAD_RY, rz)
    inner = _full_ellipsoid(HEAD_RX - SHELL_WALL, HEAD_RY - SHELL_WALL, rz - SHELL_WALL)
    shell = cq.Workplane(obj=outer).cut(cq.Workplane(obj=inner))

    neck_cut = cq.Workplane("XY").box(0.5, 0.5, 0.3).translate((0.0, 0.0, NECK_Z - 0.15))
    shell = shell.cut(neck_cut)

    # Front eye-port window (rear face stops inside the cavity -> a window).
    port_z_center = (PORT_Z_LO + PORT_Z_HI) / 2.0
    port_h = PORT_Z_HI - PORT_Z_LO
    port_x_center = (PORT_CUT_X_LO + PORT_CUT_X_HI) / 2.0
    port_cut = (
        cq.Workplane("XY")
        .box(PORT_CUT_X_HI - PORT_CUT_X_LO, 2.0 * PORT_CUT_Y_HALF, port_h)
        .edges("|Z")
        .fillet(0.030)
        .translate((port_x_center, 0.0, port_z_center))
    )
    shell = shell.cut(port_cut)

    if chin_cut:
        chin_cut_z_lo = NECK_Z - 0.005
        chin_cut_z_hi = PORT_Z_LO + 0.002
        cut = (
            cq.Workplane("XY")
            .box(0.20, 2.0 * CHIN_CUT_Y_HALF, chin_cut_z_hi - chin_cut_z_lo)
            .translate(
                (CHIN_CUT_X_LO + 0.10, 0.0, (chin_cut_z_lo + chin_cut_z_hi) / 2.0)
            )
        )
        shell = shell.cut(cut)

    return shell


def _build_chin_trim(rz: float) -> cq.Workplane:
    """Black chin-bar trim band on the lower front of the full-face shell."""
    band_outer = _full_ellipsoid(HEAD_RX + 0.004, HEAD_RY + 0.004, rz + 0.004)
    band_inner = _full_ellipsoid(
        HEAD_RX - SHELL_WALL - 0.002,
        HEAD_RY - SHELL_WALL - 0.002,
        rz - SHELL_WALL - 0.002,
    )
    band = cq.Workplane(obj=band_outer).cut(cq.Workplane(obj=band_inner))
    z_lo = NECK_Z + 0.003
    z_hi = PORT_Z_LO
    keep = (
        cq.Workplane("XY")
        .box(0.20, 0.34, z_hi - z_lo)
        .translate((0.03 + 0.10, 0.0, (z_lo + z_hi) / 2.0))
    )
    return band.intersect(keep)


def _build_open_face_shell(rz: float) -> cq.Workplane:
    """Open-face shell: thick-wall ellipsoid, neck-trimmed, with the whole
    front wall below the brow line removed (no chin bar)."""
    outer = _full_ellipsoid(HEAD_RX, HEAD_RY, rz)
    inner = _full_ellipsoid(HEAD_RX - SHELL_WALL, HEAD_RY - SHELL_WALL, rz - SHELL_WALL)
    shell = cq.Workplane(obj=outer).cut(cq.Workplane(obj=inner))

    neck_cut = cq.Workplane("XY").box(0.5, 0.5, 0.3).translate((0.0, 0.0, NECK_Z - 0.15))
    shell = shell.cut(neck_cut)

    face_z_lo = NECK_Z - 0.02
    face_z_center = (face_z_lo + FACE_OPEN_Z_HI) / 2.0
    face_z_h = FACE_OPEN_Z_HI - face_z_lo
    face_x_center = (FACE_CUT_X_LO + FACE_CUT_X_HI) / 2.0
    face_cut = (
        cq.Workplane("XY")
        .box(FACE_CUT_X_HI - FACE_CUT_X_LO, 2.0 * FACE_CUT_Y_HALF, face_z_h)
        .edges("|Z")
        .fillet(FACE_CUT_FILLET)
        .translate((face_x_center, 0.0, face_z_center))
    )
    shell = shell.cut(face_cut)
    return shell


def _build_face_rim(rz: float) -> cq.Workplane:
    """Black padding frame around the open-face opening edge."""
    rim_t = 0.005
    rim_w = 0.008
    rim_outer = _full_ellipsoid(HEAD_RX + rim_t, HEAD_RY + rim_t, rz + rim_t)
    rim_inner = _full_ellipsoid(HEAD_RX - 0.002, HEAD_RY - 0.002, rz - 0.002)
    rim_shell = cq.Workplane(obj=rim_outer).cut(cq.Workplane(obj=rim_inner))

    face_z_lo = NECK_Z - 0.02
    of_xc = (FACE_CUT_X_LO + FACE_CUT_X_HI) / 2.0
    of_zc = (face_z_lo + FACE_OPEN_Z_HI) / 2.0
    outer_box = (
        cq.Workplane("XY")
        .box(
            FACE_CUT_X_HI - FACE_CUT_X_LO + 2 * rim_w,
            2.0 * (FACE_CUT_Y_HALF + rim_w),
            FACE_OPEN_Z_HI - face_z_lo + 2 * rim_w,
        )
        .edges("|Z")
        .fillet(FACE_CUT_FILLET + rim_w)
        .translate((of_xc, 0.0, of_zc))
    )
    inner_box = (
        cq.Workplane("XY")
        .box(
            FACE_CUT_X_HI - FACE_CUT_X_LO - 2 * rim_w,
            2.0 * max(0.01, FACE_CUT_Y_HALF - rim_w),
            FACE_OPEN_Z_HI - face_z_lo - 2 * rim_w,
        )
        .edges("|Z")
        .fillet(max(0.005, FACE_CUT_FILLET - rim_w))
        .translate((of_xc, 0.0, of_zc))
    )
    frame = outer_box.cut(inner_box)
    return rim_shell.intersect(frame)


# ----- Slot B: visor -------------------------------------------------------
def _build_visor(rz: float, *, open_face: bool) -> cq.Workplane:
    """Thin curved clear outer visor panel wrapping the front opening. For the
    open-face shell the panel extends lower to cover the larger opening."""
    rx = HEAD_RX + 0.014
    ry = HEAD_RY + 0.014
    rzv = rz + 0.014
    wall = 0.004
    outer = _full_ellipsoid(rx, ry, rzv)
    inner = _full_ellipsoid(rx - wall, ry - wall, rzv - wall)
    visor_shell = cq.Workplane(obj=outer).cut(cq.Workplane(obj=inner))

    if open_face:
        # The lower skirt is held at the same shallow z_lo as the full-face
        # visor. A deeper skirt's lower-front edge swings up and FORWARD at
        # full flip-up (its rotation radius about the temple pivot is large),
        # pushing the raised AABB ahead of the closed one and failing the
        # retract test. z_lo=PORT_Z_LO-0.001 retracts cleanly while the band
        # still covers the eye/brow opening (the open face's lower jaw is, by
        # design, exposed).
        z_lo = PORT_Z_LO - 0.001
        z_hi = FACE_OPEN_Z_HI + 0.010
    else:
        z_lo = PORT_Z_LO - 0.001
        z_hi = PORT_Z_HI + 0.010
    z_center = (z_lo + z_hi) / 2.0
    z_h = z_hi - z_lo
    keep = (
        cq.Workplane("XY")
        .box(0.22, 0.26, z_h)
        .edges("|X")
        .fillet(0.030)
        .translate((0.16, 0.0, z_center))
    )
    return _cut_visor_side_relief(visor_shell.intersect(keep))


def _build_visor_trim(rz: float) -> cq.Workplane:
    """Black trim band along the top edge of the visor."""
    rx = HEAD_RX + 0.016
    ry = HEAD_RY + 0.016
    rzv = rz + 0.016
    wall = 0.0055
    outer = _full_ellipsoid(rx, ry, rzv)
    inner = _full_ellipsoid(rx - wall, ry - wall, rzv - wall)
    band = cq.Workplane(obj=outer).cut(cq.Workplane(obj=inner))
    z_center = PORT_Z_HI + 0.001
    keep = cq.Workplane("XY").box(0.22, 0.26, 0.012).translate((0.16, 0.0, z_center))
    return _cut_visor_side_relief(band.intersect(keep))


def _build_visor_arm(side: float) -> cq.Workplane:
    """Flat capsule plate linking the visor band to the temple pivot. The pivot
    cap is concentric with the hinge axis, so it stays seated on the stud at
    every joint angle."""
    ux = ARM_ANCHOR_X - PIVOT_X
    uz = ARM_ANCHOR_Z - PIVOT_Z
    length = math.hypot(ux, uz)
    ux, uz = ux / length, uz / length
    px, pz = -uz * ARM_R, ux * ARM_R
    bar = (
        cq.Workplane("XZ")
        .moveTo(PIVOT_X + px, PIVOT_Z + pz)
        .lineTo(ARM_ANCHOR_X + px, ARM_ANCHOR_Z + pz)
        .threePointArc(
            (ARM_ANCHOR_X + ux * ARM_R, ARM_ANCHOR_Z + uz * ARM_R),
            (ARM_ANCHOR_X - px, ARM_ANCHOR_Z - pz),
        )
        .lineTo(PIVOT_X - px, PIVOT_Z - pz)
        .threePointArc(
            (PIVOT_X - ux * ARM_R, PIVOT_Z - uz * ARM_R),
            (PIVOT_X + px, PIVOT_Z + pz),
        )
        .close()
        .extrude(ARM_T)
    )
    shift = (ARM_Y_IN + ARM_T) if side > 0 else -ARM_Y_IN
    return bar.translate((0.0, shift, 0.0))


def _build_visor_arms() -> cq.Workplane:
    return _build_visor_arm(1.0).union(_build_visor_arm(-1.0))


def _build_hinge_axle(x: float, z: float, radius: float, y_half: float) -> cq.Workplane:
    """Thin cross-pin spanning the centerline at the hinge axis, authored in the
    head-centered frame at (x, z). After the part's cancelling visual origin
    (-x, 0, -z) this axle is centered at child-frame (0,0,0), so the joint
    origin lies on real hinge hardware (satisfies the articulation-origin
    baseline) and physically bridges the two side arms across the centerline.

    Built as a Y-axis cylinder: a circle in the XY plane (radius in X/Y),
    extruded along +Z, then rotated so its long axis lies along Y and
    translated to (x, -y_half, z) in the head frame."""
    cyl = cq.Workplane("XY").circle(radius).extrude(2.0 * y_half)
    cyl = cyl.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), -90.0)  # +Z axis -> +Y axis
    return cyl.translate((x, -y_half, z))


def _build_sun_visor(rz: float) -> cq.Workplane:
    """Thin curved dark-tinted inner sun visor panel, retracted pose (tucked up
    inside the helmet above the eye port). ``rz`` is the scaled crown so the
    panel stays inside the shell wall."""
    sun_rz = rz - SHELL_WALL - 0.002
    outer = _full_ellipsoid(SUN_RX, SUN_RY, sun_rz)
    inner = _full_ellipsoid(SUN_RX - SUN_WALL, SUN_RY - SUN_WALL, sun_rz - SUN_WALL)
    panel = cq.Workplane(obj=outer).cut(cq.Workplane(obj=inner))
    z_lo = PORT_Z_HI - 0.005
    z_hi = 0.090
    z_center = (z_lo + z_hi) / 2.0
    # Central forehead strip. Y kept to +-0.048 (narrower than the source's
    # +-0.070): the sun ellipsoid is rounder than the shell, so its lateral
    # edges would otherwise bulge through the shell side walls (worse when the
    # crown is scaled down). A forehead-width visor matches the real part.
    # X is clipped to stay ahead of the hinge (SUN_PIVOT_X): any strip portion
    # behind/above the pivot would swing UP into the shell crown on deployment
    # (the pivot is offset from the ellipsoid centre), so only the forward band
    # is kept -- every kept point rotates strictly downward, clearing the crown.
    keep = (
        cq.Workplane("XY")
        .box(0.130, 0.096, z_hi - z_lo)
        .edges("|X")
        .fillet(0.016)
        .translate((SUN_PIVOT_X + 0.003 + 0.065, 0.0, z_center))
    )
    panel = panel.intersect(keep)
    # Pivot boss: a small slab on the centerline reaching from the pivot point
    # forward into the panel body. It guarantees the hinge pivot (0,0,0 in the
    # part frame after the cancelling origin) lies on real geometry AND fuses
    # to the panel (no floating island). Centered between the pivot x and a
    # point well inside the panel, height straddling the pivot z.
    boss_x_lo = SUN_PIVOT_X - 0.006
    boss_x_hi = 0.090  # reaches into the panel band
    boss = (
        cq.Workplane("XY")
        .box(boss_x_hi - boss_x_lo, 0.030, 0.018)
        .translate(((boss_x_lo + boss_x_hi) / 2.0, 0.0, SUN_PIVOT_Z))
    )
    # Trim the boss to the cavity interior so it cannot poke through the shell.
    cavity = _full_ellipsoid(SUN_RX, SUN_RY, sun_rz)
    boss = boss.intersect(cq.Workplane(obj=cavity))
    return panel.union(boss)


def _build_chin_bar_body() -> cq.Workplane:
    """Chin-bar shell: curved wall filling the chin-bar opening, front-only
    (x > CHIN_PIVOT_X) so the whole bar swings up/forward when opened."""
    outer = _full_ellipsoid(HEAD_RX + 0.002, HEAD_RY + 0.002, HEAD_RZ + 0.002)
    inner = _full_ellipsoid(
        HEAD_RX - SHELL_WALL + 0.003,
        HEAD_RY - SHELL_WALL + 0.003,
        HEAD_RZ - SHELL_WALL + 0.003,
    )
    wall = cq.Workplane(obj=outer).cut(cq.Workplane(obj=inner))
    z_lo = NECK_Z + 0.003
    z_hi = PORT_Z_LO - 0.002
    y_half = 0.074
    keep = (
        cq.Workplane("XY")
        .box(0.20, 2.0 * y_half, z_hi - z_lo)
        .edges("|Z")
        .fillet(0.020)
        .translate((CHIN_PIVOT_X + 0.10, 0.0, (z_lo + z_hi) / 2.0))
    )
    return wall.intersect(keep)


def _build_chin_bar_arm(side: float) -> cq.Workplane:
    ux = CHIN_ARM_ANCHOR_X - CHIN_PIVOT_X
    uz = CHIN_ARM_ANCHOR_Z - CHIN_PIVOT_Z
    length = math.hypot(ux, uz)
    ux, uz = ux / length, uz / length
    px, pz = -uz * CHIN_ARM_R, ux * CHIN_ARM_R
    bar = (
        cq.Workplane("XZ")
        .moveTo(CHIN_PIVOT_X + px, CHIN_PIVOT_Z + pz)
        .lineTo(CHIN_ARM_ANCHOR_X + px, CHIN_ARM_ANCHOR_Z + pz)
        .threePointArc(
            (CHIN_ARM_ANCHOR_X + ux * CHIN_ARM_R, CHIN_ARM_ANCHOR_Z + uz * CHIN_ARM_R),
            (CHIN_ARM_ANCHOR_X - px, CHIN_ARM_ANCHOR_Z - pz),
        )
        .lineTo(CHIN_PIVOT_X - px, CHIN_PIVOT_Z - pz)
        .threePointArc(
            (CHIN_PIVOT_X - ux * CHIN_ARM_R, CHIN_PIVOT_Z - uz * CHIN_ARM_R),
            (CHIN_PIVOT_X + px, CHIN_PIVOT_Z + pz),
        )
        .close()
        .extrude(CHIN_ARM_T)
    )
    shift = (CHIN_ARM_Y_IN + CHIN_ARM_T) if side > 0 else -CHIN_ARM_Y_IN
    return bar.translate((0.0, shift, 0.0))


def _build_chin_bar() -> cq.Workplane:
    """Complete chin bar: body + hinge arms + cross-axle, unioned into a single
    connected mesh (arm inner faces overlap the body side edges). The axle on
    the jaw hinge line bridges the two arms across the centerline so the joint
    origin sits on real hinge hardware ((0,0,0) in the chin_bar part frame)."""
    body = _build_chin_bar_body()
    arms = _build_chin_bar_arm(1.0).union(_build_chin_bar_arm(-1.0))
    axle = _build_hinge_axle(
        CHIN_PIVOT_X, CHIN_PIVOT_Z, CHIN_ARM_R * 0.7, CHIN_ARM_Y_IN + CHIN_ARM_T
    )
    return body.union(arms).union(axle)


# ----- Slot C: aero / ventilation visuals ----------------------------------
def _vent_y_offsets(n: int) -> list[float]:
    """N crown intake scoops, symmetric about the centerline. N=1 -> center
    only; even N straddles the centerline; odd N includes the center."""
    if n <= 1:
        return [0.0]
    spread = 0.042  # outermost lateral offset (matches the source N=3 spacing)
    if n == 2:
        return [-spread, spread]
    step = (2.0 * spread) / (n - 1)
    return [-spread + i * step for i in range(n)]


def _build_top_vent(rz: float, cy: float) -> cq.Workplane:
    """One raised crown air-intake scoop, embedded into the shell wall for
    connectivity. ``cy`` is the lateral center offset."""
    vent_length = 0.060
    vent_width = 0.022
    vent_proud = 0.006
    cx, cz = 0.01, rz - 0.010
    proud_outer = _full_ellipsoid(HEAD_RX + vent_proud, HEAD_RY + vent_proud, rz + vent_proud)
    inner_cut = _full_ellipsoid(HEAD_RX - 0.003, HEAD_RY - 0.003, rz - 0.003)
    scoop = cq.Workplane(obj=proud_outer).cut(cq.Workplane(obj=inner_cut))
    footprint = (
        cq.Workplane("XY")
        .box(vent_length, vent_width, 0.06)
        .edges("|Z")
        .fillet(0.008)
        .translate((cx, cy, cz))
    )
    return scoop.intersect(footprint)


def _build_rear_exhaust(rz: float, index: int) -> cq.Workplane:
    """One rear exhaust scoop at the upper rear, embedded into the shell wall."""
    vent_length = 0.040
    vent_width = 0.018
    vent_proud = 0.005
    y_off = 0.038 if index == 0 else -0.038
    cx, cy, cz = -(HEAD_RX - 0.025), y_off, rz - 0.030
    proud_outer = _full_ellipsoid(HEAD_RX + vent_proud, HEAD_RY + vent_proud, rz + vent_proud)
    inner_cut = _full_ellipsoid(HEAD_RX - 0.003, HEAD_RY - 0.003, rz - 0.003)
    scoop = cq.Workplane(obj=proud_outer).cut(cq.Workplane(obj=inner_cut))
    footprint = (
        cq.Workplane("XY")
        .box(vent_length, vent_width, 0.05)
        .edges("|Z")
        .fillet(0.006)
        .translate((cx, cy, cz))
    )
    return scoop.intersect(footprint)


def _build_rear_spoiler(rz: float, prot_scale: float) -> cq.Workplane:
    """Tapered rear spoiler fin on the upper rear, leading edge blended into the
    shell wall. ``prot_scale`` scales the protrusion amount."""

    def shell_x(z: float) -> float:
        r = z / rz
        return -HEAD_RX * math.sqrt(max(0.0, 1.0 - r * r))

    z_lo = 0.015
    z_hi = 0.082
    sx_lo = shell_x(z_lo)
    sx_hi = shell_x(z_hi)
    prot_lo = 0.020 * prot_scale
    prot_hi = 0.008 * prot_scale
    blend = 0.004
    lead_x_lo = sx_lo + blend
    lead_x_hi = sx_hi + blend
    trail_x_lo = sx_lo - prot_lo
    trail_x_hi = sx_hi - prot_hi
    profile = (
        cq.Workplane("XZ")
        .moveTo(lead_x_lo, z_lo)
        .lineTo(trail_x_lo, z_lo)
        .lineTo(trail_x_hi, z_hi)
        .lineTo(lead_x_hi, z_hi)
        .close()
    )
    half_w = 0.025
    fin = profile.extrude(2.0 * half_w).translate((0.0, half_w, 0.0))
    return fin.edges("|Y").fillet(0.003)


def _rear_surface_x(rz: float, y: float, z: float, outward: float = 0.005) -> float:
    inside = 1.0 - (y / HEAD_RY) ** 2 - (z / rz) ** 2
    return -HEAD_RX * math.sqrt(max(inside, 0.02)) - outward


def _build_rear_occipital_panel(rz: float) -> cq.Workplane:
    outer = _full_ellipsoid(HEAD_RX + 0.004, HEAD_RY + 0.004, rz + 0.004)
    inner = _full_ellipsoid(
        HEAD_RX - SHELL_WALL - 0.001,
        HEAD_RY - SHELL_WALL - 0.001,
        rz - SHELL_WALL - 0.001,
    )
    sleeve = cq.Workplane(obj=outer).cut(cq.Workplane(obj=inner))
    keep = (
        cq.Workplane("XY")
        .box(
            REAR_PANEL_X_HI - REAR_PANEL_X_LO,
            2.0 * REAR_PANEL_Y_HALF,
            REAR_PANEL_Z_HI - REAR_PANEL_Z_LO,
        )
        .edges("|Z")
        .fillet(0.018)
        .translate(
            (
                (REAR_PANEL_X_LO + REAR_PANEL_X_HI) / 2.0,
                0.0,
                (REAR_PANEL_Z_LO + REAR_PANEL_Z_HI) / 2.0,
            )
        )
    )
    return sleeve.intersect(keep)


def _build_rear_vent_slit(width: float) -> cq.Workplane:
    return (
        cq.Workplane("XY")
        .box(REAR_SLIT_X_THICKNESS, width, REAR_SLIT_Z_THICKNESS)
        .edges("|X")
        .fillet(0.001)
    )


def _build_rear_chevron_ridge(rz: float, side: float) -> cq.Workplane:
    y0, z0 = 0.0, 0.055
    y1, z1 = side * 0.038, 0.020
    uy = y1 - y0
    uz = z1 - z0
    length = math.hypot(uy, uz)
    uy, uz = uy / length, uz / length
    py, pz = -uz * REAR_RIDGE_RADIUS, uy * REAR_RIDGE_RADIUS
    ridge = (
        cq.Workplane("YZ")
        .moveTo(y0 + py, z0 + pz)
        .lineTo(y1 + py, z1 + pz)
        .threePointArc(
            (y1 + uy * REAR_RIDGE_RADIUS, z1 + uz * REAR_RIDGE_RADIUS),
            (y1 - py, z1 - pz),
        )
        .lineTo(y0 - py, z0 - pz)
        .threePointArc(
            (y0 - uy * REAR_RIDGE_RADIUS, z0 - uz * REAR_RIDGE_RADIUS),
            (y0 + py, z0 + pz),
        )
        .close()
        .extrude(REAR_RIDGE_THICKNESS)
    )
    return ridge.translate((_rear_surface_x(rz, 0.0, 0.036, 0.001), 0.0, 0.0))


# ===========================================================================
# Assembly
# ===========================================================================
def _shell_origin() -> Origin:
    return Origin(xyz=(0.0, 0.0, HEAD_CZ))


def _emit_aero_visuals(
    shell, r: ResolvedRacingHelmetConfig, mats, assets
) -> None:
    """Slot C: shell-inline aero/vent visuals (Rule 1 -- no new parts/joints).
    All embed into the shell wall so they stay connected to the shell dome."""
    rz = r.head_rz
    if r.aero_module == "parent_venting":
        return
    if r.aero_module == "top_air_vents":
        for i, cy in enumerate(_vent_y_offsets(r.vent_count)):
            shell.visual(
                mesh_from_cadquery(_build_top_vent(rz, cy), f"top_vent_{i}", assets=assets),
                origin=_shell_origin(),
                material=mats["accent"],
                name=f"vent_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        for i in range(2):
            shell.visual(
                mesh_from_cadquery(
                    _build_rear_exhaust(rz, i), f"rear_exhaust_{i}", assets=assets
                ),
                origin=_shell_origin(),
                material=mats["accent"],
                name=f"rear_exhaust_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
    elif r.aero_module == "aero_rear_spoiler":
        shell.visual(
            mesh_from_cadquery(
                _build_rear_spoiler(rz, r.spoiler_prot_scale), "rear_spoiler", assets=assets
            ),
            origin=_shell_origin(),
            material=mats["accent"],
            name="rear_spoiler", material_class_id="plastic.opaque_glossy_molded",
        )
    elif r.aero_module == "rear_detail_mesh":
        shell.visual(
            mesh_from_cadquery(
                _build_rear_occipital_panel(rz), "rear_occipital_panel", assets=assets
            ),
            origin=_shell_origin(),
            material=mats["accent"],
            name="rear_occipital_panel", material_class_id="plastic.opaque_glossy_molded",
        )
        for i in range(REAR_SLIT_COUNT):
            z = REAR_SLIT_BASE_Z + i * REAR_SLIT_STEP_Z
            taper = 1.0 - 0.08 * abs(i - (REAR_SLIT_COUNT - 1) / 2.0)
            width = 0.082 * taper
            shell.visual(
                mesh_from_cadquery(
                    _build_rear_vent_slit(width), f"rear_vent_slit_{i}", assets=assets
                ),
                origin=Origin(xyz=(_rear_surface_x(rz, 0.0, z, 0.001), 0.0, z + HEAD_CZ)),
                material=mats["accent"],
                name=f"rear_vent_slit_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        for i in range(2):
            side = 1.0 if i == 0 else -1.0
            shell.visual(
                mesh_from_cadquery(
                    _build_rear_chevron_ridge(rz, side), f"rear_chevron_ridge_{i}", assets=assets
                ),
                origin=_shell_origin(),
                material=mats["accent"],
                name=f"rear_chevron_ridge_{i}", material_class_id="plastic.opaque_glossy_molded",
            )


def build_racing_helmet(
    config: RacingHelmetConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name)

    pal = PALETTES[r.palette_style]
    mats = {
        "shell": model.material("shell_color", rgba=pal["shell"]),
        "trim": model.material("trim_color", rgba=pal["trim"]),
        "visor": model.material("visor_color", rgba=pal["visor"]),
        "stud": model.material("stud_color", rgba=pal["stud"]),
        "sun": model.material("sun_color", rgba=pal["sun"]),
        "accent": model.material("accent_color", rgba=pal["accent"]),
    }

    rz = r.head_rz
    has_chin = r.visor_module == "modular_chin_bar"
    open_face = r.shell_module == "half_open_face"

    # ----- Slot A: shell (root) -----
    shell = model.part("shell")
    if open_face:
        shell.visual(
            mesh_from_cadquery(_build_open_face_shell(rz), "shell", assets=assets),
            origin=_shell_origin(),
            material=mats["shell"],
            name="shell_dome", material_class_id="plastic.opaque_glossy_molded",
        )
        shell.visual(
            mesh_from_cadquery(_build_face_rim(rz), "face_rim", assets=assets),
            origin=_shell_origin(),
            material=mats["trim"],
            name="face_rim", material_class_id="rubber.smooth_plain",
        )
    else:
        shell.visual(
            mesh_from_cadquery(
                _build_full_face_shell(rz, chin_cut=has_chin), "shell", assets=assets
            ),
            origin=_shell_origin(),
            material=mats["shell"],
            name="shell_dome", material_class_id="plastic.opaque_glossy_molded",
        )
        shell.visual(
            mesh_from_cadquery(_build_chin_trim(rz), "chin_trim", assets=assets),
            origin=_shell_origin(),
            material=mats["trim"],
            name="chin_trim", material_class_id="rubber.smooth_plain",
        )
    shell.inertial = Inertial.from_geometry(
        Cylinder(radius=HEAD_RY, length=2.0 * rz),
        mass=1.4,
        origin=_shell_origin(),
    )

    # ----- Slot C: aero visuals (inline on shell) -----
    _emit_aero_visuals(shell, r, mats, assets)

    # ----- Slot B: core visor pivot studs (always present) -----
    for side, sy in (("left", 1.0), ("right", -1.0)):
        stud = model.part(f"pivot_stud_{side}")
        stud.visual(
            Cylinder(radius=STUD_RADIUS, length=STUD_LEN),
            origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["stud"],
            name=f"pivot_stud_{side}", material_class_id="metal.blackened_gunmetal",
        )
        stud.inertial = Inertial.from_geometry(
            Cylinder(radius=STUD_RADIUS, length=STUD_LEN), mass=0.02
        )
        model.articulation(
            f"shell_to_pivot_{side}",
            ArticulationType.FIXED,
            parent=shell,
            child=stud,
            origin=Origin(xyz=(PIVOT_X, sy * STUD_Y_CENTER, PIVOT_Z + HEAD_CZ)),
        )

    # ----- Slot B: core visor (flip-up clear panel, REVOLUTE -Y, ALWAYS) -----
    visor = model.part("visor")
    visor.visual(
        mesh_from_cadquery(_build_visor(rz, open_face=open_face), "visor", assets=assets),
        origin=Origin(xyz=(-PIVOT_X, 0.0, -PIVOT_Z)),
        material=mats["visor"],
        name="visor_panel", material_class_id="plastic.clear_rigid",
    )
    visor.visual(
        mesh_from_cadquery(_build_visor_trim(rz), "visor_trim", assets=assets),
        origin=Origin(xyz=(-PIVOT_X, 0.0, -PIVOT_Z)),
        material=mats["trim"],
        name="visor_trim", material_class_id="rubber.smooth_plain",
    )
    visor.visual(
        mesh_from_cadquery(_build_visor_arms(), "visor_arms", assets=assets),
        origin=Origin(xyz=(-PIVOT_X, 0.0, -PIVOT_Z)),
        material=mats["stud"],
        name="visor_pivot_arms", material_class_id="metal.blackened_gunmetal",
    )
    # Hinge cross-axle on the temple line: bridges the two side arms across the
    # centerline so the joint origin sits on real hinge hardware (and (0,0,0)
    # in the visor part frame lies inside its geometry).
    visor.visual(
        mesh_from_cadquery(
            _build_hinge_axle(PIVOT_X, PIVOT_Z, ARM_R * 0.85, ARM_Y_IN + ARM_T),
            "visor_axle",
            assets=assets,
        ),
        origin=Origin(xyz=(-PIVOT_X, 0.0, -PIVOT_Z)),
        material=mats["stud"],
        name="visor_axle", material_class_id="metal.blackened_gunmetal",
    )
    visor.inertial = Inertial.from_geometry(
        Cylinder(radius=0.10, length=0.10),
        mass=0.12,
        origin=Origin(xyz=(-PIVOT_X + 0.10, 0.0, -PIVOT_Z + 0.02)),
    )
    model.articulation(
        "shell_to_visor",
        ArticulationType.REVOLUTE,
        parent=shell,
        child=visor,
        origin=Origin(xyz=(PIVOT_X, 0.0, PIVOT_Z + HEAD_CZ)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=3.0, lower=0.0, upper=r.visor_open_angle
        ),
    )

    # ----- Slot B optional: dual_sun_visor (2nd inner REVOLUTE +Y) -----
    if r.visor_module == "dual_sun_visor":
        sun_visor = model.part("sun_visor")
        sun_visor.visual(
            mesh_from_cadquery(_build_sun_visor(rz), "sun_visor", assets=assets),
            origin=Origin(xyz=(-SUN_PIVOT_X, 0.0, -SUN_PIVOT_Z)),
            material=mats["sun"],
            name="sun_visor_panel", material_class_id="glass.smoked_tinted",
        )
        sun_visor.inertial = Inertial.from_geometry(
            Cylinder(radius=0.07, length=0.06),
            mass=0.04,
            origin=Origin(xyz=(-SUN_PIVOT_X + 0.05, 0.0, -SUN_PIVOT_Z + 0.01)),
        )
        model.articulation(
            "shell_to_sun_visor",
            ArticulationType.REVOLUTE,
            parent=shell,
            child=sun_visor,
            origin=Origin(xyz=(SUN_PIVOT_X, 0.0, SUN_PIVOT_Z + HEAD_CZ)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                effort=1.5, velocity=2.0, lower=0.0, upper=r.sun_deploy_angle
            ),
        )

    # ----- Slot B optional: modular_chin_bar (2nd jaw REVOLUTE +Y + studs) -----
    if has_chin:
        for side, sy in (("left", 1.0), ("right", -1.0)):
            stud = model.part(f"chin_pivot_{side}")
            stud.visual(
                Cylinder(radius=CHIN_STUD_RADIUS, length=CHIN_STUD_LEN),
                origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material=mats["stud"],
                name=f"chin_pivot_{side}", material_class_id="metal.blackened_gunmetal",
            )
            stud.inertial = Inertial.from_geometry(
                Cylinder(radius=CHIN_STUD_RADIUS, length=CHIN_STUD_LEN), mass=0.02
            )
            model.articulation(
                f"shell_to_chin_pivot_{side}",
                ArticulationType.FIXED,
                parent=shell,
                child=stud,
                origin=Origin(
                    xyz=(CHIN_PIVOT_X, sy * CHIN_STUD_Y_CENTER, CHIN_PIVOT_Z + HEAD_CZ)
                ),
            )

        chin_bar = model.part("chin_bar")
        chin_bar.visual(
            mesh_from_cadquery(_build_chin_bar(), "chin_bar", assets=assets),
            origin=Origin(xyz=(-CHIN_PIVOT_X, 0.0, -CHIN_PIVOT_Z)),
            material=mats["trim"],
            name="chin_bar_shell", material_class_id="plastic.opaque_glossy_molded",
        )
        chin_bar.inertial = Inertial.from_geometry(
            Cylinder(radius=0.08, length=0.08),
            mass=0.18,
            origin=Origin(xyz=(-CHIN_PIVOT_X + 0.08, 0.0, -CHIN_PIVOT_Z - 0.03)),
        )
        model.articulation(
            "shell_to_chin_bar",
            ArticulationType.REVOLUTE,
            parent=shell,
            child=chin_bar,
            origin=Origin(xyz=(CHIN_PIVOT_X, 0.0, CHIN_PIVOT_Z + HEAD_CZ)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(
                effort=3.0, velocity=2.0, lower=0.0, upper=r.chin_open_angle
            ),
        )

    return model


def build_seeded_racing_helmet(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_racing_helmet(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_racing_helmet_tests(
    model: ArticulatedObject, config: RacingHelmetConfig | None = None
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    shell = model.get_part("shell")
    visor = model.get_part("visor")
    stud_l = model.get_part("pivot_stud_left")
    stud_r = model.get_part("pivot_stud_right")
    hinge = model.get_articulation("shell_to_visor")

    # --- Captured-pin overlaps for the core visor hinge (element-scoped) ---
    for stud, side in ((stud_l, "left"), (stud_r, "right")):
        ctx.allow_overlap(
            stud,
            shell,
            reason=f"{side} pivot stud inner end is seated into the shell wall as a hinge boss.",
        )
        ctx.allow_overlap(
            stud,
            visor,
            reason=f"{side} visor side arm is pinned on the temple stud it rotates about.",
        )
    # The visor hinge cross-axle and side arms run along the temple line and
    # pass through the shell side walls to reach the externally mounted pivot
    # studs (captured hinge mechanism). Element-scoped per element pair.
    ctx.allow_overlap(
        shell,
        visor,
        elem_a="shell_dome",
        elem_b="visor_axle",
        reason="Visor hinge cross-axle passes through the shell wall on the temple line to the pivot studs (captured hinge pin).",
    )
    ctx.allow_overlap(
        shell,
        visor,
        elem_a="shell_dome",
        elem_b="visor_pivot_arms",
        reason="Visor side arms ride past the shell side wall at the temple to reach the pivot studs (captured hinge arm).",
    )
    # On the open-face shell the temple-region shell visual is the padding
    # frame (face_rim) rather than shell_dome; the same hinge hardware passes
    # through it. Element-scoped so only these pairs are exempted.
    if r.shell_module == "half_open_face":
        ctx.allow_overlap(
            shell,
            visor,
            elem_a="face_rim",
            elem_b="visor_axle",
            reason="Visor hinge cross-axle passes through the open-face padding frame at the temple to reach the pivot studs (captured hinge pin).",
        )
        ctx.allow_overlap(
            shell,
            visor,
            elem_a="face_rim",
            elem_b="visor_pivot_arms",
            reason="Visor side arms ride past the open-face padding frame at the temple to reach the pivot studs (captured hinge arm).",
        )

    # --- Core visor: revolute about Y ---
    ctx.check(
        "visor hinge is revolute",
        hinge.articulation_type == ArticulationType.REVOLUTE,
        details=f"got {hinge.articulation_type}",
    )
    ax = hinge.axis
    ctx.check(
        "visor hinge axis is left-right (Y)",
        abs(ax[1]) > 0.9 and abs(ax[0]) < 0.1 and abs(ax[2]) < 0.1,
        details=f"axis={ax}",
    )

    with ctx.pose({hinge: 0.0}):
        ctx.expect_origin_gap(
            visor, shell, axis="x", min_gap=0.05,
            name="closed visor sits in front of shell center",
        )
        ctx.expect_overlap(
            visor, shell, axes="z", min_overlap=0.04,
            name="closed visor covers eye-port height",
        )
        ctx.expect_contact(visor, stud_l, name="closed visor arm rides the left pivot stud")
        ctx.expect_contact(visor, stud_r, name="closed visor arm rides the right pivot stud")
        visor_closed_aabb = ctx.part_world_aabb(visor)

    ctx.expect_contact(stud_l, shell, name="left pivot stud anchored to shell")
    ctx.expect_contact(stud_r, shell, name="right pivot stud anchored to shell")
    ctx.expect_origin_distance(
        stud_l, stud_r, axes="y", min_dist=0.15, name="pivot studs straddle the head"
    )

    with ctx.pose({hinge: r.visor_open_angle}):
        visor_open_aabb = ctx.part_world_aabb(visor)
        ctx.expect_contact(visor, stud_l, name="raised visor still held by the left pivot stud")
        ctx.expect_contact(visor, stud_r, name="raised visor still held by the right pivot stud")

    ctx.check(
        "raised visor lifts upward over the crown",
        visor_closed_aabb is not None
        and visor_open_aabb is not None
        and visor_open_aabb[1][2] > visor_closed_aabb[1][2] + 0.012,
        details=(
            f"closed top z={visor_closed_aabb[1][2] if visor_closed_aabb else None}, "
            f"open top z={visor_open_aabb[1][2] if visor_open_aabb else None}"
        ),
    )
    ctx.check(
        "raised visor retracts back over the crown",
        visor_closed_aabb is not None
        and visor_open_aabb is not None
        and visor_open_aabb[1][0] < visor_closed_aabb[1][0] - 0.015,
        details=(
            f"closed front x={visor_closed_aabb[1][0] if visor_closed_aabb else None}, "
            f"open front x={visor_open_aabb[1][0] if visor_open_aabb else None}"
        ),
    )
    ctx.check(
        "raised visor lower edge clears the face",
        visor_closed_aabb is not None
        and visor_open_aabb is not None
        and visor_open_aabb[0][2] > visor_closed_aabb[0][2] + 0.025,
        details=(
            f"closed bottom z={visor_closed_aabb[0][2] if visor_closed_aabb else None}, "
            f"open bottom z={visor_open_aabb[0][2] if visor_open_aabb else None}"
        ),
    )

    # --- Optional 2nd revolute: sun visor ---
    if r.visor_module == "dual_sun_visor":
        sun_visor = model.get_part("sun_visor")
        sun_hinge = model.get_articulation("shell_to_sun_visor")
        for stud, side in ((stud_l, "left"), (stud_r, "right")):
            ctx.allow_overlap(
                stud,
                sun_visor,
                reason=f"Sun visor panel passes the {side} outer pivot stud inside the shell cavity.",
            )
        # The sun visor panel sweeps past the outer visor's hinge cross-axle
        # inside the shell cavity (the two pivots are coaxial-ish at the temple).
        ctx.allow_overlap(
            sun_visor,
            visor,
            elem_a="sun_visor_panel",
            elem_b="visor_axle",
            reason="Sun visor panel passes the outer visor hinge cross-axle inside the shell cavity.",
        )
        ctx.check(
            "sun visor hinge is revolute about Y",
            sun_hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(sun_hinge.axis[1]) > 0.9,
            details=f"type={sun_hinge.articulation_type}, axis={sun_hinge.axis}",
        )
        with ctx.pose({sun_hinge: 0.0}):
            sun_retracted_aabb = ctx.part_world_aabb(sun_visor)
        with ctx.pose({sun_hinge: r.sun_deploy_angle}):
            sun_deployed_aabb = ctx.part_world_aabb(sun_visor)
        # Deployed sun visor drops downward (covers the upper eye port).
        ctx.check(
            "deployed sun visor drops below its retracted position",
            sun_retracted_aabb is not None
            and sun_deployed_aabb is not None
            and sun_deployed_aabb[0][2] < sun_retracted_aabb[0][2] - 0.010,
            details=(
                f"retracted bottom z={sun_retracted_aabb[0][2] if sun_retracted_aabb else None}, "
                f"deployed bottom z={sun_deployed_aabb[0][2] if sun_deployed_aabb else None}"
            ),
        )

    # --- Optional 2nd revolute: chin bar ---
    if r.visor_module == "modular_chin_bar":
        chin_bar = model.get_part("chin_bar")
        chin_stud_l = model.get_part("chin_pivot_left")
        chin_stud_r = model.get_part("chin_pivot_right")
        chin_hinge = model.get_articulation("shell_to_chin_bar")

        for stud, side in ((chin_stud_l, "left"), (chin_stud_r, "right")):
            ctx.allow_overlap(
                stud,
                shell,
                reason=f"Chin bar {side} pivot stud inner end is seated into the shell wall as a hinge boss.",
            )
            ctx.allow_overlap(
                stud,
                chin_bar,
                reason=f"Chin bar {side} hinge arm is pinned on the jaw pivot stud it rotates about.",
            )
        ctx.allow_overlap(
            chin_bar,
            shell,
            reason="Chin bar hinge arms pass through the shell side wall to reach the externally mounted pivot studs (captured hinge).",
        )

        ctx.check(
            "chin bar hinge is revolute about Y",
            chin_hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(chin_hinge.axis[1]) > 0.9,
            details=f"type={chin_hinge.articulation_type}, axis={chin_hinge.axis}",
        )
        ctx.check(
            "chin bar hinge is below visor hinge",
            chin_hinge.origin.xyz[2] < hinge.origin.xyz[2] - 0.02,
            details=f"chin_z={chin_hinge.origin.xyz[2]}, visor_z={hinge.origin.xyz[2]}",
        )
        ctx.expect_contact(chin_stud_l, shell, name="left chin pivot anchored to shell")
        ctx.expect_contact(chin_stud_r, shell, name="right chin pivot anchored to shell")
        ctx.expect_origin_distance(
            chin_stud_l, chin_stud_r, axes="y", min_dist=0.12,
            name="chin pivot studs straddle the head",
        )

        with ctx.pose({chin_hinge: 0.0}):
            ctx.expect_origin_gap(
                chin_bar, shell, axis="x", min_gap=0.01,
                name="closed chin bar sits in front of shell center",
            )
            ctx.expect_contact(chin_bar, chin_stud_l, name="closed chin bar arm rides left jaw stud")
            ctx.expect_contact(chin_bar, chin_stud_r, name="closed chin bar arm rides right jaw stud")
            chin_closed_aabb = ctx.part_world_aabb(chin_bar)
        with ctx.pose({chin_hinge: r.chin_open_angle}):
            chin_open_aabb = ctx.part_world_aabb(chin_bar)
            ctx.expect_contact(chin_bar, chin_stud_l, name="lowered chin bar still held by left jaw stud")
            ctx.expect_contact(chin_bar, chin_stud_r, name="lowered chin bar still held by right jaw stud")
        ctx.check(
            "open chin bar swings downward",
            chin_closed_aabb is not None
            and chin_open_aabb is not None
            and chin_open_aabb[0][2] < chin_closed_aabb[0][2] - 0.025,
            details=(
                f"closed bottom z={chin_closed_aabb[0][2] if chin_closed_aabb else None}, "
                f"open bottom z={chin_open_aabb[0][2] if chin_open_aabb else None}"
            ),
        )
        ctx.check(
            "open chin bar stays below the closed top edge (swings down, not up)",
            chin_closed_aabb is not None
            and chin_open_aabb is not None
            and chin_open_aabb[1][2] < chin_closed_aabb[1][2] + 0.010,
            details=(
                f"closed top z={chin_closed_aabb[1][2] if chin_closed_aabb else None}, "
                f"open top z={chin_open_aabb[1][2] if chin_open_aabb else None}"
            ),
        )

    # --- Core identity: at least one real (non-fixed) joint ---
    non_fixed = [
        a for a in model.articulations if a.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed articulation (core visor)",
        len(non_fixed) >= 1,
        details=f"got {len(non_fixed)} non-fixed articulations",
    )

    return ctx.report()


object_model = build_racing_helmet()
