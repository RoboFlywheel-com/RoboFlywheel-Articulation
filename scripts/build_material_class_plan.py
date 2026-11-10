#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Build class-level fleet statistics and BlenderKit discovery profiles.

This is an offline planning tool.  It never evaluates facets, similarities,
surface importance, or fallback categories.  Every material callsite names one
controlled ``material_class_id`` and every class carries one fixed initial
quota from the registry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping

from articraft.appearance import (
    MATERIAL_CLASS_POLICY_VERSION,
    MaterialCatalog,
    MaterialClassAssignments,
    MaterialClassRegistry,
)

MATERIAL_CLASS_BINDING_SCHEMA = "articraft-material-class-binding/v1"
MATERIAL_CLASS_PLAN_SCHEMA = "articraft-material-class-plan/v1"
DOWNLOADER_PROFILE_SCHEMA = 2
_MATERIAL_ASSET_TYPES = frozenset({"pbr_material", "optical_material"})


def _downloader_profile(
    *,
    class_id: str,
    parent_category: str,
    queries: Iterable[str],
    quota: int,
) -> dict[str, Any]:
    """Build offline discovery policy without changing the runtime class key."""

    profile: dict[str, Any] = {
        "id": class_id,
        "material_class_id": class_id,
        "category_slug": parent_category,
        "queries": list(queries),
        "quota": quota,
    }
    if parent_category in {"glass", "liquid"}:
        profile["shader_profile"] = "optical_principled"
    return profile


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON at {path}:{line_number}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain an object")
        rows.append(value)
    return rows


def _binding_demand(
    rows: Iterable[Mapping[str, Any]],
    *,
    registry: MaterialClassRegistry,
) -> tuple[Counter[str], dict[str, set[str]], int]:
    counts: Counter[str] = Counter()
    templates: dict[str, set[str]] = defaultdict(set)
    identities: set[tuple[str, str]] = set()
    ignored_non_material = 0
    for index, row in enumerate(rows):
        field = f"bindings[{index}]"
        allowed = {
            "schema_version",
            "template",
            "callsite_id",
            "asset_type",
            "material_class_id",
        }
        unknown = sorted(set(row) - allowed)
        if unknown:
            raise ValueError(f"{field} has unsupported fields: {unknown}")
        if row.get("schema_version") != MATERIAL_CLASS_BINDING_SCHEMA:
            raise ValueError(f"{field} has unsupported schema_version")
        template = str(row.get("template") or "").strip()
        callsite_id = str(row.get("callsite_id") or "").strip()
        asset_type = str(row.get("asset_type") or "").strip()
        if not template or not callsite_id or not asset_type:
            raise ValueError(f"{field} lacks template/callsite_id/asset_type")
        identity = (template, callsite_id)
        if identity in identities:
            raise ValueError(f"duplicate material class binding: {template}/{callsite_id}")
        identities.add(identity)
        class_value = row.get("material_class_id")
        if asset_type not in _MATERIAL_ASSET_TYPES:
            if class_value not in (None, ""):
                raise ValueError(f"{field} non-material asset cannot have material_class_id")
            ignored_non_material += 1
            continue
        class_id = str(class_value or "").strip()
        if not class_id:
            raise ValueError(f"{field} material asset requires material_class_id")
        try:
            registry.get(class_id)
        except KeyError as exc:
            raise ValueError(str(exc)) from exc
        counts[class_id] += 1
        templates[class_id].add(template)
    return counts, templates, ignored_non_material


def build_material_class_documents(
    registry: MaterialClassRegistry,
    *,
    catalog: MaterialCatalog | None = None,
    assignments: MaterialClassAssignments | None = None,
    binding_rows: Iterable[Mapping[str, Any]] = (),
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return deterministic statistics and downloader schema-v2 profiles."""

    if (catalog is None) != (assignments is None):
        raise ValueError("catalog and assignments must be supplied together")
    if assignments is not None and catalog is not None:
        if assignments.registry_snapshot_sha256 != registry.snapshot_sha256:
            raise ValueError("assignment registry snapshot mismatch")
        if assignments.catalog_snapshot_sha256 != catalog.snapshot_sha256:
            raise ValueError("assignment catalog snapshot mismatch")

    demand_counts, templates_by_class, ignored_non_material = _binding_demand(
        binding_rows,
        registry=registry,
    )
    catalog_by_id = (
        {record.material_id: record for record in catalog.records} if catalog is not None else {}
    )
    assignment_pairs = assignments.assignments if assignments is not None else ()
    assigned_by_class: dict[str, list[str]] = defaultdict(list)
    for material_id, class_id in assignment_pairs:
        assigned_by_class[class_id].append(material_id)

    class_rows: list[dict[str, Any]] = []
    profiles: list[dict[str, Any]] = []
    for definition in registry.classes:
        class_id = definition.material_class_id
        assigned_ids = sorted(assigned_by_class.get(class_id, ()))
        runtime_ids = [
            material_id
            for material_id in assigned_ids
            if catalog_by_id[material_id].runtime_enabled
        ]
        shortfall = max(0, definition.initial_quota - len(runtime_ids))
        class_rows.append(
            {
                "material_class_id": class_id,
                "parent_category": definition.parent_category,
                "demand_callsite_count": demand_counts[class_id],
                "demand_template_count": len(templates_by_class[class_id]),
                "initial_quota": definition.initial_quota,
                "assigned_material_count": len(assigned_ids),
                "runtime_enabled_material_count": len(runtime_ids),
                "download_shortfall": shortfall,
            }
        )
        if shortfall:
            profiles.append(
                _downloader_profile(
                    class_id=class_id,
                    parent_category=definition.parent_category,
                    queries=definition.discovery_queries,
                    quota=shortfall,
                )
            )

    plan = {
        "schema_version": MATERIAL_CLASS_PLAN_SCHEMA,
        "policy_version": MATERIAL_CLASS_POLICY_VERSION,
        "registry_snapshot_sha256": registry.snapshot_sha256,
        "catalog_snapshot_sha256": catalog.snapshot_sha256 if catalog is not None else None,
        "assignments_snapshot_sha256": (
            assignments.snapshot_sha256 if assignments is not None else None
        ),
        "summary": {
            "material_class_count": len(registry.classes),
            "demanded_material_class_count": sum(bool(value) for value in demand_counts.values()),
            "material_callsite_count": sum(demand_counts.values()),
            "ignored_non_material_callsite_count": ignored_non_material,
            "initial_quota_total": sum(row.initial_quota for row in registry.classes),
            "runtime_enabled_assigned_total": sum(
                row["runtime_enabled_material_count"] for row in class_rows
            ),
            "download_shortfall_total": sum(row["download_shortfall"] for row in class_rows),
        },
        "classes": class_rows,
    }
    downloader_profiles = {
        "schema_version": DOWNLOADER_PROFILE_SCHEMA,
        "material_class_policy_version": MATERIAL_CLASS_POLICY_VERSION,
        "material_class_registry_sha256": registry.snapshot_sha256,
        "defaults": {
            "file_types": ["resolution_1K", "resolution_0_5K"],
            "require_nonprocedural": True,
            "require_pure_pbr": True,
            "realistic_only": True,
        },
        "profiles": profiles,
    }
    return plan, downloader_profiles


def _atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def write_documents(
    output_dir: Path,
    plan: Mapping[str, Any],
    downloader_profiles: Mapping[str, Any],
) -> tuple[Path, Path]:
    root = output_dir.resolve()
    plan_path = root / "material_class_plan.json"
    profiles_path = root / "blenderkit_profiles.json"
    _atomic_json(plan_path, dict(plan))
    _atomic_json(profiles_path, dict(downloader_profiles))
    return plan_path, profiles_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--library-root", type=Path)
    parser.add_argument("--assignments", type=Path)
    parser.add_argument("--bindings", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if (args.catalog is None) != (args.assignments is None):
        raise SystemExit("--catalog and --assignments must be supplied together")
    registry = MaterialClassRegistry.from_json(args.registry)
    catalog = None
    assignments = None
    if args.catalog is not None:
        catalog = MaterialCatalog.from_jsonl(
            args.catalog,
            library_root=args.library_root,
            verify_hashes=True,
            strict_normalized=True,
        )
        assignments = MaterialClassAssignments.from_json(
            args.assignments,
            registry=registry,
            catalog=catalog,
        )
    bindings = _read_jsonl(args.bindings) if args.bindings is not None else []
    plan, profiles = build_material_class_documents(
        registry,
        catalog=catalog,
        assignments=assignments,
        binding_rows=bindings,
    )
    plan_path, profiles_path = write_documents(args.output_dir, plan, profiles)
    print(
        json.dumps(
            {
                "schema_version": MATERIAL_CLASS_PLAN_SCHEMA,
                "plan": plan_path.as_posix(),
                "profiles": profiles_path.as_posix(),
                **plan["summary"],
                "plan_sha256": _sha256(plan_path),
                "profiles_sha256": _sha256(profiles_path),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
