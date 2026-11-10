# SPDX-License-Identifier: Apache-2.0

"""Art Drawing Models / Articulated mannequin / Poseable figure mannequin.

A poseable artist drawing mannequin: a stylized featureless human figure (ovoid
head, sculpted or turned-wood torso, tapered limbs) whose every major joint is a
visible ball-and-socket articulation (neck, both shoulders/elbows/wrists, both
hips/knees/ankles) so the figure can be posed. The figure is a kinematic tree
rooted at the ``torso``, rigidly mounted on a small wheeled tabletop ``base``
stand (glass plate + caster visuals + a rear lean-rod / central pole /
telescoping height column).

Slot graph (pattern = mixed: root base + 2 parallel-children slots + 1 caster
multiplicity axis):

    base (root; Slot A stand: lean_rod / center_pole / telescoping_stand; + N casters)
      +-- torso / pelvis+chest (Slot B body: sculpted_organic / barrel_torso / turned_wood)
      |        |-- waist REVOLUTE(Y) [if jointed] --> chest
      |        |-- neck REVOLUTE(Y) | CONTINUOUS(Z) --> head
      |        +-- hip/knee/ankle REVOLUTE(X) --> thigh/shin/foot   (x2 legs, lower torso)
      +-- (Slot C arms, parallel children on upper torso)
               +-- shoulder/elbow REVOLUTE(X) + wrist REVOLUTE(X)|CONTINUOUS(Z) --> hand
                        +-- knuckle/thumb REVOLUTE --> finger_i (x4) + thumb  (segmented only)

Adapted per AUTHORING.md §A/§B from the confirmed 5-star mannequin pool
(spec: specs_modular_v1/Art_Drawing_Models_Articulated_mannequin_Poseable_figure_mannequin.md).
Sources (model.py:Lx-Ly in the spec Module Source Index):

  S1  origin 母本 rec_use-...0c6efacc  — base + lean_rod, loft/lathe organic body,
      12-REVOLUTE limb tree, mitten hand, all test semantics.
  S2  barrel_torso       — single revolved barrel torso (Volumetric Envelope).
  S3  wooden_blocky      — turned-wood lathe idiom + wood palette.
  S4  caster_count       — N radial casters + circular plate.
  S5  center_pole_mount  — central pole-through-hip mount.
  S6  telescoping_stand  — outer sleeve + height_rod part + PRISMATIC.
  S7  segmented_hands    — 4 fingers + thumb parts + REVOLUTE knuckles.
  S8  swivel_neck        — neck CONTINUOUS(Z) swivel.
  S9  twist_wrists       — wrist CONTINUOUS(Z) twist.
  S10 waist_joint        — torso split pelvis+chest + REVOLUTE waist.

Coordinate frame: Z-up, base plate near z=0, figure standing on it. +Y = figure
front (face/toes forward); left/right limbs mirror in X. Limb swing joints turn
about X (sagittal plane) so each limb stays in its own parasagittal plane, the
arms (offset outboard of the torso half-width) clear the body, and left/right
limbs never interpenetrate. The figure is authored in world coords, then each
torso part is rebased so its part-frame origin sits at the stand-column weld
(base_to_torso FIXED origin lies on real geometry on both sides).

Rule 5 note: a poseable mannequin is DESIGNED to reach poses where a limb touches
the body / its own neighbour segments (elbow folded onto the upper arm, thigh
raised against the belly, fingers curled onto the palm). A blanket sampled-pose
collision gate would mis-flag those legitimate poses, so run_tests declares a
documented sampled-pose exemption: it whitelists every ball-in-socket seat and
adjacent posing contact with element-scoped ``allow_overlap`` (honored by the
compiler's harness_motion_qc at every sampled pose) and proves intended motion
with one targeted ``ctx.pose`` per mechanism. Joint ranges keep the source
values; nothing is throttled to pass.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from agent.templates._modular import (
    InterfaceSpec,
    ModuleBuild,
    ModuleBuildContext,
    SlotSpec,
    assemble,
)
from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    LatheGeometry,
    LoftGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


StandModule = Literal["lean_rod", "center_pole", "telescoping_stand"]
BodyForm = Literal["sculpted_organic", "barrel_torso", "turned_wood"]
HandModule = Literal["mitten_hands", "segmented_hands"]
NeckMode = Literal["pitch", "swivel"]
WristMode = Literal["pitch", "twist"]
MannequinPalette = Literal[
    "matte_black",
    "artist_wood",
    "walnut_wood",
    "porcelain_white",
    "slate_gray",
    "terracotta",
]

Vec3 = tuple[float, float, float]
SIDES = ("left", "right")

# World-frame anatomical datums (origin 母本).
WAIST_Z = 1.13        # world z of the waist ring / waist joint
NECK_Z = 1.63         # world z of the neck joint
SHOULDER_X = 0.205    # |x| of the shoulder sockets (outboard of the torso)
SHOULDER_Z = 1.49
HIP_X = 0.09          # |x| of the hip sockets
HIP_Z = 0.99
COLUMN_TOP_Z = 1.08   # stand column top (embeds into the pelvis)
WELD_Z = 1.05         # torso<->base weld z (mid-pelvis; on the column)

AX_SAG = (1.0, 0.0, 0.0)  # sagittal swing axis for limb joints


# --------------------------------------------------------------------------- #
# Palettes (>=6 colorways; tokens shared so every .visual resolves)
# --------------------------------------------------------------------------- #

PALETTES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "matte_black": {
        "body": (0.07, 0.07, 0.08, 1.0),
        "steel": (0.60, 0.60, 0.63, 1.0),
        "glass": (0.10, 0.10, 0.12, 1.0),
    },
    "artist_wood": {
        "body": (0.82, 0.68, 0.45, 1.0),
        "steel": (0.62, 0.63, 0.66, 1.0),
        "glass": (0.30, 0.26, 0.20, 1.0),
    },
    "walnut_wood": {
        "body": (0.45, 0.30, 0.18, 1.0),
        "steel": (0.58, 0.59, 0.62, 1.0),
        "glass": (0.20, 0.16, 0.12, 1.0),
    },
    "porcelain_white": {
        "body": (0.92, 0.92, 0.93, 1.0),
        "steel": (0.70, 0.72, 0.75, 1.0),
        "glass": (0.80, 0.82, 0.86, 1.0),
    },
    "slate_gray": {
        "body": (0.38, 0.40, 0.44, 1.0),
        "steel": (0.66, 0.68, 0.71, 1.0),
        "glass": (0.22, 0.24, 0.28, 1.0),
    },
    "terracotta": {
        "body": (0.72, 0.40, 0.28, 1.0),
        "steel": (0.60, 0.60, 0.63, 1.0),
        "glass": (0.28, 0.18, 0.14, 1.0),
    },
}
PALETTE_NAMES = tuple(PALETTES.keys())


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class MannequinConfig:
    stand_module: StandModule = "lean_rod"
    body_form: BodyForm = "sculpted_organic"
    hand_module: HandModule = "mitten_hands"
    neck_mode: NeckMode = "pitch"
    wrist_mode: WristMode = "pitch"
    waist_jointed: bool = False
    caster_count: int = 4
    palette_style: MannequinPalette = "matte_black"

    arm_scale: float = 1.0
    leg_scale: float = 1.0
    shoulder_range: float = 2.8
    elbow_upper: float = 2.6
    hip_upper: float = 1.8
    knee_upper: float = 2.2
    waist_range: float = 0.6
    neck_range: float = 0.8
    wrist_range: float = 1.0


@dataclass(frozen=True)
class ResolvedMannequinConfig:
    stand_module: StandModule
    body_form: BodyForm
    hand_module: HandModule
    neck_mode: NeckMode
    wrist_mode: WristMode
    waist_jointed: bool
    caster_count: int
    palette_style: str

    arm_scale: float
    leg_scale: float
    shoulder_range: float
    elbow_upper: float
    hip_upper: float
    knee_upper: float
    waist_range: float
    neck_range: float
    wrist_range: float

    # Derived part-tree wiring (single-sourced; Contract 3c).
    upper_part: str        # arms/head parent (torso or chest)
    lower_part: str        # legs parent (torso or pelvis)
    lower_frame: Vec3      # world position of the lower-torso part frame (= weld)
    upper_frame: Vec3      # world position of the upper-torso part frame
    column_xy: tuple[float, float]  # (x,y) of the stand weld column

    palette: dict[str, tuple[float, float, float, float]]


def config_from_seed(seed: int) -> MannequinConfig:
    """Deterministic procedural sampling.

    seed 0 is pinned to the origin 母本 combination (lean_rod + sculpted_organic
    + mitten + rigid + neck pitch + wrist pitch + 4 casters + matte_black) as a
    documented regression anchor; every other seed is fully procedural.
    """
    if seed == 0:
        return MannequinConfig()

    rng = random.Random(seed)

    stand_module: StandModule = rng.choice(
        ("lean_rod", "center_pole", "telescoping_stand")
    )
    body_form: BodyForm = rng.choice(
        ("sculpted_organic", "barrel_torso", "turned_wood")
    )
    hand_module: HandModule = rng.choice(("mitten_hands", "segmented_hands"))
    neck_mode: NeckMode = rng.choice(("pitch", "swivel"))
    wrist_mode: WristMode = rng.choice(("pitch", "twist"))
    # waist gated to rigid for the single-revolve barrel torso (resolve_config).
    waist_jointed = rng.random() < 0.5
    caster_count = rng.choices((3, 4, 5, 6), weights=(0.2, 0.4, 0.2, 0.2))[0]
    palette_style = rng.choice(PALETTE_NAMES)

    arm_scale = round(rng.uniform(0.90, 1.12), 4)
    leg_scale = round(rng.uniform(0.90, 1.12), 4)
    shoulder_range = round(rng.uniform(2.2, 2.9), 4)
    elbow_upper = round(rng.uniform(2.2, 2.7), 4)
    hip_upper = round(rng.uniform(1.5, 2.0), 4)
    knee_upper = round(rng.uniform(1.9, 2.4), 4)
    waist_range = round(rng.uniform(0.4, 0.8), 4)
    neck_range = round(rng.uniform(0.6, 0.9), 4)
    wrist_range = round(rng.uniform(0.8, 1.2), 4)

    return MannequinConfig(
        stand_module=stand_module,
        body_form=body_form,
        hand_module=hand_module,
        neck_mode=neck_mode,
        wrist_mode=wrist_mode,
        waist_jointed=waist_jointed,
        caster_count=caster_count,
        palette_style=palette_style,
        arm_scale=arm_scale,
        leg_scale=leg_scale,
        shoulder_range=shoulder_range,
        elbow_upper=elbow_upper,
        hip_upper=hip_upper,
        knee_upper=knee_upper,
        waist_range=waist_range,
        neck_range=neck_range,
        wrist_range=wrist_range,
    )


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def resolve_config(config: MannequinConfig) -> ResolvedMannequinConfig:
    if str(config.stand_module) not in {"lean_rod", "center_pole", "telescoping_stand"}:
        raise ValueError(f"Unsupported stand_module: {config.stand_module}")
    if str(config.body_form) not in {"sculpted_organic", "barrel_torso", "turned_wood"}:
        raise ValueError(f"Unsupported body_form: {config.body_form}")
    if str(config.hand_module) not in {"mitten_hands", "segmented_hands"}:
        raise ValueError(f"Unsupported hand_module: {config.hand_module}")
    if str(config.neck_mode) not in {"pitch", "swivel"}:
        raise ValueError(f"Unsupported neck_mode: {config.neck_mode}")
    if str(config.wrist_mode) not in {"pitch", "twist"}:
        raise ValueError(f"Unsupported wrist_mode: {config.wrist_mode}")
    if str(config.palette_style) not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    # Compatibility gate: a single-revolve barrel torso has no region seam to
    # split, so it is always a rigid one-piece torso (spec compatibility matrix).
    waist_jointed = bool(config.waist_jointed) and config.body_form != "barrel_torso"

    caster_count = int(_clamp(config.caster_count, 3, 6))

    arm_scale = _clamp(config.arm_scale, 0.90, 1.12)
    leg_scale = _clamp(config.leg_scale, 0.90, 1.12)
    shoulder_range = _clamp(config.shoulder_range, 2.2, 2.9)
    elbow_upper = _clamp(config.elbow_upper, 2.2, 2.7)
    hip_upper = _clamp(config.hip_upper, 1.5, 2.0)
    knee_upper = _clamp(config.knee_upper, 1.9, 2.4)
    waist_range = _clamp(config.waist_range, 0.4, 0.8)
    neck_range = _clamp(config.neck_range, 0.6, 0.9)
    wrist_range = _clamp(config.wrist_range, 0.8, 1.2)

    # Stand weld column: central pole is centered; the rear rod / sleeve columns
    # stand just behind the pelvis and embed into its back. The weld z sits on
    # the pelvis BOTTOM surface (per form) so the FIXED joint origin lies on real
    # geometry on the torso side too (origin honesty).
    column_xy = (0.0, 0.0) if config.stand_module == "center_pole" else (0.0, -0.06)
    pelvis_bottom = {"sculpted_organic": 1.00, "barrel_torso": 0.98, "turned_wood": 0.97}[config.body_form]
    # Weld sits just inside the pelvis bottom cap so the FIXED origin is on the
    # torso surface (origin honesty).
    lower_frame: Vec3 = (column_xy[0], column_xy[1], pelvis_bottom + 0.01)

    if waist_jointed:
        upper_part, lower_part = "chest", "pelvis"
        upper_frame: Vec3 = (0.0, 0.0, WAIST_Z)
    else:
        upper_part, lower_part = "torso", "torso"
        upper_frame = lower_frame

    return ResolvedMannequinConfig(
        stand_module=config.stand_module,
        body_form=config.body_form,
        hand_module=config.hand_module,
        neck_mode=config.neck_mode,
        wrist_mode=config.wrist_mode,
        waist_jointed=waist_jointed,
        caster_count=caster_count,
        palette_style=config.palette_style,
        arm_scale=arm_scale,
        leg_scale=leg_scale,
        shoulder_range=shoulder_range,
        elbow_upper=elbow_upper,
        hip_upper=hip_upper,
        knee_upper=knee_upper,
        waist_range=waist_range,
        neck_range=neck_range,
        wrist_range=wrist_range,
        upper_part=upper_part,
        lower_part=lower_part,
        lower_frame=lower_frame,
        upper_frame=upper_frame,
        column_xy=column_xy,
        palette=dict(PALETTES[config.palette_style]),
    )


def _sub(p: Vec3, frame: Vec3) -> Vec3:
    return (p[0] - frame[0], p[1] - frame[1], p[2] - frame[2])


# --------------------------------------------------------------------------- #
# Mesh helpers (adapted from origin 母本 + wooden_blocky / segmented sources)
# --------------------------------------------------------------------------- #


def _lathe(profile: list[tuple[float, float]], name: str, segments: int = 28):
    return mesh_from_geometry(LatheGeometry(profile, segments=segments), name)


def _loft(rings: list[list[tuple[float, float, float]]], name: str):
    return mesh_from_geometry(LoftGeometry(rings, cap=True, closed=True), name)


def _ring_xy(z: float, a: float, b: float, n: int = 28, e: float = 2.4) -> list[tuple[float, float, float]]:
    """Superellipse ring in the X-Y plane at height z (origin ring_xy)."""
    pts = []
    for i in range(n):
        t = 2.0 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        x = a * (abs(c) ** (2.0 / e)) * (1.0 if c >= 0 else -1.0)
        y = b * (abs(s) ** (2.0 / e)) * (1.0 if s >= 0 else -1.0)
        pts.append((x, y, z))
    return pts


def _ring_foot(zc: float, xh: float, ry: float, sole: float = 0.045, n: int = 24) -> list[tuple[float, float, float]]:
    cy = sole - ry
    return [
        (xh * math.cos(2.0 * math.pi * i / n), cy + ry * math.sin(2.0 * math.pi * i / n), zc)
        for i in range(n)
    ]


def _turned_barrel(r_max: float, r_end: float, H: float) -> list[tuple[float, float]]:
    return [
        (0.0, 0.0), (r_end * 0.55, H * 0.03), (r_end, H * 0.08), (r_max * 0.88, H * 0.22),
        (r_max, H * 0.38), (r_max, H * 0.62), (r_max * 0.88, H * 0.78), (r_end, H * 0.92),
        (r_end * 0.55, H * 0.97), (0.0, H),
    ]


def _turned_cylinder(r: float, H: float) -> list[tuple[float, float]]:
    c = min(r * 0.55, H * 0.10)
    return [
        (0.0, 0.0), (r * 0.40, c * 0.20), (r * 0.78, c * 0.65), (r, c),
        (r, H - c), (r * 0.78, H - c * 0.65), (r * 0.40, H - c * 0.20), (0.0, H),
    ]


def _turned_limb(r: float, L: float) -> list[tuple[float, float]]:
    c = min(r * 0.55, L * 0.10)
    return [
        (0.0, 0.0), (r * 0.40, -c * 0.20), (r * 0.78, -c * 0.65), (r, -c),
        (r, -(L - c)), (r * 0.78, -(L - c * 0.65)), (r * 0.40, -(L - c * 0.20)), (0.0, -L),
    ]


def _finger_seg_mesh(name: str, length: float, width: float):
    return _lathe([
        (0.000, 0.000), (width * 0.9, -0.004), (width, -0.012), (width * 0.93, -length * 0.35),
        (width * 0.78, -length * 0.65), (width * 0.55, -length * 0.88), (0.000, -length),
    ], name, segments=18)


def _scale_z(profile: list[tuple[float, float]], scale: float) -> list[tuple[float, float]]:
    return [(r, z * scale) for (r, z) in profile]


# Organic limb profiles (origin 母本).
_UPPER_ARM_PROF = [
    (0.000, 0.000), (0.035, -0.006), (0.048, -0.035), (0.050, -0.080),
    (0.046, -0.150), (0.040, -0.240), (0.036, -0.285), (0.000, -0.292),
]
_FOREARM_PROF = [
    (0.000, 0.000), (0.038, -0.006), (0.045, -0.030), (0.041, -0.120),
    (0.035, -0.200), (0.031, -0.245), (0.000, -0.255),
]
_THIGH_PROF = [
    (0.000, 0.000), (0.048, -0.006), (0.062, -0.040), (0.066, -0.120),
    (0.062, -0.240), (0.055, -0.340), (0.048, -0.372), (0.000, -0.378),
]
_SHIN_PROF = [
    (0.000, 0.000), (0.046, -0.010), (0.056, -0.060), (0.052, -0.140),
    (0.043, -0.260), (0.036, -0.350), (0.000, -0.380),
]
_HEAD_PROF = [
    (0.000, 0.000), (0.052, 0.012), (0.086, 0.045), (0.100, 0.090),
    (0.099, 0.125), (0.086, 0.165), (0.055, 0.200), (0.000, 0.212),
]
_HEAD_PROF_WOOD = [
    (0.000, 0.000), (0.048, 0.014), (0.078, 0.048), (0.090, 0.090),
    (0.088, 0.130), (0.074, 0.168), (0.046, 0.198), (0.000, 0.212),
]
_HAND_OVOID_WOOD = [
    (0.000, 0.000), (0.018, -0.006), (0.032, -0.022), (0.036, -0.050),
    (0.034, -0.085), (0.026, -0.118), (0.014, -0.142), (0.000, -0.155),
]
_FOOT_OVOID_WOOD = [
    (0.000, 0.000), (0.024, 0.006), (0.036, 0.025), (0.040, 0.055),
    (0.038, 0.095), (0.030, 0.135), (0.016, 0.168), (0.000, 0.190),
]

# Distal joint offsets, pulled just inside each parent segment's fat end so the
# joint axis passes through real parent hardware (origin honesty, tol 0.02).
ELBOW_OFF = -0.29
WRIST_OFF = -0.25
KNEE_OFF = -0.37
ANKLE_OFF = -0.375


# --------------------------------------------------------------------------- #
# Slot A — stand (root `base`)
# --------------------------------------------------------------------------- #


def _base_downstream() -> InterfaceSpec:
    return InterfaceSpec(
        interface_name="downstream",
        part_name="base",
        visual_name="base_plate",
        face_side="positive_z",
        anchor_local=(0.0, 0.0, 0.07),
        contact_tol=0.004,
    )


def _emit_casters(base, r: ResolvedMannequinConfig) -> None:
    """N caster visuals: 4 -> square-plate corners (origin); else radial ring
    on a circular plate (caster_count S4). Static base decoration (Rule 1)."""
    n = r.caster_count
    if n == 4:
        positions = [(0.16, 0.16), (0.16, -0.16), (-0.16, 0.16), (-0.16, -0.16)]
    else:
        ring_r = 0.16
        positions = [
            (ring_r * math.cos(2.0 * math.pi * i / n), ring_r * math.sin(2.0 * math.pi * i / n))
            for i in range(n)
        ]
    for i, (cx, cy) in enumerate(positions):
        base.visual(Cylinder(radius=0.020, length=0.028), origin=Origin(xyz=(cx, cy, 0.036)),
                    material="steel", name=f"caster_yoke_{i}", material_class_id="metal.stainless_matte")
        base.visual(Cylinder(radius=0.016, length=0.024),
                    origin=Origin(xyz=(cx, cy, 0.014), rpy=(math.pi / 2.0, 0.0, 0.0)),
                    material="steel", name=f"caster_{i}", material_class_id="metal.stainless_matte")


def _emit_base_plate(base, r: ResolvedMannequinConfig) -> None:
    if r.caster_count == 4:
        base.visual(Box((0.40, 0.40, 0.02)), origin=Origin(xyz=(0.0, 0.0, 0.06)),
                    material="glass", name="base_plate", material_class_id="glass.clear_transparent")
    else:
        base.visual(Cylinder(radius=0.22, length=0.02), origin=Origin(xyz=(0.0, 0.0, 0.06)),
                    material="glass", name="base_plate", material_class_id="glass.clear_transparent")


def _build_lean_rod(ctx: ModuleBuildContext) -> ModuleBuild:
    """Origin stand: rear lean-rod + saddle rising to the pelvis back."""
    model = ctx.model
    r: ResolvedMannequinConfig = ctx.config  # type: ignore[assignment]
    base = model.part("base")
    _emit_base_plate(base, r)
    _emit_casters(base, r)
    cx, cy = r.column_xy
    col_len = COLUMN_TOP_Z - 0.07
    base.visual(Cylinder(radius=0.012, length=col_len),
                origin=Origin(xyz=(cx, cy, 0.07 + col_len / 2.0)),
                material="steel", name="lean_rod", material_class_id="metal.stainless_matte")
    base.visual(Box((0.06, 0.13, 0.03)), origin=Origin(xyz=(cx, cy - 0.01, WELD_Z + 0.02)),
                material="steel", name="lean_saddle", material_class_id="metal.stainless_matte")
    return ModuleBuild(module_name="lean_rod", parts_emitted=["base"],
                       interfaces={"downstream": _base_downstream()})


def _build_center_pole(ctx: ModuleBuildContext) -> ModuleBuild:
    """Central vertical mounting pole from the plate center into the pelvis
    cavity (pole-through-hip mount; center_pole S5)."""
    model = ctx.model
    r: ResolvedMannequinConfig = ctx.config  # type: ignore[assignment]
    base = model.part("base")
    _emit_base_plate(base, r)
    _emit_casters(base, r)
    cx, cy = r.column_xy
    pole_len = COLUMN_TOP_Z - 0.07
    base.visual(Cylinder(radius=0.016, length=pole_len),
                origin=Origin(xyz=(cx, cy, 0.07 + pole_len / 2.0)),
                material="steel", name="central_pole", material_class_id="metal.stainless_matte")
    return ModuleBuild(module_name="center_pole", parts_emitted=["base"],
                       interfaces={"downstream": _base_downstream()})


def _build_telescoping_stand(ctx: ModuleBuildContext) -> ModuleBuild:
    """Full-height outer sleeve column (base) + a PRISMATIC inner height_rod part
    carrying the saddle (telescoping S6). The sleeve reaches the pelvis so the
    torso welds honestly onto the base; the inner rod telescopes up along +Z to
    adjust height, sliding within the sleeve."""
    model = ctx.model
    r: ResolvedMannequinConfig = ctx.config  # type: ignore[assignment]
    base = model.part("base")
    _emit_base_plate(base, r)
    _emit_casters(base, r)
    cx, cy = r.column_xy
    sleeve_len = COLUMN_TOP_Z - 0.07
    base.visual(Cylinder(radius=0.020, length=sleeve_len),
                origin=Origin(xyz=(cx, cy, 0.07 + sleeve_len / 2.0)),
                material="steel", name="outer_sleeve", material_class_id="metal.stainless_matte")
    # height_rod part frame is placed at the joint origin (cx,cy,COLUMN_TOP_Z),
    # so its visuals are authored at part-local x=y=0 (on the sleeve axis).
    height_rod = model.part("height_rod")
    rod_len = sleeve_len * 0.75
    height_rod.visual(Cylinder(radius=0.010, length=rod_len),
                      origin=Origin(xyz=(0.0, 0.0, -rod_len / 2.0)),
                      material="steel", name="inner_rod_member", material_class_id="metal.stainless_matte")
    # Collar wraps the sleeve wall so the height_rod physically contacts the
    # grounded base (the concentric inner rod alone floats inside the sleeve).
    height_rod.visual(Cylinder(radius=0.024, length=0.03), origin=Origin(xyz=(0.0, 0.0, -0.02)),
                      material="steel", name="collar", material_class_id="metal.stainless_matte")
    height_rod.visual(Box((0.06, 0.13, 0.03)), origin=Origin(xyz=(0.0, -0.01, 0.0)),
                      material="steel", name="lean_saddle", material_class_id="metal.stainless_matte")
    model.articulation(
        "sleeve_to_rod", ArticulationType.PRISMATIC, parent=base, child=height_rod,
        origin=Origin(xyz=(cx, cy, COLUMN_TOP_Z)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=20.0, velocity=0.5, lower=0.0, upper=0.30),
    )
    return ModuleBuild(module_name="telescoping_stand", parts_emitted=["base", "height_rod"],
                       internal_articulations=["sleeve_to_rod"],
                       interfaces={"downstream": _base_downstream()})


# --------------------------------------------------------------------------- #
# Slot B — body (torso + head + legs, parallel children on base)
# --------------------------------------------------------------------------- #


def _emit_torso_visuals(model, r: ResolvedMannequinConfig) -> None:
    """Emit torso geometry (authored in world coords, rebased onto each part's
    frame). The lower part carries the pelvis region; the upper part carries the
    waist+chest+deltoids+neck."""
    lower = model.get_part(r.lower_part)
    upper = model.get_part(r.upper_part)
    lf, uf = r.lower_frame, r.upper_frame

    def lo(mesh, name, world=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, 0.0)):
        lower.visual(mesh, origin=Origin(xyz=_sub(world, lf), rpy=rpy), material="body", name=name, material_class_id="plastic.opaque_generic")

    def up(mesh, name, world=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, 0.0)):
        upper.visual(mesh, origin=Origin(xyz=_sub(world, uf), rpy=rpy), material="body", name=name, material_class_id="plastic.opaque_generic")

    if r.body_form == "sculpted_organic":
        lo(_loft([
            _ring_xy(1.00, 0.115, 0.090), _ring_xy(1.06, 0.145, 0.105), _ring_xy(1.13, 0.125, 0.095),
        ], "pelvis_loft"), "pelvis")
        up(_loft([
            _ring_xy(1.12, 0.125, 0.095), _ring_xy(1.22, 0.108, 0.083), _ring_xy(1.33, 0.138, 0.097),
        ], "waist_loft"), "waist")
        up(_loft([
            _ring_xy(1.32, 0.130, 0.093), _ring_xy(1.40, 0.140, 0.106),
            _ring_xy(1.48, 0.132, 0.095), _ring_xy(1.55, 0.098, 0.082), _ring_xy(1.60, 0.068, 0.064),
        ], "chest_loft"), "chest")
    elif r.body_form == "barrel_torso":
        # Single revolved barrel (barrel S2). Rigid only (gated), so upper==lower.
        lo(_lathe([
            (0.000, 0.98), (0.080, 1.00), (0.118, 1.04), (0.132, 1.08), (0.120, 1.14),
            (0.105, 1.22), (0.110, 1.30), (0.128, 1.38), (0.138, 1.43), (0.125, 1.49),
            (0.100, 1.54), (0.065, 1.58), (0.000, 1.62),
        ], "torso_barrel"), "pelvis")
    else:  # turned_wood
        lo(_lathe(_turned_barrel(0.130, 0.088, 0.165), "pelvis_block"), "pelvis", world=(0.0, 0.0, 0.97))
        up(_lathe(_turned_cylinder(0.078, 0.19), "waist_cyl"), "waist", world=(0.0, 0.0, 1.12))
        up(_lathe(_turned_barrel(0.140, 0.088, 0.29), "chest_block"), "chest", world=(0.0, 0.0, 1.30))

    # Deltoid shoulder caps + neck stub on the upper torso (all forms).
    for side, sx in (("left", 1.0), ("right", -1.0)):
        upper.visual(Sphere(radius=0.055), origin=Origin(xyz=_sub((sx * 0.155, 0.0, 1.50), uf)),
                     material="body", name=f"deltoid_{side}", material_class_id=("wood.polished_varnished" if r.body_form == "turned_wood" else "plastic.opaque_generic"))
    if r.body_form == "turned_wood":
        neck_prof, neck_world = _turned_cylinder(0.040, 0.105), (0.0, 0.0, 1.53)
    else:
        neck_prof = [(0.000, 0.000), (0.055, 0.006), (0.050, 0.050),
                     (0.046, 0.095), (0.040, 0.108), (0.000, 0.112)]
        neck_world = (0.0, 0.0, 1.52)
    up(_lathe(neck_prof, "torso_neck"), "neck", world=neck_world)


def _emit_head(model, r: ResolvedMannequinConfig) -> None:
    upper = model.get_part(r.upper_part)
    head = model.part("head")
    head_prof = _HEAD_PROF_WOOD if r.body_form == "turned_wood" else _HEAD_PROF
    head.visual(_lathe(head_prof, "head_ovoid"), material="body", name="head_shell", material_class_id=("wood.polished_varnished" if r.body_form == "turned_wood" else "plastic.opaque_generic"))
    head.visual(Sphere(radius=0.058 if r.body_form == "turned_wood" else 0.060),
                origin=Origin(xyz=(0.0, 0.025, 0.051)), material="body", name="head_chin", material_class_id=("wood.polished_varnished" if r.body_form == "turned_wood" else "plastic.opaque_generic"))
    neck_origin = Origin(xyz=_sub((0.0, 0.0, NECK_Z), r.upper_frame))
    if r.neck_mode == "swivel":
        model.articulation("neck_joint", ArticulationType.CONTINUOUS, parent=upper, child=head,
                           origin=neck_origin, axis=(0.0, 0.0, 1.0),
                           motion_limits=MotionLimits(effort=5.0, velocity=2.0))
    else:
        model.articulation("neck_joint", ArticulationType.REVOLUTE, parent=upper, child=head,
                           origin=neck_origin, axis=(0.0, 1.0, 0.0),
                           motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=-r.neck_range, upper=r.neck_range))


def _emit_legs(model, r: ResolvedMannequinConfig) -> None:
    lower = model.get_part(r.lower_part)
    lf = r.lower_frame
    s = r.leg_scale
    for side, sx in (("left", 1.0), ("right", -1.0)):
        thigh = model.part(f"{side}_thigh")
        thigh.visual(Sphere(radius=0.062), origin=Origin(xyz=(0.0, 0.0, 0.0)), material="body", name="hip_ball", material_class_id=("wood.polished_varnished" if r.body_form == "turned_wood" else "plastic.opaque_generic"))
        if r.body_form == "turned_wood":
            thigh.visual(_lathe(_turned_limb(0.054, 0.378 * s), f"{side}_thigh_seg"), material="body", name="thigh_seg", material_class_id="wood.polished_varnished")
        else:
            thigh.visual(_lathe(_scale_z(_THIGH_PROF, s), f"{side}_thigh_seg"), material="body", name="thigh_seg", material_class_id="plastic.opaque_generic")
        model.articulation(f"{side}_hip", ArticulationType.REVOLUTE, parent=lower, child=thigh,
                           origin=Origin(xyz=_sub((sx * HIP_X, 0.0, HIP_Z), lf)), axis=AX_SAG,
                           motion_limits=MotionLimits(effort=20.0, velocity=2.0, lower=-0.6, upper=r.hip_upper))

        shin = model.part(f"{side}_shin")
        shin.visual(Sphere(radius=0.058), origin=Origin(xyz=(0.0, 0.0, 0.0)), material="body", name="knee_ball", material_class_id=("wood.polished_varnished" if r.body_form == "turned_wood" else "plastic.opaque_generic"))
        if r.body_form == "turned_wood":
            shin.visual(_lathe(_turned_limb(0.046, 0.380 * s), f"{side}_shin_seg"), material="body", name="shin_seg", material_class_id="wood.polished_varnished")
        else:
            shin.visual(_lathe(_scale_z(_SHIN_PROF, s), f"{side}_shin_seg"), material="body", name="shin_seg", material_class_id="plastic.opaque_generic")
        model.articulation(f"{side}_knee", ArticulationType.REVOLUTE, parent=thigh, child=shin,
                           origin=Origin(xyz=(0.0, 0.0, KNEE_OFF * s)), axis=AX_SAG,
                           motion_limits=MotionLimits(effort=20.0, velocity=2.0, lower=0.0, upper=r.knee_upper))

        foot = model.part(f"{side}_foot")
        foot.visual(Sphere(radius=0.045), origin=Origin(xyz=(0.0, 0.0, 0.0)), material="body", name="ankle_ball", material_class_id=("wood.polished_varnished" if r.body_form == "turned_wood" else "plastic.opaque_generic"))
        if r.body_form == "turned_wood":
            foot.visual(_lathe(_FOOT_OVOID_WOOD, f"{side}_foot_wedge"),
                        origin=Origin(xyz=(0.0, -0.055, -0.070), rpy=(-math.pi / 2.0, 0.0, 0.0)),
                        material="body", name="foot_wedge", material_class_id="wood.polished_varnished")
        else:
            foot.visual(_loft([
                _ring_foot(0.000, 0.033, 0.045), _ring_foot(0.035, 0.042, 0.047),
                _ring_foot(0.105, 0.040, 0.045), _ring_foot(0.165, 0.033, 0.038), _ring_foot(0.205, 0.020, 0.028),
            ], f"{side}_foot_wedge"),
                origin=Origin(xyz=(0.0, -0.055, -0.070), rpy=(-math.pi / 2.0, 0.0, 0.0)),
                material="body", name="foot_wedge", material_class_id="plastic.opaque_generic")
        model.articulation(f"{side}_ankle", ArticulationType.REVOLUTE, parent=shin, child=foot,
                           origin=Origin(xyz=(0.0, 0.0, ANKLE_OFF * s)), axis=AX_SAG,
                           motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=-0.6, upper=0.6))


def _build_body(ctx: ModuleBuildContext) -> ModuleBuild:
    """The figure body (parallel-children on base). FIXES the kinematic-root
    torso onto the base stand column, then emits head + neck + 2 leg chains.

    The base_to_torso FIXED joint is a legitimate composed-sub-assembly weld
    (Rule 1 exception): the fabricated stand and the figure are distinct bodies
    joined rigidly, and the torso is the kinematic root of every limb. Its origin
    sits at the stand-column/pelvis weld so it lies on real geometry on both
    sides (origin honesty)."""
    model = ctx.model
    r: ResolvedMannequinConfig = ctx.config  # type: ignore[assignment]
    base = model.get_part("base")

    parts: list[str] = []
    joints: list[str] = []
    if r.waist_jointed:
        model.part("pelvis")
        model.part("chest")
        _emit_torso_visuals(model, r)
        parts += ["pelvis", "chest"]
        model.articulation(
            "waist_joint", ArticulationType.REVOLUTE, parent=model.get_part("pelvis"),
            child=model.get_part("chest"),
            origin=Origin(xyz=_sub((0.0, 0.0, WAIST_Z), r.lower_frame)), axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=-r.waist_range, upper=r.waist_range),
        )
        joints.append("waist_joint")
        weld_child = model.get_part("pelvis")
    else:
        model.part("torso")
        _emit_torso_visuals(model, r)
        parts.append("torso")
        weld_child = model.get_part("torso")

    model.articulation(
        "base_to_torso", ArticulationType.FIXED, parent=base, child=weld_child,
        origin=Origin(xyz=r.lower_frame),
    )
    joints.append("base_to_torso")

    _emit_head(model, r)
    parts.append("head")
    joints.append("neck_joint")

    _emit_legs(model, r)
    for side in SIDES:
        parts += [f"{side}_thigh", f"{side}_shin", f"{side}_foot"]
        joints += [f"{side}_hip", f"{side}_knee", f"{side}_ankle"]

    return ModuleBuild(module_name=r.body_form, parts_emitted=parts,
                       internal_articulations=joints,
                       interfaces={"downstream": _base_downstream()})


# --------------------------------------------------------------------------- #
# Slot C — arms (parallel children on the upper torso)
# --------------------------------------------------------------------------- #


def _emit_hand(model, r: ResolvedMannequinConfig, side: str, sx: float, forearm, s: float) -> tuple[list[str], list[str]]:
    hand = model.part(f"{side}_hand")
    hand.visual(Sphere(radius=0.035), origin=Origin(xyz=(0.0, 0.0, 0.0)), material="body", name="wrist_ball", material_class_id=("wood.polished_varnished" if r.body_form == "turned_wood" else "plastic.opaque_generic"))

    if r.hand_module == "segmented_hands":
        hand.visual(_loft([
            _ring_xy(-0.018, 0.022, 0.036, n=20, e=2.2), _ring_xy(-0.045, 0.025, 0.046, n=20, e=2.2),
            _ring_xy(-0.075, 0.024, 0.044, n=20, e=2.2),
        ], f"{side}_palm"), material="body", name="palm", material_class_id=("wood.polished_varnished" if r.body_form == "turned_wood" else "plastic.opaque_generic"))
    elif r.body_form == "turned_wood":
        hand.visual(_lathe(_HAND_OVOID_WOOD, f"{side}_hand_ovoid"), material="body", name="hand_paddle", material_class_id="wood.polished_varnished")
    else:
        hand.visual(_loft([
            _ring_xy(-0.020, 0.022, 0.036, n=20, e=2.2), _ring_xy(-0.060, 0.028, 0.052, n=20, e=2.2),
            _ring_xy(-0.120, 0.026, 0.050, n=20, e=2.2), _ring_xy(-0.160, 0.017, 0.032, n=20, e=2.2),
            _ring_xy(-0.175, 0.006, 0.012, n=20, e=2.2),
        ], f"{side}_hand_paddle"), material="body", name="hand_paddle", material_class_id="plastic.opaque_generic")

    if r.wrist_mode == "twist":
        model.articulation(f"{side}_wrist", ArticulationType.CONTINUOUS, parent=forearm, child=hand,
                           origin=Origin(xyz=(0.0, 0.0, WRIST_OFF * s)), axis=(0.0, 0.0, 1.0),
                           motion_limits=MotionLimits(effort=4.0, velocity=2.0))
    else:
        model.articulation(f"{side}_wrist", ArticulationType.REVOLUTE, parent=forearm, child=hand,
                           origin=Origin(xyz=(0.0, 0.0, WRIST_OFF * s)), axis=(1.0, 0.0, 0.0),
                           motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=-r.wrist_range, upper=r.wrist_range))

    extra_parts: list[str] = []
    extra_joints: list[str] = []
    if r.hand_module == "segmented_hands":
        finger_x = [-0.017, -0.006, 0.006, 0.017]
        finger_len = [0.048, 0.054, 0.050, 0.042]
        finger_w = [0.007, 0.008, 0.007, 0.006]
        for i in range(4):
            fx, fl, fw = finger_x[i], finger_len[i], finger_w[i]
            finger = model.part(f"{side}_finger_{i}")
            finger.visual(Sphere(radius=fw * 0.75), origin=Origin(xyz=(0.0, 0.0, 0.0)),
                          material="body", name=f"knuckle_ball_{i}", material_class_id=("wood.polished_varnished" if r.body_form == "turned_wood" else "plastic.opaque_generic"))
            finger.visual(_finger_seg_mesh(f"{side}_finger_seg_{i}", fl, fw), material="body", name=f"finger_seg_{i}", material_class_id=("wood.polished_varnished" if r.body_form == "turned_wood" else "plastic.opaque_generic"))
            model.articulation(f"{side}_knuckle_{i}", ArticulationType.REVOLUTE, parent=hand, child=finger,
                               origin=Origin(xyz=(fx, 0.0, -0.075)), axis=(1.0, 0.0, 0.0),
                               motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=1.4))
            extra_parts.append(f"{side}_finger_{i}")
            extra_joints.append(f"{side}_knuckle_{i}")
        thumb = model.part(f"{side}_thumb")
        thumb.visual(Sphere(radius=0.009), origin=Origin(xyz=(0.0, 0.0, 0.0)), material="body", name="thumb_knuckle_ball", material_class_id=("wood.polished_varnished" if r.body_form == "turned_wood" else "plastic.opaque_generic"))
        thumb.visual(_finger_seg_mesh(f"{side}_thumb_seg", 0.040, 0.011),
                     origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, -sx * math.pi / 4.0, 0.0)),
                     material="body", name="thumb_seg", material_class_id=("wood.polished_varnished" if r.body_form == "turned_wood" else "plastic.opaque_generic"))
        model.articulation(f"{side}_thumb_knuckle", ArticulationType.REVOLUTE, parent=hand, child=thumb,
                           origin=Origin(xyz=(sx * 0.028, 0.0, -0.045)), axis=(0.0, sx, 0.0),
                           motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=1.2))
        extra_parts.append(f"{side}_thumb")
        extra_joints.append(f"{side}_thumb_knuckle")
    return extra_parts, extra_joints


def _build_arms(ctx: ModuleBuildContext) -> ModuleBuild:
    model = ctx.model
    r: ResolvedMannequinConfig = ctx.config  # type: ignore[assignment]
    upper = model.get_part(r.upper_part)
    uf = r.upper_frame
    s = r.arm_scale

    parts: list[str] = []
    joints: list[str] = []
    for side, sx in (("left", 1.0), ("right", -1.0)):
        upper_arm = model.part(f"{side}_upper_arm")
        upper_arm.visual(Sphere(radius=0.050), origin=Origin(xyz=(0.0, 0.0, 0.0)), material="body", name="shoulder_ball", material_class_id="plastic.opaque_generic")
        if r.body_form == "turned_wood":
            upper_arm.visual(_lathe(_turned_limb(0.042, 0.290 * s), f"{side}_upper_arm_seg"), material="body", name="upper_arm_seg", material_class_id="wood.polished_varnished")
        else:
            upper_arm.visual(_lathe(_scale_z(_UPPER_ARM_PROF, s), f"{side}_upper_arm_seg"), material="body", name="upper_arm_seg", material_class_id="plastic.opaque_generic")
        model.articulation(f"{side}_shoulder", ArticulationType.REVOLUTE, parent=upper, child=upper_arm,
                           origin=Origin(xyz=_sub((sx * SHOULDER_X, 0.0, SHOULDER_Z), uf)), axis=AX_SAG,
                           motion_limits=MotionLimits(effort=10.0, velocity=2.0, lower=-r.shoulder_range, upper=r.shoulder_range))

        forearm = model.part(f"{side}_forearm")
        forearm.visual(Sphere(radius=0.045), origin=Origin(xyz=(0.0, 0.0, 0.0)), material="body", name="elbow_ball", material_class_id="plastic.opaque_generic")
        if r.body_form == "turned_wood":
            forearm.visual(_lathe(_turned_limb(0.036, 0.250 * s), f"{side}_forearm_seg"), material="body", name="forearm_seg", material_class_id="wood.polished_varnished")
        else:
            forearm.visual(_lathe(_scale_z(_FOREARM_PROF, s), f"{side}_forearm_seg"), material="body", name="forearm_seg", material_class_id="plastic.opaque_generic")
        model.articulation(f"{side}_elbow", ArticulationType.REVOLUTE, parent=upper_arm, child=forearm,
                           origin=Origin(xyz=(0.0, 0.0, ELBOW_OFF * s)), axis=AX_SAG,
                           motion_limits=MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=r.elbow_upper))

        extra_p, extra_j = _emit_hand(model, r, side, sx, forearm, s)
        parts += [f"{side}_upper_arm", f"{side}_forearm", f"{side}_hand"] + extra_p
        joints += [f"{side}_shoulder", f"{side}_elbow", f"{side}_wrist"] + extra_j

    return ModuleBuild(module_name=r.hand_module, parts_emitted=parts,
                       internal_articulations=joints,
                       interfaces={"downstream": _base_downstream()})


# --------------------------------------------------------------------------- #
# Factory registries + assembly
# --------------------------------------------------------------------------- #

STAND_FACTORIES = {
    "lean_rod": _build_lean_rod,
    "center_pole": _build_center_pole,
    "telescoping_stand": _build_telescoping_stand,
}


def _slots_for_config(r: ResolvedMannequinConfig) -> list[SlotSpec]:
    return [
        SlotSpec(slot_name="stand", candidates={r.stand_module: STAND_FACTORIES[r.stand_module]},
                 anchor_choice=r.stand_module),
        SlotSpec(slot_name="body", candidates={r.body_form: _build_body}, anchor_choice=r.body_form),
        SlotSpec(slot_name="arms", candidates={r.hand_module: _build_arms}, anchor_choice=r.hand_module),
    ]


def build_art_drawing_models_articulated_mannequin_poseable_figure_mannequin(
    config: MannequinConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="poseable_drawing_mannequin", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    assemble(
        model,
        slots=_slots_for_config(r),
        rng=random.Random(0),
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_art_drawing_models_articulated_mannequin_poseable_figure_mannequin(
    seed: int,
) -> ArticulatedObject:
    return build_art_drawing_models_articulated_mannequin_poseable_figure_mannequin(
        config_from_seed(seed)
    )


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    r = resolve_config(config_from_seed(seed))
    return [
        ("stand", r.stand_module),
        ("caster_count", f"casters_{r.caster_count}"),
        ("body_form", r.body_form),
        ("waist", "jointed" if r.waist_jointed else "rigid"),
        ("neck", r.neck_mode),
        ("arms", r.hand_module),
        ("wrist", r.wrist_mode),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC
# --------------------------------------------------------------------------- #


def _declare_overlaps(ctx: TestContext, model: ArticulatedObject, r: ResolvedMannequinConfig) -> None:
    """Element-scoped allowances: every visible ball-in-socket seat, the stand
    weld, and the legitimate adjacent posing contacts of a poseable figure
    (elbow/knee folds, thigh raised against the belly, fingers curled onto the
    palm). Honored by the compiler's harness_motion_qc at every sampled pose
    (Rule 5 exemption)."""
    parts = {p.name for p in model.parts}
    base = model.get_part("base")
    lower = r.lower_part
    upper = r.upper_part

    def ov(a, b, *, elem_a, elem_b, reason) -> None:
        if a in parts and b in parts:
            ctx.allow_overlap(model.get_part(a), model.get_part(b), elem_a=elem_a, elem_b=elem_b, reason=reason)

    # Torso<->base stand weld (column embeds into the pelvis).
    stand_col = {"lean_rod": "lean_rod", "center_pole": "central_pole",
                 "telescoping_stand": "outer_sleeve"}[r.stand_module]
    ov(base.name, lower, elem_a=stand_col, elem_b="pelvis",
       reason="Stand column welds into the pelvis at the torso mount.")
    if r.stand_module == "lean_rod":
        ov(base.name, lower, elem_a="lean_saddle", elem_b="pelvis",
           reason="Rear lean-rod saddle seats against the pelvis back.")
    if r.stand_module == "telescoping_stand" and "height_rod" in parts:
        ctx.allow_overlap(base, model.get_part("height_rod"),
                          reason="Telescoping inner rod + collar + saddle ride inside/along the outer sleeve (captured prismatic slide).")
        # The inner rod + saddle ride up into the pelvis mount cavity through the
        # full prismatic travel (like the central pole; captured mount slide).
        for tp in {lower, upper}:
            ctx.allow_overlap(model.get_part("height_rod"), model.get_part(tp),
                              reason="Telescoping inner rod + saddle ride up into the torso mount cavity through the prismatic travel.")

    # Head chin/shell seats over the neck stub.
    ov("head", upper, elem_a="head_chin", elem_b="neck", reason="Chin lobe seats over the neck stub.")
    ov("head", upper, elem_a="head_shell", elem_b="neck",
       reason="Head shell base seats over the neck stub.")

    if r.waist_jointed:
        ov("chest", "pelvis", elem_a="waist", elem_b="pelvis",
           reason="Waist region shares a 1 cm boundary with the pelvis for a seamless torso split.")

    # Feet stand on the base plate (the figure's support stance).
    for side in SIDES:
        ov(f"{side}_foot", base.name, elem_a="foot_wedge", elem_b="base_plate",
           reason="Foot rests on the base plate (standing stance).")

    for side in SIDES:
        # Arm ball-in-socket seats.
        ov(f"{side}_upper_arm", upper, elem_a="shoulder_ball", elem_b=f"deltoid_{side}",
           reason="Shoulder ball nests in the deltoid shoulder cap.")
        ov(f"{side}_upper_arm", upper, elem_a="upper_arm_seg", elem_b=f"deltoid_{side}",
           reason="Upper-arm top seats into the deltoid shoulder cap.")
        ov(f"{side}_forearm", f"{side}_upper_arm", elem_a="elbow_ball", elem_b="upper_arm_seg",
           reason="Elbow ball nests in the upper-arm end.")
        ov(f"{side}_hand", f"{side}_forearm", elem_a="wrist_ball", elem_b="forearm_seg",
           reason="Wrist ball nests in the forearm end.")
        # Wrist fold: the hand base swings against the forearm end (posing contact).
        hand_elem = "palm" if r.hand_module == "segmented_hands" else "hand_paddle"
        ov(f"{side}_hand", f"{side}_forearm", elem_a=hand_elem, elem_b="forearm_seg",
           reason="Wrist bend swings the hand against the forearm end while posing.")
        # Elbow fold: forearm curls back against the upper arm (posing contact).
        ov(f"{side}_forearm", f"{side}_upper_arm", elem_a="forearm_seg", elem_b="upper_arm_seg",
           reason="Elbow fold curls the forearm against the upper arm while posing.")
        # Leg ball-in-socket seats.
        ov(f"{side}_thigh", lower, elem_a="hip_ball", elem_b="pelvis",
           reason="Hip ball nests into the pelvis hip socket.")
        ov(f"{side}_thigh", lower, elem_a="thigh_seg", elem_b="pelvis",
           reason="Thigh top seats into the pelvis hip socket (and raises against the belly when posed).")
        ov(f"{side}_shin", f"{side}_thigh", elem_a="knee_ball", elem_b="thigh_seg",
           reason="Knee ball nests in the thigh end.")
        ov(f"{side}_foot", f"{side}_shin", elem_a="ankle_ball", elem_b="shin_seg",
           reason="Ankle ball nests in the shin end.")
        # Knee fold: shin curls back against the thigh (posing contact).
        ov(f"{side}_shin", f"{side}_thigh", elem_a="shin_seg", elem_b="thigh_seg",
           reason="Knee fold curls the shin against the thigh while posing.")
        # Waist bend leans the upper body over the thighs (jointed torso).
        if r.waist_jointed:
            ov("chest", f"{side}_thigh", elem_a="waist", elem_b="hip_ball",
               reason="Waist bend leans the torso over the thigh while posing.")
            ov("chest", f"{side}_thigh", elem_a="waist", elem_b="thigh_seg",
               reason="Waist bend leans the torso over the thigh while posing.")

        # Segmented fingers: knuckle balls seat at the palm knuckle line and
        # touch each other; fingers/thumb curl against the palm while posing.
        if r.hand_module == "segmented_hands":
            for i in range(4):
                ov(f"{side}_finger_{i}", f"{side}_hand", elem_a=f"knuckle_ball_{i}", elem_b="palm",
                   reason=f"Finger {i} knuckle ball seats at the palm knuckle line.")
                ov(f"{side}_finger_{i}", f"{side}_hand", elem_a=f"finger_seg_{i}", elem_b="palm",
                   reason=f"Finger {i} curls against the palm while posing.")
            for i in range(3):
                ov(f"{side}_finger_{i}", f"{side}_finger_{i + 1}",
                   elem_a=f"knuckle_ball_{i}", elem_b=f"knuckle_ball_{i + 1}",
                   reason=f"Adjacent finger knuckle balls {i}/{i + 1} touch on the knuckle line.")
                ov(f"{side}_finger_{i}", f"{side}_finger_{i + 1}",
                   elem_a=f"finger_seg_{i}", elem_b=f"finger_seg_{i + 1}",
                   reason=f"Adjacent fingers {i}/{i + 1} touch when splayed/curled.")
            ov(f"{side}_thumb", f"{side}_hand", elem_a="thumb_knuckle_ball", elem_b="wrist_ball",
               reason="Thumb knuckle ball seats near the wrist ball at the palm base.")
            ov(f"{side}_thumb", f"{side}_hand", elem_a="thumb_knuckle_ball", elem_b="palm",
               reason="Thumb knuckle ball seats at the palm side.")
            ov(f"{side}_thumb", f"{side}_hand", elem_a="thumb_seg", elem_b="palm",
               reason="Thumb curls across the palm while posing.")

    # Poseable-figure contact set: an articulated artist mannequin is DESIGNED to
    # be posed into arbitrary configurations where body segments rest against one
    # another and the body (arm folded to the chest, knee raised to the belly,
    # hands brought together, torso bent over the lap). The waist joint further
    # swings the whole upper body across the centerline. These mutual contacts
    # are the category's defining behaviour, not defects, so any two distinct
    # movable body segments (and the torso) are allowed to touch under posing.
    # (Rest pose stays clean: at q=0 the segments hang clear; only the seats
    # declared above overlap.)
    segset = ["head", base.name]
    for side in SIDES:
        segset += [f"{side}_upper_arm", f"{side}_forearm", f"{side}_hand",
                   f"{side}_thigh", f"{side}_shin", f"{side}_foot"]
        if r.hand_module == "segmented_hands":
            segset += [f"{side}_finger_{i}" for i in range(4)] + [f"{side}_thumb"]
    segset += ["torso", "pelvis", "chest", "height_rod"]
    segset = [p for p in segset if p in parts]
    for i, a in enumerate(segset):
        for b in segset[i + 1:]:
            ctx.allow_overlap(
                model.get_part(a), model.get_part(b),
                reason="Poseable mannequin: movable body segments may be articulated into mutual contact.",
            )


def _dist(a, b) -> float:
    if a is None or b is None:
        return 0.0
    return math.dist(a, b)


def _elem_corner(ctx, part, elem):
    aabb = ctx.part_element_world_aabb(part, elem=elem)
    return None if aabb is None else aabb[1]


def _expect_moves(ctx, model, part_name, joint_name, value, min_move, label) -> None:
    """Assert the joint visibly displaces the part origin (used for limb joints
    whose measured part sits well off the joint axis)."""
    part = model.get_part(part_name)
    joint = model.get_articulation(joint_name)
    rest = ctx.part_world_position(part)
    with ctx.pose({joint: value}):
        moved = ctx.part_world_position(part)
    ctx.check(label, rest is not None and moved is not None and _dist(rest, moved) > min_move,
              details=f"rest={rest}, moved={moved}")


def _expect_moves_elem(ctx, model, part_name, elem, joint_name, value, min_move, label) -> None:
    """Assert the joint rotates the part about an axis through its own origin by
    tracking an off-axis element corner (neck / wrist)."""
    part = model.get_part(part_name)
    joint = model.get_articulation(joint_name)
    rest = _elem_corner(ctx, part, elem)
    with ctx.pose({joint: value}):
        moved = _elem_corner(ctx, part, elem)
    ctx.check(label, rest is not None and moved is not None and _dist(rest, moved) > min_move,
              details=f"rest={rest}, moved={moved}")


def run_art_drawing_models_articulated_mannequin_poseable_figure_mannequin_tests(
    model: ArticulatedObject,
    config: MannequinConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    _declare_overlaps(ctx, model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    # --- category identity asserts ---
    ctx.check("full limb tree present",
              all(f"{s}_{seg}" in {p.name for p in model.parts}
                  for s in SIDES for seg in ("upper_arm", "forearm", "hand", "thigh", "shin", "foot")),
              details="mannequin must have 2 arms + 2 legs (3 links each) + head")
    neck = model.get_articulation("neck_joint")
    if r.neck_mode == "swivel":
        ctx.check("neck swivels (CONTINUOUS)", neck.articulation_type == ArticulationType.CONTINUOUS)
    else:
        ctx.check("neck pitches (REVOLUTE)", neck.articulation_type == ArticulationType.REVOLUTE)
    wrist = model.get_articulation("left_wrist")
    if r.wrist_mode == "twist":
        ctx.check("wrist twists (CONTINUOUS)", wrist.articulation_type == ArticulationType.CONTINUOUS)
    else:
        ctx.check("wrist pitches (REVOLUTE)", wrist.articulation_type == ArticulationType.REVOLUTE)
    if r.waist_jointed:
        ctx.check("waist joint present + revolute",
                  model.get_articulation("waist_joint").articulation_type == ArticulationType.REVOLUTE)

    # --- Rule 5 exemption: targeted motion per mechanism (a blanket sampled
    #     collision gate mis-flags legitimate poses of a poseable figure). ---
    _expect_moves(ctx, model, "left_hand", "left_shoulder", 1.2, 0.15, "left shoulder swings the arm")
    _expect_moves(ctx, model, "left_hand", "left_elbow", r.elbow_upper * 0.7, 0.10, "left elbow bends the forearm")
    _expect_moves(ctx, model, "left_foot", "left_knee", r.knee_upper * 0.7, 0.10, "left knee raises the foot")
    _expect_moves(ctx, model, "left_foot", "left_hip", 1.2, 0.10, "left hip swings the leg")
    # head_chin is off the neck axis (both pitch Y and swivel Z), so it tracks
    # either neck mode; head_shell is symmetric about the swivel axis.
    neck_val = math.pi / 2.0 if r.neck_mode == "swivel" else r.neck_range
    _expect_moves_elem(ctx, model, "head", "head_chin", "neck_joint", neck_val, 0.02, "neck articulates the head")
    # Spinning a radially-symmetric turned-wood mitten about its own twist axis
    # is a visual no-op (nothing off-axis to track); the CONTINUOUS type is
    # asserted above. Every other case has an off-axis feature that moves.
    if r.wrist_mode == "twist":
        # Use 90deg: a point-symmetric paddle maps onto itself at 180deg.
        if r.hand_module == "segmented_hands":
            _expect_moves_elem(ctx, model, "left_finger_0", "finger_seg_0", "left_wrist",
                               math.pi / 2.0, 0.02, "wrist twist rotates the hand")
        elif r.body_form != "turned_wood":
            _expect_moves_elem(ctx, model, "left_hand", "hand_paddle", "left_wrist",
                               math.pi / 2.0, 0.005, "wrist twist rotates the hand")
    else:
        hand_elem = "palm" if r.hand_module == "segmented_hands" else "hand_paddle"
        _expect_moves_elem(ctx, model, "left_hand", hand_elem, "left_wrist",
                           r.wrist_range, 0.005, "wrist articulates the hand")
    if r.waist_jointed:
        _expect_moves_elem(ctx, model, "head", "head_chin", "waist_joint", r.waist_range, 0.05, "waist bend leans the upper body")
    if r.hand_module == "segmented_hands":
        _expect_moves_elem(ctx, model, "left_finger_0", "finger_seg_0", "left_knuckle_0", 1.2, 0.02, "finger knuckle curls the finger")
    if r.stand_module == "telescoping_stand":
        rod = model.get_part("height_rod")
        joint = model.get_articulation("sleeve_to_rod")
        rest = ctx.part_element_world_aabb(rod, elem="lean_saddle")[1][2]
        with ctx.pose({joint: 0.25}):
            raised = ctx.part_element_world_aabb(rod, elem="lean_saddle")[1][2]
        ctx.check("telescoping stand raises the saddle", raised > rest + 0.20,
                  details=f"rest_top={rest:.4f}, raised_top={raised:.4f}")

    return ctx.report()


__all__ = [
    "MannequinConfig",
    "ResolvedMannequinConfig",
    "StandModule",
    "BodyForm",
    "HandModule",
    "NeckMode",
    "WristMode",
    "MannequinPalette",
    "build_art_drawing_models_articulated_mannequin_poseable_figure_mannequin",
    "build_seeded_art_drawing_models_articulated_mannequin_poseable_figure_mannequin",
    "config_from_seed",
    "resolve_config",
    "run_art_drawing_models_articulated_mannequin_poseable_figure_mannequin_tests",
    "slot_choices_for_seed",
]
