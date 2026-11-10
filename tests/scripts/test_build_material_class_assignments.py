# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from articraft.appearance import (
    MATERIAL_CLASS_POLICY_VERSION,
    MATERIAL_CLASS_REGISTRY_SCHEMA,
    MaterialCatalog,
    MaterialClassAssignments,
    MaterialClassRegistry,
    MaterialRecord,
)
from scripts import build_material_class_assignments as target


def _registry() -> MaterialClassRegistry:
    return MaterialClassRegistry.from_dict(
        {
            "schema_version": MATERIAL_CLASS_REGISTRY_SCHEMA,
            "policy_version": MATERIAL_CLASS_POLICY_VERSION,
            "classes": [
                {
                    "material_class_id": "metal.brushed",
                    "parent_category": "metal",
                    "display_name": "Brushed metal",
                    "description": "Brushed metal surface.",
                    "discovery_queries": ["brushed metal"],
                    "initial_quota": 2,
                },
                {
                    "material_class_id": "plastic.matte",
                    "parent_category": "plastic",
                    "display_name": "Matte plastic",
                    "description": "Matte opaque plastic surface.",
                    "discovery_queries": ["matte plastic"],
                    "initial_quota": 2,
                },
            ],
        }
    )


def _registry_with_marble() -> MaterialClassRegistry:
    payload = _registry().as_dict()
    payload["classes"].append(
        {
            "material_class_id": "marble.generic",
            "parent_category": "marble",
            "display_name": "Polished or honed marble",
            "description": "Broad marble surface class.",
            "discovery_queries": ["marble"],
            "initial_quota": 2,
        }
    )
    return MaterialClassRegistry.from_dict(payload)


def _catalog(tmp_path: Path) -> MaterialCatalog:
    records = []
    for material_id, category, runtime_enabled in (
        ("metal-active", "metal", True),
        ("metal-disabled", "metal", False),
        ("plastic-active", "plastic", True),
    ):
        blend = tmp_path / f"{material_id}.blend"
        payload = material_id.encode()
        blend.write_bytes(payload)
        records.append(
            MaterialRecord(
                material_id=material_id,
                category_slug=category,
                blend_path=blend,
                sha256=hashlib.sha256(payload).hexdigest(),
                license="cc_zero",
                provider="test",
                asset_base_id=material_id,
                display_name=material_id.replace("-", " "),
                runtime_enabled=runtime_enabled,
            )
        )
    return MaterialCatalog(
        records=tuple(records),
        library_root=tmp_path,
        snapshot_sha256="1" * 64,
        source_path=tmp_path / "materials.jsonl",
    )


def _decision(
    material_id: str,
    *,
    class_id: str | None,
    candidates: tuple[str, ...],
) -> target.AssignmentDecision:
    return target.AssignmentDecision(
        material_id=material_id,
        status="assigned" if class_id is not None else "review",
        material_class_id=class_id,
        candidate_material_class_ids=candidates,
        method="manual" if class_id is not None else "unassigned",
        evidence=("offline audit",) if class_id is not None else (),
        note=None,
    )


def _complete_decisions() -> tuple[target.AssignmentDecision, ...]:
    return (
        _decision(
            "metal-active",
            class_id="metal.brushed",
            candidates=("metal.brushed",),
        ),
        _decision(
            "metal-disabled",
            class_id=None,
            candidates=("metal.brushed",),
        ),
        _decision(
            "plastic-active",
            class_id="plastic.matte",
            candidates=("plastic.matte",),
        ),
    )


def test_init_worklist_covers_catalog_with_parent_bounded_candidates(
    tmp_path: Path,
) -> None:
    rows = target.initial_review_rows(
        registry=_registry(),
        catalog=_catalog(tmp_path),
    )

    assert len(rows) == 3
    by_id = {row["material_id"]: row for row in rows}
    assert by_id["metal-active"]["candidate_material_class_ids"] == ["metal.brushed"]
    assert by_id["plastic-active"]["candidate_material_class_ids"] == ["plastic.matte"]
    assert all(row["status"] == "review" for row in rows)
    assert all(row["material_class_id"] is None for row in rows)


@pytest.mark.parametrize(
    ("category", "display_name"),
    [
        ("food-material", "Glossy candy shell"),
        ("ground-material", "Loose gravel"),
    ],
)
def test_categories_without_controlled_leaves_emit_review_rows(
    category: str,
    display_name: str,
) -> None:
    record = SimpleNamespace(
        material_id=f"{category}-one",
        category_slug=category,
        display_name=display_name,
        tags=(),
    )
    catalog = SimpleNamespace(records=(record,))

    initial = target.initial_review_rows(registry=_registry(), catalog=catalog)
    suggested = target.suggested_decision_row(registry=_registry(), record=record)

    assert initial[0]["candidate_material_class_ids"] == []
    assert suggested["status"] == "review"
    assert suggested["material_class_id"] is None
    assert suggested["candidate_material_class_ids"] == []


def test_decision_loader_rejects_missing_rows_and_wrong_parent(tmp_path: Path) -> None:
    registry = _registry()
    catalog = _catalog(tmp_path)
    worklist = list(target.initial_review_rows(registry=registry, catalog=catalog))
    incomplete = tmp_path / "incomplete.jsonl"
    incomplete.write_text(
        "".join(json.dumps(row) + "\n" for row in worklist[:-1]),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="does not cover catalog"):
        target.load_decisions(incomplete, registry=registry, catalog=catalog)

    wrong = dict(worklist[0])
    wrong.update(
        {
            "status": "assigned",
            "material_class_id": "plastic.matte",
            "candidate_material_class_ids": ["plastic.matte"],
            "method": "manual",
        }
    )
    with pytest.raises(ValueError, match="candidate class parent mismatch"):
        target._decision_from_row(
            wrong,
            index=0,
            registry=registry,
            catalog_by_id={row.material_id: row for row in catalog.records},
        )


def test_runtime_review_requires_explicit_draft_mode(tmp_path: Path) -> None:
    registry = _registry()
    catalog = _catalog(tmp_path)
    decisions = tuple(
        _decision(
            record.material_id,
            class_id=None,
            candidates=("metal.brushed" if record.category_slug == "metal" else "plastic.matte",),
        )
        for record in catalog.records
    )

    with pytest.raises(ValueError, match="runtime-enabled catalog"):
        target.build_snapshot(
            registry=registry,
            catalog=catalog,
            decisions=decisions,
            allow_runtime_review=False,
        )
    snapshot = target.build_snapshot(
        registry=registry,
        catalog=catalog,
        decisions=decisions,
        allow_runtime_review=True,
    )
    assert snapshot.manifest["summary"]["runtime_ready"] is False
    assert snapshot.manifest["summary"]["runtime_review_material_count"] == 2
    assert snapshot.assignments_document["assignments"] == []

    destination, pointer = target.publish_snapshot(
        snapshot,
        output_root=tmp_path / "sidecars",
    )
    assert destination.name == snapshot.logical_snapshot_sha256
    assert pointer.name == "latest-review.json"
    assert not (pointer.parent / "latest.json").exists()
    assert (
        target.validate_published_snapshot(
            destination,
            registry=registry,
            catalog=catalog,
        )["runtime_ready"]
        is False
    )
    with pytest.raises(ValueError, match="not runtime-ready"):
        target.validate_published_snapshot(
            destination,
            registry=registry,
            catalog=catalog,
            require_runtime_ready=True,
        )


def test_runtime_ready_snapshot_assigns_each_enabled_material_exactly_once(
    tmp_path: Path,
) -> None:
    registry = _registry()
    catalog = _catalog(tmp_path)
    snapshot = target.build_snapshot(
        registry=registry,
        catalog=catalog,
        decisions=tuple(reversed(_complete_decisions())),
        allow_runtime_review=False,
    )

    assert snapshot.manifest["summary"] == {
        "catalog_material_count": 3,
        "runtime_enabled_material_count": 2,
        "assigned_material_count": 2,
        "review_material_count": 1,
        "runtime_assigned_material_count": 2,
        "runtime_review_material_count": 0,
        "assigned_class_count": 2,
        "runtime_ready": True,
    }
    assignments = MaterialClassAssignments.from_dict(
        snapshot.assignments_document,
        registry=registry,
        catalog=catalog,
        require_runtime_enabled_catalog=True,
    )
    assert len(assignments.assignments) == 2
    assert {material_id for material_id, _class_id in assignments.assignments} == {
        "metal-active",
        "plastic-active",
    }

    first_destination, pointer = target.publish_snapshot(
        snapshot,
        output_root=tmp_path / "sidecars",
    )
    second_destination, second_pointer = target.publish_snapshot(
        snapshot,
        output_root=tmp_path / "sidecars",
    )
    assert first_destination == second_destination
    assert pointer == second_pointer
    assert pointer.name == "latest.json"
    assert json.loads(pointer.read_text())["runtime_ready"] is True
    assert (
        target.validate_published_snapshot(
            first_destination,
            registry=registry,
            catalog=catalog,
            require_runtime_ready=True,
        )["runtime_assigned_material_count"]
        == 2
    )

    (first_destination / "review.jsonl").write_text("tampered\n", encoding="utf-8")
    with pytest.raises(ValueError, match="review.jsonl SHA mismatch"):
        target.validate_published_snapshot(
            first_destination,
            registry=registry,
            catalog=catalog,
        )


def test_content_identity_is_independent_of_decision_input_order(tmp_path: Path) -> None:
    registry = _registry()
    catalog = _catalog(tmp_path)
    first = target.build_snapshot(
        registry=registry,
        catalog=catalog,
        decisions=_complete_decisions(),
        allow_runtime_review=False,
    )
    second = target.build_snapshot(
        registry=registry,
        catalog=catalog,
        decisions=tuple(reversed(_complete_decisions())),
        allow_runtime_review=False,
    )

    assert first.logical_snapshot_sha256 == second.logical_snapshot_sha256
    assert first.manifest == second.manifest


def test_catalog_snapshot_directory_and_manifest_resolve_to_materials_jsonl(
    tmp_path: Path,
) -> None:
    snapshot = tmp_path / "normalized" / "catalogs" / ("a" * 64)
    snapshot.mkdir(parents=True)
    catalog = snapshot / "materials.jsonl"
    catalog.write_text("", encoding="utf-8")
    manifest = snapshot / "manifest.json"
    manifest.write_text("{}\n", encoding="utf-8")

    expected_root = tmp_path / "normalized"
    assert target.resolve_catalog_pointer(snapshot) == (catalog, expected_root)
    assert target.resolve_catalog_pointer(manifest) == (catalog, expected_root)


def test_incremental_classification_preserves_old_snapshot_and_only_classifies_new_ids(
    tmp_path: Path,
) -> None:
    registry = _registry_with_marble()
    old_catalog = _catalog(tmp_path)
    old_snapshot = target.build_snapshot(
        registry=registry,
        catalog=old_catalog,
        decisions=_complete_decisions(),
        allow_runtime_review=False,
    )
    _old_destination, pointer = target.publish_snapshot(
        old_snapshot,
        output_root=tmp_path / "old-sidecars",
    )

    blend = tmp_path / "new-marble.blend"
    payload = b"new-marble"
    blend.write_bytes(payload)
    current_catalog = MaterialCatalog(
        records=(
            *old_catalog.records,
            MaterialRecord(
                material_id="new-marble",
                category_slug="marble",
                blend_path=blend,
                sha256=hashlib.sha256(payload).hexdigest(),
                license="cc_zero",
                provider="test",
                asset_base_id="new-marble",
                display_name="Unusual marble tiles",
                runtime_enabled=True,
            ),
        ),
        library_root=tmp_path,
        snapshot_sha256="2" * 64,
        source_path=tmp_path / "current-materials.jsonl",
    )
    inherited = target.load_inherited_assignment_snapshot(
        pointer,
        registry=registry,
        catalog=current_catalog,
    )

    rows, summary = target.incremental_decision_rows(
        registry=registry,
        catalog=current_catalog,
        inherited_snapshot=inherited,
    )
    by_id = {row["material_id"]: row for row in rows}
    assert by_id["metal-active"]["material_class_id"] == "metal.brushed"
    assert by_id["metal-disabled"]["status"] == "review"
    assert by_id["new-marble"]["material_class_id"] == "marble.generic"
    assert by_id["new-marble"]["evidence"][1] == (f"classifier:{target.LOCAL_CLASSIFIER_VERSION}")
    assert any(
        evidence.startswith("inherited_assignment_snapshot:")
        for evidence in by_id["metal-active"]["evidence"]
    )
    assert summary == {
        "inheritance_enabled": True,
        "inheritance_snapshot_sha256": old_snapshot.logical_snapshot_sha256,
        "inheritance_manifest_sha256": inherited.manifest_sha256,
        "inheritance_assignments_sha256": inherited.assignments_snapshot_sha256,
        "inheritance_decisions_sha256": inherited.decisions_sha256,
        "inherited_material_count": 3,
        "inherited_assigned_count": 2,
        "inherited_review_count": 1,
        "new_material_count": 1,
        "new_assigned_count": 1,
        "new_review_count": 0,
        "review_count_by_category": {"metal": 1},
        "new_review_count_by_category": {},
    }

    rebuilt, rebuilt_summary = target.build_incremental_classification_snapshot(
        registry=registry,
        catalog=current_catalog,
        inherited_snapshot=inherited,
        require_runtime_ready=True,
    )
    assert rebuilt_summary == summary
    assert rebuilt.manifest["summary"]["runtime_ready"] is True
    assert rebuilt.manifest["summary"]["assigned_material_count"] == 3

    _rebuilt_destination, rebuilt_pointer = target.publish_snapshot(
        rebuilt,
        output_root=tmp_path / "current-sidecars",
    )
    repeated_inheritance = target.load_inherited_assignment_snapshot(
        rebuilt_pointer,
        registry=registry,
        catalog=current_catalog,
    )
    repeated, repeated_summary = target.build_incremental_classification_snapshot(
        registry=registry,
        catalog=current_catalog,
        inherited_snapshot=repeated_inheritance,
        require_runtime_ready=True,
    )
    assert repeated_summary["new_material_count"] == 0
    assert repeated.logical_snapshot_sha256 == rebuilt.logical_snapshot_sha256


@pytest.mark.parametrize(
    ("category", "name", "tags", "expected"),
    [
        ("marble", "Fantasy Marble", (), "marble.generic"),
        ("food-material", "Glossy Candy", (), None),
        ("ground-material", "Loose Gravel", (), None),
        ("liquid", "Clear Still Water", (), None),
        ("liquid", "Ocean Wave Foam", (), "liquid.water_wave_foam"),
        ("tech", "Photovoltaic Solar Panel", (), "tech.solar_cell"),
        ("tech", "Green NeoCircuit", ("pcb",), "tech.circuit_board"),
        ("tech", "Sci-Fi Cargo Rack", (), "tech.scifi_panel"),
        ("tech", "Sci Fi Wall Panel", (), "tech.scifi_panel"),
        ("tech", "Space Shuttle Pads", (), "tech.scifi_panel"),
        ("tech", "Thick Red Cables", (), "tech.cable_pipe_bundle"),
        ("tech", "Button Panel Material", ("design",), "tech.control_interface"),
        ("tech", "SciFi Floor Emissive", (), "tech.emissive_surface"),
        ("tech", "Carbon Fiber", (), None),
        ("metal", "Bare Aluminum", (), "metal.aluminum_bare"),
        ("metal", "Blue Anodized Aluminium", (), "metal.aluminum_bare"),
        ("metal", "Antique Brass", (), "metal.brass_aged"),
        ("metal", "Polished Brass", (), "metal.brass_polished"),
        ("metal", "Verdigris Copper", (), "metal.copper_patinated"),
        ("metal", "Brushed Stainless", (), "metal.stainless_matte"),
        ("metal", "Mirror Stainless", (), "metal.stainless_matte"),
        ("metal", "Rusted Cast Iron", (), "metal.steel_rusted"),
        ("metal", "Metal Chainmail", (), "metal.mesh_chainmail"),
        ("metal", "Metal Chain Link", (), "metal.mesh_chainmail"),
        ("metal", "Metal Ventilation", (), "metal.mesh_chainmail"),
        ("metal", "Corrugated Steel Sheet", (), "metal.patterned_sheet_panel"),
        ("metal", "Hammered Geometric Metal", (), "metal.patterned_sheet_panel"),
        ("metal", "Powder Coated Metal", (), "metal.paint_coated"),
        ("metal", "Metal Powdercoat Matte", (), "metal.paint_coated"),
        ("metal", "Car Paint Red", (), "metal.paint_coated"),
        ("metal", "Old Gold", ("jewelry",), "metal.precious_gold"),
        ("metal", "Black Woven Leather", (), None),
        ("metal", "Wooden Block Wall", (), None),
        ("metal", "Metal Ribs", (), "metal.patterned_sheet_panel"),
        ("metal", "Old Iron", (), "metal.generic_scratched"),
        ("metal", "Scuffed Titanium", (), "metal.generic_scratched"),
        ("ceramic", "Matte Brake Ceramic", (), "ceramic.porcelain_glazed_plain"),
        (
            "concrete",
            "Garage Floor",
            ("chipped", "cracked", "damaged"),
            "concrete.formed_patterned",
        ),
    ],
)
def test_final124_classifier_uses_exact_conservative_visible_rules(
    category: str,
    name: str,
    tags: tuple[str, ...],
    expected: str | None,
) -> None:
    record = SimpleNamespace(category_slug=category, display_name=name, tags=tags)
    assert target.suggest_material_class_id(record) == expected


@pytest.mark.parametrize(
    ("source_category", "name", "tags", "expected"),
    [
        ("velvet", "Plain Red Velvet", ("upholstery",), "fabric.velvet"),
        ("chenille", "Plain Red Chenille", (), "fabric.upholstery_plain"),
        ("suede", "Plain Brown Suede", (), "fabric.upholstery_plain"),
        ("vinyl-imitation-leather", "Plain White Vinyl", (), "fabric.upholstery_plain"),
        ("embroidery", "Graphical Gold Embroidery", (), "fabric.printed_pattern"),
        ("fabric", "Stripe Blue Flat", ("upholstery",), "fabric.printed_pattern"),
        ("dimout", "Stripe Blue Dimout", (), "fabric.printed_pattern"),
        ("fabric", "Blue Corduroy", (), "fabric.corduroy_ribbed"),
        ("fabric", "Dark Denim Twill", (), "fabric.denim_twill"),
        ("fabric", "Quilted Textile", (), "fabric.quilted_pleated"),
        ("fabric", "Pleated Waffle Fabric", (), "fabric.quilted_pleated"),
        ("fabric", "Carbon Fiber Cloth", (), "fabric.carbon_weave"),
        ("fabric", "Pink Twill Fabric", (), "fabric.denim_twill"),
        ("fabric", "White Ribbed Fabric", (), "fabric.corduroy_ribbed"),
        ("fabric", "Pink Fur", (), "fabric.carpet_fleece"),
        ("fabric", "Cat", (), "fabric.printed_pattern"),
        ("fabric", "Soft Carpet", (), "fabric.carpet_fleece"),
        ("fabric", "Sherpa Fabric", (), "fabric.carpet_fleece"),
        ("fabric", "Satin Silk", (), "fabric.satin_silk"),
        ("velvet", "Satin Collection", (), "fabric.satin_silk"),
        ("velvet", "Wool Carpet", (), "fabric.carpet_fleece"),
        ("fabric", "Floral Tartan Pattern", (), "fabric.printed_pattern"),
        ("fabric", "Red Ornament Fabric", (), "fabric.printed_pattern"),
        ("fabric", "Synthetic Leather", (), "fabric.upholstery_plain"),
        ("fabric", "Rustic Burlap", (), "fabric.canvas"),
        ("fabric", "Window Screen", (), "fabric.open_mesh"),
        ("fabric", "Seamless Wicker", (), "fabric.open_mesh"),
        ("fabric", "Old Clay Rusty Texture", (), None),
        ("fabric", "Thick Rope", ("thread",), "fabric.thread_yarn"),
        ("fabric", "Woven Seat Webbing", (), "fabric.webbing"),
        ("fabric", "Pressed Wool Felt", (), "fabric.felt"),
    ],
)
def test_final123_fabric_classifier_uses_provider_subcategory_and_visible_identity(
    source_category: str,
    name: str,
    tags: tuple[str, ...],
    expected: str,
) -> None:
    record = SimpleNamespace(
        category_slug="fabric",
        source_category_slug=source_category,
        display_name=name,
        tags=tags,
    )
    assert target.suggest_material_class_id(record) == expected


@pytest.mark.parametrize(
    ("category", "name", "expected"),
    [
        ("glass", "Smoked Blue Tinted Glass", "glass.smoked_tinted"),
        ("wood", "Weathered Rough Wood", "wood.rustic_weathered"),
        ("glass", "Crystal Patterned Glass", "glass.stained_decorative"),
        ("glass", "Diamond Grid Glass", "glass.stained_decorative"),
        ("glass", "Acrylic Glass Sheet", None),
        ("glass", "Building Facade", "glass.architectural_window_patterned"),
        ("glass", "Architectural Glass", "glass.clear_transparent"),
        ("glass", "Glass Window", "glass.architectural_window_patterned"),
        ("glass", "Black Opaque Glass", "glass.smoked_tinted"),
        ("glass", "Black and White Glass", "glass.stained_decorative"),
        ("glass", "Blue Chipped Glass", "glass.damaged_cracked"),
        ("rubber", "Black Textured Rubber", "rubber.pebbled"),
        ("rubber", "Octagon Stud Mat", "rubber.pebbled"),
        ("rubber", "Old Rubber", "rubber.worn_cracked"),
        ("rubber", "Shredded Rubber Mulch", "rubber.pebbled"),
        ("rubber", "Plain Natural Rubber", "rubber.smooth_plain"),
        ("wood", "Light Oak Wood Grain", "wood.oak"),
        ("wood", "Chevron Parquet", "wood.patterned_decorative"),
        ("wood", "Walnut Veneer Panel", "wood.veneer_panel"),
        ("wood", "Wall Timber Panelling", "wood.veneer_panel"),
        ("wood", "Car Tyre", None),
        ("wood", "Rattan Weave", "wood.woven_plant_fiber"),
        ("wood", "Weaving Reed", "wood.woven_plant_fiber"),
        ("wood", "OSB Composite Board", "wood.engineered_board"),
        ("wood", "Decorative Wood Pattern", "wood.patterned_decorative"),
        ("wood", "Old Damaged Wood", "wood.rustic_weathered"),
        ("wood", "Golden Wood", "wood.natural_generic"),
        ("wood", "Carved Wood", "wood.patterned_decorative"),
        ("wood", "Wood Moss", "wood.rustic_weathered"),
        ("wood", "Wood-like Fiber Paper", None),
        ("wood", "Wooden Floor", "wood.plank_floor"),
        ("wood", "Natural Cork", "wood.cork_surface"),
        ("paper", "Floral Wallpaper", "paper.wallpaper_patterned"),
        ("stone", "Cobblestone Ground", "stone.aggregate_ground"),
        ("plastic", "Bubble Wrap", "plastic.flexible_bubble_wrap"),
        ("plastic", "Geometric Plastic", "plastic.patterned_textured"),
        ("plastic", "Carbon Fiber Panel", "plastic.patterned_textured"),
        ("plastic", "Blue Textured Plastic", "plastic.patterned_textured"),
        ("plastic", "Plastic Vents", "plastic.patterned_textured"),
        ("plastic", "Old Plastic", "plastic.weathered_worn"),
        ("plastic", "Old Blue Plastic", "plastic.weathered_worn"),
        ("plastic", "Piano Black Plastic", "plastic.opaque_glossy_molded"),
        ("plastic", "Roller Shutters", "plastic.patterned_textured"),
        ("plastic", "Fingerprints", None),
        ("plastic", "Duct Tape", None),
        ("plastic", "Skin - Black", None),
        ("plastic", "Carbon", "plastic.patterned_textured"),
        ("plastic", "Grey Crystal Plastic", "plastic.patterned_textured"),
        ("plastic", "Yellow Sponge Material", None),
        ("plastic", "Lacquered Plastic", "plastic.opaque_glossy_molded"),
        ("organic", "Candle Wax", "organic.wax"),
        ("organic", "Alien Skin", "organic.biological_surface"),
    ],
)
def test_final123_classifier_recovers_visible_classes_from_bulk_metadata(
    category: str,
    name: str,
    expected: str | None,
) -> None:
    record = SimpleNamespace(category_slug=category, display_name=name, tags=())
    assert target.suggest_material_class_id(record) == expected


@pytest.mark.parametrize(
    ("name", "tags", "expected"),
    [
        ("Rusty iron", ("oxidized",), "rust.oxidized_metal"),
        ("Deep corrosion", ("pitted", "flaking"), "rust.heavy_corrosion"),
        ("Corrugated rusty sheet", ("metal",), "rust.patterned_sheet"),
        ("Black rusty plate", ("diamond-pattern",), "rust.patterned_sheet"),
        ("Chipped painted rust", ("metal",), "rust.painted_weathered"),
        ("Verdigris metal", ("copper", "patina"), "rust.verdigris_patina"),
        ("Adobe Painter Rust", ("oxidized",), "rust.oxidized_metal"),
        ("Worn Metal Sheet with Scuffs", ("metal",), None),
        ("Rusty Painted Surface", ("rust", "paint", "concrete"), None),
    ],
)
def test_final123_rust_classifier_uses_visible_corrosion_archetypes(
    name: str,
    tags: tuple[str, ...],
    expected: str | None,
) -> None:
    record = SimpleNamespace(category_slug="rust", display_name=name, tags=tags)
    assert target.suggest_material_class_id(record) == expected


def test_final123_rust_classifier_uses_provider_description_offline() -> None:
    heavy = SimpleNamespace(
        category_slug="rust",
        display_name="Rust",
        tags=("metal", "rust"),
        source_description="Fully rusted surface with dense iron oxide coverage.",
    )
    patterned = SimpleNamespace(
        category_slug="rust",
        display_name="Rusty metal surface",
        tags=("metal", "rust"),
        source_description="Old metal plates with screws and rivets.",
    )

    assert target.suggest_material_class_id(heavy) == "rust.heavy_corrosion"
    assert target.suggest_material_class_id(patterned) == "rust.patterned_sheet"


def test_final127_metal_classifier_uses_provider_description_offline() -> None:
    mesh = SimpleNamespace(
        category_slug="metal",
        display_name="Metal Frame",
        tags=(),
        source_description="A hex wires frame forming a regular metal mesh.",
    )
    tread = SimpleNamespace(
        category_slug="metal",
        display_name="Metal",
        tags=(),
        source_description="A repeated tread rectangle panel surface.",
    )

    assert target.suggest_material_class_id(mesh) == "metal.mesh_chainmail"
    assert target.suggest_material_class_id(tread) == "metal.patterned_sheet_panel"


@pytest.mark.parametrize(
    ("category", "name", "tags", "description", "expected"),
    [
        ("metal", "Silver Ore", ("silver", "ore"), "", None),
        ("metal", "Medieval iron door", ("door", "iron", "medieval"), "", None),
        ("metal", "Treasure Coins Silver", ("treasure", "coins"), "", None),
        (
            "plastic",
            "Recycled plastic",
            ("plastic", "inserts", "terrazzo"),
            "White recycled plastic with colored inserts.",
            "plastic.patterned_textured",
        ),
        (
            "plastic",
            "Dirt PVC",
            ("plastic", "pvc"),
            "A plastic with a few scratches and dust applied.",
            "plastic.weathered_worn",
        ),
        (
            "rubber",
            "Tyre Sidewall",
            ("tyre", "sidewall", "rubber"),
            "Use UV MAP to get the sidewall correctly aligned.",
            None,
        ),
        ("fabric", "Zarape", ("multicolor", "zarape"), "", "fabric.printed_pattern"),
        (
            "fabric",
            "Brown wave basket",
            ("wave", "pattern", "rope"),
            "",
            "fabric.printed_pattern",
        ),
        (
            "fabric",
            "Wave Pattern Cloth Fabric",
            ("wave", "pattern", "carpet"),
            "",
            "fabric.printed_pattern",
        ),
        (
            "fabric",
            "Fabric black panels",
            ("panels", "bed", "decor"),
            "",
            "fabric.printed_pattern",
        ),
        (
            "fabric",
            "Fabric red bed panels",
            ("fabric", "panel", "bed"),
            "",
            "fabric.printed_pattern",
        ),
        (
            "fabric",
            "Fabric06 PBR",
            ("pbr", "fabric"),
            "Pink striped fabric (Cordoroy?)",
            "fabric.corduroy_ribbed",
        ),
        (
            "fabric",
            "Forest Green Velure",
            (),
            "Directional nap of high-end velvet fabric.",
            "fabric.velvet",
        ),
        (
            "fabric",
            "Nylon V2",
            ("nylon", "pantyhose", "mesh"),
            "Better Nylon Shader with sheer control.",
            "fabric.open_mesh",
        ),
        (
            "fabric",
            "Hessian Sackcloth",
            ("essian", "sackcloth"),
            "",
            "fabric.canvas",
        ),
        ("fabric", "Hook", ("wires", "plastic", "rubber"), "", None),
        (
            "fabric",
            "Wrinkled Sheet",
            ("cloth", "wrinkle"),
            "",
            "fabric.quilted_pleated",
        ),
        (
            "fabric",
            "Wrinkled Fabric",
            ("wrinkled", "stitched"),
            "",
            "fabric.quilted_pleated",
        ),
        ("fabric", "Reddish Leather", ("leather", "wrinkled"), "", None),
        (
            "fabric",
            "Puffy Weathered Red Rubber",
            ("puffy", "weathered", "rubber"),
            "",
            None,
        ),
        (
            "fabric",
            "Red Worn Sofa",
            ("worn", "wrinkled", "sofa"),
            "",
            "fabric.upholstery_plain",
        ),
        ("wood", "Wooden Studs", ("studs", "iron"), "", None),
        ("wood", "Wooden Game Crate One", ("game", "crate", "box"), "", None),
        ("wood", "Medieval chest", ("chest", "metal", "plate"), "", None),
        (
            "wood",
            "Wood Dust Gold",
            ("wood", "dust", "dirt"),
            "",
            "wood.natural_generic",
        ),
        (
            "wood",
            "Wood Dust Pale",
            ("wood", "dust", "dirt"),
            "",
            "wood.natural_generic",
        ),
        (
            "wood",
            "Wood Dust Light",
            ("wood", "dust", "dirt"),
            "",
            "wood.natural_generic",
        ),
        (
            "wood",
            "Wood Dust Brown",
            ("wood", "dust", "dirt"),
            "",
            "wood.natural_generic",
        ),
        (
            "wood",
            "Wood Chip",
            ("wood", "chip", "scan"),
            "",
            "wood.natural_generic",
        ),
        (
            "wood",
            "Black Wood Chiseled",
            ("wood", "chiseled", "abstract"),
            "",
            "wood.patterned_decorative",
        ),
        ("wood", "Chess", ("wood", "chess"), "", "wood.patterned_decorative"),
        (
            "wood",
            "Variant square wood",
            ("variant", "square", "wood"),
            "",
            "wood.patterned_decorative",
        ),
        ("wood", "Square wood", ("square", "wood"), "", "wood.patterned_decorative"),
        ("wood", "Log wall", ("wood", "log", "wall"), "", "wood.patterned_decorative"),
        (
            "wood",
            "Stylized Woven Wood",
            ("stylized", "woven", "wood"),
            "",
            "wood.patterned_decorative",
        ),
        (
            "wood",
            "Stylized Woven Wood Planks",
            ("stylized", "woven", "wood"),
            "",
            "wood.patterned_decorative",
        ),
        (
            "wood",
            "Square Basket pattern parquet",
            ("basket", "parquet", "wood"),
            "",
            "wood.patterned_decorative",
        ),
        (
            "wood",
            "Slatted wood - Arauco MDf MAdeiral",
            ("wood", "mdf", "slat"),
            "",
            "wood.patterned_decorative",
        ),
        (
            "wood",
            "Woven Bamboo Lattice PBR",
            ("bamboo", "woven", "lattice"),
            "",
            "wood.woven_plant_fiber",
        ),
        (
            "wood",
            "Woven  Bamboo Lattice",
            ("bamboo", "woven", "lattice"),
            "",
            "wood.woven_plant_fiber",
        ),
        (
            "wood",
            "Bamboo Woven",
            ("bamboo", "woven", "pattern"),
            "",
            "wood.woven_plant_fiber",
        ),
        (
            "wood",
            "Woven Bamboo Lattice Screen",
            ("bamboo", "woven", "lattice", "screen"),
            "",
            "wood.woven_plant_fiber",
        ),
        (
            "wood",
            "Wood Design",
            ("wood", "wire", "basket"),
            "",
            "wood.woven_plant_fiber",
        ),
        ("wood", "Plywood", ("wood", "plywood", "decor"), "", "wood.plywood"),
        (
            "wood",
            "Old plywood",
            ("wood", "plywood", "old"),
            "",
            "wood.plywood",
        ),
        (
            "wood",
            "Wall with Star Shaped Ornament",
            ("concrete", "wall", "star"),
            "",
            None,
        ),
        ("wood", "Dark Wall with Star", ("concrete", "wall", "star"), "", None),
        ("wood", "Sci-Fi Panel", ("scifi", "metal", "panel"), "", None),
        (
            "wood",
            "Camouflage Netting",
            ("camouflage mesh", "textile pattern"),
            "",
            None,
        ),
    ],
)
def test_v15_classifier_resolves_known_runtime_blockers(
    category: str,
    name: str,
    tags: tuple[str, ...],
    description: str,
    expected: str | None,
) -> None:
    record = SimpleNamespace(
        category_slug=category,
        display_name=name,
        tags=tags,
        source_description=description,
    )

    assert target.suggest_material_class_id(record) == expected
