# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

import sdk


def _bounds(
    geometry: sdk.MeshGeometry,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    xs = [v[0] for v in geometry.vertices]
    ys = [v[1] for v in geometry.vertices]
    zs = [v[2] for v in geometry.vertices]
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))


def test_partition_shell_splits_named_regions_and_remainder() -> None:
    shell = sdk.BoxGeometry((0.08, 0.12, 0.03))
    center_gap = 0.004
    split_front = sdk.BoxGeometry((center_gap, 0.075, 0.04)).translate(0.0, -0.0225, 0.0)

    parts = sdk.partition_shell(
        sdk.ShellPartitionSpec(
            shell=shell,
            regions=(
                sdk.ShellPartitionRegion(name="left_click", side="left", y_max=0.0),
                sdk.ShellPartitionRegion(name="right_click", side="right", y_max=0.0),
            ),
            splitters=(split_front,),
            remainder_name="body",
            center_gap=center_gap,
            padding=0.01,
        )
    )

    assert set(parts) == {"left_click", "right_click", "body"}

    left_min, left_max = _bounds(parts["left_click"])
    right_min, right_max = _bounds(parts["right_click"])
    body_min, body_max = _bounds(parts["body"])

    assert left_max[0] <= -0.5 * center_gap + 1e-6
    assert right_min[0] >= 0.5 * center_gap - 1e-6
    assert left_max[1] <= 0.0 + 1e-6
    assert right_max[1] <= 0.0 + 1e-6
    assert body_max[1] >= 0.059
    assert body_min[1] <= -0.059


def test_partition_shell_rejects_duplicate_names() -> None:
    with pytest.raises(sdk.ValidationError):
        sdk.ShellPartitionSpec(
            shell=sdk.BoxGeometry((0.04, 0.04, 0.04)),
            regions=(
                sdk.ShellPartitionRegion(name="button"),
                sdk.ShellPartitionRegion(name="button"),
            ),
        )


def test_partition_shell_requires_positive_center_gap_for_center_region() -> None:
    shell = sdk.BoxGeometry((0.08, 0.12, 0.03))
    spec = sdk.ShellPartitionSpec(
        shell=shell,
        regions=(sdk.ShellPartitionRegion(name="middle", side="center"),),
    )

    with pytest.raises(sdk.ValidationError):
        sdk.partition_shell(spec)


def test_cylinder_geometry_is_usable_as_boolean_splitter() -> None:
    shell = sdk.BoxGeometry((0.08, 0.12, 0.05))
    cutter = sdk.CylinderGeometry(radius=0.012, height=0.04, radial_segments=40, closed=True)
    cutter.rotate_y(1.5707963267948966).translate(0.0, 0.0, 0.01)

    carved = sdk.boolean_difference(shell, cutter)

    assert carved.vertices
    assert carved.faces
