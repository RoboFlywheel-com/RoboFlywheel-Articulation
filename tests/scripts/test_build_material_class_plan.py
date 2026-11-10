# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import pytest

from articraft.appearance import (
    MATERIAL_CLASS_ASSIGNMENTS_SCHEMA,
    MATERIAL_CLASS_POLICY_VERSION,
    MATERIAL_CLASS_REGISTRY_SCHEMA,
    MaterialCatalog,
    MaterialClassAssignments,
    MaterialClassRegistry,
    MaterialRecord,
)
from scripts import build_material_class_plan as target


def _registry() -> MaterialClassRegistry:
    return MaterialClassRegistry.from_dict(
        {
            "schema_version": MATERIAL_CLASS_REGISTRY_SCHEMA,
            "policy_version": MATERIAL_CLASS_POLICY_VERSION,
            "classes": [
                {
                    "material_class_id": "metal.brushed_steel",
                    "parent_category": "metal",
                    "display_name": "Brushed steel",
                    "description": "Directional brushed steel.",
                    "discovery_queries": ["brushed steel"],
                    "initial_quota": 3,
                },
                {
                    "material_class_id": "plastic.molded_plain",
                    "parent_category": "plastic",
                    "display_name": "Molded plain plastic",
                    "description": "Plain injection-molded plastic.",
                    "discovery_queries": ["plain molded plastic"],
                    "initial_quota": 2,
                },
            ],
        }
    )


def _catalog_and_assignments(
    tmp_path: Path,
    registry: MaterialClassRegistry,
) -> tuple[MaterialCatalog, MaterialClassAssignments]:
    blend = tmp_path / "material.blend"
    blend.write_bytes(b"blend")
    catalog = MaterialCatalog(
        records=(
            MaterialRecord(
                material_id="metal-a",
                category_slug="metal",
                blend_path=blend,
                sha256="0" * 64,
                license="cc_zero",
                provider="test",
                asset_base_id="metal-a",
                display_name="metal-a",
            ),
        ),
        library_root=tmp_path,
        snapshot_sha256="1" * 64,
        source_path=tmp_path / "materials.jsonl",
    )
    assignments = MaterialClassAssignments.from_dict(
        {
            "schema_version": MATERIAL_CLASS_ASSIGNMENTS_SCHEMA,
            "policy_version": MATERIAL_CLASS_POLICY_VERSION,
            "registry_snapshot_sha256": registry.snapshot_sha256,
            "catalog_snapshot_sha256": catalog.snapshot_sha256,
            "assignments": [
                {
                    "material_id": "metal-a",
                    "material_class_id": "metal.brushed_steel",
                }
            ],
        },
        registry=registry,
        catalog=catalog,
    )
    return catalog, assignments


def _binding(
    template: str,
    callsite: str,
    class_id: str | None,
    *,
    asset_type: str = "pbr_material",
) -> dict[str, object]:
    return {
        "schema_version": target.MATERIAL_CLASS_BINDING_SCHEMA,
        "template": template,
        "callsite_id": callsite,
        "asset_type": asset_type,
        "material_class_id": class_id,
    }


def test_plan_uses_fixed_class_quota_without_facets_or_importance(tmp_path: Path) -> None:
    registry = _registry()
    catalog, assignments = _catalog_and_assignments(tmp_path, registry)
    plan, profiles = target.build_material_class_documents(
        registry,
        catalog=catalog,
        assignments=assignments,
        binding_rows=[
            _binding("asset_a", "a", "metal.brushed_steel"),
            _binding("asset_b", "b", "metal.brushed_steel"),
            _binding("asset_b", "c", "plastic.molded_plain"),
            _binding("asset_b", "marking", None, asset_type="flat_color"),
        ],
    )

    by_class = {row["material_class_id"]: row for row in plan["classes"]}
    assert by_class["metal.brushed_steel"] == {
        "material_class_id": "metal.brushed_steel",
        "parent_category": "metal",
        "demand_callsite_count": 2,
        "demand_template_count": 2,
        "initial_quota": 3,
        "assigned_material_count": 1,
        "runtime_enabled_material_count": 1,
        "download_shortfall": 2,
    }
    assert by_class["plastic.molded_plain"]["download_shortfall"] == 2
    profile_by_id = {row["id"]: row for row in profiles["profiles"]}
    assert profile_by_id["metal.brushed_steel"] == {
        "id": "metal.brushed_steel",
        "material_class_id": "metal.brushed_steel",
        "category_slug": "metal",
        "queries": ["brushed steel"],
        "quota": 2,
    }
    serialized = repr((plan, profiles))
    for retired in (
        "required_all",
        "required_any",
        "preferred",
        "excluded",
        "surface_importance",
        "major",
        "secondary",
        "micro",
        "similarity",
        "finish_hints",
    ):
        assert retired not in serialized
    assert plan["summary"]["ignored_non_material_callsite_count"] == 1


def test_plan_rejects_unknown_class_and_duplicate_callsite() -> None:
    registry = _registry()
    with pytest.raises(ValueError, match="unknown material_class_id"):
        target.build_material_class_documents(
            registry,
            binding_rows=[_binding("asset", "a", "metal.unknown")],
        )
    duplicate = _binding("asset", "a", "metal.brushed_steel")
    with pytest.raises(ValueError, match="duplicate material class binding"):
        target.build_material_class_documents(
            registry,
            binding_rows=[duplicate, duplicate],
        )


def test_plan_requires_catalog_and_assignment_as_one_snapshot(tmp_path: Path) -> None:
    registry = _registry()
    catalog, _assignments = _catalog_and_assignments(tmp_path, registry)
    with pytest.raises(ValueError, match="supplied together"):
        target.build_material_class_documents(registry, catalog=catalog)


def test_optical_profiles_keep_class_only_runtime_and_standard_texture_policy() -> None:
    registry = MaterialClassRegistry.from_dict(
        {
            "schema_version": MATERIAL_CLASS_REGISTRY_SCHEMA,
            "policy_version": MATERIAL_CLASS_POLICY_VERSION,
            "classes": [
                {
                    "material_class_id": "glass.clear",
                    "parent_category": "glass",
                    "display_name": "Clear glass",
                    "description": "Clear transparent glass.",
                    "discovery_queries": ["clear glass"],
                    "initial_quota": 2,
                },
                {
                    "material_class_id": "liquid.water_wave_foam",
                    "parent_category": "liquid",
                    "display_name": "Water with waves or foam",
                    "description": "Wave or foam water surface.",
                    "discovery_queries": ["ocean water waves foam"],
                    "initial_quota": 2,
                },
            ],
        }
    )
    _plan, profiles = target.build_material_class_documents(registry)
    by_id = {row["id"]: row for row in profiles["profiles"]}

    assert by_id["glass.clear"]["shader_profile"] == "optical_principled"
    assert "require_nonprocedural" not in by_id["glass.clear"]
    assert by_id["liquid.water_wave_foam"] == {
        "id": "liquid.water_wave_foam",
        "material_class_id": "liquid.water_wave_foam",
        "category_slug": "liquid",
        "queries": ["ocean water waves foam"],
        "quota": 2,
        "shader_profile": "optical_principled",
    }
