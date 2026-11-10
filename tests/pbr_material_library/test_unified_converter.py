# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from copy import deepcopy
from pathlib import Path

import pytest
from PIL import Image

builder = pytest.importorskip("pbr_material_library.tools.build_unified_catalog", reason="optional frozen-library builder is distributed separately")

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BPY_PYTHON = REPOSITORY_ROOT / ".cache" / "bpy-5.2-venv" / "bin" / "python"
FIXTURE_BUILDER = Path(__file__).with_name("_bpy_make_unified_fixture.py")
WORKER = REPOSITORY_ROOT / "pbr_material_library" / "tools" / "_bpy_export_unified_materials.py"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _export_fixture_once(
    source: builder.SourceMaterial,
    build_root: Path,
) -> dict[str, object]:
    payload = {
        "schema_version": builder.JOB_SCHEMA,
        "exporter_version": builder.EXPORTER_VERSION,
        "workspace_root": str(REPOSITORY_ROOT),
        "materials": [builder._worker_row(build_root, source, resolution=1024)],
    }
    completed = subprocess.run(
        (str(BPY_PYTHON), str(WORKER)),
        cwd=REPOSITORY_ROOT,
        input=json.dumps(payload),
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert completed.returncode == 0, completed.stderr
    rows = [
        json.loads(line[len(builder.RESULT_PREFIX) :])
        for line in completed.stdout.splitlines()
        if line.startswith(builder.RESULT_PREFIX)
    ]
    assert len(rows) == 1
    result = rows[0]
    assert result["status"] == "success", result["failure_reasons"]
    builder._attach_decoded_hashes(result, source, build_root)
    builder._validate_result(result, source, build_root, verify_hashes=True)
    return result


def _estimate(value: float) -> dict[str, object]:
    return {
        "applicability": "fixture",
        "basis": "fixture",
        "confidence": 1.0,
        "high": value,
        "low": value,
        "value": value,
    }


@pytest.fixture
def workspace_fixture_dir() -> Path:
    root = REPOSITORY_ROOT / "pbr_material_library" / ".build" / "pytest"
    root.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix="unified-converter-", dir=root))
    try:
        yield path
    finally:
        shutil.rmtree(path)


def test_unified_physics_sidecar_is_local_and_matches_six_values(
    workspace_fixture_dir: Path,
) -> None:
    material_id = "fixture-material"
    class_id = "fixture.class"
    material_key = hashlib.sha256(material_id.encode()).hexdigest()
    values = {
        "density_kg_m3": 1000.0,
        "youngs_modulus_pa": 1_000_000.0,
        "poissons_ratio": 0.3,
        "static_friction_coefficient": 0.6,
        "dynamic_friction_coefficient": 0.5,
        "restitution_coefficient": 0.1,
    }
    estimates = {key: _estimate(value) for key, value in values.items()}
    quality = {"risk_tier": "low", "warnings": []}
    annotation_sha = "a" * 64
    sidecar = {
        "schema_version": builder.SOURCE_PHYSICS_SCHEMA,
        "material_id": material_id,
        "material_class_id": class_id,
        "source_material_class_id": class_id,
        "physics": values,
        "estimates": estimates,
        "reference_conditions_id": "fixture-conditions",
        "quality": quality,
        "provenance": {"annotation_run_sha256": annotation_sha},
    }
    relative = Path("physics") / "by-id" / material_key[:2] / f"{material_key}.json"
    path = workspace_fixture_dir / relative
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(sidecar, sort_keys=True), encoding="utf-8")
    row = {
        "material_id": material_id,
        "material_key": material_key,
        "material_class_id": class_id,
        "physics": {
            "values": values,
            "estimates": estimates,
            "reference_conditions_id": "fixture-conditions",
            "quality": quality,
            "source_ref": {
                "path": relative.as_posix(),
                "sha256": _sha256(path),
                "size_bytes": path.stat().st_size,
                "annotation_run_sha256": annotation_sha,
            },
        },
    }
    assert builder._validate_catalog_physics_sidecar(workspace_fixture_dir, row, set()) == (
        relative.as_posix(),
        _sha256(path),
        path.stat().st_size,
        material_id,
        class_id,
    )
    mismatched = deepcopy(row)
    mismatched["physics"]["values"]["density_kg_m3"] = 999.0
    with pytest.raises(ValueError, match="values disagree with sidecar"):
        builder._validate_catalog_physics_sidecar(workspace_fixture_dir, mismatched, set())


@pytest.mark.skipif(not BPY_PYTHON.is_file(), reason="pinned bpy 5.2 environment is unavailable")
def test_worker_exports_nested_active_graph_and_ignores_shader_closures(
    workspace_fixture_dir: Path,
) -> None:
    material_id = "fixture-material"
    source_dir = workspace_fixture_dir / "source"
    completed = subprocess.run(
        (str(BPY_PYTHON), str(FIXTURE_BUILDER), str(source_dir), material_id),
        cwd=REPOSITORY_ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr

    blend_path = source_dir / "material.blend"
    metadata_path = source_dir / "metadata.json"
    source = builder.SourceMaterial(
        material_id=material_id,
        material_key=hashlib.sha256(material_id.encode()).hexdigest(),
        material_class_id="fixture.class",
        runtime_record={
            "blend_sha256": _sha256(blend_path),
            "display_name": "Unified Fixture",
            "metadata_sha256": _sha256(metadata_path),
            "texture_size_m": 1.0,
        },
        metadata=json.loads(metadata_path.read_text(encoding="utf-8")),
        physics={},
        blend_path=blend_path,
        metadata_path=metadata_path,
        physics_path=metadata_path,
    )
    build_root = workspace_fixture_dir / "build-first"
    result = _export_fixture_once(source, build_root)
    assert result["audit"]["primary_surface"] is not None, json.dumps(
        result["audit"], sort_keys=True
    )
    assert result["appearance"]["standardized_maps"], json.dumps(
        result["appearance"], sort_keys=True
    )

    wrong_dimensions = deepcopy(result)
    wrong_dimensions["files"][0]["width"] += 1
    with pytest.raises(ValueError, match="decoded PNG dimensions mismatch"):
        builder._validate_result(wrong_dimensions, source, build_root, verify_hashes=True)
    incomplete_packed_coverage = deepcopy(result)
    incomplete_packed_coverage["audit"]["packed_image_count"] -= 1
    with pytest.raises(ValueError, match="packed image coverage mismatch"):
        builder._validate_result(incomplete_packed_coverage, source, build_root, verify_hashes=True)

    appearance = result["appearance"]
    audit = result["audit"]
    assert appearance["representation"] == "standard_pbr"
    assert audit["primary_surface"] == {
        "distance": 2,
        "kind": "principled",
        "node_path": "root/SurfaceGroup/Nested Principled",
    }
    assert {"light_path", "multi_bsdf", "volume"}.issubset(audit["ignored_shader_semantics"])
    assert "ior" in audit["ignored_inputs"]
    assert audit["displacement"] == {
        "connected": True,
        "height_source": "root/Output Height Displacement",
        "height_status": "baked",
        "tangent_normal": "primary_normal",
    }
    assert appearance["channels"]["metallic"]["kind"] == "factor"
    assert appearance["channels"]["metallic"]["value"] == pytest.approx(0.3, abs=1 / 255)
    assert appearance["channels"]["roughness"]["kind"] == "factor"
    assert appearance["channels"]["roughness"]["value"] == pytest.approx(0.4, abs=1 / 255)
    assert appearance["channels"]["emission_strength"]["kind"] == "factor"
    assert appearance["channels"]["emission_strength"]["value"] == pytest.approx(0.5, abs=1 / 255)
    assert {"emission_strength", "metallic", "roughness"}.issubset(audit["constant_channels"])
    assert "normal" not in audit["constant_channels"]

    standardized = appearance["standardized_maps"]
    assert {"ambient_occlusion", "base_color", "height", "normal"}.issubset(standardized)
    assert standardized["ambient_occlusion"]["colorspace"] == "Non-Color"
    assert standardized["height"]["colorspace"] == "Non-Color"
    assert not {
        "emission_strength.png",
        "metallic.png",
        "roughness.png",
        "ior.png",
        "transmission.png",
    } & {row["path"] for row in result["files"]}
    assert audit["packed_image_count"] == 5
    assert audit["source_only_image_count"] == 1
    base_source = next(
        row for row in appearance["source_maps"] if row["image_name"] == "Fixture Base Color"
    )
    assert base_source["active_graph"] is True
    assert base_source["node_paths"] == ["root/Outer Base Image"]
    orphan = next(row for row in appearance["source_maps"] if row["image_name"] == "Fixture Orphan")
    assert orphan["active_graph"] is False
    assert orphan["role"] == "source_only"

    decoded_by_path = {row["path"]: row["decoded_pixel_sha256"] for row in result["files"]}
    assert len(decoded_by_path) == len(result["files"])
    for row in [*appearance["source_maps"], *standardized.values()]:
        assert row["decoded_pixel_sha256"] == decoded_by_path[row["path"]]
        path = builder._material_output_dir(build_root, source) / row["path"]
        with Image.open(path) as image:
            image.verify()

    second_result = _export_fixture_once(source, workspace_fixture_dir / "build-second")
    assert builder._canonical_bytes(second_result) == builder._canonical_bytes(result)
    first_hashes = {
        row["path"]: (row["sha256"], row["decoded_pixel_sha256"]) for row in result["files"]
    }
    second_hashes = {
        row["path"]: (row["sha256"], row["decoded_pixel_sha256"]) for row in second_result["files"]
    }
    assert second_hashes == first_hashes
