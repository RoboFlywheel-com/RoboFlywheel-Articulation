# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json
import sys
import textwrap
from pathlib import Path

import pytest

from articraft.appearance.catalog import MaterialCatalog
from articraft.appearance.normalized import (
    NORMALIZED_CATALOG_MANIFEST_SCHEMA,
    NORMALIZED_CATALOG_SCHEMA,
    NORMALIZED_PACKAGE_SCHEMA,
    NORMALIZER_VERSION,
    RUNTIME_PROFILE_POLICY_VERSION,
    generic_eligibility,
    logical_catalog_snapshot_sha256,
    native_runtime_allowlist_sha256,
)
from scripts import convert_native_texture_sets as target


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _source_library(
    workspace: Path,
    material_ids: tuple[str, ...] = ("native-good", "native-bad"),
) -> tuple[Path, Path, list[dict[str, object]]]:
    root = workspace / "source-normalized"
    raw_catalog = root / "catalog" / "materials.jsonl"
    raw_catalog.parent.mkdir(parents=True)
    raw_catalog.write_text("raw provenance\n", encoding="utf-8")
    raw_sha = _sha256(raw_catalog)
    rows: list[dict[str, object]] = []
    for index, material_id in enumerate(material_ids, 1):
        identity = f"{index:016x}"
        source_identity = f"{index + 100:016x}"
        blend_relative = Path("packages") / "metal" / identity / source_identity / "material.blend"
        metadata_relative = blend_relative.with_name("metadata.json")
        blend = root / blend_relative
        blend.parent.mkdir(parents=True)
        blend.write_bytes(f"native-blend:{material_id}".encode())
        blend_sha = _sha256(blend)
        mapping = {
            "coordinate_source": "native_node_graph",
            "coordinate_unit": "meter",
            "generic_box_projection_allowed": False,
            "mapping_profile": "native_node_graph",
            "model_uvs_are_not_baked": True,
            "normal_space": "native",
            "requires_uv": False,
            "tile_size_m": 1.0,
        }
        eligibility = generic_eligibility(
            display_name=material_id,
            category_slug="metal",
            profile="native_procedural",
            tile_size_m=1.0,
            qa_status="pass",
        )
        node_qa = {
            "status": "pass",
            "issues": [],
            "output_surface_connected": True,
        }
        displacement = {
            "policy": "disconnect_true_displacement",
            "source_output_link_count": 0,
            "removed_output_link_count": 0,
            "normal_and_bump_preserved": True,
        }
        channel_qa = {"channels": [], "channel_counts": {}}
        metadata = {
            "schema_version": NORMALIZED_PACKAGE_SCHEMA,
            "material_id": material_id,
            "category_slug": "metal",
            "display_name": material_id,
            "material_profile": "native_procedural",
            "normalization_class": "native",
            "texture_size_m": 1.0,
            "mapping_contract": mapping,
            "eligibility": eligibility,
            "displacement_policy": displacement,
            "channel_qa": channel_qa,
            "node_qa": node_qa,
            "package": {
                "blend_path": blend_relative.as_posix(),
                "blend_sha256": blend_sha,
            },
            "normalizer": {
                "version": NORMALIZER_VERSION,
                "source_preserved": True,
                "shader_graph_policy": "provider_graph_preserved",
            },
        }
        _write_json(root / metadata_relative, metadata)
        source = {
            "asset_base_id": f"asset-{material_id}",
            "category": "metal",
            "display_name": material_id,
            "parameters": {"procedural": True, "textureSizeMeters": 1.0},
            "tags": ["metal"],
        }
        row = {
            "schema_version": NORMALIZED_CATALOG_SCHEMA,
            "material_id": material_id,
            "category_slug": "metal",
            "display_name": material_id,
            "provider": "blenderkit",
            "license": "royalty_free",
            "asset_base_id": f"asset-{material_id}",
            "tags": ["metal"],
            "source": source,
            "normalized_blend_path": blend_relative.as_posix(),
            "normalized_metadata_path": metadata_relative.as_posix(),
            "sha256": blend_sha,
            "material_profile": "native_procedural",
            "normalization_class": "native",
            "texture_size_m": 1.0,
            "mapping_contract": mapping,
            "eligibility": eligibility,
            "eligible_for_generic": True,
            "restrictions": eligibility["restrictions"],
            "quarantine_reason": None,
            "normalization_version": NORMALIZER_VERSION,
            "channels": [],
            "channel_qa": channel_qa,
            "displacement_policy": displacement,
            "package_reopen_qa": {"status": "pass"},
            "active": True,
            "validation": eligibility["validation"],
            "selection_scope": "generic",
            "semantic_risk_reason": None,
            "node_qa": node_qa,
            "provenance": {
                "provider": "blenderkit",
                "license": "royalty_free",
                "asset_base_id": f"asset-{material_id}",
                "blend_path": f"raw/{material_id}.blend",
                "blend_sha256": hashlib.sha256(f"raw:{material_id}".encode()).hexdigest(),
                "catalog_path": "catalog/materials.jsonl",
                "catalog_sha256": raw_sha,
                "catalog_row_sha256": hashlib.sha256(material_id.encode()).hexdigest(),
            },
            "normalizer": metadata["normalizer"],
            "runtime_enabled": False,
            "runtime_profile": {
                "enabled": False,
                "native_allowlisted": False,
                "policy_version": RUNTIME_PROFILE_POLICY_VERSION,
                "reason": "native_procedural_not_allowlisted",
            },
        }
        rows.append(row)

    staging = root / "catalogs" / "staging"
    staging.mkdir(parents=True)
    catalog = staging / "materials.jsonl"
    catalog.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    catalog_sha = _sha256(catalog)
    allowlist_sha = native_runtime_allowlist_sha256(())
    logical_sha = logical_catalog_snapshot_sha256(
        catalog_file_sha256=catalog_sha,
        raw_catalog_sha256=raw_sha,
        native_allowlist_sha256=allowlist_sha,
    )
    manifest = {
        "schema_version": NORMALIZED_CATALOG_MANIFEST_SCHEMA,
        "logical_snapshot_sha256": logical_sha,
        "materials_file": {
            "material_count": len(rows),
            "path": "materials.jsonl",
            "sha256": catalog_sha,
        },
        "raw_catalog": {
            "path": raw_catalog.relative_to(root).as_posix(),
            "sha256": raw_sha,
        },
        "native_runtime_allowlist_sha256": allowlist_sha,
        "normalizer_version": NORMALIZER_VERSION,
        "runtime_profile_policy_version": RUNTIME_PROFILE_POLICY_VERSION,
    }
    _write_json(staging / "manifest.json", manifest)
    destination = root / "catalogs" / logical_sha
    staging.rename(destination)
    _write_json(
        root / "catalogs" / "latest.json",
        {
            "catalog_path": f"catalogs/{logical_sha}/materials.jsonl",
            "logical_snapshot_sha256": logical_sha,
            "manifest_path": f"catalogs/{logical_sha}/manifest.json",
        },
    )
    return root, destination / "materials.jsonl", rows


def _safe_file(workspace: Path, catalog: Path, rows: list[dict[str, object]]) -> Path:
    catalog_sha = _sha256(catalog)
    safe = workspace / "safe.jsonl"
    safe_rows = []
    for row in rows:
        material_id = str(row["material_id"])
        safe_rows.append(
            {
                "schema_version": target.SAFE_SCHEMA,
                "classifier_version": target.CLASSIFIER_VERSION,
                "decision": target.SAFE_DECISION,
                "material_id": material_id,
                "display_name": row["display_name"],
                "category_slug": row["category_slug"],
                "catalog_sha256": catalog_sha,
                "package_relative_path": row["normalized_blend_path"],
                "package_sha256": row["sha256"],
                "input_sha256": hashlib.sha256(f"safe:{material_id}".encode()).hexdigest(),
                "reason_codes": ["generic_repeatable_image_or_constant_pbr"],
            }
        )
    safe.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in safe_rows),
        encoding="utf-8",
    )
    return safe


def _fake_worker(workspace: Path) -> Path:
    worker = workspace / "fake_worker.py"
    worker.write_text(
        textwrap.dedent(
            f"""
            import hashlib
            import json
            from pathlib import Path
            import sys

            PREFIX = {target.RESULT_PREFIX!r}
            VERSION = {target.CONVERSION_VERSION!r}
            RESULT_SCHEMA = {target.RESULT_SCHEMA!r}
            METADATA_SCHEMA = {target.WORKER_METADATA_SCHEMA!r}
            CHANNELS = {target.CHANNELS!r}

            def sha(path):
                return hashlib.sha256(path.read_bytes()).hexdigest()

            def canonical(value):
                raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
                return hashlib.sha256(raw.encode()).hexdigest()

            payload = json.loads(sys.stdin.read())
            root = Path(payload["workspace_root"])
            with (root / ".fake_worker_calls").open("a", encoding="utf-8") as handle:
                handle.write("call\\n")
            for job in payload["materials"]:
                base = {{
                    "schema_version": RESULT_SCHEMA,
                    "conversion_version": VERSION,
                    "material_id": job["material_id"],
                    "source_blend_path": job["source_blend_path"],
                    "source_blend_sha256": job["source_blend_sha256"],
                    "catalog_sha256": job["catalog_sha256"],
                    "eligibility_input_sha256": job["eligibility_input_sha256"],
                    "bpy_version": "5.2.0",
                    "resolution": [1024, 1024],
                }}
                if job["material_id"].endswith("bad"):
                    result = {{**base, "status": "failure", "failure_codes": ["fake_failure"],
                              "conversion_input_sha256": None, "channels": [],
                              "output": None, "reopen_qa": None}}
                else:
                    output = root / job["output_dir"]
                    output.mkdir(parents=True)
                    blend = output / "material.blend"
                    blend.write_bytes(("derived:" + job["material_id"]).encode())
                    channel_rows = {{}}
                    for channel in CHANNELS:
                        channel_rows[channel] = {{
                            "image_name": "Articraft_" + channel + "_1K",
                            "colorspace": "sRGB" if channel == "base_color" else "Non-Color",
                            "packed": True,
                            "png_sha256": hashlib.sha256((job["material_id"] + channel).encode()).hexdigest(),
                            "resolution": [1024, 1024],
                        }}
                    conversion_input = canonical({{"conversion_version": VERSION, **job}})
                    metadata = {{
                        "schema_version": METADATA_SCHEMA,
                        "material_id": job["material_id"],
                        "channels": [
                            {{"role": channel, **channel_rows[channel]}}
                            for channel in CHANNELS
                        ],
                        "baked_channels": channel_rows,
                        "bake": {{"resolution": [1024, 1024], "uv_layout": "canonical_unit_plane"}},
                    }}
                    metadata_path = output / "metadata.json"
                    metadata_path.write_text(json.dumps(metadata, sort_keys=True) + "\\n", encoding="utf-8")
                    relative_blend = (Path(job["output_dir"]) / "material.blend").as_posix()
                    relative_metadata = (Path(job["output_dir"]) / "metadata.json").as_posix()
                    result = {{
                        **base,
                        "status": "success",
                        "failure_codes": [],
                        "conversion_input_sha256": conversion_input,
                        "channels": list(CHANNELS),
                        "output": {{
                            "blend_path": relative_blend,
                            "blend_sha256": sha(blend),
                            "metadata_path": relative_metadata,
                            "metadata_sha256": sha(metadata_path),
                        }},
                        "reopen_qa": {{"status": "pass"}},
                    }}
                print(PREFIX + json.dumps(result, sort_keys=True), flush=True)
            """
        ),
        encoding="utf-8",
    )
    return worker


def _args(
    *,
    workspace: Path,
    source_root: Path,
    catalog: Path,
    safe: Path,
    output: Path,
    worker: Path,
) -> list[str]:
    return [
        "--workspace-root",
        str(workspace),
        "--source-root",
        str(source_root),
        "--catalog",
        str(catalog),
        "--safe-jsonl",
        str(safe),
        "--output-root",
        str(output),
        "--bpy-python",
        sys.executable,
        "--worker",
        str(worker),
        "--workers",
        "2",
        "--batch-size",
        "2",
    ]


def test_dry_run_execute_failure_exclusion_hashes_resume_and_strict_reader(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    workspace = tmp_path
    source_root, catalog, source_rows = _source_library(workspace)
    safe = _safe_file(workspace, catalog, source_rows)
    worker = _fake_worker(workspace)
    output = workspace / "derived"
    source_paths = {catalog, source_root / "catalogs" / "latest.json"}
    source_paths.update(source_root / str(row["normalized_blend_path"]) for row in source_rows)
    source_hashes = {path: _sha256(path) for path in source_paths}
    args = _args(
        workspace=workspace,
        source_root=source_root,
        catalog=catalog,
        safe=safe,
        output=output,
        worker=worker,
    )

    assert target.main(args) == 0
    dry_run = json.loads(capsys.readouterr().out)
    assert dry_run["mode"] == "dry_run"
    assert dry_run["planned_material_count"] == 2
    assert not output.exists()
    assert not (workspace / ".fake_worker_calls").exists()

    assert target.main([*args, "--execute"]) == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["converted_success_count"] == 1
    assert summary["conversion_failure_count"] == 1
    assert summary["failure_material_ids"] == ["native-bad"]
    assert (workspace / ".fake_worker_calls").read_text().splitlines() == ["call"]
    assert source_hashes == {path: _sha256(path) for path in source_hashes}

    latest = json.loads((output / "catalogs" / "latest.json").read_text(encoding="utf-8"))
    derived_catalog = output / latest["catalog_path"]
    derived_rows = [json.loads(line) for line in derived_catalog.read_text().splitlines()]
    assert [row["material_id"] for row in derived_rows] == ["native-good"]
    row = derived_rows[0]
    blend = output / row["normalized_blend_path"]
    metadata_path = output / row["normalized_metadata_path"]
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    assert _sha256(blend) == row["sha256"]
    assert metadata["schema_version"] == NORMALIZED_PACKAGE_SCHEMA
    assert metadata["normalizer"]["shader_graph_policy"] == "native_baked_to_texture_set"
    assert metadata["derivation"]["safe_list_sha256"] == _sha256(safe)
    assert row["material_profile"] == "texture_set"
    assert row["runtime_enabled"] is True
    assert not list(output.glob("packages/**/native-bad/**"))

    strict = MaterialCatalog.from_jsonl(
        derived_catalog, library_root=output, strict_normalized=True
    )
    assert [record.material_id for record in strict.records] == ["native-good"]
    assert strict.records[0].runtime_enabled is True

    checkpoint = output / ".conversion" / "conversion_results.jsonl"
    checkpoint_rows = [json.loads(line) for line in checkpoint.read_text().splitlines()]
    assert {row["status"] for row in checkpoint_rows} == {"success", "failure"}
    assert next(row for row in checkpoint_rows if row["status"] == "success")["publisher"]

    first_catalog_sha = _sha256(derived_catalog)
    assert target.main([*args, "--execute", "--resume"]) == 0
    resumed = json.loads(capsys.readouterr().out)
    assert resumed["logical_snapshot_sha256"] == summary["logical_snapshot_sha256"]
    assert _sha256(derived_catalog) == first_catalog_sha
    assert (workspace / ".fake_worker_calls").read_text().splitlines() == ["call"]


def test_safe_join_rejects_package_hash_drift_before_output(tmp_path: Path) -> None:
    source_root, catalog, source_rows = _source_library(tmp_path, material_ids=("native-good",))
    safe = _safe_file(tmp_path, catalog, source_rows)
    safe_row = json.loads(safe.read_text(encoding="utf-8"))
    safe_row["package_sha256"] = "0" * 64
    safe.write_text(json.dumps(safe_row) + "\n", encoding="utf-8")
    output = tmp_path / "derived"

    with pytest.raises(ValueError, match="safe/source mismatch"):
        target.load_conversion_jobs(
            source_catalog=catalog,
            source_root=source_root,
            safe_jsonl=safe,
            workspace_root=tmp_path,
            output_root=output,
        )

    assert not output.exists()
