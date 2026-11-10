# SPDX-License-Identifier: Apache-2.0

"""Electronic cash register modular template.

Sourced from the reviewed modular spec
``articraft_template_authoring/specs_modular_v1/cash_register.md`` and the
``Retail_Shop Fixtures / Cash register`` 5-star sample pool (2 origin parents +
4 single-axis fork variants):

  * S_A white ECR (``rec_a-white-electronic-cash-register-...546084bd``)
  * S_B charcoal Sharp-style ECR (``rec_a-dark-charcoal-...7fc07459``)
  * S_flat flat POS base fork (``rec_cash_register_var_body_flat_pos``)
  * S_tower tiered tower fork (``rec_cash_register_var_body_tiered_tower``)
  * S_coin8 8-coin multiplicity fork (``rec_cash_register_var_n_coin8``)
  * S_bill7 7-bill multiplicity fork (``rec_cash_register_var_n_bill7``)

Structure (pattern = ``mixed``): a constant ``drawer_housing`` root carries a
FIXED ``register_body`` head (③ Primary Form Family slot) plus a set of
**parallel children** that mount on the housing / body / drawer:

  * ``body_form`` (3, ③): ``classic_ecr_wedge`` (sculpted lofted wedge prism),
    ``flat_pos_base`` (low flat control deck), ``tiered_tower`` (stacked box
    tiers). Sets the deck / printer / display mount surfaces. (S_A/S_B vs S_flat
    vs S_tower)
  * ``display_mount`` (3, ①②): ``fixed_display_pod`` (inline body visual, no
    joint), ``tilting_operator_lcd`` (REVOLUTE +X part), or
    ``pole_swivel_customer_display`` (REVOLUTE +Z head on a pole). (S_A vs S_B)
  * ``receipt_printer`` (2, ②): ``hinged_printer_cover`` (REVOLUTE +X cover over
    a printer bay), or ``open_twin_paper_wells`` (inline roll wells, no joint).
    (S_A vs S_B)
  * ``drawer_till`` (2, ①): ``coin_only_single_row_till`` (single row of coin
    dividers), or ``bill_and_coin_till_with_clips`` (rear bill row + hinged
    REVOLUTE bill clips + front coin row). (S_A vs S_B)
  * coin **multiplicity**: ``n_coin`` coin compartments (always). (S_A n=5,
    S_B n=6, S_coin8 n=8)
  * bill **multiplicity**: ``n_bill`` bill compartments + one hinged clip each,
    only present with the bill-and-coin till. (S_B n=5, S_bill7 n=7)

Always-on core mechanisms: a PRISMATIC ``cash_drawer`` sliding out of the
housing, a REVOLUTE ``drawer_lock`` on the drawer front, and a regular grid of
PRISMATIC pressable keypad keys on the body deck.

All articulated children use captured-pin / seated geometry, so their joints
omit ``MatingContract`` (grandfathered) and rely on the flat articulation-origin
baseline (origins on real hardware) plus element-scoped ``allow_overlap`` for
the captured hinge hardware — mirroring the source records and the calculator
template.
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
    MeshGeometry,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
    mesh_from_geometry,
)

__modular__ = True

BodyForm = Literal["classic_ecr_wedge", "flat_pos_base", "tiered_tower"]
DisplayMount = Literal[
    "fixed_display_pod", "tilting_operator_lcd", "pole_swivel_customer_display"
]
ReceiptPrinter = Literal["hinged_printer_cover", "open_twin_paper_wells"]
DrawerTill = Literal["coin_only_single_row_till", "bill_and_coin_till_with_clips"]
MaterialStyle = Literal["white_ecr", "charcoal_ecr", "light_pos"]

BODY_FORMS: tuple[BodyForm, ...] = (
    "classic_ecr_wedge",
    "flat_pos_base",
    "tiered_tower",
)
DISPLAY_MOUNTS: tuple[DisplayMount, ...] = (
    "fixed_display_pod",
    "tilting_operator_lcd",
    "pole_swivel_customer_display",
)
RECEIPT_PRINTERS: tuple[ReceiptPrinter, ...] = (
    "hinged_printer_cover",
    "open_twin_paper_wells",
)
DRAWER_TILLS: tuple[DrawerTill, ...] = (
    "coin_only_single_row_till",
    "bill_and_coin_till_with_clips",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = ("white_ecr", "charcoal_ecr", "light_pos")

# Multiplicity domains (spec §8).
N_COIN_MIN, N_COIN_MAX = 4, 10
N_BILL_MIN, N_BILL_MAX = 3, 8

# --------------------------------------------------------------------------- #
# Constant housing (world frame: origin at housing bottom center, +Y front,
# +Z up). The register body seats on the housing top plane BODY_SEAT_Z.
# --------------------------------------------------------------------------- #
HOUSING_W = 0.42
HOUSING_D = 0.42
WALL_T = 0.012
BODY_SEAT_Z = 0.137  # top surface of the counter plate (register body seats here)

DRAWER_TRAVEL = 0.255
KEY_TRAVEL = 0.0026
KEY_SEAT_EMBED = 0.0006  # keycap skirt seats into the deck (allowed overlap)
KEY_H = 0.010

# Keypad grid (heterogeneous in the sources; here a regular grid — NOT a swept
# multiplicity axis, see spec §8 "Blocked").
KEY_COLS = 5
KEY_ROWS = 5

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "white_ecr": {
        "body": (0.93, 0.93, 0.91, 1.0),
        "base": (0.89, 0.89, 0.87, 1.0),
        "tray": (0.80, 0.80, 0.78, 1.0),
        "foot": (0.16, 0.16, 0.17, 1.0),
        "key": (0.63, 0.80, 0.90, 1.0),
        "key_accent": (0.92, 0.65, 0.72, 1.0),
        "bezel": (0.12, 0.12, 0.13, 1.0),
        "screen": (0.25, 0.63, 0.83, 1.0),
        "chrome": (0.76, 0.77, 0.79, 1.0),
        "paper": (0.97, 0.97, 0.95, 1.0),
        "clip": (0.20, 0.20, 0.22, 1.0),
        "digit": (0.25, 0.95, 0.35, 1.0),
    },
    "charcoal_ecr": {
        "body": (0.25, 0.22, 0.20, 1.0),
        "base": (0.17, 0.15, 0.14, 1.0),
        "tray": (0.18, 0.18, 0.19, 1.0),
        "foot": (0.10, 0.10, 0.11, 1.0),
        "key": (0.52, 0.52, 0.54, 1.0),
        "key_accent": (0.35, 0.72, 0.78, 1.0),
        "bezel": (0.05, 0.05, 0.06, 1.0),
        "screen": (0.62, 0.72, 0.82, 1.0),
        "chrome": (0.75, 0.75, 0.78, 1.0),
        "paper": (0.95, 0.95, 0.93, 1.0),
        "clip": (0.10, 0.10, 0.11, 1.0),
        "digit": (0.25, 0.95, 0.35, 1.0),
    },
    "light_pos": {
        "body": (0.82, 0.82, 0.84, 1.0),
        "base": (0.68, 0.68, 0.70, 1.0),
        "tray": (0.30, 0.30, 0.32, 1.0),
        "foot": (0.14, 0.14, 0.15, 1.0),
        "key": (0.30, 0.42, 0.62, 1.0),
        "key_accent": (0.35, 0.72, 0.78, 1.0),
        "bezel": (0.07, 0.07, 0.09, 1.0),
        "screen": (0.62, 0.72, 0.82, 1.0),
        "chrome": (0.75, 0.75, 0.78, 1.0),
        "paper": (0.95, 0.95, 0.93, 1.0),
        "clip": (0.18, 0.18, 0.20, 1.0),
        "digit": (0.25, 0.95, 0.35, 1.0),
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class CashRegisterConfig:
    body_form: BodyForm | None = None
    display_mount: DisplayMount | None = None
    receipt_printer: ReceiptPrinter | None = None
    drawer_till: DrawerTill | None = None
    n_coin: int | None = None
    n_bill: int | None = None
    material_style: MaterialStyle | None = None
    body_width_scale: float = 1.0
    drawer_travel_scale: float = 1.0
    key_pitch_scale: float = 1.0
    name: str = "cash_register"


@dataclass(frozen=True)
class ResolvedCashRegisterConfig:
    body_form: BodyForm
    display_mount: DisplayMount
    receipt_printer: ReceiptPrinter
    drawer_till: DrawerTill
    n_coin: int
    n_bill: int
    material_style: MaterialStyle
    body_half_w: float
    drawer_travel: float
    key_pitch_scale: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> CashRegisterConfig:
    """Deterministic weighted procedural sampling (seed 0 is not special)."""
    rng = random.Random(seed)
    body_form = rng.choices(BODY_FORMS, weights=[5, 3, 3], k=1)[0]
    display = rng.choice(DISPLAY_MOUNTS)
    printer = rng.choice(RECEIPT_PRINTERS)
    till = rng.choice(DRAWER_TILLS)
    # Coin count: small tills common, large tills rare (long tail).
    n_coin = rng.choices(
        [4, 5, 6, 7, 8, 9, 10], weights=[3, 6, 6, 3, 3, 1, 1], k=1
    )[0]
    n_bill = rng.choices([3, 4, 5, 6, 7, 8], weights=[3, 4, 6, 3, 2, 1], k=1)[0]
    return CashRegisterConfig(
        body_form=body_form,
        display_mount=display,
        receipt_printer=printer,
        drawer_till=till,
        n_coin=n_coin,
        n_bill=n_bill,
        material_style=rng.choice(MATERIAL_STYLES),
        body_width_scale=round(rng.uniform(0.94, 1.06), 4),
        drawer_travel_scale=round(rng.uniform(0.90, 1.08), 4),
        key_pitch_scale=round(rng.uniform(0.92, 1.08), 4),
        name=f"seeded_cash_register_{seed}",
    )


def resolve_config(
    config: CashRegisterConfig | None = None,
) -> ResolvedCashRegisterConfig:
    cfg = config or CashRegisterConfig()
    body_form = _pick(cfg.body_form, BODY_FORMS)
    display = _pick(cfg.display_mount, DISPLAY_MOUNTS)
    printer = _pick(cfg.receipt_printer, RECEIPT_PRINTERS)
    till = _pick(cfg.drawer_till, DRAWER_TILLS)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)

    n_coin = int(_clamp(cfg.n_coin if cfg.n_coin is not None else 5, N_COIN_MIN, N_COIN_MAX))
    n_bill = int(_clamp(cfg.n_bill if cfg.n_bill is not None else 5, N_BILL_MIN, N_BILL_MAX))

    width_scale = _clamp(cfg.body_width_scale, 0.94, 1.06)
    travel_scale = _clamp(cfg.drawer_travel_scale, 0.90, 1.08)
    key_pitch_scale = _clamp(cfg.key_pitch_scale, 0.92, 1.08)

    return ResolvedCashRegisterConfig(
        body_form=body_form,
        display_mount=display,
        receipt_printer=printer,
        drawer_till=till,
        n_coin=n_coin,
        n_bill=n_bill,
        material_style=material_style,
        body_half_w=0.19 * width_scale,
        drawer_travel=DRAWER_TRAVEL * travel_scale,
        key_pitch_scale=key_pitch_scale,
        name=cfg.name or "cash_register",
    )


def slot_choices_for_config(
    config: CashRegisterConfig | ResolvedCashRegisterConfig,
) -> tuple[tuple[str, str], ...]:
    r = config if isinstance(config, ResolvedCashRegisterConfig) else resolve_config(config)
    bill = f"{r.n_bill}_bills" if r.drawer_till == "bill_and_coin_till_with_clips" else "no_bills"
    return (
        ("body_form", r.body_form),
        ("display_mount", r.display_mount),
        ("receipt_printer", r.receipt_printer),
        ("drawer_till", r.drawer_till),
        ("coin_multiplicity", f"{r.n_coin}_coins"),
        ("bill_multiplicity", bill),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


# --------------------------------------------------------------------------- #
# Body-form mount surfaces (all fields in BODY-LOCAL frame: z=0 at the seat
# plane = housing top; the FIXED body joint lifts everything to world z).
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class BodyMounts:
    # Keyboard deck (front region carrying the keys).
    deck_pitch: float          # slope about +X (rad); 0 for a flat deck
    deck_rear_y: float         # rear edge of the key region
    deck_front_y: float        # front edge of the key region
    deck_rear_z: float         # deck surface z at deck_rear_y
    key_half_w: float          # lateral half-extent available for keys
    # Printer region (raised rear top surface).
    printer_cx: float
    printer_front_y: float
    printer_rear_y: float
    printer_top_z: float
    printer_half_w: float
    # Display mount.
    disp_x: float              # operator display anchor x (pod / lcd bracket)
    disp_seat_y: float
    disp_seat_z: float         # surface the pod/bracket sits on
    pole_x: float
    pole_y: float
    pole_seat_z: float         # deck/tier top where the pole rises from
    pole_len: float

    def key_surface_z(self, y: float) -> float:
        return self.deck_rear_z - (y - self.deck_rear_y) * math.tan(self.deck_pitch)


# --------------------------------------------------------------------------- #
# Wedge sculpted prism helper (kept Mesh-typed per Rule 3; the wedge profile is
# the recognizable ③ form). Adapted from S_A ``_prism_mesh`` (model.py:L57-79).
# --------------------------------------------------------------------------- #
def _prism_mesh(profile_yz: list[tuple[float, float]], half_width: float, name: str):
    """Convex prism spanning x = +/-half_width with a (y, z) cross-section."""
    pts = list(profile_yz)
    area = 0.0
    for i in range(len(pts)):
        y0, z0 = pts[i]
        y1, z1 = pts[(i + 1) % len(pts)]
        area += y0 * z1 - y1 * z0
    if area < 0.0:
        pts.reverse()
    geom = MeshGeometry()
    plus = [geom.add_vertex(half_width, y, z) for (y, z) in pts]
    minus = [geom.add_vertex(-half_width, y, z) for (y, z) in pts]
    for i in range(1, len(pts) - 1):
        geom.add_face(plus[0], plus[i], plus[i + 1])
        geom.add_face(minus[0], minus[i + 1], minus[i])
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        geom.add_face(minus[i], minus[j], plus[j])
        geom.add_face(minus[i], plus[j], plus[i])
    return mesh_from_geometry(geom, name)


# --------------------------------------------------------------------------- #
# Body form factories: emit register_body visuals, return BodyMounts.
# --------------------------------------------------------------------------- #
def _build_body_wedge(body, r: ResolvedCashRegisterConfig, mats) -> BodyMounts:
    """Adapted from S_A/S_B lofted wedge (model.py:L182-206 / L82-99)."""
    hw = r.body_half_w
    rear_top = 0.157
    deck_rear_z = 0.097
    deck_front_z = 0.053
    front_y = 0.185
    printer_front_y = -0.05
    rear_y = -0.19
    profile = [
        (rear_y, 0.0),
        (rear_y, rear_top),
        (printer_front_y, rear_top),
        (printer_front_y, deck_rear_z),
        (front_y, deck_front_z),
        (front_y, 0.0),
    ]
    body.visual(_prism_mesh(profile, hw, "body_shell"), material=mats["body"], name="body_shell", material_class_id="plastic.opaque_glossy_molded")
    pitch = math.atan2(deck_rear_z - deck_front_z, front_y - printer_front_y)
    return BodyMounts(
        deck_pitch=pitch,
        deck_rear_y=printer_front_y + 0.02,
        deck_front_y=front_y - 0.02,
        deck_rear_z=deck_rear_z - (0.02) * math.tan(pitch),
        key_half_w=hw - 0.02,
        printer_cx=-0.055,
        printer_front_y=printer_front_y,
        printer_rear_y=rear_y,
        printer_top_z=rear_top,
        printer_half_w=0.085,
        disp_x=0.10,
        disp_seat_y=-0.12,
        disp_seat_z=rear_top,
        pole_x=0.135,
        pole_y=-0.155,
        pole_seat_z=rear_top,
        pole_len=0.14,
    )


def _build_body_flat(body, r: ResolvedCashRegisterConfig, mats) -> BodyMounts:
    """Adapted from S_flat flat POS deck (model.py:L87-96)."""
    hw = r.body_half_w
    deck_h = 0.050
    deck_d = 0.38
    body.visual(
        Box((2 * hw, deck_d, deck_h)),
        origin=Origin(xyz=(0.0, 0.0, deck_h / 2.0)),
        material=mats["body"],
        name="body_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    deck_z = deck_h
    return BodyMounts(
        deck_pitch=0.0,
        deck_rear_y=-0.055,
        deck_front_y=deck_d / 2.0 - 0.02,
        deck_rear_z=deck_z,
        key_half_w=hw - 0.02,
        printer_cx=-0.06,
        printer_front_y=-0.075,
        printer_rear_y=-deck_d / 2.0 + 0.01,
        printer_top_z=deck_z,
        printer_half_w=0.085,
        disp_x=0.10,
        disp_seat_y=-0.12,
        disp_seat_z=deck_z,
        pole_x=0.135,
        pole_y=-0.15,
        pole_seat_z=deck_z,
        pole_len=0.24,
    )


def _build_body_tower(body, r: ResolvedCashRegisterConfig, mats) -> BodyMounts:
    """Adapted from S_tower stacked tiers (model.py:L184-218)."""
    hw = r.body_half_w
    base_h = 0.050
    base_d = 0.38
    body.visual(
        Box((2 * hw, base_d, base_h)),
        origin=Origin(xyz=(0.0, 0.0, base_h / 2.0)),
        material=mats["body"],
        name="body_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    # Middle printer tier (rear).
    tier_w = 2 * hw - 0.06
    tier_d = 0.17
    tier_h = 0.10
    tier_cy = -base_d / 2.0 + tier_d / 2.0 + 0.005
    tier_top = base_h + tier_h
    body.visual(
        Box((tier_w, tier_d, tier_h)),
        origin=Origin(xyz=(0.0, tier_cy, base_h + tier_h / 2.0)),
        material=mats["body"],
        name="printer_tier", material_class_id="plastic.opaque_glossy_molded",
    )
    # Upper display crown (rear of the printer tier), offset to the RIGHT so the
    # centered printer bay + its up-swinging cover stay clear of it (mirrors the
    # x-separated crown vs printer bay in the S_tower source).
    crown_w = 0.12
    crown_d = 0.11
    crown_h = 0.09
    crown_cx = 0.09
    crown_cy = tier_cy - 0.02
    crown_top = tier_top + crown_h
    body.visual(
        Box((crown_w, crown_d, crown_h)),
        origin=Origin(xyz=(crown_cx, crown_cy, tier_top + crown_h / 2.0)),
        material=mats["body"],
        name="display_crown", material_class_id="plastic.opaque_glossy_molded",
    )
    return BodyMounts(
        deck_pitch=0.0,
        deck_rear_y=-base_d / 2.0 + tier_d + 0.01,
        deck_front_y=base_d / 2.0 - 0.02,
        deck_rear_z=base_h,
        key_half_w=hw - 0.02,
        printer_cx=-0.055,
        printer_front_y=tier_cy + tier_d / 2.0,
        printer_rear_y=tier_cy - tier_d / 2.0,
        printer_top_z=tier_top,
        printer_half_w=0.072,
        disp_x=crown_cx,
        disp_seat_y=crown_cy + crown_d / 2.0,
        disp_seat_z=crown_top - 0.02,
        pole_x=crown_cx,
        pole_y=crown_cy,
        pole_seat_z=crown_top,
        pole_len=0.02,
    )


_BODY_BUILDERS = {
    "classic_ecr_wedge": _build_body_wedge,
    "flat_pos_base": _build_body_flat,
    "tiered_tower": _build_body_tower,
}


# --------------------------------------------------------------------------- #
# Keypad (parallel children of the body). Regular grid, per-key PRISMATIC press.
# Adapted from S_A/S_B per-key prismatic (model.py:L318-337 / L267-283).
# --------------------------------------------------------------------------- #
def _emit_keypad(model, r: ResolvedCashRegisterConfig, body, m: BodyMounts, mats) -> list[str]:
    y0, y1 = m.deck_rear_y, m.deck_front_y
    pitch_y = (y1 - y0) / KEY_ROWS
    half_w = m.key_half_w
    pitch_x = (2 * half_w) / KEY_COLS
    key_w = min(pitch_x, pitch_y) * 0.62 * r.key_pitch_scale
    key_w = min(key_w, min(pitch_x, pitch_y) * 0.82)
    names: list[str] = []
    for row in range(KEY_ROWS):
        cy = y0 + (row + 0.5) * pitch_y
        for col in range(KEY_COLS):
            cx = -half_w + (col + 0.5) * pitch_x
            kid = f"key_{row}_{col}"
            key = model.part(kid)
            is_accent = col == KEY_COLS - 1 or row == 0
            key.visual(
                Box((key_w, key_w, KEY_H)),
                origin=Origin(xyz=(0.0, 0.0, KEY_H / 2.0 - KEY_SEAT_EMBED)),
                material=mats["key_accent"] if is_accent else mats["key"],
                name="keycap", material_class_id="plastic.opaque_glossy_molded",
            )
            # Joint frame on the deck surface; press axis is the deck normal
            # (deck is tilted by deck_pitch about +X for the wedge, flat else).
            model.articulation(
                f"body_to_{kid}",
                ArticulationType.PRISMATIC,
                parent=body,
                child=key,
                origin=Origin(
                    xyz=(cx, cy, m.key_surface_z(cy)),
                    rpy=(-m.deck_pitch, 0.0, 0.0),
                ),
                axis=(0.0, 0.0, -1.0),
                motion_limits=MotionLimits(
                    effort=2.0, velocity=0.05, lower=0.0, upper=KEY_TRAVEL
                ),
            )
            names.append(kid)
    return names


# --------------------------------------------------------------------------- #
# Display mount (Slot B) — parallel children of the body.
# --------------------------------------------------------------------------- #
def _emit_display(model, r: ResolvedCashRegisterConfig, body, m: BodyMounts, mats) -> list[str]:
    if r.display_mount == "fixed_display_pod":
        return _emit_pod(body, m, mats)
    if r.display_mount == "tilting_operator_lcd":
        return _emit_tilt_lcd(model, body, m, mats)
    return _emit_pole_swivel(model, body, m, mats)


def _emit_pod(body, m: BodyMounts, mats) -> list[str]:
    """Fixed sloped display pod, inlined as body visuals (S_A model.py:L207-252)."""
    cx = m.disp_x
    cy = m.disp_seat_y
    cz = m.disp_seat_z
    body.visual(
        Box((0.10, 0.055, 0.052)),
        origin=Origin(xyz=(cx, cy + 0.005, cz + 0.026)),
        material=mats["body"],
        name="display_pod", material_class_id="plastic.opaque_glossy_molded",
    )
    tilt = -0.38  # pitch the face up-and-toward the operator
    front_y = cy + 0.005 + 0.028
    face_z = cz + 0.044
    body.visual(
        Box((0.086, 0.05, 0.005)),
        origin=Origin(xyz=(cx, front_y, face_z), rpy=(tilt, 0.0, 0.0)),
        material=mats["bezel"],
        name="display_bezel", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((0.07, 0.036, 0.003)),
        origin=Origin(xyz=(cx, front_y + 0.004, face_z + 0.003), rpy=(tilt, 0.0, 0.0)),
        material=mats["screen"],
        name="display_screen", material_class_id="tech.emissive_surface",
    )
    return []


def _emit_tilt_lcd(model, body, m: BodyMounts, mats) -> list[str]:
    """Tilt-up operator LCD, REVOLUTE about +X (S_B model.py:L323-345)."""
    cx = m.disp_x
    cy = m.disp_seat_y
    cz = m.disp_seat_z
    # Body-side mounting bracket (real anchoring visual for Rule 2).
    body.visual(
        Box((0.032, 0.024, 0.042)),
        origin=Origin(xyz=(cx, cy, cz + 0.021)),
        material=mats["body"],
        name="lcd_bracket", material_class_id="plastic.opaque_glossy_molded",
    )
    lcd = model.part("lcd_display")
    # Authored so the hinge edge sits at the part-frame origin (bottom edge);
    # the housing bottom dips ~3.5 mm onto the bracket top so it seats (contact).
    lcd.visual(
        Box((0.12, 0.016, 0.085)),
        origin=Origin(xyz=(0.0, 0.0, 0.039)),
        material=mats["bezel"],
        name="lcd_housing", material_class_id="plastic.opaque_glossy_molded",
    )
    lcd.visual(
        Box((0.10, 0.002, 0.062)),
        origin=Origin(xyz=(0.0, 0.009, 0.043)),
        material=mats["screen"],
        name="lcd_screen", material_class_id="tech.emissive_surface",
    )
    model.articulation(
        "body_to_lcd",
        ArticulationType.REVOLUTE,
        parent=body,
        child=lcd,
        origin=Origin(xyz=(cx, cy, cz + 0.042)),
        axis=(1.0, 0.0, 0.0),  # +q tilts the screen back toward the rear
        motion_limits=MotionLimits(effort=4.0, velocity=1.5, lower=-0.40, upper=0.40),
    )
    return ["lcd_display"]


def _emit_pole_swivel(model, body, m: BodyMounts, mats) -> list[str]:
    """Pole-mounted customer display that swivels about +Z (S_B model.py:L203-381)."""
    pole_top = m.pole_seat_z + m.pole_len
    body.visual(
        Cylinder(radius=0.010, length=m.pole_len),
        origin=Origin(xyz=(m.pole_x, m.pole_y, m.pole_seat_z + m.pole_len / 2.0)),
        material=mats["bezel"],
        name="display_pole", material_class_id="metal.blackened_gunmetal",
    )
    head = model.part("customer_display_head")
    head.visual(
        Cylinder(radius=0.013, length=0.018),
        origin=Origin(xyz=(0.0, 0.0, 0.006)),
        material=mats["bezel"],
        name="pole_collar", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((0.15, 0.032, 0.052)),
        origin=Origin(xyz=(0.0, 0.0, 0.040)),
        material=mats["bezel"],
        name="head_shell", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((0.128, 0.0016, 0.030)),
        origin=Origin(xyz=(0.0, 0.0163, 0.040)),
        material=mats["body"],
        name="digit_window", material_class_id="plastic.opaque_glossy_molded",
    )
    head.visual(
        Box((0.105, 0.0014, 0.014)),
        origin=Origin(xyz=(0.0, 0.0174, 0.040)),
        material=mats["digit"],
        name="digit_band", material_class_id="tech.emissive_surface",
    )
    model.articulation(
        "body_to_customer_display_head",
        ArticulationType.REVOLUTE,
        parent=body,
        child=head,
        origin=Origin(xyz=(m.pole_x, m.pole_y, pole_top)),
        axis=(0.0, 0.0, 1.0),
        motion_limits=MotionLimits(effort=4.0, velocity=2.0, lower=-1.5, upper=1.5),
    )
    return ["customer_display_head"]


# --------------------------------------------------------------------------- #
# Receipt printer (Slot C) — parallel children of the body.
# --------------------------------------------------------------------------- #
def _bay_bounds(m: BodyMounts) -> tuple[float, float, float, float, float]:
    bay_rear = m.printer_rear_y + 0.012
    bay_front = m.printer_front_y - 0.006
    bay_cx = m.printer_cx
    bay_hw = min(m.printer_half_w, 0.072)
    return bay_rear, bay_front, bay_cx, bay_hw, m.printer_top_z


def _emit_printer(model, r: ResolvedCashRegisterConfig, body, m: BodyMounts, mats) -> list[str]:
    if r.receipt_printer == "hinged_printer_cover":
        return _emit_hinged_cover(model, body, m, mats)
    return _emit_open_wells(body, m, mats)


def _emit_hinged_cover(model, body, m: BodyMounts, mats) -> list[str]:
    """Printer bay + hinged cover, REVOLUTE about +X (S_A model.py:L254-399)."""
    bay_rear, bay_front, cx, hw, top = _bay_bounds(m)
    wall_h = 0.026
    bay_w = 2.0 * hw
    mid_y = (bay_rear + bay_front) / 2.0
    body.visual(
        Box((bay_w, 0.008, wall_h)),
        origin=Origin(xyz=(cx, bay_rear, top + wall_h / 2.0)),
        material=mats["body"],
        name="printer_bay_rear_wall", material_class_id="plastic.opaque_glossy_molded",
    )
    body.visual(
        Box((bay_w, 0.008, wall_h)),
        origin=Origin(xyz=(cx, bay_front, top + wall_h / 2.0)),
        material=mats["body"],
        name="printer_bay_front_wall", material_class_id="plastic.opaque_glossy_molded",
    )
    for i, wx in enumerate((cx - hw + 0.004, cx + hw - 0.004)):
        body.visual(
            Box((0.008, bay_front - bay_rear, wall_h)),
            origin=Origin(xyz=(wx, mid_y, top + wall_h / 2.0)),
            material=mats["body"],
            name=f"printer_bay_wall_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    body.visual(
        Cylinder(radius=0.012, length=bay_w - 0.02),
        origin=Origin(xyz=(cx, mid_y, top + 0.012), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["paper"],
        name="paper_roll", material_class_id="paper.plain_sheet",
    )
    # Hinged cover: hinge edge at the part-frame origin (rear-top), panels +Y.
    cover = model.part("printer_cover")
    reach = bay_front - bay_rear - 0.004
    cover.visual(
        Box((bay_w, reach * 0.62, 0.008)),
        origin=Origin(xyz=(0.0, reach * 0.31, 0.004)),
        material=mats["body"],
        name="cover_rear_panel", material_class_id="plastic.opaque_glossy_molded",
    )
    cover.visual(
        Box((bay_w, reach * 0.32, 0.008)),
        origin=Origin(xyz=(0.0, reach * 0.84, 0.004)),
        material=mats["body"],
        name="cover_front_panel", material_class_id="plastic.opaque_glossy_molded",
    )
    # Side rails span the full cover length, bridging the rear + front panels
    # into one connected island across the receipt slot between them.
    for i, rx in enumerate((-(bay_w / 2.0 - 0.006), bay_w / 2.0 - 0.006)):
        cover.visual(
            Box((0.010, reach, 0.008)),
            origin=Origin(xyz=(rx, reach * 0.5, 0.004)),
            material=mats["body"],
            name=f"cover_rail_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
    cover.visual(
        Box((bay_w * 0.4, 0.009, 0.0035)),
        origin=Origin(xyz=(0.0, reach * 0.7, 0.0095)),
        material=mats["screen"],
        name="paper_cutter", material_class_id="metal.stainless_matte",
    )
    model.articulation(
        "body_to_printer_cover",
        ArticulationType.REVOLUTE,
        parent=body,
        child=cover,
        origin=Origin(xyz=(cx, bay_rear, top + wall_h)),
        axis=(1.0, 0.0, 0.0),
        motion_limits=MotionLimits(effort=3.0, velocity=2.0, lower=0.0, upper=1.35),
    )
    return ["printer_cover"]


def _emit_open_wells(body, m: BodyMounts, mats) -> list[str]:
    """Twin open paper-roll wells, inlined as body visuals (S_B model.py:L169-194)."""
    bay_rear, bay_front, cx, hw, top = _bay_bounds(m)
    mid_y = (bay_rear + bay_front) / 2.0
    depth = bay_front - bay_rear
    wall_h = 0.030
    for i, wxc in enumerate((cx - hw / 2.0, cx + hw / 2.0)):
        # Each well: a short 3-sided box frame + a roll + a rising paper strip.
        body.visual(
            Box((hw - 0.006, 0.007, wall_h)),
            origin=Origin(xyz=(wxc, bay_rear, top + wall_h / 2.0)),
            material=mats["body"],
            name=f"well_rear_wall_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        body.visual(
            Box((0.007, depth, wall_h)),
            origin=Origin(
                xyz=(wxc - (hw - 0.006) / 2.0 + 0.0035, mid_y, top + wall_h / 2.0)
            ),
            material=mats["body"],
            name=f"well_side_wall_{i}", material_class_id="plastic.opaque_glossy_molded",
        )
        body.visual(
            Cylinder(radius=0.014, length=hw - 0.012),
            origin=Origin(xyz=(wxc, mid_y, top + 0.014), rpy=(0.0, math.pi / 2.0, 0.0)),
            material=mats["paper"],
            name=f"paper_roll_{i}", material_class_id="paper.plain_sheet",
        )
        body.visual(
            Box((hw - 0.02, 0.0012, 0.06)),
            origin=Origin(xyz=(wxc, bay_rear + 0.004, top + 0.05), rpy=(0.14, 0.0, 0.0)),
            material=mats["paper"],
            name=f"paper_strip_{i}", material_class_id="paper.plain_sheet",
        )
    return []


# --------------------------------------------------------------------------- #
# Cash drawer + till + lock (world frame; drawer PRISMATIC on the housing).
# --------------------------------------------------------------------------- #
# Till interior geometry (world z).
_TRAY_FLOOR_Z = 0.030
_TRAY_WALL_H = 0.050
_TRAY_REAR_Y = -0.150
_TRAY_FRONT_Y = 0.206  # front wall front face (0.210) seats against drawer_front rear
_TRAY_HALF_W = 0.180


def _build_drawer(drawer, r: ResolvedCashRegisterConfig, mats) -> None:
    drawer.visual(
        Box((HOUSING_W, 0.020, 0.112)),
        origin=Origin(xyz=(0.0, 0.220, 0.072)),
        material=mats["base"],
        name="drawer_front", material_class_id="metal.paint_coated",
    )


def _emit_till(model, r: ResolvedCashRegisterConfig, drawer, mats) -> None:
    # Shared tray shell (floor + perimeter walls) — FIXED decoration visuals.
    cy = (_TRAY_REAR_Y + _TRAY_FRONT_Y) / 2.0
    depth = _TRAY_FRONT_Y - _TRAY_REAR_Y
    drawer.visual(
        Box((2 * _TRAY_HALF_W, depth, 0.008)),
        origin=Origin(xyz=(0.0, cy, _TRAY_FLOOR_Z)),
        material=mats["tray"],
        name="tray_floor", material_class_id="metal.paint_coated",
    )
    wall_cz = _TRAY_FLOOR_Z + _TRAY_WALL_H / 2.0
    drawer.visual(
        Box((2 * _TRAY_HALF_W, 0.008, _TRAY_WALL_H)),
        origin=Origin(xyz=(0.0, _TRAY_REAR_Y, wall_cz)),
        material=mats["tray"],
        name="tray_rear_wall", material_class_id="metal.paint_coated",
    )
    drawer.visual(
        Box((2 * _TRAY_HALF_W, 0.008, _TRAY_WALL_H)),
        origin=Origin(xyz=(0.0, _TRAY_FRONT_Y, wall_cz)),
        material=mats["tray"],
        name="tray_front_wall", material_class_id="metal.paint_coated",
    )
    for i, wx in enumerate((-_TRAY_HALF_W, _TRAY_HALF_W)):
        drawer.visual(
            Box((0.008, depth, _TRAY_WALL_H)),
            origin=Origin(xyz=(wx, cy, wall_cz)),
            material=mats["tray"],
            name=f"tray_side_wall_{i}", material_class_id="metal.paint_coated",
        )

    if r.drawer_till == "coin_only_single_row_till":
        _emit_coin_dividers(drawer, mats, r.n_coin, _TRAY_REAR_Y + 0.006, _TRAY_FRONT_Y - 0.006)
    else:
        _emit_bill_and_coin(model, r, drawer, mats)


def _emit_coin_dividers(drawer, mats, n_coin: int, y_lo: float, y_hi: float) -> None:
    depth = y_hi - y_lo
    cy = (y_lo + y_hi) / 2.0
    div_h = _TRAY_WALL_H - 0.006
    div_cz = _TRAY_FLOOR_Z + 0.004 + div_h / 2.0
    span = 2 * _TRAY_HALF_W - 0.012
    for i in range(n_coin - 1):
        dx = -span / 2.0 + (i + 1) * span / n_coin
        drawer.visual(
            Box((0.006, depth, div_h)),
            origin=Origin(xyz=(dx, cy, div_cz)),
            material=mats["tray"],
            name=f"coin_divider_{i}", material_class_id="metal.paint_coated",
        )


def _emit_bill_and_coin(model, r: ResolvedCashRegisterConfig, drawer, mats) -> None:
    # Rear half = bill row, front half = coin row, split by a lateral divider.
    bill_depth = 0.145
    mid_y = _TRAY_REAR_Y + bill_depth
    div_h = _TRAY_WALL_H - 0.006
    div_cz = _TRAY_FLOOR_Z + 0.004 + div_h / 2.0
    drawer.visual(
        Box((2 * _TRAY_HALF_W, 0.006, div_h)),
        origin=Origin(xyz=(0.0, mid_y, div_cz)),
        material=mats["tray"],
        name="till_mid_divider", material_class_id="metal.paint_coated",
    )
    # Coin row (front).
    _emit_coin_dividers(drawer, mats, r.n_coin, mid_y + 0.006, _TRAY_FRONT_Y - 0.006)
    # Bill row (rear): n_bill compartments -> n_bill-1 dividers.
    span = 2 * _TRAY_HALF_W - 0.012
    bill_cy = (_TRAY_REAR_Y + 0.006 + mid_y) / 2.0
    bill_row_depth = mid_y - (_TRAY_REAR_Y + 0.006)
    for i in range(r.n_bill - 1):
        dx = -span / 2.0 + (i + 1) * span / r.n_bill
        drawer.visual(
            Box((0.006, bill_row_depth, div_h)),
            origin=Origin(xyz=(dx, bill_cy, div_cz)),
            material=mats["tray"],
            name=f"bill_divider_{i}", material_class_id="metal.paint_coated",
        )
    # Hinged bill clips: one short spring flipper per bill compartment, hinged
    # at the till rear wall top, REVOLUTE about +X. The arm is a stubby flipper
    # (not the full bill depth) so lifting it clears the counter top above the
    # closed drawer.
    hinge_y = _TRAY_REAR_Y + 0.005  # tube captured in the rear wall (overlap)
    hinge_z = _TRAY_FLOOR_Z + _TRAY_WALL_H - 0.004
    arm_len = min(bill_row_depth - 0.006, 0.045)
    for i in range(r.n_bill):
        cx = -span / 2.0 + (i + 0.5) * span / r.n_bill
        clip = model.part(f"bill_clip_{i}")
        _build_bill_clip(clip, mats, span / r.n_bill, arm_len)
        model.articulation(
            f"bill_clip_{i}_hinge",
            ArticulationType.REVOLUTE,
            parent=drawer,
            child=clip,
            origin=Origin(xyz=(cx, hinge_y, hinge_z)),
            axis=(1.0, 0.0, 0.0),
            motion_limits=MotionLimits(effort=2.0, velocity=3.0, lower=0.0, upper=0.90),
        )


def _build_bill_clip(clip, mats, cell_w: float, arm_len: float) -> None:
    """Hinge tube (captured in the rear wall) + a pressing arm + a pad.
    Local origin on the hinge axis (part-frame y=0, z=0). Adapted from S_B
    ``_bill_clip`` (model.py:L119-129)."""
    tube_w = min(cell_w * 0.8, 0.05)
    clip.visual(
        Cylinder(radius=0.0045, length=tube_w),
        origin=Origin(xyz=(0.0, 0.0, 0.0), rpy=(0.0, math.pi / 2.0, 0.0)),
        material=mats["clip"],
        name="clip_tube", material_class_id="metal.blackened_gunmetal",
    )
    droop = 0.30  # rest arm droops down over the bills
    clip.visual(
        Box((tube_w * 0.7, arm_len, 0.003)),
        origin=Origin(
            xyz=(0.0, arm_len / 2.0 * math.cos(droop), -arm_len / 2.0 * math.sin(droop)),
            rpy=(-droop, 0.0, 0.0),
        ),
        material=mats["clip"],
        name="clip_arm", material_class_id="metal.blackened_gunmetal",
    )
    clip.visual(
        Box((tube_w, 0.02, 0.0035)),
        origin=Origin(
            xyz=(0.0, arm_len * math.cos(droop), -arm_len * math.sin(droop) - 0.002),
        ),
        material=mats["clip"],
        name="clip_pad", material_class_id="rubber.smooth_plain",
    )


def _emit_lock(model, r: ResolvedCashRegisterConfig, drawer, mats) -> None:
    """Rotating key lock on the drawer front, REVOLUTE about +Y (S_A L454-481)."""
    lock = model.part("drawer_lock")
    lock.visual(
        Cylinder(radius=0.0115, length=0.013),
        origin=Origin(xyz=(0.0, 0.0065, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["chrome"],
        name="lock_barrel", material_class_id="metal.chrome_polished",
    )
    lock.visual(
        Cylinder(radius=0.009, length=0.002),
        origin=Origin(xyz=(0.0, 0.0140, 0.0), rpy=(math.pi / 2.0, 0.0, 0.0)),
        material=mats["chrome"],
        name="lock_face_ring", material_class_id="metal.chrome_polished",
    )
    lock.visual(
        Box((0.0026, 0.0018, 0.011)),
        origin=Origin(xyz=(0.0, 0.0142, 0.0)),
        material=mats["bezel"],
        name="keyway", material_class_id="metal.blackened_gunmetal",
    )
    model.articulation(
        "drawer_to_lock",
        ArticulationType.REVOLUTE,
        parent=drawer,
        child=lock,
        origin=Origin(xyz=(0.11, 0.230, 0.072)),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(effort=1.0, velocity=2.0, lower=-1.4, upper=1.4),
    )


# --------------------------------------------------------------------------- #
# Housing (constant root).
# --------------------------------------------------------------------------- #
def _build_housing(housing, r: ResolvedCashRegisterConfig, mats) -> None:
    hw = HOUSING_W / 2.0
    hd = HOUSING_D / 2.0
    for i, (fx, fy) in enumerate(
        ((-0.18, -0.18), (0.18, -0.18), (-0.18, 0.18), (0.18, 0.18))
    ):
        housing.visual(
            Box((0.032, 0.032, 0.010)),
            origin=Origin(xyz=(fx, fy, 0.005)),
            material=mats["foot"],
            name=f"foot_{i}", material_class_id="rubber.smooth_plain",
        )
    housing.visual(
        Box((HOUSING_W, HOUSING_D, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, 0.016)),
        material=mats["base"],
        name="bottom_panel", material_class_id="metal.paint_coated",
    )
    for i, wx in enumerate((-hw + 0.006, hw - 0.006)):
        housing.visual(
            Box((0.012, HOUSING_D, 0.103)),
            origin=Origin(xyz=(wx, 0.0, 0.0735)),
            material=mats["base"],
            name=f"side_wall_{i}", material_class_id="metal.paint_coated",
        )
    housing.visual(
        Box((HOUSING_W - 0.024, 0.012, 0.103)),
        origin=Origin(xyz=(0.0, -hd + 0.006, 0.0735)),
        material=mats["base"],
        name="back_wall", material_class_id="metal.paint_coated",
    )
    housing.visual(
        Box((HOUSING_W, HOUSING_D, 0.012)),
        origin=Origin(xyz=(0.0, 0.0, BODY_SEAT_Z - 0.006)),
        material=mats["base"],
        name="counter_top", material_class_id="metal.paint_coated",
    )


# --------------------------------------------------------------------------- #
# Build
# --------------------------------------------------------------------------- #
def build_cash_register(
    config: CashRegisterConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    palette = PALETTES[r.material_style]
    mats = {
        key: model.material(f"cr_{key}_{r.material_style}", rgba=rgba)
        for key, rgba in palette.items()
    }

    housing = model.part("drawer_housing")
    _build_housing(housing, r, mats)

    body = model.part("register_body")
    mounts = _BODY_BUILDERS[r.body_form](body, r, mats)
    model.articulation(
        "housing_to_register_body",
        ArticulationType.FIXED,
        parent=housing,
        child=body,
        origin=Origin(xyz=(0.0, 0.0, BODY_SEAT_Z)),
    )

    _emit_keypad(model, r, body, mounts, mats)
    _emit_display(model, r, body, mounts, mats)
    _emit_printer(model, r, body, mounts, mats)

    drawer = model.part("cash_drawer")
    _build_drawer(drawer, r, mats)
    model.articulation(
        "housing_to_drawer",
        ArticulationType.PRISMATIC,
        parent=housing,
        child=drawer,
        origin=Origin(),
        axis=(0.0, 1.0, 0.0),
        motion_limits=MotionLimits(
            effort=40.0, velocity=0.4, lower=0.0, upper=r.drawer_travel
        ),
    )
    _emit_till(model, r, drawer, mats)
    _emit_lock(model, r, drawer, mats)

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_cash_register(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_cash_register(config_from_seed(seed), assets=assets)


# --------------------------------------------------------------------------- #
# Tests
# --------------------------------------------------------------------------- #
def run_cash_register_tests(
    object_model: ArticulatedObject,
    config: CashRegisterConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)

    housing = object_model.get_part("drawer_housing")
    body = object_model.get_part("register_body")
    drawer = object_model.get_part("cash_drawer")

    # --- Captured-pin / seated allowances (grandfathered joints). ---
    ctx.allow_isolated_part(
        drawer,
        reason="cash drawer slides out of the housing on its tray floor and loses contact",
    )
    if "drawer_lock" in {p.name for p in object_model.parts}:
        ctx.allow_isolated_part(
            object_model.get_part("drawer_lock"),
            reason="drawer lock rides on the cash drawer and detaches with it when the drawer is opened",
        )
    for part in object_model.parts:
        if part.name.startswith("bill_clip_"):
            ctx.allow_isolated_part(
                part,
                reason="bill clip hinges on the till rear wall and detaches with the opened drawer",
            )
    ctx.allow_overlap(
        drawer, housing, elem_a="tray_floor", elem_b="bottom_panel",
        reason="drawer tray rides directly on the housing floor like a drawer slide.",
    )
    for part in object_model.parts:
        if part.name.startswith("key_"):
            ctx.allow_overlap(
                part, body, elem_a="keycap", elem_b="body_shell",
                reason="keycap skirt seats slightly into the deck like a key well.",
            )
    if r.display_mount == "tilting_operator_lcd":
        ctx.allow_overlap(
            object_model.get_part("lcd_display"), body,
            elem_a="lcd_housing", elem_b="lcd_bracket",
            reason="operator LCD hinge boss seats over the mounting bracket for the tilt joint.",
        )
    if r.display_mount == "pole_swivel_customer_display":
        ctx.allow_overlap(
            object_model.get_part("customer_display_head"), body,
            elem_a="pole_collar", elem_b="display_pole",
            reason="customer display collar sockets over the pole top for the swivel joint.",
        )
    if r.drawer_till == "bill_and_coin_till_with_clips":
        for i in range(r.n_bill):
            ctx.allow_overlap(
                object_model.get_part(f"bill_clip_{i}"), drawer,
                elem_a="clip_tube", elem_b="tray_rear_wall",
                reason="bill clip hinge tube is captured in the till rear wall like a hinge pin.",
            )

    # --- Compiler baseline. ---
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.warn_if_part_contains_disconnected_geometry_islands()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.015)
    ctx.fail_if_joint_mating_has_gap()
    # Rule 5: all non-FIXED joints stay clear across their sampled travel.
    ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)

    # --- Slot choices recorded and consistent. ---
    ctx.check(
        "slot_choices_recorded",
        tuple(object_model.meta.get("slot_choices", ())) == slot_choices_for_config(r),
        details=str(object_model.meta.get("slot_choices")),
    )

    # --- Cash drawer slides forward and stays retained. ---
    slide = object_model.get_articulation("housing_to_drawer")
    rest = ctx.part_world_position(drawer)
    with ctx.pose({slide: r.drawer_travel}):
        opened = ctx.part_world_position(drawer)
        ctx.expect_overlap(
            drawer, housing, axes="y", min_overlap=0.05,
            name="open drawer stays captured in the housing",
        )
    ctx.check(
        "drawer slides forward when opened",
        rest is not None and opened is not None and opened[1] > rest[1] + 0.9 * r.drawer_travel,
        details=f"rest={rest}, open={opened}",
    )

    # --- Keypad: regular grid of prismatic press keys; one presses down. ---
    key_parts = [p for p in object_model.parts if p.name.startswith("key_")]
    ctx.check(
        "keypad emits a full grid of pressable keys",
        len(key_parts) == KEY_COLS * KEY_ROWS,
        details=f"found {len(key_parts)}",
    )
    k0 = object_model.get_part("key_2_2")
    j0 = object_model.get_articulation("body_to_key_2_2")
    kr = ctx.part_world_position(k0)
    with ctx.pose({j0: KEY_TRAVEL}):
        kd = ctx.part_world_position(k0)
    ctx.check(
        "a keypad key presses down into the deck",
        kr is not None and kd is not None and kd[2] < kr[2] - 0.001,
        details=f"rest={kr}, pressed={kd}",
    )

    # --- Drawer lock rotates. ---
    lock_joint = object_model.get_articulation("drawer_to_lock")
    ctx.check(
        "drawer lock rotates both ways about +Y",
        lock_joint.motion_limits is not None
        and lock_joint.motion_limits.lower < -1.0
        and lock_joint.motion_limits.upper > 1.0
        and round(lock_joint.axis[1], 3) == 1.0,
        details=f"axis={lock_joint.axis} limits={lock_joint.motion_limits}",
    )

    # --- Coin compartments present (multiplicity). ---
    coin_dividers = [
        v for v in drawer.visuals if v.name.startswith("coin_divider_")
    ]
    ctx.check(
        "coin till has n_coin-1 dividers",
        len(coin_dividers) == r.n_coin - 1,
        details=f"expected {r.n_coin - 1}, found {len(coin_dividers)}",
    )

    # --- Display mount topology. ---
    if r.display_mount == "tilting_operator_lcd":
        lcd = object_model.get_part("lcd_display")
        jd = object_model.get_articulation("body_to_lcd")
        with ctx.pose({jd: 0.0}):
            a0 = ctx.part_world_aabb(lcd)
        with ctx.pose({jd: 0.35}):
            a1 = ctx.part_world_aabb(lcd)
        ctx.check(
            "tilting the operator LCD moves it toward the rear",
            a0 is not None and a1 is not None and a1[0][1] < a0[0][1] - 0.005,
            details=f"rest={a0}, tilted={a1}",
        )
    elif r.display_mount == "pole_swivel_customer_display":
        head = object_model.get_part("customer_display_head")
        jy = object_model.get_articulation("body_to_customer_display_head")
        with ctx.pose({jy: 0.0}):
            h0 = ctx.part_world_aabb(head)
        with ctx.pose({jy: 1.3}):
            h1 = ctx.part_world_aabb(head)
        ctx.check(
            "customer display swivels on the pole",
            h0 is not None and h1 is not None
            and (h1[1][0] - h1[0][0]) < (h0[1][0] - h0[0][0]) - 0.02,
            details=f"rest={h0}, turned={h1}",
        )
    else:
        ctx.check(
            "fixed display pod is inlined as body visuals (no display part)",
            "display_screen" in {v.name for v in body.visuals}
            and "lcd_display" not in {p.name for p in object_model.parts},
            details=str([v.name for v in body.visuals]),
        )

    # --- Receipt printer topology. ---
    if r.receipt_printer == "hinged_printer_cover":
        cover = object_model.get_part("printer_cover")
        jc = object_model.get_articulation("body_to_printer_cover")
        with ctx.pose({jc: 0.0}):
            c0 = ctx.part_world_aabb(cover)
        with ctx.pose({jc: 1.2}):
            c1 = ctx.part_world_aabb(cover)
        ctx.check(
            "printer cover swings open upward",
            c0 is not None and c1 is not None and c1[1][2] > c0[1][2] + 0.03,
            details=f"closed={c0}, open={c1}",
        )
    else:
        ctx.check(
            "open paper wells are inlined body visuals (no cover part)",
            "printer_cover" not in {p.name for p in object_model.parts}
            and any(v.name.startswith("paper_roll_") for v in body.visuals),
            details=str([v.name for v in body.visuals]),
        )

    # --- Bill clips lift when present. ---
    if r.drawer_till == "bill_and_coin_till_with_clips":
        clips = [p for p in object_model.parts if p.name.startswith("bill_clip_")]
        ctx.check(
            "one hinged bill clip per bill compartment",
            len(clips) == r.n_bill,
            details=f"expected {r.n_bill}, found {len(clips)}",
        )
        jclip = object_model.get_articulation("bill_clip_0_hinge")
        with ctx.pose({jclip: 0.0}):
            b0 = ctx.part_world_aabb("bill_clip_0")
        with ctx.pose({jclip: jclip.motion_limits.upper}):
            b1 = ctx.part_world_aabb("bill_clip_0")
        ctx.check(
            "bill clip lifts upward",
            b0 is not None and b1 is not None and b1[1][2] > b0[1][2] + 0.015,
            details=f"rest={b0}, lifted={b1}",
        )

    return ctx.report()


__all__ = (
    "CashRegisterConfig",
    "ResolvedCashRegisterConfig",
    "build_cash_register",
    "build_seeded_cash_register",
    "config_from_seed",
    "resolve_config",
    "run_cash_register_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
)
