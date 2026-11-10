# SPDX-License-Identifier: Apache-2.0

"""Clipboard modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Stationary_Clipboard.md`` and the
``picture/Stationary/Clipboard`` 5-star sample pool (1 parent + 10 single-axis
fork variants: hangloop / togglelever / foldback / sideclamp / clamps2 /
clamps3 / roundedtop / foldingcover / archring / wirebail).

Structure (pattern = ``mixed``): a single root ``board`` panel carries a set of
**parallel children** plus a **clamp multiplicity** axis. The core mechanism is
always a board + at least one paper clamp whose moving jaw/arch/bail is a real
REVOLUTE:

  * ``board_form`` (3): rounded-corner rectangle (portrait), arched-top
    rounded-head (portrait), or landscape side-mount panel. The form picks the
    board outline AND the clamp mounting edge/axis together. (parent S0 /
    roundedtop / sideclamp)
  * ``clamp_mechanism`` (4): torsion spring-jaw lever, over-center toggle cam
    lever, single bent wire bail, or split wire arch ring-binder. Each emits a
    FIXED metal base part + a REVOLUTE moving gripper part. (parent / togglelever
    / wirebail / archring)
  * ``hang_hardware`` (2, optional): none, or a swivel ring captured in an eyelet
    boss on the board edge (REVOLUTE about the eyelet axis). (hangloop)
  * ``cover`` (2, optional): none, or a hinged front cover panel folding over the
    board along one long side edge (REVOLUTE). (foldingcover)
  * clamp **multiplicity**: an ``n_clamps`` row of identical clamp assemblies
    (each its own FIXED base + REVOLUTE moving part) evenly spaced along the
    mounting edge. Encoded in slot_choices as ``clamps_{n}`` so the
    ``module_topology_diversity`` gate sees distinct clamp topologies. (clean
    ``for i in range(n)`` emission from clamps2 / clamps3)

Rivet heads / decorative plates are inlined as parent visuals (no FIXED
decoration parts). All articulated children use captured-pin / seated geometry,
so their joints omit ``MatingContract`` (grandfathered) and rely on the flat
articulation-origin baseline + broad ``allow_overlap`` for the captured pivot
hardware, mirroring calculator's hinge treatment.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

import cadquery as cq

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Inertial,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

BoardForm = Literal["rect_rounded", "arched_top", "side_landscape"]
ClampMechanism = Literal["spring_jaw", "toggle_lever", "wire_bail", "arch_ring"]
HangHardware = Literal["none", "swivel_ring"]
Cover = Literal["none", "folding_cover"]
MaterialStyle = Literal["blue_chrome", "black_steel", "kraft_brass"]

BOARD_FORMS: tuple[BoardForm, ...] = ("rect_rounded", "arched_top", "side_landscape")
CLAMP_MECHANISMS: tuple[ClampMechanism, ...] = (
    "spring_jaw",
    "toggle_lever",
    "wire_bail",
    "arch_ring",
)
HANG_HARDWARES: tuple[HangHardware, ...] = ("none", "swivel_ring")
COVERS: tuple[Cover, ...] = ("none", "folding_cover")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = ("blue_chrome", "black_steel", "kraft_brass")

# Clamp multiplicity domain (spec §8).
N_CLAMPS_MIN, N_CLAMPS_MAX = 1, 3

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "blue_chrome": {
        "board": (0.13, 0.45, 0.92, 1.0),
        "metal": (0.78, 0.80, 0.83, 1.0),
        "cap": (0.10, 0.10, 0.11, 1.0),
        "cover": (0.20, 0.30, 0.52, 0.92),
    },
    "black_steel": {
        "board": (0.16, 0.16, 0.18, 1.0),
        "metal": (0.66, 0.68, 0.70, 1.0),
        "cap": (0.05, 0.05, 0.06, 1.0),
        "cover": (0.22, 0.22, 0.24, 0.92),
    },
    "kraft_brass": {
        "board": (0.70, 0.58, 0.38, 1.0),
        "metal": (0.78, 0.66, 0.36, 1.0),
        "cap": (0.20, 0.16, 0.10, 1.0),
        "cover": (0.55, 0.45, 0.30, 0.92),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Scaled per-build by board_scale.
# Baselines from parent f7e86c02 (rect portrait) and the side/rounded forks.
# ---------------------------------------------------------------------------
_BOARD_LEN = 0.330  # long dimension
_BOARD_WID = 0.232  # short dimension
_BOARD_THK = 0.0032  # plastic panel thickness (not scaled)
_BOARD_CORNER_R = 0.012
_ARCH_RISE = 0.035  # arched-top extension past the straight edge

# Clamp geometry — real mechanical sizes, never scaled by board_scale.
_CLAMP_WID = 0.078  # clamp footprint along the mount edge
_BASE_LEN = 0.046  # fixed base footprint along the loading direction
_PIVOT_RISE = 0.0090  # pivot axis height above the board top face
_PIVOT_RADIUS = 0.0030
_LEVER_FRONT = 0.026  # spring/toggle lever front lip reach
_LEVER_BACK = 0.024  # finger-pad tail reach behind pivot
_LEVER_CROWN = 0.0080
_BAIL_REACH = 0.030  # wire bail / arch forward reach
_WIRE_R = 0.0019
_GRIP_DROP = 0.0006  # closed gripper rests this far above the board top

# Hang swivel ring.
_RING_R = 0.010  # ring centerline radius
_RING_WIRE_R = 0.0016
_EYELET_R = 0.0040

# Folding cover.
_COVER_THK = 0.0018
_HINGE_R = 0.0030


@dataclass(frozen=True)
class ClipboardConfig:
    board_form: BoardForm | None = None
    clamp_mechanism: ClampMechanism | None = None
    hang_hardware: HangHardware | None = None
    cover: Cover | None = None
    n_clamps: int | None = None
    material_style: MaterialStyle = "blue_chrome"
    board_scale: float = 1.0
    clamp_span_scale: float = 1.0
    lever_reach_scale: float = 1.0
    open_angle_scale: float = 1.0
    name: str = "clipboard"


@dataclass(frozen=True)
class ResolvedClipboardConfig:
    board_form: BoardForm
    clamp_mechanism: ClampMechanism
    hang_hardware: HangHardware
    cover: Cover
    n_clamps: int
    material_style: MaterialStyle
    # Concrete geometry (scaled).
    load_len: float  # board extent along the loading direction (X)
    edge_len: float  # board extent along the mount edge (Y)
    board_thk: float
    corner_r: float
    arch_rise: float
    face_z: float  # board top face height
    clamp_wid: float
    base_len: float
    clamp_center_x: float  # x of the pivot axis (loading direction)
    pivot_z: float
    lever_reach_scale: float
    open_angle_scale: float
    name: str

    @property
    def is_arched(self) -> bool:
        return self.board_form == "arched_top"

    @property
    def is_landscape(self) -> bool:
        return self.board_form == "side_landscape"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> ClipboardConfig:
    rng = random.Random(seed)
    # Weighted procedural sampling: the plain rect board and spring-jaw clamp are
    # the common baseline; optional hang ring / cover and the multi-clamp rows are
    # rarer (spec §9 sampler policy).
    board = rng.choices(BOARD_FORMS, weights=[6, 3, 3], k=1)[0]
    mech = rng.choices(CLAMP_MECHANISMS, weights=[5, 3, 3, 3], k=1)[0]
    hang = rng.choices(HANG_HARDWARES, weights=[6, 4], k=1)[0]
    cover = rng.choices(COVERS, weights=[6, 4], k=1)[0]
    n_clamps = rng.choices([1, 2, 3], weights=[6, 3, 2], k=1)[0]
    return ClipboardConfig(
        board_form=board,
        clamp_mechanism=mech,
        hang_hardware=hang,
        cover=cover,
        n_clamps=n_clamps,
        material_style=rng.choice(MATERIAL_STYLES),
        board_scale=round(rng.uniform(0.92, 1.10), 4),
        clamp_span_scale=round(rng.uniform(0.88, 1.08), 4),
        lever_reach_scale=round(rng.uniform(0.90, 1.10), 4),
        open_angle_scale=round(rng.uniform(0.85, 1.12), 4),
        name=f"seeded_clipboard_{seed}",
    )


def resolve_config(
    config: ClipboardConfig | None = None,
) -> ResolvedClipboardConfig:
    cfg = config or ClipboardConfig()
    board = _pick(cfg.board_form, BOARD_FORMS)
    mech = _pick(cfg.clamp_mechanism, CLAMP_MECHANISMS)
    hang = _pick(cfg.hang_hardware, HANG_HARDWARES)
    cover = _pick(cfg.cover, COVERS)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)

    n_clamps = int(
        _clamp(cfg.n_clamps if cfg.n_clamps is not None else 1, N_CLAMPS_MIN, N_CLAMPS_MAX)
    )

    s = _clamp(cfg.board_scale, 0.92, 1.10)
    span_scale = _clamp(cfg.clamp_span_scale, 0.88, 1.08)
    lever_reach_scale = _clamp(cfg.lever_reach_scale, 0.90, 1.10)
    open_angle_scale = _clamp(cfg.open_angle_scale, 0.85, 1.12)

    # The "loading direction" (X) is the short board dimension in landscape and
    # the long dimension in portrait; "edge" (Y) is the clamp-row direction.
    if board == "side_landscape":
        load_len = _BOARD_WID * s
        edge_len = _BOARD_LEN * s
    else:
        load_len = _BOARD_LEN * s
        edge_len = _BOARD_WID * s

    clamp_wid = _CLAMP_WID * span_scale
    base_len = _BASE_LEN
    clamp_center_x = 0.034
    arch_rise = _ARCH_RISE * s if board == "arched_top" else 0.0

    # Multiplicity inequality (spec §7): n_clamps evenly spaced along the edge each
    # occupy a clamp_wid-wide Y footprint and need a real gap between neighbors.
    # The required edge span for n clamps is n*clamp_wid + (n-1)*gap; shrink each
    # clamp footprint until the row (plus end margins) fits the usable edge.
    _CLAMP_GAP = 0.010  # minimum Y clearance between adjacent clamp bases
    usable_edge = edge_len - 2.0 * 0.014
    needed = n_clamps * clamp_wid + (n_clamps - 1) * _CLAMP_GAP
    if needed > usable_edge:
        clamp_wid = max(0.038, (usable_edge - (n_clamps - 1) * _CLAMP_GAP) / n_clamps)

    return ResolvedClipboardConfig(
        board_form=board,
        clamp_mechanism=mech,
        hang_hardware=hang,
        cover=cover,
        n_clamps=n_clamps,
        material_style=material_style,
        load_len=load_len,
        edge_len=edge_len,
        board_thk=_BOARD_THK,
        corner_r=_BOARD_CORNER_R,
        arch_rise=arch_rise,
        face_z=_BOARD_THK,
        clamp_wid=clamp_wid,
        base_len=base_len,
        clamp_center_x=clamp_center_x,
        pivot_z=_BOARD_THK + _PIVOT_RISE,
        lever_reach_scale=lever_reach_scale,
        open_angle_scale=open_angle_scale,
        name=cfg.name or "clipboard",
    )


def with_overrides(config: ClipboardConfig, **kwargs: object) -> ClipboardConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ClipboardConfig | ResolvedClipboardConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedClipboardConfig) else resolve_config(config)
    return (
        ("board_form", r.board_form),
        ("clamp_mechanism", r.clamp_mechanism),
        ("hang_hardware", r.hang_hardware),
        ("cover", r.cover),
        ("clamps", f"clamps_{r.n_clamps}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Clamp row layout
# ---------------------------------------------------------------------------
def _clamp_centers_y(r: ResolvedClipboardConfig) -> list[float]:
    """Evenly spaced Y centers for the n_clamps row along the mount edge.

    resolve_config has already shrunk clamp_wid so the row fits with a real gap,
    so the pitch is clamp_wid + a guaranteed clearance.
    """
    n = r.n_clamps
    if n == 1:
        return [0.0]
    pitch = r.clamp_wid + 0.010
    span = (n - 1) * pitch
    return [-span / 2.0 + i * pitch for i in range(n)]


# ---------------------------------------------------------------------------
# Board geometry
# ---------------------------------------------------------------------------
def _board_solid(r: ResolvedClipboardConfig):
    """Thin rounded-corner / arched-head plastic panel, top face at z=board_thk.

    The board occupies x in [-arch_rise, load_len] (arched forms push the top
    edge below x=0), centered on Y, lifted so the bottom face sits on z=0.
    """
    if r.is_arched:
        hw = r.edge_len / 2.0
        rise = r.arch_rise
        ln = r.load_len
        # Bottom-right -> up right side -> arch across top -> down left side.
        board = (
            cq.Workplane("XY")
            .moveTo(ln, -hw)
            .lineTo(ln, hw)
            .lineTo(0.0, hw)
            .threePointArc((-rise, 0.0), (0.0, -hw))
            .close()
            .extrude(r.board_thk)
            .edges("|Z and >X")
            .fillet(r.corner_r)
        )
    else:
        board = (
            cq.Workplane("XY")
            .box(r.load_len, r.edge_len, r.board_thk, centered=(False, True, False))
            .edges("|Z")
            .fillet(r.corner_r)
        )
    return board.translate((0.0, 0.0, 0.0))


def _board_mesh(r: ResolvedClipboardConfig, *, assets):
    board = _board_solid(r)
    # Eyelet boss for the swivel ring is fused onto the board top corner so the
    # ring pivot origin lands on real board geometry.
    if r.hang_hardware == "swivel_ring":
        ex, ey = _eyelet_xy(r)
        boss = (
            cq.Workplane("XY", origin=(ex, ey, 0.0)).circle(_EYELET_R).extrude(r.face_z + _EYELET_R)
        )
        board = board.union(boss)
    return mesh_from_cadquery(board, "board_panel", assets=assets)


def _eyelet_xy(r: ResolvedClipboardConfig) -> tuple[float, float]:
    """Top-corner eyelet position for the swivel ring."""
    return (0.006, r.edge_len / 2.0 - 0.012)


# ---------------------------------------------------------------------------
# Geometry helper: a round-wire cylinder between two 3D points (for bent wire).
# ---------------------------------------------------------------------------
def _cyl_between(p0: tuple[float, float, float], p1: tuple[float, float, float], radius: float):
    dx, dy, dz = (p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-9:
        return cq.Workplane("XY", origin=p0).sphere(radius)
    # Build along +Z then rotate the Z axis onto the (dx,dy,dz) direction.
    cyl = cq.Workplane("XY", origin=p0).circle(radius).extrude(length)
    # Rotation axis = Z x dir; angle = acos(dz/length).
    ux, uy, uz = (dx / length, dy / length, dz / length)
    ax, ay, az = (-uy, ux, 0.0)  # cross((0,0,1),(ux,uy,uz))
    an = math.sqrt(ax * ax + ay * ay + az * az)
    if an < 1e-9:
        # Parallel to Z; flip if pointing -Z.
        if uz < 0:
            cyl = cyl.rotate((p0[0], p0[1], p0[2]), (p0[0] + 1.0, p0[1], p0[2]), 180.0)
        return cyl
    angle = math.degrees(math.acos(max(-1.0, min(1.0, uz))))
    return cyl.rotate((p0[0], p0[1], p0[2]), (p0[0] + ax, p0[1] + ay, p0[2] + az), angle)


# ---------------------------------------------------------------------------
# Clamp base meshes (fixed parts). Authored in the base's own frame (footplate
# bottom at z=0, pivot at (0,0,_PIVOT_RISE)); the FIXED joint seats them on the
# board top face and rises to a pivot barrel.
# ---------------------------------------------------------------------------
def _spring_base_mesh(r: ResolvedClipboardConfig, *, assets):
    """Riveted footplate + hump + side cheeks + pivot barrel (spring/toggle).

    Authored in the base's OWN frame: footplate bottom at z=0, pivot center at
    local (0, 0, _PIVOT_RISE). The FIXED joint places the base at the board face
    (clamp_center_x, cy, face_z), so the joint origin sits on real base geometry.
    """
    fz = 0.0
    cx = 0.0
    pivot_z = _PIVOT_RISE
    cw = r.clamp_wid
    plate = (
        cq.Workplane("XY")
        .workplane(offset=fz)
        .box(r.base_len, cw, 0.0016, centered=(True, True, False))
        .translate((cx, 0.0, 0.0))
        .edges("|Z")
        .fillet(0.004)
    )
    hump = (
        cq.Workplane("XY")
        .workplane(offset=fz)
        .box(0.020, cw, _PIVOT_RISE - 0.001, centered=(True, True, False))
        .translate((cx, 0.0, 0.0))
        .edges("|Y and >Z")
        .fillet(0.0035)
    )
    base = plate.union(hump)
    cheek_thk = 0.0040
    cheek_y = cw / 2.0 - cheek_thk / 2.0
    for sign in (-1.0, 1.0):
        cheek = (
            cq.Workplane("XY")
            .workplane(offset=fz)
            .box(0.018, cheek_thk, _PIVOT_RISE + 0.003, centered=(True, True, False))
            .translate((cx, sign * cheek_y, 0.0))
        )
        base = base.union(cheek)
    barrel = (
        cq.Workplane("XZ", origin=(cx, 0.0, pivot_z))
        .circle(_PIVOT_RADIUS + 0.0009)
        .extrude(cw / 2.0, both=True)
    )
    base = base.union(barrel)
    # Rivet decoration inlined into the base mesh (not a separate part).
    for sign in (-1.0, 1.0):
        rivet = (
            cq.Workplane("XY", origin=(cx + r.base_len / 2.0 - 0.008, sign * 0.020, fz + 0.0016))
            .circle(0.0035)
            .extrude(0.0012)
        )
        base = base.union(rivet)
    return mesh_from_cadquery(base, "clamp_base", assets=assets)


def _block_base_mesh(r: ResolvedClipboardConfig, *, assets, with_ears: bool):
    """Low anchor block + pivot barrel for wire bail / arch ring fasteners.

    Authored in the base's OWN frame (footplate bottom at z=0, pivot at local
    (0, 0, _PIVOT_RISE)); the FIXED joint places it at the board face.
    """
    fz = 0.0
    cx = 0.0
    pivot_z = _PIVOT_RISE
    cw = r.clamp_wid
    block = (
        cq.Workplane("XY")
        .workplane(offset=fz)
        .box(0.024, cw, _PIVOT_RISE, centered=(True, True, False))
        .translate((cx, 0.0, 0.0))
        .edges("|Y and >Z")
        .fillet(0.003)
    )
    base = block
    if with_ears:
        ear_thk = 0.004
        for sign in (-1.0, 1.0):
            ear = (
                cq.Workplane("XY")
                .workplane(offset=fz)
                .box(0.014, ear_thk, _PIVOT_RISE + 0.003, centered=(True, True, False))
                .translate((cx, sign * (cw / 2.0 - ear_thk / 2.0), 0.0))
            )
            base = base.union(ear)
    barrel = (
        cq.Workplane("XZ", origin=(cx, 0.0, pivot_z))
        .circle(_PIVOT_RADIUS + 0.0009)
        .extrude(cw / 2.0, both=True)
    )
    base = base.union(barrel)
    for sign in (-1.0, 1.0):
        rivet = (
            cq.Workplane("XY", origin=(cx, sign * (cw / 2.0 - 0.010), fz + _PIVOT_RISE))
            .circle(0.0030)
            .extrude(0.0010)
        )
        base = base.union(rivet)
    return mesh_from_cadquery(base, "clamp_base", assets=assets)


# ---------------------------------------------------------------------------
# Clamp moving-part meshes. Authored in the JOINT-LOCAL frame: origin at the
# pivot axis, local +x toward the front gripping zone, +z up.
# ---------------------------------------------------------------------------
def _spring_lever_mesh(r: ResolvedClipboardConfig, *, assets):
    """Curved sheet-metal spring jaw: cover + front lip + finger shelf + sleeve."""
    cw = r.clamp_wid
    half_w = cw / 2.0 - 0.0050
    front = _LEVER_FRONT * r.lever_reach_scale
    back = -_LEVER_BACK
    cover = (
        cq.Workplane("XZ")
        .moveTo(back, 0.0026)
        .lineTo(-0.006, 0.0040)
        .lineTo(0.010, 0.0028)
        .lineTo(front, 0.0010)
        .lineTo(front, 0.0024)
        .lineTo(0.008, _LEVER_CROWN - 0.0008)
        .lineTo(-0.008, _LEVER_CROWN)
        .lineTo(back, 0.0050)
        .close()
        .extrude(half_w, both=True)
    )
    lip_top = 0.0024
    lip_bottom = -(r.pivot_z - r.face_z - _GRIP_DROP)
    lip_h = lip_top - lip_bottom
    lip = (
        cq.Workplane("XY")
        .box(0.0060, 2.0 * half_w, lip_h, centered=(True, True, False))
        .edges("|Y and <Z")
        .fillet(0.0010)
        .translate((front - 0.0030, 0.0, lip_bottom))
    )
    shelf = (
        cq.Workplane("XY")
        .box(0.014, 2.0 * half_w, 0.0040, centered=(True, True, True))
        .translate((back + 0.006, 0.0, 0.0030))
    )
    sleeve = (
        cq.Workplane("XZ", origin=(0.0, 0.0, 0.0))
        .circle(_PIVOT_RADIUS + 0.0018)
        .circle(_PIVOT_RADIUS + 0.0010)
        .extrude(half_w, both=True)
    )
    lever = cover.union(lip).union(shelf).union(sleeve)
    return mesh_from_cadquery(lever, "spring_lever", assets=assets)


def _finger_caps_mesh(r: ResolvedClipboardConfig, *, assets):
    cw = r.clamp_wid
    half_w = cw / 2.0 - 0.0050
    back = -_LEVER_BACK
    caps = None
    for sign in (-1.0, 1.0):
        cap = (
            cq.Workplane("XY")
            .box(0.0110, 0.0150, 0.0040, centered=(True, True, False))
            .edges("|Z")
            .fillet(0.0016)
            .translate((back + 0.004, sign * (half_w - 0.010), 0.0044))
        )
        caps = cap if caps is None else caps.union(cap)
    return mesh_from_cadquery(caps, "finger_caps", assets=assets)


def _toggle_lever_mesh(r: ResolvedClipboardConfig, *, assets):
    """Over-center toggle cam lever: a long arm + rounded cam lobe + pressure foot.

    Authored joint-local: pivot at origin. The lever arm points up/back at q=0
    and the cam lobe + pressure foot reach down toward the board's grip zone.
    """
    cw = r.clamp_wid
    half_w = cw / 2.0 - 0.006
    reach = _LEVER_FRONT * r.lever_reach_scale
    # Cam lobe: a fat rounded disc around the pivot whose lower profile presses
    # the foot down when the lever lies flat.
    lobe = cq.Workplane("XZ", origin=(0.0, 0.0, 0.0)).circle(0.0070).extrude(half_w, both=True)
    # Lever arm (handle) extending forward (+x) and up.
    arm = (
        cq.Workplane("XZ")
        .moveTo(0.0, 0.0035)
        .lineTo(reach, 0.0060)
        .lineTo(reach + 0.010, 0.0048)
        .lineTo(reach + 0.010, -0.0010)
        .lineTo(0.0, -0.0030)
        .close()
        .extrude(half_w, both=True)
    )
    # Pressure foot hanging below the cam to contact the board grip zone.
    foot_bottom = -(r.pivot_z - r.face_z - _GRIP_DROP)
    foot = (
        cq.Workplane("XY")
        .box(0.012, 2.0 * half_w, abs(foot_bottom) + 0.004, centered=(True, True, False))
        .edges("|Y and <Z")
        .fillet(0.0012)
        .translate((0.004, 0.0, foot_bottom))
    )
    sleeve = (
        cq.Workplane("XZ", origin=(0.0, 0.0, 0.0))
        .circle(_PIVOT_RADIUS + 0.0018)
        .circle(_PIVOT_RADIUS + 0.0010)
        .extrude(half_w, both=True)
    )
    lever = lobe.union(arm).union(foot).union(sleeve)
    return mesh_from_cadquery(lever, "toggle_lever", assets=assets)


def _wire_bail_mesh(r: ResolvedClipboardConfig, *, assets):
    """Single bent round-wire bail (hairpin U). Pivot line on local Y at z=0;
    the front cross-bar reaches +x and drops to the board grip zone."""
    cw = r.clamp_wid
    half_w = cw / 2.0 - 0.004
    reach = _BAIL_REACH * r.lever_reach_scale
    drop = -(r.pivot_z - r.face_z - _GRIP_DROP)
    wr = _WIRE_R
    # Clean swept hairpin: front cross-bar + two angled legs + pivot axle.
    cross = cq.Workplane("XZ", origin=(reach, 0.0, drop)).circle(wr).extrude(half_w, both=True)
    bail = cross
    for sign in (-1.0, 1.0):
        # Leg from the pivot axle (x=0,z=0) to the front cross-bar (x=reach,z=drop)
        # at this end of the bail (y=sign*half_w), built as a real 3D cylinder so
        # both endpoints actually fuse to the axle and cross-bar.
        leg = _cyl_between((0.0, sign * half_w, 0.0), (reach, sign * half_w, drop), wr)
        bail = bail.union(leg)
    # Pivot axle rod along Y at z=0 (the real pivot pin) so the child origin
    # (0,0,0) sits on real wire geometry.
    axle = cq.Workplane("XZ", origin=(0.0, 0.0, 0.0)).circle(wr * 0.9).extrude(half_w, both=True)
    bail = bail.union(axle)
    return mesh_from_cadquery(bail, "wire_bail", assets=assets)


def _arch_ring_mesh(r: ResolvedClipboardConfig, *, assets):
    """Split round-wire semicircular arch ring-binder. Pivot line on local Y at
    z=0; the arch arcs forward (+x) over the board, lying flat at q=0."""
    cw = r.clamp_wid
    half_w = cw / 2.0 - 0.006
    reach = _BAIL_REACH * r.lever_reach_scale
    wr = _WIRE_R
    # Build a swept-tube approximation as a chain of short cylinders along a
    # semicircular path in the local XY plane (z=0): foot1 -> apex -> foot2.
    # Consecutive cylinders overlap at shared nodes, so the arch is one solid
    # without extra sphere joints (cheaper to build for the multi-clamp sweep).
    n = 12
    ring = None
    prev = None
    for i in range(n + 1):
        theta = -math.pi / 2.0 + math.pi * i / n
        x = reach * math.cos(theta)
        y = half_w * math.sin(theta)
        if prev is not None:
            seg = _cyl_between((prev[0], prev[1], 0.0), (x, y, 0.0), wr)
            ring = seg if ring is None else ring.union(seg)
        prev = (x, y)
    # Pivot axle rod along Y at z=0 (the real hinge pin) connecting the two arch
    # feet, so the child origin (0,0,0) and the base barrel contact lie on real
    # wire geometry along the whole hinge line.
    axle = cq.Workplane("XZ", origin=(0.0, 0.0, 0.0)).circle(wr * 1.1).extrude(half_w, both=True)
    ring = ring.union(axle)
    return mesh_from_cadquery(ring, "arch_ring", assets=assets)


# ---------------------------------------------------------------------------
# Hang ring + cover meshes.
# ---------------------------------------------------------------------------
def _ring_mesh(r: ResolvedClipboardConfig, *, assets):
    """Round-wire swivel ring. The ring loop lies in the local YZ plane and its
    top point sits at the local origin (0,0,0) where the REVOLUTE joint axis (X,
    the eyelet axis) passes; the ring hangs in -Z. A short axle stub along X at
    the origin places real wire geometry on the joint origin."""
    # Ring centered at (0,0,-_RING_R) so the topmost wire point is at the origin.
    cz = -_RING_R
    n = 18
    ring = None
    prev = None
    for i in range(n + 1):
        a = 2.0 * math.pi * i / n
        y = _RING_R * math.cos(a)
        z = cz + _RING_R * math.sin(a)
        if prev is not None:
            seg = _cyl_between((0.0, prev[0], prev[1]), (0.0, y, z), _RING_WIRE_R)
            ring = seg if ring is None else ring.union(seg)
        prev = (y, z)
    # Axle stub along X at the top of the ring (the captured eyelet pin).
    stub = (
        cq.Workplane("YZ", origin=(0.0, 0.0, 0.0))
        .circle(_RING_WIRE_R)
        .extrude(_EYELET_R + 0.001, both=True)
    )
    ring = ring.union(stub)
    return mesh_from_cadquery(ring, "swivel_ring", assets=assets)


def _cover_mesh(r: ResolvedClipboardConfig, *, assets):
    """Hinged front cover panel + knuckle. Authored joint-local: hinge edge at
    part frame y=0, z=0; panel extends in -Y across the board, top surface near
    z=0 (closed = lying flat over the board)."""
    cov_x = r.load_len - 0.006
    cov_y = r.edge_len - 0.004
    # Joint-local X=0 maps to the board mid-X (the joint origin already offsets
    # by load_len/2), so the panel is centered on local X=0 to lie flat over the
    # board — NOT translated by load_len/2 again (that pushed it half off the far
    # board edge).
    panel = (
        cq.Workplane("XY")
        .box(cov_x, cov_y, _COVER_THK, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.006)
        .translate((0.0, -cov_y / 2.0, -_COVER_THK))
    )
    # Hinge knuckle along X at the hinge line (y=0, z=0), centered on local X=0
    # so it wraps the board spine along the board length.
    knuckle = (
        cq.Workplane("YZ", origin=(0.0, 0.0, 0.0))
        .circle(_HINGE_R)
        .extrude(cov_x * 0.45, both=True)
    )
    panel = panel.union(knuckle)
    return mesh_from_cadquery(panel, "cover_panel", assets=assets)


def _hinge_spine_mesh(r: ResolvedClipboardConfig, *, assets):
    """Board-side hinge spine barrel, in WORLD coords.

    The barrel axis is X (the hinge line runs along the board length at the +Y
    long edge); it spans the board X extent and embeds slightly into the board
    top for connectivity. Built on a YZ workplane so the extrude is along X.
    """
    spine_len = r.load_len - 0.010
    x_start = (r.load_len - spine_len) / 2.0
    spine = (
        cq.Workplane("YZ")
        .workplane(offset=x_start)
        .center(r.edge_len / 2.0, r.face_z + _HINGE_R - 0.0006)
        .circle(_HINGE_R)
        .extrude(spine_len)
    )
    return mesh_from_cadquery(spine, "hinge_spine", assets=assets)


# ---------------------------------------------------------------------------
# Build helpers
# ---------------------------------------------------------------------------
def _open_limit(r: ResolvedClipboardConfig) -> float:
    base = {
        "spring_jaw": 0.42,
        "toggle_lever": 0.55,
        "wire_bail": 0.85,
        "arch_ring": 1.10,
    }[r.clamp_mechanism]
    return _clamp(base * r.open_angle_scale, 0.20, 1.40)


def _emit_clamp(model, r, board, mech_meshes, mats, idx, cy, *, assets) -> list[str]:
    """Emit one clamp assembly (FIXED base + REVOLUTE moving part) at edge Y=cy."""
    base_mesh, move_mesh, caps_mesh = mech_meshes
    base = model.part(f"clamp_base_{idx}")
    base.visual(base_mesh, material=mats["metal"], name="clamp_base", material_class_id=("metal.chrome_polished" if r.material_style in {"blue_chrome", "kraft_brass"} else "metal.blackened_gunmetal"))
    # Base mesh is authored in its own frame (footplate bottom at z=0, pivot at
    # local (0,0,_PIVOT_RISE)); the FIXED origin lands on the footplate so it
    # sits on real base + board geometry.
    base.inertial = Inertial.from_geometry(
        Box((r.base_len, r.clamp_wid, _PIVOT_RISE)),
        mass=0.02,
        origin=Origin(xyz=(0.0, 0.0, _PIVOT_RISE / 2.0)),
    )
    model.articulation(
        f"board_to_clamp_base_{idx}",
        ArticulationType.FIXED,
        parent=board,
        child=base,
        origin=Origin(xyz=(r.clamp_center_x, cy, r.face_z)),
    )

    mover = model.part(f"clamp_mover_{idx}")
    mover.visual(move_mesh, material=mats["metal"], name="clamp_mover", material_class_id=("metal.chrome_polished" if r.material_style in {"blue_chrome", "kraft_brass"} else "metal.blackened_gunmetal"))
    if caps_mesh is not None:
        mover.visual(caps_mesh, material=mats["cap"], name="finger_caps", material_class_id="plastic.opaque_glossy_molded")
    mover.inertial = Inertial.from_geometry(
        Box((2.0 * _LEVER_FRONT, r.clamp_wid, _LEVER_CROWN + 0.006)),
        mass=0.012,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    # REVOLUTE about -Y: positive q lifts the front gripper up off the board.
    # Origin is in the base's local frame; the base's pivot barrel sits at local
    # (0, 0, _PIVOT_RISE), and the mover mesh is authored with its pivot at the
    # mesh origin, so the REVOLUTE origin is (0, 0, _PIVOT_RISE).
    model.articulation(
        f"clamp_base_{idx}_to_mover_{idx}",
        ArticulationType.REVOLUTE,
        parent=base,
        child=mover,
        origin=Origin(xyz=(0.0, 0.0, _PIVOT_RISE)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=_open_limit(r)),
    )
    return [f"clamp_base_{idx}", f"clamp_mover_{idx}"]


def _build_mech_meshes(r: ResolvedClipboardConfig, *, assets):
    """Return (base_mesh, mover_mesh, caps_mesh) for the chosen mechanism."""
    if r.clamp_mechanism == "spring_jaw":
        return (
            _spring_base_mesh(r, assets=assets),
            _spring_lever_mesh(r, assets=assets),
            _finger_caps_mesh(r, assets=assets),
        )
    if r.clamp_mechanism == "toggle_lever":
        return (
            _spring_base_mesh(r, assets=assets),
            _toggle_lever_mesh(r, assets=assets),
            None,
        )
    if r.clamp_mechanism == "wire_bail":
        return (
            _block_base_mesh(r, assets=assets, with_ears=True),
            _wire_bail_mesh(r, assets=assets),
            None,
        )
    # arch_ring
    return (
        _block_base_mesh(r, assets=assets, with_ears=True),
        _arch_ring_mesh(r, assets=assets),
        None,
    )


def _emit_hang_ring(model, r, board, mats, *, assets) -> list[str]:
    if r.hang_hardware != "swivel_ring":
        return []
    ex, ey = _eyelet_xy(r)
    ring = model.part("swivel_ring")
    ring.visual(_ring_mesh(r, assets=assets), material=mats["metal"], name="swivel_ring", material_class_id=("metal.chrome_polished" if r.material_style in {"blue_chrome", "kraft_brass"} else "metal.blackened_gunmetal"))
    ring.inertial = Inertial.from_geometry(
        Box((2.0 * _RING_R, 2.0 * _RING_R, 2.0 * _RING_WIRE_R)),
        mass=0.003,
        origin=Origin(xyz=(0.0, 0.0, 0.0)),
    )
    # REVOLUTE about X (the eyelet axis): the ring swivels freely so the board
    # can hang. Origin on the eyelet boss top.
    model.articulation(
        "board_to_swivel_ring",
        ArticulationType.REVOLUTE,
        parent=board,
        child=ring,
        origin=Origin(xyz=(ex, ey, r.face_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=0.5, velocity=6.0, lower=-math.pi, upper=math.pi),
    )
    return ["swivel_ring"]


def _emit_cover(model, r, board, mats, *, assets) -> list[str]:
    if r.cover != "folding_cover":
        return []
    # Board-side hinge spine inlined as a board visual (non-moving hardware).
    board.visual(
        _hinge_spine_mesh(r, assets=assets),
        material=mats["metal"],
        name="hinge_spine", material_class_id=("metal.chrome_polished" if r.material_style in {"blue_chrome", "kraft_brass"} else "metal.blackened_gunmetal"),
    )
    cover = model.part("cover")
    cover.visual(_cover_mesh(r, assets=assets), material=mats["cover"], name="cover_panel", material_class_id="plastic.frosted_translucent")
    cover.inertial = Inertial.from_geometry(
        Box((r.load_len, r.edge_len, _COVER_THK)),
        mass=0.05,
        origin=Origin(xyz=(r.load_len / 2.0, -r.edge_len / 2.0, -_COVER_THK / 2.0)),
    )
    # REVOLUTE about -X along the +Y long side edge: positive q lifts the free
    # edge (opens the cover). q=0 lies flat over the board.
    model.articulation(
        "board_to_cover",
        ArticulationType.REVOLUTE,
        parent=board,
        child=cover,
        origin=Origin(xyz=(r.load_len / 2.0, r.edge_len / 2.0, r.face_z + _HINGE_R)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=3.0, lower=0.0, upper=2.4),
    )
    return ["cover"]


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_clipboard(
    config: ClipboardConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.material_style]
    mats = {
        key: model.material(f"clip_{key}_{r.material_style}", rgba=palette[key])
        for key in ("board", "metal", "cap", "cover")
    }

    # Root board panel (carries inlined rivet/eyelet/hinge-spine visuals).
    board = model.part("board")
    board.visual(_board_mesh(r, assets=assets), material=mats["board"], name="board_panel", material_class_id=("plastic.opaque_glossy_molded" if r.material_style in {"blue_chrome", "kraft_brass"} else "metal.paint_coated"))
    board.inertial = Inertial.from_geometry(
        Box((r.load_len, r.edge_len, r.board_thk)),
        mass=0.18,
        origin=Origin(xyz=(r.load_len / 2.0, 0.0, r.board_thk / 2.0)),
    )

    # Clamp row (multiplicity). Identical mechanism geometry rebuilt per clamp so
    # each part owns its own mesh asset; the shared helper keeps them uniform.
    centers = _clamp_centers_y(r)
    for i, cy in enumerate(centers):
        per = _build_mech_meshes(r, assets=assets)
        _emit_clamp(model, r, board, per, mats, i, cy, assets=assets)

    _emit_hang_ring(model, r, board, mats, assets=assets)
    _emit_cover(model, r, board, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_clipboard(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_clipboard(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_clipboard_tests(
    object_model: ArticulatedObject,
    config: ClipboardConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    board = object_model.get_part("board")

    # --- Captured-pin / seated allowances for the articulated children. ---
    for i in range(r.n_clamps):
        base = object_model.get_part(f"clamp_base_{i}")
        mover = object_model.get_part(f"clamp_mover_{i}")
        ctx.allow_overlap(
            base,
            mover,
            reason=(
                "clamp mover pin sleeve is captured around the fixed base pivot "
                "barrel (captured-pin pivot); the gripper nests over the base."
            ),
        )
        ctx.allow_overlap(
            board,
            mover,
            reason="closed clamp gripper presses down onto the board paper zone.",
        )
    if r.hang_hardware == "swivel_ring":
        ctx.allow_overlap(
            board,
            object_model.get_part("swivel_ring"),
            reason="swivel ring wire wraps the board eyelet boss (captured-pin swivel).",
        )
    if r.cover == "folding_cover":
        cover_part = object_model.get_part("cover")
        ctx.allow_overlap(
            board,
            cover_part,
            reason="folding cover hinge knuckle wraps the board hinge spine; closed cover rests flat over the board.",
        )
        # A closed folder cover lies flat over the whole board top, so it slides
        # under every clamp assembly (the clamp presses onto the cover as it would
        # onto paper) and over the hang ring, as in a real form-holder clipboard.
        for i in range(r.n_clamps):
            ctx.allow_overlap(
                object_model.get_part(f"clamp_base_{i}"),
                cover_part,
                reason="closed folding cover panel slides under the clamp base (form-holder folder).",
            )
            ctx.allow_overlap(
                object_model.get_part(f"clamp_mover_{i}"),
                cover_part,
                reason="closed folding cover panel rests under the clamp gripper (form-holder folder).",
            )
        if r.hang_hardware == "swivel_ring":
            ctx.allow_overlap(
                object_model.get_part("swivel_ring"),
                cover_part,
                reason="closed folding cover panel lies over the board hang-ring corner.",
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    # Joints omit MatingContract (captured-pin / seated geometry, grandfathered);
    # the flat 0.015 m articulation-origin baseline runs in the compiler and all
    # origins sit on real hardware (pivot barrel / eyelet boss / hinge spine).
    ctx.fail_if_joint_mating_has_gap()

    # --- Board hero geometry: wide thin flat panel. ---
    bmin, bmax = ctx.part_world_aabb(board)
    board_len = bmax[0] - bmin[0]
    board_wid = bmax[1] - bmin[1]
    board_thk = bmax[2] - bmin[2]
    ctx.check(
        "board reads as a wide thin clipboard panel",
        board_len > 0.18 and board_wid > 0.18 and board_thk < 0.010,
        details=f"len={board_len:.3f} wid={board_wid:.3f} thk={board_thk:.4f}",
    )
    # Guard against runaway inlined hardware (e.g. a hinge spine extruded along
    # the wrong axis / far too long): the board part incl. its inlined visuals
    # must not overrun the nominal panel footprint by more than a small margin.
    ctx.check(
        "board footprint stays within the nominal panel bounds",
        board_len <= r.load_len + r.arch_rise + 0.02 and board_wid <= r.edge_len + 0.02,
        details=(
            f"len={board_len:.3f}<=({r.load_len:.3f}+{r.arch_rise:.3f}) "
            f"wid={board_wid:.3f}<=({r.edge_len:.3f})"
        ),
    )

    # --- Clamp count + topology. ---
    ctx.check(
        "expected number of clamp movers emitted",
        sum(1 for p in object_model.parts if p.name.startswith("clamp_mover_")) == r.n_clamps,
        details=f"n_clamps={r.n_clamps}",
    )
    for i in range(r.n_clamps):
        j = object_model.get_articulation(f"clamp_base_{i}_to_mover_{i}")
        ctx.check(
            f"clamp {i} mover is REVOLUTE about the mount edge (Y)",
            j.articulation_type == ArticulationType.REVOLUTE and abs(round(j.axis[1], 3)) == 1.0,
            details=f"type={j.articulation_type} axis={tuple(round(c, 3) for c in j.axis)}",
        )
        jb = object_model.get_articulation(f"board_to_clamp_base_{i}")
        ctx.check(
            f"clamp {i} base is FIXED to the board",
            jb.articulation_type == ArticulationType.FIXED,
            details=f"type={jb.articulation_type}",
        )

    # --- Opening the first clamp lifts its front gripper up off the board. ---
    mover0 = object_model.get_part("clamp_mover_0")
    j0 = object_model.get_articulation("clamp_base_0_to_mover_0")
    with ctx.pose({j0: 0.0}):
        a0 = ctx.part_world_aabb(mover0)
    with ctx.pose({j0: _open_limit(r)}):
        a1 = ctx.part_world_aabb(mover0)
    if a0 is not None and a1 is not None:
        ctx.check(
            "opening the clamp lifts its gripper up",
            a1[1][2] > a0[1][2] + 0.003,
            details=f"closed_top={a0[1][2]:.4f} open_top={a1[1][2]:.4f}",
        )

    # --- Closed clamp gripper reaches down near the board top face. The arch-ring
    #     binder lies flat at the hinge line capturing hole-punched sheets, so it
    #     does not press a foot onto the board; the press check is jaw/foot/bail
    #     mechanisms only. ---
    if a0 is not None and r.clamp_mechanism != "arch_ring":
        ctx.check(
            "closed clamp gripper reaches down near the board top",
            a0[0][2] < r.face_z + 0.006,
            details=f"closed_min_z={a0[0][2]:.4f} face={r.face_z:.4f}",
        )

    # --- Optional swivel hang ring. ---
    if r.hang_hardware == "swivel_ring":
        jr = object_model.get_articulation("board_to_swivel_ring")
        ctx.check(
            "swivel ring is REVOLUTE about the eyelet axis (X)",
            jr.articulation_type == ArticulationType.REVOLUTE and abs(round(jr.axis[0], 3)) == 1.0,
            details=f"type={jr.articulation_type} axis={tuple(round(c, 3) for c in jr.axis)}",
        )
        ring = object_model.get_part("swivel_ring")
        # The ring hangs in -Z from the eyelet at rest; swiveling 180 deg about
        # the eyelet (X) axis flips it to +Z, so its AABB Z-center rises.
        with ctx.pose({jr: 0.0}):
            r0 = ctx.part_world_aabb(ring)
        with ctx.pose({jr: math.pi}):
            r1 = ctx.part_world_aabb(ring)
        if r0 is not None and r1 is not None:
            zc0 = (r0[0][2] + r0[1][2]) / 2.0
            zc1 = (r1[0][2] + r1[1][2]) / 2.0
            ctx.check(
                "swiveling the ring 180 deg about the eyelet axis flips it up",
                zc1 > zc0 + 0.004,
                details=f"rest_zc={zc0:.4f} flipped_zc={zc1:.4f}",
            )
    else:
        ctx.check(
            "no swivel ring part when hang_hardware is none",
            "swivel_ring" not in {p.name for p in object_model.parts},
            details=str([p.name for p in object_model.parts]),
        )

    # --- Optional folding cover. ---
    if r.cover == "folding_cover":
        jc = object_model.get_articulation("board_to_cover")
        ctx.check(
            "folding cover is REVOLUTE about -X (long side edge)",
            jc.articulation_type == ArticulationType.REVOLUTE and round(jc.axis[0], 3) == -1.0,
            details=f"type={jc.articulation_type} axis={tuple(round(c, 3) for c in jc.axis)}",
        )
        cover = object_model.get_part("cover")
        with ctx.pose({jc: 0.0}):
            c0 = ctx.part_world_aabb(cover)
        with ctx.pose({jc: 1.5}):
            c1 = ctx.part_world_aabb(cover)
        if c0 is not None and c1 is not None:
            ctx.check(
                "opening the cover raises it",
                (c1[0][2] + c1[1][2]) / 2.0 > (c0[0][2] + c0[1][2]) / 2.0 + 0.004,
                details=f"closed_zc={(c0[0][2] + c0[1][2]) / 2.0:.4f} open_zc={(c1[0][2] + c1[1][2]) / 2.0:.4f}",
            )
            # Closed cover must lie over the board, not hang off its far edge.
            ctx.check(
                "closed cover stays within the board X footprint",
                c0[1][0] <= r.load_len + 0.02 and c0[0][0] >= -r.arch_rise - 0.02,
                details=f"cover_x=[{c0[0][0]:.3f},{c0[1][0]:.3f}] board_x=[{-r.arch_rise:.3f},{r.load_len:.3f}]",
            )
        ctx.check(
            "hinge spine inlined as a board visual",
            "hinge_spine" in {v.name for v in board.visuals},
            details=str([v.name for v in board.visuals]),
        )

    # --- Board silhouette: thin slab resting near z=0. ---
    ctx.check(
        "board is a thin slab near z=0",
        board_thk < 0.010 and bmin[2] < 0.01,
        details=f"thk={board_thk:.4f} z_min={bmin[2]:.4f}",
    )

    # --- slot_choices recorded. ---
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "ClipboardConfig",
    "ResolvedClipboardConfig",
    "build_clipboard",
    "build_seeded_clipboard",
    "config_from_seed",
    "resolve_config",
    "run_clipboard_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
