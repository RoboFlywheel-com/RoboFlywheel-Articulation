# SPDX-License-Identifier: Apache-2.0

"""Dual independent finger chains — modular procedural template.

Canonical spec: ``articraft_template_authoring/specs_modular_v1/dual_independent_finger_chains.md``

One palm chassis + exactly two uncoupled 2-phalanx REVOLUTE chains.
Left axes mirror right (-Z / +Z per ``rec_dual_independent_finger_chains_0001``).
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
    MatingContract,
    MotionLimits,
    Origin,
    TestContext,
    TestReport,
)

__modular__ = True

PHALANX_COUNT = 2
CHAIN_COUNT = 2

PalmStyle = Literal[
    "compact_gripper_palm",
    "mounting_plate_palm",
    "pedestal_palm",
    "tray_backplate_palm",
]
LinkProfile = Literal[
    "rounded_box_phalanx",
    "barrel_hinge_phalanx",
    "sideplate_phalanx",
    "tapered_box_phalanx",
]
MaterialStyle = Literal[
    "palm_gray_aluminum",
    "dark_polymer",
    "anodized_blue",
    "warm_bronze",
]
FingerSpacing = Literal["narrow", "standard", "wide"]

PALM_STYLES: tuple[PalmStyle, ...] = (
    "compact_gripper_palm",
    "mounting_plate_palm",
    "pedestal_palm",
    "tray_backplate_palm",
)
LINK_PROFILES: tuple[LinkProfile, ...] = (
    "rounded_box_phalanx",
    "barrel_hinge_phalanx",
    "sideplate_phalanx",
    "tapered_box_phalanx",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "palm_gray_aluminum",
    "dark_polymer",
    "anodized_blue",
    "warm_bronze",
)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "palm_gray_aluminum": {
        "palm": (0.24, 0.26, 0.30, 1.0),
        "palm_dark": (0.12, 0.13, 0.15, 1.0),
        "link": (0.72, 0.75, 0.79, 1.0),
        "joint": (0.56, 0.58, 0.60, 1.0),
        "pad": (0.18, 0.19, 0.20, 1.0),
        "accent": (0.10, 0.32, 0.58, 1.0),
    },
    "dark_polymer": {
        "palm": (0.10, 0.11, 0.12, 1.0),
        "palm_dark": (0.04, 0.04, 0.05, 1.0),
        "link": (0.28, 0.30, 0.31, 1.0),
        "joint": (0.46, 0.47, 0.48, 1.0),
        "pad": (0.06, 0.06, 0.07, 1.0),
        "accent": (0.82, 0.44, 0.10, 1.0),
    },
    "anodized_blue": {
        "palm": (0.14, 0.22, 0.34, 1.0),
        "palm_dark": (0.06, 0.10, 0.16, 1.0),
        "link": (0.22, 0.38, 0.58, 1.0),
        "joint": (0.60, 0.62, 0.64, 1.0),
        "pad": (0.08, 0.10, 0.12, 1.0),
        "accent": (0.90, 0.58, 0.14, 1.0),
    },
    "warm_bronze": {
        "palm": (0.36, 0.28, 0.18, 1.0),
        "palm_dark": (0.16, 0.12, 0.08, 1.0),
        "link": (0.58, 0.46, 0.30, 1.0),
        "joint": (0.74, 0.60, 0.36, 1.0),
        "pad": (0.14, 0.11, 0.08, 1.0),
        "accent": (0.24, 0.36, 0.48, 1.0),
    },
}

_SPACING_SCALE: dict[FingerSpacing, float] = {
    "narrow": 0.82,
    "standard": 1.0,
    "wide": 1.22,
}

# The two finger chains are UNCOUPLED revolute stacks that both curl toward the
# centreline (left axis -Z, right axis +Z). The motion-QC sampler drives all
# four joints independently, so the worst inter-chain case is BOTH chains fully
# curled inward at once — that is where the two distal links meet at the centre
# and 穿模. Derived limits below guarantee two things for every sampled pose:
#   * per-chain fold budget: a single finger's cumulative curl (proximal +
#     distal) stays under `_FINGER_FOLD_BUDGET` — the folding_arm_chain
#     `_safe_fold_limit` pattern applied per chain so a finger never over-curls
#     back onto its own palm/root;
#   * inter-chain tip gap: at the worst (both-full-curl) pose the two distal
#     links keep at least `_TIP_GAP_MIN` between them.
# Both are enforced by a single symmetric down-scale of the two per-joint limits
# (Contract 3c single source), solved in `resolve_config`.
_TIP_GAP_MIN = 0.008
_FINGER_FOLD_BUDGET = 1.45


def _distal_combined_h(distal_height: float) -> float:
    """Hub+neck stack height of a distal phalanx (matches ``_build_phalanx``)."""
    hub_h = max(0.004, distal_height * 0.55)
    neck_h = max(0.004, distal_height * 0.14)
    return hub_h + neck_h


def _distal_inward_reach(
    prox_limit: float,
    dist_limit: float,
    *,
    proximal_length: float,
    distal_width: float,
    distal_height: float,
    distal_length: float,
) -> float:
    """Conservative max inward (toward-centre) reach of one chain's distal link.

    Measured in +X from the chain root at curl ``(prox_limit, dist_limit)``. The
    proximal link swings the distal joint inward by ``proximal_length*sin(θp)``;
    the distal link then reaches a further ``tip_y*sin(θp+θd)`` at its tip plus a
    half-width ``hw*cos(θp+θd)`` at the inner corner. ``tip_y`` and ``hw`` take
    the largest extent across every link profile, so the estimate never
    under-states the true reach (the resulting gap is a safe lower bound).
    """
    combined_h = _distal_combined_h(distal_height)
    tip_y = combined_h + distal_length
    hw = max(0.005, distal_width * 0.6, distal_height * 0.45)
    phi = prox_limit + dist_limit
    return proximal_length * math.sin(prox_limit) + tip_y * math.sin(phi) + hw * math.cos(phi)


def _fit_curl_limits(
    prox_limit: float,
    dist_limit: float,
    *,
    root_x_offset: float,
    proximal_length: float,
    distal_width: float,
    distal_height: float,
    distal_length: float,
) -> tuple[float, float]:
    """Return per-joint curl limits that respect the fold budget AND tip gap.

    First caps the per-chain cumulative curl at ``_FINGER_FOLD_BUDGET``, then
    shrinks both limits by a single scale until the worst-case (both chains at
    full curl) inter-chain distal gap is at least ``_TIP_GAP_MIN``. Symmetric
    scaling keeps the proximal:distal ratio the config asked for.
    """
    total = prox_limit + dist_limit
    if total > _FINGER_FOLD_BUDGET:
        fold_scale = _FINGER_FOLD_BUDGET / total
        prox_limit *= fold_scale
        dist_limit *= fold_scale

    def gap(scale: float) -> float:
        reach = _distal_inward_reach(
            prox_limit * scale,
            dist_limit * scale,
            proximal_length=proximal_length,
            distal_width=distal_width,
            distal_height=distal_height,
            distal_length=distal_length,
        )
        return 2.0 * (root_x_offset - reach)

    if gap(1.0) >= _TIP_GAP_MIN:
        return prox_limit, dist_limit
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) * 0.5
        if gap(mid) >= _TIP_GAP_MIN:
            lo = mid
        else:
            hi = mid
    return prox_limit * lo, dist_limit * lo


@dataclass(frozen=True)
class DualIndependentFingerChainsConfig:
    palm_style: PalmStyle | None = None
    link_profile: LinkProfile | None = None
    material_style: MaterialStyle = "palm_gray_aluminum"
    finger_spacing: FingerSpacing = "standard"
    palm_width: float = 0.082
    palm_depth: float = 0.032
    palm_height: float = 0.024
    root_y_offset: float = 0.006
    proximal_width: float = 0.010
    proximal_length: float = 0.036
    proximal_height: float = 0.010
    distal_width: float = 0.008
    distal_length: float = 0.022
    distal_height: float = 0.009
    proximal_limit: float = 0.42
    distal_limit: float = 0.34
    name: str = "dual_independent_finger_chains"


@dataclass(frozen=True)
class ChainMount:
    side: Literal["left", "right"]
    root_x: float
    root_y: float
    root_z: float
    axis: tuple[float, float, float]


@dataclass(frozen=True)
class ResolvedDualIndependentFingerChainsConfig:
    palm_style: PalmStyle
    link_profile: LinkProfile
    material_style: MaterialStyle
    finger_spacing: FingerSpacing
    palm_width: float
    palm_depth: float
    palm_height: float
    root_y_offset: float
    root_x_offset: float
    proximal_width: float
    proximal_length: float
    proximal_height: float
    distal_width: float
    distal_length: float
    distal_height: float
    proximal_limit: float
    distal_limit: float
    mounts: tuple[ChainMount, ...]
    name: str


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _choice(value: str | None, allowed: tuple[str, ...], fallback: str, field: str) -> str:
    if value is None:
        return fallback
    if value not in allowed:
        raise ValueError(f"Unsupported {field}: {value}")
    return value


def config_from_seed(seed: int) -> DualIndependentFingerChainsConfig:
    if seed == 0:
        return DualIndependentFingerChainsConfig()

    rng = random.Random(seed)
    palm_style: PalmStyle = rng.choice(PALM_STYLES)
    link_profile: LinkProfile = rng.choice(LINK_PROFILES)
    material_style: MaterialStyle = rng.choice(MATERIAL_STYLES)
    finger_spacing: FingerSpacing = rng.choice(("narrow", "standard", "wide"))

    compact = palm_style == "compact_gripper_palm"
    palm_width = round(rng.uniform(0.068, 0.098) if compact else rng.uniform(0.090, 0.140), 4)
    palm_depth = round(rng.uniform(0.026, 0.040) if compact else rng.uniform(0.034, 0.058), 4)
    palm_height = round(rng.uniform(0.018, 0.030) if compact else rng.uniform(0.020, 0.038), 4)

    return DualIndependentFingerChainsConfig(
        palm_style=palm_style,
        link_profile=link_profile,
        material_style=material_style,
        finger_spacing=finger_spacing,
        palm_width=palm_width,
        palm_depth=palm_depth,
        palm_height=palm_height,
        root_y_offset=round(rng.uniform(0.004, 0.012), 4),
        proximal_width=round(rng.uniform(0.008, 0.014), 4),
        proximal_length=round(rng.uniform(0.028, 0.048), 4),
        proximal_height=round(rng.uniform(0.008, 0.014), 4),
        distal_width=round(rng.uniform(0.006, 0.012), 4),
        distal_length=round(rng.uniform(0.016, 0.030), 4),
        distal_height=round(rng.uniform(0.006, 0.012), 4),
        proximal_limit=round(rng.uniform(0.34, 0.52), 4),
        distal_limit=round(rng.uniform(0.26, 0.42), 4),
        name=f"seeded_dual_independent_finger_chains_{seed}",
    )


def resolve_config(
    config: DualIndependentFingerChainsConfig,
) -> ResolvedDualIndependentFingerChainsConfig:
    palm_style = _choice(config.palm_style, PALM_STYLES, "compact_gripper_palm", "palm_style")
    link_profile = _choice(
        config.link_profile, LINK_PROFILES, "rounded_box_phalanx", "link_profile"
    )
    material_style = _choice(
        config.material_style, MATERIAL_STYLES, "palm_gray_aluminum", "material_style"
    )
    if config.finger_spacing not in _SPACING_SCALE:
        raise ValueError(f"Unsupported finger_spacing: {config.finger_spacing}")

    palm_width = _clamp(config.palm_width, 0.060, 0.150)
    palm_depth = _clamp(config.palm_depth, 0.022, 0.065)
    palm_height = _clamp(config.palm_height, 0.016, 0.042)
    root_y_offset = _clamp(config.root_y_offset, 0.002, 0.016)
    proximal_width = _clamp(config.proximal_width, 0.006, 0.018)
    proximal_length = _clamp(config.proximal_length, 0.022, 0.058)
    proximal_height = _clamp(config.proximal_height, 0.006, 0.018)
    distal_width = _clamp(config.distal_width, 0.005, 0.016)
    distal_length = _clamp(config.distal_length, 0.012, 0.038)
    distal_height = _clamp(config.distal_height, 0.005, 0.016)
    proximal_limit = _clamp(config.proximal_limit, 0.28, 0.58)
    distal_limit = _clamp(config.distal_limit, 0.20, 0.48)

    anchor_spacing = 0.034
    root_x_offset = _clamp(anchor_spacing * _SPACING_SCALE[config.finger_spacing], 0.024, 0.052)

    # Fold-budget + inter-chain tip-gap derivation (single source, Contract 3c).
    proximal_limit, distal_limit = _fit_curl_limits(
        proximal_limit,
        distal_limit,
        root_x_offset=root_x_offset,
        proximal_length=proximal_length,
        distal_width=distal_width,
        distal_height=distal_height,
        distal_length=distal_length,
    )

    root_z = palm_height * 0.5 + proximal_height * 0.5
    mounts = (
        ChainMount("left", -root_x_offset, root_y_offset, root_z, (0.0, 0.0, -1.0)),
        ChainMount("right", root_x_offset, root_y_offset, root_z, (0.0, 0.0, 1.0)),
    )
    return ResolvedDualIndependentFingerChainsConfig(
        palm_style=palm_style,
        link_profile=link_profile,
        material_style=material_style,
        finger_spacing=config.finger_spacing,
        palm_width=palm_width,
        palm_depth=palm_depth,
        palm_height=palm_height,
        root_y_offset=root_y_offset,
        root_x_offset=root_x_offset,
        proximal_width=proximal_width,
        proximal_length=proximal_length,
        proximal_height=proximal_height,
        distal_width=distal_width,
        distal_length=distal_length,
        distal_height=distal_height,
        proximal_limit=proximal_limit,
        distal_limit=distal_limit,
        mounts=mounts,
        name=config.name or "dual_independent_finger_chains",
    )


def with_overrides(
    config: DualIndependentFingerChainsConfig, **kwargs: object
) -> DualIndependentFingerChainsConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: DualIndependentFingerChainsConfig | ResolvedDualIndependentFingerChainsConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedDualIndependentFingerChainsConfig)
        else resolve_config(config)
    )
    return (
        ("palm_chassis", r.palm_style),
        ("finger_chain_multiplicity", f"{CHAIN_COUNT}_independent_chains"),
        ("phalanx_multiplicity", f"{PHALANX_COUNT}_phalanxes_per_chain"),
        ("link_profile", r.link_profile),
        ("material_palette", r.material_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _mat(model: ArticulatedObject, r: ResolvedDualIndependentFingerChainsConfig, key: str):
    return model.material(f"dual_finger_{key}", rgba=PALETTES[r.material_style][key])


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="metal.aluminum_bare")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.aluminum_bare",
    )


def _build_palm(
    model: ArticulatedObject,
    r: ResolvedDualIndependentFingerChainsConfig,
    mats: dict[str, object],
):
    palm = model.part("palm")
    px, py, pz = r.palm_width, r.palm_depth, r.palm_height
    _box(palm, (px, py, pz), (0.0, 0.0, 0.0), mats["palm"], "palm_body")
    _box(
        palm,
        (px * 0.88, py * 0.72, pz * 0.55),
        (0.0, 0.0, -pz * 0.12),
        mats["palm_dark"],
        "palm_core",
    )

    if r.palm_style == "mounting_plate_palm":
        _box(
            palm,
            (px * 1.08, py * 1.12, pz * 0.28),
            (0.0, 0.0, -pz * 0.34),
            mats["palm_dark"],
            "mounting_plate",
        )
        for k, (ox, oy) in enumerate(
            (
                (px * 0.40, py * 0.42),
                (-px * 0.40, py * 0.42),
                (px * 0.40, -py * 0.42),
                (-px * 0.40, -py * 0.42),
            )
        ):
            _cyl(palm, 0.004, pz * 0.42, (ox, oy, -pz * 0.18), mats["accent"], f"mount_bolt_{k}")
    elif r.palm_style == "pedestal_palm":
        _cyl(
            palm, px * 0.28, pz * 1.35, (0.0, 0.0, -pz * 0.78), mats["palm_dark"], "pedestal_column"
        )
    elif r.palm_style == "tray_backplate_palm":
        _box(
            palm,
            (px * 0.92, py * 0.18, pz * 0.42),
            (0.0, -py * 0.44, 0.0),
            mats["palm_dark"],
            "rear_tray_lip",
        )

    for mount in r.mounts:
        _build_root_socket(palm, r, mount, mats)
    return palm


def _build_root_socket(
    palm,
    r: ResolvedDualIndependentFingerChainsConfig,
    mount: ChainMount,
    mats: dict[str, object],
) -> None:
    tag = mount.side
    x, y, z = mount.root_x, mount.root_y, mount.root_z
    socket_size = (
        max(0.012, r.proximal_width * 1.15),
        max(0.006, r.proximal_height * 0.55),
        max(0.012, r.proximal_height * 1.15),
    )
    _box(palm, socket_size, (x, y - socket_size[1] * 0.5, z), mats["joint"], f"{tag}_root_socket")
    _cyl(
        palm,
        max(0.004, r.proximal_height * 0.45),
        socket_size[0] * 1.05,
        (x, y, z),
        mats["joint"],
        f"{tag}_root_pin",
        (0.0, math.pi / 2.0, 0.0),
    )


def _build_phalanx(
    model: ArticulatedObject,
    *,
    name: str,
    width: float,
    length: float,
    height: float,
    profile: LinkProfile,
    mats: dict[str, object],
    is_distal: bool,
) -> object:
    part = model.part(name)
    hub_h = max(0.004, height * 0.55)
    neck_h = max(0.004, height * 0.14)
    combined_h = hub_h + neck_h
    hub_size = (max(0.010, width * 1.15), combined_h, max(0.010, height * 1.15))
    _box(part, hub_size, (0.0, combined_h * 0.5, 0.0), mats["joint"], "pivot_hub")
    _box(
        part,
        (max(0.008, width * 0.94), 0.006, max(0.008, height * 0.94)),
        (0.0, combined_h + 0.003, 0.0),
        mats["link"],
        "hub_seam",
    )

    body_cy = combined_h + length * 0.5
    if profile == "rounded_box_phalanx":
        _box(part, (width, length, height), (0.0, body_cy, 0.0), mats["link"], "phalanx_body")
        _cyl(
            part,
            min(width, height) * 0.34,
            width * 1.05,
            (0.0, combined_h * 0.52, 0.0),
            mats["joint"],
            "root_barrel",
            (0.0, math.pi / 2.0, 0.0),
        )
    elif profile == "barrel_hinge_phalanx":
        _cyl(
            part,
            height * 0.42,
            length * 0.92,
            (0.0, body_cy, 0.0),
            mats["link"],
            "phalanx_barrel",
            (math.pi / 2.0, 0.0, 0.0),
        )
        _box(
            part,
            (width * 0.55, length * 0.72, height * 0.55),
            (0.0, body_cy, 0.0),
            mats["palm_dark"],
            "phalanx_web",
        )
    elif profile == "sideplate_phalanx":
        plate_t = max(0.003, width * 0.28)
        _box(
            part,
            (plate_t, length, height * 0.92),
            (width * 0.34, body_cy, 0.0),
            mats["link"],
            "side_plate_left",
        )
        _box(
            part,
            (plate_t, length, height * 0.92),
            (-width * 0.34, body_cy, 0.0),
            mats["link"],
            "side_plate_right",
        )
        _cyl(
            part,
            height * 0.36,
            length * 0.86,
            (0.0, body_cy, 0.0),
            mats["joint"],
            "sideplate_spine",
            (math.pi / 2.0, 0.0, 0.0),
        )
    else:
        taper = 0.82 if is_distal else 0.90
        _box(
            part,
            (width, length * 0.92, height),
            (0.0, body_cy - length * 0.04, 0.0),
            mats["link"],
            "phalanx_upper",
        )
        _box(
            part,
            (width * taper, length * 0.72, height * taper),
            (0.0, body_cy + length * 0.10, 0.0),
            mats["link"],
            "phalanx_lower",
        )

    tip_y = combined_h + length
    tip_w = width * (0.88 if is_distal else 0.94)
    _box(
        part,
        (tip_w, max(0.004, length * 0.10), height * 0.72),
        (0.0, tip_y - length * 0.05, 0.0),
        mats["pad"],
        "tip_pad",
    )
    return part


def build_dual_independent_finger_chains(
    config: DualIndependentFingerChainsConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    cfg = config or DualIndependentFingerChainsConfig()
    r = resolve_config(cfg)
    model = ArticulatedObject(name=r.name, assets=assets)
    model.meta["slot_choices"] = slot_choices_for_config(r)

    mats = {
        key: _mat(model, r, key) for key in ("palm", "palm_dark", "link", "joint", "pad", "accent")
    }
    palm = _build_palm(model, r, mats)

    left_prox = _build_phalanx(
        model,
        name="left_proximal",
        width=r.proximal_width,
        length=r.proximal_length,
        height=r.proximal_height,
        profile=r.link_profile,
        mats=mats,
        is_distal=False,
    )
    left_dist = _build_phalanx(
        model,
        name="left_distal",
        width=r.distal_width,
        length=r.distal_length,
        height=r.distal_height,
        profile=r.link_profile,
        mats=mats,
        is_distal=True,
    )
    right_prox = _build_phalanx(
        model,
        name="right_proximal",
        width=r.proximal_width,
        length=r.proximal_length,
        height=r.proximal_height,
        profile=r.link_profile,
        mats=mats,
        is_distal=False,
    )
    right_dist = _build_phalanx(
        model,
        name="right_distal",
        width=r.distal_width,
        length=r.distal_length,
        height=r.distal_height,
        profile=r.link_profile,
        mats=mats,
        is_distal=True,
    )

    prox_limits = MotionLimits(lower=0.0, upper=r.proximal_limit, effort=3.0, velocity=3.0)
    dist_limits = MotionLimits(lower=0.0, upper=r.distal_limit, effort=2.0, velocity=3.0)
    mating = MatingContract(
        parent_face_geometry="root_socket",
        parent_face_side="positive_y",
        child_face_geometry="pivot_hub",
        child_face_side="negative_y",
        contact_tol=0.002,
    )

    left_mount, right_mount = r.mounts
    model.articulation(
        "palm_to_left_proximal",
        ArticulationType.REVOLUTE,
        parent=palm,
        child=left_prox,
        origin=Origin(xyz=(left_mount.root_x, left_mount.root_y, left_mount.root_z)),
        axis=left_mount.axis,
        motion_limits=prox_limits,
        mating=replace(mating, parent_face_geometry="left_root_socket"),
    )
    model.articulation(
        "left_proximal_to_left_distal",
        ArticulationType.REVOLUTE,
        parent=left_prox,
        child=left_dist,
        origin=Origin(xyz=(0.0, r.proximal_length, 0.0)),
        axis=left_mount.axis,
        motion_limits=dist_limits,
    )
    model.articulation(
        "palm_to_right_proximal",
        ArticulationType.REVOLUTE,
        parent=palm,
        child=right_prox,
        origin=Origin(xyz=(right_mount.root_x, right_mount.root_y, right_mount.root_z)),
        axis=right_mount.axis,
        motion_limits=prox_limits,
        mating=replace(mating, parent_face_geometry="right_root_socket"),
    )
    model.articulation(
        "right_proximal_to_right_distal",
        ArticulationType.REVOLUTE,
        parent=right_prox,
        child=right_dist,
        origin=Origin(xyz=(0.0, r.proximal_length, 0.0)),
        axis=right_mount.axis,
        motion_limits=dist_limits,
    )
    return model


def build_seeded_dual_independent_finger_chains(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_dual_independent_finger_chains(config_from_seed(seed), assets=assets)


def _allow_expected_overlaps(ctx: TestContext, model: ArticulatedObject) -> None:
    palm = model.get_part("palm")
    for side in ("left", "right"):
        prox = model.get_part(f"{side}_proximal")
        dist = model.get_part(f"{side}_distal")
        ctx.allow_overlap(palm, prox, reason="proximal root hub is seated on the palm socket")
        ctx.allow_overlap(prox, dist, reason="distal hub is seated on the proximal knuckle")


def run_dual_independent_finger_chains_tests(
    object_model: ArticulatedObject,
    config: DualIndependentFingerChainsConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.020)

    part_names = {part.name for part in object_model.parts}
    expected_parts = {
        "palm",
        "left_proximal",
        "left_distal",
        "right_proximal",
        "right_distal",
    }
    ctx.check(
        "identity_parts", expected_parts.issubset(part_names), details=str(sorted(part_names))
    )

    joint_names = {joint.name for joint in object_model.joints}
    for name in (
        "palm_to_left_proximal",
        "left_proximal_to_left_distal",
        "palm_to_right_proximal",
        "right_proximal_to_right_distal",
    ):
        ctx.check(f"{name}_present", name in joint_names, details=name)

    left_root = object_model.get_articulation("palm_to_left_proximal")
    right_root = object_model.get_articulation("palm_to_right_proximal")
    ctx.check(
        "left_root_axis_neg_z",
        left_root.articulation_type == ArticulationType.REVOLUTE
        and tuple(left_root.axis) == (0.0, 0.0, -1.0),
        details=f"type={left_root.articulation_type}, axis={left_root.axis}",
    )
    ctx.check(
        "right_root_axis_pos_z",
        right_root.articulation_type == ArticulationType.REVOLUTE
        and tuple(right_root.axis) == (0.0, 0.0, 1.0),
        details=f"type={right_root.articulation_type}, axis={right_root.axis}",
    )

    left_mid = object_model.get_articulation("left_proximal_to_left_distal")
    right_mid = object_model.get_articulation("right_proximal_to_right_distal")
    ctx.check(
        "left_chain_axes_match",
        tuple(left_mid.axis) == tuple(left_root.axis),
        details=f"root={left_root.axis}, mid={left_mid.axis}",
    )
    ctx.check(
        "right_chain_axes_match",
        tuple(right_mid.axis) == tuple(right_root.axis),
        details=f"root={right_root.axis}, mid={right_mid.axis}",
    )

    slot_choices = dict(slot_choices_for_config(r))
    ctx.check(
        "finger_chain_multiplicity",
        slot_choices.get("finger_chain_multiplicity") == "2_independent_chains",
        details=str(slot_choices),
    )
    ctx.check(
        "phalanx_multiplicity",
        slot_choices.get("phalanx_multiplicity") == "2_phalanxes_per_chain",
        details=str(slot_choices),
    )

    left_dist = object_model.get_part("left_distal")
    rest_aabb = ctx.part_world_aabb(left_dist)
    with ctx.pose({left_root: r.proximal_limit * 0.65, left_mid: r.distal_limit * 0.55}):
        posed_aabb = ctx.part_world_aabb(left_dist)
    if rest_aabb and posed_aabb:
        rest_span = rest_aabb[1][0] - rest_aabb[0][0]
        posed_span = posed_aabb[1][0] - posed_aabb[0][0]
        ctx.check(
            "left_chain_motion_moves_distal",
            posed_span > rest_span + 0.004,
            details=f"rest={rest_span:.4f}, posed={posed_span:.4f}",
        )

    # Lock the inter-chain invariant: at the worst (both chains fully curled
    # inward) pose the two distal links must not 穿模 (this is the exact pose the
    # motion-QC sampler drives). The derived limits guarantee an analytic gap of
    # at least `_TIP_GAP_MIN`; verify both the closed form and the real FK pose.
    reach = _distal_inward_reach(
        r.proximal_limit,
        r.distal_limit,
        proximal_length=r.proximal_length,
        distal_width=r.distal_width,
        distal_height=r.distal_height,
        distal_length=r.distal_length,
    )
    interchain_gap = 2.0 * (r.root_x_offset - reach)
    ctx.check(
        "interchain_tip_gap_respected",
        interchain_gap >= _TIP_GAP_MIN - 1e-6,
        details=f"gap={interchain_gap:.4f} min={_TIP_GAP_MIN:.4f}",
    )
    full_curl = {
        left_root: r.proximal_limit,
        object_model.get_articulation("left_proximal_to_left_distal"): r.distal_limit,
        right_root: r.proximal_limit,
        object_model.get_articulation("right_proximal_to_right_distal"): r.distal_limit,
    }
    with ctx.pose(full_curl):
        ctx.fail_if_parts_overlap_in_current_pose(name="no_interchain_overlap_at_full_curl")

    return ctx.report()


__all__ = (
    "DualIndependentFingerChainsConfig",
    "ResolvedDualIndependentFingerChainsConfig",
    "build_dual_independent_finger_chains",
    "build_seeded_dual_independent_finger_chains",
    "config_from_seed",
    "resolve_config",
    "run_dual_independent_finger_chains_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
