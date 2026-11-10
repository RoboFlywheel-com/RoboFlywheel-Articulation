#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Validate a frozen material-class snapshot and report runtime pool coverage."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from articraft.appearance import (
    MATERIAL_CLASS_ASSIGNMENTS_SCHEMA,
    MATERIAL_CLASS_POLICY_VERSION,
    MaterialClassRegistry,
)

REPORT_SCHEMA = "articraft-material-class-reassessment-report/v1"
POINTER_SCHEMA = "articraft-material-class-assignment-pointer/v1"
SNAPSHOT_SCHEMA = "articraft-material-class-assignment-snapshot/v1"
DECISION_SCHEMA = "articraft-material-class-decision/v1"
BUILDER_VERSION = "articraft-material-class-assignment-builder/v1"

_SHA256_LENGTH = 64
_POINTER_FIELDS = {
    "schema_version",
    "logical_snapshot_sha256",
    "snapshot_path",
    "assignments_path",
    "manifest_path",
    "runtime_ready",
}
_MANIFEST_FIELDS = {
    "schema_version",
    "builder_version",
    "policy_version",
    "registry_snapshot_sha256",
    "catalog_snapshot_sha256",
    "assignments_snapshot_sha256",
    "decisions_sha256",
    "review_sha256",
    "runtime_ready",
    "logical_snapshot_sha256",
    "files",
    "summary",
}
_SUMMARY_FIELDS = {
    "catalog_material_count",
    "runtime_enabled_material_count",
    "assigned_material_count",
    "review_material_count",
    "runtime_assigned_material_count",
    "runtime_review_material_count",
    "assigned_class_count",
    "runtime_ready",
}
_DECISION_FIELDS = {
    "schema_version",
    "material_id",
    "category_slug",
    "display_name",
    "runtime_enabled",
    "status",
    "material_class_id",
    "candidate_material_class_ids",
    "method",
    "evidence",
    "note",
}
_DECISION_METHODS = {"manual", "rule", "qwen", "imported", "unassigned"}
_ASSIGNMENT_FIELDS = {
    "schema_version",
    "policy_version",
    "registry_snapshot_sha256",
    "catalog_snapshot_sha256",
    "assignments",
}


def _canonical_json_bytes(value: object, *, pretty: bool = False) -> bytes:
    if pretty:
        text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    else:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return (text + "\n").encode("utf-8")


def _canonical_jsonl_bytes(rows: Sequence[Mapping[str, Any]]) -> bytes:
    return b"".join(_canonical_json_bytes(dict(row)) for row in rows)


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _sha256(value: object, *, field: str) -> str:
    result = _text(value, field=field)
    if len(result) != _SHA256_LENGTH or any(char not in "0123456789abcdef" for char in result):
        raise ValueError(f"{field} must be a lowercase SHA-256 digest")
    return result


def _strict_object(
    value: object,
    *,
    field: str,
    fields: set[str],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be a JSON object")
    missing = sorted(fields - set(value))
    unknown = sorted(set(value) - fields)
    if missing or unknown:
        raise ValueError(f"{field} fields mismatch: missing={missing}, unknown={unknown}")
    return value


def _safe_child(root: Path, value: object, *, field: str) -> Path:
    relative = Path(_text(value, field=field))
    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        raise ValueError(f"{field} must be a safe relative path")
    target = (root / relative).resolve(strict=True)
    if root != target and root not in target.parents:
        raise ValueError(f"{field} escapes its pointer root")
    return target


@dataclass(frozen=True, slots=True)
class SnapshotPaths:
    input_path: Path
    pointer_path: Path | None
    snapshot_dir: Path
    manifest_path: Path
    assignments_path: Path
    decisions_path: Path
    review_path: Path
    pointer: dict[str, Any] | None


def resolve_snapshot(path: Path) -> SnapshotPaths:
    source = path.resolve(strict=True)
    pointer_path: Path | None = None
    pointer: dict[str, Any] | None = None
    if source.is_dir():
        snapshot_dir = source
    elif source.name == "manifest.json":
        snapshot_dir = source.parent
    else:
        pointer_path = source
        pointer = _strict_object(
            json.loads(source.read_text(encoding="utf-8")),
            field="assignment pointer",
            fields=_POINTER_FIELDS,
        )
        if pointer["schema_version"] != POINTER_SCHEMA:
            raise ValueError("unsupported assignment pointer schema")
        root = source.parent.resolve(strict=True)
        snapshot_dir = _safe_child(root, pointer["snapshot_path"], field="snapshot_path")
        if not snapshot_dir.is_dir():
            raise ValueError("snapshot_path must resolve to a directory")
        expected_manifest = _safe_child(root, pointer["manifest_path"], field="manifest_path")
        expected_assignments = _safe_child(
            root, pointer["assignments_path"], field="assignments_path"
        )
        if expected_manifest != snapshot_dir / "manifest.json":
            raise ValueError("pointer manifest_path does not match snapshot_path")
        if expected_assignments != snapshot_dir / "assignments.json":
            raise ValueError("pointer assignments_path does not match snapshot_path")

    paths = SnapshotPaths(
        input_path=source,
        pointer_path=pointer_path,
        snapshot_dir=snapshot_dir,
        manifest_path=snapshot_dir / "manifest.json",
        assignments_path=snapshot_dir / "assignments.json",
        decisions_path=snapshot_dir / "decisions.jsonl",
        review_path=snapshot_dir / "review.jsonl",
        pointer=pointer,
    )
    for required in (
        paths.manifest_path,
        paths.assignments_path,
        paths.decisions_path,
        paths.review_path,
    ):
        if not required.is_file():
            raise ValueError(f"assignment snapshot is missing {required.name}")
    return paths


def _load_jsonl(
    path: Path, *, field: str, allow_empty: bool = False
) -> tuple[list[dict[str, Any]], bytes]:
    payload = path.read_bytes()
    lines = payload.decode("utf-8").splitlines()
    if not lines and not allow_empty:
        raise ValueError(f"{field} must not be empty")
    rows: list[dict[str, Any]] = []
    for index, line in enumerate(lines):
        if not line:
            raise ValueError(f"{field}[{index}] must not be blank")
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{field}[{index}] is invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{field}[{index}] must be a JSON object")
        rows.append(value)
    if payload != _canonical_jsonl_bytes(rows):
        raise ValueError(f"{field} is not canonical JSONL")
    return rows, payload


def _validate_decisions(
    rows: list[dict[str, Any]],
    *,
    registry: MaterialClassRegistry,
) -> None:
    definitions = {row.material_class_id: row for row in registry.classes}
    categories = {row.parent_category for row in registry.classes}
    material_ids: list[str] = []
    for index, raw in enumerate(rows):
        row = _strict_object(raw, field=f"decisions[{index}]", fields=_DECISION_FIELDS)
        if row["schema_version"] != DECISION_SCHEMA:
            raise ValueError(f"decisions[{index}] has unsupported schema_version")
        material_id = _text(row["material_id"], field=f"decisions[{index}].material_id")
        material_ids.append(material_id)
        category = _text(row["category_slug"], field=f"decisions[{index}].category_slug")
        if category not in categories:
            raise ValueError(f"decisions[{index}] has no registry class for {category!r}")
        _text(row["display_name"], field=f"decisions[{index}].display_name")
        if not isinstance(row["runtime_enabled"], bool):
            raise ValueError(f"decisions[{index}].runtime_enabled must be boolean")
        status = _text(row["status"], field=f"decisions[{index}].status")
        if status not in {"assigned", "review"}:
            raise ValueError(f"decisions[{index}].status must be assigned or review")
        method = _text(row["method"], field=f"decisions[{index}].method")
        if method not in _DECISION_METHODS:
            raise ValueError(f"decisions[{index}].method is unsupported")
        if row["note"] is not None and not isinstance(row["note"], str):
            raise ValueError(f"decisions[{index}].note must be a string or null")
        for list_field in ("candidate_material_class_ids", "evidence"):
            values = row[list_field]
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                raise ValueError(f"decisions[{index}].{list_field} must be a string list")
            for value_index, value in enumerate(values):
                _text(value, field=f"decisions[{index}].{list_field}[{value_index}]")
            if len(values) != len(set(values)):
                raise ValueError(f"decisions[{index}].{list_field} contains duplicates")
        candidate_ids = row["candidate_material_class_ids"]
        for candidate_id in candidate_ids:
            definition = definitions.get(candidate_id)
            if definition is None:
                raise ValueError(f"decisions[{index}] references unknown candidate class")
            if definition.parent_category != category:
                raise ValueError(f"decisions[{index}] candidate class parent mismatch")
        selected = row["material_class_id"]
        if status == "assigned":
            if not isinstance(selected, str) or selected not in definitions:
                raise ValueError(f"decisions[{index}] assigned row has unknown material_class_id")
            if definitions[selected].parent_category != category:
                raise ValueError(f"decisions[{index}] selected class parent mismatch")
            if candidate_ids and selected not in candidate_ids:
                raise ValueError(f"decisions[{index}] selected class is absent from candidates")
        elif selected is not None:
            raise ValueError(f"decisions[{index}] review row must not select a class")
    if material_ids != sorted(material_ids):
        raise ValueError("decisions must be sorted by material_id")
    if len(material_ids) != len(set(material_ids)):
        raise ValueError("decisions repeat material_id")


def _validate_assignments(
    payload: bytes,
    *,
    manifest: Mapping[str, Any],
    registry: MaterialClassRegistry,
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    document = _strict_object(json.loads(payload), field="assignments", fields=_ASSIGNMENT_FIELDS)
    if document["schema_version"] != MATERIAL_CLASS_ASSIGNMENTS_SCHEMA:
        raise ValueError("unsupported assignments schema")
    if document["policy_version"] != MATERIAL_CLASS_POLICY_VERSION:
        raise ValueError("unsupported assignments policy")
    if document["registry_snapshot_sha256"] != registry.snapshot_sha256:
        raise ValueError("assignments registry snapshot mismatch")
    if document["catalog_snapshot_sha256"] != manifest["catalog_snapshot_sha256"]:
        raise ValueError("assignments catalog snapshot mismatch")
    rows = document["assignments"]
    if not isinstance(rows, list):
        raise ValueError("assignments.assignments must be a list")
    pairs: list[tuple[str, str]] = []
    for index, raw in enumerate(rows):
        row = _strict_object(
            raw,
            field=f"assignments.assignments[{index}]",
            fields={"material_id", "material_class_id"},
        )
        pairs.append(
            (
                _text(row["material_id"], field=f"assignments[{index}].material_id"),
                _text(row["material_class_id"], field=f"assignments[{index}].material_class_id"),
            )
        )
    if pairs != sorted(pairs):
        raise ValueError("assignments must be sorted")
    if len({material_id for material_id, _class_id in pairs}) != len(pairs):
        raise ValueError("assignments repeat material_id")
    expected_pairs = [
        (row["material_id"], row["material_class_id"])
        for row in decisions
        if row["status"] == "assigned"
    ]
    if pairs != expected_pairs:
        raise ValueError("assignments do not exactly match assigned decisions")
    logical_sha = _sha256_bytes(_canonical_json_bytes(document))
    if logical_sha != manifest["assignments_snapshot_sha256"]:
        raise ValueError("assignments logical snapshot SHA mismatch")
    return document


def _validate_manifest(
    paths: SnapshotPaths,
    *,
    registry: MaterialClassRegistry,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, str]]:
    manifest_bytes = paths.manifest_path.read_bytes()
    manifest = _strict_object(json.loads(manifest_bytes), field="manifest", fields=_MANIFEST_FIELDS)
    if manifest["schema_version"] != SNAPSHOT_SCHEMA:
        raise ValueError("unsupported assignment snapshot schema")
    if manifest["builder_version"] != BUILDER_VERSION:
        raise ValueError("unsupported assignment snapshot builder")
    if manifest["policy_version"] != MATERIAL_CLASS_POLICY_VERSION:
        raise ValueError("unsupported assignment snapshot policy")
    if manifest["registry_snapshot_sha256"] != registry.snapshot_sha256:
        raise ValueError("manifest registry snapshot mismatch")
    for field in (
        "registry_snapshot_sha256",
        "catalog_snapshot_sha256",
        "assignments_snapshot_sha256",
        "decisions_sha256",
        "review_sha256",
        "logical_snapshot_sha256",
    ):
        _sha256(manifest[field], field=f"manifest.{field}")
    if not isinstance(manifest["runtime_ready"], bool):
        raise ValueError("manifest.runtime_ready must be boolean")
    logical_sha = manifest["logical_snapshot_sha256"]
    if paths.snapshot_dir.name != logical_sha:
        raise ValueError("snapshot directory does not match its logical digest")
    identity_fields = (
        "schema_version",
        "builder_version",
        "policy_version",
        "registry_snapshot_sha256",
        "catalog_snapshot_sha256",
        "assignments_snapshot_sha256",
        "decisions_sha256",
        "review_sha256",
        "runtime_ready",
    )
    logical_identity = {field: manifest[field] for field in identity_fields}
    if _sha256_bytes(_canonical_json_bytes(logical_identity)) != logical_sha:
        raise ValueError("assignment snapshot logical identity mismatch")

    files = _strict_object(
        manifest["files"],
        field="manifest.files",
        fields={"assignments.json", "decisions.jsonl", "review.jsonl"},
    )
    file_paths = {
        "assignments.json": paths.assignments_path,
        "decisions.jsonl": paths.decisions_path,
        "review.jsonl": paths.review_path,
    }
    file_hashes: dict[str, str] = {}
    for name, path in file_paths.items():
        metadata = _strict_object(
            files[name], field=f"manifest.files.{name}", fields={"sha256", "row_count"}
        )
        digest = _sha256_path(path)
        file_hashes[name] = digest
        if metadata["sha256"] != digest:
            raise ValueError(f"{name} SHA mismatch")
        if isinstance(metadata["row_count"], bool) or not isinstance(metadata["row_count"], int):
            raise ValueError(f"manifest.files.{name}.row_count must be an integer")

    decisions, decisions_bytes = _load_jsonl(paths.decisions_path, field="decisions")
    reviews, review_bytes = _load_jsonl(paths.review_path, field="review", allow_empty=True)
    _validate_decisions(decisions, registry=registry)
    _validate_decisions(reviews, registry=registry)
    if decisions_bytes != _canonical_jsonl_bytes(decisions):
        raise ValueError("decisions canonicalization mismatch")
    if review_bytes != _canonical_jsonl_bytes(reviews):
        raise ValueError("review canonicalization mismatch")
    expected_reviews = [row for row in decisions if row["status"] == "review"]
    if reviews != expected_reviews:
        raise ValueError("review rows do not exactly match review decisions")

    assignments_bytes = paths.assignments_path.read_bytes()
    assignments = _validate_assignments(
        assignments_bytes,
        manifest=manifest,
        registry=registry,
        decisions=decisions,
    )
    row_counts = {
        "assignments.json": len(assignments["assignments"]),
        "decisions.jsonl": len(decisions),
        "review.jsonl": len(reviews),
    }
    for name, count in row_counts.items():
        if files[name]["row_count"] != count:
            raise ValueError(f"{name} row count mismatch")
    if manifest["decisions_sha256"] != file_hashes["decisions.jsonl"]:
        raise ValueError("manifest decisions SHA mismatch")
    if manifest["review_sha256"] != file_hashes["review.jsonl"]:
        raise ValueError("manifest review SHA mismatch")

    summary = _strict_object(manifest["summary"], field="manifest.summary", fields=_SUMMARY_FIELDS)
    for field in _SUMMARY_FIELDS - {"runtime_ready"}:
        value = summary[field]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"manifest.summary.{field} must be a non-negative integer")
    if not isinstance(summary["runtime_ready"], bool):
        raise ValueError("manifest.summary.runtime_ready must be boolean")
    assigned = [row for row in decisions if row["status"] == "assigned"]
    runtime = [row for row in decisions if row["runtime_enabled"]]
    runtime_assigned = [row for row in runtime if row["status"] == "assigned"]
    runtime_review = [row for row in runtime if row["status"] == "review"]
    expected_summary = {
        "catalog_material_count": len(decisions),
        "runtime_enabled_material_count": len(runtime),
        "assigned_material_count": len(assigned),
        "review_material_count": len(reviews),
        "runtime_assigned_material_count": len(runtime_assigned),
        "runtime_review_material_count": len(runtime_review),
        "assigned_class_count": len({row["material_class_id"] for row in assigned}),
        "runtime_ready": not runtime_review,
    }
    if summary != expected_summary:
        raise ValueError(
            f"manifest summary mismatch: expected={expected_summary}, actual={summary}"
        )
    if manifest["runtime_ready"] != expected_summary["runtime_ready"]:
        raise ValueError("manifest runtime_ready mismatch")

    if paths.pointer is not None:
        pointer = paths.pointer
        if pointer["logical_snapshot_sha256"] != logical_sha:
            raise ValueError("pointer logical snapshot mismatch")
        if pointer["runtime_ready"] != manifest["runtime_ready"]:
            raise ValueError("pointer runtime_ready mismatch")
    hashes = {
        "manifest_file_sha256": _sha256_bytes(manifest_bytes),
        "assignments_file_sha256": file_hashes["assignments.json"],
        "decisions_file_sha256": file_hashes["decisions.jsonl"],
        "review_file_sha256": file_hashes["review.jsonl"],
    }
    return manifest, decisions, reviews, hashes


def build_report(*, registry_path: Path, snapshot_path: Path) -> dict[str, Any]:
    registry_source = registry_path.resolve(strict=True)
    registry = MaterialClassRegistry.from_json(registry_source)
    paths = resolve_snapshot(snapshot_path)
    manifest, decisions, _reviews, file_hashes = _validate_manifest(paths, registry=registry)

    runtime_assigned = [
        row for row in decisions if row["runtime_enabled"] and row["status"] == "assigned"
    ]
    runtime_reviews = [
        row for row in decisions if row["runtime_enabled"] and row["status"] == "review"
    ]
    assigned_by_class: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in runtime_assigned:
        assigned_by_class[str(row["material_class_id"])].append(row)

    class_rows: list[dict[str, Any]] = []
    for definition in registry.classes:
        rows = sorted(
            assigned_by_class.get(definition.material_class_id, []),
            key=lambda row: (row["material_id"], row["display_name"]),
        )
        class_rows.append(
            {
                "material_class_id": definition.material_class_id,
                "parent_category": definition.parent_category,
                "runtime_material_count": len(rows),
                "samples": [
                    {
                        "material_id": row["material_id"],
                        "display_name": row["display_name"],
                        "category_slug": row["category_slug"],
                    }
                    for row in rows[:3]
                ],
            }
        )

    review_by_category: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in sorted(runtime_reviews, key=lambda row: (row["category_slug"], row["material_id"])):
        review_by_category[row["category_slug"]].append(dict(row))
    review_groups = [
        {"category_slug": category, "count": len(rows), "rows": rows}
        for category, rows in sorted(review_by_category.items())
    ]

    registry_file_sha = _sha256_path(registry_source)
    pointer_file_sha = _sha256_path(paths.pointer_path) if paths.pointer_path is not None else None
    input_identity = {
        "registry_file_sha256": registry_file_sha,
        "registry_snapshot_sha256": registry.snapshot_sha256,
        "pointer_file_sha256": pointer_file_sha,
        "assignment_logical_snapshot_sha256": manifest["logical_snapshot_sha256"],
        **file_hashes,
    }
    input_sha = _sha256_bytes(_canonical_json_bytes(input_identity))
    empty_classes = [
        row["material_class_id"] for row in class_rows if row["runtime_material_count"] == 0
    ]
    low_supply = [
        {
            "material_class_id": row["material_class_id"],
            "runtime_material_count": row["runtime_material_count"],
        }
        for row in class_rows
        if row["runtime_material_count"] <= 3
    ]
    return {
        "schema_version": REPORT_SCHEMA,
        "input_sha256": input_sha,
        "inputs": {
            "registry_path": registry_source.as_posix(),
            "assignment_input_path": paths.input_path.as_posix(),
            "resolved_snapshot_path": paths.snapshot_dir.as_posix(),
            "catalog_snapshot_sha256": manifest["catalog_snapshot_sha256"],
            **input_identity,
        },
        "summary": {
            "registry_class_count": len(registry.classes),
            "runtime_enabled_material_count": len(runtime_assigned) + len(runtime_reviews),
            "runtime_assigned_material_count": len(runtime_assigned),
            "runtime_review_material_count": len(runtime_reviews),
            "runtime_nonempty_class_count": sum(
                row["runtime_material_count"] > 0 for row in class_rows
            ),
            "empty_class_count": len(empty_classes),
            "low_supply_class_count_le_3": len(low_supply),
        },
        "classes": class_rows,
        "empty_class_ids": empty_classes,
        "low_supply_classes_le_3": low_supply,
        "runtime_review": {
            "count": len(runtime_reviews),
            "category_counts": {group["category_slug"]: group["count"] for group in review_groups},
            "by_category": review_groups,
        },
    }


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_report(registry_path=args.registry, snapshot_path=args.snapshot)
    payload = _canonical_json_bytes(report, pretty=True)
    output = args.output.resolve()
    snapshot_paths = resolve_snapshot(args.snapshot)
    snapshot_dir = snapshot_paths.snapshot_dir
    if output == snapshot_dir or snapshot_dir in output.parents:
        raise ValueError("report output must not be inside the immutable assignment snapshot")
    protected_inputs = {
        snapshot_paths.input_path,
        snapshot_paths.manifest_path,
        snapshot_paths.assignments_path,
        snapshot_paths.decisions_path,
        snapshot_paths.review_path,
    }
    if snapshot_paths.pointer_path is not None:
        protected_inputs.add(snapshot_paths.pointer_path)
    if output in protected_inputs:
        raise ValueError("report output must not overwrite an assignment input")
    if args.execute:
        _atomic_write(output, payload)
    print(payload.decode("utf-8"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
