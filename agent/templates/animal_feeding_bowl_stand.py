# SPDX-License-Identifier: Apache-2.0

"""Animal feeding bowl stand — modular procedural template.

Category identity: an elevated stand/frame that raises one or more OPEN pet
feeding bowls off the floor to eating height, holding each bowl in a support
ring / socket / cutout, with at least one real non-fixed joint (height slide,
bowl tilt, leg fold, or bowl lift-out).

Canonical spec: ``articraft_template_authoring/specs_modular_v1/animal_feeding_bowl_stand.md``

Slots (exported via ``slot_choices_for_seed``):

* ``base_skeleton`` — h_skid_frame / cross_pedestal / tripod_pedestal /
  disc_pedestal / fold_pedestal / diner_frame  (① skeleton + ③ form family)
* ``bowl_coupling`` — fixed_seat / tilt_cradle / liftout  (② joint type)
* ``bowl_multiplicity`` — n1 / n2 / n3  (side-by-side bowl count)

Two honest body-form families from the 5-star pool:
  A) planar box-frame chain: H-skid frame + square post + sliding ring carriage
     carrying side-by-side bowls (source records 001 / bowls_n3 / probe_twin_tilt).
  B) volumetric pedestal-column: radial/tripod/disc/foldable base + hollow sleeve
     + telescoping socket holder carrying one central bowl (records 002 / base_*).
Plus a rigid diner panel with prismatic lift-out bowls.

``config_from_seed`` is procedural for every seed (no seed=0 special case).
Support style (square ring-carriage vs round ribbed-socket vs cutout panel) is
base-family-internal (derived from the ③ form), not a separate slot.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Literal

from sdk import (
    AppearanceOnlySpec,
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    CapsuleGeometry,
    Cylinder,
    CylinderGeometry,
    ExtrudeWithHolesGeometry,
    Inertial,
    KnobBore,
    KnobGeometry,
    KnobGrip,
    LatheGeometry,
    MeshGeometry,
    MotionLimits,
    Origin,
    Part,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_geometry,
    rounded_rect_profile,
    tube_from_spline_points,
)

from agent.templates._modular import mount_fixed

__modular__ = True

# ---------------------------------------------------------------------------
# Slot enums
# ---------------------------------------------------------------------------
BaseSkeleton = Literal[
    "h_skid_frame",
    "cross_pedestal",
    "tripod_pedestal",
    "disc_pedestal",
    "fold_pedestal",
    "diner_frame",
]
BowlCoupling = Literal["fixed_seat", "tilt_cradle", "liftout"]
MaterialStyle = Literal["powder_black", "graphite_plastic", "walnut_frame", "chrome_white"]

BASE_SKELETONS: tuple[BaseSkeleton, ...] = (
    "h_skid_frame",
    "cross_pedestal",
    "tripod_pedestal",
    "disc_pedestal",
    "fold_pedestal",
    "diner_frame",
)
BOWL_COUPLINGS: tuple[BowlCoupling, ...] = ("fixed_seat", "tilt_cradle", "liftout")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "powder_black",
    "graphite_plastic",
    "walnut_frame",
    "chrome_white",
)

PEDESTAL_BASES = ("cross_pedestal", "tripod_pedestal", "disc_pedestal", "fold_pedestal")
FRAME_BASES = ("h_skid_frame",)
DINER_BASES = ("diner_frame",)

# Material keys used by every module (registered per palette).
PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "powder_black": {
        "frame": (0.02, 0.022, 0.020, 1.0),
        "plastic": (0.05, 0.052, 0.055, 1.0),
        "rubber": (0.006, 0.006, 0.005, 1.0),
        "stainless": (0.82, 0.82, 0.78, 1.0),
        "accent": (0.23, 0.25, 0.24, 1.0),
        "enamel": (0.02, 0.30, 0.72, 1.0),
        "white": (0.95, 0.97, 0.98, 1.0),
    },
    "graphite_plastic": {
        "frame": (0.11, 0.12, 0.13, 1.0),
        "plastic": (0.015, 0.017, 0.018, 1.0),
        "rubber": (0.025, 0.028, 0.030, 1.0),
        "stainless": (0.78, 0.80, 0.83, 1.0),
        "accent": (0.30, 0.32, 0.34, 1.0),
        "enamel": (0.05, 0.34, 0.60, 1.0),
        "white": (0.94, 0.95, 0.96, 1.0),
    },
    "walnut_frame": {
        "frame": (0.36, 0.22, 0.13, 1.0),
        "plastic": (0.28, 0.18, 0.11, 1.0),
        "rubber": (0.015, 0.015, 0.014, 1.0),
        "stainless": (0.80, 0.80, 0.76, 1.0),
        "accent": (0.20, 0.13, 0.08, 1.0),
        "enamel": (0.10, 0.36, 0.42, 1.0),
        "white": (0.95, 0.93, 0.86, 1.0),
    },
    "chrome_white": {
        "frame": (0.80, 0.81, 0.83, 1.0),
        "plastic": (0.90, 0.91, 0.90, 1.0),
        "rubber": (0.20, 0.21, 0.22, 1.0),
        "stainless": (0.86, 0.87, 0.88, 1.0),
        "accent": (0.55, 0.57, 0.60, 1.0),
        "enamel": (0.70, 0.16, 0.18, 1.0),
        "white": (0.97, 0.98, 0.99, 1.0),
    },
}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AnimalFeedingBowlStandConfig:
    base_skeleton: BaseSkeleton | None = None
    bowl_coupling: BowlCoupling | None = None
    n_bowls: int = 1
    material_style: MaterialStyle = "powder_black"
    base_span_scale: float = 1.0
    slide_travel_scale: float = 1.0
    tilt_upper_deg: float = 25.0
    name: str = "animal_feeding_bowl_stand"


@dataclass(frozen=True)
class ResolvedAnimalFeedingBowlStandConfig:
    base_skeleton: BaseSkeleton
    bowl_coupling: BowlCoupling
    n_bowls: int
    material_style: MaterialStyle
    base_span_scale: float
    slide_travel_scale: float
    tilt_upper: float  # radians
    bowl_spacing: float
    bowl_x: tuple[float, ...]
    slide_lower: float
    slide_upper: float
    palette: dict[str, tuple[float, float, float, float]]
    name: str


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def config_from_seed(seed: int) -> AnimalFeedingBowlStandConfig:
    rng = random.Random(seed)
    base = rng.choice(BASE_SKELETONS)
    coupling = rng.choice(BOWL_COUPLINGS)
    # N weighted toward small counts (product domain [1,3]).
    n = rng.choices((1, 2, 3), weights=(5, 3, 2), k=1)[0]
    return AnimalFeedingBowlStandConfig(
        base_skeleton=base,
        bowl_coupling=coupling,
        n_bowls=n,
        material_style=rng.choice(MATERIAL_STYLES),
        base_span_scale=round(rng.uniform(0.90, 1.15), 4),
        slide_travel_scale=round(rng.uniform(0.90, 1.10), 4),
        tilt_upper_deg=round(rng.uniform(16.0, 27.0), 3),
        name=f"seeded_animal_feeding_bowl_stand_{seed}",
    )


def resolve_config(
    config: AnimalFeedingBowlStandConfig,
) -> ResolvedAnimalFeedingBowlStandConfig:
    base = config.base_skeleton or "cross_pedestal"
    coupling = config.bowl_coupling or "fixed_seat"
    n = int(config.n_bowls)

    if base not in BASE_SKELETONS:
        raise ValueError(f"Unsupported base_skeleton: {base!r}")
    if coupling not in BOWL_COUPLINGS:
        raise ValueError(f"Unsupported bowl_coupling: {coupling!r}")
    if config.material_style not in PALETTES:
        raise ValueError(f"Unsupported material_style: {config.material_style!r}")

    # --- compatibility gating (spec §9) ---
    if base in DINER_BASES:
        coupling = "liftout"
        n = _clamp(n, 1, 3)
    elif base == "fold_pedestal":
        # folding legs already dominate the sampled-pose budget: keep a single
        # fixed central bowl so the fold joint is the mechanism under test.
        coupling = "fixed_seat"
        n = 1
    elif base in PEDESTAL_BASES:
        # central socket holder carries one bowl directly over the pedestal post;
        # tilting a bowl above the post dips into the socket, so pedestals use a
        # fixed central seat (tilt lives on the frame family where the trunnion
        # axis is clear of any under-bowl obstruction).
        coupling = "fixed_seat"
        n = 1
    else:  # frame family (side-by-side rings)
        if coupling == "liftout":
            coupling = "fixed_seat"
        n = int(_clamp(n, 1, 3))

    n = int(n)

    span = _clamp(config.base_span_scale, 0.85, 1.20)
    tscale = _clamp(config.slide_travel_scale, 0.85, 1.15)
    tilt_upper = math.radians(_clamp(config.tilt_upper_deg, 14.0, 30.0))

    bowl_spacing = _clamp(0.32 * span, 0.28, 0.37)
    if base in DINER_BASES:
        bowl_x = tuple((i - (n - 1) / 2.0) * bowl_spacing for i in range(n))
    elif base in FRAME_BASES:
        bowl_x = tuple((i - (n - 1) / 2.0) * bowl_spacing for i in range(n))
    else:  # pedestal central
        bowl_x = (0.0,)

    if base in FRAME_BASES:
        slide_lower = -0.110 * tscale
        slide_upper = 0.080 * tscale
    elif base in PEDESTAL_BASES:
        slide_lower = 0.0
        slide_upper = 0.090 * tscale
    else:  # diner lift-out
        slide_lower = 0.0
        slide_upper = 0.120

    return ResolvedAnimalFeedingBowlStandConfig(
        base_skeleton=base,
        bowl_coupling=coupling,
        n_bowls=n,
        material_style=config.material_style,
        base_span_scale=span,
        slide_travel_scale=tscale,
        tilt_upper=tilt_upper,
        bowl_spacing=bowl_spacing,
        bowl_x=bowl_x,
        slide_lower=slide_lower,
        slide_upper=slide_upper,
        palette=dict(PALETTES[config.material_style]),
        name=config.name,
    )


# ---------------------------------------------------------------------------
# Geometry helpers (ported from the 5-star source records)
# ---------------------------------------------------------------------------
def _box_shim(box: Box) -> MeshGeometry:
    """Box → MeshGeometry so radial ribs can merge into one connected ring."""
    sx, sy, sz = box.size
    x, y, z = sx / 2.0, sy / 2.0, sz / 2.0
    vertices = [
        (-x, -y, -z), (x, -y, -z), (x, y, -z), (-x, y, -z),
        (-x, -y, z), (x, -y, z), (x, y, z), (-x, y, z),
    ]
    faces = [
        (0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6),
        (0, 4, 5), (0, 5, 1), (1, 5, 6), (1, 6, 2),
        (2, 6, 7), (2, 7, 3), (3, 7, 4), (3, 4, 0),
    ]
    return MeshGeometry(vertices=list(vertices), faces=list(faces))


def _small_bowl_cup(name: str):
    """Thin open stainless bowl (frame / diner). Wide hollow so the upright post
    can nest through a centered bowl (bowls_n3 inner profile)."""
    outer = [
        (0.036, -0.090), (0.050, -0.084), (0.066, -0.065), (0.080, -0.034),
        (0.087, -0.006), (0.088, 0.004), (0.090, 0.0052), (0.095, 0.00942),
    ]
    inner = [
        (0.028, -0.078), (0.044, -0.073), (0.060, -0.056), (0.074, -0.028),
        (0.081, -0.004), (0.083, 0.004), (0.089, 0.00942),
    ]
    return mesh_from_geometry(
        LatheGeometry.from_shell_profiles(outer, inner, segments=72, lip_samples=5),
        name,
    )


def _big_bowl_shell(name: str):
    """Larger stainless bowl shell for the pedestal ribbed ring (record 002)."""
    outer_profile = [
        (0.048, 0.000), (0.070, 0.006), (0.094, 0.022),
        (0.124, 0.066), (0.146, 0.104), (0.152, 0.112),
    ]
    inner_profile = [
        (0.030, 0.010), (0.064, 0.017), (0.087, 0.031),
        (0.115, 0.071), (0.139, 0.101),
    ]
    bowl = LatheGeometry.from_shell_profiles(
        outer_profile, inner_profile, segments=96,
        start_cap="round", end_cap="round", lip_samples=8,
    )
    bowl.merge(
        TorusGeometry(radius=0.148, tube=0.008, radial_segments=16, tubular_segments=96)
        .translate(0, 0, 0.106)
    )
    return mesh_from_geometry(bowl, name)


def _conical_band(name: str):
    """Blue enamel sleeve derived from the big-bowl outer profile per-z (④)."""
    band = LatheGeometry.from_shell_profiles(
        [(0.085, 0.020), (0.118, 0.056), (0.145, 0.092)],
        [(0.082, 0.022), (0.115, 0.058), (0.141, 0.090)],
        segments=96, start_cap="flat", end_cap="flat",
    )
    return mesh_from_geometry(band, name)


def _ribbed_ring(name: str):
    """Circular support ring with grip ribs (record 002)."""
    base = TorusGeometry(radius=0.150, tube=0.012, radial_segments=16, tubular_segments=96)
    base.merge(CylinderGeometry(radius=0.140, height=0.010, radial_segments=72).translate(0.0, 0.0, -0.010))
    rib = Box((0.010, 0.014, 0.026))
    rib_geom = MeshGeometry()
    for index in range(36):
        angle = index * math.tau / 36.0
        r = 0.142
        rib_geom.merge(
            _box_shim(rib).rotate_z(angle).translate(r * math.cos(angle), r * math.sin(angle), -0.014)
        )
    base.merge(rib_geom)
    return mesh_from_geometry(base, name)


def _tube_shell(*, outer_radius: float, inner_radius: float, z_min: float, z_max: float, name: str):
    wall = LatheGeometry.from_shell_profiles(
        [(outer_radius, z_min), (outer_radius, z_max)],
        [(inner_radius, z_min + 0.002), (inner_radius, z_max - 0.002)],
        segments=72, start_cap="flat", end_cap="flat",
    )
    return mesh_from_geometry(wall, name)


def _weighted_disc(name: str):
    disc = CylinderGeometry(radius=0.155, height=0.024, radial_segments=72)
    disc.merge(TorusGeometry(radius=0.151, tube=0.005, radial_segments=12, tubular_segments=72).translate(0, 0, 0.012))
    disc.merge(TorusGeometry(radius=0.151, tube=0.005, radial_segments=12, tubular_segments=72).translate(0, 0, -0.012))
    return mesh_from_geometry(disc, name)


def _circle_profile(cx: float, cy: float, r: float, segments: int = 40) -> list[tuple[float, float]]:
    return [
        (cx + r * math.cos(2.0 * math.pi * i / segments), cy + r * math.sin(2.0 * math.pi * i / segments))
        for i in range(segments)
    ]


def _tab_spline(bx: float, ring_r: float = 0.096) -> list[tuple[float, float, float]]:
    collar_hw = 0.043
    collar_hd = 0.043
    sx = max(-collar_hw, min(collar_hw, bx))
    sy = collar_hd
    if abs(bx) > 0.01:
        approach = math.radians(50.0)
        sign_x = 1.0 if bx < 0 else -1.0
        dx = sign_x * math.cos(approach)
        dy = math.sin(approach)
    else:
        dx, dy = 0.0, 1.0
    ex = bx + ring_r * dx
    ey = ring_r * dy
    mx = 0.5 * (sx + ex)
    my = 0.5 * (sy + ey) + 0.005
    return [(sx, sy, 0.0), (mx, my, 0.0), (ex, ey, 0.0)]


def _knob_meshes():
    large = mesh_from_geometry(
        KnobGeometry(
            0.052, 0.026, body_style="lobed", base_diameter=0.034, top_diameter=0.046,
            crown_radius=0.0015, grip=KnobGrip(style="ribbed", count=8, depth=0.0012),
            bore=KnobBore(style="round", diameter=0.009),
        ),
        "large_clamp_knob",
    )
    small = mesh_from_geometry(
        KnobGeometry(
            0.032, 0.020, body_style="lobed", base_diameter=0.022, top_diameter=0.030,
            crown_radius=0.0010, grip=KnobGrip(style="ribbed", count=6, depth=0.0009),
            bore=KnobBore(style="round", diameter=0.006),
        ),
        "small_clamp_knob",
    )
    return large, small


# ---------------------------------------------------------------------------
# Bowl emitters (small = frame/diner rim 0.099; big = pedestal shell 0.152)
# ---------------------------------------------------------------------------
def _emit_small_bowl(model: ArticulatedObject, part_name: str, *, add_trunnions: bool = False) -> Part:
    bowl = model.part(part_name)
    bowl.visual(_small_bowl_cup(f"{part_name}_cup"), material="stainless", name="cup", material_class_id="metal.stainless_matte")
    bowl.visual(
        mesh_from_geometry(TorusGeometry(0.099, 0.0050, radial_segments=18, tubular_segments=72), f"{part_name}_rim"),
        origin=Origin(xyz=(0.0, 0.0, 0.00942)),
        material="stainless",
        name="rim", material_class_id="metal.stainless_matte",
    )
    # Base disc overlaps the cup inner wall so the bowl part stays one connected
    # island (cup inner bottom radius ≈ 0.028 at z=-0.078).
    bowl.visual(
        Cylinder(radius=0.030, length=0.016),
        origin=Origin(xyz=(0.0, 0.0, -0.078)),
        material="stainless",
        name="flat_bottom", material_class_id="metal.stainless_matte",
    )
    if add_trunnions:
        for stub_idx, dy in enumerate((-0.094, 0.094)):
            bowl.visual(
                Cylinder(radius=0.005, length=0.024),
                origin=Origin(xyz=(0.0, dy, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
                material="stainless",
                name=f"trunnion_{stub_idx}", material_class_id="metal.stainless_matte",
            )
    bowl.inertial = Inertial.from_geometry(
        Cylinder(radius=0.10, length=0.10), mass=0.35, origin=Origin(xyz=(0, 0, -0.04))
    )
    return bowl


def _emit_big_bowl(model: ArticulatedObject, part_name: str) -> Part:
    bowl = model.part(part_name)
    bowl.visual(_big_bowl_shell(f"{part_name}_shell"), material="stainless", name="stainless_bowl_shell", material_class_id="metal.stainless_matte")
    # Solid bowl base disc: covers the central axis at bowl-local (0,0,0) so the
    # FIXED seat joint's child anchor lands on real geometry (origin-proximity).
    bowl.visual(
        Cylinder(radius=0.045, length=0.012),
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        material="stainless",
        name="base_disc", material_class_id="metal.stainless_matte",
    )
    bowl.visual(_conical_band(f"{part_name}_band"), material="enamel", name="blue_outer_band", material_class_id="metal.paint_coated")
    paw_specs = [
        (-0.020, -0.119, 0.061, 0.013), (0.000, -0.128, 0.078, 0.007),
        (-0.016, -0.130, 0.082, 0.005), (0.016, -0.130, 0.082, 0.005),
        (-0.030, -0.124, 0.073, 0.0045), (0.030, -0.124, 0.073, 0.0045),
    ]
    for index, (x, y, z, radius) in enumerate(paw_specs):
        bowl.visual(
            Cylinder(radius=radius, length=0.010),
            origin=Origin(xyz=(x, y, z), rpy=(-math.pi / 2.0, 0.0, 0.0)),
            material="white",
            name=f"paw_mark_{index}", appearance_only=AppearanceOnlySpec(kind="overlay"),
        )
    bowl.inertial = Inertial.from_geometry(
        Cylinder(radius=0.15, length=0.11), mass=0.45, origin=Origin(xyz=(0, 0, 0.055))
    )
    return bowl


# ---------------------------------------------------------------------------
# Frame family (h_skid_frame) — record 001 / bowls_n3 / probe_twin_tilt
# ---------------------------------------------------------------------------
def _build_frame(model: ArticulatedObject, r: ResolvedAnimalFeedingBowlStandConfig) -> None:
    bowl_x = r.bowl_x
    n = r.n_bowls
    foot_x_outer = max((abs(x) for x in bowl_x), default=0.0) + 0.080
    foot_x_outer = max(foot_x_outer, 0.230)
    crossbar_w = 2.0 * foot_x_outer + 0.050
    foot_positions = sorted(set((-foot_x_outer, foot_x_outer)) | ({0.0} if n >= 3 else set()))

    base = model.part("base_frame")
    for fi, fx in enumerate(foot_positions):
        base.visual(
            Box((0.050, 0.540, 0.036)),
            origin=Origin(xyz=(fx, 0.0, 0.035)),
            material="frame",
            name=f"foot_{fi}", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"),
        )
    base.visual(
        Box((crossbar_w, 0.050, 0.036)),
        origin=Origin(xyz=(0.0, 0.0, 0.035)),
        material="frame",
        name="base_crossbar", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"),
    )
    base.visual(
        Box((0.036, 0.036, 0.420)),
        origin=Origin(xyz=(0.0, 0.0, 0.258)),
        material="frame",
        name="upright_post", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"),
    )
    pad_idx = 0
    for fx in foot_positions:
        for fy in (-0.250, 0.250):
            base.visual(
                Box((0.070, 0.090, 0.014)),
                origin=Origin(xyz=(fx, fy, 0.010)),
                material="rubber",
                name=f"rubber_pad_{pad_idx}", material_class_id="rubber.smooth_plain",
            )
            pad_idx += 1
    base.inertial = Inertial.from_geometry(
        Box((crossbar_w, 0.54, 0.42)), mass=3.0, origin=Origin(xyz=(0, 0, 0.20))
    )

    tilt = r.bowl_coupling == "tilt_cradle"

    carriage = model.part("height_carriage")
    for name, size, xyz in (
        ("collar_front", (0.098, 0.025, 0.086), (0.0, 0.0305, 0.0)),
        ("collar_back", (0.098, 0.025, 0.086), (0.0, -0.0305, 0.0)),
        ("collar_side_0", (0.025, 0.048, 0.086), (-0.0305, 0.0, 0.0)),
        ("collar_side_1", (0.025, 0.048, 0.086), (0.0305, 0.0, 0.0)),
    ):
        carriage.visual(Box(size), origin=Origin(xyz=xyz), material="accent", name=name, material_class_id="plastic.opaque_generic")

    ring_mesh = mesh_from_geometry(
        TorusGeometry(0.096, 0.0048, radial_segments=20, tubular_segments=72), "bowl_holder_ring"
    )
    for idx, bx in enumerate(bowl_x):
        carriage.visual(ring_mesh, origin=Origin(xyz=(bx, 0.0, 0.0)), material="frame", name=f"ring_{idx}", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"))
    for idx, bx in enumerate(bowl_x):
        carriage.visual(
            mesh_from_geometry(
                tube_from_spline_points(_tab_spline(bx), radius=0.0045, samples_per_segment=8, radial_segments=12),
                f"tab_{idx}_tube",
            ),
            material="frame",
            name=f"tab_{idx}", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"),
        )
    carriage.visual(
        Box((0.020, 0.032, 0.040)),
        origin=Origin(xyz=(0.0, 0.059, 0.030)),
        material="frame",
        name="clamp_backbone", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"),
    )
    if tilt:
        # Trunnion yoke brackets flanking each bowl (probe_twin_tilt L203-210).
        for idx, bx in enumerate(bowl_x):
            for bracket_idx, dy in enumerate((-0.108, 0.108)):
                carriage.visual(
                    Box((0.014, 0.016, 0.050)),
                    origin=Origin(xyz=(bx, dy, 0.025)),
                    material="frame",
                    name=f"yoke_{idx}_{bracket_idx}", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"),
                )
    carriage.inertial = Inertial.from_geometry(
        Box((crossbar_w, 0.20, 0.10)), mass=0.6, origin=Origin(xyz=(0, 0, 0.0))
    )

    model.articulation(
        "base_to_carriage",
        ArticulationType.PRISMATIC,
        parent=base,
        child=carriage,
        origin=Origin(xyz=(0.0, 0.0, 0.295)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=80.0, velocity=0.08, lower=r.slide_lower, upper=r.slide_upper),
    )

    # Bowls
    for idx, bx in enumerate(bowl_x):
        bowl = _emit_small_bowl(model, f"bowl_{idx}", add_trunnions=tilt)
        if tilt:
            model.articulation(
                f"carriage_to_bowl_{idx}",
                ArticulationType.REVOLUTE,
                parent=carriage,
                child=bowl,
                origin=Origin(xyz=(bx, 0.0, 0.0)),
                axis=(0.0, 1.0, 0.0),
                motion_limits=MotionLimits(effort=3.0, velocity=1.5, lower=0.0, upper=r.tilt_upper),
            )
        else:
            # FIXED seat pinned at the rim-on-ring contact (front point) so the
            # joint origin sits on real geometry on BOTH sides; mount_fixed
            # rebases the bowl so its rim front lands on the ring front.
            mount_fixed(
                model,
                joint_name=f"carriage_to_bowl_{idx}",
                parent="height_carriage",
                child=f"bowl_{idx}",
                parent_anchor=(bx, 0.096, 0.003),
                child_anchor=(0.0, 0.099, 0.00942),
            )

    # Clamp knobs (CONTINUOUS ② control, family A) — raised above bowl rim.
    # Only on fixed seats: a tilting bowl's rim would sweep into the knobs.
    if tilt:
        return
    large_knob, small_knob = _knob_meshes()
    knob_0 = model.part("clamp_knob_0")
    knob_0.visual(
        Cylinder(radius=0.006, length=0.030),
        origin=Origin(xyz=(0.0, -0.015, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="frame",
        name="threaded_stem", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"),
    )
    knob_0.visual(
        large_knob,
        origin=Origin(xyz=(0.0, -0.041, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material="frame",
        name="hand_grip", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"),
    )
    knob_0.inertial = Inertial.from_geometry(
        Cylinder(radius=0.05, length=0.03), mass=0.05, origin=Origin(xyz=(0, -0.03, 0))
    )
    model.articulation(
        "carriage_to_knob_0",
        ArticulationType.CONTINUOUS,
        parent=carriage,
        child=knob_0,
        origin=Origin(xyz=(0.0, -0.043, 0.040)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=4.0),
    )
    knob_1 = model.part("clamp_knob_1")
    knob_1.visual(
        Cylinder(radius=0.0045, length=0.024),
        origin=Origin(xyz=(0.0, 0.012, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material="frame",
        name="threaded_stem", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"),
    )
    knob_1.visual(
        small_knob,
        origin=Origin(xyz=(0.0, 0.034, 0.0), rpy=(-math.pi / 2.0, 0.0, 0.0)),
        material="frame",
        name="hand_grip", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"),
    )
    knob_1.inertial = Inertial.from_geometry(
        Cylinder(radius=0.03, length=0.024), mass=0.03, origin=Origin(xyz=(0, 0.03, 0))
    )
    model.articulation(
        "carriage_to_knob_1",
        ArticulationType.CONTINUOUS,
        parent=carriage,
        child=knob_1,
        origin=Origin(xyz=(0.0, 0.049, 0.040)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=0.8, velocity=4.0),
    )


# ---------------------------------------------------------------------------
# Pedestal family — records 002 / base_tripod / base_disc / base_fold
# ---------------------------------------------------------------------------
def _emit_pedestal_base(model: ArticulatedObject, r: ResolvedAnimalFeedingBowlStandConfig) -> Part:
    base = model.part("base")
    span = r.base_span_scale
    kind = r.base_skeleton

    if kind == "cross_pedestal":
        foot_mesh = mesh_from_geometry(
            CapsuleGeometry(radius=0.032, length=0.260, radial_segments=20), "rounded_cross_foot"
        )
        for index, angle in enumerate((0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)):
            base.visual(
                foot_mesh,
                origin=Origin(xyz=(0.130 * span * math.cos(angle), 0.130 * span * math.sin(angle), 0.032),
                              rpy=(0.0, math.pi / 2.0, angle)),
                material="plastic",
                name=f"foot_{index}", material_class_id="plastic.opaque_generic",
            )
            base.visual(
                Box((0.095, 0.052, 0.020)),
                origin=Origin(xyz=(0.270 * span * math.cos(angle), 0.270 * span * math.sin(angle), 0.020),
                              rpy=(0.0, 0.0, angle)),
                material="plastic",
                name=f"toe_pad_{index}", material_class_id="plastic.opaque_generic",
            )
        sleeve_zmin, hub_z = 0.058, 0.045
        collar_z = (0.062, 0.250, 0.418)
    elif kind == "tripod_pedestal":
        num_legs = 3
        splay = math.radians(35)
        leg_tube_r = 0.013
        leg_length = 0.157
        leg_top_r, leg_top_z, leg_bot_z = 0.053, 0.135, 0.006
        leg_bot_r = leg_top_r + (leg_top_z - leg_bot_z) * math.tan(splay)
        leg_r_mid = (leg_top_r + leg_bot_r) / 2.0 * span
        leg_z_mid = (leg_top_z + leg_bot_z) / 2.0
        leg_mesh = mesh_from_geometry(CylinderGeometry(radius=leg_tube_r, height=leg_length, radial_segments=24), "tripod_leg")
        pad_mesh = mesh_from_geometry(CylinderGeometry(radius=0.020, height=0.010, radial_segments=24), "tripod_foot_pad")
        for index in range(num_legs):
            angle = index * math.tau / num_legs
            base.visual(
                leg_mesh,
                origin=Origin(xyz=(leg_r_mid * math.cos(angle), leg_r_mid * math.sin(angle), leg_z_mid),
                              rpy=(0.0, -splay, angle)),
                material="plastic",
                name=f"leg_{index}", material_class_id="plastic.opaque_generic",
            )
            base.visual(
                pad_mesh,
                origin=Origin(xyz=(leg_bot_r * span * math.cos(angle), leg_bot_r * span * math.sin(angle), 0.005)),
                material="rubber",
                name=f"foot_pad_{index}", material_class_id="rubber.smooth_plain",
            )
        # Hub radius sized so the splayed leg tops stay embedded across the full
        # clamped base_span_scale range [0.85, 1.20]: at span 1.20 the leg-top
        # tube inner reach is ~0.060, so a 0.066 hub keeps ~6mm of embed (legs
        # drift radially outward as span scales leg_r_mid; a 0.055 hub detached
        # them at span>=1.15 → disconnected-island failures on seeds 36/395).
        base.visual(
            Cylinder(radius=0.066, length=0.040),
            origin=Origin(xyz=(0.0, 0.0, 0.150)),
            material="plastic",
            name="central_hub", material_class_id="plastic.opaque_generic",
        )
        sleeve_zmin, hub_z = 0.160, 0.150
        collar_z = (0.168, 0.290, 0.418)
    elif kind == "disc_pedestal":
        base.visual(_weighted_disc("weighted_disc_base"), origin=Origin(xyz=(0.0, 0.0, 0.017)), material="plastic", name="weighted_disc_base", material_class_id="plastic.opaque_generic")
        base.visual(Cylinder(radius=0.135, length=0.010), origin=Origin(xyz=(0.0, 0.0, 0.005)), material="rubber", name="anti_slip_pad", material_class_id="rubber.smooth_plain")
        sleeve_zmin, hub_z = 0.058, 0.045
        collar_z = (0.062, 0.250, 0.418)
    else:  # fold_pedestal
        hinge_barrel_mesh = mesh_from_geometry(CylinderGeometry(radius=0.010, height=0.038, radial_segments=24), "hinge_barrel")
        for index, angle in enumerate((0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)):
            base.visual(
                hinge_barrel_mesh,
                origin=Origin(xyz=(0.090 * math.cos(angle), 0.090 * math.sin(angle), 0.030),
                              rpy=(0.0, math.pi / 2.0, angle + math.pi / 2.0)),
                material="plastic",
                name=f"hinge_barrel_{index}", material_class_id="plastic.opaque_generic",
            )
        sleeve_zmin, hub_z = 0.058, 0.045
        collar_z = (0.062, 0.250, 0.418)

    if kind != "tripod_pedestal":
        base.visual(Cylinder(radius=0.090, length=0.050), origin=Origin(xyz=(0.0, 0.0, hub_z)), material="plastic", name="central_hub", material_class_id="plastic.opaque_generic")

    base.visual(
        _tube_shell(outer_radius=0.047, inner_radius=0.036, z_min=sleeve_zmin, z_max=0.420, name="hollow_pedestal_sleeve"),
        material="plastic",
        name="hollow_pedestal_sleeve", material_class_id="plastic.opaque_generic",
    )
    collar_mesh = mesh_from_geometry(TorusGeometry(radius=0.047, tube=0.007, radial_segments=14, tubular_segments=72), "pedestal_collar")
    for z, vn in zip(collar_z, ("lower_lock_collar", "height_lock_collar", "upper_socket_lip")):
        base.visual(collar_mesh, origin=Origin(xyz=(0.0, 0.0, z)), material="plastic", name=vn, material_class_id="plastic.opaque_generic")
    base.inertial = Inertial.from_geometry(
        Cylinder(radius=0.20, length=0.44), mass=2.0, origin=Origin(xyz=(0, 0, 0.18))
    )

    # Folding legs as separate REVOLUTE parts (base_fold L298-334).
    if kind == "fold_pedestal":
        leg_member_mesh = mesh_from_geometry(CapsuleGeometry(radius=0.018, length=0.220, radial_segments=16), "folding_leg_member")
        for index, angle in enumerate((0.0, math.pi / 2.0, math.pi, 3.0 * math.pi / 2.0)):
            leg = model.part(f"leg_{index}")
            leg.visual(
                leg_member_mesh,
                origin=Origin(xyz=(0.110 * math.cos(angle), 0.110 * math.sin(angle), -0.012),
                              rpy=(0.0, math.pi / 2.0, angle)),
                material="rubber",
                name=f"leg_member_{index}", material_class_id="rubber.smooth_plain",
            )
            leg.visual(
                Box((0.016, 0.044, 0.060)),
                origin=Origin(xyz=(0.190 * math.cos(angle), 0.190 * math.sin(angle), -0.030),
                              rpy=(0.0, math.pi / 2.0, angle)),
                material="rubber",
                name=f"toe_pad_{index}", material_class_id="rubber.smooth_plain",
            )
            leg.inertial = Inertial.from_geometry(
                Box((0.22, 0.05, 0.06)), mass=0.15,
                origin=Origin(xyz=(0.13 * math.cos(angle), 0.13 * math.sin(angle), -0.02)),
            )
            model.articulation(
                f"hub_to_leg_{index}",
                ArticulationType.REVOLUTE,
                parent=base,
                child=leg,
                origin=Origin(xyz=(0.090 * math.cos(angle), 0.090 * math.sin(angle), 0.030)),
                axis=(math.sin(angle), -math.cos(angle), 0.0),
                motion_limits=MotionLimits(effort=5.0, velocity=2.0, lower=0.0, upper=1.55),
            )
    return base


def _build_pedestal(model: ArticulatedObject, r: ResolvedAnimalFeedingBowlStandConfig) -> None:
    base = _emit_pedestal_base(model, r)
    tilt = r.bowl_coupling == "tilt_cradle"

    holder = model.part("bowl_holder")
    holder.visual(Cylinder(radius=0.036, length=0.340), origin=Origin(xyz=(0.0, 0.0, 0.060)), material="plastic", name="sliding_inner_post", material_class_id="plastic.opaque_generic")
    holder.visual(Cylinder(radius=0.056, length=0.055), origin=Origin(xyz=(0.0, 0.0, 0.228)), material="plastic", name="top_socket", material_class_id="plastic.opaque_generic")
    holder.visual(
        mesh_from_geometry(TorusGeometry(radius=0.064, tube=0.010, radial_segments=14, tubular_segments=72), "top_socket_lip"),
        origin=Origin(xyz=(0.0, 0.0, 0.256)),
        material="plastic",
        name="top_socket_lip", material_class_id="plastic.opaque_generic",
    )
    if not tilt:
        holder.visual(_ribbed_ring("ribbed_bowl_support_ring"), origin=Origin(xyz=(0.0, 0.0, 0.268)), material="plastic", name="ribbed_support_ring", material_class_id="plastic.opaque_generic")
        for index, angle in enumerate((math.radians(18), math.radians(162), math.radians(198), math.radians(342))):
            holder.visual(Box((0.084, 0.022, 0.018)), origin=Origin(xyz=(0.160 * math.cos(angle), 0.160 * math.sin(angle), 0.274), rpy=(0.0, 0.0, angle)), material="plastic", name=f"radial_bracket_{index}", material_class_id="plastic.opaque_generic")
            holder.visual(Box((0.048, 0.026, 0.105)), origin=Origin(xyz=(0.176 * math.cos(angle), 0.176 * math.sin(angle), 0.335), rpy=(0.0, 0.0, angle)), material="plastic", name=f"upright_clip_{index}", material_class_id="plastic.opaque_generic")
            holder.visual(Box((0.052, 0.036, 0.014)), origin=Origin(xyz=(0.180 * math.cos(angle), 0.180 * math.sin(angle), 0.392), rpy=(0.0, 0.0, angle)), material="plastic", name=f"clip_cap_{index}", material_class_id="plastic.opaque_generic")
    holder.inertial = Inertial.from_geometry(Cylinder(radius=0.18, length=0.46), mass=0.8, origin=Origin(xyz=(0, 0, 0.15)))

    model.articulation(
        "height_slide",
        ArticulationType.PRISMATIC,
        parent=base,
        child=holder,
        origin=Origin(xyz=(0.0, 0.0, 0.340)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=30.0, velocity=0.12, lower=r.slide_lower, upper=r.slide_upper),
    )

    if tilt:
        # Tilt yoke carries the ring + clips (bowl_tilt L233-276); bowl fixed to yoke.
        yoke = model.part("tilt_yoke")
        yoke.visual(_ribbed_ring("ribbed_bowl_support_ring"), origin=Origin(xyz=(0.0, 0.0, 0.0)), material="plastic", name="ribbed_support_ring", material_class_id="plastic.opaque_generic")
        for side, y_sign in enumerate((1.0, -1.0)):
            yoke.visual(Box((0.016, 0.020, 0.050)), origin=Origin(xyz=(0.0, y_sign * 0.090, -0.020)), material="plastic", name=f"yoke_ear_{side}", material_class_id="plastic.opaque_generic")
        for index, angle in enumerate((math.radians(18), math.radians(162), math.radians(198), math.radians(342))):
            yoke.visual(Box((0.084, 0.022, 0.018)), origin=Origin(xyz=(0.160 * math.cos(angle), 0.160 * math.sin(angle), 0.006), rpy=(0.0, 0.0, angle)), material="plastic", name=f"radial_bracket_{index}", material_class_id="plastic.opaque_generic")
            yoke.visual(Box((0.048, 0.026, 0.105)), origin=Origin(xyz=(0.176 * math.cos(angle), 0.176 * math.sin(angle), 0.067), rpy=(0.0, 0.0, angle)), material="plastic", name=f"upright_clip_{index}", material_class_id="plastic.opaque_generic")
            yoke.visual(Box((0.052, 0.036, 0.014)), origin=Origin(xyz=(0.180 * math.cos(angle), 0.180 * math.sin(angle), 0.124), rpy=(0.0, 0.0, angle)), material="plastic", name=f"clip_cap_{index}", material_class_id="plastic.opaque_generic")
        yoke.inertial = Inertial.from_geometry(Cylinder(radius=0.20, length=0.15), mass=0.3, origin=Origin(xyz=(0, 0, 0.05)))
        model.articulation(
            "holder_to_yoke",
            ArticulationType.REVOLUTE,
            parent=holder,
            child=yoke,
            origin=Origin(xyz=(0.0, 0.0, 0.268)),
            axis=(0.0, 1.0, 0.0),
            motion_limits=MotionLimits(effort=5.0, velocity=1.0, lower=0.0, upper=r.tilt_upper),
        )
        bowl = _emit_big_bowl(model, "bowl_0")
        model.articulation("yoke_to_bowl", ArticulationType.FIXED, parent=yoke, child=bowl, origin=Origin(xyz=(0.0, 0.0, 0.002)))
    else:
        bowl = _emit_big_bowl(model, "bowl_0")
        model.articulation("holder_to_bowl", ArticulationType.FIXED, parent=holder, child=bowl, origin=Origin(xyz=(0.0, 0.0, 0.270)))


# ---------------------------------------------------------------------------
# Diner family (diner_frame) — record diner_platform
# ---------------------------------------------------------------------------
def _build_diner(model: ArticulatedObject, r: ResolvedAnimalFeedingBowlStandConfig) -> None:
    bowl_x = r.bowl_x
    panel_t = 0.022
    panel_z = 0.300
    leg_w = 0.036
    leg_h = panel_z - panel_t / 2.0
    cutout_r = 0.093
    corner_r = 0.012
    panel_w = max(0.30, 2.0 * (max(abs(x) for x in bowl_x) + cutout_r + 0.020))
    panel_d = 0.260

    base = model.part("base_frame")
    outer = rounded_rect_profile(panel_w, panel_d, corner_r, corner_segments=6)
    holes = [_circle_profile(bx, 0.0, cutout_r, segments=40) for bx in bowl_x]
    panel_mesh = mesh_from_geometry(ExtrudeWithHolesGeometry(outer, holes, panel_t, cap=True, center=True), "top_panel")
    base.visual(panel_mesh, origin=Origin(xyz=(0.0, 0.0, panel_z)), material="frame", name="top_panel", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"))

    leg_positions = [
        (-panel_w / 2.0 + leg_w / 2.0 + corner_r, -panel_d / 2.0 + leg_w / 2.0 + corner_r),
        (-panel_w / 2.0 + leg_w / 2.0 + corner_r, panel_d / 2.0 - leg_w / 2.0 - corner_r),
        (panel_w / 2.0 - leg_w / 2.0 - corner_r, -panel_d / 2.0 + leg_w / 2.0 + corner_r),
        (panel_w / 2.0 - leg_w / 2.0 - corner_r, panel_d / 2.0 - leg_w / 2.0 - corner_r),
    ]
    for i, (lx, ly) in enumerate(leg_positions):
        base.visual(Box((leg_w, leg_w, leg_h)), origin=Origin(xyz=(lx, ly, leg_h / 2.0)), material="frame", name=f"leg_{i}", material_class_id=("metal.chrome_polished" if r.material_style in {"powder_black", "walnut_frame", "chrome_white"} else "plastic.opaque_generic"))
    pad_t = 0.006
    for i, (lx, ly) in enumerate(leg_positions):
        base.visual(Box((leg_w + 0.004, leg_w + 0.004, pad_t)), origin=Origin(xyz=(lx, ly, pad_t / 2.0)), material="rubber", name=f"rubber_pad_{i}", material_class_id="rubber.smooth_plain")
    base.inertial = Inertial.from_geometry(Box((panel_w, panel_d, panel_z)), mass=3.0, origin=Origin(xyz=(0, 0, panel_z * 0.5)))

    panel_top_z = panel_z + panel_t / 2.0
    rim_bottom_offset = 0.00942 - 0.005
    for idx, bx in enumerate(bowl_x):
        bowl = _emit_small_bowl(model, f"bowl_{idx}")
        model.articulation(
            f"base_to_bowl_{idx}",
            ArticulationType.PRISMATIC,
            parent=base,
            child=bowl,
            origin=Origin(xyz=(bx, 0.0, panel_top_z - rim_bottom_offset)),
            axis=(0.0, 0.0, 1.0),
            motion_limits=MotionLimits(effort=10.0, velocity=0.15, lower=r.slide_lower, upper=r.slide_upper),
        )


# ---------------------------------------------------------------------------
# Build entry point
# ---------------------------------------------------------------------------
def build_animal_feeding_bowl_stand(
    config: AnimalFeedingBowlStandConfig, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name="animal_feeding_bowl_stand", assets=assets)
    for key, rgba in r.palette.items():
        model.material(key, rgba=rgba)

    if r.base_skeleton in FRAME_BASES:
        _build_frame(model, r)
    elif r.base_skeleton in DINER_BASES:
        _build_diner(model, r)
    else:
        _build_pedestal(model, r)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_animal_feeding_bowl_stand(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_animal_feeding_bowl_stand(config_from_seed(seed), assets=assets)


def slot_choices_for_config(r: ResolvedAnimalFeedingBowlStandConfig) -> list[tuple[str, str]]:
    return [
        ("base_skeleton", r.base_skeleton),
        ("bowl_coupling", r.bowl_coupling),
        ("bowl_multiplicity", f"n{r.n_bowls}"),
    ]


def slot_choices_for_seed(seed: int) -> list[tuple[str, str]]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def _run_frame_tests(ctx: TestContext, model: ArticulatedObject, r: ResolvedAnimalFeedingBowlStandConfig) -> None:
    base = model.get_part("base_frame")
    carriage = model.get_part("height_carriage")
    height_joint = model.get_articulation("base_to_carriage")
    tilt = r.bowl_coupling == "tilt_cradle"
    bowl_x = r.bowl_x

    ctx.allow_overlap("clamp_knob_1", "height_carriage", elem_a="threaded_stem", elem_b="clamp_backbone",
                      reason="Small clamp knob stem is intentionally screwed through the collar backbone.")

    n_tabs = len(bowl_x)
    for idx, bx in enumerate(bowl_x):
        bowl_name = f"bowl_{idx}"
        # Rim/cup embeds into its cradle ring and the welded tabs terminating there.
        for elem in ("rim", "cup"):
            ctx.allow_overlap(bowl_name, "height_carriage", elem_a=elem, elem_b=f"ring_{idx}",
                              reason="Bowl rim/cup seats a few mm into its cradle ring.")
            for tab_idx in range(n_tabs):
                ctx.allow_overlap(bowl_name, "height_carriage", elem_a=elem, elem_b=f"tab_{tab_idx}",
                                  reason="Welded tab terminates at the ring under the bowl rim/cup.")
        # Center bowl (odd N) nests the upright post + sliding collar.
        if abs(bx) < 0.05:
            for elem in ("cup", "rim", "flat_bottom"):
                ctx.allow_overlap(bowl_name, "base_frame", elem_a=elem, elem_b="upright_post",
                                  reason="Center bowl cavity nests the upright post passing through it.")
                for cn in ("collar_front", "collar_back", "collar_side_0", "collar_side_1"):
                    ctx.allow_overlap(bowl_name, "height_carriage", elem_a=elem, elem_b=cn,
                                      reason="Center bowl cavity nests the sliding collar under it.")
        if tilt:
            for stub_idx in range(2):
                ctx.allow_overlap(bowl_name, "height_carriage", elem_a=f"trunnion_{stub_idx}", elem_b=f"yoke_{idx}_{stub_idx}",
                                  reason="Trunnion pivot stub captured in the yoke bracket bearing for tilt.")
                ctx.allow_overlap(bowl_name, "height_carriage", elem_a=f"trunnion_{stub_idx}", elem_b=f"ring_{idx}",
                                  reason="Trunnion pin passes through the holder ring bore toward the yoke bracket.")
                for tab_idx in range(n_tabs):
                    ctx.allow_overlap(bowl_name, "height_carriage", elem_a=f"trunnion_{stub_idx}", elem_b=f"tab_{tab_idx}",
                                      reason="Trunnion pin passes over the welded ring tab.")

    # Seating checks
    for idx in range(len(bowl_x)):
        ctx.expect_overlap(f"bowl_{idx}", carriage, axes="xy", min_overlap=0.10, elem_a="rim", elem_b=f"ring_{idx}",
                           name=f"bowl {idx} rim seated over holder ring")
    if len(bowl_x) >= 2:
        for i in range(len(bowl_x) - 1):
            ctx.expect_origin_distance(f"bowl_{i}", f"bowl_{i+1}", axes="x", min_dist=0.24, max_dist=0.40,
                                       name=f"bowls {i},{i+1} side-by-side spacing")

    # Height slide raises bowls (derived threshold from actual travel).
    travel = r.slide_upper - r.slide_lower
    low_z = None
    with ctx.pose({height_joint: r.slide_lower}):
        low_z = ctx.part_world_position(model.get_part("bowl_0"))[2]
    with ctx.pose({height_joint: r.slide_upper}):
        high_z = ctx.part_world_position(model.get_part("bowl_0"))[2]
    ctx.check("height adjustment raises the bowls", high_z > low_z + 0.5 * travel,
              details=f"low_z={low_z:.3f}, high_z={high_z:.3f}, travel={travel:.3f}")
    for q in (r.slide_lower, 0.0, r.slide_upper):
        with ctx.pose({height_joint: q}):
            ctx.expect_overlap(carriage, base, axes="z", min_overlap=0.05, elem_a="collar_front", elem_b="upright_post",
                               name=f"collar engaged on post at q={q:.3f}")

    if tilt:
        tilt_j = model.get_articulation("carriage_to_bowl_0")
        rest_rim = ctx.part_element_world_aabb(model.get_part("bowl_0"), elem="rim")
        with ctx.pose({tilt_j: r.tilt_upper}):
            tilted_rim = ctx.part_element_world_aabb(model.get_part("bowl_0"), elem="rim")
        ctx.check("bowl tilt moves the rim", rest_rim is not None and tilted_rim is not None
                  and abs(tilted_rim[0][2] - rest_rim[0][2]) > 0.004,
                  details=f"rest={rest_rim[0][2] if rest_rim else None}, tilt={tilted_rim[0][2] if tilted_rim else None}")


def _run_pedestal_tests(ctx: TestContext, model: ArticulatedObject, r: ResolvedAnimalFeedingBowlStandConfig) -> None:
    base = model.get_part("base")
    holder = model.get_part("bowl_holder")
    slide = model.get_articulation("height_slide")
    tilt = r.bowl_coupling == "tilt_cradle"
    seat = model.get_part("tilt_yoke") if tilt else holder
    seat_name = "tilt_yoke" if tilt else "bowl_holder"

    ctx.allow_overlap(base, holder, elem_a="hollow_pedestal_sleeve", elem_b="sliding_inner_post",
                      reason="Inner height post retained inside the pedestal sleeve.")
    if tilt:
        ctx.allow_overlap(holder, seat, elem_a="top_socket_lip", elem_b="ribbed_support_ring",
                          reason="Ribbed support ring sits atop the socket lip as the tilt pivot seat.")
    ctx.allow_overlap(seat_name, "bowl_0", elem_a="ribbed_support_ring", elem_b="stainless_bowl_shell",
                      reason="Removable bowl seated a few mm into the molded support ring.")
    for index in range(4):
        ctx.allow_overlap("bowl_0", seat_name, elem_a="stainless_bowl_shell", elem_b=f"upright_clip_{index}",
                          reason="Molded upright clip lightly captures the bowl wall.")

    if r.base_skeleton == "fold_pedestal":
        for index in range(4):
            ctx.allow_overlap(base, f"leg_{index}", elem_a="central_hub", elem_b=f"leg_member_{index}",
                              reason="Leg member end wraps the hub hinge at the folding pivot.")
            ctx.allow_overlap(base, f"leg_{index}", elem_a=f"hinge_barrel_{index}", elem_b=f"leg_member_{index}",
                              reason="Hinge barrel captured inside the leg member end at the pivot.")

    ctx.expect_overlap(seat_name, "bowl_0", axes="xy", min_overlap=0.18, elem_a="ribbed_support_ring", elem_b="stainless_bowl_shell",
                       name="bowl seated in circular support ring")
    ctx.expect_within(holder, base, axes="xy", margin=0.006, inner_elem="sliding_inner_post", outer_elem="hollow_pedestal_sleeve",
                      name="telescoping post centered in sleeve")

    travel = r.slide_upper - r.slide_lower
    rest_pos = ctx.part_world_position(holder)
    with ctx.pose({slide: r.slide_upper}):
        ctx.expect_overlap(holder, base, axes="z", min_overlap=0.045, elem_a="sliding_inner_post", elem_b="hollow_pedestal_sleeve",
                           name="extended post retained in sleeve")
        ext_pos = ctx.part_world_position(holder)
    ctx.check("height slide raises the holder", ext_pos[2] > rest_pos[2] + 0.5 * travel,
              details=f"rest={rest_pos[2]:.3f}, ext={ext_pos[2]:.3f}, travel={travel:.3f}")

    if tilt:
        tilt_j = model.get_articulation("holder_to_yoke")
        rest_aabb = ctx.part_world_aabb(model.get_part("bowl_0"))
        with ctx.pose({tilt_j: r.tilt_upper}):
            tilt_aabb = ctx.part_world_aabb(model.get_part("bowl_0"))
        ctx.check("tilt yoke angles the bowl", rest_aabb is not None and tilt_aabb is not None
                  and abs(tilt_aabb[1][2] - rest_aabb[1][2]) > 0.015,
                  details=f"rest_zmax={rest_aabb[1][2]:.3f}, tilt_zmax={tilt_aabb[1][2]:.3f}")

    if r.base_skeleton == "fold_pedestal":
        for index in range(4):
            leg = model.get_part(f"leg_{index}")
            hinge = model.get_articulation(f"hub_to_leg_{index}")
            deployed = ctx.part_world_aabb(leg)
            with ctx.pose({hinge: 1.50}):
                folded = ctx.part_world_aabb(leg)
            ctx.check(f"leg_{index} folds upward", deployed is not None and folded is not None
                      and folded[1][2] > deployed[1][2] + 0.03,
                      details=f"deployed_zmax={deployed[1][2]:.3f}, folded_zmax={folded[1][2]:.3f}")


def _run_diner_tests(ctx: TestContext, model: ArticulatedObject, r: ResolvedAnimalFeedingBowlStandConfig) -> None:
    base = model.get_part("base_frame")
    bowl_x = r.bowl_x
    ctx.expect_gap(base, base, axis="z", min_gap=0.20, positive_elem="top_panel", negative_elem="rubber_pad_0",
                   name="top panel stands well above the floor (elevated feeder)")
    for idx in range(len(bowl_x)):
        ctx.allow_overlap("base_frame", f"bowl_{idx}", elem_a="top_panel", elem_b="cup",
                          reason="Bowl cup drops through the panel cutout, retained by the rim on the panel.")
        ctx.allow_overlap("base_frame", f"bowl_{idx}", elem_a="top_panel", elem_b="flat_bottom",
                          reason="Bowl base disc passes through the panel cutout during lift-out.")
        ctx.expect_overlap(f"bowl_{idx}", base, axes="xy", min_overlap=0.006, elem_a="rim", elem_b="top_panel",
                           name=f"bowl_{idx} rim rests on panel around cutout")
    joint_0 = model.get_articulation("base_to_bowl_0")
    rest_z = ctx.part_world_position(model.get_part("bowl_0"))[2]
    with ctx.pose({joint_0: r.slide_upper}):
        lifted_z = ctx.part_world_position(model.get_part("bowl_0"))[2]
    ctx.check("prismatic lift-out raises the bowl", lifted_z > rest_z + 0.5 * (r.slide_upper - r.slide_lower),
              details=f"rest_z={rest_z:.3f}, lifted_z={lifted_z:.3f}")


def run_animal_feeding_bowl_stand_tests(
    object_model: ArticulatedObject, config: AnimalFeedingBowlStandConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    ctx.check("slot_choices match config", object_model.meta.get("slot_choices") == slot_choices_for_config(r))

    if r.base_skeleton in FRAME_BASES:
        _run_frame_tests(ctx, object_model, r)
    elif r.base_skeleton in DINER_BASES:
        _run_diner_tests(ctx, object_model, r)
    else:
        _run_pedestal_tests(ctx, object_model, r)

    # Rule 5: full-travel collision sweep across every mechanism.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)
    return ctx.report()


__all__ = [
    "AnimalFeedingBowlStandConfig",
    "ResolvedAnimalFeedingBowlStandConfig",
    "build_animal_feeding_bowl_stand",
    "build_seeded_animal_feeding_bowl_stand",
    "config_from_seed",
    "resolve_config",
    "run_animal_feeding_bowl_stand_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
]
