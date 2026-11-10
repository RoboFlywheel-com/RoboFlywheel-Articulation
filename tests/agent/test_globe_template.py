# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

from agent.templates.globe import (
    build_globe,
    config_from_seed,
    run_globe_tests,
    slot_choices_for_seed,
)
from sdk import Box, Mesh


def _obj_vertices_and_faces(
    path: Path,
) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "v":
            vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
        elif parts[0] == "f":
            faces.append(
                tuple(int(token.split("/", 1)[0]) - 1 for token in parts[1:4])  # type: ignore[arg-type]
            )
    return vertices, faces


def test_seed_zero_anchor_combination() -> None:
    assert slot_choices_for_seed(0) == [
        ("support_base", "classic_desktop"),
        ("meridian_or_cradle", "full_tilting"),
        ("globe_surface", "continent_patch"),
        ("auxiliary_rotary", "none"),
        ("graticule_density", "medium"),
        ("land_patch_style", "simple_continents"),
    ]


def test_first_five_seeds_cover_distinct_support_styles() -> None:
    support_styles = [dict(slot_choices_for_seed(seed))["support_base"] for seed in range(5)]

    assert support_styles == [
        "classic_desktop",
        "outer_cradle",
        "rotating_pedestal",
        "partial_ring",
        "wall_arm",
    ]


def test_non_curated_seed_window_stratifies_support_styles() -> None:
    support_styles = [dict(slot_choices_for_seed(seed))["support_base"] for seed in range(5, 10)]

    assert support_styles == [
        "classic_desktop",
        "outer_cradle",
        "rotating_pedestal",
        "partial_ring",
        "wall_arm",
    ]


def test_seed_zero_globe_template_passes_author_checks() -> None:
    config = config_from_seed(0)
    model = build_globe(config)
    report = run_globe_tests(model, config)
    assert report.passed, report.failures


def test_seed_zero_continents_are_surface_meshes_not_box_tabs() -> None:
    model = build_globe(config_from_seed(0))
    globe = model.get_part("globe")
    continent_visuals = [
        visual
        for visual in globe.visuals
        if visual.name and visual.name.startswith("continent_patch_")
    ]

    assert continent_visuals
    assert all(isinstance(visual.geometry, Mesh) for visual in continent_visuals)
    assert not any(isinstance(visual.geometry, Box) for visual in continent_visuals)


def test_seed_zero_continent_mesh_faces_point_outward() -> None:
    model = build_globe(config_from_seed(0))
    globe = model.get_part("globe")
    continent_meshes = [
        visual.geometry
        for visual in globe.visuals
        if visual.name and visual.name.startswith("continent_patch_")
    ]

    for mesh in continent_meshes:
        assert isinstance(mesh, Mesh)
        assert mesh.materialized_path is not None
        vertices, faces = _obj_vertices_and_faces(Path(mesh.materialized_path))
        assert faces
        for a, b, c in faces:
            ax, ay, az = vertices[a]
            bx, by, bz = vertices[b]
            cx, cy, cz = vertices[c]
            ux, uy, uz = bx - ax, by - ay, bz - az
            vx, vy, vz = cx - ax, cy - ay, cz - az
            nx = uy * vz - uz * vy
            ny = uz * vx - ux * vz
            nz = ux * vy - uy * vx
            mx = (ax + bx + cx) / 3.0
            my = (ay + by + cy) / 3.0
            mz = (az + bz + cz) / 3.0
            assert nx * mx + ny * my + nz * mz > 0.0


def test_seed_zero_continents_are_filled_irregular_blocks() -> None:
    model = build_globe(config_from_seed(0))
    globe = model.get_part("globe")
    continent_meshes = [
        visual.geometry
        for visual in globe.visuals
        if visual.name and visual.name.startswith("continent_patch_")
    ]

    for mesh in continent_meshes:
        assert isinstance(mesh, Mesh)
        assert mesh.materialized_path is not None
        vertices, faces = _obj_vertices_and_faces(Path(mesh.materialized_path))
        assert len(vertices) >= 25
        assert len(faces) >= 40
