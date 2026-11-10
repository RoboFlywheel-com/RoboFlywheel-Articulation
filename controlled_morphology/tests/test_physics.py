# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from articraft.appearance.unified_runtime import PHYSICS_FIELDS
from controlled_morphology.generators import single_drawer_cabinet as drawer
from controlled_morphology.physics import build_physics_payload
from controlled_morphology.pipeline import run_pipeline

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def isolated_physics_library(monkeypatch):
    """Exercise binding independently of the separately distributed material library."""
    values = dict(zip(PHYSICS_FIELDS, (7800.0, 2e11, 0.3, 0.6, 0.4, 0.1), strict=True))

    def pool(class_id):
        return [
            SimpleNamespace(
                material_id=f"fixture-{class_id}", material_key="a" * 64, physics_values=values
            )
        ]

    library = SimpleNamespace(
        load_pool=pool,
        pool_sha256=lambda _: "b" * 64,
        catalog_sha256="c" * 64,
        manifest_sha256="d" * 64,
        pointer_sha256="e" * 64,
        pool_index_sha256="f" * 64,
        snapshot_sha256="0" * 64,
    )
    monkeypatch.setattr("controlled_morphology.physics._load_library", lambda _: library)


def test_physics_payload_is_complete_and_deterministic_by_class():
    model = drawer.build_single_drawer_cabinet(drawer.Config())
    payload = build_physics_payload(model, model_urdf_sha256="0" * 64)

    assert payload["mode"] == "physics_only"
    assert payload["appearance_materialized"] is False
    assert payload["fields"] == list(PHYSICS_FIELDS)
    assert payload["bindings"]
    assert all(set(row["values"]) == set(PHYSICS_FIELDS) for row in payload["bindings"])

    material_by_class: dict[str, set[str]] = {}
    for binding in payload["bindings"]:
        material_by_class.setdefault(binding["material_class_id"], set()).add(
            binding["material_id"]
        )
    assert all(len(material_ids) == 1 for material_ids in material_by_class.values())
    assert all("appearance" not in binding for binding in payload["bindings"])
    assert "texture" not in json.dumps(payload).lower()


def test_pipeline_writes_physics_without_pbr_materials(tmp_path: Path):
    source = json.loads((ROOT / "specs" / "drawer_p1_joint_range.json").read_text())
    source["name"] = "physics_only_test"
    source["axes"][0]["levels"] = [0.48]
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(source), encoding="utf-8")

    result = run_pipeline(spec_path, tmp_path / "out")

    assert result.ok
    asset_dir = next((result.output_root / "assets").glob("*/*"))
    physics_path = asset_dir / "physics.json"
    assert physics_path.is_file()
    assert not (asset_dir / "appearance.json").exists()
    assert not (asset_dir / "assets" / "textures").exists()
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["assets"][0]["hashes"]["physics_json"]
