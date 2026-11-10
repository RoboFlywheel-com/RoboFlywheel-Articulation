# SPDX-License-Identifier: Apache-2.0

"""Controlled material classes and content-addressed catalog assignments.

Material classes are an offline-authored taxonomy below one official
BlenderKit top-level category.  Runtime code never interprets the description
or discovery queries: it uses only an exact ``material_class_id`` assignment.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from sdk._core.v0.types import BLENDERKIT_MATERIAL_CATEGORIES

from .catalog import MaterialCatalog, MaterialRecord

MATERIAL_CLASS_REGISTRY_SCHEMA = "articraft-material-class-registry/v1"
MATERIAL_CLASS_ASSIGNMENTS_SCHEMA = "articraft-material-class-assignments/v1"
MATERIAL_CLASS_POLICY_VERSION = "exact-material-class-pool/v1"

_CLASS_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _material_class_id(value: object, *, field: str) -> str:
    result = _text(value, field=field)
    if _CLASS_ID_RE.fullmatch(result) is None:
        raise ValueError(
            f"{field} must be a lowercase dotted identifier such as 'metal.brushed_steel'"
        )
    return result


def _string_tuple(value: object, *, field: str) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, list):
        raise ValueError(f"{field} must be a non-empty list of strings")
    result = tuple(_text(item, field=f"{field}[{index}]") for index, item in enumerate(value))
    if not result:
        raise ValueError(f"{field} must be a non-empty list of strings")
    if len(result) != len(set(result)):
        raise ValueError(f"{field} must not contain duplicates")
    return result


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


@dataclass(frozen=True, slots=True)
class MaterialClassDefinition:
    """One controlled semantic class inside an official provider category."""

    material_class_id: str
    parent_category: str
    display_name: str
    description: str
    discovery_queries: tuple[str, ...]
    initial_quota: int

    @classmethod
    def from_dict(cls, value: Mapping[str, Any], *, field: str) -> MaterialClassDefinition:
        allowed = {
            "material_class_id",
            "parent_category",
            "display_name",
            "description",
            "discovery_queries",
            "initial_quota",
        }
        unknown = sorted(set(value) - allowed)
        if unknown:
            raise ValueError(f"{field} has unsupported fields: {unknown}")
        class_id = _material_class_id(
            value.get("material_class_id"), field=f"{field}.material_class_id"
        )
        category = _text(value.get("parent_category"), field=f"{field}.parent_category")
        if category not in BLENDERKIT_MATERIAL_CATEGORIES:
            raise ValueError(
                f"{field}.parent_category must be an official BlenderKit top-level slug"
            )
        if class_id.split(".", 1)[0] != category:
            raise ValueError(
                f"{field}.material_class_id must start with parent category {category!r}"
            )
        quota = value.get("initial_quota")
        if isinstance(quota, bool) or not isinstance(quota, int) or quota < 1:
            raise ValueError(f"{field}.initial_quota must be a positive integer")
        return cls(
            material_class_id=class_id,
            parent_category=category,
            display_name=_text(value.get("display_name"), field=f"{field}.display_name"),
            description=_text(value.get("description"), field=f"{field}.description"),
            discovery_queries=_string_tuple(
                value.get("discovery_queries"), field=f"{field}.discovery_queries"
            ),
            initial_quota=quota,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "material_class_id": self.material_class_id,
            "parent_category": self.parent_category,
            "display_name": self.display_name,
            "description": self.description,
            "discovery_queries": list(self.discovery_queries),
            "initial_quota": self.initial_quota,
        }


@dataclass(frozen=True, slots=True)
class MaterialClassRegistry:
    """Immutable registry used by offline planning and exact runtime lookup."""

    classes: tuple[MaterialClassDefinition, ...]
    snapshot_sha256: str
    source_path: Path | None = None

    @classmethod
    def from_dict(
        cls,
        value: Mapping[str, Any],
        *,
        source_path: Path | None = None,
    ) -> MaterialClassRegistry:
        allowed = {"schema_version", "policy_version", "classes"}
        unknown = sorted(set(value) - allowed)
        if unknown:
            raise ValueError(f"material class registry has unsupported fields: {unknown}")
        if value.get("schema_version") != MATERIAL_CLASS_REGISTRY_SCHEMA:
            raise ValueError(
                f"unsupported material class registry schema: {value.get('schema_version')!r}"
            )
        policy = value.get("policy_version", MATERIAL_CLASS_POLICY_VERSION)
        if policy != MATERIAL_CLASS_POLICY_VERSION:
            raise ValueError(f"unsupported material class policy: {policy!r}")
        rows = value.get("classes")
        if not isinstance(rows, list) or not rows:
            raise ValueError("material class registry classes must be a non-empty list")
        classes = []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise ValueError(f"classes[{index}] must be an object")
            classes.append(MaterialClassDefinition.from_dict(row, field=f"classes[{index}]"))
        ids = [row.material_class_id for row in classes]
        if len(ids) != len(set(ids)):
            raise ValueError("material class registry repeats material_class_id")
        ordered = tuple(sorted(classes, key=lambda row: row.material_class_id))
        canonical = {
            "schema_version": MATERIAL_CLASS_REGISTRY_SCHEMA,
            "policy_version": MATERIAL_CLASS_POLICY_VERSION,
            "classes": [row.as_dict() for row in ordered],
        }
        return cls(
            classes=ordered,
            snapshot_sha256=_sha256_bytes(_canonical_bytes(canonical)),
            source_path=source_path,
        )

    @classmethod
    def from_json(cls, path: Path) -> MaterialClassRegistry:
        source = path.resolve(strict=True)
        return cls.from_dict(_read_json_object(source), source_path=source)

    def get(self, material_class_id: str) -> MaterialClassDefinition:
        normalized = _material_class_id(material_class_id, field="material_class_id")
        for row in self.classes:
            if row.material_class_id == normalized:
                return row
        raise KeyError(f"unknown material_class_id: {normalized}")

    def by_parent_category(self, category_slug: str) -> tuple[MaterialClassDefinition, ...]:
        return tuple(row for row in self.classes if row.parent_category == category_slug)

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": MATERIAL_CLASS_REGISTRY_SCHEMA,
            "policy_version": MATERIAL_CLASS_POLICY_VERSION,
            "classes": [row.as_dict() for row in self.classes],
        }


@dataclass(frozen=True, slots=True)
class MaterialClassAssignments:
    """A content-addressed material-id to class-id assignment sidecar."""

    assignments: tuple[tuple[str, str], ...]
    registry_snapshot_sha256: str
    catalog_snapshot_sha256: str
    snapshot_sha256: str
    source_path: Path | None = None

    @classmethod
    def from_dict(
        cls,
        value: Mapping[str, Any],
        *,
        registry: MaterialClassRegistry,
        catalog: MaterialCatalog,
        source_path: Path | None = None,
        require_complete_catalog: bool = False,
        require_runtime_enabled_catalog: bool = False,
    ) -> MaterialClassAssignments:
        allowed = {
            "schema_version",
            "policy_version",
            "registry_snapshot_sha256",
            "catalog_snapshot_sha256",
            "assignments",
        }
        unknown = sorted(set(value) - allowed)
        if unknown:
            raise ValueError(f"material class assignments have unsupported fields: {unknown}")
        if value.get("schema_version") != MATERIAL_CLASS_ASSIGNMENTS_SCHEMA:
            raise ValueError(
                f"unsupported material class assignments schema: {value.get('schema_version')!r}"
            )
        if value.get("policy_version") != MATERIAL_CLASS_POLICY_VERSION:
            raise ValueError(
                f"unsupported material class assignment policy: {value.get('policy_version')!r}"
            )
        registry_sha = _text(
            value.get("registry_snapshot_sha256"), field="registry_snapshot_sha256"
        )
        catalog_sha = _text(value.get("catalog_snapshot_sha256"), field="catalog_snapshot_sha256")
        if _SHA256_RE.fullmatch(registry_sha) is None or registry_sha != (registry.snapshot_sha256):
            raise ValueError("material class assignments registry snapshot mismatch")
        if _SHA256_RE.fullmatch(catalog_sha) is None or catalog_sha != catalog.snapshot_sha256:
            raise ValueError("material class assignments catalog snapshot mismatch")
        raw_rows = value.get("assignments")
        if not isinstance(raw_rows, list):
            raise ValueError("material class assignments must be a list")
        catalog_by_id = {row.material_id: row for row in catalog.records}
        pairs: list[tuple[str, str]] = []
        for index, raw in enumerate(raw_rows):
            if not isinstance(raw, dict) or set(raw) != {"material_id", "material_class_id"}:
                raise ValueError(
                    f"assignments[{index}] must contain only material_id and material_class_id"
                )
            material_id = _text(raw.get("material_id"), field=f"assignments[{index}].material_id")
            class_id = _material_class_id(
                raw.get("material_class_id"),
                field=f"assignments[{index}].material_class_id",
            )
            try:
                definition = registry.get(class_id)
            except KeyError as exc:
                raise ValueError(str(exc)) from exc
            material = catalog_by_id.get(material_id)
            if material is None:
                raise ValueError(f"assignment references unknown material_id: {material_id}")
            if material.category_slug != definition.parent_category:
                raise ValueError(
                    f"assignment {material_id!r} category {material.category_slug!r} does not "
                    f"match class parent {definition.parent_category!r}"
                )
            pairs.append((material_id, class_id))
        material_ids = [material_id for material_id, _ in pairs]
        if len(material_ids) != len(set(material_ids)):
            raise ValueError("material class assignments repeat material_id")
        if require_complete_catalog and set(material_ids) != set(catalog_by_id):
            missing = sorted(set(catalog_by_id) - set(material_ids))
            raise ValueError(f"material class assignments do not cover catalog: {missing[:5]}")
        if require_runtime_enabled_catalog:
            required_runtime_ids = {
                row.material_id for row in catalog.records if row.runtime_enabled
            }
            missing_runtime = sorted(required_runtime_ids - set(material_ids))
            if missing_runtime:
                raise ValueError(
                    "material class assignments do not cover runtime-enabled catalog: "
                    f"{missing_runtime[:5]}"
                )
        ordered = tuple(sorted(pairs))
        canonical = {
            "schema_version": MATERIAL_CLASS_ASSIGNMENTS_SCHEMA,
            "policy_version": MATERIAL_CLASS_POLICY_VERSION,
            "registry_snapshot_sha256": registry_sha,
            "catalog_snapshot_sha256": catalog_sha,
            "assignments": [
                {"material_id": material_id, "material_class_id": class_id}
                for material_id, class_id in ordered
            ],
        }
        return cls(
            assignments=ordered,
            registry_snapshot_sha256=registry_sha,
            catalog_snapshot_sha256=catalog_sha,
            snapshot_sha256=_sha256_bytes(_canonical_bytes(canonical)),
            source_path=source_path,
        )

    @classmethod
    def from_json(
        cls,
        path: Path,
        *,
        registry: MaterialClassRegistry,
        catalog: MaterialCatalog,
        require_complete_catalog: bool = False,
        require_runtime_enabled_catalog: bool = False,
    ) -> MaterialClassAssignments:
        source = path.resolve(strict=True)
        return cls.from_dict(
            _read_json_object(source),
            registry=registry,
            catalog=catalog,
            source_path=source,
            require_complete_catalog=require_complete_catalog,
            require_runtime_enabled_catalog=require_runtime_enabled_catalog,
        )

    def material_ids_for_class(self, material_class_id: str) -> tuple[str, ...]:
        normalized = _material_class_id(material_class_id, field="material_class_id")
        return tuple(
            material_id for material_id, class_id in self.assignments if class_id == normalized
        )

    def records_for_class(
        self,
        catalog: MaterialCatalog,
        material_class_id: str,
        *,
        runtime_enabled_only: bool = True,
    ) -> tuple[MaterialRecord, ...]:
        ids = set(self.material_ids_for_class(material_class_id))
        return tuple(
            row
            for row in catalog.records
            if row.material_id in ids and (row.runtime_enabled or not runtime_enabled_only)
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": MATERIAL_CLASS_ASSIGNMENTS_SCHEMA,
            "policy_version": MATERIAL_CLASS_POLICY_VERSION,
            "registry_snapshot_sha256": self.registry_snapshot_sha256,
            "catalog_snapshot_sha256": self.catalog_snapshot_sha256,
            "assignments": [
                {"material_id": material_id, "material_class_id": class_id}
                for material_id, class_id in self.assignments
            ],
        }


def build_assignment_document(
    *,
    registry: MaterialClassRegistry,
    catalog: MaterialCatalog,
    assignments: Iterable[tuple[str, str]],
) -> dict[str, Any]:
    """Build and validate a canonical assignment document for offline QA tools."""

    document = {
        "schema_version": MATERIAL_CLASS_ASSIGNMENTS_SCHEMA,
        "policy_version": MATERIAL_CLASS_POLICY_VERSION,
        "registry_snapshot_sha256": registry.snapshot_sha256,
        "catalog_snapshot_sha256": catalog.snapshot_sha256,
        "assignments": [
            {"material_id": material_id, "material_class_id": class_id}
            for material_id, class_id in assignments
        ],
    }
    return MaterialClassAssignments.from_dict(
        document,
        registry=registry,
        catalog=catalog,
    ).as_dict()
