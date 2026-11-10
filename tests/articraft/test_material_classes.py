# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import random
from pathlib import Path

import pytest

from articraft.appearance import (
    MATERIAL_CLASS_ASSIGNMENTS_SCHEMA,
    MATERIAL_CLASS_POLICY_VERSION,
    MATERIAL_CLASS_REGISTRY_SCHEMA,
    AppearanceRequest,
    MaterialCatalog,
    MaterialClassAssignments,
    MaterialClassRegistry,
    MaterialRecord,
    appearance_requests_from_model,
    resolve_appearances_from_pools,
)
from sdk import AppearanceOnlyKind, AppearanceOnlySpec, ArticulatedObject, Box


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
                    "description": "Directional brushed steel sheet and hardware.",
                    "discovery_queries": ["brushed steel", "satin stainless steel"],
                    "initial_quota": 8,
                },
                {
                    "material_class_id": "metal.paint_coated",
                    "parent_category": "metal",
                    "display_name": "Paint-coated metal",
                    "description": "Opaque painted or powder-coated metal.",
                    "discovery_queries": ["painted metal", "powder coated metal"],
                    "initial_quota": 6,
                },
            ],
        }
    )


def _record(tmp_path: Path, material_id: str, *, runtime_enabled: bool = True) -> MaterialRecord:
    blend = tmp_path / f"{material_id}.blend"
    blend.write_bytes(material_id.encode())
    return MaterialRecord(
        material_id=material_id,
        category_slug="metal",
        blend_path=blend,
        sha256=hashlib.sha256(material_id.encode()).hexdigest(),
        license="cc_zero",
        provider="test",
        asset_base_id=material_id,
        display_name=material_id,
        runtime_enabled=runtime_enabled,
    )


def _catalog(tmp_path: Path) -> MaterialCatalog:
    return MaterialCatalog(
        records=(
            _record(tmp_path, "brushed-a"),
            _record(tmp_path, "brushed-b"),
            _record(tmp_path, "brushed-disabled", runtime_enabled=False),
            _record(tmp_path, "painted-a"),
        ),
        library_root=tmp_path,
        snapshot_sha256="1" * 64,
        source_path=tmp_path / "materials.jsonl",
    )


def _assignments(
    registry: MaterialClassRegistry,
    catalog: MaterialCatalog,
) -> MaterialClassAssignments:
    return MaterialClassAssignments.from_dict(
        {
            "schema_version": MATERIAL_CLASS_ASSIGNMENTS_SCHEMA,
            "policy_version": MATERIAL_CLASS_POLICY_VERSION,
            "registry_snapshot_sha256": registry.snapshot_sha256,
            "catalog_snapshot_sha256": catalog.snapshot_sha256,
            "assignments": [
                {
                    "material_id": "brushed-a",
                    "material_class_id": "metal.brushed_steel",
                },
                {
                    "material_id": "brushed-b",
                    "material_class_id": "metal.brushed_steel",
                },
                {
                    "material_id": "brushed-disabled",
                    "material_class_id": "metal.brushed_steel",
                },
                {
                    "material_id": "painted-a",
                    "material_class_id": "metal.paint_coated",
                },
            ],
        },
        registry=registry,
        catalog=catalog,
    )


def _request(
    surface: str,
    material_class_id: str = "metal.brushed_steel",
    *,
    selection_group_key: str | None = None,
) -> AppearanceRequest:
    return AppearanceRequest(
        surface_key=surface,
        asset_type="pbr_material",
        material_class_id=material_class_id,
        selection_group_key=selection_group_key,
    )


def test_minimal_visual_contract_derives_independent_runtime_requests() -> None:
    model = ArticulatedObject(name="minimal")
    body = model.part("body")
    body.visual(
        Box((0.2, 0.2, 0.2)),
        name="shell",
        material_class_id="metal.brushed_steel",
    )
    body.visual(
        Box((0.05, 0.05, 0.05)),
        name="handle",
        material_class_id="metal.paint_coated",
    )

    requests = appearance_requests_from_model(model)

    assert [row.surface_key for row in requests] == ["body::shell", "body::handle"]
    assert [row.material_class_id for row in requests] == [
        "metal.brushed_steel",
        "metal.paint_coated",
    ]
    assert all(row.asset_type == "pbr_material" for row in requests)


@pytest.mark.parametrize("class_id", ["glass.clear_transparent", "liquid.clear_still"])
def test_minimal_visual_contract_derives_optical_asset_type(class_id: str) -> None:
    model = ArticulatedObject(name="optical")
    model.part("vessel").visual(
        Box((0.1, 0.1, 0.1)),
        name="shell",
        material_class_id=class_id,
    )

    request = appearance_requests_from_model(model)[0]

    assert request.asset_type == "optical_material"
    assert request.material_class_id == class_id


def test_model_request_derivation_preserves_typed_appearance_only_material() -> None:
    model = ArticulatedObject(name="decal")
    color = model.material(
        "marking",
        rgba=(0.1, 0.2, 0.3, 0.8),
        texture="assets/source/marking.png",
    )
    model.part("panel").visual(
        Box((0.1, 0.1, 0.001)),
        name="marking",
        material=color,
        appearance_only=AppearanceOnlySpec(kind="decal", alpha_mode="blend"),
    )

    request = appearance_requests_from_model(model)[0]

    assert request.surface_key == "panel::marking"
    assert request.asset_type == "appearance_only"
    assert request.material_class_id is None
    assert request.rgba == (0.1, 0.2, 0.3, 0.8)
    assert request.material_name == "marking"
    assert request.texture == "assets/source/marking.png"
    assert request.appearance_only is not None
    assert request.appearance_only.kind is AppearanceOnlyKind.DECAL
    assert request.selection_group_key is None


def test_model_request_derivation_groups_repeated_material_roles_within_one_class() -> None:
    model = ArticulatedObject(name="grouped")
    shared = model.material("wheel_tire", rgba=(0.02, 0.02, 0.02, 1.0))
    distinct = model.material("spare_tire", rgba=(0.02, 0.02, 0.02, 1.0))
    for index in range(2):
        model.part(f"wheel_{index}").visual(
            Box((0.1, 0.1, 0.1)),
            name=f"tire_{index}",
            material=shared,
            material_class_id="rubber.smooth_plain",
        )
    model.part("spare").visual(
        Box((0.1, 0.1, 0.1)),
        name="tire",
        material=distinct,
        material_class_id="rubber.smooth_plain",
    )

    requests = appearance_requests_from_model(model)
    by_surface = {request.surface_key: request for request in requests}

    assert by_surface["wheel_0::tire_0"].selection_group_key == "material:wheel_tire"
    assert by_surface["wheel_1::tire_1"].selection_group_key == "material:wheel_tire"
    assert by_surface["spare::tire"].selection_group_key == "material:spare_tire"


def test_model_request_group_boundaries() -> None:
    model = ArticulatedObject(name="group_boundaries")
    model.material("shared_role", rgba=(0.1, 0.1, 0.1, 1.0))
    model.part("left").visual(
        Box((0.1, 0.1, 0.1)),
        name="panel",
        material="shared_role",
        material_class_id="metal.brushed_steel",
    )
    model.part("right").visual(
        Box((0.1, 0.1, 0.1)),
        name="panel",
        material="shared_role",
        material_class_id="metal.paint_coated",
    )
    model.part("ungrouped_a").visual(
        Box((0.1, 0.1, 0.1)),
        name="panel",
        material_class_id="metal.brushed_steel",
    )
    model.part("ungrouped_b").visual(
        Box((0.1, 0.1, 0.1)),
        name="panel",
        material_class_id="metal.brushed_steel",
    )

    by_surface = {request.surface_key: request for request in appearance_requests_from_model(model)}

    assert by_surface["left::panel"].selection_group_key == "material:shared_role"
    assert by_surface["right::panel"].selection_group_key == "material:shared_role"
    assert (
        by_surface["left::panel"].material_class_id != by_surface["right::panel"].material_class_id
    )
    assert by_surface["ungrouped_a::panel"].selection_group_key == "surface:ungrouped_a::panel"
    assert by_surface["ungrouped_b::panel"].selection_group_key == "surface:ungrouped_b::panel"


def test_model_request_derivation_rejects_missing_or_duplicate_visual_contract() -> None:
    missing = ArticulatedObject(name="missing")
    missing.part("body").visual(Box((0.1, 0.1, 0.1)), name="shell")
    with pytest.raises(ValueError, match="must declare exactly one"):
        appearance_requests_from_model(missing)
    assert appearance_requests_from_model(missing, require_all=False) == ()

    duplicate = ArticulatedObject(name="duplicate")
    part = duplicate.part("body")
    for class_id in ("metal.brushed_steel", "metal.paint_coated"):
        part.visual(Box((0.1, 0.1, 0.1)), name="shell", material_class_id=class_id)
    with pytest.raises(ValueError, match="duplicate visual surface key"):
        appearance_requests_from_model(duplicate)


def test_model_request_derivation_rejects_class_and_appearance_only_conflict() -> None:
    model = ArticulatedObject(name="conflict")
    ink = model.material("ink", rgba=(0.2, 0.3, 0.4, 1.0))
    model.part("panel").visual(
        Box((0.1, 0.1, 0.001)),
        name="marking",
        material=ink,
        material_class_id="metal.paint_coated",
        appearance_only=AppearanceOnlySpec(kind="decal"),
    )

    with pytest.raises(ValueError, match="cannot combine"):
        appearance_requests_from_model(model)


def test_registry_is_canonical_and_rejects_nonofficial_parent() -> None:
    first = _registry()
    second = MaterialClassRegistry.from_dict(
        {
            **first.as_dict(),
            "classes": list(reversed(first.as_dict()["classes"])),
        }
    )

    assert first.classes == second.classes
    assert first.snapshot_sha256 == second.snapshot_sha256
    assert first.get("metal.brushed_steel").initial_quota == 8

    invalid = first.as_dict()
    invalid["classes"][0]["parent_category"] = "brushed-metal"
    with pytest.raises(ValueError, match="official BlenderKit"):
        MaterialClassRegistry.from_dict(invalid)


def test_assignments_bind_both_registry_and_catalog_snapshots(tmp_path: Path) -> None:
    registry = _registry()
    catalog = _catalog(tmp_path)
    assignments = _assignments(registry, catalog)

    assert assignments.material_ids_for_class("metal.brushed_steel") == (
        "brushed-a",
        "brushed-b",
        "brushed-disabled",
    )
    assert [
        row.material_id for row in assignments.records_for_class(catalog, "metal.brushed_steel")
    ] == ["brushed-a", "brushed-b"]

    drifted = assignments.as_dict()
    drifted["catalog_snapshot_sha256"] = "2" * 64
    with pytest.raises(ValueError, match="catalog snapshot mismatch"):
        MaterialClassAssignments.from_dict(
            drifted,
            registry=registry,
            catalog=catalog,
        )


def test_assignments_can_require_exact_runtime_enabled_coverage(tmp_path: Path) -> None:
    registry = _registry()
    catalog = _catalog(tmp_path)
    document = _assignments(registry, catalog).as_dict()
    document["assignments"] = [
        row for row in document["assignments"] if row["material_id"] != "brushed-disabled"
    ]

    MaterialClassAssignments.from_dict(
        document,
        registry=registry,
        catalog=catalog,
        require_runtime_enabled_catalog=True,
    )
    with pytest.raises(ValueError, match="do not cover catalog"):
        MaterialClassAssignments.from_dict(
            document,
            registry=registry,
            catalog=catalog,
            require_complete_catalog=True,
        )

    document["assignments"] = [
        row for row in document["assignments"] if row["material_id"] != "painted-a"
    ]
    with pytest.raises(ValueError, match="do not cover runtime-enabled catalog"):
        MaterialClassAssignments.from_dict(
            document,
            registry=registry,
            catalog=catalog,
            require_runtime_enabled_catalog=True,
        )


def test_exact_class_pool_choice_is_direct_deterministic_and_local(
    tmp_path: Path,
) -> None:
    pools = {
        "metal.brushed_steel": (
            _record(tmp_path, "brushed-a"),
            _record(tmp_path, "brushed-b"),
        )
    }
    pool_sha256 = {"metal.brushed_steel": "4" * 64}
    first_request = _request("body::shell_a")

    previous_global_state = random.getstate()
    try:
        random.seed(817_263)
        global_state = random.getstate()

        first = resolve_appearances_from_pools(
            [first_request],
            pools,
            pool_sha256,
            slug="test_asset",
            material_seed=17,
        )
        repeated = resolve_appearances_from_pools(
            [first_request],
            pools,
            pool_sha256,
            slug="another_asset",
            material_seed=17,
        )
        with_other_component = resolve_appearances_from_pools(
            [_request("body::shell_b"), first_request],
            pools,
            pool_sha256,
            slug="test_asset",
            material_seed=17,
        )

        assert random.getstate() == global_state
    finally:
        random.setstate(previous_global_state)
    assert first == repeated
    assert first[0] == with_other_component[0]
    assert first[0].candidate_pool_count == 2
    assert first[0].candidate_pool_material_class_id == "metal.brushed_steel"
    assert first[0].material is not None
    assert first[0].material.material_id in {"brushed-a", "brushed-b"}
    assert first[0].material == random.Random(17).choice(pools["metal.brushed_steel"])
    assert first[0].draw_order == 0
    assert first[0].selection_index == pools["metal.brushed_steel"].index(first[0].material)
    assert [row.draw_order for row in with_other_component] == [0, 1]
    assert not hasattr(first[0], "selection_key_sha256")


def test_exact_class_pool_choice_uses_stable_group_order(
    tmp_path: Path,
) -> None:
    candidates = (
        _record(tmp_path, "brushed-a"),
        _record(tmp_path, "brushed-b"),
    )
    pools = {"metal.brushed_steel": candidates}
    pool_sha256 = {"metal.brushed_steel": "4" * 64}
    left = _request("body::left")
    right = _request("body::right")

    alone = resolve_appearances_from_pools(
        [left],
        pools,
        pool_sha256,
        slug="test_asset",
        material_seed=23,
    )
    forward = resolve_appearances_from_pools(
        [left, right],
        pools,
        pool_sha256,
        slug="test_asset",
        material_seed=23,
    )
    reverse = resolve_appearances_from_pools(
        [right, left],
        pools,
        pool_sha256,
        slug="test_asset",
        material_seed=23,
    )

    assert forward == reverse
    assert alone[0] == forward[0]
    assert [row.request.surface_key for row in forward] == ["body::left", "body::right"]


def test_exact_class_pool_choice_does_not_deduplicate_components(tmp_path: Path) -> None:
    pools = {"metal.paint_coated": (_record(tmp_path, "painted-a"),)}
    pool_sha256 = {"metal.paint_coated": "5" * 64}

    resolved = resolve_appearances_from_pools(
        [
            _request("body::left", "metal.paint_coated"),
            _request("body::right", "metal.paint_coated"),
        ],
        pools,
        pool_sha256,
        slug="test_asset",
        material_seed=23,
    )

    assert [row.material.material_id for row in resolved if row.material is not None] == [
        "painted-a",
        "painted-a",
    ]
    assert [row.draw_order for row in resolved] == [0, 1]


def test_exact_class_pool_choice_reuses_one_choice_for_an_explicit_group(tmp_path: Path) -> None:
    candidates = (
        _record(tmp_path, "brushed-a"),
        _record(tmp_path, "brushed-b"),
    )
    pools = {"metal.brushed_steel": candidates}
    pool_sha256 = {"metal.brushed_steel": "4" * 64}

    resolved = resolve_appearances_from_pools(
        [
            _request("lid_0::panel", selection_group_key="lid_0::panel"),
            _request("lid_1::panel", selection_group_key="lid_0::panel"),
        ],
        pools,
        pool_sha256,
        slug="test_asset",
        material_seed=23,
    )

    assert resolved[0].draw_order == resolved[1].draw_order == 0
    assert resolved[0].selection_index == resolved[1].selection_index
    assert resolved[0].material == resolved[1].material


def test_exact_class_group_choice_is_stable_when_members_change_and_separates_classes(
    tmp_path: Path,
) -> None:
    pools = {
        "metal.brushed_steel": (
            _record(tmp_path, "brushed-a"),
            _record(tmp_path, "brushed-b"),
        ),
        "metal.paint_coated": (_record(tmp_path, "painted-a"),),
    }
    pool_sha256 = {
        "metal.brushed_steel": "4" * 64,
        "metal.paint_coated": "5" * 64,
    }
    shared_group = "material:shared_hardware"

    one_member = resolve_appearances_from_pools(
        [_request("wheel_0::rim", selection_group_key=shared_group)],
        pools,
        pool_sha256,
        slug="test_asset",
        material_seed=23,
    )[0]
    two_members = resolve_appearances_from_pools(
        [
            _request("wheel_0::rim", selection_group_key=shared_group),
            _request("wheel_1::rim", selection_group_key=shared_group),
        ],
        pools,
        pool_sha256,
        slug="test_asset",
        material_seed=23,
    )
    other_class = resolve_appearances_from_pools(
        [
            _request(
                "body::shell",
                "metal.paint_coated",
                selection_group_key=shared_group,
            )
        ],
        pools,
        pool_sha256,
        slug="test_asset",
        material_seed=23,
    )[0]

    assert one_member.draw_order == two_members[0].draw_order == two_members[1].draw_order == 0
    assert (
        one_member.selection_index
        == two_members[0].selection_index
        == two_members[1].selection_index
    )
    assert one_member.material == two_members[0].material == two_members[1].material
    assert other_class.candidate_pool_material_class_id == "metal.paint_coated"


def test_material_request_requires_one_exact_class() -> None:
    with pytest.raises(ValueError, match="requires material_class_id"):
        AppearanceRequest(
            surface_key="shell",
            asset_type="pbr_material",
        )
