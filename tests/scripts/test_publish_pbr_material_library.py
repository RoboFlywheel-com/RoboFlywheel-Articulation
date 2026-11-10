# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import errno
import hashlib
import json
from pathlib import Path

import pytest

from scripts import publish_pbr_material_library as target


def _json_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(target._canonical_json_bytes(value, pretty=True))


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join(_json_bytes(row) for row in rows))


def _class(class_id: str, category: str) -> dict[str, object]:
    return {
        "material_class_id": class_id,
        "parent_category": category,
        "display_name": class_id,
        "description": f"Test class {class_id}.",
        "discovery_queries": [class_id.replace(".", " ")],
        "initial_quota": 2,
    }


def _build_inputs(
    workspace: Path,
    *,
    bad_blend_sha: bool = False,
    traversal: bool = False,
    extra_empty_class: bool = False,
) -> dict[str, Path]:
    registry_path = workspace / "data/material_classes_v1.json"
    registry_classes = [
        _class("metal.brushed", "metal"),
        _class("metal.polished", "metal"),
    ]
    if extra_empty_class:
        registry_classes.append(_class("metal.unused", "metal"))
    registry = {
        "schema_version": target.REGISTRY_SCHEMA,
        "classes": registry_classes,
    }
    _write_json(registry_path, registry)
    _registry, _by_id, registry_sha, _file_sha = target.load_registry(
        registry_path,
        workspace_root=workspace,
    )

    normalized = workspace / ".artifacts/pbr_material_library/normalized"
    rows: list[dict[str, object]] = []
    for material_id, runtime_enabled in (
        ("material-assigned", True),
        ("material-polished", True),
        ("material-review", True),
        ("material-disabled", False),
    ):
        package_relative = Path("packages/metal") / material_id / "v1"
        blend_relative = package_relative / "material.blend"
        metadata_relative = package_relative / "metadata.json"
        blend_path = normalized / blend_relative
        blend_path.parent.mkdir(parents=True, exist_ok=True)
        blend_payload = f"blend:{material_id}".encode()
        blend_path.write_bytes(blend_payload)
        blend_sha = hashlib.sha256(blend_payload).hexdigest()
        metadata = {
            "schema_version": "articraft-normalized-material-package/v1",
            "material_id": material_id,
            "category_slug": "metal",
            "display_name": material_id.replace("-", " ").title(),
            "material_profile": "texture_set",
            "texture_size_m": 0.5,
            "mapping_contract": {
                "mapping_profile": "metric_uv_tangent",
                "normal_space": "tangent",
                "requires_uv": True,
            },
            "package": {
                "blend_path": blend_relative.as_posix(),
                "blend_sha256": blend_sha,
            },
            "source": {"license": "cc_zero"},
        }
        _write_json(normalized / metadata_relative, metadata)
        published_blend_relative = (
            "../escape/material.blend"
            if traversal and material_id == "material-assigned"
            else blend_relative.as_posix()
        )
        rows.append(
            {
                "schema_version": "articraft-normalized-material-catalog/v1",
                "material_id": material_id,
                "asset_base_id": material_id,
                "category_slug": "metal",
                "runtime_enabled": runtime_enabled,
                "normalized_blend_path": published_blend_relative,
                "normalized_metadata_path": metadata_relative.as_posix(),
                "sha256": (
                    "0" * 64 if bad_blend_sha and material_id == "material-assigned" else blend_sha
                ),
                "license": "cc_zero",
                "provider": "test",
                "display_name": material_id.replace("-", " ").title(),
                "material_profile": "texture_set",
                "mapping_profile": "metric_uv_tangent",
                "texture_size_m": 0.5,
                "normal_space": "tangent",
                "requires_uv": True,
                "mapping_contract": {
                    "mapping_profile": "metric_uv_tangent",
                    "normal_space": "tangent",
                    "requires_uv": True,
                },
                "provenance": {
                    "catalog_row_sha256": hashlib.sha256(material_id.encode()).hexdigest(),
                    "license": "cc_zero",
                    "provider": "test",
                },
            }
        )

    catalog_payload = b"".join(_json_bytes(row) for row in rows)
    catalog_file_sha = hashlib.sha256(catalog_payload).hexdigest()
    raw_sha = "1" * 64
    allowlist_sha = "2" * 64
    catalog_sha = target._logical_catalog_sha(
        catalog_file_sha256=catalog_file_sha,
        raw_catalog_sha256=raw_sha,
        native_allowlist_sha256=allowlist_sha,
        normalizer_version=target.NORMALIZER_VERSION,
    )
    catalog_dir = normalized / "catalogs" / catalog_sha
    catalog_path = catalog_dir / "materials.jsonl"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_bytes(catalog_payload)
    catalog_manifest = {
        "schema_version": target.NORMALIZED_CATALOG_MANIFEST_SCHEMA,
        "logical_snapshot_sha256": catalog_sha,
        "materials_file": {
            "material_count": len(rows),
            "path": "materials.jsonl",
            "sha256": catalog_file_sha,
        },
        "native_runtime_allowlist_sha256": allowlist_sha,
        "normalizer_version": target.NORMALIZER_VERSION,
        "raw_catalog": {"path": "catalog/materials.jsonl", "sha256": raw_sha},
        "runtime_profile_policy_version": target.RUNTIME_PROFILE_POLICY_VERSION,
    }
    _write_json(catalog_dir / "manifest.json", catalog_manifest)
    catalog_pointer = normalized / "catalogs/latest.json"
    _write_json(
        catalog_pointer,
        {
            "catalog_path": f"catalogs/{catalog_sha}/materials.jsonl",
            "manifest_path": f"catalogs/{catalog_sha}/manifest.json",
            "logical_snapshot_sha256": catalog_sha,
        },
    )

    base_snapshot_sha = "3" * 64
    base = workspace / "pbr_material_library/snapshots" / base_snapshot_sha
    base_pool_rows: list[dict[str, object]] = []
    base_records_by_class: dict[str, list[dict[str, object]]] = {
        "metal.brushed": [],
        "metal.polished": [],
    }
    for row in rows:
        material_id = str(row["material_id"])
        if material_id not in {"material-assigned", "material-polished"}:
            continue
        material_class_id = (
            "metal.brushed" if material_id == "material-assigned" else "metal.polished"
        )
        package_relative = Path("packages/metal") / material_id / "v1"
        blend_relative = package_relative / "material.blend"
        metadata_relative = package_relative / "metadata.json"
        blend_path = normalized / blend_relative
        metadata_path = normalized / metadata_relative
        base_records_by_class[material_class_id].append(
            {
                "asset_base_id": row["asset_base_id"],
                "material_id": material_id,
                "material_class_id": material_class_id,
                "category_slug": row["category_slug"],
                "blend_path": blend_relative.as_posix(),
                "blend_sha256": row["sha256"],
                "blend_size_bytes": blend_path.stat().st_size,
                "metadata_path": metadata_relative.as_posix(),
                "metadata_sha256": target._sha256_file(metadata_path),
                "metadata_size_bytes": metadata_path.stat().st_size,
                "display_name": row["display_name"],
                "license": row["license"],
                "provider": row["provider"],
                "material_profile": row["material_profile"],
                "mapping_profile": row["mapping_profile"],
                "texture_size_m": row["texture_size_m"],
                "normal_space": row["normal_space"],
                "requires_uv": row["requires_uv"],
            }
        )
    for class_id, materials in base_records_by_class.items():
        pool_path = base / "pools/by-class" / f"{class_id}.json"
        _write_json(
            pool_path,
            {
                "schema_version": "articraft-material-class-pool/v2",
                "policy_version": target.POLICY_VERSION,
                "material_class_id": class_id,
                "parent_category": "metal",
                "material_count": len(materials),
                "materials": materials,
            },
        )
        base_pool_rows.append(
            {
                "material_class_id": class_id,
                "parent_category": "metal",
                "material_count": len(materials),
                "pool_path": pool_path.relative_to(base).as_posix(),
                "pool_sha256": target._sha256_file(pool_path),
                "pool_size_bytes": pool_path.stat().st_size,
            }
        )
    base_pool_index = base / "pools/index.json"
    _write_json(
        base_pool_index,
        {
            "schema_version": target.LEGACY_POOL_INDEX_SCHEMA,
            "policy_version": target.POLICY_VERSION,
            "logical_snapshot_sha256": base_snapshot_sha,
            "material_count": 2,
            "class_count": 2,
            "nonempty_class_count": 2,
            "empty_class_count": 0,
            "pools": base_pool_rows,
        },
    )
    base_identity = {
        "schema_version": target.LEGACY_RELEASE_SCHEMA,
        "publisher_version": target.LEGACY_PUBLISHER_VERSION,
        "material_count": 2,
        "class_count": 2,
    }
    # Content-address validation is separately exercised against the real
    # frozen release. Keep the fixture's identity digest consistent by naming
    # its directory after that digest.
    base_snapshot_sha = target._canonical_json_sha256(base_identity)
    renamed_base = base.parent / base_snapshot_sha
    base.rename(renamed_base)
    base = renamed_base
    base_pool_index = base / "pools/index.json"
    base_pool_index_value = json.loads(base_pool_index.read_text())
    base_pool_index_value["logical_snapshot_sha256"] = base_snapshot_sha
    _write_json(base_pool_index, base_pool_index_value)
    base_manifest = base / "manifest.json"
    _write_json(
        base_manifest,
        {
            "schema_version": target.LEGACY_RELEASE_SCHEMA,
            "publisher_version": target.LEGACY_PUBLISHER_VERSION,
            "logical_snapshot_sha256": base_snapshot_sha,
            "identity": base_identity,
            "files": {
                "pool_index": {
                    "path": "pools/index.json",
                    "row_count": 2,
                    "sha256": target._sha256_file(base_pool_index),
                    "size_bytes": base_pool_index.stat().st_size,
                }
            },
        },
    )

    assignment_root = normalized / "assignments"
    assignments = {
        "schema_version": target.ASSIGNMENTS_SCHEMA,
        "policy_version": target.POLICY_VERSION,
        "registry_snapshot_sha256": registry_sha,
        "catalog_snapshot_sha256": catalog_sha,
        "assignments": [
            {
                "material_id": "material-assigned",
                "material_class_id": "metal.brushed",
            },
            {
                "material_id": "material-disabled",
                "material_class_id": "metal.polished",
            },
            {
                "material_id": "material-polished",
                "material_class_id": "metal.polished",
            },
        ],
    }
    decisions = [
        {
            "material_id": "material-assigned",
            "material_class_id": "metal.brushed",
            "runtime_enabled": True,
            "status": "assigned",
        },
        {
            "material_id": "material-polished",
            "material_class_id": "metal.polished",
            "runtime_enabled": True,
            "status": "assigned",
        },
        {
            "material_id": "material-review",
            "material_class_id": None,
            "runtime_enabled": True,
            "status": "review",
        },
        {
            "material_id": "material-disabled",
            "material_class_id": "metal.polished",
            "runtime_enabled": False,
            "status": "assigned",
        },
    ]
    review = [decisions[2]]
    assignments_snapshot_sha = hashlib.sha256(target._canonical_json_bytes(assignments)).hexdigest()
    decisions_sha = hashlib.sha256(b"".join(_json_bytes(row) for row in decisions)).hexdigest()
    review_sha = hashlib.sha256(b"".join(_json_bytes(row) for row in review)).hexdigest()
    assignment_identity = {
        "schema_version": "articraft-material-class-assignment-snapshot/v1",
        "builder_version": "articraft-material-class-assignment-builder/v1",
        "policy_version": target.POLICY_VERSION,
        "catalog_snapshot_sha256": catalog_sha,
        "registry_snapshot_sha256": registry_sha,
        "assignments_snapshot_sha256": assignments_snapshot_sha,
        "decisions_sha256": decisions_sha,
        "review_sha256": review_sha,
        "runtime_ready": False,
    }
    assignment_sha = hashlib.sha256(target._canonical_json_bytes(assignment_identity)).hexdigest()
    assignment_dir = assignment_root / "snapshots" / assignment_sha
    _write_json(assignment_dir / "assignments.json", assignments)
    _write_jsonl(assignment_dir / "decisions.jsonl", decisions)
    _write_jsonl(assignment_dir / "review.jsonl", review)
    assignment_manifest = {
        **assignment_identity,
        "logical_snapshot_sha256": assignment_sha,
        "files": {
            name: {
                "sha256": target._sha256_file(assignment_dir / name),
                "row_count": count,
            }
            for name, count in (
                ("assignments.json", 3),
                ("decisions.jsonl", 4),
                ("review.jsonl", 1),
            )
        },
        "summary": {
            "runtime_assigned_material_count": 2,
            "runtime_review_material_count": 1,
        },
    }
    _write_json(assignment_dir / "manifest.json", assignment_manifest)
    assignment_pointer = assignment_root / "latest-review.json"
    _write_json(
        assignment_pointer,
        {
            "logical_snapshot_sha256": assignment_sha,
            "snapshot_path": f"snapshots/{assignment_sha}",
        },
    )
    physics = workspace / ".artifacts/physics/snapshot"
    physics_rows: list[dict[str, object]] = []
    for material_id, material_class_id in (
        ("material-assigned", "metal.brushed"),
        ("material-polished", "metal.polished"),
    ):
        material_key = hashlib.sha256(material_id.encode()).hexdigest()
        record_path = physics / "records/by-id" / material_key[:2] / f"{material_key}.json"
        record = {
            "schema_version": target.PHYSICS_ANNOTATION_SCHEMA,
            "material_id": material_id,
            "material_class_id": material_class_id,
            "reference_conditions_id": "dry-steel-23c-v1",
            "physics": {
                "density_kg_m3": 1000.0,
                "youngs_modulus_pa": 1.0e9,
                "poissons_ratio": 0.3,
                "static_friction_coefficient": 0.5,
                "dynamic_friction_coefficient": 0.4,
                "restitution_coefficient": 0.2,
            },
            "estimates": {
                field: {
                    "low": value * 0.9 if value else 0.0,
                    "value": value,
                    "high": value * 1.1 if value else 0.0,
                    "confidence": 0.8,
                    "applicability": "effective_proxy",
                    "basis": "test fixture",
                }
                for field, value in {
                    "density_kg_m3": 1000.0,
                    "youngs_modulus_pa": 1.0e9,
                    "poissons_ratio": 0.3,
                    "static_friction_coefficient": 0.5,
                    "dynamic_friction_coefficient": 0.4,
                    "restitution_coefficient": 0.2,
                }.items()
            },
            "quality": {"risk_tier": "low", "warnings": ["simulation proxy"]},
            "input": {"formal_snapshot_sha256": base_snapshot_sha},
            "model_run": {"model": "test"},
            "interpretation": {"bulk_form": "solid"},
        }
        _write_json(record_path, record)
        physics_rows.append(
            {
                "material_id": material_id,
                "material_class_id": material_class_id,
                "record_path": record_path.relative_to(physics).as_posix(),
                "record_sha256": target._sha256_file(record_path),
                "risk_tier": "low",
            }
        )
    _write_jsonl(physics / "index.jsonl", physics_rows)
    (physics / "jobs.jsonl").write_text("{}\n", encoding="utf-8")
    _write_json(
        physics / "audit.json",
        {
            "schema_version": target.PHYSICS_RUN_SCHEMA,
            "expected_count": 2,
            "valid_count": 2,
            "missing_count": 0,
            "invalid_or_extra_count": 0,
            "failures": [],
        },
    )
    _write_json(
        physics / "run.json",
        {
            "schema_version": target.PHYSICS_RUN_SCHEMA,
            "material_count": 2,
            "formal_snapshot_sha256": base_snapshot_sha,
            "formal_manifest_sha256": target._sha256_file(base_manifest),
            "formal_pool_index_sha256": target._sha256_file(base_pool_index),
            "jobs_file_sha256": target._sha256_file(physics / "jobs.jsonl"),
        },
    )
    _write_json(
        physics / "manifest.json",
        {
            "schema_version": target.PHYSICS_RUN_SCHEMA,
            "status": "complete",
            "material_count": 2,
            "formal_snapshot_sha256": base_snapshot_sha,
            "formal_manifest_sha256": target._sha256_file(base_manifest),
            "formal_pool_index_sha256": target._sha256_file(base_pool_index),
            "run_file_sha256": target._sha256_file(physics / "run.json"),
            "audit_sha256": target._sha256_file(physics / "audit.json"),
            "index_sha256": target._sha256_file(physics / "index.jsonl"),
            "jobs_file_sha256": target._sha256_file(physics / "jobs.jsonl"),
        },
    )
    _write_json(
        physics / "COMPLETE.json",
        {
            "schema_version": target.PHYSICS_RUN_SCHEMA,
            "status": "complete",
            "material_count": 2,
            "manifest_sha256": target._sha256_file(physics / "manifest.json"),
            "run_file_sha256": target._sha256_file(physics / "run.json"),
            "audit_sha256": target._sha256_file(physics / "audit.json"),
            "index_sha256": target._sha256_file(physics / "index.jsonl"),
            "jobs_file_sha256": target._sha256_file(physics / "jobs.jsonl"),
        },
    )
    return {
        "catalog": catalog_pointer,
        "assignments": assignment_pointer,
        "registry": registry_path,
        "normalized": normalized,
        "physics": physics,
        "base_appearance_manifest": base_manifest,
    }


def _publish(workspace: Path, inputs: dict[str, Path]) -> dict[str, object]:
    return target.publish_library(
        catalog_pointer=inputs["catalog"],
        assignment_pointer=inputs["assignments"],
        registry_path=inputs["registry"],
        physics_run=inputs["physics"],
        base_appearance_manifest=inputs["base_appearance_manifest"],
        output_root=workspace / "pbr_material_library",
        workspace_root=workspace,
        workers=2,
        expected_material_count=2,
        expected_class_count=2,
        expected_nonempty_class_count=2,
        expected_empty_class_count=0,
    )


def test_publish_is_exact_atomic_hardlinked_and_idempotent(tmp_path: Path) -> None:
    inputs = _build_inputs(tmp_path)

    first = _publish(tmp_path, inputs)

    assert first["material_count"] == 2
    assert first["class_count"] == 2
    assert first["nonempty_class_count"] == 2
    assert first["empty_class_count"] == 0
    assert first["hardlinked_file_count"] == 4
    assert first["copied_file_count"] == 0
    assert first["published_new"] is True
    pointer = tmp_path / "pbr_material_library/latest.json"
    pointer_value = json.loads(pointer.read_text())
    assert set(pointer_value) == {
        "schema_version",
        "logical_snapshot_sha256",
        "snapshot_path",
        "manifest_path",
        "manifest_sha256",
        "pool_index_path",
        "pool_index_sha256",
        "physics_index_path",
        "physics_index_sha256",
    }
    snapshot = tmp_path / "pbr_material_library" / pointer_value["snapshot_path"]
    pool_index = json.loads(
        (tmp_path / "pbr_material_library" / pointer_value["pool_index_path"]).read_text()
    )
    manifest = json.loads(
        (tmp_path / "pbr_material_library" / pointer_value["manifest_path"]).read_text()
    )
    assert set(manifest["files"]) == {"pool_index", "physics_index"}
    assert pool_index["logical_snapshot_sha256"] == pointer_value["logical_snapshot_sha256"]
    assert len(pool_index["pools"]) == 2
    assert pool_index["nonempty_class_count"] == 2
    assert pool_index["empty_class_count"] == 0
    brushed_pool_row = next(
        row for row in pool_index["pools"] if row["material_class_id"] == "metal.brushed"
    )
    brushed_pool = json.loads((snapshot / brushed_pool_row["pool_path"]).read_text())
    assert brushed_pool["material_count"] == 1
    assert [row["material_id"] for row in brushed_pool["materials"]] == ["material-assigned"]
    runtime_record = brushed_pool["materials"][0]
    assert set(runtime_record) == target.RUNTIME_MATERIAL_RECORD_FIELDS
    assert runtime_record["material_class_id"] == "metal.brushed"
    assert runtime_record["category_slug"] == "metal"
    assert runtime_record["mapping_profile"] == "metric_uv_tangent"
    assert runtime_record["normal_space"] == "tangent"
    assert runtime_record["requires_uv"] is True
    assert runtime_record["texture_size_m"] == 0.5
    assert runtime_record["physics_ref"]["risk_tier"] == "low"
    physics_sidecar = json.loads((snapshot / runtime_record["physics_ref"]["path"]).read_text())
    assert physics_sidecar["physics"]["density_kg_m3"] == 1000.0
    assert not (snapshot / "catalogs").exists()
    assert not (snapshot / "material_class_registry.json").exists()
    assert not (snapshot / "material_class_assignments.json").exists()
    assert not (snapshot / "packages/index.jsonl").exists()

    published_blend = snapshot / runtime_record["blend_path"]
    source_blend = inputs["normalized"] / runtime_record["blend_path"]
    assert published_blend.stat().st_ino == source_blend.stat().st_ino
    assert (
        target.validate_library(
            pointer,
            workspace_root=tmp_path,
            verify_package_hashes=True,
        )["valid"]
        is True
    )

    second = _publish(tmp_path, inputs)
    assert second["logical_snapshot_sha256"] == first["logical_snapshot_sha256"]
    assert second["published_new"] is False
    assert inputs["catalog"].is_file()


def test_validation_hash_mode_is_explicit_for_package_payloads(tmp_path: Path) -> None:
    inputs = _build_inputs(tmp_path)
    _publish(tmp_path, inputs)
    pointer = tmp_path / "pbr_material_library/latest.json"
    pointer_value = json.loads(pointer.read_text())
    snapshot = tmp_path / "pbr_material_library" / pointer_value["snapshot_path"]
    pool_index = json.loads(
        (tmp_path / "pbr_material_library" / pointer_value["pool_index_path"]).read_text()
    )
    pool = json.loads((snapshot / pool_index["pools"][0]["pool_path"]).read_text())
    blend_path = snapshot / pool["materials"][0]["blend_path"]
    payload = blend_path.read_bytes()
    blend_path.write_bytes(bytes([payload[0] ^ 1]) + payload[1:])

    size_only = target.validate_library(
        pointer,
        workspace_root=tmp_path,
        verify_package_hashes=False,
    )
    assert size_only["valid"] is True
    assert size_only["package_hashes_verified"] is False
    with pytest.raises(ValueError, match="package SHA mismatch"):
        target.validate_library(
            pointer,
            workspace_root=tmp_path,
            verify_package_hashes=True,
        )


def test_publish_rejects_catalog_traversal_without_pointer(tmp_path: Path) -> None:
    inputs = _build_inputs(tmp_path, traversal=True)

    with pytest.raises(ValueError, match="contained POSIX relative path"):
        _publish(tmp_path, inputs)

    assert not (tmp_path / "pbr_material_library/latest.json").exists()


def test_publish_rejects_bad_blend_hash_without_pointer(tmp_path: Path) -> None:
    inputs = _build_inputs(tmp_path, bad_blend_sha=True)

    with pytest.raises(ValueError, match="mismatch"):
        _publish(tmp_path, inputs)

    assert not (tmp_path / "pbr_material_library/latest.json").exists()


def test_publish_rejects_any_empty_runtime_pool(tmp_path: Path) -> None:
    inputs = _build_inputs(tmp_path, extra_empty_class=True)

    with pytest.raises(ValueError, match="requires every material class pool to be non-empty"):
        target.publish_library(
            catalog_pointer=inputs["catalog"],
            assignment_pointer=inputs["assignments"],
            registry_path=inputs["registry"],
            physics_run=inputs["physics"],
            base_appearance_manifest=inputs["base_appearance_manifest"],
            output_root=tmp_path / "pbr_material_library",
            workspace_root=tmp_path,
            workers=2,
        )

    assert not (tmp_path / "pbr_material_library/latest.json").exists()


def test_link_or_copy_only_falls_back_for_cross_device(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.write_bytes(b"payload")

    def cross_device(_source: Path, _destination: Path) -> None:
        raise OSError(errno.EXDEV, "cross-device")

    monkeypatch.setattr(target.os, "link", cross_device)
    assert target._link_or_copy(source, destination) == "copy"
    assert destination.read_bytes() == b"payload"


def test_publish_rebinds_only_explicit_zero_assignment_class_removal(
    tmp_path: Path,
) -> None:
    inputs = _build_inputs(tmp_path, extra_empty_class=True)
    old_registry = tmp_path / "old-material-class-registry.json"
    old_value = json.loads(inputs["registry"].read_text())
    _write_json(old_registry, old_value)
    old_registry_sha = target.load_registry(
        old_registry,
        workspace_root=tmp_path,
    )[2]
    old_value["classes"] = [
        row for row in old_value["classes"] if row["material_class_id"] != "metal.unused"
    ]
    _write_json(inputs["registry"], old_value)
    new_registry_sha = target.load_registry(
        inputs["registry"],
        workspace_root=tmp_path,
    )[2]

    def publish() -> dict[str, object]:
        return target.publish_library(
            catalog_pointer=inputs["catalog"],
            assignment_pointer=inputs["assignments"],
            registry_path=inputs["registry"],
            physics_run=inputs["physics"],
            base_appearance_manifest=inputs["base_appearance_manifest"],
            assignment_registry_path=old_registry,
            allowed_zero_assignment_class_removals=("metal.unused",),
            output_root=tmp_path / "pbr_material_library",
            workspace_root=tmp_path,
            workers=2,
            expected_material_count=2,
            expected_class_count=2,
            expected_nonempty_class_count=2,
            expected_empty_class_count=0,
        )

    first = publish()

    assert first["published_new"] is True
    assert first["source_registry_snapshot_sha256"] == new_registry_sha
    assert first["registry_removal_audit"] == {
        "schema_version": target.REGISTRY_REMOVAL_AUDIT_SCHEMA,
        "source_assignment_snapshot_sha256": json.loads(inputs["assignments"].read_text())[
            "logical_snapshot_sha256"
        ],
        "source_registry_snapshot_sha256": old_registry_sha,
        "target_registry_snapshot_sha256": new_registry_sha,
        "removed_zero_assignment_class_ids": ["metal.unused"],
        "removed_classes": [
            {
                "material_class_id": "metal.unused",
                "definition": _class("metal.unused", "metal"),
                "source_assignment_count": 0,
                "source_decision_count": 0,
            }
        ],
        "removed_source_assignment_count": 0,
        "removed_source_decision_count": 0,
    }
    pointer = tmp_path / "pbr_material_library/latest.json"
    pointer_value = json.loads(pointer.read_text())
    pool_index = json.loads(
        (tmp_path / "pbr_material_library" / pointer_value["pool_index_path"]).read_text()
    )
    manifest = json.loads(
        (tmp_path / "pbr_material_library" / pointer_value["manifest_path"]).read_text()
    )
    assert manifest["identity"]["source_registry_snapshot_sha256"] == new_registry_sha
    assert {row["material_class_id"] for row in pool_index["pools"]} == {
        "metal.brushed",
        "metal.polished",
    }
    assert target.validate_library(pointer, workspace_root=tmp_path)["valid"] is True

    second = publish()
    assert second["logical_snapshot_sha256"] == first["logical_snapshot_sha256"]
    assert second["published_new"] is False


def test_publish_rejects_removal_with_nonruntime_source_assignment(tmp_path: Path) -> None:
    inputs = _build_inputs(tmp_path)
    old_registry = tmp_path / "old-material-class-registry.json"
    old_value = json.loads(inputs["registry"].read_text())
    _write_json(old_registry, old_value)
    old_value["classes"] = [
        row for row in old_value["classes"] if row["material_class_id"] != "metal.polished"
    ]
    _write_json(inputs["registry"], old_value)

    with pytest.raises(ValueError, match="nonzero source assignment references"):
        target.publish_library(
            catalog_pointer=inputs["catalog"],
            assignment_pointer=inputs["assignments"],
            registry_path=inputs["registry"],
            physics_run=inputs["physics"],
            base_appearance_manifest=inputs["base_appearance_manifest"],
            assignment_registry_path=old_registry,
            allowed_zero_assignment_class_removals=("metal.polished",),
            output_root=tmp_path / "pbr_material_library",
            workspace_root=tmp_path,
            workers=2,
        )

    assert not (tmp_path / "pbr_material_library/latest.json").exists()


def test_publish_cli_defaults_to_no_empty_classes_and_accepts_explicit_zero() -> None:
    base_argument = ["--base-appearance-manifest", "/archive/v2/manifest.json"]
    defaults = target.build_parser().parse_args(["publish", *base_argument])
    explicit = target.build_parser().parse_args(
        ["publish", *base_argument, "--expect-empty-class-count", "0"]
    )

    assert defaults.expect_class_count == 124
    assert defaults.expect_nonempty_class_count == 124
    assert defaults.expect_empty_class_count == 0
    assert defaults.base_appearance_manifest == Path("/archive/v2/manifest.json")
    assert explicit.expect_empty_class_count == 0


def test_publish_rejects_physics_bound_to_tampered_base_manifest(tmp_path: Path) -> None:
    inputs = _build_inputs(tmp_path)
    base_manifest = inputs["base_appearance_manifest"]
    value = json.loads(base_manifest.read_text())
    value["publisher_version"] = "tampered"
    _write_json(base_manifest, value)

    with pytest.raises(ValueError, match="content-addressed v2 release"):
        _publish(tmp_path, inputs)

    assert not (tmp_path / "pbr_material_library/latest.json").exists()


def test_publish_rejects_physics_bound_to_tampered_base_pool_index(tmp_path: Path) -> None:
    inputs = _build_inputs(tmp_path)
    base_manifest = inputs["base_appearance_manifest"]
    base_pool_index = base_manifest.parent / "pools/index.json"
    value = json.loads(base_pool_index.read_text())
    value["material_count"] = 3
    _write_json(base_pool_index, value)

    with pytest.raises(ValueError, match="pool index receipt mismatch"):
        _publish(tmp_path, inputs)

    assert not (tmp_path / "pbr_material_library/latest.json").exists()
