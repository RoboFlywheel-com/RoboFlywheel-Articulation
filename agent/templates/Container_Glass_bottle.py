# SPDX-License-Identifier: Apache-2.0

"""Container glass bottle — modular procedural template.

Category identity: an upright hollow **glass** vessel (beer / wine / oil /
dropper bottle). The translucent glass shell (ROOT ``bottle``) rests on z=0
with its axis along +Z; one closure mechanism opens/closes on top by one of
several motions (the main articulation). No multiplicity axis — one bottle,
one closure.

Two parallel slots (spec ``Container_Glass_bottle.md``):

  * ``bottle_body_profile`` (7) — the ROOT ``bottle`` glass-shell mesh
    (``outer.cut(inner)`` hollow open shell, translucent ``alpha < 1``):
    long_neck (beer), wine_bottle (high shoulder + punt), stubby_steinie
    (fat short neck), boston_round (cosine rounded shoulder), hip_flask
    (**non-circular** D/kidney loft — the only non-axisymmetric body),
    decanter_carafe (wide belly + long slim neck), slim_flute (continuous
    taper, ``revolve`` lathe). All bodies blend back to a circular neck bore
    so every closure interface (lip top, circular bore) is identical.
  * ``closure_mechanism`` (7) — the bottle-mouth closure (>=1 non-fixed joint
    each):
      - pry_off_crown_cap: PRISMATIC +Z pop-off crown cap (crimp skirt).
      - screw_cap: CONTINUOUS +Z screw cap + fixed neck_threads visual.
      - swing_top: REVOLUTE +Y wire-bail stopper (bail + plug + gasket) +
        fixed neck_collar visual.
      - cork: PRISMATIC +Z tapered cork pull.
      - dropper_pipette: PRISMATIC +Z dropper (collar + pipette tube + bulb).
      - pour_spout: fixed pour_spout insert + REVOLUTE +X flip_cap.
      - codd_marble: PRISMATIC -Z captive glass marble (Sphere) push-down +
        fixed rubber_ring torus; ``allow_isolated_part``.

Continuous size/proportion variation (height/radius/neck/closure/travel
scales) lives in ``resolve_config`` as clamped params, never as slot
candidates. ``palette_style`` (9 glass colorways + finish) is palette only and
is NOT a slot choice.

Sources (arti-template ``data/records`` 5-star pool): parent
``rec_dark-glass-beer-bottle-…_2a24ec81`` (long_neck body + crown cap), plus
``rec_container_glass_bottle_var_*`` forks for each body and closure family.

Canonical spec:
``articraft_template_authoring/specs_modular_v1/Container_Glass_bottle.md``
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
    Cylinder,
    Inertial,
    LatheGeometry,
    MotionLimits,
    Origin,
    Sphere,
    TestContext,
    TestReport,
    TorusGeometry,
    mesh_from_cadquery,
    mesh_from_geometry,
)

__modular__ = True

# ---------------------------------------------------------------------------
# Slot domains
# ---------------------------------------------------------------------------
BodyProfile = Literal[
    "long_neck",
    "wine_bottle",
    "stubby_steinie",
    "boston_round",
    "hip_flask",
    "decanter_carafe",
    "slim_flute",
]
ClosureMechanism = Literal[
    "pry_off_crown_cap",
    "screw_cap",
    "swing_top",
    "cork",
    "dropper_pipette",
    "pour_spout",
    "codd_marble",
]
PaletteStyle = Literal[
    "clear_flint",
    "green_wine",
    "amber_beer",
    "cobalt_blue",
    "olive_oil_green",
    "frosted_satin_white",
    "smoke_grey",
    "uv_violet",
    "opaline_milk",
]

BODY_PROFILES: tuple[BodyProfile, ...] = (
    "long_neck",
    "wine_bottle",
    "stubby_steinie",
    "boston_round",
    "hip_flask",
    "decanter_carafe",
    "slim_flute",
)
CLOSURE_MECHANISMS: tuple[ClosureMechanism, ...] = (
    "pry_off_crown_cap",
    "screw_cap",
    "swing_top",
    "cork",
    "dropper_pipette",
    "pour_spout",
    "codd_marble",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "clear_flint",
    "green_wine",
    "amber_beer",
    "cobalt_blue",
    "olive_oil_green",
    "frosted_satin_white",
    "smoke_grey",
    "uv_violet",
    "opaline_milk",
)

# ---------------------------------------------------------------------------
# Material palettes. Every glass tint carries alpha < 1 (Glass identity).
# finish is a viewer label only: gloss (low alpha), satin (frosted, higher
# alpha), opaque_matt (opaline, highest alpha but still < 1). Closure
# materials are coordinated per colorway from the shared hardware pool.
# ---------------------------------------------------------------------------
_METAL = (0.62, 0.60, 0.58, 1.0)
_GOLD = (0.55, 0.52, 0.18, 1.0)
_CORK = (0.76, 0.60, 0.42, 1.0)
_CERAMIC = (0.92, 0.88, 0.80, 1.0)
_RUBBER = (0.35, 0.08, 0.06, 1.0)
_SEAL_DARK = (0.10, 0.08, 0.06, 1.0)
_RED_FLIP = (0.70, 0.15, 0.12, 1.0)
_SPOUT_OFF_WHITE = (0.92, 0.90, 0.85, 1.0)
_CAP_COLLAR_DARK = (0.12, 0.12, 0.12, 1.0)
_PIPETTE_GLASS = (0.82, 0.85, 0.88, 0.55)
_BULB_RUBBER = (0.08, 0.06, 0.06, 1.0)
_MARBLE_GLASS = (0.82, 0.88, 0.86, 0.55)


@dataclass(frozen=True)
class _Palette:
    glass: tuple[float, float, float, float]
    finish: str  # gloss | satin | opaque_matt
    metal: tuple[float, float, float, float] = _METAL
    gold: tuple[float, float, float, float] = _GOLD
    cork: tuple[float, float, float, float] = _CORK
    ceramic: tuple[float, float, float, float] = _CERAMIC
    rubber: tuple[float, float, float, float] = _RUBBER
    seal: tuple[float, float, float, float] = _SEAL_DARK
    red_flip: tuple[float, float, float, float] = _RED_FLIP
    spout: tuple[float, float, float, float] = _SPOUT_OFF_WHITE
    collar: tuple[float, float, float, float] = _CAP_COLLAR_DARK
    pipette: tuple[float, float, float, float] = _PIPETTE_GLASS
    bulb: tuple[float, float, float, float] = _BULB_RUBBER
    marble: tuple[float, float, float, float] = _MARBLE_GLASS


PALETTES: dict[PaletteStyle, _Palette] = {
    "clear_flint": _Palette(glass=(0.82, 0.85, 0.88, 0.40), finish="gloss"),
    "green_wine": _Palette(glass=(0.06, 0.10, 0.05, 0.38), finish="gloss"),
    "amber_beer": _Palette(glass=(0.18, 0.12, 0.07, 0.40), finish="gloss"),
    "cobalt_blue": _Palette(glass=(0.05, 0.10, 0.30, 0.40), finish="gloss"),
    "olive_oil_green": _Palette(glass=(0.12, 0.13, 0.06, 0.45), finish="gloss"),
    "frosted_satin_white": _Palette(glass=(0.88, 0.90, 0.90, 0.62), finish="satin"),
    "smoke_grey": _Palette(glass=(0.22, 0.22, 0.24, 0.42), finish="gloss"),
    "uv_violet": _Palette(glass=(0.16, 0.05, 0.22, 0.42), finish="gloss"),
    "opaline_milk": _Palette(glass=(0.93, 0.92, 0.90, 0.80), finish="opaque_matt"),
}


def _material_class_id(
    surface: Literal[
        "bottle_glass",
        "closure_metal",
        "ceramic_stopper",
        "plug_gasket",
        "cork",
        "dropper_collar",
        "pipette_glass",
        "squeeze_bulb",
        "pour_spout",
        "flip_cap",
        "rubber_ring",
        "codd_marble",
    ],
    r: ResolvedContainerGlassBottleConfig,
) -> str:
    """Return the formal material pool for one bottle surface."""
    if surface == "bottle_glass":
        return (
            "glass.frosted_smooth"
            if r.palette_style in {"frosted_satin_white", "opaline_milk"}
            else "glass.clear_transparent"
        )
    return {
        "closure_metal": "metal.paint_coated",
        "ceramic_stopper": "ceramic.porcelain_glazed_plain",
        "plug_gasket": "rubber.smooth_plain",
        "cork": "organic.cork",
        "dropper_collar": "plastic.opaque_glossy_molded",
        "pipette_glass": "glass.clear_transparent",
        "squeeze_bulb": "rubber.smooth_plain",
        "pour_spout": "plastic.opaque_glossy_molded",
        "flip_cap": "plastic.opaque_glossy_molded",
        "rubber_ring": "rubber.smooth_plain",
        "codd_marble": "glass.clear_transparent",
    }[surface]


# ---------------------------------------------------------------------------
# Per-body nominal geometry. Every body shares the SAME closure interface:
# a circular lip of radius ``lip_r`` whose top face is at ``lip_top_z``, over
# a circular neck bore of ``bore_r`` at neck radius ``neck_r``. The silhouette
# differs (and hip_flask is non-circular below the neck) but the neck/lip is
# always circular so all 7 closures attach identically.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class _BodyGeom:
    lip_top_z: float
    body_r: float
    neck_r: float
    lip_r: float
    bore_r: float
    wall: float
    primitive: str  # loft | revolve | flask


_BODIES: dict[BodyProfile, _BodyGeom] = {
    # long_neck beer (parent baseline).
    "long_neck": _BodyGeom(0.230, 0.0325, 0.0115, 0.0135, 0.0085, 0.0028, "loft"),
    # wine: taller, fatter body, high shoulder + punt.
    "wine_bottle": _BodyGeom(0.283, 0.0375, 0.0140, 0.0148, 0.0085, 0.0028, "loft"),
    # stubby steinie: short, fat, very short neck.
    "stubby_steinie": _BodyGeom(0.142, 0.0400, 0.0125, 0.0135, 0.0085, 0.0028, "loft"),
    # boston round apothecary: cosine rounded shoulder, short neck.
    "boston_round": _BodyGeom(0.165, 0.0330, 0.0120, 0.0140, 0.0090, 0.0028, "loft"),
    # hip flask: non-circular D/kidney body, short narrow neck.
    "hip_flask": _BodyGeom(0.168, 0.0400, 0.0105, 0.0135, 0.0085, 0.0025, "flask"),
    # decanter / carafe: wide belly, long slim neck.
    "decanter_carafe": _BodyGeom(0.230, 0.0550, 0.0115, 0.0135, 0.0085, 0.0030, "loft"),
    # slim flute: tall narrow continuous taper, revolve lathe.
    "slim_flute": _BodyGeom(0.298, 0.0270, 0.0110, 0.0130, 0.0082, 0.0025, "revolve"),
}


@dataclass(frozen=True)
class ContainerGlassBottleConfig:
    bottle_body_profile: BodyProfile = "long_neck"
    closure_mechanism: ClosureMechanism = "pry_off_crown_cap"
    palette_style: PaletteStyle = "green_wine"
    body_height_scale: float = 1.0
    body_radius_scale: float = 1.0
    neck_radius_scale: float = 1.0
    closure_size_scale: float = 1.0
    joint_travel_scale: float = 1.0
    name: str = "container_glass_bottle"


@dataclass(frozen=True)
class ResolvedContainerGlassBottleConfig:
    bottle_body_profile: BodyProfile
    closure_mechanism: ClosureMechanism
    palette_style: PaletteStyle
    body_height_scale: float
    body_radius_scale: float
    neck_radius_scale: float
    closure_size_scale: float
    joint_travel_scale: float
    # derived interface geometry (world frame, metres)
    lip_top_z: float  # world z of the lip top (closure mount plane)
    body_r: float
    neck_r: float
    lip_r: float
    bore_r: float
    wall: float
    primitive: str
    finish: str
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ---------------------------------------------------------------------------
# Seed / resolve
# ---------------------------------------------------------------------------
def config_from_seed(seed: int) -> ContainerGlassBottleConfig:
    """Deterministic procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    return ContainerGlassBottleConfig(
        bottle_body_profile=rng.choice(BODY_PROFILES),
        closure_mechanism=rng.choice(CLOSURE_MECHANISMS),
        palette_style=rng.choice(PALETTE_STYLES),
        body_height_scale=round(rng.uniform(0.85, 1.18), 4),
        body_radius_scale=round(rng.uniform(0.88, 1.15), 4),
        neck_radius_scale=round(rng.uniform(0.92, 1.10), 4),
        closure_size_scale=round(rng.uniform(0.88, 1.12), 4),
        joint_travel_scale=round(rng.uniform(0.85, 1.12), 4),
        name=f"seeded_container_glass_bottle_{seed}",
    )


def resolve_config(
    config: ContainerGlassBottleConfig | None = None,
) -> ResolvedContainerGlassBottleConfig:
    cfg = config or ContainerGlassBottleConfig()
    body_profile = _pick(cfg.bottle_body_profile, BODY_PROFILES)
    closure = _pick(cfg.closure_mechanism, CLOSURE_MECHANISMS)
    palette = _pick(cfg.palette_style, PALETTE_STYLES)

    g = _BODIES[body_profile]
    h_scale = _clamp(cfg.body_height_scale, 0.85, 1.18)
    r_scale = _clamp(cfg.body_radius_scale, 0.88, 1.15)
    n_scale = _clamp(cfg.neck_radius_scale, 0.92, 1.10)
    c_scale = _clamp(cfg.closure_size_scale, 0.88, 1.12)
    jt_scale = _clamp(cfg.joint_travel_scale, 0.85, 1.12)

    lip_top_z = g.lip_top_z * h_scale
    body_r = g.body_r * r_scale
    # Neck radius follows its own scale; the lip / bore follow neck so every
    # closure's mouth fit (cap bore = neck_r + clearance, cork/pipette/marble
    # R <= bore - clearance) stays valid. Clamp neck strictly inside the body.
    neck_r = _clamp(g.neck_r * n_scale, 0.009, body_r - 0.004)
    lip_r = _clamp(g.lip_r * n_scale, neck_r + 0.0008, body_r - 0.002)
    bore_r = _clamp(g.bore_r * n_scale, 0.006, neck_r - 0.0015)

    return ResolvedContainerGlassBottleConfig(
        bottle_body_profile=body_profile,
        closure_mechanism=closure,
        palette_style=palette,
        body_height_scale=h_scale,
        body_radius_scale=r_scale,
        neck_radius_scale=n_scale,
        closure_size_scale=c_scale,
        joint_travel_scale=jt_scale,
        lip_top_z=lip_top_z,
        body_r=body_r,
        neck_r=neck_r,
        lip_r=lip_r,
        bore_r=bore_r,
        wall=g.wall,
        primitive=g.primitive,
        finish=PALETTES[palette].finish,
        name=cfg.name or "container_glass_bottle",
    )


def with_overrides(
    config: ContainerGlassBottleConfig, **kwargs: object
) -> ContainerGlassBottleConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: ContainerGlassBottleConfig | ResolvedContainerGlassBottleConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedContainerGlassBottleConfig)
        else resolve_config(config)
    )
    return (
        ("bottle_body_profile", r.bottle_body_profile),
        ("closure_mechanism", r.closure_mechanism),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Slot A — body geometry. Six circular bodies (loft or revolve), one
# non-circular flask. The silhouette is authored at the source heights, then
# scaled vertically by (lip_top_z / source_lip) and radially so the neck/lip
# match the resolved interface. All bodies hollow via outer.cut(inner).
# ===========================================================================
def _profile_loft(sections, ruled: bool = True) -> cq.Workplane:
    """Loft circular sections (z, radius) stacked along +Z (parent helper)."""
    wp = cq.Workplane("XY")
    prev = 0.0
    for i, (z, r) in enumerate(sections):
        off = z if i == 0 else z - prev
        if i > 0 or abs(off) > 1e-12:
            wp = wp.workplane(offset=off)
        wp = wp.circle(r)
        prev = z
    return wp.loft(ruled=ruled)


def _revolve_profile(profile_pts: list[tuple[float, float]]) -> cq.Workplane:
    """Revolve (z, radius) profile points about +Z (slim_flute helper)."""
    wp = cq.Workplane("XZ")
    wp = wp.moveTo(0.0, profile_pts[0][0])
    wp = wp.lineTo(profile_pts[0][1], profile_pts[0][0])
    for z, r in profile_pts[1:]:
        wp = wp.lineTo(r, z)
    wp = wp.lineTo(0.0, profile_pts[-1][0])
    wp = wp.close()
    return wp.revolve(360, (0, 0), (0, 1))


def _scaled(sections, sz: float, sr: float):
    """Scale (z, radius) profile sections vertically by sz, radially by sr."""
    return [(z * sz, r * sr) for (z, r) in sections]


def _interface_overrides(sections, r: ResolvedContainerGlassBottleConfig):
    """Force the last few (neck/lip) sections to the resolved circular
    interface so every body presents an identical mouth to the closures.

    ``sections`` is the already z/r-scaled outer silhouette; the top region
    (z near lip) is rewritten to neck_r -> lip flare -> lip_r at lip_top_z.
    """
    lip = r.lip_top_z
    out = [(z, rr) for (z, rr) in sections if z < lip - 0.016]
    out.append((lip - 0.014, r.neck_r))
    out.append((lip - 0.006, r.neck_r))  # straight neck section
    out.append((lip - 0.003, r.lip_r))   # neck flares to the lip
    out.append((lip, r.lip_r))           # flat mouth top (equal radius)
    return out


def _bore_overrides(r: ResolvedContainerGlassBottleConfig):
    """Top of the inner cavity — a circular bore that opens at the mouth."""
    lip = r.lip_top_z
    return [
        (lip - 0.012, r.bore_r),
        (lip - 0.004, r.bore_r),
        (lip + 0.004, r.bore_r),  # poke out the top so the mouth is open
    ]


def _long_neck_outer(r):
    s = _scaled(
        [
            (0.0, 0.0235), (0.003, 0.0250), (0.008, 0.0305), (0.013, 0.0322),
            (0.018, 0.0325), (0.120, 0.0325), (0.128, 0.0316), (0.137, 0.0288),
            (0.150, 0.0205), (0.160, 0.0150), (0.170, 0.0122),
        ],
        r.lip_top_z / 0.230, r.body_r / 0.0325,
    )
    return _interface_overrides(s, r)


def _long_neck_inner(r):
    s = _scaled(
        [
            (0.010, 0.0200), (0.018, 0.0270), (0.024, 0.0297), (0.116, 0.0297),
            (0.128, 0.0288), (0.137, 0.0260), (0.150, 0.0177), (0.160, 0.0122),
            (0.170, 0.0094),
        ],
        r.lip_top_z / 0.230, r.body_r / 0.0325,
    )
    return s + _bore_overrides(r)


def _wine_outer(r):
    s = _scaled(
        [
            (0.0, 0.033), (0.005, 0.035), (0.014, 0.0370), (0.020, 0.0375),
            (0.190, 0.0375), (0.200, 0.0373), (0.206, 0.0368), (0.212, 0.0350),
            (0.218, 0.0320), (0.224, 0.0275), (0.230, 0.0220), (0.234, 0.0180),
            (0.240, 0.0150),
        ],
        r.lip_top_z / 0.283, r.body_r / 0.0375,
    )
    return _interface_overrides(s, r)


def _wine_inner(r):
    s = _scaled(
        [
            (0.022, 0.018), (0.028, 0.028), (0.035, 0.032), (0.185, 0.0345),
            (0.200, 0.0343), (0.206, 0.0338), (0.212, 0.0320), (0.218, 0.0290),
            (0.224, 0.0245), (0.230, 0.0190), (0.234, 0.0150), (0.240, 0.0120),
        ],
        r.lip_top_z / 0.283, r.body_r / 0.0375,
    )
    return s + _bore_overrides(r)


def _stubby_outer(r):
    s = _scaled(
        [
            (0.0, 0.0280), (0.003, 0.0300), (0.008, 0.0355), (0.014, 0.0390),
            (0.020, 0.0400), (0.085, 0.0400), (0.092, 0.0396), (0.097, 0.0380),
            (0.102, 0.0350), (0.107, 0.0300), (0.112, 0.0240), (0.118, 0.0190),
        ],
        r.lip_top_z / 0.142, r.body_r / 0.0400,
    )
    return _interface_overrides(s, r)


def _stubby_inner(r):
    s = _scaled(
        [
            (0.010, 0.0210), (0.015, 0.0290), (0.020, 0.0340), (0.028, 0.0370),
            (0.082, 0.0370), (0.092, 0.0366), (0.097, 0.0350), (0.102, 0.0320),
            (0.107, 0.0270), (0.112, 0.0210), (0.118, 0.0160),
        ],
        r.lip_top_z / 0.142, r.body_r / 0.0400,
    )
    return s + _bore_overrides(r)


def _rounded_shoulder_sections(z_start, z_end, r_body, r_neck, n):
    """Cosine-interpolated shoulder sections (boston_round helper)."""
    out = []
    for i in range(n + 1):
        t = i / n
        z = z_start + (z_end - z_start) * t
        rr = r_neck + (r_body - r_neck) * math.cos(t * math.pi / 2.0)
        out.append((z, rr))
    return out


def _boston_outer(r):
    sz = r.lip_top_z / 0.165
    sr = r.body_r / 0.0330
    base = _scaled(
        [(0.0, 0.0220), (0.004, 0.0240), (0.008, 0.0290), (0.012, 0.0330),
         (0.105, 0.0330)],
        sz, sr,
    )
    shoulder = _scaled(
        _rounded_shoulder_sections(0.105, 0.140, 0.0330, 0.0120, 14)[1:],
        sz, sr,
    )
    return _interface_overrides(base + shoulder, r)


def _boston_inner(r):
    sz = r.lip_top_z / 0.165
    sr = r.body_r / 0.0330
    base = _scaled(
        [(0.010, 0.0190), (0.012, 0.0302), (0.101, 0.0302)],
        sz, sr,
    )
    shoulder = _scaled(
        _rounded_shoulder_sections(0.101, 0.140, 0.0302, 0.0097, 14)[1:],
        sz, sr,
    )
    return base + shoulder + _bore_overrides(r)


def _decanter_outer(r):
    s = _scaled(
        [
            (0.0, 0.0240), (0.003, 0.0260), (0.007, 0.0310), (0.012, 0.0370),
            (0.018, 0.0425), (0.026, 0.0475), (0.036, 0.0515), (0.048, 0.0540),
            (0.060, 0.0550), (0.072, 0.0548), (0.084, 0.0535), (0.096, 0.0515),
            (0.104, 0.0490), (0.108, 0.0455), (0.115, 0.0405), (0.122, 0.0345),
            (0.128, 0.0280), (0.134, 0.0225), (0.140, 0.0180), (0.148, 0.0145),
            (0.158, 0.0125),
        ],
        r.lip_top_z / 0.230, r.body_r / 0.0550,
    )
    return _interface_overrides(s, r)


def _decanter_inner(r):
    s = _scaled(
        [
            (0.010, 0.0190), (0.015, 0.0250), (0.022, 0.0330), (0.032, 0.0395),
            (0.044, 0.0440), (0.058, 0.0475), (0.072, 0.0488), (0.084, 0.0478),
            (0.096, 0.0458), (0.104, 0.0432), (0.108, 0.0398), (0.115, 0.0348),
            (0.122, 0.0288), (0.128, 0.0225), (0.134, 0.0172), (0.140, 0.0130),
            (0.148, 0.0115), (0.158, 0.0095),
        ],
        r.lip_top_z / 0.230, r.body_r / 0.0550,
    )
    return s + _bore_overrides(r)


def _flute_outer(r):
    s = _scaled(
        [
            (0.0, 0.0190), (0.004, 0.0215), (0.010, 0.0245), (0.018, 0.0262),
            (0.028, 0.0270), (0.050, 0.0268), (0.080, 0.0246), (0.110, 0.0222),
            (0.140, 0.0198), (0.170, 0.0174), (0.200, 0.0152), (0.230, 0.0132),
            (0.265, 0.0115),
        ],
        r.lip_top_z / 0.298, r.body_r / 0.0270,
    )
    return _interface_overrides(s, r)


def _flute_inner(r):
    s = _scaled(
        [
            (0.012, 0.0155), (0.018, 0.0232), (0.028, 0.0242), (0.050, 0.0240),
            (0.080, 0.0218), (0.110, 0.0194), (0.140, 0.0170), (0.170, 0.0148),
            (0.200, 0.0126), (0.230, 0.0106), (0.265, 0.0088),
        ],
        r.lip_top_z / 0.298, r.body_r / 0.0270,
    )
    return s + _bore_overrides(r)


# --- hip_flask (non-circular D/kidney loft) --------------------------------
_FLASK_N_PTS = 32


def _flask_profile_pts(hw, r_pos, r_neg, sag, cb, n=_FLASK_N_PTS):
    """2D D/kidney cross-section points (convex +Y, concave -Y).

    ``cb`` (circle_blend) 0 = full flask shape, 1 = circle of radius hw.
    """
    pts = []
    for i in range(n):
        t = 2.0 * math.pi * i / n
        ct, st = math.cos(t), math.sin(t)
        x = hw * ct
        if st >= 0.0:
            y = (1.0 - cb) * r_pos * st + cb * hw * st
        else:
            s = -st
            y_flask = -r_neg * s * (2.0 - s) + sag * s * s
            y_circle = -hw * s
            y = (1.0 - cb) * y_flask + cb * y_circle
        pts.append((x, y))
    return pts


def _flask_loft(sections, n=_FLASK_N_PTS, ruled=True):
    """Loft through D-shaped sections: (z, hw, r_pos, r_neg, sag, circle_blend)."""
    wp = cq.Workplane("XY")
    prev_z = 0.0
    for i, (z, hw, rp, rn, sag, cb) in enumerate(sections):
        off = z if i == 0 else z - prev_z
        if i > 0 or abs(off) > 1e-12:
            wp = wp.workplane(offset=off)
        pts = _flask_profile_pts(hw, rp, rn, sag, cb, n)
        wp = wp.moveTo(pts[0][0], pts[0][1])
        for x, y in pts[1:]:
            wp = wp.lineTo(x, y)
        wp = wp.close()
        prev_z = z
    return wp.loft(ruled=ruled)


def _flask_solid(r: ResolvedContainerGlassBottleConfig) -> cq.Workplane:
    """Hollow D/kidney flask body that blends back to a circular neck so the
    closure interface (lip_r, bore_r) is identical to the circular bodies."""
    sz = r.lip_top_z / 0.168
    sr = r.body_r / 0.0400  # body half-width scale
    hw = 0.0400 * sr
    rp = 0.014 * sr
    rn = 0.010 * sr
    sag = 0.006 * sr
    nr = r.neck_r
    lr = r.lip_r
    br = r.bore_r
    lip = r.lip_top_z

    # Consolidated section list (fewer loft slices => much cheaper CadQuery
    # polygon loft) while keeping the D/kidney silhouette (convex +Y / concave
    # -Y belly at 0.040-0.075) and the circular-neck snap intact.
    outer = _flask_loft([
        (0.000 * sz, 0.020 * sr, 0.008 * sr, 0.006 * sr, 0.002 * sr, 0.0),
        (0.012 * sz, 0.036 * sr, 0.012 * sr, 0.009 * sr, 0.004 * sr, 0.0),
        (0.040 * sz, hw, rp, rn, sag, 0.0),
        (0.075 * sz, hw, rp, rn, sag, 0.0),
        (0.108 * sz, 0.033 * sr, 0.012 * sr, 0.008 * sr, 0.003 * sr, 0.0),
        (0.130 * sz, 0.013 * sr, 0.010 * sr, 0.009 * sr, 0.0, 0.0),
        # snap to circular neck
        (lip - 0.018, nr, nr, nr, 0.0, 1.0),
        (lip - 0.003, lr, lr, lr, 0.0, 1.0),
        (lip, lr, lr, lr, 0.0, 1.0),
    ])

    w = r.wall
    inner = _flask_loft([
        (0.010 * sz, 0.016 * sr, 0.005 * sr, 0.004 * sr, 0.001 * sr, 0.0),
        (0.040 * sz, hw - w, rp - w, rn - w, sag * 0.8, 0.0),
        (0.075 * sz, hw - w, rp - w, rn - w, sag * 0.8, 0.0),
        (0.106 * sz, 0.030 * sr, 0.010 * sr, 0.006 * sr, 0.002 * sr, 0.0),
        (0.130 * sz, 0.011 * sr, 0.008 * sr, 0.007 * sr, 0.0, 0.0),
        (lip - 0.018, br, br, br, 0.0, 1.0),
        (lip + 0.004, br, br, br, 0.0, 1.0),
    ])
    return outer.cut(inner)


_BODY_PROFILE_FNS = {
    "long_neck": (_long_neck_outer, _long_neck_inner),
    "wine_bottle": (_wine_outer, _wine_inner),
    "stubby_steinie": (_stubby_outer, _stubby_inner),
    "boston_round": (_boston_outer, _boston_inner),
    "decanter_carafe": (_decanter_outer, _decanter_inner),
    "slim_flute": (_flute_outer, _flute_inner),
}


def _bottle_solid(r: ResolvedContainerGlassBottleConfig) -> cq.Workplane:
    """Hollow open glass shell for the resolved body profile."""
    if r.primitive == "flask":
        return _flask_solid(r)
    outer_fn, inner_fn = _BODY_PROFILE_FNS[r.bottle_body_profile]
    if r.primitive == "revolve":
        outer = _revolve_profile(outer_fn(r))
        inner = _revolve_profile(inner_fn(r))
    else:
        outer = _profile_loft(outer_fn(r))
        inner = _profile_loft(inner_fn(r))
    solid = outer.cut(inner)
    if r.bottle_body_profile == "wine_bottle":
        # Punt: concave dome cut into the base (wine identity).
        punt_sphere_r = 0.035 * (r.body_r / 0.0375)
        punt_depth = 0.015 * (r.lip_top_z / 0.283)
        punt_center_z = -(punt_sphere_r - punt_depth)
        punt = cq.Workplane("XY").sphere(punt_sphere_r).translate((0, 0, punt_center_z))
        solid = solid.cut(punt)
    return solid


def _codd_neck_solid(r: ResolvedContainerGlassBottleConfig) -> cq.Workplane:
    """long_neck body re-bored with a Codd pinch + marble chamber in the neck."""
    sz = r.lip_top_z / 0.230
    sr = r.body_r / 0.0325
    nr = r.neck_r
    lr = r.lip_r
    br = r.bore_r
    lip = r.lip_top_z
    marble_r = _codd_marble_r(r)
    chamber_r = marble_r + 0.0017
    pinch_r = marble_r - 0.0017

    outer = _profile_loft(_interface_overrides(_scaled(
        [
            (0.0, 0.0235), (0.003, 0.0250), (0.008, 0.0305), (0.013, 0.0322),
            (0.018, 0.0325), (0.120, 0.0325), (0.128, 0.0316), (0.137, 0.0288),
            (0.150, 0.0205), (0.160, 0.0150), (0.168, 0.0130), (0.170, 0.0140),
            (0.174, 0.0130), (0.180, 0.0152), (0.206, 0.0152), (0.212, 0.0130),
        ],
        sz, sr,
    ), r))
    # Inner bore with pinch (below chamber) + marble chamber + circular mouth.
    chamber_bottom = lip - 0.052
    chamber_top = lip - 0.018
    pinch_z = lip - 0.058
    inner = _profile_loft([
        (0.010 * sz, 0.0200 * sr), (0.018 * sz, 0.0270 * sr),
        (0.024 * sz, 0.0297 * sr), (0.116 * sz, 0.0297 * sr),
        (0.128 * sz, 0.0288 * sr), (0.137 * sz, 0.0260 * sr),
        (0.150 * sz, 0.0177 * sr), (0.160 * sz, 0.0122 * sr),
        (pinch_z - 0.004, 0.0095 * sr),
        (pinch_z, pinch_r), (pinch_z + 0.003, pinch_r),
        (chamber_bottom, chamber_r), (chamber_top, chamber_r),
        (lip - 0.012, br), (lip - 0.004, br), (lip + 0.004, br),
    ])
    return outer.cut(inner)


# ===========================================================================
# Slot B — closure mechanisms (parallel children of the bottle). Captured-fit
# overlaps are grandfathered (no MatingContract) per the spec and guarded by
# element-scoped allow_overlap in run_*_tests; joint origins land on the real
# lip / neck pivot / spout rear / marble seat hardware.
# ===========================================================================

# ---- crown cap -------------------------------------------------------------
def _crown_cap_mesh(r: ResolvedContainerGlassBottleConfig):
    """Crimped crown cap: dome top + fluted skirt over the lip (parent)."""
    c = r.closure_size_scale
    skirt_h = 0.0080 * c
    top_h = 0.0035 * c
    top_r = r.lip_r + 0.0017
    skirt_r = top_r - 0.0002

    top = (
        cq.Workplane("XY").circle(top_r)
        .workplane(offset=top_h).circle(top_r * 0.86).loft(ruled=True)
    )
    skirt = (
        cq.Workplane("XY").workplane(offset=-skirt_h).circle(skirt_r)
        .workplane(offset=skirt_h).circle(top_r).loft(ruled=True)
    )
    skirt_bore = (
        cq.Workplane("XY").workplane(offset=-skirt_h - 0.001).circle(skirt_r - 0.0016)
        .workplane(offset=skirt_h + 0.0005).circle(top_r - 0.0016).loft(ruled=True)
    )
    skirt = skirt.cut(skirt_bore)
    cap = top.union(skirt)

    n_flutes = 21
    flute_z = -skirt_h + 0.0030
    for i in range(n_flutes):
        ang = 2.0 * math.pi * i / n_flutes
        fx = (skirt_r + 0.0004) * math.cos(ang)
        fy = (skirt_r + 0.0004) * math.sin(ang)
        tab = (
            cq.Workplane("XY").workplane(offset=flute_z).center(fx, fy)
            .rect(0.0026, 0.0026).extrude(0.0050 * c)
        )
        cap = cap.union(tab)
    return mesh_from_cadquery(cap, "crown_cap")


def _build_crown_cap(model, bottle, r, *, mats):
    cap = model.part("crown_cap")
    cap.visual(
        _crown_cap_mesh(r),
        material=mats["metal"],
        name="crown_cap",
        material_class_id=_material_class_id("closure_metal", r),
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(radius=r.lip_r + 0.0017, length=0.012),
        mass=0.004, origin=Origin(xyz=(0.0, 0.0, -0.003)),
    )
    model.articulation(
        "bottle_to_cap", ArticulationType.PRISMATIC, parent=bottle, child=cap,
        origin=Origin(xyz=(0.0, 0.0, r.lip_top_z)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=4.0, velocity=0.2, lower=0.0, upper=0.03 * r.joint_travel_scale
        ),
    )


# ---- screw cap -------------------------------------------------------------
def _thread_ring(z, inner_r, outer_r, h):
    return (
        cq.Workplane("XY").workplane(offset=z).circle(outer_r).circle(inner_r).extrude(h)
    )


def _neck_threads_mesh(r: ResolvedContainerGlassBottleConfig):
    """External thread rings on the neck for the screw cap to engage.

    A thin sleeve digs into the neck wall (inner_r < neck_r) and unites the
    three thread ridges into one connected solid that overlaps the glass, so
    the threads never form a floating disconnected island."""
    thread_h = 0.0015
    spacing = 0.0045
    depth = 0.0012
    z0 = r.lip_top_z - 0.020
    z1 = z0 + 2 * spacing + thread_h
    inner_r = r.neck_r - 0.0012  # bites into the neck wall for connectivity
    # Backing sleeve spanning the whole thread band (binds the rings together
    # and into the glass).
    sleeve = (
        cq.Workplane("XY").workplane(offset=z0).circle(r.neck_r + 0.0002)
        .circle(inner_r).extrude(z1 - z0)
    )
    result = sleeve
    for i in range(3):
        z = z0 + i * spacing + thread_h
        ring = _thread_ring(z, inner_r, r.neck_r + depth, thread_h)
        result = result.union(ring)
    return mesh_from_cadquery(result, "neck_threads")


def _screw_cap_mesh(r: ResolvedContainerGlassBottleConfig):
    """Knurled cylindrical screw cap with internal thread rings."""
    c = r.closure_size_scale
    cap_outer_r = r.lip_r + 0.0035
    cap_bore_r = r.lip_r + 0.0015
    skirt_h = 0.020 * c
    top_wall = 0.003
    total_h = skirt_h + top_wall
    n_knurls = 36
    knurl_depth = 0.0008

    r_root = cap_outer_r - knurl_depth
    pts = []
    for i in range(n_knurls * 2):
        ang = math.pi * i / n_knurls
        rad = cap_outer_r if i % 2 == 0 else r_root
        pts.append((rad * math.cos(ang), rad * math.sin(ang)))
    wp = cq.Workplane("XY").workplane(offset=-skirt_h).moveTo(pts[0][0], pts[0][1])
    for pt in pts[1:]:
        wp = wp.lineTo(pt[0], pt[1])
    outer_shell = wp.close().extrude(total_h)

    bore = (
        cq.Workplane("XY").workplane(offset=-skirt_h - 0.001)
        .circle(cap_bore_r).extrude(total_h - top_wall + 0.001)
    )
    cap = outer_shell.cut(bore)
    spacing = 0.0045
    thread_inner_r = cap_bore_r - 0.0030
    thread_outer_r = cap_bore_r + 0.0005
    for i in range(3):
        z = -skirt_h + i * spacing
        cap = cap.union(_thread_ring(z, thread_inner_r, thread_outer_r, 0.0010))
    return mesh_from_cadquery(cap, "screw_cap")


def _build_screw_cap(model, bottle, r, *, mats):
    bottle.visual(
        _neck_threads_mesh(r),
        material=mats["glass"],
        name="neck_threads",
        material_class_id=_material_class_id("bottle_glass", r),
    )
    cap = model.part("screw_cap")
    cap.visual(
        _screw_cap_mesh(r),
        material=mats["metal"],
        name="screw_cap",
        material_class_id=_material_class_id("closure_metal", r),
    )
    cap.inertial = Inertial.from_geometry(
        Cylinder(radius=r.lip_r + 0.0035, length=0.023),
        mass=0.008, origin=Origin(xyz=(0.0, 0.0, -0.008)),
    )
    model.articulation(
        "bottle_to_cap", ArticulationType.CONTINUOUS, parent=bottle, child=cap,
        origin=Origin(xyz=(0.0, 0.0, r.lip_top_z)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=2.0, velocity=6.0),
    )


# ---- swing top -------------------------------------------------------------
def _rod(p1, p2, rad) -> cq.Workplane:
    dx, dy, dz = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-9:
        return cq.Workplane("XY").sphere(rad)
    cyl = cq.Workplane("XY").circle(rad).extrude(length)
    z_vec = cq.Vector(0, 0, 1)
    d_vec = cq.Vector(dx, dy, dz).normalized()
    cross = z_vec.cross(d_vec)
    dot = max(-1.0, min(1.0, z_vec.dot(d_vec)))
    if cross.Length > 1e-9:
        angle = math.degrees(math.acos(dot))
        ax = cross.normalized()
        cyl = cyl.rotate((0, 0, 0), (ax.x, ax.y, ax.z), angle)
    elif dot < 0:
        cyl = cyl.rotate((0, 0, 0), (1, 0, 0), 180.0)
    return cyl.translate(p1)


def _swing_params(r):
    pivot_z = r.lip_top_z - 0.020
    pivot_y = 0.018
    wire_r = 0.0012
    collar_r = r.neck_r + 0.0015
    return pivot_z, pivot_y, wire_r, collar_r


def _collar_mesh(r):
    """Wire collar ring + pivot ears clipped around the neck (fixed visual)."""
    pivot_z, pivot_y, wire_r, collar_r = _swing_params(r)
    ring_h = 0.005
    ring_z0 = pivot_z - ring_h / 2.0
    ring_outer = collar_r + wire_r * 1.5
    ring_inner = collar_r - wire_r * 1.5
    ring = (
        cq.Workplane("XY").workplane(offset=ring_z0)
        .circle(ring_outer).circle(ring_inner).extrude(ring_h)
    )
    ear_half_x = wire_r * 1.8
    ear_inner_y = ring_outer - 0.002
    ear_outer_y = pivot_y + 0.003
    for sign in (1, -1):
        cy = sign * (ear_inner_y + ear_outer_y) / 2.0
        half_y = (ear_outer_y - ear_inner_y) / 2.0
        ear = (
            cq.Workplane("XY").workplane(offset=ring_z0).center(0.0, cy)
            .rect(ear_half_x * 2, half_y * 2).extrude(ring_h)
        )
        ring = ring.union(ear)
    return mesh_from_cadquery(ring, "neck_collar")


def _swing_local_zs(r):
    pivot_z, _, _, _ = _swing_params(r)
    gasket_local_z = r.lip_top_z - pivot_z
    plug_local_z = gasket_local_z + 0.003
    return gasket_local_z, plug_local_z


def _bail_mesh(r):
    pivot_z, pivot_y, wire_r, _ = _swing_params(r)
    _, plug_local_z = _swing_local_zs(r)
    plug_h = 0.014 * r.closure_size_scale
    arm_top_y = 0.007
    arm_top_z = plug_local_z + plug_h + 0.003
    arm_paths = [
        [(0.0, pivot_y, 0.0), (0.0, pivot_y * 0.88, 0.018),
         (0.0, pivot_y * 0.45, 0.032), (0.0, arm_top_y, arm_top_z)],
        [(0.0, -pivot_y, 0.0), (0.0, -pivot_y * 0.88, 0.018),
         (0.0, -pivot_y * 0.45, 0.032), (0.0, -arm_top_y, arm_top_z)],
    ]
    segments = []
    for path in arm_paths:
        for i in range(len(path) - 1):
            segments.append(_rod(path[i], path[i + 1], wire_r))
        for pt in path[1:-1]:
            segments.append(cq.Workplane("XY").sphere(wire_r * 1.3).translate(pt))
    segments.append(_rod((0.0, -arm_top_y, arm_top_z), (0.0, arm_top_y, arm_top_z), wire_r))
    pin_inset = 0.005
    for sign in (1, -1):
        segments.append(_rod(
            (0.0, sign * pivot_y, 0.0),
            (0.0, sign * (pivot_y - pin_inset), 0.0), wire_r * 0.85,
        ))
    result = segments[0]
    for seg in segments[1:]:
        result = result.union(seg)
    return mesh_from_cadquery(result, "bail_wire")


def _plug_mesh(r):
    _, plug_local_z = _swing_local_zs(r)
    plug_r = min(0.009, r.bore_r + 0.0005)
    plug_h = 0.014 * r.closure_size_scale
    body = (
        cq.Workplane("XY").workplane(offset=plug_local_z).circle(plug_r)
        .workplane(offset=plug_h).circle(plug_r * 0.92).loft(ruled=True)
    )
    dome = (
        cq.Workplane("XY").workplane(offset=plug_local_z + plug_h).circle(plug_r * 0.92)
        .workplane(offset=0.005).circle(plug_r * 0.30).loft(ruled=True)
    )
    plug = body.union(dome)
    rim = (
        cq.Workplane("XY").workplane(offset=plug_local_z - 0.001)
        .circle(plug_r + 0.001).circle(plug_r - 0.001).extrude(0.002)
    )
    return mesh_from_cadquery(plug.union(rim), "plug_ceramic")


def _gasket_mesh(r):
    gasket_local_z, _ = _swing_local_zs(r)
    gasket_r = min(0.0105, r.lip_r - 0.002)
    gasket = (
        cq.Workplane("XY").workplane(offset=gasket_local_z)
        .circle(gasket_r).circle(gasket_r - 0.003).extrude(0.003)
    )
    return mesh_from_cadquery(gasket, "plug_gasket")


def _build_swing_top(model, bottle, r, *, mats):
    pivot_z, _, _, _ = _swing_params(r)
    bottle.visual(
        _collar_mesh(r),
        material=mats["metal"],
        name="neck_collar",
        material_class_id=_material_class_id("closure_metal", r),
    )
    stopper = model.part("stopper")
    stopper.visual(
        _bail_mesh(r),
        material=mats["metal"],
        name="bail_wire",
        material_class_id=_material_class_id("closure_metal", r),
    )
    stopper.visual(
        _plug_mesh(r),
        material=mats["ceramic"],
        name="plug_ceramic",
        material_class_id=_material_class_id("ceramic_stopper", r),
    )
    stopper.visual(
        _gasket_mesh(r),
        material=mats["rubber"],
        name="plug_gasket",
        material_class_id=_material_class_id("plug_gasket", r),
    )
    stopper.inertial = Inertial.from_geometry(
        Cylinder(radius=0.012, length=0.040),
        mass=0.025, origin=Origin(xyz=(0.0, 0.0, 0.020)),
    )
    # Cap the swing limit so jt_scale never pushes it past ~2.8 rad (beyond
    # that the plug swings back over the axis and lateral displacement shrinks).
    swing_upper = min(2.8 * r.joint_travel_scale, 2.95)
    model.articulation(
        "bottle_to_stopper", ArticulationType.REVOLUTE, parent=bottle, child=stopper,
        origin=Origin(xyz=(0.0, 0.0, pivot_z)), axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=3.0, velocity=4.0, lower=0.0, upper=swing_upper
        ),
    )


# ---- cork ------------------------------------------------------------------
def _cork_mesh(r: ResolvedContainerGlassBottleConfig):
    """Tapered cork: plug seated in the bore + grip head above the lip."""
    c = r.closure_size_scale
    plug_length = 0.026 * c
    plug_top_r = r.bore_r + 0.0005
    plug_bot_r = plug_top_r - 0.0012
    head_h = 0.006
    head_r = r.lip_r - 0.0015
    chamfer = 0.0012

    plug = (
        cq.Workplane("XY").workplane(offset=-plug_length).circle(plug_bot_r)
        .workplane(offset=plug_length).circle(plug_top_r).loft(ruled=True)
    )
    tip = cq.Workplane("XY").workplane(offset=-plug_length).sphere(plug_bot_r * 0.7)
    plug = plug.union(tip)
    head = (
        cq.Workplane("XY").circle(head_r)
        .workplane(offset=head_h - chamfer).circle(head_r)
        .workplane(offset=chamfer).circle(head_r - chamfer).loft(ruled=True)
    )
    cork = plug.union(head)
    for i in range(3):
        gz = -plug_length * (0.25 + 0.25 * i)
        t = (gz + plug_length) / plug_length
        gr = plug_bot_r + t * (plug_top_r - plug_bot_r)
        groove = (
            cq.Workplane("XY").workplane(offset=gz - 0.0005).circle(gr + 0.0002)
            .workplane(offset=0.001).circle(gr + 0.0002).loft(ruled=True)
        )
        inner = (
            cq.Workplane("XY").workplane(offset=gz - 0.0006).circle(gr - 0.0006)
            .workplane(offset=0.0012).circle(gr - 0.0006).loft(ruled=True)
        )
        cork = cork.cut(groove.cut(inner))
    return mesh_from_cadquery(cork, "cork_stopper")


def _build_cork(model, bottle, r, *, mats):
    cork = model.part("cork_stopper")
    cork.visual(
        _cork_mesh(r),
        material=mats["cork"],
        name="cork_stopper",
        material_class_id=_material_class_id("cork", r),
    )
    cork.inertial = Inertial.from_geometry(
        Cylinder(radius=0.010, length=0.032),
        mass=0.006, origin=Origin(xyz=(0.0, 0.0, -0.010)),
    )
    model.articulation(
        "bottle_to_cork", ArticulationType.PRISMATIC, parent=bottle, child=cork,
        origin=Origin(xyz=(0.0, 0.0, r.lip_top_z)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=6.0, velocity=0.15, lower=0.0, upper=0.05 * r.joint_travel_scale
        ),
    )


# ---- dropper pipette -------------------------------------------------------
def _cap_collar_mesh(r):
    c = r.closure_size_scale
    ring_od = (r.lip_r + 0.0015) * 2.0
    ring_id = (r.lip_r + 0.00075) * 2.0
    ring_h = 0.014 * c
    outer = cq.Workplane("XY").circle(ring_od / 2.0).extrude(ring_h)
    bore = (
        cq.Workplane("XY").workplane(offset=-0.001).circle(ring_id / 2.0)
        .extrude(ring_h + 0.002)
    )
    collar = outer.cut(bore)
    for t in range(3):
        phase = 2.0 * math.pi * t / 3
        for i in range(6):
            frac = i / 6
            ang = phase + frac * (2.0 * math.pi / 3)
            z_pos = frac * ring_h
            r_mid = ring_id / 2.0 + 0.0006
            tab = (
                cq.Workplane("XY").workplane(offset=z_pos)
                .center(r_mid * math.cos(ang), r_mid * math.sin(ang))
                .rect(0.0020, 0.0016).extrude(0.0018)
            )
            collar = collar.union(tab)
    top_ring = (
        cq.Workplane("XY").workplane(offset=ring_h - 0.001).circle(ring_od / 2.0)
        .workplane(offset=0.001).circle(ring_od / 2.0 - 0.001).loft(ruled=True)
    )
    return collar.union(top_ring), ring_h


def _pipette_tube_mesh(r):
    flange_h = 0.002
    flange_r = (r.lip_r + 0.00075) + 0.001
    tube_r = 0.0020
    bore_r = 0.0014
    tip_r = 0.0008
    tip_len = 0.006
    tube_len = min(0.105, r.lip_top_z * 0.46)
    outer_profile = [
        (flange_r, 0.0), (flange_r, -flange_h), (tube_r, -flange_h),
        (tube_r, -tube_len), (tip_r, -(tube_len + tip_len)),
    ]
    inner_profile = [
        (bore_r, -flange_h), (bore_r, -tube_len),
        (max(tip_r - 0.0002, 0.0002), -(tube_len + tip_len - 0.001)),
    ]
    geom = LatheGeometry.from_shell_profiles(
        outer_profile, inner_profile, segments=24, start_cap="flat", end_cap="flat",
    )
    return mesh_from_geometry(geom, "pipette_tube")


def _squeeze_bulb_mesh(r, ring_h):
    bulb_rx = 0.0095
    bulb_rz = 0.012
    stem_h = 0.005
    stem_r = 0.004
    stem = (
        cq.Workplane("XY").workplane(offset=ring_h).circle(stem_r).extrude(stem_h)
    )
    bulb_base_z = ring_h + stem_h
    sections = []
    for i in range(13):
        t = i / 12
        theta = math.pi * t
        z = bulb_base_z + bulb_rz * (1.0 - math.cos(theta)) * 0.5
        rr = bulb_rx * math.sin(theta)
        sections.append((z, max(rr, 0.0005)))
    bulb = _profile_loft(sections, ruled=False)
    result = stem.union(bulb)
    neck_ring = (
        cq.Workplane("XY").workplane(offset=bulb_base_z - 0.001).circle(bulb_rx * 0.55)
        .workplane(offset=0.002).circle(stem_r + 0.0005).loft(ruled=True)
    )
    return mesh_from_cadquery(result.union(neck_ring), "squeeze_bulb")


def _build_dropper(model, bottle, r, *, mats):
    dropper = model.part("dropper_cap")
    collar_solid, ring_h = _cap_collar_mesh(r)
    dropper.visual(
        mesh_from_cadquery(collar_solid, "cap_collar"),
        material=mats["collar"],
        name="cap_collar",
        material_class_id=_material_class_id("dropper_collar", r),
    )
    dropper.visual(
        _pipette_tube_mesh(r),
        material=mats["pipette"],
        name="pipette_tube",
        material_class_id=_material_class_id("pipette_glass", r),
    )
    dropper.visual(
        _squeeze_bulb_mesh(r, ring_h),
        material=mats["bulb"],
        name="squeeze_bulb",
        material_class_id=_material_class_id("squeeze_bulb", r),
    )
    dropper.inertial = Inertial.from_geometry(
        Cylinder(radius=0.015, length=0.030),
        mass=0.012, origin=Origin(xyz=(0.0, 0.0, ring_h / 2.0)),
    )
    model.articulation(
        "bottle_to_dropper", ArticulationType.PRISMATIC, parent=bottle, child=dropper,
        origin=Origin(xyz=(0.0, 0.0, r.lip_top_z)), axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(
            effort=3.0, velocity=0.15, lower=0.0, upper=0.13 * r.joint_travel_scale
        ),
    )


# ---- pour spout ------------------------------------------------------------
def _pour_spout_params(r):
    flange_h = 0.003
    spout_h = 0.018 * r.closure_size_scale
    spout_top_r = 0.004
    barrel_r = 0.0018
    hinge_y = -(spout_top_r + barrel_r)
    hinge_z = r.lip_top_z + flange_h + spout_h
    return flange_h, spout_h, spout_top_r, barrel_r, hinge_y, hinge_z


def _spout_solid_mesh(r):
    """Pour-spout insert (fixed visual). Origin local z=0 = lip top."""
    flange_h, spout_h, spout_top_r, _, _, _ = _pour_spout_params(r)
    plug_r = r.bore_r - 0.0007
    plug_h = 0.012
    flange_r = r.lip_r - 0.0005
    spout_base_r = 0.006
    spout_bore_r = 0.003
    lug_w, lug_d = 0.006, 0.004

    plug = _profile_loft([(-plug_h, plug_r), (0.0, plug_r)])
    flange = _profile_loft([(0.0, flange_r), (flange_h, flange_r)])
    spout_tube = _profile_loft([
        (flange_h, spout_base_r), (flange_h + spout_h, spout_top_r),
    ])
    rib_top = spout_h - 0.002
    rib_bottom = rib_top - 0.008
    rib = (
        cq.Workplane("XY").workplane(offset=flange_h + rib_bottom)
        .center(0.0, -(spout_base_r + spout_top_r) / 2.0 - 0.001)
        .rect(lug_w, lug_d).extrude(0.008)
    )
    body = plug.union(flange).union(spout_tube).union(rib)
    channel = _profile_loft([
        (-plug_h + 0.003, spout_bore_r),
        (flange_h + spout_h + 0.002, spout_bore_r * 0.75),
    ])
    return mesh_from_cadquery(body.cut(channel), "pour_spout")


def _flip_cap_solid_mesh(r):
    flange_h, spout_h, spout_top_r, barrel_r, hinge_y, hinge_z = _pour_spout_params(r)
    cap_r = 0.008
    cap_h = 0.003
    barrel_w = 0.007
    tab_w, tab_d, tab_h = 0.005, 0.004, 0.004
    spout_cy = -hinge_y
    disc = cq.Workplane("XY").center(0.0, spout_cy).circle(cap_r).extrude(cap_h)
    dome = (
        cq.Workplane("XY").workplane(offset=cap_h).center(0.0, spout_cy).circle(cap_r)
        .workplane(offset=cap_r * 0.3).circle(cap_r * 0.6).loft(ruled=True)
    )
    barrel = (
        cq.Workplane("YZ").workplane(offset=-barrel_w / 2.0)
        .center(0.0, cap_h / 2.0).circle(barrel_r).extrude(barrel_w)
    )
    tab = (
        cq.Workplane("XY").center(0.0, spout_cy + cap_r - 0.001)
        .rect(tab_w, tab_d).extrude(tab_h)
    )
    return mesh_from_cadquery(disc.union(dome).union(barrel).union(tab), "flip_cap")


def _build_pour_spout(model, bottle, r, *, mats):
    _, _, _, _, hinge_y, hinge_z = _pour_spout_params(r)
    bottle.visual(
        _spout_solid_mesh(r),
        material=mats["spout"],
        origin=Origin(xyz=(0.0, 0.0, r.lip_top_z)),
        name="pour_spout",
        material_class_id=_material_class_id("pour_spout", r),
    )
    flip_cap = model.part("flip_cap")
    flip_cap.visual(
        _flip_cap_solid_mesh(r),
        material=mats["red_flip"],
        name="flip_cap",
        material_class_id=_material_class_id("flip_cap", r),
    )
    flip_cap.inertial = Inertial.from_geometry(
        Cylinder(radius=0.008, length=0.003),
        mass=0.005, origin=Origin(xyz=(0.0, -hinge_y, 0.0015)),
    )
    model.articulation(
        "bottle_to_flip_cap", ArticulationType.REVOLUTE, parent=bottle, child=flip_cap,
        origin=Origin(xyz=(0.0, hinge_y, hinge_z)), axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=4.0, lower=0.0, upper=2.3 * r.joint_travel_scale
        ),
    )


# ---- codd marble -----------------------------------------------------------
def _codd_marble_r(r: ResolvedContainerGlassBottleConfig) -> float:
    return min(0.0075 * r.closure_size_scale, r.bore_r - 0.0002)


def _build_codd_marble(model, bottle, r, *, mats):
    marble_r = _codd_marble_r(r)
    rubber_ring = TorusGeometry(
        radius=r.bore_r - 0.0012, tube=0.0014, radial_segments=16, tubular_segments=32,
    )
    bottle.visual(
        mesh_from_geometry(rubber_ring, "rubber_ring"),
        material=mats["seal"],
        origin=Origin(xyz=(0.0, 0.0, r.lip_top_z - 0.0015)),
        name="rubber_ring",
        material_class_id=_material_class_id("rubber_ring", r),
    )
    marble = model.part("marble")
    marble.visual(
        Sphere(radius=marble_r),
        material=mats["marble"],
        name="marble",
        material_class_id=_material_class_id("codd_marble", r),
    )
    marble.inertial = Inertial.from_geometry(Sphere(radius=marble_r), mass=0.005)
    marble_seat_z = r.lip_top_z - marble_r
    model.articulation(
        "bottle_to_marble", ArticulationType.PRISMATIC, parent=bottle, child=marble,
        origin=Origin(xyz=(0.0, 0.0, marble_seat_z)), axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(
            effort=2.0, velocity=0.5, lower=0.0, upper=0.025 * r.joint_travel_scale
        ),
    )


# ===========================================================================
# Build entry point
# ===========================================================================
def build_container_glass_bottle(
    config: ContainerGlassBottleConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = PALETTES[r.palette_style]
    mats = {
        "glass": model.material(f"cgb_glass_{r.palette_style}", rgba=pal.glass),
        "metal": model.material(f"cgb_metal_{r.palette_style}", rgba=pal.metal),
        "gold": model.material(f"cgb_gold_{r.palette_style}", rgba=pal.gold),
        "cork": model.material(f"cgb_cork_{r.palette_style}", rgba=pal.cork),
        "ceramic": model.material(f"cgb_ceramic_{r.palette_style}", rgba=pal.ceramic),
        "rubber": model.material(f"cgb_rubber_{r.palette_style}", rgba=pal.rubber),
        "seal": model.material(f"cgb_seal_{r.palette_style}", rgba=pal.seal),
        "red_flip": model.material(f"cgb_flip_{r.palette_style}", rgba=pal.red_flip),
        "spout": model.material(f"cgb_spout_{r.palette_style}", rgba=pal.spout),
        "collar": model.material(f"cgb_collar_{r.palette_style}", rgba=pal.collar),
        "pipette": model.material(f"cgb_pipette_{r.palette_style}", rgba=pal.pipette),
        "bulb": model.material(f"cgb_bulb_{r.palette_style}", rgba=pal.bulb),
        "marble": model.material(f"cgb_marble_{r.palette_style}", rgba=pal.marble),
    }

    # --- ROOT: bottle glass shell -------------------------------------------
    bottle = model.part("bottle")
    if r.closure_mechanism == "codd_marble":
        solid = _codd_neck_solid(r)
    else:
        solid = _bottle_solid(r)
    bottle.visual(
        mesh_from_cadquery(solid, "bottle_glass"),
        material=mats["glass"],
        name="bottle_glass",
        material_class_id=_material_class_id("bottle_glass", r),
    )
    bottle.inertial = Inertial.from_geometry(
        Cylinder(radius=r.body_r, length=r.lip_top_z),
        mass=0.30, origin=Origin(xyz=(0.0, 0.0, r.lip_top_z / 2.0)),
    )

    # --- closure mechanism --------------------------------------------------
    if r.closure_mechanism == "pry_off_crown_cap":
        _build_crown_cap(model, bottle, r, mats=mats)
    elif r.closure_mechanism == "screw_cap":
        _build_screw_cap(model, bottle, r, mats=mats)
    elif r.closure_mechanism == "swing_top":
        _build_swing_top(model, bottle, r, mats=mats)
    elif r.closure_mechanism == "cork":
        _build_cork(model, bottle, r, mats=mats)
    elif r.closure_mechanism == "dropper_pipette":
        _build_dropper(model, bottle, r, mats=mats)
    elif r.closure_mechanism == "pour_spout":
        _build_pour_spout(model, bottle, r, mats=mats)
    elif r.closure_mechanism == "codd_marble":
        _build_codd_marble(model, bottle, r, mats=mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_container_glass_bottle(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_container_glass_bottle(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests / QC. Captured-fit overlaps (cap skirt over the lip, cork in the bore,
# pipette in the bore, screw thread engagement, swing plug/gasket on the rim +
# bail in collar, flip cap over the spout, marble in the chamber) are declared
# element-scoped so the sweep's island/overlap checks pass; the closure
# actions are exercised.
# ===========================================================================
def _ext(aabb):
    mn, mx = aabb
    return (mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2])


def run_container_glass_bottle_tests(
    object_model: ArticulatedObject,
    config: ContainerGlassBottleConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    bottle = object_model.get_part("bottle")
    pal = PALETTES[r.palette_style]

    # ---- translucent Glass identity (alpha < 1) ----
    ctx.check(
        "bottle glass is translucent (alpha < 1)",
        pal.glass[3] < 1.0,
        details=f"glass rgba={pal.glass}, finish={pal.finish}",
    )

    # ---- bottle rests on the ground (base near z=0) ----
    aabb = ctx.part_world_aabb(bottle)
    bext = _ext(aabb)
    ctx.check(
        "bottle rests on the ground (base near z=0)",
        abs(aabb[0][2]) < 0.012,
        details=f"body min z={aabb[0][2]:.4f}",
    )
    ctx.check(
        "bottle has real volume",
        bext[0] > 0.02 and bext[1] > 0.02 and bext[2] > 0.05,
        details=f"body extents={bext}",
    )

    # ---- closure: action + captured-fit overlaps ----
    if r.closure_mechanism == "pry_off_crown_cap":
        cap = object_model.get_part("crown_cap")
        joint = object_model.get_articulation("bottle_to_cap")
        ctx.allow_isolated_part(
            cap,
            reason="crown cap pries off the bottle lip and loses body contact",
        )
        ctx.allow_overlap(
            cap, bottle, elem_a="crown_cap", elem_b="bottle_glass",
            reason="Crown cap skirt is crimped down over the bottle lip when seated.",
        )
        ctx.check(
            "bottle_to_cap is PRISMATIC about +Z",
            joint.articulation_type == ArticulationType.PRISMATIC
            and abs(joint.axis[2]) > 0.99,
            details=f"axis={joint.axis}, type={joint.articulation_type}",
        )
        rest_z = ctx.part_world_position(cap)[2]
        with ctx.pose({joint: 0.03 * r.joint_travel_scale}):
            lifted_z = ctx.part_world_position(cap)[2]
        ctx.check(
            "cap pops straight up off the mouth",
            lifted_z > rest_z + 0.02 * r.joint_travel_scale,
            details=f"rest_z={rest_z:.4f}, lifted_z={lifted_z:.4f}",
        )

    elif r.closure_mechanism == "screw_cap":
        cap = object_model.get_part("screw_cap")
        joint = object_model.get_articulation("bottle_to_cap")
        ctx.allow_overlap(
            cap, bottle, elem_a="screw_cap", elem_b="neck_threads",
            reason="Cap internal thread rings engage the neck external thread rings.",
        )
        ctx.allow_overlap(
            cap, bottle, elem_a="screw_cap", elem_b="bottle_glass",
            reason="Screw cap skirt is seated down over the threaded neck lip.",
        )
        ctx.check(
            "bottle_to_cap is CONTINUOUS about +Z",
            joint.articulation_type == ArticulationType.CONTINUOUS
            and abs(joint.axis[2]) > 0.99,
            details=f"axis={joint.axis}, type={joint.articulation_type}",
        )
        ctx.check(
            "bottle has neck_threads visual",
            bottle.get_visual("neck_threads") is not None,
            details="neck_threads visual missing",
        )
        rest = ctx.part_world_position(cap)
        with ctx.pose({joint: math.pi}):
            rot = ctx.part_world_position(cap)
        ctx.check(
            "cap spins in place (Z + XY unchanged after half turn)",
            abs(rot[2] - rest[2]) < 0.001
            and abs(rot[0] - rest[0]) < 0.001
            and abs(rot[1] - rest[1]) < 0.001,
            details=f"rest={rest}, rotated={rot}",
        )

    elif r.closure_mechanism == "swing_top":
        stopper = object_model.get_part("stopper")
        joint = object_model.get_articulation("bottle_to_stopper")
        ctx.allow_isolated_part(
            stopper,
            reason="swing-top stopper swings clear of the bottle mouth and loses contact",
        )
        ctx.allow_overlap(
            stopper, bottle,
            reason="swing-top plug sweeps across the bottle mouth lip while opening (bail hinge)",
        )
        ctx.allow_overlap(
            stopper, bottle, elem_a="plug_ceramic", elem_b="bottle_glass",
            reason="Ceramic plug is seated on the bottle mouth lip when closed.",
        )
        ctx.allow_overlap(
            stopper, bottle, elem_a="plug_gasket", elem_b="bottle_glass",
            reason="Rubber gasket compresses against the bottle mouth rim when closed.",
        )
        ctx.allow_overlap(
            stopper, bottle, elem_a="bail_wire", elem_b="neck_collar",
            reason="Bail pivot pins insert into collar ear holes (captured pivot fit).",
        )
        ctx.check(
            "bottle_to_stopper is REVOLUTE about +Y",
            joint.articulation_type == ArticulationType.REVOLUTE
            and abs(joint.axis[1]) > 0.99,
            details=f"axis={joint.axis}, type={joint.articulation_type}",
        )
        plug_rest = ctx.part_element_world_aabb(stopper, elem="plug_ceramic")
        rest_x = (plug_rest[0][0] + plug_rest[1][0]) / 2.0
        # Pose at ~1.6 rad where lateral (X) displacement of the swung plug is
        # maximal (sin near 1); the full upper limit swings further back.
        swing_q = min(1.6, joint.motion_limits.upper)
        with ctx.pose({joint: swing_q}):
            plug_open = ctx.part_element_world_aabb(stopper, elem="plug_ceramic")
            open_x = (plug_open[0][0] + plug_open[1][0]) / 2.0
        ctx.check(
            "stopper swings laterally when opened",
            abs(open_x - rest_x) > 0.008,
            details=f"rest_x={rest_x:.4f}, open_x={open_x:.4f}",
        )

    elif r.closure_mechanism == "cork":
        cork = object_model.get_part("cork_stopper")
        joint = object_model.get_articulation("bottle_to_cork")
        ctx.allow_overlap(
            cork, bottle, elem_a="cork_stopper", elem_b="bottle_glass",
            reason="Cork plug is seated inside the bottle bore when at rest.",
        )
        ctx.check(
            "bottle_to_cork is PRISMATIC about +Z",
            joint.articulation_type == ArticulationType.PRISMATIC
            and abs(joint.axis[2]) > 0.99,
            details=f"axis={joint.axis}, type={joint.articulation_type}",
        )
        rest_z = ctx.part_world_position(cork)[2]
        with ctx.pose({joint: 0.05 * r.joint_travel_scale}):
            lifted_z = ctx.part_world_position(cork)[2]
        ctx.check(
            "cork pulls straight up out of the mouth",
            lifted_z > rest_z + 0.04 * r.joint_travel_scale,
            details=f"rest_z={rest_z:.4f}, lifted_z={lifted_z:.4f}",
        )

    elif r.closure_mechanism == "dropper_pipette":
        dropper = object_model.get_part("dropper_cap")
        joint = object_model.get_articulation("bottle_to_dropper")
        ctx.allow_overlap(
            dropper, bottle, elem_a="cap_collar", elem_b="bottle_glass",
            reason="Cap collar is seated over the bottle lip when closed.",
        )
        ctx.allow_overlap(
            dropper, bottle, elem_a="pipette_tube", elem_b="bottle_glass",
            reason="Pipette tube hangs down through the bottle bore into the cavity.",
        )
        ctx.check(
            "dropper has collar, tube, and bulb visuals",
            dropper.get_visual("cap_collar") is not None
            and dropper.get_visual("pipette_tube") is not None
            and dropper.get_visual("squeeze_bulb") is not None,
            details="missing one or more dropper sub-visuals",
        )
        ctx.check(
            "bottle_to_dropper is PRISMATIC about +Z",
            joint.articulation_type == ArticulationType.PRISMATIC
            and abs(joint.axis[2]) > 0.99,
            details=f"axis={joint.axis}, type={joint.articulation_type}",
        )
        rest_z = ctx.part_world_position(dropper)[2]
        with ctx.pose({joint: 0.13 * r.joint_travel_scale}):
            lifted_z = ctx.part_world_position(dropper)[2]
        ctx.check(
            "dropper lifts straight up out of the mouth",
            lifted_z > rest_z + 0.10 * r.joint_travel_scale,
            details=f"rest_z={rest_z:.4f}, lifted_z={lifted_z:.4f}",
        )

    elif r.closure_mechanism == "pour_spout":
        flip_cap = object_model.get_part("flip_cap")
        joint = object_model.get_articulation("bottle_to_flip_cap")
        ctx.allow_overlap(
            flip_cap, bottle, elem_a="flip_cap", elem_b="pour_spout",
            reason="Flip cap rests over the pour-spout opening when closed.",
        )
        ctx.check(
            "bottle has fixed pour_spout insert visual",
            bottle.get_visual("pour_spout") is not None,
            details="pour_spout visual missing",
        )
        ctx.check(
            "bottle_to_flip_cap is REVOLUTE about +X",
            joint.articulation_type == ArticulationType.REVOLUTE
            and abs(joint.axis[0]) > 0.99,
            details=f"axis={joint.axis}, type={joint.articulation_type}",
        )
        top0 = ctx.part_world_aabb(flip_cap)[1][2]
        with ctx.pose({joint: 1.5 * r.joint_travel_scale}):
            top1 = ctx.part_world_aabb(flip_cap)[1][2]
        ctx.check(
            "flip cap flips open at positive q (top rises)",
            top1 > top0 + 0.003,
            details=f"closed_top_z={top0:.4f}, open_top_z={top1:.4f}",
        )

    elif r.closure_mechanism == "codd_marble":
        marble = object_model.get_part("marble")
        joint = object_model.get_articulation("bottle_to_marble")
        ctx.allow_isolated_part(
            marble,
            reason="Marble is captive inside the Codd-neck chamber, retained by the "
            "pinch ring constriction below.",
        )
        ctx.allow_overlap(
            marble, bottle, elem_a="marble", elem_b="bottle_glass",
            reason="Marble is captive inside the Codd-neck chamber as a stopper.",
        )
        ctx.expect_within(
            marble, bottle, axes="xy", margin=0.004,
            name="marble stays centered in the bottle neck (XY)",
        )
        ctx.check(
            "bottle has fixed rubber_ring visual",
            bottle.get_visual("rubber_ring") is not None,
            details="rubber_ring visual missing",
        )
        ctx.check(
            "bottle_to_marble is PRISMATIC about -Z",
            joint.articulation_type == ArticulationType.PRISMATIC
            and joint.axis[2] < -0.99,
            details=f"axis={joint.axis}, type={joint.articulation_type}",
        )
        rest_z = ctx.part_world_position(marble)[2]
        with ctx.pose({joint: 0.025 * r.joint_travel_scale}):
            open_z = ctx.part_world_position(marble)[2]
        ctx.check(
            "marble pushes down into the chamber to open",
            open_z < rest_z - 0.015 * r.joint_travel_scale,
            details=f"rest_z={rest_z:.4f}, open_z={open_z:.4f}",
        )

    # ---- at least one non-fixed closure joint exists ----
    non_fixed = [
        j for j in object_model.articulations
        if j.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "at least one non-fixed closure joint exists",
        len(non_fixed) >= 1,
        details=f"non-fixed joints={[j.name for j in non_fixed]}",
    )

    return ctx.report()
