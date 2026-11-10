# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from articraft.appearance import (
    MATERIAL_CLASS_POLICY_VERSION,
    MATERIAL_CLASS_REGISTRY_SCHEMA,
    MaterialCatalog,
    MaterialClassRegistry,
    MaterialRecord,
)
from scripts import build_material_class_assignments as builder
from scripts import report_material_class_reassessment as target


def _registry(path: Path) -> MaterialClassRegistry:
    registry = MaterialClassRegistry.from_dict(
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
                    "material_class_id": "metal.polished",
                    "parent_category": "metal",
                    "display_name": "Polished metal",
                    "description": "Polished metal surface.",
                    "discovery_queries": ["polished metal"],
                    "initial_quota": 2,
                },
                {
                    "material_class_id": "plastic.matte",
                    "parent_category": "plastic",
                    "display_name": "Matte plastic",
                    "description": "Matte plastic surface.",
                    "discovery_queries": ["matte plastic"],
                    "initial_quota": 2,
                },
            ],
        }
    )
    path.write_text(json.dumps(registry.as_dict()), encoding="utf-8")
    return registry


def _catalog(tmp_path: Path) -> MaterialCatalog:
    records = []
    for material_id, category, runtime_enabled in (
        ("metal-a", "metal", True),
        ("metal-b", "metal", True),
        ("metal-c", "metal", True),
        ("metal-d", "metal", True),
        ("metal-disabled", "metal", False),
        ("plastic-review", "plastic", True),
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


def _snapshot(tmp_path: Path, *, leave_runtime_review: bool = True) -> tuple[Path, Path]:
    registry_path = tmp_path / "registry.json"
    registry = _registry(registry_path)
    catalog = _catalog(tmp_path)
    decisions = []
    for record in catalog.records:
        selected = (
            "metal.brushed"
            if record.category_slug == "metal"
            else (None if leave_runtime_review else "plastic.matte")
        )
        decisions.append(
            builder.AssignmentDecision(
                material_id=record.material_id,
                status="assigned" if selected else "review",
                material_class_id=selected,
                candidate_material_class_ids=(selected,) if selected else ("plastic.matte",),
                method="rule" if selected else "manual",
                evidence=("test",),
                note=None,
            )
        )
    snapshot = builder.build_snapshot(
        registry=registry,
        catalog=catalog,
        decisions=decisions,
        allow_runtime_review=True,
    )
    _destination, pointer = builder.publish_snapshot(snapshot, output_root=tmp_path / "assignments")
    return registry_path, pointer


def test_report_includes_zero_classes_stable_samples_and_full_runtime_review(
    tmp_path: Path,
) -> None:
    registry_path, pointer = _snapshot(tmp_path)

    report = target.build_report(registry_path=registry_path, snapshot_path=pointer)

    assert report["summary"] == {
        "registry_class_count": 3,
        "runtime_enabled_material_count": 5,
        "runtime_assigned_material_count": 4,
        "runtime_review_material_count": 1,
        "runtime_nonempty_class_count": 1,
        "empty_class_count": 2,
        "low_supply_class_count_le_3": 2,
    }
    by_class = {row["material_class_id"]: row for row in report["classes"]}
    assert by_class["metal.brushed"]["runtime_material_count"] == 4
    assert [row["material_id"] for row in by_class["metal.brushed"]["samples"]] == [
        "metal-a",
        "metal-b",
        "metal-c",
    ]
    assert by_class["metal.polished"]["runtime_material_count"] == 0
    assert by_class["metal.polished"]["samples"] == []
    assert report["empty_class_ids"] == ["metal.polished", "plastic.matte"]
    assert report["runtime_review"]["category_counts"] == {"plastic": 1}
    review_row = report["runtime_review"]["by_category"][0]["rows"][0]
    assert review_row["material_id"] == "plastic-review"
    assert set(review_row) == target._DECISION_FIELDS
    assert len(report["input_sha256"]) == 64


def test_cli_is_dry_run_unless_execute_is_explicit(tmp_path: Path, capsys) -> None:
    registry_path, pointer = _snapshot(tmp_path)
    output = tmp_path / "report.json"
    args = [
        "--registry",
        str(registry_path),
        "--snapshot",
        str(pointer),
        "--output",
        str(output),
    ]

    assert target.main(args) == 0
    dry_report = json.loads(capsys.readouterr().out)
    assert not output.exists()

    assert target.main([*args, "--execute"]) == 0
    written_report = json.loads(output.read_text(encoding="utf-8"))
    stdout_report = json.loads(capsys.readouterr().out)
    assert written_report == dry_report == stdout_report


def test_report_accepts_empty_review_file(tmp_path: Path) -> None:
    registry_path, pointer = _snapshot(tmp_path, leave_runtime_review=False)

    report = target.build_report(registry_path=registry_path, snapshot_path=pointer)

    assert report["summary"]["runtime_assigned_material_count"] == 5
    assert report["summary"]["runtime_review_material_count"] == 0
    assert report["runtime_review"] == {
        "count": 0,
        "category_counts": {},
        "by_category": [],
    }


def test_cli_refuses_to_overwrite_assignment_pointer(tmp_path: Path) -> None:
    registry_path, pointer = _snapshot(tmp_path)
    original = pointer.read_bytes()

    with pytest.raises(ValueError, match="must not overwrite an assignment input"):
        target.main(
            [
                "--registry",
                str(registry_path),
                "--snapshot",
                str(pointer),
                "--output",
                str(pointer),
                "--execute",
            ]
        )
    assert pointer.read_bytes() == original


def test_report_rejects_manifest_count_drift(tmp_path: Path) -> None:
    registry_path, pointer = _snapshot(tmp_path)
    pointer_payload = json.loads(pointer.read_text(encoding="utf-8"))
    manifest_path = pointer.parent / pointer_payload["manifest_path"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["summary"]["runtime_assigned_material_count"] += 1
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="manifest summary mismatch"):
        target.build_report(registry_path=registry_path, snapshot_path=pointer)


def test_report_rejects_pointer_escape(tmp_path: Path) -> None:
    registry_path, pointer = _snapshot(tmp_path)
    pointer_payload = json.loads(pointer.read_text(encoding="utf-8"))
    pointer_payload["snapshot_path"] = "../outside"
    pointer.write_text(json.dumps(pointer_payload), encoding="utf-8")

    with pytest.raises(ValueError, match="safe relative path"):
        target.build_report(registry_path=registry_path, snapshot_path=pointer)
