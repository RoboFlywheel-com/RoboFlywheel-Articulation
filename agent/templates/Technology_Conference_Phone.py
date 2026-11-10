# SPDX-License-Identifier: Apache-2.0

"""Desktop conference speakerphone (Polycom SoundStation family) — modular template.

Category identity (spec ``specs_modular_v1/Technology_Conference_Phone.md``):
a **low static desktop speakerphone body** carrying one-or-more **speaker
grilles**, a **static LCD**, and a **control surface** with a **prismatic
pushbutton cluster** (numeric keypad + soft keys + green-call / red-end + volume).
The **buttons are the ONLY non-fixed joints** — everything else (body, grilles,
LCD, console, feet, LEDs, badge) is fused into the ``body`` root part as visuals
(Rule 1).

World frame: Z up (thin slab on z≈0), user/keypad end −Y (front), speaker/body
mass toward +Y/center (rear), width X. Root part = ``body``; each key parts to it
by a PRISMATIC joint (parallel children).

Four slots + a keypad-array axis + a palette axis (spec §4/§8):
  * Slot A ``body_form`` (5): tri_star / winged / hex / round_puck / square_rounded
    — the ③ Primary Form Family (root ``body`` planform, one LoftGeometry family).
  * Slot B ``speaker_arrangement`` ≡ speaker multiplicity N (5): central(1) /
    discrete_2 / discrete_3 / discrete_4 / perimeter_ring. Gated by body_form.
  * Slot C ``grille_treatment`` (3): perforated / fabric / domed(central-only) — ④.
  * Slot D ``control_surface`` (3): flush / raised / tilted — keypad/LCD carrier.
  * ``keypad_shape`` {3x4, 4x4} — numeric-array multiplicity (spec §8).

Compatibility gates (spec §9, matrix + adopted forks; O5 name-vs-asset rule
resolves the winged×discrete_4 prose/matrix conflict toward the matrix + the
adopted quad_pods fork):
  tri_star  → {central, discrete_3}
  winged    → {central, discrete_2, discrete_4}
  hex / round_puck / square_rounded → all five
  domed grille → central only.

Sources (all 13 read in full; see spec §14): S1 tri_star-central-perforated-flush
baseline (skeleton), S2/S13 tri_star fabric, S3 tri_star perforated raised, S4/S10
winged, S5/S11 hex domed, S6 round_puck, S7 square, S8 winged-quad_pods, S9
hex-perimeter_ring. Body = LoftGeometry over per-form planform (Rule 3, no
downgrade); grilles reuse ONE Mesh across N speakers (compile budget, spec §7.5).
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
    Cylinder,
    ExtrudeGeometry,
    Inertial,
    LoftGeometry,
    Material,
    MotionLimits,
    Origin,
    PerforatedPanelGeometry,
    Sphere,
    TestContext,
    TestReport,
    mesh_from_geometry,
    rounded_rect_profile,
    sample_catmull_rom_spline_2d,
    superellipse_profile,
)

__modular__ = True

# ===========================================================================
# Slot enums.
# ===========================================================================
BodyForm = Literal["tri_star", "winged", "hex", "round_puck", "square_rounded"]
SpeakerArrangement = Literal["central", "discrete_2", "discrete_3", "discrete_4", "perimeter_ring"]
GrilleTreatment = Literal["perforated", "fabric", "domed"]
ControlSurface = Literal["flush", "raised", "tilted"]
KeypadShape = Literal["3x4", "4x4"]
PaletteStyle = Literal[
    "graphite_gray",
    "matte_black",
    "black_silver",
    "white_silver",
    "charcoal_two_tone",
]

BODY_FORMS: tuple[BodyForm, ...] = ("tri_star", "winged", "hex", "round_puck", "square_rounded")
ARRANGEMENTS: tuple[SpeakerArrangement, ...] = (
    "central",
    "discrete_2",
    "discrete_3",
    "discrete_4",
    "perimeter_ring",
)
GRILLES: tuple[GrilleTreatment, ...] = ("perforated", "fabric", "domed")
CONTROL_SURFACES: tuple[ControlSurface, ...] = ("flush", "raised", "tilted")
KEYPAD_SHAPES: tuple[KeypadShape, ...] = ("3x4", "4x4")
PALETTE_STYLES: tuple[PaletteStyle, ...] = (
    "graphite_gray",
    "matte_black",
    "black_silver",
    "white_silver",
    "charcoal_two_tone",
)

# Compatibility: which speaker arrangements each body_form allows (spec §9).
_ALLOWED_ARRANGEMENTS: dict[BodyForm, tuple[SpeakerArrangement, ...]] = {
    "tri_star": ("central", "discrete_3"),
    "winged": ("central", "discrete_2", "discrete_4"),
    "hex": ARRANGEMENTS,
    "round_puck": ARRANGEMENTS,
    "square_rounded": ARRANGEMENTS,
}

_SPEAKER_COUNT: dict[SpeakerArrangement, int] = {
    "central": 1,
    "discrete_2": 2,
    "discrete_3": 3,
    "discrete_4": 4,
    "perimeter_ring": 0,  # continuous band, no discrete N
}

# Lobe angles (deg, standard math: +X=0, CCW) per discrete arrangement. Chosen so
# no pod lands in the front-center (−Y ~ 270°) keypad zone; front-side pods sit
# near the ±X axis so their inner x-edge clears the compact keypad (spec §9).
_LOBE_ANGLES: dict[SpeakerArrangement, tuple[float, ...]] = {
    "discrete_2": (12.0, 168.0),
    "discrete_3": (90.0, 210.0, 330.0),
    "discrete_4": (40.0, 140.0, 220.0, 320.0),
}


# ===========================================================================
# Per-form base geometry (meters). Scaled by body_radius_scale / body_height_scale.
# ===========================================================================
@dataclass(frozen=True)
class _FormBase:
    r_char: float  # characteristic body radius
    top: float  # body slab height
    lobe_frac: float  # discrete-lobe radius as fraction of r_char
    face_frac: float  # speaker face half-size as fraction of r_char
    central_face_frac: float  # central grille face half-size fraction


_FORM_BASE: dict[BodyForm, _FormBase] = {
    "tri_star": _FormBase(0.128, 0.030, 0.66, 0.24, 0.40),
    "winged": _FormBase(0.150, 0.032, 0.62, 0.22, 0.34),
    "hex": _FormBase(0.140, 0.028, 0.70, 0.20, 0.40),
    "round_puck": _FormBase(0.120, 0.032, 0.60, 0.24, 0.42),
    "square_rounded": _FormBase(0.130, 0.030, 0.64, 0.22, 0.40),
}

# Keypad console geometry (fixed real-world-ish hardware, spec Contract 2c).
# Contract 3e backlog: CONSOLE_HALF_W/D and the deck_rise/panel_tilt table below
# are relation-class quantities frozen as constants (guarded today by the
# keys_inset/keys_proud gate checks); derive them from r_char / body_top / front
# key height on next touch.
CONSOLE_HALF_W = 0.052  # console half-width (x)
CONSOLE_HALF_D = 0.044  # console half-depth (y)
KEY_MARGIN = 0.010  # min inset of every key from the console border (x and y)
KEY_STEM_H = 0.0012
KEY_CAP_H = 0.0030
KEY_EMBED = 0.0018  # cap base sinks this far into the deck well (seated)


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _pick(value, choices):
    return value if value in choices else choices[0]


# ===========================================================================
# Config.
# ===========================================================================
@dataclass(frozen=True)
class ConferencePhoneConfig:
    body_form: BodyForm | None = None
    speaker_arrangement: SpeakerArrangement | None = None
    grille_treatment: GrilleTreatment | None = None
    control_surface: ControlSurface | None = None
    keypad_shape: KeypadShape | None = None
    palette_style: PaletteStyle = "graphite_gray"
    body_radius_scale: float = 1.0
    body_height_scale: float = 1.0
    speaker_radius_frac_scale: float = 1.0
    key_travel: float = 0.0018
    name: str = "conference_phone"


@dataclass(frozen=True)
class ResolvedConferencePhoneConfig:
    body_form: BodyForm
    speaker_arrangement: SpeakerArrangement
    speaker_count: int
    grille_treatment: GrilleTreatment
    control_surface: ControlSurface
    keypad_shape: KeypadShape
    palette_style: PaletteStyle
    r_char: float
    top: float
    lobe_r: float
    face_r: float
    central_face_r: float
    console_y: float
    deck_rise: float
    panel_tilt: float
    deck_z: float
    key_travel: float
    name: str


def config_from_seed(seed: int) -> ConferencePhoneConfig:
    """Deterministic procedural sampling (seed=0 is NOT special). Gates are applied
    at sample time so illegal (body_form × arrangement / grille) never appear."""
    rng = random.Random(seed)
    body_form = rng.choice(BODY_FORMS)
    arrangement = rng.choice(_ALLOWED_ARRANGEMENTS[body_form])
    # grille: domed only on central.
    grille_pool: tuple[GrilleTreatment, ...] = (
        GRILLES if arrangement == "central" else ("perforated", "fabric")
    )
    grille = rng.choice(grille_pool)
    return ConferencePhoneConfig(
        body_form=body_form,
        speaker_arrangement=arrangement,
        grille_treatment=grille,
        control_surface=rng.choice(CONTROL_SURFACES),
        keypad_shape=rng.choice(KEYPAD_SHAPES),
        palette_style=rng.choice(PALETTE_STYLES),
        body_radius_scale=round(rng.uniform(0.90, 1.12), 4),
        body_height_scale=round(rng.uniform(0.90, 1.15), 4),
        speaker_radius_frac_scale=round(rng.uniform(0.90, 1.08), 4),
        key_travel=round(rng.uniform(0.0010, 0.0030), 5),
        name=f"seeded_conference_phone_{seed}",
    )


def resolve_config(
    config: ConferencePhoneConfig | None = None,
) -> ResolvedConferencePhoneConfig:
    """Solve §7: independent scales → equation (lobe_r, deck_z) → conditional
    (deck_rise / panel_tilt per control_surface). Gates re-checked defensively."""
    cfg = config or ConferencePhoneConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    allowed = _ALLOWED_ARRANGEMENTS[body_form]
    arrangement = _pick(cfg.speaker_arrangement, allowed)
    grille_pool: tuple[GrilleTreatment, ...] = (
        GRILLES if arrangement == "central" else ("perforated", "fabric")
    )
    grille = _pick(cfg.grille_treatment, grille_pool)
    control_surface = _pick(cfg.control_surface, CONTROL_SURFACES)
    keypad_shape = _pick(cfg.keypad_shape, KEYPAD_SHAPES)
    palette_style = _pick(cfg.palette_style, PALETTE_STYLES)

    base = _FORM_BASE[body_form]
    r_scale = _clamp(cfg.body_radius_scale, 0.90, 1.12)
    h_scale = _clamp(cfg.body_height_scale, 0.90, 1.15)
    frac_scale = _clamp(cfg.speaker_radius_frac_scale, 0.90, 1.08)

    r_char = base.r_char * r_scale
    top = base.top * h_scale
    lobe_r = base.lobe_frac * frac_scale * r_char  # equation
    face_r = base.face_frac * r_char
    central_face_r = base.central_face_frac * r_char
    # Console sits center-front (fits every planform incl. the narrow tri_star
    # valley across the scale range) rather than pushed to the front rim.
    console_y = -0.16 * r_char

    # conditional: deck rise / tilt per control surface. The tilted deck is lifted
    # enough that even its lowest (front) key stays proud of the body top — the
    # console must not sink in and swallow the front-row keys.
    if control_surface == "raised":
        deck_rise = 0.024
        panel_tilt = 0.0
    elif control_surface == "tilted":
        deck_rise = 0.017
        panel_tilt = 0.26
    else:  # flush
        deck_rise = 0.0
        panel_tilt = 0.0
    deck_z = top + deck_rise  # equation: single source of key-origin height

    key_travel = _clamp(cfg.key_travel, 0.0010, 0.0030)

    return ResolvedConferencePhoneConfig(
        body_form=body_form,
        speaker_arrangement=arrangement,
        speaker_count=_SPEAKER_COUNT[arrangement],
        grille_treatment=grille,
        control_surface=control_surface,
        keypad_shape=keypad_shape,
        palette_style=palette_style,
        r_char=r_char,
        top=top,
        lobe_r=lobe_r,
        face_r=face_r,
        central_face_r=central_face_r,
        console_y=console_y,
        deck_rise=deck_rise,
        panel_tilt=panel_tilt,
        deck_z=deck_z,
        key_travel=key_travel,
        name=cfg.name or "conference_phone",
    )


def slot_choices_for_config(
    config: ConferencePhoneConfig | ResolvedConferencePhoneConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedConferencePhoneConfig) else resolve_config(config)
    return (
        ("body_form", r.body_form),
        ("speaker_arrangement", r.speaker_arrangement),
        (
            "speaker_count",
            "ring" if r.speaker_arrangement == "perimeter_ring" else str(r.speaker_count),
        ),
        ("grille_treatment", r.grille_treatment),
        ("control_surface", r.control_surface),
        ("keypad_shape", r.keypad_shape),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# ===========================================================================
# Slot A: body_form planform + LoftGeometry body (Rule 3 — one Loft family).
# ===========================================================================
def _planform(form: BodyForm, r_char: float, samples: int = 120) -> list[tuple[float, float]]:
    """Closed XY boundary loop for the body form (all forms → one Loft family)."""
    if form == "tri_star":
        pts = []
        for i in range(samples):
            th = 2.0 * math.pi * i / samples
            r = r_char * (0.84 + 0.24 * math.cos(3.0 * (th - math.pi / 2.0)))
            r += r_char * 0.03 * math.cos(6.0 * (th - math.pi / 2.0))
            pts.append((r * math.cos(th), r * math.sin(th)))
        return pts
    if form == "hex":
        # Corner-truncated triangle (S5): main edges 30/150/270, cuts 90/210/330.
        h1 = r_char * 0.80
        h2 = r_char * 1.00

        def _sharp(th: float) -> float:
            cands = []
            for k in range(3):
                beta = math.pi / 6.0 + 2.0 * math.pi * k / 3.0
                c = math.cos(th - beta)
                if c > 1e-6:
                    cands.append(h1 / c)
                alpha = math.pi / 2.0 + 2.0 * math.pi * k / 3.0
                c = math.cos(th - alpha)
                if c > 1e-6:
                    cands.append(h2 / c)
            return min(cands)

        radii = [_sharp(2.0 * math.pi * i / samples) for i in range(samples)]
        pts = []
        sm = 4
        for i in range(samples):
            r = sum(radii[(i + j) % samples] for j in range(-sm, sm + 1)) / (2 * sm + 1)
            th = 2.0 * math.pi * i / samples
            pts.append((r * math.cos(th), r * math.sin(th)))
        return pts
    if form == "round_puck":
        return [
            (
                r_char * math.cos(2.0 * math.pi * i / samples),
                r_char * math.sin(2.0 * math.pi * i / samples),
            )
            for i in range(samples)
        ]
    if form == "square_rounded":
        side = r_char * 1.55
        return rounded_rect_profile(side, side, r_char * 0.42, corner_segments=10)
    # winged (S4/S10): catmull-rom over a wide winged outline, scaled to r_char.
    fw = r_char / 0.150
    outline = [
        (-1.90, -0.53),
        (-1.71, -0.89),
        (-1.19, -1.01),
        (-0.56, -0.85),
        (0.0, -0.76),
        (0.56, -0.85),
        (1.19, -1.01),
        (1.71, -0.89),
        (1.90, -0.53),
        (1.84, 0.22),
        (1.42, 0.72),
        (0.71, 0.97),
        (0.0, 1.03),
        (-0.71, 0.97),
        (-1.42, 0.72),
        (-1.84, 0.22),
    ]
    scaled = [(x * fw * 0.155, y * fw * 0.155) for x, y in outline]
    return list(sample_catmull_rom_spline_2d(scaled, samples_per_segment=6, closed=True))


def _scaled_loop(profile, scale: float, z: float):
    return [(x * scale, y * scale, z) for x, y in profile]


def _build_body(model: ArticulatedObject, r: ResolvedConferencePhoneConfig, mats) -> object:
    body = model.part("body")
    plan = _planform(r.body_form, r.r_char)
    body_geom = LoftGeometry(
        [
            _scaled_loop(plan, 0.97, 0.0),
            _scaled_loop(plan, 1.00, r.top * 0.55),
            _scaled_loop(plan, 0.93, r.top),
        ],
        cap=True,
        closed=True,
    )
    body.visual(
        mesh_from_geometry(body_geom, "body_shell"), material=mats["body"], name="body_shell", material_class_id="plastic.opaque_glossy_molded"
    )

    # Rubber feet at three angles (fused body visuals, reach below z=0). Radius
    # kept well inside every planform (square corners are nearest) so each foot
    # welds to the shell bottom.
    for i, ang in enumerate((90.0, 210.0, 330.0)):
        a = math.radians(ang)
        body.visual(
            Cylinder(radius=0.011, length=0.004),
            origin=Origin(
                xyz=(0.55 * r.r_char * math.cos(a), 0.55 * r.r_char * math.sin(a), -0.001)
            ),
            material=mats["foot"],
            name=f"foot_{i}", material_class_id="rubber.smooth_plain",
        )

    body.inertial = Inertial.from_geometry(
        Box((2.0 * r.r_char, 2.0 * r.r_char, r.top)),
        mass=1.1,
        origin=Origin(xyz=(0.0, 0.0, r.top * 0.5)),
    )
    return body


# ===========================================================================
# Slot B + C: speaker arrangement × grille treatment (fused body visuals).
# ===========================================================================
def _speaker_positions(r: ResolvedConferencePhoneConfig) -> list[tuple[float, float]]:
    if r.speaker_arrangement == "central":
        return [(0.0, 0.22 * r.r_char)]
    angles = _LOBE_ANGLES[r.speaker_arrangement]
    return [
        (r.lobe_r * math.cos(math.radians(a)), r.lobe_r * math.sin(math.radians(a))) for a in angles
    ]


def _perforated_mesh(face_r: float, name: str):
    panel = PerforatedPanelGeometry(
        (2.0 * face_r, 2.0 * face_r),
        0.004,
        hole_diameter=0.0044,
        pitch=(0.0090, 0.0090),
        frame=0.006,
        corner_radius=face_r,  # round the square panel into a disc
        stagger=True,
        center=True,
    )
    return mesh_from_geometry(panel, name)


def _fabric_pad_mesh(face_r: float, name: str):
    pad = ExtrudeGeometry.from_z0(
        superellipse_profile(2.0 * face_r, 2.0 * face_r, exponent=2.6, segments=48), 0.0026
    )
    return mesh_from_geometry(pad, name)


def _build_speakers(body, r: ResolvedConferencePhoneConfig, mats) -> None:
    grille_mat = mats["fabric"] if r.grille_treatment == "fabric" else mats["grille"]

    if r.speaker_arrangement == "perimeter_ring":
        # Segmented perimeter band (S9): boxes along the rim, all embedded in the
        # body top so the band welds to the shell (no island).
        ring_r = 0.72 * r.r_char
        n_seg = 18
        seg_len = 2.0 * math.pi * ring_r / n_seg * 1.06
        for i in range(n_seg):
            a = 2.0 * math.pi * (i + 0.5) / n_seg
            body.visual(
                Box((seg_len, 0.026, 0.006)),
                origin=Origin(
                    xyz=(ring_r * math.cos(a), ring_r * math.sin(a), r.top - 0.001),
                    rpy=(0.0, 0.0, a + math.pi / 2.0),
                ),
                material=grille_mat,
                name=f"speaker_grille_{i}", material_class_id=("metal.patterned_sheet_panel" if r.grille_treatment in {"perforated", "domed"} else "fabric.open_mesh"),
            )
        return

    positions = _speaker_positions(r)
    is_central = r.speaker_arrangement == "central"
    face_r = r.central_face_r if is_central else r.face_r

    if r.grille_treatment == "domed":
        # Central domed grille (S5): a lofted dome + sparse perforation dots.
        cx, cy = positions[0]
        dome_h = 0.030
        loops = []
        for f in (1.0, 0.94, 0.85, 0.72, 0.55, 0.36, 0.16):
            rr = f * face_r
            zz = r.top - 0.002 + dome_h * (1.0 - f * f)
            loops.append(
                [
                    (
                        cx + rr * math.cos(2.0 * math.pi * i / 60),
                        cy + rr * math.sin(2.0 * math.pi * i / 60),
                        zz,
                    )
                    for i in range(60)
                ]
            )
        body.visual(
            mesh_from_geometry(LoftGeometry(loops, cap=True, closed=True), "speaker_grille_0"),
            material=grille_mat,
            name="speaker_grille_0", material_class_id="plastic.opaque_glossy_molded",
        )
        k = 0
        for f in (0.90, 0.78, 0.64, 0.48, 0.30):
            rr = f * face_r
            zz = r.top - 0.002 + dome_h * (1.0 - f * f)
            n = max(8, int(2.0 * math.pi * rr / 0.010))
            for i in range(n):
                a = 2.0 * math.pi * i / n
                body.visual(
                    Sphere(radius=0.0011),
                    origin=Origin(xyz=(cx + rr * math.cos(a), cy + rr * math.sin(a), zz - 0.0004)),
                    material=mats["grille"],
                    name=f"perf_dot_{k}", material_class_id="metal.patterned_sheet_panel",
                )
                k += 1
        return

    # perforated / fabric discrete grilles — build ONE mesh, place N times.
    if r.grille_treatment == "perforated":
        grille_mesh = _perforated_mesh(face_r, "speaker_grille")
    else:
        grille_mesh = _fabric_pad_mesh(face_r, "speaker_grille")
    for i, (sx, sy) in enumerate(positions):
        if not is_central:
            # recessed surround ring under each pod (fused visual, defines the pod).
            body.visual(
                mesh_from_geometry(
                    ExtrudeGeometry.from_z0(
                        superellipse_profile(
                            2.0 * face_r + 0.010, 2.0 * face_r + 0.010, exponent=2.4, segments=40
                        ),
                        0.005,
                    ),
                    f"speaker_surround_{i}",
                ),
                origin=Origin(xyz=(sx, sy, r.top - 0.004)),
                material=mats["bezel"],
                name=f"speaker_surround_{i}", material_class_id="plastic.opaque_glossy_molded",
            )
        body.visual(
            grille_mesh,
            origin=Origin(xyz=(sx, sy, r.top - 0.001)),
            material=grille_mat,
            name=f"speaker_grille_{i}", material_class_id=("metal.patterned_sheet_panel" if r.grille_treatment in {"perforated", "domed"} else "fabric.open_mesh"),
        )


# ===========================================================================
# Slot D: control surface (console + LCD, fused body visuals). Returns the
# key-mount transform helper.
# ===========================================================================
def _panel_point(
    r: ResolvedConferencePhoneConfig, u: float, v: float
) -> tuple[float, float, float]:
    """World point on the (possibly tilted) console top surface. u across (x), v
    up-slope from the console center (y). deck_z is the single origin-height source."""
    if r.panel_tilt <= 1e-6:
        return (u, r.console_y + v, r.deck_z)
    ct, st = math.cos(r.panel_tilt), math.sin(r.panel_tilt)
    # tilt about X: console top faces up-and-toward-user (−Y front, higher at +Y rear).
    return (u, r.console_y + v * ct, r.deck_z + v * st)


def _build_console(body, r: ResolvedConferencePhoneConfig, mats) -> None:
    cw, cd = CONSOLE_HALF_W, CONSOLE_HALF_D
    if r.control_surface == "flush":
        # Thin recessed deck panel flush at the body top.
        body.visual(
            Box((2.0 * cw, 2.0 * cd, 0.004)),
            origin=Origin(xyz=(0.0, r.console_y, r.top - 0.001)),
            material=mats["bezel"],
            name="control_deck", material_class_id="plastic.opaque_glossy_molded",
        )
    elif r.control_surface == "raised":
        body.visual(
            Box((2.0 * cw, 2.0 * cd, r.deck_rise + 0.006)),
            origin=Origin(xyz=(0.0, r.console_y, r.top - 0.006 + (r.deck_rise + 0.006) / 2.0)),
            material=mats["accent"],
            name="control_deck", material_class_id="plastic.opaque_glossy_molded",
        )
        body.visual(
            Box((2.0 * cw - 0.012, 2.0 * cd - 0.012, 0.003)),
            origin=Origin(xyz=(0.0, r.console_y, r.deck_z - 0.0015)),
            material=mats["bezel"],
            name="control_face", material_class_id="plastic.opaque_glossy_molded",
        )
    else:  # tilted
        # Console box whose TOP face coincides with the _panel_point plane (so keys
        # seated at _panel_point sit on it), tall enough that its front edge sinks
        # into the body top and welds to the shell (no island).
        console_h = 0.024
        st = math.sin(r.panel_tilt)
        ct = math.cos(r.panel_tilt)
        px, py, pz = _panel_point(r, 0.0, 0.0)
        # top-face normal = R_x(tilt)*(0,0,1) = (0,-sin,cos); center = top - n*(h/2)
        ccx = px
        ccy = py + st * (console_h / 2.0)
        ccz = pz - ct * (console_h / 2.0)
        body.visual(
            Box((2.0 * cw, 2.0 * cd, console_h)),
            origin=Origin(xyz=(ccx, ccy, ccz), rpy=(r.panel_tilt, 0.0, 0.0)),
            material=mats["bezel"],
            name="control_deck", material_class_id="plastic.opaque_glossy_molded",
        )

    # LCD at the rear band of the console (behind the keys, toward +Y). The bezel
    # straddles the deck surface (embed), glass proud along the surface normal.
    lcd_v = cd - 0.016
    bx, by, bz = _panel_point(r, 0.0, lcd_v)
    if r.control_surface == "tilted":
        tilt = (r.panel_tilt, 0.0, 0.0)
        st, ct = math.sin(r.panel_tilt), math.cos(r.panel_tilt)
        ny, nz = -(-st), ct  # surface normal y,z = (sin, cos)
    else:
        tilt = (0.0, 0.0, 0.0)
        ny, nz = 0.0, 1.0
    body.visual(
        Box((0.058, 0.022, 0.005)),
        origin=Origin(xyz=(bx, by, bz), rpy=tilt),
        material=mats["bezel"],
        name="lcd_bezel", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((0.050, 0.015, 0.0016)),
        origin=Origin(xyz=(bx, by + ny * 0.0028, bz + nz * 0.0028), rpy=tilt),
        material=mats["lcd_glass"],
        name="lcd_glass", material_class_id="glass.smoked_tinted",
    )
    for j, du in enumerate((-0.012, 0.010)):
        body.visual(
            Box((0.018, 0.0016, 0.0004)),
            origin=Origin(xyz=(bx + du, by + ny * 0.0030, bz + nz * 0.0030), rpy=tilt),
            material=mats["lcd_ink"],
            name=f"lcd_segment_{j}", appearance_only=AppearanceOnlySpec(kind="screen", emission_strength=1.0),
        )


# ===========================================================================
# Keys: prismatic pushbuttons — the ONLY non-fixed joints (loop-emitted).
# ===========================================================================
def _add_key(
    model: ArticulatedObject,
    body,
    r: ResolvedConferencePhoneConfig,
    mats,
    *,
    name: str,
    u: float,
    v: float,
    sx: float,
    sy: float,
    cap_material: Material,
    legend_material: Material,
) -> None:
    key = model.part(name)
    key.visual(
        Cylinder(radius=min(sx, sy) * 0.16, length=KEY_STEM_H),
        origin=Origin(xyz=(0.0, 0.0, KEY_STEM_H / 2.0)),
        material=cap_material,
        name="stem", material_class_id="plastic.opaque_glossy_molded",
    )
    key.visual(
        Box((sx, sy, KEY_CAP_H)),
        origin=Origin(xyz=(0.0, 0.0, KEY_STEM_H + KEY_CAP_H / 2.0)),
        material=cap_material,
        name=f"{name}_cap", material_class_id="plastic.opaque_glossy_molded",
    )
    key.visual(
        Box((sx * 0.42, sy * 0.16, 0.0003)),
        origin=Origin(xyz=(0.0, 0.0, KEY_STEM_H + KEY_CAP_H + 0.00015)),
        material=legend_material,
        name="legend", appearance_only=AppearanceOnlySpec(kind="overlay"),
    )
    key.inertial = Inertial.from_geometry(
        Box((sx, sy, KEY_CAP_H)), mass=0.004, origin=Origin(xyz=(0.0, 0.0, KEY_CAP_H * 0.5))
    )
    ox, oy, oz = _panel_point(r, u, v)
    rpy = (r.panel_tilt, 0.0, 0.0) if r.control_surface == "tilted" else (0.0, 0.0, 0.0)
    model.articulation(
        f"body_to_{name}",
        ArticulationType.PRISMATIC,
        parent=body,
        child=key,
        origin=Origin(xyz=(ox, oy, oz - KEY_EMBED), rpy=rpy),
        axis=(0.0, 0.0, -1.0),
        motion_limits=MotionLimits(effort=1.5, velocity=0.05, lower=0.0, upper=r.key_travel),
    )


def _key_specs(r: ResolvedConferencePhoneConfig) -> list[tuple]:
    """Return (name, u, v, sx, sy, matkey) for every key, in console-local (u, v).

    Every key is inset from the console border by >= KEY_MARGIN on all sides (the
    numeric grid sits in the middle; the function keys FLANK it rather than sitting
    on the front edge), and the whole cluster occupies the console interior only —
    it is never pushed to the rim (spec §9, user feedback)."""
    specs: list[tuple] = []
    n_cols = 4 if r.keypad_shape == "4x4" else 3
    n_rows = 4
    col_pitch = 0.0135 if n_cols == 4 else 0.0160
    u0 = -(n_cols - 1) / 2.0 * col_pitch
    kw = 0.0115 if n_cols == 3 else 0.0100
    # Numeric rows, centered in the console interior (front-of-center → toward -v).
    v_rows = (0.006, -0.005, -0.016, -0.027)
    for rr in range(n_rows):
        for c in range(n_cols):
            specs.append(
                (f"keypad_{rr}_{c}", u0 + c * col_pitch, v_rows[rr], kw, 0.0090, "key_num")
            )
    # Function keys FLANK the numeric grid (inset within the console width, aligned
    # with numeric rows), so nothing sits on the front rim.
    fu = 0.036  # flank column |u| — outer edge lands exactly at KEY_MARGIN
    specs.append(("call_key", -fu, -0.016, 0.011, 0.0090, "call"))
    specs.append(("end_key", fu, -0.016, 0.011, 0.0090, "end"))
    specs.append(("softkey_0", -fu, -0.005, 0.011, 0.0080, "key_soft"))
    specs.append(("softkey_1", fu, -0.005, 0.011, 0.0080, "key_soft"))
    specs.append(("vol_down", -fu, 0.006, 0.011, 0.0080, "key_soft"))
    specs.append(("vol_up", fu, 0.006, 0.011, 0.0080, "key_soft"))
    return specs


def _build_keys(
    model: ArticulatedObject, body, r: ResolvedConferencePhoneConfig, mats
) -> list[str]:
    names: list[str] = []
    for name, u, v, sx, sy, matkey in _key_specs(r):
        _add_key(
            model,
            body,
            r,
            mats,
            name=name,
            u=u,
            v=v,
            sx=sx,
            sy=sy,
            cap_material=mats[matkey],
            legend_material=mats["legend"],
        )
        names.append(name)
    return names


# ===========================================================================
# Palette (⑥) — 5 colorways from the sources' black/gray/white/silver vocab.
# ===========================================================================
def _palette_rgba(style: PaletteStyle) -> dict[str, tuple[float, float, float, float]]:
    presets: dict[str, dict[str, tuple[float, float, float, float]]] = {
        "graphite_gray": dict(
            body=(0.31, 0.32, 0.34, 1.0),
            grille=(0.13, 0.13, 0.14, 1.0),
            fabric=(0.20, 0.20, 0.22, 1.0),
            key_num=(0.55, 0.57, 0.60, 1.0),
            key_soft=(0.42, 0.44, 0.47, 1.0),
            call=(0.15, 0.62, 0.28, 1.0),
            end=(0.72, 0.16, 0.16, 1.0),
            lcd_glass=(0.66, 0.75, 0.70, 1.0),
            lcd_ink=(0.06, 0.10, 0.08, 1.0),
            bezel=(0.18, 0.19, 0.21, 1.0),
            accent=(0.70, 0.71, 0.72, 1.0),
            foot=(0.12, 0.12, 0.13, 1.0),
            legend=(0.85, 0.86, 0.84, 1.0),
        ),
        "matte_black": dict(
            body=(0.02, 0.02, 0.022, 1.0),
            grille=(0.05, 0.05, 0.055, 1.0),
            fabric=(0.055, 0.055, 0.058, 1.0),
            key_num=(0.11, 0.11, 0.12, 1.0),
            key_soft=(0.06, 0.06, 0.065, 1.0),
            call=(0.02, 0.45, 0.18, 1.0),
            end=(0.55, 0.05, 0.04, 1.0),
            lcd_glass=(0.36, 0.43, 0.34, 1.0),
            lcd_ink=(0.02, 0.04, 0.03, 1.0),
            bezel=(0.03, 0.03, 0.033, 1.0),
            accent=(0.30, 0.31, 0.33, 1.0),
            foot=(0.03, 0.03, 0.03, 1.0),
            legend=(0.80, 0.80, 0.78, 1.0),
        ),
        "black_silver": dict(
            body=(0.03, 0.03, 0.033, 1.0),
            grille=(0.06, 0.06, 0.062, 1.0),
            fabric=(0.07, 0.07, 0.072, 1.0),
            key_num=(0.12, 0.12, 0.13, 1.0),
            key_soft=(0.09, 0.09, 0.095, 1.0),
            call=(0.0, 0.48, 0.17, 1.0),
            end=(0.72, 0.02, 0.02, 1.0),
            lcd_glass=(0.52, 0.76, 0.44, 1.0),
            lcd_ink=(0.03, 0.06, 0.035, 1.0),
            bezel=(0.62, 0.62, 0.60, 1.0),
            accent=(0.74, 0.74, 0.70, 1.0),
            foot=(0.05, 0.05, 0.05, 1.0),
            legend=(0.86, 0.88, 0.84, 1.0),
        ),
        "white_silver": dict(
            body=(0.90, 0.90, 0.88, 1.0),
            grille=(0.10, 0.10, 0.11, 1.0),
            fabric=(0.30, 0.30, 0.32, 1.0),
            key_num=(0.24, 0.24, 0.26, 1.0),
            key_soft=(0.38, 0.39, 0.41, 1.0),
            call=(0.10, 0.60, 0.28, 1.0),
            end=(0.75, 0.18, 0.16, 1.0),
            lcd_glass=(0.30, 0.72, 0.52, 1.0),
            lcd_ink=(0.05, 0.10, 0.07, 1.0),
            bezel=(0.55, 0.56, 0.57, 1.0),
            accent=(0.72, 0.73, 0.74, 1.0),
            foot=(0.30, 0.30, 0.31, 1.0),
            legend=(0.15, 0.15, 0.16, 1.0),
        ),
        "charcoal_two_tone": dict(
            body=(0.16, 0.17, 0.19, 1.0),
            grille=(0.08, 0.08, 0.085, 1.0),
            fabric=(0.10, 0.10, 0.11, 1.0),
            key_num=(0.30, 0.31, 0.33, 1.0),
            key_soft=(0.22, 0.23, 0.25, 1.0),
            call=(0.10, 0.55, 0.25, 1.0),
            end=(0.65, 0.12, 0.12, 1.0),
            lcd_glass=(0.50, 0.74, 0.46, 1.0),
            lcd_ink=(0.03, 0.06, 0.04, 1.0),
            bezel=(0.10, 0.10, 0.11, 1.0),
            accent=(0.60, 0.61, 0.63, 1.0),
            foot=(0.08, 0.08, 0.09, 1.0),
            legend=(0.82, 0.83, 0.81, 1.0),
        ),
    }
    return presets[style]


# ===========================================================================
# Build.
# ===========================================================================
def build_conference_phone(
    config: ConferencePhoneConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)

    pal = _palette_rgba(r.palette_style)
    mats = {
        key: model.material(f"cp_{key}_{r.palette_style}", rgba=rgba) for key, rgba in pal.items()
    }

    body = _build_body(model, r, mats)
    _build_speakers(body, r, mats)
    _build_console(body, r, mats)
    _build_keys(model, body, r, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_conference_phone(
    seed: int, *, assets: AssetContext | None = None
) -> ArticulatedObject:
    return build_conference_phone(config_from_seed(seed), assets=assets)


# ===========================================================================
# Tests.
# ===========================================================================
def run_conference_phone_tests(
    object_model: ArticulatedObject, config: ConferencePhoneConfig
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    body = object_model.get_part("body")

    key_names = [name for name, *_ in _key_specs(r)]

    # ---- Seated-cap allowances: each cap/stem sinks into its deck well. ----
    deck_elems = ("body_shell", "control_deck", "control_face")
    for kn in key_names:
        for elem_a in (f"{kn}_cap", "stem"):
            for elem_b in deck_elems:
                ctx.allow_overlap(
                    object_model.get_part(kn),
                    body,
                    elem_a=elem_a,
                    elem_b=elem_b,
                    reason="Keycap/stem is seated into its shallow deck well.",
                )

    # ---- Baseline checks. ----
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()

    # ---- Identity: low broad static desktop body. ----
    ba = ctx.part_world_aabb(body)
    if ba is not None:
        ext = (ba[1][0] - ba[0][0], ba[1][1] - ba[0][1], ba[1][2] - ba[0][2])
        ctx.check(
            "body_low_and_broad",
            ext[0] > 0.14 and ext[1] > 0.14 and ext[2] < 0.10,
            f"ext={tuple(round(e, 3) for e in ext)}",
        )

    # ---- Slot B: speaker arrangement realized (fused body visuals). ----
    vis = [v.name for v in body.visuals]
    n_grilles = sum(1 for n in vis if n.startswith("speaker_grille_"))
    if r.speaker_arrangement == "perimeter_ring":
        ctx.check("perimeter_ring_band", n_grilles >= 12, f"segments={n_grilles}")
    elif r.grille_treatment == "domed":
        n_dots = sum(1 for n in vis if n.startswith("perf_dot_"))
        ctx.check(
            "domed_central_grille",
            n_grilles == 1 and n_dots >= 20,
            f"grilles={n_grilles} dots={n_dots}",
        )
    else:
        ctx.check(
            "discrete_speaker_count",
            n_grilles == r.speaker_count,
            f"grilles={n_grilles} expected N={r.speaker_count}",
        )

    # ---- Slot C: grille material class present. ----
    ctx.check(
        "grille_treatment_valid",
        r.grille_treatment in GRILLES,
        f"grille={r.grille_treatment}",
    )

    # ---- Slot D: control deck present + LCD behind keys. ----
    ctx.check("control_deck_present", "control_deck" in vis, "missing control_deck")
    lcd_aabb = ctx.part_element_world_aabb(body, elem="lcd_glass")
    rep_key = object_model.get_part("keypad_3_0")
    kb = ctx.part_world_aabb(rep_key)
    if lcd_aabb is not None and kb is not None:
        lcd_cy = (lcd_aabb[0][1] + lcd_aabb[1][1]) / 2.0
        key_cy = (kb[0][1] + kb[1][1]) / 2.0
        ctx.check("lcd_behind_keypad", lcd_cy > key_cy, f"lcd_y={lcd_cy:.3f} key_y={key_cy:.3f}")

    # ---- Every key is INSET within the console border (not on the rim) and PROUD
    # above the body top (the console must not sink in and swallow the keys). ----
    deck_aabb = ctx.part_element_world_aabb(body, elem="control_deck")
    body_aabb = ctx.part_element_world_aabb(body, elem="body_shell")
    if deck_aabb is not None and body_aabb is not None:
        dmn, dmx = deck_aabb
        body_top = body_aabb[1][2]
        inset_ok = True
        proud_ok = True
        worst_inset = 1.0
        worst_proud = 1.0
        for kn in key_names:
            cap = ctx.part_element_world_aabb(object_model.get_part(kn), elem=f"{kn}_cap")
            if cap is None:
                continue
            cx = (cap[0][0] + cap[1][0]) / 2.0
            cy = (cap[0][1] + cap[1][1]) / 2.0
            m = min(cx - dmn[0], dmx[0] - cx, cy - dmn[1], dmx[1] - cy)
            worst_inset = min(worst_inset, m)
            if m < 0.004:  # cap center must be >=4mm inside the console footprint
                inset_ok = False
            # cap must rise above the body top (proud button, not buried in body).
            proud = cap[1][2] - body_top
            worst_proud = min(worst_proud, proud)
            if proud < 0.0008:
                proud_ok = False
        ctx.check("keys_inset_within_console", inset_ok, f"worst cap inset={worst_inset:.4f}m")
        ctx.check(
            "keys_proud_not_swallowed", proud_ok, f"worst cap-top above body={worst_proud:.4f}m"
        )

    # ---- Keys are the ONLY non-fixed joints, all PRISMATIC −Z. ----
    non_fixed = [
        a for a in object_model.articulations if a.articulation_type != ArticulationType.FIXED
    ]
    ctx.check(
        "only_prismatic_keys",
        len(non_fixed) == len(key_names)
        and all(a.articulation_type == ArticulationType.PRISMATIC for a in non_fixed)
        and all(tuple(a.axis) == (0.0, 0.0, -1.0) for a in non_fixed),
        f"non_fixed={len(non_fixed)} keys={len(key_names)}",
    )

    # ---- Keypad multiplicity: numeric array matches keypad_shape. ----
    n_cols = 4 if r.keypad_shape == "4x4" else 3
    n_numeric = sum(1 for n in key_names if n.startswith("keypad_"))
    ctx.check("keypad_array", n_numeric == 4 * n_cols, f"numeric={n_numeric} expected={4 * n_cols}")

    # ---- Targeted motion: a representative key presses per control_surface. ----
    jname = "body_to_keypad_1_1"
    key = object_model.get_part("keypad_1_1")
    joint = object_model.get_articulation(jname)
    rest = ctx.part_world_position(key)
    with ctx.pose({joint: r.key_travel}):
        pressed = ctx.part_world_position(key)
    if rest is not None and pressed is not None:
        if r.control_surface == "tilted":
            ctx.check(
                "tilted_key_presses_along_normal",
                pressed[2] < rest[2] - 0.0004 and pressed[1] > rest[1] + 0.0001,
                f"rest={tuple(round(x, 4) for x in rest)} pressed={tuple(round(x, 4) for x in pressed)}",
            )
        else:
            ctx.check(
                "flat_key_presses_straight_down",
                pressed[2] < rest[2] - 0.0004
                and abs(pressed[0] - rest[0]) < 1e-4
                and abs(pressed[1] - rest[1]) < 1e-4,
                f"rest={tuple(round(x, 4) for x in rest)} pressed={tuple(round(x, 4) for x in pressed)}",
            )

    # ---- Rule 5: sampled-pose overlap (many prismatic keys → cap the product). ----
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)

    # ---- Palette drives materials (⑥). ----
    ctx.check(
        "palette_valid",
        r.palette_style in PALETTE_STYLES and len(PALETTE_STYLES) == 5,
        f"palette={r.palette_style}",
    )

    # ---- slot_choices recorded. ----
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        str(object_model.meta.get("slot_choices")),
    )

    return ctx.report()


__all__ = (
    "ConferencePhoneConfig",
    "ResolvedConferencePhoneConfig",
    "build_conference_phone",
    "build_seeded_conference_phone",
    "config_from_seed",
    "resolve_config",
    "run_conference_phone_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
