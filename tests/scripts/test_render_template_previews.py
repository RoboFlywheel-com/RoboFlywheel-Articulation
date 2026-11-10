# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

import pytest
import trimesh
from PIL import Image

from scripts import render_template_previews as previews


def test_semantic_view_directions_support_legacy_negative_y_front() -> None:
    default = previews._semantic_view_directions(SimpleNamespace())
    legacy = previews._semantic_view_directions(
        SimpleNamespace(__preview_front_axis__="-y")
    )

    assert default["front_iso"][1] > 0.0
    assert legacy["front_iso"][1] < 0.0
    assert legacy["rear_iso"][1] > 0.0


def test_semantic_view_directions_support_z_fronts() -> None:
    positive = previews._semantic_view_directions(
        SimpleNamespace(__preview_front_axis__="+z")
    )
    negative = previews._semantic_view_directions(
        SimpleNamespace(__preview_front_axis__="-z")
    )

    assert positive["front_iso"][2] > 0.0
    assert negative["front_iso"][2] < 0.0


class _FakeXvfb:
    def __init__(self) -> None:
        self.terminated = 0

    def poll(self) -> None:
        return None

    def terminate(self) -> None:
        self.terminated += 1

    def wait(self, timeout: float) -> int:
        return 0

    def kill(self) -> None:  # pragma: no cover - timeout fallback only
        raise AssertionError("healthy fake Xvfb should not be killed")


def test_headless_vtk_batch_owns_and_cleans_xvfb(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.setattr(previews, "_XVFB_LOCK_PATH", tmp_path / "xvfb.lock")
    starts: list[_FakeXvfb] = []

    def start() -> tuple[_FakeXvfb, str]:
        process = _FakeXvfb()
        starts.append(process)
        return process, ":117"

    monkeypatch.setattr(previews, "_start_xvfb", start)
    with previews.headless_render_display("vtk"):
        assert os.environ["DISPLAY"] == ":117"
        with previews.headless_render_display("vtk"):
            assert os.environ["DISPLAY"] == ":117"

    assert len(starts) == 1
    assert starts[0].terminated == 1
    assert "DISPLAY" not in os.environ


def test_vtk_renderer_uses_in_process_path(monkeypatch, tmp_path: Path) -> None:
    output = tmp_path / "vtk.png"
    mesh = trimesh.creation.box(extents=(1.0, 1.0, 1.0))
    calls: list[Path] = []

    def render_vtk(meshes, out: Path) -> None:
        calls.append(out)
        image = Image.new("RGB", (64, 64), (35, 70, 105))
        for x in range(32, 64):
            for y in range(64):
                image.putpixel((x, y), (180, 205, 225))
        image.save(out)

    monkeypatch.setattr(previews, "_render_scene_vtk", render_vtk)
    previews._render_scene.renderer_mode = "vtk"
    previews._render_scene.direction = previews.VIEW_DIRECTIONS[0][1]  # type: ignore[attr-defined]

    previews._render_scene([(mesh, (0.5, 0.5, 0.5, 1.0))], output)

    assert calls == [output]


def test_validate_render_image_rejects_black_and_accepts_visible(tmp_path: Path) -> None:
    black = tmp_path / "black.png"
    visible = tmp_path / "visible.png"
    Image.new("RGB", (64, 64), (0, 0, 0)).save(black)
    visible_image = Image.new("RGB", (64, 64), (35, 70, 105))
    for x in range(32, 64):
        for y in range(64):
            visible_image.putpixel((x, y), (180, 205, 225))
    visible_image.save(visible)

    with pytest.raises(previews.RenderBackendError, match="black/near-black"):
        previews.validate_render_image(black)
    assert previews.validate_render_image(visible)["nonblack_fraction"] == 1.0


def test_egl_dependency_failure_never_calls_software(monkeypatch, tmp_path: Path) -> None:
    output = tmp_path / "egl.png"
    mesh = trimesh.creation.box(extents=(1.0, 1.0, 1.0))
    software_calls: list[Path] = []

    def fail_egl(*args, **kwargs) -> None:
        raise ModuleNotFoundError("pyrender")

    monkeypatch.setattr(previews, "_render_scene_egl", fail_egl)
    monkeypatch.setattr(
        previews,
        "_render_scene_software",
        lambda meshes, out: software_calls.append(out),
    )
    previews._render_scene.renderer_mode = "egl"

    with pytest.raises(previews.RenderBackendError, match="refusing software fallback"):
        previews._render_scene([(mesh, (0.5, 0.5, 0.5, 1.0))], output)
    assert software_calls == []


def test_egl_black_output_is_a_hard_failure(monkeypatch, tmp_path: Path) -> None:
    output = tmp_path / "egl-black.png"
    mesh = trimesh.creation.box(extents=(1.0, 1.0, 1.0))

    def render_black(meshes, out: Path) -> None:
        Image.new("RGB", (64, 64), (0, 0, 0)).save(out)

    monkeypatch.setattr(previews, "_render_scene_egl", render_black)
    previews._render_scene.renderer_mode = "egl"

    with pytest.raises(previews.RenderBackendError, match="black/near-black"):
        previews._render_scene([(mesh, (0.5, 0.5, 0.5, 1.0))], output)
