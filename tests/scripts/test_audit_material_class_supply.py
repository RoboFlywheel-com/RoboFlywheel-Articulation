# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib.util
import json
import sys

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOWNLOADER_PATH = ROOT.parent / "download_blenderkit_materials.py"
if not DOWNLOADER_PATH.is_file():
    pytest.skip("optional BlenderKit discovery downloader is not included", allow_module_level=True)

DOWNLOADER_SPEC = importlib.util.spec_from_file_location(
    "download_blenderkit_materials", DOWNLOADER_PATH
)
assert DOWNLOADER_SPEC is not None and DOWNLOADER_SPEC.loader is not None
downloader = importlib.util.module_from_spec(DOWNLOADER_SPEC)
sys.modules[DOWNLOADER_SPEC.name] = downloader
DOWNLOADER_SPEC.loader.exec_module(downloader)

MODULE_PATH = ROOT / "scripts" / "audit_material_class_supply.py"
SPEC = importlib.util.spec_from_file_location("audit_material_class_supply", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


def _write_taxonomy(path: Path) -> None:
    path.write_text(
        json.dumps({"top_level_slugs": ["liquid", "surface-finish", "metal", "plastic"]}),
        encoding="utf-8",
    )


def _profile_payload(class_count: int) -> dict[str, object]:
    profiles = []
    for index in range(class_count):
        profiles.append(
            {
                "material_class_id": f"metal.class_{index}",
                "category_slug": "metal",
                "demand_count": 1,
                "quota": 2,
                "offline_search_queries": [f"metal class {index}"],
                "offline_match": {
                    "priority": 1,
                    "include_any": [f"class {index}"],
                    "exclude_any": [],
                },
            }
        )
    return {
        "schema_version": 3,
        "policy": {
            "runtime_selector": "material_class_id_only",
            "forbidden_runtime_inputs": [
                "facet",
                "tag_query",
                "query_terms",
                "finish_hints",
                "similarity",
            ],
            "quota_policy": {
                "basis": "demand_frequency_only",
                "tiers": [{"minimum_demand_count": 0, "quota": 2}],
            },
        },
        "defaults": {
            "accepted_licenses": ["cc_zero", "royalty_free"],
            "file_types": ["resolution_1K"],
            "max_file_bytes": 1024,
            "require_pure_pbr": True,
            "require_nonprocedural": True,
            "realistic_only": True,
        },
        "profiles": profiles,
    }


def test_registry_size_is_not_hard_coded(tmp_path: Path) -> None:
    taxonomy_path = tmp_path / "taxonomy.json"
    profile_path = tmp_path / "profiles.json"
    _write_taxonomy(taxonomy_path)
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": "articraft-material-class-registry/v1",
                "classes": [
                    {
                        "material_class_id": f"metal.class_{index}",
                        "parent_category": "metal",
                        "display_name": f"Metal class {index}",
                        "description": "Controlled test class",
                        "discovery_queries": [f"metal class {index}"],
                        "initial_quota": 2,
                    }
                    for index in range(111)
                ],
            }
        ),
        encoding="utf-8",
    )

    payload, profiles = audit.load_profiles(profile_path, taxonomy_path)

    assert len(profiles) == 111
    assert profiles[-1].material_class_id == "metal.class_110"
    assert payload["policy"]["quota_policy"] == {
        "basis": "uniform_per_class",
        "quota": 2,
        "demand_frequency_is_reporting_only": True,
    }


def test_latest_pointer_is_resolved_inside_normalized_root(tmp_path: Path) -> None:
    normalized = tmp_path / "normalized"
    snapshot_sha = "a" * 64
    catalog = normalized / "catalogs" / snapshot_sha / "materials.jsonl"
    catalog.parent.mkdir(parents=True)
    catalog.write_text("{}\n", encoding="utf-8")
    pointer_path = normalized / "catalogs" / "latest.json"
    pointer_path.write_text(
        json.dumps(
            {
                "catalog_path": f"catalogs/{snapshot_sha}/materials.jsonl",
                "logical_snapshot_sha256": snapshot_sha,
            }
        ),
        encoding="utf-8",
    )

    resolved, pointer = audit.resolve_normalized_catalog_path(pointer_path)

    assert resolved == catalog.resolve()
    assert pointer is not None
    assert pointer["logical_snapshot_sha256"] == snapshot_sha


def test_hyphenated_parent_slug_is_a_valid_class_prefix(
    tmp_path: Path,
) -> None:
    taxonomy_path = tmp_path / "taxonomy.json"
    profile_path = tmp_path / "registry.json"
    _write_taxonomy(taxonomy_path)
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": "articraft-material-class-registry/v1",
                "classes": [
                    {
                        "material_class_id": "surface-finish.polished",
                        "parent_category": "surface-finish",
                        "display_name": "Polished finish",
                        "discovery_queries": ["polished surface finish"],
                        "initial_quota": 2,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    _payload, profiles = audit.load_profiles(profile_path, taxonomy_path)

    assert profiles[0].material_class_id == "surface-finish.polished"


def test_liquid_registry_profile_keeps_standard_texture_requirements(tmp_path: Path) -> None:
    taxonomy_path = tmp_path / "taxonomy.json"
    profile_path = tmp_path / "registry.json"
    _write_taxonomy(taxonomy_path)
    profile_path.write_text(
        json.dumps(
            {
                "schema_version": "articraft-material-class-registry/v1",
                "classes": [
                    {
                        "material_class_id": "liquid.water_wave_foam",
                        "parent_category": "liquid",
                        "display_name": "Water with waves or foam",
                        "discovery_queries": ["ocean water waves foam"],
                        "initial_quota": 2,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    _payload, profiles = audit.load_profiles(profile_path, taxonomy_path)

    profile = profiles[0]
    assert profile.shader_profile == "optical_principled"
    assert profile.require_pure_pbr
    assert profile.require_nonprocedural
    assert profile.file_types == tuple(downloader.DEFAULT_FILE_TYPES)


def test_classification_emits_only_material_class_id_as_runtime_field(
    tmp_path: Path,
) -> None:
    taxonomy_path = tmp_path / "taxonomy.json"
    profile_path = tmp_path / "profiles.json"
    _write_taxonomy(taxonomy_path)
    profile_path.write_text(json.dumps(_profile_payload(1)), encoding="utf-8")
    _payload, profiles = audit.load_profiles(profile_path, taxonomy_path)
    row = {
        "material_id": "raw:one",
        "category_slug": "metal",
        "display_name": "Metal Class 0",
        "source": {"asset_base_id": "asset-one", "tags": ["class 0"]},
    }

    assignment = audit._assignment_row(
        row,
        audit.classify_catalog_row(row, profiles),
        catalog_kind="raw",
        catalog_sha256="digest",
        inherited_from_raw=False,
    )

    assert assignment["status"] == "assigned"
    assert assignment["material_class_id"] == "metal.class_0"
    assert assignment["runtime_fields_emitted"] == ["material_class_id"]
    for retired in ("facet", "tag_query", "query_terms", "finish_hints", "similarity"):
        assert retired not in assignment


def test_category_expansion_signal_uses_non_additive_probe_distribution() -> None:
    profile = audit.MaterialClassProfile
    offline = audit.OfflineMatch(priority=1, include_any=("metal",), exclude_any=())
    common = {
        "category_slug": "metal",
        "demand_count": 1,
        "quota": 2,
        "offline_search_queries": ("metal",),
        "offline_match": offline,
        "shader_profile": "opaque_metallic_roughness",
        "file_types": ("resolution_1K",),
        "require_pure_pbr": True,
        "require_nonprocedural": True,
        "realistic_only": True,
        "accepted_licenses": ("cc_zero", "royalty_free"),
        "max_file_bytes": 1024,
    }
    profiles = (
        profile(material_class_id="metal.a", **common),
        profile(material_class_id="metal.b", **common),
    )
    probes = {
        "metal.a": {
            "api_probe_status": "complete",
            "eligible_supply_sample_lower_bound": 12,
            "quota_feasible_in_sample": True,
        },
        "metal.b": {
            "api_probe_status": "complete",
            "eligible_supply_sample_lower_bound": 20,
            "quota_feasible_in_sample": True,
        },
    }

    rows = audit._category_supply_rows(
        profiles,
        raw_counts={},
        normalized_active_counts={},
        probes=probes,
    )

    assert rows[0]["taxonomy_expansion_signal"] == "strong"
    assert rows[0]["supply_counts_are_non_additive"] is True
    assert "api_eligible_supply_total" not in rows[0]
    overlap = audit._cross_class_overlap_report(
        profiles,
        {
            key: {**probe, "eligible_sample_asset_base_ids": ["shared-asset"]}
            for key, probe in probes.items()
        },
    )
    assert overlap["overlap_asset_count"] == 1
    assert overlap["cross_category_overlap_asset_count"] == 0
    assert overlap["assets"][0]["material_class_ids"] == ["metal.a", "metal.b"]


def test_cli_writes_supply_and_raw_strict_assignments(
    tmp_path: Path,
    monkeypatch,
) -> None:
    taxonomy_path = tmp_path / "taxonomy.json"
    registry_path = tmp_path / "registry.json"
    raw_path = tmp_path / "raw.jsonl"
    normalized_root = tmp_path / "normalized"
    snapshot_sha = "b" * 64
    normalized_path = normalized_root / "catalogs" / snapshot_sha / "materials.jsonl"
    pointer_path = normalized_root / "catalogs" / "latest.json"
    output_dir = tmp_path / "output"
    _write_taxonomy(taxonomy_path)
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": "articraft-material-class-registry/v1",
                "classes": [
                    {
                        "material_class_id": "metal.stainless_steel",
                        "parent_category": "metal",
                        "display_name": "Stainless steel",
                        "description": "Stainless steel PBR",
                        "discovery_queries": ["stainless steel"],
                        "initial_quota": 2,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    raw_row = {
        "material_id": "blenderkit:raw",
        "category_slug": "metal",
        "display_name": "Brushed Stainless Steel",
        "source": {"asset_base_id": "base-one"},
    }
    normalized_row = {
        **raw_row,
        "material_id": "blenderkit:normalized",
        "runtime_enabled": True,
    }
    raw_path.write_text(json.dumps(raw_row) + "\n", encoding="utf-8")
    normalized_path.parent.mkdir(parents=True)
    normalized_path.write_text(json.dumps(normalized_row) + "\n", encoding="utf-8")
    pointer_path.write_text(
        json.dumps(
            {
                "catalog_path": f"catalogs/{snapshot_sha}/materials.jsonl",
                "logical_snapshot_sha256": snapshot_sha,
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(
        audit,
        "_probe_profile",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("API probe must remain optional")
        ),
    )

    result = audit.main(
        [
            "--profiles",
            str(registry_path),
            "--taxonomy",
            str(taxonomy_path),
            "--raw-catalog",
            str(raw_path),
            "--normalized-catalog",
            str(pointer_path),
            "--output-dir",
            str(output_dir),
            "--execute",
        ]
    )

    assert result == 0
    report = json.loads((output_dir / "supply_report.json").read_text())
    assert report["summary"]["material_class_count"] == 1
    assert report["summary"]["normalized_runtime_enabled_total"] == 1
    assert report["summary"]["normalized_active_assigned_count"] == 1
    assert report["summary"]["download_gap_total"] == 1
    assert report["probe"]["requested"] is False
    assert report["probe"]["downloads_endpoint_called"] is False
    for name in ("raw_assignments.jsonl", "normalized_assignments.jsonl"):
        assignment = json.loads((output_dir / name).read_text())
        assert assignment["material_class_id"] == "metal.stainless_steel"
        assert assignment["runtime_fields_emitted"] == ["material_class_id"]


def test_api_probe_reads_search_metadata_without_downloading(monkeypatch) -> None:
    class Session:
        def close(self) -> None:
            pass

    class Response:
        def json(self) -> dict[str, object]:
            return {
                "count": 7,
                "results": [
                    {
                        "id": "version-one",
                        "assetBaseId": "base-one",
                        "assetType": "material",
                        "isFree": True,
                        "license": "royalty_free",
                        "canDownload": True,
                        "verificationStatus": "validated",
                        "dictParameters": {
                            "purePbr": True,
                            "procedural": False,
                            "materialStyle": "realistic",
                            "pbrType": "metallic",
                        },
                    }
                ],
            }

    requested_urls: list[str] = []

    def request(_session, url, **_kwargs):
        requested_urls.append(url)
        return Response()

    monkeypatch.setattr(audit.downloader, "_new_session", lambda: Session())
    monkeypatch.setattr(audit.downloader, "_request", request)
    monkeypatch.setattr(
        audit.downloader,
        "_candidate_file",
        lambda *_args, **_kwargs: ({"id": "file-one"}, None),
    )
    profile = audit.MaterialClassProfile(
        material_class_id="metal.stainless_steel",
        category_slug="metal",
        demand_count=10,
        quota=2,
        offline_search_queries=("stainless steel",),
        offline_match=audit.OfflineMatch(
            priority=0,
            include_any=("stainless steel",),
            exclude_any=(),
        ),
        shader_profile="opaque_metallic_roughness",
        file_types=("resolution_1K",),
        require_pure_pbr=True,
        require_nonprocedural=True,
        realistic_only=True,
        accepted_licenses=("cc_zero", "royalty_free"),
        max_file_bytes=1024,
    )

    probe = audit._probe_profile(
        profile,
        page_size=40,
        sample_per_query=40,
        retries=1,
    )

    assert requested_urls == [audit.downloader.SEARCH_URL]
    assert probe["eligible_supply_sample_lower_bound"] == 1
    assert probe["eligible_sample_asset_base_ids"] == ["base-one"]
    assert probe["quota_feasible_in_sample"] is False
