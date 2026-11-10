#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Audit controlled Articraft material classes without downloading assets.

The runtime contract is deliberately tiny: a component requests exactly one
``material_class_id``.  BlenderKit search strings, provider tags, and the
legacy-catalog migration rules in this module are offline discovery evidence
only.  They are never emitted as runtime retrieval fields.

The command can optionally probe the public BlenderKit search API.  A probe
reads metadata and file manifests only; it never calls the downloads endpoint.
"""

from __future__ import annotations

import argparse
import collections
import concurrent.futures
import hashlib
import importlib.util
import json
import math
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = REPO_ROOT.parent
DOWNLOADER_PATH = WORKSPACE_ROOT / "download_blenderkit_materials.py"
DOWNLOADER_SPEC = importlib.util.spec_from_file_location(
    "download_blenderkit_materials", DOWNLOADER_PATH
)
if DOWNLOADER_SPEC is None or DOWNLOADER_SPEC.loader is None:
    raise RuntimeError(f"cannot load BlenderKit downloader: {DOWNLOADER_PATH}")
downloader = importlib.util.module_from_spec(DOWNLOADER_SPEC)
sys.modules[DOWNLOADER_SPEC.name] = downloader
DOWNLOADER_SPEC.loader.exec_module(downloader)

SCHEMA_VERSION = "articraft-material-class-supply/v1"
ASSIGNMENT_SCHEMA_VERSION = "articraft-legacy-material-class-assignment/v1"
DEFAULT_PROFILE_PATH = REPO_ROOT / "data/material_classes_v1.json"
DEFAULT_TAXONOMY_PATH = (
    REPO_ROOT / ".artifacts/pbr_material_library/taxonomy/blenderkit_categories.json"
)
DEFAULT_RAW_CATALOG_PATH = REPO_ROOT / ".artifacts/pbr_material_library/catalog/materials.jsonl"
DEFAULT_NORMALIZED_CATALOG_PATH = (
    REPO_ROOT / ".artifacts/pbr_material_library/normalized/catalogs/latest.json"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / ".artifacts/material_class_supply_v1"
_CLASS_ID_RE = re.compile(r"[a-z0-9][a-z0-9_-]*\.[a-z0-9][a-z0-9_-]*")


@dataclass(frozen=True, slots=True)
class OfflineMatch:
    priority: int
    include_any: tuple[str, ...]
    exclude_any: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class MaterialClassProfile:
    material_class_id: str
    category_slug: str
    demand_count: int
    quota: int
    offline_search_queries: tuple[str, ...]
    offline_match: OfflineMatch
    shader_profile: str
    file_types: tuple[str, ...]
    require_pure_pbr: bool
    require_nonprocedural: bool
    realistic_only: bool
    accepted_licenses: tuple[str, ...]
    max_file_bytes: int


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json_bytes(value: Any, *, pretty: bool = False) -> bytes:
    if pretty:
        payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    else:
        payload = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    return (payload + "\n").encode("utf-8")


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


def _atomic_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    payload = b"".join(_canonical_json_bytes(dict(row)) for row in rows)
    _atomic_write(path, payload)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict) or not value.get("material_id"):
            raise ValueError(f"invalid catalog row at {path}:{line_number}")
        rows.append(value)
    return rows


def resolve_normalized_catalog_path(path: Path) -> tuple[Path, dict[str, Any] | None]:
    """Resolve the immutable strict snapshot selected by ``latest.json``."""

    path = path.resolve()
    if path.suffix == ".jsonl":
        return path, None
    pointer = json.loads(path.read_text(encoding="utf-8"))
    relative = Path(str(pointer.get("catalog_path") or ""))
    if not relative.parts or relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"invalid normalized catalog pointer: {path}")
    # ``latest.json`` lives at normalized/catalogs/latest.json, while its
    # catalog_path is relative to the normalized root.
    normalized_root = path.parent.parent
    resolved = (normalized_root / relative).resolve()
    if normalized_root != resolved and normalized_root not in resolved.parents:
        raise ValueError(f"normalized catalog pointer escapes its root: {path}")
    if not resolved.is_file():
        raise FileNotFoundError(resolved)
    logical_sha = str(pointer.get("logical_snapshot_sha256") or "")
    if logical_sha and resolved.parent.name != logical_sha:
        raise ValueError("normalized catalog pointer digest/path mismatch")
    return resolved, pointer


def _string_tuple(value: Any, *, field: str, allow_empty: bool = False) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field} must be a list of strings")
    result = tuple(dict.fromkeys(item.strip() for item in value if item.strip()))
    if not result and not allow_empty:
        raise ValueError(f"{field} must not be empty")
    return result


def _quota_for_demand(policy: Mapping[str, Any], demand_count: int) -> int:
    quota_policy = policy.get("quota_policy") or {}
    basis = quota_policy.get("basis")
    if basis == "uniform_per_class":
        quota = int(quota_policy.get("quota", 0))
        if quota < 1:
            raise ValueError("uniform_per_class quota must be positive")
        return quota
    if basis != "demand_frequency_only":
        raise ValueError(
            "material class quota policy must use uniform_per_class or demand_frequency_only"
        )
    tiers = quota_policy.get("tiers") or []
    if not isinstance(tiers, list) or not tiers:
        raise ValueError("material class quota policy has no tiers")
    normalized: list[tuple[int, int]] = []
    for row in tiers:
        if not isinstance(row, dict):
            raise ValueError("quota tier must be an object")
        normalized.append((int(row["minimum_demand_count"]), int(row["quota"])))
    for minimum, quota in sorted(normalized, reverse=True):
        if demand_count >= minimum:
            return quota
    raise ValueError(f"quota tiers do not cover demand_count={demand_count}")


def _normalize_registry_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Adapt the formal class registry to the offline supply-profile contract."""

    if payload.get("schema_version") != "articraft-material-class-registry/v1":
        return dict(payload)
    classes = payload.get("classes")
    if not isinstance(classes, list) or not classes:
        raise ValueError("material class registry must contain classes")
    profiles: list[dict[str, Any]] = []
    for index, source_row in enumerate(classes):
        if not isinstance(source_row, dict):
            raise ValueError(f"registry class {index} must be an object")
        retired = {
            "facets",
            "tag_query",
            "query_terms",
            "finish_hints",
            "similarity",
        } & set(source_row)
        if retired:
            raise ValueError(f"registry class {index} uses retired fields: {sorted(retired)}")
        material_class_id = str(source_row.get("material_class_id") or "")
        category_slug = str(source_row.get("parent_category") or "")
        display_name = str(source_row.get("display_name") or "")
        suffix_phrase = material_class_id.partition(".")[2].replace("_", " ")
        offline_match = source_row.get("offline_match")
        if offline_match is None:
            offline_match = {
                "priority": 0,
                "include_any": list(
                    dict.fromkeys(phrase for phrase in (display_name, suffix_phrase) if phrase)
                ),
                "exclude_any": [],
            }
        profiles.append(
            {
                "material_class_id": material_class_id,
                "category_slug": category_slug,
                "demand_count": int(source_row.get("demand_count", 0)),
                "quota": int(source_row.get("initial_quota", 0)),
                "offline_search_queries": source_row.get("discovery_queries") or [],
                "offline_match": offline_match,
                "shader_profile": source_row.get("shader_profile")
                or (
                    "optical_principled"
                    if category_slug in {"glass", "liquid"}
                    else "opaque_metallic_roughness"
                ),
                **{
                    key: source_row[key]
                    for key in (
                        "file_types",
                        "require_pure_pbr",
                        "require_nonprocedural",
                        "realistic_only",
                        "accepted_licenses",
                        "max_file_bytes",
                    )
                    if key in source_row
                },
            }
        )
    return {
        "schema_version": 3,
        "source_schema_version": payload["schema_version"],
        "policy": {
            "runtime_selector": "material_class_id_only",
            "offline_only_fields": [
                "offline_search_queries",
                "offline_match",
                "provider_metadata",
            ],
            "forbidden_runtime_inputs": [
                "facet",
                "tag_query",
                "query_terms",
                "finish_hints",
                "similarity",
            ],
            "quota_policy": {
                "basis": "uniform_per_class",
                "quota": 2,
                "demand_frequency_is_reporting_only": True,
            },
        },
        "defaults": {
            "accepted_licenses": list(downloader.SUPPORTED_LICENSES),
            "file_types": list(downloader.DEFAULT_FILE_TYPES),
            "max_file_bytes": downloader.DEFAULT_MAX_FILE_BYTES,
            "require_pure_pbr": True,
            "require_nonprocedural": True,
            "realistic_only": True,
        },
        "profiles": profiles,
    }


def load_profiles(
    profile_path: Path,
    taxonomy_path: Path,
) -> tuple[dict[str, Any], tuple[MaterialClassProfile, ...]]:
    source_payload = json.loads(profile_path.read_text(encoding="utf-8"))
    payload = _normalize_registry_payload(source_payload)
    if payload.get("schema_version") != 3:
        raise ValueError("material class profiles must use schema_version 3")
    policy = payload.get("policy") or {}
    if policy.get("runtime_selector") != "material_class_id_only":
        raise ValueError("runtime_selector must be material_class_id_only")
    forbidden_runtime = set(policy.get("forbidden_runtime_inputs") or [])
    required_forbidden = {
        "facet",
        "tag_query",
        "query_terms",
        "finish_hints",
        "similarity",
    }
    if not required_forbidden <= forbidden_runtime:
        raise ValueError("profile policy does not forbid all retired runtime inputs")

    taxonomy = json.loads(taxonomy_path.read_text(encoding="utf-8"))
    official_categories = set(taxonomy.get("top_level_slugs") or [])
    if not official_categories:
        raise ValueError("taxonomy has no official top-level slugs")
    defaults = payload.get("defaults") or {}
    rows = payload.get("profiles")
    if not isinstance(rows, list) or not rows:
        raise ValueError("material class profiles must be a non-empty list")

    profiles: list[MaterialClassProfile] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"profile {index} must be an object")
        retired = {"id", "queries", "finish_hints", "facets", "tag_query"} & set(row)
        if retired:
            raise ValueError(f"profile {index} uses retired fields: {sorted(retired)}")
        material_class_id = str(row.get("material_class_id") or "")
        category_slug = str(row.get("category_slug") or "")
        if not _CLASS_ID_RE.fullmatch(material_class_id):
            raise ValueError(f"invalid material_class_id: {material_class_id!r}")
        if material_class_id in seen:
            raise ValueError(f"duplicate material_class_id: {material_class_id}")
        seen.add(material_class_id)
        if category_slug not in official_categories:
            raise ValueError(
                f"{material_class_id} category {category_slug!r} is not official top-level"
            )
        if not material_class_id.startswith(f"{category_slug}."):
            raise ValueError(f"{material_class_id} must remain inside category {category_slug!r}")
        demand_count = int(row.get("demand_count", -1))
        quota = int(row.get("quota", 0))
        if demand_count < 0 or quota < 1:
            raise ValueError(f"{material_class_id} has invalid demand/quota")
        expected_quota = _quota_for_demand(policy, demand_count)
        if quota != expected_quota:
            raise ValueError(
                f"{material_class_id} quota {quota} does not match demand tier "
                f"quota {expected_quota}"
            )
        offline_match_value = row.get("offline_match") or {}
        if not isinstance(offline_match_value, dict):
            raise ValueError(f"{material_class_id}.offline_match must be an object")
        file_types = _string_tuple(
            row.get("file_types", defaults.get("file_types", [])),
            field=f"{material_class_id}.file_types",
        )
        accepted_licenses = _string_tuple(
            row.get(
                "accepted_licenses",
                defaults.get("accepted_licenses", list(downloader.SUPPORTED_LICENSES)),
            ),
            field=f"{material_class_id}.accepted_licenses",
        )
        if not set(accepted_licenses) <= set(downloader.SUPPORTED_LICENSES):
            raise ValueError(f"{material_class_id} uses unsupported licenses")
        profiles.append(
            MaterialClassProfile(
                material_class_id=material_class_id,
                category_slug=category_slug,
                demand_count=demand_count,
                quota=quota,
                offline_search_queries=_string_tuple(
                    row.get("offline_search_queries"),
                    field=f"{material_class_id}.offline_search_queries",
                ),
                offline_match=OfflineMatch(
                    priority=int(offline_match_value.get("priority", 0)),
                    include_any=_string_tuple(
                        offline_match_value.get("include_any", []),
                        field=f"{material_class_id}.offline_match.include_any",
                    ),
                    exclude_any=_string_tuple(
                        offline_match_value.get("exclude_any", []),
                        field=f"{material_class_id}.offline_match.exclude_any",
                        allow_empty=True,
                    ),
                ),
                shader_profile=str(
                    row.get(
                        "shader_profile",
                        defaults.get("shader_profile", "opaque_metallic_roughness"),
                    )
                ),
                file_types=file_types,
                require_pure_pbr=bool(
                    row.get("require_pure_pbr", defaults.get("require_pure_pbr", True))
                ),
                require_nonprocedural=bool(
                    row.get(
                        "require_nonprocedural",
                        defaults.get("require_nonprocedural", True),
                    )
                ),
                realistic_only=bool(
                    row.get("realistic_only", defaults.get("realistic_only", True))
                ),
                accepted_licenses=accepted_licenses,
                max_file_bytes=int(
                    row.get(
                        "max_file_bytes",
                        defaults.get("max_file_bytes", downloader.DEFAULT_MAX_FILE_BYTES),
                    )
                ),
            )
        )
    return payload, tuple(profiles)


_SPACE_RE = re.compile(r"\s+")


def _normalized_text(value: Any) -> str:
    text = str(value or "").lower().replace("_", " ").replace("-", " ")
    text = re.sub(r"[^a-z0-9\u00c0-\u024f]+", " ", text)
    return _SPACE_RE.sub(" ", text).strip()


def _offline_catalog_text(row: Mapping[str, Any]) -> str:
    source = row.get("source")
    source = source if isinstance(source, dict) else {}
    fields: list[Any] = [
        row.get("name"),
        row.get("display_name"),
        source.get("name"),
        source.get("display_name"),
        source.get("description"),
        source.get("category"),
    ]
    tags = source.get("tags") or []
    if isinstance(tags, list):
        fields.extend(tags)
    return _normalized_text(" ".join(str(value or "") for value in fields))


def _phrase_present(text: str, phrase: str) -> bool:
    normalized_phrase = _normalized_text(phrase)
    return bool(normalized_phrase) and f" {normalized_phrase} " in f" {text} "


def classify_catalog_row(
    row: Mapping[str, Any],
    profiles: Iterable[MaterialClassProfile],
) -> dict[str, Any]:
    category_slug = str(row.get("category_slug") or "")
    text = _offline_catalog_text(row)
    candidates: list[dict[str, Any]] = []
    for profile in profiles:
        if profile.category_slug != category_slug:
            continue
        excluded_hits = sorted(
            phrase for phrase in profile.offline_match.exclude_any if _phrase_present(text, phrase)
        )
        if excluded_hits:
            continue
        include_hits = sorted(
            phrase for phrase in profile.offline_match.include_any if _phrase_present(text, phrase)
        )
        if not include_hits:
            continue
        candidates.append(
            {
                "material_class_id": profile.material_class_id,
                "priority": profile.offline_match.priority,
                "include_hits": include_hits,
                "score": [
                    profile.offline_match.priority,
                    max(len(_normalized_text(hit).split()) for hit in include_hits),
                    len(include_hits),
                ],
            }
        )
    if not candidates:
        return {
            "status": "unclassified",
            "material_class_id": None,
            "offline_evidence": [],
            "candidate_material_class_ids": [],
        }
    candidates.sort(
        key=lambda value: (value["score"], value["material_class_id"]),
        reverse=True,
    )
    best_score = candidates[0]["score"]
    best = [row for row in candidates if row["score"] == best_score]
    if len(best) != 1:
        return {
            "status": "needs_review",
            "material_class_id": None,
            "offline_evidence": [],
            "candidate_material_class_ids": sorted(value["material_class_id"] for value in best),
        }
    return {
        "status": "assigned",
        "material_class_id": best[0]["material_class_id"],
        "offline_evidence": best[0]["include_hits"],
        "candidate_material_class_ids": [best[0]["material_class_id"]],
    }


def _asset_base_id(row: Mapping[str, Any]) -> str | None:
    source = row.get("source")
    source = source if isinstance(source, dict) else {}
    value = source.get("asset_base_id") or row.get("asset_base_id")
    normalized = str(value or "").strip()
    return normalized or None


def _assignment_row(
    row: Mapping[str, Any],
    classification: Mapping[str, Any],
    *,
    catalog_kind: str,
    catalog_sha256: str,
    inherited_from_raw: bool,
) -> dict[str, Any]:
    return {
        "schema_version": ASSIGNMENT_SCHEMA_VERSION,
        "catalog_kind": catalog_kind,
        "catalog_sha256": catalog_sha256,
        "material_id": str(row["material_id"]),
        "asset_base_id": _asset_base_id(row),
        "category_slug": str(row.get("category_slug") or ""),
        "display_name": str(row.get("display_name") or row.get("name") or ""),
        "status": classification["status"],
        "material_class_id": classification["material_class_id"],
        "candidate_material_class_ids": classification["candidate_material_class_ids"],
        "offline_evidence": classification["offline_evidence"],
        "classification_source": (
            "raw_catalog_asset_base_id" if inherited_from_raw else "offline_exact_phrase_rules"
        ),
        "runtime_fields_emitted": ["material_class_id"],
    }


def classify_catalogs(
    raw_rows: Iterable[Mapping[str, Any]],
    normalized_rows: Iterable[Mapping[str, Any]],
    profiles: Iterable[MaterialClassProfile],
    *,
    raw_catalog_sha256: str,
    normalized_catalog_sha256: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    profile_tuple = tuple(profiles)
    raw_assignments = [
        _assignment_row(
            row,
            classify_catalog_row(row, profile_tuple),
            catalog_kind="raw",
            catalog_sha256=raw_catalog_sha256,
            inherited_from_raw=False,
        )
        for row in raw_rows
    ]
    raw_by_asset_base_id = {
        str(row["asset_base_id"]): row
        for row in raw_assignments
        if row.get("asset_base_id") and row["status"] == "assigned"
    }
    normalized_assignments: list[dict[str, Any]] = []
    for row in normalized_rows:
        asset_base_id = _asset_base_id(row)
        inherited = raw_by_asset_base_id.get(str(asset_base_id)) if asset_base_id else None
        if inherited is None:
            classification = classify_catalog_row(row, profile_tuple)
            inherited_from_raw = False
        else:
            classification = {
                "status": "assigned",
                "material_class_id": inherited["material_class_id"],
                "candidate_material_class_ids": [inherited["material_class_id"]],
                "offline_evidence": inherited["offline_evidence"],
            }
            inherited_from_raw = True
        assignment = _assignment_row(
            row,
            classification,
            catalog_kind="normalized",
            catalog_sha256=normalized_catalog_sha256,
            inherited_from_raw=inherited_from_raw,
        )
        if "runtime_enabled" in row:
            assignment["normalized_active"] = row.get("runtime_enabled") is True
        else:
            assignment["normalized_active"] = (
                row.get("active") is True
                and (row.get("validation") or {}).get("status") == "active"
            )
        normalized_assignments.append(assignment)
    return raw_assignments, normalized_assignments


def _parameter_dict(asset: Mapping[str, Any]) -> dict[str, Any]:
    direct = asset.get("dictParameters")
    if isinstance(direct, dict):
        return dict(direct)
    result: dict[str, Any] = {}
    for row in asset.get("parameters") or []:
        if not isinstance(row, dict):
            continue
        key = row.get("parameterType")
        if isinstance(key, str) and key:
            result[key] = row.get("value")
    return result


def _eligible_asset(
    asset: Mapping[str, Any],
    profile: MaterialClassProfile,
) -> tuple[bool, str]:
    if asset.get("assetType") != "material":
        return False, "not_material"
    if asset.get("isFree") is not True:
        return False, "not_free"
    if str(asset.get("license") or "").lower() not in profile.accepted_licenses:
        return False, "license_not_allowed"
    if asset.get("canDownload") is False:
        return False, "cannot_download"
    if asset.get("verificationStatus") != "validated":
        return False, "not_validated"
    parameters = _parameter_dict(asset)
    if profile.require_pure_pbr and parameters.get("purePbr") is not True:
        return False, "not_pure_pbr"
    if profile.require_nonprocedural and parameters.get("procedural") is not False:
        return False, "procedural_or_unknown"
    if profile.realistic_only and parameters.get("materialStyle") != "realistic":
        return False, "not_realistic"
    if profile.shader_profile == "opaque_metallic_roughness" and parameters.get("pbrType") not in (
        None,
        "",
        "metallic",
    ):
        return False, "incompatible_pbr_type"
    selected_file, issue = downloader._candidate_file(
        dict(asset),
        file_types=profile.file_types,
        max_file_bytes=profile.max_file_bytes,
    )
    if selected_file is None:
        return False, str(issue or "no_preferred_file")
    return True, "eligible"


def _probe_profile(
    profile: MaterialClassProfile,
    *,
    page_size: int,
    sample_per_query: int,
    retries: int,
) -> dict[str, Any]:
    session = downloader._new_session()
    query_rows: list[dict[str, Any]] = []
    unique_assets: dict[str, dict[str, Any]] = {}
    try:
        for offline_query in profile.offline_search_queries:
            query = downloader._build_search_query(
                keywords=offline_query,
                category=profile.category_slug,
                require_nonprocedural=profile.require_nonprocedural,
            )
            response = downloader._request(
                session,
                downloader.SEARCH_URL,
                params={
                    "query": query,
                    "page_size": min(page_size, sample_per_query),
                    "dict_parameters": 1,
                },
                retries=retries,
            )
            payload = response.json()
            results = payload.get("results") or []
            for asset in results[:sample_per_query]:
                asset_base_id = str(asset.get("assetBaseId") or asset.get("id") or "")
                if asset_base_id:
                    unique_assets.setdefault(asset_base_id, asset)
            query_rows.append(
                {
                    "offline_search_query": offline_query,
                    "api_query": query,
                    "api_count": int(payload.get("count") or 0),
                    "sample_count": min(len(results), sample_per_query),
                }
            )
    finally:
        session.close()

    rejected: collections.Counter[str] = collections.Counter()
    eligible_asset_base_ids: list[str] = []
    for asset_base_id, asset in sorted(unique_assets.items()):
        eligible, reason = _eligible_asset(asset, profile)
        if eligible:
            eligible_asset_base_ids.append(asset_base_id)
        else:
            rejected[reason] += 1
    sample_unique_count = len(unique_assets)
    eligible_unique_count = len(eligible_asset_base_ids)
    acceptance_ratio = eligible_unique_count / sample_unique_count if sample_unique_count else 0.0
    max_query_count = max((row["api_count"] for row in query_rows), default=0)
    estimated = max(
        eligible_unique_count,
        math.floor(max_query_count * acceptance_ratio),
    )
    return {
        "api_probe_status": "complete",
        "queries": query_rows,
        "api_query_counts_are_non_additive": True,
        "sample_unique_asset_count": sample_unique_count,
        "eligible_sample_unique_asset_count": eligible_unique_count,
        "eligible_sample_asset_base_ids": eligible_asset_base_ids,
        "eligible_sample_acceptance_ratio": round(acceptance_ratio, 6),
        "eligible_supply_sample_lower_bound": eligible_unique_count,
        "eligible_supply_rough_estimate": estimated,
        "eligible_supply_estimate_method": (
            "max_non_additive_query_count_x_sample_acceptance_ratio"
        ),
        "semantic_class_membership_verified": False,
        "quota_feasible_in_sample": eligible_unique_count >= profile.quota,
        "rejected_sample": dict(sorted(rejected.items())),
    }


def _probe_contract_digest(profile: MaterialClassProfile) -> str:
    contract = {
        "probe_schema_version": 2,
        "material_class_id": profile.material_class_id,
        "category_slug": profile.category_slug,
        "quota": profile.quota,
        "offline_search_queries": list(profile.offline_search_queries),
        "shader_profile": profile.shader_profile,
        "file_types": list(profile.file_types),
        "require_pure_pbr": profile.require_pure_pbr,
        "require_nonprocedural": profile.require_nonprocedural,
        "realistic_only": profile.realistic_only,
        "accepted_licenses": list(profile.accepted_licenses),
        "max_file_bytes": profile.max_file_bytes,
    }
    return hashlib.sha256(_canonical_json_bytes(contract)).hexdigest()


def _cross_class_overlap_report(
    profiles: Iterable[MaterialClassProfile],
    probes: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    category_by_class = {profile.material_class_id: profile.category_slug for profile in profiles}
    classes_by_asset: dict[str, set[str]] = collections.defaultdict(set)
    for material_class_id, probe in probes.items():
        if probe.get("api_probe_status") != "complete":
            continue
        for asset_base_id in probe.get("eligible_sample_asset_base_ids") or []:
            classes_by_asset[str(asset_base_id)].add(material_class_id)

    overlap_rows: list[dict[str, Any]] = []
    per_class_overlap_assets: collections.Counter[str] = collections.Counter()
    cross_category_count = 0
    for asset_base_id, class_ids in sorted(classes_by_asset.items()):
        if len(class_ids) < 2:
            continue
        sorted_class_ids = sorted(class_ids)
        categories = sorted({category_by_class[class_id] for class_id in class_ids})
        if len(categories) > 1:
            cross_category_count += 1
        overlap_rows.append(
            {
                "asset_base_id": asset_base_id,
                "material_class_ids": sorted_class_ids,
                "category_slugs": categories,
            }
        )
        per_class_overlap_assets.update(sorted_class_ids)
    return {
        "method": "deduplicated_eligible_top_sample_asset_base_id_intersection",
        "sample_counts_are_not_provider_totals": True,
        "eligible_unique_asset_count_across_classes": len(classes_by_asset),
        "overlap_asset_count": len(overlap_rows),
        "cross_category_overlap_asset_count": cross_category_count,
        "per_class_overlap_asset_count": dict(sorted(per_class_overlap_assets.items())),
        "assets": overlap_rows,
    }


def _class_counts(
    assignments: Iterable[Mapping[str, Any]],
    *,
    active_only: bool = False,
) -> collections.Counter[str]:
    return collections.Counter(
        str(row["material_class_id"])
        for row in assignments
        if row.get("status") == "assigned"
        and row.get("material_class_id")
        and (not active_only or row.get("normalized_active") is True)
    )


def _category_supply_rows(
    profiles: Iterable[MaterialClassProfile],
    *,
    raw_counts: Mapping[str, int],
    normalized_active_counts: Mapping[str, int],
    probes: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Aggregate prototype evidence without turning it into runtime policy.

    Results from different free-text searches overlap and therefore are never
    summed into a provider-wide supply count.  This distribution is only an
    offline signal for deciding where a larger controlled registry can be
    audited next.
    """

    by_category: dict[str, list[MaterialClassProfile]] = collections.defaultdict(list)
    for profile in profiles:
        by_category[profile.category_slug].append(profile)

    rows: list[dict[str, Any]] = []
    for category_slug, category_profiles in sorted(by_category.items()):
        completed = [
            probes[profile.material_class_id]
            for profile in category_profiles
            if probes.get(profile.material_class_id, {}).get("api_probe_status") == "complete"
        ]
        lower_bounds = sorted(
            int(probe.get("eligible_supply_sample_lower_bound") or 0) for probe in completed
        )
        feasible_count = sum(probe.get("quota_feasible_in_sample") is True for probe in completed)
        if not completed:
            expansion_signal = "not_assessed"
        elif len(category_profiles) < 2:
            expansion_signal = "insufficient_class_diversity_evidence"
        elif feasible_count != len(category_profiles):
            expansion_signal = "cautious"
        else:
            quota_ceiling = max(profile.quota for profile in category_profiles)
            midpoint = len(lower_bounds) // 2
            median_lower_bound = (
                float(lower_bounds[midpoint])
                if len(lower_bounds) % 2
                else (lower_bounds[midpoint - 1] + lower_bounds[midpoint]) / 2
            )
            expansion_signal = (
                "strong"
                if min(lower_bounds) >= 2 * quota_ceiling
                and median_lower_bound >= 4 * quota_ceiling
                else "moderate"
            )
        midpoint = len(lower_bounds) // 2
        median_value = (
            (
                float(lower_bounds[midpoint])
                if len(lower_bounds) % 2
                else (lower_bounds[midpoint - 1] + lower_bounds[midpoint]) / 2
            )
            if lower_bounds
            else None
        )
        rows.append(
            {
                "category_slug": category_slug,
                "prototype_class_count": len(category_profiles),
                "prototype_demand_count": sum(
                    profile.demand_count for profile in category_profiles
                ),
                "prototype_quota_total": sum(profile.quota for profile in category_profiles),
                "current_raw_assigned_count": sum(
                    raw_counts.get(profile.material_class_id, 0) for profile in category_profiles
                ),
                "current_normalized_active_count": sum(
                    normalized_active_counts.get(profile.material_class_id, 0)
                    for profile in category_profiles
                ),
                "api_probed_class_count": len(completed),
                "api_sample_feasible_class_count": feasible_count,
                "api_eligible_sample_lower_bound_min": (
                    min(lower_bounds) if lower_bounds else None
                ),
                "api_eligible_sample_lower_bound_median": median_value,
                "taxonomy_expansion_signal": expansion_signal,
                "supply_counts_are_non_additive": True,
            }
        )
    return rows


def build_report(
    *,
    profile_payload: Mapping[str, Any],
    profiles: tuple[MaterialClassProfile, ...],
    raw_assignments: list[dict[str, Any]],
    normalized_assignments: list[dict[str, Any]],
    profile_path: Path,
    taxonomy_path: Path,
    raw_catalog_path: Path,
    normalized_catalog_path: Path,
    normalized_catalog_pointer_path: Path | None,
    normalized_catalog_pointer: Mapping[str, Any] | None,
    probe_api: bool,
    workers: int,
    page_size: int,
    sample_per_query: int,
    retries: int,
    probe_cache_dir: Path | None,
) -> dict[str, Any]:
    raw_counts = _class_counts(raw_assignments)
    normalized_counts = _class_counts(normalized_assignments)
    normalized_active_counts = _class_counts(
        normalized_assignments,
        active_only=True,
    )
    probes: dict[str, dict[str, Any]] = {}
    probe_cache_hit_count = 0
    if probe_api:
        profiles_to_probe: list[MaterialClassProfile] = []
        for profile in profiles:
            cache_path = (
                probe_cache_dir / f"{profile.material_class_id}.json"
                if probe_cache_dir is not None
                else None
            )
            cached: Mapping[str, Any] | None = None
            if cache_path is not None and cache_path.is_file():
                candidate = json.loads(cache_path.read_text(encoding="utf-8"))
                if (
                    candidate.get("probe_contract_sha256") == _probe_contract_digest(profile)
                    and isinstance(candidate.get("probe"), dict)
                    and candidate["probe"].get("api_probe_status") == "complete"
                ):
                    cached = candidate["probe"]
            if cached is None:
                profiles_to_probe.append(profile)
            else:
                probes[profile.material_class_id] = dict(cached)
                probe_cache_hit_count += 1
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as executor:
            futures = {
                executor.submit(
                    _probe_profile,
                    profile,
                    page_size=page_size,
                    sample_per_query=sample_per_query,
                    retries=retries,
                ): profile.material_class_id
                for profile in profiles_to_probe
            }
            completed = 0
            for future in concurrent.futures.as_completed(futures):
                material_class_id = futures[future]
                try:
                    probes[material_class_id] = future.result()
                except Exception as exc:  # one provider query must not lose the audit
                    probes[material_class_id] = {
                        "api_probe_status": "error",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                        "quota_feasible_in_sample": False,
                    }
                else:
                    if probe_cache_dir is not None:
                        cache_path = probe_cache_dir / f"{material_class_id}.json"
                        profile = next(
                            profile
                            for profile in profiles_to_probe
                            if profile.material_class_id == material_class_id
                        )
                        _atomic_write(
                            cache_path,
                            _canonical_json_bytes(
                                {
                                    "schema_version": (
                                        "articraft-material-class-api-probe-cache/v1"
                                    ),
                                    "probe_contract_sha256": _probe_contract_digest(profile),
                                    "probe": probes[material_class_id],
                                },
                                pretty=True,
                            ),
                        )
                completed += 1
                print(
                    f"[{completed:03d}/{len(profiles_to_probe):03d}] probed {material_class_id}",
                    file=sys.stderr,
                )

    class_rows: list[dict[str, Any]] = []
    for profile in profiles:
        raw_count = raw_counts[profile.material_class_id]
        normalized_count = normalized_counts[profile.material_class_id]
        active_count = normalized_active_counts[profile.material_class_id]
        row = {
            "material_class_id": profile.material_class_id,
            "category_slug": profile.category_slug,
            "demand_count": profile.demand_count,
            "initial_quota": profile.quota,
            "offline_search_queries": list(profile.offline_search_queries),
            "current_raw_assigned_count": raw_count,
            "current_normalized_assigned_count": normalized_count,
            "current_normalized_active_count": active_count,
            "download_gap_to_initial_quota": max(0, profile.quota - raw_count),
            "normalization_gap_to_initial_quota": max(0, profile.quota - active_count),
            "recommended_next_action": (
                "ready"
                if active_count >= profile.quota
                else "normalize_existing"
                if raw_count >= profile.quota
                else "discover_and_plan_delta"
            ),
            "api_probe": probes.get(
                profile.material_class_id,
                {"api_probe_status": "not_requested"},
            ),
        }
        class_rows.append(row)

    category_rows = _category_supply_rows(
        profiles,
        raw_counts=raw_counts,
        normalized_active_counts=normalized_active_counts,
        probes=probes,
    )
    overlap_report = _cross_class_overlap_report(profiles, probes)

    raw_status = collections.Counter(row["status"] for row in raw_assignments)
    normalized_status = collections.Counter(row["status"] for row in normalized_assignments)
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "policy": profile_payload["policy"],
        "inputs": {
            "profiles": {
                "path": os.fspath(profile_path),
                "sha256": _sha256(profile_path),
            },
            "taxonomy": {
                "path": os.fspath(taxonomy_path),
                "sha256": _sha256(taxonomy_path),
            },
            "raw_catalog": {
                "path": os.fspath(raw_catalog_path),
                "sha256": _sha256(raw_catalog_path),
                "row_count": len(raw_assignments),
            },
            "normalized_catalog": {
                "path": os.fspath(normalized_catalog_path),
                "sha256": _sha256(normalized_catalog_path),
                "row_count": len(normalized_assignments),
                "pointer_path": (
                    os.fspath(normalized_catalog_pointer_path)
                    if normalized_catalog_pointer_path is not None
                    else None
                ),
                "pointer_sha256": (
                    _sha256(normalized_catalog_pointer_path)
                    if normalized_catalog_pointer_path is not None
                    else None
                ),
                "logical_snapshot_sha256": (
                    normalized_catalog_pointer.get("logical_snapshot_sha256")
                    if normalized_catalog_pointer is not None
                    else None
                ),
            },
        },
        "probe": {
            "api_root": downloader.API_ROOT,
            "requested": probe_api,
            "page_size": page_size,
            "sample_per_query": sample_per_query,
            "downloads_endpoint_called": False,
            "semantic_class_assignment_performed": False,
            "quota_feasibility_scope": ("provider_search_result_after_technical_gates_only"),
            "cache_hit_count": probe_cache_hit_count,
        },
        "summary": {
            "material_class_count": len(profiles),
            "category_count": len({profile.category_slug for profile in profiles}),
            "initial_quota_total": sum(profile.quota for profile in profiles),
            "raw_assignment_status": dict(sorted(raw_status.items())),
            "normalized_assignment_status": dict(sorted(normalized_status.items())),
            "normalized_runtime_enabled_total": sum(
                row.get("normalized_active") is True for row in normalized_assignments
            ),
            "raw_assigned_count": sum(raw_counts.values()),
            "normalized_active_assigned_count": sum(normalized_active_counts.values()),
            "download_gap_total": sum(
                max(0, profile.quota - raw_counts[profile.material_class_id])
                for profile in profiles
            ),
            "normalization_gap_total": sum(
                max(
                    0,
                    profile.quota - normalized_active_counts[profile.material_class_id],
                )
                for profile in profiles
            ),
            "api_sample_feasible_class_count": sum(
                probes.get(profile.material_class_id, {}).get("quota_feasible_in_sample", False)
                for profile in profiles
            ),
            "strong_expansion_category_count": sum(
                row["taxonomy_expansion_signal"] == "strong" for row in category_rows
            ),
            "api_sample_cross_class_overlap_asset_count": overlap_report["overlap_asset_count"],
        },
        "classes": class_rows,
        "categories": category_rows,
        "cross_class_overlap": overlap_report,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILE_PATH)
    parser.add_argument("--taxonomy", type=Path, default=DEFAULT_TAXONOMY_PATH)
    parser.add_argument("--raw-catalog", type=Path, default=DEFAULT_RAW_CATALOG_PATH)
    parser.add_argument(
        "--normalized-catalog",
        type=Path,
        default=DEFAULT_NORMALIZED_CATALOG_PATH,
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--probe-api", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--page-size", type=int, default=80)
    parser.add_argument("--sample-per-query", type=int, default=80)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Write audit artifacts; never downloads BlenderKit files",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.workers < 1 or args.retries < 1:
        raise ValueError("workers and retries must be positive")
    if not 1 <= args.page_size <= 80 or not 1 <= args.sample_per_query <= 80:
        raise ValueError("page_size and sample_per_query must be between 1 and 80")
    profile_path = args.profiles.resolve()
    taxonomy_path = args.taxonomy.resolve()
    raw_catalog_path = args.raw_catalog.resolve()
    normalized_catalog_argument = args.normalized_catalog.resolve()
    normalized_catalog_path, normalized_catalog_pointer = resolve_normalized_catalog_path(
        normalized_catalog_argument
    )
    profile_payload, profiles = load_profiles(profile_path, taxonomy_path)
    raw_rows = _read_jsonl(raw_catalog_path)
    normalized_rows = _read_jsonl(normalized_catalog_path)
    raw_assignments, normalized_assignments = classify_catalogs(
        raw_rows,
        normalized_rows,
        profiles,
        raw_catalog_sha256=_sha256(raw_catalog_path),
        normalized_catalog_sha256=_sha256(normalized_catalog_path),
    )
    report = build_report(
        profile_payload=profile_payload,
        profiles=profiles,
        raw_assignments=raw_assignments,
        normalized_assignments=normalized_assignments,
        profile_path=profile_path,
        taxonomy_path=taxonomy_path,
        raw_catalog_path=raw_catalog_path,
        normalized_catalog_path=normalized_catalog_path,
        normalized_catalog_pointer_path=(
            normalized_catalog_argument if normalized_catalog_pointer is not None else None
        ),
        normalized_catalog_pointer=normalized_catalog_pointer,
        probe_api=bool(args.probe_api),
        workers=args.workers,
        page_size=args.page_size,
        sample_per_query=args.sample_per_query,
        retries=args.retries,
        probe_cache_dir=(
            args.output_dir.resolve() / "api_probe_cache"
            if args.execute and args.probe_api
            else None
        ),
    )
    if args.execute:
        output_dir = args.output_dir.resolve()
        _atomic_jsonl(output_dir / "raw_assignments.jsonl", raw_assignments)
        _atomic_jsonl(
            output_dir / "normalized_assignments.jsonl",
            normalized_assignments,
        )
        _atomic_write(
            output_dir / "supply_report.json",
            _canonical_json_bytes(report, pretty=True),
        )
    print(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "executed": bool(args.execute),
                "probe_api": bool(args.probe_api),
                **report["summary"],
            },
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
