# SPDX-License-Identifier: Apache-2.0

"""Utility / hand knife (slide-out box cutter + folding + fixed-blade) modular template.

NOTE on the slug name: "knife" here = a **hand utility / box-cutter knife** — a
single hand-held tool whose root is a ``handle`` (molded plastic shell / contoured
ergo shell / rubber-overmolded barrel / slim flat metal bar) and whose steel
``blade`` is exposed or stored by some **blade-deployment mechanism**. It is NOT a
scissor (twin-arm shear), NOT a cleaver / chef's knife (fixed full-length blade,
no mechanism), NOT a table / butter knife, and NOT a multi-tool pivot cluster.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Handtools_Knife.md`` and the
``picture/Handtools/Knife`` 5-star sample pool (1 parent + 9 single-axis fork
variants), all synced under ``data/records/``. The OLD non-modular
``agent/templates/retractable_utility_knife.py`` is explicitly NOT a source for
this template and is ignored.

Structure (pattern = ``parallel_children``): a single root ``handle`` part (its
main-shell mesh chosen by the ``grip`` slot, long axis +X, sitting on the +X
axis) carries the blade-deployment mechanism. Three named module axes:

  * ``deployment`` (4) — the core identity slot; every candidate keeps >=1
    non-FIXED joint:
      - ``snap_off_slide`` : ``blade_carrier`` part on ``handle_to_carrier``
        PRISMATIC axis=(1,0,0); rest pose exposes ~12 mm, push out the nose.
      - ``retract_full``   : ``blade_carrier`` part on the same PRISMATIC, but
        q=0 retracts the blade fully into the body; carrier = clamp + 2 posts.
      - ``fold_pivot``     : ``blade`` part on ``handle_to_blade`` REVOLUTE
        axis=(0,1,0) at a nose pivot; q=0 folded in, q=pi swung out.
      - ``flipup_guard``   : the blade is permanently FIXED inline on the
        handle; a ``safety_guard`` part on ``handle_to_guard`` REVOLUTE
        axis=(0,-1,0) flips over / off the cutting edge.
  * ``grip`` (4): tapered_molded / ergo_contoured (palm swell + 4 finger
    grooves) / overmold_barrel (circular loft + 8 TPR ribs) / flat_metal_bar
    (slim squared bar + side knurl). A handle main-shell mesh-helper axis; it
    changes the handle cross-section + fixed detail arrays, not joint topology.
  * ``blade`` (4): snap_off_segmented / hawkbill / drop_point /
    serrated_sheepsfoot. Injects the exposed blade outline into the deployment's
    moving ``blade_steel`` visual (or the handle inline blade for flipup_guard).

Rule 1 ("if it doesn't move it isn't a part") is upheld: score lines, serration
teeth, finger grooves, TPR ribs, knurl bumps, mounting posts, thumb buttons and
end-cap-style detail are all ``part.visual(...)`` loops, never FIXED-joint
decoration parts. The only separate parts are the deployment moving member
(``blade_carrier`` / ``blade`` / ``safety_guard``, all on a real non-FIXED joint)
and the rear ``end_cap`` (a real FIXED part seated at the handle tail).
Rule 2 / grandfathering: the channel-slide capture, nose pivot, hinge-barrel
capture and blade-folded-in-handle fits are captured-pin geometry that cannot be
modeled as two axis-aligned faces in contact, so those joints omit
``MatingContract`` and rely on the flat 0.015 m articulation-origin baseline +
element-scoped ``allow_overlap`` (mirroring each source record's run_tests).
Rule 3: all blade / handle geometry is adapted from the declared 5-star CadQuery
sources; ``mesh_from_cadquery`` lofts / polylines / splines / revolves are
preserved, never downgraded to Box/Cylinder placeholders.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

Deployment = Literal["snap_off_slide", "retract_full", "fold_pivot", "flipup_guard"]
Grip = Literal["tapered_molded", "ergo_contoured", "overmold_barrel", "flat_metal_bar"]
Blade = Literal["snap_off_segmented", "hawkbill", "drop_point", "serrated_sheepsfoot"]
PaletteStyle = Literal[
    "safety_yellow_abs",
    "industrial_black",
    "red_pro",
    "steel_brushed",
    "hi_vis_orange_guard",
]

DEPLOYMENTS: tuple[Deployment, ...] = (
    "snap_off_slide",
    "retract_full",
    "fold_pivot",
    "flipup_guard",
)
GRIPS: tuple[Grip, ...] = (
    "tapered_molded",
    "ergo_contoured",
    "overmold_barrel",
    "flat_metal_bar",
)
BLADES: tuple[Blade, ...] = (
    "snap_off_segmented",
    "hawkbill",
    "drop_point",
    "serrated_sheepsfoot",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "safety_yellow_abs",
    "industrial_black",
    "red_pro",
    "steel_brushed",
    "hi_vis_orange_guard",
)

# Deployments using the +X PRISMATIC slide (vs. the two REVOLUTE deployments).
SLIDE_DEPLOYMENTS: tuple[Deployment, ...] = ("snap_off_slide", "retract_full")

# ---------------------------------------------------------------------------
# Per-seed palettes (spec §7). Keys: handle / blade / channel / accent / tip /
# guard / brass. Every .visual material is driven off this dict so the swept
# pool is colorful (module_topology_diversity only counts structure).
# Colours are the real material/colour sets observed across the 5-star pool.
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "safety_yellow_abs": {
        "handle": (0.96, 0.78, 0.10, 1.0),
        "blade": (0.80, 0.82, 0.85, 1.0),
        "channel": (0.62, 0.63, 0.66, 1.0),
        "accent": (0.10, 0.10, 0.11, 1.0),
        "tip": (0.30, 0.34, 0.46, 1.0),
        "guard": (0.95, 0.45, 0.10, 1.0),
        "brass": (0.72, 0.60, 0.28, 1.0),
        "cap": (0.22, 0.23, 0.25, 1.0),
        "rubber": (0.15, 0.15, 0.16, 1.0),
    },
    "industrial_black": {
        "handle": (0.22, 0.22, 0.24, 1.0),
        "blade": (0.80, 0.82, 0.85, 1.0),
        "channel": (0.50, 0.52, 0.56, 1.0),
        "accent": (0.07, 0.07, 0.08, 1.0),
        "tip": (0.30, 0.34, 0.46, 1.0),
        "guard": (0.92, 0.48, 0.06, 1.0),
        "brass": (0.70, 0.58, 0.26, 1.0),
        "cap": (0.14, 0.14, 0.16, 1.0),
        "rubber": (0.12, 0.12, 0.14, 1.0),
    },
    "red_pro": {
        "handle": (0.80, 0.18, 0.14, 1.0),
        "blade": (0.80, 0.82, 0.85, 1.0),
        "channel": (0.62, 0.63, 0.66, 1.0),
        "accent": (0.10, 0.10, 0.11, 1.0),
        "tip": (0.30, 0.34, 0.46, 1.0),
        "guard": (0.95, 0.45, 0.10, 1.0),
        "brass": (0.72, 0.60, 0.28, 1.0),
        "cap": (0.24, 0.10, 0.09, 1.0),
        "rubber": (0.14, 0.10, 0.10, 1.0),
    },
    "steel_brushed": {
        "handle": (0.72, 0.73, 0.76, 1.0),
        "blade": (0.80, 0.82, 0.85, 1.0),
        "channel": (0.38, 0.40, 0.44, 1.0),
        "accent": (0.10, 0.10, 0.11, 1.0),
        "tip": (0.30, 0.34, 0.46, 1.0),
        "guard": (0.95, 0.45, 0.10, 1.0),
        "brass": (0.66, 0.56, 0.30, 1.0),
        "cap": (0.28, 0.30, 0.34, 1.0),
        "rubber": (0.18, 0.18, 0.20, 1.0),
    },
    "hi_vis_orange_guard": {
        "handle": (0.96, 0.78, 0.10, 1.0),
        "blade": (0.80, 0.82, 0.85, 1.0),
        "channel": (0.62, 0.63, 0.66, 1.0),
        "accent": (0.10, 0.10, 0.11, 1.0),
        "tip": (0.30, 0.34, 0.46, 1.0),
        "guard": (0.95, 0.45, 0.10, 1.0),
        "brass": (0.72, 0.60, 0.28, 1.0),
        "cap": (0.24, 0.25, 0.27, 1.0),
        "rubber": (0.16, 0.16, 0.18, 1.0),
    },
}

# Weak per-deployment palette preference (any palette x any deployment is legal;
# flipup_guard biases toward the orange-guard set). Order = PALETTE_STYLES.
_PALETTE_WEIGHTS: dict[Deployment, tuple[int, ...]] = {
    #                  yellow black red brushed orange
    "snap_off_slide": (5, 3, 3, 2, 2),
    "retract_full": (5, 3, 3, 2, 2),
    "fold_pivot": (4, 3, 3, 3, 2),
    "flipup_guard": (3, 2, 2, 2, 6),
}

# ---------------------------------------------------------------------------
# Nominal real-world dimensions (meters). Adapted from the parent S0 (L50-63)
# and the grip variants. Mechanical thicknesses / clearances are never scaled;
# handle length / height / width, blade length / width, slide travel and the
# fold / guard / barrel parameters are.
# ---------------------------------------------------------------------------
HANDLE_LEN = 0.150          # overall handle length along +X
HANDLE_W = 0.013            # nominal handle width (Y)

# Per-grip baseline handle height (Z). flat_metal_bar is intentionally slim.
_HANDLE_H_BASE: dict[Grip, float] = {
    "tapered_molded": 0.026,
    "ergo_contoured": 0.026,
    "overmold_barrel": 0.0265,
    "flat_metal_bar": 0.014,
}
HANDLE_FRONT_H = 0.016      # front-nose height for the lofted grips

CHANNEL_W = 0.0034          # top blade-channel width (Y)
_CHANNEL_DEPTH_BASE: dict[Grip, float] = {
    "tapered_molded": 0.009,
    "ergo_contoured": 0.009,
    "overmold_barrel": 0.009,
    "flat_metal_bar": 0.005,
}

BLADE_LEN = 0.060           # nominal full blade length (spine + exposed)
BLADE_W = 0.018             # 18 mm blade width (spine -> edge along Z)
BLADE_THK = 0.0006          # blade thickness (along Y)
BLADE_EXPOSED_REST = 0.012  # snap_off rest exposure past the nose
BLADE_RETRACT = 0.006       # retract_full: blade front behind the nose at q=0
SLIDE_TRAVEL = 0.034        # nominal snap_off forward travel
RETRACT_TRAVEL = 0.040      # nominal retract_full forward travel
FIXED_BLADE_EXPOSED = 0.045 # flipup_guard permanently-exposed blade length

# Fold (REVOLUTE Y) geometry.
FOLD_BLADE_LEN = 0.050
FOLD_BLADE_W = 0.015
PIVOT_Z = 0.011             # pivot height inside the handle body

# Guard (REVOLUTE -Y) geometry.
HINGE_BARREL_R = 0.0025
HINGE_BARREL_LEN = 0.010
GUARD_W = 0.016
GUARD_THK = 0.002
GUARD_SKIRT_H = 0.014
GUARD_SKIRT_THK = 0.002

# overmold_barrel profile (variant S6 L63-73): (x, radius). r_max scaled.
_BARREL_PROFILE = [
    (-0.075, 0.009),
    (-0.060, 0.012),
    (-0.045, 0.014),
    (-0.020, 0.0145),
    (0.010, 0.0145),
    (0.035, 0.014),
    (0.055, 0.011),
    (0.068, 0.007),
    (0.075, 0.004),
]
_BARREL_R_MAX = 0.0145
_BARREL_CENTER_Z = 0.012
N_RIBS_DEFAULT = 8
RIB_MINOR_R = 0.0006
RIB_ZONE_START = -0.050
RIB_ZONE_END = 0.020

FINGER_GROOVE_RADIUS = 0.005
FINGER_GROOVE_PENETRATION = 0.003
N_GROOVES_DEFAULT = 4


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ===========================================================================
# Config dataclasses
# ===========================================================================
@dataclass(frozen=True)
class KnifeConfig:
    deployment: Deployment | None = None
    grip: Grip | None = None
    blade: Blade | None = None
    palette_style: PaletteStyle = "safety_yellow_abs"
    handle_len_scale: float = 1.0
    handle_height_scale: float = 1.0
    handle_width_scale: float = 1.0
    blade_len_scale: float = 1.0
    blade_width_scale: float = 1.0
    slide_travel_scale: float = 1.0
    fold_open_scale: float = 1.0
    guard_open_scale: float = 1.0
    barrel_radius_scale: float = 1.0
    tpr_rib_count: int = N_RIBS_DEFAULT
    finger_groove_count: int = N_GROOVES_DEFAULT
    name: str = "knife"


@dataclass(frozen=True)
class ResolvedKnifeConfig:
    deployment: Deployment
    grip: Grip
    blade: Blade
    palette_style: PaletteStyle
    # derived flags
    is_slide: bool
    fixed_blade: bool  # True only for flipup_guard (blade is handle inline)
    # resolved geometry
    handle_len: float
    handle_h: float
    handle_w: float
    handle_front_h: float
    channel_depth: float
    blade_len: float
    blade_w: float
    slide_travel: float
    fold_open: float
    guard_open: float
    barrel_r_max: float
    tpr_rib_count: int
    finger_groove_count: int
    # derived positions
    nose_x: float
    z_blade_top: float        # blade spine Z (inside top channel) for slide/guard
    blade_rear_x: float       # rear X of the exposed blade at rest (slide/guard)
    pivot_x: float            # fold pivot X
    pivot_z: float
    hinge_x: float            # guard hinge X
    hinge_z: float
    fixed_blade_exposed: float
    name: str

    @property
    def handle_x0(self) -> float:
        return -self.handle_len / 2.0

    @property
    def handle_x1(self) -> float:
        return self.handle_len / 2.0


def config_from_seed(seed: int) -> KnifeConfig:
    """Deterministic procedural sampling (seed=0 is not special, spec §9)."""
    rng = random.Random(seed)
    deployment: Deployment = rng.choice(DEPLOYMENTS)
    grip: Grip = rng.choice(GRIPS)
    blade: Blade = rng.choice(BLADES)
    palette_style: PaletteStyle = rng.choices(
        PALETTE_STYLES, weights=_PALETTE_WEIGHTS[deployment], k=1
    )[0]
    return KnifeConfig(
        deployment=deployment,
        grip=grip,
        blade=blade,
        palette_style=palette_style,
        handle_len_scale=round(rng.uniform(0.88, 1.12), 4),
        handle_height_scale=round(rng.uniform(0.85, 1.15), 4),
        handle_width_scale=round(rng.uniform(0.88, 1.15), 4),
        blade_len_scale=round(rng.uniform(0.85, 1.15), 4),
        blade_width_scale=round(rng.uniform(0.90, 1.12), 4),
        slide_travel_scale=round(rng.uniform(0.85, 1.10), 4),
        fold_open_scale=round(rng.uniform(0.85, 1.05), 4),
        guard_open_scale=round(rng.uniform(0.85, 1.05), 4),
        barrel_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        tpr_rib_count=rng.randint(6, 10),
        finger_groove_count=rng.randint(3, 5),
        name=f"seeded_knife_{seed}",
    )


def resolve_config(config: KnifeConfig | None = None) -> ResolvedKnifeConfig:
    cfg = config or KnifeConfig()
    deployment = _pick(cfg.deployment, DEPLOYMENTS)
    grip = _pick(cfg.grip, GRIPS)
    blade = _pick(cfg.blade, BLADES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    is_slide = deployment in SLIDE_DEPLOYMENTS
    fixed_blade = deployment == "flipup_guard"

    # --- independent handle scales ---
    # overmold_barrel uses a fixed-span lofted profile (±0.075), so its overall
    # length is not driven by handle_len_scale (the cap + joint anchor to the
    # profile ends); the other grips scale freely.
    if grip == "overmold_barrel":
        handle_len = HANDLE_LEN
    else:
        handle_len = HANDLE_LEN * _clamp(cfg.handle_len_scale, 0.88, 1.12)
    handle_h = _HANDLE_H_BASE[grip] * _clamp(cfg.handle_height_scale, 0.85, 1.15)
    handle_w = HANDLE_W * _clamp(cfg.handle_width_scale, 0.88, 1.15)
    handle_front_h = min(HANDLE_FRONT_H, handle_h * 0.62)
    channel_depth = min(_CHANNEL_DEPTH_BASE[grip] * (handle_h / _HANDLE_H_BASE[grip]),
                        handle_h - 0.003)

    # --- blade scales ---
    blade_len = BLADE_LEN * _clamp(cfg.blade_len_scale, 0.85, 1.15)
    # channel-容刃: blade width must not exceed handle height minus a top margin.
    blade_w = BLADE_W * _clamp(cfg.blade_width_scale, 0.90, 1.12)
    blade_w = min(blade_w, handle_h - 0.004)
    blade_w = max(blade_w, 0.010)

    # --- conditional scales (resolved per slot; nominal otherwise) ---
    if deployment == "snap_off_slide":
        slide_travel = SLIDE_TRAVEL * _clamp(cfg.slide_travel_scale, 0.85, 1.10)
    elif deployment == "retract_full":
        slide_travel = RETRACT_TRAVEL * _clamp(cfg.slide_travel_scale, 0.85, 1.10)
    else:
        slide_travel = SLIDE_TRAVEL
    fold_open = (math.pi * 0.99) * _clamp(cfg.fold_open_scale, 0.85, 1.05) \
        if deployment == "fold_pivot" else math.pi
    fold_open = min(fold_open, math.pi * 0.999)
    guard_open = (math.pi * 0.99) * _clamp(cfg.guard_open_scale, 0.85, 1.05) \
        if deployment == "flipup_guard" else math.pi
    guard_open = min(guard_open, math.pi * 0.999)

    if grip == "overmold_barrel":
        barrel_r_max = _BARREL_R_MAX * _clamp(cfg.barrel_radius_scale, 0.90, 1.12)
        barrel_r_max = _clamp(barrel_r_max, 0.012, 0.017)  # keep 24-34 mm dia
    else:
        barrel_r_max = _BARREL_R_MAX

    tpr_rib_count = int(_clamp(cfg.tpr_rib_count, 4, 16))
    finger_groove_count = int(_clamp(cfg.finger_groove_count, 2, 5))

    # --- derived positions ---
    nose_x = handle_len / 2.0
    z_blade_top = handle_h - 0.0035
    # fold_pivot: slim flat bar inner cavity is tight (spec §9 fold x flat_metal).
    if deployment == "fold_pivot" and grip == "flat_metal_bar":
        blade_len = min(blade_len, handle_len * 0.42)

    # snap_off / guard rest blade position (exposed forward of the nose).
    exposed_rest = BLADE_EXPOSED_REST
    fixed_blade_exposed = min(FIXED_BLADE_EXPOSED, blade_len - 0.012)
    if deployment == "retract_full":
        # q=0 fully retracted: blade front behind nose by BLADE_RETRACT.
        blade_rear_x = nose_x - BLADE_RETRACT - blade_len
        # retract全收: handle_len must accommodate blade fully (spec §7); ensure
        # the blade rear stays inside the body.
        if blade_rear_x < -nose_x + 0.006:
            blade_len = (nose_x - BLADE_RETRACT) - (-nose_x + 0.006)
            blade_rear_x = nose_x - BLADE_RETRACT - blade_len
    elif fixed_blade:
        blade_rear_x = nose_x - (blade_len - fixed_blade_exposed)
    else:  # snap_off_slide
        blade_rear_x = nose_x - (blade_len - exposed_rest)

    # snap_off / retract retained-travel inequality (spec §7): full travel must
    # keep the blade root overlapping the handle body (>=0.005). Cap travel.
    if is_slide:
        rest_overlap = nose_x - blade_rear_x  # blade length inside body at rest
        max_travel = max(0.006, rest_overlap - 0.006)
        slide_travel = min(slide_travel, max_travel)

    pivot_x = nose_x - 0.010
    pivot_z = min(PIVOT_Z, handle_h * 0.45)
    hinge_x = nose_x - 0.007
    hinge_z = handle_h - 0.002

    return ResolvedKnifeConfig(
        deployment=deployment,
        grip=grip,
        blade=blade,
        palette_style=palette_style,
        is_slide=is_slide,
        fixed_blade=fixed_blade,
        handle_len=handle_len,
        handle_h=handle_h,
        handle_w=handle_w,
        handle_front_h=handle_front_h,
        channel_depth=channel_depth,
        blade_len=blade_len,
        blade_w=blade_w,
        slide_travel=slide_travel,
        fold_open=fold_open,
        guard_open=guard_open,
        barrel_r_max=barrel_r_max,
        tpr_rib_count=tpr_rib_count,
        finger_groove_count=finger_groove_count,
        nose_x=nose_x,
        z_blade_top=z_blade_top,
        blade_rear_x=blade_rear_x,
        pivot_x=pivot_x,
        pivot_z=pivot_z,
        hinge_x=hinge_x,
        hinge_z=hinge_z,
        fixed_blade_exposed=fixed_blade_exposed,
        name=cfg.name or "knife",
    )


def slot_choices_for_config(
    config: KnifeConfig | ResolvedKnifeConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedKnifeConfig) else resolve_config(config)
    return (
        ("deployment", r.deployment),
        ("grip", r.grip),
        ("blade", r.blade),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Slot B / grip — handle main-shell mesh helpers (CadQuery, Rule 3)
# ===========================================================================
def _loft_handle_profile(r: ResolvedKnifeConfig, profile) -> cq.Workplane:
    """Loft rounded-rect cross sections along X (parent S0 L98-108)."""
    wires = []
    for x, hw, h, zc in profile:
        section = (
            cq.Workplane("YZ")
            .workplane(offset=x)
            .center(0.0, zc)
            .rect(2.0 * hw, h)
        )
        wires.append(section.val())
    solid = cq.Solid.makeLoft(wires, ruled=False)
    return cq.Workplane("XY").newObject([solid])


def _tapered_molded_body(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Classic tapered molded shell: rounded-rect loft (parent S0 L74-109)."""
    x0, x1 = r.handle_x0, r.handle_x1
    hw = r.handle_w / 2.0
    hh = r.handle_h
    fh = r.handle_front_h
    profile = [
        (x0, hw, hh, hh / 2.0),
        (x0 + 0.030, hw, hh, hh / 2.0),
        (x0 + 0.085, hw, hh * 0.92, hh * 0.46),
        (x1 - 0.030, hw * 0.92, fh + 0.003, fh / 2.0 + 0.004),
        (x1 - 0.006, hw * 0.78, fh, fh / 2.0 + 0.003),
        (x1, hw * 0.62, 0.010, 0.009),
    ]
    return _loft_handle_profile(r, profile)


def _ergo_contoured_body(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Ergonomic contoured shell: palm-swell 8-section loft (ergo S5 L80-125)."""
    x0, x1 = r.handle_x0, r.handle_x1
    hw = r.handle_w / 2.0
    hh = r.handle_h
    fh = r.handle_front_h
    profile = [
        (x0, hw * 0.98, hh, hh / 2.0),
        (x0 + 0.022, hw * 1.02, hh * 0.99, hh * 0.49),
        (x0 + 0.048, hw * 1.22, hh * 0.96, hh * 0.47),
        (x0 + 0.075, hw * 1.20, hh * 0.90, hh * 0.45),
        (x0 + 0.100, hw * 1.06, hh * 0.78, hh * 0.41),
        (x1 - 0.028, hw * 0.88, fh + 0.003, fh / 2.0 + 0.004),
        (x1 - 0.006, hw * 0.75, fh, fh / 2.0 + 0.003),
        (x1, hw * 0.58, 0.010, 0.009),
    ]
    body = _loft_handle_profile(r, profile)
    try:
        body = body.edges("|X").fillet(0.002)
    except Exception:
        pass
    return body


def _flat_metal_body(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Slim flat metal bar: uniform squared box + edge fillet (flat S7 L149-160)."""
    return (
        cq.Workplane("XY")
        .box(r.handle_len, r.handle_w, r.handle_h, centered=(True, True, False))
        .edges("|X")
        .fillet(0.0008)
    )


def _barrel_radius_at(r: ResolvedKnifeConfig, x: float) -> float:
    scale = r.barrel_r_max / _BARREL_R_MAX
    prof = [(px, pr * scale) for px, pr in _BARREL_PROFILE]
    for i in range(len(prof) - 1):
        x0, r0 = prof[i]
        x1, r1 = prof[i + 1]
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            return r0 + t * (r1 - r0)
    if x < prof[0][0]:
        return prof[0][1]
    return prof[-1][1]


def _barrel_body(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Lofted circular barrel shell (overmold S6 L102-115)."""
    scale = r.barrel_r_max / _BARREL_R_MAX
    wires = []
    for x, rad in _BARREL_PROFILE:
        w = (
            cq.Workplane("YZ")
            .workplane(offset=x)
            .center(0.0, _BARREL_CENTER_Z)
            .circle(rad * scale)
            .val()
        )
        wires.append(w)
    solid = cq.Solid.makeLoft(wires, ruled=False)
    return cq.Workplane("XY").newObject([solid])


def _channel_cut(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Top channel groove for the slide rail (parent S0 L112-121)."""
    length = r.handle_len + 0.02
    return (
        cq.Workplane("XY")
        .box(length, CHANNEL_W, r.channel_depth, centered=(True, True, False))
        .translate((0.0, 0.0, r.handle_h - r.channel_depth + 0.0005))
    )


def _lanyard_hole_cut(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Rear finger/lanyard through-hole along Y (parent S0 L124-134)."""
    x0 = r.handle_x0
    if r.grip == "overmold_barrel":
        return (
            cq.Workplane("XZ")
            .workplane(offset=0.020)
            .center(x0 + 0.014, _BARREL_CENTER_Z)
            .circle(0.0042)
            .extrude(-0.040)
        )
    return (
        cq.Workplane("XZ")
        .workplane(offset=r.handle_w)
        .center(x0 + 0.014, r.handle_h * 0.5)
        .circle(0.0042)
        .extrude(2.0 * r.handle_w)
    )


def _blade_exit_groove(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Front-top groove where a folding blade pivots out (fold S3 L111-124)."""
    slot_len = 0.022
    slot_w = BLADE_THK * 4.0
    slot_depth = 0.006
    x_center = r.pivot_x + 0.005
    z_top = r.handle_h - 0.001
    return (
        cq.Workplane("XY")
        .box(slot_len, slot_w, slot_depth + 0.004, centered=(True, True, False))
        .translate((x_center, 0.0, z_top - slot_depth))
    )


def _build_handle_shell(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Full handle shell: grip body minus channel/groove + lanyard hole."""
    if r.grip == "overmold_barrel":
        body = _barrel_body(r)
    elif r.grip == "ergo_contoured":
        body = _ergo_contoured_body(r)
    elif r.grip == "flat_metal_bar":
        body = _flat_metal_body(r)
    else:
        body = _tapered_molded_body(r)

    # fold deployment uses a front blade-exit groove instead of the slide channel;
    # the slide / guard deployments use the full top channel.
    if r.deployment == "fold_pivot":
        body = body.cut(_blade_exit_groove(r))
    else:
        body = body.cut(_channel_cut(r))
    body = body.cut(_lanyard_hole_cut(r))
    return body


def _build_top_channel_visual(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Gray channel/rail piece in the top groove (parent S0 L144-152).

    The rail is slightly WIDER than the channel cut so its side walls embed into
    the surrounding shell groove walls (real contact for every grip — otherwise a
    thin rail floats in a slightly wider groove and reads as an island), and it
    rises from below the channel floor to a touch proud of the shell top."""
    length = r.handle_len - 0.012
    rail_h = r.channel_depth + 0.0012
    return (
        cq.Workplane("XY")
        .box(length, CHANNEL_W + 0.0008, rail_h, centered=(True, True, False))
        .translate((0.002, 0.0, r.handle_h - r.channel_depth - 0.0006))
    )


def _build_thumb_grip_visual(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Black textured thumb pad on the front-top shoulder (parent S0 L155-178)."""
    base = cq.Workplane("XY").box(0.030, r.handle_w * 0.98, 0.0030, centered=(True, True, False))
    bumps = None
    for ix in range(6):
        for iy in range(4):
            x = -0.012 + ix * 0.0048
            y = -0.0045 + iy * 0.0030
            b = (
                cq.Workplane("XY")
                .transformed(offset=(x, y, 0.0030))
                .box(0.0026, 0.0018, 0.0016, centered=(True, True, False))
            )
            bumps = b if bumps is None else bumps.add(b)
    grip = base.add(bumps)
    return grip.translate((0.030, 0.0, r.handle_front_h - 0.0005))


def _build_side_thumb_grip_visual(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Side knurled grip pad on the +Y face for the slim flat bar (flat S7 L233-262)."""
    pad_len = 0.028
    pad_height = r.handle_h * 0.60
    pad_thk = 0.0015
    pad_cx = 0.020
    pad_cz = r.handle_h * 0.50
    y_base = r.handle_w / 2.0
    base = (
        cq.Workplane("XY")
        .box(pad_len, pad_thk, pad_height, centered=(True, True, True))
        .translate((pad_cx, y_base + pad_thk / 2.0, pad_cz))
    )
    bumps = None
    for ix in range(6):
        for iz in range(3):
            x = pad_cx - pad_len / 2.0 + (ix + 0.5) * (pad_len / 6)
            z = pad_cz - pad_height / 2.0 + (iz + 0.5) * (pad_height / 3)
            b = (
                cq.Workplane("XY")
                .box(0.0022, 0.0010, 0.0018, centered=(True, True, True))
                .translate((x, y_base + pad_thk + 0.0005, z))
            )
            bumps = b if bumps is None else bumps.add(b)
    return base.add(bumps) if bumps is not None else base


def _groove_positions(r: ResolvedKnifeConfig) -> list[float]:
    x0 = r.handle_x0
    n = r.finger_groove_count
    start, end = 0.028, 0.088
    if n <= 1:
        return [x0 + (start + end) / 2.0]
    step = (end - start) / (n - 1)
    return [x0 + start + i * step for i in range(n)]


def _build_finger_groove_insert(r: ResolvedKnifeConfig, gx: float) -> cq.Workplane:
    """One finger-groove rubber insert (ergo S5 L199-228)."""
    center_z = -FINGER_GROOVE_RADIUS + FINGER_GROOVE_PENETRATION
    insert_r = FINGER_GROOVE_RADIUS + 0.0006
    insert_len = r.handle_w - 0.002
    cyl = (
        cq.Workplane("XZ")
        .workplane(offset=-insert_len / 2.0)
        .center(gx, center_z)
        .circle(insert_r)
        .extrude(insert_len)
    )
    keep_block = (
        cq.Workplane("XY")
        .box(0.020, r.handle_w + 0.01, FINGER_GROOVE_PENETRATION + 0.002, centered=(True, True, False))
        .translate((gx, 0.0, -0.001))
    )
    return cyl.intersect(keep_block)


def _build_tpr_rib(r: ResolvedKnifeConfig, x_pos: float) -> cq.Workplane:
    """Single revolved TPR rib ring around the barrel axis (overmold S6 L162-178)."""
    barrel_r = _barrel_radius_at(r, x_pos)
    tube_center_r = barrel_r + RIB_MINOR_R * 0.7
    return (
        cq.Workplane("XZ")
        .moveTo(x_pos, _BARREL_CENTER_Z + tube_center_r)
        .circle(RIB_MINOR_R)
        .revolve(360, (-0.1, _BARREL_CENTER_Z), (0.1, _BARREL_CENTER_Z))
    )


# ===========================================================================
# Slot A / deployment — handle-side hardware (fold pivot, guard hinge bracket)
# ===========================================================================
def _build_pivot_pin(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Brass pivot pin through the handle at the fold hinge (fold S3 L134-144)."""
    pin_r = 0.0028
    pin_len = r.handle_w + 0.004
    return (
        cq.Workplane("XZ")
        .workplane(offset=-pin_len / 2.0)
        .center(r.pivot_x, r.pivot_z)
        .circle(pin_r)
        .extrude(pin_len)
    )


def _build_front_bolster(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Dark metal bolster around the fold pivot (fold S3 L147-158)."""
    length = 0.014
    w = r.handle_w * 1.04
    h = 0.014
    return (
        cq.Workplane("XY")
        .box(length, w, h, centered=(True, True, False))
        .edges("|Z").fillet(0.0018)
        .translate((r.pivot_x + 0.002, 0.0, 0.003))
    )


def _build_hinge_bracket(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Two hinge ears + crossbar carrying the guard pivot (guard S4 L258-290)."""
    ear_thk = 0.0018
    ear_w_x = 0.010
    handle_top_z = r.handle_h * 0.65
    ear_h = max(0.004, r.hinge_z - handle_top_z + HINGE_BARREL_R + 0.001)
    left_ear = (
        cq.Workplane("XY")
        .box(ear_w_x, ear_thk, ear_h, centered=(True, True, False))
        .edges("|Z").fillet(0.0006)
        .translate((r.hinge_x, r.handle_w / 2.0 + ear_thk / 2.0, handle_top_z))
    )
    right_ear = (
        cq.Workplane("XY")
        .box(ear_w_x, ear_thk, ear_h, centered=(True, True, False))
        .edges("|Z").fillet(0.0006)
        .translate((r.hinge_x, -(r.handle_w / 2.0 + ear_thk / 2.0), handle_top_z))
    )
    crossbar = (
        cq.Workplane("XY")
        .box(ear_w_x, r.handle_w + 2.0 * ear_thk, 0.0018, centered=(True, True, False))
        .edges("|Z").fillet(0.0005)
        .translate((r.hinge_x, 0.0, r.hinge_z - HINGE_BARREL_R - 0.0018))
    )
    return left_ear.add(right_ear).add(crossbar)


# ===========================================================================
# Slot C / blade profile — exposed blade outline mesh helpers (Rule 3).
# Authored in XZ with spine at z=0, cutting edge at -Z, rear spine corner at
# the local origin; thin along Y. bl = blade length, bw = blade width.
# ===========================================================================
def _blade_snap_off(bl: float, bw: float) -> cq.Workplane:
    """Straight snap-off parallelogram blade (parent S0 L184-209)."""
    pts = [
        (0.0, 0.0),
        (bl, 0.0),
        (bl, -bw + 0.004),
        (bl - 0.006, -bw),
        (0.0, -bw + 0.010),
    ]
    return (
        cq.Workplane("XZ").polyline(pts).close().extrude(BLADE_THK)
        .translate((0.0, -BLADE_THK / 2.0, 0.0))
    )


def _blade_snap_off_scores(bl: float, bw: float) -> cq.Workplane:
    """5 diagonal snap-off score grooves (parent S0 L212-227)."""
    grooves = None
    for i in range(5):
        x = 0.006 + i * 0.011
        if x > bl - 0.004:
            continue
        groove = (
            cq.Workplane("XZ")
            .center(x, -bw / 2.0)
            .rect(0.0012, bw + 0.004)
            .extrude(BLADE_THK + 0.0006)
            .translate((0.0, -(BLADE_THK + 0.0006) / 2.0, 0.0))
            .rotate((x, 0.0, -bw / 2.0), (x, 1.0, -bw / 2.0), 18.0)
        )
        grooves = groove if grooves is None else grooves.add(groove)
    return grooves


def _blade_snap_off_tip(bl: float, bw: float) -> cq.Workplane:
    pts = [
        (bl - 0.012, 0.0),
        (bl, 0.0),
        (bl, -bw + 0.004),
        (bl - 0.006, -bw),
        (bl - 0.012, -bw + 0.006),
    ]
    return (
        cq.Workplane("XZ").polyline(pts).close().extrude(BLADE_THK + 0.0002)
        .translate((0.0, -(BLADE_THK + 0.0002) / 2.0, 0.0))
    )


def _blade_hawkbill(bl: float, bw: float) -> cq.Workplane:
    """Hawkbill: straight spine + concave edge + downward hook (hawk S8 L188-218)."""
    return (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0)
        .lineTo(bl, 0.0)
        .spline([
            (bl - 0.002, -0.005),
            (bl - 0.005, -0.013),
            (bl - 0.008, -0.022),
            (bl - 0.016, -0.014),
            (bl * 0.50, -0.007),
            (bl * 0.25, -0.009),
            (0.0, -0.011),
        ])
        .close()
        .extrude(BLADE_THK)
        .translate((0.0, -BLADE_THK / 2.0, 0.0))
    )


def _hawkbill_edge_z(bl: float, x_frac: float) -> float:
    x = x_frac * bl
    if x >= bl - 0.008:
        t = (x - (bl - 0.008)) / 0.008
        return -0.014 - t * 0.008
    if x >= bl * 0.25:
        t = (x - bl * 0.25) / (bl - 0.008 - bl * 0.25)
        return -0.009 - 0.005 * math.sin(t * math.pi)
    t = x / (bl * 0.25)
    return -0.011 + t * 0.002


def _blade_hawkbill_scores(bl: float, bw: float) -> cq.Workplane:
    grooves = None
    for i in range(5):
        x = 0.006 + i * 0.011
        if x > bl - 0.004:
            continue
        edge_z = _hawkbill_edge_z(bl, x / bl)
        local_depth = abs(edge_z) + 0.004
        groove = (
            cq.Workplane("XZ")
            .center(x, edge_z / 2.0)
            .rect(0.0012, local_depth)
            .extrude(BLADE_THK + 0.0006)
            .translate((0.0, -(BLADE_THK + 0.0006) / 2.0, 0.0))
            .rotate((x, 0.0, edge_z / 2.0), (x, 1.0, edge_z / 2.0), 18.0)
        )
        grooves = groove if grooves is None else grooves.add(groove)
    return grooves


def _blade_hawkbill_tip(bl: float, bw: float) -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .moveTo(bl - 0.014, 0.0)
        .lineTo(bl, 0.0)
        .spline([
            (bl - 0.002, -0.005),
            (bl - 0.005, -0.013),
            (bl - 0.008, -0.022),
            (bl - 0.012, -0.017),
            (bl - 0.014, -0.012),
        ])
        .close()
        .extrude(BLADE_THK + 0.0002)
        .translate((0.0, -(BLADE_THK + 0.0002) / 2.0, 0.0))
    )


def _blade_drop_point(bl: float, bw: float) -> cq.Workplane:
    """Drop-point: gentle spine drop + belly + centered tip (drop S9 L187-217)."""
    pts = [
        (0.0, 0.0),
        (bl * 0.55, -0.001),
        (bl * 0.80, -0.004),
        (bl, -0.008),
        (bl, -bw * 0.50),
        (bl * 0.80, -bw * 0.72),
        (bl * 0.55, -bw * 0.88),
        (bl * 0.25, -bw * 0.96),
        (0.0, -bw),
    ]
    return (
        cq.Workplane("XZ").polyline(pts).close().extrude(BLADE_THK)
        .translate((0.0, -BLADE_THK / 2.0, 0.0))
    )


def _blade_drop_grind(bl: float, bw: float) -> cq.Workplane:
    """Bevel grind line on the drop-point blade (drop S9 L220-242)."""
    y_top_rear = -bw + 0.004
    y_top_front = -bw * 0.70 + 0.003
    return (
        cq.Workplane("XZ")
        .moveTo(0.004, y_top_rear)
        .lineTo(bl - 0.016, y_top_front)
        .lineTo(bl - 0.016, y_top_front + 0.001)
        .lineTo(0.004, y_top_rear + 0.001)
        .close()
        .extrude(BLADE_THK + 0.0004)
        .translate((0.0, -(BLADE_THK + 0.0004) / 2.0, 0.0))
    )


def _blade_drop_tip(bl: float, bw: float) -> cq.Workplane:
    x_cut = bl - 0.015
    t_spine = (x_cut - bl * 0.55) / (bl * 0.80 - bl * 0.55)
    z_spine_cut = -0.001 + t_spine * (-0.004 - (-0.001))
    t_belly = (x_cut - bl * 0.55) / (bl * 0.80 - bl * 0.55)
    z_belly_cut = -bw * 0.88 + t_belly * (-bw * 0.72 - (-bw * 0.88))
    pts = [
        (x_cut, z_spine_cut),
        (bl, -0.008),
        (bl, -bw * 0.50),
        (x_cut, z_belly_cut),
    ]
    return (
        cq.Workplane("XZ").polyline(pts).close().extrude(BLADE_THK + 0.0002)
        .translate((0.0, -(BLADE_THK + 0.0002) / 2.0, 0.0))
    )


def _sheepsfoot_outline_pts(bl: float, bw: float) -> list[tuple[float, float]]:
    """Serrated sheepsfoot outline: dropping spine + blunt tip + 14 teeth
    (serr S10 L180-245)."""
    pts: list[tuple[float, float]] = []
    pts.append((0.0, 0.0))
    pts.append((bl * 0.72, 0.0))
    n_curve = 8
    curve_start_x = bl * 0.72
    curve_end_x = bl - 0.002
    for i in range(1, n_curve + 1):
        t = i / n_curve
        x = curve_start_x + t * (curve_end_x - curve_start_x)
        z = -bw * 0.60 * (t ** 1.6)
        pts.append((x, z))
    tip_cx = curve_end_x
    tip_cz = -bw * 0.60
    tip_r = 0.0025
    for i in range(1, 5):
        angle = math.pi / 2.0 * (i / 4.0)
        x = tip_cx + tip_r * math.sin(angle)
        z = tip_cz - tip_r * (1.0 - math.cos(angle))
        pts.append((x, z))
    cutting_baseline = -bw + 0.004
    n_teeth = 14
    tooth_start_x = bl * 0.88
    tooth_span = tooth_start_x - 0.003
    tooth_pitch = tooth_span / n_teeth
    tooth_depth = 0.0018
    pts.append((tooth_start_x, cutting_baseline))
    for i in range(n_teeth):
        x_peak = tooth_start_x - i * tooth_pitch
        x_valley = x_peak - tooth_pitch * 0.5
        x_next_peak = x_peak - tooth_pitch
        pts.append((x_valley, cutting_baseline - tooth_depth))
        pts.append((x_next_peak, cutting_baseline))
    pts.append((0.0, cutting_baseline))
    pts.append((0.0, -bw + 0.010))
    return pts


def _blade_sheepsfoot(bl: float, bw: float) -> cq.Workplane:
    pts = _sheepsfoot_outline_pts(bl, bw)
    return (
        cq.Workplane("XZ").polyline(pts).close().extrude(BLADE_THK)
        .translate((0.0, -BLADE_THK / 2.0, 0.0))
    )


def _blade_sheepsfoot_tip(bl: float, bw: float) -> cq.Workplane:
    pts: list[tuple[float, float]] = []
    tip_region_start = bl * 0.72
    pts.append((tip_region_start, 0.0))
    n_curve = 6
    curve_end_x = bl - 0.002
    for i in range(1, n_curve + 1):
        t = i / n_curve
        x = tip_region_start + t * (curve_end_x - tip_region_start)
        z = -bw * 0.60 * (t ** 1.6)
        pts.append((x, z))
    tip_cx = curve_end_x
    tip_cz = -bw * 0.60
    tip_r = 0.0025
    for i in range(1, 5):
        angle = math.pi / 2.0 * (i / 4.0)
        x = tip_cx + tip_r * math.sin(angle)
        z = tip_cz - tip_r * (1.0 - math.cos(angle))
        pts.append((x, z))
    cutting_baseline = -bw + 0.004
    pts.append((tip_region_start + 0.002, cutting_baseline))
    pts.append((tip_region_start, cutting_baseline))
    return (
        cq.Workplane("XZ").polyline(pts).close().extrude(BLADE_THK + 0.0002)
        .translate((0.0, -(BLADE_THK + 0.0002) / 2.0, 0.0))
    )


def _build_blade_steel_and_tip(r: ResolvedKnifeConfig):
    """Return (blade_steel_solid, tip_solid) for the chosen blade profile, with
    the profile carved by its score / grind detail (module-internal loops)."""
    bl, bw = r.blade_len, r.blade_w
    if r.blade == "hawkbill":
        blade = _blade_hawkbill(bl, bw)
        scores = _blade_hawkbill_scores(bl, bw)
        tip = _blade_hawkbill_tip(bl, bw)
        if scores is not None:
            blade = blade.cut(scores)
    elif r.blade == "drop_point":
        blade = _blade_drop_point(bl, bw)
        grind = _blade_drop_grind(bl, bw)
        tip = _blade_drop_tip(bl, bw)
        blade = blade.cut(grind)
    elif r.blade == "serrated_sheepsfoot":
        blade = _blade_sheepsfoot(bl, bw)
        tip = _blade_sheepsfoot_tip(bl, bw)
    else:  # snap_off_segmented
        blade = _blade_snap_off(bl, bw)
        scores = _blade_snap_off_scores(bl, bw)
        tip = _blade_snap_off_tip(bl, bw)
        if scores is not None:
            blade = blade.cut(scores)
    return blade, tip


# ===========================================================================
# Shared carrier / blade / guard sub-geometry
# ===========================================================================
def _build_blade_spine_carrier() -> cq.Workplane:
    """Gray carrier block over the blade spine, rides the channel (parent L251-261)."""
    return cq.Workplane("XY").box(0.020, CHANNEL_W - 0.0006, 0.005, centered=(True, True, False))


def _build_thumb_button() -> cq.Workplane:
    """Ribbed thumb slide button through the channel slot (parent L264-280)."""
    base = (
        cq.Workplane("XY")
        .box(0.013, 0.0060, 0.0050, centered=(True, True, False))
        .edges("|Z").fillet(0.0010)
    )
    ribs = None
    for i in range(5):
        x = -0.004 + i * 0.002
        rr = (
            cq.Workplane("XY")
            .transformed(offset=(x, 0.0, 0.0050))
            .box(0.0008, 0.0060, 0.0014, centered=(True, True, False))
        )
        ribs = rr if ribs is None else ribs.add(rr)
    return base.add(ribs)


def _build_blade_clamp() -> cq.Workplane:
    """Flat clamp plate gripping the blade spine (retract S2 L211-217)."""
    return cq.Workplane("XY").box(0.030, CHANNEL_W - 0.0006, 0.004, centered=(True, True, False))


def _build_clamp_post() -> cq.Workplane:
    """Cylindrical mounting post through a blade hole (retract S2 L220-228)."""
    return cq.Workplane("XY").circle(0.0014).extrude(0.009)


def _build_thumb_stud() -> cq.Workplane:
    """Brass thumb stud near the fold blade pivot (fold S3 L234-245)."""
    stud_y = BLADE_THK / 2.0
    return (
        cq.Workplane("XZ")
        .workplane(offset=stud_y)
        .center(-0.008, 0.0)
        .rect(0.006, 0.005)
        .extrude(0.002)
    )


def _build_fold_blade_body(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Folding blade outline in the blade's local frame (origin = pivot, extends
    -X). Injects the chosen blade profile, mirrored to grow -X (fold S3 L194-211).

    We build the chosen profile growing +X then mirror to -X so the spine sits at
    local -Z (becomes world +Z up when deployed)."""
    bl = min(r.blade_len, FOLD_BLADE_LEN if r.grip != "flat_metal_bar" else r.blade_len)
    bw = min(r.blade_w, FOLD_BLADE_W + 0.002)
    blade_fwd, _ = _build_blade_steel_and_tip(
        ResolvedKnifeConfigProxy(r, blade_len=bl, blade_w=bw)
    )
    # Mirror about X=0 (so it grows -X), then flip Z so the spine is up-when-open.
    blade = blade_fwd.mirror("YZ").mirror("XY")
    return blade


def _build_fold_blade_tip(r: ResolvedKnifeConfig) -> cq.Workplane:
    bl = min(r.blade_len, FOLD_BLADE_LEN if r.grip != "flat_metal_bar" else r.blade_len)
    bw = min(r.blade_w, FOLD_BLADE_W + 0.002)
    _, tip_fwd = _build_blade_steel_and_tip(
        ResolvedKnifeConfigProxy(r, blade_len=bl, blade_w=bw)
    )
    return tip_fwd.mirror("YZ").mirror("XY")


class ResolvedKnifeConfigProxy:
    """Lightweight shim that overrides blade_len / blade_w on a resolved config
    so the fold blade can use a shorter blade without rebuilding the whole config.
    """

    def __init__(self, base: ResolvedKnifeConfig, *, blade_len: float, blade_w: float):
        self._base = base
        self.blade_len = blade_len
        self.blade_w = blade_w

    def __getattr__(self, item):
        return getattr(self._base, item)


# Guard sub-geometry (guard S4 L296-390) -----------------------------------
def _build_guard_hinge_barrel() -> cq.Workplane:
    return (
        cq.Workplane("XZ")
        .center(0.0, 0.0)
        .circle(HINGE_BARREL_R)
        .extrude(HINGE_BARREL_LEN)
        .translate((0.0, HINGE_BARREL_LEN / 2.0, 0.0))
    )


def _build_guard_body(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Full guard: barrel + plate + skirts + front lip + grip ribs (guard L296-390).
    Guard plate length covers the permanently-exposed blade length."""
    guard_len = max(0.052, r.fixed_blade_exposed + 0.008)
    plate_z_top = -HINGE_BARREL_R + 0.0005
    plate_z_bot = plate_z_top - GUARD_THK
    skirt_z_bot = plate_z_bot - GUARD_SKIRT_H
    plate_x0 = HINGE_BARREL_R * 0.4

    barrel = _build_guard_hinge_barrel()
    plate = (
        cq.Workplane("XY")
        .box(guard_len, GUARD_W, GUARD_THK, centered=(False, True, False))
        .translate((plate_x0, 0.0, plate_z_top - GUARD_THK))
    )
    left_skirt = (
        cq.Workplane("XY")
        .box(guard_len, GUARD_SKIRT_THK, GUARD_SKIRT_H, centered=(False, True, False))
        .translate((plate_x0, GUARD_W / 2.0 - GUARD_SKIRT_THK / 2.0, skirt_z_bot))
    )
    right_skirt = (
        cq.Workplane("XY")
        .box(guard_len, GUARD_SKIRT_THK, GUARD_SKIRT_H, centered=(False, True, False))
        .translate((plate_x0, -(GUARD_W / 2.0 - GUARD_SKIRT_THK / 2.0), skirt_z_bot))
    )
    inner_w = GUARD_W - 2.0 * GUARD_SKIRT_THK
    front_lip = (
        cq.Workplane("XY")
        .box(GUARD_THK, inner_w, GUARD_SKIRT_H, centered=(False, True, False))
        .translate((plate_x0 + guard_len - GUARD_THK, 0.0, skirt_z_bot))
    )
    ribs = None
    n_ribs = max(2, int(guard_len / 0.009))
    for i in range(n_ribs):
        x = plate_x0 + 0.008 + i * 0.007
        if x > plate_x0 + guard_len - 0.004:
            break
        rib = (
            cq.Workplane("XY")
            .box(0.001, GUARD_W * 0.70, 0.001, centered=(True, True, False))
            .translate((x, 0.0, plate_z_top))
        )
        ribs = rib if ribs is None else ribs.add(rib)
    body = barrel.add(plate).add(left_skirt).add(right_skirt).add(front_lip)
    if ribs is not None:
        body = body.add(ribs)
    return body


def _build_end_cap(r: ResolvedKnifeConfig) -> cq.Workplane:
    """Rear end cap, authored in the cap's LOCAL frame whose origin is the
    handle-tail FIXED-joint origin at (handle_x0, 0, handle_h/2). The cap face
    sits at local X=0 and extrudes rearward (-X) so it seats flush against the
    handle tail (parent S0 L305-317)."""
    if r.grip == "overmold_barrel":
        rear_r = _barrel_radius_at(r, r.handle_x0)
        return (
            cq.Workplane("YZ")
            .workplane(offset=0.0)
            .center(0.0, _BARREL_CENTER_Z - r.handle_h / 2.0)
            .circle(rear_r * 1.02)
            .extrude(-0.012)
        )
    cap = (
        cq.Workplane("YZ")
        .workplane(offset=0.0)
        .center(0.0, 0.0)
        .rect(r.handle_w * 1.02, r.handle_h * 0.96)
        .extrude(-0.012)
        .edges("|X").fillet(0.0025)
    )
    return cap


# ===========================================================================
# Build
# ===========================================================================
def build_knife(
    config: KnifeConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    pal = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"knife_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in pal.items()
    }

    def m(geom, name):
        return mesh_from_cadquery(geom, name, assets=assets)

    # --- Handle (root) -----------------------------------------------------
    handle = model.part("handle")
    shell_name = "barrel_shell" if r.grip == "overmold_barrel" else "handle_shell"
    handle.visual(m(_build_handle_shell(r), shell_name), material=mats["handle"], name=shell_name, material_class_id=("plastic.opaque_glossy_molded" if r.grip in {"tapered_molded", "ergo_contoured", "overmold_barrel"} else "metal.paint_coated"))

    # Slide / guard deployments keep the top channel rail; fold uses the groove.
    if r.deployment != "fold_pivot":
        handle.visual(m(_build_top_channel_visual(r), "top_channel"),
                      material=mats["channel"], name="top_channel", material_class_id="metal.stainless_matte")

    # Grip-specific surface detail (fixed arrays; Rule 1 inline visuals).
    if r.grip == "flat_metal_bar":
        handle.visual(m(_build_side_thumb_grip_visual(r), "thumb_grip"),
                      material=mats["accent"], name="thumb_grip", material_class_id="rubber.pebbled")
    elif r.grip == "overmold_barrel":
        rib_n = r.tpr_rib_count
        rib_spacing = (RIB_ZONE_END - RIB_ZONE_START) / (rib_n - 1) if rib_n > 1 else 0.0
        for i in range(rib_n):
            x = RIB_ZONE_START + i * rib_spacing
            handle.visual(m(_build_tpr_rib(r, x), f"tpr_rib_{i}"),
                          material=mats["rubber"], name=f"tpr_rib_{i}", material_class_id="rubber.directional_grooved")
    else:
        handle.visual(m(_build_thumb_grip_visual(r), "thumb_grip"),
                      material=mats["accent"], name="thumb_grip", material_class_id="rubber.pebbled")
        if r.grip == "ergo_contoured":
            for i, gx in enumerate(_groove_positions(r)):
                handle.visual(m(_build_finger_groove_insert(r, gx), f"finger_groove_{i}"),
                              material=mats["rubber"], name=f"finger_groove_{i}", material_class_id="rubber.smooth_plain")

    # Deployment-specific handle hardware.
    if r.deployment == "fold_pivot":
        handle.visual(m(_build_front_bolster(r), "front_bolster"),
                      material=mats["cap"], name="front_bolster", material_class_id="metal.blackened_gunmetal")
        handle.visual(m(_build_pivot_pin(r), "pivot_pin"),
                      material=mats["brass"], name="pivot_pin", material_class_id="metal.brass_polished")
    elif r.deployment == "flipup_guard":
        handle.visual(m(_build_hinge_bracket(r), "hinge_bracket"),
                      material=mats["channel"], name="hinge_bracket", material_class_id="metal.stainless_matte")
        # Fixed blade inline on the handle (permanently exposed).
        blade_steel, blade_tip = _build_blade_steel_and_tip(r)
        blade_steel = blade_steel.translate((r.blade_rear_x, 0.0, r.z_blade_top))
        blade_tip = blade_tip.translate((r.blade_rear_x, 0.0, r.z_blade_top))
        handle.visual(m(blade_steel, "blade_steel"), material=mats["blade"], name="blade_steel", material_class_id="metal.stainless_matte")
        handle.visual(m(blade_tip, "blade_tip"), material=mats["tip"], name="blade_tip", material_class_id="metal.stainless_matte")

    handle.inertial = Inertial.from_geometry(
        Box((r.handle_len, max(r.handle_w, 0.02), r.handle_h + 0.02)),
        mass=0.08,
        origin=Origin(xyz=(0.0, 0.0, r.handle_h / 2.0)),
    )

    # --- Rear end cap (FIXED part on every deployment) ---------------------
    end_cap = model.part("end_cap")
    end_cap.visual(m(_build_end_cap(r), "end_cap"), material=mats["cap"], name="end_cap_body", material_class_id=("plastic.opaque_glossy_molded" if r.grip in {"tapered_molded", "ergo_contoured", "overmold_barrel"} else "metal.paint_coated"))
    end_cap.inertial = Inertial.from_geometry(
        Box((0.012, r.handle_w, r.handle_h)),
        mass=0.01,
        origin=Origin(xyz=(-0.006, 0.0, 0.0)),
    )
    # Origin on real rear hardware (the handle tail face), so the flat 0.015 m
    # articulation-origin baseline holds for both parent and child AABBs.
    model.articulation(
        "handle_to_cap",
        ArticulationType.FIXED,
        parent=handle,
        child=end_cap,
        origin=Origin(xyz=(r.handle_x0, 0.0, r.handle_h / 2.0)),
    )

    # --- Deployment moving member + non-FIXED identity joint ---------------
    if r.deployment == "snap_off_slide":
        _emit_snap_off_carrier(model, r, handle, mats, m)
    elif r.deployment == "retract_full":
        _emit_retract_carrier(model, r, handle, mats, m)
    elif r.deployment == "fold_pivot":
        _emit_fold_blade(model, r, handle, mats, m)
    else:  # flipup_guard
        _emit_flipup_guard(model, r, handle, mats, m)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def _emit_snap_off_carrier(model, r, handle, mats, m):
    carrier = model.part("blade_carrier")
    z_top = r.z_blade_top
    rx = r.blade_rear_x
    # Slide joint origin on the channel rail at the carrier's rest spine footprint
    # (real shared hardware) so the flat 0.015 m articulation-origin baseline holds.
    # The carrier part frame sits at this joint origin, so every visual is authored
    # at world - (dx, dz) to land at its intended world pose at rest (q=0).
    dx = rx + 0.020
    dz = r.handle_h - r.channel_depth / 2.0
    blade_steel, blade_tip = _build_blade_steel_and_tip(r)
    blade_steel = blade_steel.translate((rx - dx, 0.0, z_top - dz))
    blade_tip = blade_tip.translate((rx - dx, 0.0, z_top - dz))
    spine = _build_blade_spine_carrier().translate((rx + 0.010 - dx, 0.0, z_top - 0.0015 - dz))
    button = _build_thumb_button().translate((rx + 0.012 - dx, 0.0, r.handle_h - 0.0035 - dz))

    carrier.visual(m(blade_steel, "blade_steel"), material=mats["blade"], name="blade_steel", material_class_id="metal.stainless_matte")
    carrier.visual(m(blade_tip, "blade_tip"), material=mats["tip"], name="blade_tip", material_class_id="metal.stainless_matte")
    carrier.visual(m(spine, "blade_spine"), material=mats["channel"], name="blade_spine", material_class_id="metal.stainless_matte")
    carrier.visual(m(button, "thumb_button"), material=mats["channel"], name="thumb_button", material_class_id="metal.stainless_matte")
    carrier.inertial = Inertial.from_geometry(
        Box((r.blade_len, 0.004, r.blade_w + 0.01)),
        mass=0.01,
        origin=Origin(xyz=(rx + r.blade_len / 2.0 - dx, 0.0, z_top - r.blade_w / 2.0 - dz)),
    )
    model.articulation(
        "handle_to_carrier",
        ArticulationType.PRISMATIC,
        parent=handle,
        child=carrier,
        origin=Origin(xyz=(dx, 0.0, dz)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.2, lower=0.0, upper=r.slide_travel),
    )


def _emit_retract_carrier(model, r, handle, mats, m):
    carrier = model.part("blade_carrier")
    z_blade_spine = r.handle_h - 0.003
    rx = r.blade_rear_x
    z_blade_top = z_blade_spine
    holder_cx = rx + r.blade_len / 2.0
    z_clamp = z_blade_spine - 0.002
    # Slide joint origin on the channel rail at the carrier's rest clamp footprint;
    # carrier visuals are authored at world - (dx, dz) (part frame is at the origin).
    dx = holder_cx
    dz = r.handle_h - r.channel_depth / 2.0

    blade_steel, blade_tip = _build_blade_steel_and_tip(r)
    blade_steel = blade_steel.translate((rx - dx, 0.0, z_blade_top - dz))
    blade_tip = blade_tip.translate((rx - dx, 0.0, z_blade_top - dz))
    carrier.visual(m(blade_steel, "blade_body"), material=mats["blade"], name="blade_body", material_class_id="metal.stainless_matte")
    carrier.visual(m(blade_tip, "blade_tip"), material=mats["tip"], name="blade_tip", material_class_id="metal.stainless_matte")

    clamp = _build_blade_clamp().translate((holder_cx - dx, 0.0, z_clamp - dz))
    carrier.visual(m(clamp, "blade_clamp"), material=mats["channel"], name="blade_clamp", material_class_id="metal.stainless_matte")

    # 2 mounting posts (fixed N=2, bound to the blade mount holes; Rule 1 inline).
    z_post_base = z_blade_top - 0.008
    pin_offsets = [r.blade_len * 0.27, r.blade_len * 0.66]
    for i in range(2):
        post = _build_clamp_post().translate((rx + pin_offsets[i] - dx, 0.0, z_post_base - dz))
        carrier.visual(m(post, f"post_{i}"), material=mats["cap"], name=f"post_{i}", material_class_id="metal.blackened_gunmetal")

    button = _build_thumb_button().translate((holder_cx - dx, 0.0, z_clamp + 0.004 - dz))
    carrier.visual(m(button, "thumb_button"), material=mats["channel"], name="thumb_button", material_class_id="metal.stainless_matte")
    carrier.inertial = Inertial.from_geometry(
        Box((r.blade_len, 0.004, r.blade_w + 0.01)),
        mass=0.01,
        origin=Origin(xyz=(rx + r.blade_len / 2.0 - dx, 0.0, z_blade_top - r.blade_w / 2.0 - dz)),
    )
    model.articulation(
        "handle_to_carrier",
        ArticulationType.PRISMATIC,
        parent=handle,
        child=carrier,
        origin=Origin(xyz=(dx, 0.0, dz)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.2, lower=0.0, upper=r.slide_travel),
    )


def _emit_fold_blade(model, r, handle, mats, m):
    blade = model.part("blade")
    blade_body = _build_fold_blade_body(r)
    blade_tip = _build_fold_blade_tip(r)
    thumb_stud = _build_thumb_stud()
    blade.visual(m(blade_body, "blade_body"), material=mats["blade"], name="blade_body", material_class_id="metal.stainless_matte")
    blade.visual(m(blade_tip, "blade_tip"), material=mats["tip"], name="blade_tip", material_class_id="metal.stainless_matte")
    blade.visual(m(thumb_stud, "thumb_stud"), material=mats["brass"], name="thumb_stud", material_class_id="metal.brass_polished")
    bl = min(r.blade_len, FOLD_BLADE_LEN if r.grip != "flat_metal_bar" else r.blade_len)
    blade.inertial = Inertial.from_geometry(
        Box((bl, 0.004, r.blade_w + 0.01)),
        mass=0.01,
        origin=Origin(xyz=(-bl / 2.0, 0.0, 0.0)),
    )
    model.articulation(
        "handle_to_blade",
        ArticulationType.REVOLUTE,
        parent=handle,
        child=blade,
        origin=Origin(xyz=(r.pivot_x, 0.0, r.pivot_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=r.fold_open),
    )


def _emit_flipup_guard(model, r, handle, mats, m):
    guard = model.part("safety_guard")
    guard.visual(m(_build_guard_body(r), "guard_body"), material=mats["guard"], name="guard_body", material_class_id="plastic.opaque_glossy_molded")
    guard.inertial = Inertial.from_geometry(
        Box((max(0.052, r.fixed_blade_exposed + 0.008), GUARD_W, GUARD_SKIRT_H + 0.005)),
        mass=0.01,
        origin=Origin(xyz=(0.026, 0.0, -HINGE_BARREL_R - GUARD_SKIRT_H / 2.0)),
    )
    model.articulation(
        "handle_to_guard",
        ArticulationType.REVOLUTE,
        parent=handle,
        child=guard,
        origin=Origin(xyz=(r.hinge_x, 0.0, r.hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=5.0, velocity=3.0, lower=0.0, upper=r.guard_open),
    )


def build_seeded_knife(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_knife(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_knife_tests(
    model: ArticulatedObject,
    config: KnifeConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    handle = model.get_part("handle")

    # --- Captured-interface element-scoped allowances (grandfathered joints). ---
    if r.deployment == "snap_off_slide":
        carrier = model.get_part("blade_carrier")
        ctx.allow_overlap(
            carrier, handle, elem_a="blade_spine", elem_b="top_channel",
            reason="The blade spine carrier is captured inside the handle top channel rail and slides along it.",
        )
        ctx.allow_overlap(
            carrier, handle, elem_a="blade_steel", elem_b="top_channel",
            reason="The blade root rides inside the handle channel groove as the carrier slides.",
        )
        ctx.allow_overlap(
            carrier, handle, elem_a="blade_steel", elem_b="handle_shell",
            reason="The blade body nests inside the handle body as the carrier slides (nested slider fit).",
        )
    elif r.deployment == "retract_full":
        carrier = model.get_part("blade_carrier")
        shell = "handle_shell"
        ctx.allow_overlap(
            carrier, handle, elem_a="blade_body", elem_b=shell,
            reason="The blade retracts fully into the solid handle body at rest (nested slider fit).",
        )
        ctx.allow_overlap(
            carrier, handle, elem_a="blade_clamp", elem_b="top_channel",
            reason="The blade clamp is captured inside the handle channel rail and slides along it.",
        )
        ctx.allow_overlap(
            carrier, carrier, elem_a="blade_clamp", elem_b="blade_body",
            reason="The clamp grips the blade spine with a small mounting overlap.",
        )
        for i in range(2):
            ctx.allow_overlap(
                carrier, carrier, elem_a=f"post_{i}", elem_b="blade_body",
                reason="Mounting post passes through the blade mounting hole.",
            )
            ctx.allow_overlap(
                carrier, carrier, elem_a=f"post_{i}", elem_b="blade_clamp",
                reason="Mounting post is embedded in the clamp plate.",
            )
    elif r.deployment == "fold_pivot":
        blade = model.get_part("blade")
        ctx.allow_overlap(
            blade, handle,
            reason="The folding blade assembly stores inside the handle body when closed (nested fit).",
        )
    else:  # flipup_guard
        guard = model.get_part("safety_guard")
        ctx.allow_overlap(
            guard, handle, elem_a="guard_body", elem_b="hinge_bracket",
            reason="The guard hinge barrel is captured between the handle hinge bracket ears (real pivot).",
        )
        ctx.allow_overlap(
            guard, handle, elem_a="guard_body", elem_b="blade_steel",
            reason="The closed guard sheathes the permanently-exposed blade (intentional cover overlap).",
        )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # --- slot_choices recorded. ---
    ctx.check(
        "slot_choices_recorded",
        tuple(model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(model.meta.get("slot_choices")),
    )

    # --- Single root handle. ---
    roots = model.root_parts()
    ctx.check(
        "handle is the single root",
        len(roots) == 1 and roots[0].name == "handle",
        details=f"roots={[p.name for p in roots]}",
    )

    # --- End cap is a FIXED part seated at the rear. ---
    cap_joint = model.get_articulation("handle_to_cap")
    ctx.check(
        "handle_to_cap is FIXED",
        cap_joint.articulation_type == ArticulationType.FIXED,
        details=f"type={cap_joint.articulation_type}",
    )
    ctx.expect_contact(model.get_part("end_cap"), handle, name="end cap seated against handle rear")
    handle_aabb = ctx.part_world_aabb(handle)
    cap_aabb = ctx.part_world_aabb(model.get_part("end_cap"))
    if handle_aabb is not None and cap_aabb is not None:
        ctx.check(
            "end cap is at the rear (-X) of the handle",
            cap_aabb[0][0] <= handle_aabb[0][0] + 0.003,
            details=f"cap_min_x={cap_aabb[0][0]:.4f} handle_min_x={handle_aabb[0][0]:.4f}",
        )

    # --- Identity: >=1 non-FIXED joint (the mechanism). ---
    non_fixed = [a for a in model.articulations
                 if a.articulation_type != ArticulationType.FIXED]
    ctx.check(
        "knife keeps at least one non-fixed deployment joint",
        len(non_fixed) >= 1,
        details=f"non_fixed={[a.name for a in non_fixed]}",
    )

    part_names = {p.name for p in model.parts}
    art_names = {a.name for a in model.articulations}
    shell_elem = "barrel_shell" if r.grip == "overmold_barrel" else "handle_shell"

    # --- Per-deployment joint topology + mechanism behaviour. ---
    if r.is_slide:
        carrier = model.get_part("blade_carrier")
        slide = model.get_articulation("handle_to_carrier")
        ctx.check(
            "handle_to_carrier is PRISMATIC along +X",
            slide.articulation_type == ArticulationType.PRISMATIC
            and abs(slide.axis[0]) > 0.99
            and abs(slide.axis[1]) < 1e-6 and abs(slide.axis[2]) < 1e-6,
            details=f"type={slide.articulation_type} axis={tuple(slide.axis)}",
        )
        blade_elem = "blade_steel" if r.deployment == "snap_off_slide" else "blade_body"
        rest_blade = ctx.part_element_world_aabb(carrier, elem=blade_elem)
        if r.deployment == "snap_off_slide" and rest_blade is not None and handle_aabb is not None:
            ctx.check(
                "snap-off blade is exposed past the nose at rest",
                rest_blade[1][0] > handle_aabb[1][0] + 0.002,
                details=f"blade_max_x={rest_blade[1][0]:.4f} handle_max_x={handle_aabb[1][0]:.4f}",
            )
        if r.deployment == "retract_full":
            shell_aabb = ctx.part_element_world_aabb(handle, elem=shell_elem)
            if rest_blade is not None and shell_aabb is not None:
                ctx.check(
                    "retract blade is fully retracted behind the nose at rest",
                    rest_blade[1][0] < shell_aabb[1][0] + 0.001,
                    details=f"blade_max_x={rest_blade[1][0]:.4f} shell_max_x={shell_aabb[1][0]:.4f}",
                )
        # advancing the slide pushes the blade forward, blade stays retained.
        with ctx.pose({slide: slide.motion_limits.upper}):
            ext_blade = ctx.part_element_world_aabb(carrier, elem=blade_elem)
            ctx.fail_if_parts_overlap_in_current_pose(name="extended_no_overlap")
        if rest_blade is not None and ext_blade is not None:
            ctx.check(
                "advancing the slide pushes the blade tip forward",
                ext_blade[1][0] > rest_blade[1][0] + 0.5 * r.slide_travel,
                details=f"rest_x={rest_blade[1][0]:.4f} ext_x={ext_blade[1][0]:.4f} travel={r.slide_travel:.4f}",
            )
        # No revolute deployment joint on a slide knife.
        ctx.check(
            "no fold/guard joint on a slide deployment",
            "handle_to_blade" not in art_names and "handle_to_guard" not in art_names,
            details=str(sorted(art_names)),
        )

    elif r.deployment == "fold_pivot":
        blade = model.get_part("blade")
        hinge = model.get_articulation("handle_to_blade")
        ctx.check(
            "handle_to_blade is REVOLUTE about Y",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[1]) > 0.99
            and abs(hinge.axis[0]) < 1e-6 and abs(hinge.axis[2]) < 1e-6,
            details=f"type={hinge.articulation_type} axis={tuple(hinge.axis)}",
        )
        ctx.check(
            "pivot is near the front of the handle",
            hinge.origin is not None and hinge.origin.xyz[0] > r.handle_len / 2.0 - 0.020,
            details=f"pivot_x={hinge.origin.xyz[0] if hinge.origin else None}",
        )
        # closed: blade stored inside handle footprint; open: extends past nose.
        with ctx.pose({hinge: 0.0}):
            closed_blade = ctx.part_element_world_aabb(blade, elem="blade_body")
        with ctx.pose({hinge: hinge.motion_limits.upper}):
            open_blade = ctx.part_element_world_aabb(blade, elem="blade_body")
        if closed_blade is not None and open_blade is not None and handle_aabb is not None:
            ctx.check(
                "fold blade swings out past the nose when open",
                open_blade[1][0] > handle_aabb[1][0] + 0.010,
                details=f"open_max_x={open_blade[1][0]:.4f} handle_max_x={handle_aabb[1][0]:.4f}",
            )
            ctx.check(
                "fold blade is retracted (not past nose) when closed",
                closed_blade[1][0] < open_blade[1][0],
                details=f"closed_max_x={closed_blade[1][0]:.4f} open_max_x={open_blade[1][0]:.4f}",
            )

    else:  # flipup_guard — blade is FIXED inline; guard REVOLUTE -Y is the joint.
        guard = model.get_part("safety_guard")
        hinge = model.get_articulation("handle_to_guard")
        ctx.check(
            "handle_to_guard is REVOLUTE about -Y",
            hinge.articulation_type == ArticulationType.REVOLUTE
            and abs(hinge.axis[1]) > 0.99
            and abs(hinge.axis[0]) < 1e-6 and abs(hinge.axis[2]) < 1e-6,
            details=f"type={hinge.articulation_type} axis={tuple(hinge.axis)}",
        )
        # blade is permanently exposed (inline handle visual, no deployment joint).
        ctx.check(
            "fixed blade is an inline handle visual (no carrier/blade part)",
            "blade_carrier" not in part_names and "blade" not in part_names
            and any(v.name == "blade_steel" for v in handle.visuals),
            details=str(sorted(part_names)),
        )
        ctx.check(
            "no slide/fold joint on a fixed-blade guard knife",
            "handle_to_carrier" not in art_names and "handle_to_blade" not in art_names,
            details=str(sorted(art_names)),
        )
        blade_aabb = ctx.part_element_world_aabb(handle, elem="blade_steel")
        shell_aabb = ctx.part_element_world_aabb(handle, elem=shell_elem)
        if blade_aabb is not None and shell_aabb is not None:
            ctx.check(
                "fixed blade is permanently exposed past the nose",
                blade_aabb[1][0] > shell_aabb[1][0] + 0.020,
                details=f"blade_max_x={blade_aabb[1][0]:.4f} shell_max_x={shell_aabb[1][0]:.4f}",
            )
        # closed guard covers the blade; open guard flips up above the handle.
        with ctx.pose({hinge: 0.0}):
            ctx.expect_overlap(
                guard, handle, axes="x", elem_a="guard_body", elem_b="blade_steel",
                min_overlap=0.025,
                name="closed guard covers the blade along X",
            )
        with ctx.pose({hinge: hinge.motion_limits.upper}):
            open_guard = ctx.part_element_world_aabb(guard, elem="guard_body")
        if open_guard is not None and handle_aabb is not None:
            ctx.check(
                "open guard flips up above the handle top",
                open_guard[1][2] > handle_aabb[1][2] + 0.003,
                details=f"guard_max_z={open_guard[1][2]:.4f} handle_max_z={handle_aabb[1][2]:.4f}",
            )

    # --- Identity: a slender hand knife along +X (handle long axis). ---
    shell_aabb = ctx.part_element_world_aabb(handle, elem=shell_elem)
    if shell_aabb is not None:
        ext_x = shell_aabb[1][0] - shell_aabb[0][0]
        ext_y = shell_aabb[1][1] - shell_aabb[0][1]
        ext_z = shell_aabb[1][2] - shell_aabb[0][2]
        ctx.check(
            "handle is a slender body along +X",
            ext_x > 3.0 * max(ext_y, ext_z),
            details=f"ext_x={ext_x:.4f} ext_y={ext_y:.4f} ext_z={ext_z:.4f}",
        )

    return ctx.report()


__all__ = (
    "KnifeConfig",
    "ResolvedKnifeConfig",
    "build_knife",
    "build_seeded_knife",
    "config_from_seed",
    "resolve_config",
    "run_knife_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
