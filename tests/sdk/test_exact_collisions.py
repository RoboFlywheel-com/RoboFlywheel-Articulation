# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import pytest

import sdk._core.v0.exact_collisions as ec
from sdk import ArticulatedObject, AssetContext, Box, Mesh, Origin
from sdk._core.v0.mesh import (
    BoxGeometry,
    mesh_from_geometry,
)
from sdk._core.v0.types import Collision


def _write_obj(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "v 0 0 0",
                "v 1 0 0",
                "v 0 1 0",
                "f 1 2 3",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _build_model_with_mesh(
    tmp_path: Path, mesh: Mesh, *, origin: Origin | None = None
) -> ArticulatedObject:
    assets = AssetContext(tmp_path)
    model = ArticulatedObject(name="exact_collision_model", assets=assets)
    part = model.part("body")
    part.visual(mesh, origin=origin or Origin(), name="body_visual")
    return model


def test_compile_exact_collisions_reuses_raw_visual_mesh(tmp_path: Path) -> None:
    mesh_path = tmp_path / "assets" / "meshes" / "raw.obj"
    _write_obj(mesh_path)
    mesh = Mesh(filename="assets/meshes/raw.obj")
    visual_origin = Origin(xyz=(0.1, 0.2, 0.3), rpy=(0.0, 0.1, 0.2))

    compiled = ec.compile_object_model_with_exact_collisions(
        _build_model_with_mesh(tmp_path, mesh, origin=visual_origin),
        asset_root=tmp_path,
    )

    collisions = compiled.parts[0].collisions
    assert len(collisions) == 1
    assert collisions[0].geometry == mesh
    assert collisions[0].origin == visual_origin
    assert collisions[0].name == "body_visual"
    assert not (tmp_path / "assets" / "meshes" / "collision" / "cache").exists()


def test_compile_exact_collisions_mirrors_primitive_backed_mesh_without_rewrite(
    tmp_path: Path,
) -> None:
    mesh = mesh_from_geometry(
        BoxGeometry((0.10, 0.20, 0.30)),
        tmp_path / "assets" / "meshes" / "box.obj",
    )

    compiled = ec.compile_object_model_with_exact_collisions(
        _build_model_with_mesh(tmp_path, mesh),
        asset_root=tmp_path,
    )

    collisions = compiled.parts[0].collisions
    assert len(collisions) == 1
    assert collisions[0].geometry == mesh
    assert collisions[0].origin == Origin()
    assert collisions[0].name == "body_visual"


def test_compile_exact_collisions_mirrors_legacy_mesh_prefix_without_rewrite(
    tmp_path: Path,
) -> None:
    mesh = mesh_from_geometry(
        BoxGeometry((0.10, 0.20, 0.30)),
        tmp_path / "assets" / "meshes" / "box.obj",
    )
    legacy_mesh = Mesh(
        filename="meshes/box.obj",
        source_geometry=mesh.source_geometry,
        source_transform=mesh.source_transform,
    )

    compiled = ec.compile_object_model_with_exact_collisions(
        _build_model_with_mesh(tmp_path, legacy_mesh),
        asset_root=tmp_path,
    )

    collisions = compiled.parts[0].collisions
    assert len(collisions) == 1
    assert collisions[0].geometry == legacy_mesh
    assert collisions[0].origin == Origin()
    assert collisions[0].name == "body_visual"


def test_compile_exact_collisions_rejects_explicit_part_collisions() -> None:
    model = ArticulatedObject(name="explicit_part_collisions")
    part = model.part("body")
    part.visual(Box((0.1, 0.1, 0.1)))
    part.collisions.append(Collision(geometry=Box((0.1, 0.1, 0.1))))

    with pytest.raises(ec.ValidationError, match="Part\\.collisions"):
        ec.compile_object_model_with_exact_collisions(model)
