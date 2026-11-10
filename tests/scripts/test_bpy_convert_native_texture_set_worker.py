# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from scripts import _bpy_convert_native_texture_set_worker as target

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
BPY_PYTHON = REPOSITORY_ROOT / ".cache" / "bpy-5.2-venv" / "bin" / "python"


@pytest.fixture
def workspace_tmp() -> Path:
    base = REPOSITORY_ROOT / ".artifacts" / "test_tmp" / "native_texture_converter"
    base.mkdir(parents=True, exist_ok=True)
    path = Path(tempfile.mkdtemp(prefix="case-", dir=base))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _raw_job(
    root: Path,
    source: Path,
    *,
    output: str = "outputs/derived",
    material_id: str = "test:constant-pbr",
) -> dict[str, object]:
    return {
        "material_id": material_id,
        "display_name": "Constant PBR",
        "category_slug": "metal",
        "source_blend_path": source.relative_to(root).as_posix(),
        "source_blend_sha256": _sha256(source),
        "output_dir": output,
        "texture_size_m": 1.0,
        "catalog_sha256": "a" * 64,
        "eligibility_input_sha256": "b" * 64,
        "eligibility_decision": target.SAFE_DECISION,
    }


def _safe_facts(**updates: object) -> dict[str, object]:
    facts: dict[str, object] = {
        "material_count": 1,
        "has_node_tree": True,
        "active_output_count": 1,
        "connected_surface_output_count": 1,
        "surface_terminal_type": "BSDF_PRINCIPLED",
        "procedural_texture_node_count": 0,
        "volume_link_count": 0,
        "displacement_link_count": 0,
        "animated_or_driven": False,
        "alpha_linked": False,
        "alpha_opaque": True,
        "emission_linked": False,
        "emission_nonzero": False,
        "unsupported_principled_inputs": [],
        "forbidden_linked_node_types": [],
        "complex_linked_node_types": [],
        "non_simple_standard_channel_sources": [],
        "normal_input_not_simple_tangent_normal_map": False,
        "unused_image_node_count": 0,
        "unpacked_image_count": 0,
        "nonstatic_image_count": 0,
        "nonflat_image_count": 0,
        "nonrepeat_image_count": 0,
        "non_uv_image_coordinate_count": 0,
    }
    facts.update(updates)
    return facts


def test_graph_failure_codes_accept_only_the_simple_contract() -> None:
    assert target.graph_failure_codes(_safe_facts()) == []


@pytest.mark.parametrize(
    ("updates", "reason"),
    (
        ({"procedural_texture_node_count": 1}, "procedural_texture_present"),
        ({"alpha_opaque": False}, "surface_not_opaque"),
        ({"emission_nonzero": True}, "emission_not_zero"),
        ({"unsupported_principled_inputs": ["IOR:linked"]}, "nonstandard_principled_input"),
        ({"complex_linked_node_types": ["MIX_RGB"]}, "complex_linked_node_graph"),
        (
            {"normal_input_not_simple_tangent_normal_map": True},
            "normal_input_not_simple_tangent_normal_map",
        ),
        ({"non_uv_image_coordinate_count": 1}, "source_image_coordinate_not_uv_or_unlinked"),
        ({"unused_image_node_count": 1}, "unused_or_ambiguous_image_node"),
    ),
)
def test_graph_failure_codes_reject_unsafe_or_complex_graphs(
    updates: dict[str, object], reason: str
) -> None:
    failures = target.graph_failure_codes(_safe_facts(**updates))

    assert reason in failures


@pytest.mark.parametrize(
    "value",
    ("/outside/material.blend", "../outside.blend", r"C:\outside.blend", "a/../../b"),
)
def test_safe_relative_path_rejects_escape(value: str) -> None:
    with pytest.raises(ValueError, match="safe POSIX"):
        target.safe_relative_path(value, field="test")


def test_prepare_job_uses_only_relative_provenance_in_its_digest(workspace_tmp: Path) -> None:
    source = workspace_tmp / "inputs" / "source.blend"
    source.parent.mkdir()
    source.write_bytes(b"BLENDER-test")
    raw = _raw_job(workspace_tmp, source)

    prepared = target.prepare_job(raw, workspace_tmp.resolve())

    assert prepared["source_blend_path"] == "inputs/source.blend"
    assert prepared["output_dir"] == "outputs/derived"
    assert str(workspace_tmp) not in prepared["conversion_input_sha256"]
    assert prepared["conversion_input_sha256"] == target.canonical_sha256(
        {
            "conversion_version": target.CONVERSION_VERSION,
            **{
                key: value
                for key, value in prepared.items()
                if not key.startswith("_") and key != "conversion_input_sha256"
            },
        }
    )


def test_metadata_is_strict_normalized_v1_and_uses_relative_paths(workspace_tmp: Path) -> None:
    source = workspace_tmp / "source.blend"
    source.write_bytes(b"BLENDER-test")
    job = target.prepare_job(_raw_job(workspace_tmp, source), workspace_tmp.resolve())
    channels = {
        channel: {
            "image_name": f"Articraft_{channel}_1K",
            "colorspace": "sRGB" if channel == "base_color" else "Non-Color",
            "packed": True,
            "png_sha256": str(index) * 64,
            "resolution": [1024, 1024],
        }
        for index, channel in enumerate(target.CHANNELS, 1)
    }
    qa = {"status": "pass", "channels": sorted(target.CHANNELS)}

    metadata = target._metadata(
        job,
        channel_rows=channels,
        blend_sha256="c" * 64,
        qa=qa,
        bpy_version="5.2.0",
    )

    assert metadata["schema_version"] == "articraft-normalized-material-package/v1"
    assert metadata["normalizer"]["version"] == "articraft-pbr-normalizer/v1"
    assert metadata["converter"]["version"] == target.CONVERSION_VERSION
    assert metadata["material_profile"] == "texture_set"
    assert metadata["package"]["blend_path"] == "outputs/derived/material.blend"
    assert metadata["mapping_contract"]["mapping_profile"] == "metric_uv_tangent"
    assert [row["role"] for row in metadata["channels"]] == list(target.CHANNELS)
    assert str(workspace_tmp) not in json.dumps(metadata)


def _create_source(path: Path, kind: str) -> None:
    script = """
import bpy
import sys
from pathlib import Path

bpy.ops.wm.read_factory_settings(use_empty=True)
material = bpy.data.materials.new("Constant PBR")
material.use_nodes = True
principled = material.node_tree.nodes.get("Principled BSDF")
principled.inputs["Base Color"].default_value = (0.18, 0.42, 0.68, 1.0)
principled.inputs["Metallic"].default_value = 0.35
principled.inputs["Roughness"].default_value = 0.6
principled.inputs["Alpha"].default_value = 1.0
kind = sys.argv[-2]
output_path = Path(sys.argv[-1])
if kind == "image":
    generated = bpy.data.images.new("Source Color Generated", width=16, height=16, alpha=True)
    generated.generated_color = (0.18, 0.42, 0.68, 1.0)
    png_path = output_path.with_suffix(".png")
    generated.filepath_raw = str(png_path)
    generated.file_format = "PNG"
    generated.save()
    bpy.data.images.remove(generated)
    image = bpy.data.images.load(str(png_path), check_existing=False)
    image.pack()
    coordinate = material.node_tree.nodes.new("ShaderNodeTexCoord")
    texture = material.node_tree.nodes.new("ShaderNodeTexImage")
    texture.image = image
    texture.projection = "FLAT"
    texture.extension = "REPEAT"
    material.node_tree.links.new(coordinate.outputs["UV"], texture.inputs["Vector"])
    material.node_tree.links.new(texture.outputs["Color"], principled.inputs["Base Color"])
elif kind == "procedural":
    noise = material.node_tree.nodes.new("ShaderNodeTexNoise")
    material.node_tree.links.new(noise.outputs["Color"], principled.inputs["Base Color"])
material.use_fake_user = True
bpy.ops.wm.save_as_mainfile(filepath=str(output_path), check_existing=False, compress=True)
"""
    completed = subprocess.run(
        (str(BPY_PYTHON), "-c", script, kind, str(path)),
        cwd=REPOSITORY_ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout


@pytest.mark.skipif(not BPY_PYTHON.is_file(), reason="workspace bpy 5.2 environment is missing")
def test_real_bpy_supported_types_and_batch_failure_isolation_smoke(workspace_tmp: Path) -> None:
    source = workspace_tmp / "inputs" / "constant.blend"
    image_source = workspace_tmp / "inputs" / "image.blend"
    procedural_source = workspace_tmp / "inputs" / "procedural.blend"
    source.parent.mkdir()
    _create_source(source, "constant")
    _create_source(image_source, "image")
    _create_source(procedural_source, "procedural")
    source_hashes = {path: _sha256(path) for path in (source, image_source, procedural_source)}
    payload = {
        "schema_version": target.JOB_SCHEMA,
        "conversion_version": target.CONVERSION_VERSION,
        "workspace_root": str(workspace_tmp),
        "materials": [
            _raw_job(workspace_tmp, source),
            _raw_job(
                workspace_tmp,
                image_source,
                output="outputs/image",
                material_id="test:image-pbr",
            ),
            _raw_job(
                workspace_tmp,
                procedural_source,
                output="outputs/procedural",
                material_id="test:procedural-pbr",
            ),
        ],
    }
    completed = subprocess.run(
        (
            str(BPY_PYTHON),
            str(REPOSITORY_ROOT / "scripts" / "_bpy_convert_native_texture_set_worker.py"),
        ),
        cwd=REPOSITORY_ROOT,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        timeout=300,
    )
    assert completed.returncode == 0, completed.stderr or completed.stdout
    result_lines = [
        line[len(target.RESULT_PREFIX) :]
        for line in completed.stdout.splitlines()
        if line.startswith(target.RESULT_PREFIX)
    ]
    assert len(result_lines) == 3, completed.stdout
    results = {row["material_id"]: row for row in map(json.loads, result_lines)}
    result = results["test:constant-pbr"]
    assert result["status"] == "success", result
    assert result["channels"] == list(target.CHANNELS)
    assert result["reopen_qa"]["status"] == "pass"
    assert result["reopen_qa"]["material_count"] == 1
    assert result["reopen_qa"]["material_fake_user"] is True
    assert result["reopen_qa"]["object_count"] == 0
    assert result["reopen_qa"]["unpacked_image_count"] == 0
    assert result["reopen_qa"]["displacement_link_count"] == 0
    assert results["test:image-pbr"]["status"] == "success"
    assert results["test:image-pbr"]["reopen_qa"]["status"] == "pass"
    assert results["test:procedural-pbr"]["status"] == "failure"
    assert "procedural_texture_present" in results["test:procedural-pbr"]["failure_codes"]
    assert all(_sha256(path) == digest for path, digest in source_hashes.items())

    output = workspace_tmp / "outputs" / "derived"
    assert {path.name for path in output.iterdir()} == {"material.blend", "metadata.json"}
    metadata = json.loads((output / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["schema_version"] == target.METADATA_SCHEMA
    assert metadata["normalizer"]["version"] == target.NORMALIZER_VERSION
    assert metadata["reopen_qa"]["channels"] == sorted(target.CHANNELS)
    assert str(workspace_tmp) not in json.dumps(metadata)
    image_output = workspace_tmp / "outputs" / "image"
    assert {path.name for path in image_output.iterdir()} == {"material.blend", "metadata.json"}
    assert not (workspace_tmp / "outputs" / "procedural").exists()
