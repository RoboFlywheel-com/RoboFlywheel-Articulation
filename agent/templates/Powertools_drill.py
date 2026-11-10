# SPDX-License-Identifier: Apache-2.0

"""Handheld cordless drill / driver modular template.

NOTE on the slug: ``cordless_drill`` here = a **handheld cordless drill-driver**
(a molded housing + keyless self-tightening chuck that spins continuously, a
torque-setting clutch collar, a squeeze trigger, a forward/reverse selector, and
a slide-on battery pack), NOT a lathe chuck (independent 4-jaw scroll chuck on a
headstock), NOT an impact driver (1/4" hex quick-change socket, no chuck), and
NOT a hammer drill or a manual screwdriver. Sourced from the reviewed modular
spec ``articraft_template_authoring/specs_modular_v1/Powertools_drill.md`` and the
7-record 5-star pool (1 pistol parent + 6 slot-fork variants), all synced under
``data/records/``.

Identity = a keyless **chuck that spins CONTINUOUS** plus the trigger / clutch /
selector / battery mechanism. The five non-fixed joints are kept on EVERY seed:

  * ``housing_to_chuck``        CONTINUOUS  (the whole chuck spins as one rigid)
  * ``housing_to_clutch_collar`` REVOLUTE   (torque-setting collar twist)
  * ``housing_to_trigger``       REVOLUTE   (squeeze lever)
  * ``housing_to_selector``      PRISMATIC  (forward/reverse slide)
  * ``housing_to_battery_pack``  PRISMATIC  (slide the pack off the foot)

Two structural slots:

  * **Slot A — body_form** (housing/grip topology): ``pistol_grip`` (parent S1) /
    ``right_angle`` (S2, L-shaped vertical motor + horizontal chuck head) /
    ``t_handle_compact`` (S3, short stubby barrel, grip centred below). The body
    form only re-lays the cadquery housing solids + the five joint origins; the
    five joints, the chuck, the clutch and the controls are shared geometry.
  * **Slot B — battery_mount** (battery interface): ``slide_on_stick`` (S1, tall
    stick pack on a rail foot) / ``flat_pod_slide`` (S4, flat dovetail pod under
    a thin platform). Slot B swaps the foot solid + the battery part.

Two count-only multiplicity axes (both loops already exist in every source):

  * ``jaw_count`` in {2, 3}: ``jaw_{i}`` steel boxes evenly angled ``2*pi*i/N``,
    **rigid inside the single CONTINUOUS chuck** (no per-jaw joint; 4-jaw is a
    lathe chuck, out of category).
  * ``detent_count`` in {12, 16, 20}: collar ``tick_{i}`` torque marks evenly
    angled ``2*pi*i/N`` plus ``round(1.5*N)`` knurl ribs, both FIXED decoration
    folded into the collar (Rule 1), rib count tracks the detent count.

All chuck / clutch / trigger / selector / battery joints are captured-geometry
fits (spindle in the gearbox bore, collar lip on the housing nose, trigger boss
in the grip recess, selector pin through a bore, battery rails in the foot
channel), so they are guarded by element-scoped ``allow_overlap`` mirroring each
source's run_tests block plus the flat 0.015 m articulation-origin baseline, and
omit ``MatingContract`` (grandfathered).
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
    BoxGeometry,
    Cylinder,
    ExtrudeGeometry,
    KnobGeometry,
    KnobGrip,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

BodyForm = Literal["pistol_grip", "right_angle", "t_handle_compact"]
BatteryMount = Literal["slide_on_stick", "flat_pod_slide"]
PaletteStyle = Literal["lime_green", "yellow_black", "blue", "red", "teal"]
BitStyle = Literal["none", "twist_bit"]

BODY_FORMS: tuple[BodyForm, ...] = ("pistol_grip", "right_angle", "t_handle_compact")
BATTERY_MOUNTS: tuple[BatteryMount, ...] = ("slide_on_stick", "flat_pod_slide")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("lime_green", "yellow_black", "blue", "red", "teal")
BIT_STYLES: tuple[BitStyle, ...] = ("none", "twist_bit")

JAW_COUNTS: tuple[int, ...] = (2, 3)
DETENT_COUNTS: tuple[int, ...] = (12, 16, 20)
JAW_WEIGHTS = (0.35, 0.65)  # 3-jaw is the common keyless chuck
DETENT_WEIGHTS = (0.5, 0.3, 0.2)
BIT_WEIGHTS = (0.45, 0.55)

# ---------------------------------------------------------------------------
# Per-body-form geometry constants. Each form fixes the barrel/head Z axis
# height, the barrel radius and X span, the clutch + chuck joint planes, and
# the control + battery-seat origins. Everything else (chuck, collar, trigger,
# selector geometry) is shared and authored about these references.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _BodyDims:
    form: BodyForm
    barrel_z: float
    barrel_r: float
    barrel_x0: float
    barrel_x1: float
    collar_x: float
    chuck_x: float
    trigger_pivot: tuple[float, float, float]
    selector_pos: tuple[float, float, float]
    battery_seat: tuple[float, float, float]  # Native slide-on stick battery joint origin
    foot_x: float  # X centre of the foot rail / battery seat plane
    foot_base_z: float  # Z of the foot cadquery workplane (foot extrudes +Z from here)
    grip_bottom_z: float  # Z of the grip polyline bottom edge


@dataclass(frozen=True)
class _RailGrooveInterface:
    foot_len: float
    foot_bottom_z: float
    foot_height: float
    rail_len: float
    rail_w: float
    rail_h: float
    rail_y: tuple[float, float]
    body_top_z: float
    side_clearance: float
    end_clearance: float
    depth_clearance: float

    @property
    def foot_top_z(self) -> float:
        return self.foot_bottom_z + self.foot_height

    @property
    def groove_len(self) -> float:
        return self.foot_len + 2.0 * self.end_clearance

    @property
    def groove_w(self) -> float:
        return self.rail_w + 2.0 * self.side_clearance

    @property
    def groove_depth(self) -> float:
        return self.rail_h + self.depth_clearance

    @property
    def rail_z_center(self) -> float:
        return self.body_top_z + 0.5 * self.rail_h


def _rail_groove_interface(d: _BodyDims, battery_mount: BatteryMount) -> _RailGrooveInterface:
    if battery_mount == "slide_on_stick":
        return _RailGrooveInterface(
            foot_len=0.078,
            foot_bottom_z=d.foot_base_z,
            foot_height=0.014,
            rail_len=0.062,
            rail_w=0.005,
            rail_h=0.008,
            rail_y=(-0.020, 0.020),
            body_top_z=-0.0005,
            side_clearance=0.0025,
            end_clearance=0.004,
            depth_clearance=0.0008,
        )
    return _RailGrooveInterface(
        foot_len=0.076,
        foot_bottom_z=d.foot_base_z + 0.006,
        foot_height=0.008,
        rail_len=0.070,
        rail_w=0.010,
        rail_h=0.005,
        rail_y=(-0.018, 0.018),
        body_top_z=0.0,
        side_clearance=0.001,
        end_clearance=0.003,
        depth_clearance=0.001,
    )


_PISTOL = _BodyDims(
    form="pistol_grip",
    barrel_z=0.155,
    barrel_r=0.032,
    barrel_x0=-0.075,
    barrel_x1=0.055,
    collar_x=0.055,
    chuck_x=0.082,
    trigger_pivot=(-0.0215, 0.0, 0.122),
    selector_pos=(-0.023, 0.0, 0.133),
    battery_seat=(-0.057, 0.0, 0.064),
    foot_x=-0.057,
    foot_base_z=0.064,
    grip_bottom_z=0.070,
)
_RIGHT_ANGLE = _BodyDims(
    form="right_angle",
    barrel_z=0.148,
    barrel_r=0.026,
    barrel_x0=-0.020,
    barrel_x1=0.045,
    collar_x=0.045,
    chuck_x=0.072,
    trigger_pivot=(-0.006, 0.0, 0.055),
    selector_pos=(-0.020, 0.0, 0.080),
    battery_seat=(-0.048, 0.0, 0.029),
    foot_x=-0.048,
    foot_base_z=0.015,
    grip_bottom_z=0.015,
)
_T_HANDLE = _BodyDims(
    form="t_handle_compact",
    barrel_z=0.150,
    barrel_r=0.028,
    barrel_x0=-0.028,
    barrel_x1=0.038,
    collar_x=0.038,
    chuck_x=0.065,
    trigger_pivot=(0.020, 0.0, 0.118),
    selector_pos=(0.018, 0.0, 0.130),
    battery_seat=(0.005, 0.0, 0.062),
    foot_x=0.005,
    foot_base_z=0.062,
    grip_bottom_z=0.062,
)

_BODY_DIMS: dict[BodyForm, _BodyDims] = {
    "pistol_grip": _PISTOL,
    "right_angle": _RIGHT_ANGLE,
    "t_handle_compact": _T_HANDLE,
}

# Palettes: shell (body), rubber (overmold/grip), charcoal (collar/chuck sleeve),
# steel (spindle/jaws), seam, label (battery + pointer), tick (white marks).
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "lime_green": {
        "shell": (0.72, 0.80, 0.20, 1.0),
        "rubber": (0.09, 0.09, 0.10, 1.0),
        "charcoal": (0.15, 0.15, 0.17, 1.0),
        "steel": (0.72, 0.74, 0.78, 1.0),
        "seam": (0.05, 0.05, 0.05, 1.0),
        "label": (0.95, 0.83, 0.10, 1.0),
        "tick": (0.92, 0.92, 0.90, 1.0),
    },
    "yellow_black": {
        "shell": (0.95, 0.78, 0.08, 1.0),
        "rubber": (0.08, 0.08, 0.09, 1.0),
        "charcoal": (0.14, 0.14, 0.15, 1.0),
        "steel": (0.74, 0.76, 0.80, 1.0),
        "seam": (0.04, 0.04, 0.04, 1.0),
        "label": (0.12, 0.12, 0.13, 1.0),
        "tick": (0.93, 0.93, 0.91, 1.0),
    },
    "blue": {
        "shell": (0.13, 0.32, 0.62, 1.0),
        "rubber": (0.09, 0.09, 0.11, 1.0),
        "charcoal": (0.16, 0.16, 0.18, 1.0),
        "steel": (0.72, 0.74, 0.78, 1.0),
        "seam": (0.05, 0.05, 0.06, 1.0),
        "label": (0.90, 0.90, 0.88, 1.0),
        "tick": (0.92, 0.92, 0.90, 1.0),
    },
    "red": {
        "shell": (0.78, 0.13, 0.13, 1.0),
        "rubber": (0.10, 0.10, 0.11, 1.0),
        "charcoal": (0.15, 0.15, 0.16, 1.0),
        "steel": (0.73, 0.75, 0.79, 1.0),
        "seam": (0.05, 0.05, 0.05, 1.0),
        "label": (0.93, 0.91, 0.20, 1.0),
        "tick": (0.93, 0.93, 0.92, 1.0),
    },
    "teal": {
        "shell": (0.08, 0.52, 0.50, 1.0),
        "rubber": (0.09, 0.09, 0.10, 1.0),
        "charcoal": (0.15, 0.16, 0.17, 1.0),
        "steel": (0.72, 0.74, 0.78, 1.0),
        "seam": (0.04, 0.05, 0.05, 1.0),
        "label": (0.92, 0.92, 0.90, 1.0),
        "tick": (0.93, 0.93, 0.91, 1.0),
    },
}


# ===========================================================================
# Config
# ===========================================================================
@dataclass(frozen=True)
class CordlessDrillConfig:
    body_form: BodyForm | None = None
    battery_mount: BatteryMount | None = None
    bit_style: BitStyle | None = None
    jaw_count: int | None = None
    detent_count: int | None = None
    palette_style: PaletteStyle = "lime_green"
    body_scale: float = 1.0
    chuck_scale: float = 1.0
    name: str = "cordless_drill"


@dataclass(frozen=True)
class ResolvedCordlessDrillConfig:
    body_form: BodyForm
    battery_mount: BatteryMount
    bit_style: BitStyle
    jaw_count: int
    detent_count: int
    rib_count: int
    palette_style: PaletteStyle
    body_scale: float
    chuck_scale: float
    dims: _BodyDims
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> CordlessDrillConfig:
    rng = random.Random(seed)
    body_form = rng.choice(BODY_FORMS)
    battery_mount = rng.choice(BATTERY_MOUNTS)
    jaw_count = rng.choices(JAW_COUNTS, weights=JAW_WEIGHTS, k=1)[0]
    detent_count = rng.choices(DETENT_COUNTS, weights=DETENT_WEIGHTS, k=1)[0]
    palette_style = rng.choice(PALETTE_STYLES)
    body_scale = round(rng.uniform(0.90, 1.15), 4)
    chuck_scale = round(rng.uniform(0.90, 1.15), 4)
    bit_style = rng.choices(BIT_STYLES, weights=BIT_WEIGHTS, k=1)[0]
    return CordlessDrillConfig(
        body_form=body_form,
        battery_mount=battery_mount,
        bit_style=bit_style,
        jaw_count=jaw_count,
        detent_count=detent_count,
        palette_style=palette_style,
        body_scale=body_scale,
        chuck_scale=chuck_scale,
        name=f"seeded_cordless_drill_{seed}",
    )


def resolve_config(
    config: CordlessDrillConfig | None = None,
) -> ResolvedCordlessDrillConfig:
    cfg = config or CordlessDrillConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    battery_mount = _pick(cfg.battery_mount, BATTERY_MOUNTS)
    bit_style = _pick(cfg.bit_style, BIT_STYLES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    jaw_count = int(cfg.jaw_count) if cfg.jaw_count is not None else 3
    if jaw_count not in JAW_COUNTS:
        jaw_count = 3  # 4-jaw is a lathe chuck (out of category); clamp into {2,3}
    jaw_count = int(_clamp(jaw_count, 2, 3))

    detent_count = int(cfg.detent_count) if cfg.detent_count is not None else 12
    if detent_count not in DETENT_COUNTS:
        # snap to nearest allowed detent count
        detent_count = min(DETENT_COUNTS, key=lambda d: abs(d - detent_count))
    # rib count tracks the detent count (parent: 18 ribs / 12 ticks = 1.5x).
    rib_count = int(round(1.5 * detent_count))

    body_scale = _clamp(cfg.body_scale, 0.90, 1.15)
    chuck_scale = _clamp(cfg.chuck_scale, 0.90, 1.15)

    return ResolvedCordlessDrillConfig(
        body_form=body_form,
        battery_mount=battery_mount,
        bit_style=bit_style,
        jaw_count=jaw_count,
        detent_count=detent_count,
        rib_count=rib_count,
        palette_style=palette_style,
        body_scale=body_scale,
        chuck_scale=chuck_scale,
        dims=_BODY_DIMS[body_form],
        name=cfg.name or "cordless_drill",
    )


def with_overrides(config: CordlessDrillConfig, **kwargs: object) -> CordlessDrillConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: CordlessDrillConfig | ResolvedCordlessDrillConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCordlessDrillConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("battery_mount", r.battery_mount),
        ("bit_style", r.bit_style),
        ("jaw_count", f"n{r.jaw_count}"),
        ("detent_count", f"n{r.detent_count}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Housing solids (Slot A body form + Slot B foot). CadQuery, mirrored shells.
# ===========================================================================
def _split_shells(solid):
    """Split a molded solid into mirrored left/right shells + a parting seam."""
    right_box = cq.Workplane("XY").transformed(offset=(0.0, 0.1504, 0.1)).box(0.8, 0.3, 0.6)
    left_box = cq.Workplane("XY").transformed(offset=(0.0, -0.1504, 0.1)).box(0.8, 0.3, 0.6)
    seam_box = cq.Workplane("XY").transformed(offset=(0.0, 0.0, 0.1)).box(0.8, 0.0016, 0.6)
    return solid.intersect(right_box), solid.intersect(left_box), solid.intersect(seam_box)


def _foot_solid(d: _BodyDims, battery_mount: BatteryMount):
    """Foot rail / dovetail platform the battery slides onto (Slot B)."""
    interface = _rail_groove_interface(d, battery_mount)
    if battery_mount == "slide_on_stick":
        foot = (
            cq.Workplane("XY")
            .workplane(offset=interface.foot_bottom_z)
            .center(d.foot_x, 0.0)
            .rect(interface.foot_len, 0.052)
            .extrude(interface.foot_height)
        )
        try:
            foot = foot.edges("|Z").fillet(0.006)
        except Exception:
            pass
        # Hollow out the battery receptacle so the slide-on stick pack seats into
        # a real pocket instead of jamming its rails/top lip through a solid
        # block. The battery ships two 0.005 x 0.008 rails at y = +/-0.020 that
        # ride 0.008 up into the foot, plus a top lip right under the foot base.
        # Cut matching through-channels into the foot underside rather than one
        # wide slot, keeping the central web while exposing the grooves at both
        # open ends of the slide.
        for y_off in interface.rail_y:
            channel = (
                cq.Workplane("XY")
                .workplane(offset=interface.foot_bottom_z)
                .center(d.foot_x, y_off)
                .rect(interface.groove_len, interface.groove_w)
                .extrude(interface.groove_depth)
            )
            foot = foot.cut(channel)
        # Shallow central relief for the battery top lip between the rails so the
        # pack shoulder tucks into a recess and does not press a flat solid face.
        relief = (
            cq.Workplane("XY")
            .workplane(offset=interface.foot_bottom_z)
            .center(d.foot_x, 0.0)
            .rect(interface.groove_len, 2.0 * abs(interface.rail_y[0]) - interface.groove_w)
            .extrude(0.0015 + interface.depth_clearance)
        )
        foot = foot.cut(relief)
        return foot
    # flat_pod_slide: thinner platform with two underside grooves. The grooves
    # run through the platform ends so the pod's raised rails can slide in/out.
    foot = (
        cq.Workplane("XY")
        .workplane(offset=interface.foot_bottom_z)
        .center(d.foot_x, 0.0)
        .rect(interface.foot_len, 0.058)
        .extrude(interface.foot_height)
    )
    try:
        foot = foot.edges("|Z").fillet(0.004)
    except Exception:
        pass
    for y_off in interface.rail_y:
        groove = (
            cq.Workplane("XY")
            .workplane(offset=interface.foot_bottom_z)
            .center(d.foot_x, y_off)
            .rect(interface.groove_len, interface.groove_w)
            .extrude(interface.groove_depth)
        )
        foot = foot.cut(groove)
    return foot


def _battery_seat_origin(d: _BodyDims, battery_mount: BatteryMount) -> tuple[float, float, float]:
    """Derive the battery joint origin from the emitted foot geometry."""
    interface = _rail_groove_interface(d, battery_mount)
    # The battery top seats at the foot underside; raised rails extend upward
    # into grooves derived from the same interface.
    return (d.foot_x, 0.0, interface.foot_bottom_z)


def _housing_solids(d: _BodyDims, battery_mount: BatteryMount, body_scale: float):
    """Build the molded housing for the chosen body form (Slot A) + foot (Slot B)."""
    br = d.barrel_r * body_scale
    if d.form == "right_angle":
        # L-shaped: horizontal head (gearbox) + vertical motor body + grip.
        head = (
            cq.Workplane("YZ")
            .workplane(offset=d.barrel_x0)
            .center(0.0, d.barrel_z)
            .circle(br)
            .extrude(d.barrel_x1 - d.barrel_x0)
        )
        try:
            head = head.edges(">X").fillet(0.006)
        except Exception:
            pass
        body_x = -0.020
        body = (
            cq.Workplane("XY")
            .workplane(offset=0.058)
            .center(body_x, 0.0)
            .circle(br)
            .extrude(d.barrel_z - 0.058)
        )
        junction = (
            cq.Workplane("XY")
            .workplane(offset=d.barrel_z - 0.018)
            .center(body_x, 0.0)
            .circle(br + 0.005)
            .extrude(0.036)
        )
        try:
            junction = junction.edges("|Z").fillet(0.008)
        except Exception:
            pass
        grip_pts = [
            (body_x + 0.019, 0.058),
            (body_x - 0.019, 0.058),
            (d.foot_x - 0.016, d.grip_bottom_z),
            (d.foot_x + 0.016, d.grip_bottom_z),
        ]
        grip = cq.Workplane("XZ").polyline(grip_pts).close().extrude(0.023, both=True)
        try:
            grip = grip.edges("|Y").fillet(0.008)
        except Exception:
            pass
        solid = head.union(body).union(junction).union(grip)
        overmold = (
            cq.Workplane("YZ")
            .workplane(offset=d.barrel_x0 + 0.005)
            .center(0.0, d.barrel_z)
            .circle(br + 0.0015)
            .extrude(d.barrel_x1 - d.barrel_x0 - 0.010)
            .intersect(
                cq.Workplane("XY")
                .transformed(offset=(0.0, 0.0, d.barrel_z + br * 0.5 + 0.05))
                .box(0.8, 0.8, 0.1)
            )
        )
    else:
        # pistol_grip / t_handle_compact: horizontal barrel + grip below.
        barrel = (
            cq.Workplane("YZ")
            .workplane(offset=d.barrel_x0)
            .center(0.0, d.barrel_z)
            .circle(br)
            .extrude(d.barrel_x1 - d.barrel_x0)
        )
        try:
            barrel = barrel.edges("<X").fillet(0.008)
        except Exception:
            pass
        if d.form == "pistol_grip":
            grip_pts = [(-0.018, 0.130), (-0.065, 0.130), (-0.085, 0.070), (-0.041, 0.070)]
            grip = cq.Workplane("XZ").polyline(grip_pts).close().extrude(0.023, both=True)
        else:  # t_handle_compact: grip centred under the barrel midpoint
            gx = d.foot_x
            # Grip top reaches up to the barrel centerline so the grip always
            # unions into the barrel core regardless of body_scale (a shrunk
            # barrel radius would otherwise leave the grip top floating below
            # the barrel and split the shell into disconnected islands).
            grip_pts = [
                (gx - 0.013, d.barrel_z),
                (gx + 0.013, d.barrel_z),
                (gx + 0.013, d.grip_bottom_z),
                (gx - 0.013, d.grip_bottom_z),
            ]
            grip = cq.Workplane("XZ").polyline(grip_pts).close().extrude(0.023, both=True)
        try:
            grip = grip.edges("|Y").fillet(0.008)
        except Exception:
            pass
        solid = barrel.union(grip)
        overmold = (
            cq.Workplane("YZ")
            .workplane(offset=d.barrel_x0 + 0.003)
            .center(0.0, d.barrel_z)
            .circle(br + 0.0015)
            .extrude(max(0.02, d.barrel_x1 - d.barrel_x0 - 0.020))
            .intersect(
                cq.Workplane("XY")
                .transformed(offset=(0.0, 0.0, d.barrel_z + 0.05))
                .box(0.8, 0.8, 0.1)
            )
        )

    solid = solid.union(_foot_solid(d, battery_mount))
    right_shell, left_shell, seam = _split_shells(solid)
    return right_shell, left_shell, seam, overmold


# ===========================================================================
# Part builders
# ===========================================================================
def _build_housing(model, housing, r, mats):
    d = r.dims
    br = d.barrel_r * r.body_scale
    right_shell, left_shell, seam, overmold = _housing_solids(d, r.battery_mount, r.body_scale)
    housing.visual(
        mesh_from_cadquery(right_shell, "housing_right"), material=mats["shell"], name="right_shell", material_class_id="plastic.opaque_glossy_molded"
    )
    housing.visual(
        mesh_from_cadquery(left_shell, "housing_left"), material=mats["shell"], name="left_shell", material_class_id="plastic.opaque_glossy_molded"
    )
    housing.visual(
        mesh_from_cadquery(seam, "housing_seam"), material=mats["seam"], name="parting_seam", material_class_id="plastic.opaque_glossy_molded"
    )
    housing.visual(
        mesh_from_cadquery(overmold, "housing_overmold"), material=mats["rubber"], name="top_overmold", material_class_id="rubber.smooth_plain"
    )

    # Vent slots recessed into both housing side walls near the barrel front.
    vent_idx = 0
    half_w = br - 0.0004
    for vz in (d.barrel_z + 0.005, d.barrel_z - 0.008):
        for vx in (d.barrel_x1 - 0.043, d.barrel_x1 - 0.025, d.barrel_x1 - 0.007):
            for side in (1.0, -1.0):
                housing.visual(
                    Box((0.012, 0.003, 0.005)),
                    origin=Origin(xyz=(vx, side * half_w, vz)),
                    material=mats["seam"],
                    name=f"vent_{vent_idx}", material_class_id="plastic.opaque_glossy_molded",
                )
                vent_idx += 1

    # Torque index mark on top of the barrel, in front of the clutch collar.
    housing.visual(
        Box((0.006, 0.003, 0.0025)),
        origin=Origin(xyz=(d.collar_x - 0.005, 0.0, d.barrel_z + br)),
        material=mats["tick"],
        name="torque_index", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )


def _build_clutch_collar(model, housing, r, mats):
    d = r.dims
    collar = model.part("clutch_collar")
    collar_geo = LatheGeometry.from_shell_profiles(
        [(0.0275, -0.0015), (0.0285, 0.004), (0.0285, 0.022), (0.026, 0.027)],
        [(0.0105, -0.0015), (0.0105, 0.027)],
        segments=48,
    )
    # Knurl ribs: count tracks the detent count (multiplicity N2).
    for i in range(r.rib_count):
        rib = BoxGeometry((0.0024, 0.0022, 0.020))
        rib.translate(0.0288, 0.0, 0.012)
        rib.rotate_z(i * 2.0 * math.pi / r.rib_count)
        collar_geo.merge(rib)
    collar_geo.rotate_y(math.pi / 2.0)
    collar.visual(
        mesh_from_geometry(collar_geo, "clutch_collar_body"),
        material=mats["charcoal"],
        name="collar_body", material_class_id="plastic.patterned_textured",
    )

    # Torque-setting detent tick marks: count = detent_count (multiplicity N2).
    ticks_geo = None
    for i in range(r.detent_count):
        tick = BoxGeometry((0.0018, 0.0018, 0.0030))
        tick.translate(0.0284, 0.0, 0.0235)
        tick.rotate_z(i * 2.0 * math.pi / r.detent_count)
        ticks_geo = tick if ticks_geo is None else ticks_geo.merge(tick)
    ticks_geo.rotate_y(math.pi / 2.0)
    collar.visual(
        mesh_from_geometry(ticks_geo, "collar_ticks"), material=mats["tick"], name="setting_ticks", appearance_only=AppearanceOnlySpec(kind="overlay")
    )

    pointer_geo = BoxGeometry((0.0020, 0.0036, 0.0050))
    pointer_geo.translate(-0.0288, 0.0, 0.0240)
    pointer_geo.rotate_y(math.pi / 2.0)
    collar.visual(
        mesh_from_geometry(pointer_geo, "collar_pointer"),
        material=mats["label"],
        name="torque_pointer", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )

    model.articulation(
        "housing_to_clutch_collar",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=collar,
        origin=Origin(xyz=(d.collar_x, 0.0, d.barrel_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=3.0, lower=-1.047, upper=1.047),
    )
    return collar


def _build_chuck(model, housing, r, mats):
    d = r.dims
    cs = r.chuck_scale
    chuck = model.part("chuck")
    chuck.visual(
        Cylinder(radius=0.0085 * cs, length=0.036),
        origin=Origin(xyz=(-0.012, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["steel"],
        name="spindle", material_class_id="metal.steel_bare",
    )
    sleeve_geo = KnobGeometry(
        0.048 * cs,
        0.028,
        body_style="cylindrical",
        grip=KnobGrip(style="knurled", count=32, depth=0.0010, helix_angle_deg=25.0),
        center=False,
    )
    chuck.visual(
        mesh_from_geometry(sleeve_geo, "chuck_sleeve_mesh"),
        origin=Origin(xyz=(0.004, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["charcoal"],
        name="chuck_sleeve", material_class_id="metal.blackened_gunmetal",
    )
    bore_r = 0.0055 * cs
    nose_geo = LatheGeometry.from_shell_profiles(
        [(0.0235 * cs, 0.0), (0.021 * cs, 0.005), (0.012 * cs, 0.0105)],
        [(bore_r, 0.0), (bore_r * 0.92, 0.0105)],
        segments=40,
        lip_samples=4,
    )
    nose_geo.rotate_y(math.pi / 2.0)
    nose_geo.translate(0.0315, 0.0, 0.0)
    chuck.visual(
        mesh_from_geometry(nose_geo, "chuck_nose"), material=mats["charcoal"], name="chuck_nose", material_class_id="metal.blackened_gunmetal"
    )

    # jaw_count steel jaws, evenly angled 2*pi*i/N, rigid inside the chuck (N1).
    # Each jaw is a visible radial shoe inside the open chuck mouth, not a small
    # square patch on a closed front disk.
    for i in range(r.jaw_count):
        jaw = BoxGeometry((0.013, 0.0032 * cs, 0.0105 * cs))
        jaw.rotate_y(0.18)
        jaw.translate(0.0405, 0.0, 0.0066 * cs)
        jaw.rotate_x(i * 2.0 * math.pi / r.jaw_count)
        chuck.visual(mesh_from_geometry(jaw, f"jaw_{i}"), material=mats["steel"], name=f"jaw_{i}", material_class_id="metal.steel_bare")

    if r.bit_style == "twist_bit":
        bit_r = 0.0032 * cs
        bit_len = 0.074 * cs
        bit_center_x = 0.078 * cs
        chuck.visual(
            Cylinder(radius=bit_r, length=bit_len),
            origin=Origin(xyz=(bit_center_x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["steel"],
            name="twist_bit_core", material_class_id="metal.steel_bare",
        )

        tip_geo = LatheGeometry([(0.0, 0.0), (bit_r, 0.0), (0.0, 0.010 * cs)], segments=28)
        tip_geo.rotate_y(math.pi / 2.0)
        tip_geo.translate(bit_center_x + 0.5 * bit_len, 0.0, 0.0)
        chuck.visual(
            mesh_from_geometry(tip_geo, "twist_bit_tip"), material=mats["steel"], name="twist_bit_tip", material_class_id="metal.steel_bare"
        )

        flute_geo = None
        flute_segments = 22
        flute_start_x = bit_center_x - 0.5 * bit_len + 0.006 * cs
        flute_step = (bit_len - 0.016 * cs) / flute_segments
        for helix in range(2):
            phase = helix * math.pi
            for k in range(flute_segments):
                angle = phase + k * 0.72
                flute = BoxGeometry((0.0042 * cs, 0.0010 * cs, 0.0014 * cs))
                flute.translate(flute_start_x + k * flute_step, 0.0, bit_r + 0.00025 * cs)
                flute.rotate_x(angle)
                flute_geo = flute if flute_geo is None else flute_geo.merge(flute)
        if flute_geo is not None:
            chuck.visual(
                mesh_from_geometry(flute_geo, "twist_bit_flutes"),
                material=mats["charcoal"],
                name="twist_bit_flutes", material_class_id="metal.blackened_gunmetal",
            )

    model.articulation(
        "housing_to_chuck",
        ArticulationType.CONTINUOUS,
        parent=housing,
        child=chuck,
        origin=Origin(xyz=(d.chuck_x, 0.0, d.barrel_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=50.0),
    )
    return chuck


def _build_trigger(model, housing, r, mats):
    d = r.dims
    trigger = model.part("trigger")
    trigger.visual(
        Cylinder(radius=0.0045, length=0.015),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["rubber"],
        name="pivot_boss", material_class_id="rubber.smooth_plain",
    )
    blade_pts = [
        (-0.0045, 0.0005),
        (0.0080, 0.0005),
        (0.0125, -0.0060),
        (0.0108, -0.0130),
        (0.0088, -0.0190),
        (0.0098, -0.0250),
        (0.0040, -0.0285),
        (-0.0045, -0.0275),
    ]
    blade_geo = ExtrudeGeometry(blade_pts, 0.016)
    blade_geo.rotate_x(math.pi / 2.0)
    trigger.visual(mesh_from_geometry(blade_geo, "trigger_blade"), material=mats["rubber"], name="blade", material_class_id="rubber.smooth_plain")

    model.articulation(
        "housing_to_trigger",
        ArticulationType.REVOLUTE,
        parent=housing,
        child=trigger,
        origin=Origin(xyz=d.trigger_pivot),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=4.0, lower=0.0, upper=0.26),
    )
    return trigger


def _build_selector(model, housing, r, mats):
    d = r.dims
    selector = model.part("selector")
    selector.visual(
        Cylinder(radius=0.0048, length=0.046),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["charcoal"],
        name="pin", material_class_id="metal.blackened_gunmetal",
    )
    for i, side in enumerate((1.0, -1.0)):
        selector.visual(
            Cylinder(radius=0.0066, length=0.0050),
            origin=Origin(xyz=(0.0, side * 0.0240, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mats["charcoal"],
            name=f"cap_{i}", material_class_id="plastic.opaque_glossy_molded",
        )

    model.articulation(
        "housing_to_selector",
        ArticulationType.PRISMATIC,
        parent=housing,
        child=selector,
        origin=Origin(xyz=d.selector_pos),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=0.05, lower=-0.006, upper=0.006),
    )
    return selector


def _build_battery(model, housing, r, mats):
    # Battery visuals are authored in the battery child-link frame (local to the
    # seat origin); the housing_to_battery_pack joint origin places the pack
    # under the foot. Geometry mirrors the source records verbatim.
    d = r.dims
    interface = _rail_groove_interface(d, r.battery_mount)
    battery = model.part("battery_pack")
    seat = _battery_seat_origin(d, r.battery_mount)
    if r.battery_mount == "slide_on_stick":
        # Tall stick pack hanging below the foot rail (parent S1, battery frame).
        battery.visual(
            Box((0.080, 0.064, 0.0635)),
            origin=Origin(xyz=(0.001, 0.0, -0.03225)),
            material=mats["rubber"],
            name="shell", material_class_id="plastic.opaque_glossy_molded",
        )
        for i, y_off in enumerate(interface.rail_y):
            battery.visual(
                Box((interface.rail_len, interface.rail_w, interface.rail_h)),
                origin=Origin(xyz=(0.0, y_off, interface.rail_z_center)),
                material=mats["charcoal"],
                name=f"rail_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        for i, side in enumerate((1.0, -1.0)):
            battery.visual(
                Box((0.040, 0.0012, 0.013)),
                origin=Origin(xyz=(0.0, side * 0.0322, -0.028)),
                material=mats["label"],
                name=f"label_18v_{i}", appearance_only=AppearanceOnlySpec(kind="decal"),
            )
            battery.visual(
                Box((0.046, 0.0012, 0.006)),
                origin=Origin(xyz=(0.0, side * 0.0322, -0.044)),
                material=mats["label"],
                name=f"label_lithium_{i}", appearance_only=AppearanceOnlySpec(kind="decal"),
            )
        battery.visual(
            Box((0.007, 0.018, 0.009)),
            origin=Origin(xyz=(0.0415, 0.0, -0.010)),
            material=mats["charcoal"],
            name="release_latch", material_class_id="plastic.opaque_glossy_molded",
        )
    else:
        # flat_pod_slide: flat pod with two raised rails that slide into the
        # through-grooves cut into the drill foot underside.
        pod = cq.Workplane("XY").rect(0.078, 0.058).extrude(-0.038)
        try:
            pod = pod.edges("|Z").fillet(0.004)
        except Exception:
            pass
        try:
            pod = pod.edges("<Z").fillet(0.003)
        except Exception:
            pass
        battery.visual(
            mesh_from_cadquery(pod, "battery_pod_body"), material=mats["rubber"], name="pod_shell", material_class_id="plastic.opaque_glossy_molded"
        )
        for i, y_off in enumerate(interface.rail_y):
            battery.visual(
                Box((interface.rail_len, interface.rail_w, interface.rail_h)),
                origin=Origin(xyz=(0.0, y_off, interface.rail_z_center)),
                material=mats["charcoal"],
                name=f"rail_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        for i in range(3):
            battery.visual(
                Box((0.015, 0.042, 0.002)),
                origin=Origin(xyz=(-0.025 + i * 0.025, 0.0, -0.039)),
                material=mats["charcoal"],
                name=f"grip_pad_{i}", material_class_id="rubber.pebbled",
            )
        for i, side in enumerate((1.0, -1.0)):
            battery.visual(
                Box((0.040, 0.0012, 0.010)),
                origin=Origin(xyz=(0.0, side * 0.0292, -0.014)),
                material=mats["label"],
                name=f"label_18v_{i}", appearance_only=AppearanceOnlySpec(kind="decal"),
            )
            battery.visual(
                Box((0.046, 0.0012, 0.005)),
                origin=Origin(xyz=(0.0, side * 0.0292, -0.027)),
                material=mats["label"],
                name=f"label_lithium_{i}", appearance_only=AppearanceOnlySpec(kind="decal"),
            )
        battery.visual(
            Box((0.007, 0.018, 0.009)),
            origin=Origin(xyz=(0.040, 0.0, -0.010)),
            material=mats["charcoal"],
            name="release_latch", material_class_id="plastic.opaque_glossy_molded",
        )

    model.articulation(
        "housing_to_battery_pack",
        ArticulationType.PRISMATIC,
        parent=housing,
        child=battery,
        origin=Origin(xyz=seat),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.2, lower=0.0, upper=0.05),
    )
    return battery


# ===========================================================================
# Top-level builder
# ===========================================================================
def build_cordless_drill(
    config: CordlessDrillConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.palette_style]
    mats = {
        key: model.material(f"drill_{key}_{r.palette_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    housing = model.part("housing")
    _build_housing(model, housing, r, mats)
    _build_clutch_collar(model, housing, r, mats)
    _build_chuck(model, housing, r, mats)
    _build_trigger(model, housing, r, mats)
    _build_selector(model, housing, r, mats)
    _build_battery(model, housing, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_cordless_drill(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_cordless_drill(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_cordless_drill_tests(
    object_model: ArticulatedObject,
    config: CordlessDrillConfig,
) -> TestReport:
    r = resolve_config(config)
    d = r.dims
    ctx = TestContext(object_model)

    housing = object_model.get_part("housing")
    chuck = object_model.get_part("chuck")
    collar = object_model.get_part("clutch_collar")
    trigger = object_model.get_part("trigger")
    selector = object_model.get_part("selector")
    battery = object_model.get_part("battery_pack")

    spin_j = object_model.get_articulation("housing_to_chuck")
    clutch_j = object_model.get_articulation("housing_to_clutch_collar")
    trigger_j = object_model.get_articulation("housing_to_trigger")
    selector_j = object_model.get_articulation("housing_to_selector")
    battery_j = object_model.get_articulation("housing_to_battery_pack")

    # ---- intentional, scoped overlaps (captured geometry fits) -------------
    # The mating-allowance matcher needs BOTH element names specified (or both
    # None) to fire, so the captured spindle / collar lip overlaps are scoped to
    # each housing shell element explicitly.
    housing_shells = ("right_shell", "left_shell", "parting_seam")
    for shell in housing_shells:
        ctx.allow_overlap(
            housing, chuck, elem_a=shell, elem_b="spindle",
            reason="The steel spindle is captured in the gearbox bore at the housing front face.",
        )
        ctx.allow_overlap(
            housing, collar, elem_a=shell, elem_b="collar_body",
            reason="The clutch collar rear lip seats onto the housing nose so it reads mounted.",
        )
        ctx.allow_overlap(
            housing, trigger, elem_a=shell, elem_b="pivot_boss",
            reason="The trigger pivot boss is captured inside the grip recess.",
        )
        ctx.allow_overlap(
            housing, trigger, elem_a=shell, elem_b="blade",
            reason="The trigger blade top edge seats into the grip recess slot at rest.",
        )
        for elem in ("pin", "cap_0", "cap_1"):
            ctx.allow_overlap(
                housing, selector, elem_a=shell, elem_b=elem,
                reason="The forward/reverse selector pin passes through a bore in the housing.",
            )
    # Spindle passes through the clutch collar bore (captured shaft).
    ctx.allow_overlap(
        chuck, collar, elem_a="spindle", elem_b="collar_body",
        reason="The chuck spindle runs through the clutch collar bore.",
    )
    # Battery rails / dovetail engage the foot channel (full-part allowance).
    ctx.allow_overlap(
        housing, battery,
        reason="The battery pack slide interface is engaged inside the foot rail / dovetail.",
    )

    # ---- overall envelope is hand-tool scale -------------------------------
    parts = (housing, chuck, collar, trigger, selector, battery)
    mins = [1e9, 1e9, 1e9]
    maxs = [-1e9, -1e9, -1e9]
    for p in parts:
        bb = ctx.part_world_aabb(p)
        if bb is None:
            ctx.fail("part aabb available", f"no aabb for {p.name}")
            continue
        for k in range(3):
            mins[k] = min(mins[k], bb[0][k])
            maxs[k] = max(maxs[k], bb[1][k])
    length = maxs[0] - mins[0]
    width = maxs[1] - mins[1]
    height = maxs[2] - mins[2]
    max_length = 0.34 if r.bit_style == "twist_bit" else 0.30
    ctx.check(
        "overall length hand-tool scale",
        0.12 <= length <= max_length,
        f"length={length:.3f} max={max_length:.3f}",
    )
    ctx.check("overall height hand-tool scale", 0.10 <= height <= 0.26, f"height={height:.3f}")
    ctx.check("overall width hand-tool scale", 0.050 <= width <= 0.090, f"width={width:.3f}")

    # ---- front-end stackup: housing -> collar -> chuck ---------------------
    ctx.expect_origin_gap(
        chuck, collar, axis="x", min_gap=0.015, max_gap=0.045,
        name="chuck sits in front of the clutch collar",
    )
    ctx.expect_gap(
        chuck, collar, axis="x", positive_elem="chuck_sleeve", negative_elem="collar_body",
        min_gap=0.0005, max_gap=0.012, name="visible spindle gap between collar and chuck sleeve",
    )
    ctx.expect_overlap(
        chuck, collar, axes="x", elem_a="spindle", elem_b="collar_body", min_overlap=0.015,
        name="spindle passes through the clutch collar",
    )

    # ---- exposed steel jaw tips at the nose (jaw_count multiplicity) -------
    jaw_names = [v.name for v in chuck.visuals if v.name and v.name.startswith("jaw_")]
    ctx.check(
        "chuck emits jaw_count jaws (rigid in chuck, no per-jaw joint)",
        len(jaw_names) == r.jaw_count,
        details=f"emitted={sorted(jaw_names)} expected N={r.jaw_count}",
    )
    nose_front = ctx.part_element_world_aabb(chuck, elem="chuck_nose")
    nose_max_x = nose_front[1][0] if nose_front else 0.0
    for i in range(r.jaw_count):
        bb = ctx.part_element_world_aabb(chuck, elem=f"jaw_{i}")
        ctx.check(
            f"jaw_{i} exposed near the chuck nose",
            bb is not None and bb[1][0] > nose_max_x - 0.010,
            f"aabb={bb} nose_max_x={nose_max_x:.4f}",
        )
    bb_jaw0_face = ctx.part_element_world_aabb(chuck, elem="jaw_0")
    if bb_jaw0_face is not None:
        radial_z_span = bb_jaw0_face[1][2] - bb_jaw0_face[0][2]
        tangential_y_span = bb_jaw0_face[1][1] - bb_jaw0_face[0][1]
    else:
        radial_z_span = 0.0
        tangential_y_span = 0.0
    ctx.check(
        "chuck jaws read as radial gripping shoes, not square front patches",
        bb_jaw0_face is not None and radial_z_span > 0.008 and tangential_y_span < 0.006,
        f"jaw0_aabb={bb_jaw0_face} radial_z_span={radial_z_span:.4f} tangential_y_span={tangential_y_span:.4f}",
    )
    bit_core = ctx.part_element_world_aabb(chuck, elem="twist_bit_core")
    bit_tip = ctx.part_element_world_aabb(chuck, elem="twist_bit_tip")
    bit_flutes = ctx.part_element_world_aabb(chuck, elem="twist_bit_flutes")
    if r.bit_style == "twist_bit":
        ctx.check(
            "twist bit has core, pointed tip, and helical flute visuals",
            bit_core is not None and bit_tip is not None and bit_flutes is not None,
            f"core={bit_core} tip={bit_tip} flutes={bit_flutes}",
        )
        bit_len_world = (bit_tip[1][0] - bit_core[0][0]) if bit_core and bit_tip else 0.0
        bit_radius_world = (
            0.5 * max(bit_core[1][1] - bit_core[0][1], bit_core[1][2] - bit_core[0][2])
            if bit_core
            else 0.0
        )
        ctx.check(
            "twist bit projects well beyond the chuck nose as a slender drill bit",
            bit_tip is not None
            and bit_core is not None
            and bit_tip[1][0] > nose_max_x + 0.050
            and bit_len_world > 0.060
            and bit_radius_world < 0.006,
            f"nose_max_x={nose_max_x:.4f} bit_len={bit_len_world:.4f} bit_radius={bit_radius_world:.4f}",
        )
    else:
        ctx.check(
            "no standalone twist bit emitted for bit_style=none",
            bit_core is None and bit_tip is None and bit_flutes is None,
            f"core={bit_core} tip={bit_tip} flutes={bit_flutes}",
        )

    # ---- chuck spins CONTINUOUS about the drill axis (X) -------------------
    ctx.check(
        "chuck joint is CONTINUOUS about +X",
        spin_j.articulation_type == ArticulationType.CONTINUOUS
        and round(abs(spin_j.axis[0]), 3) == 1.0,
        details=f"type={spin_j.articulation_type} axis={tuple(spin_j.axis)}",
    )
    bb_jaw_rest = ctx.part_element_world_aabb(chuck, elem="jaw_0")
    with ctx.pose({spin_j: math.pi}):
        bb_jaw_flip = ctx.part_element_world_aabb(chuck, elem="jaw_0")
    cz_rest = 0.5 * (bb_jaw_rest[0][2] + bb_jaw_rest[1][2]) if bb_jaw_rest else 0.0
    cz_flip = 0.5 * (bb_jaw_flip[0][2] + bb_jaw_flip[1][2]) if bb_jaw_flip else 0.0
    ctx.check(
        "chuck jaw swings around the X axis when the spindle spins",
        bb_jaw_rest is not None and bb_jaw_flip is not None
        and cz_rest > d.barrel_z + 0.002 and cz_flip < d.barrel_z - 0.002,
        f"jaw0 z center rest={cz_rest:.4f}, half turn={cz_flip:.4f}",
    )

    # ---- clutch collar is REVOLUTE and twists between torque settings ------
    ctx.check(
        "clutch collar joint is REVOLUTE about +X",
        clutch_j.articulation_type == ArticulationType.REVOLUTE
        and round(abs(clutch_j.axis[0]), 3) == 1.0,
        details=f"type={clutch_j.articulation_type} axis={tuple(clutch_j.axis)}",
    )
    bb_ptr_rest = ctx.part_element_world_aabb(collar, elem="torque_pointer")
    with ctx.pose({clutch_j: 1.0}):
        bb_ptr_turn = ctx.part_element_world_aabb(collar, elem="torque_pointer")
    py_rest = 0.5 * (bb_ptr_rest[0][1] + bb_ptr_rest[1][1]) if bb_ptr_rest else 0.0
    py_turn = 0.5 * (bb_ptr_turn[0][1] + bb_ptr_turn[1][1]) if bb_ptr_turn else 0.0
    ctx.check(
        "torque pointer rotates with the clutch collar",
        bb_ptr_rest is not None and bb_ptr_turn is not None and abs(py_turn - py_rest) > 0.015,
        f"pointer y rest={py_rest:.4f}, turned={py_turn:.4f}",
    )

    # ---- detent ticks present (detent_count multiplicity) ------------------
    ticks_bb = ctx.part_element_world_aabb(collar, elem="setting_ticks")
    ctx.check(
        "clutch collar emits the merged detent tick ring",
        ticks_bb is not None,
        details=f"detent_count={r.detent_count} rib_count={r.rib_count}",
    )

    # ---- trigger is REVOLUTE and squeezes rearward into the grip -----------
    ctx.check(
        "trigger joint is REVOLUTE about +Y",
        trigger_j.articulation_type == ArticulationType.REVOLUTE
        and round(abs(trigger_j.axis[1]), 3) == 1.0,
        details=f"type={trigger_j.articulation_type} axis={tuple(trigger_j.axis)}",
    )
    ctx.expect_contact(trigger, housing, name="trigger is seated against the grip")
    bb_blade_rest = ctx.part_element_world_aabb(trigger, elem="blade")
    with ctx.pose({trigger_j: 0.26}):
        bb_blade_sq = ctx.part_element_world_aabb(trigger, elem="blade")
    ctx.check(
        "squeezed trigger blade swings rearward into the grip",
        bb_blade_rest is not None and bb_blade_sq is not None
        and bb_blade_sq[0][0] < bb_blade_rest[0][0] - 0.002,
        f"blade min x rest={bb_blade_rest}, squeezed={bb_blade_sq}",
    )

    # ---- forward/reverse selector is PRISMATIC and slides through housing --
    ctx.check(
        "selector joint is PRISMATIC about +Y",
        selector_j.articulation_type == ArticulationType.PRISMATIC
        and round(abs(selector_j.axis[1]), 3) == 1.0,
        details=f"type={selector_j.articulation_type} axis={tuple(selector_j.axis)}",
    )
    bb_sel = ctx.part_world_aabb(selector)
    ctx.check(
        "selector protrudes from both sides of the housing",
        bb_sel is not None and bb_sel[1][1] > 0.022 and bb_sel[0][1] < -0.022,
        f"selector aabb={bb_sel}",
    )
    p_sel_rest = ctx.part_world_position(selector)
    with ctx.pose({selector_j: 0.006}):
        p_sel_push = ctx.part_world_position(selector)
    ctx.check(
        "selector slides 6 mm sideways through the housing",
        p_sel_rest is not None and p_sel_push is not None
        and abs((p_sel_push[1] - p_sel_rest[1]) - 0.006) < 1e-6,
        f"selector y rest={p_sel_rest}, pushed={p_sel_push}",
    )

    # ---- battery pack is PRISMATIC and slides off the foot -----------------
    ctx.check(
        "battery joint is PRISMATIC about the X axis",
        battery_j.articulation_type == ArticulationType.PRISMATIC
        and round(abs(battery_j.axis[0]), 3) == 1.0,
        details=f"type={battery_j.articulation_type} axis={tuple(battery_j.axis)}",
    )
    ctx.expect_contact(battery, housing, name="battery slide interface engages the foot")
    p_bat_rest = ctx.part_world_position(battery)
    with ctx.pose({battery_j: 0.05}):
        p_bat_out = ctx.part_world_position(battery)
    ctx.check(
        "battery pack slides 50 mm rearward to detach",
        p_bat_rest is not None and p_bat_out is not None
        and abs((p_bat_rest[0] - p_bat_out[0]) - 0.05) < 1e-6,
        f"battery x rest={p_bat_rest}, released={p_bat_out}",
    )
    interface = _rail_groove_interface(d, r.battery_mount)
    ctx.check(
        "battery foot grooves run through the slide ends",
        interface.groove_len > interface.foot_len,
        f"groove_len={interface.groove_len:.4f} foot_len={interface.foot_len:.4f}",
    )
    groove_top_z = interface.foot_bottom_z + interface.groove_depth
    for i, expected_y in enumerate(interface.rail_y):
        bb = ctx.part_element_world_aabb(battery, elem=f"rail_{i}")
        cy = 0.5 * (bb[0][1] + bb[1][1]) if bb else 0.0
        ctx.check(
            f"battery rail_{i} is captured inside the drill foot groove",
            bb is not None
            and bb[0][2] >= interface.foot_bottom_z - 0.0005
            and bb[1][2] <= groove_top_z + 0.0005
            and abs(cy - expected_y) < 0.001,
            f"aabb={bb} groove_z=({interface.foot_bottom_z:.4f},{groove_top_z:.4f}) expected_y={expected_y:.3f}",
        )
        ctx.check(
            f"battery rail_{i} grows from the battery shell top",
            bb is not None
            and abs(bb[0][2] - (interface.foot_bottom_z + interface.body_top_z)) < 0.0003,
            f"rail_aabb={bb} shell_top_world_z={interface.foot_bottom_z + interface.body_top_z:.4f}",
        )

    # ---- mirrored shells, seam, overmold, vents identity -------------------
    bb_seam = ctx.part_element_world_aabb(housing, elem="parting_seam")
    ctx.check(
        "visible parting seam runs along the housing midplane",
        bb_seam is not None
        and (bb_seam[1][1] - bb_seam[0][1]) < 0.002
        and (bb_seam[1][2] - bb_seam[0][2]) > 0.06,
        f"seam aabb={bb_seam}",
    )
    for elem in ("right_shell", "left_shell"):
        bb = ctx.part_element_world_aabb(housing, elem=elem)
        ctx.check(f"{elem} present as a mirrored half", bb is not None, f"aabb={bb}")
    bb_om = ctx.part_element_world_aabb(housing, elem="top_overmold")
    ctx.check(
        "rubber overmold strip caps the motor housing top",
        bb_om is not None and bb_om[1][2] > d.barrel_z + d.barrel_r * r.body_scale,
        f"overmold aabb={bb_om}",
    )

    # ---- slot_choices recorded --------------------------------------------
    ctx.check(
        "slot_choices recorded (body_form/battery_mount/jaw/detent)",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # ---- baseline geometry gates ------------------------------------------
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_joint_mating_has_gap()

    return ctx.report()


__all__ = (
    "CordlessDrillConfig",
    "ResolvedCordlessDrillConfig",
    "build_cordless_drill",
    "build_seeded_cordless_drill",
    "config_from_seed",
    "resolve_config",
    "run_cordless_drill_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
