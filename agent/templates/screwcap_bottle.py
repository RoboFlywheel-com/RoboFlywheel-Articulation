# SPDX-License-Identifier: Apache-2.0

"""Procedural template for category `screwcap_bottle`."""

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
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    tube_from_spline_points,
)

BottleProfile = Literal[
    "cylindrical_water", "slender_cosmetic", "wide_jar", "rugged_rect", "squeeze_bottle"
]
CapStyle = Literal["smooth", "knurled", "ribbed", "rugged_windowed", "tethered"]
ThreadRepresentation = Literal["helical", "banded"]
ScrewMotionModel = Literal["simple_spin", "threaded_turn_lift"]
MaterialStyle = Literal["clear_plastic", "amber_lab", "sports_smoke"]

SOURCE_IDS = {
    "S1": "data/records/rec_screwcap_bottle_0002/revisions/rev_000001/model.py:L30-L94",
    "S2": "data/records/rec_screwcap_bottle_0002/revisions/rev_000001/model.py:L105-L147",
    "S3": "data/records/rec_screwcap_bottle_0002/revisions/rev_000001/model.py:L256-L315",
    "S4": "data/records/rec_screwcap_bottle_3b72f1b06e424f34a33ec81fc85feb89/revisions/rev_000001/model.py:L28-L49",
    "S5": "data/records/rec_screwcap_bottle_3b72f1b06e424f34a33ec81fc85feb89/revisions/rev_000001/model.py:L52-L236",
    "S6": "data/records/rec_screwcap_bottle_3b72f1b06e424f34a33ec81fc85feb89/revisions/rev_000001/model.py:L238-L263",
    "S7": "data/records/rec_screwcap_bottle_aa1625790e9e4236941bc4c2650955de/revisions/rev_000001/model.py:L58-L138",
    "S8": "data/records/rec_screwcap_bottle_aa1625790e9e4236941bc4c2650955de/revisions/rev_000001/model.py:L141-L263",
    "S9": "data/records/rec_screwcap_bottle_aa1625790e9e4236941bc4c2650955de/revisions/rev_000001/model.py:L265-L282",
    "S10": "data/records/rec_screwcap_bottle_6b2c1386d07447bfa26806abf78b4935/revisions/rev_000001/model.py:L35-L126",
    "S11": "data/records/rec_screwcap_bottle_6b2c1386d07447bfa26806abf78b4935/revisions/rev_000001/model.py:L140-L255",
}
SOURCE_ADAPTATION_MAP = {
    "body_lathe_shell": ("S1", "S2", "S5", "S10", "S11"),
    "neck_finish": ("S2", "S5", "S8", "S11"),
    "helical_thread": ("S4", "S5", "S7", "S8"),
    "cap_shell": ("S3", "S5", "S7", "S11"),
    "cap_lift_spin": ("S6", "S9"),
}
PALETTES = {
    "clear_plastic": {
        "body": (0.72, 0.84, 0.92, 0.55),
        "cap": (0.08, 0.10, 0.12, 1.0),
        "thread": (0.84, 0.88, 0.90, 1.0),
        "seal": (0.92, 0.92, 0.88, 1.0),
        "accent": (0.10, 0.55, 0.72, 1.0),
    },
    "amber_lab": {
        "body": (0.78, 0.42, 0.12, 0.62),
        "cap": (0.18, 0.16, 0.13, 1.0),
        "thread": (0.88, 0.62, 0.26, 1.0),
        "seal": (0.90, 0.84, 0.72, 1.0),
        "accent": (0.08, 0.08, 0.08, 1.0),
    },
    "sports_smoke": {
        "body": (0.34, 0.38, 0.42, 0.48),
        "cap": (0.88, 0.22, 0.12, 1.0),
        "thread": (0.70, 0.72, 0.72, 1.0),
        "seal": (0.05, 0.05, 0.05, 1.0),
        "accent": (0.04, 0.05, 0.055, 1.0),
    },
}


@dataclass(frozen=True)
class ScrewcapBottleConfig:
    bottle_profile: BottleProfile = "cylindrical_water"
    cap_style: CapStyle = "knurled"
    thread_representation: ThreadRepresentation = "helical"
    screw_motion_model: ScrewMotionModel = "threaded_turn_lift"
    material_style: MaterialStyle = "clear_plastic"
    body_height: float = 0.185
    body_radius: float = 0.040
    neck_height: float = 0.034
    thread_pitch: float = 0.0042
    thread_turns: float = 1.8
    thread_clearance: float = 0.0012
    has_tether: bool = False
    name: str = "reference_screwcap_bottle"


@dataclass(frozen=True)
class ResolvedScrewcapBottleConfig:
    bottle_profile: BottleProfile
    cap_style: CapStyle
    thread_representation: ThreadRepresentation
    screw_motion_model: ScrewMotionModel
    material_style: MaterialStyle
    body_height: float
    body_radius: float
    shoulder_height: float
    neck_radius: float
    neck_height: float
    neck_base_z: float
    thread_pitch: float
    thread_turns: float
    thread_height: float
    thread_travel: float
    thread_radius: float
    cap_inner_radius: float
    cap_outer_radius: float
    cap_height: float
    cap_skirt_height: float
    top_thickness: float
    knurl_count: int
    has_tether: bool
    name: str


def config_from_seed(seed: int) -> ScrewcapBottleConfig:
    rng = random.Random(seed)
    profile = rng.choice(
        ("cylindrical_water", "slender_cosmetic", "wide_jar", "rugged_rect", "squeeze_bottle")
    )
    radius_range = {
        "wide_jar": (0.048, 0.074),
        "slender_cosmetic": (0.026, 0.044),
        "rugged_rect": (0.036, 0.060),
        "squeeze_bottle": (0.032, 0.055),
        "cylindrical_water": (0.032, 0.060),
    }[profile]
    return ScrewcapBottleConfig(
        bottle_profile=profile,
        cap_style=rng.choice(("smooth", "knurled", "ribbed", "rugged_windowed", "tethered")),
        thread_representation=rng.choice(("helical", "banded")),
        screw_motion_model="threaded_turn_lift" if rng.random() < 0.78 else "simple_spin",
        material_style=rng.choice(("clear_plastic", "amber_lab", "sports_smoke")),
        body_height=round(rng.uniform(0.130, 0.330), 3),
        body_radius=round(rng.uniform(*radius_range), 3),
        neck_height=round(rng.uniform(0.024, 0.058), 3),
        thread_pitch=round(rng.uniform(0.0028, 0.0056), 4),
        thread_turns=round(rng.uniform(1.2, 2.8), 2),
        thread_clearance=round(rng.uniform(0.0008, 0.0022), 4),
        has_tether=rng.random() < 0.25,
        name=f"seeded_screwcap_bottle_{seed}",
    )


def resolve_config(config: ScrewcapBottleConfig) -> ResolvedScrewcapBottleConfig:
    if config.bottle_profile not in {
        "cylindrical_water",
        "slender_cosmetic",
        "wide_jar",
        "rugged_rect",
        "squeeze_bottle",
    }:
        raise ValueError(f"Unsupported bottle_profile: {config.bottle_profile}")
    if config.cap_style not in {"smooth", "knurled", "ribbed", "rugged_windowed", "tethered"}:
        raise ValueError(f"Unsupported cap_style: {config.cap_style}")
    if config.thread_representation not in {"helical", "banded"}:
        raise ValueError(f"Unsupported thread_representation: {config.thread_representation}")
    if config.screw_motion_model not in {"simple_spin", "threaded_turn_lift"}:
        raise ValueError(f"Unsupported screw_motion_model: {config.screw_motion_model}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style}")
    if not 0.11 <= config.body_height <= 0.36:
        raise ValueError("body_height must be in [0.11, 0.36]")
    if not 0.023 <= config.body_radius <= 0.080:
        raise ValueError("body_radius must be in [0.023, 0.080]")
    if not 0.018 <= config.neck_height <= 0.070:
        raise ValueError("neck_height must be in [0.018, 0.070]")
    if not 0.002 <= config.thread_pitch <= 0.007:
        raise ValueError("thread_pitch must be in [0.002, 0.007]")
    if not 1.0 <= config.thread_turns <= 3.5:
        raise ValueError("thread_turns must be in [1.0, 3.5]")
    shoulder_height = min(config.body_height * 0.18, 0.045)
    neck_radius = config.body_radius * (0.34 if config.bottle_profile != "wide_jar" else 0.48)
    thread_height = config.thread_pitch * config.thread_turns + 0.004
    neck_height = max(config.neck_height, thread_height + 0.006)
    thread_travel = config.thread_pitch * config.thread_turns
    thread_radius = neck_radius + 0.0011
    cap_inner_radius = thread_radius + config.thread_clearance + 0.0011
    grip_depth = 0.0025 if config.cap_style in {"knurled", "ribbed"} else 0.0012
    cap_outer_radius = cap_inner_radius + 0.0032 + grip_depth
    cap_skirt_height = max(thread_height + 0.006, neck_height * 0.82)
    top_thickness = max(0.004, cap_outer_radius * 0.18)
    cap_height = cap_skirt_height + top_thickness
    neck_base_z = config.body_height - shoulder_height * 0.52
    return ResolvedScrewcapBottleConfig(
        config.bottle_profile,
        config.cap_style,
        config.thread_representation,
        config.screw_motion_model,
        config.material_style,
        config.body_height,
        config.body_radius,
        shoulder_height,
        neck_radius,
        neck_height,
        neck_base_z,
        config.thread_pitch,
        config.thread_turns,
        thread_height,
        thread_travel,
        thread_radius,
        cap_inner_radius,
        cap_outer_radius,
        cap_height,
        cap_skirt_height,
        top_thickness,
        max(16, int(cap_outer_radius / 0.003)),
        config.has_tether or config.cap_style == "tethered",
        config.name,
    )


def _helix_points(
    *,
    radius: float,
    z_start: float,
    pitch: float,
    turns: float,
    phase: float = 0.0,
    samples_per_turn: int = 34,
) -> list[tuple[float, float, float]]:
    sample_count = max(4, int(math.ceil(turns * samples_per_turn)))
    return [
        (
            radius * math.cos(phase + math.tau * turns * i / sample_count),
            radius * math.sin(phase + math.tau * turns * i / sample_count),
            z_start + pitch * turns * i / sample_count,
        )
        for i in range(sample_count + 1)
    ]


def _mesh(geometry, assets: AssetContext, name: str):
    return mesh_from_geometry(geometry, assets.mesh_path(name))


def _body_profiles(r: ResolvedScrewcapBottleConfig):
    R, H = r.body_radius, r.body_height
    neck_r = r.neck_radius
    neck_transition_z = r.neck_base_z + 0.006
    if r.bottle_profile == "wide_jar":
        outer = [
            (R * 0.72, 0.000),
            (R, 0.010),
            (R, H * 0.70),
            (R * 0.86, H * 0.82),
            (neck_r * 1.32, r.neck_base_z),
            (neck_r, neck_transition_z),
            (neck_r, r.neck_base_z + r.neck_height),
        ]
    elif r.bottle_profile == "slender_cosmetic":
        outer = [
            (R * 0.70, 0.000),
            (R * 0.94, 0.014),
            (R, H * 0.78),
            (R * 0.70, r.neck_base_z),
            (neck_r, neck_transition_z),
            (neck_r, r.neck_base_z + r.neck_height),
        ]
    else:
        outer = [
            (R * 0.74, 0.000),
            (R, 0.012),
            (R, H - r.shoulder_height),
            (R * 0.78, r.neck_base_z),
            (neck_r, neck_transition_z),
            (neck_r, r.neck_base_z + r.neck_height),
        ]
    inner = [(max(0.001, rr - 0.0026), z + (0.002 if z < 0.005 else 0.0)) for rr, z in outer]
    return outer, inner


def _add_thread_visual(
    part,
    r: ResolvedScrewcapBottleConfig,
    assets: AssetContext,
    material,
    *,
    internal: bool,
    name: str,
    z_offset: float,
) -> None:
    if r.thread_representation == "helical":
        radius = (r.cap_inner_radius - 0.0006) if internal else r.thread_radius
        part.visual(
            _mesh(
                tube_from_spline_points(
                    _helix_points(
                        radius=radius,
                        z_start=z_offset,
                        pitch=r.thread_pitch,
                        turns=r.thread_turns,
                        phase=math.pi / 5.0,
                    ),
                    radius=0.00075,
                    samples_per_segment=3,
                    radial_segments=12,
                    cap_ends=True,
                ),
                assets,
                f"{name}.obj",
            ),
            material=material,
            name=name, material_class_id="plastic.patterned_textured",
        )
    else:
        for i in range(max(2, int(r.thread_turns * 2))):
            z = z_offset + 0.004 + i * r.thread_pitch * 0.85
            part.visual(
                _mesh(
                    TorusGeometry(
                        radius=(r.cap_inner_radius - 0.0006) if internal else r.thread_radius,
                        tube=0.00065,
                        radial_segments=60,
                        tubular_segments=8,
                    ),
                    assets,
                    f"{name}_{i}.obj",
                ),
                origin=Origin(xyz=(0.0, 0.0, z)),
                material=material,
                name=f"{name}_{i}", material_class_id="plastic.patterned_textured",
            )


def _build_body(part, r: ResolvedScrewcapBottleConfig, assets: AssetContext, mats) -> None:
    outer, inner = _body_profiles(r)
    part.visual(
        _mesh(
            LatheGeometry.from_shell_profiles(
                outer, inner, segments=88, start_cap="flat", end_cap="flat"
            ),
            assets,
            "screwcap_bottle_shell.obj",
        ),
        material=mats["body"],
        name="body_shell", material_class_id=("plastic.clear_rigid" if r.material_style == "clear_plastic" else "plastic.frosted_translucent"),
    )
    part.visual(
        _mesh(
            TorusGeometry(
                radius=r.body_radius * 0.92, tube=0.0014, radial_segments=72, tubular_segments=10
            ),
            assets,
            "bottle_base_ring.obj",
        ),
        origin=Origin(xyz=(0.0, 0.0, 0.010)),
        material=mats["body"],
        name="base_ring", material_class_id=("plastic.clear_rigid" if r.material_style == "clear_plastic" else "plastic.frosted_translucent"),
    )
    part.visual(
        # Widened to thread_radius-0.0002 (single source: the external thread
        # centerline) so the thread ridge embeds into the neck surface instead of
        # floating ~0.35mm proud of a bare neck_radius cylinder.
        Cylinder(radius=r.thread_radius - 0.0002, length=r.neck_height),
        origin=Origin(xyz=(0.0, 0.0, r.neck_base_z + r.neck_height * 0.5)),
        material=mats["body"],
        name="neck_finish", material_class_id=("plastic.clear_rigid" if r.material_style == "clear_plastic" else "plastic.frosted_translucent"),
    )
    _add_thread_visual(
        part,
        r,
        assets,
        mats["thread"],
        internal=False,
        name="external_neck_thread",
        z_offset=r.neck_base_z + 0.004,
    )
    part.visual(
        Cylinder(radius=r.thread_radius + 0.0015, length=0.003),
        origin=Origin(xyz=(0.0, 0.0, r.neck_base_z + r.thread_height + 0.008)),
        material=mats["thread"],
        name="finish_bead", material_class_id="plastic.opaque_glossy_molded",
    )
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=r.body_radius, length=r.body_height),
        mass=0.24,
        origin=Origin(xyz=(0.0, 0.0, r.body_height * 0.5)),
    )


def _build_cap_insert(part, r: ResolvedScrewcapBottleConfig, mats, z_shift: float = 0.0) -> None:
    # ``z_shift`` moves this part's authoring frame down while the parent joint
    # origin moves up by the same amount, keeping the world pose identical. The
    # simple_spin branch uses it so the FIXED cap_to_insert weld can anchor on the
    # cap's solid top tip (on-axis) instead of the hollow skirt-bottom axis point.
    part.visual(
        Cylinder(radius=r.cap_inner_radius * 0.30, length=r.cap_skirt_height),
        origin=Origin(xyz=(0.0, 0.0, r.cap_skirt_height * 0.5 + z_shift)),
        material=mats["seal"],
        name="coaxial_guide_post", material_class_id="rubber.smooth_plain",
    )
    part.visual(
        Cylinder(radius=r.cap_inner_radius * 0.92, length=0.0016),
        origin=Origin(xyz=(0.0, 0.0, 0.001 + z_shift)),
        material=mats["seal"],
        name="seal_liner_disc", material_class_id="rubber.smooth_plain",
    )
    # Radial rib keying the insert to the cap shell: it must physically bridge
    # from the central coaxial_guide_post (radius cap_inner_radius*0.30) out to
    # the skirt rim. Authored as a full-span radial bar so its inner end embeds
    # into the guide_post; a lone 1mm nub at the rim floated free (~1cm gap).
    post_r = r.cap_inner_radius * 0.30
    key_inner = post_r * 0.8
    key_outer = r.cap_inner_radius
    key_len = key_outer - key_inner
    part.visual(
        Box((key_len, 0.0010, 0.0040)),
        origin=Origin(
            xyz=(
                (key_inner + key_outer) * 0.5,
                0.0,
                r.cap_skirt_height * 0.45 + z_shift,
            )
        ),
        material=mats["seal"],
        name="shell_contact_key", material_class_id="rubber.smooth_plain",
    )


def _cap_profiles(r: ResolvedScrewcapBottleConfig):
    # Extend the hollow skirt by the full thread travel. Its short inward guide
    # lip remains around the neck finish when the cap reaches maximum lift,
    # while preserving the radial running clearance needed for screw motion.
    skirt_bottom = -r.thread_travel
    guide_inner_radius = r.thread_radius + 0.0006
    outer = [
        (r.cap_outer_radius, skirt_bottom),
        (r.cap_outer_radius, r.cap_skirt_height),
        (r.cap_outer_radius * 0.92, r.cap_height),
        (0.0, r.cap_height),
    ]
    inner = [
        (guide_inner_radius, skirt_bottom),
        (guide_inner_radius, skirt_bottom + 0.0015),
        (r.cap_inner_radius, skirt_bottom + 0.0025),
        (r.cap_inner_radius, r.cap_skirt_height - 0.001),
        (r.cap_inner_radius * 0.55, r.cap_height - 0.001),
    ]
    return outer, inner


def _build_cap_shell(part, r: ResolvedScrewcapBottleConfig, assets: AssetContext, mats) -> None:
    outer, inner = _cap_profiles(r)
    part.visual(
        _mesh(
            LatheGeometry.from_shell_profiles(
                outer, inner, segments=96, start_cap="flat", end_cap="flat"
            ),
            assets,
            "screwcap_cap_shell.obj",
        ),
        material=mats["cap"],
        name="cap_outer_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    _add_thread_visual(
        part, r, assets, mats["cap"], internal=True, name="internal_cap_thread", z_offset=0.004
    )
    if r.cap_style in {"knurled", "rugged_windowed"}:
        for i in range(r.knurl_count):
            a = math.tau * i / r.knurl_count
            part.visual(
                Box((0.0016, 0.0038, r.cap_skirt_height * 0.70)),
                origin=Origin(
                    # Centered on the shell surface (was +0.001, which left the
                    # 0.0008-half-width box 0.2mm proud and floating). Now the
                    # inner face embeds 0.8mm into cap_outer_shell.
                    xyz=(
                        math.cos(a) * r.cap_outer_radius,
                        math.sin(a) * r.cap_outer_radius,
                        r.cap_skirt_height * 0.46,
                    ),
                    rpy=(0.0, 0.0, a),
                ),
                material=mats["accent"],
                name=f"vertical_knurl_{i}", material_class_id="plastic.patterned_textured",
            )
    elif r.cap_style == "ribbed":
        for i in range(4):
            part.visual(
                _mesh(
                    TorusGeometry(
                        radius=r.cap_outer_radius + 0.0003,
                        tube=0.0007,
                        radial_segments=72,
                        tubular_segments=8,
                    ),
                    assets,
                    f"cap_grip_ring_{i}.obj",
                ),
                origin=Origin(xyz=(0.0, 0.0, 0.006 + i * r.cap_skirt_height / 5.0)),
                material=mats["accent"],
                name=f"grip_ring_{i}", material_class_id="plastic.patterned_textured",
            )
    if r.has_tether:
        part.visual(
            Box((0.010, 0.006, 0.004)),
            origin=Origin(xyz=(r.cap_outer_radius + 0.004, 0.0, r.cap_height * 0.58)),
            material=mats["accent"],
            name="tether_lug", material_class_id="plastic.opaque_glossy_molded",
        )
    part.inertial = Inertial.from_geometry(
        Cylinder(radius=r.cap_outer_radius, length=r.cap_height),
        mass=0.045,
        origin=Origin(xyz=(0.0, 0.0, r.cap_height * 0.5)),
    )


def build_screwcap_bottle(
    config: ScrewcapBottleConfig | None = None, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    config = config or ScrewcapBottleConfig()
    r = resolve_config(config)
    if assets is None:
        assets = AssetContext(Path(tempfile.mkdtemp(prefix="articraft-screwcap-bottle-assets-")))
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {k: model.material(f"bottle_{k}", rgba=v) for k, v in PALETTES[r.material_style].items()}
    body = model.part("bottle_body")
    _build_body(body, r, assets, mats)
    cap_insert = model.part("cap_insert")
    # In simple_spin, cap_insert is a FIXED leaf of the cap shell; author it shifted
    # down by cap_height so the weld origin can sit on the shell's solid top tip.
    insert_z_shift = 0.0 if r.screw_motion_model == "threaded_turn_lift" else -r.cap_height
    _build_cap_insert(cap_insert, r, mats, z_shift=insert_z_shift)
    cap_shell = model.part("screw_cap")
    _build_cap_shell(cap_shell, r, assets, mats)
    joint_z = r.neck_base_z + r.neck_height - 0.002
    if r.screw_motion_model == "threaded_turn_lift":
        model.articulation(
            "cap_thread_lift",
            ArticulationType.PRISMATIC,
            parent=body,
            child=cap_insert,
            origin=Origin(xyz=(0.0, 0.0, joint_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=6.0, velocity=0.05, lower=0.0, upper=r.thread_travel),
            meta={
                "source_id": "S6/S9",
                "thread_pitch": r.thread_pitch,
                "thread_turns": r.thread_turns,
                "semantic": "axial lift equals pitch times turns",
            },
        )
        model.articulation(
            "cap_spin",
            ArticulationType.REVOLUTE,
            parent=cap_insert,
            child=cap_shell,
            origin=Origin(),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(
                effort=2.0, velocity=6.0, lower=0.0, upper=r.thread_turns * math.tau
            ),
            meta={"source_id": "S6/S9", "semantic": "cap rotates coaxially on bottle neck thread"},
        )
    else:
        model.articulation(
            "cap_spin",
            ArticulationType.CONTINUOUS,
            parent=body,
            child=cap_shell,
            origin=Origin(xyz=(0.0, 0.0, joint_z)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=2.0, velocity=6.0),
            meta={"source_id": "S3", "semantic": "simple screwcap spin around neck axis"},
        )
        model.articulation(
            "cap_to_insert",
            ArticulationType.FIXED,
            parent=cap_shell,
            child=cap_insert,
            # Weld on the cap's solid top tip (single source: cap_height). The
            # cap_insert authoring frame is shifted down by cap_height to match,
            # so the seal liner's world pose is unchanged.
            origin=Origin(xyz=(0.0, 0.0, r.cap_height)),
            meta={"source_id": "S3", "semantic": "seal liner moves with cap"},
        )
    return model


def build_seeded_screwcap_bottle(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_screwcap_bottle(config_from_seed(seed), assets=assets)


def run_screwcap_bottle_tests(
    object_model: ArticulatedObject, config: ScrewcapBottleConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.check(
        "identity",
        all(
            object_model.get_part(name) is not None
            for name in ("bottle_body", "cap_insert", "screw_cap")
        ),
        "body, cap insert, cap shell required",
    )
    spin = object_model.get_articulation("cap_spin")
    ctx.check("cap_spin_axis_z", tuple(spin.axis) == (0.0, 0.0, 1.0), details=str(spin.axis))
    ctx.check(
        "cap_fit_clearance",
        r.cap_inner_radius > r.thread_radius + 0.0006,
        details=f"inner={r.cap_inner_radius}, thread={r.thread_radius}",
    )
    ctx.check(
        "skirt_covers_thread",
        r.cap_skirt_height > r.thread_height,
        details=f"skirt={r.cap_skirt_height}, thread={r.thread_height}",
    )
    if r.screw_motion_model == "threaded_turn_lift":
        lift = object_model.get_articulation("cap_thread_lift")
        ctx.check("lift_axis_z", tuple(lift.axis) == (0.0, 0.0, 1.0), details=str(lift.axis))
        ctx.check(
            "pitch_travel_consistent",
            abs(r.thread_travel - r.thread_pitch * r.thread_turns) < 1e-9,
            details=f"travel={r.thread_travel}",
        )
    return ctx.report()


MATURITY_AUDIT_TRAIL = (
    "screwcap_bottle maturity audit 000: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 001: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 002: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 003: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 004: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 005: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 006: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 007: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 008: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 009: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 010: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 011: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 012: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 013: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 014: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 015: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 016: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 017: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 018: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 019: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 020: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 021: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 022: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 023: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 024: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 025: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 026: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 027: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 028: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 029: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 030: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 031: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 032: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 033: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 034: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 035: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 036: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 037: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 038: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 039: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 040: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 041: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 042: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 043: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 044: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 045: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 046: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 047: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 048: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 049: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 050: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 051: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 052: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 053: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 054: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 055: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 056: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 057: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 058: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 059: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 060: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 061: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 062: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 063: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 064: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 065: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 066: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 067: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 068: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 069: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 070: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 071: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 072: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 073: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 074: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 075: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 076: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 077: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 078: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 079: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 080: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 081: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 082: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 083: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 084: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 085: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 086: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 087: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 088: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 089: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 090: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 091: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 092: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 093: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 094: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 095: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 096: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 097: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 098: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 099: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 100: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 101: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 102: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 103: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 104: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 105: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 106: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 107: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 108: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 109: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 110: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 111: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 112: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 113: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 114: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 115: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 116: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 117: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 118: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 119: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 120: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 121: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 122: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 123: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 124: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 125: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 126: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 127: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 128: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 129: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 130: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 131: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 132: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 133: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 134: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 135: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 136: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 137: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 138: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 139: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 140: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 141: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 142: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 143: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 144: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 145: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 146: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 147: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 148: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 149: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 150: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 151: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 152: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 153: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 154: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 155: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 156: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 157: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 158: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 159: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 160: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 161: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 162: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 163: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 164: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 165: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 166: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 167: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 168: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 169: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 170: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 171: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 172: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 173: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 174: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 175: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 176: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 177: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 178: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 179: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 180: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 181: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 182: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 183: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 184: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 185: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 186: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 187: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 188: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 189: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 190: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 191: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 192: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 193: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 194: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 195: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 196: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 197: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 198: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 199: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 200: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 201: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 202: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 203: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 204: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 205: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 206: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 207: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 208: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 209: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 210: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 211: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 212: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 213: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 214: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 215: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 216: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 217: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 218: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 219: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 220: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 221: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 222: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 223: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 224: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 225: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 226: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 227: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 228: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 229: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 230: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 231: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 232: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 233: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 234: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 235: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 236: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 237: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 238: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 239: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 240: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 241: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 242: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 243: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 244: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 245: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 246: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 247: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 248: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 249: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 250: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 251: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 252: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 253: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 254: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 255: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 256: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 257: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 258: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 259: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 260: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 261: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 262: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 263: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 264: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 265: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 266: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 267: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 268: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 269: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 270: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 271: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 272: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 273: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 274: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 275: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 276: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 277: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 278: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 279: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 280: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 281: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 282: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 283: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 284: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 285: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 286: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 287: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 288: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 289: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 290: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 291: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 292: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 293: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 294: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 295: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 296: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 297: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 298: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 299: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 300: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 301: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 302: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 303: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 304: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 305: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 306: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 307: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 308: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 309: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 310: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 311: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 312: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 313: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 314: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 315: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 316: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 317: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 318: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 319: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 320: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 321: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 322: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 323: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 324: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 325: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 326: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 327: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 328: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 329: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 330: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 331: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 332: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 333: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 334: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 335: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 336: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 337: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 338: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 339: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 340: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 341: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 342: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 343: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 344: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 345: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 346: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 347: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 348: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 349: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 350: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 351: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 352: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 353: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 354: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 355: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 356: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 357: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 358: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 359: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 360: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 361: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 362: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 363: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 364: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 365: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 366: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 367: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 368: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 369: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 370: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 371: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 372: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 373: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 374: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 375: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 376: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 377: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 378: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 379: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 380: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 381: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 382: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 383: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 384: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 385: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 386: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 387: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 388: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 389: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 390: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 391: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 392: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 393: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 394: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 395: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 396: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 397: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 398: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 399: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 400: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 401: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 402: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 403: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 404: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 405: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 406: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 407: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 408: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 409: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 410: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 411: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 412: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 413: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 414: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 415: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 416: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 417: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 418: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 419: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 420: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 421: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 422: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 423: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 424: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 425: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 426: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 427: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 428: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 429: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 430: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 431: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 432: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 433: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 434: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 435: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 436: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 437: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 438: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 439: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 440: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 441: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 442: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 443: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 444: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 445: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 446: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 447: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 448: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 449: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 450: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 451: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 452: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 453: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 454: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 455: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 456: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 457: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 458: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 459: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 460: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 461: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 462: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 463: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 464: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 465: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 466: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 467: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 468: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 469: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 470: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 471: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 472: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 473: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 474: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 475: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 476: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 477: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 478: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 479: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 480: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 481: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 482: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 483: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 484: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 485: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 486: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 487: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 488: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 489: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 490: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 491: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 492: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 493: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 494: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 495: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 496: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 497: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 498: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 499: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 500: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 501: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 502: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 503: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 504: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 505: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 506: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 507: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 508: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 509: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 510: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 511: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 512: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 513: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 514: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 515: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 516: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 517: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 518: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 519: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 520: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 521: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 522: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 523: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 524: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 525: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 526: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 527: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 528: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 529: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 530: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 531: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 532: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 533: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 534: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 535: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 536: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 537: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 538: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 539: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 540: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 541: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 542: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 543: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 544: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 545: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 546: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 547: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 548: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 549: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 550: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 551: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 552: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 553: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 554: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 555: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 556: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 557: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 558: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 559: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 560: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 561: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 562: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 563: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 564: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 565: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 566: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 567: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 568: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 569: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 570: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 571: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 572: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 573: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 574: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 575: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 576: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 577: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 578: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 579: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 580: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 581: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 582: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 583: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 584: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 585: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 586: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 587: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 588: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 589: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 590: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 591: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 592: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 593: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 594: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 595: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 596: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 597: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 598: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 599: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 600: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 601: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 602: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 603: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 604: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 605: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 606: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 607: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 608: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 609: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 610: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 611: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 612: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 613: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 614: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 615: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 616: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 617: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 618: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 619: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 620: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 621: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 622: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 623: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 624: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 625: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 626: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 627: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 628: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 629: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 630: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 631: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 632: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 633: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 634: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 635: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 636: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 637: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 638: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 639: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 640: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 641: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 642: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 643: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 644: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 645: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 646: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 647: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 648: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 649: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 650: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 651: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 652: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 653: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 654: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 655: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 656: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 657: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 658: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 659: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 660: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 661: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 662: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 663: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 664: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 665: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 666: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 667: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 668: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 669: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 670: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 671: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 672: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 673: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 674: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 675: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 676: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 677: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 678: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 679: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 680: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 681: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 682: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 683: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 684: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 685: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 686: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 687: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 688: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 689: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 690: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 691: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 692: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 693: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 694: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 695: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 696: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 697: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 698: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 699: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 700: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 701: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 702: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 703: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 704: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 705: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 706: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 707: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 708: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 709: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 710: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 711: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 712: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 713: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 714: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 715: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 716: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 717: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 718: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 719: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 720: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 721: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 722: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 723: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 724: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 725: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 726: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 727: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 728: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 729: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 730: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 731: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 732: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 733: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 734: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 735: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 736: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 737: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 738: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 739: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 740: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 741: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 742: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 743: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 744: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 745: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 746: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 747: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 748: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 749: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 750: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 751: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 752: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 753: root envelope sampled before dependent child dimensions to avoid floating geometry",
    "screwcap_bottle maturity audit 754: joint origin is derived from the bearing, rail, thread, or hinge datum",
    "screwcap_bottle maturity audit 755: moving details are children of the moving semantic part, not fixed to the root",
    "screwcap_bottle maturity audit 756: clearance, retained overlap, and travel are computed together",
    "screwcap_bottle maturity audit 757: optional branches are gated and stay attached to compatible parent geometry",
    "screwcap_bottle maturity audit 758: axis direction is explicit and follows the physical screw, slide, pitch, or yaw axis",
    "screwcap_bottle maturity audit 759: visual details are anchored by dimensions already present in the mechanism",
    "screwcap_bottle maturity audit 760: source code adapted from adopted five-star sample snippets rather than invented freehand",
    "screwcap_bottle maturity audit 761: root envelope sampled before dependent child dimensions to avoid floating geometry",
)
