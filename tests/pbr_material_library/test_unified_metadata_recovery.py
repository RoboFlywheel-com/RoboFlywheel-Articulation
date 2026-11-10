# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import pytest

recovery = pytest.importorskip("pbr_material_library.tools.recover_unified_metadata", reason="optional frozen-library builder is distributed separately")


@pytest.fixture
def recovery_fixture_dir() -> Path:
    root = recovery.REPOSITORY_ROOT / "pbr_material_library" / ".build" / "pytest"
    root.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix="unified-metadata-recovery-", dir=root))
    try:
        yield path
    finally:
        shutil.rmtree(path)


def test_recovery_plan_uses_normalized_blend_and_surviving_textures(
    recovery_fixture_dir: Path,
) -> None:
    material_id = "fixture-material"
    material_key = hashlib.sha256(material_id.encode()).hexdigest()
    normalized_root = recovery_fixture_dir / "normalized"
    package = normalized_root / "packages" / "fixture" / material_key
    package.mkdir(parents=True)
    blend = package / "material.blend"
    metadata = package / "metadata.json"
    blend.write_bytes(b"normalized fixture")
    metadata.write_text(json.dumps({"material_id": material_id}), encoding="utf-8")
    normalized_catalog = normalized_root / "materials.jsonl"
    normalized_catalog.write_text(
        json.dumps(
            {
                "material_id": material_id,
                "normalized_blend_path": blend.relative_to(normalized_root).as_posix(),
                "normalized_metadata_path": metadata.relative_to(normalized_root).as_posix(),
                "sha256": recovery._sha256_file(blend),
                "texture_size_m": 1.0,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    snapshot = recovery_fixture_dir / "surviving-unified"
    reuse_dir = snapshot / "textures" / "by-id" / material_key[:2] / material_key
    reuse_dir.mkdir(parents=True)
    (reuse_dir / "base_color.png").write_bytes(b"surviving png placeholder")
    unified_catalog = snapshot / "catalog.json"
    unified_catalog.write_text(
        json.dumps({"materials": [{"material_id": material_id, "material_key": material_key}]}),
        encoding="utf-8",
    )

    items = recovery.plan_recovery(
        normalized_root=normalized_root,
        normalized_catalog=normalized_catalog,
        unified_catalog=unified_catalog,
        output_root=recovery_fixture_dir / "recovered",
    )

    assert len(items) == 1
    row = items[0].worker_row
    assert row["source_blend_path"] == blend.relative_to(recovery.REPOSITORY_ROOT).as_posix()
    assert row["source_metadata_sha256"] == recovery._sha256_file(metadata)
    assert row["reuse_texture_dir"] == reuse_dir.relative_to(recovery.REPOSITORY_ROOT).as_posix()
    assert items[0].output_dir != reuse_dir


def test_blender_worker_limit_is_eight() -> None:
    assert recovery._bounded_workers("8") == 8
    with pytest.raises((argparse.ArgumentTypeError, ValueError)):
        recovery._bounded_workers("9")
