# SPDX-License-Identifier: Apache-2.0

"""Modular procedural template for one or more fingerlike phalanx chains."""

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

BaseStyle = Literal[
    "metacarpal_socket_base",
    "palm_plate_base",
    "robotic_knuckle_block",
    "bracelet_cuff_mount",
]
PhalanxProfile = Literal[
    "rounded_box_phalanx",
    "barrel_hinge_phalanx",
    "sideplate_phalanx",
    "tapered_pad_phalanx",
]
TerminalStyle = Literal["rounded_fingertip", "flat_rubber_pad", "pincher_claw_tip"]
MaterialStyle = Literal["warm_polymer", "brushed_mechanism", "medical_white", "dark_robotic"]

BASE_STYLES: tuple[BaseStyle, ...] = (
    "metacarpal_socket_base",
    "palm_plate_base",
    "robotic_knuckle_block",
    "bracelet_cuff_mount",
)
PHALANX_PROFILES: tuple[PhalanxProfile, ...] = (
    "rounded_box_phalanx",
    "barrel_hinge_phalanx",
    "sideplate_phalanx",
    "tapered_pad_phalanx",
)
CHAIN_COUNTS = (1, 2, 3)
PHALANX_COUNTS = (2, 3, 4, 5)
TERMINAL_STYLES: tuple[TerminalStyle, ...] = (
    "rounded_fingertip",
    "flat_rubber_pad",
    "pincher_claw_tip",
)
MATERIAL_STYLES: tuple[MaterialStyle, ...] = (
    "warm_polymer",
    "brushed_mechanism",
    "medical_white",
    "dark_robotic",
)

PALETTES: dict[MaterialStyle, dict[str, tuple[float, float, float, float]]] = {
    "warm_polymer": {
        "base": (0.63, 0.47, 0.38, 1.0),
        "base_dark": (0.35, 0.26, 0.22, 1.0),
        "link": (0.72, 0.56, 0.45, 1.0),
        "joint": (0.16, 0.16, 0.17, 1.0),
        "pad": (0.10, 0.08, 0.075, 1.0),
        "accent": (0.86, 0.72, 0.48, 1.0),
    },
    "brushed_mechanism": {
        "base": (0.48, 0.50, 0.49, 1.0),
        "base_dark": (0.22, 0.23, 0.24, 1.0),
        "link": (0.62, 0.64, 0.62, 1.0),
        "joint": (0.08, 0.09, 0.10, 1.0),
        "pad": (0.03, 0.03, 0.032, 1.0),
        "accent": (0.18, 0.30, 0.42, 1.0),
    },
    "medical_white": {
        "base": (0.86, 0.86, 0.82, 1.0),
        "base_dark": (0.48, 0.50, 0.50, 1.0),
        "link": (0.94, 0.93, 0.88, 1.0),
        "joint": (0.20, 0.22, 0.23, 1.0),
        "pad": (0.14, 0.16, 0.17, 1.0),
        "accent": (0.15, 0.46, 0.56, 1.0),
    },
    "dark_robotic": {
        "base": (0.10, 0.11, 0.12, 1.0),
        "base_dark": (0.025, 0.028, 0.030, 1.0),
        "link": (0.19, 0.20, 0.21, 1.0),
        "joint": (0.62, 0.57, 0.46, 1.0),
        "pad": (0.012, 0.012, 0.014, 1.0),
        "accent": (0.70, 0.36, 0.20, 1.0),
    },
}


@dataclass(frozen=True)
class FingerlikePhalanxChainConfig:
    base_style: BaseStyle | None = None
    phalanx_profile: PhalanxProfile | None = None
    chain_count: int | None = None
    phalanx_count: int | None = None
    terminal_style: TerminalStyle | None = None
    material_style: MaterialStyle = "warm_polymer"
    base_width: float = 0.108
    base_depth: float = 0.070
    base_height: float = 0.038
    proximal_length: float = 0.076
    proximal_width: float = 0.032
    proximal_height: float = 0.026
    length_taper: float = 0.82
    width_taper: float = 0.88
    curl_upper: float = 1.08
    name: str = "fingerlike_phalanx_chain"


@dataclass(frozen=True)
class PhalanxSpec:
    index: int
    name: str
    length: float
    width: float
    height: float
    hinge_depth: float
    distal_depth: float
    upper_limit: float


@dataclass(frozen=True)
class ChainSpec:
    index: int
    root_origin: tuple[float, float, float]


@dataclass(frozen=True)
class ResolvedFingerlikePhalanxChainConfig:
    base_style: BaseStyle
    phalanx_profile: PhalanxProfile
    chain_count: int
    phalanx_count: int
    terminal_style: TerminalStyle
    material_style: MaterialStyle
    base_width: float
    base_depth: float
    base_height: float
    chains: tuple[ChainSpec, ...]
    root_axis: tuple[float, float, float]
    phalanxes: tuple[PhalanxSpec, ...]
    curl_upper: float
    name: str


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _pick(value, choices):
    return value if value in choices else choices[0]


def config_from_seed(seed: int) -> FingerlikePhalanxChainConfig:
    rng = random.Random(seed)
    return FingerlikePhalanxChainConfig(
        base_style=rng.choice(BASE_STYLES),
        phalanx_profile=rng.choice(PHALANX_PROFILES),
        chain_count=rng.choice(CHAIN_COUNTS),
        phalanx_count=rng.choice(PHALANX_COUNTS),
        terminal_style=rng.choice(TERMINAL_STYLES),
        material_style=rng.choice(MATERIAL_STYLES),
        base_width=rng.uniform(0.098, 0.126),
        base_depth=rng.uniform(0.062, 0.082),
        base_height=rng.uniform(0.033, 0.046),
        proximal_length=rng.uniform(0.066, 0.088),
        proximal_width=rng.uniform(0.028, 0.038),
        proximal_height=rng.uniform(0.022, 0.031),
        length_taper=rng.uniform(0.76, 0.88),
        width_taper=rng.uniform(0.84, 0.92),
        curl_upper=rng.uniform(0.88, 1.26),
        name=f"seeded_fingerlike_phalanx_chain_{seed}",
    )


def resolve_config(
    config: FingerlikePhalanxChainConfig | None = None,
) -> ResolvedFingerlikePhalanxChainConfig:
    cfg = config or FingerlikePhalanxChainConfig()
    base_style = _pick(cfg.base_style, BASE_STYLES)
    phalanx_profile = _pick(cfg.phalanx_profile, PHALANX_PROFILES)
    terminal_style = _pick(cfg.terminal_style, TERMINAL_STYLES)
    material_style = _pick(cfg.material_style, MATERIAL_STYLES)
    chain_count = int(cfg.chain_count or 1)
    chain_count = max(min(chain_count, max(CHAIN_COUNTS)), min(CHAIN_COUNTS))
    if chain_count not in CHAIN_COUNTS:
        chain_count = min(CHAIN_COUNTS, key=lambda item: abs(item - chain_count))
    phalanx_count = int(cfg.phalanx_count or 3)
    phalanx_count = max(min(phalanx_count, max(PHALANX_COUNTS)), min(PHALANX_COUNTS))
    if phalanx_count not in PHALANX_COUNTS:
        phalanx_count = min(PHALANX_COUNTS, key=lambda item: abs(item - phalanx_count))

    base_width = _clamp(cfg.base_width, 0.084, 0.180)
    base_depth = _clamp(cfg.base_depth, 0.052, 0.096)
    base_height = _clamp(cfg.base_height, 0.028, 0.054)
    proximal_length = _clamp(cfg.proximal_length, 0.054, 0.102)
    proximal_width = _clamp(cfg.proximal_width, 0.022, 0.046)
    proximal_height = _clamp(cfg.proximal_height, 0.018, 0.036)
    length_taper = _clamp(cfg.length_taper, 0.72, 0.92)
    width_taper = _clamp(cfg.width_taper, 0.80, 0.95)
    curl_upper = _clamp(cfg.curl_upper, 0.72, 1.34)

    phalanxes: list[PhalanxSpec] = []
    for index in range(phalanx_count):
        length = max(0.040, proximal_length * (length_taper**index))
        width = max(0.017, proximal_width * (width_taper**index))
        height = max(0.015, proximal_height * (0.90**index))
        hinge_depth = max(0.010, height * 0.70)
        distal_depth = max(0.008, height * 0.48)
        upper_limit = curl_upper * (1.00 - min(index, 2) * 0.16)
        phalanxes.append(
            PhalanxSpec(
                index=index,
                name=f"phalanx_{index}",
                length=length,
                width=width,
                height=height,
                hinge_depth=hinge_depth,
                distal_depth=distal_depth,
                upper_limit=upper_limit,
            )
        )

    socket_depth = max(0.014, proximal_height * 0.62)
    station_spacing = max(proximal_width * 2.15, 0.060)
    base_width = max(base_width, station_spacing * max(0, chain_count - 1) + proximal_width * 3.20)
    root_y = base_depth * 0.5 + socket_depth
    root_z = base_height * 0.16
    center_offset = (chain_count - 1) * 0.5
    chains = tuple(
        ChainSpec(
            index=index,
            root_origin=((index - center_offset) * station_spacing, root_y, root_z),
        )
        for index in range(chain_count)
    )
    return ResolvedFingerlikePhalanxChainConfig(
        base_style=base_style,
        phalanx_profile=phalanx_profile,
        chain_count=chain_count,
        phalanx_count=phalanx_count,
        terminal_style=terminal_style,
        material_style=material_style,
        base_width=base_width,
        base_depth=base_depth,
        base_height=base_height,
        chains=chains,
        root_axis=(1.0, 0.0, 0.0),
        phalanxes=tuple(phalanxes),
        curl_upper=curl_upper,
        name=cfg.name or "fingerlike_phalanx_chain",
    )


def with_overrides(
    config: FingerlikePhalanxChainConfig, **kwargs: object
) -> FingerlikePhalanxChainConfig:
    return replace(config, **kwargs)


def slot_choices_for_config(
    config: FingerlikePhalanxChainConfig | ResolvedFingerlikePhalanxChainConfig,
) -> tuple[tuple[str, str], ...]:
    r = (
        config
        if isinstance(config, ResolvedFingerlikePhalanxChainConfig)
        else resolve_config(config)
    )
    chain_label = (
        "1_fingerlike_chain" if r.chain_count == 1 else f"{r.chain_count}_fingerlike_chains"
    )
    return (
        ("base", r.base_style),
        ("chain_multiplicity", chain_label),
        ("phalanx_multiplicity", f"{r.phalanx_count}_phalanxes"),
        ("phalanx_profile", r.phalanx_profile),
        ("terminal", r.terminal_style),
        ("material_palette", r.material_style),
    )


def slot_choices_for_seed(seed: int) -> tuple[tuple[str, str], ...]:
    return slot_choices_for_config(config_from_seed(seed))


def _mat(model: ArticulatedObject, r: ResolvedFingerlikePhalanxChainConfig, key: str):
    return model.material(f"fingerlike_{key}", rgba=PALETTES[r.material_style][key])


def _box(part, size, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(Box(size), origin=Origin(xyz=xyz, rpy=rpy), material=material, name=name, material_class_id="plastic.opaque_glossy_molded")


def _cyl(part, radius, length, xyz, material, name, rpy=(0.0, 0.0, 0.0)) -> None:
    part.visual(
        Cylinder(radius=radius, length=length),
        origin=Origin(xyz=xyz, rpy=rpy),
        material=material,
        name=name, material_class_id="metal.blackened_gunmetal",
    )


def _part_name(
    r: ResolvedFingerlikePhalanxChainConfig, chain_index: int, phalanx_index: int
) -> str:
    if r.chain_count == 1:
        return f"phalanx_{phalanx_index}"
    return f"chain_{chain_index}_phalanx_{phalanx_index}"


def _root_socket_name(r: ResolvedFingerlikePhalanxChainConfig, chain_index: int) -> str:
    if r.chain_count == 1:
        return "root_socket"
    return f"chain_{chain_index}_root_socket"


def _build_base(model: ArticulatedObject, r: ResolvedFingerlikePhalanxChainConfig, mats):
    base = model.part("base")
    bw, bd, bh = r.base_width, r.base_depth, r.base_height
    prox = r.phalanxes[0]
    socket_depth = r.chains[0].root_origin[1] - bd * 0.5
    socket_size = (prox.width * 1.35, socket_depth, prox.height * 1.36)

    _box(base, (bw, bd, bh), (0.0, 0.0, 0.0), mats["base"], "base_body")
    for chain in r.chains:
        root_x, _root_y, root_z = chain.root_origin
        _box(
            base,
            socket_size,
            (root_x, bd * 0.5 + socket_depth * 0.5, root_z),
            mats["joint"],
            _root_socket_name(r, chain.index),
        )
        _cyl(
            base,
            prox.height * 0.43,
            socket_size[0] * 1.06,
            chain.root_origin,
            mats["joint"],
            f"chain_{chain.index}_root_cross_pin",
            (0.0, math.pi / 2.0, 0.0),
        )

    if r.base_style == "metacarpal_socket_base":
        _box(
            base,
            (bw * 0.72, bd * 0.30, bh * 0.48),
            (0.0, -bd * 0.34, bh * 0.16),
            mats["base_dark"],
            "rear_metacarpal_pad",
        )
    elif r.base_style == "palm_plate_base":
        _box(
            base,
            (bw * 1.18, bd * 0.62, bh * 0.24),
            (0.0, -bd * 0.18, -bh * 0.28),
            mats["base_dark"],
            "palm_flange_plate",
        )
        for index, ox in enumerate((-bw * 0.42, bw * 0.42)):
            _cyl(
                base,
                0.0032,
                bh * 0.34,
                (ox, -bd * 0.24, -bh * 0.10),
                mats["accent"],
                f"mount_bolt_{index}",
            )
    elif r.base_style == "robotic_knuckle_block":
        cheek_t = max(0.006, prox.width * 0.18)
        for chain in r.chains:
            root_x, _root_y, root_z = chain.root_origin
            for side, ox in (
                ("left", root_x - prox.width * 0.66),
                ("right", root_x + prox.width * 0.66),
            ):
                _box(
                    base,
                    (cheek_t, socket_depth * 1.18, prox.height * 1.58),
                    (ox, bd * 0.5 + socket_depth * 0.48, root_z),
                    mats["base_dark"],
                    f"chain_{chain.index}_{side}_knuckle_cheek",
                )
        _box(
            base,
            (bw * 0.52, bd * 0.34, bh * 0.34),
            (0.0, -bd * 0.26, bh * 0.31),
            mats["accent"],
            "servo_cap",
        )
    else:
        _cyl(
            base,
            bh * 0.48,
            bw * 0.82,
            (0.0, -bd * 0.22, -bh * 0.02),
            mats["base_dark"],
            "cuff_cross_tube",
            (0.0, math.pi / 2.0, 0.0),
        )
        _box(
            base,
            (bw * 0.74, bd * 0.22, bh * 0.34),
            (0.0, bd * 0.18, r.chains[0].root_origin[2]),
            mats["base"],
            "cuff_to_socket_web",
        )
    return base


def _build_terminal(part, spec: PhalanxSpec, style: TerminalStyle, mats) -> None:
    y = spec.length - spec.distal_depth * 0.5
    if style == "rounded_fingertip":
        _cyl(
            part,
            spec.height * 0.36,
            spec.width * 0.88,
            (0.0, y, 0.0),
            mats["pad"],
            "rounded_fingertip",
            (0.0, math.pi / 2.0, 0.0),
        )
    elif style == "flat_rubber_pad":
        _box(
            part,
            (spec.width * 0.92, spec.distal_depth * 1.08, spec.height * 0.70),
            (0.0, y, -spec.height * 0.06),
            mats["pad"],
            "flat_rubber_pad",
        )
    else:
        tine = max(0.004, spec.width * 0.18)
        _box(
            part,
            (tine, spec.distal_depth * 1.20, spec.height * 0.58),
            (-spec.width * 0.23, y, 0.0),
            mats["pad"],
            "left_claw_tine",
        )
        _box(
            part,
            (tine, spec.distal_depth * 1.20, spec.height * 0.58),
            (spec.width * 0.23, y, 0.0),
            mats["pad"],
            "right_claw_tine",
        )
        _box(
            part,
            (spec.width * 0.72, spec.distal_depth * 0.34, spec.height * 0.38),
            (0.0, spec.length - spec.distal_depth * 0.98, 0.0),
            mats["joint"],
            "claw_bridge",
        )


def _build_phalanx(
    model: ArticulatedObject,
    r: ResolvedFingerlikePhalanxChainConfig,
    spec: PhalanxSpec,
    mats,
    *,
    part_name: str,
    is_terminal: bool,
):
    part = model.part(part_name)
    _box(
        part,
        (spec.width * 1.12, spec.hinge_depth, spec.height * 1.12),
        (0.0, spec.hinge_depth * 0.5, 0.0),
        mats["joint"],
        "pivot_hub",
    )
    _cyl(
        part,
        spec.height * 0.38,
        spec.width * 1.20,
        (0.0, spec.hinge_depth * 0.5, 0.0),
        mats["joint"],
        "root_barrel",
        (0.0, math.pi / 2.0, 0.0),
    )

    distal_name = "terminal_socket" if is_terminal else "distal_socket"
    _box(
        part,
        (spec.width * 0.96, spec.distal_depth, spec.height * 0.86),
        (0.0, spec.length - spec.distal_depth * 0.5, 0.0),
        mats["joint"],
        distal_name,
    )

    body_len = max(0.014, spec.length - spec.hinge_depth - spec.distal_depth)
    body_y = spec.hinge_depth + body_len * 0.5
    if r.phalanx_profile == "rounded_box_phalanx":
        _box(
            part,
            (spec.width, body_len, spec.height),
            (0.0, body_y, 0.0),
            mats["link"],
            "rounded_body",
        )
        _cyl(
            part,
            spec.height * 0.32,
            spec.width * 0.98,
            (0.0, spec.length - spec.distal_depth * 0.5, 0.0),
            mats["joint"],
            "distal_barrel",
            (0.0, math.pi / 2.0, 0.0),
        )
    elif r.phalanx_profile == "barrel_hinge_phalanx":
        _cyl(
            part,
            spec.height * 0.36,
            body_len,
            (0.0, body_y, 0.0),
            mats["link"],
            "central_barrel",
            (math.pi / 2.0, 0.0, 0.0),
        )
        _box(
            part,
            (spec.width * 0.56, body_len, spec.height * 0.36),
            (0.0, body_y, -spec.height * 0.06),
            mats["base_dark"],
            "barrel_web",
        )
    elif r.phalanx_profile == "sideplate_phalanx":
        plate_t = max(0.004, spec.width * 0.18)
        _box(
            part,
            (plate_t, body_len, spec.height * 0.92),
            (-spec.width * 0.36, body_y, 0.0),
            mats["link"],
            "left_sideplate",
        )
        _box(
            part,
            (plate_t, body_len, spec.height * 0.92),
            (spec.width * 0.36, body_y, 0.0),
            mats["link"],
            "right_sideplate",
        )
        _box(
            part,
            (spec.width * 0.82, max(0.004, body_len * 0.12), spec.height * 0.32),
            (0.0, spec.hinge_depth + body_len * 0.24, 0.0),
            mats["accent"],
            "proximal_cross_web",
        )
        _box(
            part,
            (spec.width * 0.82, max(0.004, body_len * 0.12), spec.height * 0.32),
            (0.0, spec.hinge_depth + body_len * 0.70, 0.0),
            mats["accent"],
            "distal_cross_web",
        )
    else:
        _box(
            part,
            (spec.width, body_len * 0.62, spec.height),
            (0.0, spec.hinge_depth + body_len * 0.31, 0.0),
            mats["link"],
            "wide_proximal_pad",
        )
        _box(
            part,
            (spec.width * 0.78, body_len * 0.66, spec.height * 0.82),
            (0.0, spec.hinge_depth + body_len * 0.69, -spec.height * 0.02),
            mats["link"],
            "tapered_distal_pad",
        )

    if is_terminal:
        _build_terminal(part, spec, r.terminal_style, mats)
    return part


def build_fingerlike_phalanx_chain(
    config: FingerlikePhalanxChainConfig | None = None,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    r = resolve_config(config)
    model = ArticulatedObject(name=r.name, assets=assets)
    mats = {
        key: _mat(model, r, key) for key in ("base", "base_dark", "link", "joint", "pad", "accent")
    }
    base = _build_base(model, r, mats)

    for chain in r.chains:
        phalanx_parts = [
            _build_phalanx(
                model,
                r,
                spec,
                mats,
                part_name=_part_name(r, chain.index, spec.index),
                is_terminal=spec.index == r.phalanx_count - 1,
            )
            for spec in r.phalanxes
        ]

        model.articulation(
            f"chain_{chain.index}_base_to_phalanx_0",
            ArticulationType.REVOLUTE,
            parent=base,
            child=phalanx_parts[0],
            origin=Origin(xyz=chain.root_origin),
            axis=r.root_axis,
            motion_limits=MotionLimits(
                lower=0.0, upper=r.phalanxes[0].upper_limit, effort=3.2, velocity=2.4
            ),
            mating=MatingContract(
                _root_socket_name(r, chain.index),
                "positive_y",
                "pivot_hub",
                "negative_y",
                contact_tol=0.002,
            ),
        )
        for index in range(1, r.phalanx_count):
            parent_spec = r.phalanxes[index - 1]
            child_spec = r.phalanxes[index]
            model.articulation(
                f"chain_{chain.index}_phalanx_{index - 1}_to_phalanx_{index}",
                ArticulationType.REVOLUTE,
                parent=phalanx_parts[index - 1],
                child=phalanx_parts[index],
                origin=Origin(xyz=(0.0, parent_spec.length, 0.0)),
                axis=r.root_axis,
                motion_limits=MotionLimits(
                    lower=0.0, upper=child_spec.upper_limit, effort=2.4, velocity=2.6
                ),
                mating=MatingContract(
                    "distal_socket",
                    "positive_y",
                    "pivot_hub",
                    "negative_y",
                    contact_tol=0.002,
                ),
            )

    model.meta["slot_choices"] = slot_choices_for_config(r)
    return model


def build_seeded_fingerlike_phalanx_chain(
    seed: int,
    *,
    assets: AssetContext | None = None,
) -> ArticulatedObject:
    return build_fingerlike_phalanx_chain(config_from_seed(seed), assets=assets)


def _allow_expected_overlaps(
    ctx: TestContext,
    model: ArticulatedObject,
    r: ResolvedFingerlikePhalanxChainConfig,
) -> None:
    base = model.get_part("base")
    for chain in r.chains:
        ctx.allow_overlap(
            base,
            model.get_part(_part_name(r, chain.index, 0)),
            reason="root hinge pin is seated in the first phalanx hub",
        )
        for index in range(1, r.phalanx_count):
            ctx.allow_overlap(
                model.get_part(_part_name(r, chain.index, index - 1)),
                model.get_part(_part_name(r, chain.index, index)),
                reason="serial phalanx hinge hub is seated on the distal socket",
            )


def run_fingerlike_phalanx_chain_tests(
    object_model: ArticulatedObject,
    config: FingerlikePhalanxChainConfig,
) -> TestReport:
    r = resolve_config(config)
    ctx = TestContext(object_model)
    _allow_expected_overlaps(ctx, object_model, r)
    ctx.check_model_valid()
    ctx.check_mesh_assets_ready()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose()
    ctx.fail_if_articulation_origin_far_from_geometry(tol=0.016)
    ctx.fail_if_joint_mating_has_gap()

    part_names = {part.name for part in object_model.parts}
    expected = {
        "base",
        *(
            _part_name(r, chain.index, index)
            for chain in r.chains
            for index in range(r.phalanx_count)
        ),
    }
    ctx.check(
        "all_chain_parts_present", expected.issubset(part_names), details=str(sorted(part_names))
    )

    ctx.check(
        "joint_count_matches_chain_and_phalanx_multiplicity",
        len(object_model.joints) == r.chain_count * r.phalanx_count,
        details=f"expected {r.chain_count * r.phalanx_count}, got {len(object_model.joints)}",
    )
    for chain in r.chains:
        for index in range(r.phalanx_count):
            name = (
                f"chain_{chain.index}_base_to_phalanx_0"
                if index == 0
                else f"chain_{chain.index}_phalanx_{index - 1}_to_phalanx_{index}"
            )
            joint = object_model.get_articulation(name)
            ctx.check(
                f"{joint.name}_revolute",
                joint.articulation_type == ArticulationType.REVOLUTE,
                details=str(joint.articulation_type),
            )
            ctx.check(
                f"{joint.name}_axis_x",
                tuple(joint.axis) == r.root_axis,
                details=str(joint.axis),
            )
            ctx.check(
                f"{joint.name}_has_mating",
                joint.mating is not None,
                details="joint should have face contact contract",
            )
            ctx.check(
                f"{joint.name}_has_positive_range",
                joint.motion_limits.upper > 0.5,
                details=str(joint.motion_limits),
            )
            expected_child = _part_name(r, chain.index, index)
            expected_parent = "base" if index == 0 else _part_name(r, chain.index, index - 1)
            ctx.check(
                f"{joint.name}_serial_parent",
                joint.parent == expected_parent and joint.child == expected_child,
                details=f"{joint.parent}->{joint.child}",
            )

    slot_choices = dict(slot_choices_for_config(r))
    expected_chain_label = (
        "1_fingerlike_chain" if r.chain_count == 1 else f"{r.chain_count}_fingerlike_chains"
    )
    ctx.check(
        "chain_multiplicity_matches",
        slot_choices.get("chain_multiplicity") == expected_chain_label,
        details=str(slot_choices),
    )
    ctx.check(
        "phalanx_multiplicity_matches",
        slot_choices.get("phalanx_multiplicity") == f"{r.phalanx_count}_phalanxes",
        details=str(slot_choices),
    )

    distal = object_model.get_part(_part_name(r, 0, r.phalanx_count - 1))
    rest_aabb = ctx.part_world_aabb(distal)
    pose = {joint: joint.motion_limits.upper * 0.45 for joint in object_model.joints}
    with ctx.pose(pose):
        posed_aabb = ctx.part_world_aabb(distal)
    if rest_aabb and posed_aabb:
        rest_max_z = rest_aabb[1][2]
        posed_max_z = posed_aabb[1][2]
        ctx.check(
            "curl_pose_moves_terminal_phalanx",
            posed_max_z > rest_max_z + 0.006,
            details=f"rest={rest_max_z:.4f}, posed={posed_max_z:.4f}",
        )

    return ctx.report()


__all__ = (
    "FingerlikePhalanxChainConfig",
    "ResolvedFingerlikePhalanxChainConfig",
    "build_fingerlike_phalanx_chain",
    "build_seeded_fingerlike_phalanx_chain",
    "config_from_seed",
    "resolve_config",
    "run_fingerlike_phalanx_chain_tests",
    "slot_choices_for_config",
    "slot_choices_for_seed",
    "with_overrides",
)
