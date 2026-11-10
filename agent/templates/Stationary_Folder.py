# SPDX-License-Identifier: Apache-2.0

"""Document folder (file / manila folder) modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/Stationary_Folder.md`` and the
``picture/Stationary/Folder`` 5-star sample pool (1 parent + 10 single-axis
fork variants: corner / tabprofile / tabposition / tabcount / gusset /
dividers / topflap / prongfastener / stackcount).

Structure (pattern = ``mixed``): a single root ``back_cover`` chassis carries
two **core REVOLUTE children** (the front cover and the loose lifting sheet,
both hinging about the bottom spine line) plus a set of **parallel optional
children / inline-visual slots** and three **multiplicity axes**:

  * ``corner_style`` (2): rounded vs square outer cover corners (footprint
    shape family; drives the corner fillet of covers / tab / flap). (parent vs
    corner fork)
  * ``tab_style`` (3): narrow rect index tab on the left third, the same tab
    centered, or a full-width straight-cut top tab. (parent / tabposition /
    tabprofile)
  * ``spine_style`` (2): a single rounded bottom fold, or an accordion-pleated
    expanding gusset emitted as ``n_pleats`` zig-zag pleat facets. (parent vs
    gusset)
  * ``interior`` (2, optional): plain, or two fixed divider panels splitting
    the interior into three compartments (inline back-cover visuals). (parent
    vs dividers)
  * ``closure`` (3, optional, single-select): none, a fold-over ``top_flap``
    (REVOLUTE +X off the front cover top edge), or an internal
    ``prong_fastener`` (a fixed strip visual + two REVOLUTE -X prong tongues).
    (parent / topflap / prongfastener)
  * captured-page **multiplicity** ``n_pages``: a regular +Y stack of inline
    captured page visuals. (parent n=3 / stackcount n=7)
  * labeling-tab **multiplicity** ``n_tabs``: a regular staggered row of tab
    blocks unioned into the front cover top edge. (parent n=1 / tabcount n=3)

Non-moving detail (spine fold/gusset, captured pages, dividers, tab, prong
fastener strip plate) is always an inline cover visual — never a FIXED part.
The two core spine hinges always articulate. Every captured/seated hinge joint
(front cover against the page stack, loose sheet inside the stack, flap against
the cover, prongs through the stack) omits
``MatingContract`` (grandfathered) and relies on the flat articulation-origin
baseline + element-scoped ``allow_overlap``, mirroring shopping_bucket's bail
pivot treatment.
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
    Inertial,
    Mimic,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_cadquery,
)

__modular__ = True

CornerStyle = Literal["rounded_corners", "square_corners"]
TabStyle = Literal["rect_index_left", "rect_index_center", "full_width_straight"]
SpineStyle = Literal["rounded_fold", "accordion_gusset"]
Interior = Literal["plain", "divider_panels"]
Closure = Literal["none", "top_flap", "prong_fastener"]
MaterialStyle = Literal["manila", "green", "blue", "red"]

CORNER_STYLES: tuple[CornerStyle, ...] = ("rounded_corners", "square_corners")
TAB_STYLES: tuple[TabStyle, ...] = (
    "rect_index_left",
    "rect_index_center",
    "full_width_straight",
)
SPINE_STYLES: tuple[SpineStyle, ...] = ("rounded_fold", "accordion_gusset")
INTERIORS: tuple[Interior, ...] = ("plain", "divider_panels")
CLOSURES: tuple[Closure, ...] = ("none", "top_flap", "prong_fastener")
MATERIAL_STYLES: tuple[MaterialStyle, ...] = ("manila", "green", "blue", "red")

# Multiplicity domains (spec §8).
N_TABS_MIN, N_TABS_MAX = 1, 4
N_PAGES_MIN, N_PAGES_MAX = 2, 8
N_PLEATS_MIN, N_PLEATS_MAX = 4, 8

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "manila": {
        "cover": (0.86, 0.78, 0.55, 1.0),
        "cover_dark": (0.74, 0.66, 0.44, 1.0),
        "page": (0.95, 0.95, 0.93, 1.0),
        "line": (0.22, 0.30, 0.52, 1.0),
        "accent": (0.62, 0.55, 0.36, 1.0),
        "metal": (0.66, 0.67, 0.69, 1.0),
    },
    "green": {
        "cover": (0.36, 0.70, 0.20, 1.0),
        "cover_dark": (0.30, 0.60, 0.16, 1.0),
        "page": (0.93, 0.94, 0.95, 1.0),
        "line": (0.20, 0.22, 0.26, 1.0),
        "accent": (0.24, 0.48, 0.13, 1.0),
        "metal": (0.62, 0.63, 0.65, 1.0),
    },
    "blue": {
        "cover": (0.20, 0.40, 0.74, 1.0),
        "cover_dark": (0.15, 0.31, 0.60, 1.0),
        "page": (0.94, 0.95, 0.96, 1.0),
        "line": (0.16, 0.18, 0.24, 1.0),
        "accent": (0.12, 0.26, 0.52, 1.0),
        "metal": (0.64, 0.66, 0.70, 1.0),
    },
    "red": {
        "cover": (0.78, 0.22, 0.20, 1.0),
        "cover_dark": (0.62, 0.16, 0.15, 1.0),
        "page": (0.95, 0.94, 0.93, 1.0),
        "line": (0.24, 0.18, 0.18, 1.0),
        "accent": (0.55, 0.13, 0.12, 1.0),
        "metal": (0.66, 0.64, 0.62, 1.0),
    },
}

# ---------------------------------------------------------------------------
# Base real-world dimensions (meters). Letter-size file folder (parent S0).
# ---------------------------------------------------------------------------
_COVER_W = 0.300  # folder width along X (spine runs along X)
_COVER_H = 0.240  # cover height (Z above the spine fold)
_COVER_T = 0.0016  # card stock thickness (Y)
_CORNER_R = 0.006  # rounded outer cover corners

_TAB_W = 0.110  # narrow index tab width along X
_TAB_H = 0.022  # tab projection above the cover top edge
_TAB_MARGIN = 0.020  # min gap from cover edge for the tab row

_SPINE_R = 0.004  # rounded single-fold spine radius
_GUSSET_DEPTH = 0.030  # accordion gusset total depth along Y
_GUSSET_RISE = 0.016  # pleat facet vertical rise

_PAGE_W = 0.282  # captured page width
_PAGE_H = 0.225  # captured page height
_PAGE_T = 0.0010  # single sheet thickness
_STACK_GAP = 0.0016  # spacing between captured pages
_STACK_Z = 0.004  # page bottom z (above the spine fold)

_COVER_GAP = 0.010  # interior gap between covers (closed/ajar)

# Spine-hinge kinematics (Contract 3c: single-sourced so the front cover and the
# captured loose sheet share one ordered angular relationship).
#
# The front cover and the loose lifting sheet both hinge about the SAME bottom
# spine line and both swing out toward +Y. Independent overlapping angular ranges
# make the flat sheet panel pass straight through the flat cover panel (genuine
# 穿模) whenever the sheet is posed more open than the cover — e.g. cover closed
# but sheet lifted. Physically the captured sheet can only rise into the space the
# cover has vacated: its motion is DERIVED from the cover's, never independent.
#
# So the loose sheet MIMICS the front cover with a multiplier < 1. Because the
# sheet's hinge pivot sits at a smaller +Y than the cover's (it is behind the
# cover in the stack) AND it always opens by a strictly smaller angle, the sheet
# panel stays behind the cover panel at every common height at every pose — no
# interpenetration is possible for any source angle in [0, FRONT_HINGE_UPPER].
_FRONT_HINGE_UPPER = 1.4  # front cover open sweep (rad)
_SHEET_MIMIC_MULTIPLIER = 0.62  # loose sheet trails the cover at this fraction
_SHEET_HINGE_UPPER = _FRONT_HINGE_UPPER * _SHEET_MIMIC_MULTIPLIER
_STACK_BASE_Y = _COVER_T + 0.0008  # front face of the back cover: page/sheet stack origin
# The loose sheet hinge sits this far BEHIND the front cover's inner face (which
# is at +Y ``_COVER_GAP``, since the front panel extrudes toward -Y from its pivot
# at ``_COVER_GAP + _COVER_T``). Tying the sheet pivot to the top of the page
# stack instead let a tall stack (large n_pages) push it flush against the cover's
# inner face, so their base triangles grazed all through the coupled swing. A
# fixed clearance keeps a real spine-line gap that only widens with height.
_SHEET_SPINE_CLEARANCE = 0.005

# Top flap (closure=top_flap).
_FLAP_H = 0.170  # flap height (~70% of cover)

# Prong fastener (closure=prong_fastener).
_STRIP_W = 0.100
_STRIP_H = 0.018
_STRIP_T = 0.0012
_STRIP_Z = 0.015  # strip bottom edge z
_PRONG_W = 0.008
_PRONG_H = 0.065
_PRONG_T = 0.0006
_PRONG_SPACING = 0.080

# Divider panels (interior=divider_panels).
_DIV_W = 0.278
_DIV_H = 0.215
_DIV_T = 0.0012


@dataclass(frozen=True)
class FolderConfig:
    corner_style: CornerStyle | None = None
    tab_style: TabStyle | None = None
    spine_style: SpineStyle | None = None
    interior: Interior | None = None
    closure: Closure | None = None
    n_tabs: int | None = None
    n_pages: int | None = None
    n_pleats: int | None = None
    material_style: MaterialStyle = "manila"
    cover_w_scale: float = 1.0
    cover_h_scale: float = 1.0
    tab_proj_scale: float = 1.0
    flap_reach_scale: float = 1.0
    name: str = "folder"


@dataclass(frozen=True)
class ResolvedFolderConfig:
    corner_style: CornerStyle
    tab_style: TabStyle
    spine_style: SpineStyle
    interior: Interior
    closure: Closure
    n_tabs: int
    n_pages: int
    n_pleats: int
    material_style: MaterialStyle
    # Concrete geometry (scaled).
    cover_w: float
    cover_h: float
    cover_t: float
    corner_r: float
    tab_w: float
    tab_h: float
    cover_gap: float
    stack_gap: float
    flap_h: float
    name: str

    @property
    def is_square(self) -> bool:
        return self.corner_style == "square_corners"

    @property
    def is_full_tab(self) -> bool:
        return self.tab_style == "full_width_straight"


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> FolderConfig:
    rng = random.Random(seed)
    # Weighted procedural sampling (spec §9): optional closures / dividers and
    # square corners are rarer; small page/tab counts are more common.
    corner = rng.choices(CORNER_STYLES, weights=[6, 4], k=1)[0]
    tab = rng.choices(TAB_STYLES, weights=[5, 3, 3], k=1)[0]
    spine = rng.choices(SPINE_STYLES, weights=[6, 4], k=1)[0]
    interior = rng.choices(INTERIORS, weights=[6, 4], k=1)[0]
    closure = rng.choices(CLOSURES, weights=[6, 3, 3], k=1)[0]
    # full-width straight tab is a single continuous tab.
    n_tabs = (
        1
        if tab == "full_width_straight"
        else rng.choices([1, 2, 3, 4], weights=[5, 3, 3, 1], k=1)[0]
    )
    n_pages = rng.choices([2, 3, 4, 5, 6, 7, 8], weights=[3, 5, 4, 3, 2, 2, 1], k=1)[0]
    n_pleats = rng.choices([4, 5, 6, 7, 8], weights=[3, 4, 4, 2, 1], k=1)[0]
    return FolderConfig(
        corner_style=corner,
        tab_style=tab,
        spine_style=spine,
        interior=interior,
        closure=closure,
        n_tabs=n_tabs,
        n_pages=n_pages,
        n_pleats=n_pleats,
        material_style=rng.choice(MATERIAL_STYLES),
        cover_w_scale=round(rng.uniform(0.90, 1.12), 4),
        cover_h_scale=round(rng.uniform(0.90, 1.12), 4),
        tab_proj_scale=round(rng.uniform(0.85, 1.20), 4),
        flap_reach_scale=round(rng.uniform(0.85, 1.10), 4),
        name=f"seeded_folder_{seed}",
    )


def resolve_config(config: FolderConfig | None = None) -> ResolvedFolderConfig:
    cfg = config or FolderConfig()
    corner = _pick(cfg.corner_style, CORNER_STYLES)
    tab = _pick(cfg.tab_style, TAB_STYLES)
    spine = _pick(cfg.spine_style, SPINE_STYLES)
    interior = _pick(cfg.interior, INTERIORS)
    closure = _pick(cfg.closure, CLOSURES)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)

    n_tabs = int(_clamp(cfg.n_tabs if cfg.n_tabs is not None else 1, N_TABS_MIN, N_TABS_MAX))
    # full-width straight tab is a single continuous tab (spec §9 gating).
    if tab == "full_width_straight":
        n_tabs = 1
    n_pages = int(_clamp(cfg.n_pages if cfg.n_pages is not None else 3, N_PAGES_MIN, N_PAGES_MAX))
    n_pleats = int(
        _clamp(cfg.n_pleats if cfg.n_pleats is not None else 6, N_PLEATS_MIN, N_PLEATS_MAX)
    )

    ws = _clamp(cfg.cover_w_scale, 0.90, 1.12)
    hs = _clamp(cfg.cover_h_scale, 0.90, 1.12)
    tps = _clamp(cfg.tab_proj_scale, 0.85, 1.20)
    frs = _clamp(cfg.flap_reach_scale, 0.85, 1.10)

    cover_w = _COVER_W * ws
    cover_h = _COVER_H * hs
    corner_r = 0.0 if corner == "square_corners" else _CORNER_R

    # Tab footprint: narrow index tab width, clamped so the staggered row fits
    # inside the cover top edge (spec §7 inequality).
    if tab == "full_width_straight":
        tab_w = cover_w - 2.0 * _TAB_MARGIN
    else:
        usable = cover_w - 2.0 * _TAB_MARGIN
        # n_tabs cells across the usable top edge; tab occupies 70% of its cell.
        tab_w = min(_TAB_W, 0.70 * usable / n_tabs)
    tab_h = _TAB_H * tps

    # Captured page stack must fit inside the interior gap (spec §7 inequality).
    stack_gap = _STACK_GAP
    if n_pages * stack_gap > _COVER_GAP - 0.002:
        stack_gap = max(0.0006, (_COVER_GAP - 0.002) / n_pages)

    flap_h = _FLAP_H * frs

    return ResolvedFolderConfig(
        corner_style=corner,
        tab_style=tab,
        spine_style=spine,
        interior=interior,
        closure=closure,
        n_tabs=n_tabs,
        n_pages=n_pages,
        n_pleats=n_pleats,
        material_style=material_style,
        cover_w=cover_w,
        cover_h=cover_h,
        cover_t=_COVER_T,
        corner_r=corner_r,
        tab_w=tab_w,
        tab_h=tab_h,
        cover_gap=_COVER_GAP,
        stack_gap=stack_gap,
        flap_h=flap_h,
        name=cfg.name or "folder",
    )


def with_overrides(config: FolderConfig, **kwargs: object) -> FolderConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: FolderConfig | ResolvedFolderConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedFolderConfig) else resolve_config(config)
    spine = r.spine_style + (f"_p{r.n_pleats}" if r.spine_style == "accordion_gusset" else "")
    return (
        ("corner_style", r.corner_style),
        ("tab_style", r.tab_style),
        ("spine_style", spine),
        ("interior", r.interior),
        ("closure", r.closure),
        ("tabs", f"tabs_{r.n_tabs}"),
        ("pages", f"pages_{r.n_pages}"),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ---------------------------------------------------------------------------
# Tab layout
# ---------------------------------------------------------------------------
def _tab_centers(r: ResolvedFolderConfig) -> list[float]:
    """X centers (in cover-local 0..cover_w frame) for the staggered tab row."""
    if r.is_full_tab:
        return [r.cover_w / 2.0]
    usable = r.cover_w - 2.0 * _TAB_MARGIN
    left = _TAB_MARGIN
    if r.n_tabs == 1:
        if r.tab_style == "rect_index_center":
            return [r.cover_w / 2.0]
        # rect_index_left: left third.
        return [left + r.tab_w / 2.0 + 0.010]
    step = usable / r.n_tabs
    return [left + (i + 0.5) * step for i in range(r.n_tabs)]


def _sheet_hinge_origin_y(r: ResolvedFolderConfig) -> float:
    """+Y of the loose-sheet hinge, pinned a fixed clearance behind the front cover.

    Single-sourced (Contract 3c). The front cover's inner face sits at +Y
    ``cover_gap`` (its pivot is at ``cover_gap + cover_t`` and the panel extrudes
    toward -Y). Placing the sheet hinge at ``cover_gap - clearance`` — independent
    of ``n_pages`` — guarantees the mimic-coupled sheet trails the cover with a
    real spine-line gap at every pose, so their base triangles never graze. The
    sheet still seats within the captured page stack (``back``/``loose`` overlap
    is allowed), it just no longer rides the very top of a tall stack.
    """
    return r.cover_gap - _SHEET_SPINE_CLEARANCE


# ---------------------------------------------------------------------------
# Geometry helpers (authored in the cover-local frame: x=0..cover_w,
# z=0..cover_h, thickness along +Y).
# ---------------------------------------------------------------------------
def _cover_profile(r: ResolvedFolderConfig, *, with_tab: bool, assets, name: str):
    w = r.cover_w
    h = r.cover_h
    body = (
        cq.Workplane("XZ").transformed(offset=(w / 2.0, h / 2.0, 0.0)).rect(w, h).extrude(r.cover_t)
    )
    if r.corner_r > 0.0:
        body = body.edges("|Y").fillet(r.corner_r)

    if with_tab:
        for cx in _tab_centers(r):
            tab = (
                cq.Workplane("XZ")
                .transformed(offset=(cx, h + r.tab_h / 2.0, 0.0))
                .rect(r.tab_w, r.tab_h + 2.0 * max(r.corner_r, 0.004))
                .extrude(r.cover_t)
            )
            if r.corner_r > 0.0:
                tab = tab.edges("|Y").fillet(min(r.corner_r, r.tab_h / 2.5))
            body = body.union(tab)
    return mesh_from_cadquery(body, name, assets=assets)


def _spine_rounded_mesh(r: ResolvedFolderConfig, *, assets):
    w = r.cover_w
    depth = r.cover_gap + 2.0 * r.cover_t
    bar = (
        cq.Workplane("XY")
        .transformed(offset=(w / 2.0, depth / 2.0, _SPINE_R))
        .box(w, depth, 2.0 * _SPINE_R)
        .edges("|X")
        .fillet(_SPINE_R * 0.9)
    )
    return mesh_from_cadquery(bar, "spine_fold", assets=assets)


def _pleat_facet(r: ResolvedFolderConfig, *, y0: float, dy: float, up: bool):
    """One accordion pleat facet: a slanted thin bar spanning the cover width."""
    w = r.cover_w
    z0 = 0.0
    z1 = _GUSSET_RISE if up else 0.0
    z_lo = 0.0 if up else _GUSSET_RISE
    # Build a slanted thin slab via a 4-point profile on the YZ plane swept in X.
    pts = [
        (y0, z0 if up else z_lo),
        (y0 + dy, z1 if up else z0),
        (y0 + dy, (z1 if up else z0) + _SPINE_R * 1.4),
        (y0, (z0 if up else z_lo) + _SPINE_R * 1.4),
    ]
    facet = cq.Workplane("YZ").polyline(pts).close().extrude(w)
    return facet


def _spine_accordion_mesh(r: ResolvedFolderConfig, *, assets):
    dy = _GUSSET_DEPTH / r.n_pleats
    facet = None
    for i in range(r.n_pleats):
        y0 = i * dy
        up = i % 2 == 0
        f = _pleat_facet(r, y0=y0, dy=dy, up=up)
        facet = f if facet is None else facet.union(f)
    return mesh_from_cadquery(facet, "spine_gusset", assets=assets)


def _page_mesh(width: float, height: float, thickness: float, name: str, *, assets):
    page = (
        cq.Workplane("XZ")
        .transformed(offset=(width / 2.0, height / 2.0, 0.0))
        .rect(width, height)
        .extrude(thickness)
    )
    return mesh_from_cadquery(page, name, assets=assets)


def _ruled_lines_mesh(width: float, height: float, thickness: float, *, assets):
    lines = None
    n = 16
    margin = 0.020
    usable = height - 2.0 * margin
    for i in range(n):
        z = margin + (i + 0.5) * usable / n
        bar = (
            cq.Workplane("XZ")
            .transformed(offset=(width / 2.0, z, 0.0))
            .rect(width - 2.0 * margin, 0.0009)
            .extrude(thickness)
        )
        lines = bar if lines is None else lines.union(bar)
    return mesh_from_cadquery(lines, "loose_lines", assets=assets)


def _divider_mesh(assets):
    panel = (
        cq.Workplane("XZ")
        .transformed(offset=(_DIV_W / 2.0, _DIV_H / 2.0, 0.0))
        .rect(_DIV_W, _DIV_H)
        .extrude(_DIV_T)
    )
    return mesh_from_cadquery(panel, "divider_panel", assets=assets)


def _flap_mesh(r: ResolvedFolderConfig, *, assets):
    """Fold-over flap: hinge edge at part z=0, panel hangs in -Z (closed)."""
    w = r.cover_w
    h = r.flap_h
    body = (
        cq.Workplane("XZ")
        .transformed(offset=(w / 2.0, -h / 2.0, 0.0))
        .rect(w, h)
        .extrude(r.cover_t)
    )
    if r.corner_r > 0.0:
        body = body.edges("|Y").fillet(r.corner_r)
    return mesh_from_cadquery(body, "top_flap", assets=assets)


def _fastener_strip_mesh(assets):
    strip = (
        cq.Workplane("XZ")
        .transformed(offset=(_STRIP_W / 2.0, _STRIP_H / 2.0, 0.0))
        .rect(_STRIP_W, _STRIP_H)
        .extrude(_STRIP_T)
    )
    return mesh_from_cadquery(strip, "fastener_strip", assets=assets)


def _prong_mesh(assets):
    """Upright prong tongue: hinge base at part z=0, tongue rises in +Z."""
    tongue = (
        cq.Workplane("XZ")
        .transformed(offset=(0.0, _PRONG_H / 2.0, 0.0))
        .rect(_PRONG_W, _PRONG_H)
        .extrude(_PRONG_T)
    )
    tongue = tongue.edges("|Y").fillet(_PRONG_W * 0.4)
    return mesh_from_cadquery(tongue, "prong_tongue", assets=assets)


# ---------------------------------------------------------------------------
# Emit helpers
# ---------------------------------------------------------------------------
def _emit_pages(model, r, back, mats, *, assets) -> None:
    x_off = (r.cover_w - _PAGE_W) / 2.0
    page_mesh = _page_mesh(_PAGE_W, _PAGE_H, _PAGE_T, "stack_page", assets=assets)
    for i in range(r.n_pages):
        y = _STACK_BASE_Y + i * r.stack_gap
        back.visual(
            page_mesh,
            origin=Origin(xyz=(x_off, y, _STACK_Z)),
            material=mats["page"],
            name=f"stack_page_{i}", material_class_id="paper.plain_sheet",
        )


def _emit_dividers(model, r, back, mats, *, assets) -> None:
    if r.interior != "divider_panels":
        return
    x_off = (r.cover_w - _DIV_W) / 2.0
    div_mesh = _divider_mesh(assets)
    # Two dividers at regular interior depths, behind/around the page stack.
    base_y = r.cover_t + 0.0008
    depth_span = r.cover_gap - 0.002
    for i in range(2):
        y = base_y + (i + 1) * depth_span / 3.0
        back.visual(
            div_mesh,
            origin=Origin(xyz=(x_off, y, _STACK_Z)),
            material=mats["accent"],
            name=f"divider_{i}", material_class_id="paper.cardboard",
        )


def _emit_closure(model, r, back, front, mats, *, assets) -> list[str]:
    if r.closure == "top_flap":
        flap = model.part("top_flap")
        flap.visual(_flap_mesh(r, assets=assets), material=mats["cover"], name="flap_panel", material_class_id="paper.cardboard")
        flap.inertial = Inertial.from_geometry(
            Box((r.cover_w, r.cover_t, r.flap_h)),
            mass=0.02,
            origin=Origin(xyz=(0.0, 0.0, -r.flap_h / 2.0)),
        )
        # REVOLUTE about +X at the front cover top edge; q=0 closed (hangs over
        # the front face), positive q lifts the free edge up and back.
        model.articulation(
            "flap_hinge",
            ArticulationType.REVOLUTE,
            parent=front,
            child=flap,
            origin=Origin(xyz=(0.0, r.cover_t, r.cover_h)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=math.pi),
        )
        return ["top_flap"]

    if r.closure == "prong_fastener":
        # Fixed fastener strip plate is an inline back-cover visual.
        strip_x = (r.cover_w - _STRIP_W) / 2.0
        back.visual(
            _fastener_strip_mesh(assets),
            origin=Origin(xyz=(strip_x, r.cover_t, _STRIP_Z)),
            material=mats["metal"],
            name="fastener_strip", material_class_id="metal.stainless_matte",
        )
        names = []
        prong_mesh = _prong_mesh(assets)
        x_center = r.cover_w / 2.0
        x_offsets = [x_center - _PRONG_SPACING / 2.0 + i * _PRONG_SPACING for i in range(2)]
        prong_base_z = _STRIP_Z + _STRIP_H
        prong_base_y = r.cover_t + _STRIP_T
        for i in range(2):
            prong = model.part(f"prong_{i}")
            prong.visual(prong_mesh, material=mats["metal"], name=f"prong_tongue_{i}", material_class_id="metal.stainless_matte")
            prong.inertial = Inertial.from_geometry(
                Box((_PRONG_W, _PRONG_T, _PRONG_H)),
                mass=0.003,
                origin=Origin(xyz=(0.0, 0.0, _PRONG_H / 2.0)),
            )
            # REVOLUTE about -X at the prong base on the strip top; positive q
            # bends the tongue toward +Y, clamping over the page stack.
            model.articulation(
                f"prong_bend_{i}",
                ArticulationType.REVOLUTE,
                parent=back,
                child=prong,
                origin=Origin(xyz=(x_offsets[i], prong_base_y, prong_base_z)),
                axis=(-1.0, 0.0, 0.0),
                motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=0.0, upper=1.6),
            )
            names.append(f"prong_{i}")
        return names

    return []


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
def build_folder(
    config: FolderConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.material_style]
    mats = {
        key: model.material(f"folder_{key}_{r.material_style}", rgba=palette[key])
        for key in ("cover", "cover_dark", "page", "line", "accent", "metal")
    }

    # --- Back cover (root). Hinge edge (bottom fold) at local z=0, cover rising
    #     along +Z, slab thickness along +Y. Carries inline spine + pages. ---
    back = model.part("back_cover")
    back.visual(
        _cover_profile(r, with_tab=False, assets=assets, name="back_cover"),
        material=mats["cover"],
        name="back_panel", material_class_id="paper.cardboard",
    )
    if r.spine_style == "accordion_gusset":
        back.visual(
            _spine_accordion_mesh(r, assets=assets), material=mats["cover_dark"], name="spine", material_class_id="paper.cardboard"
        )
    else:
        back.visual(
            _spine_rounded_mesh(r, assets=assets), material=mats["cover_dark"], name="spine", material_class_id="paper.cardboard"
        )
    back.inertial = Inertial.from_geometry(
        Box((r.cover_w, r.cover_t, r.cover_h)),
        mass=0.05,
        origin=Origin(xyz=(r.cover_w / 2.0, r.cover_t / 2.0, r.cover_h / 2.0)),
    )

    _emit_pages(model, r, back, mats, assets=assets)
    _emit_dividers(model, r, back, mats, assets=assets)

    # --- Front cover: REVOLUTE child swinging open about the bottom spine. ---
    front = model.part("front_cover")
    front.visual(
        _cover_profile(r, with_tab=True, assets=assets, name="front_cover"),
        material=mats["cover"],
        name="front_panel", material_class_id="paper.cardboard",
    )
    front.inertial = Inertial.from_geometry(
        Box((r.cover_w, r.cover_t, r.cover_h)),
        mass=0.05,
        origin=Origin(xyz=(r.cover_w / 2.0, r.cover_t / 2.0, r.cover_h / 2.0)),
    )
    model.articulation(
        "spine_hinge_front",
        ArticulationType.REVOLUTE,
        parent=back,
        child=front,
        origin=Origin(xyz=(0.0, r.cover_gap + r.cover_t, 0.0)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=_FRONT_HINGE_UPPER),
    )

    # --- Loose sheet lifting out: REVOLUTE child of the back cover. ---
    loose = model.part("loose_sheet")
    loose.visual(
        _page_mesh(_PAGE_W, _PAGE_H, _PAGE_T, "loose_sheet", assets=assets),
        material=mats["page"],
        name="loose_panel", material_class_id="paper.plain_sheet",
    )
    loose.visual(
        _ruled_lines_mesh(_PAGE_W, _PAGE_H, _PAGE_T * 1.4, assets=assets),
        origin=Origin(xyz=(0.0, _PAGE_T * 0.5, 0.0)),
        material=mats["line"],
        name="loose_lines", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    loose.inertial = Inertial.from_geometry(
        Box((_PAGE_W, _PAGE_T, _PAGE_H)),
        mass=0.01,
        origin=Origin(xyz=(_PAGE_W / 2.0, _PAGE_T / 2.0, _PAGE_H / 2.0)),
    )
    # The sheet MIMICS the front cover (spine_hinge_front): as the cover opens the
    # captured sheet lifts to a fraction of that angle, always trailing strictly
    # inside the cover panel. This removes the independent overlapping-range 穿模
    # (sheet posed more open than the cover) by construction — the QC only poses
    # the source cover joint and derives the sheet pose from it.
    model.articulation(
        "spine_hinge_sheet",
        ArticulationType.REVOLUTE,
        parent=back,
        child=loose,
        origin=Origin(xyz=((r.cover_w - _PAGE_W) / 2.0, _sheet_hinge_origin_y(r), 0.0)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=2.0, velocity=2.0, lower=0.0, upper=_SHEET_HINGE_UPPER),
        mimic=Mimic("spine_hinge_front", multiplier=_SHEET_MIMIC_MULTIPLIER),
    )

    _emit_closure(model, r, back, front, mats, assets=assets)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_folder(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_folder(config_from_seed(seed), assets=assets)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def run_folder_tests(
    object_model: ArticulatedObject,
    config: FolderConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    back = object_model.get_part("back_cover")
    front = object_model.get_part("front_cover")
    loose = object_model.get_part("loose_sheet")

    # --- Captured / seated allowances for the articulated children. ---
    ctx.allow_overlap(
        back,
        front,
        reason=(
            "front cover hinges about the bottom spine; closed it rests against "
            "the captured page stack and shares the spine fold geometry."
        ),
    )
    ctx.allow_overlap(
        back,
        loose,
        reason="loose sheet seats inside the captured page stack at the spine line.",
    )
    if r.closure == "top_flap":
        ctx.allow_isolated_part(
            object_model.get_part("top_flap"),
            reason="fold-over flap opens clear of the folder and loses contact",
        )
        ctx.allow_overlap(
            front,
            object_model.get_part("top_flap"),
            reason="closed fold-over flap rests against the front cover outer face.",
        )
    elif r.closure == "prong_fastener":
        for i in range(2):
            prong = object_model.get_part(f"prong_{i}")
            ctx.allow_overlap(
                back,
                prong,
                reason="prong tongue rises from the fastener strip through the page stack (captured bend pivot).",
            )
            ctx.allow_overlap(
                loose,
                prong,
                reason=(
                    "the loose sheet seats within the captured page stack; when the "
                    "prong fastener bends over it clamps down onto that sheet (seated "
                    "captured contact, the fastener's purpose)."
                ),
            )

    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    # Captured/seated hinge joints omit MatingContract (grandfathered); the flat
    # 0.015 m articulation-origin baseline runs in the compiler and all origins
    # sit on real hardware (spine line / cover top edge / strip top / cover edge).
    ctx.fail_if_joint_mating_has_gap()

    # --- Core spine hinges are REVOLUTE about the X (spine) axis. ---
    jf = object_model.get_articulation("spine_hinge_front")
    js = object_model.get_articulation("spine_hinge_sheet")
    ctx.check(
        "front cover hinge is REVOLUTE about X (spine)",
        jf.articulation_type == ArticulationType.REVOLUTE and round(abs(jf.axis[0]), 3) == 1.0,
        details=f"type={jf.articulation_type} axis={tuple(round(c, 3) for c in jf.axis)}",
    )
    ctx.check(
        "loose sheet hinge is REVOLUTE about X (spine)",
        js.articulation_type == ArticulationType.REVOLUTE and round(abs(js.axis[0]), 3) == 1.0,
        details=f"type={js.articulation_type} axis={tuple(round(c, 3) for c in js.axis)}",
    )

    # --- HERO motion: opening the front cover swings its top edge forward. ---
    rest = ctx.part_world_aabb(front)
    with ctx.pose({jf: 1.2}):
        opened = ctx.part_world_aabb(front)
    if rest is not None and opened is not None:
        ctx.check(
            "opening front cover swings its top edge forward (+Y)",
            opened[1][1] > rest[1][1] + 0.05,
            details=f"rest_y={rest[1][1]:.3f} open_y={opened[1][1]:.3f}",
        )

    # --- Loose sheet is mimic-coupled to the front cover (no independent DOF that
    #     would drive the flat sheet through the flat cover). ---
    ctx.check(
        "loose sheet hinge mimics the front cover hinge",
        js.mimic is not None and js.mimic.joint == "spine_hinge_front",
        details=f"mimic={js.mimic}",
    )
    ctx.check(
        "loose sheet mimic multiplier trails the cover (0 < m < 1)",
        js.mimic is not None and 0.0 < js.mimic.multiplier < 1.0,
        details=f"multiplier={None if js.mimic is None else js.mimic.multiplier}",
    )

    # --- HERO motion: opening the front cover lifts the captured sheet out (+Y),
    #     and the sheet stays strictly inside (behind, smaller +Y than) the cover
    #     panel across the whole open sweep — never passing through it. ---
    rest_s = ctx.part_world_aabb(loose)
    with ctx.pose({jf: _FRONT_HINGE_UPPER}):
        lifted = ctx.part_world_aabb(loose)
        cover_open = ctx.part_world_aabb(front)
    if rest_s is not None and lifted is not None:
        ctx.check(
            "opening the cover lifts the coupled loose sheet out (+Y)",
            lifted[1][1] > rest_s[1][1] + 0.05,
            details=f"rest_y={rest_s[1][1]:.3f} lifted_y={lifted[1][1]:.3f}",
        )
    if lifted is not None and cover_open is not None:
        ctx.check(
            "loose sheet stays behind (inside) the front cover panel when open",
            lifted[1][1] < cover_open[1][1] + 1e-4,
            details=f"sheet_max_y={lifted[1][1]:.4f} cover_max_y={cover_open[1][1]:.4f}",
        )

    # --- Covers share the bottom spine line (no floating cover). ---
    f_aabb = ctx.part_world_aabb(front)
    b_aabb = ctx.part_world_aabb(back)
    if f_aabb is not None and b_aabb is not None:
        ctx.check(
            "front and back covers share the bottom spine line",
            abs(f_aabb[0][2] - b_aabb[0][2]) < 0.02 and f_aabb[0][2] < 0.02,
            details=f"front_bottom={f_aabb[0][2]:.3f} back_bottom={b_aabb[0][2]:.3f}",
        )
        ctx.check(
            "front cover spans the folder width",
            (f_aabb[1][0] - f_aabb[0][0]) > r.cover_w - 0.03,
            details=f"front_w={f_aabb[1][0] - f_aabb[0][0]:.3f} cover_w={r.cover_w:.3f}",
        )

    # --- Tab projects above the cover top edge. ---
    if f_aabb is not None and b_aabb is not None:
        ctx.check(
            "labeling tab projects above the cover top edge",
            f_aabb[1][2] > b_aabb[1][2] + r.tab_h * 0.4,
            details=f"front_top={f_aabb[1][2]:.3f} back_top={b_aabb[1][2]:.3f}",
        )

    # --- Captured page stack present and inside the footprint. ---
    page0 = back.get_visual("stack_page_0")
    ctx.check("captured page stack present", page0 is not None, details="stack_page_0 missing")
    expected_pages = r.n_pages
    page_count = sum(1 for v in back.visuals if v.name.startswith("stack_page_"))
    ctx.check(
        "captured page stack emits the expected count",
        page_count == expected_pages,
        details=f"emitted={page_count} expected={expected_pages}",
    )

    # --- Spine inline visual present (rounded fold or accordion gusset). ---
    ctx.check(
        "spine is an inline back-cover visual",
        "spine" in {v.name for v in back.visuals},
        details=str([v.name for v in back.visuals]),
    )

    # --- Tab multiplicity: tab count matches (best-effort via tab centers). ---
    expected_tab_centers = 1 if r.is_full_tab else r.n_tabs
    ctx.check(
        "tab layout matches n_tabs",
        len(_tab_centers(r)) == expected_tab_centers,
        details=f"centers={len(_tab_centers(r))} expected={expected_tab_centers}",
    )

    # --- Interior dividers (optional). ---
    if r.interior == "divider_panels":
        div_count = sum(1 for v in back.visuals if v.name.startswith("divider_"))
        ctx.check(
            "two interior divider panels emitted as inline visuals",
            div_count == 2,
            details=f"dividers={div_count}",
        )

    # --- Closure (optional moving children). ---
    if r.closure == "top_flap":
        jc = object_model.get_articulation("flap_hinge")
        ctx.check(
            "top flap is REVOLUTE about +X",
            jc.articulation_type == ArticulationType.REVOLUTE and round(jc.axis[0], 3) == 1.0,
            details=f"type={jc.articulation_type} axis={tuple(round(c, 3) for c in jc.axis)}",
        )
        flap = object_model.get_part("top_flap")
        with ctx.pose({jc: 0.0}):
            c0 = ctx.part_world_aabb(flap)
        with ctx.pose({jc: 2.0}):
            c1 = ctx.part_world_aabb(flap)
        if c0 is not None and c1 is not None:
            ctx.check(
                "opening the flap raises its free edge",
                c1[1][2] > c0[1][2] + 0.01,
                details=f"closed_top={c0[1][2]:.3f} open_top={c1[1][2]:.3f}",
            )
    elif r.closure == "prong_fastener":
        ctx.check(
            "fastener strip is an inline back-cover visual",
            "fastener_strip" in {v.name for v in back.visuals},
            details=str([v.name for v in back.visuals]),
        )
        for i in range(2):
            jprong = object_model.get_articulation(f"prong_bend_{i}")
            ctx.check(
                f"prong_bend_{i} is REVOLUTE about -X",
                jprong.articulation_type == ArticulationType.REVOLUTE
                and round(jprong.axis[0], 3) == -1.0,
                details=f"type={jprong.articulation_type} axis={tuple(round(c, 3) for c in jprong.axis)}",
            )

    # --- slot_choices recorded. ---
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "FolderConfig",
    "ResolvedFolderConfig",
    "build_folder",
    "build_seeded_folder",
    "config_from_seed",
    "resolve_config",
    "run_folder_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
