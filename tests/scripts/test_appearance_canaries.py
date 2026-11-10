# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import ast
import importlib
import json
import re
from functools import lru_cache
from pathlib import Path

import pytest

from articraft.appearance import appearance_requests_from_model
from articraft.appearance.pool_runtime import POINTER_SCHEMA, POOL_INDEX_SCHEMA
from scripts.check_appearance_mechanical_invariance import (
    config_mechanical_fingerprint,
    object_model_mechanical_fingerprint,
)
from sdk import AppearanceOnlySpec, Material

CANARIES = {
    "Container_Glass_bottle": {
        "build": "build_container_glass_bottle",
        "visual_calls": 16,
        "material_calls": 16,
        "appearance_calls": 0,
        "config": "3b4a0a02811e574618072f566bf729c1c2c7ec7b3dd00b91c080c4d33c24ecdc",
        "mechanical": "4972f9ef2432ff6a86ae6e95801aca9841c770db0319072e467eaa5071ae182d",
    },
    "Container_Plastic_can": {
        "build": "build_container_plastic_can",
        "visual_calls": 9,
        "material_calls": 7,
        "appearance_calls": 2,
        "config": "f1028bfc8f620b18158fdb2d578502bbabaad1f5eaf8c7092ba14f5f1529b8bc",
        "mechanical": "c8bc838233541cff45488040d4299df678f841231f4163b3c51b4bb19dece8a0",
    },
    "Handtools_clothes_peg": {
        "build": "build_clothes_peg",
        "visual_calls": 5,
        "material_calls": 5,
        "appearance_calls": 0,
        "config": "c98db09599a9075f4e935052fc2e178a0bc032d62329e5767a76f59cdd126f9d",
        "mechanical": "52d5b054a66e17a0794014972bea095f258cfb3b78dd92a796a6764b4597c462",
    },
    "Urban_Environment_Large_Trashcan": {
        "build": "build_large_trashcan",
        "visual_calls": 9,
        "material_calls": 9,
        "appearance_calls": 0,
        "config": "413b03f0be609be63dfa2add0b73f2b76c86349b206991830406ef67d686b256",
        "mechanical": "df4b314cc76762f302d61ee5bb836494327bc2446ea97c26491fd957f1928e7e",
    },
    "loom_shuttle": {
        "build": "build_loom_shuttle",
        "visual_calls": 30,
        "material_calls": 29,
        "appearance_calls": 1,
        "config": "c36e1000ce94ebede6fda07ce1df46cc56cee90e78f53d672b8d3d8a899e9fd1",
        "mechanical": "e4efbc5cc967d033cf47190421d0abb902eebfa159d287182cbe942573f46ec6",
    },
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_ROOT = PROJECT_ROOT / "agent" / "templates"
PBR_LIBRARY_ROOT = PROJECT_ROOT / "pbr_material_library"

LEGACY_PBR_IDENTIFIERS = {
    "AppearanceRelation",
    "SurfaceBinding",
    "appearance",
    "blenderkit_category",
    "condition_key",
    "finish_hints",
    "GraphicIntent",
    "cavity_mode",
    "graphic",
    "host_surface_slot",
    "mapping_mode",
    "material_class_ids",
    "optical_profile",
    "physical_scale_m",
    "query_terms",
    "relations",
    "reuse_group",
}
MATERIAL_CLASS_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$")


def _iter_visuals(model):
    for part in model.parts:
        for index, visual in enumerate(part.visuals):
            yield f"{part.name}::{visual.name or f'visual_{index}'}", visual


def _keyword(call: ast.Call, name: str) -> ast.keyword | None:
    return next((item for item in call.keywords if item.arg == name), None)


def _visual_calls(tree: ast.AST) -> list[ast.Call]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "visual"
    ]


def _contained_library_path(relative_path: object) -> Path:
    assert isinstance(relative_path, str) and relative_path
    root = PBR_LIBRARY_ROOT.resolve()
    resolved = (root / relative_path).resolve()
    assert resolved.is_relative_to(root), f"library pointer escapes root: {relative_path!r}"
    return resolved


@lru_cache(maxsize=1)
def _formal_class_supply() -> dict[str, int]:
    """Load only the small control files, never all 8,295 material packages."""

    if not (PBR_LIBRARY_ROOT / "latest.json").is_file():
        pytest.skip("formal material-library snapshot is distributed separately")
    pointer = json.loads((PBR_LIBRARY_ROOT / "latest.json").read_text(encoding="utf-8"))
    assert pointer["schema_version"] == POINTER_SCHEMA
    pool_index = json.loads(
        _contained_library_path(pointer["pool_index_path"]).read_text(encoding="utf-8")
    )
    assert pool_index["schema_version"] == POOL_INDEX_SCHEMA
    supply = {
        row["material_class_id"]: row["material_count"]
        for row in pool_index["pools"]
        if isinstance(row, dict)
        and isinstance(row.get("material_class_id"), str)
        and isinstance(row.get("material_count"), int)
    }
    assert pool_index["class_count"] == len(supply)
    assert pool_index["nonempty_class_count"] == len(supply)
    assert pool_index["empty_class_count"] == 0
    assert all(count > 0 for count in supply.values())
    return supply


@pytest.mark.parametrize("slug", CANARIES)
def test_canary_visual_calls_use_the_strict_annotation_contract(slug: str) -> None:
    case = CANARIES[slug]
    source = TEMPLATE_ROOT.joinpath(f"{slug}.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    calls = _visual_calls(tree)

    assert len(calls) == case["visual_calls"]
    material_calls = [call for call in calls if _keyword(call, "material_class_id")]
    appearance_calls = [call for call in calls if _keyword(call, "appearance_only")]
    assert len(material_calls) == case["material_calls"]
    assert len(appearance_calls) == case["appearance_calls"]

    invalid = [
        call.lineno
        for call in calls
        if (_keyword(call, "material_class_id") is None)
        == (_keyword(call, "appearance_only") is None)
    ]
    assert not invalid, (
        f"{slug}: each visual must declare exactly one of material_class_id or "
        f"appearance_only; invalid lines={invalid}"
    )


def test_five_canaries_have_66_class_calls_and_three_appearance_only_calls() -> None:
    material_count = 0
    appearance_count = 0
    for slug in CANARIES:
        tree = ast.parse(TEMPLATE_ROOT.joinpath(f"{slug}.py").read_text(encoding="utf-8"))
        calls = _visual_calls(tree)
        material_count += sum(_keyword(call, "material_class_id") is not None for call in calls)
        appearance_count += sum(_keyword(call, "appearance_only") is not None for call in calls)

    assert (material_count, appearance_count) == (66, 3)


@pytest.mark.parametrize("seed", (0, 1))
def test_trashcan_repeated_parts_share_automatic_selection_groups(seed: int) -> None:
    module = importlib.import_module("agent.templates.Urban_Environment_Large_Trashcan")
    model = module.build_large_trashcan(module.config_from_seed(seed))
    requests = appearance_requests_from_model(model)

    groups = {
        role: {
            request.selection_group_key
            for request in requests
            if request.surface_key.startswith(prefix) and marker in request.surface_key
        }
        for role, prefix, marker in (
            ("lids", "lid_", "::lid_panel_"),
            ("rims", "wheel_", "::rim_"),
            ("tires", "wheel_", "::tire_"),
        )
    }

    assert all(len(group_keys) == 1 for group_keys in groups.values())
    assert all(
        selection_group_key.startswith("material:trashcan_")
        for group_keys in groups.values()
        for selection_group_key in group_keys
    )


@pytest.mark.parametrize("slug", CANARIES)
def test_old_pbr_binding_semantics_are_absent_from_canary_source(slug: str) -> None:
    source = TEMPLATE_ROOT.joinpath(f"{slug}.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    identifiers = (
        {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
        | {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
        | {node.arg for node in ast.walk(tree) if isinstance(node, ast.keyword) and node.arg}
    )
    assert "_appearance_binding" not in identifiers
    assert not (identifiers & LEGACY_PBR_IDENTIFIERS), (
        f"{slug}: legacy PBR authoring fields remain: "
        f"{sorted(identifiers & LEGACY_PBR_IDENTIFIERS)}"
    )


@pytest.mark.parametrize("slug", CANARIES)
def test_every_authored_class_branch_exists_in_the_formal_library(slug: str) -> None:
    source = TEMPLATE_ROOT.joinpath(f"{slug}.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    helpers = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "_material_class_id"
    ]
    assert len(helpers) == 1
    authored_classes = {
        node.value
        for node in ast.walk(helpers[0])
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and MATERIAL_CLASS_ID_RE.fullmatch(node.value)
    }
    assert authored_classes, f"{slug}: no material classes found in _material_class_id"

    supply = _formal_class_supply()
    missing_or_empty = {
        material_class_id: supply.get(material_class_id, 0)
        for material_class_id in authored_classes
        if supply.get(material_class_id, 0) <= 0
    }
    assert not missing_or_empty, (
        f"{slug}: authored classes absent or empty in formal library: {missing_or_empty}"
    )


@pytest.mark.parametrize("slug", CANARIES)
@pytest.mark.parametrize("seed", range(6))
def test_canary_seeds_resolve_to_formal_classes_and_preserve_mechanics(
    slug: str,
    seed: int,
) -> None:
    case = CANARIES[slug]
    module = importlib.import_module(f"agent.templates.{slug}")
    config = module.config_from_seed(seed)
    model = getattr(module, case["build"])(config)
    visuals = list(_iter_visuals(model))
    requests = {row.surface_key: row for row in appearance_requests_from_model(model)}
    class_supply = _formal_class_supply()

    assert visuals, f"{slug} seed={seed}: no visuals emitted"
    assert set(requests) == {visual_id for visual_id, _visual in visuals}
    for visual_id, visual in visuals:
        request = requests[visual_id]
        if visual.material_class_id is not None:
            assert isinstance(visual.material_class_id, str)
            assert class_supply.get(visual.material_class_id, 0) > 0, (
                f"{slug} seed={seed} {visual_id}: class is absent or empty in formal library: "
                f"{visual.material_class_id!r}"
            )
            assert request.material_class_id == visual.material_class_id
            assert request.asset_type in {"pbr_material", "optical_material"}
            assert request.rgba is None
            continue

        assert isinstance(visual.material, Material)
        assert visual.material.rgba is not None
        assert isinstance(visual.appearance_only, AppearanceOnlySpec)
        assert request.asset_type == "appearance_only"
        assert request.material_class_id is None
        assert request.rgba == visual.material.rgba
        assert request.appearance_only == visual.appearance_only

    model.validate(strict=True)
    if seed == 0:
        assert config_mechanical_fingerprint(config) == case["config"]
        assert object_model_mechanical_fingerprint(model) == case["mechanical"]
