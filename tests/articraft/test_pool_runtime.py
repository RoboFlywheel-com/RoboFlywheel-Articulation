# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest

from articraft.appearance import (
    POINTER_SCHEMA,
    POOL_INDEX_SCHEMA,
    POOL_SCHEMA,
    RELEASE_SCHEMA,
    load_material_pools,
)


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_json(path: Path, value: object) -> str:
    payload = _json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def _material_row(material_id: str, material_class_id: str) -> dict[str, Any]:
    category = material_class_id.split(".", 1)[0]
    package = f"packages/{category}/{material_id}"
    return {
        "asset_base_id": material_id,
        "blend_path": f"{package}/material.blend",
        "blend_sha256": hashlib.sha256(f"blend:{material_id}".encode()).hexdigest(),
        "blend_size_bytes": 123,
        "category_slug": category,
        "display_name": material_id,
        "license": "cc_zero",
        "mapping_profile": "metric_uv_tangent",
        "material_class_id": material_class_id,
        "material_id": material_id,
        "material_profile": "texture_set",
        "metadata_path": f"{package}/metadata.json",
        "metadata_sha256": hashlib.sha256(f"metadata:{material_id}".encode()).hexdigest(),
        "metadata_size_bytes": 45,
        "normal_space": "tangent",
        "provider": "test",
        "requires_uv": True,
        "texture_size_m": 0.5,
        "physics_ref": {
            "schema_version": "articraft-pbr-material-physics-ref/v1",
            "path": f"physics/by-id/{material_id}.json",
            "sha256": hashlib.sha256(f"physics:{material_id}".encode()).hexdigest(),
            "risk_tier": "low",
            "reference_conditions_id": "dry-steel-23c-v1",
        },
    }


def _build_library(
    tmp_path: Path,
    *,
    snapshot_dir_name: str | None = None,
) -> tuple[Path, Path, Path]:
    root = tmp_path / "pbr_material_library"
    identity = {"purpose": "direct-pool-runtime-test"}
    logical_sha = hashlib.sha256(
        json.dumps(identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    snapshot = root / "snapshots" / (snapshot_dir_name or logical_sha)

    classes = {
        "metal.brushed_steel": [
            _material_row("brushed-a", "metal.brushed_steel"),
            _material_row("brushed-b", "metal.brushed_steel"),
        ],
        "plastic.hard": [_material_row("plastic-a", "plastic.hard")],
    }
    pool_entries: list[dict[str, Any]] = []
    pool_paths: dict[str, Path] = {}
    for material_class_id, materials in classes.items():
        pool_relative = Path("pools/by-class") / f"{material_class_id}.json"
        pool_path = snapshot / pool_relative
        pool_sha = _write_json(
            pool_path,
            {
                "schema_version": POOL_SCHEMA,
                "policy_version": "exact-material-class-pool/v1",
                "material_class_id": material_class_id,
                "parent_category": material_class_id.split(".", 1)[0],
                "material_count": len(materials),
                "materials": materials,
            },
        )
        pool_paths[material_class_id] = pool_path
        pool_entries.append(
            {
                "material_class_id": material_class_id,
                "parent_category": material_class_id.split(".", 1)[0],
                "material_count": len(materials),
                "pool_path": pool_relative.as_posix(),
                "pool_sha256": pool_sha,
                "pool_size_bytes": pool_path.stat().st_size,
            }
        )

    pool_index_path = snapshot / "pools/index.json"
    pool_index_sha = _write_json(
        pool_index_path,
        {
            "schema_version": POOL_INDEX_SCHEMA,
            "policy_version": "exact-material-class-pool/v1",
            "logical_snapshot_sha256": logical_sha,
            "material_count": 3,
            "class_count": 2,
            "nonempty_class_count": 2,
            "empty_class_count": 0,
            "pools": pool_entries,
        },
    )
    physics_index_path = snapshot / "physics/index.json"
    physics_index_sha = _write_json(
        physics_index_path,
        {
            "schema_version": "articraft-pbr-material-physics-index/v1",
            "logical_snapshot_sha256": logical_sha,
            "annotation_run_sha256": "9" * 64,
            "material_count": 3,
            "risk_tier_counts": {"low": 3},
            "materials": [],
        },
    )
    manifest_path = snapshot / "manifest.json"
    manifest_sha = _write_json(
        manifest_path,
        {
            "schema_version": RELEASE_SCHEMA,
            "logical_snapshot_sha256": logical_sha,
            "identity": identity,
            "files": {
                "pool_index": {
                    "path": "pools/index.json",
                    "sha256": pool_index_sha,
                    "size_bytes": pool_index_path.stat().st_size,
                    "row_count": 2,
                },
                "physics_index": {
                    "path": "physics/index.json",
                    "sha256": physics_index_sha,
                    "size_bytes": physics_index_path.stat().st_size,
                    "row_count": 3,
                },
            },
        },
    )
    pointer = root / "latest.json"
    _write_json(
        pointer,
        {
            "schema_version": POINTER_SCHEMA,
            "logical_snapshot_sha256": logical_sha,
            "snapshot_path": snapshot.relative_to(root).as_posix(),
            "manifest_path": manifest_path.relative_to(root).as_posix(),
            "manifest_sha256": manifest_sha,
            "pool_index_path": pool_index_path.relative_to(root).as_posix(),
            "pool_index_sha256": pool_index_sha,
            "physics_index_path": physics_index_path.relative_to(root).as_posix(),
            "physics_index_sha256": physics_index_sha,
        },
    )
    return pointer, pool_paths["metal.brushed_steel"], pool_paths["plastic.hard"]


def test_load_material_pools_reads_only_requested_pool_and_no_packages(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pointer, requested_pool, unrequested_pool = _build_library(tmp_path)
    original_open = Path.open
    opened: list[Path] = []

    def tracked_open(path: Path, *args: object, **kwargs: object):
        current = Path(path).absolute()
        opened.append(current)
        if current == unrequested_pool.absolute():
            raise AssertionError("runtime opened an unrequested material pool")
        if current.suffix == ".blend":
            raise AssertionError("runtime opened or hashed a material package")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", tracked_open)

    loaded = load_material_pools(pointer, ["metal.brushed_steel"])

    assert set(loaded.pools) == {"metal.brushed_steel"}
    assert [row.material_id for row in loaded.pools["metal.brushed_steel"]] == [
        "brushed-a",
        "brushed-b",
    ]
    assert requested_pool.absolute() in opened
    assert unrequested_pool.absolute() not in opened
    assert not any(path.suffix == ".blend" for path in opened)
    assert not loaded.pools["metal.brushed_steel"][0].blend_path.exists()


def test_load_material_pools_accepts_stable_current_directory(tmp_path: Path) -> None:
    pointer, _requested_pool, _unrequested_pool = _build_library(
        tmp_path,
        snapshot_dir_name="current",
    )

    loaded = load_material_pools(pointer, ["plastic.hard"])

    assert loaded.snapshot_root.name == "current"
    assert set(loaded.pools) == {"plastic.hard"}


def test_load_material_pools_rejects_removed_v1_pointer_schema(tmp_path: Path) -> None:
    pointer, _requested_pool, _unrequested_pool = _build_library(tmp_path)
    value = json.loads(pointer.read_text(encoding="utf-8"))
    value["schema_version"] = "articraft-pbr-material-library-pointer/v1"
    _write_json(pointer, value)

    with pytest.raises(ValueError, match="pointer schema mismatch"):
        load_material_pools(pointer, ["metal.brushed_steel"])
