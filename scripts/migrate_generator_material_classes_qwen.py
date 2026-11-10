#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Annotate the remaining generator visual callsites with direct-pool PBR classes.

The workflow is intentionally one-pass: current source is inventoried, Qwen emits
one strict proposal per non-composition generator, the existing max2 builder
validates each proposal, and only a globally valid shadow tree can be written
back.  Runtime output remains one scalar ``material_class_id`` per visual.
"""

from __future__ import annotations

import argparse
import ast
import asyncio
import copy
import functools
import hashlib
import json
import os
import random
import re
import tempfile
import time
from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from dotenv import dotenv_values

from articraft.appearance.generator_annotations import (
    GENERATOR_CLASS_ANNOTATION_POLICY,
    GENERATOR_CLASS_PROPOSALS_SCHEMA,
    GENERATOR_CLASS_ROLE_ROUTED_ANNOTATION_POLICY,
    GENERATOR_CLASS_ROLE_ROUTED_ANNOTATIONS_SCHEMA,
    GENERATOR_CLASS_ROLE_ROUTING_KIND,
)
from scripts import build_generator_material_class_annotations as annotation_builder

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = REPO_ROOT.parent.resolve()
TEMPLATE_ROOT = REPO_ROOT / "agent" / "templates"
FORMAL_LIBRARY = REPO_ROOT / "pbr_material_library" / "latest.json"
CLASS_DESCRIPTIONS = REPO_ROOT / "data" / "material_classes_v1.json"
DOTENV_PATH = WORKSPACE_ROOT / "articraft_data" / ".env"

INVENTORY_SCHEMA = "articraft-generator-material-class-inventory/v2"
RUN_SCHEMA = "articraft-generator-material-class-migration-run/v2"
SHADOW_MANIFEST_SCHEMA = "articraft-generator-material-class-shadow/v2"
SUMMARY_SCHEMA = "articraft-generator-material-class-migration-summary/v2"
ATTEMPT_SCHEMA = "articraft-generator-material-class-api-attempt/v2"
RESPONSE_CACHE_SCHEMA = "articraft-generator-material-class-api-response/v2"
NORMALIZATION_SCHEMA = "articraft-generator-material-class-normalization/v2"

CANARY_FILES = (
    "Container_Glass_bottle.py",
    "Container_Plastic_can.py",
    "Handtools_clothes_peg.py",
    "Urban_Environment_Large_Trashcan.py",
    "loom_shuttle.py",
)
SUPPORT_FILES = ("__init__.py", "_mechanisms.py", "_modular.py")
EXPECTED_GENERATOR_COUNT = 531
EXPECTED_REMAINING_COUNT = 526
EXPECTED_REMAINING_CALLSITE_COUNT = 17_640
EXPECTED_COMPOSITION_ONLY = "Urban_Environment_Public_toilet1.py"
EXPECTED_RAW_FLAT_COLOR_COUNT = 289
EXPECTED_RAW_FLAT_COLOR_SHA256 = "940f50c04ede23434662f174a9b75ee60bc4a2be2192a060a602b9a05a84855d"
EXPECTED_FLAT_PBR_CORRECTION_COUNT = 24
COMPOSITION_DEPENDENCIES = {
    EXPECTED_COMPOSITION_ONLY: (
        "Urban_Environment_Public_toilet.py",
        "Bathroom_toilet.py",
    )
}
DEFAULT_DASHSCOPE_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MAX_CONCURRENCY = 50
THINKING_LEVEL = "medium"
THINKING_BUDGET = 32_000
DEFAULT_MAX_TOKENS = 64_000
DEFAULT_CONTEXT_TOKENS = 1_000_000
DEFAULT_TIMEOUT_SECONDS = 900.0
REQUIRED_FINAL_GATES = frozenset(
    {
        "formal_library",
        "focused_tests",
        "full_tests",
        "ruff_check",
        "ruff_format",
        "diff_check",
    }
)

MATERIAL_HELPER_CALLSITE_IDS = frozenset(
    {
        "Industrial_Blast_door:383:4",
        "aquarium:332:4",
        "casino_machine:362:4",
        "studio_spotlight_on_yoke:458:4",
        "studio_spotlight_on_yoke:470:4",
    }
)
MATERIAL_CLASS_HELPER_DEFINITION = """\
def _material_class_id(
    value: str,
    first_values: tuple[str, ...],
    first_id: str,
    second_id: str,
) -> str:
    return first_id if value in first_values else second_id
"""

AQUARIUM_ROLE_ROUTED_CALLSITE_ID = "aquarium:332:4"
AQUARIUM_ROLE_ROUTED_SOURCE_SHA256 = (
    "ebfc63d710e57cab9c412465ec6a7a50f10fb33edea3799dde89b8d8f3b4d51e"
)
AQUARIUM_PALETTE_STYLES = (
    "classic_warm",
    "cool_blue",
    "planted_green",
    "mono_black",
)
AQUARIUM_MATERIAL_CLASS_BY_KEY = {
    "glass": "glass.clear_transparent",
    "frame": "plastic.opaque_glossy_molded",
    "dark": "plastic.opaque_glossy_molded",
    "canister": "plastic.opaque_glossy_molded",
    "led": "tech.emissive_surface",
    "red": "tech.emissive_surface",
    "orange": "tech.emissive_surface",
    "green": "tech.emissive_surface",
    "gravel": "stone.aggregate_ground",
    "gravel_dark": "stone.aggregate_ground",
    "rock": "stone.rough_rock",
    "plant_a": "organic.plant_leaf",
    "plant_b": "organic.plant_leaf",
    "plant_c": "organic.plant_leaf",
    "hose": "rubber.smooth_plain",
}
AQUARIUM_MATERIAL_CLASS_BY_NAME = {
    f"aq_{material_key}_{palette}": (
        "organic.coral_reef"
        if material_key == "rock" and palette == "cool_blue"
        else material_class_id
    )
    for material_key, material_class_id in AQUARIUM_MATERIAL_CLASS_BY_KEY.items()
    for palette in AQUARIUM_PALETTE_STYLES
}
AQUARIUM_MATERIAL_CLASS_HELPER_DEFINITION = """\
def _material_class_id(material_name: str) -> str:
    if material_name.startswith("aq_glass_"):
        return "glass.clear_transparent"
    if material_name.startswith(("aq_frame_", "aq_dark_", "aq_canister_")):
        return "plastic.opaque_glossy_molded"
    if material_name.startswith(("aq_led_", "aq_red_", "aq_orange_", "aq_green_")):
        return "tech.emissive_surface"
    if material_name.startswith(("aq_gravel_", "aq_gravel_dark_")):
        return "stone.aggregate_ground"
    if material_name == "aq_rock_cool_blue":
        return "organic.coral_reef"
    if material_name.startswith("aq_rock_"):
        return "stone.rough_rock"
    if material_name.startswith(("aq_plant_a_", "aq_plant_b_", "aq_plant_c_")):
        return "organic.plant_leaf"
    if material_name.startswith("aq_hose_"):
        return "rubber.smooth_plain"
    raise ValueError(f"Unsupported aquarium material role: {material_name!r}")
"""

_CONFIG_TYPE_EXPRESSION_RE = re.compile(
    r"^(?P<class_name>[A-Za-z_][A-Za-z0-9_]*Config)\.(?P<field>[A-Za-z_][A-Za-z0-9_]*)$"
)


def _constant_pbr_correction(material_class_id: str, rationale: str) -> dict[str, Any]:
    return {
        "config_expression": None,
        "config_domain": ["*"],
        "proposals": [
            {
                "config_values": ["*"],
                "material_class_id": material_class_id,
                "priority": 100,
                "rationale": rationale,
            }
        ],
    }


# These rows were the only first-pass flat decisions that failed the explicit
# text/logo/scale/state/pure-graphic rule. Each correction is bound to the
# inventoried source SHA and reuses a class selected elsewhere in the same
# first-pass proposal whenever an equivalent visible surface exists.
FLAT_PBR_CORRECTIONS: dict[str, dict[str, Any]] = {
    "Electrical_Wiring_Circuit_breaker": {
        "source_sha256": "28b9dc39842ae324f27df40e238f9a33996e01a78fa0aab517b61df353ab7457",
        "callsites": {
            "Electrical_Wiring_Circuit_breaker:540:16": _constant_pbr_correction(
                "plastic.opaque_glossy_molded",
                "The molded terminal cavity is a physical breaker housing surface.",
            ),
            "Electrical_Wiring_Circuit_breaker:571:16": _constant_pbr_correction(
                "plastic.opaque_glossy_molded",
                "The terminal opening is a physical molded breaker housing surface.",
            ),
            "Electrical_Wiring_Circuit_breaker:704:12": _constant_pbr_correction(
                "plastic.opaque_glossy_molded",
                "The mounting recess is part of the molded breaker housing.",
            ),
        },
    },
    "Electrical_Wiring_Surge_protector_switch": {
        "source_sha256": "565944e2cb92ca485d185602409ea6eacb43e2bcdab043b8ab503328caa99718",
        "callsites": {
            "Electrical_Wiring_Surge_protector_switch:506:12": _constant_pbr_correction(
                "plastic.opaque_glossy_molded",
                "The raised outlet recess is a physical molded receptacle surface.",
            ),
            "Electrical_Wiring_Surge_protector_switch:520:12": _constant_pbr_correction(
                "plastic.opaque_glossy_molded",
                "The recessed outlet cavity is a physical molded receptacle surface.",
            ),
        },
    },
    "Industrial_Blast_door": {
        "source_sha256": "b88649805b3831c106a645c7f44cc58ad4db8c9982dc95dbf8af89d00199c77c",
        "callsites": {
            "Industrial_Blast_door:383:4": {
                "config_expression": "material",
                "config_domain": ["concrete", "frame_steel"],
                "proposals": [
                    {
                        "config_values": ["concrete"],
                        "material_class_id": "concrete.formed_patterned",
                        "priority": 100,
                        "rationale": "Board-formed wall boxes use patterned formed concrete.",
                    },
                    {
                        "config_values": ["frame_steel"],
                        "material_class_id": "metal.paint_coated",
                        "priority": 100,
                        "rationale": "Blast-door frame and rail boxes are coated structural steel.",
                    },
                ],
            }
        },
    },
    "Other_armchair": {
        "source_sha256": "8779dd13ceff90c374aceeb8e2ebe0172777a5daeeacfd9a44815a8ba94b71b9",
        "callsites": {
            "Other_armchair:984:4": _constant_pbr_correction(
                "metal.paint_coated",
                "The pedestal spindle is a physical coated steel mechanism surface.",
            ),
            "Other_armchair:990:4": _constant_pbr_correction(
                "metal.paint_coated",
                "The hidden pedestal core is a physical coated steel mechanism surface.",
            ),
            "Other_armchair:1017:4": _constant_pbr_correction(
                "metal.paint_coated",
                "The pedestal socket is a physical coated steel mechanism surface.",
            ),
        },
    },
    "Urban_Environment_Well_lid": {
        "source_sha256": "ded0d8fccd08df3546b2b8785e838b8d83ad5f4eb03fbb07846ea329b9b41d76",
        "callsites": {
            "Urban_Environment_Well_lid:460:4": _constant_pbr_correction(
                "metal.cast_iron_bare",
                "The modeled cast shaft floor is a physical bare cast-iron surface.",
            )
        },
    },
    "casino_machine": {
        "source_sha256": "73721512397c6b6cd9bfb8f9089dccfd1a758cd871894d893b7b856b2dbd3cd5",
        "callsites": {
            "casino_machine:362:4": {
                "config_expression": "material.name",
                "config_domain": [
                    "casino_screen",
                    "casino_trim",
                    "casino_payout",
                    "casino_cabinet_dark",
                    "casino_metal",
                    "casino_glass",
                    "casino_button",
                ],
                "proposals": [
                    {
                        "config_values": [
                            "casino_screen",
                            "casino_glass",
                            "casino_button",
                        ],
                        "material_class_id": "tech.control_interface",
                        "priority": 100,
                        "rationale": "Screen, glazing, and reel-symbol panels form the control display.",
                    },
                    {
                        "config_values": [
                            "casino_trim",
                            "casino_payout",
                            "casino_cabinet_dark",
                            "casino_metal",
                        ],
                        "material_class_id": "metal.brushed_silver",
                        "priority": 100,
                        "rationale": "The remaining front inserts are physical metal panels and trim.",
                    },
                ],
            }
        },
    },
    "globe": {
        "source_sha256": "969c4b10bdc628cd4534e2df8fc5036db0b35e0d2b51014681e1c9e334420a8b",
        "callsites": {
            "globe:1578:4": _constant_pbr_correction(
                "plastic.opaque_glossy_molded",
                "The deep-ocean core is a physical molded globe shell surface.",
            )
        },
    },
    "ironing_board": {
        "source_sha256": "e325083501c7b773d3c99ed69511ad351dceae6a4a689558e7a338ce09caa10c",
        "callsites": {
            "ironing_board:421:12": _constant_pbr_correction(
                "metal.blackened_gunmetal",
                "The underside perforation walls are physical darkened metal surfaces.",
            )
        },
    },
    "playground_swing": {
        "source_sha256": "d5a106f0e82e395e9b7f1dadac269e7818e060cc77bc53d9dd837b905849169e",
        "callsites": {
            "playground_swing:841:4": _constant_pbr_correction(
                "plastic.opaque_glossy_molded",
                "The left leg opening is a physical molded bucket-seat surface.",
            ),
            "playground_swing:847:4": _constant_pbr_correction(
                "plastic.opaque_glossy_molded",
                "The right leg opening is a physical molded bucket-seat surface.",
            ),
        },
    },
    "studio_spotlight_on_yoke": {
        "source_sha256": "e3c129d6946ceb56e2e1840757bfaa4511a2f9bf9a704d55ad1c7f228ea8e200",
        "callsites": {
            "studio_spotlight_on_yoke:458:4": {
                "config_expression": "material.name",
                "config_domain": [
                    "yoke_rubber",
                    "yoke_base_dark",
                    "yoke_accent",
                    "yoke_metal",
                    "yoke_bezel",
                    "yoke_base",
                    "yoke_glass",
                ],
                "proposals": [
                    {
                        "config_values": [
                            "yoke_base_dark",
                            "yoke_accent",
                            "yoke_metal",
                            "yoke_bezel",
                            "yoke_base",
                        ],
                        "material_class_id": "metal.paint_coated",
                        "priority": 100,
                        "rationale": "Structural spotlight boxes are coated metal surfaces.",
                    },
                    {
                        "config_values": ["yoke_rubber"],
                        "material_class_id": "rubber.smooth_plain",
                        "priority": 100,
                        "rationale": "Feet and grips are smooth rubber surfaces.",
                    },
                    {
                        "config_values": ["yoke_glass"],
                        "material_class_id": "glass.clear_transparent",
                        "priority": 100,
                        "rationale": "The filter insert is a clear optical glass surface.",
                    },
                ],
            },
            "studio_spotlight_on_yoke:470:4": {
                "config_expression": "material.name",
                "config_domain": [
                    "yoke_base_dark",
                    "yoke_metal",
                    "yoke_bezel",
                    "yoke_accent",
                    "yoke_can",
                    "yoke_rubber",
                    "yoke_base",
                    "yoke_glass",
                    "yoke_emitter",
                ],
                "proposals": [
                    {
                        "config_values": [
                            "yoke_base_dark",
                            "yoke_metal",
                            "yoke_bezel",
                            "yoke_accent",
                            "yoke_can",
                            "yoke_base",
                        ],
                        "material_class_id": "metal.paint_coated",
                        "priority": 100,
                        "rationale": "Structural spotlight cylinders are coated metal surfaces.",
                    },
                    {
                        "config_values": ["yoke_rubber"],
                        "material_class_id": "rubber.smooth_plain",
                        "priority": 100,
                        "rationale": "Feet and grips are smooth rubber surfaces.",
                    },
                    {
                        "config_values": ["yoke_glass", "yoke_emitter"],
                        "material_class_id": "glass.clear_transparent",
                        "priority": 100,
                        "rationale": "Lens and emitter-cover cylinders are clear optical surfaces.",
                    },
                ],
            },
            "studio_spotlight_on_yoke:481:4": _constant_pbr_correction(
                "metal.paint_coated",
                "The generic sphere helper represents physical coated hardware.",
            ),
        },
    },
    "traditional_windmill": {
        "source_sha256": "4362071655a853b8ddb1a5e060fdfeae50f2cc9e5593fd87dcacf574a3e0420e",
        "callsites": {
            "traditional_windmill:308:8": _constant_pbr_correction(
                "glass.smoked_tinted",
                "The dark front window is a physical tinted window surface.",
            ),
            "traditional_windmill:453:12": _constant_pbr_correction(
                "wood.oak",
                "The upper-window louvers are physical oak slats.",
            ),
            "traditional_windmill:657:12": _constant_pbr_correction(
                "metal.paint_coated",
                "The weatherproof-cap louvers are physical coated metal slats.",
            ),
            "traditional_windmill:961:8": _constant_pbr_correction(
                "metal.steel_bare",
                "The hub-face bolts are physical bare steel fasteners.",
            ),
        },
    },
    "overshot_waterwheel": {
        "source_sha256": "ff2506855869dd7b93f1da381f8023f8ad9bb8ca8df596fa348eba1033c153de",
        "callsites": {
            "overshot_waterwheel:879:8": {
                "config_expression": "r.bucket_wheel_module",
                "config_domain": [
                    "spoked_shallow_bucket_wheel",
                    "deep_timber_bucket_wheel",
                    "drive_pinion_rotor",
                    "cast_iron_bucket_wheel",
                    "open_spoke_paddle_wheel",
                ],
                "proposals": [
                    {
                        "config_values": [
                            "cast_iron_bucket_wheel",
                            "drive_pinion_rotor",
                        ],
                        "material_class_id": "metal.cast_iron_bare",
                        "priority": 100,
                        "rationale": "The physical inner rim follows the cast-iron wheel module.",
                    },
                    {
                        "config_values": [
                            "spoked_shallow_bucket_wheel",
                            "deep_timber_bucket_wheel",
                            "open_spoke_paddle_wheel",
                        ],
                        "material_class_id": "wood.rustic_weathered",
                        "priority": 100,
                        "rationale": "The physical inner rim follows the weathered timber wheel module.",
                    },
                ],
            }
        },
    },
}


# The inventory exposes each field's full domain. These exact current-source
# callsites are only reachable from the narrower domains below. They remain
# unmodified proposals; the proof is recorded during cache normalization.
REACHABLE_DOMAIN_OVERRIDES: dict[tuple[str, str, str], dict[str, Any]] = {
    (
        "defibrillator_case",
        "2a25e79dcc39e23ce2c2faa3ad641dd48d9965b44ce055d02fa8aec016aee50c",
        "defibrillator_case:1170:8",
    ): {
        "config_expression": "r.body_form",
        "config_domain": [
            "rigid_hard_shell_case",
            "molded_soft_carry_case",
            "soft_shoulder_bag_pouch",
        ],
        "proof": "clamshell opening is built only by the carry-case family",
    },
    (
        "defibrillator_case",
        "2a25e79dcc39e23ce2c2faa3ad641dd48d9965b44ce055d02fa8aec016aee50c",
        "defibrillator_case:1176:8",
    ): {
        "config_expression": "r.body_form",
        "config_domain": [
            "rigid_hard_shell_case",
            "molded_soft_carry_case",
            "soft_shoulder_bag_pouch",
        ],
        "proof": "clamshell opening is built only by the carry-case family",
    },
    (
        "defibrillator_case",
        "2a25e79dcc39e23ce2c2faa3ad641dd48d9965b44ce055d02fa8aec016aee50c",
        "defibrillator_case:1214:4",
    ): {
        "config_expression": "r.body_form",
        "config_domain": [
            "rigid_hard_shell_case",
            "molded_soft_carry_case",
            "soft_shoulder_bag_pouch",
        ],
        "proof": "foldover flap is built only by the carry-case family",
    },
    (
        "pet_carrier",
        "fe241c7bfd8c89f100a290757a10edb1a771acdac36c6c5312f14b55e069e663",
        "pet_carrier:737:4",
    ): {
        "config_expression": "r.body_form",
        "config_domain": ["soft_fabric_envelope", "woven_wicker_basket"],
        "proof": "front-fold access is legal only for soft and wicker bodies",
    },
    (
        "pet_carrier",
        "fe241c7bfd8c89f100a290757a10edb1a771acdac36c6c5312f14b55e069e663",
        "pet_carrier:745:8",
    ): {
        "config_expression": "r.body_form",
        "config_domain": ["soft_fabric_envelope", "woven_wicker_basket"],
        "proof": "front-fold access is legal only for soft and wicker bodies",
    },
    (
        "pet_carrier",
        "fe241c7bfd8c89f100a290757a10edb1a771acdac36c6c5312f14b55e069e663",
        "pet_carrier:760:4",
    ): {
        "config_expression": "r.body_form",
        "config_domain": ["soft_fabric_envelope", "woven_wicker_basket"],
        "proof": "top-hatch access is legal only for soft and wicker bodies",
    },
    (
        "pet_carrier",
        "fe241c7bfd8c89f100a290757a10edb1a771acdac36c6c5312f14b55e069e663",
        "pet_carrier:768:8",
    ): {
        "config_expression": "r.body_form",
        "config_domain": ["soft_fabric_envelope", "woven_wicker_basket"],
        "proof": "top-hatch access is legal only for soft and wicker bodies",
    },
    (
        "pet_carrier",
        "fe241c7bfd8c89f100a290757a10edb1a771acdac36c6c5312f14b55e069e663",
        "pet_carrier:831:8",
    ): {
        "config_expression": "r.body_form",
        "config_domain": ["rigid_molded_clamshell", "open_wire_cage_lattice"],
        "proof": "slide-out tray access is legal only for rigid and wire bodies",
    },
    (
        "pet_carrier",
        "fe241c7bfd8c89f100a290757a10edb1a771acdac36c6c5312f14b55e069e663",
        "pet_carrier:910:4",
    ): {
        "config_expression": "r.body_form",
        "config_domain": ["soft_fabric_envelope", "woven_wicker_basket"],
        "proof": "webbing carry handle is legal only for soft and wicker bodies",
    },
    (
        "pictureX_0611_ergonomic_clamp_with_adjustable",
        "763b885427b453c0ca9144a409929bf2a299293efa9f399f6fb0a05c101071ce",
        "pictureX_0611_ergonomic_clamp_with_adjustable:1367:4",
    ): {
        "config_expression": "r.support_linkage",
        "config_domain": [
            "plain_arm",
            "ratchet_elbow",
            "gas_spring_arm",
            "linear_rail",
        ],
        "proof": "the shared rising-arm helper has exactly these four source callers",
    },
}


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _contained(
    path: Path,
    *,
    root: Path = WORKSPACE_ROOT,
    must_exist: bool = False,
) -> Path:
    resolved_root = root.resolve(strict=True)
    resolved = path.resolve(strict=must_exist)
    if not resolved.is_relative_to(resolved_root):
        raise ValueError(f"path is outside the authorized workspace: {resolved}")
    return resolved


def _json_object(path: Path) -> dict[str, Any]:
    resolved = _contained(path, must_exist=True)
    value = json.loads(resolved.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {resolved}")
    return value


def _atomic_bytes(path: Path, payload: bytes) -> None:
    destination = _contained(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, raw_tmp = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    tmp = Path(raw_tmp)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, destination)
    finally:
        tmp.unlink(missing_ok=True)


def _atomic_json(path: Path, value: object) -> None:
    payload = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    _atomic_bytes(path, payload)


def _run_path(run_dir: Path, *parts: str) -> Path:
    run_root = _contained(run_dir, root=REPO_ROOT)
    return _contained(run_root.joinpath(*parts), root=REPO_ROOT)


def _name_of(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _visual_call(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "visual"
    )


def _visual_name(node: ast.Call) -> tuple[str, ast.keyword]:
    keyword = next((item for item in node.keywords if item.arg == "name"), None)
    if keyword is None:
        raise ValueError(f"visual call at line {node.lineno} has no explicit name")
    value = keyword.value
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return value.value, keyword
    return ast.unparse(value), keyword


def _annotation_names(node: ast.AST | None) -> set[str]:
    if node is None:
        return set()
    return {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}


def _string_values(
    node: ast.AST | None,
    known: Mapping[str, tuple[str, ...]],
) -> tuple[str, ...]:
    if node is None:
        return ()
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return (node.value,)
    if isinstance(node, ast.Name):
        return known.get(node.id, ())
    if isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        values: list[str] = []
        for child in node.elts:
            child_values = _string_values(child, known)
            if not child_values:
                return ()
            values.extend(child_values)
        return tuple(dict.fromkeys(values))
    if isinstance(node, ast.Subscript) and _name_of(node.value) == "Literal":
        slice_node = node.slice
        children = slice_node.elts if isinstance(slice_node, ast.Tuple) else (slice_node,)
        values = []
        for child in children:
            if isinstance(child, ast.Constant) and isinstance(child.value, str):
                values.append(child.value)
        return tuple(dict.fromkeys(values))
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return tuple(
            dict.fromkeys(_string_values(node.left, known) + _string_values(node.right, known))
        )
    return ()


def _choice_values(
    node: ast.AST | None,
    known: Mapping[str, tuple[str, ...]],
) -> tuple[str, ...]:
    direct = _string_values(node, known)
    if direct:
        return direct
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr in {"choice", "choices", "sample"} and node.args:
            return _string_values(node.args[0], known)
    if isinstance(node, ast.IfExp):
        return tuple(
            dict.fromkeys(_choice_values(node.body, known) + _choice_values(node.orelse, known))
        )
    return ()


def _config_domains(
    tree: ast.Module,
) -> tuple[dict[str, dict[str, list[str]]], dict[str, list[str]]]:
    known: dict[str, tuple[str, ...]] = {}
    assignments: list[tuple[str, ast.AST]] = []
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            assignments.append((node.targets[0].id, node.value))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.value is not None:
                assignments.append((node.target.id, node.value))
            values = _string_values(node.annotation, known)
            if values:
                known[node.target.id] = values

    for _ in range(max(1, len(assignments))):
        changed = False
        for name, value in assignments:
            values = _string_values(value, known)
            if values and known.get(name) != values:
                known[name] = values
                changed = True
        if not changed:
            break

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        if not any(_name_of(base) in {"Enum", "StrEnum"} for base in node.bases):
            continue
        values = []
        for child in node.body:
            if isinstance(child, ast.Assign) and isinstance(child.value, ast.Constant):
                if isinstance(child.value.value, str):
                    values.append(child.value.value)
        if values:
            known[node.name] = tuple(dict.fromkeys(values))

    classes: dict[str, dict[str, list[str]]] = {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef) or not node.name.endswith("Config"):
            continue
        fields: dict[str, list[str]] = {}
        for child in node.body:
            if not isinstance(child, ast.AnnAssign) or not isinstance(child.target, ast.Name):
                continue
            values = _string_values(child.annotation, known)
            if not values and child.value is not None:
                values = _choice_values(child.value, known)
            if values:
                fields[child.target.id] = list(values)
        classes[node.name] = fields

    for function in (node for node in tree.body if isinstance(node, ast.FunctionDef)):
        if function.name not in {"config_from_seed", "resolve_config"}:
            continue
        local_known = dict(known)
        for child in ast.walk(function):
            if (
                isinstance(child, ast.Assign)
                and len(child.targets) == 1
                and isinstance(child.targets[0], ast.Name)
            ):
                values = _choice_values(child.value, local_known)
                if values:
                    local_known[child.targets[0].id] = values
        for call in (child for child in ast.walk(function) if isinstance(child, ast.Call)):
            class_name = _name_of(call.func)
            if class_name not in classes:
                continue
            for keyword in call.keywords:
                if keyword.arg is None:
                    continue
                values = _choice_values(keyword.value, local_known)
                if values:
                    existing = classes[class_name].get(keyword.arg, [])
                    classes[class_name][keyword.arg] = list(dict.fromkeys(existing + list(values)))

    serial_known = {name: list(values) for name, values in sorted(known.items()) if values}
    return classes, serial_known


def _function_scope_domains(
    function: ast.FunctionDef | ast.AsyncFunctionDef | None,
    *,
    call_lineno: int,
    class_domains: Mapping[str, Mapping[str, Sequence[str]]],
) -> dict[str, list[str]]:
    if function is None:
        return {}
    roots: dict[str, set[str]] = defaultdict(set)
    arguments = (
        list(function.args.posonlyargs) + list(function.args.args) + list(function.args.kwonlyargs)
    )
    for argument in arguments:
        names = _annotation_names(argument.annotation)
        for class_name in class_domains:
            if class_name in names:
                roots[argument.arg].add(class_name)

    resolved_classes = [name for name in class_domains if name.startswith("Resolved")]
    config_classes = [
        name
        for name in class_domains
        if name.endswith("Config") and not name.startswith("Resolved")
    ]
    for argument in arguments:
        if roots.get(argument.arg):
            continue
        if argument.arg in {"r", "resolved", "resolved_config"} and len(resolved_classes) == 1:
            roots[argument.arg].add(resolved_classes[0])
        elif argument.arg in {"config", "cfg"} and len(config_classes) == 1:
            roots[argument.arg].add(config_classes[0])

    for child in ast.walk(function):
        if getattr(child, "lineno", call_lineno + 1) >= call_lineno:
            continue
        if (
            not isinstance(child, ast.Assign)
            or len(child.targets) != 1
            or not isinstance(child.targets[0], ast.Name)
        ):
            continue
        target = child.targets[0].id
        if isinstance(child.value, ast.Call):
            called = _name_of(child.value.func)
            if called == "resolve_config" and len(resolved_classes) == 1:
                roots[target].add(resolved_classes[0])
            elif called in class_domains:
                roots[target].add(str(called))

    result: dict[str, list[str]] = {}
    for root, class_names in sorted(roots.items()):
        merged: dict[str, list[str]] = {}
        conflicts: set[str] = set()
        for class_name in class_names:
            fields = dict(class_domains[class_name])
            if class_name.startswith("Resolved"):
                base_name = class_name.removeprefix("Resolved")
                for field, values in class_domains.get(base_name, {}).items():
                    fields.setdefault(field, values)
            for field, values in fields.items():
                current = merged.get(field)
                candidate = list(values)
                if current is not None and current != candidate:
                    conflicts.add(field)
                else:
                    merged[field] = candidate
        for field, values in sorted(merged.items()):
            if field not in conflicts and values:
                result[f"{root}.{field}"] = values
    return result


class _CallsiteVisitor(ast.NodeVisitor):
    def __init__(
        self,
        *,
        source: str,
        slug: str,
        class_domains: Mapping[str, Mapping[str, Sequence[str]]],
    ) -> None:
        self.source = source
        self.slug = slug
        self.class_domains = class_domains
        self.functions: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
        self.loops = 0
        self.rows: list[dict[str, Any]] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.functions.append(node)
        self.generic_visit(node)
        self.functions.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.functions.append(node)
        self.generic_visit(node)
        self.functions.pop()

    def visit_For(self, node: ast.For) -> None:
        self.loops += 1
        self.generic_visit(node)
        self.loops -= 1

    def visit_While(self, node: ast.While) -> None:
        self.loops += 1
        self.generic_visit(node)
        self.loops -= 1

    def visit_Call(self, node: ast.Call) -> None:
        if _visual_call(node):
            visual_name, name_keyword = _visual_name(node)
            callsite_id = f"{self.slug}:{node.lineno}:{node.col_offset}"
            function = self.functions[-1] if self.functions else None
            self.rows.append(
                {
                    "callsite_id": callsite_id,
                    "visual_name": visual_name,
                    "function": function.name if function is not None else "<module>",
                    "in_loop": self.loops > 0,
                    "call_source": ast.get_source_segment(self.source, node) or ast.unparse(node),
                    "allowed_config_expressions": _function_scope_domains(
                        function,
                        call_lineno=node.lineno,
                        class_domains=self.class_domains,
                    ),
                    "name_keyword_end": [name_keyword.end_lineno, name_keyword.end_col_offset],
                    "has_material_class_id": any(
                        keyword.arg == "material_class_id" for keyword in node.keywords
                    ),
                }
            )
        self.generic_visit(node)


class _DropMaterialClass(ast.NodeTransformer):
    def visit_Module(self, node: ast.Module) -> ast.AST:
        node.body = [
            child
            for child in node.body
            if not (
                isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                and child.name == "_material_class_id"
            )
        ]
        self.generic_visit(node)
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        self.generic_visit(node)
        node.keywords = [keyword for keyword in node.keywords if keyword.arg != "material_class_id"]
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        self.generic_visit(node)
        node.args.kwonlyargs, node.args.kw_defaults = _drop_material_class_kwonly_arg(
            node.args.kwonlyargs,
            node.args.kw_defaults,
        )
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        self.generic_visit(node)
        node.args.kwonlyargs, node.args.kw_defaults = _drop_material_class_kwonly_arg(
            node.args.kwonlyargs,
            node.args.kw_defaults,
        )
        return node


def _drop_material_class_kwonly_arg(
    args: list[ast.arg],
    defaults: list[ast.expr | None],
) -> tuple[list[ast.arg], list[ast.expr | None]]:
    pairs = [
        (argument, default)
        for argument, default in zip(args, defaults, strict=True)
        if argument.arg != "material_class_id"
    ]
    return [argument for argument, _ in pairs], [default for _, default in pairs]


def _ast_hash(nodes: ast.AST | Sequence[ast.AST]) -> str:
    if isinstance(nodes, ast.AST):
        payload = ast.dump(nodes, include_attributes=False)
    else:
        payload = "\n".join(ast.dump(node, include_attributes=False) for node in nodes)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _source_fingerprints(source: str) -> dict[str, str]:
    tree = ast.parse(source)
    normalized = _DropMaterialClass().visit(copy.deepcopy(tree))
    config_nodes = [
        node
        for node in tree.body
        if (isinstance(node, ast.ClassDef) and node.name.endswith("Config"))
        or (
            isinstance(node, ast.FunctionDef)
            and node.name in {"config_from_seed", "resolve_config"}
        )
    ]
    rng_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and (
            _name_of(node.func)
            in {"choice", "choices", "randint", "randrange", "uniform", "random"}
            or (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id in {"rng", "random"}
            )
        )
    ]
    rng_calls.sort(key=lambda node: (node.lineno, node.col_offset))
    mechanical_calls = [
        node
        for node in ast.walk(normalized)
        if isinstance(node, ast.Call)
        and (
            _name_of(node.func) in {"Origin", "Part", "Joint", "Axis", "Limit"}
            or (
                isinstance(node.func, ast.Attribute)
                and node.func.attr in {"part", "articulation", "visual", "collision"}
            )
        )
    ]
    mechanical_calls.sort(key=lambda node: (node.lineno, node.col_offset))
    return {
        "mechanical_ast_sha256": _ast_hash(normalized),
        "config_ast_sha256": _ast_hash(config_nodes),
        "rng_ast_sha256": _ast_hash(rng_calls),
        "entity_ast_sha256": _ast_hash(mechanical_calls),
    }


def _inventory_source(path: Path) -> dict[str, Any]:
    source_path = _contained(path, root=TEMPLATE_ROOT, must_exist=True)
    source_bytes = source_path.read_bytes()
    source = source_bytes.decode("utf-8")
    tree = ast.parse(source, filename=str(source_path))
    class_domains, named_domains = _config_domains(tree)
    visitor = _CallsiteVisitor(
        source=source,
        slug=source_path.stem,
        class_domains=class_domains,
    )
    visitor.visit(tree)
    rows = sorted(visitor.rows, key=lambda row: row["callsite_id"])
    return {
        "template_slug": source_path.stem,
        "relative_path": source_path.relative_to(REPO_ROOT).as_posix(),
        "template_source_sha256": _sha256_bytes(source_bytes),
        "source_size_bytes": len(source_bytes),
        "source_line_count": source.count("\n") + (0 if source.endswith("\n") else 1),
        "visual_callsite_count": len(rows),
        "config_domains": class_domains,
        "named_literal_domains": named_domains,
        "callsites": rows,
        **_source_fingerprints(source),
    }


def _formal_classes() -> tuple[str, list[dict[str, Any]]]:
    logical_sha, class_ids = annotation_builder.load_formal_class_ids(FORMAL_LIBRARY)
    descriptions = _json_object(CLASS_DESCRIPTIONS)
    rows = descriptions.get("classes")
    if not isinstance(rows, list):
        raise ValueError("material class descriptions have no classes list")
    by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("material_class_id"), str):
            raise ValueError("invalid material class description row")
        by_id[row["material_class_id"]] = row
    if set(by_id) != set(class_ids):
        raise ValueError("material class descriptions do not exactly match the formal v2 pools")
    prompt_rows = [
        {
            "material_class_id": class_id,
            "description": str(by_id[class_id].get("display_name") or class_id),
        }
        for class_id in sorted(class_ids)
    ]
    return logical_sha, prompt_rows


def build_inventory(run_dir: Path) -> dict[str, Any]:
    run_root = _contained(run_dir, root=REPO_ROOT)
    run_root.mkdir(parents=True, exist_ok=True)
    logical_sha, class_rows = _formal_classes()
    files = sorted(TEMPLATE_ROOT.glob("*.py"), key=lambda path: path.name)
    generators = [path for path in files if path.name not in SUPPORT_FILES]
    if len(generators) != EXPECTED_GENERATOR_COUNT:
        raise ValueError(f"expected {EXPECTED_GENERATOR_COUNT} generators, found {len(generators)}")
    canary_sha = {name: _sha256_path(TEMPLATE_ROOT / name) for name in CANARY_FILES}
    remaining = [path for path in generators if path.name not in CANARY_FILES]
    if len(remaining) != EXPECTED_REMAINING_COUNT:
        raise ValueError(f"expected {EXPECTED_REMAINING_COUNT} remaining generators")

    templates = [_inventory_source(path) for path in remaining]
    total_callsites = sum(row["visual_callsite_count"] for row in templates)
    if total_callsites != EXPECTED_REMAINING_CALLSITE_COUNT:
        raise ValueError(
            f"expected {EXPECTED_REMAINING_CALLSITE_COUNT} current-source callsites, "
            f"found {total_callsites}"
        )
    composition = [row for row in templates if row["visual_callsite_count"] == 0]
    if [row["relative_path"].rsplit("/", 1)[-1] for row in composition] != [
        EXPECTED_COMPOSITION_ONLY
    ]:
        raise ValueError("composition-only generator set changed")
    already_annotated = [
        callsite["callsite_id"]
        for row in templates
        for callsite in row["callsites"]
        if callsite["has_material_class_id"]
    ]
    if already_annotated:
        raise ValueError(
            f"remaining fleet already contains material annotations: {already_annotated[:5]}"
        )

    document = {
        "schema_version": INVENTORY_SCHEMA,
        "created_at": _now(),
        "formal_library_snapshot_sha256": logical_sha,
        "formal_material_class_count": len(class_rows),
        "generator_count": len(templates),
        "visual_generator_count": len(templates) - len(composition),
        "composition_only_count": len(composition),
        "visual_callsite_count": total_callsites,
        "canary_sha256": canary_sha,
        "composition_dependencies": {
            key: list(value) for key, value in COMPOSITION_DEPENDENCIES.items()
        },
        "templates": templates,
    }
    document["inventory_sha256"] = _digest(document)
    _atomic_json(_run_path(run_root, "inventory.json"), document)
    _atomic_json(
        _run_path(run_root, "run.json"),
        {
            "schema_version": RUN_SCHEMA,
            "created_at": document["created_at"],
            "inventory_sha256": document["inventory_sha256"],
            "run_dir": run_root.as_posix(),
            "thinking_level": THINKING_LEVEL,
        },
    )
    return document


def load_inventory(run_dir: Path, *, verify_sources: bool = True) -> dict[str, Any]:
    inventory = _json_object(_run_path(run_dir, "inventory.json"))
    if inventory.get("schema_version") != INVENTORY_SCHEMA:
        raise ValueError("unsupported inventory schema")
    expected_digest = inventory.get("inventory_sha256")
    unsigned = dict(inventory)
    unsigned.pop("inventory_sha256", None)
    if expected_digest != _digest(unsigned):
        raise ValueError("inventory content digest mismatch")
    if verify_sources:
        for row in inventory["templates"]:
            path = _contained(REPO_ROOT / row["relative_path"], root=TEMPLATE_ROOT, must_exist=True)
            if _sha256_path(path) != row["template_source_sha256"]:
                raise ValueError(f"template changed after inventory: {path.name}")
        for name, expected in inventory["canary_sha256"].items():
            if _sha256_path(TEMPLATE_ROOT / name) != expected:
                raise ValueError(f"canary changed after inventory: {name}")
    return inventory


def _template_by_slug(inventory: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {str(row["template_slug"]): dict(row) for row in inventory["templates"]}


def _proposal_callsites(proposal: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows = proposal.get("callsites")
    if not isinstance(rows, list):
        raise ValueError("proposal callsites must be a list")
    result: dict[str, Mapping[str, Any]] = {}
    for row in rows:
        if not isinstance(row, Mapping) or not isinstance(row.get("callsite_id"), str):
            raise ValueError("proposal contains an invalid callsite row")
        if str(row["callsite_id"]) in result:
            raise ValueError(f"proposal repeats callsite ID {row['callsite_id']!r}")
        result[str(row["callsite_id"])] = row
    return result


def _recoverable_visual_name(raw: object, expected: str) -> bool:
    if not isinstance(raw, str):
        return False
    try:
        raw_ast = ast.dump(ast.parse(raw, mode="eval"), include_attributes=False)
        expected_ast = ast.dump(ast.parse(expected, mode="eval"), include_attributes=False)
    except SyntaxError:
        raw_ast = expected_ast = None
    if raw_ast is not None and raw_ast == expected_ast:
        return True
    return bool(expected) and expected[-1] in {"'", '"'} and raw == expected[:-1]


@functools.lru_cache(maxsize=None)
def _current_scope_domains(
    relative_path: str,
    template_source_sha256: str,
    callsite_id: str,
) -> dict[str, list[str]]:
    path = _contained(REPO_ROOT / relative_path, root=TEMPLATE_ROOT, must_exist=True)
    if _sha256_path(path) != template_source_sha256:
        raise ValueError(f"source changed while inferring Config scope: {path.name}")
    source = path.read_text(encoding="utf-8")
    return _scope_domains_from_source(source, source_label=str(path), callsite_id=callsite_id)


def _scope_domains_from_source(
    source: str,
    *,
    source_label: str,
    callsite_id: str,
) -> dict[str, list[str]]:
    tree = ast.parse(source, filename=source_label)
    _, raw_line, raw_column = callsite_id.rsplit(":", 2)
    line = int(raw_line)
    column = int(raw_column)
    target = next(
        (
            node
            for node in ast.walk(tree)
            if _visual_call(node)
            and getattr(node, "lineno", None) == line
            and getattr(node, "col_offset", None) == column
        ),
        None,
    )
    if target is None:
        raise ValueError(f"cannot find current-source callsite {callsite_id}")
    functions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.lineno <= line <= (node.end_lineno or node.lineno)
    ]
    function = min(
        functions,
        key=lambda node: (node.end_lineno or node.lineno) - node.lineno,
        default=None,
    )
    class_domains, _ = _config_domains(tree)
    return _function_scope_domains(
        function,
        call_lineno=line,
        class_domains=class_domains,
    )


def _flat_correction(
    inventory_row: Mapping[str, Any],
    callsite_id: str,
) -> Mapping[str, Any] | None:
    slug = str(inventory_row["template_slug"])
    template = FLAT_PBR_CORRECTIONS.get(slug)
    if template is None:
        return None
    if template["source_sha256"] != inventory_row["template_source_sha256"]:
        raise ValueError(f"flat correction source SHA drifted for {slug}")
    correction = template["callsites"].get(callsite_id)
    return correction if isinstance(correction, Mapping) else None


def _material_helper_definition(slug: str) -> str:
    if slug == "aquarium":
        return AQUARIUM_MATERIAL_CLASS_HELPER_DEFINITION
    return MATERIAL_CLASS_HELPER_DEFINITION


def _aquarium_role_routed_row() -> dict[str, Any]:
    values_by_class: dict[str, list[str]] = defaultdict(list)
    for material_name, class_id in AQUARIUM_MATERIAL_CLASS_BY_NAME.items():
        values_by_class[class_id].append(material_name)
    branches = [
        {
            "config_values": values,
            "material_class_id": class_id,
        }
        for class_id, values in values_by_class.items()
    ]
    return {
        "callsite_id": AQUARIUM_ROLE_ROUTED_CALLSITE_ID,
        "visual_name": "name",
        "decision": "material_class",
        "config_expression": "material.name",
        "config_domain": [value for branch in branches for value in branch["config_values"]],
        "branches": branches,
        "source_material_class_ids": [str(branch["material_class_id"]) for branch in branches],
        "compression": None,
        "routing_kind": GENERATOR_CLASS_ROLE_ROUTING_KIND,
    }


def _apply_role_routed_annotation_overrides(
    annotation: Mapping[str, Any],
    inventory_row: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    result = copy.deepcopy(dict(annotation))
    if inventory_row.get("template_slug") != "aquarium":
        return result, []
    if inventory_row.get("template_source_sha256") != AQUARIUM_ROLE_ROUTED_SOURCE_SHA256:
        raise ValueError("aquarium role-routed helper source SHA drifted")
    rows = result.get("callsites")
    if not isinstance(rows, list):
        raise ValueError("aquarium annotation has no callsites list")
    matches = [
        index
        for index, row in enumerate(rows)
        if isinstance(row, Mapping) and row.get("callsite_id") == AQUARIUM_ROLE_ROUTED_CALLSITE_ID
    ]
    if len(matches) != 1:
        raise ValueError("aquarium role-routed callsite is not unique")
    index = matches[0]
    original = rows[index]
    if not isinstance(original, Mapping) or original.get("source_material_class_ids") != [
        "plastic.opaque_generic"
    ]:
        raise ValueError("aquarium first-pass helper annotation drifted")
    corrected = _aquarium_role_routed_row()
    rows[index] = corrected
    result["schema_version"] = GENERATOR_CLASS_ROLE_ROUTED_ANNOTATIONS_SCHEMA
    result["policy_version"] = GENERATOR_CLASS_ROLE_ROUTED_ANNOTATION_POLICY
    return result, [
        {
            "callsite_id": AQUARIUM_ROLE_ROUTED_CALLSITE_ID,
            "reason": "heterogeneous_source_material_role_routing",
            "before_material_class_ids": ["plastic.opaque_generic"],
            "after_material_class_ids": corrected["source_material_class_ids"],
            "runtime_material_name_count": len(corrected["config_domain"]),
        }
    ]


def _scope_domains_for_inventory(
    inventory_row: Mapping[str, Any],
    callsite_id: str,
    *,
    source_override: str | None = None,
) -> dict[str, list[str]]:
    relative_path = inventory_row.get("relative_path")
    source_sha = inventory_row.get("template_source_sha256")
    if not isinstance(relative_path, str) or not isinstance(source_sha, str):
        return {}
    if source_override is not None:
        if _sha256_bytes(source_override.encode("utf-8")) != source_sha:
            raise ValueError("scope source override does not match inventory SHA")
        return _scope_domains_from_source(
            source_override,
            source_label=relative_path,
            callsite_id=callsite_id,
        )
    candidate = (REPO_ROOT / relative_path).resolve(strict=False)
    if not candidate.is_file() or not candidate.is_relative_to(TEMPLATE_ROOT.resolve()):
        return {}
    return _current_scope_domains(relative_path, source_sha, callsite_id)


def _reachable_domain_override(
    inventory_row: Mapping[str, Any],
    callsite_id: str,
) -> Mapping[str, Any] | None:
    source_sha = inventory_row.get("template_source_sha256")
    if not isinstance(source_sha, str):
        return None
    key = (
        str(inventory_row["template_slug"]),
        source_sha,
        callsite_id,
    )
    return REACHABLE_DOMAIN_OVERRIDES.get(key)


def _normalize_received_proposal(
    proposal: Mapping[str, Any],
    inventory_row: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    normalized = copy.deepcopy(dict(proposal))
    expected_rows = {str(row["callsite_id"]): row for row in inventory_row.get("callsites", [])}
    rows = normalized.get("callsites")
    if not isinstance(rows, list):
        raise ValueError("proposal callsites must be a list before normalization")
    by_id = _proposal_callsites(normalized)
    if len(rows) != len(by_id) or set(by_id) != set(expected_rows):
        raise ValueError("normalizer requires the exact current-source callsite set")

    audits: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("normalizer received a non-object callsite row")
        callsite_id = str(row["callsite_id"])
        expected = expected_rows[callsite_id]
        original = copy.deepcopy(row)

        if row.get("visual_name") != expected["visual_name"]:
            if not _recoverable_visual_name(row.get("visual_name"), str(expected["visual_name"])):
                raise ValueError(f"unrecoverable visual-name mismatch at {callsite_id}")
            before = row.get("visual_name")
            row["visual_name"] = expected["visual_name"]
            audits.append(
                {
                    "callsite_id": callsite_id,
                    "field": "visual_name",
                    "before": before,
                    "after": row["visual_name"],
                    "reason": "source_inventory_canonical_echo",
                }
            )

        if row.get("decision") == "material_class" and isinstance(row.get("config_domain"), str):
            raw_domain = str(row["config_domain"])
            proposals = row.get("proposals")
            values = [
                value
                for candidate in proposals or []
                if isinstance(candidate, Mapping)
                for value in candidate.get("config_values", [])
            ]
            if row.get("config_expression") is not None or raw_domain != "*" or values != ["*"]:
                raise ValueError(f"unsafe scalar config_domain at {callsite_id}")
            row["config_domain"] = [raw_domain]
            audits.append(
                {
                    "callsite_id": callsite_id,
                    "field": "config_domain",
                    "before": raw_domain,
                    "after": [raw_domain],
                    "reason": "strict_json_container_recovery",
                }
            )

        if row.get("decision") == "material_class" and isinstance(
            row.get("config_expression"), str
        ):
            expression = str(row["config_expression"])
            allowed = dict(expected.get("allowed_config_expressions", {}))
            if expression not in allowed:
                match = _CONFIG_TYPE_EXPRESSION_RE.fullmatch(expression)
                if match is not None and isinstance(row.get("config_domain"), list):
                    class_name = match.group("class_name")
                    field = match.group("field")
                    declared = (
                        inventory_row.get("config_domains", {}).get(class_name, {}).get(field)
                    )
                    current = _scope_domains_for_inventory(inventory_row, callsite_id)
                    candidates = [
                        candidate
                        for candidate, domain in current.items()
                        if candidate.rsplit(".", 1)[-1] == field
                        and domain == row["config_domain"]
                        and declared == row["config_domain"]
                    ]
                    if len(candidates) == 1:
                        row["config_expression"] = candidates[0]
                        audits.append(
                            {
                                "callsite_id": callsite_id,
                                "field": "config_expression",
                                "before": expression,
                                "after": candidates[0],
                                "reason": "unique_in_scope_resolved_config_root",
                            }
                        )

        correction = _flat_correction(inventory_row, callsite_id)
        if correction is not None:
            corrected = {
                "callsite_id": callsite_id,
                "visual_name": row["visual_name"],
                "decision": "material_class",
                "config_expression": copy.deepcopy(correction["config_expression"]),
                "config_domain": copy.deepcopy(correction["config_domain"]),
                "proposals": copy.deepcopy(correction["proposals"]),
            }
            if row.get("decision") == "flat_color":
                row.clear()
                row.update(corrected)
                audits.append(
                    {
                        "callsite_id": callsite_id,
                        "field": "decision",
                        "before": "flat_color",
                        "after": "material_class",
                        "reason": "flat_color_hard_rule_pbr_correction",
                        "material_class_ids": [
                            candidate["material_class_id"] for candidate in correction["proposals"]
                        ],
                    }
                )
            elif row != corrected:
                raise ValueError(f"normalized flat correction drifted at {callsite_id}")

        if original.get("decision") == "material_class":
            if row.get("decision") != "material_class":
                raise ValueError(f"normalizer changed a material decision at {callsite_id}")
            if row.get("proposals") != original.get("proposals"):
                raise ValueError(f"normalizer changed material proposals at {callsite_id}")

    return normalized, sorted(
        audits,
        key=lambda row: (str(row["callsite_id"]), str(row["field"])),
    )


def validate_proposal_source_domains(
    proposal: Mapping[str, Any],
    inventory_row: Mapping[str, Any],
    *,
    source_override: str | None = None,
) -> list[dict[str, Any]]:
    expected_rows = {str(row["callsite_id"]): row for row in inventory_row.get("callsites", [])}
    proposal_rows = _proposal_callsites(proposal)
    if set(proposal_rows) != set(expected_rows):
        raise ValueError("proposal callsite set differs from current-source inventory")
    audits: list[dict[str, Any]] = []
    for callsite_id, row in proposal_rows.items():
        if row.get("decision") != "material_class":
            continue
        expression = row.get("config_expression")
        domain = row.get("config_domain")
        if expression is None:
            if domain != ["*"]:
                raise ValueError(f"{callsite_id} constant annotation must use ['*']")
            continue
        if not isinstance(expression, str):
            raise ValueError(f"{callsite_id} has an invalid config expression")
        allowed = dict(expected_rows[callsite_id].get("allowed_config_expressions", {}))
        correction = _flat_correction(inventory_row, callsite_id)
        if (
            expression not in allowed
            and correction is not None
            and expression == correction["config_expression"]
        ):
            if callsite_id not in MATERIAL_HELPER_CALLSITE_IDS:
                raise ValueError(
                    f"{callsite_id} has a non-Config condition without a material helper"
                )
            expected_domain = correction["config_domain"]
            if domain != expected_domain:
                raise ValueError(
                    f"{callsite_id} corrected source-parameter domain mismatch; "
                    f"expected={expected_domain!r}, got={domain!r}"
                )
            audits.append(
                {
                    "callsite_id": callsite_id,
                    "kind": "material_helper_domain",
                    "config_expression": expression,
                    "config_domain": domain,
                }
            )
            continue
        if expression not in allowed:
            scope_domains = (
                _scope_domains_for_inventory(inventory_row, callsite_id)
                if source_override is None
                else _scope_domains_for_inventory(
                    inventory_row,
                    callsite_id,
                    source_override=source_override,
                )
            )
            allowed.update(scope_domains)
        if expression not in allowed:
            raise ValueError(
                f"{callsite_id} condition {expression!r} is not a source-proven "
                "Config/ResolvedConfig expression"
            )
        expected_domain = allowed[expression]
        if (
            not isinstance(domain, list)
            or set(domain) != set(expected_domain)
            or len(domain) != len(expected_domain)
        ):
            override = _reachable_domain_override(inventory_row, callsite_id)
            if (
                override is not None
                and expression == override["config_expression"]
                and domain == override["config_domain"]
                and set(domain).issubset(expected_domain)
            ):
                audits.append(
                    {
                        "callsite_id": callsite_id,
                        "kind": "current_source_reachable_domain",
                        "config_expression": expression,
                        "field_domain": expected_domain,
                        "reachable_domain": domain,
                        "proof": override["proof"],
                    }
                )
                continue
            raise ValueError(
                f"{callsite_id} config domain mismatch for {expression!r}; "
                f"expected={expected_domain!r}, got={domain!r}"
            )
    return audits


def _relevant_helper_source(source: str) -> list[dict[str, str]]:
    tree = ast.parse(source)
    result: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        module = node.module or ""
        target: Path | None = None
        if module in {"_mechanisms", "_modular"} and node.level:
            target = TEMPLATE_ROOT / f"{module}.py"
        elif module.startswith("agent.templates."):
            target = TEMPLATE_ROOT / f"{module.rsplit('.', 1)[-1]}.py"
        if target is None or not target.is_file():
            continue
        helper_path = _contained(target, root=TEMPLATE_ROOT, must_exist=True)
        helper_source = helper_path.read_text(encoding="utf-8")
        if helper_path.name in {"_mechanisms.py", "_modular.py"}:
            key = (helper_path.name, "*")
            if key not in seen:
                result.append({"source": helper_source, "source_path": helper_path.name})
                seen.add(key)
            continue
        helper_tree = ast.parse(helper_source)
        imported = {alias.name for alias in node.names if alias.name != "*"}
        for child in helper_tree.body:
            name = getattr(child, "name", None)
            if not isinstance(name, str) or name not in imported:
                continue
            segment = ast.get_source_segment(helper_source, child)
            if not segment or (helper_path.name, name) in seen:
                continue
            result.append(
                {
                    "source": segment,
                    "source_path": f"{helper_path.name}:{name}",
                }
            )
            seen.add((helper_path.name, name))
    return result


def _prompt_callsites(inventory_row: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "callsite_id": row["callsite_id"],
            "visual_name": row["visual_name"],
            "function": row["function"],
            "in_loop": row["in_loop"],
            "allowed_config_expressions": row["allowed_config_expressions"],
            "call_source": row["call_source"],
        }
        for row in inventory_row["callsites"]
    ]


def _proposal_prompt(
    *,
    inventory: Mapping[str, Any],
    inventory_row: Mapping[str, Any],
    class_rows: Sequence[Mapping[str, Any]],
    usage_tiebreaker: Mapping[str, int],
) -> tuple[str, str]:
    source_path = _contained(
        REPO_ROOT / str(inventory_row["relative_path"]),
        root=TEMPLATE_ROOT,
        must_exist=True,
    )
    source = source_path.read_text(encoding="utf-8")
    system = (
        "You are the sole semantic annotator for an Articraft direct-pool v2 migration. "
        "Return exactly one JSON object and no Markdown, explanation, or code edits. "
        "The local validator will reject any missing, extra, stale, or unavailable value."
    )
    contract = {
        "top_level_exact_fields": [
            "schema_version",
            "policy_version",
            "library_snapshot_sha256",
            "template_slug",
            "template_source_sha256",
            "callsites",
        ],
        "top_level_fixed_values": {
            "schema_version": GENERATOR_CLASS_PROPOSALS_SCHEMA,
            "policy_version": GENERATOR_CLASS_ANNOTATION_POLICY,
            "library_snapshot_sha256": inventory["formal_library_snapshot_sha256"],
            "template_slug": inventory_row["template_slug"],
            "template_source_sha256": inventory_row["template_source_sha256"],
        },
        "material_class_callsite_exact_fields": [
            "callsite_id",
            "visual_name",
            "decision",
            "config_expression",
            "config_domain",
            "proposals",
        ],
        "material_class_callsite_shape": {
            "callsite_id": "copy exactly",
            "visual_name": "copy exactly",
            "decision": "material_class",
            "config_expression": "null or one exact allowed dotted expression",
            "config_domain": ["every exact value, or * for a constant"],
            "proposals": [
                {
                    "config_values": ["an exhaustive disjoint subset"],
                    "material_class_id": "one exact allowed ID",
                    "priority": "integer 0..100",
                    "rationale": "short component and visible-surface rationale",
                }
            ],
        },
        "proposal_row_exact_fields": [
            "config_values",
            "material_class_id",
            "priority",
            "rationale",
        ],
        "flat_color_callsite_exact_fields": ["callsite_id", "visual_name", "decision"],
        "flat_color_callsite_shape": {
            "callsite_id": "copy exactly",
            "visual_name": "copy exactly",
            "decision": "flat_color",
        },
        "flat_color_rule": (
            "Do not include null or material-only fields on flat_color rows. It is allowed "
            "only for explicit text, logo, scale/tick, state marker, or an existing "
            "intentionally pure-color graphic visual."
        ),
    }
    payload = {
        "task": (
            "Classify every static .visual() callsite independently. A resolved visual gets "
            "one scalar material_class_id. Use a constant for one material. Use a simple "
            "Config/ResolvedConfig condition only when the callsite has a real two-or-more "
            "material branch and only from allowed_config_expressions. If source semantics "
            "suggest more than two classes, preserve every Config value in proposals; the "
            "local max2 builder will compress deterministically. Never emit multiple candidate "
            "IDs for one resolved visual. Do not annotate construction or physics."
        ),
        "selection_policy": (
            "Component material semantics are mandatory. Prefer the most specific visible "
            "surface class. Do not fall back wholesale to generic metal, plastic, or wood when "
            "a specific class is justified. There is no pool quota. Only when multiple classes "
            "are equally specific and equally correct, prefer the currently less-used class "
            "shown in usage_tiebreaker."
        ),
        "output_contract": contract,
        "formal_material_classes": list(class_rows),
        "usage_tiebreaker": dict(sorted(usage_tiebreaker.items())),
        "config_and_resolved_config_domains": inventory_row["config_domains"],
        "named_literal_domains": inventory_row["named_literal_domains"],
        "visual_callsites": _prompt_callsites(inventory_row),
        "relevant_helpers": _relevant_helper_source(source),
    }
    user = (
        json.dumps(payload, ensure_ascii=False, sort_keys=True)
        + '\n<generator_source path="'
        + str(inventory_row["relative_path"])
        + '">\n'
        + source
        + "\n</generator_source>\nReturn the strict proposal JSON object now."
    )
    return system, user


def _dotenv_settings() -> dict[str, Any]:
    env_path = _contained(DOTENV_PATH, must_exist=True)
    raw = dotenv_values(env_path)

    def text_value(name: str, default: str = "") -> str:
        value = raw.get(name)
        return str(value).strip() if value is not None else default

    def int_value(name: str, default: int) -> int:
        try:
            return int(text_value(name).replace("_", ""))
        except ValueError:
            return default

    def float_value(name: str, default: float) -> float:
        try:
            return float(text_value(name))
        except ValueError:
            return default

    keys: list[str] = []
    primary = text_value("DASHSCOPE_API_KEY")
    if primary:
        keys.append(primary)
    plural = text_value("DASHSCOPE_API_KEYS")
    if plural:
        keys.extend(
            token.strip() for token in plural.replace("\n", ",").split(",") if token.strip()
        )
    keys = list(dict.fromkeys(keys))
    if not keys:
        raise ValueError("DashScope credentials are missing from articraft_data/.env")
    model = text_value("DASHSCOPE_MODEL")
    if not model:
        raise ValueError("DASHSCOPE_MODEL is missing from articraft_data/.env")
    return {
        "api_keys": keys,
        "model": model,
        "base_url": text_value("DASHSCOPE_BASE_URL") or DEFAULT_DASHSCOPE_BASE_URL,
        "max_attempts": max(1, min(8, int_value("DASHSCOPE_MAX_ATTEMPTS", 4))),
        "retry_base_seconds": max(0.0, float_value("DASHSCOPE_RETRY_BASE_SECONDS", 0.5)),
        "retry_max_seconds": max(0.0, float_value("DASHSCOPE_RETRY_MAX_SECONDS", 20.0)),
        "timeout_seconds": max(
            1.0, float_value("DASHSCOPE_REQUEST_TIMEOUT_SECONDS", DEFAULT_TIMEOUT_SECONDS)
        ),
        "max_tokens": max(1, int_value("DASHSCOPE_MAX_TOKENS", DEFAULT_MAX_TOKENS)),
        "context_tokens": max(1, int_value("DASHSCOPE_CONTEXT_TOKENS", DEFAULT_CONTEXT_TOKENS)),
    }


def _usage_from_proposal(proposal: Mapping[str, Any]) -> Counter[str]:
    result: Counter[str] = Counter()
    rows = proposal.get("callsites")
    if not isinstance(rows, list):
        return result
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        proposals = row.get("proposals")
        if not isinstance(proposals, list):
            continue
        for candidate in proposals:
            if isinstance(candidate, Mapping) and isinstance(
                candidate.get("material_class_id"), str
            ):
                result[str(candidate["material_class_id"])] += 1
    return result


def _safe_error(exc: BaseException) -> dict[str, Any]:
    status = getattr(exc, "status_code", None)
    return {
        "error_type": type(exc).__name__,
        "status_code": status if isinstance(status, int) else None,
    }


def _retryable(exc: BaseException) -> bool:
    status = getattr(exc, "status_code", None)
    if status in {429, 503}:
        return True
    return type(exc).__name__ in {
        "APITimeoutError",
        "APIConnectionError",
        "TimeoutError",
    } or isinstance(exc, (asyncio.TimeoutError, TimeoutError))


def _retry_after_seconds(exc: BaseException) -> float | None:
    response = getattr(exc, "response", None)
    headers = getattr(response, "headers", None)
    if headers is None:
        return None
    raw = headers.get("retry-after")
    if raw is None:
        return None
    try:
        return max(0.0, float(raw))
    except (TypeError, ValueError):
        return None


def _response_payload(response: Any) -> tuple[str, dict[str, Any]]:
    choices = getattr(response, "choices", None)
    if not choices:
        raise ValueError("DashScope response has no choices")
    choice = choices[0]
    message = getattr(choice, "message", None)
    content = getattr(message, "content", None)
    if not isinstance(content, str) or not content.strip():
        raise ValueError("DashScope response has no JSON content")
    usage = getattr(response, "usage", None)
    usage_payload: dict[str, Any] = {}
    if usage is not None:
        for field in ("prompt_tokens", "completion_tokens", "total_tokens"):
            value = getattr(usage, field, None)
            if isinstance(value, int):
                usage_payload[field] = value
    metadata = {
        "finish_reason": getattr(choice, "finish_reason", None),
        "response_model": getattr(response, "model", None),
        "usage": usage_payload,
    }
    return content, metadata


def _validate_received_proposal(
    proposal: Mapping[str, Any],
    *,
    inventory: Mapping[str, Any],
    inventory_row: Mapping[str, Any],
    class_ids: Iterable[str],
) -> list[dict[str, Any]]:
    expected_callsites = {
        str(row["callsite_id"]): str(row["visual_name"]) for row in inventory_row["callsites"]
    }
    annotation_builder.build_generator_class_annotations(
        proposal,
        available_material_class_ids=class_ids,
        expected_library_snapshot_sha256=str(inventory["formal_library_snapshot_sha256"]),
        expected_template_source_sha256=str(inventory_row["template_source_sha256"]),
        expected_callsites=expected_callsites,
    )
    return validate_proposal_source_domains(proposal, inventory_row)


def _load_cached_proposal(
    run_dir: Path,
    *,
    inventory: Mapping[str, Any],
    inventory_row: Mapping[str, Any],
    class_ids: Iterable[str],
) -> tuple[dict[str, Any] | None, str | None]:
    slug = str(inventory_row["template_slug"])
    proposal_path = _run_path(run_dir, "proposals", f"{slug}.json")
    response_path = _run_path(run_dir, "responses", f"{slug}.json")
    proposal: dict[str, Any] | None = None
    if proposal_path.is_file():
        proposal = _json_object(proposal_path)
    elif response_path.is_file():
        response_cache = _json_object(response_path)
        content = response_cache.get("content")
        if not isinstance(content, str):
            return None, "cached_response_has_no_content"
        try:
            value = json.loads(content)
        except json.JSONDecodeError:
            return None, "cached_response_is_not_strict_json"
        if not isinstance(value, dict):
            return None, "cached_response_json_root_is_not_object"
        proposal = value
        _atomic_json(proposal_path, proposal)
    if proposal is None:
        return None, None
    try:
        _validate_received_proposal(
            proposal,
            inventory=inventory,
            inventory_row=inventory_row,
            class_ids=class_ids,
        )
    except Exception as exc:
        return None, f"{type(exc).__name__}:proposal_validation_failed"
    return proposal, None


async def _request_one(
    *,
    clients: Sequence[Any],
    settings: Mapping[str, Any],
    run_dir: Path,
    inventory: Mapping[str, Any],
    inventory_row: Mapping[str, Any],
    class_rows: Sequence[Mapping[str, Any]],
    usage_tiebreaker: Mapping[str, int],
    client_index: int,
) -> dict[str, Any]:
    slug = str(inventory_row["template_slug"])
    system, user = _proposal_prompt(
        inventory=inventory,
        inventory_row=inventory_row,
        class_rows=class_rows,
        usage_tiebreaker=usage_tiebreaker,
    )
    request_descriptor = {
        "model": settings["model"],
        "base_url": settings["base_url"],
        "thinking_level": THINKING_LEVEL,
        "thinking_budget": THINKING_BUDGET,
        "library_snapshot_sha256": inventory["formal_library_snapshot_sha256"],
        "template_source_sha256": inventory_row["template_source_sha256"],
        "inventory_sha256": inventory["inventory_sha256"],
        "messages_sha256": _digest({"system": system, "user": user}),
        "prompt_size_bytes": len(system.encode("utf-8")) + len(user.encode("utf-8")),
        "request_part_count": 1,
    }
    estimated_prompt_tokens = max(1, request_descriptor["prompt_size_bytes"] // 3)
    if estimated_prompt_tokens + int(settings["max_tokens"]) + 1024 >= int(
        settings["context_tokens"]
    ):
        raise ValueError(f"{slug} exceeds the configured API context limit and requires splitting")
    request_descriptor["request_sha256"] = _digest(request_descriptor)
    _atomic_json(_run_path(run_dir, "requests", f"{slug}.json"), request_descriptor)

    attempt_path = _run_path(run_dir, "attempts", f"{slug}.json")
    attempt_state: dict[str, Any]
    if attempt_path.is_file():
        attempt_state = _json_object(attempt_path)
    else:
        attempt_state = {
            "schema_version": ATTEMPT_SCHEMA,
            "template_slug": slug,
            "request_sha256": request_descriptor["request_sha256"],
            "attempt_count": 0,
            "retry_count": 0,
            "events": [],
        }
    if attempt_state.get("request_sha256") != request_descriptor["request_sha256"]:
        raise ValueError(f"cached attempt request mismatch for {slug}")

    max_attempts = int(settings["max_attempts"])
    while int(attempt_state["attempt_count"]) < max_attempts:
        attempt = int(attempt_state["attempt_count"]) + 1
        started = time.monotonic()
        try:
            response = await asyncio.wait_for(
                clients[client_index % len(clients)].chat.completions.create(
                    model=settings["model"],
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                    max_tokens=int(settings["max_tokens"]),
                    extra_body={
                        "enable_thinking": True,
                        "thinking_budget": THINKING_BUDGET,
                    },
                ),
                timeout=float(settings["timeout_seconds"]),
            )
            content, metadata = _response_payload(response)
            event = {
                "attempt": attempt,
                "elapsed_seconds": round(time.monotonic() - started, 6),
                "finished_at": _now(),
                "status": "response_received",
            }
            attempt_state["attempt_count"] = attempt
            attempt_state["events"].append(event)
            _atomic_json(attempt_path, attempt_state)
            response_cache = {
                "schema_version": RESPONSE_CACHE_SCHEMA,
                "template_slug": slug,
                "request_sha256": request_descriptor["request_sha256"],
                "received_at": event["finished_at"],
                "content": content,
                **metadata,
            }
            _atomic_json(_run_path(run_dir, "responses", f"{slug}.json"), response_cache)
            try:
                proposal = json.loads(content)
            except json.JSONDecodeError as exc:
                return {
                    "template_slug": slug,
                    "status": "failed",
                    "failure": "response_not_strict_json",
                    "detail": {"line": exc.lineno, "column": exc.colno},
                }
            if not isinstance(proposal, dict):
                return {
                    "template_slug": slug,
                    "status": "failed",
                    "failure": "response_json_root_not_object",
                }
            _atomic_json(_run_path(run_dir, "proposals", f"{slug}.json"), proposal)
            return {
                "template_slug": slug,
                "status": "received",
                "proposal": proposal,
                "retry_count": int(attempt_state["retry_count"]),
            }
        except Exception as exc:
            retryable = _retryable(exc)
            event = {
                "attempt": attempt,
                "elapsed_seconds": round(time.monotonic() - started, 6),
                "finished_at": _now(),
                "status": "transport_error",
                "retryable": retryable,
                **_safe_error(exc),
            }
            attempt_state["attempt_count"] = attempt
            attempt_state["events"].append(event)
            can_retry = retryable and attempt < max_attempts
            if can_retry:
                attempt_state["retry_count"] = int(attempt_state["retry_count"]) + 1
            _atomic_json(attempt_path, attempt_state)
            if not can_retry:
                return {
                    "template_slug": slug,
                    "status": "failed",
                    "failure": "transport_error",
                    "detail": _safe_error(exc),
                    "retry_count": int(attempt_state["retry_count"]),
                }
            exponential = min(
                float(settings["retry_max_seconds"]),
                float(settings["retry_base_seconds"]) * (2 ** (attempt - 1)),
            )
            retry_after = _retry_after_seconds(exc)
            delay = random.uniform(0.0, exponential) if exponential > 0 else 0.0
            if retry_after is not None:
                delay = max(delay, min(float(settings["retry_max_seconds"]), retry_after))
            event["retry_delay_seconds"] = round(delay, 6)
            _atomic_json(attempt_path, attempt_state)
            await asyncio.sleep(delay)
    return {
        "template_slug": slug,
        "status": "failed",
        "failure": "attempt_budget_exhausted",
        "retry_count": int(attempt_state["retry_count"]),
    }


async def propose_all(
    run_dir: Path,
    *,
    concurrency: int,
    limit: int | None = None,
) -> dict[str, Any]:
    if not 1 <= concurrency <= MAX_CONCURRENCY:
        raise ValueError(f"concurrency must be between 1 and {MAX_CONCURRENCY}")
    inventory = load_inventory(run_dir)
    logical_sha, class_rows = _formal_classes()
    if logical_sha != inventory["formal_library_snapshot_sha256"]:
        raise ValueError("formal library changed after inventory")
    class_ids = {str(row["material_class_id"]) for row in class_rows}
    settings = _dotenv_settings()
    from openai import AsyncOpenAI

    clients = [
        AsyncOpenAI(
            api_key=key,
            base_url=settings["base_url"],
            max_retries=0,
            timeout=float(settings["timeout_seconds"]),
        )
        for key in settings["api_keys"]
    ]
    visual_rows = [row for row in inventory["templates"] if int(row["visual_callsite_count"]) > 0]
    usage: Counter[str] = Counter()
    results: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    for row in visual_rows:
        cached, failure = _load_cached_proposal(
            run_dir,
            inventory=inventory,
            inventory_row=row,
            class_ids=class_ids,
        )
        if cached is not None:
            usage.update(_usage_from_proposal(cached))
            results.append(
                {
                    "template_slug": row["template_slug"],
                    "status": "cache_hit",
                    "proposal": cached,
                    "retry_count": 0,
                }
            )
        elif failure is not None:
            results.append(
                {
                    "template_slug": row["template_slug"],
                    "status": "failed",
                    "failure": failure,
                }
            )
        else:
            pending.append(row)
    if limit is not None:
        pending = pending[: max(0, limit)]

    semaphore = asyncio.Semaphore(concurrency)
    usage_lock = asyncio.Lock()
    completed = 0

    async def run_row(index: int, row: dict[str, Any]) -> dict[str, Any]:
        nonlocal completed
        async with semaphore:
            async with usage_lock:
                usage_snapshot = {class_id: usage[class_id] for class_id in sorted(class_ids)}
            result = await _request_one(
                clients=clients,
                settings=settings,
                run_dir=run_dir,
                inventory=inventory,
                inventory_row=row,
                class_rows=class_rows,
                usage_tiebreaker=usage_snapshot,
                client_index=index,
            )
            if result.get("status") == "received" and isinstance(result.get("proposal"), dict):
                try:
                    _validate_received_proposal(
                        result["proposal"],
                        inventory=inventory,
                        inventory_row=row,
                        class_ids=class_ids,
                    )
                except Exception as exc:
                    result = {
                        "template_slug": row["template_slug"],
                        "status": "failed",
                        "failure": f"{type(exc).__name__}:proposal_validation_failed",
                        "retry_count": result.get("retry_count", 0),
                    }
                else:
                    async with usage_lock:
                        usage.update(_usage_from_proposal(result["proposal"]))
                    result["status"] = "success"
            completed += 1
            print(
                json.dumps(
                    {
                        "completed": completed,
                        "scheduled": len(pending),
                        "status": result.get("status"),
                        "template_slug": row["template_slug"],
                    },
                    sort_keys=True,
                ),
                flush=True,
            )
            return result

    try:
        if pending:
            requested = await asyncio.gather(
                *(run_row(index, row) for index, row in enumerate(pending))
            )
            results.extend(requested)
    finally:
        await asyncio.gather(*(client.close() for client in clients))

    public_results = [
        {key: value for key, value in row.items() if key != "proposal"} for row in results
    ]
    stage = {
        "stage": "propose",
        "finished_at": _now(),
        "model": settings["model"],
        "thinking_level": THINKING_LEVEL,
        "thinking_budget": THINKING_BUDGET,
        "concurrency": concurrency,
        "scheduled_request_count": len(pending),
        "api_success_count": sum(row.get("status") == "success" for row in results),
        "cache_hit_count": sum(row.get("status") == "cache_hit" for row in results),
        "failure_count": sum(row.get("status") == "failed" for row in results),
        "retry_count": sum(int(row.get("retry_count", 0)) for row in results),
        "results": sorted(public_results, key=lambda row: str(row["template_slug"])),
    }
    _atomic_json(_run_path(run_dir, "proposal_summary.json"), stage)
    failures = [row for row in public_results if row.get("status") == "failed"]
    _atomic_json(
        _run_path(run_dir, "failures.json"),
        {
            "schema_version": SUMMARY_SCHEMA,
            "updated_at": _now(),
            "failure_count": len(failures),
            "failures": sorted(failures, key=lambda row: str(row["template_slug"])),
        },
    )
    return stage


def normalize_cache(run_dir: Path) -> dict[str, Any]:
    """Normalize cached first-pass responses without entering any API path."""

    inventory = load_inventory(run_dir)
    logical_sha, class_rows = _formal_classes()
    if logical_sha != inventory["formal_library_snapshot_sha256"]:
        raise ValueError("formal library changed after inventory")
    class_ids = {str(row["material_class_id"]) for row in class_rows}
    visual_rows = [row for row in inventory["templates"] if int(row["visual_callsite_count"]) > 0]
    failures: list[dict[str, Any]] = []
    template_audits: list[dict[str, Any]] = []
    normalization_count = 0
    reachability_proof_count = 0
    flat_pbr_correction_count = 0
    raw_flat_ids: list[str] = []

    for inventory_row in visual_rows:
        slug = str(inventory_row["template_slug"])
        response_path = _run_path(run_dir, "responses", f"{slug}.json")
        proposal_path = _run_path(run_dir, "proposals", f"{slug}.json")
        response_sha_before = _sha256_path(response_path)
        try:
            response = _json_object(response_path)
            content = response.get("content")
            if not isinstance(content, str):
                raise ValueError("cached response has no JSON content")
            raw = json.loads(content)
            if not isinstance(raw, dict):
                raise ValueError("cached response JSON root is not an object")
            raw_flat_ids.extend(
                str(row["callsite_id"])
                for row in raw.get("callsites", [])
                if isinstance(row, Mapping)
                and row.get("decision") == "flat_color"
                and isinstance(row.get("callsite_id"), str)
            )
            normalized, changes = _normalize_received_proposal(raw, inventory_row)
            second, second_changes = _normalize_received_proposal(normalized, inventory_row)
            if second != normalized or second_changes:
                raise ValueError("proposal normalizer is not idempotent")
            domain_audits = _validate_received_proposal(
                normalized,
                inventory=inventory,
                inventory_row=inventory_row,
                class_ids=class_ids,
            )
            if _sha256_path(response_path) != response_sha_before:
                raise ValueError("raw response cache changed during normalization")
            _atomic_json(proposal_path, normalized)
            audit = {
                "schema_version": NORMALIZATION_SCHEMA,
                "created_at": _now(),
                "template_slug": slug,
                "template_source_sha256": inventory_row["template_source_sha256"],
                "raw_response_path": response_path.as_posix(),
                "raw_response_sha256": response_sha_before,
                "raw_proposal_sha256": _digest(raw),
                "normalized_proposal_path": proposal_path.as_posix(),
                "normalized_proposal_sha256": _digest(normalized),
                "normalizations": changes,
                "domain_audits": domain_audits,
            }
            audit["normalization_audit_sha256"] = _digest(audit)
            audit_path = _run_path(run_dir, "normalizations", f"{slug}.json")
            _atomic_json(audit_path, audit)
            normalization_count += len(changes)
            reachability_proof_count += sum(
                row.get("kind") == "current_source_reachable_domain" for row in domain_audits
            )
            flat_pbr_correction_count += sum(
                row.get("reason") == "flat_color_hard_rule_pbr_correction" for row in changes
            )
            template_audits.append(
                {
                    "template_slug": slug,
                    "audit_path": audit_path.as_posix(),
                    "normalization_count": len(changes),
                    "domain_audit_count": len(domain_audits),
                }
            )
        except Exception as exc:
            failures.append(
                {
                    "stage": "normalize_cache",
                    "template_slug": slug,
                    "failure": f"{type(exc).__name__}:normalization_or_validation_failed",
                    "detail": str(exc),
                }
            )

    raw_flat_sha256 = _digest(sorted(raw_flat_ids))
    if len(raw_flat_ids) != EXPECTED_RAW_FLAT_COLOR_COUNT:
        raise ValueError(
            "reviewed raw flat-color count drifted; "
            f"expected={EXPECTED_RAW_FLAT_COLOR_COUNT}, got={len(raw_flat_ids)}"
        )
    if raw_flat_sha256 != EXPECTED_RAW_FLAT_COLOR_SHA256:
        raise ValueError("reviewed raw flat-color callsite set drifted")
    if flat_pbr_correction_count != EXPECTED_FLAT_PBR_CORRECTION_COUNT:
        raise ValueError(
            "reviewed flat-to-PBR correction count drifted; "
            f"expected={EXPECTED_FLAT_PBR_CORRECTION_COUNT}, "
            f"got={flat_pbr_correction_count}"
        )

    summary = {
        "schema_version": NORMALIZATION_SCHEMA,
        "finished_at": _now(),
        "status": "valid" if not failures else "blocked",
        "visual_generator_count": len(visual_rows),
        "normalized_generator_count": len(template_audits),
        "failure_count": len(failures),
        "normalization_count": normalization_count,
        "reachability_proof_count": reachability_proof_count,
        "flat_pbr_correction_count": flat_pbr_correction_count,
        "raw_flat_color_callsite_count": len(raw_flat_ids),
        "raw_flat_color_callsite_sha256": raw_flat_sha256,
        "templates": sorted(template_audits, key=lambda row: row["template_slug"]),
    }
    summary["normalization_summary_sha256"] = _digest(summary)
    _atomic_json(_run_path(run_dir, "normalization_summary.json"), summary)
    _atomic_json(
        _run_path(run_dir, "failures.json"),
        {
            "schema_version": SUMMARY_SCHEMA,
            "updated_at": _now(),
            "failure_count": len(failures),
            "failures": sorted(failures, key=lambda row: str(row["template_slug"])),
        },
    )
    if failures:
        raise ValueError(f"cache normalization failed for {len(failures)} templates")
    return summary


def _source_call_nodes(source: str, *, slug: str) -> dict[str, tuple[ast.Call, ast.keyword]]:
    tree = ast.parse(source)
    result: dict[str, tuple[ast.Call, ast.keyword]] = {}
    for node in ast.walk(tree):
        if not _visual_call(node):
            continue
        assert isinstance(node, ast.Call)
        _, keyword = _visual_name(node)
        callsite_id = f"{slug}:{node.lineno}:{node.col_offset}"
        if callsite_id in result:
            raise ValueError(f"duplicate visual callsite: {callsite_id}")
        result[callsite_id] = (node, keyword)
    return result


def _byte_offset(source: bytes, *, lineno: int, col_offset: int) -> int:
    if lineno < 1 or col_offset < 0:
        raise ValueError("invalid AST source position")
    lines = source.splitlines(keepends=True)
    if lineno > len(lines):
        raise ValueError("AST line is outside the source")
    line = lines[lineno - 1]
    if col_offset > len(line):
        raise ValueError("AST column is outside the source line")
    return sum(len(item) for item in lines[: lineno - 1]) + col_offset


def _python_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=True)


def _annotation_expression(
    row: Mapping[str, Any],
    *,
    use_material_helper: bool = False,
) -> str:
    branches = row.get("branches")
    if not isinstance(branches, list) or not branches:
        raise ValueError(f"material annotation has no branches: {row.get('callsite_id')}")
    if row.get("routing_kind") == GENERATOR_CLASS_ROLE_ROUTING_KIND:
        expression = row.get("config_expression")
        if not isinstance(expression, str):
            raise ValueError("role-routed annotation has no source material expression")
        return f"_material_class_id({expression})"
    if len(branches) == 1:
        class_id = branches[0].get("material_class_id")
        if not isinstance(class_id, str):
            raise ValueError("material branch has no scalar class ID")
        return _python_string(class_id)
    if len(branches) != 2:
        raise ValueError("final annotation exceeds max2")
    expression = row.get("config_expression")
    if not isinstance(expression, str):
        raise ValueError("dual-class annotation has no Config expression")
    first, second = branches
    first_id = first.get("material_class_id")
    second_id = second.get("material_class_id")
    values = first.get("config_values")
    if not isinstance(first_id, str) or not isinstance(second_id, str):
        raise ValueError("dual-class branch has no scalar class ID")
    if (
        not isinstance(values, list)
        or not values
        or not all(isinstance(value, str) for value in values)
    ):
        raise ValueError("dual-class condition values must be strings")
    if use_material_helper:
        if len(values) == 1:
            rendered_values = f"({_python_string(values[0])},)"
        else:
            rendered_values = "(" + ", ".join(_python_string(value) for value in values) + ")"
        return (
            f"_material_class_id({expression}, {rendered_values}, "
            f"{_python_string(first_id)}, {_python_string(second_id)})"
        )
    if len(values) == 1:
        condition = f"{expression} == {_python_string(values[0])}"
    else:
        rendered = ", ".join(_python_string(value) for value in values)
        condition = f"{expression} in {{{rendered}}}"
    return f"({_python_string(first_id)} if {condition} else {_python_string(second_id)})"


def apply_annotations_to_source(
    source: bytes,
    *,
    slug: str,
    annotation: Mapping[str, Any],
) -> tuple[bytes, list[dict[str, Any]]]:
    text = source.decode("utf-8")
    nodes = _source_call_nodes(text, slug=slug)
    annotation_rows = annotation.get("callsites")
    if not isinstance(annotation_rows, list):
        raise ValueError("annotation has no callsites list")
    by_id = {
        str(row["callsite_id"]): row
        for row in annotation_rows
        if isinstance(row, Mapping) and isinstance(row.get("callsite_id"), str)
    }
    if set(by_id) != set(nodes):
        raise ValueError("annotation and source callsite sets differ")
    helper_callsite_ids = set(by_id) & MATERIAL_HELPER_CALLSITE_IDS
    existing_helper = [
        node
        for node in ast.parse(text).body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "_material_class_id"
    ]
    if helper_callsite_ids and existing_helper:
        raise ValueError("source already defines _material_class_id")
    insertions: list[tuple[int, bytes, dict[str, Any]]] = []
    for callsite_id, row in by_id.items():
        node, name_keyword = nodes[callsite_id]
        decision = row.get("decision")
        if decision == "flat_color":
            if not any(keyword.arg == "material" for keyword in node.keywords):
                raise ValueError(
                    f"flat_color callsite lacks an explicit existing material: {callsite_id}"
                )
            continue
        if decision != "material_class":
            raise ValueError(f"unknown annotation decision at {callsite_id}")
        if any(keyword.arg == "material_class_id" for keyword in node.keywords):
            raise ValueError(f"source already has material_class_id at {callsite_id}")
        if name_keyword.end_lineno is None or name_keyword.end_col_offset is None:
            raise ValueError(f"name keyword has no AST end position at {callsite_id}")
        use_material_helper = callsite_id in helper_callsite_ids
        expression = _annotation_expression(
            row,
            use_material_helper=use_material_helper,
        )
        insertion = f", material_class_id={expression}".encode("ascii")
        if b"\n" in insertion:
            raise ValueError("material insertion must preserve source line count")
        offset = _byte_offset(
            source,
            lineno=name_keyword.end_lineno,
            col_offset=name_keyword.end_col_offset,
        )
        audit = {
            "callsite_id": callsite_id,
            "byte_offset": offset,
            "expression": expression,
            "writeback_mode": "material_helper" if use_material_helper else "inline_scalar",
            "material_class_ids": [
                branch["material_class_id"] for branch in row.get("branches", [])
            ],
        }
        insertions.append((offset, insertion, audit))
    output = source
    for offset, insertion, _ in sorted(insertions, key=lambda item: item[0], reverse=True):
        output = output[:offset] + insertion + output[offset:]
    if helper_callsite_ids:
        helper_definition = _material_helper_definition(slug)
        separator = b"\n\n" if output.endswith(b"\n") else b"\n\n\n"
        output += separator + helper_definition.encode("ascii")
    return output, [audit for _, _, audit in sorted(insertions, key=lambda item: item[0])]


def _verify_shadow_source(
    *,
    original: bytes,
    shadow: bytes,
    inventory_row: Mapping[str, Any],
    annotation: Mapping[str, Any] | None,
) -> dict[str, Any]:
    original_text = original.decode("utf-8")
    shadow_text = shadow.decode("utf-8")
    compile(shadow_text, str(inventory_row["relative_path"]), "exec")
    decisions = {} if annotation is None else _proposal_callsites(annotation)
    helper_callsite_ids = set(decisions) & MATERIAL_HELPER_CALLSITE_IDS
    original_tree = ast.parse(original_text)
    shadow_tree = ast.parse(shadow_text)
    original_helpers = [
        node
        for node in original_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "_material_class_id"
    ]
    shadow_helpers = [
        node
        for node in shadow_tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "_material_class_id"
    ]
    helper_line_delta = 0
    if helper_callsite_ids:
        if original_helpers:
            raise ValueError("original source already defines _material_class_id")
        helper_definition = _material_helper_definition(str(inventory_row["template_slug"]))
        expected_helper = ast.parse(helper_definition).body[0]
        if len(shadow_helpers) != 1 or _ast_hash(shadow_helpers[0]) != _ast_hash(expected_helper):
            raise ValueError("shadow source has an unexpected material-class helper")
        separator = b"\n\n" if original.endswith(b"\n") else b"\n\n\n"
        expected_suffix = separator + helper_definition.encode("ascii")
        if not shadow.endswith(expected_suffix):
            raise ValueError("material-class helper was not appended verbatim")
        helper_line_delta = expected_suffix.count(b"\n")
    elif [_ast_hash(node) for node in original_helpers] != [
        _ast_hash(node) for node in shadow_helpers
    ]:
        raise ValueError("shadow rewrite changed an existing material-class helper")
    if original_text.count("\n") + helper_line_delta != shadow_text.count("\n"):
        raise ValueError("shadow rewrite changed source line count outside the allowed helper")
    before_fingerprints = _source_fingerprints(original_text)
    after_fingerprints = _source_fingerprints(shadow_text)
    if before_fingerprints != after_fingerprints:
        raise ValueError(
            f"appearance rewrite changed mechanical AST: {inventory_row['template_slug']}"
        )
    before_nodes = _source_call_nodes(original_text, slug=str(inventory_row["template_slug"]))
    after_nodes = _source_call_nodes(shadow_text, slug=str(inventory_row["template_slug"]))
    if set(before_nodes) != set(after_nodes):
        raise ValueError("shadow rewrite changed visual callsite IDs")
    before_names = {
        callsite_id: _visual_name(node)[0] for callsite_id, (node, _) in before_nodes.items()
    }
    after_names = {
        callsite_id: _visual_name(node)[0] for callsite_id, (node, _) in after_nodes.items()
    }
    if before_names != after_names:
        raise ValueError("shadow rewrite changed visual names")

    pbr_count = 0
    flat_count = 0
    if annotation is None:
        if before_nodes:
            raise ValueError("composition-only source unexpectedly has visual callsites")
        if original != shadow:
            raise ValueError("composition-only source must remain byte-identical")
    else:
        for callsite_id, (node, _) in after_nodes.items():
            material_keywords = [
                keyword for keyword in node.keywords if keyword.arg == "material_class_id"
            ]
            decision = decisions[callsite_id].get("decision")
            if decision == "material_class":
                pbr_count += 1
                if len(material_keywords) != 1:
                    raise ValueError(f"PBR callsite lacks one scalar annotation: {callsite_id}")
                value = material_keywords[0].value
                use_material_helper = callsite_id in helper_callsite_ids
                expected_value = ast.parse(
                    _annotation_expression(
                        decisions[callsite_id],
                        use_material_helper=use_material_helper,
                    ),
                    mode="eval",
                ).body
                if _ast_hash(value) != _ast_hash(expected_value):
                    raise ValueError(f"material expression drifted at {callsite_id}")
                if use_material_helper:
                    if not (
                        isinstance(value, ast.Call)
                        and isinstance(value.func, ast.Name)
                        and value.func.id == "_material_class_id"
                    ):
                        raise ValueError(f"invalid material helper call at {callsite_id}")
                elif isinstance(value, ast.Constant) and isinstance(value.value, str):
                    pass
                elif (
                    isinstance(value, ast.IfExp)
                    and isinstance(value.body, ast.Constant)
                    and isinstance(value.body.value, str)
                    and isinstance(value.orelse, ast.Constant)
                    and isinstance(value.orelse.value, str)
                ):
                    pass
                else:
                    raise ValueError(f"non-scalar material expression at {callsite_id}")
            elif decision == "flat_color":
                flat_count += 1
                if material_keywords:
                    raise ValueError(f"flat_color callsite received a PBR class: {callsite_id}")
            else:
                raise ValueError(f"unknown decision at {callsite_id}")
    return {
        "original_sha256": _sha256_bytes(original),
        "shadow_sha256": _sha256_bytes(shadow),
        "source_line_count": original_text.count("\n") + (0 if original_text.endswith("\n") else 1),
        "visual_callsite_count": len(before_nodes),
        "pbr_visual_count": pbr_count,
        "flat_color_visual_count": flat_count,
        "material_class_helper_count": 1 if helper_callsite_ids else 0,
        **after_fingerprints,
    }


def _annotation_usage(
    annotations: Iterable[Mapping[str, Any]],
    *,
    class_ids: Iterable[str],
) -> dict[str, Any]:
    assignment: Counter[str] = Counter()
    callsite_mentions: Counter[str] = Counter()
    pbr = 0
    flat = 0
    constants = 0
    dual = 0
    compressed = 0
    role_routed = 0
    for annotation in annotations:
        for row in annotation.get("callsites", []):
            if row.get("decision") == "flat_color":
                flat += 1
                continue
            pbr += 1
            branches = row.get("branches", [])
            if len(branches) == 1:
                constants += 1
            elif len(branches) == 2:
                dual += 1
            if row.get("routing_kind") == GENERATOR_CLASS_ROLE_ROUTING_KIND:
                role_routed += 1
            if row.get("compression") is not None:
                compressed += 1
            seen: set[str] = set()
            for branch in branches:
                class_id = str(branch["material_class_id"])
                values = branch.get("config_values", [])
                assignment[class_id] += max(1, len(values))
                seen.add(class_id)
            callsite_mentions.update(seen)
    all_ids = sorted(set(class_ids))
    generic_ids = sorted(class_id for class_id in all_ids if "generic" in class_id)
    assignment_total = sum(assignment.values())
    mention_total = sum(callsite_mentions.values())
    most_assignment = sorted(assignment.items(), key=lambda item: (-item[1], item[0]))[:1]
    most_mentions = sorted(callsite_mentions.items(), key=lambda item: (-item[1], item[0]))[:1]
    return {
        "pbr_visual_count": pbr,
        "flat_color_visual_count": flat,
        "constant_class_callsite_count": constants,
        "dual_class_condition_callsite_count": dual,
        "compressed_callsite_count": compressed,
        "role_routed_helper_callsite_count": role_routed,
        "pool_usage_assignment_count": {class_id: assignment[class_id] for class_id in all_ids},
        "pool_usage_callsite_mentions": {
            class_id: callsite_mentions[class_id] for class_id in all_ids
        },
        "unused_material_class_ids": [
            class_id for class_id in all_ids if not callsite_mentions[class_id]
        ],
        "most_used_by_assignment": (
            {"material_class_id": most_assignment[0][0], "count": most_assignment[0][1]}
            if most_assignment
            else None
        ),
        "most_used_by_callsite_mentions": (
            {"material_class_id": most_mentions[0][0], "count": most_mentions[0][1]}
            if most_mentions
            else None
        ),
        "generic_material_class_ids": generic_ids,
        "generic_assignment_count": sum(assignment[class_id] for class_id in generic_ids),
        "generic_assignment_ratio": (
            sum(assignment[class_id] for class_id in generic_ids) / assignment_total
            if assignment_total
            else 0.0
        ),
        "generic_callsite_mention_count": sum(
            callsite_mentions[class_id] for class_id in generic_ids
        ),
        "generic_callsite_mention_ratio": (
            sum(callsite_mentions[class_id] for class_id in generic_ids) / mention_total
            if mention_total
            else 0.0
        ),
    }


def _api_totals(run_dir: Path, *, expected_visual_generators: int) -> dict[str, Any]:
    attempt_dir = _run_path(run_dir, "attempts")
    response_dir = _run_path(run_dir, "responses")
    attempts = sorted(attempt_dir.glob("*.json")) if attempt_dir.is_dir() else []
    responses = sorted(response_dir.glob("*.json")) if response_dir.is_dir() else []
    retry_count = 0
    attempt_count = 0
    terminal_failure_count = 0
    retry_reason_counts: Counter[str] = Counter()
    for path in attempts:
        row = _json_object(path)
        retry_count += int(row.get("retry_count", 0))
        attempt_count += int(row.get("attempt_count", 0))
        events = row.get("events", [])
        if not isinstance(events, list) or not events:
            terminal_failure_count += 1
            continue
        for event in events[:-1]:
            if not isinstance(event, Mapping) or event.get("status") != "transport_error":
                continue
            status_code = event.get("status_code")
            reason = str(status_code) if status_code is not None else str(event.get("error_type"))
            retry_reason_counts[reason] += 1
        terminal = events[-1]
        if not isinstance(terminal, Mapping) or terminal.get("status") != "response_received":
            terminal_failure_count += 1
    proposal_summary_path = _run_path(run_dir, "proposal_summary.json")
    proposal_summary = (
        _json_object(proposal_summary_path) if proposal_summary_path.is_file() else {}
    )
    return {
        "expected_api_generator_count": expected_visual_generators,
        "api_success_count": len(responses),
        "api_failure_count": terminal_failure_count,
        "api_response_cache_count": len(responses),
        "api_attempt_file_count": len(attempts),
        "api_attempt_count": attempt_count,
        "api_retry_count": retry_count,
        "api_retry_reason_counts": dict(sorted(retry_reason_counts.items())),
        "cache_hit_count": int(proposal_summary.get("cache_hit_count", 0)),
        "model": proposal_summary.get("model"),
        "thinking_level": THINKING_LEVEL,
        "thinking_budget": THINKING_BUDGET,
        "concurrency": proposal_summary.get("concurrency"),
    }


def build_shadow(run_dir: Path) -> dict[str, Any]:
    inventory = load_inventory(run_dir, verify_sources=False)
    logical_sha, class_rows = _formal_classes()
    if logical_sha != inventory["formal_library_snapshot_sha256"]:
        raise ValueError("formal library changed after inventory")
    class_ids = {str(row["material_class_id"]) for row in class_rows}
    failures: list[dict[str, Any]] = []
    manifest_rows: list[dict[str, Any]] = []
    annotations: list[dict[str, Any]] = []
    annotation_index: list[dict[str, Any]] = []
    prior_manifest_path = _run_path(run_dir, "shadow_manifest.json")
    prior_manifest = (
        _load_shadow_manifest(run_dir) if prior_manifest_path.is_file() else {"templates": []}
    )
    prior_manifest_by_slug = {
        str(row["template_slug"]): dict(row)
        for row in prior_manifest.get("templates", [])
        if isinstance(row, Mapping) and isinstance(row.get("template_slug"), str)
    }
    writeback_state_path = _run_path(run_dir, "writeback_state.json")
    writeback_state = _json_object(writeback_state_path) if writeback_state_path.is_file() else {}
    written_rows = writeback_state.get("templates", {})
    if not isinstance(written_rows, Mapping):
        raise ValueError("invalid prior writeback state")
    prior_summary_path = _run_path(run_dir, "summary.json")
    prior_summary = _json_object(prior_summary_path) if prior_summary_path.is_file() else {}

    for inventory_row in inventory["templates"]:
        slug = str(inventory_row["template_slug"])
        live_source_path = _contained(
            REPO_ROOT / str(inventory_row["relative_path"]),
            root=TEMPLATE_ROOT,
            must_exist=True,
        )
        live_source_sha256 = _sha256_path(live_source_path)
        allowed_live_sha256 = {str(inventory_row["template_source_sha256"])}
        prior_manifest_row = prior_manifest_by_slug.get(slug, {})
        for field in ("shadow_sha256", "previous_shadow_sha256"):
            value = prior_manifest_row.get(field)
            if isinstance(value, str):
                allowed_live_sha256.add(value)
        written_row = written_rows.get(slug)
        if isinstance(written_row, Mapping) and isinstance(written_row.get("sha256"), str):
            allowed_live_sha256.add(str(written_row["sha256"]))
        if live_source_sha256 not in allowed_live_sha256:
            raise ValueError(f"template changed outside this migration: {live_source_path.name}")
        original_path = _run_path(run_dir, "original", str(inventory_row["relative_path"]))
        source = (
            original_path.read_bytes() if original_path.is_file() else live_source_path.read_bytes()
        )
        if _sha256_bytes(source) != inventory_row["template_source_sha256"]:
            raise ValueError(f"staged original source drifted for {slug}")
        _atomic_bytes(original_path, source)
        shadow_path = _run_path(run_dir, "shadow", str(inventory_row["relative_path"]))
        if int(inventory_row["visual_callsite_count"]) == 0:
            try:
                verification = _verify_shadow_source(
                    original=source,
                    shadow=source,
                    inventory_row=inventory_row,
                    annotation=None,
                )
                _atomic_bytes(shadow_path, source)
                manifest_rows.append(
                    {
                        "template_slug": slug,
                        "relative_path": inventory_row["relative_path"],
                        "status": "composition_dependency_verified",
                        "annotation_path": None,
                        "insertions": [],
                        "previous_shadow_sha256": live_source_sha256,
                        **verification,
                    }
                )
            except Exception as exc:
                failures.append(
                    {
                        "stage": "shadow",
                        "template_slug": slug,
                        "failure": f"{type(exc).__name__}:composition_verification_failed",
                    }
                )
            continue

        proposal_path = _run_path(run_dir, "proposals", f"{slug}.json")
        annotation_path = _run_path(run_dir, "annotations", f"{slug}.json")
        if not proposal_path.is_file():
            failures.append(
                {
                    "stage": "shadow",
                    "template_slug": slug,
                    "failure": "missing_proposal",
                }
            )
            continue
        try:
            proposal = _json_object(proposal_path)
            validate_proposal_source_domains(
                proposal,
                inventory_row,
                source_override=source.decode("utf-8"),
            )
            annotation = annotation_builder.build_file(
                proposals_path=proposal_path,
                template_path=original_path,
                library_path=FORMAL_LIBRARY,
                output_path=annotation_path,
            )
            annotation, role_routing_audits = _apply_role_routed_annotation_overrides(
                annotation,
                inventory_row,
            )
            _atomic_json(annotation_path, annotation)
            validated = annotation_builder.validate_file(
                annotations_path=annotation_path,
                template_path=original_path,
                library_path=FORMAL_LIBRARY,
            )
            if annotation != validated:
                raise ValueError("builder validation did not round-trip canonically")
            shadow, insertions = apply_annotations_to_source(
                source,
                slug=slug,
                annotation=annotation,
            )
            verification = _verify_shadow_source(
                original=source,
                shadow=shadow,
                inventory_row=inventory_row,
                annotation=annotation,
            )
            _atomic_bytes(shadow_path, shadow)
            annotations.append(annotation)
            annotation_index.append(
                {
                    "template_slug": slug,
                    "path": annotation_path.as_posix(),
                    "annotation_sha256": _sha256_path(annotation_path),
                    "callsite_count": len(annotation["callsites"]),
                }
            )
            manifest_rows.append(
                {
                    "template_slug": slug,
                    "relative_path": inventory_row["relative_path"],
                    "status": "valid",
                    "annotation_path": annotation_path.as_posix(),
                    "insertions": insertions,
                    "role_routing_audits": role_routing_audits,
                    "previous_shadow_sha256": live_source_sha256,
                    **verification,
                }
            )
        except Exception as exc:
            failures.append(
                {
                    "stage": "shadow",
                    "template_slug": slug,
                    "failure": f"{type(exc).__name__}:annotation_or_shadow_validation_failed",
                }
            )

    by_name = {
        f"{row['template_slug']}.py": row for row in manifest_rows if row["status"] == "valid"
    }
    for composition_name, dependencies in COMPOSITION_DEPENDENCIES.items():
        composition_row = next(
            (
                row
                for row in manifest_rows
                if Path(str(row["relative_path"])).name == composition_name
            ),
            None,
        )
        if composition_row is None:
            continue
        missing = [name for name in dependencies if name not in by_name]
        if missing:
            failures.append(
                {
                    "stage": "shadow",
                    "template_slug": Path(composition_name).stem,
                    "failure": "composition_dependencies_not_fully_annotated",
                    "missing_dependencies": missing,
                }
            )
        else:
            composition_row["dependency_templates"] = list(dependencies)
            composition_row["dependency_visual_callsite_count"] = sum(
                int(by_name[name]["visual_callsite_count"]) for name in dependencies
            )

    for name, expected in inventory["canary_sha256"].items():
        actual = _sha256_path(TEMPLATE_ROOT / name)
        if actual != expected:
            failures.append(
                {
                    "stage": "shadow",
                    "template_slug": Path(name).stem,
                    "failure": "canary_sha256_changed",
                }
            )

    manifest_status = (
        "valid"
        if not failures and len(manifest_rows) == int(inventory["generator_count"])
        else "blocked"
    )
    manifest = {
        "schema_version": SHADOW_MANIFEST_SCHEMA,
        "created_at": _now(),
        "status": manifest_status,
        "inventory_sha256": inventory["inventory_sha256"],
        "formal_library_snapshot_sha256": logical_sha,
        "generator_count": len(manifest_rows),
        "canary_sha256_before": inventory["canary_sha256"],
        "canary_sha256_after": {name: _sha256_path(TEMPLATE_ROOT / name) for name in CANARY_FILES},
        "templates": sorted(manifest_rows, key=lambda row: str(row["template_slug"])),
    }
    manifest["shadow_manifest_sha256"] = _digest(manifest)
    _atomic_json(_run_path(run_dir, "shadow_manifest.json"), manifest)
    _atomic_json(
        _run_path(run_dir, "annotations", "index.json"),
        {
            "schema_version": SUMMARY_SCHEMA,
            "formal_library_snapshot_sha256": logical_sha,
            "annotation_count": len(annotation_index),
            "annotations": sorted(annotation_index, key=lambda row: row["template_slug"]),
        },
    )
    _atomic_json(
        _run_path(run_dir, "failures.json"),
        {
            "schema_version": SUMMARY_SCHEMA,
            "updated_at": _now(),
            "failure_count": len(failures),
            "failures": sorted(
                failures,
                key=lambda row: (str(row.get("template_slug")), str(row.get("failure"))),
            ),
        },
    )
    usage = _annotation_usage(annotations, class_ids=class_ids)
    api = _api_totals(
        run_dir,
        expected_visual_generators=int(inventory["visual_generator_count"]),
    )
    summary = {
        "schema_version": SUMMARY_SCHEMA,
        "updated_at": _now(),
        "status": "shadow_valid" if manifest_status == "valid" else "blocked",
        "run_dir": _contained(run_dir, root=REPO_ROOT).as_posix(),
        "inventory_path": _run_path(run_dir, "inventory.json").as_posix(),
        "annotation_path": _run_path(run_dir, "annotations", "index.json").as_posix(),
        "failure_path": _run_path(run_dir, "failures.json").as_posix(),
        "shadow_manifest_path": _run_path(run_dir, "shadow_manifest.json").as_posix(),
        "formal_library_snapshot_sha256": logical_sha,
        "formal_material_count": 8295,
        "formal_material_class_count": len(class_ids),
        "processed_generator_count": len(manifest_rows),
        "visual_generator_count": int(inventory["visual_generator_count"]),
        "composition_only_generator_count": int(inventory["composition_only_count"]),
        "visual_callsite_count": sum(int(row["visual_callsite_count"]) for row in manifest_rows),
        "material_class_helper_generator_count": sum(
            int(row["material_class_helper_count"]) for row in manifest_rows
        ),
        "shadow_valid_generator_count": len(manifest_rows) if manifest_status == "valid" else 0,
        "blocked_generator_count": len(failures),
        "writeback": {
            "status": "not_started",
            "successful_generator_count": 0,
            "modified_template_count": 0,
        },
        "api": api,
        "usage": usage,
        "canary_sha256": inventory["canary_sha256"],
        "source_invariance": {
            "callsite_ids_preserved": manifest_status == "valid",
            "geometry_parts_joints_origins_config_rng_preserved": manifest_status == "valid",
            "palette_rgba_preserved": manifest_status == "valid",
        },
    }
    if isinstance(prior_summary.get("gates"), Mapping):
        summary["gates"] = dict(prior_summary["gates"])
    if isinstance(prior_summary.get("required_gates"), list):
        summary["required_gates"] = list(prior_summary["required_gates"])
    _atomic_json(_run_path(run_dir, "summary.json"), summary)
    return summary


def _load_shadow_manifest(run_dir: Path) -> dict[str, Any]:
    manifest = _json_object(_run_path(run_dir, "shadow_manifest.json"))
    if manifest.get("schema_version") != SHADOW_MANIFEST_SCHEMA:
        raise ValueError("unsupported shadow manifest schema")
    expected = manifest.get("shadow_manifest_sha256")
    unsigned = dict(manifest)
    unsigned.pop("shadow_manifest_sha256", None)
    if expected != _digest(unsigned):
        raise ValueError("shadow manifest content digest mismatch")
    return manifest


def _verify_staged_template(
    run_dir: Path,
    *,
    inventory_row: Mapping[str, Any],
    manifest_row: Mapping[str, Any],
) -> None:
    relative_path = str(inventory_row["relative_path"])
    original_path = _run_path(run_dir, "original", relative_path)
    shadow_path = _run_path(run_dir, "shadow", relative_path)
    original = _contained(original_path, root=REPO_ROOT, must_exist=True).read_bytes()
    shadow = _contained(shadow_path, root=REPO_ROOT, must_exist=True).read_bytes()
    if _sha256_bytes(original) != inventory_row["template_source_sha256"]:
        raise ValueError(f"staged original SHA mismatch: {inventory_row['template_slug']}")
    if _sha256_bytes(shadow) != manifest_row["shadow_sha256"]:
        raise ValueError(f"staged shadow SHA mismatch: {inventory_row['template_slug']}")
    annotation: Mapping[str, Any] | None
    annotation_path = manifest_row.get("annotation_path")
    if annotation_path is None:
        annotation = None
    else:
        annotation = _json_object(Path(str(annotation_path)))
    verification = _verify_shadow_source(
        original=original,
        shadow=shadow,
        inventory_row=inventory_row,
        annotation=annotation,
    )
    for field in (
        "original_sha256",
        "shadow_sha256",
        "source_line_count",
        "visual_callsite_count",
        "pbr_visual_count",
        "flat_color_visual_count",
        "material_class_helper_count",
        "mechanical_ast_sha256",
        "config_ast_sha256",
        "rng_ast_sha256",
        "entity_ast_sha256",
    ):
        if verification[field] != manifest_row[field]:
            raise ValueError(
                f"staged verification field drift for {inventory_row['template_slug']}: {field}"
            )


def writeback(run_dir: Path) -> dict[str, Any]:
    inventory = load_inventory(run_dir, verify_sources=False)
    manifest = _load_shadow_manifest(run_dir)
    if manifest.get("status") != "valid":
        raise ValueError("global shadow manifest is not valid; writeback is blocked")
    if manifest.get("inventory_sha256") != inventory["inventory_sha256"]:
        raise ValueError("shadow manifest inventory mismatch")
    inventory_by_slug = _template_by_slug(inventory)
    manifest_by_slug = {str(row["template_slug"]): row for row in manifest.get("templates", [])}
    if set(inventory_by_slug) != set(manifest_by_slug):
        raise ValueError("shadow manifest does not cover every remaining generator")

    for name, expected in inventory["canary_sha256"].items():
        if _sha256_path(TEMPLATE_ROOT / name) != expected:
            raise ValueError(f"canary changed before writeback: {name}")
    for slug, inventory_row in inventory_by_slug.items():
        _verify_staged_template(
            run_dir,
            inventory_row=inventory_row,
            manifest_row=manifest_by_slug[slug],
        )
        target = _contained(
            REPO_ROOT / str(inventory_row["relative_path"]),
            root=TEMPLATE_ROOT,
            must_exist=True,
        )
        current_sha = _sha256_path(target)
        allowed = {
            str(inventory_row["template_source_sha256"]),
            str(manifest_by_slug[slug]["shadow_sha256"]),
        }
        previous_shadow_sha = manifest_by_slug[slug].get("previous_shadow_sha256")
        if isinstance(previous_shadow_sha, str):
            allowed.add(previous_shadow_sha)
        if current_sha not in allowed:
            raise ValueError(f"template changed outside this migration: {target.name}")

    state_path = _run_path(run_dir, "writeback_state.json")
    if state_path.is_file():
        state = _json_object(state_path)
    else:
        state = {
            "schema_version": SUMMARY_SCHEMA,
            "started_at": _now(),
            "status": "in_progress",
            "templates": {},
        }
    completed = state.get("templates")
    if not isinstance(completed, dict):
        raise ValueError("invalid writeback state")

    modified = 0
    for slug in sorted(inventory_by_slug):
        inventory_row = inventory_by_slug[slug]
        manifest_row = manifest_by_slug[slug]
        target = _contained(
            REPO_ROOT / str(inventory_row["relative_path"]),
            root=TEMPLATE_ROOT,
            must_exist=True,
        )
        shadow_path = _contained(
            _run_path(run_dir, "shadow", str(inventory_row["relative_path"])),
            root=REPO_ROOT,
            must_exist=True,
        )
        before_sha = _sha256_path(target)
        shadow_sha = str(manifest_row["shadow_sha256"])
        if before_sha != shadow_sha:
            _atomic_bytes(target, shadow_path.read_bytes())
            modified += 1
        if _sha256_path(target) != shadow_sha:
            raise ValueError(f"atomic template writeback did not publish exact shadow: {slug}")
        completed[slug] = {
            "finished_at": _now(),
            "relative_path": inventory_row["relative_path"],
            "sha256": shadow_sha,
            "status": (
                "composition_unchanged"
                if manifest_row["status"] == "composition_dependency_verified"
                else "written"
            ),
        }
        state["templates"] = completed
        state["completed_generator_count"] = len(completed)
        _atomic_json(state_path, state)

    for name, expected in inventory["canary_sha256"].items():
        if _sha256_path(TEMPLATE_ROOT / name) != expected:
            raise ValueError(f"canary changed during writeback: {name}")
    state["status"] = "complete"
    state["finished_at"] = _now()
    state["completed_generator_count"] = len(completed)
    state["modified_template_count_this_invocation"] = modified
    state["modified_template_count"] = sum(row["status"] == "written" for row in completed.values())
    _atomic_json(state_path, state)

    summary_path = _run_path(run_dir, "summary.json")
    summary = _json_object(summary_path)
    summary["updated_at"] = _now()
    summary["status"] = "writeback_complete"
    summary["writeback"] = {
        "status": "complete",
        "successful_generator_count": len(completed),
        "modified_template_count": int(state["modified_template_count"]),
        "composition_unchanged_count": sum(
            row["status"] == "composition_unchanged" for row in completed.values()
        ),
        "state_path": state_path.as_posix(),
    }
    _atomic_json(summary_path, summary)
    return summary


def verify_writeback(run_dir: Path) -> dict[str, Any]:
    inventory = load_inventory(run_dir, verify_sources=False)
    manifest = _load_shadow_manifest(run_dir)
    if manifest.get("status") != "valid":
        raise ValueError("cannot verify a blocked shadow manifest")
    inventory_by_slug = _template_by_slug(inventory)
    manifest_by_slug = {str(row["template_slug"]): row for row in manifest.get("templates", [])}
    failures: list[dict[str, Any]] = []
    for slug, inventory_row in inventory_by_slug.items():
        try:
            manifest_row = manifest_by_slug[slug]
            _verify_staged_template(
                run_dir,
                inventory_row=inventory_row,
                manifest_row=manifest_row,
            )
            target = _contained(
                REPO_ROOT / str(inventory_row["relative_path"]),
                root=TEMPLATE_ROOT,
                must_exist=True,
            )
            if _sha256_path(target) != manifest_row["shadow_sha256"]:
                raise ValueError("live generator does not equal the validated shadow")
        except Exception as exc:
            failures.append(
                {
                    "stage": "verify_writeback",
                    "template_slug": slug,
                    "failure": f"{type(exc).__name__}:live_source_verification_failed",
                }
            )
    for name, expected in inventory["canary_sha256"].items():
        if _sha256_path(TEMPLATE_ROOT / name) != expected:
            failures.append(
                {
                    "stage": "verify_writeback",
                    "template_slug": Path(name).stem,
                    "failure": "canary_sha256_changed",
                }
            )
    _atomic_json(
        _run_path(run_dir, "failures.json"),
        {
            "schema_version": SUMMARY_SCHEMA,
            "updated_at": _now(),
            "failure_count": len(failures),
            "failures": failures,
        },
    )
    summary_path = _run_path(run_dir, "summary.json")
    summary = _json_object(summary_path)
    summary["updated_at"] = _now()
    summary["status"] = "verified" if not failures else "blocked"
    summary["blocked_generator_count"] = len({row["template_slug"] for row in failures})
    summary["final_source_verification"] = {
        "status": "pass" if not failures else "fail",
        "verified_generator_count": len(inventory_by_slug) - len(failures),
        "callsite_ids_preserved": not failures,
        "geometry_parts_joints_origins_config_rng_preserved": not failures,
        "canary_sha256_preserved": not any(
            row["failure"] == "canary_sha256_changed" for row in failures
        ),
    }
    _atomic_json(summary_path, summary)
    if failures:
        raise ValueError(f"writeback verification failed for {len(failures)} templates")
    return summary


def record_gates(run_dir: Path, results: Sequence[str]) -> dict[str, Any]:
    summary_path = _run_path(run_dir, "summary.json")
    summary = _json_object(summary_path)
    gates: dict[str, str] = {}
    for raw in results:
        name, separator, status = raw.partition("=")
        if separator != "=" or not name.strip() or status not in {"pass", "fail", "not_run"}:
            raise ValueError(f"invalid gate result: {raw!r}")
        gates[name.strip()] = status
    summary["updated_at"] = _now()
    summary["gates"] = dict(sorted(gates.items()))
    summary["required_gates"] = sorted(REQUIRED_FINAL_GATES)
    if (
        summary.get("status") == "verified"
        and set(gates) == REQUIRED_FINAL_GATES
        and all(gates[name] == "pass" for name in REQUIRED_FINAL_GATES)
    ):
        summary["status"] = "complete"
    _atomic_json(summary_path, summary)
    return summary


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    inventory = subparsers.add_parser("inventory", help="inventory current generator sources")
    inventory.add_argument("--run-dir", type=Path, required=True)
    propose = subparsers.add_parser(
        "propose", help="request and cache one Qwen proposal per generator"
    )
    propose.add_argument("--run-dir", type=Path, required=True)
    propose.add_argument("--concurrency", type=int, default=MAX_CONCURRENCY)
    propose.add_argument("--limit", type=int, default=None)
    normalize = subparsers.add_parser(
        "normalize-cache",
        help="strictly normalize cached first-pass responses without API access",
    )
    normalize.add_argument("--run-dir", type=Path, required=True)
    shadow = subparsers.add_parser("shadow", help="build annotations and validate the shadow tree")
    shadow.add_argument("--run-dir", type=Path, required=True)
    publish = subparsers.add_parser("writeback", help="atomically publish a globally valid shadow")
    publish.add_argument("--run-dir", type=Path, required=True)
    verify = subparsers.add_parser("verify", help="verify live generators against the shadow")
    verify.add_argument("--run-dir", type=Path, required=True)
    gates = subparsers.add_parser("record-gates", help="record externally executed final gates")
    gates.add_argument("--run-dir", type=Path, required=True)
    gates.add_argument("--result", action="append", default=[], required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    run_dir = _contained(args.run_dir, root=REPO_ROOT)
    if args.command == "inventory":
        result = build_inventory(run_dir)
        public = {
            "generator_count": result["generator_count"],
            "inventory_sha256": result["inventory_sha256"],
            "status": "valid",
            "visual_callsite_count": result["visual_callsite_count"],
        }
    elif args.command == "propose":
        public = asyncio.run(propose_all(run_dir, concurrency=args.concurrency, limit=args.limit))
    elif args.command == "normalize-cache":
        public = normalize_cache(run_dir)
    elif args.command == "shadow":
        public = build_shadow(run_dir)
    elif args.command == "writeback":
        public = writeback(run_dir)
    elif args.command == "verify":
        public = verify_writeback(run_dir)
    else:
        public = record_gates(run_dir, args.result)
    print(json.dumps(public, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
