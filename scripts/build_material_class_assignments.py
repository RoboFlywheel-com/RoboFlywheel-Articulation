#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Build a content-addressed exact material-class assignment sidecar.

The decision file is offline audit input.  Every catalog material appears
exactly once as either ``assigned`` or ``review``.  Only the compact
``assignments.json`` document is a runtime input; review candidates, evidence,
and annotation methods never participate in runtime retrieval.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from articraft.appearance import (  # noqa: E402
    MATERIAL_CLASS_ASSIGNMENTS_SCHEMA,
    MATERIAL_CLASS_POLICY_VERSION,
    MaterialCatalog,
    MaterialClassAssignments,
    MaterialClassRegistry,
    build_assignment_document,
)

DECISION_SCHEMA = "articraft-material-class-decision/v1"
SNAPSHOT_MANIFEST_SCHEMA = "articraft-material-class-assignment-snapshot/v1"
SNAPSHOT_POINTER_SCHEMA = "articraft-material-class-assignment-pointer/v1"
BUILDER_VERSION = "articraft-material-class-assignment-builder/v1"
LOCAL_CLASSIFIER_VERSION = "articraft-material-class-local-classifier/v17"
DECISION_METHODS = frozenset({"manual", "rule", "qwen", "imported", "unassigned"})
DECISION_INPUT_FIELDS = frozenset(
    {
        "schema_version",
        "material_id",
        "status",
        "material_class_id",
        "candidate_material_class_ids",
        "method",
        "evidence",
        "note",
    }
)

DEFAULT_REGISTRY = REPO_ROOT / "data/material_classes_v1.json"
DEFAULT_CATALOG = REPO_ROOT / ".artifacts/pbr_material_library/normalized/catalogs/latest.json"
DEFAULT_OUTPUT_ROOT = (
    REPO_ROOT / ".artifacts/pbr_material_library/normalized/material_class_assignments"
)


def _canonical_json_bytes(value: object, *, pretty: bool = False) -> bytes:
    if pretty:
        text = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    else:
        text = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    return (text + "\n").encode("utf-8")


def _canonical_jsonl_bytes(rows: Iterable[Mapping[str, Any]]) -> bytes:
    return b"".join(_canonical_json_bytes(dict(row)) for row in rows)


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


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


def _text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _optional_text(value: object, *, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field} must be a string or null")
    result = value.strip()
    return result or None


def _string_tuple(
    value: object,
    *,
    field: str,
    allow_empty: bool = True,
) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, list):
        raise ValueError(f"{field} must be a list of strings")
    result = tuple(_text(item, field=f"{field}[{index}]") for index, item in enumerate(value))
    if not allow_empty and not result:
        raise ValueError(f"{field} must not be empty")
    if len(result) != len(set(result)):
        raise ValueError(f"{field} must not contain duplicates")
    return result


def resolve_catalog_pointer(path: Path) -> tuple[Path, Path]:
    """Return ``(catalog_jsonl, normalized_library_root)`` safely."""

    source = path.resolve(strict=True)
    if source.is_dir():
        catalog = source / "materials.jsonl"
        if not catalog.is_file():
            raise ValueError(f"normalized catalog snapshot has no materials.jsonl: {source}")
        source = catalog.resolve(strict=True)
    elif source.name == "manifest.json":
        catalog = source.with_name("materials.jsonl")
        if not catalog.is_file():
            raise ValueError(f"normalized catalog manifest has no materials.jsonl: {source}")
        source = catalog.resolve(strict=True)
    if source.suffix == ".jsonl":
        if source.parent.parent.name == "catalogs":
            return source, source.parents[2]
        return source, source.parent.parent
    pointer = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(pointer, dict):
        raise ValueError(f"catalog pointer must be a JSON object: {source}")
    relative = Path(str(pointer.get("catalog_path") or ""))
    if not relative.parts or relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"catalog pointer contains an unsafe path: {source}")
    normalized_root = source.parent.parent.resolve(strict=True)
    catalog = (normalized_root / relative).resolve(strict=True)
    if normalized_root != catalog and normalized_root not in catalog.parents:
        raise ValueError(f"catalog pointer escapes normalized root: {source}")
    logical_sha = _text(
        pointer.get("logical_snapshot_sha256"),
        field="logical_snapshot_sha256",
    )
    if catalog.parent.name != logical_sha:
        raise ValueError("catalog pointer logical digest does not match snapshot path")
    return catalog, normalized_root


def load_catalog(
    path: Path,
    *,
    library_root: Path | None = None,
) -> MaterialCatalog:
    catalog_path, inferred_root = resolve_catalog_pointer(path)
    return MaterialCatalog.from_jsonl(
        catalog_path,
        library_root=(library_root.resolve(strict=True) if library_root else inferred_root),
        verify_hashes=True,
        strict_normalized=True,
    )


@dataclass(frozen=True, slots=True)
class AssignmentDecision:
    material_id: str
    status: str
    material_class_id: str | None
    candidate_material_class_ids: tuple[str, ...]
    method: str
    evidence: tuple[str, ...]
    note: str | None

    def audit_row(self, catalog: MaterialCatalog) -> dict[str, Any]:
        record = next(row for row in catalog.records if row.material_id == self.material_id)
        return {
            "schema_version": DECISION_SCHEMA,
            "material_id": self.material_id,
            "category_slug": record.category_slug,
            "display_name": record.display_name,
            "runtime_enabled": record.runtime_enabled,
            "status": self.status,
            "material_class_id": self.material_class_id,
            "candidate_material_class_ids": list(self.candidate_material_class_ids),
            "method": self.method,
            "evidence": list(self.evidence),
            "note": self.note,
        }


@dataclass(frozen=True, slots=True)
class InheritedAssignmentSnapshot:
    snapshot_path: Path
    logical_snapshot_sha256: str
    manifest_sha256: str
    assignments_snapshot_sha256: str
    decisions_sha256: str
    decisions: tuple[AssignmentDecision, ...]


def _resolve_assignment_snapshot_dir(path: Path) -> Path:
    source = path.resolve(strict=True)
    if source.is_dir():
        return source
    if source.name in {"latest.json", "latest-review.json"}:
        pointer = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(pointer, dict) or pointer.get("schema_version") != (
            SNAPSHOT_POINTER_SCHEMA
        ):
            raise ValueError(f"unsupported assignment snapshot pointer: {source}")
        relative = Path(str(pointer.get("snapshot_path") or ""))
        if not relative.parts or relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"assignment snapshot pointer contains an unsafe path: {source}")
        root = source.parent.resolve(strict=True)
        snapshot = (root / relative).resolve(strict=True)
        if root != snapshot and root not in snapshot.parents:
            raise ValueError(f"assignment snapshot pointer escapes its root: {source}")
        if not snapshot.is_dir():
            raise ValueError(f"assignment snapshot pointer target is not a directory: {snapshot}")
        return snapshot
    if source.name in {"manifest.json", "assignments.json", "decisions.jsonl", "review.jsonl"}:
        return source.parent
    raise ValueError(
        "inherit snapshot must be a snapshot directory, pointer, manifest, "
        "assignments.json, decisions.jsonl, or review.jsonl"
    )


def _decision_from_row(
    value: Mapping[str, Any],
    *,
    index: int,
    registry: MaterialClassRegistry,
    catalog_by_id: Mapping[str, Any],
) -> AssignmentDecision:
    unknown = sorted(set(value) - DECISION_INPUT_FIELDS)
    if unknown:
        raise ValueError(f"decision[{index}] has unsupported fields: {unknown}")
    if value.get("schema_version") != DECISION_SCHEMA:
        raise ValueError(f"decision[{index}] has unsupported schema_version")
    material_id = _text(value.get("material_id"), field=f"decision[{index}].material_id")
    record = catalog_by_id.get(material_id)
    if record is None:
        raise ValueError(f"decision[{index}] references unknown material_id: {material_id}")
    status = _text(value.get("status"), field=f"decision[{index}].status")
    if status not in {"assigned", "review"}:
        raise ValueError(f"decision[{index}].status must be assigned or review")
    method = _text(value.get("method"), field=f"decision[{index}].method")
    if method not in DECISION_METHODS:
        raise ValueError(f"decision[{index}].method must be one of {sorted(DECISION_METHODS)}")
    evidence = _string_tuple(
        value.get("evidence", []),
        field=f"decision[{index}].evidence",
    )
    note = _optional_text(value.get("note"), field=f"decision[{index}].note")
    candidate_ids = _string_tuple(
        value.get("candidate_material_class_ids", []),
        field=f"decision[{index}].candidate_material_class_ids",
    )
    definitions = []
    for candidate_id in candidate_ids:
        try:
            definitions.append(registry.get(candidate_id))
        except KeyError as exc:
            raise ValueError(str(exc)) from exc
    wrong_candidate_parents = [
        definition.material_class_id
        for definition in definitions
        if definition.parent_category != record.category_slug
    ]
    if wrong_candidate_parents:
        raise ValueError(
            f"decision[{index}] candidate class parent mismatch: {wrong_candidate_parents}"
        )

    material_class_id = _optional_text(
        value.get("material_class_id"),
        field=f"decision[{index}].material_class_id",
    )
    if status == "assigned":
        if material_class_id is None:
            raise ValueError(f"decision[{index}] assigned row has no material_class_id")
        if method == "unassigned":
            raise ValueError(f"decision[{index}] assigned row cannot use unassigned method")
        try:
            definition = registry.get(material_class_id)
        except KeyError as exc:
            raise ValueError(str(exc)) from exc
        if definition.parent_category != record.category_slug:
            raise ValueError(
                f"decision[{index}] material category {record.category_slug!r} "
                f"does not match class parent {definition.parent_category!r}"
            )
        if candidate_ids and material_class_id not in candidate_ids:
            raise ValueError(f"decision[{index}] selected class is absent from candidate list")
    elif material_class_id is not None:
        raise ValueError(f"decision[{index}] review row must not select material_class_id")

    return AssignmentDecision(
        material_id=material_id,
        status=status,
        material_class_id=material_class_id,
        candidate_material_class_ids=candidate_ids,
        method=method,
        evidence=evidence,
        note=note,
    )


def load_inherited_assignment_snapshot(
    path: Path,
    *,
    registry: MaterialClassRegistry,
    catalog: MaterialCatalog,
) -> InheritedAssignmentSnapshot:
    """Validate and load one older assignment snapshot against a superset catalog."""

    snapshot = _resolve_assignment_snapshot_dir(path)
    manifest_path = snapshot / "manifest.json"
    assignments_path = snapshot / "assignments.json"
    decisions_path = snapshot / "decisions.jsonl"
    review_path = snapshot / "review.jsonl"
    for required in (manifest_path, assignments_path, decisions_path, review_path):
        if not required.is_file():
            raise ValueError(f"inherit snapshot is missing {required.name}: {snapshot}")

    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes)
    if not isinstance(manifest, dict):
        raise ValueError("inherit snapshot manifest must be an object")
    if manifest.get("schema_version") != SNAPSHOT_MANIFEST_SCHEMA:
        raise ValueError("inherit snapshot manifest schema mismatch")
    if manifest.get("builder_version") != BUILDER_VERSION:
        raise ValueError("inherit snapshot builder version mismatch")
    if manifest.get("policy_version") != MATERIAL_CLASS_POLICY_VERSION:
        raise ValueError("inherit snapshot policy version mismatch")
    if manifest.get("registry_snapshot_sha256") != registry.snapshot_sha256:
        raise ValueError("inherit snapshot registry mismatch")

    logical_sha = _text(
        manifest.get("logical_snapshot_sha256"),
        field="inherit.logical_snapshot_sha256",
    )
    if snapshot.name != logical_sha:
        raise ValueError("inherit snapshot directory does not match logical digest")
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
    logical_identity = {field: manifest.get(field) for field in identity_fields}
    if _sha256_bytes(_canonical_json_bytes(logical_identity)) != logical_sha:
        raise ValueError("inherit snapshot logical identity mismatch")

    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ValueError("inherit snapshot manifest has no files table")
    payloads = {
        "assignments.json": assignments_path.read_bytes(),
        "decisions.jsonl": decisions_path.read_bytes(),
        "review.jsonl": review_path.read_bytes(),
    }
    for name, payload in payloads.items():
        metadata = files.get(name)
        if not isinstance(metadata, dict) or metadata.get("sha256") != _sha256_bytes(payload):
            raise ValueError(f"inherit snapshot {name} SHA mismatch")

    assignments_document = json.loads(payloads["assignments.json"])
    if not isinstance(assignments_document, dict):
        raise ValueError("inherit snapshot assignments document must be an object")
    allowed_assignment_fields = {
        "schema_version",
        "policy_version",
        "registry_snapshot_sha256",
        "catalog_snapshot_sha256",
        "assignments",
    }
    if set(assignments_document) != allowed_assignment_fields:
        raise ValueError("inherit snapshot assignments document fields mismatch")
    if assignments_document.get("schema_version") != MATERIAL_CLASS_ASSIGNMENTS_SCHEMA:
        raise ValueError("inherit snapshot assignments schema mismatch")
    if assignments_document.get("policy_version") != MATERIAL_CLASS_POLICY_VERSION:
        raise ValueError("inherit snapshot assignments policy mismatch")
    if assignments_document.get("registry_snapshot_sha256") != registry.snapshot_sha256:
        raise ValueError("inherit snapshot assignments registry mismatch")
    if assignments_document.get("catalog_snapshot_sha256") != manifest.get(
        "catalog_snapshot_sha256"
    ):
        raise ValueError("inherit snapshot assignments catalog mismatch")
    raw_assignments = assignments_document.get("assignments")
    if not isinstance(raw_assignments, list):
        raise ValueError("inherit snapshot assignments must be a list")
    document_pairs: list[tuple[str, str]] = []
    for index, row in enumerate(raw_assignments):
        if not isinstance(row, dict) or set(row) != {"material_id", "material_class_id"}:
            raise ValueError(f"inherit assignment[{index}] has invalid fields")
        document_pairs.append(
            (
                _text(row.get("material_id"), field=f"inherit assignment[{index}].material_id"),
                _text(
                    row.get("material_class_id"),
                    field=f"inherit assignment[{index}].material_class_id",
                ),
            )
        )
    if files["assignments.json"].get("row_count") != len(raw_assignments):
        raise ValueError("inherit snapshot assignments.json row count mismatch")
    assignments_canonical = {
        **{
            field: assignments_document[field]
            for field in allowed_assignment_fields - {"assignments"}
        },
        "assignments": sorted(
            raw_assignments,
            key=lambda row: (str(row.get("material_id")), str(row.get("material_class_id"))),
        ),
    }
    assignments_sha = _sha256_bytes(_canonical_json_bytes(assignments_canonical))
    if assignments_sha != manifest.get("assignments_snapshot_sha256"):
        raise ValueError("inherit snapshot assignments logical digest mismatch")

    catalog_by_id = {row.material_id: row for row in catalog.records}
    raw_decisions: list[dict[str, Any]] = []
    decisions: list[AssignmentDecision] = []
    for index, line in enumerate(payloads["decisions.jsonl"].decode("utf-8").splitlines()):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"inherit decision[{index}] must be an object")
        material_id = _text(row.get("material_id"), field=f"inherit decision[{index}].material_id")
        if material_id not in catalog_by_id:
            raise ValueError(
                f"inherit snapshot material is absent from current catalog: {material_id}"
            )
        input_row = {field: row.get(field) for field in DECISION_INPUT_FIELDS}
        raw_decisions.append(row)
        decisions.append(
            _decision_from_row(
                input_row,
                index=index,
                registry=registry,
                catalog_by_id=catalog_by_id,
            )
        )
    material_ids = [row.material_id for row in decisions]
    if len(material_ids) != len(set(material_ids)):
        raise ValueError("inherit snapshot decisions repeat material_id")
    if files["decisions.jsonl"].get("row_count") != len(decisions):
        raise ValueError("inherit snapshot decisions.jsonl row count mismatch")
    summary = manifest.get("summary")
    if not isinstance(summary, dict) or summary.get("catalog_material_count") != len(decisions):
        raise ValueError("inherit snapshot decision coverage mismatch")

    assigned_pairs = sorted(
        (row.material_id, str(row.material_class_id))
        for row in decisions
        if row.status == "assigned"
    )
    if sorted(document_pairs) != assigned_pairs:
        raise ValueError("inherit snapshot assignments do not match assigned decisions")
    inherited_reviews = [row for row in raw_decisions if str(row.get("status") or "") == "review"]
    if _canonical_jsonl_bytes(inherited_reviews) != payloads["review.jsonl"]:
        raise ValueError("inherit snapshot review queue does not match decisions")
    if files["review.jsonl"].get("row_count") != len(inherited_reviews):
        raise ValueError("inherit snapshot review.jsonl row count mismatch")

    return InheritedAssignmentSnapshot(
        snapshot_path=snapshot,
        logical_snapshot_sha256=logical_sha,
        manifest_sha256=_sha256_bytes(manifest_bytes),
        assignments_snapshot_sha256=assignments_sha,
        decisions_sha256=_sha256_bytes(payloads["decisions.jsonl"]),
        decisions=tuple(sorted(decisions, key=lambda row: row.material_id)),
    )


def load_decisions(
    path: Path,
    *,
    registry: MaterialClassRegistry,
    catalog: MaterialCatalog,
) -> tuple[AssignmentDecision, ...]:
    source = path.resolve(strict=True)
    values: list[dict[str, Any]] = []
    for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"decision line {line_number} must be an object")
        values.append(value)
    if not values:
        raise ValueError("decision file must not be empty")
    catalog_by_id = {row.material_id: row for row in catalog.records}
    decisions = tuple(
        _decision_from_row(
            value,
            index=index,
            registry=registry,
            catalog_by_id=catalog_by_id,
        )
        for index, value in enumerate(values)
    )
    material_ids = [row.material_id for row in decisions]
    if len(material_ids) != len(set(material_ids)):
        raise ValueError("decision file repeats material_id")
    missing = sorted(set(catalog_by_id) - set(material_ids))
    if missing:
        raise ValueError(f"decision file does not cover catalog: {missing[:5]}")
    return tuple(sorted(decisions, key=lambda row: row.material_id))


def initial_review_rows(
    *,
    registry: MaterialClassRegistry,
    catalog: MaterialCatalog,
) -> tuple[dict[str, Any], ...]:
    result = []
    for record in sorted(catalog.records, key=lambda row: row.material_id):
        candidates = [
            definition.material_class_id
            for definition in registry.by_parent_category(record.category_slug)
        ]
        result.append(
            {
                "schema_version": DECISION_SCHEMA,
                "material_id": record.material_id,
                "status": "review",
                "material_class_id": None,
                "candidate_material_class_ids": candidates,
                "method": "unassigned",
                "evidence": [],
                "note": None,
            }
        )
    return tuple(result)


def suggest_material_class_id(record: Any) -> str | None:
    """Return one conservative offline suggestion for the current visual taxonomy.

    This is exact, inspectable migration policy for provider metadata.  It is
    never imported by runtime retrieval.  Explicit material identity/finish in
    the display name wins over incidental provider tags such as ``scratched``.
    """

    category = record.category_slug
    name = record.display_name.casefold()
    normalized_name = " ".join(name.split())
    tags = " ".join(str(value).casefold() for value in record.tags)
    source_category = str(getattr(record, "source_category_slug", None) or "").casefold()
    text = f"{name} {tags}"
    source_description = str(getattr(record, "source_description", None) or "").casefold()
    if category in {"organic", "rust", "tech"}:
        text = f"{text} {source_description}"
    words = set("".join(char if char.isalnum() else " " for char in text).split())
    name_words = set("".join(char if char.isalnum() else " " for char in name).split())
    if category == "asphalt":
        if any(marker in name for marker in ("concrete", "cement", "plaster")):
            return None
        return (
            "asphalt.weathered_damaged"
            if any(
                marker in text
                for marker in (
                    "snow",
                    "weathered",
                    "crack",
                    "damaged",
                    "old concrete",
                    "patched",
                    "broken",
                )
            )
            else "asphalt.plain_road"
        )
    if category == "ceramic":
        if any(marker in name for marker in ("granite", "marble")):
            return None
        if "brake" in text:
            return "ceramic.porcelain_glazed_plain"
        if any(marker in text for marker in ("blue willow", "floral", "patterned porcelain")):
            return "ceramic.decorative_glazed"
        if any(marker in name for marker in ("clay", "earthen", "terracotta")):
            return "ceramic.terracotta_earthenware"
        if any(marker in text for marker in ("tile", "floor", "patio", "granite")):
            return "ceramic.architectural_tile"
        return "ceramic.porcelain_glazed_plain"
    if category == "concrete":
        if "facade" in name and any(marker in text for marker in ("window", "glass")):
            return None
        if any(
            marker in text
            for marker in ("board formed", "boardformed", "garage floor", "industrial floor")
        ):
            return "concrete.formed_patterned"
        if any(
            marker in text
            for marker in ("rough", "dirty", "weathered", "damaged", "crack", "old", "broken")
        ):
            return "concrete.rough_weathered"
        return "concrete.smooth_cast"
    if category == "fabric":
        if name in {"cellophane", "flag color changeable", "old clay rusty texture", "wood"} or any(
            marker in name for marker in ("rough floor planks", "sci-fi armor plated surface")
        ):
            return None
        if normalized_name in {
            "reddish leather",
            "puffy weathered red rubber",
        }:
            return None
        if normalized_name == "hook" and {"wires", "plastic", "rubber"}.issubset(words):
            return None
        if normalized_name == "red worn sofa":
            return "fabric.upholstery_plain"
        if (
            normalized_name == "zarape"
            or "wave" in name_words
            or ("fabric" in name_words and {"panel", "panels"}.intersection(name_words))
        ):
            return "fabric.printed_pattern"
        if any(marker in text for marker in ("corduroy", "cordoroy", "ribbed fabric")) or any(
            marker in source_description for marker in ("corduroy", "cordoroy")
        ):
            return "fabric.corduroy_ribbed"
        if normalized_name == "nylon v2" and ("mesh" in words or "sheer" in source_description):
            return "fabric.open_mesh"
        if normalized_name == "hessian sackcloth":
            return "fabric.canvas"
        if "velvet" in source_description:
            return "fabric.velvet"
        if any(marker in text for marker in ("carbon fiber", "carbon fibre")):
            return "fabric.carbon_weave"
        if any(marker in text for marker in ("webbing", "woven strap", "seat belt")):
            return "fabric.webbing"
        if any(
            marker in text
            for marker in (
                "open mesh",
                "fabric mesh",
                "textile mesh",
                "netting",
                "perforated",
                "lace",
                "spacer mesh",
                "window screen",
                "syntetic net",
                "rattan wicker",
                "seamless wicker",
                "wicker",
            )
        ) or name_words.intersection({"mesh", "net"}):
            return "fabric.open_mesh"
        if any(
            marker in text for marker in ("thread", "yarn", "rope", "knit", "knitted", "crochet")
        ):
            return "fabric.thread_yarn"
        if any(marker in text for marker in ("foam", "sponge")):
            return "fabric.flexible_foam"
        if any(marker in name for marker in ("satin", "silk")):
            return "fabric.satin_silk"
        if (
            any(
                marker in name
                for marker in (
                    "carpet",
                    "rug",
                    "fleece",
                    "boucle",
                    "sherpa",
                    "furry",
                    "terrycloth",
                    "terry cloth",
                    "towel",
                )
            )
            or "fur" in name_words
        ):
            return "fabric.carpet_fleece"
        if "jacquard" in text:
            return "fabric.jacquard"
        if source_category == "velvet" or "velvet" in text:
            return "fabric.velvet"
        if "felt" in text:
            return "fabric.felt"
        if source_category == "sheer" or "sheer" in text:
            return "fabric.sheer"
        if any(marker in text for marker in ("corduroy", "cordoroy", "ribbed fabric")):
            return "fabric.corduroy_ribbed"
        if any(marker in text for marker in ("denim", "jean", "twill")):
            return "fabric.denim_twill"
        if any(
            marker in text
            for marker in (
                "quilt",
                "quilted",
                "tufted",
                "padded",
                "pleated",
                "waffle",
                "pique",
                "capitone",
                "puffy",
                "wrinkled",
                "creased",
                "stitched blanket",
            )
        ):
            return "fabric.quilted_pleated"
        if any(
            marker in text
            for marker in (
                "carpet",
                "rug",
                "fleece",
                "boucle",
                "sherpa",
                "furry",
                "terrycloth",
                "terry cloth",
                "towel",
            )
        ):
            return "fabric.carpet_fleece"
        if any(marker in text for marker in ("satin", "silk")):
            return "fabric.satin_silk"
        if (
            name == "cat"
            or source_category in {"print", "embroidery"}
            or any(
                marker in text
                for marker in (
                    "print",
                    "embroidery",
                    "pattern 07",
                    "checkered",
                    "geometric",
                    "stripe",
                    "graphical_abstract",
                    "animalskins",
                    "camouflage",
                    "herringbone",
                    "houndstooth",
                    "pattern",
                    "floral",
                    "tartan",
                    "gingham",
                    "brocade",
                    "ornament",
                    "sequin",
                    "camo",
                    "plaid",
                    " check ",
                    "embroidered",
                    "celtic",
                    "hexagonal",
                    "square",
                    "patch",
                    "leaves",
                    "sci-fi pads",
                    "scifi fabric panels",
                )
            )
        ):
            return "fabric.printed_pattern"
        if any(marker in text for marker in ("canvas", "burlap", "sacking", "jute")):
            return "fabric.canvas"
        if source_category in {
            "chenille",
            "suede",
            "texture",
            "vinyl-imitation-leather",
        } or any(
            marker in text
            for marker in (
                "chenille",
                "suede",
                "upholstery",
                "vinyl",
                "sofa",
                "couch",
                "chesterfield",
                "curtain",
                "synthetic leather",
                "leatherette",
                "leather",
                "furniture",
                "bed panel",
                "jacket",
            )
        ):
            return "fabric.upholstery_plain"
        return "fabric.plain_flat_weave"
    if category == "glass":
        if any(
            marker in name
            for marker in (
                "windows brick facade",
                "lush green grass",
                "acrylic",
            )
        ):
            return None
        if any(
            marker in text for marker in ("crack", "scratch", "damaged", "chipped", "shattered")
        ):
            return "glass.damaged_cracked"
        if "mirror" in text:
            return "glass.mirror"
        if "frosted" in text:
            return "glass.frosted_smooth"
        if "opaque" in name_words or any(
            marker in text
            for marker in ("smoked", "tinted", "dark glass", "black glass", "opaque glass")
        ):
            return "glass.smoked_tinted"
        if any(
            marker in text
            for marker in ("wavy", "ripple", "textured", "relief", "fluted", "reeded")
        ):
            return "glass.textured_rippled"
        if any(
            marker in text
            for marker in (
                "crystal",
                "pattern",
                "decor",
                "stained",
                "colored",
                "colorled",
                "mosaic",
                "diamond grid",
                "medieval",
                "leaded",
                "cut glass",
                "glass block",
                "glass brick",
                "grid",
                "polkadot",
                "tile",
                "brick",
                "block",
                "iridescent",
                "color glass",
                "black and white glass",
                "blue glass",
            )
        ):
            return "glass.stained_decorative"
        if name == "windows" or any(
            marker in name
            for marker in (
                "building facade",
                "window wall",
                "window facade",
                "glass window",
                "glass windows",
                "medieval windows",
                "woden glass window",
            )
        ):
            return "glass.architectural_window_patterned"
        return "glass.clear_transparent"
    if category == "leather":
        if "suede" in text:
            return "leather.suede"
        if "quilt" in text or "button tuft" in text:
            return "leather.quilted_upholstery"
        if any(
            marker in text
            for marker in ("aged", "worn", "weathered", "vintage", "scratched", "old", "creased")
        ):
            return "leather.aged_distressed"
        if any(marker in text for marker in ("pebble", "grain")):
            return "leather.pebbled_grained"
        return "leather.smooth_plain"
    if category == "liquid":
        if any(
            marker in text
            for marker in (
                "abstract color",
                "latte",
                "coffee",
                "grass under water",
                "water droplet",
                "milky foam",
            )
        ):
            return None
        if any(marker in text for marker in ("wave", "water foam", "ocean", "sea")):
            return "liquid.water_wave_foam"
        return None
    if category == "marble":
        # The frozen v1 registry intentionally has one broad marble leaf.
        return "marble.generic"
    if category == "metal":
        metal_text = f"{text} {source_description}"
        if normalized_name in {
            "silver ore",
            "medieval iron door",
            "treasure coins silver",
        }:
            return None
        if any(
            marker in name
            for marker in (
                "jewelry",
                "lapislazuli",
                "leather",
                "glass",
                "abstract pbr",
                "castle wall",
                "lizard skin",
                "wooden block",
                "uk car tag",
            )
        ):
            return None
        if any(
            marker in metal_text
            for marker in (
                "chainmail",
                "chain mail",
                "mesh",
                "grate",
                "grating",
                "grille",
                "lattice",
                "perforated",
                "chain link",
                "chain",
                "gause",
                "net",
                "wire fence",
                "vent",
                "ventilation",
            )
        ):
            return "metal.mesh_chainmail"
        if any(
            marker in metal_text
            for marker in (
                "panel",
                "plate",
                "sheet",
                "diamond",
                "tread",
                "checker",
                "corrugated",
                "ribbed",
                "tile",
                "pattern",
                "ornament",
                "geometric",
                "hexagon",
                "stripe",
                "scallop",
                "armor",
                "armour",
                "braid",
                "camo",
                "carbon fiber",
                "carbon fibre",
                "carving",
                "scale",
                "manhole",
                "garage door",
                "hammered",
                "foil",
                "weave",
                "blinds",
                "triangle",
                "pyramid",
                "wave",
                "sci-fi",
                "scifi",
                "pannel",
                "padded",
                "grid",
                "arabesque",
                "plating",
                "riveted",
                "anti-slip",
                "ribs",
                "roof",
                "punch through",
                "depth surface",
                "pyramic",
                "shutter",
                "glitter",
                "sci fi",
                "spiked",
                "slat",
                "textured metal",
                "faceted",
                "triangular",
                "design",
                "hex wires",
            )
        ):
            return "metal.patterned_sheet_panel"
        if "rust" in text:
            return "metal.steel_rusted"
        if any(marker in text for marker in ("cast iron", "castiron")):
            return "metal.cast_iron_bare"
        if "galvanized" in text or "galvanised" in text:
            return "metal.steel_galvanized"
        if "chrome" in text:
            return "metal.chrome_polished"
        if any(marker in text for marker in ("blackened", "gunmetal", "brushed black")):
            return "metal.blackened_gunmetal"
        if "stainless" in text:
            return "metal.stainless_matte"
        if any(marker in text for marker in ("aluminium", "aluminum", "anodized", "anodised")):
            return "metal.aluminum_bare"
        if "brass" in text:
            return (
                "metal.brass_aged"
                if any(
                    marker in text
                    for marker in ("aged", "antique", "patina", "oxidized", "oxidised", "weathered")
                )
                else "metal.brass_polished"
            )
        if "copper" in text or "cooper wire" in name:
            return (
                "metal.copper_patinated"
                if any(
                    marker in text
                    for marker in (
                        "aged",
                        "antique",
                        "patina",
                        "verdigris",
                        "oxidized",
                        "oxidised",
                        "weathered",
                    )
                )
                else "metal.copper_bare"
            )
        if "bronze" in text:
            return "metal.bronze_cast"
        if "zinc" in text:
            return "metal.steel_galvanized"
        if any(
            marker in text
            for marker in (
                "painted",
                "paint coated",
                "powder coated",
                "enamel",
                "car paint",
                "carpaint",
                "powdercoat",
                "paintwork",
                "chipped paint",
                "peeling paint",
            )
        ):
            return "metal.paint_coated"
        if "gold" in text:
            return "metal.precious_gold"
        if "brushed" in text or "silver brushed" in text:
            return "metal.brushed_silver"
        if any(
            marker in text
            for marker in (
                "scratched",
                "scratch",
                "scrached",
                "scuff",
                "battered",
                "distressed",
                "grunge",
                "dirty metal",
                "worn metal",
                "dirty flooring",
                "worn shutter",
            )
        ) or name_words.intersection({"old", "aged", "shabby", "stained"}):
            return "metal.generic_scratched"
        if "steel" in text:
            return "metal.steel_bare"
        return "metal.generic_plain"
    if category == "organic":
        if any(
            marker in text
            for marker in (
                "atlas",
                "decal",
                "moss chunk",
                "black patterned stripes tile",
                "blistred paint",
                "wall decor",
                "decor wall",
                "pigeon poop",
                "pond water",
                "stylized water",
            )
        ):
            return None
        if any(
            marker in text
            for marker in (
                "forest floor",
                "forest ground",
                "leaf litter",
                "leaf_litter",
                "mud leaves",
                "ground leaves",
                "wood snips",
                "organic debris",
            )
        ):
            return "organic.ground_litter"
        if "wax" in text:
            return "organic.wax"
        if any(marker in text for marker in ("fur", "fleece", "sherpa", "wool")):
            return "organic.fur_fleece"
        if any(marker in text for marker in ("coral", "reef", "seashell")):
            return "organic.coral_reef"
        if any(
            marker in text
            for marker in (
                "alien",
                "flesh",
                "meat",
                "skin",
                "virus",
                "tentacle",
                "egg",
                "brain",
                "fish scale",
                "stylized scales",
            )
        ):
            return "organic.biological_surface"
        if any(marker in text for marker in ("leaf", "leaves", "flower", "lilies", "lillies")):
            return "organic.plant_leaf"
        if "cork" in text:
            return "organic.cork"
        if any(marker in text for marker in ("rattan", "wicker", "riet", "reed", "thatch")):
            return "organic.woven_plant_fiber"
        return None
    if category == "paper":
        if any(marker in text for marker in ("piñata", "pinata")):
            return None
        if any(marker in text for marker in ("wallpaper", "glitter", "floral", "pattern")):
            return "paper.wallpaper_patterned"
        return (
            "paper.cardboard"
            if "cardboard" in text or "paperboard" in text
            else "paper.plain_sheet"
        )
    if category == "plaster":
        if any(
            marker in text for marker in ("stucco", "weathered", "chipped", "damaged", "cracked")
        ):
            return "plaster.stucco"
        return "plaster.smooth"
    if category == "plastic":
        if (
            "plastic bag" in name
            or name == "fingerprints"
            or "caution tape" in name
            or "duct tape" in name
            or name.startswith("skin -")
        ):
            return None
        if normalized_name == "recycled plastic" and "colored insert" in source_description:
            return "plastic.patterned_textured"
        if normalized_name == "dirt pvc" and all(
            marker in source_description for marker in ("scratch", "dust")
        ):
            return "plastic.weathered_worn"
        if "bubble wrap" in text:
            return "plastic.flexible_bubble_wrap"
        if "polystyrene" in name or "styrofoam" in text:
            return "plastic.polystyrene_foam"
        if any(marker in name for marker in ("sponge", "foam")):
            return None
        if any(marker in text for marker in ("bubble wrap", "transparent", "clear")):
            return "plastic.clear_rigid"
        if "frosted" in text or "translucent" in text:
            return "plastic.frosted_translucent"
        if any(
            marker in name
            for marker in (
                "weathered",
                "worn",
                "damaged",
                "scratched",
                "scuffed",
                "cracked",
                "old plastic",
                "old white paint",
            )
        ) or name_words.intersection({"old", "used"}):
            return "plastic.weathered_worn"
        if (
            any(
                marker in text
                for marker in (
                    "pattern",
                    "geometric",
                    "relief",
                    "studded",
                    "mosaic",
                    "groove",
                    "ribbed",
                    "corrugated",
                    "woven",
                    "net",
                    "tile",
                    "dots",
                    "quilt",
                    "carbon fiber",
                    "carbon fibre",
                    "weave",
                    "acoustic panel",
                    "decorative",
                    "wallpaper",
                    "grid",
                    "textured",
                    "grained",
                    "grainy",
                    "dossier",
                    "striped",
                    "perfored",
                    "perforated",
                    "vent",
                    "blinds",
                    "wall paper",
                    "panel",
                    "plank",
                    "spike",
                    "rivet",
                    "diamond",
                    "zipper",
                    "carpet",
                    "ornament",
                    "decoration",
                    "warning sign",
                    "hazard",
                    "sci-fi",
                    "scifi",
                    "camo",
                    "grip",
                    "rough finish",
                    "shutter",
                    "siding",
                    "rubiks",
                    "crystal",
                    "grain ",
                )
            )
            or name == "carbon"
        ):
            return "plastic.patterned_textured"
        if any(marker in name for marker in ("gloss", "polished", "lacquer", "piano black")):
            return "plastic.opaque_glossy_molded"
        return "plastic.opaque_generic"
    if category == "rubber":
        if normalized_name in {"tyre sidewall", "tire sidewall"} and (
            "uv map" in source_description
            or "design" in source_description
            or "insignia" in source_description
        ):
            return None
        if "sponge" in text or "foam" in text:
            return "rubber.sponge_foam"
        if any(
            marker in text for marker in ("worn", "old rubber", "crack", "running track", "faded")
        ):
            return "rubber.worn_cracked"
        if any(marker in name for marker in ("corrugated", "ribbed", "groove", "herring")):
            return "rubber.directional_grooved"
        if any(
            marker in text
            for marker in (
                "basketball",
                "pebbled",
                "textured",
                "grained",
                "pattern",
                "grip",
                "studded",
                "mosaic",
                "hex",
                "woven",
                "perforated",
                "octagon",
                "stud",
                "quilt",
                "bubble",
                "mat non slip",
                "antiskid",
                "shredded",
                "mulch",
            )
        ):
            return "rubber.pebbled"
        return "rubber.smooth_plain"
    if category == "rust":
        explicit_review_names = {
            "ghiaia",
            "math plotter",
            "moldy wall",
            "phantom fnaf",
            "rusty painted surface",
            "terriccio",
            "worn metal sheet with scuffs",
        }
        rust_evidence = (
            "rust",
            "corro",
            "oxid",
            "erosion",
            "errosion",
            "verdigris",
            "patina",
        )
        if name in explicit_review_names or "concrete" in text:
            return None
        if not any(marker in text for marker in rust_evidence):
            return None
        if any(
            marker in text
            for marker in (
                "corrugated",
                "shutter",
                "panel blocks",
                "metal panel",
                "diamond pattern",
                "diamond-pattern",
                "screws",
                "rivets",
                "mechanical elements",
            )
        ):
            return "rust.patterned_sheet"
        if any(
            marker in text
            for marker in (
                "verdigris",
                "patina",
                "turquoise",
                "turqoise",
                "copper",
                "green rusty",
            )
        ):
            return "rust.verdigris_patina"
        if words.intersection({"paint", "painted", "paintwork", "chipped", "chipping"}) or (
            "white layer" in text
        ):
            return "rust.painted_weathered"
        if any(
            marker in text
            for marker in (
                "extreme",
                "heavily",
                "heavy rust",
                "fully rust",
                "very rusty",
                "dense iron oxide",
                "pitted",
                "flaking",
                "peeling layers",
                "cracked",
                "deep corrosion",
                "completely degraded",
                "extensive peeling",
            )
        ):
            return "rust.heavy_corrosion"
        return "rust.oxidized_metal"
    if category == "stone":
        if any(marker in name for marker in ("ground", "cobble", "gravel", "pebble")):
            return "stone.aggregate_ground"
        if any(
            marker in text for marker in ("travertine", "sandstone", "limestone", "sedimentary")
        ):
            return "stone.cut_sedimentary"
        if "wall" in text or "brick" in text:
            return "stone.masonry_wall"
        if any(marker in text for marker in ("floor", "tile", "pavement")):
            return "stone.floor_tile"
        if "slate" in text:
            return "stone.slate"
        if "granite" in text:
            return "stone.polished_granite"
        return "stone.rough_rock"
    if category == "tech":
        if words.intersection({"decal", "decals", "sign", "signs"}):
            return None
        if any(
            marker in text
            for marker in ("solar cell", "solar panel", "photovoltaic", "photovoltaics")
        ):
            return "tech.solar_cell"
        if any(marker in text for marker in ("carbon fiber", "carbon fibre", "heat shield")):
            return None
        if any(marker in name for marker in ("cable", "wire", "pipe")):
            return "tech.cable_pipe_bundle"
        if any(
            marker in name
            for marker in (
                "control panel",
                "electrical panel",
                "button panel",
                "analogue dial",
                "voltmeter",
                "gear shift",
            )
        ):
            return "tech.control_interface"
        if any(marker in text for marker in ("emissive", "emission", "led strip")):
            return "tech.emissive_surface"
        if any(
            marker in text
            for marker in ("circuit", "circuitboard", "circuit board", "pcb", "motherboard")
        ):
            return "tech.circuit_board"
        if any(
            marker in text
            for marker in (
                "scifi",
                "sci-fi",
                "sci fi",
                "spaceship",
                "space ship",
                "space shuttle",
                "space pads",
            )
        ):
            return "tech.scifi_panel"
        return None
    if category == "wood":
        if normalized_name in {
            "wooden studs",
            "wooden game crate one",
            "medieval chest",
            "wall with star shaped ornament",
            "dark wall with star",
            "sci-fi panel",
            "camouflage netting",
        }:
            return None
        if normalized_name in {
            "wood dust gold",
            "wood dust pale",
            "wood dust light",
            "wood dust brown",
            "wood chip",
        }:
            return "wood.natural_generic"
        if normalized_name in {
            "black wood chiseled",
            "chess",
            "variant square wood",
            "square wood",
            "log wall",
            "stylized woven wood",
            "stylized woven wood planks",
            "square basket pattern parquet",
            "slatted wood - arauco mdf madeiral",
        }:
            return "wood.patterned_decorative"
        if normalized_name in {
            "woven bamboo lattice pbr",
            "woven bamboo lattice",
            "bamboo woven",
            "woven bamboo lattice screen",
            "wood design",
        }:
            return "wood.woven_plant_fiber"
        if normalized_name in {"plywood", "old plywood"}:
            return "wood.plywood"
        if any(
            marker in name
            for marker in (
                "rattan",
                "wicker",
                "raffia",
                "weaving reed",
                "weaved cane",
                "woven cane",
                "basket",
                "seagrass",
                "coconut straw",
                "woven wood",
                "woven wooden",
                "woven jute",
            )
        ):
            return "wood.woven_plant_fiber"
        if "cork" in name:
            return "wood.cork_surface"
        if name in {"doormat", "fabric", "textile", "windows"} or any(
            marker in name
            for marker in (
                "tyre",
                "tire",
                "carpet",
                "cashmere",
                "donut",
                "chocolate spread",
                "aluminium film",
                "aluminum film",
                "leather sofa",
                "porcelain mosaic",
                "plaster",
                "rock wall",
                "train rock",
                "asphalt rooftop",
                "wafer biscuit",
                "knit wool",
                "tech lattice",
                "wood and metal",
                "metal braced wood",
                "metal wooden gate",
                "pvc wooden",
                "traditional bricks",
                "wood-like fiber paper",
                "wood plant wall",
                "scan windows",
            )
        ):
            return None
        if any(
            marker in text
            for marker in (
                "mdf",
                "osb",
                "oriented strand board",
                "particleboard",
                "particle board",
                "chipboard",
                "fibreboard",
                "fiberboard",
                "masonite",
                "melamine-faced",
                "chip board",
            )
        ):
            return "wood.engineered_board"
        if any(marker in text for marker in ("bark", "tree trunk", "log atlas", "wood chips")):
            return "wood.bark"
        if "paint" in text and any(
            marker in text for marker in ("scratch", "weathered", "old", "worn", "chipped")
        ):
            return "wood.painted_weathered"
        if "paint" in text:
            return "wood.painted_clean"
        if any(
            marker in text
            for marker in (
                "parquet",
                "herringbone",
                "chevron",
                "pattern",
                "decor",
                "ornament",
                "carving",
                "triangular",
                "triangle",
                "tile",
                "patchwork",
                "star shaped",
                "floral",
                "lattice",
                "hexagonal",
                "design",
                "carved",
                "perforated",
                "trellis",
                "sci-fi panel",
                "ribbed",
            )
        ):
            return "wood.patterned_decorative"
        if any(
            marker in text
            for marker in (
                "plank",
                "flooring",
                "floorboard",
                "wood floor",
                "wooden floor",
                "decking",
                "boards",
                "board wall",
                "shingle",
                "siding",
                "slat",
                "shutter",
                "weatherboard",
                "wooden roof",
            )
        ):
            return "wood.plank_floor"
        if any(
            marker in text
            for marker in (
                "veneer",
                "wood panel",
                "wooden panel",
                "wall panel",
                "furniture",
                "panelling",
                "paneling",
                "cabinet",
                "worktop",
                "wooden door",
                "wooden facade",
                "wooden frame",
                "shoji screen",
                "wood wall",
            )
        ):
            return "wood.veneer_panel"
        if "walnut" in text:
            return "wood.walnut_dark"
        if "mahogany" in text or "teak" in text:
            return "wood.mahogany_teak_dark"
        if any(
            marker in text
            for marker in ("polished", "varnish", "glossy", "lacquer", "stained wood", "vanished")
        ):
            return "wood.polished_varnished"
        if "plywood" in text:
            return "wood.plywood"
        if "bamboo" in text:
            return "wood.bamboo"
        if "pine" in text or "softwood" in text:
            return "wood.softwood_pine"
        if any(
            marker in text
            for marker in (
                "rustic",
                "weathered",
                "reclaimed",
                "distressed",
                "burn",
                "charred",
                "crack",
                "damaged",
                "rough",
                "stressed",
                "roten",
                "rotten",
                "worn",
                "scratch",
                "snow",
                "moss",
            )
        ) or words.intersection({"old", "used"}):
            return "wood.rustic_weathered"
        if "oak" in text:
            return "wood.oak"
        return "wood.natural_generic"
    return None


def suggested_decision_row(
    *,
    registry: MaterialClassRegistry,
    record: Any,
) -> dict[str, Any]:
    material_class_id = suggest_material_class_id(record)
    parent_classes = [
        definition.material_class_id
        for definition in registry.by_parent_category(record.category_slug)
    ]
    if material_class_id is not None and material_class_id not in parent_classes:
        raise ValueError(
            f"offline suggestion {material_class_id!r} is unavailable below "
            f"{record.category_slug!r}"
        )
    evidence = [
        f"display_name:{record.display_name}",
        f"classifier:{LOCAL_CLASSIFIER_VERSION}",
    ]
    if record.tags:
        evidence.append("source_tags:" + ",".join(record.tags[:8]))
    return {
        "schema_version": DECISION_SCHEMA,
        "material_id": record.material_id,
        "status": "assigned" if material_class_id else "review",
        "material_class_id": material_class_id,
        "candidate_material_class_ids": (
            [material_class_id] if material_class_id else parent_classes
        ),
        "method": "rule" if material_class_id else "manual",
        "evidence": evidence,
        "note": (
            None
            if material_class_id
            else "No honest visual class in the frozen registry for this provider-category material."
        ),
    }


def suggested_decision_rows(
    *,
    registry: MaterialClassRegistry,
    catalog: MaterialCatalog,
) -> tuple[dict[str, Any], ...]:
    return tuple(
        suggested_decision_row(registry=registry, record=record)
        for record in sorted(catalog.records, key=lambda row: row.material_id)
    )


def incremental_decision_rows(
    *,
    registry: MaterialClassRegistry,
    catalog: MaterialCatalog,
    inherited_snapshot: InheritedAssignmentSnapshot | None = None,
) -> tuple[tuple[dict[str, Any], ...], dict[str, Any]]:
    """Preserve an older snapshot and classify only newly introduced material IDs."""

    inherited_by_id = (
        {row.material_id: row for row in inherited_snapshot.decisions}
        if inherited_snapshot is not None
        else {}
    )
    rows: list[dict[str, Any]] = []
    inherited_assigned_count = 0
    inherited_review_count = 0
    new_assigned_count = 0
    new_review_count = 0
    new_review_by_category: collections.Counter[str] = collections.Counter()
    review_by_category: collections.Counter[str] = collections.Counter()
    catalog_by_id = {row.material_id: row for row in catalog.records}
    inheritance_marker = (
        f"inherited_assignment_snapshot:{inherited_snapshot.logical_snapshot_sha256}"
        if inherited_snapshot is not None
        else None
    )

    for material_id in sorted(catalog_by_id):
        inherited = inherited_by_id.get(material_id)
        if inherited is not None:
            evidence = list(inherited.evidence)
            has_origin_evidence = any(
                value.startswith(("classifier:", "inherited_assignment_snapshot:"))
                for value in evidence
            )
            if inheritance_marker is not None and not has_origin_evidence:
                evidence.append(inheritance_marker)
            row = {
                "schema_version": DECISION_SCHEMA,
                "material_id": inherited.material_id,
                "status": inherited.status,
                "material_class_id": inherited.material_class_id,
                "candidate_material_class_ids": list(inherited.candidate_material_class_ids),
                "method": inherited.method,
                "evidence": evidence,
                "note": inherited.note,
            }
            if inherited.status == "assigned":
                inherited_assigned_count += 1
            else:
                inherited_review_count += 1
        else:
            row = suggested_decision_row(
                registry=registry,
                record=catalog_by_id[material_id],
            )
            if row["status"] == "assigned":
                new_assigned_count += 1
            else:
                new_review_count += 1
                new_review_by_category[catalog_by_id[material_id].category_slug] += 1
        if row["status"] == "review":
            review_by_category[catalog_by_id[material_id].category_slug] += 1
        rows.append(row)

    inherited_count = len(inherited_by_id)
    summary = {
        "inheritance_enabled": inherited_snapshot is not None,
        "inheritance_snapshot_sha256": (
            inherited_snapshot.logical_snapshot_sha256 if inherited_snapshot else None
        ),
        "inheritance_manifest_sha256": (
            inherited_snapshot.manifest_sha256 if inherited_snapshot else None
        ),
        "inheritance_assignments_sha256": (
            inherited_snapshot.assignments_snapshot_sha256 if inherited_snapshot else None
        ),
        "inheritance_decisions_sha256": (
            inherited_snapshot.decisions_sha256 if inherited_snapshot else None
        ),
        "inherited_material_count": inherited_count,
        "inherited_assigned_count": inherited_assigned_count,
        "inherited_review_count": inherited_review_count,
        "new_material_count": len(rows) - inherited_count,
        "new_assigned_count": new_assigned_count,
        "new_review_count": new_review_count,
        "review_count_by_category": dict(sorted(review_by_category.items())),
        "new_review_count_by_category": dict(sorted(new_review_by_category.items())),
    }
    return tuple(rows), summary


def build_incremental_classification_snapshot(
    *,
    registry: MaterialClassRegistry,
    catalog: MaterialCatalog,
    inherited_snapshot: InheritedAssignmentSnapshot | None = None,
    require_runtime_ready: bool = False,
) -> tuple[BuiltAssignmentSnapshot, dict[str, Any]]:
    raw_rows, incremental_summary = incremental_decision_rows(
        registry=registry,
        catalog=catalog,
        inherited_snapshot=inherited_snapshot,
    )
    catalog_by_id = {row.material_id: row for row in catalog.records}
    decisions = tuple(
        _decision_from_row(
            row,
            index=index,
            registry=registry,
            catalog_by_id=catalog_by_id,
        )
        for index, row in enumerate(raw_rows)
    )
    return (
        build_snapshot(
            registry=registry,
            catalog=catalog,
            decisions=decisions,
            allow_runtime_review=not require_runtime_ready,
        ),
        incremental_summary,
    )


def build_local_classification_snapshot(
    *,
    registry: MaterialClassRegistry,
    catalog: MaterialCatalog,
    inherited_snapshot: InheritedAssignmentSnapshot | None = None,
    require_runtime_ready: bool = False,
) -> BuiltAssignmentSnapshot:
    """Classify one normalized catalog without network or runtime similarity.

    The local policy emits exactly one class or an explicit review decision for
    every catalog row.  The returned snapshot is bound to the exact registry and
    catalog digests by :func:`build_snapshot`.
    """

    snapshot, _summary = build_incremental_classification_snapshot(
        registry=registry,
        catalog=catalog,
        inherited_snapshot=inherited_snapshot,
        require_runtime_ready=require_runtime_ready,
    )
    return snapshot


@dataclass(frozen=True, slots=True)
class BuiltAssignmentSnapshot:
    assignments_document: dict[str, Any]
    decisions_rows: tuple[dict[str, Any], ...]
    review_rows: tuple[dict[str, Any], ...]
    manifest: dict[str, Any]
    logical_snapshot_sha256: str


def build_snapshot(
    *,
    registry: MaterialClassRegistry,
    catalog: MaterialCatalog,
    decisions: Sequence[AssignmentDecision],
    allow_runtime_review: bool,
) -> BuiltAssignmentSnapshot:
    ordered_decisions = tuple(sorted(decisions, key=lambda row: row.material_id))
    decision_ids = [row.material_id for row in ordered_decisions]
    catalog_ids = {row.material_id for row in catalog.records}
    if len(decision_ids) != len(set(decision_ids)):
        raise ValueError("decisions repeat material_id")
    if set(decision_ids) != catalog_ids:
        missing = sorted(catalog_ids - set(decision_ids))
        extra = sorted(set(decision_ids) - catalog_ids)
        raise ValueError(
            f"decisions do not exactly cover catalog; missing={missing[:5]}, extra={extra[:5]}"
        )
    assigned = [row for row in ordered_decisions if row.status == "assigned"]
    audit_rows = tuple(row.audit_row(catalog) for row in ordered_decisions)
    review_rows = tuple(row for row in audit_rows if row["status"] == "review")
    assignments_document = build_assignment_document(
        registry=registry,
        catalog=catalog,
        assignments=((row.material_id, str(row.material_class_id)) for row in assigned),
    )
    assignments = MaterialClassAssignments.from_dict(
        assignments_document,
        registry=registry,
        catalog=catalog,
        require_runtime_enabled_catalog=not allow_runtime_review,
    )
    runtime_enabled_ids = {
        record.material_id for record in catalog.records if record.runtime_enabled
    }
    assigned_ids = {row.material_id for row in assigned}
    runtime_review_ids = sorted(runtime_enabled_ids - assigned_ids)
    if runtime_review_ids and not allow_runtime_review:
        raise ValueError(f"runtime-enabled materials remain in review: {runtime_review_ids[:5]}")
    decisions_sha = _sha256_bytes(_canonical_jsonl_bytes(audit_rows))
    review_sha = _sha256_bytes(_canonical_jsonl_bytes(review_rows))
    runtime_ready = not runtime_review_ids
    logical_identity = {
        "schema_version": SNAPSHOT_MANIFEST_SCHEMA,
        "builder_version": BUILDER_VERSION,
        "policy_version": MATERIAL_CLASS_POLICY_VERSION,
        "registry_snapshot_sha256": registry.snapshot_sha256,
        "catalog_snapshot_sha256": catalog.snapshot_sha256,
        "assignments_snapshot_sha256": assignments.snapshot_sha256,
        "decisions_sha256": decisions_sha,
        "review_sha256": review_sha,
        "runtime_ready": runtime_ready,
    }
    logical_sha = _sha256_bytes(_canonical_json_bytes(logical_identity))
    manifest = {
        **logical_identity,
        "logical_snapshot_sha256": logical_sha,
        "files": {
            "assignments.json": {
                "sha256": _sha256_bytes(_canonical_json_bytes(assignments_document, pretty=True)),
                "row_count": len(assigned),
            },
            "decisions.jsonl": {
                "sha256": decisions_sha,
                "row_count": len(audit_rows),
            },
            "review.jsonl": {
                "sha256": review_sha,
                "row_count": len(review_rows),
            },
        },
        "summary": {
            "catalog_material_count": len(catalog.records),
            "runtime_enabled_material_count": len(runtime_enabled_ids),
            "assigned_material_count": len(assigned),
            "review_material_count": len(review_rows),
            "runtime_assigned_material_count": len(runtime_enabled_ids & assigned_ids),
            "runtime_review_material_count": len(runtime_review_ids),
            "assigned_class_count": len({str(row.material_class_id) for row in assigned}),
            "runtime_ready": runtime_ready,
        },
    }
    return BuiltAssignmentSnapshot(
        assignments_document=assignments_document,
        decisions_rows=audit_rows,
        review_rows=review_rows,
        manifest=manifest,
        logical_snapshot_sha256=logical_sha,
    )


def publish_snapshot(
    snapshot: BuiltAssignmentSnapshot,
    *,
    output_root: Path,
) -> tuple[Path, Path]:
    root = output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".assignment-staging-", dir=root))
    try:
        expected = {
            "assignments.json": _canonical_json_bytes(snapshot.assignments_document, pretty=True),
            "decisions.jsonl": _canonical_jsonl_bytes(snapshot.decisions_rows),
            "review.jsonl": _canonical_jsonl_bytes(snapshot.review_rows),
            "manifest.json": _canonical_json_bytes(snapshot.manifest, pretty=True),
        }
        for name, payload in expected.items():
            (staging / name).write_bytes(payload)
        destination = root / "snapshots" / snapshot.logical_snapshot_sha256
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            for name, payload in expected.items():
                published = destination / name
                if not published.is_file() or published.read_bytes() != payload:
                    raise FileExistsError(f"immutable assignment snapshot collision: {published}")
        else:
            os.replace(staging, destination)
        pointer_name = (
            "latest.json" if snapshot.manifest["summary"]["runtime_ready"] else "latest-review.json"
        )
        pointer = root / pointer_name
        _atomic_write(
            pointer,
            _canonical_json_bytes(
                {
                    "schema_version": SNAPSHOT_POINTER_SCHEMA,
                    "logical_snapshot_sha256": snapshot.logical_snapshot_sha256,
                    "snapshot_path": destination.relative_to(root).as_posix(),
                    "assignments_path": (destination / "assignments.json")
                    .relative_to(root)
                    .as_posix(),
                    "manifest_path": (destination / "manifest.json").relative_to(root).as_posix(),
                    "runtime_ready": snapshot.manifest["summary"]["runtime_ready"],
                },
                pretty=True,
            ),
        )
        return destination, pointer
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def validate_published_snapshot(
    snapshot_dir: Path,
    *,
    registry: MaterialClassRegistry,
    catalog: MaterialCatalog,
    require_runtime_ready: bool = False,
) -> dict[str, Any]:
    root = snapshot_dir.resolve(strict=True)
    manifest_path = root / "manifest.json"
    assignments_path = root / "assignments.json"
    decisions_path = root / "decisions.jsonl"
    review_path = root / "review.jsonl"
    for path in (manifest_path, assignments_path, decisions_path, review_path):
        if not path.is_file():
            raise ValueError(f"assignment snapshot is missing {path.name}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("assignment snapshot manifest must be an object")
    if manifest.get("schema_version") != SNAPSHOT_MANIFEST_SCHEMA:
        raise ValueError("assignment snapshot manifest schema mismatch")
    if manifest.get("builder_version") != BUILDER_VERSION:
        raise ValueError("assignment snapshot builder version mismatch")
    if manifest.get("policy_version") != MATERIAL_CLASS_POLICY_VERSION:
        raise ValueError("assignment snapshot policy version mismatch")
    if manifest.get("registry_snapshot_sha256") != registry.snapshot_sha256:
        raise ValueError("assignment snapshot registry mismatch")
    if manifest.get("catalog_snapshot_sha256") != catalog.snapshot_sha256:
        raise ValueError("assignment snapshot catalog mismatch")
    logical_sha = _text(
        manifest.get("logical_snapshot_sha256"),
        field="logical_snapshot_sha256",
    )
    if root.name != logical_sha:
        raise ValueError("assignment snapshot directory is not content-addressed")

    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ValueError("assignment snapshot manifest has no files table")
    payloads = {
        "assignments.json": assignments_path.read_bytes(),
        "decisions.jsonl": decisions_path.read_bytes(),
        "review.jsonl": review_path.read_bytes(),
    }
    for name, payload in payloads.items():
        metadata = files.get(name)
        if not isinstance(metadata, dict) or metadata.get("sha256") != _sha256_bytes(payload):
            raise ValueError(f"assignment snapshot {name} SHA mismatch")

    catalog_by_id = {row.material_id: row for row in catalog.records}
    audit_rows: list[dict[str, Any]] = []
    decisions: list[AssignmentDecision] = []
    input_fields = {
        "schema_version",
        "material_id",
        "status",
        "material_class_id",
        "candidate_material_class_ids",
        "method",
        "evidence",
        "note",
    }
    for index, line in enumerate(decisions_path.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"published decision[{index}] must be an object")
        material_id = _text(
            row.get("material_id"), field=f"published decision[{index}].material_id"
        )
        record = catalog_by_id.get(material_id)
        if record is None:
            raise ValueError(f"published decision references unknown material: {material_id}")
        for field, expected in {
            "category_slug": record.category_slug,
            "display_name": record.display_name,
            "runtime_enabled": record.runtime_enabled,
        }.items():
            if row.get(field) != expected:
                raise ValueError(f"published decision {material_id} has stale {field}")
        audit_rows.append(row)
        decisions.append(
            _decision_from_row(
                {key: row[key] for key in input_fields},
                index=index,
                registry=registry,
                catalog_by_id=catalog_by_id,
            )
        )
    if len(audit_rows) != len(catalog.records):
        raise ValueError("published decisions do not cover the catalog exactly")

    runtime_ready = bool((manifest.get("summary") or {}).get("runtime_ready"))
    if require_runtime_ready and not runtime_ready:
        raise ValueError("assignment snapshot is not runtime-ready")
    rebuilt = build_snapshot(
        registry=registry,
        catalog=catalog,
        decisions=decisions,
        allow_runtime_review=not runtime_ready,
    )
    if rebuilt.logical_snapshot_sha256 != logical_sha or rebuilt.manifest != manifest:
        raise ValueError("assignment snapshot logical identity mismatch")
    if rebuilt.assignments_document != json.loads(assignments_path.read_text(encoding="utf-8")):
        raise ValueError("assignment snapshot assignments document mismatch")
    if _canonical_jsonl_bytes(rebuilt.decisions_rows) != payloads["decisions.jsonl"]:
        raise ValueError("assignment snapshot decision ordering/canonicalization mismatch")
    if _canonical_jsonl_bytes(rebuilt.review_rows) != payloads["review.jsonl"]:
        raise ValueError("assignment snapshot review queue mismatch")
    MaterialClassAssignments.from_json(
        assignments_path,
        registry=registry,
        catalog=catalog,
        require_runtime_enabled_catalog=runtime_ready,
    )
    return dict(manifest["summary"])


def _add_common_inputs(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--library-root", type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    init = subparsers.add_parser("init", help="write a complete review worklist")
    _add_common_inputs(init)
    init.add_argument("--output", type=Path, required=True)
    init.add_argument("--execute", action="store_true")

    suggest = subparsers.add_parser(
        "suggest", help="write a reproducible offline exact-class decision worklist"
    )
    _add_common_inputs(suggest)
    suggest.add_argument("--output", type=Path, required=True)
    suggest.add_argument(
        "--inherit-snapshot",
        type=Path,
        help="Preserve all decisions from an older assignment snapshot and classify only new IDs",
    )
    suggest.add_argument("--execute", action="store_true")

    classify = subparsers.add_parser(
        "classify",
        help="classify a normalized catalog and build an exact assignment snapshot",
    )
    _add_common_inputs(classify)
    classify.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    classify.add_argument(
        "--inherit-snapshot",
        type=Path,
        help="Preserve all decisions from an older assignment snapshot and classify only new IDs",
    )
    classify.add_argument("--require-runtime-ready", action="store_true")
    classify.add_argument("--execute", action="store_true")

    build = subparsers.add_parser(
        "build", help="validate decisions and build an immutable sidecar snapshot"
    )
    _add_common_inputs(build)
    build.add_argument("--decisions", type=Path, required=True)
    build.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    build.add_argument("--allow-runtime-review", action="store_true")
    build.add_argument("--execute", action="store_true")

    validate = subparsers.add_parser(
        "validate", help="re-open and fully validate a published sidecar snapshot"
    )
    _add_common_inputs(validate)
    validate.add_argument("--snapshot", type=Path, required=True)
    validate.add_argument("--require-runtime-ready", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    registry = MaterialClassRegistry.from_json(args.registry)
    catalog = load_catalog(args.catalog, library_root=args.library_root)
    inherited_snapshot = None
    if getattr(args, "inherit_snapshot", None) is not None:
        inherited_snapshot = load_inherited_assignment_snapshot(
            args.inherit_snapshot,
            registry=registry,
            catalog=catalog,
        )
    classification_inputs = {
        "registry_input_sha256": _sha256_path(args.registry.resolve(strict=True)),
        "catalog_file_sha256": (catalog.catalog_file_sha256 or _sha256_path(catalog.source_path)),
        "raw_catalog_sha256": catalog.raw_catalog_sha256,
    }
    if args.command == "validate":
        summary = validate_published_snapshot(
            args.snapshot,
            registry=registry,
            catalog=catalog,
            require_runtime_ready=bool(args.require_runtime_ready),
        )
        print(
            json.dumps(
                {
                    "schema_version": SNAPSHOT_MANIFEST_SCHEMA,
                    "validated": True,
                    "snapshot_path": args.snapshot.resolve().as_posix(),
                    **summary,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    if args.command == "init":
        rows = initial_review_rows(registry=registry, catalog=catalog)
        payload = _canonical_jsonl_bytes(rows)
        if args.execute:
            _atomic_write(args.output.resolve(), payload)
        print(
            json.dumps(
                {
                    "schema_version": DECISION_SCHEMA,
                    "executed": bool(args.execute),
                    "output": args.output.resolve().as_posix(),
                    "decision_count": len(rows),
                    "runtime_enabled_count": sum(row.runtime_enabled for row in catalog.records),
                    "sha256": _sha256_bytes(payload),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    if args.command == "suggest":
        rows, incremental_summary = incremental_decision_rows(
            registry=registry,
            catalog=catalog,
            inherited_snapshot=inherited_snapshot,
        )
        payload = _canonical_jsonl_bytes(rows)
        assigned_count = sum(row["status"] == "assigned" for row in rows)
        review_ids = {row["material_id"] for row in rows if row["status"] == "review"}
        runtime_review_count = sum(
            row.runtime_enabled and row.material_id in review_ids for row in catalog.records
        )
        if args.execute:
            _atomic_write(args.output.resolve(), payload)
        print(
            json.dumps(
                {
                    "schema_version": DECISION_SCHEMA,
                    "executed": bool(args.execute),
                    "output": args.output.resolve().as_posix(),
                    "decision_count": len(rows),
                    "assigned_count": assigned_count,
                    "review_count": len(rows) - assigned_count,
                    "runtime_review_count": runtime_review_count,
                    "sha256": _sha256_bytes(payload),
                    **classification_inputs,
                    **incremental_summary,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0
    if args.command == "classify":
        snapshot, incremental_summary = build_incremental_classification_snapshot(
            registry=registry,
            catalog=catalog,
            inherited_snapshot=inherited_snapshot,
            require_runtime_ready=bool(args.require_runtime_ready),
        )
        destination = None
        pointer = None
        if args.execute:
            destination, pointer = publish_snapshot(
                snapshot,
                output_root=args.output_root,
            )
            validate_published_snapshot(
                destination,
                registry=registry,
                catalog=catalog,
                require_runtime_ready=bool(args.require_runtime_ready),
            )
        print(
            json.dumps(
                {
                    "schema_version": SNAPSHOT_MANIFEST_SCHEMA,
                    "classifier_version": LOCAL_CLASSIFIER_VERSION,
                    "executed": bool(args.execute),
                    "logical_snapshot_sha256": snapshot.logical_snapshot_sha256,
                    "registry_snapshot_sha256": registry.snapshot_sha256,
                    "catalog_snapshot_sha256": catalog.snapshot_sha256,
                    "snapshot_path": destination.as_posix() if destination else None,
                    "pointer_path": pointer.as_posix() if pointer else None,
                    **classification_inputs,
                    **incremental_summary,
                    **snapshot.manifest["summary"],
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 0

    decisions = load_decisions(
        args.decisions,
        registry=registry,
        catalog=catalog,
    )
    snapshot = build_snapshot(
        registry=registry,
        catalog=catalog,
        decisions=decisions,
        allow_runtime_review=bool(args.allow_runtime_review),
    )
    destination = None
    pointer = None
    if args.execute:
        destination, pointer = publish_snapshot(
            snapshot,
            output_root=args.output_root,
        )
        validate_published_snapshot(
            destination,
            registry=registry,
            catalog=catalog,
            require_runtime_ready=False,
        )
    print(
        json.dumps(
            {
                "schema_version": SNAPSHOT_MANIFEST_SCHEMA,
                "executed": bool(args.execute),
                "logical_snapshot_sha256": snapshot.logical_snapshot_sha256,
                "snapshot_path": destination.as_posix() if destination else None,
                "pointer_path": pointer.as_posix() if pointer else None,
                **snapshot.manifest["summary"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
