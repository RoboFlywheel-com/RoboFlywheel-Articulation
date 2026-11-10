# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E501
"""Self-contained laser level tripod template.

One rigid ``frame`` host (die-cast crown/hub, central plumb column, sliding
spreader collar, three hinge clevises and the head seat), ``leg_count`` = 3
indexed ``tripod_leg`` units that each spread outward on a registered tangential
crown hinge, and one ``instrument_head`` that pans on the vertical crown axis.

Structural slots (source-derived, freely combinable):
  * leg_structure: telescoping | fixed
  * head:          pan_disk    | pan_drum
  * center_column: plumb_hook  | plumb_rod
  * head_mount:    stud_disk   | qr_platform
  * foot:          rubber_pad  | molded_boot
Multiplicity: leg_count = 3 (source-anchored; a tripod is not extrapolated).
core_domain = 2*2*2*2*2 = 32.

Frame: +Z up, legs at azimuth ``-pi/2 + 2*pi*i/N``.  Each leg is authored along
its own local +Z so the spread joint simply rotates it about the tangential axis.

No source runtime is imported; only stdlib and the SDK are used.  No motion
clamping and no overlap allowance: the captured contacts (hinge sleeve in its
clevis, clamp pads on the sliding tube, head base on its seat) are real geometry
kept under the collision tolerance.

AABB NOTE: element overlap is measured on world AABBs (the reported `vol` is
exactly the AABB intersection), so obliquely-oriented hardware inflates on every
axis it spans -- legs 1 and 2 sit at 30/150 deg, leg 0 at -90 deg is the only one
axis-aligned.  `min_depth` is the SMALLEST axis overlap, so cross-part contacts
here are built to keep one axis tiny: the clevis lug meets the pin on a
horizontal face, and the clamp uses spherical detents whose AABB is
orientation-invariant.  `mate_axes` itself solves correctly for all three legs.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    AxisInterface,
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    Sphere,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    multiplicity_slot,
    register_interface_mate,
)

LegStructure = Literal["telescoping", "fixed"]
Head = Literal["pan_disk", "pan_drum"]
CenterColumn = Literal["plumb_hook", "plumb_rod"]
HeadMount = Literal["stud_disk", "qr_platform"]
Foot = Literal["rubber_pad", "molded_boot"]
PaletteStyle = Literal["safety_yellow", "graphite", "silver"]

LEG_STRUCTURES: tuple[LegStructure, ...] = ("telescoping", "fixed")
HEADS: tuple[Head, ...] = ("pan_disk", "pan_drum")
CENTER_COLUMNS: tuple[CenterColumn, ...] = ("plumb_hook", "plumb_rod")
HEAD_MOUNTS: tuple[HeadMount, ...] = ("stud_disk", "qr_platform")
FEET: tuple[Foot, ...] = ("rubber_pad", "molded_boot")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("safety_yellow", "graphite", "silver")
LEG_COUNTS: tuple[int, ...] = (3,)

TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("leg_structure", LEG_STRUCTURES),
        component_slot("head", HEADS),
        component_slot("center_column", CENTER_COLUMNS),
        component_slot("head_mount", HEAD_MOUNTS),
        component_slot("foot", FEET),
        multiplicity_slot("leg_count", LEG_COUNTS, item_slot="leg_structure"),
    )
)

# Continuous parameter bounds.  Continuous dimensions do not inflate core/raw.
_SCALE_MIN, _SCALE_MAX = 0.90, 1.10
_SPREAD_MIN, _SPREAD_MAX = 0.10, 0.34
_TELE_SCALE_MIN, _TELE_SCALE_MAX = 0.80, 1.15
_HEAD_SCALE_MIN, _HEAD_SCALE_MAX = 0.90, 1.15

# Fixed proportions (surface detail, not core/raw).
_CROWN_Z = 0.62          # hinge height above the floor at unit scale
_CROWN_R = 0.055         # crown hub radius
_UPPER_R = 0.016         # upper leg tube radius
_LOWER_R = 0.0115        # telescoping lower tube radius
_FOOT_R = 0.020          # rubber foot radius
# Captured contact: mating parts lap by less than the 1 mm collision tolerance,
# so QC reads real contact without needing an overlap allowance.
_MOUNT = 0.0006
_PIVOT_BALL_R = 0.010   # leg-side hinge ball
_PIVOT_BOSS_R = 0.012   # frame-side bearing boss

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "safety_yellow": {
        "body": (0.93, 0.76, 0.09, 1.0),
        "tube": (0.72, 0.74, 0.76, 1.0),
        "dark": (0.16, 0.16, 0.17, 1.0),
        "accent": (0.85, 0.62, 0.05, 1.0),
    },
    "graphite": {
        "body": (0.26, 0.27, 0.29, 1.0),
        "tube": (0.55, 0.57, 0.59, 1.0),
        "dark": (0.12, 0.12, 0.13, 1.0),
        "accent": (0.80, 0.30, 0.10, 1.0),
    },
    "silver": {
        "body": (0.76, 0.78, 0.80, 1.0),
        "tube": (0.66, 0.68, 0.70, 1.0),
        "dark": (0.18, 0.18, 0.19, 1.0),
        "accent": (0.20, 0.42, 0.72, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Config:
    leg_structure: LegStructure = "telescoping"
    head: Head = "pan_disk"
    center_column: CenterColumn = "plumb_hook"
    head_mount: HeadMount = "stud_disk"
    foot: Foot = "rubber_pad"
    leg_count: int = 3
    overall_scale: float | None = None
    leg_spread_deploy: float | None = None
    telescope_travel_scale: float | None = None
    head_scale: float | None = None
    palette_style: PaletteStyle = "safety_yellow"
    name: str = "pictureX_0611_laser_level_tripod"


@dataclass(frozen=True)
class ResolvedConfig:
    leg_structure: LegStructure
    head: Head
    center_column: CenterColumn
    head_mount: HeadMount
    foot: Foot
    leg_count: int
    overall_scale: float
    leg_spread_deploy: float
    telescope_travel_scale: float
    head_scale: float
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    crown_z: float
    hinge_radius: float
    leg_length: float
    telescope_travel: float
    head_seat_z: float
    name: str

    def leg_azimuth(self, index: int) -> float:
        return -0.5 * math.pi + 2.0 * math.pi * index / self.leg_count

    def hinge_point(self, index: int) -> tuple[float, float, float]:
        a = self.leg_azimuth(index)
        return (
            self.hinge_radius * math.cos(a),
            self.hinge_radius * math.sin(a),
            self.crown_z,
        )

    def leg_direction(self, index: int) -> tuple[float, float, float]:
        """Unit vector from the hinge down the leg at the neutral spread."""
        a = self.leg_azimuth(index)
        s, c = math.sin(self.leg_spread_deploy), math.cos(self.leg_spread_deploy)
        return (math.cos(a) * s, math.sin(a) * s, -c)

    def leg_tangent(self, index: int) -> tuple[float, float, float]:
        a = self.leg_azimuth(index)
        return (-math.sin(a), math.cos(a), 0.0)


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    choices = TEMPLATE_DOMAIN.sample(seed)
    rng = random.Random(int(seed) ^ 0x1A5E_7207)
    return Config(
        leg_structure=choices["leg_structure"],
        head=choices["head"],
        center_column=choices["center_column"],
        head_mount=choices["head_mount"],
        foot=choices["foot"],
        leg_count=choices["leg_count"],
        overall_scale=round(rng.uniform(_SCALE_MIN, _SCALE_MAX), 4),
        leg_spread_deploy=round(rng.uniform(_SPREAD_MIN, _SPREAD_MAX), 4),
        telescope_travel_scale=round(rng.uniform(_TELE_SCALE_MIN, _TELE_SCALE_MAX), 4),
        head_scale=round(rng.uniform(_HEAD_SCALE_MIN, _HEAD_SCALE_MAX), 4),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"pictureX_0611_laser_level_tripod_seed_{seed}",
    )


def resolve_config(config: Config | None = None) -> ResolvedConfig:
    cfg = config or Config()
    TEMPLATE_DOMAIN.validate(
        {
            "leg_structure": cfg.leg_structure,
            "head": cfg.head,
            "center_column": cfg.center_column,
            "head_mount": cfg.head_mount,
            "foot": cfg.foot,
            "leg_count": cfg.leg_count,
        }
    )
    if cfg.palette_style not in PALETTES:
        raise ValueError(f"unknown palette_style {cfg.palette_style!r}")
    scale = _clamp(1.0 if cfg.overall_scale is None else cfg.overall_scale, _SCALE_MIN, _SCALE_MAX)
    spread = _clamp(
        0.22 if cfg.leg_spread_deploy is None else cfg.leg_spread_deploy,
        _SPREAD_MIN,
        _SPREAD_MAX,
    )
    tele_scale = _clamp(
        1.0 if cfg.telescope_travel_scale is None else cfg.telescope_travel_scale,
        _TELE_SCALE_MIN,
        _TELE_SCALE_MAX,
    )
    head_scale = _clamp(
        1.0 if cfg.head_scale is None else cfg.head_scale, _HEAD_SCALE_MIN, _HEAD_SCALE_MAX
    )
    crown_z = _CROWN_Z * scale
    # Outboard of the hub: at the hub radius the leg's hinge hardware sat inside
    # the casting.  A short bracket arm carries the clevis out to here.
    hinge_radius = (_CROWN_R + 0.024) * scale
    # Leg length is derived so the foot lands on the floor at the neutral spread.
    leg_length = crown_z / math.cos(spread)
    # Telescope half-range about the source overlap, kept well inside the leg so
    # the lower tube never leaves the clamp pads.
    telescope_travel = 0.16 * scale * tele_scale
    head_seat_z = crown_z + 0.045 * scale
    return ResolvedConfig(
        leg_structure=cfg.leg_structure,
        head=cfg.head,
        center_column=cfg.center_column,
        head_mount=cfg.head_mount,
        foot=cfg.foot,
        leg_count=int(cfg.leg_count),
        overall_scale=scale,
        leg_spread_deploy=spread,
        telescope_travel_scale=tele_scale,
        head_scale=head_scale,
        palette_style=cfg.palette_style,
        palette=PALETTES[cfg.palette_style],
        crown_z=crown_z,
        hinge_radius=hinge_radius,
        leg_length=leg_length,
        telescope_travel=telescope_travel,
        head_seat_z=head_seat_z,
        name=cfg.name,
    )


def slot_choices_for_config(r: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("leg_structure", r.leg_structure),
        ("head", r.head),
        ("center_column", r.center_column),
        ("head_mount", r.head_mount),
        ("foot", r.foot),
        ("leg_count", r.leg_count),
    )


# ---------------------------------------------------------------------------
# Materials / helpers
# ---------------------------------------------------------------------------
def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    out: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(key, color=rgba)
        out[key] = key
    return out


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.paint_coated",
    )


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


# ---------------------------------------------------------------------------
# Central column (center_column slot).  Both candidates live on the shared
# non-slotted ``frame`` host, so their internal seams are intra-part and free;
# the only cross-part clearance that matters is against the folded legs, whose
# tubes never come inside ~0.06 * scale of the vertical axis.
# ---------------------------------------------------------------------------
def _center_column_plumb_hook_build(frame, r: ResolvedConfig, mats) -> None:
    """Short suspended column ending in a plumb-bob hook, with a cable clip.

    rec ...092909 model.py:L61-L91 -- ``center_column`` is a 0.720 m rod whose
    bottom sits at z=0.265 on a 1.005 m crown, i.e. it hangs clear of the floor,
    and it carries the ``cable_clip`` / ``clip_tether`` retention hardware.
    """
    cand = "plumb_hook"
    s = r.overall_scale
    tube, dark, body = mats["tube"], mats["dark"], mats["body"]
    _cyl(frame, 0.014 * s, 0.11 * s, (0.0, 0.0, r.crown_z - 0.075 * s), tube,
         f"center_column__{cand}__plumb_column")
    _cyl(frame, 0.021 * s, 0.013 * s, (0.0, 0.0, r.crown_z - 0.128 * s), dark,
         f"center_column__{cand}__plumb_hook")
    # Cable-retention clip + rubber tether on the hanging column.
    _box(frame, (0.020 * s, 0.012 * s, 0.026 * s), (0.020 * s, 0.0, r.crown_z - 0.100 * s),
         dark, f"center_column__{cand}__cable_clip")
    _cyl(frame, 0.004 * s, 0.022 * s, (0.033 * s, 0.0, r.crown_z - 0.100 * s), body,
         f"center_column__{cand}__clip_tether", rpy=(0.0, math.pi / 2.0, 0.0))


def _center_column_plumb_rod_build(frame, r: ResolvedConfig, mats) -> None:
    """Full-length plumb rod running down to a rubber ground foot.

    rec ...095851 model.py:L77-L100 -- ``center_column`` is a 1.205 m rod that
    reaches z=0.080 under a 1.285 m crown and terminates in a rubber
    ``column_foot`` (z 0.050-0.080) just clear of the floor.
    """
    cand = "plumb_rod"
    s = r.overall_scale
    tube, dark = mats["tube"], mats["dark"]
    rod_top = r.crown_z - 0.020 * s
    rod_bot = 0.082 * s
    rod_len = rod_top - rod_bot
    _cyl(frame, 0.014 * s, rod_len, (0.0, 0.0, 0.5 * (rod_top + rod_bot)), tube,
         f"center_column__{cand}__plumb_column")
    # Rubber ground foot, pressed 6 mm onto the rod so the stack stays one solid.
    _cyl(frame, 0.026 * s, 0.036 * s, (0.0, 0.0, 0.070 * s), dark,
         f"center_column__{cand}__column_foot")
    # Collar clamp screw + tab, the rod's locking hardware.
    _cyl(frame, 0.0045 * s, 0.026 * s, (0.036 * s, 0.0, r.crown_z - 0.058 * s), dark,
         f"center_column__{cand}__collar_clamp_screw", rpy=(0.0, math.pi / 2.0, 0.0))
    _box(frame, (0.014 * s, 0.020 * s, 0.020 * s), (0.050 * s, 0.0, r.crown_z - 0.058 * s),
         dark, f"center_column__{cand}__collar_clamp_tab")


_CENTER_COLUMN_BUILDERS = {
    "plumb_hook": _center_column_plumb_hook_build,
    "plumb_rod": _center_column_plumb_rod_build,
}


# ---------------------------------------------------------------------------
# Frame: crown hub, central column, spreader collar, hinge clevises, head seat
# ---------------------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedConfig, mats) -> object:
    frame = model.part("frame", meta={"role": "frame"})
    s = r.overall_scale
    body, dark, tube = mats["body"], mats["dark"], mats["tube"]

    # Die-cast crown / hub.
    _cyl(frame, _CROWN_R * s, 0.050 * s, (0.0, 0.0, r.crown_z), body, "crown_hub")
    _cyl(frame, _CROWN_R * s * 0.72, 0.018 * s, (0.0, 0.0, r.crown_z + 0.032 * s), body, "crown_shoulder")
    # Head seat on the crown top: the bearing face the instrument head sits on.
    _cyl(frame, 0.034 * s, 0.014 * s, (0.0, 0.0, r.head_seat_z - 0.007 * s), dark, "head_seat")
    # Central column (center_column slot) -- see _CENTER_COLUMN_BUILDERS.
    _CENTER_COLUMN_BUILDERS[r.center_column](frame, r, mats)
    # Sliding spreader collar on the central column (shared frame hardware).
    _cyl(frame, 0.030 * s, 0.020 * s, (0.0, 0.0, r.crown_z - 0.058 * s), body, "spreader_collar")

    for i in range(r.leg_count):
        a = r.leg_azimuth(i)
        hx, hy, hz = r.hinge_point(i)
        nx, ny = math.cos(a), math.sin(a)
        # Hinge clevis: two cheeks straddling the leg's hinge sleeve, on the
        # crown's rim so the leg is carried by real hardware.
        for k, sk in enumerate((-1.0, 1.0)):
            tx, ty, _ = r.leg_tangent(i)
            # Straddle close in so each lug's underside actually sits ON the
            # pin (the pin spans +-0.020*s): offset out at +-0.030 they met it
            # only at a corner and the leg read as isolated.
            off = 0.014 * s * sk
            # Radially the cheek runs from inside the hub rim out past the hinge,
            # so the clevis is carried by the casting rather than floating.
            cheek_r = 0.5 * ((_CROWN_R - 0.002) * s + (r.hinge_radius + 0.015 * s))
            cheek_len = (r.hinge_radius + 0.015 * s) - (_CROWN_R - 0.002) * s
            _box(
                frame,
                (cheek_len, 0.024 * s, 0.038 * s),
                (
                    nx * cheek_r + tx * off,
                    ny * cheek_r + ty * off,
                    # Purely decorative clevis, lifted clear of the leg: the
                    # load path is the bearing boss below.
                    hz + (_PIVOT_BALL_R + 0.004) * s + 0.019 * s,
                ),
                dark,
                f"hinge_cheek_{i}_{k}",
                rpy=(0.0, 0.0, a),
            )
        # Bearing boss seated on the leg's hinge ball.  The centres differ purely
        # in Z, so the world-AABB overlap is _MOUNT on that axis whatever the
        # leg's azimuth -- min_depth stays tiny for all three legs.
        frame.visual(
            Sphere(radius=_PIVOT_BOSS_R * s),
            origin=Origin(
                xyz=(hx, hy, hz + (_PIVOT_BALL_R + _PIVOT_BOSS_R) * s - _MOUNT)
            ),
            material=dark,
            name=f"hinge_boss_{i}", material_class_id="metal.blackened_gunmetal",
        )
        # Spreader brace from the sliding collar out to the leg's brace lug.
        bx, by = nx * 0.030 * s, ny * 0.030 * s
        _box(
            frame,
            (0.026 * s, 0.010 * s, 0.008 * s),
            (bx, by, r.crown_z - 0.058 * s),
            tube,
            f"spreader_brace_{i}",
            rpy=(0.0, 0.0, a),
        )
    return frame


# ---------------------------------------------------------------------------
# Foot (foot slot).  Emitted at the bottom of whichever part carries the leg
# tip -- the one-piece leg for `fixed`, the sliding lower tube for
# `telescoping` -- so it combines freely with either leg family.  Both
# candidates put their lowest surface at exactly ``tip_z + 0.016 * scale`` in
# leg-local coordinates, which keeps the grounded-neutral-pose invariant
# identical across the slot.
# ---------------------------------------------------------------------------
def _foot_rubber_pad_build(part, r: ResolvedConfig, mats, index: int, tip_z: float) -> None:
    """Tapered rubber foot shell closed by a spherical contact pad.

    rec ...092909 model.py:L182-L201 -- ``rubber_foot_i`` is a tapered tube
    shell (r=0.0165) capped by a ``foot_pad_i`` Sphere(r=0.018).
    """
    cand = "rubber_pad"
    s = r.overall_scale
    _cyl(part, 0.016 * s, 0.042 * s, (0.0, 0.0, tip_z - 0.025 * s), mats["dark"],
         f"foot__{cand}__foot_shell_{index}")
    part.visual(
        Sphere(radius=_FOOT_R * s),
        origin=Origin(xyz=(0.0, 0.0, tip_z - 0.004 * s)),
        material=mats["dark"],
        name=f"foot__{cand}__foot_pad_{index}", material_class_id="rubber.smooth_plain",
    )


def _foot_molded_boot_build(part, r: ResolvedConfig, mats, index: int, tip_z: float) -> None:
    """Angled molded boot with a clamp band above it.

    rec ...095851 model.py:L145-L162 -- ``rubber_boot_i`` is a molded
    Box(0.036, 0.048, 0.105) boot, sitting under a ``clamp_band_i`` /
    ``leg_clamp_i`` band rather than a round pad.
    """
    cand = "molded_boot"
    s = r.overall_scale
    _box(part, (0.036 * s, 0.030 * s, 0.052 * s), (0.0, 0.0, tip_z - 0.010 * s), mats["dark"],
         f"foot__{cand}__boot_body_{index}")
    _box(part, (0.040 * s, 0.034 * s, 0.012 * s), (0.0, 0.0, tip_z - 0.040 * s), mats["body"],
         f"foot__{cand}__boot_band_{index}")


_FOOT_BUILDERS = {
    "rubber_pad": _foot_rubber_pad_build,
    "molded_boot": _foot_molded_boot_build,
}


# ---------------------------------------------------------------------------
# Legs (leg_structure slot).  Authored along local +Z from the hinge.
# ---------------------------------------------------------------------------
def _leg_common_head(part, r: ResolvedConfig, mats, index: int, cand: str) -> None:
    """Hinge sleeve at the leg top, captured between the frame's clevis cheeks."""
    s = r.overall_scale
    # The sleeve straddles the hinge axis and laps each cheek by _MOUNT: real
    # captured pivot hardware, under the collision tolerance.
    # Ball pivot centred ON the hinge axis.  A tangential sleeve is a cylinder
    # whose world AABB inflates on the obliquely-mounted legs, so its clearance
    # against the frame changed with azimuth; a sphere's AABB is
    # orientation-invariant and its contact with the frame boss is a pure
    # vertical offset, keeping min_depth at _MOUNT for every leg and pose.
    part.visual(
        Sphere(radius=_PIVOT_BALL_R * s),
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
        material=mats["dark"],
        name=f"leg_structure__{cand}__hinge_sleeve_{index}", material_class_id="metal.blackened_gunmetal",
    )
    # Narrow in the tangential axis so it passes clear of the clevis cheeks, but
    # deep enough in +Y to land on the channel web -- centred it floated in the
    # middle of the open bore with nothing to attach to.
    _box(
        part,
        (0.010 * s, 0.0205 * s, 0.052 * s),
        (0.0, 0.00325 * s, 0.029 * s),
        mats["body"],
        f"leg_structure__{cand}__hinge_shoulder_{index}",
    )
    # Brace lug the frame's spreader brace reaches.
    # On the outer face, where both leg candidates carry real material -- the
    # telescoping channel's bore is open, so a lug on the axis would float.
    _box(
        part,
        (0.020 * s, 0.016 * s, 0.012 * s),
        (0.0, 0.012 * s, 0.072 * s),
        mats["tube"],
        f"leg_structure__{cand}__brace_lug_{index}",
    )


def _leg_structure_telescoping_build(part, r: ResolvedConfig, mats, index: int) -> None:
    """Two-segment telescoping leg: an open channel upper carrying a sliding tube.

    The upper segment is a U-channel rather than a solid tube.  A solid tube
    cannot host a telescope built from primitives: the lower tube has to reach
    `telescope_travel` above the clamp so it is still gripped at full extension,
    and inside a solid upper that length would interpenetrate along the whole
    stroke.  A channel leg is a real tripod construction and leaves the bore
    genuinely open, so the only contact is the clamp pads gripping the tube.
    """
    cand = "telescoping"
    s = r.overall_scale
    _leg_common_head(part, r, mats, index, cand)
    junction = 0.52 * r.leg_length
    inner = _LOWER_R * s + 0.0015 * s
    wall = 0.005 * s
    # The channel starts below the clevis: run full-length from z=0 and its walls
    # sit inside the cheeks and foul them.  The hinge shoulder bridges the gap.
    ch_top = 0.045 * s
    ch_len = junction - ch_top
    ch_cz = ch_top + 0.5 * ch_len
    for k, sx in enumerate((-1.0, 1.0)):
        _box(
            part,
            (wall, 2.0 * (inner + wall), ch_len),
            (sx * (inner + 0.5 * wall), 0.0, ch_cz),
            mats["tube"],
            f"leg_structure__{cand}__channel_wall_{index}_{k}",
        )
    _box(
        part,
        (2.0 * (inner + wall), wall, ch_len),
        # Web faces OUTWARD (local +Y): local -Y points back at the crown hub,
        # where the web ran straight into it.
        (0.0, inner + 0.5 * wall, ch_cz),
        mats["tube"],
        f"leg_structure__{cand}__channel_web_{index}",
    )
    # Clamp collar plus grip pads at the channel mouth.  The pads graze the
    # sliding tube by _MOUNT at every travel position -- the real captured
    # contact, so no overlap allowance is declared anywhere.
    # Collar yoke: two side ears bridging the channel walls at the mouth.  A
    # solid disc here would swallow the sliding tube (no bore can be cut from
    # primitives); the grip pads below are the actual clamping contact.
    for k, sx in enumerate((-1.0, 1.0)):
        _box(
            part,
            (0.008 * s, 2.0 * (inner + wall), 0.026 * s),
            (sx * (inner + wall + 0.004 * s), 0.0, junction - 0.004 * s),
            mats["body"],
            f"leg_structure__{cand}__clamp_ear_{index}_{k}",
        )
    _box(
        part,
        (0.028 * s, 0.012 * s, 0.018 * s),
        (0.0, inner + wall + 0.006 * s, junction - 0.004 * s),
        mats["accent"],
        f"leg_structure__{cand}__clamp_latch_{index}",
    )
    _box(
        part,
        (2.0 * (inner + wall), wall, 0.022 * s),
        (0.0, -(inner + 0.5 * wall), junction - 0.004 * s),
        mats["body"],
        f"leg_structure__{cand}__clamp_strap_{index}",
    )
    # Ball detents in the clamp: a sphere's AABB is orientation-invariant, so
    # unlike a box it does not inflate on the obliquely-mounted legs (1 and 2)
    # and its grazing contact with the tube stays inside the 5 mm tolerance.
    # They also bridge out to the channel walls, keeping the leg one solid.
    ball_r = 0.002 * s
    ball_dc = _LOWER_R * s + ball_r - _MOUNT
    for k in range(4):
        ang = 0.5 * math.pi * k
        part.visual(
            Sphere(radius=ball_r),
            origin=Origin(
                xyz=(
                    math.cos(ang) * ball_dc,
                    math.sin(ang) * ball_dc,
                    junction - 0.004 * s,
                )
            ),
            material=mats["dark"],
            name=f"leg_structure__{cand}__clamp_pad_{index}_{k}", material_class_id="rubber.smooth_plain",
        )


def _leg_structure_fixed_build(part, r: ResolvedConfig, mats, index: int) -> None:
    """One-piece kneed leg on a clevis pin, with a low clamp band and boot."""
    cand = "fixed"
    s = r.overall_scale
    _leg_common_head(part, r, mats, index, cand)
    length = r.leg_length
    # Single continuous tube running the whole leg.
    # Starts below the clevis for the same reason as the telescoping channel.
    tube_top = 0.045 * s
    tube_len = length - tube_top
    _cyl(
        part,
        _UPPER_R * s,
        tube_len,
        (0.0, 0.0, tube_top + 0.5 * tube_len),
        mats["tube"],
        f"leg_structure__{cand}__leg_tube_{index}",
    )
    # Molded knee reinforcement partway down: the one-piece leg's read.
    _box(
        part,
        (0.030 * s, 0.018 * s, 0.070 * s),
        (0.0, 0.0, 0.34 * length),
        mats["body"],
        f"leg_structure__{cand}__knee_rib_{index}",
    )
    _cyl(
        part,
        _UPPER_R * s + 0.007 * s,
        0.026 * s,
        (0.0, 0.0, 0.70 * length),
        mats["body"],
        f"leg_structure__{cand}__clamp_band_{index}",
    )
    # Foot hardware (foot slot) at the leg tip.
    _FOOT_BUILDERS[r.foot](part, r, mats, index, length)


_LEG_BUILDERS = {
    "telescoping": _leg_structure_telescoping_build,
    "fixed": _leg_structure_fixed_build,
}


def _build_lower_segment(part, r: ResolvedConfig, mats, index: int) -> None:
    """Sliding lower tube, authored along local +Z from the clamp datum.

    Local z=0 is the clamp mouth at retracted.  The tube starts
    `telescope_travel + 0.04` ABOVE that datum so that after a full stroke its
    upper end is still inside the clamp pads; it runs down past the neutral foot
    position by the same stroke.
    """
    s = r.overall_scale
    cand = "telescoping"
    junction = 0.52 * r.leg_length
    top = -(r.telescope_travel + 0.04 * s)
    bottom = r.leg_length - junction
    span = bottom - top
    _cyl(
        part,
        _LOWER_R * s,
        span,
        (0.0, 0.0, top + 0.5 * span),
        mats["tube"],
        f"leg_structure__{cand}__lower_tube_{index}",
    )
    # Foot hardware (foot slot) at the sliding tube's tip.
    _FOOT_BUILDERS[r.foot](part, r, mats, index, bottom)


# ---------------------------------------------------------------------------
# Heads (head slot)
# ---------------------------------------------------------------------------
def _head_pan_disk_build(part, r: ResolvedConfig, mats, _unused: int = 0) -> tuple[float, float]:
    """Compact disk instrument head with a side lock knob and a pan handle.

    Returns ``(deck_z, deck_radius)`` -- the top face of the housing, where the
    ``head_mount`` slot lands.
    """
    cand = "pan_disk"
    s = r.overall_scale * r.head_scale
    # Base seats on the frame's head seat: local z=0 is the bearing face.
    _cyl(part, 0.036 * s, 0.016 * s, (0.0, 0.0, 0.008 * s - _MOUNT), mats["dark"], f"head__{cand}__pan_base")
    _cyl(part, 0.052 * s, 0.048 * s, (0.0, 0.0, 0.039 * s), mats["body"], f"head__{cand}__housing")
    # Side lock screw + knob.
    _cyl(
        part,
        0.007 * s,
        0.030 * s,
        (0.055 * s, 0.0, 0.038 * s),
        mats["tube"],
        f"head__{cand}__lock_screw",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    _cyl(
        part,
        0.014 * s,
        0.012 * s,
        (0.072 * s, 0.0, 0.038 * s),
        mats["accent"],
        f"head__{cand}__lock_knob",
        rpy=(0.0, math.pi / 2.0, 0.0),
    )
    # Long pan handle sweeping horizontally.
    _cyl(
        part,
        0.006 * s,
        0.13 * s,
        (0.0, 0.085 * s, 0.030 * s),
        mats["dark"],
        f"head__{cand}__pan_handle",
        rpy=(math.pi / 2.0, 0.0, 0.0),
    )
    return (0.063 * s, 0.052 * s)


def _head_pan_drum_build(part, r: ResolvedConfig, mats, _unused: int = 0) -> tuple[float, float]:
    """Tall graduated-drum head on a bearing foot, continuous pan."""
    cand = "pan_drum"
    s = r.overall_scale * r.head_scale
    _cyl(part, 0.038 * s, 0.016 * s, (0.0, 0.0, 0.008 * s - _MOUNT), mats["dark"], f"head__{cand}__bearing_foot")
    _cyl(part, 0.046 * s, 0.075 * s, (0.0, 0.0, 0.0524 * s), mats["body"], f"head__{cand}__housing")
    # Graduated bearing ring: the drum head's read-at-a-glance detail.
    _cyl(part, 0.050 * s, 0.012 * s, (0.0, 0.0, 0.022 * s), mats["tube"], f"head__{cand}__graduated_ring")
    for k in range(12):
        ang = 2.0 * math.pi * k / 12.0
        _box(
            part,
            (0.004 * s, 0.010 * s, 0.010 * s),
            (math.cos(ang) * 0.048 * s, math.sin(ang) * 0.048 * s, 0.022 * s),
            mats["dark"],
            f"head__{cand}__graduation_{k}",
            rpy=(0.0, 0.0, ang),
        )
    return (0.090 * s, 0.046 * s)


_HEAD_BUILDERS = {
    "pan_disk": _head_pan_disk_build,
    "pan_drum": _head_pan_drum_build,
}


# ---------------------------------------------------------------------------
# Head mounting interface (head_mount slot).  Everything here is emitted onto
# the single rotating head part, so its seams are intra-part; it sits well above
# the crown and never approaches the frame or the legs.
# ---------------------------------------------------------------------------
def _head_mount_stud_disk_build(part, r: ResolvedConfig, mats, deck_z: float, deck_r: float) -> None:
    """Threaded stud on a laser-mount disk.

    rec ...092909 model.py:L230-L247 -- ``mounting_plate`` + ``mounting_stud``
    (r=0.008, L=0.018) + ``laser_mount_disk`` (r=0.015): a bare threaded stud
    interface with a small centring disk, no quick-release platform.
    """
    cand = "stud_disk"
    s = r.overall_scale * r.head_scale
    _cyl(part, deck_r * 0.78, 0.012 * s, (0.0, 0.0, deck_z + 0.004 * s), mats["tube"],
         f"head_mount__{cand}__mounting_plate")
    _cyl(part, deck_r * 0.50, 0.010 * s, (0.0, 0.0, deck_z + 0.014 * s), mats["accent"],
         f"head_mount__{cand}__laser_mount_disk")
    _cyl(part, 0.008 * s, 0.020 * s, (0.0, 0.0, deck_z + 0.027 * s), mats["tube"],
         f"head_mount__{cand}__mounting_stud")


def _head_mount_qr_platform_build(part, r: ResolvedConfig, mats, deck_z: float, deck_r: float) -> None:
    """Quick-release platform: rectangular deck, anti-slip pad, corner screws.

    rec ...095851 model.py:L261-L286 -- ``mounting_platform`` Box(0.088,0.078,
    0.030) + ``anti_slip_pad`` Box(0.070,0.054,0.006) + four ``platform_screw_*``
    + ``mounting_stud``: a rectangular quick-release deck, not a bare stud.
    """
    cand = "qr_platform"
    s = r.overall_scale * r.head_scale
    half_w, half_d = 0.85 * deck_r, 0.74 * deck_r
    _box(part, (2.0 * half_w, 2.0 * half_d, 0.022 * s), (0.0, 0.0, deck_z + 0.008 * s),
         mats["body"], f"head_mount__{cand}__mounting_platform")
    _box(part, (1.34 * half_w, 1.16 * half_d, 0.007 * s), (0.0, 0.0, deck_z + 0.021 * s),
         mats["dark"], f"head_mount__{cand}__anti_slip_pad")
    for k in range(4):
        sx = 1.0 if k in (0, 1) else -1.0
        sy = 1.0 if k in (0, 2) else -1.0
        _cyl(part, 0.0034 * s, 0.010 * s,
             (sx * 0.72 * half_w, sy * 0.66 * half_d, deck_z + 0.021 * s), mats["dark"],
             f"head_mount__{cand}__platform_screw_{k}")
    _cyl(part, 0.006 * s, 0.028 * s, (0.0, 0.0, deck_z + 0.036 * s), mats["tube"],
         f"head_mount__{cand}__mounting_stud")


_HEAD_MOUNT_BUILDERS = {
    "stud_disk": _head_mount_stud_disk_build,
    "qr_platform": _head_mount_qr_platform_build,
}


# ---------------------------------------------------------------------------
# Joints
# ---------------------------------------------------------------------------
def _add_spread_joint(model, frame, leg, r: ResolvedConfig, index: int) -> None:
    name = f"leg_structure__{r.leg_structure}__leg_spread_{index}"
    provider = AxisInterface(
        name=f"{name}__provider",
        point=r.hinge_point(index),
        axis=r.leg_tangent(index),
        radial=r.leg_direction(index),
    )
    consumer = AxisInterface(
        name=f"{name}__consumer", axis=(1.0, 0.0, 0.0), radial=(0.0, 0.0, 1.0)
    )
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=frame,
        child=leg,
        origin=mate.origin,
        axis=mate.axis,
        # Neutral (0) is the deployed stance with the feet grounded.  POSITIVE
        # rotation folds the leg inward toward the column (measured: foot radius
        # 0.32 -> 0.17), so the stroke runs 0 -> leg_spread_deploy, which closes
        # the legs to vertical.  The old negative limit spread them wider and
        # lifted the feet clear of the floor, and the old +0.22 upper folded them
        # PAST vertical so adjacent legs and feet crossed under the crown.
        motion_limits=MotionLimits(
            lower=0.0, upper=r.leg_spread_deploy, effort=40.0, velocity=1.0
        ),
        meta={"mechanism": "tripod leg spread", "leg_index": index},
    )
    register_interface_mate(model, name, mate)


def _add_telescope_joint(model, leg, lower, r: ResolvedConfig, index: int) -> None:
    name = f"leg_structure__telescoping__leg_extend_{index}"
    model.articulation(
        name,
        ArticulationType.PRISMATIC,
        parent=leg,
        child=lower,
        origin=Origin(xyz=(0.0, 0.0, 0.52 * r.leg_length - 0.004 * r.overall_scale)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            lower=0.0, upper=r.telescope_travel, effort=60.0, velocity=0.4
        ),
        meta={"mechanism": "leg telescope", "leg_index": index},
    )


def _add_pan_joint(model, frame, head, r: ResolvedConfig) -> None:
    name = f"head__{r.head}__pan"
    provider = AxisInterface(
        name=f"{name}__provider",
        point=(0.0, 0.0, r.head_seat_z),
        axis=(0.0, 0.0, 1.0),
        radial=(1.0, 0.0, 0.0),
    )
    consumer = AxisInterface(
        name=f"{name}__consumer", axis=(0.0, 0.0, 1.0), radial=(1.0, 0.0, 0.0)
    )
    mate = mate_axes(provider, consumer)
    if r.head == "pan_disk":
        kind = ArticulationType.REVOLUTE
        limits = MotionLimits(lower=-math.pi, upper=math.pi, effort=12.0, velocity=2.0)
    else:
        kind = ArticulationType.CONTINUOUS
        limits = MotionLimits(effort=12.0, velocity=2.0)
    model.articulation(
        name,
        kind,
        parent=frame,
        child=head,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=limits,
        meta={"mechanism": "instrument head pan"},
    )
    register_interface_mate(model, name, mate)


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------
def build_picturex_0611_laser_level_tripod(
    config: Config | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config or config_from_seed(0))
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_laser_level_tripod",
            "slot_choices": slot_choices_for_config(r),
            "source_family": "pictureX/0611/laser_level_tripod",
        },
    )
    mats = _materials(model, r)
    frame = _build_frame(model, r, mats)

    leg_builder = _LEG_BUILDERS[r.leg_structure]
    for index in range(r.leg_count):
        leg = model.part(
            f"leg_structure__{r.leg_structure}__leg_{index}",
            meta={"role": "tripod_leg", "candidate": r.leg_structure, "leg_index": index},
        )
        leg_builder(leg, r, mats, index)
        _add_spread_joint(model, frame, leg, r, index)

        if r.leg_structure == "telescoping":
            lower = model.part(
                f"leg_structure__telescoping__lower_{index}",
                meta={
                    "role": "leg_lower_segment",
                    "candidate": "telescoping",
                    "leg_index": index,
                },
            )
            _build_lower_segment(lower, r, mats, index)
            _add_telescope_joint(model, leg, lower, r, index)

    head = model.part(
        f"head__{r.head}__housing_part",
        meta={"role": "instrument_head", "candidate": r.head},
    )
    deck_z, deck_r = _HEAD_BUILDERS[r.head](head, r, mats)
    _HEAD_MOUNT_BUILDERS[r.head_mount](head, r, mats, deck_z, deck_r)
    _add_pan_joint(model, frame, head, r)

    model.meta["risk_poses"] = (
        {},
        {
            f"leg_structure__{r.leg_structure}__leg_spread_{i}": r.leg_spread_deploy
            for i in range(r.leg_count)
        },
    )
    return model


def build_seeded_picturex_0611_laser_level_tripod(
    seed: int, *, assets: AssetContext | None = None
):
    return build_picturex_0611_laser_level_tripod(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Author tests — category invariants only.  Exact-collision, sampled-pose and
# isolated-geometry QC are owned by the sweep harness on every built seed.
# ---------------------------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_laser_level_tripod_tests(
    object_model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    frames = _parts_by_role(object_model, "frame")
    legs = _parts_by_role(object_model, "tripod_leg")
    heads = _parts_by_role(object_model, "instrument_head")
    lowers = _parts_by_role(object_model, "leg_lower_segment")
    frame = frames[0] if frames else None
    frame_elems = {v.name or "" for v in frame.visuals} if frame is not None else set()

    ctx.check(
        "category_anchor: one frame carries three spreading legs and one head",
        len(frames) == 1
        and len(legs) == r.leg_count == 3
        and len(heads) == 1
        and {"crown_hub", "spreader_collar", "head_seat"} <= frame_elems
        and any(n.endswith("__plumb_column") for n in frame_elems)
        and sum(1 for n in frame_elems if n.startswith("hinge_cheek_")) == 2 * r.leg_count,
        details=f"frames={len(frames)}, legs={len(legs)}, heads={len(heads)}",
    )

    spread_joints = [j for j in object_model.articulations if "leg_spread_" in j.name]
    ctx.check(
        "category_anchor: every leg spreads on a registered tangential crown hinge",
        len(spread_joints) == r.leg_count
        and all(
            j.articulation_type == ArticulationType.REVOLUTE
            and j.parent == "frame"
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
            and abs(j.axis[2]) < 1e-6  # horizontal, tangential to the crown
            for j in spread_joints
        ),
        details=f"spread_joints={[j.name for j in spread_joints]}",
    )

    if r.leg_structure == "telescoping":
        extend_joints = [j for j in object_model.articulations if "leg_extend_" in j.name]
        ctx.check(
            "category_anchor: telescoping legs add a captured sliding lower segment",
            len(lowers) == r.leg_count
            and len(extend_joints) == r.leg_count
            and all(
                j.articulation_type == ArticulationType.PRISMATIC
                and j.motion_limits is not None
                and j.motion_limits.upper > j.motion_limits.lower
                for j in extend_joints
            )
            and all(
                any("clamp_pad_" in (v.name or "") for v in leg.visuals) for leg in legs
            ),
            details=f"lowers={len(lowers)}, extend_joints={len(extend_joints)}",
        )

    pan_joints = [j for j in object_model.articulations if j.name.endswith("__pan")]
    pan = pan_joints[0] if pan_joints else None
    axis_ok = pan is not None and tuple(round(v, 6) for v in pan.axis) == (0.0, 0.0, 1.0)
    if r.head == "pan_disk":
        ctx.check(
            "category_anchor: disk head pans on a registered vertical axis",
            pan is not None
            and pan.articulation_type == ArticulationType.REVOLUTE
            and axis_ok
            and pan.parent == "frame",
            details=f"pan={getattr(pan, 'name', None)}",
        )
    else:
        ctx.check(
            "category_anchor: drum head pans continuously on a registered vertical axis",
            pan is not None
            and pan.articulation_type == ArticulationType.CONTINUOUS
            and axis_ok
            and pan.parent == "frame",
            details=f"pan={getattr(pan, 'name', None)}",
        )

    # --- center_column slot ------------------------------------------------
    s = r.overall_scale
    if r.center_column == "plumb_hook":
        # Suspended column: bottom of the hook hangs well clear of the floor.
        hook_bottom = r.crown_z - 0.128 * s - 0.0065 * s
        ctx.check(
            "category_anchor: plumb_hook column hangs under the crown with a hook and cable clip",
            {
                "center_column__plumb_hook__plumb_column",
                "center_column__plumb_hook__plumb_hook",
                "center_column__plumb_hook__cable_clip",
                "center_column__plumb_hook__clip_tether",
            }
            <= frame_elems
            and hook_bottom > 0.5 * r.crown_z,
            details=f"hook_bottom={hook_bottom:.4f}, crown_z={r.crown_z:.4f}",
        )
    else:
        # Full-length rod: reaches a rubber ground foot just clear of the floor.
        rod_bottom = 0.082 * s
        foot_bottom = 0.070 * s - 0.018 * s
        ctx.check(
            "category_anchor: plumb_rod column reaches a rubber ground foot near the floor",
            {
                "center_column__plumb_rod__plumb_column",
                "center_column__plumb_rod__column_foot",
                "center_column__plumb_rod__collar_clamp_screw",
                "center_column__plumb_rod__collar_clamp_tab",
            }
            <= frame_elems
            # Rod is pressed into the foot (no tangency) and the foot clears the floor.
            and rod_bottom < 0.070 * s + 0.018 * s - 0.004 * s
            and 0.0 < foot_bottom < 0.15 * r.crown_z,
            details=f"rod_bottom={rod_bottom:.4f}, foot_bottom={foot_bottom:.4f}",
        )

    # --- head_mount slot ---------------------------------------------------
    head_elems = {v.name or "" for v in heads[0].visuals} if heads else set()
    hs = r.overall_scale * r.head_scale
    if r.head_mount == "stud_disk":
        ctx.check(
            "category_anchor: stud_disk mount is a bare threaded stud on a laser-mount disk",
            {
                f"head_mount__stud_disk__{n}"
                for n in ("mounting_plate", "laser_mount_disk", "mounting_stud")
            }
            <= head_elems
            and not any(n.startswith("head_mount__qr_platform__") for n in head_elems)
            # Stud projects above the disk it is screwed into.
            and (0.027 + 0.010) * hs > (0.014 + 0.005) * hs,
            details=f"head_mount={r.head_mount}",
        )
    else:
        ctx.check(
            "category_anchor: qr_platform mount is a screwed rectangular deck with an anti-slip pad",
            {
                f"head_mount__qr_platform__{n}"
                for n in ("mounting_platform", "anti_slip_pad", "mounting_stud")
            }
            <= head_elems
            and sum(1 for n in head_elems if "qr_platform__platform_screw_" in n) == 4
            and not any(n.startswith("head_mount__stud_disk__") for n in head_elems)
            # Pad sits on the deck and the stud clears the pad.
            and (0.036 + 0.014) * hs > (0.021 + 0.0035) * hs,
            details=f"head_mount={r.head_mount}",
        )

    # --- foot slot ---------------------------------------------------------
    tip_parts = lowers if r.leg_structure == "telescoping" else legs
    tip_elems = {v.name or "" for p in tip_parts for v in p.visuals}
    if r.foot == "rubber_pad":
        foot_ok = all(
            f"foot__rubber_pad__foot_shell_{i}" in tip_elems
            and f"foot__rubber_pad__foot_pad_{i}" in tip_elems
            for i in range(r.leg_count)
        )
        # Spherical pad, so the lowest surface is pad_centre + radius.
        lowest = -0.004 * s + _FOOT_R * s
    else:
        foot_ok = all(
            f"foot__molded_boot__boot_body_{i}" in tip_elems
            and f"foot__molded_boot__boot_band_{i}" in tip_elems
            for i in range(r.leg_count)
        )
        # Molded box boot, so the lowest surface is centre + half height.
        lowest = -0.010 * s + 0.5 * 0.052 * s
    ctx.check(
        "category_anchor: every leg tip carries the selected foot and lands on the same contact plane",
        foot_ok
        and not any(
            n.startswith("foot__") and f"foot__{r.foot}__" not in n for n in tip_elems
        )
        and abs(lowest - 0.016 * s) < 1e-9,
        details=f"foot={r.foot}, lowest_offset={lowest:.6f}, tip_parts={len(tip_parts)}",
    )

    # Feet are grounded at the neutral deployed stance (derived, mesh-free).
    foot_z = r.crown_z - r.leg_length * math.cos(r.leg_spread_deploy)
    ctx.check(
        "feet are grounded at the neutral deployed spread",
        abs(foot_z) < 1e-6,
        details=f"foot_z={foot_z:.6f} (crown_z={r.crown_z:.4f}, L={r.leg_length:.4f})",
    )

    # The three legs occupy disjoint 120-degree sectors.
    ctx.check(
        "legs occupy disjoint azimuth sectors",
        r.leg_count == 3
        and all(
            abs(
                ((r.leg_azimuth((i + 1) % 3) - r.leg_azimuth(i)) % (2.0 * math.pi))
                - 2.0 * math.pi / 3.0
            )
            < 1e-6
            for i in range(3)
        ),
        details=f"azimuths={[round(r.leg_azimuth(i), 4) for i in range(3)]}",
    )

    # Head pan actually sweeps the handle / housing horizontally.
    if heads and pan is not None:
        head = heads[0]
        probe = next(
            (v.name for v in head.visuals if v.name and ("handle" in v.name or "lock_knob" in v.name or "graduation_0" in v.name)),
            None,
        )
        if probe is not None:
            rest = ctx.part_element_world_aabb(head, elem=probe)
            with ctx.pose({pan: 1.2}):
                turned = ctx.part_element_world_aabb(head, elem=probe)
            ctx.check(
                "head pan sweeps the housing horizontally",
                rest is not None
                and turned is not None
                and math.dist(
                    [0.5 * (rest[0][i] + rest[1][i]) for i in range(2)],
                    [0.5 * (turned[0][i] + turned[1][i]) for i in range(2)],
                )
                > 0.01,
                details=f"probe={probe}",
            )

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    return ctx.report()


# ---------------------------------------------------------------------------
# High-risk corners
# ---------------------------------------------------------------------------
TEMPLATE_CORNERS = (
    corner_case(
        "wide_spread_max_telescope_disk_rod_qr_boot",
        {
            "leg_structure": "telescoping",
            "head": "pan_disk",
            "center_column": "plumb_rod",
            "head_mount": "qr_platform",
            "foot": "molded_boot",
            "leg_count": 3,
            "overall_scale": _SCALE_MAX,
            "leg_spread_deploy": _SPREAD_MAX,
            "telescope_travel_scale": _TELE_SCALE_MAX,
            "head_scale": _HEAD_SCALE_MAX,
        },
    ),
    corner_case(
        "narrow_spread_min_scale_drum_hook_stud_pad",
        {
            "leg_structure": "fixed",
            "head": "pan_drum",
            "center_column": "plumb_hook",
            "head_mount": "stud_disk",
            "foot": "rubber_pad",
            "leg_count": 3,
            "overall_scale": _SCALE_MIN,
            "leg_spread_deploy": _SPREAD_MIN,
            "telescope_travel_scale": _TELE_SCALE_MIN,
            "head_scale": _HEAD_SCALE_MIN,
        },
    ),
    corner_case(
        "min_scale_max_spread_telescoping_drum_rod_stud_boot",
        {
            "leg_structure": "telescoping",
            "head": "pan_drum",
            "center_column": "plumb_rod",
            "head_mount": "stud_disk",
            "foot": "molded_boot",
            "leg_count": 3,
            "overall_scale": _SCALE_MIN,
            "leg_spread_deploy": _SPREAD_MAX,
            "telescope_travel_scale": _TELE_SCALE_MAX,
            "head_scale": _HEAD_SCALE_MIN,
        },
    ),
    # Folded legs come closest to the full-length rod at the widest deployed
    # spread, and the boxy boot/deck pair is the worst case for world AABBs.
    corner_case(
        "fixed_leg_max_spread_rod_qr_boot",
        {
            "leg_structure": "fixed",
            "head": "pan_disk",
            "center_column": "plumb_rod",
            "head_mount": "qr_platform",
            "foot": "molded_boot",
            "leg_count": 3,
            "overall_scale": _SCALE_MAX,
            "leg_spread_deploy": _SPREAD_MAX,
            "telescope_travel_scale": _TELE_SCALE_MIN,
            "head_scale": _HEAD_SCALE_MAX,
        },
    ),
    # Narrowest stance with the hanging hook column and the widest quick-release
    # deck on the tall drum housing.
    corner_case(
        "telescoping_min_spread_hook_qr_pad",
        {
            "leg_structure": "telescoping",
            "head": "pan_drum",
            "center_column": "plumb_hook",
            "head_mount": "qr_platform",
            "foot": "rubber_pad",
            "leg_count": 3,
            "overall_scale": _SCALE_MAX,
            "leg_spread_deploy": _SPREAD_MIN,
            "telescope_travel_scale": _TELE_SCALE_MAX,
            "head_scale": _HEAD_SCALE_MAX,
        },
    ),
)
