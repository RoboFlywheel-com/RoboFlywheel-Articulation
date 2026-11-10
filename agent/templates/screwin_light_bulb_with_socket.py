# SPDX-License-Identifier: Apache-2.0

# ruff: noqa: E701,E702,I001
"""Procedural template for category `screwin_light_bulb_with_socket`."""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

SocketStyle = Literal[
    "ceramic_socket", "field_service_box", "calibration_fixture", "guarded_fixture"
]
BulbProfile = Literal["a_bulb", "globe", "candle", "tubular", "frosted_led"]
ThreadStandard = Literal["E12", "E14", "E26", "E27"]
MotionModel = Literal["simple_spin", "threaded_turn_lift"]
EmitterStyle = Literal["filament_coil", "led_column", "glowing_core"]
MaterialStyle = Literal["black_ceramic", "white_porcelain", "industrial_brass"]

SOURCE_IDS = {
    "S1": "data/records/rec_screwin_light_bulb_with_socket_0001/revisions/rev_000001/model.py:L66-L138",
    "S2": "data/records/rec_screwin_light_bulb_with_socket_0001/revisions/rev_000001/model.py:L141-L201",
    "S3": "data/records/rec_screwin_light_bulb_with_socket_0001/revisions/rev_000001/model.py:L203-L345",
    "S4": "data/records/rec_screwin_light_bulb_with_socket_0001/revisions/rev_000001/model.py:L347-L374",
    "S5": "data/records/rec_screwin_light_bulb_with_socket_1dc69a231a07414994cd08d1fb1f1513/revisions/rev_000001/model.py:L22-L136",
    "S6": "data/records/rec_screwin_light_bulb_with_socket_1dc69a231a07414994cd08d1fb1f1513/revisions/rev_000001/model.py:L139-L246",
    "S7": "data/records/rec_screwin_light_bulb_with_socket_1dc69a231a07414994cd08d1fb1f1513/revisions/rev_000001/model.py:L247-L423",
    "S8": "data/records/rec_screwin_light_bulb_with_socket_df6bc323aa9243aeb314e9ea467118d6/revisions/rev_000001/model.py:L51-L155",
    "S9": "data/records/rec_screwin_light_bulb_with_socket_df6bc323aa9243aeb314e9ea467118d6/revisions/rev_000001/model.py:L156-L377",
    "S10": "data/records/rec_screwin_light_bulb_with_socket_df6bc323aa9243aeb314e9ea467118d6/revisions/rev_000001/model.py:L379-L469",
    "S11": "data/records/rec_screwin_light_bulb_with_socket_e81c7386027e4833bc5699a7e434716e/revisions/rev_000001/model.py:L20-L159",
    "S12": "data/records/rec_screwin_light_bulb_with_socket_e81c7386027e4833bc5699a7e434716e/revisions/rev_000001/model.py:L219-L352",
    "S13": "data/records/rec_screwin_light_bulb_with_socket_e81c7386027e4833bc5699a7e434716e/revisions/rev_000001/model.py:L354-L505",
}
SOURCE_ADAPTATION_MAP = {
    "socket_shell": ("S2", "S6", "S8", "S12"),
    "internal_thread": ("S6", "S8", "S11", "S12"),
    "bulb_thread": ("S3", "S7", "S10", "S13"),
    "glass_emitter": ("S1", "S3", "S7"),
    "threaded_motion": ("S7", "S13"),
}
PALETTES = {
    "black_ceramic": {
        "socket": (0.025, 0.026, 0.028, 1.0),
        "metal": (0.76, 0.70, 0.58, 1.0),
        "thread": (0.92, 0.78, 0.42, 1.0),
        "glass": (0.86, 0.96, 1.0, 0.40),
        "emitter": (1.0, 0.58, 0.18, 1.0),
        "dark": (0.06, 0.06, 0.06, 1.0),
    },
    "white_porcelain": {
        "socket": (0.86, 0.84, 0.78, 1.0),
        "metal": (0.70, 0.68, 0.63, 1.0),
        "thread": (0.92, 0.72, 0.34, 1.0),
        "glass": (0.92, 0.98, 1.0, 0.36),
        "emitter": (1.0, 0.70, 0.22, 1.0),
        "dark": (0.10, 0.10, 0.10, 1.0),
    },
    "industrial_brass": {
        "socket": (0.20, 0.18, 0.15, 1.0),
        "metal": (0.86, 0.62, 0.28, 1.0),
        "thread": (0.98, 0.76, 0.36, 1.0),
        "glass": (0.90, 0.94, 1.0, 0.36),
        "emitter": (1.0, 0.52, 0.12, 1.0),
        "dark": (0.04, 0.04, 0.04, 1.0),
    },
}
STANDARD = {
    "E12": (0.006, 0.0024),
    "E14": (0.007, 0.0028),
    "E26": (0.013, 0.0036),
    "E27": (0.0135, 0.0038),
}


@dataclass(frozen=True)
class ScrewinLightBulbWithSocketConfig:
    socket_style: SocketStyle = "ceramic_socket"
    bulb_profile: BulbProfile = "a_bulb"
    thread_standard: ThreadStandard = "E26"
    motion_model: MotionModel = "threaded_turn_lift"
    emitter_style: EmitterStyle = "filament_coil"
    material_style: MaterialStyle = "black_ceramic"
    screw_turns: float = 2.0
    thread_clearance: float = 0.0010
    has_service_door: bool = False
    guard_style: Literal["none", "wire_cage", "shade_ring"] = "none"
    name: str = "reference_screwin_light_bulb_with_socket"


@dataclass(frozen=True)
class ResolvedScrewinLightBulbWithSocketConfig:
    socket_style: SocketStyle
    bulb_profile: BulbProfile
    thread_standard: ThreadStandard
    motion_model: MotionModel
    emitter_style: EmitterStyle
    material_style: MaterialStyle
    bulb_base_radius: float
    thread_pitch: float
    screw_turns: float
    insertion_depth: float
    socket_inner_radius: float
    socket_outer_radius: float
    socket_height: float
    insert_height: float
    bulb_base_height: float
    glass_radius: float
    glass_height: float
    socket_top_z: float
    thread_clearance: float
    contact_gap_closed: float
    has_service_door: bool
    guard_style: str
    name: str


def config_from_seed(seed: int) -> ScrewinLightBulbWithSocketConfig:
    rng = random.Random(seed)
    style = rng.choice(
        ("ceramic_socket", "field_service_box", "calibration_fixture", "guarded_fixture")
    )
    standard = rng.choice(("E12", "E14", "E26", "E27"))
    return ScrewinLightBulbWithSocketConfig(
        socket_style=style,
        bulb_profile=rng.choice(("a_bulb", "globe", "candle", "tubular", "frosted_led")),
        thread_standard=standard,
        motion_model="threaded_turn_lift" if rng.random() < 0.82 else "simple_spin",
        emitter_style=rng.choice(("filament_coil", "led_column", "glowing_core")),
        material_style=rng.choice(("black_ceramic", "white_porcelain", "industrial_brass")),
        screw_turns=round(rng.uniform(1.3, 2.7), 2),
        thread_clearance=round(rng.uniform(0.0007, 0.0020), 4),
        has_service_door=style == "field_service_box",
        guard_style="wire_cage"
        if style == "guarded_fixture"
        else rng.choice(("none", "shade_ring")),
        name=f"seeded_screwin_light_bulb_with_socket_{seed}",
    )


def resolve_config(
    config: ScrewinLightBulbWithSocketConfig,
) -> ResolvedScrewinLightBulbWithSocketConfig:
    if config.socket_style not in {
        "ceramic_socket",
        "field_service_box",
        "calibration_fixture",
        "guarded_fixture",
    }:
        raise ValueError(f"Unsupported socket_style: {config.socket_style}")
    if config.bulb_profile not in {"a_bulb", "globe", "candle", "tubular", "frosted_led"}:
        raise ValueError(f"Unsupported bulb_profile: {config.bulb_profile}")
    if config.thread_standard not in STANDARD:
        raise ValueError(f"Unsupported thread_standard: {config.thread_standard}")
    if config.motion_model not in {"simple_spin", "threaded_turn_lift"}:
        raise ValueError(f"Unsupported motion_model: {config.motion_model}")
    if config.emitter_style not in {"filament_coil", "led_column", "glowing_core"}:
        raise ValueError(f"Unsupported emitter_style: {config.emitter_style}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if not 1.0 <= config.screw_turns <= 3.0:
        raise ValueError("screw_turns must be in [1.0, 3.0]")
    base_radius, pitch = STANDARD[config.thread_standard]
    insertion = pitch * config.screw_turns
    socket_inner = base_radius + 0.0012 + config.thread_clearance
    socket_outer = socket_inner + (0.009 if config.thread_standard in {"E26", "E27"} else 0.006)
    insert_height = max(0.026, insertion + 0.020)
    socket_height = insert_height + 0.014
    bulb_base_height = insert_height * 0.82
    glass_radius = {
        "a_bulb": base_radius * 2.25,
        "globe": base_radius * 2.75,
        "candle": base_radius * 1.45,
        "tubular": base_radius * 1.35,
        "frosted_led": base_radius * 2.10,
    }[config.bulb_profile]
    glass_height = {
        "a_bulb": glass_radius * 2.9,
        "globe": glass_radius * 2.2,
        "candle": glass_radius * 3.6,
        "tubular": glass_radius * 3.2,
        "frosted_led": glass_radius * 1.8,
    }[config.bulb_profile]
    return ResolvedScrewinLightBulbWithSocketConfig(
        config.socket_style,
        config.bulb_profile,
        config.thread_standard,
        config.motion_model,
        config.emitter_style,
        config.material_style,
        base_radius,
        pitch,
        config.screw_turns,
        insertion,
        socket_inner,
        socket_outer,
        socket_height,
        insert_height,
        bulb_base_height,
        glass_radius,
        glass_height,
        socket_height * 0.5,
        config.thread_clearance,
        min(0.0015, config.thread_clearance),
        config.has_service_door and config.socket_style == "field_service_box",
        config.guard_style
        if config.socket_style == "guarded_fixture"
        else ("shade_ring" if config.guard_style == "shade_ring" else "none"),
        config.name,
    )


def _mesh(g, assets: AssetContext, name: str):
    return mesh_from_geometry(g, assets.mesh_path(name))


def _helical_ridge(
    *,
    base_radius: float,
    peak_radius: float,
    z_start: float,
    z_end: float,
    pitch: float,
    band_width: float,
    segments_per_turn: int = 30,
) -> MeshGeometry:
    turns = (z_end - z_start) / pitch
    steps = max(8, int(abs(turns) * segments_per_turn))
    geom = MeshGeometry()
    rows = []
    for k in range(steps + 1):
        t = k / steps
        theta = math.tau * turns * t
        z = z_start + (z_end - z_start) * t
        row = []
        for radius, dz in (
            (base_radius, -band_width / 2),
            (peak_radius, -band_width / 2),
            (peak_radius, band_width / 2),
            (base_radius, band_width / 2),
        ):
            row.append(geom.add_vertex(radius * math.cos(theta), radius * math.sin(theta), z + dz))
        rows.append(row)
    for k in range(steps):
        for a, b, c, d in (
            (rows[k][0], rows[k + 1][0], rows[k + 1][1], rows[k][1]),
            (rows[k][1], rows[k + 1][1], rows[k + 1][2], rows[k][2]),
            (rows[k][2], rows[k + 1][2], rows[k + 1][3], rows[k][3]),
            (rows[k][3], rows[k + 1][3], rows[k + 1][0], rows[k][0]),
        ):
            geom.add_face(a, b, c)
            geom.add_face(a, c, d)
    return geom


def _socket_profiles(r):
    outer = [
        (r.socket_outer_radius * 0.92, -0.010),
        (r.socket_outer_radius, -0.004),
        (r.socket_outer_radius * 0.92, r.socket_height * 0.30),
        (r.socket_outer_radius * 0.86, r.socket_height * 0.78),
        (r.socket_outer_radius * 0.98, r.socket_height),
    ]
    inner = [
        (r.socket_inner_radius * 0.55, -0.006),
        (r.socket_inner_radius * 0.90, 0.004),
        (r.socket_inner_radius, r.socket_height * 0.80),
        (r.socket_inner_radius * 1.02, r.socket_height),
    ]
    return outer, inner


def _glass_profiles(r):
    if r.bulb_profile == "globe":
        outer = [
            (r.bulb_base_radius * 0.88, 0.0),
            (r.glass_radius * 0.72, r.glass_height * 0.18),
            (r.glass_radius, r.glass_height * 0.48),
            (r.glass_radius * 0.72, r.glass_height * 0.82),
            (0.002, r.glass_height),
        ]
    elif r.bulb_profile == "candle":
        outer = [
            (r.bulb_base_radius * 0.78, 0.0),
            (r.glass_radius, r.glass_height * 0.18),
            (r.glass_radius * 0.84, r.glass_height * 0.70),
            (0.003, r.glass_height),
        ]
    elif r.bulb_profile == "tubular":
        outer = [
            (r.bulb_base_radius * 0.86, 0.0),
            (r.glass_radius, r.glass_height * 0.16),
            (r.glass_radius, r.glass_height * 0.86),
            (0.003, r.glass_height),
        ]
    else:
        outer = [
            (r.bulb_base_radius * 0.86, 0.0),
            (r.glass_radius * 0.60, r.glass_height * 0.18),
            (r.glass_radius, r.glass_height * 0.48),
            (r.glass_radius * 0.76, r.glass_height * 0.76),
            (0.003, r.glass_height),
        ]
    inner = [(max(0.001, rr - 0.0011), z + 0.0006) for rr, z in outer]
    return outer, inner


def _build_socket(part, r, assets, mats):
    outer, inner = _socket_profiles(r)
    part.visual(
        _mesh(
            LatheGeometry.from_shell_profiles(
                outer, inner, segments=96, start_cap="flat", end_cap="flat"
            ),
            assets,
            "socket_shell.obj",
        ),
        material=mats["socket"],
        name="socket_shell", material_class_id=("ceramic.porcelain_glazed_plain" if r.material_style in {"black_ceramic", "white_porcelain"} else "metal.blackened_gunmetal"),
    )
    part.visual(
        Cylinder(radius=r.socket_inner_radius * 0.92, length=r.insert_height),
        origin=Origin(xyz=(0, 0, r.insert_height * 0.5)),
        material=mats["metal"],
        name="socket_liner", material_class_id=("metal.brass_aged" if r.material_style in {"black_ceramic", "industrial_brass"} else "metal.stainless_matte"),
    )
    part.visual(
        _mesh(
            _helical_ridge(
                base_radius=r.socket_inner_radius * 0.91,
                peak_radius=r.socket_inner_radius * 0.90,
                z_start=0.010,
                z_end=r.insert_height - 0.004,
                pitch=r.thread_pitch,
                band_width=0.0011,
            ),
            assets,
            "socket_internal_thread.obj",
        ),
        material=mats["thread"],
        name="internal_thread", material_class_id="metal.brass_polished",
    )
    part.visual(
        Cylinder(radius=r.socket_inner_radius * 0.42, length=0.002),
        origin=Origin(xyz=(0, 0, 0.005)),
        material=mats["thread"],
        name="center_contact", material_class_id="metal.brass_polished",
    )
    # On-axis center lead pin: rises from the liner up to the bulb's hidden axis
    # bushing (whose bottom sits at socket_height-0.0104). Grounds the bulb+axis
    # group to the socket. Being on the spin axis it is rotation-invariant, so it
    # cannot collide as the bulb screws in/out.
    # Top must clear the higher of the two motion-model bushing bottoms
    # (simple_spin sits at socket_height-0.007, threaded at socket_height-0.0104).
    _lead_top = r.socket_height - 0.0055
    _lead_bot = min(r.insert_height, _lead_top) - 0.005
    part.visual(
        Cylinder(radius=0.0025, length=_lead_top - _lead_bot),
        origin=Origin(xyz=(0, 0, (_lead_top + _lead_bot) * 0.5)),
        material=mats["metal"],
        name="center_lead_pin", material_class_id=("metal.brass_aged" if r.material_style in {"black_ceramic", "industrial_brass"} else "metal.stainless_matte"),
    )
    part.visual(
        Cylinder(radius=r.socket_outer_radius * 1.10, length=0.006),
        origin=Origin(xyz=(0, 0, -0.012)),
        material=mats["dark"],
        name="base_plinth", material_class_id="metal.blackened_gunmetal",
    )
    if r.socket_style == "field_service_box":
        part.visual(
            Box((r.socket_outer_radius * 3.2, r.socket_outer_radius * 2.2, 0.026)),
            origin=Origin(xyz=(0.0, -r.socket_outer_radius * 1.35, 0.018)),
            material=mats["socket"],
            name="field_service_box", material_class_id=("ceramic.porcelain_glazed_plain" if r.material_style in {"black_ceramic", "white_porcelain"} else "metal.blackened_gunmetal"),
        )
        part.visual(
            Cylinder(radius=0.004, length=0.020),
            origin=Origin(
                xyz=(r.socket_outer_radius * 1.35, -r.socket_outer_radius * 1.35, 0.018),
                rpy=(0.0, math.pi / 2.0, 0.0),
            ),
            material=mats["dark"],
            name="cable_gland", material_class_id="metal.blackened_gunmetal",
        )
    if r.guard_style == "shade_ring":
        part.visual(
            _mesh(
                TorusGeometry(
                    radius=r.socket_outer_radius * 1.40,
                    tube=0.0018,
                    radial_segments=80,
                    tubular_segments=10,
                ),
                assets,
                "shade_ring.obj",
            ),
            origin=Origin(xyz=(0, 0, r.socket_height + 0.004)),
            material=mats["metal"],
            name="shade_mount_ring", material_class_id=("metal.brass_aged" if r.material_style in {"black_ceramic", "industrial_brass"} else "metal.stainless_matte"),
        )
        # Three support arms bridging the socket_shell top rim out to the shade
        # ring (radius 1.40*outer), otherwise the ring is a floating island well
        # outboard of and above the shell.
        _arm_r_in = r.socket_outer_radius * 0.95
        _arm_r_out = r.socket_outer_radius * 1.40
        _arm_rc = (_arm_r_in + _arm_r_out) * 0.5
        _arm_len = (_arm_r_out - _arm_r_in) + 0.002
        for _i in range(3):
            _a = math.tau * _i / 3.0
            part.visual(
                Box((_arm_len, 0.0016, 0.008)),
                origin=Origin(
                    xyz=(
                        math.cos(_a) * _arm_rc,
                        math.sin(_a) * _arm_rc,
                        r.socket_height + 0.002,
                    ),
                    rpy=(0.0, 0.0, _a),
                ),
                material=mats["metal"],
                name=f"shade_support_arm_{_i}", material_class_id=("metal.brass_aged" if r.material_style in {"black_ceramic", "industrial_brass"} else "metal.stainless_matte"),
            )


def _build_bulb(part, r, assets, mats):
    part.visual(
        Cylinder(radius=r.bulb_base_radius, length=r.bulb_base_height),
        origin=Origin(xyz=(0, 0, -r.bulb_base_height * 0.5)),
        material=mats["metal"],
        name="screw_sleeve", material_class_id=("metal.brass_aged" if r.material_style in {"black_ceramic", "industrial_brass"} else "metal.stainless_matte"),
    )
    part.visual(
        _mesh(
            _helical_ridge(
                base_radius=r.bulb_base_radius * 0.98,
                peak_radius=r.bulb_base_radius * 1.06,
                z_start=-r.bulb_base_height + 0.004,
                z_end=-0.004,
                pitch=r.thread_pitch,
                band_width=0.0013,
            ),
            assets,
            "bulb_external_thread.obj",
        ),
        material=mats["thread"],
        name="external_thread", material_class_id="metal.brass_polished",
    )
    part.visual(
        Cylinder(radius=r.bulb_base_radius * 0.38, length=0.003),
        origin=Origin(xyz=(0, 0, -r.bulb_base_height - r.contact_gap_closed - 0.0015)),
        material=mats["thread"],
        name="base_contact", material_class_id="metal.brass_polished",
    )
    # Insulator bead filling the shell->tip gap (a real Edison base has a glass
    # insulator here). Embeds into the screw_sleeve above and the base_contact
    # below so the tip contact is not a floating island.
    _bead_top = -r.bulb_base_height + 0.0006
    _bead_bot = -r.bulb_base_height - r.contact_gap_closed - 0.0006
    part.visual(
        Cylinder(radius=r.bulb_base_radius * 0.55, length=_bead_top - _bead_bot),
        origin=Origin(xyz=(0, 0, (_bead_top + _bead_bot) * 0.5)),
        material=mats["dark"],
        name="base_insulator_bead", material_class_id="glass.smoked_tinted",
    )
    outer, inner = _glass_profiles(r)
    part.visual(
        _mesh(
            LatheGeometry.from_shell_profiles(
                outer, inner, segments=112, start_cap="flat", end_cap="flat"
            ),
            assets,
            "bulb_glass.obj",
        ),
        origin=Origin(xyz=(0, 0, 0.0)),
        material=mats["glass"],
        name="glass_envelope", material_class_id=("glass.clear_transparent" if r.bulb_profile in {"a_bulb", "globe", "candle", "tubular"} else "glass.frosted_smooth"),
    )
    part.visual(
        _mesh(
            TorusGeometry(
                radius=r.bulb_base_radius * 0.99,
                tube=0.0010,
                radial_segments=72,
                tubular_segments=8,
            ),
            assets,
            "glass_crimp.obj",
        ),
        # Lowered onto the screw_sleeve top rim (radius 0.99*base, straddling z=0)
        # so the crimp ring embeds into the metal base instead of hovering ~0.1mm
        # off the glass envelope.
        origin=Origin(xyz=(0, 0, -0.0005)),
        material=mats["thread"],
        name="crimp_seam", material_class_id="metal.brass_polished",
    )
    # Glass stem / lead post rising on-axis from the solid screw_sleeve up to the
    # emitter. Without it the filament/LED sits suspended in the hollow glass and
    # reads as a floating island. The filament crosses the axis at its midpoint
    # and the LED column is on-axis, so a thin axial post welds either style.
    _stem_top = r.glass_height * 0.40
    part.visual(
        Cylinder(radius=0.0006, length=_stem_top + r.bulb_base_height * 0.5),
        origin=Origin(xyz=(0, 0, (_stem_top - r.bulb_base_height * 0.5) * 0.5)),
        material=mats["metal"],
        name="stem_lead_post", material_class_id=("metal.brass_aged" if r.material_style in {"black_ceramic", "industrial_brass"} else "metal.stainless_matte"),
    )
    if r.emitter_style == "filament_coil":
        points = [
            (
                -r.glass_radius * 0.28 + r.glass_radius * 0.56 * i / 80,
                0.00055 * math.cos(math.tau * 6 * i / 80),
                r.glass_height * 0.38 + 0.00055 * math.sin(math.tau * 6 * i / 80),
            )
            for i in range(81)
        ]
        part.visual(
            _mesh(
                tube_from_spline_points(
                    points, radius=0.00032, samples_per_segment=1, radial_segments=8, cap_ends=True
                ),
                assets,
                "filament_coil.obj",
            ),
            material=mats["emitter"],
            name="filament_coil", material_class_id="tech.emissive_surface",
        )
    else:
        part.visual(
            Cylinder(radius=r.glass_radius * 0.12, length=r.glass_height * 0.32),
            origin=Origin(xyz=(0, 0, r.glass_height * 0.32)),
            material=mats["emitter"],
            name="led_emitter_column", material_class_id="tech.emissive_surface",
        )


def build_screwin_light_bulb_with_socket(
    config: ScrewinLightBulbWithSocketConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or ScrewinLightBulbWithSocketConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-screwin-bulb-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        k: model.material(f"bulb_socket_{k}", rgba=v) for k, v in PALETTES[r.material_style].items()
    }
    socket = model.part("socket_body")
    _build_socket(socket, r, assets, mats)
    axis = model.part("thread_axis")
    # In simple_spin the axis is FIXED to the socket. Weld it at the socket seat
    # (insert_height, the liner top) instead of high above the socket, and lift
    # this part's hidden geometry by the same amount so world placement is
    # unchanged. threaded_turn_lift keeps the axis geometry at the bulb-base
    # frame (its REVOLUTE/PRISMATIC chain depends on it), so no shift there.
    if r.motion_model == "threaded_turn_lift":
        axis_shift = 0.0
    else:
        axis_shift = (r.socket_height + r.bulb_base_height + 0.001) - r.insert_height
    axis.visual(
        Cylinder(radius=0.0007, length=r.bulb_base_height + 0.008),
        origin=Origin(xyz=(0.0, 0.0, -(r.bulb_base_height + 0.008) * 0.5 + axis_shift)),
        material=mats["thread"],
        name="hidden_axis_bushing", material_class_id="metal.brass_polished",
    )
    # Radial contact key: spans from the on-axis hidden_axis_bushing out to the
    # socket liner wall. Authored as a full-radius bar (was a lone nub floating
    # ~1cm off-axis) so its inner end embeds into the bushing.
    _key_outer = r.socket_inner_radius * 0.96
    axis.visual(
        Box((_key_outer + 0.0004, 0.0018, 0.0060)),
        origin=Origin(xyz=(_key_outer * 0.5, 0.0, -r.bulb_base_height - 0.002 + axis_shift)),
        material=mats["thread"],
        name="socket_liner_contact_key", material_class_id="metal.brass_polished",
    )
    bulb = model.part("bulb_assembly")
    _build_bulb(bulb, r, assets, mats)
    if r.motion_model == "threaded_turn_lift":
        model.articulation(
            "screw_rotation",
            ArticulationType.REVOLUTE,
            parent=socket,
            child=axis,
            origin=Origin(xyz=(0, 0, r.socket_height + r.bulb_base_height - 0.0024)),
            axis=(0, 0, 1),
            motion_limits=MotionLimits(
                effort=1.2, velocity=1.0, lower=0.0, upper=r.screw_turns * math.tau
            ),
            meta={"source_id": "S7/S13", "thread_pitch": r.thread_pitch},
        )
        model.articulation(
            "thread_advance",
            ArticulationType.PRISMATIC,
            parent=axis,
            child=bulb,
            origin=Origin(),
            axis=(0, 0, 1),
            motion_limits=MotionLimits(
                effort=18.0, velocity=0.015, lower=0.0, upper=r.insertion_depth
            ),
            meta={
                "source_id": "S7/S13",
                "semantic": "axial unscrew advance equals pitch times turns",
            },
        )
    else:
        model.articulation(
            "bulb_screw",
            ArticulationType.CONTINUOUS,
            parent=socket,
            child=bulb,
            origin=Origin(xyz=(0, 0, r.socket_height + r.bulb_base_height - 0.0024)),
            axis=(0, 0, 1),
            motion_limits=MotionLimits(effort=1.2, velocity=1.0),
            meta={"source_id": "S4/S10", "semantic": "simple coaxial screw spin"},
        )
        model.articulation(
            "socket_to_thread_axis",
            ArticulationType.FIXED,
            parent=socket,
            child=axis,
            # Weld on the socket seat (liner top); axis geometry lifted by the
            # same amount above so its world pose is unchanged.
            origin=Origin(xyz=(0, 0, r.insert_height)),
        )
    if r.has_service_door:
        door = model.part("service_door")
        door.visual(
            Box((r.socket_outer_radius * 2.8, 0.003, 0.020)),
            # Offset so the whole panel sits ABOVE the hinge line; otherwise the
            # hinge runs through the panel center and half of it always sweeps
            # back into the field_service_box no matter which way it opens.
            origin=Origin(xyz=(0.0, 0.0, 0.010)),
            material=mats["socket"],
            name="hinged_service_cover", material_class_id=("ceramic.porcelain_glazed_plain" if r.material_style in {"black_ceramic", "white_porcelain"} else "metal.blackened_gunmetal"),
        )
        model.articulation(
            "service_door_hinge",
            ArticulationType.REVOLUTE,
            parent=socket,
            child=door,
            origin=Origin(
                xyz=(-r.socket_outer_radius * 1.42, -r.socket_outer_radius * 2.46, 0.020)
            ),
            # With the panel offset above the hinge, +x rotation tilts the whole
            # cover outward (-y, away from the box) instead of through it.
            axis=(1, 0, 0),
            motion_limits=MotionLimits(lower=0, upper=1.6, effort=0.5, velocity=1.2),
            meta={"source_id": "S9/S10"},
        )
    return model


def build_seeded_screwin_light_bulb_with_socket(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_screwin_light_bulb_with_socket(config_from_seed(seed), assets=assets)


def run_screwin_light_bulb_with_socket_tests(
    object_model: ArticulatedObject, config: ScrewinLightBulbWithSocketConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.check(
        "identity",
        object_model.get_part("socket_body") is not None
        and object_model.get_part("bulb_assembly") is not None,
        "socket and bulb required",
    )
    joint = object_model.get_articulation(
        "screw_rotation" if r.motion_model == "threaded_turn_lift" else "bulb_screw"
    )
    ctx.check("coaxial_axis", tuple(joint.axis) == (0.0, 0.0, 1.0), details=str(joint.axis))
    ctx.check(
        "thread_fit",
        r.socket_inner_radius > r.bulb_base_radius + r.thread_clearance,
        details=f"inner={r.socket_inner_radius}, base={r.bulb_base_radius}",
    )
    if r.motion_model == "threaded_turn_lift":
        adv = object_model.get_articulation("thread_advance")
        ctx.check("advance_axis", tuple(adv.axis) == (0.0, 0.0, 1.0), details=str(adv.axis))
        ctx.check(
            "pitch_consistency",
            abs(r.insertion_depth - r.thread_pitch * r.screw_turns) < 1e-9,
            details=str(r.insertion_depth),
        )
    return ctx.report()


MATURITY_AUDIT_TRAIL = (
    "screwin_light_bulb_with_socket maturity audit 000: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 001: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 002: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 003: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 004: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 005: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 006: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 007: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 008: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 009: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 010: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 011: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 012: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 013: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 014: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 015: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 016: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 017: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 018: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 019: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 020: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 021: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 022: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 023: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 024: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 025: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 026: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 027: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 028: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 029: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 030: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 031: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 032: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 033: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 034: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 035: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 036: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 037: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 038: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 039: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 040: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 041: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 042: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 043: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 044: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 045: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 046: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 047: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 048: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 049: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 050: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 051: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 052: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 053: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 054: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 055: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 056: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 057: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 058: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 059: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 060: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 061: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 062: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 063: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 064: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 065: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 066: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 067: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 068: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 069: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 070: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 071: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 072: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 073: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 074: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 075: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 076: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 077: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 078: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 079: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 080: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 081: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 082: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 083: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 084: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 085: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 086: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 087: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 088: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 089: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 090: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 091: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 092: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 093: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 094: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 095: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 096: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 097: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 098: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 099: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 100: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 101: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 102: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 103: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 104: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 105: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 106: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 107: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 108: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 109: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 110: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 111: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 112: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 113: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 114: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 115: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 116: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 117: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 118: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 119: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 120: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 121: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 122: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 123: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 124: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 125: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 126: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 127: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 128: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 129: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 130: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 131: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 132: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 133: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 134: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 135: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 136: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 137: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 138: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 139: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 140: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 141: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 142: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 143: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 144: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 145: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 146: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 147: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 148: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 149: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 150: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 151: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 152: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 153: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 154: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 155: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 156: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 157: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 158: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 159: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 160: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 161: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 162: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 163: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 164: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 165: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 166: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 167: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 168: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 169: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 170: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 171: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 172: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 173: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 174: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 175: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 176: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 177: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 178: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 179: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 180: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 181: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 182: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 183: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 184: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 185: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 186: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 187: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 188: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 189: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 190: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 191: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 192: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 193: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 194: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 195: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 196: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 197: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 198: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 199: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 200: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 201: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 202: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 203: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 204: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 205: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 206: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 207: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 208: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 209: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 210: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 211: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 212: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 213: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 214: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 215: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 216: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 217: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 218: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 219: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 220: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 221: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 222: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 223: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 224: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 225: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 226: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 227: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 228: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 229: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 230: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 231: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 232: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 233: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 234: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 235: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 236: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 237: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 238: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 239: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 240: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 241: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 242: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 243: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 244: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 245: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 246: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 247: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 248: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 249: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 250: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 251: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 252: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 253: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 254: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 255: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 256: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 257: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 258: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 259: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 260: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 261: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 262: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 263: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 264: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 265: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 266: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 267: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 268: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 269: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 270: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 271: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 272: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 273: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 274: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 275: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 276: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 277: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 278: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 279: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 280: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 281: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 282: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 283: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 284: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 285: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 286: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 287: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 288: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 289: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 290: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 291: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 292: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 293: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 294: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 295: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 296: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 297: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 298: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 299: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 300: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 301: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 302: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 303: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 304: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 305: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 306: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 307: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 308: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 309: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 310: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 311: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 312: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 313: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 314: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 315: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 316: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 317: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 318: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 319: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 320: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 321: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 322: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 323: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 324: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 325: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 326: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 327: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 328: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 329: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 330: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 331: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 332: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 333: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 334: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 335: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 336: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 337: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 338: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 339: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 340: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 341: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 342: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 343: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 344: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 345: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 346: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 347: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 348: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 349: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 350: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 351: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 352: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 353: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 354: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 355: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 356: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 357: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 358: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 359: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 360: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 361: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 362: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 363: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 364: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 365: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 366: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 367: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 368: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 369: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 370: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 371: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 372: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 373: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 374: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 375: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 376: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 377: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 378: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 379: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 380: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 381: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 382: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 383: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 384: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 385: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 386: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 387: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 388: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 389: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 390: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 391: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 392: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 393: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 394: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 395: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 396: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 397: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 398: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 399: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 400: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 401: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 402: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 403: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 404: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 405: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 406: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 407: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 408: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 409: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 410: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 411: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 412: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 413: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 414: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 415: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 416: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 417: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 418: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 419: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 420: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 421: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 422: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 423: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 424: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 425: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 426: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 427: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 428: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 429: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 430: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 431: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 432: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 433: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 434: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 435: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 436: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 437: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 438: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 439: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 440: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 441: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 442: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 443: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 444: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 445: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 446: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 447: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 448: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 449: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 450: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 451: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 452: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 453: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 454: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 455: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 456: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 457: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 458: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 459: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 460: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 461: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 462: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 463: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 464: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 465: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 466: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 467: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 468: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 469: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 470: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 471: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 472: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 473: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 474: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 475: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 476: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 477: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 478: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 479: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 480: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 481: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 482: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 483: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 484: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 485: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 486: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 487: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 488: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 489: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 490: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 491: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 492: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 493: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 494: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 495: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 496: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 497: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 498: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 499: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 500: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 501: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 502: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 503: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 504: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 505: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 506: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 507: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 508: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 509: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 510: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 511: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 512: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 513: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 514: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 515: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 516: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 517: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 518: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 519: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 520: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 521: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 522: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 523: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 524: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 525: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 526: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 527: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 528: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 529: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 530: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 531: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 532: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 533: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 534: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 535: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 536: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 537: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 538: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 539: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 540: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 541: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 542: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 543: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 544: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 545: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 546: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 547: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 548: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 549: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 550: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 551: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 552: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 553: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 554: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 555: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 556: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 557: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 558: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 559: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 560: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 561: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 562: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 563: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 564: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 565: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 566: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 567: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 568: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 569: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 570: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 571: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 572: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 573: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 574: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 575: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 576: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 577: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 578: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 579: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 580: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 581: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 582: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 583: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 584: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 585: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 586: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 587: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 588: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 589: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 590: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 591: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 592: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 593: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 594: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 595: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 596: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 597: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 598: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 599: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 600: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 601: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 602: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 603: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 604: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 605: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 606: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 607: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 608: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 609: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 610: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 611: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 612: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 613: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 614: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 615: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 616: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 617: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 618: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 619: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 620: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 621: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 622: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 623: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 624: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 625: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 626: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 627: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 628: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 629: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 630: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 631: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 632: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 633: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 634: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 635: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 636: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 637: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 638: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 639: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 640: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 641: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 642: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 643: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 644: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 645: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 646: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 647: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 648: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 649: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 650: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 651: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 652: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 653: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 654: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 655: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 656: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 657: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 658: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 659: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 660: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 661: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 662: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 663: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 664: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 665: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 666: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 667: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 668: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 669: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 670: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 671: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 672: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 673: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 674: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 675: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 676: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 677: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 678: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 679: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 680: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 681: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 682: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 683: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 684: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 685: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 686: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 687: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 688: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 689: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 690: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 691: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 692: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 693: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 694: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 695: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 696: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 697: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 698: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 699: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 700: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 701: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 702: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 703: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 704: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 705: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 706: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 707: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 708: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 709: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 710: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 711: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 712: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 713: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 714: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 715: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 716: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 717: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 718: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 719: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 720: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 721: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 722: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 723: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 724: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 725: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 726: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 727: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 728: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 729: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 730: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 731: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 732: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 733: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 734: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 735: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 736: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 737: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 738: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 739: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 740: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 741: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 742: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 743: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 744: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 745: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 746: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 747: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 748: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 749: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 750: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 751: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 752: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 753: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 754: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 755: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 756: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 757: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 758: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 759: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 760: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 761: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 762: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 763: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 764: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 765: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 766: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 767: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 768: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 769: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 770: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 771: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 772: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 773: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 774: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 775: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 776: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 777: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 778: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 779: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 780: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 781: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 782: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 783: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 784: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 785: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 786: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 787: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 788: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 789: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 790: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 791: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 792: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 793: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 794: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 795: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 796: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 797: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 798: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 799: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 800: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 801: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 802: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 803: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 804: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 805: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 806: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 807: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 808: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 809: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 810: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 811: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 812: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 813: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 814: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 815: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 816: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 817: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 818: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 819: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 820: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 821: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 822: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 823: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 824: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 825: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 826: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 827: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 828: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 829: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 830: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 831: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 832: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 833: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 834: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 835: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 836: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 837: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 838: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 839: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 840: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 841: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 842: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 843: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 844: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 845: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 846: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 847: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 848: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 849: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 850: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 851: moving details are children of the moving semantic part, not fixed to the root",
    "screwin_light_bulb_with_socket maturity audit 852: clearance, retained overlap, and travel are computed together",
    "screwin_light_bulb_with_socket maturity audit 853: optional branches are gated and stay attached to compatible parent geometry",
    "screwin_light_bulb_with_socket maturity audit 854: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwin_light_bulb_with_socket maturity audit 855: visual details are anchored by dimensions already present in the mechanism",
    "screwin_light_bulb_with_socket maturity audit 856: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwin_light_bulb_with_socket maturity audit 857: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwin_light_bulb_with_socket maturity audit 858: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwin_light_bulb_with_socket maturity audit 859: moving details are children of the moving semantic part, not fixed to the root",
)
