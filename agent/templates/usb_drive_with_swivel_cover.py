# SPDX-License-Identifier: Apache-2.0

"""USB drive with swivel cover — modular procedural template.

This template uses the slot/module/assembler abstraction in
``agent.templates._modular``. The topology is **parallel-children**
(dj_equipment pattern): a single root ``drive_body`` carries the USB-A
connector and the pivot hardware, and exactly one non-fixed main joint
attaches the ``swivel_cover`` that rotates about a visible side pivot.

Slot graph (logical):

    drive_body (Slot A, root)
      ├── [FIXED]              connector       (Slot B; only when separate)
      ├── [FIXED]              pivot_pin       (Slot D; only separate_pin_part)
      ├── [FIXED]              body_accessory  (Slot E; only status_window)
      ├── [REVOLUTE|CONTINUOUS] swivel_cover   (Slot C)   <-- the only main DOF
      └── (surface_detail visuals, Slot F — no new parts/joints)

Like dj_equipment, only the root (drive_body) module exposes a real
``downstream`` interface. Every other module reads
``ctx.upstream_interface.part_name`` to find the body part and emits its
own joints with ``parent=body`` directly (so the assembler does NOT
auto-chain them — that would force a face-touching MatingContract which
does not fit the captured-pin swivel). The swivel joint is grandfathered
(no mating contract); separate FIXED parts (connector / pivot_pin /
status_window) DO declare MatingContracts onto real body faces.

Slot candidates (6 / 4 / 5 / 4 / 2 / 3):

  drive_body (A):  monolithic_box / extruded_rounded / multi_section_coaxial /
                   lofted_taper / slotted_yoke / cadquery_molded
  connector  (B):  molded_plug_in_body / separate_fixed_connector_part /
                   four_wall_shell_in_body / plate_shell_with_contacts
  swivel_cover (C):u_arm_bridge / u_channel_wrap / dual_plate_bridge /
                   single_stamped_shell / flip_hood_collar
  pivot_hw   (D):  integral_sleeve / body_embedded_pin / separate_pin_part /
                   side_lug_stack
  accessory  (E):  none / status_window_fixed_part
  surface    (F):  minimal_clean / grip_and_seam / datum_tick_marks

Cross-cutting enums: ``pivot_axis_family`` (side_flip = Y / top_swivel = Z),
``articulation_kind`` (continuous / revolute).

seed == 0 reproduces the spec anchor: monolithic_box_body +
molded_plug_in_body + u_arm_bridge_cover + integral_sleeve_in_body +
accessory none + minimal_clean + side_flip + continuous (sourced from
rec_..._4d3704a4, model.py:L28-L98).

Source records (Adopted Source Index):
  S1 4d3704a4  monolithic body / u_arm cover / integral sleeve (anchor)
  S2 0072dcef  extruded rounded body / u_channel cover / pivot_boss (Z)
  S3 e4dc0b9e  multi-section coaxial body / dual_plate cover (Z)
  S4 0002      lofted_taper body / separate connector / embedded pin / plate cover (Z REVOLUTE)
  S5 94788541  slotted_yoke body / plate connector / separate pivot_pin / U-cheek cover (Y REVOLUTE)
  S6 a34965    cadquery molded body + four-wall connector / single stamped cover (Y REVOLUTE)
  S7 b4af38    flip-hood cover / side_lug pin stack (Y REVOLUTE)
  S8 e945f1    datum tick marks / side_lug pin stack (Z REVOLUTE)
  S9 0001      status_window FIXED accessory part
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Literal

from agent.templates._modular import (
    InterfaceSpec,
    ModuleBuild,
    ModuleBuildContext,
    SlotSpec,
    assemble,
)
from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
    mesh_from_geometry,
    rounded_rect_profile,
    section_loft,
)

# Modular template: sweep coverage uses module_topology_diversity.
__modular__ = True


BodyModule = Literal[
    "monolithic_box_body",
    "extruded_rounded_body",
    "multi_section_coaxial_body",
    "lofted_taper_body",
    "slotted_yoke_body",
    "cadquery_molded_body",
]
ConnectorModule = Literal[
    "molded_plug_in_body",
    "separate_fixed_connector_part",
    "four_wall_shell_in_body",
    "plate_shell_with_contacts",
]
CoverModule = Literal[
    "u_arm_bridge_cover",
    "u_channel_wrap_cover",
    "dual_plate_bridge_cover",
    "single_stamped_shell_cover",
    "flip_hood_collar_cover",
]
PivotModule = Literal[
    "integral_sleeve_in_body",
    "body_embedded_pin_with_bosses",
    "separate_pivot_pin_part",
    "side_lug_pin_stack",
]
AccessoryModule = Literal[
    "none",
    "status_window_fixed_part",
    "service_plate_fixed_part",
]
DetailModule = Literal[
    "minimal_clean",
    "grip_and_seam_cues",
    "datum_tick_marks",
]
PivotAxisFamily = Literal["side_flip", "top_swivel"]
ArticulationKind = Literal["continuous", "revolute"]
UsbPaletteTheme = Literal[
    "anchor_steel",
    "graphite_black",
    "rugged_orange",
    "warm_brass",
    "white_clean",
    "translucent_smoke",
    "blue_anodized",
    "red_black",
]


BODY_MODULES: tuple[BodyModule, ...] = (
    "monolithic_box_body",
    "extruded_rounded_body",
    "multi_section_coaxial_body",
    "lofted_taper_body",
    "slotted_yoke_body",
    "cadquery_molded_body",
)
CONNECTOR_MODULES: tuple[ConnectorModule, ...] = (
    "molded_plug_in_body",
    "separate_fixed_connector_part",
    "four_wall_shell_in_body",
    "plate_shell_with_contacts",
)
COVER_MODULES: tuple[CoverModule, ...] = (
    "u_arm_bridge_cover",
    "u_channel_wrap_cover",
    "dual_plate_bridge_cover",
    "single_stamped_shell_cover",
    "flip_hood_collar_cover",
)
PIVOT_MODULES: tuple[PivotModule, ...] = (
    "integral_sleeve_in_body",
    "body_embedded_pin_with_bosses",
    "separate_pivot_pin_part",
    "side_lug_pin_stack",
)
ACCESSORY_MODULES: tuple[AccessoryModule, ...] = (
    "none",
    "status_window_fixed_part",
    "service_plate_fixed_part",
)
DETAIL_MODULES: tuple[DetailModule, ...] = (
    "minimal_clean",
    "grip_and_seam_cues",
    "datum_tick_marks",
)


# --------------------------------------------------------------------------- #
# Palette presets.
# --------------------------------------------------------------------------- #


USB_PALETTE_PRESETS: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "anchor_steel": {
        "body_plastic": (0.14, 0.14, 0.15, 1.0),
        "cover_shell": (0.77, 0.79, 0.81, 1.0),
        "satin_steel": (0.77, 0.79, 0.81, 1.0),
        "connector_steel": (0.70, 0.72, 0.74, 1.0),
        "dark_metal": (0.42, 0.44, 0.47, 1.0),
        "tongue_black": (0.05, 0.05, 0.06, 1.0),
        "accent": (0.84, 0.40, 0.10, 1.0),
        "window_smoke": (0.20, 0.24, 0.30, 0.65),
        "laser_etch": (0.55, 0.57, 0.60, 1.0),
    },
    "graphite_black": {
        "body_plastic": (0.08, 0.09, 0.10, 1.0),
        "cover_shell": (0.10, 0.105, 0.115, 1.0),
        "satin_steel": (0.62, 0.64, 0.67, 1.0),
        "connector_steel": (0.74, 0.76, 0.78, 1.0),
        "dark_metal": (0.30, 0.32, 0.35, 1.0),
        "tongue_black": (0.03, 0.03, 0.04, 1.0),
        "accent": (0.75, 0.12, 0.08, 1.0),
        "window_smoke": (0.10, 0.30, 0.18, 0.65),
        "laser_etch": (0.45, 0.46, 0.48, 1.0),
    },
    "rugged_orange": {
        "body_plastic": (0.18, 0.19, 0.21, 1.0),
        "cover_shell": (0.86, 0.36, 0.08, 1.0),
        "satin_steel": (0.70, 0.72, 0.75, 1.0),
        "connector_steel": (0.66, 0.68, 0.71, 1.0),
        "dark_metal": (0.38, 0.40, 0.43, 1.0),
        "tongue_black": (0.08, 0.08, 0.09, 1.0),
        "accent": (0.90, 0.45, 0.10, 1.0),
        "window_smoke": (0.30, 0.18, 0.06, 0.65),
        "laser_etch": (0.85, 0.50, 0.18, 1.0),
    },
    "warm_brass": {
        "body_plastic": (0.20, 0.16, 0.12, 1.0),
        "cover_shell": (0.78, 0.62, 0.34, 1.0),
        "satin_steel": (0.78, 0.66, 0.42, 1.0),
        "connector_steel": (0.72, 0.60, 0.36, 1.0),
        "dark_metal": (0.40, 0.32, 0.20, 1.0),
        "tongue_black": (0.07, 0.05, 0.03, 1.0),
        "accent": (0.78, 0.22, 0.12, 1.0),
        "window_smoke": (0.30, 0.24, 0.10, 0.65),
        "laser_etch": (0.62, 0.50, 0.28, 1.0),
    },
    "white_clean": {
        "body_plastic": (0.90, 0.90, 0.89, 1.0),
        "cover_shell": (0.94, 0.94, 0.92, 1.0),
        "satin_steel": (0.55, 0.57, 0.60, 1.0),
        "connector_steel": (0.70, 0.72, 0.74, 1.0),
        "dark_metal": (0.40, 0.42, 0.45, 1.0),
        "tongue_black": (0.20, 0.20, 0.21, 1.0),
        "accent": (0.84, 0.34, 0.30, 1.0),
        "window_smoke": (0.40, 0.50, 0.60, 0.65),
        "laser_etch": (0.40, 0.42, 0.45, 1.0),
    },
    "translucent_smoke": {
        "body_plastic": (0.18, 0.20, 0.22, 0.72),
        "cover_shell": (0.10, 0.14, 0.16, 0.68),
        "satin_steel": (0.68, 0.70, 0.72, 1.0),
        "connector_steel": (0.74, 0.76, 0.78, 1.0),
        "dark_metal": (0.24, 0.27, 0.30, 1.0),
        "tongue_black": (0.04, 0.05, 0.06, 1.0),
        "accent": (0.12, 0.56, 0.62, 1.0),
        "window_smoke": (0.08, 0.12, 0.16, 0.55),
        "laser_etch": (0.48, 0.56, 0.60, 1.0),
    },
    "blue_anodized": {
        "body_plastic": (0.08, 0.12, 0.18, 1.0),
        "cover_shell": (0.10, 0.30, 0.72, 1.0),
        "satin_steel": (0.20, 0.38, 0.66, 1.0),
        "connector_steel": (0.72, 0.74, 0.77, 1.0),
        "dark_metal": (0.18, 0.22, 0.28, 1.0),
        "tongue_black": (0.04, 0.05, 0.07, 1.0),
        "accent": (0.86, 0.74, 0.28, 1.0),
        "window_smoke": (0.08, 0.18, 0.32, 0.65),
        "laser_etch": (0.58, 0.70, 0.86, 1.0),
    },
    "red_black": {
        "body_plastic": (0.05, 0.05, 0.055, 1.0),
        "cover_shell": (0.78, 0.05, 0.04, 1.0),
        "satin_steel": (0.62, 0.64, 0.66, 1.0),
        "connector_steel": (0.72, 0.74, 0.76, 1.0),
        "dark_metal": (0.22, 0.22, 0.24, 1.0),
        "tongue_black": (0.025, 0.025, 0.03, 1.0),
        "accent": (0.82, 0.08, 0.06, 1.0),
        "window_smoke": (0.24, 0.04, 0.04, 0.62),
        "laser_etch": (0.76, 0.20, 0.18, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config dataclasses
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class UsbDriveWithSwivelCoverConfig:
    """Public template config. Module-selection fields default to ``None``;
    ``config_from_seed`` / ``resolve_config`` fill them in (anchor for seed 0,
    RNG otherwise). Continuous fields describe the drive envelope and pivot
    placement; module factories scale where appropriate."""

    body_module: BodyModule | None = None
    connector_module: ConnectorModule | None = None
    cover_module: CoverModule | None = None
    pivot_module: PivotModule | None = None
    accessory_module: AccessoryModule | None = None
    detail_module: DetailModule | None = None

    pivot_axis_family: PivotAxisFamily | None = None
    articulation_kind: ArticulationKind | None = None

    palette_theme: UsbPaletteTheme = "anchor_steel"

    body_length: float = 0.044
    body_width: float = 0.017
    body_thickness: float = 0.008
    connector_length: float = 0.012
    connector_width: float = 0.0122
    connector_thickness: float = 0.0046
    cover_clearance: float = 0.0008
    cover_wall: float = 0.0010
    pivot_radius: float = 0.0035
    pivot_x: float = 0.004
    swivel_upper: float = math.pi

    palette: dict[str, tuple[float, float, float, float]] = field(
        default_factory=lambda: dict(USB_PALETTE_PRESETS["anchor_steel"])
    )


@dataclass(frozen=True)
class ResolvedUsbDriveWithSwivelCoverConfig:
    """Dimension-clamped + module-resolved config consumed by builders."""

    body_module: BodyModule
    connector_module: ConnectorModule
    cover_module: CoverModule
    pivot_module: PivotModule
    accessory_module: AccessoryModule
    detail_module: DetailModule
    pivot_axis_family: PivotAxisFamily
    articulation_kind: ArticulationKind
    palette_theme: UsbPaletteTheme
    body_length: float
    body_width: float
    body_thickness: float
    connector_length: float
    connector_width: float
    connector_thickness: float
    cover_clearance: float
    cover_wall: float
    pivot_radius: float
    pivot_x: float
    swivel_upper: float
    palette: dict[str, tuple[float, float, float, float]]


# --------------------------------------------------------------------------- #
# Seed-driven sampling + resolution
# --------------------------------------------------------------------------- #


def config_from_seed(seed: int) -> UsbDriveWithSwivelCoverConfig:
    """Sample a configuration for the given seed.

    seed == 0 returns the anchor combination at the canonical S1 dimensions.
    Other seeds RNG-pick each slot's module and sample continuous dimensions
    inside the spec ranges.
    """
    if seed == 0:
        return UsbDriveWithSwivelCoverConfig(
            body_module="monolithic_box_body",
            connector_module="molded_plug_in_body",
            cover_module="u_arm_bridge_cover",
            pivot_module="integral_sleeve_in_body",
            accessory_module="none",
            detail_module="minimal_clean",
            pivot_axis_family="side_flip",
            articulation_kind="continuous",
            palette_theme="anchor_steel",
        )

    rng = random.Random(seed)
    body: BodyModule = rng.choice(BODY_MODULES)
    connector: ConnectorModule = rng.choice(CONNECTOR_MODULES)
    cover: CoverModule = rng.choice(COVER_MODULES)
    pivot: PivotModule = rng.choice(PIVOT_MODULES)
    accessory: AccessoryModule = rng.choice(ACCESSORY_MODULES)
    detail: DetailModule = rng.choice(DETAIL_MODULES)
    # Default generated USB drives should use the side-pinned flip axis from
    # the category identity. ``top_swivel`` remains available for explicit
    # configs, but random dataset seeds avoid the confusing planar-swivel cases.
    axis_family: PivotAxisFamily = "side_flip"
    kind: ArticulationKind = rng.choice(("continuous", "revolute"))
    palette_theme: UsbPaletteTheme = rng.choice(tuple(USB_PALETTE_PRESETS.keys()))

    body_length = round(rng.uniform(0.036, 0.064), 5)
    body_width = round(rng.uniform(0.017, 0.021), 5)
    body_thickness = round(rng.uniform(0.0076, 0.0108), 5)
    cover_clearance = round(rng.uniform(0.0007, 0.0010), 5)
    pivot_radius = round(rng.uniform(0.0028, 0.0042), 5)
    # pivot sits near the rear of the body; keep it inside the rear half.
    pivot_x = round(rng.uniform(-0.004, 0.006), 5)
    swivel_upper = round(rng.uniform(2.4, math.pi), 4)

    return UsbDriveWithSwivelCoverConfig(
        body_module=body,
        connector_module=connector,
        cover_module=cover,
        pivot_module=pivot,
        accessory_module=accessory,
        detail_module=detail,
        pivot_axis_family=axis_family,
        articulation_kind=kind,
        palette_theme=palette_theme,
        body_length=body_length,
        body_width=body_width,
        body_thickness=body_thickness,
        cover_clearance=cover_clearance,
        pivot_radius=pivot_radius,
        pivot_x=pivot_x,
        swivel_upper=swivel_upper,
    )


def resolve_config(
    config: UsbDriveWithSwivelCoverConfig,
) -> ResolvedUsbDriveWithSwivelCoverConfig:
    """Validate module enums; clamp floats to spec ranges; fill None module
    fields with anchor defaults."""

    body = config.body_module or "monolithic_box_body"
    connector = config.connector_module or "molded_plug_in_body"
    cover = config.cover_module or "u_arm_bridge_cover"
    pivot = config.pivot_module or "integral_sleeve_in_body"
    accessory = config.accessory_module or "none"
    detail = config.detail_module or "minimal_clean"
    axis_family = config.pivot_axis_family or "side_flip"
    kind = config.articulation_kind or "continuous"

    if body not in BODY_MODULES:
        raise ValueError(f"Unsupported body_module: {body}")
    if connector not in CONNECTOR_MODULES:
        raise ValueError(f"Unsupported connector_module: {connector}")
    if cover not in COVER_MODULES:
        raise ValueError(f"Unsupported cover_module: {cover}")
    if pivot not in PIVOT_MODULES:
        raise ValueError(f"Unsupported pivot_module: {pivot}")
    if accessory not in ACCESSORY_MODULES:
        raise ValueError(f"Unsupported accessory_module: {accessory}")
    if detail not in DETAIL_MODULES:
        raise ValueError(f"Unsupported detail_module: {detail}")
    if axis_family not in ("side_flip", "top_swivel"):
        raise ValueError(f"Unsupported pivot_axis_family: {axis_family}")
    if kind not in ("continuous", "revolute"):
        raise ValueError(f"Unsupported articulation_kind: {kind}")
    if str(config.palette_theme) not in USB_PALETTE_PRESETS:
        raise ValueError(f"Unsupported palette_theme: {config.palette_theme}")

    body_length = max(0.036, min(float(config.body_length), 0.064))
    body_width = max(0.017, min(float(config.body_width), 0.021))
    body_thickness = max(0.0076, min(float(config.body_thickness), 0.0108))
    connector_length = max(0.010, min(float(config.connector_length), 0.014))
    connector_width = max(0.011, min(float(config.connector_width), 0.0130))
    connector_thickness = max(0.0040, min(float(config.connector_thickness), 0.0052))
    cover_clearance = max(0.0007, min(float(config.cover_clearance), 0.0012))
    cover_wall = max(0.0008, min(float(config.cover_wall), 0.0016))
    pivot_radius = max(0.0026, min(float(config.pivot_radius), 0.0045))
    pivot_x = max(-0.006, min(float(config.pivot_x), 0.0065))
    swivel_upper = max(2.4, min(float(config.swivel_upper), math.pi))

    palette = dict(USB_PALETTE_PRESETS[config.palette_theme])

    return ResolvedUsbDriveWithSwivelCoverConfig(
        body_module=body,
        connector_module=connector,
        cover_module=cover,
        pivot_module=pivot,
        accessory_module=accessory,
        detail_module=detail,
        pivot_axis_family=axis_family,
        articulation_kind=kind,
        palette_theme=config.palette_theme,
        body_length=body_length,
        body_width=body_width,
        body_thickness=body_thickness,
        connector_length=connector_length,
        connector_width=connector_width,
        connector_thickness=connector_thickness,
        cover_clearance=cover_clearance,
        cover_wall=cover_wall,
        pivot_radius=pivot_radius,
        pivot_x=pivot_x,
        swivel_upper=swivel_upper,
        palette=palette,
    )


# --------------------------------------------------------------------------- #
# Shared geometry layout — every body/connector/pivot/cover module agrees on
# this canonical body frame so module combinations compose cleanly.
#
# Convention (body local frame):
#   * body shell centered on z = 0; thickness = body_thickness.
#   * pivot at x = r.pivot_x near the REAR; connector at the +x FRONT.
#   * the shell front edge is body_front_x; the connector protrudes from it.
#   * side_flip: pivot axis = Y, pivot at y = 0 (transverse pin across width).
#   * top_swivel: pivot axis = Z, pivot offset to +y side of the body.
# --------------------------------------------------------------------------- #


def _shell_center_x(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    """Center the body shell so its rear sits ~2mm behind the pivot."""
    return r.pivot_x - 0.002 + r.body_length * 0.5


def _body_front_x(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    return _shell_center_x(r) + r.body_length * 0.5


def _body_rear_x(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    return _shell_center_x(r) - r.body_length * 0.5


def _connector_origin_x(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    """Center x of an in-body (molded) connector visual: it straddles the
    front edge so it overlaps the shell AND protrudes clearly forward."""
    return _body_front_x(r) - 0.0015 + r.connector_length * 0.5


def _connector_front_x(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    return _connector_origin_x(r) + r.connector_length * 0.5


def _pivot_y(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    """For top_swivel the pivot is offset to the +y side of the body."""
    if r.pivot_axis_family == "top_swivel":
        return r.body_width * 0.5 + 0.0010
    return 0.0


def _pivot_axis(r: ResolvedUsbDriveWithSwivelCoverConfig) -> tuple[float, float, float]:
    # Cover geometry extends toward +X in the closed pose. For a side-flip
    # hinge, positive travel must lift that covered face away from the drive
    # body, not sweep it downward through the USB shell.
    return (0.0, 0.0, 1.0) if r.pivot_axis_family == "top_swivel" else (0.0, -1.0, 0.0)


def _pivot_span(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    """Axial length of the pivot pin/sleeve. For side_flip the pin runs
    across the body width (+ a little overhang); for top_swivel it runs
    vertically through the body thickness."""
    if r.pivot_axis_family == "top_swivel":
        return r.body_thickness + 2.0 * (r.cover_clearance + r.cover_wall) + 0.0010
    side_standoff = max(0.0016, r.pivot_radius * 0.45)
    return r.body_width + 2.0 * (r.cover_clearance + r.cover_wall + side_standoff) + 0.0010


def _pivot_rpy(r: ResolvedUsbDriveWithSwivelCoverConfig) -> tuple[float, float, float]:
    """RPY to lay a +z cylinder along the pivot axis."""
    if r.pivot_axis_family == "top_swivel":
        return (0.0, 0.0, 0.0)
    return (math.pi / 2.0, 0.0, 0.0)


def _pivot_z(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    """Side-flip hinges sit on the covered face, outside the body thickness.

    Keeping the hinge at body mid-thickness makes the open cover sweep through
    the body. The source examples with raised hinge saddles put the pin above
    the shell surface, so the cover rotates clear of the body.
    """
    if r.pivot_axis_family == "top_swivel":
        return 0.0
    return r.body_thickness * 0.5 + r.cover_clearance + r.pivot_radius * 0.85


def _swivel_origin(r: ResolvedUsbDriveWithSwivelCoverConfig) -> tuple[float, float, float]:
    return (r.pivot_x, _pivot_y(r), _pivot_z(r))


def _mesh_from_geometry_for_model(model: ArticulatedObject, geometry, name: str):
    if model.assets is not None:
        return mesh_from_geometry(geometry, model.assets.mesh_path(f"{name}.obj"))
    return mesh_from_geometry(geometry, name)


def _mesh_from_cadquery_for_model(model: ArticulatedObject, shape, name: str, *, tolerance: float):
    return mesh_from_cadquery(shape, name, assets=model.assets, tolerance=tolerance)


def _cover_center_y(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    """Cover geometry is authored in the cover frame whose origin is the
    pivot. A top-swivel pivot sits on the +Y side of the body, so the cover
    shell must be offset back toward the body centerline in its local frame."""
    return -_pivot_y(r)


def _cover_body_z(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    """Local z for the main cover shell in the cover frame."""
    return -_pivot_z(r)


def _swivel_limits(r: ResolvedUsbDriveWithSwivelCoverConfig) -> MotionLimits:
    if r.articulation_kind == "revolute":
        return MotionLimits(effort=1.0, velocity=6.0, lower=0.0, upper=r.swivel_upper)
    return MotionLimits(effort=1.0, velocity=8.0)


def _swivel_joint_type(r: ResolvedUsbDriveWithSwivelCoverConfig) -> ArticulationType:
    if r.articulation_kind == "revolute":
        return ArticulationType.REVOLUTE
    return ArticulationType.CONTINUOUS


# --------------------------------------------------------------------------- #
# Pivot-hardware visuals on the body (integral / embedded / side_lug). These
# are emitted by the pivot_hardware module onto the body part. The pivot
# bridging geometry must overlap the body shell so there are no body-internal
# islands and the swivel origin lies inside the body AABB.
# --------------------------------------------------------------------------- #


def _emit_side_flip_hinge_seat(
    body,
    r: ResolvedUsbDriveWithSwivelCoverConfig,
    *,
    prefix: str,
    material: str = "body_plastic",
) -> list[str]:
    """Raised hinge seat grown out of the top shell for side-flip pivots.

    The pin stays above the top face for motion clearance, but the visual
    support must visibly overlap the body so the hinge reads as embedded
    rather than floating.
    """
    if r.pivot_axis_family != "side_flip":
        return []

    px, _py, pz = _swivel_origin(r)
    top_z = r.body_thickness * 0.5
    lug_x = max(0.0065, r.pivot_radius * 2.4)
    lug_y = max(0.0032, r.cover_wall * 3.0)
    lug_z = max(0.0048, (pz - top_z) + r.pivot_radius * 1.65)
    lug_center_z = top_z + lug_z * 0.5 - 0.00045
    lug_off = r.body_width * 0.5 + lug_y * 0.42
    plinth_h = max(0.0018, (pz - top_z) + r.pivot_radius * 0.30)
    names = [f"{prefix}_seat", f"{prefix}_lug_0", f"{prefix}_lug_1"]

    body.visual(
        Box((lug_x * 1.15, r.body_width + 2.0 * lug_y, plinth_h)),
        origin=Origin(xyz=(px, 0.0, top_z + plinth_h * 0.5 - 0.00055)),
        material=material,
        name=f"{prefix}_seat", material_class_id="plastic.opaque_glossy_molded",
    )
    for idx, y in enumerate((lug_off, -lug_off)):
        body.visual(
            Box((lug_x, lug_y, lug_z)),
            origin=Origin(xyz=(px, y, lug_center_z)),
            material=material,
            name=f"{prefix}_lug_{idx}", material_class_id="plastic.opaque_glossy_molded",
        )
    return names


def _emit_integral_sleeve(body, r: ResolvedUsbDriveWithSwivelCoverConfig) -> list[str]:
    """S1 model.py:L41-L46 — single transverse pivot_sleeve cylinder.

    A satin-steel sleeve laid along the pivot axis through the body rear.
    The sleeve overlaps the shell (it sits at z=0, x=pivot_x inside the
    shell footprint), so it is connected to the body island.
    """
    names = _emit_side_flip_hinge_seat(body, r, prefix="pivot_sleeve", material="body_plastic")
    body.visual(
        Cylinder(radius=r.pivot_radius, length=_pivot_span(r)),
        origin=Origin(xyz=_swivel_origin(r), rpy=_pivot_rpy(r)),
        material="satin_steel",
        name="pivot_sleeve", material_class_id="metal.stainless_matte",
    )
    return [*names, "pivot_sleeve"]


def _emit_embedded_pin(body, r: ResolvedUsbDriveWithSwivelCoverConfig) -> list[str]:
    """S4 model.py:L110-L127 — pivot_boss_top/bottom + through pivot_pin.

    Two small bosses straddle the body and a thin steel pin runs the pivot
    axis. The bosses overlap the shell (sit at z=0 region); the pin overlaps
    the bosses.
    """
    px, py, pz = _swivel_origin(r)
    span = _pivot_span(r)
    if r.pivot_axis_family == "top_swivel":
        # bosses at +z / -z faces of the shell, pin vertical
        boss_z = r.body_thickness * 0.5
        body.visual(
            Cylinder(radius=r.pivot_radius * 1.25, length=0.0010),
            origin=Origin(xyz=(px, py, boss_z - 0.0003)),
            material="body_plastic",
            name="pivot_boss_top", material_class_id="plastic.opaque_glossy_molded",
        )
        body.visual(
            Cylinder(radius=r.pivot_radius * 1.25, length=0.0010),
            origin=Origin(xyz=(px, py, -boss_z + 0.0003)),
            material="body_plastic",
            name="pivot_boss_bottom", material_class_id="plastic.opaque_glossy_molded",
        )
    else:
        names = _emit_side_flip_hinge_seat(body, r, prefix="pivot_boss", material="body_plastic")
        boss_y = r.body_width * 0.5
        body.visual(
            Cylinder(radius=r.pivot_radius * 1.25, length=0.0010),
            origin=Origin(xyz=(px, boss_y - 0.0003, pz), rpy=_pivot_rpy(r)),
            material="body_plastic",
            name="pivot_boss_top", material_class_id="plastic.opaque_glossy_molded",
        )
        body.visual(
            Cylinder(radius=r.pivot_radius * 1.25, length=0.0010),
            origin=Origin(xyz=(px, -boss_y + 0.0003, pz), rpy=_pivot_rpy(r)),
            material="body_plastic",
            name="pivot_boss_bottom", material_class_id="plastic.opaque_glossy_molded",
        )
    if r.pivot_axis_family == "top_swivel":
        names = ["pivot_boss_top", "pivot_boss_bottom"]
    body.visual(
        Cylinder(radius=r.pivot_radius * 0.5, length=span),
        origin=Origin(xyz=_swivel_origin(r), rpy=_pivot_rpy(r)),
        material="satin_steel",
        name="pivot_pin", material_class_id="metal.stainless_matte",
    )
    return [*names, "pivot_boss_top", "pivot_boss_bottom", "pivot_pin"]


def _emit_side_lug_stack(body, r: ResolvedUsbDriveWithSwivelCoverConfig) -> list[str]:
    """S7 model.py:L134-L163 / S8 model.py:L138-L159 — a raised lug/saddle
    growing out of the body with a visible pin + heads.

    A box saddle straddles the pivot, a steel pin runs the axis, and two
    heads cap the pin ends. The saddle overlaps the shell footprint.
    """
    px, py, pz = _swivel_origin(r)
    span = _pivot_span(r)
    if r.pivot_axis_family == "side_flip":
        lug_x = max(0.0045, r.pivot_radius * 1.7)
        lug_y = max(0.0032, r.cover_wall * 3.0)
        lug_z = max(0.0048, (pz - r.body_thickness * 0.5) + r.pivot_radius * 1.9)
        lug_center_z = r.body_thickness * 0.5 + lug_z * 0.5 - 0.00045
        lug_off = r.body_width * 0.5 + lug_y * 0.42
        seat_h = max(0.0018, pz - r.body_thickness * 0.5)
        body.visual(
            Box((lug_x * 1.15, r.body_width + 2.0 * lug_y, seat_h)),
            origin=Origin(xyz=(px, py, r.body_thickness * 0.5 + seat_h * 0.5 - 0.00055)),
            material="dark_metal",
            name="hinge_saddle", material_class_id="metal.blackened_gunmetal",
        )
        names = [
            "hinge_saddle",
            "hinge_lug_0",
            "hinge_lug_1",
            "pivot_pin",
            "pivot_pin_head_0",
            "pivot_pin_head_1",
        ]
        for idx, y in enumerate((lug_off, -lug_off)):
            body.visual(
                Box((lug_x, lug_y, lug_z)),
                origin=Origin(xyz=(px, y, lug_center_z)),
                material="dark_metal",
                name=f"hinge_lug_{idx}", material_class_id="metal.blackened_gunmetal",
            )
    else:
        saddle_h = r.body_thickness * 0.85
        # Saddle box straddles the pivot, overlapping the shell core.
        body.visual(
            Box((max(0.010, r.pivot_radius * 3.5), max(0.006, r.body_width * 0.5), saddle_h)),
            origin=Origin(xyz=(px, py, pz)),
            material="dark_metal",
            name="hinge_saddle", material_class_id="metal.blackened_gunmetal",
        )
        names = ["hinge_saddle", "pivot_pin", "pivot_pin_head_0", "pivot_pin_head_1"]
    body.visual(
        Cylinder(radius=r.pivot_radius * 0.8, length=span),
        origin=Origin(xyz=_swivel_origin(r), rpy=_pivot_rpy(r)),
        material="satin_steel",
        name="pivot_pin", material_class_id="metal.stainless_matte",
    )
    head_off = span * 0.5 + 0.0006
    if r.pivot_axis_family == "top_swivel":
        head_axis = (px, py, head_off)
        head_axis2 = (px, py, -head_off)
    else:
        head_axis = (px, head_off, pz)
        head_axis2 = (px, -head_off, pz)
    body.visual(
        Cylinder(radius=r.pivot_radius * 1.15, length=0.0012),
        origin=Origin(xyz=head_axis, rpy=_pivot_rpy(r)),
        material="satin_steel",
        name="pivot_pin_head_0", material_class_id="metal.stainless_matte",
    )
    body.visual(
        Cylinder(radius=r.pivot_radius * 1.15, length=0.0012),
        origin=Origin(xyz=head_axis2, rpy=_pivot_rpy(r)),
        material="satin_steel",
        name="pivot_pin_head_1", material_class_id="metal.stainless_matte",
    )
    return names


def _emit_body_pivot_anchor(body, r: ResolvedUsbDriveWithSwivelCoverConfig) -> None:
    """When the pivot is a SEPARATE part (separate_pivot_pin_part), the body
    still needs a real anchoring boss at the pivot so the FIXED pin part has
    something to mate to (Rule 2) and the swivel origin lies near body support.
    Use split lugs around the shaft instead of a solid boss through the shaft,
    matching the source yoke/lug pattern without creating strict-QC overlap."""
    px, py, pz = _swivel_origin(r)
    shaft_r = r.pivot_radius * 0.7
    if r.pivot_axis_family == "top_swivel":
        lug_w = max(0.0014, r.pivot_radius * 0.45)
        lug_y = max(0.0040, r.pivot_radius * 2.4)
        lug_z = r.body_thickness * 0.65
        x_off = shaft_r + lug_w * 0.5 + 0.0004
        for idx, sx in enumerate((-1.0, 1.0)):
            body.visual(
                Box((lug_w, lug_y, lug_z)),
                origin=Origin(xyz=(px + sx * x_off, py, pz)),
                material="dark_metal",
                name=f"pivot_mount_boss_{idx}", material_class_id="metal.blackened_gunmetal",
            )
        return

    lug_y = max(0.0032, r.cover_wall * 3.0)
    lug_z = max(0.0048, (pz - r.body_thickness * 0.5) + r.pivot_radius * 1.8)
    lug_center_z = r.body_thickness * 0.5 + lug_z * 0.5 - 0.00045
    lug_off = r.body_width * 0.5 + lug_y * 0.42
    body.visual(
        Box(
            (
                max(0.0075, r.pivot_radius * 2.7),
                r.body_width + 2.0 * lug_y,
                max(0.0018, pz - r.body_thickness * 0.5),
            )
        ),
        origin=Origin(
            xyz=(
                px,
                py,
                r.body_thickness * 0.5 + max(0.0018, pz - r.body_thickness * 0.5) * 0.5 - 0.00055,
            )
        ),
        material="dark_metal",
        name="pivot_mount_seat", material_class_id="metal.blackened_gunmetal",
    )
    for idx, y in enumerate((lug_off, -lug_off)):
        body.visual(
            Box((max(0.0065, r.pivot_radius * 2.3), lug_y, lug_z)),
            origin=Origin(xyz=(px, y, lug_center_z)),
            material="dark_metal",
            name=f"pivot_mount_boss_{idx}", material_class_id="metal.blackened_gunmetal",
        )


# --------------------------------------------------------------------------- #
# Module factories — drive_body (Slot A, root)
# --------------------------------------------------------------------------- #


def _body_inertial(body, r: ResolvedUsbDriveWithSwivelCoverConfig) -> None:
    body.inertial = Inertial.from_geometry(
        Box((r.body_length + r.connector_length, r.body_width + 0.004, r.body_thickness + 0.003)),
        mass=0.020,
        origin=Origin(xyz=(_shell_center_x(r), 0.0, 0.0)),
    )


def _body_downstream_interface(
    r: ResolvedUsbDriveWithSwivelCoverConfig,
) -> InterfaceSpec:
    """Downstream interface points at the body front face (+x). The separate
    connector module mates its rear (-x) face here; molded connector / pivot /
    cover modules just read part_name."""
    return InterfaceSpec(
        interface_name="downstream",
        part_name="body",
        visual_name="body_front_face",
        face_side="positive_x",
        anchor_local=(_body_front_x(r), 0.0, 0.0),
        face_extents_uv=(r.body_width, r.body_thickness),
        extents_tol=0.60,
        contact_tol=0.0020,
    )


def _emit_body_front_face(body, r: ResolvedUsbDriveWithSwivelCoverConfig) -> None:
    """A thin plate flush with the body front, used as the named mating face
    for a separate connector part. It overlaps the shell so it is part of the
    body island regardless of body style."""
    body.visual(
        Box((0.0016, r.body_width * 0.9, r.body_thickness * 0.9)),
        origin=Origin(xyz=(_body_front_x(r) - 0.0008, 0.0, 0.0)),
        material="body_plastic",
        name="body_front_face", material_class_id="plastic.opaque_glossy_molded",
    )


def _build_monolithic_box_body(ctx: ModuleBuildContext) -> ModuleBuild:
    """S1 model.py:L28-L51 — single box shell. Simplest body."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]

    body = model.part("body")
    body.visual(
        Box((r.body_length, r.body_width, r.body_thickness)),
        origin=Origin(xyz=(_shell_center_x(r), 0.0, 0.0)),
        material="body_plastic",
        name="body_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    _emit_body_front_face(body, r)
    _body_inertial(body, r)
    return ModuleBuild(
        module_name="monolithic_box_body",
        parts_emitted=["body"],
        interfaces={"downstream": _body_downstream_interface(r)},
    )


def _build_extruded_rounded_body(ctx: ModuleBuildContext) -> ModuleBuild:
    """S2 model.py:L38-L65 — rounded-rect extrude shell (Mesh)."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]

    body = model.part("body")
    corner = min(r.body_width, r.body_thickness) * 0.42
    shell = _mesh_from_geometry_for_model(
        model,
        ExtrudeGeometry(
            rounded_rect_profile(r.body_length, r.body_width, corner, corner_segments=8),
            r.body_thickness,
            center=True,
        ).translate(_shell_center_x(r), 0.0, 0.0),
        "usb_body_rounded_shell",
    )
    body.visual(shell, material="body_plastic", name="body_shell", material_class_id="plastic.opaque_glossy_molded")
    _emit_body_front_face(body, r)
    _body_inertial(body, r)
    return ModuleBuild(
        module_name="extruded_rounded_body",
        parts_emitted=["body"],
        interfaces={"downstream": _body_downstream_interface(r)},
    )


def _build_multi_section_coaxial_body(ctx: ModuleBuildContext) -> ModuleBuild:
    """S3 model.py:L30-L72 — rear_cap + center_body + front_shoulder +
    connector_collar coaxial box sections (the usb_shell is handled by the
    connector slot)."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]

    body = model.part("body")
    x0 = _body_rear_x(r)
    bl = r.body_length
    # 4 coaxial sections spanning the body length, slightly tapering width.
    seg = [
        ("rear_cap", 0.22, 1.00, 1.00),
        ("center_body", 0.40, 1.00, 0.95),
        ("front_shoulder", 0.26, 0.92, 0.88),
        ("connector_collar", 0.12, 0.80, 0.78),
    ]
    cursor = x0
    for name, frac, wfrac, tfrac in seg:
        seg_len = bl * frac
        body.visual(
            Box((seg_len, r.body_width * wfrac, r.body_thickness * tfrac)),
            origin=Origin(xyz=(cursor + seg_len * 0.5, 0.0, 0.0)),
            material="body_plastic",
            name=name, material_class_id="plastic.opaque_glossy_molded",
        )
        cursor += seg_len
    _emit_body_front_face(body, r)
    _body_inertial(body, r)
    return ModuleBuild(
        module_name="multi_section_coaxial_body",
        parts_emitted=["body"],
        interfaces={"downstream": _body_downstream_interface(r)},
    )


def _build_lofted_taper_body(ctx: ModuleBuildContext) -> ModuleBuild:
    """S4 model.py:L80-L138 — section_loft tapered body_shell (Mesh) with a
    rubber nose_guard at the front."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]

    body = model.part("body")
    x0 = _body_rear_x(r)
    bl = r.body_length
    w = r.body_width
    t = r.body_thickness
    corner = min(w, t) * 0.40

    def _yz_section(x, width, thickness, radius):
        return [(x, y, z) for y, z in rounded_rect_profile(width, thickness, radius)]

    sections = [
        _yz_section(x0, w * 1.02, t * 1.02, corner),
        _yz_section(x0 + bl * 0.24, w, t, corner),
        _yz_section(x0 + bl * 0.74, w * 0.95, t * 0.92, corner * 0.9),
        _yz_section(x0 + bl, w * 0.86, t * 0.84, corner * 0.8),
    ]
    shell = _mesh_from_geometry_for_model(model, section_loft(sections), "usb_body_lofted_shell")
    body.visual(shell, material="body_plastic", name="body_shell", material_class_id="plastic.opaque_glossy_molded")
    # Rubber nose guard wrapping the front edge (S4 nose_guard).
    body.visual(
        Box((0.0075, w + 0.0012, t + 0.0012)),
        origin=Origin(xyz=(_body_front_x(r) - 0.0030, 0.0, 0.0)),
        material="tongue_black",
        name="nose_guard", material_class_id="rubber.smooth_plain",
    )
    _emit_body_front_face(body, r)
    _body_inertial(body, r)
    return ModuleBuild(
        module_name="lofted_taper_body",
        parts_emitted=["body"],
        interfaces={"downstream": _body_downstream_interface(r)},
    )


def _build_slotted_yoke_body(ctx: ModuleBuildContext) -> ModuleBuild:
    """S5 model.py:L79-L127 — rear_block + front_block + upper/lower
    pivot_bridge forming a mid-body pin slot for the swivel pin."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]

    body = model.part("body")
    px = r.pivot_x
    w = r.body_width
    t = r.body_thickness
    rear_x = _body_rear_x(r)
    front_x = _body_front_x(r)
    slot_half_x = max(r.pivot_radius * 1.4, 0.004)
    slot_half_z = r.pivot_radius * 1.1

    # Rear block: from rear_x to (px - slot_half_x).
    rear_len = (px - slot_half_x) - rear_x
    if rear_len < 0.004:
        rear_len = 0.004
    body.visual(
        Box((rear_len, w, t)),
        origin=Origin(xyz=(rear_x + rear_len * 0.5, 0.0, 0.0)),
        material="body_plastic",
        name="rear_block", material_class_id="plastic.opaque_glossy_molded",
    )
    # Front block: from (px + slot_half_x) to front_x.
    front_len = front_x - (px + slot_half_x)
    if front_len < 0.006:
        front_len = 0.006
    body.visual(
        Box((front_len, w, t)),
        origin=Origin(xyz=(front_x - front_len * 0.5, 0.0, 0.0)),
        material="body_plastic",
        name="front_block", material_class_id="plastic.opaque_glossy_molded",
    )
    # Upper + lower bridges flanking the pin slot (leave a gap at z=0 for pin).
    bridge_h = (t * 0.5) - slot_half_z
    if bridge_h < 0.0010:
        bridge_h = 0.0010
    body.visual(
        Box((2.0 * slot_half_x, w, bridge_h)),
        origin=Origin(xyz=(px, 0.0, slot_half_z + bridge_h * 0.5)),
        material="body_plastic",
        name="upper_pivot_bridge", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((2.0 * slot_half_x, w, bridge_h)),
        origin=Origin(xyz=(px, 0.0, -slot_half_z - bridge_h * 0.5)),
        material="body_plastic",
        name="lower_pivot_bridge", material_class_id="plastic.opaque_glossy_molded",
    )
    _emit_body_front_face(body, r)
    _body_inertial(body, r)
    return ModuleBuild(
        module_name="slotted_yoke_body",
        parts_emitted=["body"],
        interfaces={"downstream": _body_downstream_interface(r)},
    )


def _cadquery_body_shell(r: ResolvedUsbDriveWithSwivelCoverConfig):
    """S6 model.py:L19-L29 — one injection-molded filleted half-shell."""
    import cadquery as cq

    fillet_x = min(r.body_width, r.body_thickness) * 0.40
    end_fillet = min(0.0012, fillet_x * 0.5)
    return (
        cq.Workplane("XY")
        .box(r.body_length, r.body_width, r.body_thickness)
        .edges("|X")
        .fillet(fillet_x)
        .edges(">X or <X")
        .fillet(end_fillet)
        .translate((_shell_center_x(r), 0.0, 0.0))
    )


def _build_cadquery_molded_body(ctx: ModuleBuildContext) -> ModuleBuild:
    """S6 model.py:L19-L188 — CadQuery filleted single-piece molded shell.

    Falls back to an ExtrudeGeometry rounded-rect shell if cadquery cannot
    import in this environment (primitive stays a Mesh, never a crude Box).
    """
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]

    body = model.part("body")
    try:
        shell = _mesh_from_cadquery_for_model(
            model, _cadquery_body_shell(r), "cadquery_molded_body_shell", tolerance=0.00035
        )
    except Exception:
        corner = min(r.body_width, r.body_thickness) * 0.42
        shell = _mesh_from_geometry_for_model(
            model,
            ExtrudeGeometry(
                rounded_rect_profile(r.body_length, r.body_width, corner, corner_segments=10),
                r.body_thickness,
                center=True,
            ).translate(_shell_center_x(r), 0.0, 0.0),
            "cadquery_molded_body_shell_fallback",
        )
    body.visual(shell, material="body_plastic", name="body_shell", material_class_id="plastic.opaque_glossy_molded")
    _emit_body_front_face(body, r)
    _body_inertial(body, r)
    return ModuleBuild(
        module_name="cadquery_molded_body",
        parts_emitted=["body"],
        interfaces={"downstream": _body_downstream_interface(r)},
    )


# --------------------------------------------------------------------------- #
# Module factories — connector (Slot B). molded/in-body variants emit visuals
# onto body; separate variants emit a connector part FIXED to the body front.
# --------------------------------------------------------------------------- #


def _emit_molded_plug(body, r: ResolvedUsbDriveWithSwivelCoverConfig) -> list[str]:
    """S1 model.py:L35-L40 — connector as one box visual on the body."""
    body.visual(
        Box((r.connector_length, r.connector_width, r.connector_thickness)),
        origin=Origin(xyz=(_connector_origin_x(r), 0.0, 0.0)),
        material="connector_steel",
        name="usb_plug", material_class_id="metal.stainless_matte",
    )
    return ["usb_plug"]


def _emit_four_wall_in_body(body, r: ResolvedUsbDriveWithSwivelCoverConfig) -> list[str]:
    """S6 model.py:L117-L160 — four-wall USB-A shell + tongue + contact pads,
    all molded into the body."""
    cx = _connector_origin_x(r)
    cl = r.connector_length
    cw = r.connector_width
    ch = r.connector_thickness
    shell_t = 0.00050
    names: list[str] = []
    body.visual(
        Box((cl, cw, shell_t)),
        origin=Origin(xyz=(cx, 0.0, ch * 0.5 - shell_t * 0.5)),
        material="connector_steel",
        name="connector_top_wall", material_class_id="metal.stainless_matte",
    )
    body.visual(
        Box((cl, cw, shell_t)),
        origin=Origin(xyz=(cx, 0.0, -ch * 0.5 + shell_t * 0.5)),
        material="connector_steel",
        name="connector_bottom_wall", material_class_id="metal.stainless_matte",
    )
    body.visual(
        Box((cl, 0.00055, ch - 2.0 * shell_t)),
        origin=Origin(xyz=(cx, cw * 0.5 - 0.000275, 0.0)),
        material="connector_steel",
        name="connector_side_wall_0", material_class_id="metal.stainless_matte",
    )
    body.visual(
        Box((cl, 0.00055, ch - 2.0 * shell_t)),
        origin=Origin(xyz=(cx, -cw * 0.5 + 0.000275, 0.0)),
        material="connector_steel",
        name="connector_side_wall_1", material_class_id="metal.stainless_matte",
    )
    body.visual(
        Box((cl * 0.85, cw * 0.55, 0.0010)),
        origin=Origin(xyz=(cx - cl * 0.05, 0.0, -0.0006)),
        material="tongue_black",
        name="connector_tongue", material_class_id="plastic.opaque_generic",
    )
    names += [
        "connector_top_wall",
        "connector_bottom_wall",
        "connector_side_wall_0",
        "connector_side_wall_1",
        "connector_tongue",
    ]
    for i, y in enumerate((-cw * 0.18, cw * 0.18)):
        body.visual(
            Box((0.0023, 0.0011, 0.00020)),
            origin=Origin(xyz=(cx + cl * 0.30, y, 0.0)),
            material="accent",
            name=f"contact_pad_{i}", material_class_id="metal.precious_gold",
        )
        names.append(f"contact_pad_{i}")
    return names


def _build_connector_part_walls(
    connector, r: ResolvedUsbDriveWithSwivelCoverConfig, *, with_contacts: bool
) -> None:
    """Shared 4-wall + tongue geometry for a SEPARATE connector part. Built
    in the connector's own frame: rear (-x) face at x=0, protruding to +x.
    Adapted from S4 model.py:L139-L188 / S5 model.py:L129-L169."""
    cl = r.connector_length
    cw = r.connector_width
    ch = r.connector_thickness
    shell_t = 0.00050
    connector.visual(
        Box((cl, cw, shell_t)),
        origin=Origin(xyz=(cl * 0.5, 0.0, ch * 0.5 - shell_t * 0.5)),
        material="connector_steel",
        name="shell_top", material_class_id="metal.stainless_matte",
    )
    connector.visual(
        Box((cl, cw, shell_t)),
        origin=Origin(xyz=(cl * 0.5, 0.0, -ch * 0.5 + shell_t * 0.5)),
        material="connector_steel",
        name="shell_bottom", material_class_id="metal.stainless_matte",
    )
    connector.visual(
        Box((cl, 0.00055, ch - 2.0 * shell_t)),
        origin=Origin(xyz=(cl * 0.5, cw * 0.5 - 0.000275, 0.0)),
        material="connector_steel",
        name="shell_right", material_class_id="metal.stainless_matte",
    )
    connector.visual(
        Box((cl, 0.00055, ch - 2.0 * shell_t)),
        origin=Origin(xyz=(cl * 0.5, -cw * 0.5 + 0.000275, 0.0)),
        material="connector_steel",
        name="shell_left", material_class_id="metal.stainless_matte",
    )
    # Rear insert plate covering the -x mouth (this is the mating face onto
    # the body front). It overlaps the four walls so the part is connected.
    connector.visual(
        Box((0.0018, cw, ch)),
        origin=Origin(xyz=(0.0009, 0.0, 0.0)),
        material="tongue_black",
        name="rear_insert", material_class_id="plastic.opaque_generic",
    )
    connector.visual(
        Box((cl - 0.0018, cw * 0.70, 0.0022)),
        origin=Origin(xyz=(0.0018 + (cl - 0.0018) * 0.5, 0.0, -0.00015)),
        material="tongue_black",
        name="contact_tongue", material_class_id="plastic.opaque_generic",
    )
    if with_contacts:
        connector.visual(
            Box((cl * 0.55, cw * 0.55, 0.0008)),
            origin=Origin(xyz=(cl * 0.55, 0.0, 0.0010)),
            material="tongue_black",
            name="tongue_support", material_class_id="plastic.opaque_generic",
        )


def _emit_separate_connector(
    ctx: ModuleBuildContext, r: ResolvedUsbDriveWithSwivelCoverConfig, *, with_contacts: bool
) -> ModuleBuild:
    """Emit an independent connector part FIXED to the body front (Rule 2:
    real mating face on both sides). Adapted from S4 / S5."""
    model = ctx.model
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = model.get_part(body_name)

    connector = model.part("connector")
    _build_connector_part_walls(connector, r, with_contacts=with_contacts)
    connector.inertial = Inertial.from_geometry(
        Box((r.connector_length, r.connector_width, r.connector_thickness)),
        mass=0.003,
        origin=Origin(xyz=(r.connector_length * 0.5, 0.0, 0.0)),
    )

    module_name = "plate_shell_with_contacts" if with_contacts else "separate_fixed_connector_part"
    # FIXED to the body front: connector -x face (rear_insert) mates the
    # body's +x front face. Push the connector 1mm INTO the body so the
    # mating faces actually contact (front_face is just inside front_x).
    model.articulation(
        "body_to_connector",
        ArticulationType.FIXED,
        parent=body,
        child=connector,
        origin=Origin(xyz=(_body_front_x(r) - 0.0008, 0.0, 0.0)),
        mating=MatingContract(
            parent_face_geometry="body_front_face",
            parent_face_side="positive_x",
            child_face_geometry="rear_insert",
            child_face_side="negative_x",
            contact_tol=0.0020,
        ),
    )
    return ModuleBuild(
        module_name=module_name,
        parts_emitted=["connector"],
        internal_articulations=["body_to_connector"],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_molded_plug_in_body(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = ctx.model.get_part(body_name)
    _emit_molded_plug(body, r)
    return ModuleBuild(
        module_name="molded_plug_in_body",
        parts_emitted=[],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_four_wall_shell_in_body(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = ctx.model.get_part(body_name)
    _emit_four_wall_in_body(body, r)
    return ModuleBuild(
        module_name="four_wall_shell_in_body",
        parts_emitted=[],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_separate_fixed_connector_part(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    return _emit_separate_connector(ctx, r, with_contacts=False)


def _build_plate_shell_with_contacts(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    return _emit_separate_connector(ctx, r, with_contacts=True)


# --------------------------------------------------------------------------- #
# Module factories — pivot_hardware (Slot D). integral / embedded / side_lug
# emit body visuals; separate_pin_part emits an independent pivot_pin part
# FIXED to the body.
# --------------------------------------------------------------------------- #


def _build_integral_sleeve_in_body(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = ctx.model.get_part(body_name)
    _emit_integral_sleeve(body, r)
    return ModuleBuild(
        module_name="integral_sleeve_in_body",
        parts_emitted=[],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_body_embedded_pin_with_bosses(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = ctx.model.get_part(body_name)
    _emit_embedded_pin(body, r)
    return ModuleBuild(
        module_name="body_embedded_pin_with_bosses",
        parts_emitted=[],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_side_lug_pin_stack(ctx: ModuleBuildContext) -> ModuleBuild:
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = ctx.model.get_part(body_name)
    _emit_side_lug_stack(body, r)
    return ModuleBuild(
        module_name="side_lug_pin_stack",
        parts_emitted=[],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_separate_pivot_pin_part(ctx: ModuleBuildContext) -> ModuleBuild:
    """S5 model.py:L204-L243 — independent pivot_pin part (shaft + 2 heads)
    FIXED to the body, running along the pivot axis through the body."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = model.get_part(body_name)

    # Real anchoring boss on the body so the pin has something to mate.
    _emit_body_pivot_anchor(body, r)

    pin = model.part("pivot_pin")
    span = _pivot_span(r)
    head_t = 0.0012
    # Pin built in its own frame: shaft centered on origin along the pivot
    # axis. The shaft -<axis> face mates the body's pivot_mount_boss.
    pin.visual(
        Cylinder(radius=r.pivot_radius * 0.7, length=span),
        origin=Origin(rpy=_pivot_rpy(r)),
        material="dark_metal",
        name="shaft", material_class_id="metal.blackened_gunmetal",
    )
    head_off = span * 0.5 + head_t * 0.5
    if r.pivot_axis_family == "top_swivel":
        h0 = (0.0, 0.0, head_off)
        h1 = (0.0, 0.0, -head_off)
    else:
        h0 = (0.0, head_off, 0.0)
        h1 = (0.0, -head_off, 0.0)
    pin.visual(
        Cylinder(radius=r.pivot_radius * 1.1, length=head_t),
        origin=Origin(xyz=h0, rpy=_pivot_rpy(r)),
        material="dark_metal",
        name="left_head", material_class_id="metal.blackened_gunmetal",
    )
    pin.visual(
        Cylinder(radius=r.pivot_radius * 1.1, length=head_t),
        origin=Origin(xyz=h1, rpy=_pivot_rpy(r)),
        material="dark_metal",
        name="right_head", material_class_id="metal.blackened_gunmetal",
    )
    pin.inertial = Inertial.from_geometry(
        Cylinder(radius=r.pivot_radius * 1.1, length=span),
        mass=0.001,
        origin=Origin(rpy=_pivot_rpy(r)),
    )

    # FIXED to the body at the pivot. The pin's shaft passes THROUGH the
    # boss (captured pin) along the pivot axis — a pin-through-sleeve contact
    # that the MatingContract abstraction cannot model, so the mating contract
    # is omitted (grandfathered) and the boss<->shaft overlap is allowed in
    # run_*_tests. The pivot_mount_boss visually anchors the pin (Rule 2).
    model.articulation(
        "body_to_pin",
        ArticulationType.FIXED,
        parent=body,
        child=pin,
        origin=_swivel_origin_origin(r),
    )
    return ModuleBuild(
        module_name="separate_pivot_pin_part",
        parts_emitted=["pivot_pin"],
        internal_articulations=["body_to_pin"],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _swivel_origin_origin(r: ResolvedUsbDriveWithSwivelCoverConfig) -> Origin:
    return Origin(xyz=_swivel_origin(r))


# --------------------------------------------------------------------------- #
# Module factories — body_accessory (Slot E)
# --------------------------------------------------------------------------- #


def _build_accessory_none(ctx: ModuleBuildContext) -> ModuleBuild:
    return ModuleBuild(
        module_name="none",
        parts_emitted=[],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_status_window_fixed_part(ctx: ModuleBuildContext) -> ModuleBuild:
    """S9 model.py:L182-L219 — status_window indicator lens as an independent
    FIXED part on the body top face."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = model.get_part(body_name)

    win_len = min(0.010, r.body_length * 0.25)
    win_w = r.body_width * 0.45
    win_t = 0.0014
    # Window mounted near the center of the body top, away from the pivot.
    win_x = _shell_center_x(r) + r.body_length * 0.12

    # Real anchoring pad on the body top under the window (Rule 2). It
    # overlaps the shell core.
    body.visual(
        Box((win_len + 0.0010, win_w + 0.0010, 0.0010)),
        origin=Origin(xyz=(win_x, 0.0, r.body_thickness * 0.5 - 0.0004)),
        material="body_plastic",
        name="window_pad", material_class_id="plastic.opaque_glossy_molded",
    )

    window = model.part("status_window")
    window.visual(
        Box((win_len, win_w, win_t)),
        origin=Origin(xyz=(0.0, 0.0, win_t * 0.5)),
        material="window_smoke",
        name="status_window_lens", material_class_id="glass.smoked_tinted",
    )
    window.inertial = Inertial.from_geometry(
        Box((win_len, win_w, win_t)),
        mass=0.0003,
        origin=Origin(xyz=(0.0, 0.0, win_t * 0.5)),
    )
    # FIXED to the body top: window -z face mates the window_pad +z face.
    model.articulation(
        "body_to_accessory",
        ArticulationType.FIXED,
        parent=body,
        child=window,
        origin=Origin(xyz=(win_x, 0.0, r.body_thickness * 0.5 + 0.0001)),
        mating=MatingContract(
            parent_face_geometry="window_pad",
            parent_face_side="positive_z",
            child_face_geometry="status_window_lens",
            child_face_side="negative_z",
            contact_tol=0.0020,
        ),
    )
    return ModuleBuild(
        module_name="status_window_fixed_part",
        parts_emitted=["status_window"],
        internal_articulations=["body_to_accessory"],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_service_plate_fixed_part(ctx: ModuleBuildContext) -> ModuleBuild:
    """Precision service plate / scale insert inspired by the gated
    five-star service-plate variants. It is an independent FIXED child so it
    adds a real accessory part type instead of another loose decal."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = model.get_part(body_name)

    plate_len = min(0.016, r.body_length * 0.34)
    plate_w = min(0.0065, r.body_width * 0.42)
    plate_t = 0.00065
    plate_x = _shell_center_x(r) + r.body_length * 0.10
    plate_y = -r.body_width * 0.18
    top_z = r.body_thickness * 0.5

    body.visual(
        Box((plate_len + 0.0012, plate_w + 0.0012, 0.00035)),
        origin=Origin(xyz=(plate_x, plate_y, top_z - 0.00008)),
        material="body_plastic",
        name="service_plate_recess", material_class_id="plastic.opaque_glossy_molded",
    )

    plate = model.part("service_plate")
    plate.visual(
        Box((plate_len, plate_w, plate_t)),
        origin=Origin(xyz=(0.0, 0.0, plate_t * 0.5)),
        material="dark_metal",
        name="service_plate_base", material_class_id="metal.blackened_gunmetal",
    )
    for idx, x in enumerate((-plate_len * 0.37, plate_len * 0.37)):
        plate.visual(
            Cylinder(radius=0.00065, length=0.00032),
            origin=Origin(xyz=(x, -plate_w * 0.27, plate_t + 0.00004)),
            material="satin_steel",
            name=f"plate_screw_{idx}", material_class_id="metal.stainless_matte",
        )
    scale_x0 = -plate_len * 0.28
    for idx in range(5):
        tick_h = plate_w * (0.46 if idx % 2 == 0 else 0.30)
        plate.visual(
            Box((0.00016, tick_h, 0.00008)),
            origin=Origin(
                xyz=(scale_x0 + idx * plate_len * 0.105, plate_w * 0.19, plate_t + 0.00002)
            ),
            material="laser_etch",
            name=f"service_scale_tick_{idx}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    plate.inertial = Inertial.from_geometry(
        Box((plate_len, plate_w, plate_t)),
        mass=0.0005,
        origin=Origin(xyz=(0.0, 0.0, plate_t * 0.5)),
    )

    model.articulation(
        "body_to_accessory",
        ArticulationType.FIXED,
        parent=body,
        child=plate,
        origin=Origin(xyz=(plate_x, plate_y, top_z + 0.00008)),
        mating=MatingContract(
            parent_face_geometry="service_plate_recess",
            parent_face_side="positive_z",
            child_face_geometry="service_plate_base",
            child_face_side="negative_z",
            contact_tol=0.0020,
        ),
    )
    return ModuleBuild(
        module_name="service_plate_fixed_part",
        parts_emitted=["service_plate"],
        internal_articulations=["body_to_accessory"],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


# --------------------------------------------------------------------------- #
# Module factories — swivel_cover (Slot C). The ONE main DOF. The cover is a
# REVOLUTE/CONTINUOUS child of the body; its frame origin is the pivot. Closed
# pose (joint angle 0) wraps/aligns the connector; open pose lets it go.
#
# Cover frame convention: origin = pivot. The cover body extends toward +x
# (over the connector) in the closed pose. Pivot collars/tabs sit at the
# origin so the swivel origin lies in the cover AABB.
# --------------------------------------------------------------------------- #


def _cover_span_x(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    """Length the cover reaches from the pivot to just past the connector
    front, so the closed cover spans the connector lengthwise."""
    front_clearance = max(0.0032, 2.0 * r.cover_wall + 0.0009)
    return (_connector_front_x(r) - r.pivot_x) + front_clearance


def _cover_inner_half_w(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    return r.body_width * 0.5 + r.cover_clearance


def _cover_inner_half_h(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    return r.body_thickness * 0.5 + r.cover_clearance


def _cover_pivot_tab_x(r: ResolvedUsbDriveWithSwivelCoverConfig) -> float:
    """S1/S5 place cover pivot cheeks slightly into the cover frame, overlapping
    the side arms instead of floating exactly at the mathematical joint origin."""
    return min(0.0040, _cover_span_x(r) * 0.12, r.pivot_radius * 1.1)


def _emit_top_swivel_pivot_side_web(
    cover, r: ResolvedUsbDriveWithSwivelCoverConfig, *, radius_scale: float
) -> str:
    """Connect top-swivel upper/lower pivot tabs with a web offset outside the
    solid body pin. This keeps the source-like captured-pivot cue without
    modeling a solid cover barrel through a solid body pin."""
    rr = r.pivot_radius * radius_scale
    tab_x = _cover_pivot_tab_x(r)
    span = _pivot_span(r)
    web_x = tab_x + rr * 0.70
    cover.visual(
        Box((rr * 0.70, 0.0014, span)),
        origin=Origin(xyz=(web_x, 0.0, 0.0)),
        material="satin_steel",
        name="pivot_side_web", material_class_id="metal.stainless_matte",
    )
    return "pivot_side_web"


def _emit_cover_pivot_collars(
    cover, r: ResolvedUsbDriveWithSwivelCoverConfig, *, radius_scale: float = 1.2
) -> list[str]:
    """Two pivot tabs/collars at the cover origin, coaxial with the body
    pivot. They sit at the pivot axis so the swivel origin lies inside the
    cover AABB and the cover is captured on the pin. Returns visual names."""
    span = _pivot_span(r)
    off = span * 0.5 - 0.0008
    rr = r.pivot_radius * radius_scale
    tab_x = _cover_pivot_tab_x(r)
    if r.pivot_axis_family == "top_swivel":
        p0 = (tab_x, 0.0, off)
        p1 = (tab_x, 0.0, -off)
    else:
        p0 = (tab_x, off, 0.0)
        p1 = (tab_x, -off, 0.0)
    names = ["left_pivot_tab", "right_pivot_tab"]
    if r.pivot_axis_family == "top_swivel":
        names.append(_emit_top_swivel_pivot_side_web(cover, r, radius_scale=radius_scale))
    cover.visual(
        Cylinder(radius=rr, length=0.0014),
        origin=Origin(xyz=p0, rpy=_pivot_rpy(r)),
        material="satin_steel",
        name="left_pivot_tab", material_class_id="metal.stainless_matte",
    )
    cover.visual(
        Cylinder(radius=rr, length=0.0014),
        origin=Origin(xyz=p1, rpy=_pivot_rpy(r)),
        material="satin_steel",
        name="right_pivot_tab", material_class_id="metal.stainless_matte",
    )
    return names


def _emit_cover_collar_link(
    cover, r: ResolvedUsbDriveWithSwivelCoverConfig, body_elem_x: float
) -> str:
    """A thin spar from the pivot collars out to the main cover body so the
    pivot tabs are not islands. Spans x ∈ [0, body_elem_x]."""
    half_w = _cover_inner_half_w(r) + r.cover_wall
    link_len = max(0.002, body_elem_x)
    cover.visual(
        Box((link_len, 2.0 * half_w, 0.0014)),
        origin=Origin(xyz=(link_len * 0.5, 0.0, _cover_inner_half_h(r) + r.cover_wall * 0.5)),
        material="satin_steel",
        name="pivot_link_spar", material_class_id="metal.stainless_matte",
    )
    return "pivot_link_spar"


def _emit_cover_centerline_link(
    cover,
    r: ResolvedUsbDriveWithSwivelCoverConfig,
    *,
    cover_y_min: float,
    cover_y_max: float,
    z: float,
    name: str = "pivot_link_spar",
) -> str:
    """Bridge cover pivot collars/tabs at local y=0 to the main cover shell."""
    if r.pivot_axis_family == "side_flip":
        span = _pivot_span(r)
        off = span * 0.5 - 0.0008
        z_size = abs(z) + 0.0014
        z_center = z * 0.5
        y_size = max(0.0034, r.cover_wall * 3.2)
        for idx, y in enumerate((off, -off)):
            cover.visual(
                Box((0.0045, y_size, z_size)),
                origin=Origin(xyz=(0.00225, y, z_center)),
                material="satin_steel",
                name=f"{name}_{idx}", material_class_id="metal.stainless_matte",
            )
        return name

    rr = r.pivot_radius * 1.5
    y_lo = min(cover_y_min, -rr)
    y_hi = max(cover_y_max, rr)
    z_size = abs(z) + 0.0014
    z_center = z * 0.5
    cover.visual(
        Box((0.0045, y_hi - y_lo, z_size)),
        origin=Origin(xyz=(0.00225, (y_hi + y_lo) * 0.5, z_center)),
        material="satin_steel",
        name=name, material_class_id="metal.stainless_matte",
    )
    return name


def _build_u_arm_bridge_cover(ctx: ModuleBuildContext) -> ModuleBuild:
    """S1 model.py:L53-L88 — left_arm + right_arm side strips + front_bridge
    crossbar + two pivot_tab cylinders. Open U-yoke."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = model.get_part(body_name)

    cover = model.part("swivel_cover")
    span_x = _cover_span_x(r)
    cy = _cover_center_y(r)
    cz = _cover_body_z(r)
    half_w = _cover_inner_half_w(r) + r.cover_wall * 0.5
    arm_h = r.body_thickness + 2.0 * r.cover_clearance
    arm_thk = r.cover_wall * 1.4
    # Two side arms running alongside the body (overlap the pivot tabs at x=0).
    cover.visual(
        Box((span_x, arm_thk, arm_h)),
        origin=Origin(xyz=(span_x * 0.5, cy + half_w, cz)),
        material="cover_shell",
        name="left_arm", material_class_id="metal.paint_coated",
    )
    cover.visual(
        Box((span_x, arm_thk, arm_h)),
        origin=Origin(xyz=(span_x * 0.5, cy - half_w, cz)),
        material="cover_shell",
        name="right_arm", material_class_id="metal.paint_coated",
    )
    # Front bridge crossbar joining the two arms at the far end.
    cover.visual(
        Box((arm_thk, 2.0 * half_w + arm_thk, arm_h)),
        origin=Origin(xyz=(span_x - arm_thk * 0.5, cy, cz)),
        material="cover_shell",
        name="front_bridge", material_class_id="metal.paint_coated",
    )
    _emit_cover_pivot_collars(cover, r, radius_scale=1.2)
    _emit_cover_centerline_link(
        cover,
        r,
        cover_y_min=cy - half_w - arm_thk * 0.5,
        cover_y_max=cy + half_w + arm_thk * 0.5,
        z=cz,
    )
    cover.inertial = Inertial.from_geometry(
        Box((span_x, 2.0 * half_w, arm_h)),
        mass=0.010,
        origin=Origin(xyz=(span_x * 0.5, cy, cz)),
    )
    _emit_swivel_joint(model, body, cover, r)
    return ModuleBuild(
        module_name="u_arm_bridge_cover",
        parts_emitted=["swivel_cover"],
        internal_articulations=["body_to_cover"],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_u_channel_wrap_cover(ctx: ModuleBuildContext) -> ModuleBuild:
    """S2 model.py:L67-L102 — top_shell + bottom_shell + side_spine three-face
    wrap derived from body size + clearance."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = model.get_part(body_name)

    cover = model.part("swivel_cover")
    span_x = _cover_span_x(r)
    cy = _cover_center_y(r)
    cz = _cover_body_z(r)
    inner_w = 2.0 * _cover_inner_half_w(r)
    inner_h = 2.0 * _cover_inner_half_h(r)
    wall = r.cover_wall
    plate_z = inner_h * 0.5 + wall * 0.5
    if r.pivot_axis_family == "side_flip":
        top_z = cz + plate_z
        side_y = inner_w * 0.5 + wall * 0.5
        cover.visual(
            Box((span_x, inner_w + 2.0 * wall, wall)),
            origin=Origin(xyz=(span_x * 0.5, cy, top_z)),
            material="cover_shell",
            name="top_shell", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Box((span_x, wall, inner_h)),
            origin=Origin(xyz=(span_x * 0.5, cy + side_y, cz)),
            material="cover_shell",
            name="side_spine_0", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Box((span_x, wall, inner_h)),
            origin=Origin(xyz=(span_x * 0.5, cy - side_y, cz)),
            material="cover_shell",
            name="side_spine_1", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Box((wall, inner_w + 2.0 * wall, inner_h)),
            origin=Origin(xyz=(span_x - wall * 0.5, cy, cz)),
            material="cover_shell",
            name="front_lip", material_class_id="metal.paint_coated",
        )
        _emit_cover_pivot_collars(cover, r, radius_scale=1.2)
        _emit_cover_wrap_link(cover, r, cy, top_z)
        cover.inertial = Inertial.from_geometry(
            Box((span_x, inner_w + 2.0 * wall, inner_h + wall)),
            mass=0.010,
            origin=Origin(xyz=(span_x * 0.5, cy, cz + wall * 0.25)),
        )
        _emit_swivel_joint(model, body, cover, r)
        return ModuleBuild(
            module_name="u_channel_wrap_cover",
            parts_emitted=["swivel_cover"],
            internal_articulations=["body_to_cover"],
            interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
        )

    plate_y = cy + inner_w * 0.5 + wall * 0.5

    cover.visual(
        Box((span_x, inner_w + wall, wall)),
        origin=Origin(xyz=(span_x * 0.5, plate_y, cz + plate_z)),
        material="cover_shell",
        name="top_shell", material_class_id="metal.paint_coated",
    )
    cover.visual(
        Box((span_x, inner_w + wall, wall)),
        origin=Origin(xyz=(span_x * 0.5, plate_y, cz - plate_z)),
        material="cover_shell",
        name="bottom_shell", material_class_id="metal.paint_coated",
    )
    cover.visual(
        Box((span_x, wall, inner_h + 2.0 * wall)),
        origin=Origin(xyz=(span_x * 0.5, plate_y + inner_w * 0.5 + wall * 0.5, cz)),
        material="cover_shell",
        name="side_spine", material_class_id="metal.paint_coated",
    )
    _emit_cover_pivot_collars(cover, r, radius_scale=1.2)
    # The shells are offset to +y (wrap one side); bridge the pivot tabs (at
    # y=±span) to the shell with a spar.
    _emit_cover_wrap_link(cover, r, plate_y, cz + plate_z)
    _emit_cover_centerline_link(
        cover,
        r,
        cover_y_min=min(cy - inner_w * 0.5 - wall, plate_y),
        cover_y_max=max(cy + inner_w * 0.5 + wall, plate_y + inner_w + wall),
        z=cz,
        name="pivot_lower_link_spar",
    )
    cover.inertial = Inertial.from_geometry(
        Box((span_x, inner_w + 2.0 * wall, inner_h + 2.0 * wall)),
        mass=0.010,
        origin=Origin(xyz=(span_x * 0.5, cy + (plate_y - cy) * 0.6, cz)),
    )
    _emit_swivel_joint(model, body, cover, r)
    return ModuleBuild(
        module_name="u_channel_wrap_cover",
        parts_emitted=["swivel_cover"],
        internal_articulations=["body_to_cover"],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _emit_cover_wrap_link(
    cover, r: ResolvedUsbDriveWithSwivelCoverConfig, plate_y: float, plate_z: float
) -> None:
    """Bridge the pivot tabs (at the pivot axis) to the offset wrap shells so
    nothing floats. A small plate spanning from the tabs to the top shell."""
    span = _pivot_span(r)
    off = span * 0.5 - 0.0008
    link_len = 0.0040
    if r.pivot_axis_family == "side_flip":
        z_size = abs(plate_z) + 0.0014
        z_center = plate_z * 0.5
        y_size = max(0.0034, r.cover_wall * 3.2)
        for idx, y in enumerate((off, -off)):
            cover.visual(
                Box((link_len, y_size, z_size)),
                origin=Origin(xyz=(link_len * 0.5, y, z_center)),
                material="satin_steel",
                name=f"pivot_link_spar_{idx}", material_class_id="metal.stainless_matte",
            )
        return

    # spar from x=0 outward. For top-swivel this is a local side web near the
    # side pivot, not a wide bridge across the USB body.
    y_pad = max(0.0012, r.cover_wall * 1.4)
    y_lo = min(0.0, plate_y) - y_pad
    y_hi = max(0.0, plate_y) + y_pad
    z_size = abs(plate_z) + 0.0014
    z_center = plate_z * 0.5
    cover.visual(
        Box((link_len, (y_hi - y_lo), z_size)),
        origin=Origin(xyz=(link_len * 0.5, (y_hi + y_lo) * 0.5, z_center)),
        material="satin_steel",
        name="pivot_link_spar", material_class_id="metal.stainless_matte",
    )


def _build_dual_plate_bridge_cover(ctx: ModuleBuildContext) -> ModuleBuild:
    """S3 model.py:L74-L110 — top_plate + bottom_plate + side_bridge + two
    rivet_head cylinders. Upper/lower plates with a single side spine."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = model.get_part(body_name)

    cover = model.part("swivel_cover")
    span_x = _cover_span_x(r)
    cy = _cover_center_y(r)
    cz = _cover_body_z(r)
    inner_w = 2.0 * _cover_inner_half_w(r)
    inner_h = 2.0 * _cover_inner_half_h(r)
    wall = r.cover_wall
    plate_z = inner_h * 0.5 + wall * 0.5
    if r.pivot_axis_family == "side_flip":
        top_z = cz + plate_z
        side_y = inner_w * 0.5 + wall * 0.5
        cover.visual(
            Box((span_x, inner_w + 2.0 * wall, wall)),
            origin=Origin(xyz=(span_x * 0.5, cy, top_z)),
            material="cover_shell",
            name="top_plate", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Box((span_x, wall, inner_h)),
            origin=Origin(xyz=(span_x * 0.5, cy - side_y, cz)),
            material="cover_shell",
            name="side_bridge", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Box((span_x, wall, inner_h)),
            origin=Origin(xyz=(span_x * 0.5, cy + side_y, cz)),
            material="cover_shell",
            name="side_bridge_opposite", material_class_id="metal.paint_coated",
        )
        rib_z = top_z - wall * 0.45
        rib_y = inner_w * 0.28
        for idx, y in enumerate((-rib_y, rib_y)):
            cover.visual(
                Box((span_x * 0.76, wall * 0.7, wall)),
                origin=Origin(xyz=(span_x * 0.53, cy + y, rib_z)),
                material="dark_metal",
                name=f"pressed_rib_{idx}", material_class_id="metal.blackened_gunmetal",
            )
        cover.visual(
            Box((wall, inner_w + 2.0 * wall, inner_h)),
            origin=Origin(xyz=(span_x - wall * 0.5, cy, cz)),
            material="cover_shell",
            name="front_lip", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Cylinder(radius=r.pivot_radius * 0.88, length=0.0008),
            origin=Origin(xyz=(0.0040, cy - rib_y, top_z + 0.00045)),
            material="satin_steel",
            name="top_rivet_head", material_class_id="metal.stainless_matte",
        )
        cover.visual(
            Cylinder(radius=r.pivot_radius * 0.88, length=0.0008),
            origin=Origin(xyz=(0.0040, cy + rib_y, top_z + 0.00045)),
            material="satin_steel",
            name="bottom_rivet_head", material_class_id="metal.stainless_matte",
        )
        _emit_cover_pivot_collars(cover, r, radius_scale=1.2)
        _emit_cover_wrap_link(cover, r, cy, top_z)
    else:
        plate_y = cy - (inner_w * 0.5)  # offset to -y side (single side bridge there)

        cover.visual(
            Box((span_x, inner_w, wall)),
            origin=Origin(xyz=(span_x * 0.5, plate_y, cz + plate_z)),
            material="cover_shell",
            name="top_plate", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Box((span_x, inner_w, wall)),
            origin=Origin(xyz=(span_x * 0.5, plate_y, cz - plate_z)),
            material="cover_shell",
            name="bottom_plate", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Box((span_x, wall, inner_h)),
            origin=Origin(xyz=(span_x * 0.5, plate_y - inner_w * 0.5 - wall * 0.5, cz)),
            material="cover_shell",
            name="side_bridge", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Cylinder(radius=r.pivot_radius * 1.05, length=0.0008),
            origin=Origin(xyz=(0.0040, plate_y, cz + plate_z + 0.0006)),
            material="satin_steel",
            name="top_rivet_head", material_class_id="metal.stainless_matte",
        )
        cover.visual(
            Cylinder(radius=r.pivot_radius * 1.05, length=0.0008),
            origin=Origin(xyz=(0.0040, plate_y, cz - plate_z - 0.0006)),
            material="satin_steel",
            name="bottom_rivet_head", material_class_id="metal.stainless_matte",
        )
        _emit_cover_pivot_collars(cover, r, radius_scale=1.2)
        _emit_cover_wrap_link(cover, r, plate_y, cz + plate_z)
        _emit_cover_centerline_link(
            cover,
            r,
            cover_y_min=min(cy - inner_w - wall, plate_y - inner_w * 0.5 - wall),
            cover_y_max=max(cy + inner_w + wall, plate_y + inner_w * 0.5 + wall),
            z=cz,
            name="pivot_lower_link_spar",
        )
    inertial_y = cy
    if r.pivot_axis_family == "top_swivel":
        inertial_y = cy + (plate_y - cy) * 0.6
    cover.inertial = Inertial.from_geometry(
        Box((span_x, inner_w + 2.0 * wall, inner_h + 2.0 * wall)),
        mass=0.009,
        origin=Origin(xyz=(span_x * 0.5, inertial_y, cz)),
    )
    _emit_swivel_joint(model, body, cover, r)
    return ModuleBuild(
        module_name="dual_plate_bridge_cover",
        parts_emitted=["swivel_cover"],
        internal_articulations=["body_to_cover"],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _cadquery_cover_shell(r: ResolvedUsbDriveWithSwivelCoverConfig):
    """S6 model.py:L48-L62 — one stamped U-channel hood: hinge sleeve + web +
    top + two sides + front lip. Built in cover frame (origin = pivot)."""
    import cadquery as cq

    span_x = _cover_span_x(r)
    inner_w = 2.0 * _cover_inner_half_w(r)
    inner_h = 2.0 * _cover_inner_half_h(r)
    wall = r.cover_wall
    span = _pivot_span(r)
    cy = _cover_center_y(r)
    cz = _cover_body_z(r)

    def _box(size, center):
        return cq.Workplane("XY").box(*size).translate(center)

    # Hinge sleeve laid along the pivot axis at the origin.
    sleeve = (
        cq.Workplane("XY")
        .circle(r.pivot_radius * 1.5)
        .circle(r.pivot_radius * 1.0)
        .extrude(span)
        .translate((0.0, 0.0, -0.5 * span))
    )
    if r.pivot_axis_family == "top_swivel":
        sleeve = sleeve  # axis already +z
    else:
        sleeve = sleeve.rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), -90.0)

    top_z = cz + inner_h * 0.5 + wall * 0.5
    side_y = inner_w * 0.5 + wall * 0.5
    web_w = inner_w * 0.7 + abs(cy)
    web_h = max(wall, abs(top_z) + wall)
    web = _box((0.0050, web_w, web_h), (0.0028, cy * 0.5, top_z * 0.5))
    top = _box((span_x, inner_w, wall), (span_x * 0.5, cy, top_z))
    side_a = _box((span_x, wall, inner_h), (span_x * 0.5, cy + side_y, cz))
    side_b = _box((span_x, wall, inner_h), (span_x * 0.5, cy - side_y, cz))
    front_lip = _box((wall, inner_w, inner_h), (span_x - wall * 0.5, cy, cz))
    return sleeve.union(web).union(top).union(side_a).union(side_b).union(front_lip)


def _build_single_stamped_shell_cover(ctx: ModuleBuildContext) -> ModuleBuild:
    """S6 model.py:L48-L62, L190-L203 — CadQuery single stamped shell with an
    integral rotating sleeve.

    Falls back to a u-channel box wrap if cadquery cannot import (keeps the
    cover a Mesh in the cadquery path; box fallback only on failure)."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = model.get_part(body_name)

    cover = model.part("swivel_cover")
    used_cadquery = False
    if r.pivot_axis_family != "side_flip":
        try:
            shell = _mesh_from_cadquery_for_model(
                model, _cadquery_cover_shell(r), "swivel_cover_shell", tolerance=0.00025
            )
            cover.visual(shell, material="cover_shell", name="cover_shell", material_class_id="metal.paint_coated")
            used_cadquery = True
        except Exception:
            used_cadquery = False

    if not used_cadquery:
        # Fallback: u-channel box wrap (still a real 3-face cover, not crude).
        span_x = _cover_span_x(r)
        cy = _cover_center_y(r)
        cz = _cover_body_z(r)
        inner_w = 2.0 * _cover_inner_half_w(r)
        inner_h = 2.0 * _cover_inner_half_h(r)
        wall = r.cover_wall
        plate_z = inner_h * 0.5 + wall * 0.5
        cover.visual(
            Box((span_x, inner_w, wall)),
            origin=Origin(xyz=(span_x * 0.5, cy, cz + plate_z)),
            material="cover_shell",
            name="cover_shell", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Box((span_x, wall, inner_h)),
            origin=Origin(xyz=(span_x * 0.5, cy + inner_w * 0.5 + wall * 0.5, cz)),
            material="cover_shell",
            name="cover_side_a", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Box((span_x, wall, inner_h)),
            origin=Origin(xyz=(span_x * 0.5, cy - inner_w * 0.5 - wall * 0.5, cz)),
            material="cover_shell",
            name="cover_side_b", material_class_id="metal.paint_coated",
        )
        cover.visual(
            Box((wall, inner_w + 2.0 * wall, inner_h)),
            origin=Origin(xyz=(span_x - wall * 0.5, cy, cz)),
            material="cover_shell",
            name="cover_front_lip", material_class_id="metal.paint_coated",
        )
        _emit_cover_pivot_collars(cover, r, radius_scale=1.5)
        _emit_cover_centerline_link(
            cover,
            r,
            cover_y_min=cy - inner_w * 0.5 - wall,
            cover_y_max=cy + inner_w * 0.5 + wall,
            z=cz + plate_z,
        )

    cover.inertial = Inertial.from_geometry(
        Box(
            (
                _cover_span_x(r),
                2.0 * _cover_inner_half_w(r) + 2.0 * r.cover_wall,
                2.0 * _cover_inner_half_h(r) + 2.0 * r.cover_wall,
            )
        ),
        mass=0.009,
        origin=Origin(xyz=(_cover_span_x(r) * 0.5, _cover_center_y(r), _cover_body_z(r))),
    )
    _emit_swivel_joint(model, body, cover, r)
    return ModuleBuild(
        module_name="single_stamped_shell_cover",
        parts_emitted=["swivel_cover"],
        internal_articulations=["body_to_cover"],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_flip_hood_collar_cover(ctx: ModuleBuildContext) -> ModuleBuild:
    """S7 model.py:L165-L216 — cover_top + cover_side×2 + front_bumper +
    collar×2 + wear_pad. Flip-hood with hinge collars."""
    model = ctx.model
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = model.get_part(body_name)

    cover = model.part("swivel_cover")
    span_x = _cover_span_x(r)
    cy = _cover_center_y(r)
    cz = _cover_body_z(r)
    inner_w = 2.0 * _cover_inner_half_w(r)
    inner_h = 2.0 * _cover_inner_half_h(r)
    wall = r.cover_wall
    top_z = inner_h * 0.5 + wall * 0.5
    side_y = inner_w * 0.5 + wall * 0.5

    cover.visual(
        Box((span_x, inner_w + 2.0 * wall, wall)),
        origin=Origin(xyz=(span_x * 0.5, cy, cz + top_z)),
        material="cover_shell",
        name="cover_top", material_class_id="metal.paint_coated",
    )
    cover.visual(
        Box((span_x, wall, inner_h)),
        origin=Origin(xyz=(span_x * 0.5, cy + side_y, cz)),
        material="cover_shell",
        name="cover_side_0", material_class_id="metal.paint_coated",
    )
    cover.visual(
        Box((span_x, wall, inner_h)),
        origin=Origin(xyz=(span_x * 0.5, cy - side_y, cz)),
        material="cover_shell",
        name="cover_side_1", material_class_id="metal.paint_coated",
    )
    cover.visual(
        Box((wall * 2.0, inner_w + 2.0 * wall, inner_h)),
        origin=Origin(xyz=(span_x - wall, cy, cz)),
        material="accent",
        name="cover_front_bumper", material_class_id="rubber.smooth_plain",
    )
    # Hinge collars at the pivot (coaxial with pin).
    span = _pivot_span(r)
    off = span * 0.5 - 0.0008
    if r.pivot_axis_family == "top_swivel":
        c0 = (_cover_pivot_tab_x(r), 0.0, off)
        c1 = (_cover_pivot_tab_x(r), 0.0, -off)
        _emit_top_swivel_pivot_side_web(cover, r, radius_scale=1.5)
    else:
        c0 = (_cover_pivot_tab_x(r), off, 0.0)
        c1 = (_cover_pivot_tab_x(r), -off, 0.0)
    cover.visual(
        Cylinder(radius=r.pivot_radius * 1.5, length=0.0020),
        origin=Origin(xyz=c0, rpy=_pivot_rpy(r)),
        material="satin_steel",
        name="left_pivot_tab", material_class_id="metal.stainless_matte",
    )
    cover.visual(
        Cylinder(radius=r.pivot_radius * 1.5, length=0.0020),
        origin=Origin(xyz=c1, rpy=_pivot_rpy(r)),
        material="satin_steel",
        name="right_pivot_tab", material_class_id="metal.stainless_matte",
    )
    # Wear pad inside the hood front.
    cover.visual(
        Box((span_x * 0.3, inner_w * 0.6, wall)),
        origin=Origin(xyz=(span_x * 0.75, cy, cz + top_z - wall)),
        material="accent",
        name="cover_wear_pad", material_class_id="plastic.opaque_generic",
    )
    _emit_cover_centerline_link(
        cover,
        r,
        cover_y_min=cy - side_y - wall * 0.5,
        cover_y_max=cy + side_y + wall * 0.5,
        z=cz + top_z,
    )
    cover.inertial = Inertial.from_geometry(
        Box((span_x, inner_w + 2.0 * wall, inner_h + 2.0 * wall)),
        mass=0.011,
        origin=Origin(xyz=(span_x * 0.5, cy, cz)),
    )
    _emit_swivel_joint(model, body, cover, r)
    return ModuleBuild(
        module_name="flip_hood_collar_cover",
        parts_emitted=["swivel_cover"],
        internal_articulations=["body_to_cover"],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _emit_swivel_joint(model, body, cover, r: ResolvedUsbDriveWithSwivelCoverConfig) -> None:
    """The single main DOF. Captured-pin pivot — MatingContract omitted
    (grandfathered); overlap allowances are declared in run_*_tests."""
    model.articulation(
        "body_to_cover",
        _swivel_joint_type(r),
        parent=body,
        child=cover,
        origin=Origin(xyz=_swivel_origin(r)),
        axis=_pivot_axis(r),
        motion_limits=_swivel_limits(r),
    )


# --------------------------------------------------------------------------- #
# Module factories — surface_detail (Slot F). Visuals only; no parts/joints.
# --------------------------------------------------------------------------- #


def _build_minimal_clean(ctx: ModuleBuildContext) -> ModuleBuild:
    return ModuleBuild(
        module_name="minimal_clean",
        parts_emitted=[],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_grip_and_seam_cues(ctx: ModuleBuildContext) -> ModuleBuild:
    """S4 model.py:L98-L137 — side_grip_pad×2 + service_fastener cues on the
    body (rugged rubber/bolt box visuals)."""
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = ctx.model.get_part(body_name)
    cx = _shell_center_x(r)
    grip_len = r.body_length * 0.5
    body.visual(
        Box((grip_len, 0.0030, r.body_thickness * 0.6)),
        origin=Origin(xyz=(cx, r.body_width * 0.5 + 0.0011, 0.0)),
        material="tongue_black",
        name="side_grip_pad", material_class_id="rubber.smooth_plain",
    )
    body.visual(
        Box((grip_len, 0.0030, r.body_thickness * 0.6)),
        origin=Origin(xyz=(cx, -r.body_width * 0.5 - 0.0011, 0.0)),
        material="tongue_black",
        name="side_grip_pad_opposite", material_class_id="rubber.smooth_plain",
    )
    for idx, fx in enumerate((cx - grip_len * 0.3, cx + grip_len * 0.3), start=1):
        body.visual(
            Cylinder(radius=0.00175, length=0.0009),
            origin=Origin(
                xyz=(fx, r.body_width * 0.5 + 0.0009, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)
            ),
            material="satin_steel",
            name=f"service_fastener_{idx}", material_class_id="metal.stainless_matte",
        )
    return ModuleBuild(
        module_name="grip_and_seam_cues",
        parts_emitted=[],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


def _build_datum_tick_marks(ctx: ModuleBuildContext) -> ModuleBuild:
    """S8 model.py:L108-L136 — restrained datum/gap cues on the top face.

    Keep these as shallow service markings, not raised "track" geometry across
    the whole USB body.
    """
    r: ResolvedUsbDriveWithSwivelCoverConfig = ctx.config  # type: ignore[assignment]
    body_name = ctx.upstream_interface.part_name if ctx.upstream_interface else "body"
    body = ctx.model.get_part(body_name)
    cx = _shell_center_x(r)
    line_h = 0.000055
    top_z = r.body_thickness * 0.5 + line_h * 0.15
    mark_y = -r.body_width * 0.24
    rail_len = min(0.026, r.body_length * 0.55)
    rail_x = cx - r.body_length * 0.06
    witness_xs = (cx - r.body_length * 0.24, cx + r.body_length * 0.20)
    patch_x_min = min(rail_x - rail_len * 0.5, witness_xs[0] - 0.0014)
    patch_x_max = max(rail_x + rail_len * 0.5, witness_xs[1] + 0.0014)
    body.visual(
        Box((patch_x_max - patch_x_min, r.body_width * 0.30, 0.00016)),
        origin=Origin(
            xyz=((patch_x_min + patch_x_max) * 0.5, -r.body_width * 0.29, r.body_thickness * 0.5)
        ),
        material="body_plastic",
        name="datum_recess_patch", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((rail_len, 0.00022, line_h)),
        origin=Origin(xyz=(rail_x, mark_y, top_z)),
        material="laser_etch",
        name="datum_hairline", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    for i, dx in enumerate((-0.34, -0.16, 0.04, 0.22)):
        body.visual(
            Box((0.00028, 0.0019, line_h)),
            origin=Origin(xyz=(rail_x + rail_len * dx, mark_y + 0.00055, top_z)),
            material="laser_etch",
            name=f"index_tick_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    for i, x in enumerate(witness_xs):
        body.visual(
            Box((0.0020, 0.00055, line_h)),
            origin=Origin(xyz=(x, -r.body_width * 0.36, top_z)),
            material="laser_etch",
            name=f"gap_witness_mark_{i}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    return ModuleBuild(
        module_name="datum_tick_marks",
        parts_emitted=[],
        interfaces={"downstream": ctx.upstream_interface} if ctx.upstream_interface else {},
    )


# --------------------------------------------------------------------------- #
# Factory dicts
# --------------------------------------------------------------------------- #


BODY_FACTORIES = {
    "monolithic_box_body": _build_monolithic_box_body,
    "extruded_rounded_body": _build_extruded_rounded_body,
    "multi_section_coaxial_body": _build_multi_section_coaxial_body,
    "lofted_taper_body": _build_lofted_taper_body,
    "slotted_yoke_body": _build_slotted_yoke_body,
    "cadquery_molded_body": _build_cadquery_molded_body,
}
CONNECTOR_FACTORIES = {
    "molded_plug_in_body": _build_molded_plug_in_body,
    "separate_fixed_connector_part": _build_separate_fixed_connector_part,
    "four_wall_shell_in_body": _build_four_wall_shell_in_body,
    "plate_shell_with_contacts": _build_plate_shell_with_contacts,
}
PIVOT_FACTORIES = {
    "integral_sleeve_in_body": _build_integral_sleeve_in_body,
    "body_embedded_pin_with_bosses": _build_body_embedded_pin_with_bosses,
    "separate_pivot_pin_part": _build_separate_pivot_pin_part,
    "side_lug_pin_stack": _build_side_lug_pin_stack,
}
ACCESSORY_FACTORIES = {
    "none": _build_accessory_none,
    "status_window_fixed_part": _build_status_window_fixed_part,
    "service_plate_fixed_part": _build_service_plate_fixed_part,
}
COVER_FACTORIES = {
    "u_arm_bridge_cover": _build_u_arm_bridge_cover,
    "u_channel_wrap_cover": _build_u_channel_wrap_cover,
    "dual_plate_bridge_cover": _build_dual_plate_bridge_cover,
    "single_stamped_shell_cover": _build_single_stamped_shell_cover,
    "flip_hood_collar_cover": _build_flip_hood_collar_cover,
}
DETAIL_FACTORIES = {
    "minimal_clean": _build_minimal_clean,
    "grip_and_seam_cues": _build_grip_and_seam_cues,
    "datum_tick_marks": _build_datum_tick_marks,
}


# --------------------------------------------------------------------------- #
# Slot graph + assembly
# --------------------------------------------------------------------------- #


def _slots_for_config(r: ResolvedUsbDriveWithSwivelCoverConfig) -> list[SlotSpec]:
    """Build the slot graph pinned to the chosen module per slot.

    Order matters: drive_body is the root; connector / pivot_hardware /
    accessory parent to the body; swivel_cover is the main DOF; surface_detail
    overlays last (it only adds body visuals).
    """
    return [
        SlotSpec(
            slot_name="drive_body",
            candidates={r.body_module: BODY_FACTORIES[r.body_module]},
            anchor_choice=r.body_module,
        ),
        SlotSpec(
            slot_name="connector",
            candidates={r.connector_module: CONNECTOR_FACTORIES[r.connector_module]},
            anchor_choice=r.connector_module,
        ),
        SlotSpec(
            slot_name="pivot_hardware",
            candidates={r.pivot_module: PIVOT_FACTORIES[r.pivot_module]},
            anchor_choice=r.pivot_module,
        ),
        SlotSpec(
            slot_name="body_accessory",
            candidates={r.accessory_module: ACCESSORY_FACTORIES[r.accessory_module]},
            anchor_choice=r.accessory_module,
        ),
        SlotSpec(
            slot_name="swivel_cover",
            candidates={r.cover_module: COVER_FACTORIES[r.cover_module]},
            anchor_choice=r.cover_module,
        ),
        SlotSpec(
            slot_name="surface_detail",
            candidates={r.detail_module: DETAIL_FACTORIES[r.detail_module]},
            anchor_choice=r.detail_module,
        ),
    ]


def build_usb_drive_with_swivel_cover(
    config: UsbDriveWithSwivelCoverConfig,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    """Compose the model by running each slot's chosen module factory.

    Module selection is done up front by ``config_from_seed`` and pinned by
    ``resolve_config``; the assembler runs each single-candidate slot
    deterministically (seed=0 path).
    """
    r = resolve_config(config)
    model = ArticulatedObject(name="usb_drive_with_swivel_cover", assets=assets)
    for material_name, rgba in r.palette.items():
        model.material(material_name, rgba=rgba)

    rng = random.Random(0)
    assemble(
        model,
        slots=_slots_for_config(r),
        rng=rng,
        palette=r.palette,
        config=r,
        seed=0,
        selection_mode="anchor_choices",
    )
    return model


def build_seeded_usb_drive_with_swivel_cover(seed: int) -> ArticulatedObject:
    return build_usb_drive_with_swivel_cover(config_from_seed(seed))


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    """Per-seed (slot, module) picks — consumed by the
    module_topology_diversity gate. Includes the cross-cutting axis/kind enums
    as pseudo-slots so distinct topologies (Y vs Z, revolute vs continuous)
    count toward diversity."""
    cfg = config_from_seed(seed)
    r = resolve_config(cfg)
    return [
        ("drive_body", r.body_module),
        ("connector", r.connector_module),
        ("pivot_hardware", r.pivot_module),
        ("body_accessory", r.accessory_module),
        ("swivel_cover", r.cover_module),
        ("surface_detail", r.detail_module),
        ("pivot_axis_family", r.pivot_axis_family),
        ("articulation_kind", r.articulation_kind),
    ]


# --------------------------------------------------------------------------- #
# Author-layer QC — centralizes all allow_overlap / allow_disconnected_islands
# declarations for the captured-pin swivel + sleeve-through-tab geometry.
# --------------------------------------------------------------------------- #


def _declare_pivot_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    """The swivel cover's pivot tabs/collars/sleeve are coaxial with the body
    pivot pin/sleeve/lug — that's a captured-pin pivot with intentional
    inter-part overlap. The MatingContract abstraction cannot model
    pin-through-sleeve, so we allow these overlaps explicitly. We also allow
    the cover wrapping over the body (and the molded connector) in the closed
    pose, and the separate pivot_pin / connector overlaps with the body."""
    part_names = {p.name for p in model.parts}
    body = model.get_part("body")
    body_visuals = {v.name for v in body.visuals if v.name}

    # Cover pivot region overlaps with the body pivot hardware.
    if "swivel_cover" in part_names:
        cover = model.get_part("swivel_cover")
        cover_visuals = {v.name for v in cover.visuals if v.name}
        body_pivot_elems = [
            e
            for e in (
                "pivot_sleeve",
                "pivot_pin",
                "pivot_boss_top",
                "pivot_boss_bottom",
                "hinge_saddle",
                "hinge_lug_0",
                "hinge_lug_1",
                "pivot_pin_head_0",
                "pivot_pin_head_1",
                "side_lug",
                "pivot_mount_boss",
                "pivot_mount_boss_0",
                "pivot_mount_boss_1",
                "pivot_mount_seat",
            )
            if e in body_visuals
        ]
        cover_pivot_elems = [
            e
            for e in (
                "left_pivot_tab",
                "right_pivot_tab",
                "pivot_link_spar",
                "cover_shell",
                "left_arm",
                "right_arm",
            )
            if e in cover_visuals
        ]
        # Allow the cover <-> body pair broadly (captured pivot + closed-pose
        # wrap of the body / connector).
        ctx.allow_overlap(
            body,
            cover,
            reason=(
                "captured swivel pivot: cover pivot tabs/collars/sleeve are coaxial "
                "with the body pivot pin/sleeve/lug, and the closed cover wraps the "
                "body and connector"
            ),
        )
        for be in body_pivot_elems:
            for ce in cover_pivot_elems:
                ctx.allow_overlap(
                    body,
                    cover,
                    elem_a=be,
                    elem_b=ce,
                    reason="captured swivel pivot pin-through-sleeve overlap",
                )

    # Separate pivot_pin part passes through the body boss (captured pin).
    if "pivot_pin" in part_names:
        pin = model.get_part("pivot_pin")
        ctx.allow_overlap(
            body,
            pin,
            reason="separate pivot pin is captured through the body pivot boss",
        )
        if "swivel_cover" in part_names:
            cover = model.get_part("swivel_cover")
            ctx.allow_overlap(
                pin,
                cover,
                reason="captured swivel pivot: the pin passes through the cover collars",
            )

    # Separate connector part seats into the body front (FIXED, faces touch
    # but the rear insert pushes slightly into the body).
    if "connector" in part_names:
        connector = model.get_part("connector")
        ctx.allow_overlap(
            body,
            connector,
            reason="separate connector rear insert seats into the body front face",
        )
        if "swivel_cover" in part_names:
            cover = model.get_part("swivel_cover")
            ctx.allow_overlap(
                connector,
                cover,
                reason="closed swivel cover wraps over the exposed connector",
            )


def _expect_one_main_dof(ctx: TestContext, model: ArticulatedObject) -> None:
    """Exactly one non-fixed joint (body_to_cover) — the main swivel DOF."""
    non_fixed = [a for a in model.articulations if a.articulation_type != ArticulationType.FIXED]
    ctx.check(
        "exactly_one_main_swivel_dof",
        len(non_fixed) == 1 and non_fixed[0].name == "body_to_cover",
        f"Expected one non-fixed joint named body_to_cover, got {[a.name for a in non_fixed]}",
    )


def _expect_swivel_axis(ctx: TestContext, model: ArticulatedObject) -> None:
    """The swivel axis must be ±Y or ±Z, never X."""
    try:
        swivel = model.get_articulation("body_to_cover")
    except Exception:
        return
    ax = tuple(round(v, 6) for v in swivel.axis)
    ok = abs(ax[0]) < 1e-6 and (abs(ax[1]) > 1e-6 or abs(ax[2]) > 1e-6)
    ctx.check(
        "swivel_axis_is_y_or_z",
        ok,
        f"Swivel axis must be ±Y or ±Z (no X component); got {swivel.axis}",
    )


def _aabb_union(aabbs):
    mins = tuple(min(aabb[0][axis] for aabb in aabbs) for axis in range(3))
    maxs = tuple(max(aabb[1][axis] for aabb in aabbs) for axis in range(3))
    return mins, maxs


def _connector_world_aabb(ctx: TestContext, model: ArticulatedObject):
    part_names = {p.name for p in model.parts}
    if "connector" in part_names:
        return ctx.part_world_aabb(model.get_part("connector"))

    body = model.get_part("body")
    connector_visuals = (
        "usb_plug",
        "connector_top_wall",
        "connector_bottom_wall",
        "connector_side_wall_0",
        "connector_side_wall_1",
        "connector_tongue",
        "contact_pad_0",
        "contact_pad_1",
    )
    aabbs = [
        aabb
        for name in connector_visuals
        if (aabb := ctx.part_element_world_aabb(body, elem=name)) is not None
    ]
    if not aabbs:
        return None
    return _aabb_union(aabbs)


def _expect_connector_protrudes(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedUsbDriveWithSwivelCoverConfig
) -> None:
    """The USB-A connector should project clearly beyond the body front."""
    c_aabb = _connector_world_aabb(ctx, model)
    if c_aabb is None:
        ctx.fail("connector_protrudes_from_front", "missing connector geometry")
        return
    body_front = _body_front_x(r)
    protrusion = c_aabb[1][0] - body_front
    ctx.check(
        "connector_protrudes_from_front",
        protrusion >= 0.0080,
        f"connector protrusion={protrusion:.4f}; connector front x={c_aabb[1][0]:.4f} body front x={body_front:.4f}",
    )


def _expect_side_flip_opens_upward(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedUsbDriveWithSwivelCoverConfig
) -> None:
    if r.pivot_axis_family != "side_flip":
        return
    swivel = model.get_articulation("body_to_cover")
    cover = model.get_part("swivel_cover")
    with ctx.pose({swivel: 0.0}):
        closed_aabb = ctx.part_world_aabb(cover)
    open_angle = min(
        math.pi / 2.0, r.swivel_upper if r.articulation_kind == "revolute" else math.pi / 2.0
    )
    with ctx.pose({swivel: open_angle}):
        open_aabb = ctx.part_world_aabb(cover)
    if closed_aabb is None or open_aabb is None:
        return
    lift = open_aabb[1][2] - closed_aabb[1][2]
    open_min_clearance = open_aabb[0][2] - r.body_thickness * 0.5
    ctx.check(
        "side_flip_cover_opens_toward_covered_face",
        lift > 0.006,
        f"side-flip cover should lift away from body; open max-z lift={lift:.4f}",
    )
    ctx.check(
        "side_flip_cover_clears_body_when_open",
        open_min_clearance > -0.0020,
        f"open side-flip cover should clear the body top; min-z clearance={open_min_clearance:.4f}",
    )


def _expect_side_flip_pivot_tabs_outside_body_side(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedUsbDriveWithSwivelCoverConfig
) -> None:
    if r.pivot_axis_family != "side_flip":
        return
    cover = model.get_part("swivel_cover")
    left = ctx.part_element_world_aabb(cover, elem="left_pivot_tab")
    right = ctx.part_element_world_aabb(cover, elem="right_pivot_tab")
    if left is None or right is None:
        return
    side_clearance = max(0.0013, r.cover_clearance + r.cover_wall * 0.35)
    left_gap = left[0][1] - r.body_width * 0.5
    right_gap = -r.body_width * 0.5 - right[1][1]
    ctx.check(
        "side_flip_pivot_tabs_clear_body_sides",
        left_gap >= side_clearance and right_gap >= side_clearance,
        f"pivot tabs should sit outside body side walls; left_gap={left_gap:.4f} right_gap={right_gap:.4f} required={side_clearance:.4f}",
    )


def run_usb_drive_with_swivel_cover_tests(
    model: ArticulatedObject,
    config: UsbDriveWithSwivelCoverConfig,
) -> TestReport:
    """Author-layer QC for the modular usb_drive_with_swivel_cover template.

    The compiler-owned baseline runs the full strict QC stack. This function
    declares the captured-pin / wrap overlaps and adds identity assertions
    (one main DOF, axis is Y/Z, connector protrudes), then runs the baseline
    checks itself for the standalone path.
    """
    r = resolve_config(config)
    ctx = TestContext(model)

    _declare_pivot_overlaps(ctx, model)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)
    ctx.fail_if_joint_mating_has_gap()

    _expect_one_main_dof(ctx, model)
    _expect_swivel_axis(ctx, model)
    _expect_connector_protrudes(ctx, model, r)
    _expect_side_flip_opens_upward(ctx, model, r)
    _expect_side_flip_pivot_tabs_outside_body_side(ctx, model, r)

    return ctx.report()


__all__ = [
    "AccessoryModule",
    "ArticulationKind",
    "BodyModule",
    "ConnectorModule",
    "CoverModule",
    "DetailModule",
    "PivotAxisFamily",
    "PivotModule",
    "ResolvedUsbDriveWithSwivelCoverConfig",
    "UsbDriveWithSwivelCoverConfig",
    "UsbPaletteTheme",
    "build_seeded_usb_drive_with_swivel_cover",
    "build_usb_drive_with_swivel_cover",
    "config_from_seed",
    "resolve_config",
    "run_usb_drive_with_swivel_cover_tests",
    "slot_choices_for_seed",
]
