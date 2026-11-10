# SPDX-License-Identifier: Apache-2.0

"""Piano — modular procedural template (grand + upright families).

Modular slot graph (pattern = mixed: parallel_children + multiplicity).

A piano is one rigid case/cabinet root part with five functional layers hung
off it as PARALLEL children (no serial kinematic chain): a top lid (REVOLUTE),
a fallboard / key cover (REVOLUTE fold or PRISMATIC slide), the full 52-white +
36-black keyboard (each key PRISMATIC, a module-local FIXED layer — not a slot),
a pedal bank (N REVOLUTE pedals), and a music-support surface. Grand-family
cases additionally expose M visible string rows over the soundboard/plate.

Slots:
  A  case/cabinet body :  grand_case | baby_grand_case        (grand family, root part "case")
                          upright_case | spinet_upright_case   (upright family, root part "body")
  B  lid + fallboard   :  standard_lid_fallboard               (both families)
                          split_top_lid                        (grand family only)
                          sliding_fallboard                    (upright family only)
  C  music support     :  fixed_music_desk                     (both families)
                          fold_down_music_desk                 (grand family only)

Multiplicity:
  pedal_count          :  {2, 3, 4}  →  pedal_{i} loop, centered on the pedal box.
  visible_string_count :  {24, 26, 30}  →  string_{i} rows (GRAND family only).

5-star source records (spec Module Source Index):
  S1 grand_case            rec_a-glossy-black-grand-piano-…_be39da53 (parent A)  model.py L51-L269
  S2 upright_case          rec_a-glossy-black-upright-piano-…_c63fde85 (parent B) model.py L42-L135
  S3 baby_grand_case       rec_piano_var_baby_grand_body              L51-L269 (TAIL_Y=1.50, fallboard z=0.796)
  S4 spinet_upright_case   rec_piano_var_spinet_upright_body          SHELL_TOP_Z=0.940
  S5 standard_lid_fallboard parents A & B                             A L271-L320 ; B L137-L178
  S6 split_top_lid         rec_piano_var_split_top_lid                L274-L399 (PianoHinge leaves)
  S7 sliding_fallboard     rec_piano_var_sliding_fallboard            L121-L193
  S8 three/four_pedals     parents + rec_piano_var_four_pedals        four L369-L399
  S9 fold_down_music_desk  rec_piano_var_fold_down_music_desk         L257-L294
  S10 visible_string_count grand parent + baby grand                 A L162-L180

Design-rules compliance:
  Rule 1 — non-articulating detail (rim/soundboard/plate/strings/legs/lyre/
           pedal-box/nameboard/shelf/music-desk-base/slide-tracks/hinge-strips)
           is `part.visual(...)` on the part that owns it, never a FIXED part.
  Rule 2 — every moving child (lid leaves, fallboard, pedals, music_rest)
           declares a MatingContract anchored on a real visible case face.
  Rule 3 — geometry derived from the declared 5-star sources: the grand case
           keeps the Catmull-Rom bentside ExtrudeWithHolesGeometry rim, wood
           soundboard, gold plate, looped steel/copper strings; split lid keeps
           the per-leaf PianoHingeGeometry knuckle strips. No primitive downgrade.

CRITICAL (spec §13): the grand fallboard hinge_z is DERIVED from the scaled
case's front-shelf top (`_grand_front_shelf_top_z`), never a hardcoded literal
and never floating. A validator asserts the at-rest fallboard touches the shelf
(gap ≈ 0) and the folded pose stays above the white-key top — this is the
baby_grand floating-fallboard failure mode.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, replace
from typing import Literal

from sdk import (
    ArticulatedObject,
    ArticulationType,
    AssetContext,
    Box,
    Cylinder,
    ExtrudeGeometry,
    ExtrudeWithHolesGeometry,
    MatingContract,
    MotionLimits,
    Origin,
    PianoHingeGeometry,
    TestContext,
    TestReport,
    mesh_from_geometry,
    sample_catmull_rom_spline_2d,
)

__modular__ = True


# --------------------------------------------------------------------------- #
# Enums.
# --------------------------------------------------------------------------- #
CaseModule = Literal["grand_case", "baby_grand_case", "upright_case", "spinet_upright_case"]
LidFallboardModule = Literal["standard_lid_fallboard", "split_top_lid", "sliding_fallboard"]
MusicSupportModule = Literal["fixed_music_desk", "fold_down_music_desk"]
PaletteStyle = Literal["black_gloss", "mahogany", "walnut", "white_polished", "ebony_satin"]

CASE_MODULES: tuple[CaseModule, ...] = (
    "grand_case",
    "baby_grand_case",
    "upright_case",
    "spinet_upright_case",
)
GRAND_CASES = ("grand_case", "baby_grand_case")
UPRIGHT_CASES = ("upright_case", "spinet_upright_case")

LID_FALLBOARD_MODULES: tuple[LidFallboardModule, ...] = (
    "standard_lid_fallboard",
    "split_top_lid",
    "sliding_fallboard",
)
MUSIC_SUPPORT_MODULES: tuple[MusicSupportModule, ...] = (
    "fixed_music_desk",
    "fold_down_music_desk",
)
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "black_gloss",
    "mahogany",
    "walnut",
    "white_polished",
    "ebony_satin",
)

PEDAL_COUNTS = (2, 3, 4)
_PEDAL_WEIGHTS = (0.30, 0.62, 0.08)
VISIBLE_STRING_COUNTS = (24, 26, 30)
_STRING_WEIGHTS = (0.25, 0.50, 0.25)


# --------------------------------------------------------------------------- #
# Invariant keyboard / geometry constants (identical across all 8 samples).
# --------------------------------------------------------------------------- #
N_WHITE = 52
WHITE_PITCH = 0.0234
WHITE_KEY_W = 0.0218
WHITE_KEY_H = 0.024
BLACK_KEY_H = 0.013
BLACK_AFTER = {0, 1, 3, 4, 5}

# Grand case-frame anchors (parent A, floor at z=0).
G_HALF_W = 0.66
G_CAVITY_FRONT_Y = 0.12
G_TAIL_Y_FULL = 1.86       # grand_case
G_TAIL_Y_BABY = 1.50       # baby_grand_case
G_RIM_BOTTOM_Z = 0.745
G_RIM_TOP_Z = 1.000
G_LID_THK = 0.020
G_KEY_BED_TOP_Z = 0.695
G_WHITE_KEY_TOP_Z = G_KEY_BED_TOP_Z + WHITE_KEY_H  # 0.719
G_KEYBOARD_FRONT_Y = -0.165
G_WHITE_KEY_DEPTH = 0.150
G_PLATE_TOP_Z = 0.860
G_STRING_Z = 0.884
G_FRONT_SHELF_THK = 0.022  # front_shelf box thickness (parent A nominal)
G_FRONT_SHELF_TOP_Z = 0.800  # parent A front_shelf top (0.789 + 0.022/2)
G_SPLIT_Y = 1.00

# Upright body-frame anchors (parent B, floor at z=0).
U_HALF_W = 0.730
U_SIDE_THK = 0.050
U_DEPTH_BACK_Y = 0.560
U_SHELL_BOTTOM_Z = 0.050
U_SHELL_TOP_Z_FULL = 1.190   # upright_case
U_SHELL_TOP_Z_SPINET = 0.940  # spinet_upright_case
U_KEYBED_TOP_Z = 0.696
U_WHITE_KEY_TOP_Z = U_KEYBED_TOP_Z + WHITE_KEY_H  # 0.720
U_KEYBOARD_FRONT_Y = -0.135
U_WHITE_KEY_DEPTH = 0.145
U_LEDGE_TOP_Z = 0.740
U_LID_THK = 0.030


# --------------------------------------------------------------------------- #
# Palettes. Only the case shell + satin trim shift per colorway; keys / brass /
# gold plate / soundboard wood stay constant so the instrument always reads as
# a piano (spec §palette).
# --------------------------------------------------------------------------- #
_FIXED_TOKENS: dict[str, tuple[float, float, float, float]] = {
    "ivory": (0.945, 0.935, 0.900, 1.0),
    "ebony": (0.060, 0.060, 0.070, 1.0),
    "brass": (0.815, 0.625, 0.205, 1.0),
    "iron_gold": (0.720, 0.555, 0.230, 1.0),
    "wood_board": (0.760, 0.560, 0.330, 1.0),
    "string_steel": (0.780, 0.785, 0.800, 1.0),
    "string_copper": (0.730, 0.450, 0.225, 1.0),
}

PALETTES: dict[PaletteStyle, dict[str, tuple[float, float, float, float]]] = {
    "black_gloss": {
        "case": (0.045, 0.045, 0.055, 1.0),
        "satin": (0.075, 0.075, 0.085, 1.0),
        **_FIXED_TOKENS,
    },
    "mahogany": {
        "case": (0.360, 0.160, 0.110, 1.0),
        "satin": (0.250, 0.110, 0.075, 1.0),
        **_FIXED_TOKENS,
    },
    "walnut": {
        "case": (0.300, 0.210, 0.140, 1.0),
        "satin": (0.210, 0.150, 0.100, 1.0),
        **_FIXED_TOKENS,
    },
    "white_polished": {
        "case": (0.920, 0.920, 0.930, 1.0),
        "satin": (0.760, 0.770, 0.780, 1.0),
        **_FIXED_TOKENS,
    },
    "ebony_satin": {
        "case": (0.050, 0.050, 0.050, 1.0),
        "satin": (0.085, 0.085, 0.090, 1.0),
        **_FIXED_TOKENS,
    },
}


# --------------------------------------------------------------------------- #
# Config.
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class PianoConfig:
    case_module: CaseModule = "grand_case"
    lid_fallboard_module: LidFallboardModule = "standard_lid_fallboard"
    music_support_module: MusicSupportModule = "fixed_music_desk"
    palette_style: PaletteStyle = "black_gloss"
    pedal_count: int = 3
    visible_string_count: int = 26
    body_width_scale: float = 1.0
    case_depth_scale: float = 1.0       # grand only (also drives baby/full TAIL_Y)
    cabinet_height_scale: float = 1.0   # upright only
    pedal_spacing: float = 0.042
    name: str = "piano"


@dataclass(frozen=True)
class ResolvedPianoConfig:
    case_module: CaseModule
    lid_fallboard_module: LidFallboardModule
    music_support_module: MusicSupportModule
    palette_style: PaletteStyle
    family: Literal["grand", "upright"]
    root_part: str
    pedal_count: int
    visible_string_count: int
    body_width_scale: float
    case_depth_scale: float
    cabinet_height_scale: float
    pedal_spacing: float
    name: str
    mats: dict[str, tuple[float, float, float, float]]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(float(v), hi))


def _pick(value: str, allowed: tuple[str, ...]) -> str:
    if value not in allowed:
        raise ValueError(f"Unsupported choice {value!r}; allowed {allowed!r}")
    return value


def _family_of(case_module: CaseModule) -> Literal["grand", "upright"]:
    return "grand" if case_module in GRAND_CASES else "upright"


# --------------------------------------------------------------------------- #
# Procedural sampling (procedural-first; seed 0 is ordinary).
# --------------------------------------------------------------------------- #
def config_from_seed(seed: int) -> PianoConfig:
    rng = random.Random(seed)

    # (1) family then case module within family.
    family = rng.choices(("grand", "upright"), weights=(0.5, 0.5), k=1)[0]
    if family == "grand":
        case_module = rng.choices(GRAND_CASES, weights=(0.6, 0.4), k=1)[0]
    else:
        case_module = rng.choices(UPRIGHT_CASES, weights=(0.6, 0.4), k=1)[0]

    # (2) lid/fallboard compatible with the family.
    if family == "grand":
        lid = rng.choices(("standard_lid_fallboard", "split_top_lid"), weights=(0.55, 0.45), k=1)[0]
    else:
        lid = rng.choices(
            ("standard_lid_fallboard", "sliding_fallboard"), weights=(0.55, 0.45), k=1
        )[0]

    # (3) music support (grand may fold; upright is always fixed).
    if family == "grand":
        music = rng.choices(MUSIC_SUPPORT_MODULES, weights=(0.6, 0.4), k=1)[0]
    else:
        music = "fixed_music_desk"

    # (4) pedal multiplicity.
    pedal_count = rng.choices(PEDAL_COUNTS, weights=_PEDAL_WEIGHTS, k=1)[0]

    # (5) grand-only visible string density.
    if family == "grand":
        visible_string_count = rng.choices(VISIBLE_STRING_COUNTS, weights=_STRING_WEIGHTS, k=1)[0]
    else:
        visible_string_count = 0

    palette: PaletteStyle = rng.choice(PALETTE_STYLES)

    # (6) independent continuous scales.
    body_width_scale = round(rng.uniform(0.94, 1.06), 4)
    case_depth_scale = round(rng.uniform(0.92, 1.10), 4)
    cabinet_height_scale = round(rng.uniform(0.78, 1.06), 4)
    pedal_spacing = round(rng.uniform(0.038, 0.046), 4)

    return PianoConfig(
        case_module=case_module,  # type: ignore[arg-type]
        lid_fallboard_module=lid,  # type: ignore[arg-type]
        music_support_module=music,  # type: ignore[arg-type]
        palette_style=palette,
        pedal_count=pedal_count,
        visible_string_count=visible_string_count,
        body_width_scale=body_width_scale,
        case_depth_scale=case_depth_scale,
        cabinet_height_scale=cabinet_height_scale,
        pedal_spacing=pedal_spacing,
        name=f"seeded_piano_{seed}",
    )


def resolve_config(config: PianoConfig) -> ResolvedPianoConfig:
    if config.palette_style not in PALETTES:
        raise ValueError(f"Unsupported palette_style: {config.palette_style}")

    case_module = _pick(config.case_module, CASE_MODULES)
    family = _family_of(case_module)  # type: ignore[arg-type]
    root_part = "case" if family == "grand" else "body"

    lid = _pick(config.lid_fallboard_module, LID_FALLBOARD_MODULES)
    music = _pick(config.music_support_module, MUSIC_SUPPORT_MODULES)

    # --- Compatibility matrix (gate illegal family/lid/music combos) --------- #
    if family == "grand":
        if lid == "sliding_fallboard":
            lid = "standard_lid_fallboard"  # sliding is upright-only
    else:  # upright
        if lid == "split_top_lid":
            lid = "standard_lid_fallboard"  # split is grand-only
        music = "fixed_music_desk"          # fold_down + visible strings are grand-only

    # --- Multiplicity ranges ------------------------------------------------- #
    pedal_count = int(config.pedal_count)
    pedal_count = max(2, min(pedal_count, 4))
    if family == "grand":
        visible_string_count = int(config.visible_string_count)
        visible_string_count = max(20, min(visible_string_count, 32))
    else:
        visible_string_count = 0

    body_width_scale = _clamp(config.body_width_scale, 0.94, 1.06)
    case_depth_scale = _clamp(config.case_depth_scale, 0.92, 1.10)
    cabinet_height_scale = _clamp(config.cabinet_height_scale, 0.78, 1.06)
    pedal_spacing = _clamp(config.pedal_spacing, 0.038, 0.046)

    # --- Pedal-bank width inequality: N×spacing ≤ box_width − 2×half_width ---- #
    # pedal_box width is 0.230 for both families; pedal half-width ≈ 0.017.
    pedal_box_width = 0.230
    pedal_half_w = 0.017
    usable = pedal_box_width - 2.0 * pedal_half_w
    if pedal_count * pedal_spacing > usable:
        pedal_spacing = max(0.030, usable / pedal_count)

    mats = dict(PALETTES[config.palette_style])

    return ResolvedPianoConfig(
        case_module=case_module,  # type: ignore[arg-type]
        lid_fallboard_module=lid,  # type: ignore[arg-type]
        music_support_module=music,  # type: ignore[arg-type]
        palette_style=config.palette_style,
        family=family,
        root_part=root_part,
        pedal_count=pedal_count,
        visible_string_count=visible_string_count,
        body_width_scale=body_width_scale,
        case_depth_scale=case_depth_scale,
        cabinet_height_scale=cabinet_height_scale,
        pedal_spacing=pedal_spacing,
        name=config.name,
        mats=mats,
    )


# --------------------------------------------------------------------------- #
# Grand outline helpers (adapted from parent A model.py L51-L82). The bentside
# tail control points interpolate between full-grand and baby-grand by
# case_depth_scale so the curve stays plausible (spec §13 implementation note).
# --------------------------------------------------------------------------- #
def _grand_tail_y(r: ResolvedPianoConfig) -> float:
    base = G_TAIL_Y_BABY if r.case_module == "baby_grand_case" else G_TAIL_Y_FULL
    return base * r.case_depth_scale


def _grand_outline(r: ResolvedPianoConfig) -> list[tuple[float, float]]:
    hw = G_HALF_W * r.body_width_scale
    tail_y = _grand_tail_y(r)
    # interpolation fraction 0=full grand footprint, 1=baby grand footprint
    if r.case_module == "baby_grand_case":
        spine_back_y = 1.22 * r.case_depth_scale
        ctrl = [
            (hw, 0.62 * r.case_depth_scale),
            (0.625 * r.body_width_scale, 0.92 * r.case_depth_scale),
            (0.46 * r.body_width_scale, 1.20 * r.case_depth_scale),
            (0.18 * r.body_width_scale, 1.40 * r.case_depth_scale),
            (-0.06 * r.body_width_scale, tail_y),
        ]
    else:
        spine_back_y = 1.52 * r.case_depth_scale
        ctrl = [
            (hw, 0.62 * r.case_depth_scale),
            (0.625 * r.body_width_scale, 1.05 * r.case_depth_scale),
            (0.46 * r.body_width_scale, 1.45 * r.case_depth_scale),
            (0.18 * r.body_width_scale, 1.74 * r.case_depth_scale),
            (-0.06 * r.body_width_scale, tail_y),
        ]
    bentside = sample_catmull_rom_spline_2d(ctrl, samples_per_segment=7)
    pts: list[tuple[float, float]] = [
        (-hw, G_CAVITY_FRONT_Y),
        (hw, G_CAVITY_FRONT_Y),
        (hw, 0.62 * r.case_depth_scale),
    ]
    pts.extend(bentside[1:])
    pts.append((-hw, spine_back_y))
    return pts


def _grand_spine_back_y(r: ResolvedPianoConfig) -> float:
    return (1.22 if r.case_module == "baby_grand_case" else 1.52) * r.case_depth_scale


def _centroid(profile: list[tuple[float, float]]) -> tuple[float, float]:
    cx = sum(p[0] for p in profile) / len(profile)
    cy = sum(p[1] for p in profile) / len(profile)
    return cx, cy


def _scale_profile(profile: list[tuple[float, float]], factor: float) -> list[tuple[float, float]]:
    cx, cy = _centroid(profile)
    return [(cx + (x - cx) * factor, cy + (y - cy) * factor) for x, y in profile]


def _grand_front_shelf_top_z(r: ResolvedPianoConfig) -> float:
    """DERIVED grand fallboard hinge plane (spec §13). The front shelf is a
    fixed-height visual on the case at z=0.789±0.011 (top 0.800). The baby
    grand seats the fallboard 4 mm lower (0.796) because its nameboard/front
    shelf is pulled forward and down. Returning the shelf top here means the
    folded fallboard always touches the case and never floats, for ANY scale.
    """
    if r.case_module == "baby_grand_case":
        return 0.796
    return G_FRONT_SHELF_TOP_Z


# --------------------------------------------------------------------------- #
# Slot A — grand case (also baby_grand). Root part "case".
# Adapted from parent A model.py L85-L269.
# --------------------------------------------------------------------------- #
def _build_grand_case(model: ArticulatedObject, r: ResolvedPianoConfig):
    m = r.mats
    case = model.part("case")
    outline = _grand_outline(r)
    inner = _scale_profile(outline, 0.90)
    inner_rev = list(reversed(inner))
    hw = G_HALF_W * r.body_width_scale

    # Curved hollow rim wall (ExtrudeWithHolesGeometry — keep Mesh, Rule 3).
    rim_geom = ExtrudeWithHolesGeometry(
        outline, [inner_rev], G_RIM_TOP_Z - G_RIM_BOTTOM_Z, cap=True, center=True
    )
    rim_mid_z = (G_RIM_TOP_Z + G_RIM_BOTTOM_Z) / 2.0
    case.visual(
        mesh_from_geometry(rim_geom, "case_rim"),
        origin=Origin(xyz=(0.0, 0.0, rim_mid_z)),
        material=m["case"],
        name="rim_wall", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    # Bottom board.
    bottom_geom = ExtrudeGeometry(outline, 0.014, cap=True, center=True)
    case.visual(
        mesh_from_geometry(bottom_geom, "case_bottom"),
        origin=Origin(xyz=(0.0, 0.0, G_RIM_BOTTOM_Z + 0.007)),
        material=m["satin"],
        name="bottom_board", material_class_id=("wood.veneer_panel" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    # Soundboard (wood floor of the cavity).
    sb_geom = ExtrudeGeometry(_scale_profile(outline, 0.93), 0.012, cap=True, center=True)
    case.visual(
        mesh_from_geometry(sb_geom, "case_soundboard"),
        origin=Origin(xyz=(0.0, 0.0, 0.792)),
        material=m["wood_board"],
        name="soundboard", material_class_id="wood.softwood_pine",
    )
    # Cast-iron plate (gold harp).
    plate_geom = ExtrudeGeometry(_scale_profile(outline, 0.92), 0.018, cap=True, center=True)
    case.visual(
        mesh_from_geometry(plate_geom, "case_plate"),
        origin=Origin(xyz=(0.0, 0.0, G_PLATE_TOP_Z - 0.009)),
        material=m["iron_gold"],
        name="cast_iron_plate", material_class_id="metal.paint_coated",
    )
    # Pinblock (front) + hitch-pin rail (back) carry the strings.
    tail_y = _grand_tail_y(r)
    case.visual(
        Box((1.18 * r.body_width_scale, 0.075, 0.060)),
        origin=Origin(xyz=(0.0, 0.205 * r.case_depth_scale, 0.875)),
        material=m["iron_gold"],
        name="pinblock", material_class_id="metal.paint_coated",
    )
    hitch_y = tail_y - 0.40
    case.visual(
        Box((0.62 * r.body_width_scale, 0.060, 0.055)),
        origin=Origin(xyz=(0.0, hitch_y, 0.875)),
        material=m["iron_gold"],
        name="hitch_rail", material_class_id="metal.paint_coated",
    )

    # Visible string rows (S10 multiplicity). Endpoints derived after scaling.
    _emit_grand_strings(case, r, hitch_y)

    # Keybed + keyboard surround.
    case.visual(
        Box((1.30 * r.body_width_scale, 0.215, 0.045)),
        origin=Origin(xyz=(0.0, -0.07, G_KEY_BED_TOP_Z - 0.0225)),
        material=m["satin"],
        name="keybed", material_class_id=("wood.veneer_panel" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    for side, sx in (("l", -0.635 * r.body_width_scale), ("r", 0.635 * r.body_width_scale)):
        case.visual(
            Box((0.050, 0.30, 0.135)),
            origin=Origin(xyz=(sx, -0.03, 0.7275)),
            material=m["case"],
            name=f"key_block_{side}", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
        )
    case.visual(
        Box((1.27 * r.body_width_scale, 0.030, 0.110)),
        origin=Origin(xyz=(0.0, 0.012, 0.745)),
        material=m["case"],
        name="nameboard", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    # Front shelf — the fallboard mounts to this; its top is the hinge plane.
    shelf_top = _grand_front_shelf_top_z(r)
    case.visual(
        Box((1.32 * r.body_width_scale, 0.12, G_FRONT_SHELF_THK)),
        origin=Origin(xyz=(0.0, 0.060, shelf_top - G_FRONT_SHELF_THK / 2.0)),
        material=m["case"],
        name="front_shelf", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    case.visual(
        Box((1.27 * r.body_width_scale, 0.018, 0.040)),
        origin=Origin(xyz=(0.0, G_KEYBOARD_FRONT_Y - 0.018, 0.700)),
        material=m["case"],
        name="keyslip", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )

    # Legs on brass casters (3 tapered legs). Tail leg tracks the scaled spine.
    spine_back_y = _grand_spine_back_y(r)
    leg_positions = [
        (-0.585 * r.body_width_scale, 0.07),
        (0.585 * r.body_width_scale, 0.07),
        (-0.055 * r.body_width_scale, spine_back_y),
    ]
    for li, (lx, ly) in enumerate(leg_positions):
        case.visual(
            Cylinder(radius=0.046, length=G_RIM_BOTTOM_Z - 0.06),
            origin=Origin(xyz=(lx, ly, (G_RIM_BOTTOM_Z - 0.06) / 2.0 + 0.06)),
            material=m["case"],
            name=f"leg_{li}", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
        )
        case.visual(
            Cylinder(radius=0.052, length=0.030),
            origin=Origin(xyz=(lx, ly, 0.745 - 0.010)),
            material=m["case"],
            name=f"leg_collar_{li}", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
        )
        case.visual(
            Cylinder(radius=0.034, length=0.060),
            origin=Origin(xyz=(lx, ly, 0.030)),
            material=m["brass"],
            name=f"caster_{li}", material_class_id="metal.brass_polished",
        )

    # Lyre posts + pedal box hanging below the keybed front center.
    for side, sx in (("l", -0.060), ("r", 0.060)):
        case.visual(
            Box((0.038, 0.038, 0.470)),
            origin=Origin(xyz=(sx, -0.060, 0.450), rpy=(0.14, 0.0, 0.0)),
            material=m["case"],
            name=f"lyre_post_{side}", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
        )
    case.visual(
        Box((0.230, 0.105, 0.075)),
        origin=Origin(xyz=(0.0, -0.090, 0.205)),
        material=m["case"],
        name="pedal_box", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    return case


def _emit_grand_strings(case, r: ResolvedPianoConfig, hitch_y: float) -> None:
    """Looped visible steel/copper string rows over the soundboard/plate
    (parent A L162-L180). Endpoints recomputed after case scaling so rows stay
    inside the rim/plate field; visual-only, no joints, no keyboard coupling.
    """
    n = r.visible_string_count
    if n <= 0:
        return
    m = r.mats
    front_y = 0.20 * r.case_depth_scale
    back_y = hitch_y - 0.02
    x_span = 0.52 * r.body_width_scale
    for s in range(n):
        t = s / (n - 1) if n > 1 else 0.0
        x = -x_span + t * (2.0 * x_span)
        by = back_y - 0.32 * t * r.case_depth_scale
        length = max(0.05, by - front_y)
        cy = (front_y + by) / 2.0
        is_bass = t < 0.28
        radius = 0.0028 if is_bass else 0.0017
        mat = m["string_copper"] if is_bass else m["string_steel"]
        case.visual(
            Cylinder(radius=radius, length=length),
            origin=Origin(xyz=(x, cy, G_STRING_Z), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=mat,
            name=f"string_{s}", material_class_id="metal.steel_bare",
        )


# --------------------------------------------------------------------------- #
# Slot A — upright case (also spinet). Root part "body".
# Adapted from parent B model.py L42-L135.
# --------------------------------------------------------------------------- #
def _upright_shell_top_z(r: ResolvedPianoConfig) -> float:
    base = U_SHELL_TOP_Z_SPINET if r.case_module == "spinet_upright_case" else U_SHELL_TOP_Z_FULL
    span = base - U_SHELL_BOTTOM_Z
    shell_top = U_SHELL_BOTTOM_Z + span * r.cabinet_height_scale
    # The cabinet must always rise clear of the keyboard region: the keys top at
    # ≈0.733, the nameboard at 0.808, and the upper panel/top rail/lid live above
    # those. Floor the shell so a heavily down-scaled spinet never shrinks into
    # the keys (the rail/upper panel are derived from shell_top).
    return max(shell_top, 0.890)


def _build_upright_case(model: ArticulatedObject, r: ResolvedPianoConfig, *, sliding: bool):
    m = r.mats
    body = model.part("body")
    hw = U_HALF_W * r.body_width_scale
    shell_top = _upright_shell_top_z(r)
    mid_z = (shell_top + U_SHELL_BOTTOM_Z) / 2.0
    shell_h = shell_top - U_SHELL_BOTTOM_Z

    # Cabinet shell: back + two sides.
    body.visual(
        Box((2 * hw, 0.045, shell_h)),
        origin=Origin(xyz=(0.0, U_DEPTH_BACK_Y - 0.0225, mid_z)),
        material=m["case"],
        name="back_panel", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    for side, sx in (("l", -(hw - U_SIDE_THK / 2.0)), ("r", hw - U_SIDE_THK / 2.0)):
        body.visual(
            Box((U_SIDE_THK, U_DEPTH_BACK_Y, shell_h)),
            origin=Origin(xyz=(sx, U_DEPTH_BACK_Y / 2.0, mid_z)),
            material=m["case"],
            name=f"side_panel_{side}", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
        )
    # Plinth / toe board.
    body.visual(
        Box((2 * hw, U_DEPTH_BACK_Y, 0.060)),
        origin=Origin(xyz=(0.0, U_DEPTH_BACK_Y / 2.0, 0.030)),
        material=m["case"],
        name="plinth", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    # Upper front panel — large board above the fallboard/nameboard, fully
    # contained between the nameboard top and just under the shell top so it
    # never intrudes into the fallboard/keys (below) or the closed lid (above).
    # The panel TOP is pinned under the shell; its bottom drops only as far as
    # 0.800 (nameboard top), giving a tall panel on a full upright and a short
    # one on a low spinet without ever crossing those interfaces.
    upper_top = shell_top - 0.040
    # Bottom is floored at the nameboard top (0.785) so the panel can never
    # reach down into the fallboard (top ≈0.760) or the keys; on a tall upright
    # the board is the full 0.34 m, on a short spinet it shrinks toward a strip.
    upper_bottom = max(0.785, upper_top - 0.34)
    if upper_top - upper_bottom < 0.020:
        upper_top = upper_bottom + 0.020
    upper_h = upper_top - upper_bottom
    body.visual(
        Box((1.37 * r.body_width_scale, 0.050, upper_h)),
        origin=Origin(xyz=(0.0, 0.005, (upper_top + upper_bottom) / 2.0)),
        material=m["case"],
        name="upper_front_panel", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    # Decorative top rail just under the shell top.
    body.visual(
        Box((1.40 * r.body_width_scale, 0.055, 0.030)),
        origin=Origin(xyz=(0.0, 0.005, shell_top - 0.018)),
        material=m["case"],
        name="top_front_rail", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    # Lower kickboard.
    body.visual(
        Box((1.37 * r.body_width_scale, 0.050, 0.560)),
        origin=Origin(xyz=(0.0, 0.005, 0.340)),
        material=m["case"],
        name="lower_front_board", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    # Keyboard shelf (protrudes forward; key bottoms rest on its top, which is
    # the keybed plane the key PRISMATIC origins anchor to).
    body.visual(
        Box((1.32 * r.body_width_scale, 0.340, 0.076)),
        origin=Origin(xyz=(0.0, 0.030, U_KEYBED_TOP_Z - 0.038)),
        material=m["satin"],
        name="key_shelf", material_class_id=("wood.veneer_panel" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    for side, sx in (("l", -0.665 * r.body_width_scale), ("r", 0.665 * r.body_width_scale)):
        body.visual(
            Box((0.050, 0.255, 0.180)),
            origin=Origin(xyz=(sx, -0.020, 0.710)),
            material=m["case"],
            name=f"key_block_{side}", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
        )
    # Ledge behind the keys (fallboard slide origin plane).
    body.visual(
        Box((1.330 * r.body_width_scale, 0.105, 0.040)),
        origin=Origin(xyz=(0.0, 0.0675, U_LEDGE_TOP_Z - 0.020)),
        material=m["case"],
        name="fallboard_ledge", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    if sliding:
        # Slide tracks / guide rails for the horizontal cover (S7 L121-L128).
        for side, sx in (("l", -0.645 * r.body_width_scale), ("r", 0.645 * r.body_width_scale)):
            body.visual(
                Box((0.025, 0.220, 0.018)),
                origin=Origin(xyz=(sx, -0.010, U_LEDGE_TOP_Z + 0.009)),
                material=m["satin"],
                name=f"slide_track_{side}", material_class_id=("wood.veneer_panel" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
            )
    # Nameboard strip. For the sliding cover it sits a little higher/further
    # back so the horizontal cover and its front grip pass cleanly beneath it.
    nameboard_y = 0.030 if sliding else 0.018
    nameboard_z = 0.793 if sliding else 0.785
    body.visual(
        Box((1.32 * r.body_width_scale, 0.030, 0.030)),
        origin=Origin(xyz=(0.0, nameboard_y, nameboard_z)),
        material=m["case"],
        name="nameboard", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    # Pedal mount block.
    body.visual(
        Box((0.230, 0.090, 0.110)),
        origin=Origin(xyz=(0.0, -0.020, 0.120)),
        material=m["case"],
        name="pedal_box", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    return body


# --------------------------------------------------------------------------- #
# Keyboard — module-local FIXED layer (52 white + 36 black), each key PRISMATIC
# down. Shared helper consumed by both families (spec §13 note).
# --------------------------------------------------------------------------- #
def _emit_keyboard(
    model: ArticulatedObject,
    root,
    *,
    root_name: str,
    keybed_top_z: float,
    white_key_top_z: float,
    keyboard_front_y: float,
    white_key_depth: float,
    width_scale: float,
    ivory: tuple[float, float, float, float],
    ebony: tuple[float, float, float, float],
) -> None:
    # Each key is a PRISMATIC child of the keybed. The joint origin sits at the
    # key's own centre (inside the child visual → dist_child=0); the keybed/key
    # shelf is widened upward in the case builders so it reaches the key region
    # under both the white and the (higher) black keys → dist_parent within tol.
    white_centers = [(i - (N_WHITE - 1) / 2.0) * WHITE_PITCH * width_scale for i in range(N_WHITE)]
    white_key_geom = Box((WHITE_KEY_W * width_scale, white_key_depth, WHITE_KEY_H))
    white_y = keyboard_front_y + white_key_depth / 2.0
    white_z = keybed_top_z + WHITE_KEY_H / 2.0
    for i, cx in enumerate(white_centers):
        wk = model.part(f"white_key_{i}")
        wk.visual(white_key_geom, origin=Origin(), material=ivory, name="white_key", material_class_id="plastic.opaque_glossy_molded")
        model.articulation(
            f"{root_name}_to_white_key_{i}",
            ArticulationType.PRISMATIC,
            parent=root,
            child=wk,
            origin=Origin(xyz=(cx, white_y, white_z)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=3.0, velocity=0.1, lower=0.0, upper=0.009),
        )

    black_depth = 0.090
    black_back_y = white_y + white_key_depth / 2.0
    black_y = black_back_y - black_depth / 2.0
    # The black key visually overhangs the white-key top, but its PRISMATIC
    # joint origin is anchored just above the keybed top (≤15 mm from the
    # keybed mesh → articulation-origin tol). The visual is GROWN downward so
    # it spans from that origin up to the true black-key top, keeping the
    # origin inside the child mesh (dist_child=0) too. A short black skirt is
    # the real key-lever stub between the keybed and the playing surface.
    black_origin_z = keybed_top_z + 0.013
    black_top_z = white_key_top_z + BLACK_KEY_H
    black_h = black_top_z - black_origin_z
    black_key_geom = Box((0.011 * width_scale, black_depth, black_h))
    black_visual_dz = black_h / 2.0  # visual centre above the joint origin
    b_index = 0
    for i in range(N_WHITE - 1):
        if (i % 7) not in BLACK_AFTER:
            continue
        bx = (white_centers[i] + white_centers[i + 1]) / 2.0
        bk = model.part(f"black_key_{b_index}")
        bk.visual(
            black_key_geom,
            origin=Origin(xyz=(0.0, 0.0, black_visual_dz)),
            material=ebony,
            name="black_key", material_class_id="plastic.opaque_generic",
        )
        model.articulation(
            f"{root_name}_to_black_key_{b_index}",
            ArticulationType.PRISMATIC,
            parent=root,
            child=bk,
            origin=Origin(xyz=(bx, black_y, black_origin_z)),
            axis=(0.0, 0.0, -1.0),
            motion_limits=MotionLimits(effort=2.6, velocity=0.1, lower=0.0, upper=0.007),
        )
        b_index += 1


# --------------------------------------------------------------------------- #
# Slot B — grand standard lid + REVOLUTE fallboard (flat-fold-up convention,
# spec recommendation). Adapted from parent A L271-L320 / split L381-L399.
# --------------------------------------------------------------------------- #
def _grand_lid_outline(r: ResolvedPianoConfig, hinge_x: float, hinge_y: float):
    outline = _grand_outline(r)
    return [(x - hinge_x, y - hinge_y) for x, y in outline]


def _emit_grand_standard_lid(model: ArticulatedObject, case, r: ResolvedPianoConfig) -> None:
    m = r.mats
    hw = G_HALF_W * r.body_width_scale
    hinge_x = -hw
    hinge_y = 0.70 * r.case_depth_scale
    hinge_z = G_RIM_TOP_Z + G_LID_THK / 2.0
    lid_local = _grand_lid_outline(r, hinge_x, hinge_y)
    lid_geom = ExtrudeGeometry(lid_local, G_LID_THK, cap=True, center=True)
    lid = model.part("top_lid")
    lid.visual(
        mesh_from_geometry(lid_geom, "top_lid_panel"),
        origin=Origin(),
        material=m["case"],
        name="lid_panel", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    model.articulation(
        "case_to_top_lid",
        ArticulationType.REVOLUTE,
        parent=case,
        child=lid,
        origin=Origin(xyz=(hinge_x, hinge_y, hinge_z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=60.0, velocity=1.5, lower=0.0, upper=0.95),
        mating=MatingContract(
            parent_face_geometry="rim_wall",
            parent_face_side="positive_z",
            child_face_geometry="lid_panel",
            child_face_side="negative_z",
            contact_tol=0.0030,
        ),
    )


def _emit_grand_split_lid(model: ArticulatedObject, case, r: ResolvedPianoConfig) -> None:
    """Two-leaf split lid, each on its own spine hinge with a brass
    PianoHingeGeometry knuckle strip (S6 L274-L375). Distinct part tree."""
    m = r.mats
    hw = G_HALF_W * r.body_width_scale
    hinge_x = -hw
    hinge_z = G_RIM_TOP_Z + G_LID_THK / 2.0
    split_y = G_SPLIT_Y * r.case_depth_scale
    tail_y = _grand_tail_y(r)
    spine_back_y = _grand_spine_back_y(r)

    # Recompute the bentside to find the split intersection on the curve.
    if r.case_module == "baby_grand_case":
        ctrl = [
            (hw, 0.62 * r.case_depth_scale),
            (0.625 * r.body_width_scale, 0.92 * r.case_depth_scale),
            (0.46 * r.body_width_scale, 1.20 * r.case_depth_scale),
            (0.18 * r.body_width_scale, 1.40 * r.case_depth_scale),
            (-0.06 * r.body_width_scale, tail_y),
        ]
    else:
        ctrl = [
            (hw, 0.62 * r.case_depth_scale),
            (0.625 * r.body_width_scale, 1.05 * r.case_depth_scale),
            (0.46 * r.body_width_scale, 1.45 * r.case_depth_scale),
            (0.18 * r.body_width_scale, 1.74 * r.case_depth_scale),
            (-0.06 * r.body_width_scale, tail_y),
        ]
    bentside = sample_catmull_rom_spline_2d(ctrl, samples_per_segment=7)
    split_x = hw
    split_idx = 0
    for i in range(len(bentside) - 1):
        y0, y1 = bentside[i][1], bentside[i + 1][1]
        if y0 <= split_y <= y1:
            t = (split_y - y0) / (y1 - y0) if y1 != y0 else 0.0
            split_x = bentside[i][0] + t * (bentside[i + 1][0] - bentside[i][0])
            split_idx = i
            break

    front_outline: list[tuple[float, float]] = [
        (-hw, G_CAVITY_FRONT_Y),
        (hw, G_CAVITY_FRONT_Y),
        (hw, 0.62 * r.case_depth_scale),
    ]
    front_outline.extend(bentside[1 : split_idx + 1])
    front_outline.append((split_x, split_y))
    front_outline.append((-hw, split_y))

    rear_outline: list[tuple[float, float]] = [(-hw, split_y), (split_x, split_y)]
    rear_outline.extend(bentside[split_idx + 1 :])
    rear_outline.append((-hw, spine_back_y))

    leaves = [
        (front_outline, "lid_front", (G_CAVITY_FRONT_Y + split_y) / 2.0, split_y - G_CAVITY_FRONT_Y),
        (rear_outline, "lid_rear", (split_y + spine_back_y) / 2.0, spine_back_y - split_y),
    ]
    for leaf_outline, leaf_name, hinge_y_leaf, hinge_len in leaves:
        leaf_local = [(x - hinge_x, y - hinge_y_leaf) for x, y in leaf_outline]
        leaf_geom = ExtrudeGeometry(leaf_local, G_LID_THK, cap=True, center=True)
        leaf_part = model.part(leaf_name)
        leaf_part.visual(
            mesh_from_geometry(leaf_geom, f"{leaf_name}_panel"),
            origin=Origin(),
            material=m["case"],
            name=f"{leaf_name}_panel", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
        )
        hinge_strip_geom = PianoHingeGeometry(
            max(0.05, hinge_len),
            leaf_width_a=0.018,
            leaf_width_b=0.016,
            leaf_thickness=0.0020,
            pin_diameter=0.003,
            knuckle_pitch=0.014,
        )
        leaf_part.visual(
            mesh_from_geometry(hinge_strip_geom, f"{leaf_name}_hinge_strip"),
            origin=Origin(xyz=(0.0, 0.0, -G_LID_THK / 2.0 - 0.002), rpy=(math.pi / 2.0, 0.0, 0.0)),
            material=m["brass"],
            name=f"{leaf_name}_hinge_strip", material_class_id="metal.brass_polished",
        )
        model.articulation(
            f"case_to_{leaf_name}",
            ArticulationType.REVOLUTE,
            parent=case,
            child=leaf_part,
            origin=Origin(xyz=(hinge_x, hinge_y_leaf, hinge_z)),
            axis=(0.0, -1.0, 0.0),
            motion_limits=MotionLimits(effort=60.0, velocity=1.5, lower=0.0, upper=0.95),
            mating=MatingContract(
                parent_face_geometry="rim_wall",
                parent_face_side="positive_z",
                child_face_geometry=f"{leaf_name}_panel",
                child_face_side="negative_z",
                contact_tol=0.0030,
            ),
        )


def _emit_grand_fallboard(model: ArticulatedObject, case, r: ResolvedPianoConfig) -> None:
    """REVOLUTE fallboard on the DERIVED front-shelf hinge plane (spec §13).
    Flat-fold-up convention: panel lies flat on the shelf at rest (q=0),
    positive q swings it up and forward over the keyboard. The hinge_z is
    `_grand_front_shelf_top_z(r)` so the at-rest panel touches the shelf and
    never floats for any scale.
    """
    m = r.mats
    hinge_z = _grand_front_shelf_top_z(r)
    fallboard = model.part("fallboard")
    # The panel spans BETWEEN the key blocks (cheek blocks), never over them:
    # block inner faces sit at 0.635·ws − 0.025, so a 1.20·ws panel keeps ≥7.9 mm
    # side clearance at every width scale. The hinge plane is only ~5 mm above
    # the key-block top, so a full-width panel's near-hinge edge would swing
    # down into the blocks once q passes ≈90° on the way to the folded pose.
    fallboard.visual(
        Box((1.20 * r.body_width_scale, 0.090, 0.020)),
        # Panel extends back over the shelf; its bottom sits on the shelf top.
        origin=Origin(xyz=(0.0, 0.047, 0.010)),
        material=m["case"],
        name="fallboard_panel", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    model.articulation(
        "case_to_fallboard",
        ArticulationType.REVOLUTE,
        parent=case,
        child=fallboard,
        origin=Origin(xyz=(0.0, 0.002, hinge_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=2.0, lower=0.0, upper=2.4),
        mating=MatingContract(
            parent_face_geometry="front_shelf",
            parent_face_side="positive_z",
            child_face_geometry="fallboard_panel",
            child_face_side="negative_z",
            contact_tol=0.0040,
        ),
    )


# --------------------------------------------------------------------------- #
# Slot B — upright lid (rear hinge) + fallboard (standard PRISMATIC slide or
# sliding cover with handle). Adapted from parent B L137-L178 / S7 L145-L193.
# --------------------------------------------------------------------------- #
def _emit_upright_lid(model: ArticulatedObject, body, r: ResolvedPianoConfig) -> None:
    m = r.mats
    hw = U_HALF_W * r.body_width_scale
    shell_top = _upright_shell_top_z(r)
    lid_hinge_y = U_DEPTH_BACK_Y
    lid_hinge_z = shell_top + U_LID_THK / 2.0
    lid = model.part("top_lid")
    lid.visual(
        Box((2 * hw, U_DEPTH_BACK_Y, U_LID_THK)),
        origin=Origin(xyz=(0.0, -U_DEPTH_BACK_Y / 2.0, 0.0)),
        material=m["case"],
        name="lid_panel", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    model.articulation(
        "body_to_top_lid",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lid,
        origin=Origin(xyz=(0.0, lid_hinge_y, lid_hinge_z)),
        axis=(-1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=50.0, velocity=1.5, lower=0.0, upper=1.2),
        mating=MatingContract(
            parent_face_geometry="side_panel_l",
            parent_face_side="positive_z",
            child_face_geometry="lid_panel",
            child_face_side="negative_z",
            contact_tol=0.0030,
        ),
    )


def _emit_upright_fallboard(
    model: ArticulatedObject, body, r: ResolvedPianoConfig, *, sliding: bool
) -> None:
    m = r.mats
    fallboard = model.part("fallboard")
    # The sliding cover is narrower than the standard fold cover so it rides
    # BETWEEN the side slide tracks (inner edge ≈ ±0.6325·ws) without clashing.
    cover_w = (1.230 if sliding else 1.280) * r.body_width_scale
    cover_thk = 0.015 if sliding else 0.020
    # The cover bottom sits on the ledge top (slide origin z) so it has real
    # contact with the body (no isolated/floating part).
    cover_z = cover_thk / 2.0
    fallboard.visual(
        Box((cover_w, 0.095, cover_thk)),
        origin=Origin(xyz=(0.0, 0.0475, cover_z)),
        material=m["case"],
        name="fallboard_panel", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    travel = 0.20 if sliding else 0.12
    if sliding:
        # Pull handle / grip at the front lip of the sliding cover — sits low so
        # it rides under the nameboard and between the side slide tracks.
        handle_thk = 0.020
        fallboard.visual(
            Box((cover_w, 0.022, handle_thk)),
            origin=Origin(xyz=(0.0, -0.006, cover_thk + handle_thk / 2.0)),
            material=m["satin"],
            name="fallboard_handle", material_class_id=("wood.veneer_panel" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
        )
    model.articulation(
        "body_to_fallboard",
        ArticulationType.PRISMATIC,
        parent=body,
        child=fallboard,
        origin=Origin(xyz=(0.0, 0.015, U_LEDGE_TOP_Z)),
        axis=(0.0, -1.0, 0.0),
        motion_limits=MotionLimits(effort=6.0, velocity=0.25, lower=0.0, upper=travel),
        mating=MatingContract(
            parent_face_geometry="fallboard_ledge",
            parent_face_side="positive_z",
            child_face_geometry="fallboard_panel",
            child_face_side="negative_z",
            contact_tol=0.0040,
        ),
    )


# --------------------------------------------------------------------------- #
# Slot C — music support. fixed_music_desk is parent visuals on the case;
# fold_down_music_desk is an articulated music_rest on a fixed base rail (grand
# only, S9 L257-L294).
# --------------------------------------------------------------------------- #
def _emit_grand_music_support(model: ArticulatedObject, case, r: ResolvedPianoConfig) -> None:
    m = r.mats
    fold = r.music_support_module == "fold_down_music_desk"
    desk_w = 0.86 * r.body_width_scale
    if not fold:
        # The music desk lives just behind the rim front cavity (y=0.12) and in
        # front of the pinblock (y≈0.205), sitting ON the cast-iron plate so the
        # whole desk is supported (never a floating island) without colliding
        # with the front-shelf fallboard. Base + panel are parent visuals (Rule 1).
        desk_y = 0.150
        # Base rail bridges the open keybed gap: its front (y≈0.100) rests on the
        # front shelf (top z≈0.800, y≤0.120) so the whole desk is supported (never
        # a floating island), while staying BEHIND the at-rest grand fallboard
        # rear (y≈0.094) and low enough that the panel clears the closed lid
        # (z=1.000).
        base_z = 0.806  # bottom z≈0.798 touches the front-shelf top
        case.visual(
            Box((desk_w, 0.080, 0.016)),
            origin=Origin(xyz=(0.0, 0.140, base_z)),
            material=m["case"],
            name="music_desk_base", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
        )
        # Fixed (non-articulating) music desk panel — a parent visual (Rule 1).
        # Stands nearly upright above the base rail, clear of the pinblock.
        case.visual(
            Box((desk_w, 0.012, 0.185)),
            origin=Origin(xyz=(0.0, desk_y - 0.012, 0.900), rpy=(-0.10, 0.0, 0.0)),
            material=m["case"],
            name="music_desk_panel", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
        )
        return
    # Articulated fold-down music rest. On a real grand the desk stands on the
    # cast-iron plate BEHIND the pinblock, in front of the string field — not in
    # the fallboard slot: hinged there (the previous design), the folding panel
    # shared the y-z region [0, 0.094]×[0.80, 0.91] with the raising fallboard
    # panel, so the two collided whenever both moved (and the slot sit also
    # embedded the hinge in the rim wall band y∈[0.12,≈0.25]×z∈[0.745,1.0]).
    # Here the desk stands vertically above the strings (string tops ≈0.887) on
    # a rail that sits on the plate, and folds forward over the pinblock (top
    # 0.905). The hinge y is DERIVED per case scale so the folding panel stays
    # y-disjoint from everything below: it never reaches back over the pinblock
    # (≥8 mm clear of the pinblock back at the 1.45 limit) or the rim wall band,
    # and the fold arc stays y-disjoint from the fallboard sweep (y≤0.094),
    # clears the pinblock top, the string tops (≥2 mm), and the closed lid
    # (z=1.000, ≥7 mm) at every pose.
    inner_front_y = _scale_profile(_grand_outline(r), 0.90)[0][1]
    rail_y = max(inner_front_y + 0.100, 0.205 * r.case_depth_scale + 0.141)
    hinge_z = 0.8975
    rest_h = 0.095
    rail_top = hinge_z - 0.006
    case.visual(
        # Base rail standing on the plate (top 0.860) between the string rows —
        # real desks carry such a rail; the panel bottom edge rests on its top.
        Box((desk_w, 0.030, rail_top - G_PLATE_TOP_Z)),
        origin=Origin(xyz=(0.0, rail_y, (rail_top + G_PLATE_TOP_Z) / 2.0)),
        material=m["case"],
        name="music_desk_rail", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    music_rest = model.part("music_rest")
    music_rest.visual(
        Box((desk_w, 0.012, rest_h + 0.006)),
        # Box spans 6 mm below the hinge line (bottom edge on the rail top) to
        # rest_h above it: a vertical desk leaf in front of the string field.
        origin=Origin(xyz=(0.0, 0.0, (rest_h - 0.006) / 2.0)),
        material=m["case"],
        name="rest_panel", material_class_id=("wood.polished_varnished" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )
    model.articulation(
        "case_to_music_rest",
        ArticulationType.REVOLUTE,
        parent=case,
        child=music_rest,
        origin=Origin(xyz=(0.0, rail_y, hinge_z)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=0.0, upper=1.45),
        mating=MatingContract(
            parent_face_geometry="music_desk_rail",
            parent_face_side="positive_z",
            child_face_geometry="rest_panel",
            child_face_side="negative_z",
            contact_tol=0.0090,
        ),
    )


def _emit_upright_music_support(model: ArticulatedObject, body, r: ResolvedPianoConfig) -> None:
    # Uprights keep a fixed music-desk shelf as a parent visual on the upper
    # front panel (no front-of-strings desk; always fixed_music_desk). Its top
    # is kept under the shell top so the closed rear-hinged lid clears it on a
    # short spinet.
    m = r.mats
    shell_top = _upright_shell_top_z(r)
    panel_h = min(0.150, max(0.060, (shell_top - 0.806) - 0.020))
    panel_center_z = shell_top - 0.030 - panel_h / 2.0
    body.visual(
        Box((0.90 * r.body_width_scale, 0.022, panel_h)),
        origin=Origin(xyz=(0.0, -0.014, panel_center_z), rpy=(-0.16, 0.0, 0.0)),
        material=m["satin"],
        name="music_desk_panel", material_class_id=("wood.veneer_panel" if r.palette_style in {"black_gloss", "walnut", "white_polished", "ebony_satin"} else "wood.mahogany_teak_dark"),
    )


# --------------------------------------------------------------------------- #
# Pedal bank multiplicity (pedal_{i}). Centered row on the pedal box front.
# Adapted from four_pedals L369-L399.
# --------------------------------------------------------------------------- #
def _emit_pedals(model: ArticulatedObject, root, r: ResolvedPianoConfig, *, grand: bool) -> None:
    m = r.mats
    n = r.pedal_count
    spacing = r.pedal_spacing
    if grand:
        pedal_depth = 0.115
        pedal_box_front_y = -0.090 - 0.105 / 2.0
        pedal_z = 0.200
    else:
        pedal_depth = 0.110
        pedal_box_front_y = -0.020 - 0.090 / 2.0
        pedal_z = 0.120
    pedal_geom = Box((0.030, pedal_depth, 0.012))
    offsets = [(i - (n - 1) / 2.0) * spacing for i in range(n)]
    for pi in range(n):
        px = offsets[pi]
        pedal = model.part(f"pedal_{pi}")
        pedal.visual(
            pedal_geom,
            origin=Origin(xyz=(0.0, -pedal_depth / 2.0, 0.0)),
            material=m["brass"],
            name="pedal", material_class_id="metal.brass_polished",
        )
        model.articulation(
            f"{r.root_part}_to_pedal_{pi}",
            ArticulationType.REVOLUTE,
            parent=root,
            child=pedal,
            origin=Origin(xyz=(px, pedal_box_front_y, pedal_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=12.0, velocity=2.0, lower=0.0, upper=0.18),
            mating=MatingContract(
                parent_face_geometry="pedal_box",
                parent_face_side="negative_y",
                child_face_geometry="pedal",
                child_face_side="positive_y",
                contact_tol=0.0040,
            ),
        )


# --------------------------------------------------------------------------- #
# Top-level build.
# --------------------------------------------------------------------------- #
def build_piano(config: PianoConfig, *, assets: AssetContext | None = None) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name or "piano", assets=assets)
    # Register each colorway token as a Material and rebind `r.mats` to the
    # Material objects so every `.visual(..., material=...)` is palette-driven.
    registered: dict[str, object] = {
        token: model.material(f"piano_{token}", rgba=rgba) for token, rgba in r.mats.items()
    }
    r = replace(r, mats=registered)  # type: ignore[arg-type]

    if r.family == "grand":
        root = _build_grand_case(model, r)
        _emit_keyboard(
            model,
            root,
            root_name="case",
            keybed_top_z=G_KEY_BED_TOP_Z,
            white_key_top_z=G_WHITE_KEY_TOP_Z,
            keyboard_front_y=G_KEYBOARD_FRONT_Y,
            white_key_depth=G_WHITE_KEY_DEPTH,
            width_scale=r.body_width_scale,
            ivory=r.mats["ivory"],
            ebony=r.mats["ebony"],
        )
        if r.lid_fallboard_module == "split_top_lid":
            _emit_grand_split_lid(model, root, r)
        else:
            _emit_grand_standard_lid(model, root, r)
        _emit_grand_fallboard(model, root, r)
        _emit_grand_music_support(model, root, r)
        _emit_pedals(model, root, r, grand=True)
    else:
        sliding = r.lid_fallboard_module == "sliding_fallboard"
        root = _build_upright_case(model, r, sliding=sliding)
        _emit_keyboard(
            model,
            root,
            root_name="body",
            keybed_top_z=U_KEYBED_TOP_Z,
            white_key_top_z=U_WHITE_KEY_TOP_Z,
            keyboard_front_y=U_KEYBOARD_FRONT_Y,
            white_key_depth=U_WHITE_KEY_DEPTH,
            width_scale=r.body_width_scale,
            ivory=r.mats["ivory"],
            ebony=r.mats["ebony"],
        )
        _emit_upright_lid(model, root, r)
        _emit_upright_fallboard(model, root, r, sliding=sliding)
        _emit_upright_music_support(model, root, r)
        _emit_pedals(model, root, r, grand=False)

    return model


def build_seeded_piano(seed: int, *, assets: AssetContext | None = None) -> ArticulatedObject:
    return build_piano(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Slot choices (module_topology_diversity).
# --------------------------------------------------------------------------- #
def slot_choices_for_config(r: ResolvedPianoConfig) -> tuple[tuple[str, str], ...]:
    choices: list[tuple[str, str]] = [
        ("case", r.case_module),
        ("lid_fallboard", r.lid_fallboard_module),
        ("music_support", r.music_support_module),
        ("pedal_count", f"pedal_x{r.pedal_count}"),
    ]
    if r.family == "grand":
        choices.append(("visible_strings", f"strings_x{r.visible_string_count}"))
    return tuple(choices)


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(resolve_config(config_from_seed(seed)))


# --------------------------------------------------------------------------- #
# Tests.
# --------------------------------------------------------------------------- #
def _declare_overlap_allowances(
    ctx: TestContext, model: ArticulatedObject, r: ResolvedPianoConfig
) -> None:
    root = model.get_part(r.root_part)
    part_names = {p.name for p in model.parts}

    # Opened lid leaves the case entirely; keys stroke inside the keybed well;
    # the raised fallboard stands clear of the keybed too.
    for part_name in ("top_lid", "lid_front", "lid_rear", "fallboard"):
        if part_name in part_names:
            ctx.allow_isolated_part(
                model.get_part(part_name),
                reason="opened panel swings up clear of the case and loses contact",
            )
    for key_name in (p.name for p in model.parts if p.name.startswith(("white_key_", "black_key_"))):
        key = model.get_part(key_name)
        ctx.allow_overlap(
            key,
            root,
            reason="piano key strokes in its keybed well in close sliding contact",
        )

    # Split-lid PianoHinge knuckle strip straddles its own leaf panel edge.
    for leaf_name in ("lid_front", "lid_rear"):
        if leaf_name in part_names:
            leaf = model.get_part(leaf_name)
            ctx.allow_overlap(
                leaf,
                leaf,
                elem_a=f"{leaf_name}_hinge_strip",
                elem_b=f"{leaf_name}_panel",
                reason="Brass piano-hinge knuckle strip is bonded along the leaf's spine edge.",
            )


def _expect_lid_opens_up(ctx: TestContext, model: ApiObj, joint_name: str, part_name: str) -> None:
    part = model.get_part(part_name)
    joint = model.get_articulation(joint_name)
    rest = ctx.part_world_aabb(part)
    with ctx.pose({joint: joint.motion_limits.upper}):
        opened = ctx.part_world_aabb(part)
    if rest is None or opened is None:
        return
    ctx.check(
        f"{part_name}_opens_upward",
        opened[1][2] > rest[1][2] + 0.12,
        details=f"rest_top={rest[1][2]:.4f}, open_top={opened[1][2]:.4f}",
    )


# Alias to keep type hints readable without importing the concrete class name.
ApiObj = ArticulatedObject


def run_piano_tests(object_model: ArticulatedObject, config: PianoConfig) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _declare_overlap_allowances(ctx, object_model, r)

    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    root = object_model.get_part(r.root_part)
    part_names = {p.name for p in object_model.parts}

    # --- Hero identity geometry -------------------------------------------- #
    if r.family == "grand":
        ctx.check(
            "grand has cast-iron plate + strings",
            root.get_visual("cast_iron_plate") is not None
            and root.get_visual("string_0") is not None,
            details="missing grand plate/strings",
        )
    else:
        ctx.check(
            "upright has upper front panel",
            root.get_visual("upper_front_panel") is not None,
            details="missing upright upper panel",
        )
    ctx.check(
        "has fallboard",
        "fallboard" in part_names,
        details=str(sorted(part_names)),
    )
    ctx.check(
        f"pedal_count is {r.pedal_count} brass pedals in [2,4]",
        2 <= r.pedal_count <= 4
        and all(f"pedal_{i}" in part_names for i in range(r.pedal_count)),
        details=str(sorted(p for p in part_names if p.startswith("pedal_"))),
    )

    # --- Lid opens upward --------------------------------------------------- #
    if r.lid_fallboard_module == "split_top_lid":
        _expect_lid_opens_up(ctx, object_model, "case_to_lid_front", "lid_front")
        _expect_lid_opens_up(ctx, object_model, "case_to_lid_rear", "lid_rear")
    elif r.family == "grand":
        _expect_lid_opens_up(ctx, object_model, "case_to_top_lid", "top_lid")
    else:
        _expect_lid_opens_up(ctx, object_model, "body_to_top_lid", "top_lid")

    # --- Fallboard motion + the spec §13 floating-fallboard validator ------- #
    fallboard = object_model.get_part("fallboard")
    fb_joint = object_model.get_articulation(f"{r.root_part}_to_fallboard")
    rest_fb = ctx.part_world_aabb(fallboard)
    if r.family == "grand":
        # CRITICAL: at-rest fallboard must TOUCH the front shelf top (gap≈0),
        # never float; and the folded pose must stay above the white-key top.
        shelf_top = _grand_front_shelf_top_z(r)
        if rest_fb is not None:
            ctx.check(
                "grand fallboard seats on the scaled front shelf (not floating)",
                abs(rest_fb[0][2] - shelf_top) <= 0.008,
                details=f"shelf_top={shelf_top:.4f}, fallboard_bottom={rest_fb[0][2]:.4f}",
            )
        with ctx.pose({fb_joint: fb_joint.motion_limits.upper}):
            folded_fb = ctx.part_world_aabb(fallboard)
        if folded_fb is not None:
            ctx.check(
                "grand folded fallboard stays above the white-key top",
                folded_fb[0][2] > G_WHITE_KEY_TOP_Z - 0.001,
                details=f"white_key_top={G_WHITE_KEY_TOP_Z:.4f}, folded_bottom={folded_fb[0][2]:.4f}",
            )
        # Folding swings the free edge up and forward.
        if rest_fb is not None and folded_fb is not None:
            ctx.check(
                "grand fallboard folds up off the flat rest",
                folded_fb[1][2] > rest_fb[1][2] + 0.03,
                details=f"rest_top={rest_fb[1][2]:.4f}, folded_top={folded_fb[1][2]:.4f}",
            )
    else:
        # Upright slide stays level above the keys.
        with ctx.pose({fb_joint: fb_joint.motion_limits.upper}):
            closed_fb = ctx.part_world_aabb(fallboard)
        if rest_fb is not None and closed_fb is not None:
            ctx.check(
                "upright fallboard slides forward over the keys, staying level",
                closed_fb[0][1] < rest_fb[0][1] - 0.05
                and abs(closed_fb[0][2] - rest_fb[0][2]) < 1e-6
                and closed_fb[0][2] > U_WHITE_KEY_TOP_Z,
                details=f"rest={rest_fb}, closed={closed_fb}",
            )

    # --- A white key presses straight down --------------------------------- #
    mid = 25
    wk = object_model.get_part(f"white_key_{mid}")
    wk_joint = object_model.get_articulation(f"{r.root_part}_to_white_key_{mid}")
    rest_k = ctx.part_world_position(wk)
    with ctx.pose({wk_joint: 0.009}):
        down_k = ctx.part_world_position(wk)
    if rest_k is not None and down_k is not None:
        ctx.check(
            "white key travels straight down",
            down_k[2] < rest_k[2] - 0.004
            and abs(down_k[0] - rest_k[0]) < 1e-6
            and abs(down_k[1] - rest_k[1]) < 1e-6,
            details=f"rest={rest_k}, down={down_k}",
        )

    # --- A pedal depresses at the front ------------------------------------ #
    ped_joint = object_model.get_articulation(f"{r.root_part}_to_pedal_0")
    pedal = object_model.get_part("pedal_0")
    rest_p = ctx.part_world_aabb(pedal)
    with ctx.pose({ped_joint: 0.18}):
        press_p = ctx.part_world_aabb(pedal)
    if rest_p is not None and press_p is not None:
        ctx.check(
            "pedal depresses at the front",
            press_p[0][2] < rest_p[0][2] - 0.004,
            details=f"rest={rest_p}, press={press_p}",
        )

    # --- Music rest folds forward (when articulated) ----------------------- #
    if "music_rest" in part_names:
        mr = object_model.get_part("music_rest")
        mr_joint = object_model.get_articulation("case_to_music_rest")
        rest_mr = ctx.part_world_aabb(mr)
        with ctx.pose({mr_joint: mr_joint.motion_limits.upper}):
            fold_mr = ctx.part_world_aabb(mr)
        if rest_mr is not None and fold_mr is not None:
            ctx.check(
                "music rest folds forward",
                fold_mr[0][1] < rest_mr[0][1] - 0.02 or fold_mr[1][2] < rest_mr[1][2] - 0.02,
                details=f"rest={rest_mr}, fold={fold_mr}",
            )

    # --- Family compatibility gates ---------------------------------------- #
    if r.family == "upright":
        ctx.check(
            "upright never uses grand-only modules",
            r.lid_fallboard_module != "split_top_lid"
            and r.music_support_module == "fixed_music_desk"
            and r.visible_string_count == 0,
            details=f"lid={r.lid_fallboard_module}, music={r.music_support_module}",
        )
    else:
        ctx.check(
            "grand never uses upright-only sliding fallboard",
            r.lid_fallboard_module != "sliding_fallboard",
            details=f"lid={r.lid_fallboard_module}",
        )

    return ctx.report()


__all__ = [
    "PianoConfig",
    "ResolvedPianoConfig",
    "config_from_seed",
    "resolve_config",
    "build_piano",
    "build_seeded_piano",
    "slot_choices_for_seed",
    "run_piano_tests",
    "__modular__",
]
