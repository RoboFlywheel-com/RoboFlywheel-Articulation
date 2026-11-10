# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from scripts import _pbr_material_preview_common as common
from scripts import _render_pbr_material_physics_previews_bpy as target


def test_pixel_gate_rejects_blank_render(tmp_path: Path) -> None:
    path = tmp_path / "blank.png"
    Image.new("RGB", (64, 64), (0, 0, 0)).save(path)

    with pytest.raises(RuntimeError, match="nonblank pixel gate"):
        target._validate_pixels(path)


def test_pixel_gate_accepts_visible_material_render(tmp_path: Path) -> None:
    path = tmp_path / "visible.png"
    image = Image.new("RGB", (64, 64), (30, 40, 50))
    for x in range(16, 48):
        for y in range(16, 48):
            image.putpixel((x, y), (180, 140, 90))
    image.save(path)

    metrics = target._validate_pixels(path)

    assert min(metrics["rgb_mean"]) > 5
    assert max(metrics["rgb_stddev"]) > 2


def test_metric_uv_scale_uses_surface_area_and_real_world_tile_period() -> None:
    factor = common._metric_uv_scale_factor(
        surface_area_m2=2.0,
        uv_area=0.5,
        texture_size_m=0.5,
    )

    assert factor == pytest.approx(4.0)
    assert common._triangle_area_3d((0, 0, 0), (2, 0, 0), (0, 1, 0)) == pytest.approx(1.0)
    assert common._triangle_area_2d((0, 0), (1, 0), (0, 1)) == pytest.approx(0.5)


def test_metric_uv_scale_rejects_nonpositive_contract_values() -> None:
    with pytest.raises(common.PreviewMaterialError, match="positive and finite"):
        common._metric_uv_scale_factor(
            surface_area_m2=1.0,
            uv_area=1.0,
            texture_size_m=0.0,
        )
