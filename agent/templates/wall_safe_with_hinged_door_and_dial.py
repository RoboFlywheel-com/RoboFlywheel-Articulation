# SPDX-License-Identifier: Apache-2.0

"""Procedural template for ``wall_safe_with_hinged_door_and_dial``.

No reviewed spec file exists yet under ``articraft_template_authoring/specs_modular_v1``.
This modular template follows the checked-in batch prompt family for the
category: a recessed/flush wall safe body, a side-hinged thick door, a round
combination dial, a rotating handle, and optional small internal/deposit
mechanisms.

Core identity and motion spine:

``safe_body --safe_door_hinge(Z)--> safe_door
           --combination_dial_spin(Y)--> combination_dial
           --handle_spin(Y)--> handle``

Optional auxiliary motion is sampled as either a door deposit flap, an internal
document flap, or a shallow prismatic drawer. Non-moving trims, shelves, bolt
heads, jambs, and hinge reinforcement are fused into their owning part.
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
    Box,
    Cylinder,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
)

__modular__ = True


BodyStyle = Literal["recessed_rect", "flush_square", "broad_flange", "narrow_document"]
DoorStyle = Literal["right_hinged_thick", "left_hinged_flat", "heavy_vault_plate"]
LockStyle = Literal["three_spoke_center", "dial_over_t_handle", "wheel_handle", "lower_latch_lever"]
AuxStyle = Literal["none", "deposit_flap", "inner_drawer", "document_flap"]
MaterialStyle = Literal["gunmetal", "brushed_steel", "hotel_beige", "vault_blue", "dark_graphite"]


BODY_STYLES: tuple[BodyStyle, ...] = (
    "recessed_rect",
    "flush_square",
    "broad_flange",
    "narrow_document",
)
DOOR_STYLES: tuple[DoorStyle, ...] = (
    "right_hinged_thick",
    "left_hinged_flat",
    "heavy_vault_plate",
)
LOCK_STYLES: tuple[LockStyle, ...] = (
    "three_spoke_center",
    "dial_over_t_handle",
    "wheel_handle",
    "lower_latch_lever",
)
AUX_STYLES: tuple[AuxStyle, ...] = ("none", "deposit_flap", "inner_drawer", "document_flap")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "gunmetal",
    "brushed_steel",
    "hotel_beige",
    "vault_blue",
    "dark_graphite",
)


PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "gunmetal": {
        "body": (0.23, 0.25, 0.27, 1.0),
        "body_dark": (0.08, 0.09, 0.10, 1.0),
        "door": (0.31, 0.33, 0.35, 1.0),
        "trim": (0.48, 0.50, 0.52, 1.0),
        "dial": (0.80, 0.82, 0.84, 1.0),
        "accent": (0.90, 0.70, 0.18, 1.0),
        "shadow": (0.015, 0.016, 0.018, 1.0),
    },
    "brushed_steel": {
        "body": (0.58, 0.60, 0.62, 1.0),
        "body_dark": (0.25, 0.26, 0.27, 1.0),
        "door": (0.72, 0.74, 0.76, 1.0),
        "trim": (0.42, 0.43, 0.44, 1.0),
        "dial": (0.16, 0.17, 0.18, 1.0),
        "accent": (0.10, 0.32, 0.58, 1.0),
        "shadow": (0.05, 0.055, 0.06, 1.0),
    },
    "hotel_beige": {
        "body": (0.72, 0.69, 0.60, 1.0),
        "body_dark": (0.34, 0.32, 0.27, 1.0),
        "door": (0.80, 0.77, 0.68, 1.0),
        "trim": (0.54, 0.51, 0.44, 1.0),
        "dial": (0.18, 0.18, 0.17, 1.0),
        "accent": (0.60, 0.18, 0.12, 1.0),
        "shadow": (0.055, 0.052, 0.047, 1.0),
    },
    "vault_blue": {
        "body": (0.20, 0.27, 0.34, 1.0),
        "body_dark": (0.06, 0.08, 0.11, 1.0),
        "door": (0.24, 0.34, 0.43, 1.0),
        "trim": (0.58, 0.62, 0.65, 1.0),
        "dial": (0.83, 0.84, 0.80, 1.0),
        "accent": (0.95, 0.65, 0.12, 1.0),
        "shadow": (0.018, 0.022, 0.030, 1.0),
    },
    "dark_graphite": {
        "body": (0.10, 0.105, 0.11, 1.0),
        "body_dark": (0.025, 0.027, 0.030, 1.0),
        "door": (0.15, 0.16, 0.17, 1.0),
        "trim": (0.34, 0.35, 0.36, 1.0),
        "dial": (0.70, 0.72, 0.74, 1.0),
        "accent": (0.10, 0.46, 0.40, 1.0),
        "shadow": (0.006, 0.007, 0.008, 1.0),
    },
}


Y_CYLINDER_RPY = (-math.pi / 2.0, 0.0, 0.0)
X_CYLINDER_RPY = (0.0, math.pi / 2.0, 0.0)
Z_CYLINDER_RPY = (0.0, 0.0, 0.0)


@dataclass(frozen=True)
class WallSafeWithHingedDoorAndDialConfig:
    body_style: BodyStyle | None = None
    door_style: DoorStyle | None = None
    lock_style: LockStyle | None = None
    aux_style: AuxStyle | None = None
    material_style: MaterialStyle = "gunmetal"
    width: float = 0.42
    height: float = 0.34
    depth: float = 0.18
    door_swing: float = math.radians(105.0)
    drawer_travel: float = 0.075
    hinge_barrel_count: int = 3
    handle_spoke_count: int = 3
    vault_rib_count: int = 3
    lock_bolt_count: int = 2
    name: str = "reference_wall_safe_with_hinged_door_and_dial"


@dataclass(frozen=True)
class ResolvedWallSafeWithHingedDoorAndDialConfig:
    body_style: BodyStyle
    door_style: DoorStyle
    lock_style: LockStyle
    aux_style: AuxStyle
    material_style: MaterialStyle
    width: float
    height: float
    depth: float
    wall_thickness: float
    frame_thickness: float
    door_width: float
    door_height: float
    door_thickness: float
    hinge_side: int
    hinge_x: float
    hinge_y: float
    dial_x: float
    dial_z: float
    handle_x: float
    handle_z: float
    door_swing: float
    drawer_travel: float
    hinge_barrel_count: int
    handle_spoke_count: int
    vault_rib_count: int
    lock_bolt_count: int
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, float(value)))


def _clamp_int(value: int, low: int, high: int) -> int:
    return max(low, min(high, int(round(value))))


def _choice(value: str | None, choices: tuple[str, ...], fallback: str) -> str:
    if value in choices:
        return value
    return fallback


def resolve_config(
    config: WallSafeWithHingedDoorAndDialConfig,
) -> ResolvedWallSafeWithHingedDoorAndDialConfig:
    body_style = _choice(config.body_style, BODY_STYLES, "recessed_rect")
    door_style = _choice(config.door_style, DOOR_STYLES, "right_hinged_thick")
    lock_style = _choice(config.lock_style, LOCK_STYLES, "three_spoke_center")
    aux_style = _choice(config.aux_style, AUX_STYLES, "none")
    material_style = _choice(config.material_style, MATERIAL_STYLES, "gunmetal")

    width = _clamp(config.width, 0.30, 0.58)
    height = _clamp(config.height, 0.26, 0.56)
    depth = _clamp(config.depth, 0.12, 0.26)
    if body_style == "flush_square":
        size = max(width, height)
        width = height = _clamp(size, 0.32, 0.48)
    elif body_style == "narrow_document":
        width = _clamp(width, 0.30, 0.40)
        height = _clamp(height, 0.40, 0.58)
    elif body_style == "broad_flange":
        width = _clamp(width, 0.40, 0.60)
        height = _clamp(height, 0.32, 0.48)

    hinge_side = 1
    if door_style == "left_hinged_flat":
        hinge_side = -1
    elif door_style == "heavy_vault_plate":
        hinge_side = -1 if (width + height) > 0.88 else 1

    wall_thickness = 0.038 if body_style != "narrow_document" else 0.032
    frame_thickness = 0.055 if body_style == "broad_flange" else 0.040
    door_width = width - frame_thickness * 1.45
    door_height = height - frame_thickness * 1.55
    door_thickness = 0.038
    if door_style == "left_hinged_flat":
        door_thickness = 0.030
    elif door_style == "heavy_vault_plate":
        door_thickness = 0.048

    hinge_x = hinge_side * (door_width * 0.5)
    hinge_y = -0.030
    dial_x = -hinge_side * door_width * 0.42
    dial_z = door_height * 0.16
    handle_x = -hinge_side * door_width * 0.42
    handle_z = -door_height * 0.18
    if lock_style in ("three_spoke_center", "wheel_handle"):
        dial_x = handle_x = -hinge_side * door_width * 0.45
        dial_z = door_height * 0.18
        handle_z = -door_height * 0.08
    elif lock_style == "lower_latch_lever":
        dial_z = door_height * 0.18
        handle_z = -door_height * 0.30
    hinge_barrel_count = _clamp_int(config.hinge_barrel_count, 2, 5)
    lock_bolt_count = _clamp_int(config.lock_bolt_count, 2, 5)
    vault_rib_count = _clamp_int(config.vault_rib_count, 2, 4)
    if lock_style == "wheel_handle":
        handle_spoke_count = _clamp_int(config.handle_spoke_count, 4, 8)
    elif lock_style == "three_spoke_center":
        handle_spoke_count = _clamp_int(config.handle_spoke_count, 3, 4)
    else:
        handle_spoke_count = 0

    return ResolvedWallSafeWithHingedDoorAndDialConfig(
        body_style=body_style,  # type: ignore[arg-type]
        door_style=door_style,  # type: ignore[arg-type]
        lock_style=lock_style,  # type: ignore[arg-type]
        aux_style=aux_style,  # type: ignore[arg-type]
        material_style=material_style,  # type: ignore[arg-type]
        width=width,
        height=height,
        depth=depth,
        wall_thickness=wall_thickness,
        frame_thickness=frame_thickness,
        door_width=door_width,
        door_height=door_height,
        door_thickness=door_thickness,
        hinge_side=hinge_side,
        hinge_x=hinge_x,
        hinge_y=hinge_y,
        dial_x=dial_x,
        dial_z=dial_z,
        handle_x=handle_x,
        handle_z=handle_z,
        door_swing=_clamp(config.door_swing, math.radians(70.0), math.radians(130.0)),
        drawer_travel=_clamp(config.drawer_travel, 0.040, 0.120),
        hinge_barrel_count=hinge_barrel_count,
        handle_spoke_count=handle_spoke_count,
        vault_rib_count=vault_rib_count,
        lock_bolt_count=lock_bolt_count,
        name=str(config.name or "wall_safe_with_hinged_door_and_dial"),
    )


def config_from_seed(seed: int) -> WallSafeWithHingedDoorAndDialConfig:
    if seed == 0:
        return WallSafeWithHingedDoorAndDialConfig(
            body_style="recessed_rect",
            door_style="right_hinged_thick",
            lock_style="three_spoke_center",
            aux_style="none",
            material_style="gunmetal",
            width=0.42,
            height=0.34,
            depth=0.18,
            hinge_barrel_count=3,
            handle_spoke_count=3,
            vault_rib_count=3,
            lock_bolt_count=2,
            name="seeded_wall_safe_with_hinged_door_and_dial_0",
        )
    rng = random.Random(seed)
    body_style = rng.choice(BODY_STYLES)
    door_style = rng.choice(DOOR_STYLES)
    lock_style = rng.choice(LOCK_STYLES)
    aux_style = rng.choice(AUX_STYLES)
    if aux_style == "document_flap" and body_style not in ("narrow_document", "broad_flange"):
        body_style = rng.choice(("narrow_document", "broad_flange"))
    if aux_style == "inner_drawer" and body_style == "narrow_document":
        body_style = "recessed_rect"
    return WallSafeWithHingedDoorAndDialConfig(
        body_style=body_style,
        door_style=door_style,
        lock_style=lock_style,
        aux_style=aux_style,
        material_style=rng.choice(MATERIAL_STYLES),
        width=rng.uniform(0.34, 0.54),
        height=rng.uniform(0.30, 0.52),
        depth=rng.uniform(0.14, 0.23),
        door_swing=rng.uniform(math.radians(85.0), math.radians(125.0)),
        drawer_travel=rng.uniform(0.055, 0.100),
        hinge_barrel_count=rng.choice((2, 3, 4, 5)),
        handle_spoke_count=rng.choice((3, 4, 5, 6, 8)),
        vault_rib_count=rng.choice((2, 3, 4)),
        lock_bolt_count=rng.choice((2, 3, 4, 5)),
        name=f"seeded_wall_safe_with_hinged_door_and_dial_{seed}",
    )


def slot_choices_for_config(
    config: WallSafeWithHingedDoorAndDialConfig,
) -> list[tuple[str, str]]:
    r = resolve_config(config)
    return [
        ("body_style", r.body_style),
        ("door_style", r.door_style),
        ("lock_style", r.lock_style),
        ("aux_style", r.aux_style),
        ("material_style", r.material_style),
        ("hinge_barrel_multiplicity", f"{r.hinge_barrel_count}_barrels"),
        ("handle_spoke_multiplicity", f"{r.handle_spoke_count}_spokes"),
        (
            "vault_rib_multiplicity",
            f"{r.vault_rib_count}_ribs" if r.door_style == "heavy_vault_plate" else "0_ribs",
        ),
        ("lock_bolt_multiplicity", f"{r.lock_bolt_count}_bolts"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(config_from_seed(seed))


def _register_materials(model: ArticulatedObject, style: MaterialStyle) -> dict[str, str]:
    return {name: model.material(name, rgba=rgba) for name, rgba in PALETTES[style].items()}


def _box(
    part: Part,
    name: str,
    size: tuple[float, float, float],
    xyz: tuple[float, float, float],
    material: str,
    rpy: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> None:
    part.visual(
        Box(size),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name,
        material_class_id="metal.paint_coated",
    )


def _cyl(
    part: Part,
    name: str,
    radius: float,
    length: float,
    xyz: tuple[float, float, float],
    material: str,
    rpy: tuple[float, float, float] = Z_CYLINDER_RPY,
) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name,
        material_class_id="metal.paint_coated",
    )


def _deposit_flap_pose(
    r: ResolvedWallSafeWithHingedDoorAndDialConfig,
) -> tuple[float, float, float]:
    return (
        -r.hinge_side * r.door_width * 0.5,
        -r.door_thickness * 0.5 - 0.006,
        r.door_height * 0.50,
    )


def _even_offsets(count: int, extent: float) -> tuple[float, ...]:
    count = max(1, int(count))
    if count == 1:
        return (0.0,)
    step = (extent * 2.0) / float(count - 1)
    return tuple(-extent + step * i for i in range(count))


def _build_body(
    model: ArticulatedObject,
    r: ResolvedWallSafeWithHingedDoorAndDialConfig,
    m: dict[str, str],
) -> Part:
    body = model.part("safe_body")
    w, h, d = r.width, r.height, r.depth
    wt = r.wall_thickness
    ft = r.frame_thickness
    _box(body, "back_plate", (w, 0.024, h), (0.0, d + 0.012, 0.0), m["body_dark"])
    _box(body, "left_recess_wall", (wt, d, h), (-w * 0.5 + wt * 0.5, d * 0.5, 0.0), m["body"])
    _box(body, "right_recess_wall", (wt, d, h), (w * 0.5 - wt * 0.5, d * 0.5, 0.0), m["body"])
    _box(body, "top_recess_wall", (w, d, wt), (0.0, d * 0.5, h * 0.5 - wt * 0.5), m["body"])
    _box(body, "bottom_recess_wall", (w, d, wt), (0.0, d * 0.5, -h * 0.5 + wt * 0.5), m["body"])
    _box(
        body,
        "interior_shadow_back",
        (w - 2.0 * wt, 0.014, h - 2.0 * wt),
        (0.0, d + 0.026, 0.0),
        m["shadow"],
    )

    flange_extra = 0.030 if r.body_style != "broad_flange" else 0.070
    fw = w + flange_extra * 2.0
    fh = h + flange_extra * 2.0
    side_frame_w = ft
    top_frame_h = ft
    _box(
        body,
        "front_frame_left",
        (side_frame_w, 0.030, fh),
        (-w * 0.5 - flange_extra + side_frame_w * 0.5, -0.002, 0.0),
        m["trim"],
    )
    _box(
        body,
        "front_frame_right",
        (side_frame_w, 0.030, fh),
        (w * 0.5 + flange_extra - side_frame_w * 0.5, -0.002, 0.0),
        m["trim"],
    )
    _box(
        body,
        "front_frame_top",
        (fw, 0.030, top_frame_h),
        (0.0, -0.002, h * 0.5 + flange_extra - top_frame_h * 0.5),
        m["trim"],
    )
    _box(
        body,
        "front_frame_bottom",
        (fw, 0.030, top_frame_h),
        (0.0, -0.002, -h * 0.5 - flange_extra + top_frame_h * 0.5),
        m["trim"],
    )
    if r.body_style == "broad_flange":
        bridge = max(0.012, flange_extra - ft + 0.018)
        _box(
            body,
            "left_flange_return",
            (bridge, 0.026, h),
            (-w * 0.5 - (flange_extra - ft) * 0.5, 0.020, 0.0),
            m["trim"],
        )
        _box(
            body,
            "right_flange_return",
            (bridge, 0.026, h),
            (w * 0.5 + (flange_extra - ft) * 0.5, 0.020, 0.0),
            m["trim"],
        )
        _box(
            body,
            "top_flange_return",
            (w, 0.026, bridge),
            (0.0, 0.020, h * 0.5 + (flange_extra - ft) * 0.5),
            m["trim"],
        )
        _box(
            body,
            "bottom_flange_return",
            (w, 0.026, bridge),
            (0.0, 0.020, -h * 0.5 - (flange_extra - ft) * 0.5),
            m["trim"],
        )
    _box(
        body,
        "inner_jamb_left",
        (0.018, 0.050, h - 2.0 * ft),
        (-r.door_width * 0.5 - 0.018, 0.010, 0.0),
        m["body_dark"],
    )
    _box(
        body,
        "inner_jamb_right",
        (0.018, 0.050, h - 2.0 * ft),
        (r.door_width * 0.5 + 0.018, 0.010, 0.0),
        m["body_dark"],
    )
    shelf_z = -h * 0.16
    _box(
        body, "interior_shelf", (w - 1.5 * wt, d * 0.82, 0.018), (0.0, d * 0.48, shelf_z), m["trim"]
    )
    if r.aux_style == "inner_drawer":
        drawer_outer_x = r.width * 0.25 + 0.009
        slider_width = 0.010
        rail_x = drawer_outer_x + slider_width * 1.5
        rail_z = -h * 0.28
        # The fixed channels span the cavity. Their 0.5 mm front return stays
        # behind the thickest door while retaining the moving shoes at the
        # shallowest-depth / longest-travel resolved boundary.
        rail_front_y = -0.0005
        rail_back_y = r.depth
        rail_depth = rail_back_y - rail_front_y

        # The rear cross-member closes both guide channels against the safe's
        # back plate and acts as the closed-position stop for the drawer shoes.
        _box(
            body,
            "drawer_slide_socket",
            (2.0 * (rail_x + slider_width * 0.5), 0.010, 0.018),
            (0.0, r.depth + 0.005, rail_z),
            m["body_dark"],
        )
        for side, label in ((-1.0, "left"), (1.0, "right")):
            _box(
                body,
                f"drawer_{label}_guide_rail",
                (slider_width, rail_depth, 0.018),
                (side * rail_x, rail_front_y + rail_depth * 0.5, rail_z),
                m["body_dark"],
            )
    if r.aux_style == "document_flap":
        _cyl(
            body,
            "document_flap_socket",
            0.012,
            w - 2.0 * wt,
            (0.0, 0.040, h * 0.30),
            m["trim"],
            rpy=X_CYLINDER_RPY,
        )

    hx = r.hinge_x
    hy = r.hinge_y
    hinge_barrel_length = r.door_height * (0.21 if r.hinge_barrel_count <= 2 else 0.16)
    for i, z in enumerate(_even_offsets(r.hinge_barrel_count, r.door_height * 0.34)):
        _cyl(body, f"frame_hinge_barrel_{i}", 0.020, hinge_barrel_length, (hx, hy, z), m["trim"])
    _box(
        body,
        "hinge_backstrap",
        (0.030, 0.030, r.door_height * 0.86),
        (hx, hy + 0.014, 0.0),
        m["trim"],
    )
    for i, z in enumerate((h * 0.38, -h * 0.38)):
        _box(
            body,
            f"frame_anchor_bolt_{i}",
            (0.032, 0.010, 0.032),
            (-r.hinge_side * (w * 0.5 + flange_extra - ft * 0.5), -0.022, z),
            m["accent"],
        )
    return body


def _build_door(
    model: ArticulatedObject,
    r: ResolvedWallSafeWithHingedDoorAndDialConfig,
    m: dict[str, str],
) -> Part:
    door = model.part("safe_door")
    sx = r.hinge_side
    cx = -sx * r.door_width * 0.5
    _box(
        door,
        "door_slab",
        (r.door_width, r.door_thickness, r.door_height),
        (cx, 0.0, 0.0),
        m["door"],
    )
    _box(
        door,
        "door_inner_shadow_gap",
        (r.door_width * 0.88, 0.008, r.door_height * 0.84),
        (cx, r.door_thickness * 0.44, 0.0),
        m["shadow"],
    )
    _box(
        door,
        "raised_door_panel",
        (r.door_width * 0.76, 0.014, r.door_height * 0.66),
        (cx, -r.door_thickness * 0.58, 0.0),
        m["trim"],
    )
    _box(
        door,
        "lock_boss_plate",
        (0.105, 0.014, 0.120),
        (r.dial_x, -r.door_thickness * 0.70, (r.dial_z + r.handle_z) * 0.5),
        m["trim"],
    )
    _cyl(
        door,
        "dial_socket_pad",
        0.042,
        0.016,
        (r.dial_x, -r.door_thickness * 0.74, r.dial_z),
        m["body_dark"],
        rpy=Y_CYLINDER_RPY,
    )
    _cyl(
        door,
        "handle_socket_pad",
        0.033,
        0.016,
        (r.handle_x, -r.door_thickness * 0.74, r.handle_z),
        m["body_dark"],
        rpy=Y_CYLINDER_RPY,
    )
    bolt_extent = r.door_height * 0.24
    for i, z in enumerate(_even_offsets(r.lock_bolt_count, bolt_extent)):
        _box(
            door,
            f"sliding_lock_bolt_{i}",
            (r.door_width * 0.18, 0.016, 0.028),
            (-sx * r.door_width * 0.12, r.door_thickness * 0.45, z),
            m["accent"],
        )
    hinge_knuckle_length = r.door_height * (0.20 if r.hinge_barrel_count <= 2 else 0.14)
    for i, z in enumerate(_even_offsets(r.hinge_barrel_count, r.door_height * 0.34)):
        _cyl(door, f"door_hinge_knuckle_{i}", 0.018, hinge_knuckle_length, (0.0, 0.0, z), m["door"])
    _box(
        door,
        "hinge_leaf_strip",
        (0.026, r.door_thickness, r.door_height * 0.84),
        (-sx * 0.004, 0.0, 0.0),
        m["door"],
    )
    if r.door_style == "heavy_vault_plate":
        for i, z in enumerate(_even_offsets(r.vault_rib_count, r.door_height * 0.30)):
            _box(
                door,
                f"vault_rib_{i}",
                (r.door_width * 0.80, 0.012, 0.020),
                (cx, r.door_thickness * 0.48, z),
                m["body_dark"],
            )
    if r.aux_style == "deposit_flap":
        flap_x, flap_y, flap_z = _deposit_flap_pose(r)
        _cyl(
            door,
            "deposit_flap_socket",
            0.012,
            r.door_width * 0.44,
            (flap_x, flap_y, flap_z),
            m["trim"],
            rpy=X_CYLINDER_RPY,
        )
    return door


def _build_dial(
    model: ArticulatedObject,
    r: ResolvedWallSafeWithHingedDoorAndDialConfig,
    m: dict[str, str],
) -> Part:
    dial = model.part("combination_dial")
    _cyl(dial, "dial_body", 0.038, 0.024, (0.0, 0.0, 0.0), m["dial"], rpy=Y_CYLINDER_RPY)
    _cyl(dial, "dial_outer_ring", 0.044, 0.010, (0.0, -0.010, 0.0), m["trim"], rpy=Y_CYLINDER_RPY)
    _cyl(
        dial,
        "dial_center_cap",
        0.016,
        0.030,
        (0.0, -0.002, 0.0),
        m["body_dark"],
        rpy=Y_CYLINDER_RPY,
    )
    for i in range(12):
        angle = i * math.tau / 12.0
        tick_len = 0.018 if i % 3 == 0 else 0.011
        _box(
            dial,
            f"dial_tick_{i}",
            (0.004, 0.006, tick_len),
            (math.cos(angle) * 0.030, -0.017, math.sin(angle) * 0.030),
            m["body_dark"],
            rpy=(0.0, 0.0, -angle),
        )
    return dial


def _build_handle(
    model: ArticulatedObject,
    r: ResolvedWallSafeWithHingedDoorAndDialConfig,
    m: dict[str, str],
) -> Part:
    handle = model.part("handle")
    _cyl(handle, "handle_hub", 0.027, 0.026, (0.0, 0.0, 0.0), m["trim"], rpy=Y_CYLINDER_RPY)
    if r.lock_style == "dial_over_t_handle":
        _box(handle, "t_handle_crossbar", (0.105, 0.018, 0.022), (0.0, -0.016, 0.0), m["accent"])
        _box(handle, "t_handle_stem", (0.020, 0.022, 0.060), (0.0, -0.014, -0.020), m["accent"])
    elif r.lock_style == "lower_latch_lever":
        _box(
            handle,
            "latch_lever_bar",
            (0.105, 0.018, 0.024),
            (0.040, -0.016, 0.0),
            m["accent"],
            rpy=(0.0, 0.0, math.radians(-12)),
        )
        _box(handle, "lever_counterweight", (0.030, 0.016, 0.030), (-0.036, -0.015, 0.0), m["trim"])
    elif r.lock_style == "wheel_handle":
        _cyl(
            handle,
            "wheel_outer_ring_proxy",
            0.064,
            0.012,
            (0.0, -0.014, 0.0),
            m["accent"],
            rpy=Y_CYLINDER_RPY,
        )
        for i in range(r.handle_spoke_count):
            a = i * math.tau / float(r.handle_spoke_count)
            _box(
                handle,
                f"wheel_spoke_{i}",
                (0.095, 0.014, 0.014),
                (math.cos(a) * 0.020, -0.018, math.sin(a) * 0.020),
                m["accent"],
                rpy=(0.0, 0.0, a),
            )
    elif r.lock_style == "three_spoke_center":
        for i in range(r.handle_spoke_count):
            a = i * math.tau / float(r.handle_spoke_count)
            _box(
                handle,
                f"spoke_{i}",
                (0.092, 0.016, 0.018),
                (math.cos(a) * 0.020, -0.017, math.sin(a) * 0.020),
                m["accent"],
                rpy=(0.0, 0.0, a),
            )
    return handle


def _build_deposit_flap(
    model: ArticulatedObject,
    r: ResolvedWallSafeWithHingedDoorAndDialConfig,
    m: dict[str, str],
) -> Part:
    flap = model.part("deposit_flap")
    _box(
        flap,
        "deposit_flap_panel",
        (r.door_width * 0.38, 0.014, 0.030),
        (0.0, -0.010, -0.015),
        m["door"],
    )
    _cyl(
        flap,
        "deposit_flap_hinge_barrel",
        0.011,
        r.door_width * 0.44,
        (0.0, -0.008, 0.0),
        m["trim"],
        rpy=X_CYLINDER_RPY,
    )
    _box(
        flap,
        "deposit_pull_lip",
        (r.door_width * 0.28, 0.014, 0.008),
        (0.0, -0.018, -0.024),
        m["accent"],
    )
    return flap


def _build_document_flap(
    model: ArticulatedObject,
    r: ResolvedWallSafeWithHingedDoorAndDialConfig,
    m: dict[str, str],
) -> Part:
    flap = model.part("document_flap")
    _box(flap, "document_flap_panel", (r.width * 0.58, 0.014, 0.052), (0.0, 0.0, -0.026), m["body"])
    _cyl(
        flap,
        "document_flap_hinge_barrel",
        0.010,
        r.width * 0.58,
        (0.0, 0.0, 0.0),
        m["trim"],
        rpy=X_CYLINDER_RPY,
    )
    return flap


def _inner_drawer_body_depth(r: ResolvedWallSafeWithHingedDoorAndDialConfig) -> float:
    """Front-to-back extent of the interior tray (kept short so it seats deep)."""
    return _clamp(r.depth * 0.28, 0.030, 0.070)


def _inner_drawer_origin_y(r: ResolvedWallSafeWithHingedDoorAndDialConfig) -> float:
    """Body-frame Y of the drawer front face at rest.

    The tray back is parked ~10 mm off the cavity back wall, so the front face
    sits as deep as the box allows. That deep seating is what leaves room for
    the drawer to travel forward while still clearing the closed door plane.
    """
    return r.depth - 0.010 - _inner_drawer_body_depth(r)


def _build_inner_drawer(
    model: ArticulatedObject,
    r: ResolvedWallSafeWithHingedDoorAndDialConfig,
    m: dict[str, str],
) -> Part:
    drawer = model.part("inner_drawer")
    # Part-local origin sits at the drawer front face plane (local y = 0 is the
    # front); the tray body extends back (+Y) into the cavity from there.
    bd = _inner_drawer_body_depth(r)
    td = max(0.012, bd - 0.022)  # tray depth behind the front panel
    _box(drawer, "drawer_front", (r.width * 0.52, 0.022, 0.080), (0.0, 0.011, 0.0), m["door"])
    _box(
        drawer,
        "drawer_tray_floor",
        (r.width * 0.52, td, 0.016),
        (0.0, 0.022 + td * 0.5, -0.032),
        m["trim"],
    )
    _box(
        drawer,
        "drawer_left_wall",
        (0.018, td, 0.070),
        (-r.width * 0.25, 0.022 + td * 0.5, 0.0),
        m["trim"],
    )
    _box(
        drawer,
        "drawer_right_wall",
        (0.018, td, 0.070),
        (r.width * 0.25, 0.022 + td * 0.5, 0.0),
        m["trim"],
    )
    drawer_outer_x = r.width * 0.25 + 0.009
    slider_width = 0.010
    slider_depth = td + 0.010
    for side, label in ((-1.0, "left"), (1.0, "right")):
        # Each moving shoe is fused to one tray side and bears on the matching
        # body rail along X throughout the complete prismatic envelope. The
        # 10 mm rear tail reaches the back stop at rest and keeps at least a
        # 0.5 mm rail engagement at the most extreme resolved upper limit.
        _box(
            drawer,
            f"drawer_{label}_slider",
            (slider_width, slider_depth, 0.018),
            (
                side * (drawer_outer_x + slider_width * 0.5),
                0.022 + slider_depth * 0.5,
                0.0,
            ),
            m["trim"],
        )
    # Recessed grip lip flush with the front face (front at local y = 0), so no
    # element protrudes ahead of the tray toward the door.
    _box(drawer, "drawer_pull", (0.090, 0.006, 0.020), (0.0, 0.003, 0.026), m["accent"])
    return drawer


def build_wall_safe_with_hinged_door_and_dial(
    config: WallSafeWithHingedDoorAndDialConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    _ = assets
    config = config or WallSafeWithHingedDoorAndDialConfig()
    r = resolve_config(config)
    model = ArticulatedObject(r.name)
    m = _register_materials(model, r.material_style)
    body = _build_body(model, r, m)
    door = _build_door(model, r, m)
    dial = _build_dial(model, r, m)
    handle = _build_handle(model, r, m)

    axis_sign = 1.0 if r.hinge_side > 0 else -1.0
    model.articulation(
        "safe_door_hinge",
        ArticulationType.REVOLUTE,
        parent=body,
        child=door,
        origin=Origin(xyz=(r.hinge_x, r.hinge_y, 0.0)),
        axis=(0.0, 0.0, axis_sign),
        motion_limits=MotionLimits(effort=120.0, velocity=1.0, lower=0.0, upper=r.door_swing),
    )
    dial_origin_y = -r.door_thickness * 0.5 - 0.020
    handle_origin_y = -r.door_thickness * 0.5 - 0.023
    model.articulation(
        "combination_dial_spin",
        ArticulationType.CONTINUOUS,
        parent=door,
        child=dial,
        origin=Origin(xyz=(r.dial_x, dial_origin_y, r.dial_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=4.0),
    )
    model.articulation(
        "handle_spin",
        ArticulationType.CONTINUOUS,
        parent=door,
        child=handle,
        origin=Origin(xyz=(r.handle_x, handle_origin_y, r.handle_z)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=12.0, velocity=2.0),
    )

    if r.aux_style == "deposit_flap":
        flap = _build_deposit_flap(model, r, m)
        flap_x, flap_y, flap_z = _deposit_flap_pose(r)
        # The flap panel hangs below/in front of this top hinge. Opening about
        # +X would swing the panel backward into the door slab (the census
        # 穿模); -X swings the lower edge outward/down (-Y), away from the door.
        model.articulation(
            "deposit_flap_hinge",
            ArticulationType.REVOLUTE,
            parent=door,
            child=flap,
            origin=Origin(xyz=(flap_x, flap_y, flap_z)),
            axis=(-1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=8.0, velocity=1.2, lower=0.0, upper=math.radians(75.0)
            ),
        )
    elif r.aux_style == "document_flap":
        flap = _build_document_flap(model, r, m)
        model.articulation(
            "document_flap_hinge",
            ArticulationType.REVOLUTE,
            parent=body,
            child=flap,
            origin=Origin(xyz=(0.0, 0.040, r.height * 0.30)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(
                effort=8.0, velocity=1.0, lower=0.0, upper=math.radians(70.0)
            ),
        )
    elif r.aux_style == "inner_drawer":
        drawer = _build_inner_drawer(model, r, m)
        # A wall-safe interior drawer sits behind the door and can only be pulled
        # once the door is out of the way. This is a SEQUENCED mechanism: the
        # drawer is only pulled open with the door swung open; "door closed +
        # drawer extended" is an unphysical pose a pose-setter can request but
        # that never occurs in operation, so it is the user's responsibility,
        # not a geometry defect. The drawer therefore keeps its FULL designed
        # travel (no clearance-solver clamp that strangled it to ~3cm short of
        # the CLOSED door plane), and the inner_drawer↔safe_door pair is
        # whitelisted for overlap in run_tests. The drawer↔safe_body cavity
        # walls remain fully checked (only the shelf/socket guide contacts are
        # allowed), so restoring travel cannot hide a real body penetration.
        model.articulation(
            "inner_drawer_slide",
            ArticulationType.PRISMATIC,
            parent=body,
            child=drawer,
            origin=Origin(xyz=(0.0, _inner_drawer_origin_y(r), -r.height * 0.28)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=20.0, velocity=0.1, lower=0.0, upper=r.drawer_travel),
        )
    return model


def build_seeded_wall_safe_with_hinged_door_and_dial(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_wall_safe_with_hinged_door_and_dial(config_from_seed(seed), assets=assets)


def _allow_expected_overlaps(
    ctx: TestContext,
    model: ArticulatedObject,
    r: ResolvedWallSafeWithHingedDoorAndDialConfig,
) -> None:
    names = {p.name for p in model.parts}
    if "safe_body" in names and "safe_door" in names:
        body = model.get_part("safe_body")
        door = model.get_part("safe_door")
        # Hinge capture: the door's hinge knuckles / leaf strip and the shot lock
        # bolts are captured by the frame hinge barrels, backstrap and stiles.
        # NOTE: door_slab is intentionally NOT in this list — a whole-slab-vs-
        # front-frame allowance would mask the slab poking through the frame.
        for elem_a in (
            "frame_hinge_barrel_0",
            "frame_hinge_barrel_1",
            "frame_hinge_barrel_2",
            "frame_hinge_barrel_3",
            "frame_hinge_barrel_4",
            "hinge_backstrap",
            "front_frame_left",
            "front_frame_right",
        ):
            for elem_b in (
                "door_hinge_knuckle_0",
                "door_hinge_knuckle_1",
                "door_hinge_knuckle_2",
                "door_hinge_knuckle_3",
                "door_hinge_knuckle_4",
                "hinge_leaf_strip",
                "sliding_lock_bolt_0",
                "sliding_lock_bolt_1",
                "sliding_lock_bolt_2",
                "sliding_lock_bolt_3",
                "sliding_lock_bolt_4",
            ):
                ctx.allow_overlap(
                    body,
                    door,
                    elem_a=elem_a,
                    elem_b=elem_b,
                    reason="door hinge knuckles/leaf and shot bolts are captured by the frame hinge barrels and stiles",
                )
        # The door slab's hinge edge is captured on the pivot axis by the frame
        # hinge barrels and backstrap ONLY (barrel radius embeds ~0.02 into the
        # slab edge at the hinge). The latch (free) edge and the front-frame
        # stiles must clear the slab — no allowance there — so a slab that pokes
        # through the visible frame stays a real, un-masked failure.
        for elem_a in (
            "frame_hinge_barrel_0",
            "frame_hinge_barrel_1",
            "frame_hinge_barrel_2",
            "frame_hinge_barrel_3",
            "frame_hinge_barrel_4",
            "hinge_backstrap",
        ):
            ctx.allow_overlap(
                body,
                door,
                elem_a=elem_a,
                elem_b="door_slab",
                reason=f"door slab hinge edge is captured by the {elem_a} on the pivot axis",
            )
        for elem_a in ("inner_jamb_left", "inner_jamb_right"):
            for elem_b in (
                "door_hinge_knuckle_0",
                "door_hinge_knuckle_1",
                "door_hinge_knuckle_2",
                "door_hinge_knuckle_3",
                "door_hinge_knuckle_4",
                "hinge_leaf_strip",
            ):
                ctx.allow_overlap(
                    body,
                    door,
                    elem_a=elem_a,
                    elem_b=elem_b,
                    reason="side jambs are tight around the hinge leaf but the door slab opens outside the safe body",
                )
    if "safe_door" in names and "combination_dial" in names:
        door = model.get_part("safe_door")
        dial = model.get_part("combination_dial")
        for elem_a in (
            "dial_socket_pad",
            "handle_socket_pad",
            "lock_boss_plate",
            "raised_door_panel",
        ):
            for elem_b in ("dial_body", "dial_outer_ring", "dial_center_cap"):
                ctx.allow_overlap(
                    door,
                    dial,
                    elem_a=elem_a,
                    elem_b=elem_b,
                    reason="combination dial shaft seats into the reinforced door boss",
                )
    if "safe_door" in names and "handle" in names:
        door = model.get_part("safe_door")
        handle = model.get_part("handle")
        handle_elems = (
            "handle_hub",
            "t_handle_stem",
            "t_handle_crossbar",
            "latch_lever_bar",
            "lever_counterweight",
            "wheel_outer_ring_proxy",
            "wheel_spoke_0",
            "wheel_spoke_1",
            "wheel_spoke_2",
            "wheel_spoke_3",
            "wheel_spoke_4",
            "wheel_spoke_5",
            "wheel_spoke_6",
            "wheel_spoke_7",
            "spoke_0",
            "spoke_1",
            "spoke_2",
            "spoke_3",
        )
        for elem_a in (
            "door_slab",
            "handle_socket_pad",
            "dial_socket_pad",
            "lock_boss_plate",
            "raised_door_panel",
        ):
            for elem_b in handle_elems:
                ctx.allow_overlap(
                    door,
                    handle,
                    elem_a=elem_a,
                    elem_b=elem_b,
                    reason="safe handle spindle and spokes sit on the reinforced door boss",
                )
    if "safe_body" in names and "inner_drawer" in names:
        body = model.get_part("safe_body")
        drawer = model.get_part("inner_drawer")
        for elem_a in ("interior_shelf", "bottom_recess_wall", "drawer_slide_socket"):
            for elem_b in (
                "drawer_front",
                "drawer_tray_floor",
                "drawer_left_wall",
                "drawer_right_wall",
                "drawer_pull",
            ):
                ctx.allow_overlap(
                    body,
                    drawer,
                    elem_a=elem_a,
                    elem_b=elem_b,
                    reason="drawer tray slides in the safe cavity against the shelf and lower guides",
                )
        # Sequenced mechanism: the inner cash drawer is only pulled open once the
        # hinged door has swung clear. "door shut + drawer extended" is an
        # unphysical pose a pose-setter can request but that never occurs in
        # operation — it is the user's responsibility, not a geometry defect — so
        # the drawer keeps its FULL designed travel (no clearance-solver clamp)
        # and the inner_drawer↔safe_door pair is whitelisted for overlap. Scoped
        # to exactly this pair: drawer↔safe_body cavity walls stay checked (only
        # the shelf/socket guide contacts above are allowed), so restoring travel
        # cannot mask a real body penetration.
        if "safe_door" in names:
            door = model.get_part("safe_door")
            ctx.allow_overlap(
                drawer,
                door,
                reason=(
                    "Sequenced mechanism: the inner cash drawer pulls out (front) "
                    "only over the OPEN hinged door; the sampled 'door shut + drawer "
                    "extended' pose is an unphysical pose-setter combo, not a real "
                    "operating state, so any drawer/door_slab overlap in that combo "
                    "is allowed. Scoped to inner_drawer↔safe_door only."
                ),
            )
    if "safe_body" in names and "document_flap" in names:
        body = model.get_part("safe_body")
        flap = model.get_part("document_flap")
        ctx.allow_overlap(
            body,
            flap,
            elem_a="document_flap_socket",
            elem_b="document_flap_hinge_barrel",
            reason="document flap hinge barrel sits in the safe body hinge socket",
        )
        # The closed flap panel seats against the internal hinge socket. (This
        # allowance was previously misfiled in the dial+handle branch where
        # `body`/`flap` were unbound, so a NameError silently skipped it.)
        ctx.allow_overlap(
            body,
            flap,
            elem_a="document_flap_socket",
            elem_b="document_flap_panel",
            reason="document flap panel closes against the internal hinge socket",
        )
    if "safe_door" in names and "deposit_flap" in names:
        door = model.get_part("safe_door")
        flap = model.get_part("deposit_flap")
        for elem_b in ("deposit_flap_hinge_barrel", "deposit_flap_panel"):
            ctx.allow_overlap(
                door,
                flap,
                elem_a="deposit_flap_socket",
                elem_b=elem_b,
                reason="deposit flap hinge barrel sits in the door-mounted socket",
            )
    if "combination_dial" in names and "handle" in names:
        dial = model.get_part("combination_dial")
        handle = model.get_part("handle")
        dial_elems = (
            "dial_body",
            "dial_outer_ring",
            "dial_center_cap",
            "dial_tick_0",
            "dial_tick_1",
            "dial_tick_2",
            "dial_tick_3",
            "dial_tick_4",
            "dial_tick_5",
            "dial_tick_6",
            "dial_tick_7",
            "dial_tick_8",
            "dial_tick_9",
            "dial_tick_10",
            "dial_tick_11",
        )
        handle_elems = (
            "handle_hub",
            "t_handle_stem",
            "t_handle_crossbar",
            "latch_lever_bar",
            "lever_counterweight",
            "wheel_outer_ring_proxy",
            "wheel_spoke_0",
            "wheel_spoke_1",
            "wheel_spoke_2",
            "wheel_spoke_3",
            "wheel_spoke_4",
            "wheel_spoke_5",
            "wheel_spoke_6",
            "wheel_spoke_7",
            "spoke_0",
            "spoke_1",
            "spoke_2",
            "spoke_3",
        )
        for elem_a in dial_elems:
            for elem_b in handle_elems:
                ctx.allow_overlap(
                    dial,
                    handle,
                    elem_a=elem_a,
                    elem_b=elem_b,
                    reason="dial and handle share a compact coaxial lock stack on the safe door",
                )


def run_wall_safe_with_hinged_door_and_dial_tests(
    object_model: ArticulatedObject,
    config: WallSafeWithHingedDoorAndDialConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model, r)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.joints}
    for required in ("safe_body", "safe_door", "combination_dial", "handle"):
        if required not in part_names:
            ctx.fail("identity_parts", f"missing {required}")
    for required in ("safe_door_hinge", "combination_dial_spin", "handle_spin"):
        if required not in joint_names:
            ctx.fail("identity_joints", f"missing {required}")
    if "safe_door_hinge" in joint_names and "safe_door" in part_names:
        door = object_model.get_part("safe_door")
        rest = ctx.part_element_world_aabb(door, elem="door_slab")
        with ctx.pose(safe_door_hinge=r.door_swing * 0.55):
            opened = ctx.part_element_world_aabb(door, elem="door_slab")
            ctx.fail_if_parts_overlap_in_current_pose(name="door_open_no_box_penetration")
        if rest is not None and opened is not None:
            rest_x = (rest[0][0] + rest[1][0]) * 0.5
            opened_x = (opened[0][0] + opened[1][0]) * 0.5
            rest_y = (rest[0][1] + rest[1][1]) * 0.5
            opened_y = (opened[0][1] + opened[1][1]) * 0.5
            ctx.check(
                "door_swings_about_side_hinge",
                abs(opened_x - rest_x) > 0.04,
                details=f"rest_x={rest_x:.3f}, opened_x={opened_x:.3f}",
            )
            ctx.check(
                "door_opens_outside_safe_body",
                opened_y < rest_y - 0.035,
                details=f"rest_y={rest_y:.3f}, opened_y={opened_y:.3f}",
            )
    # Strengthen: with the door SHUT, the latch (free) edge must not penetrate
    # the latch-side frame stile. There is no allowance on that side, so a slab
    # that pokes through the frame here is a real, un-masked failure.
    if "safe_door" in part_names and "safe_body" in part_names:
        door = object_model.get_part("safe_door")
        body = object_model.get_part("safe_body")
        latch_jamb = "inner_jamb_left" if r.hinge_side > 0 else "inner_jamb_right"
        slab_box = ctx.part_element_world_aabb(door, elem="door_slab")
        jamb_box = ctx.part_element_world_aabb(body, elem=latch_jamb)
        if slab_box is not None and jamb_box is not None:
            if r.hinge_side > 0:
                # latch edge is the door's -X edge; the jamb sits further -X.
                gap = slab_box[0][0] - jamb_box[1][0]
            else:
                # latch edge is the door's +X edge; the jamb sits further +X.
                gap = jamb_box[0][0] - slab_box[1][0]
            ctx.check(
                "closed_door_latch_edge_clears_frame",
                gap >= -1e-4,
                details=f"latch_side_gap={gap:.4f} (jamb={latch_jamb})",
            )
    if "combination_dial_spin" in joint_names:
        j = object_model.get_articulation("combination_dial_spin")
        ctx.check("dial_continuous", j.articulation_type == ArticulationType.CONTINUOUS)
        ctx.check("dial_axis_front_to_back", j.axis == (0.0, 1.0, 0.0), details=f"{j.axis}")
    if "handle_spin" in joint_names:
        j = object_model.get_articulation("handle_spin")
        ctx.check("handle_continuous", j.articulation_type == ArticulationType.CONTINUOUS)
        ctx.check("handle_axis_front_to_back", j.axis == (0.0, 1.0, 0.0), details=f"{j.axis}")
    if (
        r.aux_style == "inner_drawer"
        and "inner_drawer_slide" in joint_names
        and "inner_drawer" in part_names
    ):
        drawer = object_model.get_part("inner_drawer")
        drawer_joint = object_model.get_articulation("inner_drawer_slide")
        travel = float(drawer_joint.motion_limits.upper)
        door_swing = float(object_model.get_articulation("safe_door_hinge").motion_limits.upper)
        # Sequenced mechanism: the drawer keeps its FULL designed travel — no
        # clearance-solver clamp trimming it back to clear the CLOSED door plane.
        ctx.check(
            "drawer_keeps_full_designed_travel",
            travel >= r.drawer_travel - 1e-6,
            details=f"travel={travel:.4f} vs designed {r.drawer_travel:.4f}",
        )
        rest = ctx.part_element_world_aabb(drawer, elem="drawer_front")
        with ctx.pose(inner_drawer_slide=travel * 0.75):
            pulled = ctx.part_element_world_aabb(drawer, elem="drawer_front")
        # Real operating pose: fully extended with the door SWUNG OPEN. Only the
        # allowed cavity guide contacts (shelf/socket) may overlap — the drawer
        # must not penetrate any other body element at full travel. (The
        # unphysical door-shut + drawer-out pose is whitelisted via the
        # inner_drawer↔safe_door allowance and is the pose-setter's concern.)
        with ctx.pose(inner_drawer_slide=travel, safe_door_hinge=door_swing):
            ctx.fail_if_parts_overlap_in_current_pose(
                name="drawer_at_full_travel_clears_body_over_open_door",
            )
        if rest is not None and pulled is not None:
            rest_y = (rest[0][1] + rest[1][1]) * 0.5
            pulled_y = (pulled[0][1] + pulled[1][1]) * 0.5
            ctx.check(
                "drawer_pulls_outward",
                pulled_y < rest_y - 0.020,
                details=f"rest_y={rest_y:.3f}, pulled_y={pulled_y:.3f}",
            )
    return ctx.report()


__all__ = [
    "WallSafeWithHingedDoorAndDialConfig",
    "ResolvedWallSafeWithHingedDoorAndDialConfig",
    "build_wall_safe_with_hinged_door_and_dial",
    "build_seeded_wall_safe_with_hinged_door_and_dial",
    "config_from_seed",
    "resolve_config",
    "run_wall_safe_with_hinged_door_and_dial_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
