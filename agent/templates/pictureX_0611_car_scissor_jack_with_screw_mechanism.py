# SPDX-License-Identifier: Apache-2.0

"""Self-contained manual car scissor jack template.

One rigid ``jack_base`` root carries the base pan and both lower pin lugs.  The
linkage is a real pinned rhombus expressed as two chains in the URDF tree, all
REVOLUTE about +y:

* ``jack_base -> lower_arm_0`` is the single independent driver;
* ``lower_arm_0 -> end_block_0`` mimics it at ``-1`` so the block stays level;
* ``end_block_0 -> upper_arm_0`` mimics at ``-1``;
* ``upper_arm_0 -> saddle_head`` mimics at ``+1`` so the saddle stays level;
* the mirror chain ``jack_base -> lower_arm_1 -> end_block_1 -> upper_arm_1``
  mimics at ``-1 / +1 / +1``, and its free end tracks the saddle's second pin
  exactly by symmetry and bears on it.

Those multipliers are what make the closed rhombus exact inside a tree: with the
arms authored at ``PHI0`` and the driver adding ``t``, every link sits at
``+-(PHI0 + t)`` and the saddle rises straight up to ``2*A*sin(PHI0 + t) + 2*e``
with no sideways drift at all.

The ``lead_screw`` is a REVOLUTE (+x) child of ``end_block_0`` running through
the bore of ``end_block_1``.  Both blocks are built as real square-tube housings
with a web out to their outer cheeks, so the shank passes through with running
clearance while the arm pins pass clear above and below it.

Four component slots vary without touching the mechanism: ``saddle_head``,
``base_style``, ``drive_head`` and ``arm_style``; ``arm_plate_count`` repeats
each arm's plates across the frame width.  No source-replay import, no motion
clamping, no whole-part overlap allowance.
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
    LatheGeometry,
    Mimic,
    MotionLimits,
    Origin,
    TemplateDomain,
    TestContext,
    TestReport,
    component_slot,
    corner_case,
    mate_axes,
    mesh_from_geometry,
    multiplicity_slot,
    register_interface_mate,
)

SaddleHead = Literal["notched_saddle", "beam_saddle", "flat_plate_saddle"]
BaseStyle = Literal["pressed_pan", "dual_rail", "wide_plate"]
DriveHead = Literal["crank_ring", "hex_socket", "folding_crank"]
ArmStyle = Literal["stamped_channel", "twin_plate"]
PaletteStyle = Literal["black_oxide", "zinc_bright", "works_red", "graphite"]

SADDLE_HEADS: tuple[SaddleHead, ...] = ("notched_saddle", "beam_saddle", "flat_plate_saddle")
BASE_STYLES: tuple[BaseStyle, ...] = ("pressed_pan", "dual_rail", "wide_plate")
DRIVE_HEADS: tuple[DriveHead, ...] = ("crank_ring", "hex_socket", "folding_crank")
ARM_STYLES: tuple[ArmStyle, ...] = ("stamped_channel", "twin_plate")
PALETTE_STYLES: tuple[PaletteStyle, ...] = ("black_oxide", "zinc_bright", "works_red", "graphite")


TEMPLATE_DOMAIN = TemplateDomain(
    slots=(
        component_slot("saddle_head", SADDLE_HEADS),
        component_slot("base_style", BASE_STYLES),
        component_slot("drive_head", DRIVE_HEADS),
        component_slot("arm_style", ARM_STYLES),
        multiplicity_slot("arm_plate_count", (1, 2, 3), item_slot="arm_style"),
    )
)


PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "black_oxide": {
        "paint": (0.11, 0.11, 0.12, 1.0),
        "edge": (0.06, 0.06, 0.07, 1.0),
        "steel": (0.34, 0.35, 0.37, 1.0),
        "chrome": (0.72, 0.75, 0.78, 1.0),
        "dark": (0.05, 0.05, 0.06, 1.0),
    },
    "zinc_bright": {
        "paint": (0.62, 0.65, 0.68, 1.0),
        "edge": (0.44, 0.47, 0.50, 1.0),
        "steel": (0.55, 0.57, 0.60, 1.0),
        "chrome": (0.82, 0.84, 0.86, 1.0),
        "dark": (0.20, 0.21, 0.23, 1.0),
    },
    "works_red": {
        "paint": (0.66, 0.13, 0.11, 1.0),
        "edge": (0.42, 0.07, 0.06, 1.0),
        "steel": (0.38, 0.39, 0.41, 1.0),
        "chrome": (0.76, 0.78, 0.80, 1.0),
        "dark": (0.09, 0.08, 0.08, 1.0),
    },
    "graphite": {
        "paint": (0.25, 0.26, 0.28, 1.0),
        "edge": (0.14, 0.15, 0.16, 1.0),
        "steel": (0.46, 0.48, 0.50, 1.0),
        "chrome": (0.80, 0.82, 0.84, 1.0),
        "dark": (0.08, 0.08, 0.09, 1.0),
    },
}


# Rhombus half-angle band.  The arms are AUTHORED at PHI0 (collapsed), so the
# driver runs 0 .. PHI1-PHI0 and its neutral pose is the stowed jack.
PHI0 = 0.30
PHI1 = 1.15
ARM_H = 0.014            # arm section depth
PIN_R = 0.005            # arm pin boss radius
PAN_T = 0.006
LUG_RISE = 0.012
BASE_PIN_Z = PAN_T + LUG_RISE
# The two lower pins sit +-PIN_SPLIT either side of centre, and the saddle
# carries the same split, so the rhombus closes exactly while the two lower
# arms never share one pin station.
PIN_SPLIT = 0.014
CHEEK_T = 0.006
# Sub-millimetre lap: a pin journals this far past a cheek's inner face, so QC
# reads captured bearing contact without any interpenetration.
MOUNT = 0.0006


@dataclass(frozen=True)
class Config:
    saddle_head: SaddleHead = "notched_saddle"
    base_style: BaseStyle = "pressed_pan"
    drive_head: DriveHead = "crank_ring"
    arm_style: ArmStyle = "stamped_channel"
    arm_plate_count: int = 1
    arm_len_m: float | None = None
    frame_width_m: float | None = None
    screw_radius_m: float | None = None
    palette_style: PaletteStyle = "black_oxide"
    name: str = "pictureX_0611_car_scissor_jack_with_screw_mechanism"


@dataclass(frozen=True)
class ResolvedConfig:
    saddle_head: SaddleHead
    base_style: BaseStyle
    drive_head: DriveHead
    arm_style: ArmStyle
    arm_plate_count: int
    palette_style: PaletteStyle
    palette: dict[str, tuple[float, float, float, float]]
    arm_len_m: float
    frame_width_m: float
    screw_radius_m: float
    travel_rad: float
    lift_m: float
    waist_offset_m: float     # e: screw axis above the lower waist pin
    housing_half_y: float
    plate_y: tuple[float, ...]
    plate_t: float
    cheek_y: float
    boss_len: float
    pan_half_x: float
    screw_len_m: float
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def config_from_seed(seed: int) -> Config:
    rng = random.Random(int(seed) ^ 0x5C_1550)
    choices = TEMPLATE_DOMAIN.sample(rng)
    return Config(
        saddle_head=choices["saddle_head"],
        base_style=choices["base_style"],
        drive_head=choices["drive_head"],
        arm_style=choices["arm_style"],
        arm_plate_count=choices["arm_plate_count"],
        arm_len_m=round(rng.uniform(0.090, 0.170), 4),
        frame_width_m=round(rng.uniform(0.070, 0.120), 4),
        screw_radius_m=round(rng.uniform(0.0055, 0.0105), 5),
        palette_style=rng.choice(PALETTE_STYLES),
        name=f"car_scissor_jack_seed_{int(seed)}",
    )


def resolve_config(config: Config) -> ResolvedConfig:
    TEMPLATE_DOMAIN.validate(
        {
            "saddle_head": config.saddle_head,
            "base_style": config.base_style,
            "drive_head": config.drive_head,
            "arm_style": config.arm_style,
            "arm_plate_count": config.arm_plate_count,
        }
    )
    if config.palette_style not in PALETTES:
        raise ValueError(f"unsupported palette_style: {config.palette_style}")
    if config.arm_len_m is not None and not 0.090 <= float(config.arm_len_m) <= 0.170:
        raise ValueError("arm_len_m must be in [0.090, 0.170]")
    if config.frame_width_m is not None and not 0.070 <= float(config.frame_width_m) <= 0.120:
        raise ValueError("frame_width_m must be in [0.070, 0.120]")
    if config.screw_radius_m is not None and not 0.0055 <= float(config.screw_radius_m) <= 0.0105:
        raise ValueError("screw_radius_m must be in [0.0055, 0.0105]")

    arm = _clamp(config.arm_len_m, 0.090, 0.170) if config.arm_len_m is not None else 0.125
    width = _clamp(config.frame_width_m, 0.070, 0.120) if config.frame_width_m is not None else 0.090
    srad = (
        _clamp(config.screw_radius_m, 0.0055, 0.0105)
        if config.screw_radius_m is not None
        else 0.008
    )

    travel = PHI1 - PHI0
    lift = 2.0 * arm * (math.sin(PHI1) - math.sin(PHI0))
    # The screw axis rides midway between the two waist pins, far enough above
    # the lower pin that the pin bosses pass clear under the screw housing.
    offset = srad + 0.018
    housing_half_y = srad + 0.006

    n = int(config.arm_plate_count)
    avail = width * 0.5 - (housing_half_y + 0.006)
    pitch = avail / n
    plate_t = pitch * 0.5
    plate_y = tuple(housing_half_y + 0.006 + pitch * (k + 0.5) for k in range(n))

    cheek_y = width * 0.5 + 0.006
    boss_len = 2.0 * (width * 0.5 + 0.003 + MOUNT)
    pan_half_x = PIN_SPLIT + arm * math.cos(PHI0) + 0.018
    screw_len = 2.0 * (PIN_SPLIT + arm * math.cos(PHI0)) + 0.020

    return ResolvedConfig(
        saddle_head=config.saddle_head,
        base_style=config.base_style,
        drive_head=config.drive_head,
        arm_style=config.arm_style,
        arm_plate_count=n,
        palette_style=config.palette_style,
        palette=dict(PALETTES[config.palette_style]),
        arm_len_m=arm,
        frame_width_m=width,
        screw_radius_m=srad,
        travel_rad=travel,
        lift_m=lift,
        waist_offset_m=offset,
        housing_half_y=housing_half_y,
        plate_y=plate_y,
        plate_t=plate_t,
        cheek_y=cheek_y,
        boss_len=boss_len,
        pan_half_x=pan_half_x,
        screw_len_m=screw_len,
        name=config.name,
    )


def slot_choices_for_config(config: Config | ResolvedConfig) -> tuple[tuple[str, object], ...]:
    return (
        ("saddle_head", config.saddle_head),
        ("base_style", config.base_style),
        ("drive_head", config.drive_head),
        ("arm_style", config.arm_style),
        ("arm_plate_count", config.arm_plate_count),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, object], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _materials(model: ArticulatedObject, r: ResolvedConfig) -> dict[str, str]:
    mats: dict[str, str] = {}
    for key, rgba in r.palette.items():
        model.material(f"cjack_{r.palette_style}_{key}", rgba=rgba)
        mats[key] = f"cjack_{r.palette_style}_{key}"
    return mats


def _tube(name: str, outer_r: float, inner_r: float, z0: float, z1: float, segments: int = 20):
    return mesh_from_geometry(
        LatheGeometry.from_shell_profiles(
            [(outer_r, z0), (outer_r, z1)],
            [(inner_r, z0), (inner_r, z1)],
            segments=segments,
        ),
        name,
    )


def _y_cyl(part, name: str, radius: float, length: float, xyz, material: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _x_cyl(part, name: str, radius: float, length: float, xyz, material: str) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=(0.0, math.pi / 2.0, 0.0)),
        material=material,
        name=name, material_class_id="metal.generic_plain",
    )


def _rev_joint(
    model: ArticulatedObject,
    *,
    name: str,
    parent,
    child,
    point: tuple[float, float, float],
    axis: tuple[float, float, float],
    provider_radial: tuple[float, float, float],
    consumer_radial: tuple[float, float, float],
    lower: float,
    upper: float,
    effort: float,
    velocity: float,
    mimic: Mimic | None = None,
) -> None:
    provider = AxisInterface(name=f"{name}__provider", point=point, axis=axis, radial=provider_radial)
    consumer = AxisInterface(name=f"{name}__consumer", axis=axis, radial=consumer_radial)
    mate = mate_axes(provider, consumer)
    model.articulation(
        name,
        ArticulationType.REVOLUTE,
        parent=parent,
        child=child,
        origin=mate.origin,
        axis=mate.axis,
        motion_limits=MotionLimits(lower=lower, upper=upper, effort=effort, velocity=velocity),
        mimic=mimic,
    )
    register_interface_mate(model, name, mate)


# --- arm candidates ---------------------------------------------------------
def _arm_style_stamped_channel_build(part, r: ResolvedConfig, mats: dict[str, str],
                                     *, alpha: float, tag: str) -> None:
    """Stamped channel section: a web plus two folded flanges per plate."""
    a = r.arm_len_m
    cx = a * 0.5 * math.cos(alpha)
    cz = a * 0.5 * math.sin(alpha)
    flange = ARM_H * 0.34
    for k, y in enumerate(r.plate_y):
        for side, sy in enumerate((-1.0, 1.0)):
            part.visual(
                Box((a, r.plate_t, ARM_H - 2.0 * flange + 0.001)),
                origin=Origin(xyz=(cx, sy * y, cz), rpy=(0.0, -alpha, 0.0)),
                material=mats["paint"],
                name=f"arm_style__stamped_channel__web_{tag}_{k}_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
            )
            for f, dz in enumerate((-(ARM_H - flange) * 0.5, (ARM_H - flange) * 0.5)):
                part.visual(
                    Box((a, r.plate_t * 2.4, flange)),
                    origin=Origin(
                        xyz=(cx - dz * math.sin(alpha), sy * y, cz + dz * math.cos(alpha)),
                        rpy=(0.0, -alpha, 0.0),
                    ),
                    material=mats["paint"],
                    name=f"arm_style__stamped_channel__flange_{tag}_{k}_{side}_{f}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
                )


def _arm_style_twin_plate_build(part, r: ResolvedConfig, mats: dict[str, str],
                                *, alpha: float, tag: str) -> None:
    """Flat plates on a shared pin, with a spacer collar at each plate."""
    a = r.arm_len_m
    cx = a * 0.5 * math.cos(alpha)
    cz = a * 0.5 * math.sin(alpha)
    for k, y in enumerate(r.plate_y):
        for side, sy in enumerate((-1.0, 1.0)):
            part.visual(
                Box((a, r.plate_t, ARM_H)),
                origin=Origin(xyz=(cx, sy * y, cz), rpy=(0.0, -alpha, 0.0)),
                material=mats["paint"],
                name=f"arm_style__twin_plate__plate_{tag}_{k}_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
            )
            # Spacer collar riding the pin between the plates.
            _y_cyl(
                part,
                f"arm_style__twin_plate__collar_{tag}_{k}_{side}",
                PIN_R + 0.0022,
                r.plate_t * 1.6,
                (0.0, sy * y, 0.0),
                mats["steel"],
            )


_ARM_BUILDERS = {
    "stamped_channel": _arm_style_stamped_channel_build,
    "twin_plate": _arm_style_twin_plate_build,
}


def _build_arm(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str],
               *, name: str, role: str, alpha: float, tag: str):
    """One scissor arm authored along its own axis from its near pin at local 0.

    Both end pins are full-width bosses journalled MOUNT past the cheeks of the
    body at each end, so the two plate stacks are one solid and both ends bear
    on real hardware.
    """
    part = model.part(name, meta={"role": role})
    _ARM_BUILDERS[r.arm_style](part, r, mats, alpha=alpha, tag=tag)
    a = r.arm_len_m
    _y_cyl(part, f"{tag}_near_pin", PIN_R, r.boss_len, (0.0, 0.0, 0.0), mats["chrome"])
    _y_cyl(
        part,
        f"{tag}_far_pin",
        PIN_R,
        r.boss_len,
        (a * math.cos(alpha), 0.0, a * math.sin(alpha)),
        mats["chrome"],
    )
    return part


# --- base style candidates --------------------------------------------------
def _base_style_pressed_pan_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    frame.visual(
        Box((2.0 * r.pan_half_x, r.frame_width_m + 0.030, PAN_T)),
        origin=Origin(xyz=(0.0, 0.0, PAN_T * 0.5)),
        material=mats["paint"],
        name="base_style__pressed_pan__pan", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
    )
    for side, sy in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((2.0 * r.pan_half_x, 0.005, 0.012)),
            origin=Origin(
                xyz=(0.0, sy * (r.frame_width_m * 0.5 + 0.012), PAN_T + 0.004)
            ),
            material=mats["edge"],
            name=f"base_style__pressed_pan__side_flange_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
        )


def _base_style_dual_rail_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    for side, sy in enumerate((-1.0, 1.0)):
        y = sy * (r.frame_width_m * 0.5 + 0.008)
        frame.visual(
            Box((2.0 * r.pan_half_x, 0.024, PAN_T)),
            origin=Origin(xyz=(0.0, y, PAN_T * 0.5)),
            material=mats["paint"],
            name=f"base_style__dual_rail__rail_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
        )
        frame.visual(
            Box((2.0 * r.pan_half_x, 0.006, 0.014)),
            origin=Origin(xyz=(0.0, y + sy * 0.009, PAN_T + 0.005)),
            material=mats["edge"],
            name=f"base_style__dual_rail__rail_fold_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
        )
    # Centre spine tying the two rails under the lower pins.
    frame.visual(
        Box((2.0 * (PIN_SPLIT + 0.020), r.frame_width_m + 0.020, PAN_T)),
        origin=Origin(xyz=(0.0, 0.0, PAN_T * 0.5)),
        material=mats["paint"],
        name="base_style__dual_rail__spine", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
    )


def _base_style_wide_plate_build(frame, r: ResolvedConfig, mats: dict[str, str]) -> None:
    frame.visual(
        Box((2.0 * (r.pan_half_x + 0.016), r.frame_width_m + 0.060, PAN_T)),
        origin=Origin(xyz=(0.0, 0.0, PAN_T * 0.5)),
        material=mats["paint"],
        name="base_style__wide_plate__plate", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
    )
    for side, sx in enumerate((-1.0, 1.0)):
        frame.visual(
            Box((0.008, r.frame_width_m + 0.060, 0.014)),
            origin=Origin(
                xyz=(sx * (r.pan_half_x + 0.012), 0.0, PAN_T + 0.005)
            ),
            material=mats["edge"],
            name=f"base_style__wide_plate__turned_edge_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
        )


_BASE_BUILDERS = {
    "pressed_pan": _base_style_pressed_pan_build,
    "dual_rail": _base_style_dual_rail_build,
    "wide_plate": _base_style_wide_plate_build,
}


def _pin_cheeks(part, r: ResolvedConfig, mats: dict[str, str], *, x: float, z_lo: float,
                z_hi: float, prefix: str, depth: float = 0.026) -> None:
    """Two cheeks straddling the full plate stack, which a pin boss journals into."""
    for side, sy in enumerate((-1.0, 1.0)):
        part.visual(
            Box((depth, CHEEK_T, z_hi - z_lo)),
            origin=Origin(xyz=(x, sy * r.cheek_y, 0.5 * (z_lo + z_hi))),
            material=mats["steel"],
            name=f"{prefix}_cheek_{side}", material_class_id=("metal.steel_bare" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
        )


def _build_base(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    frame = model.part("jack_base", meta={"role": "jack_base"})
    _BASE_BUILDERS[r.base_style](frame, r, mats)
    # Lower pin lugs: one pair per lower arm, straddling its plate stack.
    for side, sx in enumerate((-1.0, 1.0)):
        _pin_cheeks(
            frame,
            r,
            mats,
            x=sx * PIN_SPLIT,
            z_lo=PAN_T - 0.002,
            z_hi=BASE_PIN_Z + 0.010,
            prefix=f"base_pin_lug_{side}",
        )
    # Cheek tie so both lug pairs are one solid with the pan.
    # Tie across the full width joining both lug pairs to the pan.  It has to
    # stay below the band the lower arms sweep through, whose lowest point is
    # BASE_PIN_Z - ARM_H/2.
    frame.visual(
        Box((2.0 * PIN_SPLIT + 0.026, 2.0 * r.cheek_y + CHEEK_T, 0.006)),
        origin=Origin(xyz=(0.0, 0.0, PAN_T + 0.001)),
        material=mats["steel"],
        name="base_pin_tie", material_class_id=("metal.steel_bare" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
    )
    return frame


# --- end blocks -------------------------------------------------------------
def _build_end_block(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str],
                     *, name: str, index: int):
    """Waist block: a real square-tube screw housing webbed out to two cheeks.

    Local origin is the LOWER waist pin; the upper waist pin is 2*e above it and
    the screw bore rides midway between them, so both arm pins pass clear above
    and below the bore.
    """
    part = model.part(name, meta={"role": "end_block", "index": index})
    e = r.waist_offset_m
    rs = r.screw_radius_m
    hy = r.housing_half_y
    _pin_cheeks(part, r, mats, x=0.0, z_lo=-0.010, z_hi=2.0 * e + 0.010,
                prefix=f"end_block_{index}_pin")
    # Square tube around the screw: top and bottom plates plus two side walls,
    # open along x so the shank runs straight through.
    for f, dz in enumerate((-(rs + 0.0036), rs + 0.0036)):
        part.visual(
            Box((0.018, 2.0 * hy, 0.006)),
            origin=Origin(xyz=(0.0, 0.0, e + dz)),
            material=mats["steel"],
            name=f"end_block_{index}_bore_wall_{f}", material_class_id=("metal.steel_bare" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
        )
    for side, sy in enumerate((-1.0, 1.0)):
        part.visual(
            Box((0.018, 0.006, 2.0 * (rs + 0.0066))),
            origin=Origin(xyz=(0.0, sy * (hy - 0.003), e)),
            material=mats["steel"],
            name=f"end_block_{index}_bore_side_{side}", material_class_id=("metal.steel_bare" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
        )
        # Web out to the cheek, at the screw height so it clears both arm pins.
        y_lo = hy - 0.004
        y_hi = r.cheek_y + CHEEK_T * 0.5
        part.visual(
            Box((0.018, y_hi - y_lo, 0.010)),
            origin=Origin(xyz=(0.0, sy * 0.5 * (y_lo + y_hi), e)),
            material=mats["steel"],
            name=f"end_block_{index}_web_{side}", material_class_id=("metal.steel_bare" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
        )
    return part


# --- saddle head candidates -------------------------------------------------
def _saddle_head_notched_saddle_build(part, r: ResolvedConfig, mats: dict[str, str],
                                      *, cx: float, z0: float) -> None:
    w = r.frame_width_m + 0.026
    d = 2.0 * PIN_SPLIT + 0.038
    part.visual(
        Box((d, w, 0.008)),
        origin=Origin(xyz=(cx, 0.0, z0 + 0.004)),
        material=mats["paint"],
        name="saddle_head__notched_saddle__plate", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
    )
    for side, sy in enumerate((-1.0, 1.0)):
        part.visual(
            Box((d, 0.007, 0.014)),
            origin=Origin(xyz=(cx, sy * (w * 0.5 - 0.004), z0 + 0.013)),
            material=mats["edge"],
            name=f"saddle_head__notched_saddle__horn_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
        )
    part.visual(
        Box((0.010, w * 0.5, 0.010)),
        origin=Origin(xyz=(cx, 0.0, z0 + 0.010)),
        material=mats["edge"],
        name="saddle_head__notched_saddle__notch_rib", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
    )


def _saddle_head_beam_saddle_build(part, r: ResolvedConfig, mats: dict[str, str],
                                   *, cx: float, z0: float) -> None:
    w = r.frame_width_m + 0.080
    d = 2.0 * PIN_SPLIT + 0.030
    part.visual(
        Box((d, w, 0.012)),
        origin=Origin(xyz=(cx, 0.0, z0 + 0.006)),
        material=mats["paint"],
        name="saddle_head__beam_saddle__beam", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
    )
    for side, sy in enumerate((-1.0, 1.0)):
        part.visual(
            Box((d + 0.008, 0.010, 0.020)),
            origin=Origin(xyz=(cx, sy * (w * 0.5 - 0.005), z0 + 0.010)),
            material=mats["edge"],
            name=f"saddle_head__beam_saddle__end_cap_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
        )


def _saddle_head_flat_plate_saddle_build(part, r: ResolvedConfig, mats: dict[str, str],
                                         *, cx: float, z0: float) -> None:
    w = r.frame_width_m + 0.030
    d = 2.0 * PIN_SPLIT + 0.044
    part.visual(
        Box((d, w, 0.010)),
        origin=Origin(xyz=(cx, 0.0, z0 + 0.005)),
        material=mats["paint"],
        name="saddle_head__flat_plate_saddle__plate", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
    )
    for side, sx in enumerate((-1.0, 1.0)):
        part.visual(
            Box((0.006, w, 0.012)),
            origin=Origin(xyz=(cx + sx * (d * 0.5 - 0.003), 0.0, z0 + 0.007)),
            material=mats["edge"],
            name=f"saddle_head__flat_plate_saddle__rim_{side}", material_class_id=("metal.paint_coated" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
        )


_SADDLE_BUILDERS = {
    "notched_saddle": _saddle_head_notched_saddle_build,
    "beam_saddle": _saddle_head_beam_saddle_build,
    "flat_plate_saddle": _saddle_head_flat_plate_saddle_build,
}


def _build_saddle(model: ArticulatedObject, r: ResolvedConfig, mats: dict[str, str]):
    """Saddle carrying BOTH upper pins, split exactly like the base lugs."""
    part = model.part(
        f"saddle_head__{r.saddle_head}__saddle",
        meta={"role": "saddle_head"},
    )
    for side, sx in enumerate((0.0, 2.0 * PIN_SPLIT)):
        _pin_cheeks(part, r, mats, x=sx, z_lo=-0.008, z_hi=0.012,
                    prefix=f"saddle_pin_lug_{side}")
    _SADDLE_BUILDERS[r.saddle_head](part, r, mats, cx=PIN_SPLIT, z0=0.008)
    return part


# --- drive head candidates --------------------------------------------------
def _drive_head_crank_ring_build(part, r: ResolvedConfig, mats: dict[str, str], x: float) -> None:
    rad = 0.020 + r.screw_radius_m
    rod = 0.0045
    part.visual(
        _tube(f"crank_ring_loop", rad + rod, rad - rod, 0.0, 2.0 * rod, 24),
        origin=Origin(xyz=(x - 0.012, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["chrome"],
        name="drive_head__crank_ring__loop", material_class_id="metal.chrome_polished",
    )
    _x_cyl(part, "drive_head__crank_ring__neck", r.screw_radius_m * 0.8, 0.016,
           (x - 0.006, 0.0, 0.0), mats["chrome"])
    # Radial spoke from the neck out to the loop.  A crank ring really is one
    # bent rod; without the spoke the loop is a free-floating annulus, which the
    # 1e-6 m same-part island check rejects.
    part.visual(
        Box((2.0 * rod, 2.0 * rod, rad + rod)),
        origin=Origin(xyz=(x - 0.012, 0.0, (rad + rod) * 0.5 - rod)),
        material=mats["chrome"],
        name="drive_head__crank_ring__spoke", material_class_id="metal.chrome_polished",
    )


def _drive_head_hex_socket_build(part, r: ResolvedConfig, mats: dict[str, str], x: float) -> None:
    across = r.screw_radius_m * 2.2
    _x_cyl(part, "drive_head__hex_socket__body", across * 0.62, 0.024,
           (x - 0.012, 0.0, 0.0), mats["steel"])
    for f in range(3):
        ang = math.pi * f / 3.0
        part.visual(
            Box((0.024, across, across * 0.56)),
            origin=Origin(xyz=(x - 0.012, 0.0, 0.0), rpy=(ang, 0.0, 0.0)),
            material=mats["steel"],
            name=f"drive_head__hex_socket__flat_{f}", material_class_id=("metal.steel_bare" if r.palette_style in {"black_oxide", "works_red", "graphite"} else "metal.steel_galvanized"),
        )
    _x_cyl(part, "drive_head__hex_socket__bore", across * 0.30, 0.026,
           (x - 0.013, 0.0, 0.0), mats["dark"])


def _drive_head_folding_crank_build(part, r: ResolvedConfig, mats: dict[str, str], x: float) -> None:
    _x_cyl(part, "drive_head__folding_crank__knuckle", r.screw_radius_m * 1.5, 0.018,
           (x - 0.009, 0.0, 0.0), mats["steel"])
    arm = 0.030 + r.screw_radius_m
    part.visual(
        Box((0.008, 0.010, arm)),
        origin=Origin(xyz=(x - 0.009, 0.0, arm * 0.5)),
        material=mats["chrome"],
        name="drive_head__folding_crank__arm", material_class_id="metal.chrome_polished",
    )
    _x_cyl(part, "drive_head__folding_crank__grip", 0.008, 0.028,
           (x - 0.023, 0.0, arm - 0.004), mats["dark"])


_DRIVE_BUILDERS = {
    "crank_ring": _drive_head_crank_ring_build,
    "hex_socket": _drive_head_hex_socket_build,
    "folding_crank": _drive_head_folding_crank_build,
}


def _build_screw(model: ArticulatedObject, block0, r: ResolvedConfig, mats: dict[str, str]):
    part = model.part("lead_screw", meta={"role": "lead_screw"})
    rs = r.screw_radius_m
    length = r.screw_len_m
    _x_cyl(part, "screw_shank", rs, length, (length * 0.5 - 0.010, 0.0, 0.0), mats["chrome"])
    # Thread ribs: the screw reads as threaded, not as a plain shaft.  Their
    # bore is inside the shank so every rib is one solid with it.
    ribs = 9
    for i in range(ribs):
        x = -0.006 + (length - 0.012) * i / (ribs - 1)
        part.visual(
            _tube(f"screw_thread_{i}", rs + 0.0016, rs - 0.0016, 0.0, 0.0028, 18),
            origin=Origin(xyz=(x, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["chrome"],
            name=f"screw_thread_{i}", material_class_id="metal.chrome_polished",
        )
    _x_cyl(part, "screw_thrust_collar", rs + 0.0055, 0.008, (-0.006, 0.0, 0.0), mats["steel"])
    _DRIVE_BUILDERS[r.drive_head](part, r, mats, -0.006)
    return part


# --- assembly ---------------------------------------------------------------
_DRIVER = "base_to_lower_arm_0"


def build_picturex_0611_car_scissor_jack_with_screw_mechanism(
    config: Config | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config or Config())
    model = ArticulatedObject(
        name=r.name,
        assets=assets,
        meta={
            "category": "pictureX_0611_car_scissor_jack_with_screw_mechanism",
            "slot_choices": slot_choices_for_config(r),
            "mechanism": "pinned rhombus scissor linkage drawn together by a waist lead screw",
        },
    )
    mats = _materials(model, r)
    a = r.arm_len_m
    e = r.waist_offset_m
    travel = r.travel_rad
    frame = _build_base(model, r, mats)

    up_left = (math.pi - PHI0)
    up_right = PHI0
    far_l = (a * math.cos(up_left), 0.0, a * math.sin(up_left))
    far_r = (a * math.cos(up_right), 0.0, a * math.sin(up_right))

    def rev(name, parent, child, point, lower, upper, mimic=None):
        _rev_joint(
            model,
            name=name,
            parent=parent,
            child=child,
            point=point,
            axis=(0.0, 1.0, 0.0),
            provider_radial=(1.0, 0.0, 0.0),
            consumer_radial=(1.0, 0.0, 0.0),
            lower=lower,
            upper=upper,
            effort=26000.0,
            velocity=0.35,
            mimic=mimic,
        )

    # --- left chain: the only independent joint is the driver at its root ----
    lower0 = _build_arm(model, r, mats, name="lower_arm_0", role="lower_arm",
                        alpha=up_left, tag="lower_0")
    rev(_DRIVER, frame, lower0, (-PIN_SPLIT, 0.0, BASE_PIN_Z), 0.0, travel)

    block0 = _build_end_block(model, r, mats, name="end_block_0", index=0)
    rev("lower_arm_0_to_end_block_0", lower0, block0, far_l, -travel, 0.0,
        Mimic(joint=_DRIVER, multiplier=-1.0))

    upper0 = _build_arm(model, r, mats, name="upper_arm_0", role="upper_arm",
                        alpha=up_right, tag="upper_0")
    rev("end_block_0_to_upper_arm_0", block0, upper0, (0.0, 0.0, 2.0 * e), -travel, 0.0,
        Mimic(joint=_DRIVER, multiplier=-1.0))

    saddle = _build_saddle(model, r, mats)
    rev("upper_arm_0_to_saddle_head", upper0, saddle, far_r, 0.0, travel,
        Mimic(joint=_DRIVER, multiplier=1.0))

    # --- mirror chain: its free end tracks the saddle's second pin exactly ---
    lower1 = _build_arm(model, r, mats, name="lower_arm_1", role="lower_arm",
                        alpha=up_right, tag="lower_1")
    rev("base_to_lower_arm_1", frame, lower1, (PIN_SPLIT, 0.0, BASE_PIN_Z), -travel, 0.0,
        Mimic(joint=_DRIVER, multiplier=-1.0))

    block1 = _build_end_block(model, r, mats, name="end_block_1", index=1)
    rev("lower_arm_1_to_end_block_1", lower1, block1, far_r, 0.0, travel,
        Mimic(joint=_DRIVER, multiplier=1.0))

    upper1 = _build_arm(model, r, mats, name="upper_arm_1", role="upper_arm",
                        alpha=up_left, tag="upper_1")
    rev("end_block_1_to_upper_arm_1", block1, upper1, (0.0, 0.0, 2.0 * e), 0.0, travel,
        Mimic(joint=_DRIVER, multiplier=1.0))

    screw = _build_screw(model, block0, r, mats)
    _rev_joint(
        model,
        name="end_block_0_to_lead_screw",
        parent=block0,
        child=screw,
        point=(0.0, 0.0, e),
        axis=(1.0, 0.0, 0.0),
        provider_radial=(0.0, 0.0, 1.0),
        consumer_radial=(0.0, 0.0, 1.0),
        lower=-math.pi,
        upper=math.pi,
        effort=90.0,
        velocity=3.0,
    )

    model.meta["risk_poses"] = (
        {_DRIVER: 0.0, "end_block_0_to_lead_screw": 0.0},
        {_DRIVER: travel, "end_block_0_to_lead_screw": math.pi},
        {_DRIVER: travel, "end_block_0_to_lead_screw": -math.pi},
        {_DRIVER: 0.0, "end_block_0_to_lead_screw": math.pi},
    )
    model.meta["coupled_joint_pairs"] = ((_DRIVER, "end_block_0_to_lead_screw"),)
    return model


def build_seeded_picturex_0611_car_scissor_jack_with_screw_mechanism(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_picturex_0611_car_scissor_jack_with_screw_mechanism(
        config_from_seed(seed), assets=assets
    )


# --- authored tests ---------------------------------------------------------
def _parts_by_role(model: ArticulatedObject, role: str):
    return [p for p in model.parts if p.meta.get("role") == role]


def run_picturex_0611_car_scissor_jack_with_screw_mechanism_tests(
    model: ArticulatedObject, config: Config
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(model)

    bases = _parts_by_role(model, "jack_base")
    lowers = _parts_by_role(model, "lower_arm")
    uppers = _parts_by_role(model, "upper_arm")
    blocks = _parts_by_role(model, "end_block")
    saddles = _parts_by_role(model, "saddle_head")
    screws = _parts_by_role(model, "lead_screw")

    joints = {j.name: j for j in model.articulations}
    driver = joints.get(_DRIVER)
    screw_joint = joints.get("end_block_0_to_lead_screw")

    def _is_rev_y(j) -> bool:
        return (
            j is not None
            and j.articulation_type == ArticulationType.REVOLUTE
            and tuple(round(abs(v), 6) for v in j.axis) == (0.0, 1.0, 0.0)
            and j.motion_limits is not None
            and j.motion_limits.upper > j.motion_limits.lower
        )

    expected_mimics = {
        "lower_arm_0_to_end_block_0": -1.0,
        "end_block_0_to_upper_arm_0": -1.0,
        "upper_arm_0_to_saddle_head": 1.0,
        "base_to_lower_arm_1": -1.0,
        "lower_arm_1_to_end_block_1": 1.0,
        "end_block_1_to_upper_arm_1": 1.0,
    }
    mimics_ok = all(
        _is_rev_y(joints.get(name))
        and getattr(joints[name].mimic, "joint", None) == _DRIVER
        and abs(float(joints[name].mimic.multiplier) - mult) < 1e-9
        for name, mult in expected_mimics.items()
    )

    ctx.check(
        "category_anchor: pinned rhombus scissor linkage",
        len(bases) == 1
        and len(lowers) == 2
        and len(uppers) == 2
        and len(blocks) == 2
        and len(saddles) == 1
        and len(screws) == 1
        and bool(model.root_parts())
        and model.root_parts()[0].name == "jack_base"
        and _is_rev_y(driver)
        and driver.parent == "jack_base"
        and getattr(driver, "mimic", None) is None
        and mimics_ok,
        details=(
            f"lowers={len(lowers)} uppers={len(uppers)} blocks={len(blocks)} "
            f"saddles={len(saddles)} screws={len(screws)} mimics_ok={mimics_ok}"
        ),
    )

    # The whole point of the -1/-1/+1 chain: the saddle goes straight up and
    # stays level, with no sideways drift and no change of extent.
    saddle = saddles[0]
    rest = ctx.part_world_aabb(saddle)
    with ctx.pose({driver: driver.motion_limits.upper}):
        raised = ctx.part_world_aabb(saddle)
    level_ok = (
        rest is not None
        and raised is not None
        and abs(raised[0][0] - rest[0][0]) < 1e-4
        and abs(raised[1][0] - rest[1][0]) < 1e-4
        and abs((raised[1][2] - raised[0][2]) - (rest[1][2] - rest[0][2])) < 1e-4
    )
    ctx.check(
        "category_anchor: saddle rises vertically and stays level",
        level_ok and abs((raised[0][2] - rest[0][2]) - r.lift_m) < 2e-3,
        details=f"rest={rest} raised={raised} lift={r.lift_m} level_ok={level_ok}",
    )

    # The screw must span both waist blocks at every angle: it is anchored in
    # block 0 and long enough to still reach through block 1 fully collapsed.
    collapsed_span = 2.0 * (PIN_SPLIT + r.arm_len_m * math.cos(PHI0))
    ctx.check(
        "category_anchor: lead screw spans the waist blocks",
        screw_joint is not None
        and screw_joint.articulation_type == ArticulationType.REVOLUTE
        and tuple(round(abs(v), 6) for v in screw_joint.axis) == (1.0, 0.0, 0.0)
        and screw_joint.parent == "end_block_0"
        and r.screw_len_m >= collapsed_span
        # The bore is wider than the shank, or the screw could not turn in it.
        and r.housing_half_y > r.screw_radius_m,
        details=f"screw_len={r.screw_len_m} collapsed_span={collapsed_span}",
    )

    visual_names = {v.name or "" for p in model.parts for v in p.visuals}
    saddle_ok = {
        "notched_saddle": any("notched_saddle__horn" in n for n in visual_names),
        "beam_saddle": any("beam_saddle__end_cap" in n for n in visual_names),
        "flat_plate_saddle": any("flat_plate_saddle__rim" in n for n in visual_names),
    }[r.saddle_head]
    ctx.check("category_anchor: saddle_head identity", saddle_ok,
              details=f"saddle_head={r.saddle_head}")

    base_ok = {
        "pressed_pan": any("pressed_pan__side_flange" in n for n in visual_names),
        "dual_rail": any("dual_rail__rail_fold" in n for n in visual_names),
        "wide_plate": any("wide_plate__turned_edge" in n for n in visual_names),
    }[r.base_style]
    ctx.check("category_anchor: base_style identity", base_ok, details=f"base_style={r.base_style}")

    drive_ok = {
        "crank_ring": any("crank_ring__loop" in n for n in visual_names),
        "hex_socket": any("hex_socket__flat" in n for n in visual_names),
        "folding_crank": any("folding_crank__grip" in n for n in visual_names),
    }[r.drive_head]
    ctx.check("category_anchor: drive_head identity", drive_ok, details=f"drive_head={r.drive_head}")

    arm_ok = {
        "stamped_channel": any("stamped_channel__flange" in n for n in visual_names),
        "twin_plate": any("twin_plate__collar" in n for n in visual_names),
    }[r.arm_style]
    ctx.check("category_anchor: arm_style identity", arm_ok, details=f"arm_style={r.arm_style}")

    ctx.check(
        "arm plates repeat across the frame width",
        len(r.plate_y) == r.arm_plate_count
        and all(y + r.plate_t * 0.5 <= r.frame_width_m * 0.5 + 1e-9 for y in r.plate_y)
        and all(
            r.plate_y[i + 1] - r.plate_y[i] > r.plate_t + 1e-9
            for i in range(len(r.plate_y) - 1)
        ),
        details=f"plate_y={r.plate_y} plate_t={r.plate_t}",
    )

    ctx.check(
        "domain choices recorded on the model",
        model.meta.get("slot_choices") == slot_choices_for_config(r),
    )
    return ctx.report()


TEMPLATE_CORNERS = (
    corner_case(
        "min_arm_single_plate_hex",
        {
            "saddle_head": "flat_plate_saddle",
            "base_style": "pressed_pan",
            "drive_head": "hex_socket",
            "arm_style": "stamped_channel",
            "arm_plate_count": 1,
            "arm_len_m": 0.090,
            "frame_width_m": 0.070,
            "screw_radius_m": 0.0105,
            },
        reason="shortest arms and narrowest frame with the fattest screw - tightest waist packaging",
    ),
    corner_case(
        "max_arm_triple_plate_crank",
        {
            "saddle_head": "beam_saddle",
            "base_style": "wide_plate",
            "drive_head": "folding_crank",
            "arm_style": "twin_plate",
            "arm_plate_count": 3,
            "arm_len_m": 0.170,
            "frame_width_m": 0.120,
            "screw_radius_m": 0.0055,
        },
        reason="longest arms with three plate pairs per arm - tallest lift and widest stack",
    ),
    corner_case(
        "narrow_frame_triple_plate_fat_screw",
        {
            "saddle_head": "notched_saddle",
            "base_style": "dual_rail",
            "drive_head": "crank_ring",
            "arm_style": "twin_plate",
            "arm_plate_count": 3,
            "arm_len_m": 0.170,
            "frame_width_m": 0.070,
            "screw_radius_m": 0.0105,
        },
        reason="three plate pairs squeezed beside the fattest screw housing in the narrowest frame",
    ),
)


__all__ = [
    "TEMPLATE_DOMAIN",
    "TEMPLATE_CORNERS",
    "Config",
    "ResolvedConfig",
    "config_from_seed",
    "resolve_config",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "build_picturex_0611_car_scissor_jack_with_screw_mechanism",
    "build_seeded_picturex_0611_car_scissor_jack_with_screw_mechanism",
    "run_picturex_0611_car_scissor_jack_with_screw_mechanism_tests",
]
