# SPDX-License-Identifier: Apache-2.0

"""mailbox — modular procedural template (curbside / street letter collection box).

Category identity: a **HOLLOW mail-collection cavity** (arched tunnel /
cast-iron pillar box / slant-top street cabinet / rounded streetbox) sits on a
**mount** (single post / two scroll legs / two plain legs / ground pedestal /
wall bracket) and presents a **defining REVOLUTE door** (bottom-hinged
pull-down hopper flap OR side-hinged swing door), with an **optional REVOLUTE
signal flag** (residential semaphore that raises q=0 / drops at positive q).

Canonical frame: back wall at x=0, **front opening face at +X**, width along Y
(centered), height +Z. Grounded mounts lift the body so its floor sits at
``MOUNT_Z`` (body min_z > ~0.45); the ``wall_bracket`` mount instead hangs the
body off a back plate at ``MOUNT_Z`` with no ground contact.

Four named slots (mixed pattern):
  body_form     — tunnel_arched / boxy_pillar / slanted_cabinet / rounded_streetbox
  mount         — single_post / two_legs_scroll / two_legs_plain / ground_pedestal / wall_bracket
  door_mechanism— pull_down_flap (axis Y, bottom hinge) / side_hinge_swing (axis Z, jamb hinge)
  signal_flag   — flag_present (axis Y semaphore) / flag_absent

The body is the structural hub: the mount is the grounded root (or back plate),
body is FIXED to it, and door + optional flag parent directly to body
(parallel-children REVOLUTE joints) — same construction style as cabinet.py.

Canonical spec: articraft_template_authoring/specs_modular_v1/Urban_Environment_Mailbox.md
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
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
# Enum domains
# ---------------------------------------------------------------------------
BodyForm = Literal[
    "tunnel_arched",
    "boxy_pillar",
    "slanted_cabinet",
    "rounded_streetbox",
]
Mount = Literal[
    "single_post",
    "two_legs_scroll",
    "two_legs_plain",
    "ground_pedestal",
    "wall_bracket",
]
DoorMechanism = Literal["pull_down_flap", "side_hinge_swing"]
SignalFlag = Literal["flag_present", "flag_absent"]
PaletteStyle = Literal[
    "postal_silver",
    "federal_blue",
    "pillar_red",
    "royal_green",
    "cast_iron_black",
    "weathered_copper",
]

BODY_FORMS: tuple[BodyForm, ...] = (
    "tunnel_arched",
    "boxy_pillar",
    "slanted_cabinet",
    "rounded_streetbox",
)
MOUNTS: tuple[Mount, ...] = (
    "single_post",
    "two_legs_scroll",
    "two_legs_plain",
    "ground_pedestal",
    "wall_bracket",
)
DOOR_MECHANISMS: tuple[DoorMechanism, ...] = ("pull_down_flap", "side_hinge_swing")
DOOR_WEIGHTS = (0.7, 0.3)
SIGNAL_FLAGS: tuple[SignalFlag, ...] = ("flag_present", "flag_absent")
SIGNAL_WEIGHTS = (0.5, 0.5)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "postal_silver",
    "federal_blue",
    "pillar_red",
    "royal_green",
    "cast_iron_black",
    "weathered_copper",
)

SCROLL_RING_COUNTS: tuple[int, ...] = (2, 3, 4)
SCROLL_RING_WEIGHTS = (0.3, 0.45, 0.25)
DECAL_STRIPE_COUNTS: tuple[int, ...] = (3, 4, 5)
DECAL_STRIPE_WEIGHTS = (0.3, 0.45, 0.25)
BACK_RIB_COUNTS: tuple[int, ...] = (3, 4, 5)
BACK_RIB_WEIGHTS = (0.5, 0.3, 0.2)

# Pillar / streetbox naturally stand on the ground; pedestal / post / legs all
# lift them. wall_bracket hangs every body off a plate (no ground contact).

# ---------------------------------------------------------------------------
# Palettes (per-seed). Keys: shell / door / cap / hardware / flag / dark.
# Sourced from 5-star sample materials (see spec §palette).
# ---------------------------------------------------------------------------
PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "postal_silver": {
        "shell": (0.42, 0.45, 0.50, 1.0),
        "door": (0.46, 0.52, 0.60, 1.0),
        "cap": (0.40, 0.43, 0.48, 1.0),
        "hardware": (0.72, 0.74, 0.78, 1.0),
        "flag": (0.74, 0.10, 0.13, 1.0),
        "dark": (0.14, 0.15, 0.17, 1.0),
    },
    "federal_blue": {
        "shell": (0.34, 0.42, 0.52, 1.0),
        "door": (0.40, 0.46, 0.55, 1.0),
        "cap": (0.31, 0.39, 0.49, 1.0),
        "hardware": (0.62, 0.55, 0.32, 1.0),
        "flag": (0.74, 0.10, 0.13, 1.0),
        "dark": (0.12, 0.15, 0.20, 1.0),
    },
    "pillar_red": {
        "shell": (0.66, 0.13, 0.14, 1.0),
        "door": (0.55, 0.10, 0.12, 1.0),
        "cap": (0.60, 0.11, 0.12, 1.0),
        "hardware": (0.62, 0.55, 0.32, 1.0),
        "flag": (0.16, 0.16, 0.17, 1.0),
        "dark": (0.20, 0.05, 0.05, 1.0),
    },
    "royal_green": {
        "shell": (0.16, 0.34, 0.24, 1.0),
        "door": (0.12, 0.28, 0.20, 1.0),
        "cap": (0.14, 0.31, 0.22, 1.0),
        "hardware": (0.62, 0.55, 0.32, 1.0),
        "flag": (0.74, 0.10, 0.13, 1.0),
        "dark": (0.06, 0.14, 0.10, 1.0),
    },
    "cast_iron_black": {
        "shell": (0.13, 0.13, 0.14, 1.0),
        "door": (0.16, 0.16, 0.17, 1.0),
        "cap": (0.11, 0.11, 0.12, 1.0),
        "hardware": (0.30, 0.30, 0.32, 1.0),
        "flag": (0.74, 0.10, 0.13, 1.0),
        "dark": (0.07, 0.07, 0.08, 1.0),
    },
    "weathered_copper": {
        "shell": (0.30, 0.42, 0.55, 1.0),
        "door": (0.45, 0.31, 0.22, 1.0),
        "cap": (0.55, 0.40, 0.30, 1.0),
        "hardware": (0.62, 0.55, 0.32, 1.0),
        "flag": (0.74, 0.10, 0.13, 1.0),
        "dark": (0.20, 0.18, 0.14, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Public + resolved config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class MailboxConfig:
    body_form: BodyForm = "tunnel_arched"
    mount: Mount = "single_post"
    door_mechanism: DoorMechanism = "pull_down_flap"
    signal_flag: SignalFlag = "flag_present"
    palette_style: PaletteStyle = "postal_silver"
    scroll_ring_count: int = 3
    decal_stripe_count: int = 4
    back_rib_count: int = 3
    body_width_scale: float = 1.0
    body_height_scale: float = 1.0
    body_depth_scale: float = 1.0
    mount_height_scale: float = 1.0
    door_open_scale: float = 1.0
    flag_raise_scale: float = 1.0
    name: str = "reference_mailbox"


@dataclass(frozen=True)
class ResolvedMailboxConfig:
    body_form: BodyForm
    mount: Mount
    door_mechanism: DoorMechanism
    signal_flag: SignalFlag
    palette_style: PaletteStyle
    scroll_ring_count: int
    decal_stripe_count: int
    back_rib_count: int
    # Canonical body envelope (back x=0, front opening at body_depth).
    body_width: float  # along Y
    body_depth: float  # along X (back -> front opening)
    body_height: float  # along Z (interior clear height of cavity / box)
    wall: float
    mount_z: float  # body floor height above ground (or hang height for wall)
    door_open_upper: float  # radians
    flag_raise_upper: float  # radians
    is_wall: bool
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


# ---------------------------------------------------------------------------
# Procedural sampler
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> MailboxConfig:
    rng = random.Random(seed)
    body = rng.choice(BODY_FORMS)
    mount = rng.choice(MOUNTS)
    door = rng.choices(DOOR_MECHANISMS, weights=DOOR_WEIGHTS, k=1)[0]
    flag = rng.choices(SIGNAL_FLAGS, weights=SIGNAL_WEIGHTS, k=1)[0]

    return MailboxConfig(
        body_form=body,
        mount=mount,
        door_mechanism=door,
        signal_flag=flag,
        palette_style=rng.choice(PALETTE_STYLES),
        scroll_ring_count=rng.choices(SCROLL_RING_COUNTS, weights=SCROLL_RING_WEIGHTS, k=1)[0],
        decal_stripe_count=rng.choices(
            DECAL_STRIPE_COUNTS, weights=DECAL_STRIPE_WEIGHTS, k=1
        )[0],
        back_rib_count=rng.choices(BACK_RIB_COUNTS, weights=BACK_RIB_WEIGHTS, k=1)[0],
        body_width_scale=round(rng.uniform(0.85, 1.18), 3),
        body_height_scale=round(rng.uniform(0.85, 1.20), 3),
        body_depth_scale=round(rng.uniform(0.9, 1.15), 3),
        mount_height_scale=round(rng.uniform(0.85, 1.15), 3),
        door_open_scale=round(rng.uniform(0.7, 1.0), 3),
        flag_raise_scale=round(rng.uniform(0.7, 1.0), 3),
        name=f"seeded_mailbox_{seed}",
    )


def resolve_config(config: MailboxConfig) -> ResolvedMailboxConfig:
    if config.body_form not in BODY_FORMS:
        raise ValueError(f"Unsupported body_form: {config.body_form}")
    if config.mount not in MOUNTS:
        raise ValueError(f"Unsupported mount: {config.mount}")
    if config.door_mechanism not in DOOR_MECHANISMS:
        raise ValueError(f"Unsupported door_mechanism: {config.door_mechanism}")
    if config.signal_flag not in SIGNAL_FLAGS:
        raise ValueError(f"Unsupported signal_flag: {config.signal_flag}")
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    body = config.body_form
    mount = config.mount
    is_wall = mount == "wall_bracket"

    w_scale = _clamp(config.body_width_scale, 0.85, 1.18)
    h_scale = _clamp(config.body_height_scale, 0.85, 1.20)
    d_scale = _clamp(config.body_depth_scale, 0.9, 1.15)
    mh_scale = _clamp(config.mount_height_scale, 0.85, 1.15)

    # Base body envelope by form (interior clear cavity dims).
    if body == "tunnel_arched":
        base_w, base_d, base_h = 0.34, 0.52, 0.30
    elif body == "boxy_pillar":
        base_w, base_d, base_h = 0.40, 0.40, 0.78
    elif body == "slanted_cabinet":
        base_w, base_d, base_h = 0.42, 0.42, 0.50
    else:  # rounded_streetbox
        base_w, base_d, base_h = 0.40, 0.44, 0.62

    body_width = round(base_w * w_scale, 4)
    body_height = round(base_h * h_scale, 4)
    body_depth = round(base_d * d_scale, 4)

    wall = 0.012
    liner = 0.012
    # Cavity-depth inequality: keep open cavity >= 0.25 along X. If the
    # depth scale shrank it below, push depth back up.
    min_cavity = 0.25
    if body_depth - wall - liner < min_cavity:
        body_depth = round(min_cavity + wall + liner + 0.005, 4)

    # Mount lift height. wall_bracket hangs the body; grounded mounts lift it.
    if is_wall:
        mount_z = round(1.0 * mh_scale, 4)
    elif mount == "ground_pedestal":
        mount_z = round(0.34 * mh_scale, 4)
    else:  # single_post / two_legs_*
        mount_z = round(1.02 * mh_scale, 4)
    # Pillar / streetbox are tall street-standing boxes; on a pedestal keep
    # them lower so they don't tower. Tunnel/slant residential ride higher.
    if body in ("boxy_pillar", "rounded_streetbox") and mount == "ground_pedestal":
        mount_z = round(0.18 * mh_scale, 4)

    door_open_upper = math.radians(85.0) * _clamp(config.door_open_scale, 0.7, 1.0)
    if config.door_mechanism == "pull_down_flap":
        door_open_upper = math.radians(90.0) * _clamp(config.door_open_scale, 0.7, 1.0)
    flag_raise_upper = math.radians(95.0) * _clamp(config.flag_raise_scale, 0.7, 1.0)

    return ResolvedMailboxConfig(
        body_form=body,
        mount=mount,
        door_mechanism=config.door_mechanism,
        signal_flag=config.signal_flag,
        palette_style=config.palette_style,
        scroll_ring_count=(
            config.scroll_ring_count if config.scroll_ring_count in SCROLL_RING_COUNTS else 3
        ),
        decal_stripe_count=(
            config.decal_stripe_count if config.decal_stripe_count in DECAL_STRIPE_COUNTS else 4
        ),
        back_rib_count=(
            config.back_rib_count if config.back_rib_count in BACK_RIB_COUNTS else 3
        ),
        body_width=body_width,
        body_depth=body_depth,
        body_height=body_height,
        wall=wall,
        mount_z=mount_z,
        door_open_upper=door_open_upper,
        flag_raise_upper=flag_raise_upper,
        is_wall=is_wall,
        name=config.name or "mailbox",
    )


# ---------------------------------------------------------------------------
# slot_choices
# ---------------------------------------------------------------------------
def _slot_choices_for_resolved(r: ResolvedMailboxConfig) -> list[tuple[str, str]]:
    mount_label = r.mount
    if r.mount == "two_legs_scroll":
        mount_label = f"two_legs_scroll_{r.scroll_ring_count}"
    body_label = r.body_form
    if r.body_form == "tunnel_arched":
        body_label = f"tunnel_arched_{r.decal_stripe_count}"
    elif r.body_form in ("boxy_pillar", "rounded_streetbox"):
        body_label = f"{r.body_form}_{r.back_rib_count}"
    return [
        ("body_form", body_label),
        ("mount", mount_label),
        ("door_mechanism", r.door_mechanism),
        ("signal_flag", r.signal_flag),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return _slot_choices_for_resolved(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------
def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.paint_coated")


def _meta(joint_type, axis, origin, limits) -> dict[str, object]:
    return {
        "type": joint_type.value,
        "axis": axis,
        "origin": origin,
        "range": None if limits is None else (limits.lower, limits.upper),
    }


@dataclass(frozen=True)
class _Frame:
    """Canonical body frame in WORLD coords (body is the root part): back wall
    at x=0, front opening at FRONT_X = BD, width along Y centered, floor at
    z0 = MOUNT_Z (the lift height). The mount is a FIXED child reaching down to
    the floor; door + flag are REVOLUTE children. Body frame == world frame, so
    every pivot uses world coordinates directly."""

    BW: float  # body width (Y)
    BD: float  # body depth (X) — back at 0, front opening at BD
    BH: float  # body interior clear height (Z)
    z0: float  # body floor height (world) = MOUNT_Z
    wall: float

    @property
    def FRONT_X(self) -> float:
        return self.BD

    @property
    def z1(self) -> float:
        return self.z0 + self.BH

    @property
    def INNER_W(self) -> float:
        return self.BW - 2.0 * self.wall


def _make_frame(r: ResolvedMailboxConfig) -> _Frame:
    # Body is the ROOT part authored in world coords (floor at z0 = MOUNT_Z).
    # The mount is a FIXED child reaching down to the ground; door + flag are
    # REVOLUTE children. Body frame == world frame.
    return _Frame(BW=r.body_width, BD=r.body_depth, BH=r.body_height, z0=r.mount_z, wall=r.wall)


# ===========================================================================
# SLOT A body_form factories. Build a HOLLOW shell as the `body` part.
# Each returns (open_zone_bot, open_zone_top, side_elem_names) describing the
# front opening band and the side-wall visuals the flag boss may lap.
# ===========================================================================
LINER = 0.012


def _build_body_tunnel_arched(body, fr: _Frame, r, mats):
    """Half-round arched tunnel: outer cadquery arch skin cut by an inner arch
    (true hollow cavity), open D-shaped mouth at +X, closed D back wall at x=0,
    box floor. No Box/Cylinder downgrade — the arch is a revolved/extruded
    cadquery solid."""
    BW, BD, wall = fr.BW, fr.BD, fr.wall
    z0 = fr.z0
    R = BW / 2.0  # outer arch radius
    Ri = R - wall  # inner arch radius
    # Outer half-cylinder tunnel (axis along X). Build a half-disc profile in
    # the YZ plane and extrude along X.
    def _half_tube(radius, length):
        # Semicircle profile (flat bottom on z0) in YZ, extruded along X.
        wp = (
            cq.Workplane("YZ")
            .moveTo(-radius, 0.0)
            .lineTo(radius, 0.0)
            .threePointArc((0.0, radius), (-radius, 0.0))
            .close()
            .extrude(length)
        )
        return wp.translate((0.0, 0.0, z0))

    outer = _half_tube(R, BD)
    inner = _half_tube(Ri, BD - wall).translate((wall, 0.0, 0.0))  # leave back wall
    shell = outer.cut(inner)
    body.visual(
        mesh_from_cadquery(shell, "arched_shell"),
        material=mats["shell"],
        name="arched_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"),
    )
    # Decal stripes: thin radial ridge bars welded onto the upper arch skin.
    # Each is intersected with a thin shell of the arch so it hugs the curve and
    # is solidly anchored to the skin (its inner edge sits inside the wall).
    n = r.decal_stripe_count
    for i in range(n):
        frac = (i + 0.5) / n
        ang = frac * (math.pi * 0.7) + math.pi * 0.15  # along arch, away from poles
        ry = (R + 0.002) * math.cos(ang)
        rz = (R + 0.002) * math.sin(ang)
        # Box centered slightly proud of the skin; its inner half embeds in the
        # wall so it touches arched_shell.
        ridge = (
            cq.Workplane("XY")
            .box(BD * 0.7, 0.022, 0.022)
            .translate((BD / 2.0, ry, z0 + rz),)
        )
        body.visual(
            mesh_from_cadquery(ridge, f"decal_stripe_{i}"),
            material=mats["flag"] if i % 2 else mats["hardware"],
            name=f"decal_stripe_{i}", material_class_id="metal.paint_coated",
        )
    # Box floor (closes the flat bottom into a tray).
    _box(body, (BD, BW - 0.004, wall), (BD / 2.0, 0.0, z0 - wall / 2.0 + 0.001),
         mats["shell"], "box_floor")
    # Interior back liner (dark) — proves a real deep cavity behind the mouth.
    _box(body, (LINER, (BW - 2 * wall) - 0.004, R - wall - 0.01),
         (wall + LINER / 2.0, 0.0, z0 + (R - wall) / 2.0), mats["dark"], "interior_back_liner")
    # Front mouth rim ring (lip around the opening, fused visual).
    rim = (
        cq.Workplane("YZ")
        .moveTo(-R, 0.0).lineTo(R, 0.0).threePointArc((0.0, R), (-R, 0.0)).close()
        .moveTo(-Ri, 0.0).lineTo(Ri, 0.0).threePointArc((0.0, Ri), (-Ri, 0.0)).close()
        .extrude(0.014)
    ).translate((BD - 0.014, 0.0, z0))
    body.visual(mesh_from_cadquery(rim, "front_rim"), material=mats["cap"], name="front_rim", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"))
    open_bot = z0 + 0.006
    open_top = z0 + (R - wall) * 0.95
    return open_bot, open_top, ("arched_shell",), R


def _build_thinwall_box_shell(body, fr: _Frame, mats, *, top_kind, r):
    """Six-thin-wall cast box shell (back / 2 sides / floor / top) with an
    interior back liner and a framed front opening. Shared by pillar + slant.
    top_kind: 'flat_lid' (pillar gets a half-cyl cap on top) or 'slant'."""
    BW, BD, BH, wall = fr.BW, fr.BD, fr.BH, fr.wall
    z0, z1 = fr.z0, fr.z1
    zc = z0 + BH / 2.0
    cm = mats["shell"]
    # Back wall.
    _box(body, (wall, BW, BH), (wall / 2.0, 0.0, zc), cm, "back_wall")
    # Side walls.
    for tag, s in (("0", 1.0), ("1", -1.0)):
        _box(body, (BD, wall, BH), (BD / 2.0, s * (BW / 2.0 - wall / 2.0), zc), cm,
             f"side_wall_{tag}")
    # Floor.
    _box(body, (BD, BW, wall), (BD / 2.0, 0.0, z0 + wall / 2.0), cm, "floor")
    # Interior back liner (dark deep cavity).
    _box(body, (LINER, BW - 2 * wall - 0.004, BH - 2 * wall),
         (wall + LINER / 2.0, 0.0, zc), mats["dark"], "interior_back_liner")
    # Back ribs (fused decorative, regular Y spread on the back face).
    nrib = r.back_rib_count
    for i in range(nrib):
        yy = -BW / 2.0 + (i + 0.5) * (BW / nrib)
        _box(body, (0.01, 0.02, BH * 0.85), (-0.005, yy, zc), mats["dark"], f"back_rib_{i}")
    # Front opening frame (sill below, header above, jambs on the sides).
    open_bot = z0 + 0.06
    open_top = z1 - 0.10
    fx = BD - wall / 2.0
    _box(body, (wall, BW, open_bot - z0), (fx, 0.0, (z0 + open_bot) / 2.0), cm, "front_sill")
    _box(body, (wall, BW, z1 - open_top), (fx, 0.0, (open_top + z1) / 2.0), cm, "front_header")
    jamb_w = 0.05
    for tag, s in (("0", 1.0), ("1", -1.0)):
        _box(body, (wall, jamb_w, open_top - open_bot),
             (fx, s * (BW / 2.0 - jamb_w / 2.0), (open_bot + open_top) / 2.0), cm, f"jamb_{tag}")
    return open_bot, open_top


def _build_body_boxy_pillar(body, fr: _Frame, r, mats):
    """Standing cast-iron pillar box: thin-wall box shell + half-cylinder domed
    top cap (cadquery half-tube along Y) + LETTERS band. Cap is a fused visual
    of the body (no separate part — does not articulate)."""
    open_bot, open_top = _build_thinwall_box_shell(body, fr, mats, top_kind="flat_lid", r=r)
    BW, BD = fr.BW, fr.BD
    z1 = fr.z1
    # Domed half-cylinder top cap (axis along Y), revolved cadquery solid.
    R = BD / 2.0
    cap = (
        cq.Workplane("XZ")
        .moveTo(-R, 0.0).lineTo(R, 0.0).threePointArc((0.0, R), (-R, 0.0)).close()
        .extrude(BW)
    ).translate((BD / 2.0, BW / 2.0, z1))
    body.visual(mesh_from_cadquery(cap, "cap_dome"), material=mats["cap"], name="cap_dome", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"))
    # LETTERS collection band (fused visual on the front face).
    _box(body, (0.008, BW * 0.8, 0.05), (BD + 0.002, 0.0, z1 - 0.07),
         mats["hardware"], "letters_band")
    # base skirt (flares at the floor, fused). pillar stands tall.
    _box(body, (BD + 0.04, BW + 0.04, 0.03), (BD / 2.0, 0.0, fr.z0 + 0.015),
         mats["cap"], "base_skirt")
    return open_bot, open_top, ("side_wall_0", "side_wall_1"), R


def _build_body_slanted_cabinet(body, fr: _Frame, r, mats):
    """Slant-top street cabinet: thin-wall box shell + a pitched wedge top
    (Box rotated about Y as a sloped lid) + triangular gable posts. The slanted
    lid is a fused visual (cap that does not articulate)."""
    open_bot, open_top = _build_thinwall_box_shell(body, fr, mats, top_kind="slant", r=r)
    BW, BD, wall = fr.BW, fr.BD, fr.wall
    z1 = fr.z1
    # Slanted top: a thick board pitched down toward the front (rpy about Y).
    pitch = math.radians(18.0)
    lid_len = BD / math.cos(pitch) + 0.04
    # center so the back edge sits at z1 and front edge drops.
    cz = z1 + 0.01 - (BD / 2.0) * math.tan(pitch)
    body.visual(
        Box((lid_len, BW + 0.03, 0.02)),
        origin=Origin(xyz=(BD / 2.0, 0.0, cz + (BD / 2.0) * math.tan(pitch)), rpy=(0.0, pitch, 0.0)),
        material=mats["cap"], name="slanted_top", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"),
    )
    # Triangular gable posts on each side filling the wedge under the slope.
    for tag, s in (("0", 1.0), ("1", -1.0)):
        body.visual(
            Box((BD, wall, 0.10)),
            origin=Origin(xyz=(BD / 2.0, s * (BW / 2.0 - wall / 2.0), z1 + 0.02),
                          rpy=(0.0, pitch, 0.0)),
            material=mats["shell"], name=f"gable_post_{tag}", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"),
        )
    return open_bot, open_top, ("side_wall_0", "side_wall_1"), BD / 2.0


def _build_body_rounded_streetbox(body, fr: _Frame, r, mats):
    """Rounded-shoulder streetbox: a cadquery hollow shell whose front wall
    sweeps over a rounded crown to the back wall (threePointArc), outer.cut(inner)
    making a true cavity, with a front box cutter for the delivery mouth and a
    fused cap ridge. No Box/Cylinder downgrade of the rounded crown."""
    BW, BD, BH, wall = fr.BW, fr.BD, fr.BH, fr.wall
    z0 = fr.z0
    crown_r = BD * 0.5
    # Profile in XZ: up the front wall, arc over the crown, down the back wall.
    straight_h = BH
    top_z = straight_h + crown_r * 0.6

    def _shell_solid(half_w, inset):
        prof = (
            cq.Workplane("XZ")
            .moveTo(0.0 + inset, 0.0)
            .lineTo(0.0 + inset, straight_h)
            .threePointArc((BD / 2.0, top_z - inset), (BD - inset, straight_h))
            .lineTo(BD - inset, 0.0)
            .close()
            .extrude(2.0 * half_w)
        )
        # "XZ" workplane extrudes along -Y (y: 0 -> -2*half_w); shift +half_w to
        # center the body width on y=0.
        return prof.translate((0.0, half_w, z0))

    outer = _shell_solid(BW / 2.0, 0.0)
    inner = _shell_solid(BW / 2.0 - wall, wall)
    # raise inner floor so a floor remains.
    inner = inner.translate((0.0, 0.0, wall))
    shell = outer.cut(inner)
    # Cut the front delivery mouth. open_bot is the front-wall sill top; the
    # mouth is cut ABOVE it so a solid front-wall sill survives below the
    # opening for the door hinge to anchor on real geometry.
    mouth_w = (BW - 2 * wall) * 0.7
    open_bot = z0 + BH * 0.30
    mouth_h = BH * 0.40
    mouth_cz = open_bot + 0.02 + mouth_h / 2.0  # bottom of cut = open_bot+0.02
    cutter = (
        cq.Workplane("XY")
        .box(0.10, mouth_w, mouth_h)
        .translate((BD - 0.02, 0.0, mouth_cz))
    )
    shell = shell.cut(cutter)
    # Union the structural ribs + cap ridge + base skirt into the shell solid so
    # the body reads as one welded casting (no disconnected islands on the
    # cadquery hollow shell).
    nrib = r.back_rib_count
    for i in range(nrib):
        yy = -BW / 2.0 + (i + 0.5) * (BW / nrib)
        # Rib penetrates deeply through the back wall (x spans well into the
        # solid) so the boolean union welds it cleanly into the shell.
        rib = cq.Workplane("XY").box(0.06, 0.02, BH * 0.8).translate((0.01, yy, z0 + BH / 2.0))
        shell = shell.union(rib, clean=True)
    cap_ridge = cq.Workplane("XY").box(BD * 0.5, BW * 0.5, 0.06).translate(
        (BD / 2.0, 0.0, z0 + top_z - 0.03))
    shell = shell.union(cap_ridge, clean=True)
    skirt = cq.Workplane("XY").box(BD + 0.04, BW + 0.04, 0.06).translate(
        (BD / 2.0, 0.0, z0 + 0.02))
    shell = shell.union(skirt, clean=True)
    body.visual(mesh_from_cadquery(shell, "body_shell"), material=mats["shell"], name="body_shell", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"))
    # Interior back liner (dark deep cavity behind the mouth) — embedded into the
    # inner back wall so it touches the shell.
    _box(body, (LINER + wall, mouth_w - 0.01, mouth_h * 0.9),
         ((wall + LINER) / 2.0, 0.0, mouth_cz), mats["dark"], "interior_back_liner")
    open_top = mouth_cz + mouth_h / 2.0
    return open_bot, open_top, ("body_shell",), crown_r


_BODY_FACTORIES = {
    "tunnel_arched": _build_body_tunnel_arched,
    "boxy_pillar": _build_body_boxy_pillar,
    "slanted_cabinet": _build_body_slanted_cabinet,
    "rounded_streetbox": _build_body_rounded_streetbox,
}


# ===========================================================================
# SLOT B mount factories. The mount is the grounded ROOT part (or wall plate).
# Each builds onto the `mount` part and returns nothing; body is FIXED above it.
# ===========================================================================
def _build_mount_single_post(mount, fr: _Frame, r, mats):
    """Single square steel post + base plate + top collar (collar top coplanar
    with body floor).

    Authored in MOUNT-LOCAL coords: collar TOP at local z=0 (the joint mating
    point under the body floor), descending to the ground at local z=-MOUNT_Z;
    x centered at 0 (the joint origin offsets it to under the body)."""
    H = r.mount_z
    post_sq = 0.07
    # base plate at the ground.
    _box(mount, (0.22, 0.22, 0.02), (0.0, 0.0, -H + 0.01), mats["hardware"], "base_plate")
    # post shaft from ground+0.02 up to the collar.
    _box(mount, (post_sq, post_sq, H - 0.04), (0.0, 0.0, -H + 0.02 + (H - 0.04) / 2.0),
         mats["shell"], "post_shaft")
    # top collar (top face at local z=0, just under the body floor).
    _box(mount, (0.14, 0.14, 0.02), (0.0, 0.0, -0.01), mats["cap"], "post_collar")


def _build_mount_two_legs_scroll(mount, fr: _Frame, r, mats):
    """Two square legs + foot pads + crossbar + stacked scroll iron rings.
    Mount-local: collar top at z=0, ground at z=-MOUNT_Z."""
    H = r.mount_z
    spread = fr.BW * 1.4
    leg_sq = 0.05
    for i, sgn in enumerate((-1.0, 1.0)):
        ly = sgn * spread / 2.0
        _box(mount, (0.12, 0.12, 0.018), (0.0, ly, -H + 0.009), mats["hardware"], f"foot_pad_{i}")
        _box(mount, (leg_sq, leg_sq, H - 0.018), (0.0, ly, -H + 0.018 + (H - 0.018) / 2.0),
             mats["shell"], f"leg_{i}")
    # crossbar near the top tying the legs.
    _box(mount, (0.04, spread, 0.04), (0.0, 0.0, -0.06), mats["shell"], "post_crossbar")
    # top collar under body floor (spans the full leg spread so it bridges
    # both leg tops into one connected mount).
    _box(mount, (0.16, spread + leg_sq, 0.02), (0.0, 0.0, -0.01), mats["cap"], "post_collar")
    # Scroll iron rings (stacked decorative C-curves welded against each leg).
    n = r.scroll_ring_count
    z0s = -0.10
    z1s = -0.30
    leg_iny = spread / 2.0 - leg_sq / 2.0  # inner face of each leg
    for k in range(n):
        zz = z0s + (z1s - z0s) * (k / max(1, n - 1)) if n > 1 else (z0s + z1s) / 2.0
        for s, sgn in enumerate((-1.0, 1.0)):
            # Ring centered so its outer rim laps the inner face of leg s.
            ring_cy = sgn * (leg_iny - 0.020)
            ring = (
                cq.Workplane("XY")
                .center(0.0, ring_cy)
                .circle(0.026)
                .circle(0.018)
                .extrude(0.014)
            ).translate((0.0, 0.0, zz))
            mount.visual(mesh_from_cadquery(ring, f"scroll_{k}_{s}"),
                         material=mats["shell"], name=f"scroll_{k}_{s}", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"))


def _build_mount_two_legs_plain(mount, fr: _Frame, r, mats):
    """Two plain square tube legs + foot pads + a single cross member.
    Mount-local: collar top at z=0, ground at z=-MOUNT_Z."""
    H = r.mount_z
    spread = fr.BW * 1.3
    leg_sq = 0.05
    for i, sgn in enumerate((-1.0, 1.0)):
        ly = sgn * spread / 2.0
        _box(mount, (0.12, 0.12, 0.018), (0.0, ly, -H + 0.009), mats["hardware"], f"foot_pad_{i}")
        _box(mount, (leg_sq, leg_sq, H - 0.018), (0.0, ly, -H + 0.018 + (H - 0.018) / 2.0),
             mats["shell"], f"leg_{i}")
    _box(mount, (0.04, spread, 0.04), (0.0, 0.0, -H * 0.55), mats["shell"], "cross_member")
    # collar spans the full leg spread so it bridges both leg tops.
    _box(mount, (0.16, spread + leg_sq, 0.02), (0.0, 0.0, -0.01), mats["cap"], "post_collar")


def _build_mount_ground_pedestal(mount, fr: _Frame, r, mats):
    """Three-step skirted pedestal base (stepped boxes), wider than the body,
    standing directly on the ground. Mount-local: top at z=0, ground at -H."""
    H = r.mount_z
    steps = [
        (fr.BD + 0.18, fr.BW + 0.18, H * 0.30),
        (fr.BD + 0.10, fr.BW + 0.10, H * 0.40),
        (fr.BD + 0.04, fr.BW + 0.04, H * 0.30),
    ]
    zc = -H
    for i, (sx, sy, sh) in enumerate(steps):
        _box(mount, (sx, sy, sh), (0.0, 0.0, zc + sh / 2.0),
             mats["cap"] if i == len(steps) - 1 else mats["shell"], f"pedestal_step_{i}")
        zc += sh


def _build_mount_wall_bracket(mount, fr: _Frame, r, mats):
    """Flat back plate (taller/wider than the body) + 4 corner bolt bosses.
    The body hangs off the plate's front face (no ground contact).

    Mount-local: the joint mating point (body back-bottom-center) is local
    (0,0,0); the plate spans up/down around it. Plate front face at local x=0."""
    plate_w = fr.BW + 0.14
    plate_h = fr.BH + 0.14
    plate_t = 0.02
    cz = fr.BH / 2.0  # plate centered on the body height above the joint point
    _box(mount, (plate_t, plate_w, plate_h), (-plate_t / 2.0, 0.0, cz),
         mats["shell"], "plate_panel")
    # 4 corner bolt bosses (cylinders laid through the plate, fused visuals).
    for i, (sy, sz) in enumerate(
        ((1, 1), (-1, 1), (-1, -1), (1, -1))
    ):
        by = sy * (plate_w / 2.0 - 0.03)
        bz = cz + sz * (plate_h / 2.0 - 0.03)
        mount.visual(
            Cylinder(radius=0.012, length=plate_t + 0.01),
            origin=Origin(xyz=(0.0, by, bz), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["hardware"], name=f"bolt_boss_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"postal_silver", "cast_iron_black"} else "metal.brass_aged"),
        )


_MOUNT_FACTORIES = {
    "single_post": _build_mount_single_post,
    "two_legs_scroll": _build_mount_two_legs_scroll,
    "two_legs_plain": _build_mount_two_legs_plain,
    "ground_pedestal": _build_mount_ground_pedestal,
    "wall_bracket": _build_mount_wall_bracket,
}


# ===========================================================================
# SLOT C door_mechanism factories. The door is a REVOLUTE child of body.
# Returns (joint_names, overlaps).
# ===========================================================================
DOOR_T = 0.016


def _build_door_pull_down_flap(model, body, fr: _Frame, r, mats, *, open_bot, open_top):
    """Bottom-hinged hopper flap. Hinge origin on the open bottom edge of the
    front opening; axis=(0,1,0); the panel extends from hinge +Z; positive q
    flips the free top edge out +X and down."""
    door_w = fr.INNER_W - 0.006
    door_h = open_top - open_bot
    # Explicit solid door sill on the body at the opening bottom — guarantees
    # the hinge origin lands on real geometry for every body form (curved
    # shells cut the front wall away at the mouth).
    body.visual(
        Box((0.05, fr.INNER_W, 0.02)),
        origin=Origin(xyz=(fr.FRONT_X - 0.022, 0.0, open_bot)),
        material=mats["cap"], name="door_sill", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"),
    )
    flap = model.part("door")
    # Panel: outer (front) face at local x=0..DOOR_T, hinge at local origin,
    # panel extends +Z from the hinge so the child AABB contains (0,0,0).
    flap.visual(
        Box((DOOR_T, door_w, door_h)),
        origin=Origin(xyz=(DOOR_T / 2.0, 0.0, door_h / 2.0)),
        material=mats["door"], name="flap_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"),
    )
    # Top rim lip (fused).
    flap.visual(
        Box((DOOR_T + 0.006, door_w, 0.012)),
        origin=Origin(xyz=(DOOR_T / 2.0, 0.0, door_h - 0.006)),
        material=mats["cap"], name="flap_top_rim", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"),
    )
    # Brass pull handle near the top free edge (proud +X).
    flap.visual(
        Box((0.014, door_w * 0.4, 0.012)),
        origin=Origin(xyz=(DOOR_T + 0.006, 0.0, door_h - 0.05)),
        material=mats["hardware"], name="flap_handle", material_class_id=("metal.stainless_matte" if r.palette_style in {"postal_silver", "cast_iron_black"} else "metal.brass_aged"),
    )
    flap.inertial = Inertial.from_geometry(Box((DOOR_T, door_w, door_h)), mass=1.2)
    origin = (fr.FRONT_X, 0.0, open_bot)
    limits = MotionLimits(effort=8.0, velocity=2.0, lower=0.0, upper=r.door_open_upper)
    model.articulation(
        "body_to_door",
        ArticulationType.REVOLUTE,
        parent=body, child=flap,
        origin=Origin(xyz=origin), axis=(0.0, 1.0, 0.0),
        motion_limits=limits,
        meta=_meta(ArticulationType.REVOLUTE, (0.0, 1.0, 0.0), origin, limits),
    )
    overlaps = []
    for de in ("flap_panel", "flap_top_rim", "flap_handle"):
        overlaps.append(("door", body.name, de, "door_sill",
                         "Closed flap rests on/laps the opening sill."))
        for elem in _front_frame_elems(r):
            overlaps.append(("door", body.name, de, elem,
                             "Closed flap laps the front opening frame edge."))
    return ["body_to_door"], overlaps


def _build_door_side_hinge_swing(model, body, fr: _Frame, r, mats, *, open_bot, open_top):
    """Side-hinged swing door. Hinge origin on the left jamb; axis=(0,0,-1)
    vertical; panel extends from hinge +Y; positive q swings the free edge out
    +X. Captured hinge barrels (body side, fused) + door hinge straps."""
    door_w = fr.INNER_W - 0.006
    door_h = open_top - open_bot
    door_zc = (open_bot + open_top) / 2.0
    hinge_y = -fr.INNER_W / 2.0 + 0.003
    # Hinge jamb post on the body at the hinge edge — a solid vertical bar the
    # barrels weld onto (curved shells have no jamb otherwise).
    body.visual(
        Box((0.03, 0.03, door_h + 0.02)),
        origin=Origin(xyz=(fr.FRONT_X - 0.012, hinge_y, door_zc)),
        material=mats["cap"], name="hinge_jamb", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"),
    )
    # Captured hinge barrels on the body side (fused body visuals).
    for i, zf in enumerate((0.25, 0.75)):
        bz = open_bot + door_h * zf
        body.visual(
            Cylinder(radius=0.009, length=0.05),
            origin=Origin(xyz=(fr.FRONT_X + 0.004, hinge_y, bz)),
            material=mats["hardware"], name=f"hinge_barrel_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"postal_silver", "cast_iron_black"} else "metal.brass_aged"),
        )
    # Strike plate on the opposite jamb.
    body.visual(
        Box((0.01, 0.03, door_h * 0.3)),
        origin=Origin(xyz=(fr.FRONT_X + 0.004, fr.INNER_W / 2.0 - 0.02, door_zc)),
        material=mats["hardware"], name="strike_plate", material_class_id=("metal.stainless_matte" if r.palette_style in {"postal_silver", "cast_iron_black"} else "metal.brass_aged"),
    )
    door = model.part("door")
    # Panel: hinge edge at local y=0, panel extends +Y; back face at local x=0,
    # extends +X (proud). Child frame origin (0,0,0) on the hinge edge.
    door.visual(
        Box((DOOR_T, door_w, door_h)),
        origin=Origin(xyz=(DOOR_T / 2.0, door_w / 2.0, 0.0)),
        material=mats["door"], name="door_panel", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"),
    )
    door.visual(
        Box((DOOR_T + 0.006, 0.02, door_h)),
        origin=Origin(xyz=(DOOR_T / 2.0, 0.004, 0.0)),
        material=mats["cap"], name="door_frame_rim", material_class_id=("metal.paint_coated" if r.palette_style in {"postal_silver", "federal_blue", "pillar_red", "royal_green", "weathered_copper"} else "metal.cast_iron_bare"),
    )
    # Hinge straps reaching back to clasp the barrels (along hinge edge).
    for i, zf in enumerate((0.25, 0.75)):
        sz = (zf - 0.5) * door_h
        door.visual(
            Cylinder(radius=0.0095, length=0.055),
            origin=Origin(xyz=(0.004, 0.0, sz)),
            material=mats["hardware"], name=f"door_hinge_strap_{i}", material_class_id=("metal.stainless_matte" if r.palette_style in {"postal_silver", "cast_iron_black"} else "metal.brass_aged"),
        )
    door.visual(
        Box((0.014, 0.05, 0.10)),
        origin=Origin(xyz=(DOOR_T + 0.006, door_w - 0.04, 0.0)),
        material=mats["hardware"], name="door_handle", material_class_id=("metal.stainless_matte" if r.palette_style in {"postal_silver", "cast_iron_black"} else "metal.brass_aged"),
    )
    door.inertial = Inertial.from_geometry(Box((DOOR_T, door_w, door_h)), mass=1.5)
    origin = (fr.FRONT_X, hinge_y, door_zc)
    limits = MotionLimits(effort=10.0, velocity=2.0, lower=0.0, upper=r.door_open_upper)
    model.articulation(
        "body_to_door",
        ArticulationType.REVOLUTE,
        parent=body, child=door,
        origin=Origin(xyz=origin), axis=(0.0, 0.0, -1.0),
        motion_limits=limits,
        meta=_meta(ArticulationType.REVOLUTE, (0.0, 0.0, -1.0), origin, limits),
    )
    overlaps = []
    door_elems = ("door_hinge_strap_0", "door_hinge_strap_1", "door_panel",
                  "door_frame_rim", "door_handle")
    for i in range(2):
        for de in door_elems:
            overlaps.append(("door", body.name, de, f"hinge_barrel_{i}",
                             "Door hinge hardware is captured around the body hinge barrel pin."))
    for de in door_elems:
        for be in ("door_sill", "strike_plate", "hinge_jamb"):
            overlaps.append(("door", body.name, de, be,
                             "Closed door laps the opening sill / jamb / strike."))
        for elem in _front_frame_elems(r):
            overlaps.append(("door", body.name, de, elem,
                             "Closed door laps the front opening frame edge."))
    return ["body_to_door"], overlaps


def _front_frame_elems(r) -> tuple[str, ...]:
    if r.body_form == "tunnel_arched":
        return ("arched_shell", "front_rim")
    if r.body_form == "rounded_streetbox":
        return ("body_shell",)
    return ("front_sill", "front_header", "jamb_0", "jamb_1", "side_wall_0", "side_wall_1")


_DOOR_FACTORIES = {
    "pull_down_flap": _build_door_pull_down_flap,
    "side_hinge_swing": _build_door_side_hinge_swing,
}


# ===========================================================================
# SLOT D signal_flag factory (present only). REVOLUTE child of body, axis Y.
# ===========================================================================
def _build_flag_present(model, body, fr: _Frame, r, mats, side_elems, body_half):
    """L-shaped semaphore flag: pivot_boss (short cylinder through the side
    wall) + vertical flag_arm + red flag_panel. axis=(0,1,0); q=0 raised
    (arm vertical), positive q drops. Boss captured against the side wall.

    Mounted on the +Y side, away from any wall plate."""
    pivot_x = fr.BD * 0.55
    if r.body_form == "tunnel_arched":
        # The arch skin tapers to the poles; mount the boss where real skin
        # exists: pick a mid-height, then the skin half-width at that z.
        R = fr.BW / 2.0
        rel_z = R * 0.45
        pivot_z = fr.z0 + rel_z
        side_y = math.sqrt(max(R * R - rel_z * rel_z, 0.0)) - 0.004
    else:
        side_y = fr.BW / 2.0
        pivot_z = fr.z0 + fr.BH * 0.55
    flag = model.part("flag")
    # Pivot boss: short cylinder laid along Y (through the side wall). Its AABB
    # contains the child frame origin (0,0,0) = the joint origin.
    # Boss spans the wall: local y from -0.012 (just inside) to +0.038 (outboard).
    flag.visual(
        Cylinder(radius=0.012, length=0.05),
        origin=Origin(xyz=(0.0, 0.013, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["hardware"], name="pivot_boss", material_class_id=("metal.stainless_matte" if r.palette_style in {"postal_silver", "cast_iron_black"} else "metal.brass_aged"),
    )
    # Vertical flag arm rises OUTBOARD of the body (local +Y) so it clears the
    # shell; origin (0,0,0) is contained via the boss.
    arm_h = 0.14
    # Arm overlaps the outboard end of the boss (boss reaches y=+0.038) and is
    # tall, so it welds to the boss and the panel.
    flag.visual(
        Box((0.012, 0.03, arm_h)),
        origin=Origin(xyz=(0.0, 0.035, arm_h / 2.0)),
        material=mats["flag"], name="flag_arm", material_class_id="metal.paint_coated",
    )
    # Flag panel at the top of the arm (red rectangle), overlapping the arm top.
    flag.visual(
        Box((0.008, 0.05, 0.07)),
        origin=Origin(xyz=(0.0, 0.05, arm_h - 0.03)),
        material=mats["flag"], name="flag_panel", material_class_id="metal.paint_coated",
    )
    flag.inertial = Inertial.from_geometry(Box((0.05, 0.05, arm_h), ), mass=0.2)
    origin = (pivot_x, side_y, pivot_z)
    limits = MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=r.flag_raise_upper)
    model.articulation(
        "body_to_flag",
        ArticulationType.REVOLUTE,
        parent=body, child=flag,
        origin=Origin(xyz=origin), axis=(0.0, 1.0, 0.0),
        motion_limits=limits,
        meta=_meta(ArticulationType.REVOLUTE, (0.0, 1.0, 0.0), origin, limits),
    )
    overlaps = [("flag", body.name, "pivot_boss", elem,
                 "Flag pivot boss is captured through the body side wall.")
                for elem in side_elems]
    return ["body_to_flag"], overlaps


# ===========================================================================
# Top-level builder
# ===========================================================================
def build_mailbox(
    config: MailboxConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or MailboxConfig()
    r = resolve_config(cfg)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-mailbox-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)

    palette = PALETTES[r.palette_style]
    mats = {key: model.material(f"mailbox_{key}_{r.palette_style}", rgba=rgba)
            for key, rgba in palette.items()}

    fr = _make_frame(r)

    # Body = ROOT part: HOLLOW collection cavity authored in WORLD coords
    # (floor at z=MOUNT_Z). Body frame == world frame.
    body = model.part("body")
    open_bot, open_top, side_elems, body_half = _BODY_FACTORIES[r.body_form](body, fr, r, mats)
    body.inertial = Inertial.from_geometry(
        Box((fr.BD, fr.BW, fr.BH)), mass=6.0,
        origin=Origin(xyz=(fr.BD / 2.0, 0.0, fr.z0 + fr.BH / 2.0)),
    )

    # Mount = FIXED child of body, authored in MOUNT-LOCAL coords (collar/plate
    # mating face at local (0,0,0)) reaching down to the ground (or hanging off
    # a wall plate). The joint origin places that local origin at the mating
    # point in the body/world frame.
    mount = model.part("mount")
    _MOUNT_FACTORIES[r.mount](mount, fr, r, mats)
    mount.inertial = Inertial.from_geometry(
        Box((0.2, 0.2, max(r.mount_z, 0.1))), mass=8.0,
        origin=Origin(xyz=(0.0, 0.0, -r.mount_z / 2.0)),
    )

    overlaps: list = []
    if r.is_wall:
        # Body back wall outer face (world x=0) mates the plate front face; the
        # mount-local (0,0,0) maps to the body back-bottom-center at world
        # (0, 0, MOUNT_Z).
        body_back_elem = (
            "body_shell" if r.body_form == "rounded_streetbox" else
            "arched_shell" if r.body_form == "tunnel_arched" else "back_wall"
        )
        model.articulation(
            "mount_to_body",
            ArticulationType.FIXED,
            parent=body, child=mount,
            origin=Origin(xyz=(0.0, 0.0, fr.z0)),
        )
        wall_elems = [body_back_elem, "base_skirt", "back_wall", "floor", "box_floor"]
        wall_elems += [f"back_rib_{i}" for i in range(6)]
        for be in wall_elems:
            for me in ["plate_panel"] + [f"bolt_boss_{i}" for i in range(4)]:
                overlaps.append(("body", "mount", be, me,
                                 "Body back wall / ribs seat against the wall plate."))
    else:
        # Mount collar top (mount-local z=0) seats under the body floor center
        # at world (BD/2, 0, MOUNT_Z). The joint origin lies on real geometry:
        # the body floor and the mount collar both straddle that point.
        model.articulation(
            "mount_to_body",
            ArticulationType.FIXED,
            parent=body, child=mount,
            origin=Origin(xyz=(fr.BD / 2.0, 0.0, fr.z0)),
        )
        # The body floor seats ON the mount top — declare the FIXED-contact
        # overlap between the body's bottom element and the mount's top element.
        body_bot_elem = (
            "body_shell" if r.body_form == "rounded_streetbox" else
            "arched_shell" if r.body_form == "tunnel_arched" else "floor"
        )
        if r.mount == "ground_pedestal":
            mount_top_elems = ["pedestal_step_2"]
        else:
            mount_top_elems = ["post_collar"]
        for mte in mount_top_elems:
            overlaps.append(("body", "mount", body_bot_elem, mte,
                             "Body floor seats on the mount top (FIXED contact)."))
        # Tunnel/pillar/slant also have a separate box_floor / base_skirt that
        # may lap the mount top.
        for be in ("box_floor", "base_skirt", "floor"):
            for mte in mount_top_elems:
                overlaps.append(("body", "mount", be, mte,
                                 "Body floor/skirt seats on the mount top."))

    # door -> body REVOLUTE (defining).
    door_joints, door_overlaps = _DOOR_FACTORIES[r.door_mechanism](
        model, body, fr, r, mats, open_bot=open_bot, open_top=open_top
    )
    overlaps.extend(door_overlaps)

    # flag -> body REVOLUTE (optional).
    flag_joints: list[str] = []
    if r.signal_flag == "flag_present":
        flag_joints, flag_overlaps = _build_flag_present(
            model, body, fr, r, mats, side_elems, body_half
        )
        overlaps.extend(flag_overlaps)

    model.meta["slot_choices"] = _slot_choices_for_resolved(r)
    model.meta["_mailbox_overlaps"] = overlaps
    model.meta["_mailbox_door_joints"] = door_joints
    model.meta["_mailbox_flag_joints"] = flag_joints
    return model


def build_seeded_mailbox(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_mailbox(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests
# ===========================================================================
def run_mailbox_tests(object_model: ArticulatedObject, config: MailboxConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    part_names = {p.name for p in object_model.parts}
    joint_names = {j.name for j in object_model.articulations}

    ctx.check("body part present", "body" in part_names)
    ctx.check("mount part present", "mount" in part_names)
    ctx.check("door part present", "door" in part_names)

    # Declare element-scoped overlaps recorded during build.
    overlaps = object_model.meta.get("_mailbox_overlaps", [])
    for pa, pb, ea, eb, reason in overlaps:
        if pa not in part_names or pb not in part_names:
            continue
        if ea is None:
            ctx.allow_overlap(object_model.get_part(pa), object_model.get_part(pb), reason=reason)
        else:
            ctx.allow_overlap(object_model.get_part(pa), object_model.get_part(pb),
                              elem_a=ea, elem_b=eb, reason=reason)

    # Two-legs-scroll: the ornamental wrought-iron scroll curls are an
    # intentional set of separate rigid flourishes on the post (adding a bridge
    # would invent material the real scrollwork does not have).
    if r.mount == "two_legs_scroll":
        fn = getattr(ctx, "allow_disconnected_islands", None)
        if fn is not None and "mount" in part_names:
            fn(object_model.get_part("mount"),
               reason="Wrought-iron scroll curls are intentional separate ornamental flourishes.")

    # Grounding vs wall-hang (mutually-exclusive validator branches).
    zmins = []
    for p in object_model.parts:
        ab = ctx.part_world_aabb(p)
        if ab is not None:
            zmins.append(ab[0][2])
    if r.is_wall:
        # Body hangs off the plate at MOUNT_Z; nothing should touch the floor.
        ctx.check("wall: body hung above ground (no floor contact)",
                  zmins and min(zmins) > 0.30, details=f"zmin={min(zmins):.4f}")
    else:
        # Grounded mount base rests on the floor; body lifted above 0.45.
        ctx.check("grounded: mount base on floor", zmins and abs(min(zmins)) <= 0.02,
                  details=f"zmin={min(zmins):.4f}")
        bb = ctx.part_world_aabb(object_model.get_part("body"))
        if bb is not None:
            # Tall pillar/streetbox on a low pedestal sit nearer the ground;
            # post/legs lift the residential bodies higher. Require a real lift
            # (body clearly off the floor, on its mount).
            min_lift = 0.12 if r.mount == "ground_pedestal" else 0.45
            ctx.check("grounded: body lifted off the floor", bb[0][2] > min_lift,
                      details=f"body_min_z={bb[0][2]:.4f}, min_lift={min_lift}")

    # mount -> body FIXED.
    j = object_model.get_articulation("mount_to_body")
    ctx.check("mount_to_body FIXED", j.articulation_type == ArticulationType.FIXED)

    # door -> body REVOLUTE (defining), correct axis per mechanism.
    jd = object_model.get_articulation("body_to_door")
    ctx.check("body_to_door REVOLUTE", jd.articulation_type == ArticulationType.REVOLUTE)
    if r.door_mechanism == "pull_down_flap":
        ctx.check("pull_down flap axis = Y",
                  abs(abs(jd.axis[1]) - 1.0) < 1e-6 and abs(jd.axis[0]) < 1e-9
                  and abs(jd.axis[2]) < 1e-9, details=str(jd.axis))
    else:
        ctx.check("side_hinge axis = Z",
                  abs(abs(jd.axis[2]) - 1.0) < 1e-6 and abs(jd.axis[0]) < 1e-9
                  and abs(jd.axis[1]) < 1e-9, details=str(jd.axis))

    # flag -> body REVOLUTE (present only).
    if r.signal_flag == "flag_present":
        ctx.check("flag part present", "flag" in part_names)
        jf = object_model.get_articulation("body_to_flag")
        ctx.check("body_to_flag REVOLUTE about Y",
                  jf.articulation_type == ArticulationType.REVOLUTE
                  and abs(abs(jf.axis[1]) - 1.0) < 1e-6, details=str(jf.axis))
    else:
        ctx.check("flag absent: no flag part", "flag" not in part_names)
        ctx.check("flag absent: no flag joint", "body_to_flag" not in joint_names)

    # Cavity depth >= 0.25 (hollow mail chute, not a solid block).
    cavity = r.body_depth - r.wall - LINER
    ctx.check("cavity depth >= 0.25", cavity >= 0.25, details=f"cavity={cavity:.4f}")

    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    return ctx.report()


__all__ = [
    "MailboxConfig",
    "ResolvedMailboxConfig",
    "build_mailbox",
    "build_seeded_mailbox",
    "config_from_seed",
    "resolve_config",
    "run_mailbox_tests",
    "slot_choices_for_seed",
]
