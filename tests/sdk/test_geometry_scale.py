# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import pytest

import sdk


def _geometry_aabb(
    geometry: sdk.Box | sdk.Cylinder | sdk.Sphere | sdk.Mesh,
    *,
    asset_root: Path | None = None,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    part = sdk.Part("body", visuals=[sdk.Visual(geometry)])
    aabb = sdk.part_local_aabb(part, asset_root=asset_root, prefer_collisions=False)
    assert aabb is not None
    return aabb


def _aabb_size(
    aabb: tuple[tuple[float, float, float], tuple[float, float, float]],
) -> tuple[float, float, float]:
    return (
        float(aabb[1][0]) - float(aabb[0][0]),
        float(aabb[1][1]) - float(aabb[0][1]),
        float(aabb[1][2]) - float(aabb[0][2]),
    )


def test_scale_geometry_to_size_stretches_box() -> None:
    scaled = sdk.scale_geometry_to_size(
        sdk.Box((0.10, 0.20, 0.30)),
        (0.40, None, 0.60),
    )

    assert isinstance(scaled, sdk.Box)
    assert scaled.size == pytest.approx((0.40, 0.20, 0.60))


def test_scale_geometry_to_size_uniformly_scales_box() -> None:
    scaled = sdk.scale_geometry_to_size(
        sdk.Box((0.10, 0.20, 0.30)),
        (0.20, None, None),
        mode="uniform",
    )

    assert isinstance(scaled, sdk.Box)
    assert scaled.size == pytest.approx((0.20, 0.40, 0.60))


def test_scale_geometry_to_size_resizes_mesh_using_current_extents(tmp_path: Path) -> None:
    mesh = sdk.mesh_from_geometry(
        sdk.BoxGeometry((0.50, 1.00, 1.50)),
        tmp_path / "assets" / "meshes" / "box.obj",
    )

    scaled = sdk.scale_geometry_to_size(
        mesh,
        (1.00, 2.00, 3.00),
        asset_root=tmp_path,
    )

    assert isinstance(scaled, sdk.Mesh)
    assert scaled.filename == mesh.filename
    assert scaled.scale == pytest.approx((2.0, 2.0, 2.0))
    assert scaled.source_geometry == mesh.source_geometry
    assert scaled.source_transform == mesh.source_transform
    assert _aabb_size(_geometry_aabb(scaled, asset_root=tmp_path)) == pytest.approx(
        (1.00, 2.00, 3.00)
    )


def test_scale_geometry_to_size_keeps_mesh_origin_fixed(tmp_path: Path) -> None:
    mesh = sdk.mesh_from_geometry(
        sdk.BoxGeometry((1.0, 1.0, 1.0)).translate(1.0, 0.0, 0.0),
        tmp_path / "assets" / "meshes" / "translated_box.obj",
    )

    scaled = sdk.scale_geometry_to_size(
        mesh,
        (2.0, None, None),
        asset_root=tmp_path,
    )

    aabb = _geometry_aabb(scaled, asset_root=tmp_path)
    assert aabb[0] == pytest.approx((1.0, -0.5, -0.5))
    assert aabb[1] == pytest.approx((3.0, 0.5, 0.5))


def test_scale_geometry_to_size_preserves_cylinder_when_xy_match() -> None:
    scaled = sdk.scale_geometry_to_size(
        sdk.Cylinder(radius=0.05, length=0.20),
        (0.20, 0.20, 0.40),
    )

    assert isinstance(scaled, sdk.Cylinder)
    assert scaled.radius == pytest.approx(0.10)
    assert scaled.length == pytest.approx(0.40)


def test_scale_geometry_to_size_preserves_sphere_when_axes_match() -> None:
    scaled = sdk.scale_geometry_to_size(
        sdk.Sphere(radius=0.05),
        (0.20, 0.20, 0.20),
    )

    assert isinstance(scaled, sdk.Sphere)
    assert scaled.radius == pytest.approx(0.10)


def test_scale_geometry_to_size_converts_cylinder_to_mesh_when_anisotropic(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "assets" / "meshes" / "scaled_cylinder.obj"
    scaled = sdk.scale_geometry_to_size(
        sdk.Cylinder(radius=0.05, length=0.20),
        (0.20, 0.30, 0.40),
        filename=output_path,
    )

    assert isinstance(scaled, sdk.Mesh)
    assert scaled.filename == "assets/meshes/scaled_cylinder.obj"
    assert output_path.exists()
    assert isinstance(scaled.source_geometry, sdk.Cylinder)
    assert _aabb_size(_geometry_aabb(scaled, asset_root=tmp_path)) == pytest.approx(
        (0.20, 0.30, 0.40),
        abs=1e-3,
    )


def test_scale_geometry_to_size_converts_sphere_to_mesh_when_anisotropic(
    tmp_path: Path,
) -> None:
    output_path = tmp_path / "assets" / "meshes" / "scaled_sphere.obj"
    scaled = sdk.scale_geometry_to_size(
        sdk.Sphere(radius=0.05),
        (0.20, 0.30, 0.40),
        filename=output_path,
    )

    assert isinstance(scaled, sdk.Mesh)
    assert scaled.filename == "assets/meshes/scaled_sphere.obj"
    assert output_path.exists()
    assert isinstance(scaled.source_geometry, sdk.Sphere)
    assert _aabb_size(_geometry_aabb(scaled, asset_root=tmp_path)) == pytest.approx(
        (0.20, 0.30, 0.40),
        abs=1e-2,
    )


def test_scale_geometry_to_size_requires_mesh_name_for_primitive_mesh_conversion() -> None:
    with pytest.raises(
        sdk.ValidationError,
        match="mesh_name is required when resizing this primitive would convert it into Mesh",
    ):
        sdk.scale_geometry_to_size(
            sdk.Cylinder(radius=0.05, length=0.20),
            (0.20, 0.30, 0.40),
        )


def test_scale_geometry_to_size_rejects_inconsistent_uniform_targets() -> None:
    with pytest.raises(sdk.ValidationError, match="inconsistent target ratios"):
        sdk.scale_geometry_to_size(
            sdk.Box((0.10, 0.20, 0.30)),
            (0.20, 0.30, None),
            mode="uniform",
        )


@pytest.mark.parametrize(
    ("target_size", "message"),
    [
        ((None, None, None), "must specify at least one axis"),
        ((-0.10, None, None), "must be a positive finite value or None"),
        ((0.0, None, None), "must be a positive finite value or None"),
    ],
)
def test_scale_geometry_to_size_rejects_invalid_target_sizes(
    target_size: tuple[float | None, float | None, float | None],
    message: str,
) -> None:
    with pytest.raises(sdk.ValidationError, match=message):
        sdk.scale_geometry_to_size(sdk.Box((0.10, 0.20, 0.30)), target_size)


def test_scale_geometry_to_size_rejects_missing_mesh_file(tmp_path: Path) -> None:
    with pytest.raises(sdk.ValidationError, match="Mesh file not found"):
        sdk.scale_geometry_to_size(
            sdk.Mesh(filename="assets/meshes/missing.obj"),
            (0.10, None, None),
            asset_root=tmp_path,
        )


def test_scale_geometry_to_size_rejects_zero_span_requested_mesh_axis(tmp_path: Path) -> None:
    mesh = sdk.mesh_from_geometry(
        sdk.MeshGeometry(
            vertices=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
            faces=[(0, 1, 2)],
        ),
        tmp_path / "assets" / "meshes" / "planar.obj",
    )

    with pytest.raises(sdk.ValidationError, match="current span is zero"):
        sdk.scale_geometry_to_size(
            mesh,
            (None, None, 0.10),
            asset_root=tmp_path,
        )
