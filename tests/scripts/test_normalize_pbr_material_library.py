# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from articraft.appearance.catalog import MaterialCatalog
from articraft.appearance.normalized import (
    NORMALIZED_CATALOG_MANIFEST_SCHEMA,
    RUNTIME_PROFILE_POLICY_VERSION,
    generic_eligibility,
    load_source_catalog,
    material_profile,
    normalized_package_paths,
    safe_relative_path,
    texture_size_m,
)
from scripts import normalize_pbr_material_library as target


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _library(tmp_path: Path) -> tuple[Path, Path, list[dict[str, object]]]:
    root = tmp_path / "library"
    rows: list[dict[str, object]] = []
    specifications = (
        (
            "texture-plastic",
            "plastic",
            "Cyan Geometric Patterned Plastic",
            {"purePbr": True, "procedural": False, "textureSizeMeters": 0.5},
        ),
        (
            "native-glass",
            "glass",
            "Clear Bottle Glass",
            {"procedural": True, "textureSizeMeters": 1.0},
        ),
    )
    for material_id, category, name, parameters in specifications:
        package = root / "raw" / category / material_id / "source.blend"
        package.parent.mkdir(parents=True, exist_ok=True)
        package.write_bytes(f"raw:{material_id}".encode())
        rows.append(
            {
                "schema_version": 1,
                "material_id": material_id,
                "category_slug": category,
                "name": name,
                "license": "royalty_free",
                "selected_file": {
                    "relative_path": package.relative_to(root).as_posix(),
                    "sha256": _sha256(package),
                },
                "source": {
                    "asset_base_id": f"asset-{material_id}",
                    "category": category,
                    "display_name": name,
                    "parameters": parameters,
                    "tags": name.lower().split(),
                },
            }
        )
    catalog = root / "catalog" / "materials.jsonl"
    catalog.parent.mkdir(parents=True)
    catalog.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    return root, catalog, rows


def _fake_inspection(source: target.SourceMaterial, destination: Path) -> dict[str, object]:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(f"normalized:{source.material_id}".encode())
    profile = source.planned_profile
    channels = (
        [
            {
                "colorspace": "Non-Color",
                "image_name": "normal.png",
                "node_path": "root/Normal",
                "packed": True,
                "role": "normal",
                "source_basename": "normal.png",
            }
        ]
        if profile == "texture_set"
        else []
    )
    return {
        "material_profile": profile,
        "texture_size_m": source.declared_texture_size_m,
        "texture_size_source": (
            "source.parameters.textureSizeMeters"
            if source.declared_texture_size_m is not None
            else None
        ),
        "channels": channels,
        "channel_counts": {"normal": 1} if channels else {},
        "node_qa": {
            "status": "pass",
            "issues": [],
            "output_surface_connected": True,
            "image_texture_count": len(channels),
            "procedural_texture_node_count": int(profile == "native_procedural"),
            "unpacked_image_count": 0,
        },
        "displacement_policy": {
            "policy": "disconnect_true_displacement",
            "source_output_link_count": 1,
            "removed_output_link_count": 1,
            "normal_and_bump_preserved": True,
        },
        "bpy_version": "5.2.0",
        "source_material_name": source.display_name,
        "available_material_names": [source.display_name],
        "package_reopen_qa": {
            "status": "pass",
            "issues": [],
            "material_count": 1,
            "material_names": [source.display_name],
            "packed_image_count": len(channels),
            "unpacked_image_count": 0,
            "true_displacement_link_count": 0,
        },
    }


@pytest.mark.parametrize(
    "value",
    ("/outside.blend", "../outside.blend", "raw/../../outside.blend", r"C:\x.blend"),
)
def test_safe_relative_path_rejects_escapes(value: str) -> None:
    with pytest.raises(ValueError, match="safe POSIX"):
        safe_relative_path(value, field="test")


def test_profile_and_texture_size_come_from_provider_metadata() -> None:
    texture = {"purePbr": True, "procedural": False, "textureSizeMeters": "0.25"}
    native = {"procedural": True, "textureSizeMeters": 1}

    assert material_profile(texture) == "texture_set"
    assert material_profile(native) == "native_procedural"
    assert (
        material_profile({}, image_texture_count=1, procedural_node_count=2) == "native_procedural"
    )
    assert texture_size_m(texture) == 0.25
    assert texture_size_m({"textureSizeMeters": -1}) is None
    assert texture_size_m({}) is None


def test_normalized_package_path_is_content_addressed_and_safe() -> None:
    first = normalized_package_paths(
        material_id="blenderkit:abc:v1",
        category_slug="plastic",
        source_sha256="a" * 64,
    )
    second = normalized_package_paths(
        material_id="blenderkit:abc:v1",
        category_slug="plastic",
        source_sha256="a" * 64,
    )

    assert first == second
    assert first[0].as_posix().startswith("packages/plastic/")
    assert first[0].name == "material.blend"
    assert first[1].name == "metadata.json"


@pytest.mark.parametrize(
    "name",
    (
        "Fabric Pattern 07",
        "Book Pattern",
        "Diamond Grid Glass Panel Green Yellow",
        "Crystal Gloss Glass",
        "Brushed black metal",
        "Fossil Reef",
        "Forest Leaves 02",
        "Industrial Dark Tech Frame",
        "Matte Tire Rubber",
        "Glossy Blue Plastic Horizontal Grooves",
        "Cyan Geometric Patterned Plastic",
        "Pebbled Basketball Rubber Material",
        "American Walnut",
        "Polished Oak Planks",
        "Wood Wood",
        "Dark Wood",
    ),
)
def test_object_specific_materials_remain_retrievable_with_soft_metadata(name: str) -> None:
    eligibility = generic_eligibility(
        display_name=name,
        profile="texture_set",
        tile_size_m=1.0,
        qa_status="pass",
    )

    assert eligibility["active"] is True
    assert eligibility["eligible_for_generic"] is True
    assert eligibility["selection_scope"] == "generic"
    assert eligibility["quarantine_reason"] is None
    assert eligibility["semantic_risk_reason"]
    assert "semantic_macro_pattern" in eligibility["qa_flags"]
    assert eligibility["semantic_advisories"]
    assert "semantic_query_required" not in eligibility["restrictions"]


def test_role_hints_are_soft_and_separate_from_technical_quarantine() -> None:
    tire = generic_eligibility(
        display_name="Matte Tire Rubber",
        category_slug="rubber",
        profile="texture_set",
        tile_size_m=1.0,
        qa_status="pass",
    )
    fabric = generic_eligibility(
        display_name="Plain White Flat",
        category_slug="fabric",
        profile="texture_set",
        tile_size_m=0.3,
        qa_status="pass",
    )

    assert tire["active"] is True
    assert tire["eligible_for_generic"] is True
    assert tire["selection_scope"] == "generic"
    assert tire["allowed_component_roles"] == []
    assert tire["recommended_component_roles"] == ["tire", "wheel"]
    assert fabric["active"] is True
    assert fabric["eligible_for_generic"] is True
    assert fabric["excluded_component_roles"] == []
    assert "prefer_surface_fabric_over_yarn_or_thread" in fabric["semantic_advisories"]
    assert fabric["material_subtype"] == "upholstery_flat_weave"


def test_node_qa_failure_is_the_only_technical_quarantine() -> None:
    eligibility = generic_eligibility(
        display_name="White plastic",
        category_slug="plastic",
        profile="texture_set",
        tile_size_m=1.0,
        qa_status="fail",
    )

    assert eligibility["active"] is False
    assert eligibility["eligible_for_generic"] is False
    assert eligibility["selection_scope"] == "quarantined"
    assert eligibility["quarantine_reason"]
    assert eligibility["semantic_risk_reason"] is None


def test_load_source_catalog_verifies_hashes_and_classifies(tmp_path: Path) -> None:
    root, catalog, _rows = _library(tmp_path)

    records = load_source_catalog(catalog, library_root=root)

    assert [record.category_slug for record in records] == ["glass", "plastic"]
    assert {record.planned_profile for record in records} == {
        "native_procedural",
        "texture_set",
    }
    assert all(record.raw_path.is_file() for record in records)


def test_load_source_catalog_rejects_hash_drift(tmp_path: Path) -> None:
    root, catalog, rows = _library(tmp_path)
    rows[0]["selected_file"]["sha256"] = "0" * 64  # type: ignore[index]
    catalog.write_text(json.dumps(rows[0]) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="source hash mismatch"):
        load_source_catalog(catalog, library_root=root)


def test_load_source_catalog_rejects_symlink_escape(tmp_path: Path) -> None:
    root = tmp_path / "library"
    outside = tmp_path / "outside.blend"
    outside.write_bytes(b"outside")
    raw = root / "raw"
    raw.mkdir(parents=True)
    (raw / "source.blend").symlink_to(outside)
    catalog = root / "catalog" / "materials.jsonl"
    catalog.parent.mkdir()
    catalog.write_text(
        json.dumps(
            {
                "material_id": "bad",
                "category_slug": "plastic",
                "selected_file": {"relative_path": "raw/source.blend"},
            }
        )
        + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="escapes the material library"):
        load_source_catalog(catalog, library_root=root)


def test_dry_run_is_read_only_and_reports_profiles(tmp_path: Path) -> None:
    root, catalog, _rows = _library(tmp_path)
    output = root / "normalized"

    first = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=False,
    )
    second = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=False,
    )

    assert first == second
    assert first["planned_profile_counts"] == {
        "native_procedural": 1,
        "texture_set": 1,
    }
    assert first["planned_reused_normalized_count"] == 0
    assert first["planned_normalizer_call_count"] == 2
    assert first["raw_sources_mutated"] is False
    assert not output.exists()


def test_execute_writes_separate_relocatable_catalog_and_metadata(tmp_path: Path) -> None:
    root, catalog, _rows = _library(tmp_path)
    output = root / "normalized"
    raw_hashes = {
        record.material_id: record.raw_sha256
        for record in load_source_catalog(catalog, library_root=root)
    }

    summary = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        normalizer=_fake_inspection,
    )

    normalized_catalog = root / summary["output_catalog"]
    manifest_path = root / summary["output_manifest"]
    rows = [json.loads(line) for line in normalized_catalog.read_text().splitlines()]
    assert summary["normalized_count"] == 2
    assert summary["normalized_profile_counts"] == {
        "native_procedural": 1,
        "texture_set": 1,
    }
    assert summary["package_reopen_status_counts"] == {"pass": 2}
    assert summary["normalization_class_counts"] == {
        "native": 1,
        "semantic_risk": 1,
    }
    assert len(rows) == 2
    assert normalized_catalog.parent.name == summary["logical_snapshot_sha256"]
    assert normalized_catalog.parent.parent.name == "catalogs"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == NORMALIZED_CATALOG_MANIFEST_SCHEMA
    assert manifest["logical_snapshot_sha256"] == summary["logical_snapshot_sha256"]
    assert manifest["materials_file"]["sha256"] == summary["output_catalog_sha256"]
    assert manifest["raw_catalog"]["sha256"] == summary["source_catalog_sha256"]
    assert manifest["normalizer_version"] == target.NORMALIZER_VERSION
    assert manifest["native_runtime_allowlist_sha256"] == summary["native_runtime_allowlist_sha256"]
    strict_catalog = MaterialCatalog.from_jsonl(
        normalized_catalog,
        strict_normalized=True,
    )
    assert strict_catalog.snapshot_sha256 == summary["logical_snapshot_sha256"]
    assert strict_catalog.manifest_path == manifest_path
    for row in rows:
        package = output / row["normalized_blend_path"]
        metadata_path = output / row["normalized_metadata_path"]
        metadata = json.loads(metadata_path.read_text())
        assert package.is_file()
        assert _sha256(package) == row["sha256"]
        assert metadata["source"]["blend_sha256"] == raw_hashes[row["material_id"]]
        assert metadata["source"]["blend_path"].startswith("raw/")
        assert not Path(metadata["source"]["blend_path"]).is_absolute()
        assert metadata["displacement_policy"]["policy"] == "disconnect_true_displacement"
        assert metadata["package"]["reopen_qa"]["status"] == "pass"
        assert row["package_reopen_qa"] == metadata["package"]["reopen_qa"]
        if row["material_profile"] == "texture_set":
            assert row["runtime_enabled"] is True
            assert row["mapping_contract"]["mapping_profile"] == "metric_uv_tangent"
            assert row["mapping_contract"]["normal_space"] == "tangent"
            assert row["mapping_contract"]["generic_box_projection_allowed"] is False
            assert row["mapping_contract"]["tile_size_m"] == 0.5
        else:
            assert row["runtime_enabled"] is False
            assert row["runtime_profile"] == {
                "enabled": False,
                "native_allowlisted": False,
                "policy_version": RUNTIME_PROFILE_POLICY_VERSION,
                "reason": "native_procedural_not_allowlisted",
            }
            assert row["mapping_contract"]["mapping_profile"] == "native_node_graph"

    current_hashes = {
        record.material_id: record.raw_sha256
        for record in load_source_catalog(catalog, library_root=root)
    }
    assert current_hashes == raw_hashes


def test_execute_is_deterministic_across_output_trees(tmp_path: Path) -> None:
    root, catalog, _rows = _library(tmp_path)
    output_a = root / "normalized_a"
    output_b = root / "normalized_b"

    summaries = []
    for output in (output_a, output_b):
        summaries.append(
            target.normalize_library(
                catalog_path=catalog,
                library_root=root,
                output_root=output,
                execute=True,
                normalizer=_fake_inspection,
            )
        )

    catalog_a = root / summaries[0]["output_catalog"]
    catalog_b = root / summaries[1]["output_catalog"]
    assert catalog_a.read_bytes() == catalog_b.read_bytes()
    assert summaries[0]["logical_snapshot_sha256"] == summaries[1]["logical_snapshot_sha256"]


def test_repeat_execute_reuses_append_only_packages_and_snapshot(tmp_path: Path) -> None:
    root, catalog, _rows = _library(tmp_path)
    output = root / "normalized"

    first = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        normalizer=_fake_inspection,
    )
    second = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        normalizer=_fake_inspection,
    )

    assert first["logical_snapshot_sha256"] == second["logical_snapshot_sha256"]
    assert second["newly_published_package_files"] == 0
    assert second["normalized_count"] == 0
    assert second["reused_normalized_count"] == 2
    assert second["reused_package_files"] == 0
    assert second["preexisting_reused_package_files"] == 4


def test_tile_size_missing_quarantine_is_strictly_reusable(tmp_path: Path) -> None:
    root, catalog, rows = _library(tmp_path)
    output = root / "normalized"
    texture_row = next(row for row in rows if row["material_id"] == "texture-plastic")
    source = texture_row["source"]
    assert isinstance(source, dict)
    parameters = source["parameters"]
    assert isinstance(parameters, dict)
    parameters.pop("textureSizeMeters")
    catalog.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    first = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        material_ids=("texture-plastic",),
        allow_qa_failures=True,
        normalizer=_fake_inspection,
    )
    normalized_row = json.loads(
        (root / first["output_catalog"]).read_text(encoding="utf-8").splitlines()[0]
    )
    assert normalized_row["normalization_class"] == "quarantine"
    assert normalized_row["active"] is False
    assert normalized_row["runtime_enabled"] is False
    assert normalized_row["runtime_profile"]["reason"] == "technical_qa_inactive"
    assert normalized_row["texture_size_m"] is None
    assert normalized_row["mapping_contract"]["tile_size_m"] is None
    assert normalized_row["validation"] == {
        "active": False,
        "status": "quarantined",
        "reasons": ["texture set has no trustworthy real-world tile size"],
    }

    dry_run = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=False,
        material_ids=("texture-plastic",),
        allow_qa_failures=True,
    )
    assert dry_run["planned_reused_normalized_count"] == 1
    assert dry_run["planned_normalizer_call_count"] == 0

    normalizer_calls: list[str] = []

    def must_not_run(
        material: target.SourceMaterial,
        destination: Path,
    ) -> dict[str, object]:
        normalizer_calls.append(material.material_id)
        return _fake_inspection(material, destination)

    second = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        material_ids=("texture-plastic",),
        allow_qa_failures=True,
        normalizer=must_not_run,
    )
    assert second["reused_normalized_count"] == 1
    assert second["normalized_count"] == 0
    assert normalizer_calls == []

    metadata_path = output / normalized_row["normalized_metadata_path"]
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["eligibility"]["active"] = True
    metadata_path.write_text(json.dumps(metadata, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="inconsistent tile-size-missing quarantine"):
        target.normalize_library(
            catalog_path=catalog,
            library_root=root,
            output_root=output,
            execute=False,
            material_ids=("texture-plastic",),
            allow_qa_failures=True,
        )


def test_incremental_execute_reuses_existing_packages_and_normalizes_only_new_sources(
    tmp_path: Path,
) -> None:
    root, catalog, rows = _library(tmp_path)
    output = root / "normalized"
    first = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        normalizer=_fake_inspection,
    )
    first_rows = [
        json.loads(line)
        for line in (root / first["output_catalog"]).read_text(encoding="utf-8").splitlines()
    ]
    existing_hashes = {
        output / row[field]: _sha256(output / row[field])
        for row in first_rows
        for field in ("normalized_blend_path", "normalized_metadata_path")
    }

    new_package = root / "raw" / "metal" / "new-metal" / "source.blend"
    new_package.parent.mkdir(parents=True)
    new_package.write_bytes(b"raw:new-metal")
    rows.append(
        {
            "schema_version": 1,
            "material_id": "new-metal",
            "category_slug": "metal",
            "name": "Brushed New Metal",
            "license": "royalty_free",
            "selected_file": {
                "relative_path": new_package.relative_to(root).as_posix(),
                "sha256": _sha256(new_package),
            },
            "source": {
                "asset_base_id": "asset-new-metal",
                "category": "metal",
                "display_name": "Brushed New Metal",
                "parameters": {
                    "purePbr": True,
                    "procedural": False,
                    "textureSizeMeters": 0.25,
                },
                "tags": ["brushed", "new", "metal"],
            },
        }
    )
    catalog.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    normalizer_calls: list[str] = []

    def count_new_only(
        source: target.SourceMaterial,
        destination: Path,
    ) -> dict[str, object]:
        normalizer_calls.append(source.material_id)
        if source.material_id != "new-metal":
            raise AssertionError(f"existing package was normalized again: {source.material_id}")
        return _fake_inspection(source, destination)

    second = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        normalizer=count_new_only,
    )

    assert normalizer_calls == ["new-metal"]
    assert second["planned_reused_normalized_count"] == 2
    assert second["planned_normalizer_call_count"] == 1
    assert second["normalized_count"] == 1
    assert second["reused_normalized_count"] == 2
    assert second["catalog_material_count"] == 3
    assert second["newly_published_package_files"] == 2
    assert second["preexisting_reused_package_files"] == 4
    assert existing_hashes == {path: _sha256(path) for path in existing_hashes}


def test_incompatible_existing_metadata_fails_before_any_normalizer_call(
    tmp_path: Path,
) -> None:
    root, catalog, _rows = _library(tmp_path)
    output = root / "normalized"
    first = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        normalizer=_fake_inspection,
    )
    first_row = json.loads(
        (root / first["output_catalog"]).read_text(encoding="utf-8").splitlines()[0]
    )
    metadata_path = output / first_row["normalized_metadata_path"]
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["normalizer"]["shader_graph_policy"] = "incompatible_test_policy"
    metadata_path.write_text(json.dumps(metadata, sort_keys=True) + "\n", encoding="utf-8")
    normalizer_calls: list[str] = []

    def must_not_run(
        source: target.SourceMaterial,
        destination: Path,
    ) -> dict[str, object]:
        normalizer_calls.append(source.material_id)
        return _fake_inspection(source, destination)

    with pytest.raises(ValueError, match="normalizer.shader_graph_policy"):
        target.normalize_library(
            catalog_path=catalog,
            library_root=root,
            output_root=output,
            execute=True,
            normalizer=must_not_run,
        )
    assert normalizer_calls == []
    assert not list(output.glob(".normalize-pbr-*"))


def test_referenced_package_is_never_overwritten(tmp_path: Path) -> None:
    root, catalog, _rows = _library(tmp_path)
    output = root / "normalized"
    summary = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        normalizer=_fake_inspection,
    )
    rows = [
        json.loads(line)
        for line in (root / summary["output_catalog"]).read_text(encoding="utf-8").splitlines()
    ]
    package = output / rows[0]["normalized_blend_path"]
    package.write_bytes(b"externally-corrupted-referenced-package")

    with pytest.raises(ValueError, match="existing normalized package hash mismatch"):
        target.normalize_library(
            catalog_path=catalog,
            library_root=root,
            output_root=output,
            execute=True,
            overwrite=True,
            normalizer=_fake_inspection,
        )
    assert package.read_bytes() == b"externally-corrupted-referenced-package"


def test_native_runtime_requires_explicit_material_id_allowlist(tmp_path: Path) -> None:
    root, catalog, _rows = _library(tmp_path)
    output = root / "normalized"
    summary = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        normalizer=_fake_inspection,
        native_runtime_material_ids=("native-glass",),
    )
    rows = [
        json.loads(line)
        for line in (root / summary["output_catalog"]).read_text(encoding="utf-8").splitlines()
    ]
    native = next(row for row in rows if row["material_id"] == "native-glass")

    assert native["runtime_enabled"] is True
    assert native["runtime_profile"]["native_allowlisted"] is True
    assert native["runtime_profile"]["reason"] == "native_procedural_explicit_allowlist"
    assert summary["runtime_enabled_count"] == 2

    with pytest.raises(ValueError, match="contains non-native"):
        target.normalize_library(
            catalog_path=catalog,
            library_root=root,
            output_root=root / "invalid-allowlist",
            execute=False,
            native_runtime_material_ids=("texture-plastic",),
        )


def test_legacy_normalized_catalog_migrates_without_mutating_source_or_packages(
    tmp_path: Path,
) -> None:
    root, catalog, _rows = _library(tmp_path)
    output = root / "normalized"
    normalized = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        normalizer=_fake_inspection,
    )
    snapshot_rows = [
        json.loads(line)
        for line in (root / normalized["output_catalog"]).read_text(encoding="utf-8").splitlines()
    ]
    for row in snapshot_rows:
        row.pop("runtime_enabled")
        row.pop("runtime_profile")
    legacy_catalog = output / "catalog" / "materials.jsonl"
    legacy_catalog.parent.mkdir(parents=True)
    legacy_catalog.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in snapshot_rows),
        encoding="utf-8",
    )
    source_before = legacy_catalog.read_bytes()
    package_hashes_before = {
        path: _sha256(path) for path in sorted((output / "packages").rglob("*")) if path.is_file()
    }

    migrated = target.snapshot_existing_normalized_catalog(
        catalog_path=legacy_catalog,
        library_root=output,
        execute=True,
    )

    assert legacy_catalog.read_bytes() == source_before
    assert migrated["source_catalog_mutated"] is False
    assert migrated["packages_mutated"] is False
    assert migrated["catalog_material_count"] == 2
    assert migrated["runtime_enabled_count"] == 1
    assert package_hashes_before == {
        path: _sha256(path) for path in sorted((output / "packages").rglob("*")) if path.is_file()
    }
    migrated_catalog = output / migrated["output_catalog"]
    loaded = MaterialCatalog.from_jsonl(
        migrated_catalog,
        library_root=output,
        strict_normalized=True,
    )
    assert loaded.snapshot_sha256 == migrated["logical_snapshot_sha256"]


def test_execute_does_not_publish_partial_catalog_on_normalizer_failure(
    tmp_path: Path,
) -> None:
    root, catalog, _rows = _library(tmp_path)
    output = root / "normalized"
    calls = 0

    def fail_second(source: target.SourceMaterial, destination: Path) -> dict[str, object]:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("inspection failed")
        return _fake_inspection(source, destination)

    with pytest.raises(RuntimeError, match="inspection failed"):
        target.normalize_library(
            catalog_path=catalog,
            library_root=root,
            output_root=output,
            execute=True,
            normalizer=fail_second,
        )

    assert not (output / "catalog" / "materials.jsonl").exists()
    assert not (output / "packages").exists()
    assert not list(output.glob(".normalize-pbr-*"))


def test_continue_on_error_checkpoints_success_and_excludes_failure(
    tmp_path: Path,
) -> None:
    root, catalog, _rows = _library(tmp_path)
    output = root / "normalized"

    def fail_native(
        source: target.SourceMaterial,
        destination: Path,
    ) -> dict[str, object]:
        if source.material_id == "native-glass":
            raise RuntimeError("broken provider graph")
        return _fake_inspection(source, destination)

    summary = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        normalizer=fail_native,
        continue_on_error=True,
    )

    assert summary["normalized_count"] == 1
    assert summary["reused_normalized_count"] == 0
    assert summary["normalization_failure_count"] == 1
    assert summary["accounted_selected_count"] == summary["selected_count"] == 2
    assert summary["newly_published_package_files"] == 2
    assert summary["normalization_failures"] == [
        {
            "material_id": "native-glass",
            "category_slug": "glass",
            "error_type": "RuntimeError",
            "message": "broken provider graph",
        }
    ]
    normalized_rows = [
        json.loads(line)
        for line in (root / summary["output_catalog"]).read_text(encoding="utf-8").splitlines()
    ]
    assert [row["material_id"] for row in normalized_rows] == ["texture-plastic"]
    assert normalized_rows[0]["runtime_enabled"] is True
    report_path = root / summary["normalization_failures_path"]
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["failure_count"] == 1
    assert report["failures"] == summary["normalization_failures"]
    assert _sha256(report_path) == summary["normalization_failures_sha256"]
    package_directories = [path.parent for path in (output / "packages").rglob("material.blend")]
    assert len(package_directories) == 1
    assert {path.name for path in package_directories[0].iterdir()} == {
        "material.blend",
        "metadata.json",
    }
    assert not list(output.glob(".normalize-pbr-*"))


def test_failed_new_source_removes_same_material_from_existing_snapshot(
    tmp_path: Path,
) -> None:
    root, catalog, rows = _library(tmp_path)
    output = root / "normalized"
    target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        normalizer=_fake_inspection,
    )
    native_row = next(row for row in rows if row["material_id"] == "native-glass")
    selected_file = native_row["selected_file"]
    assert isinstance(selected_file, dict)
    source_path = root / str(selected_file["relative_path"])
    source_path.write_bytes(b"raw:native-glass:v2")
    selected_file["sha256"] = _sha256(source_path)
    catalog.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    def fail_changed_source(
        source: target.SourceMaterial,
        destination: Path,
    ) -> dict[str, object]:
        raise RuntimeError("changed source is invalid")

    summary = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        material_ids=("native-glass",),
        normalizer=fail_changed_source,
        continue_on_error=True,
    )
    normalized_rows = [
        json.loads(line)
        for line in (root / summary["output_catalog"]).read_text(encoding="utf-8").splitlines()
    ]

    assert [row["material_id"] for row in normalized_rows] == ["texture-plastic"]
    assert summary["all_normalizer_calls_failed"] is True
    assert summary["published_existing_only"] is True
    assert summary["normalization_failure_count"] == 1


def test_continue_on_error_refuses_empty_catalog_when_all_work_fails(
    tmp_path: Path,
) -> None:
    root, catalog, _rows = _library(tmp_path)
    output = root / "normalized"

    def always_fail(
        source: target.SourceMaterial,
        destination: Path,
    ) -> dict[str, object]:
        raise RuntimeError("nothing usable")

    with pytest.raises(RuntimeError, match="all selected material normalizations failed"):
        target.normalize_library(
            catalog_path=catalog,
            library_root=root,
            output_root=output,
            execute=True,
            material_ids=("native-glass",),
            normalizer=always_fail,
            continue_on_error=True,
        )

    assert not (output / "catalogs" / "latest.json").exists()
    assert not (output / "packages").exists()
    reports = list((output / "reports" / "normalization_failures").glob("*.json"))
    assert len(reports) == 1
    assert json.loads(reports[0].read_text(encoding="utf-8"))["failure_count"] == 1


def test_existing_package_directory_rejects_extra_or_missing_files(tmp_path: Path) -> None:
    root, catalog, _rows = _library(tmp_path)
    output = root / "normalized"
    summary = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=output,
        execute=True,
        normalizer=_fake_inspection,
    )
    row = json.loads((root / summary["output_catalog"]).read_text(encoding="utf-8").splitlines()[0])
    package_directory = (output / row["normalized_blend_path"]).parent
    extra = package_directory / "unexpected.tmp"
    extra.write_text("unexpected", encoding="utf-8")

    with pytest.raises(FileExistsError, match="must contain exactly"):
        target.normalize_library(
            catalog_path=catalog,
            library_root=root,
            output_root=output,
            execute=False,
        )

    extra.unlink()
    (package_directory / "metadata.json").unlink()
    with pytest.raises(FileExistsError, match="must contain exactly"):
        target.normalize_library(
            catalog_path=catalog,
            library_root=root,
            output_root=output,
            execute=False,
        )


def test_package_pair_publication_is_atomic_and_collision_checked(tmp_path: Path) -> None:
    destination_directory = tmp_path / "normalized" / "packages" / "metal" / "identity" / "sha"
    destination_package = destination_directory / "material.blend"
    destination_metadata = destination_directory / "metadata.json"

    def staged_pair(label: str, *, package_bytes: bytes = b"package") -> tuple[Path, Path]:
        directory = tmp_path / label / "packages" / "metal" / "identity" / "sha"
        directory.mkdir(parents=True)
        package = directory / "material.blend"
        metadata = directory / "metadata.json"
        package.write_bytes(package_bytes)
        metadata.write_text('{"valid":true}\n', encoding="utf-8")
        return package, metadata

    staged_package, staged_metadata = staged_pair("staging-a")
    assert target._commit_staged_package_directory(
        staged_package=staged_package,
        staged_metadata=staged_metadata,
        destination_package=destination_package,
        destination_metadata=destination_metadata,
    ) == (2, 0)
    assert not staged_package.parent.exists()
    assert {path.name for path in destination_directory.iterdir()} == {
        "material.blend",
        "metadata.json",
    }

    duplicate_package, duplicate_metadata = staged_pair("staging-b")
    assert target._commit_staged_package_directory(
        staged_package=duplicate_package,
        staged_metadata=duplicate_metadata,
        destination_package=destination_package,
        destination_metadata=destination_metadata,
    ) == (0, 2)

    conflicting_package, conflicting_metadata = staged_pair(
        "staging-c",
        package_bytes=b"different",
    )
    with pytest.raises(FileExistsError, match="different content"):
        target._commit_staged_package_directory(
            staged_package=conflicting_package,
            staged_metadata=conflicting_metadata,
            destination_package=destination_package,
            destination_metadata=destination_metadata,
        )
    assert destination_package.read_bytes() == b"package"


def test_parallel_results_are_reassembled_deterministically(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, catalog, _rows = _library(tmp_path)
    sequential = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=root / "sequential",
        execute=True,
        normalizer=_fake_inspection,
    )
    submitted: list[str] = []
    contexts: list[object] = []

    class InlineProcessPoolExecutor:
        def __init__(self, *, max_workers: int, mp_context: object) -> None:
            assert max_workers == 2
            contexts.append(mp_context)

        def __enter__(self) -> InlineProcessPoolExecutor:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def submit(
            self,
            function: target.Normalizer,
            source: target.SourceMaterial,
            destination: Path,
        ) -> target.concurrent.futures.Future[dict[str, object]]:
            submitted.append(source.material_id)
            future: target.concurrent.futures.Future[dict[str, object]] = (
                target.concurrent.futures.Future()
            )
            future.set_result(function(source, destination))
            return future

    monkeypatch.setattr(target, "_normalize_blend_package", _fake_inspection)
    monkeypatch.setattr(
        target.concurrent.futures,
        "ProcessPoolExecutor",
        InlineProcessPoolExecutor,
    )
    original_as_completed = target.concurrent.futures.as_completed
    monkeypatch.setattr(
        target.concurrent.futures,
        "as_completed",
        lambda futures: reversed(tuple(futures)),
    )
    parallel = target.normalize_library(
        catalog_path=catalog,
        library_root=root,
        output_root=root / "parallel",
        execute=True,
        workers=2,
    )
    monkeypatch.setattr(target.concurrent.futures, "as_completed", original_as_completed)

    assert contexts[0].get_start_method() == "spawn"  # type: ignore[union-attr]
    assert submitted == ["native-glass", "texture-plastic"]
    assert parallel["workers"] == 2
    assert parallel["logical_snapshot_sha256"] == sequential["logical_snapshot_sha256"]
    assert (root / parallel["output_catalog"]).read_bytes() == (
        root / sequential["output_catalog"]
    ).read_bytes()


def test_injected_normalizer_rejects_parallel_workers(tmp_path: Path) -> None:
    root, catalog, _rows = _library(tmp_path)

    with pytest.raises(ValueError, match="injected normalizer requires workers=1"):
        target.normalize_library(
            catalog_path=catalog,
            library_root=root,
            output_root=root / "normalized",
            execute=True,
            normalizer=_fake_inspection,
            workers=2,
        )


def test_output_root_must_not_be_raw_or_outside_library(tmp_path: Path) -> None:
    root, catalog, _rows = _library(tmp_path)

    with pytest.raises(ValueError, match="separate from the raw"):
        target.normalize_library(
            catalog_path=catalog,
            library_root=root,
            output_root=root / "raw" / "normalized",
            execute=False,
        )
    with pytest.raises(ValueError, match="inside the source library"):
        target.normalize_library(
            catalog_path=catalog,
            library_root=root,
            output_root=tmp_path / "outside",
            execute=False,
        )


def test_cli_is_dry_run_unless_execute_is_explicit() -> None:
    parser = target.build_parser()

    assert parser.parse_args(["--catalog", "materials.jsonl"]).execute is False
    assert parser.parse_args(["--catalog", "materials.jsonl", "--execute"]).execute is True
    parallel = parser.parse_args(
        ["--catalog", "materials.jsonl", "--workers", "4", "--continue-on-error"]
    )
    assert parallel.workers == 4
    assert parallel.continue_on_error is True
    migrated = parser.parse_args(
        [
            "--catalog",
            "normalized/catalog/materials.jsonl",
            "--snapshot-existing-normalized",
            "--native-runtime-material-id",
            "native-glass",
        ]
    )
    assert migrated.snapshot_existing_normalized is True
    assert migrated.native_runtime_material_id == ["native-glass"]
