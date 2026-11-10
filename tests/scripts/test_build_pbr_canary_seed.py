# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import sdk
from scripts import build_pbr_canary_seed as target
from sdk import AppearanceOnlySpec, Box, Material, Origin
from sdk._core.v0.assets import current_asset_session


class _Visual:
    def __init__(
        self,
        name: str,
        *,
        material_class_id: str | None = None,
        material: Material | None = None,
        appearance_only: AppearanceOnlySpec | None = None,
    ) -> None:
        self.name = name
        self.material_class_id = material_class_id
        self.material = material
        self.appearance_only = appearance_only
        self.geometry = Box((1.0, 1.0, 1.0))
        self.origin = Origin()


def test_requests_derive_exact_class_surface_identity_from_model() -> None:
    model = SimpleNamespace(
        parts=[
            SimpleNamespace(
                name="body",
                visuals=[_Visual("shell", material_class_id="plastic.opaque_generic")],
            )
        ]
    )

    requests = target.appearance_requests_from_model(model)

    assert len(requests) == 1
    request = requests[0]
    assert request.surface_key == "body::shell"
    assert request.material_class_id == "plastic.opaque_generic"


def test_write_json_is_deterministic(tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    target._write_json(output, {"z": 1, "a": ("x", "y")})
    first = output.read_bytes()
    target._write_json(output, {"a": ("x", "y"), "z": 1})

    assert output.read_bytes() == first
    assert json.loads(first) == {"a": ["x", "y"], "z": 1}


def test_unknown_template_is_rejected_before_import(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown template"):
        target._build_model("not-a-template", 0, target.AssetContext(tmp_path))


def test_build_model_activates_seed_asset_session(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: dict[str, object] = {}

    class _Model:
        def validate(self, *, strict: bool) -> None:
            assert strict is True

    def _build(config: dict[str, int], *, assets: target.AssetContext) -> _Model:
        session = current_asset_session()
        observed["session"] = session
        observed["assets"] = assets
        observed["mesh"] = sdk.mesh_from_geometry(
            sdk.BoxGeometry((0.1, 0.2, 0.3)),
            "managed_body",
        )
        assert config == {"seed": 7}
        return _Model()

    module = SimpleNamespace(
        __file__=__file__,
        config_from_seed=lambda seed: {"seed": seed},
        build_dummy=_build,
    )
    monkeypatch.setitem(target.TEMPLATE_REGISTRY, "dummy", "dummy")
    monkeypatch.setattr(target.importlib, "import_module", lambda _name: module)

    previous_session = current_asset_session()
    model, config, _source = target._build_model("dummy", 7, target.AssetContext(tmp_path))

    session = observed["session"]
    assert isinstance(session, target.AssetSession)
    assert session.asset_root == tmp_path.resolve()
    mesh = observed["mesh"]
    assert isinstance(mesh, sdk.Mesh)
    assert mesh.filename == "assets/meshes/managed_body.obj"
    assert (tmp_path / str(mesh.filename)).is_file()
    assert model.__class__ is _Model
    assert config == {"seed": 7}
    assert current_asset_session() is previous_session


def test_validate_urdf_mesh_assets_accepts_contained_files(tmp_path: Path) -> None:
    mesh = tmp_path / "assets" / "meshes" / "body.obj"
    mesh.parent.mkdir(parents=True)
    mesh.write_text("o body\n", encoding="utf-8")
    urdf = (
        "<robot name='x'><link name='body'><visual><geometry>"
        "<mesh filename='assets/meshes/body.obj'/>"
        "</geometry></visual></link></robot>"
    )

    resolved = target._validate_urdf_mesh_assets(urdf, tmp_path)

    assert resolved == (mesh.resolve(),)


def test_validate_urdf_mesh_assets_rejects_missing_file(tmp_path: Path) -> None:
    urdf = "<robot name='x'><mesh filename='assets/meshes/missing.obj'/></robot>"

    with pytest.raises(FileNotFoundError, match="missing from the seed"):
        target._validate_urdf_mesh_assets(urdf, tmp_path)


@pytest.mark.parametrize(
    "mesh_ref",
    (
        "/tmp/outside.obj",
        "../outside.obj",
        "assets/meshes/../../outside.obj",
        r"C:\\outside.obj",
        r"assets\\meshes\\body.obj",
    ),
)
def test_validate_urdf_mesh_assets_rejects_unsafe_paths(
    tmp_path: Path,
    mesh_ref: str,
) -> None:
    urdf = f"<robot name='x'><mesh filename='{mesh_ref}'/></robot>"

    with pytest.raises(ValueError, match="safe seed-relative path"):
        target._validate_urdf_mesh_assets(urdf, tmp_path)


def test_validate_urdf_mesh_assets_rejects_symlink_escape(tmp_path: Path) -> None:
    seed_root = tmp_path / "seed"
    mesh_dir = seed_root / "assets" / "meshes"
    mesh_dir.mkdir(parents=True)
    outside = tmp_path / "outside.obj"
    outside.write_text("o outside\n", encoding="utf-8")
    (mesh_dir / "body.obj").symlink_to(outside)
    urdf = "<robot name='x'><mesh filename='assets/meshes/body.obj'/></robot>"

    with pytest.raises(ValueError, match="escapes the seed root"):
        target._validate_urdf_mesh_assets(urdf, seed_root)


def test_standard_seed_does_not_emit_debug_geometry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    observed: dict[str, object] = {}
    model = SimpleNamespace(
        parts=[
            SimpleNamespace(
                name="body",
                visuals=[_Visual("shell", material_class_id="plastic.opaque_generic")],
            )
        ]
    )
    template_path = Path(__file__).resolve()
    fake_library = SimpleNamespace(
        pointer_sha256="pointer-sha",
        snapshot_root=tmp_path / "pbr_material_library" / "snapshots" / "release-sha",
        library_snapshot_sha256="release-sha",
        manifest_sha256="manifest-sha",
        pool_index_sha256="pool-index-sha",
        pools={"plastic.opaque_generic": ("candidate",)},
        pool_sha256={"plastic.opaque_generic": "pool-sha"},
    )

    def _load_pools(_path: Path, class_ids: set[str]) -> object:
        observed["loaded_class_ids"] = class_ids
        return fake_library

    monkeypatch.setattr(target, "load_material_pools", _load_pools)

    def _build_model(
        _slug: str,
        _seed: int,
        assets: target.AssetContext,
    ) -> tuple[object, dict[str, int], Path]:
        cache = assets.root / "assets" / ".cadquery_cache" / "duplicate.obj"
        cache.parent.mkdir(parents=True)
        cache.write_text("o duplicate\n", encoding="utf-8")
        return model, {"seed": 0}, template_path

    monkeypatch.setattr(target, "_build_model", _build_model)
    monkeypatch.setattr(
        target,
        "compile_object_to_urdf_xml",
        lambda *_args, **_kwargs: (
            "<robot name='x'><link name='body'><visual name='shell'><geometry>"
            "<box size='1 1 1'/></geometry></visual></link></robot>"
        ),
    )

    def _resolve(
        requests: list[object],
        pools: object,
        pool_sha256: object,
        **kwargs: object,
    ) -> tuple[()]:
        assert pools is fake_library.pools
        assert pool_sha256 is fake_library.pool_sha256
        observed["requests"] = [
            (getattr(row, "surface_key"), getattr(row, "material_class_id")) for row in requests
        ]
        observed["resolve_material_seed"] = kwargs.get("material_seed")
        return ()

    monkeypatch.setattr(target, "resolve_appearances_from_pools", _resolve)

    def _materialize_lock(seed_root: Path, *_args, **_kwargs) -> dict[str, object]:
        observed["lock_material_seed"] = _kwargs.get("material_seed")
        observed["lock_library_sha"] = _kwargs.get("library_snapshot_sha256")
        observed["lock_pool_index_sha"] = _kwargs.get("pool_index_sha256")
        (seed_root / "appearance.lock.json").write_text("{}\n", encoding="utf-8")
        return {"bindings": [{"asset_type": "pbr_material", "material": None}]}

    monkeypatch.setattr(target, "materialize_appearance_lock", _materialize_lock)
    monkeypatch.setattr(target, "config_mechanical_fingerprint", lambda _config: "config-sha")
    monkeypatch.setattr(target, "object_model_mechanical_fingerprint", lambda _model: "model-sha")
    output = tmp_path / "seed"

    manifest = target.build_canary_seed(
        slug="Handtools_clothes_peg",
        seed=0,
        material_seed=101,
        pbr_library=tmp_path / "pbr_material_library" / "latest.json",
        output_dir=output,
    )

    assert (output / "model.urdf").is_file()
    assert (output / "appearance.lock.json").is_file()
    assert not (output / "physics.lock.json").exists()
    assert not (output / "render_job.json").exists()
    assert not (output / "render_meshes").exists()
    assert not (output / "assets" / ".cadquery_cache").exists()
    assert manifest["visual_count"] == 1
    assert manifest["mesh_asset_count"] == 0
    assert manifest["material_seed"] == 101
    assert manifest["flat_color_binding_count"] == 0
    assert manifest["physics"] == {"status": "not_resolved"}
    assert manifest["pbr_library_logical_snapshot_sha256"] == "release-sha"
    assert manifest["pbr_library_pool_index_sha256"] == "pool-index-sha"
    assert observed == {
        "loaded_class_ids": {"plastic.opaque_generic"},
        "lock_library_sha": "release-sha",
        "lock_material_seed": 101,
        "lock_pool_index_sha": "pool-index-sha",
        "requests": [("body::shell", "plastic.opaque_generic")],
        "resolve_material_seed": 101,
    }


def test_typed_appearance_only_visual_keeps_authored_material() -> None:
    model = SimpleNamespace(
        materials=[],
        parts=[
            SimpleNamespace(
                name="cap",
                visuals=[
                    _Visual(
                        "marker",
                        material=Material(name="marker", rgba=(0.2, 0.4, 0.6, 1.0)),
                        appearance_only=AppearanceOnlySpec(kind="overlay"),
                    )
                ],
            )
        ],
    )

    request = target.appearance_requests_from_model(model)[0]

    assert request.surface_key == "cap::marker"
    assert request.asset_type == "appearance_only"
    assert request.material_class_id is None
    assert request.rgba == (0.2, 0.4, 0.6, 1.0)
    assert request.material_name == "marker"
    assert request.appearance_only == AppearanceOnlySpec(kind="overlay")


def test_debug_render_job_cli_flag_is_explicit() -> None:
    parser = target.build_parser()
    base = [
        "Handtools_clothes_peg",
        "--output",
        "seed",
    ]

    assert parser.parse_args(base).emit_debug_render_job is False
    assert parser.parse_args([*base, "--emit-debug-render-job"]).emit_debug_render_job is True
    assert parser.parse_args(base).material_seed is None
    assert parser.parse_args([*base, "--material-seed", "17"]).material_seed == 17
    assert parser.parse_args(base).pbr_library == target.DEFAULT_PBR_LIBRARY
    assert parser.parse_args([*base, "--pbr-library", "library/latest.json"]).pbr_library == Path(
        "library/latest.json"
    )
