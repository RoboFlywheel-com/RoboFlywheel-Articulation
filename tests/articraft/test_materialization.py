# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import hashlib
import json
import random
import struct
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from PIL import Image

from articraft import materialization
from articraft.appearance.retrieval import appearance_requests_from_model
from articraft.appearance.unified_runtime import (
    PHYSICS_FIELDS,
    UNIFIED_CATALOG_SCHEMA,
    UNIFIED_MATERIAL_SCHEMA,
    UNIFIED_POINTER_SCHEMA,
    UNIFIED_POOL_INDEX_SCHEMA,
    UNIFIED_POOL_SCHEMA,
    UNIFIED_RELEASE_SCHEMA,
    load_unified_material_library,
)
from sdk import AppearanceOnlySpec, Material

_AUTHORED_INERTIAL_XML = (
    '<inertial><origin xyz="0.11 -0.22 0.33" rpy="0.01 0.02 0.03" />'
    '<mass value="2.125" />'
    '<inertia ixx="1.1" ixy="0.12" ixz="0.13" iyy="1.2" iyz="0.23" izz="1.3" />'
    "</inertial>"
)


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _write_json(path: Path, value: object) -> str:
    payload = _json_bytes(value)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return hashlib.sha256(payload).hexdigest()


def _physics(density: float) -> dict[str, float]:
    return {
        "density_kg_m3": density,
        "youngs_modulus_pa": 2.0e11,
        "poissons_ratio": 0.3,
        "static_friction_coefficient": 0.6,
        "dynamic_friction_coefficient": 0.4,
        "restitution_coefficient": 0.1,
    }


def _write_png(path: Path, color: tuple[int, int, int, int]) -> dict[str, Any]:
    width, height = 2, 1
    image = Image.new("RGBA", (width, height), color)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")
    payload = path.read_bytes()
    decoded = b"RGBA\0" + struct.pack(">II", width, height) + image.tobytes()
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "decoded_pixel_sha256": hashlib.sha256(decoded).hexdigest(),
        "size_bytes": len(payload),
        "width": width,
        "height": height,
    }


def _material_record(
    snapshot: Path,
    *,
    material_id: str,
    material_class_id: str,
    color: tuple[int, int, int, int],
) -> dict[str, Any]:
    material_key = hashlib.sha256(material_id.encode("utf-8")).hexdigest()
    texture_relative = (
        Path("textures") / "by-id" / material_key[:2] / material_key / "base_color.png"
    )
    texture = snapshot / texture_relative
    texture_receipt = _write_png(texture, color)
    texture_sha = texture_receipt["sha256"]
    source_relative = texture_relative.parent / "source_maps" / "original.png"
    source_receipt = _write_png(snapshot / source_relative, color)
    return {
        "schema_version": UNIFIED_MATERIAL_SCHEMA,
        "material_id": material_id,
        "material_key": material_key,
        "material_class_id": material_class_id,
        "category_slug": material_class_id.split(".", 1)[0],
        "display_name": material_id,
        "provider": "test",
        "license": "cc0",
        "appearance": {
            "representation": "standard_pbr",
            "texture_runtime_enabled": True,
            "mapping_contract": {
                "profile": "canonical_metric_uv/v1",
                "coordinate_unit": "meter",
                "tile_size_m": 0.5,
                "normal_space": "tangent",
                "normal_convention": "opengl_tangent",
                "requires_uv": True,
            },
            "channels": {
                "base_color": {
                    "kind": "texture",
                    "path": texture_relative.as_posix(),
                    "sha256": texture_sha,
                    "colorspace": "sRGB",
                },
                "metallic": {"kind": "factor", "value": 0.2},
                "roughness": {"kind": "factor", "value": 0.4},
                "normal": {"kind": "none"},
            },
            "factors": {"ior": 1.5},
            "source_maps": [
                {
                    "active_graph": False,
                    "image_name": "original.png",
                    "path": source_relative.as_posix(),
                    "role": "source_only",
                    **source_receipt,
                }
            ],
            "files": [
                {
                    "kind": "standardized_map",
                    "role": "base_color",
                    "path": texture_relative.as_posix(),
                    "colorspace": "sRGB",
                    **texture_receipt,
                },
                {
                    "kind": "source_map",
                    "role": "source_only",
                    "path": source_relative.as_posix(),
                    "colorspace": "sRGB",
                    **source_receipt,
                },
            ],
        },
        "physics": {"values": _physics(7800.0)},
        "source": {"material_profile": "texture_set"},
    }


def _build_library(tmp_path: Path, *, png_fault: str | None = None) -> dict[str, Any]:
    root = tmp_path / "pbr_material_library"
    identity = {"fixture": "portable-runtime"}
    snapshot_sha = hashlib.sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    snapshot = root / "unified" / "snapshots" / snapshot_sha
    records = [
        _material_record(
            snapshot,
            material_id="metal-a",
            material_class_id="metal.brushed_steel",
            color=(180, 185, 190, 255),
        ),
        _material_record(
            snapshot,
            material_id="metal-b",
            material_class_id="metal.brushed_steel",
            color=(120, 125, 130, 255),
        ),
        _material_record(
            snapshot,
            material_id="plastic-a",
            material_class_id="plastic.hard",
            color=(40, 90, 180, 255),
        ),
    ]
    for record in records:
        file_row = record["appearance"]["files"][0]
        if png_fault == "corrupt":
            texture = snapshot / file_row["path"]
            texture.write_bytes(b"not-a-real-png")
            digest = hashlib.sha256(texture.read_bytes()).hexdigest()
            file_row["sha256"] = digest
            file_row["size_bytes"] = texture.stat().st_size
            record["appearance"]["channels"]["base_color"]["sha256"] = digest
        elif png_fault == "dimension":
            file_row["width"] += 1
        elif png_fault == "decoded_hash":
            file_row["decoded_pixel_sha256"] = "0" * 64
        elif png_fault is not None:
            raise AssertionError(f"unknown PNG fixture fault: {png_fault}")
    records.sort(key=lambda row: row["material_id"])
    catalog_path = snapshot / "catalog.json"
    catalog_sha = _write_json(
        catalog_path,
        {
            "schema_version": UNIFIED_CATALOG_SCHEMA,
            "logical_snapshot_sha256": snapshot_sha,
            "identity": identity,
            "summary": {"material_count": len(records)},
            "materials": records,
        },
    )

    pool_entries: list[dict[str, Any]] = []
    pool_paths: dict[str, Path] = {}
    for class_id in ("metal.brushed_steel", "plastic.hard"):
        rows = [
            {"material_id": row["material_id"], "material_key": row["material_key"]}
            for row in records
            if row["material_class_id"] == class_id
        ]
        filename = hashlib.sha256(class_id.encode("utf-8")).hexdigest() + ".json"
        relative = Path("pools") / "by-class" / filename
        pool_path = snapshot / relative
        pool_sha = _write_json(
            pool_path,
            {
                "schema_version": UNIFIED_POOL_SCHEMA,
                "logical_snapshot_sha256": snapshot_sha,
                "material_class_id": class_id,
                "material_count": len(rows),
                "materials": rows,
            },
        )
        pool_paths[class_id] = pool_path
        pool_entries.append(
            {
                "material_class_id": class_id,
                "material_count": len(rows),
                "pool_path": relative.as_posix(),
                "pool_sha256": pool_sha,
                "pool_size_bytes": pool_path.stat().st_size,
            }
        )
    pool_index_path = snapshot / "pools" / "index.json"
    pool_index_sha = _write_json(
        pool_index_path,
        {
            "schema_version": UNIFIED_POOL_INDEX_SCHEMA,
            "logical_snapshot_sha256": snapshot_sha,
            "material_count": len(records),
            "class_count": len(pool_entries),
            "pools": pool_entries,
        },
    )
    manifest_path = snapshot / "manifest.json"
    manifest_sha = _write_json(
        manifest_path,
        {
            "schema_version": UNIFIED_RELEASE_SCHEMA,
            "logical_snapshot_sha256": snapshot_sha,
            "identity": identity,
            "files": {
                "catalog": {"path": "catalog.json", "sha256": catalog_sha},
                "pool_index": {"path": "pools/index.json", "sha256": pool_index_sha},
            },
        },
    )
    pointer = root / "unified" / "latest.json"
    _write_json(
        pointer,
        {
            "schema_version": UNIFIED_POINTER_SCHEMA,
            "logical_snapshot_sha256": snapshot_sha,
            "snapshot_path": f"unified/snapshots/{snapshot_sha}",
            "manifest_path": f"unified/snapshots/{snapshot_sha}/manifest.json",
            "manifest_sha256": manifest_sha,
            "catalog_path": f"unified/snapshots/{snapshot_sha}/catalog.json",
            "catalog_sha256": catalog_sha,
            "pool_index_path": f"unified/snapshots/{snapshot_sha}/pools/index.json",
            "pool_index_sha256": pool_index_sha,
        },
    )
    return {
        "pointer": pointer,
        "snapshot": snapshot,
        "catalog": catalog_path,
        "pool_paths": pool_paths,
        "records": records,
    }


def _fake_model() -> object:
    steel = Material(name="shared_steel", rgba=(0.3, 0.3, 0.3, 1.0))
    screen = Material(
        name="screen",
        rgba=(0.1, 0.2, 0.3, 0.75),
        texture="assets/textures/screen.png",
    )
    visuals = [
        SimpleNamespace(
            name="shell_a",
            material=steel,
            material_class_id="metal.brushed_steel",
            appearance_only=None,
        ),
        SimpleNamespace(
            name="shell_b",
            material=steel,
            material_class_id="metal.brushed_steel",
            appearance_only=None,
        ),
        SimpleNamespace(
            name="display",
            material=screen,
            material_class_id=None,
            appearance_only=AppearanceOnlySpec(
                kind="screen",
                alpha_mode="blend",
                emission_color=(0.2, 0.4, 0.8),
                emission_strength=2.0,
                text="READY",
                uv_offset=(0.1, 0.2),
                uv_scale=(0.8, 0.7),
                uv_rotation_rad=0.25,
            ),
        ),
    ]
    return SimpleNamespace(parts=[SimpleNamespace(name="body", visuals=visuals)], materials=[])


def _fake_compile(**kwargs: Any) -> materialization._CompiledSeed:
    workspace = Path(kwargs["workspace"])
    (workspace / "assets" / "meshes").mkdir(parents=True)
    (workspace / "assets" / "textures").mkdir(parents=True)
    (workspace / "assets" / "meshes" / "body.obj").write_text(
        "v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n",
        encoding="utf-8",
    )
    (workspace / "assets" / "textures" / "screen.png").write_bytes(b"screen-png")
    urdf = f"""<robot name="fixture">
  <material name="screen"><texture filename="assets/textures/screen.png" /></material>
  <link name="body">
    {_AUTHORED_INERTIAL_XML}
    <visual name="shell_a"><geometry><mesh filename="assets/meshes/body.obj" /></geometry></visual>
  </link>
</robot>"""
    return materialization._CompiledSeed(object_model=_fake_model(), urdf_xml=urdf)


def test_ordinary_compile_keeps_exact_collisions_and_authored_inertial(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    object_model = object()
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        "agent.compiler.load_model_globals",
        lambda _script, sdk_package: {"object_model": object_model},
    )

    def fake_urdf_compile(model: object, **kwargs: object) -> str:
        captured["model"] = model
        captured.update(kwargs)
        return f'<robot name="fixture"><link name="body">{_AUTHORED_INERTIAL_XML}</link></robot>'

    monkeypatch.setattr(
        "sdk.v0._urdf_export.compile_object_to_urdf_xml",
        fake_urdf_compile,
    )
    compiled = materialization._compile_ordinary_model(
        slug="turntable",
        stem="turntable",
        seed=1,
        workspace=tmp_path / "compile",
    )

    assert captured["model"] is object_model
    assert captured["include_physical_collisions"] is True
    assert captured["validate"] is True
    assert _AUTHORED_INERTIAL_XML in compiled.urdf_xml
    inertial = ET.fromstring(compiled.urdf_xml).find("./link/inertial")
    assert inertial is not None
    inertial.tail = None
    assert ET.tostring(inertial, encoding="unicode") == _AUTHORED_INERTIAL_XML


def test_ordinary_compile_wraps_generator_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_model(_script: Path, *, sdk_package: str) -> dict[str, object]:
        raise RuntimeError(f"invalid model for {sdk_package}")

    monkeypatch.setattr("agent.compiler.load_model_globals", fail_model)

    with pytest.raises(materialization.AssetExportError, match="failed to compile"):
        materialization._compile_ordinary_model(
            slug="turntable",
            stem="turntable",
            seed=1,
            workspace=tmp_path / "compile",
        )


def test_unified_loader_keeps_class_pools_and_pngs_lazy(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _build_library(tmp_path)
    unrequested = fixture["pool_paths"]["plastic.hard"].resolve()
    original_open = Path.open

    def tracked_open(path: Path, *args: object, **kwargs: object):
        if Path(path).resolve() == unrequested:
            raise AssertionError("unrequested pool was opened")
        if Path(path).suffix == ".png":
            raise AssertionError("PNG payload was opened during pool loading")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", tracked_open)
    library = load_unified_material_library(fixture["pointer"])
    pool = library.load_pool("metal.brushed_steel")

    assert [row.material_id for row in pool] == ["metal-a", "metal-b"]


@pytest.mark.parametrize(
    ("png_fault", "error"),
    [
        ("corrupt", "not a decodable PNG"),
        ("dimension", "declared dimensions"),
        ("decoded_hash", "decoded pixel SHA mismatch"),
    ],
)
def test_unified_texture_source_structurally_validates_png_receipt(
    tmp_path: Path,
    png_fault: str,
    error: str,
) -> None:
    fixture = _build_library(tmp_path, png_fault=png_fault)
    library = load_unified_material_library(fixture["pointer"])
    material = library.load_pool("metal.brushed_steel")[0]
    file_row = material.appearance["files"][0]

    with pytest.raises(ValueError, match=error):
        library.texture_source(material, file_row["path"], file_row["sha256"])


def test_unified_loader_rejects_catalog_sha_mismatch(tmp_path: Path) -> None:
    fixture = _build_library(tmp_path)
    fixture["catalog"].write_bytes(fixture["catalog"].read_bytes() + b" ")

    with pytest.raises(ValueError, match="catalog SHA mismatch"):
        load_unified_material_library(fixture["pointer"])


def test_unified_loader_rejects_pool_symlink_escape(tmp_path: Path) -> None:
    fixture = _build_library(tmp_path)
    pool = fixture["pool_paths"]["metal.brushed_steel"]
    outside = tmp_path / "outside-pool.json"
    outside.write_bytes(pool.read_bytes())
    pool.unlink()
    pool.symlink_to(outside)

    with pytest.raises(ValueError, match="escapes or is missing"):
        load_unified_material_library(fixture["pointer"])


def test_export_assets_writes_portable_tree_and_null_appearance_only_physics(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _build_library(tmp_path)
    repo_root = Path(__file__).resolve().parents[2]

    def forbidden_lock(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("legacy appearance lock/receipt path was touched")

    monkeypatch.setattr(
        "articraft.appearance.lock.materialize_appearance_lock",
        forbidden_lock,
    )
    paths = materialization.export_template_assets(
        repo_root=repo_root,
        slug="turntable",
        stem="turntable",
        seeds=[7],
        out_root=tmp_path / "exports",
        material_seed=19,
        library_pointer=fixture["pointer"],
        _compile_seed=_fake_compile,
    )

    seed = paths[0]
    assert seed == tmp_path / "exports" / "turntable" / "seed_7"
    model_urdf = (seed / "model.urdf").read_text(encoding="utf-8")
    assert _AUTHORED_INERTIAL_XML in model_urdf
    inertial = ET.fromstring(model_urdf).find("./link/inertial")
    assert inertial is not None
    inertial.tail = None
    assert ET.tostring(inertial, encoding="unicode") == _AUTHORED_INERTIAL_XML
    assert (seed / "assets" / "meshes" / "body.obj").is_file()
    assert not (seed / "model.py").exists()
    assert not list(seed.rglob("*.blend"))

    appearance = json.loads((seed / "appearance.json").read_text(encoding="utf-8"))
    physics = json.loads((seed / "physics.json").read_text(encoding="utf-8"))
    physical = [row for row in appearance["bindings"] if not row["appearance_only"]]
    overlay = next(row for row in appearance["bindings"] if row["appearance_only"])
    assert len(physical) == 2
    assert physical[0]["material"]["material_id"] == physical[1]["material"]["material_id"]
    assert physical[0]["selection"] == physical[1]["selection"]
    assert physical[0]["selection"]["algorithm"] == "local-random-choice/v1"
    assert physical[0]["selection"]["draw_order"] == 0
    assert physical[0]["selection"]["selection_index"] in {0, 1}
    assert "selection_key_sha256" not in physical[0]["selection"]
    assert physical[0]["appearance"]["mapping_contract"]["profile"] == ("canonical_metric_uv/v1")
    texture_path = seed / physical[0]["appearance"]["channels"]["base_color"]["path"]
    assert texture_path.is_file()
    assert texture_path.parent.name.startswith("mat_")
    assert "source_maps" not in physical[0]["appearance"]
    assert "standardized_maps" not in physical[0]["appearance"]
    assert {row["kind"] for row in physical[0]["appearance"]["files"]} == {"standardized_map"}
    assert not list(seed.rglob("source_maps"))
    assert len(list((seed / "assets" / "textures").glob("mat_*"))) == 1
    assert appearance["authoritative"] is True
    assert overlay["material"] is None
    assert overlay["appearance"]["spec"]["kind"] == "screen"
    assert overlay["appearance"]["spec"]["text"] == "READY"
    assert overlay["appearance"]["rgba"] == [0.1, 0.2, 0.3, 0.75]
    assert overlay["appearance"]["texture"]["path"] == "assets/textures/screen.png"

    by_surface = {row["surface_key"]: row for row in physics["bindings"]}
    display = by_surface["body::display"]
    assert list(display["values"]) == sorted(PHYSICS_FIELDS)
    assert all(value is None for value in display["values"].values())
    assert by_surface["body::shell_a"]["values"]["density_kg_m3"] == 7800.0
    assert set(by_surface["body::shell_a"]["values"]) == set(PHYSICS_FIELDS)


def test_export_assets_fails_existing_target_before_library_or_compile(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    target = tmp_path / "exports" / "turntable" / "seed_3"
    target.mkdir(parents=True)

    def forbidden(*_args: object, **_kwargs: object):
        raise AssertionError("work started before target preflight")

    with pytest.raises(FileExistsError, match="already exists"):
        materialization.export_template_assets(
            repo_root=repo_root,
            slug="turntable",
            stem="turntable",
            seeds=[3],
            out_root=tmp_path / "exports",
            _compile_seed=forbidden,
            _load_library=forbidden,
        )


@pytest.mark.parametrize("linked_name", ["turntable", ".staging"])
def test_export_assets_rejects_symlink_output_ancestor_before_work(
    tmp_path: Path,
    linked_name: str,
) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    output = tmp_path / "exports"
    outside = tmp_path / "outside"
    output.mkdir()
    outside.mkdir()
    (output / linked_name).symlink_to(outside, target_is_directory=True)

    def forbidden(*_args: object, **_kwargs: object):
        raise AssertionError("work started before output ancestor preflight")

    with pytest.raises(materialization.AssetExportError, match="must not be a symlink"):
        materialization.export_template_assets(
            repo_root=repo_root,
            slug="turntable",
            stem="turntable",
            seeds=[3],
            out_root=output,
            _compile_seed=forbidden,
            _load_library=forbidden,
        )

    assert not (outside / "seed_3").exists()


def test_export_assets_rejects_symlink_output_root_before_work(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    outside = tmp_path / "outside"
    output_link = tmp_path / "exports"
    outside.mkdir()
    output_link.symlink_to(outside, target_is_directory=True)

    def forbidden(*_args: object, **_kwargs: object):
        raise AssertionError("work started before output root preflight")

    with pytest.raises(
        materialization.AssetExportError,
        match="must not contain symlink components",
    ):
        materialization.export_template_assets(
            repo_root=repo_root,
            slug="turntable",
            stem="turntable",
            seeds=[3],
            out_root=output_link,
            _compile_seed=forbidden,
            _load_library=forbidden,
        )

    assert not (outside / "turntable").exists()


def test_bad_png_sha_leaves_no_partial_seed(tmp_path: Path) -> None:
    fixture = _build_library(tmp_path)
    for record in fixture["records"]:
        if record["material_class_id"] == "metal.brushed_steel":
            texture = fixture["snapshot"] / record["appearance"]["files"][0]["path"]
            texture.write_bytes(b"x" * texture.stat().st_size)
    repo_root = Path(__file__).resolve().parents[2]

    with pytest.raises(ValueError, match="texture SHA mismatch"):
        materialization.export_template_assets(
            repo_root=repo_root,
            slug="turntable",
            stem="turntable",
            seeds=[4],
            out_root=tmp_path / "exports",
            library_pointer=fixture["pointer"],
            _compile_seed=_fake_compile,
        )

    assert not (tmp_path / "exports" / "turntable" / "seed_4").exists()


def test_seed_tree_rejects_corrupt_pbr_png_even_with_matching_byte_receipts(
    tmp_path: Path,
) -> None:
    fixture = _build_library(tmp_path)
    repo_root = Path(__file__).resolve().parents[2]
    seed = materialization.export_template_assets(
        repo_root=repo_root,
        slug="turntable",
        stem="turntable",
        seeds=[4],
        out_root=tmp_path / "exports",
        library_pointer=fixture["pointer"],
        _compile_seed=_fake_compile,
    )[0]
    appearance_path = seed / "appearance.json"
    appearance = json.loads(appearance_path.read_text(encoding="utf-8"))
    asset_row = next(row for row in appearance["assets"]["textures"] if row.get("kind"))
    texture_path = seed / asset_row["path"]
    texture_path.write_bytes(b"not-a-real-png")
    digest = hashlib.sha256(texture_path.read_bytes()).hexdigest()
    asset_row["sha256"] = digest
    asset_row["size_bytes"] = texture_path.stat().st_size
    for binding in appearance["bindings"]:
        if binding["appearance_only"]:
            continue
        for file_row in binding["appearance"]["files"]:
            if file_row["path"] == asset_row["path"]:
                file_row["sha256"] = digest
                file_row["size_bytes"] = texture_path.stat().st_size
        for channel in binding["appearance"]["channels"].values():
            if isinstance(channel, dict) and channel.get("path") == asset_row["path"]:
                channel["sha256"] = digest
    _write_json(appearance_path, appearance)

    with pytest.raises(materialization.AssetExportError, match="not a decodable PNG"):
        materialization._validate_seed_tree(seed)


def test_later_seed_failure_publishes_no_earlier_seed(tmp_path: Path) -> None:
    fixture = _build_library(tmp_path)
    repo_root = Path(__file__).resolve().parents[2]

    def fail_second(**kwargs: Any) -> materialization._CompiledSeed:
        if kwargs["seed"] == 5:
            raise materialization.AssetExportError("second seed failed")
        return _fake_compile(**kwargs)

    with pytest.raises(materialization.AssetExportError, match="second seed failed"):
        materialization.export_template_assets(
            repo_root=repo_root,
            slug="turntable",
            stem="turntable",
            seeds=[4, 5],
            out_root=tmp_path / "exports",
            library_pointer=fixture["pointer"],
            _compile_seed=fail_second,
        )

    assert not (tmp_path / "exports" / "turntable" / "seed_4").exists()
    assert not (tmp_path / "exports" / "turntable" / "seed_5").exists()


def test_material_selection_uses_the_supplied_local_rng_directly(tmp_path: Path) -> None:
    fixture = _build_library(tmp_path)
    library = load_unified_material_library(fixture["pointer"])
    request = appearance_requests_from_model(_fake_model())[0]
    rng = random.Random(23)
    global_state = random.getstate()
    selected = materialization.select_material(
        library,
        request,
        rng=rng,
        draw_order=0,
    )
    assert random.getstate() == global_state
    candidates = library.load_pool("metal.brushed_steel")
    expected = random.Random(23).choice(candidates)

    assert selected.material == expected
    assert selected.material_class_id == "metal.brushed_steel"
    assert selected.selection_group_key == "material:shared_steel"
    assert selected.draw_order == 0
    assert selected.selection_index == candidates.index(expected)
    assert selected.pool_sha256 == library.pool_sha256("metal.brushed_steel")
    assert not hasattr(selected, "selection_key_sha256")
