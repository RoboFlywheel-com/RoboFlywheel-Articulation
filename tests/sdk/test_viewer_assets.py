# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import trimesh

from sdk._core.v0.mesh import BoxGeometry, mesh_from_geometry
from sdk._core.v0.viewer_assets import convert_obj_file_to_glb, convert_urdf_visual_meshes_to_glb


def test_convert_urdf_visual_meshes_to_glb_resolves_legacy_mesh_prefix(tmp_path) -> None:
    mesh_from_geometry(
        BoxGeometry((1.0, 1.0, 1.0)),
        tmp_path / "assets" / "meshes" / "part.obj",
    )

    urdf_xml = (
        "<robot name='legacy'>"
        "<link name='base'>"
        "<visual><geometry><mesh filename='meshes/part.obj'/></geometry></visual>"
        "</link>"
        "</robot>"
    )

    converted_xml, warnings = convert_urdf_visual_meshes_to_glb(
        urdf_xml,
        asset_root=tmp_path,
    )

    assert warnings == []
    assert "meshes/part.glb" in converted_xml
    assert (tmp_path / "assets" / "meshes" / "part.glb").exists()


def test_convert_obj_file_to_glb_preserves_triangle_count(tmp_path: Path) -> None:
    obj_path = tmp_path / "plate.obj"
    obj_path.write_text(
        "\n".join(
            [
                "o mesh",
                "v 0 0 0",
                "v 1 0 0",
                "v 0 1 0",
                "f 1 2 3",
                "f 3 2 1",
                "",
            ]
        ),
        encoding="utf-8",
    )

    glb_path = convert_obj_file_to_glb(obj_path)
    glb_mesh = trimesh.load_mesh(glb_path, force="mesh")

    assert len(glb_mesh.faces) == 2
