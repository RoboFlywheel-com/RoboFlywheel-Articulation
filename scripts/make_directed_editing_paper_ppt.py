#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Render directed-edit paper rows once, then emit a tight PNG and an editable PPTX.

Every render is stored as an individual PNG under ``--render-root`` so the PPTX
can place each object as its own picture shape (movable/resizable in
PowerPoint) instead of one flattened bitmap.  Renders default to an opaque
white background; pass ``--transparent-background`` to keep the Blender film
alpha (transparent background with a semi-transparent ground shadow).
"""

from __future__ import annotations

import argparse
import gc
import json
import tempfile
from pathlib import Path

from PIL import Image

from pptx import Presentation
from pptx.util import Emu

from sdk import AssetContext
from specific_editing.generators import get_generator
from specific_editing.pipeline import build_variant, validate_spec
from specific_editing.render import SceneFrame, _render_blender_batch, extract_visual_meshes

from make_directed_editing_paper_figure import _foreground_crop
from make_directed_editing_shadow_variants import (
    PAPER_ROWS,
    SPEC_ROOT,
    SOURCE_ROOT,
    VIEW_KEY,
    _scene_frame,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "specific_editing" / "paper_figures"

SHADOW_STRENGTH = 0.8
BACKGROUND = (255, 255, 255)

PIXELS_PER_INCH = 200
CELL_WIDTH = 5.0
CELL_HEIGHT = 3.9
CELL_GAP = 0.08
OUTER_MARGIN = 0.04
GRID_COLUMNS = 4 * len(PAPER_ROWS) // 2
GRID_ROWS = 2

EMU_PER_INCH = 914400


def _render_root_for(output_dir: Path, strength: float, transparent: bool) -> Path:
    suffix = "_transparent" if transparent else ""
    return output_dir / f"renders_shadow_{strength:.1f}{suffix}"


def _row_render_paths(render_root: Path, asset_name: str, variant_ids: list[str]) -> list[Path]:
    root = render_root / asset_name
    return [root / "base.png", *(root / f"{variant_id}.png" for variant_id in variant_ids)]


def _render_model(
    model: object,
    *,
    frame: SceneFrame,
    front_axis: str,
    destination: Path,
    image_size: tuple[int, int],
    supersample: int,
    transparent: bool,
) -> None:
    meshes = extract_visual_meshes(model, pose="closed")
    _render_blender_batch(
        meshes,
        (("front_iso", destination),),
        front_axis=front_axis,
        frame=frame,
        image_size=image_size,
        supersample=supersample,
        background=BACKGROUND,
        shadow_strength=SHADOW_STRENGTH,
        transparent=transparent,
    )


def _render_row(
    asset_name: str,
    edit_kind: str,
    *,
    build_root: Path,
    render_root: Path,
    force: bool,
    transparent: bool,
) -> list[str]:
    spec, _summary = validate_spec(SPEC_ROOT / f"{asset_name}.json")
    variants = [variant for variant in spec.variants if variant.kind == edit_kind]
    if len(variants) != 3:
        raise RuntimeError(f"{asset_name}:{edit_kind} needs three variants")
    variant_ids = [variant.variant_id for variant in variants]
    destinations = _row_render_paths(render_root, asset_name, variant_ids)
    if not force and all(path.is_file() for path in destinations):
        print(f"reuse {asset_name}:{edit_kind} renders", flush=True)
        return variant_ids

    source_manifest = json.loads((SOURCE_ROOT / asset_name / "manifest.json").read_text())
    frame_payload = source_manifest.get("comparison_frames", {}).get(
        edit_kind, source_manifest["shared_frame"]
    )
    frame = _scene_frame(frame_payload)
    registration = get_generator(spec.generator_id)

    base_config = registration.make_config(spec.base_config, seed=spec.seed)
    base_model = registration.build(
        base_config, assets=AssetContext(build_root / asset_name / "base")
    )
    base_model.meta["specific_editing_generator_id"] = spec.generator_id
    _render_model(
        base_model,
        frame=frame,
        front_axis=registration.front_axis,
        destination=destinations[0],
        image_size=spec.image_size,
        supersample=spec.supersample,
        transparent=transparent,
    )
    del base_model
    gc.collect()

    for variant, destination in zip(variants, destinations[1:]):
        built = build_variant(
            spec, variant, build_root / asset_name / "variants" / variant.variant_id
        )
        _render_model(
            built.object_model,
            frame=frame,
            front_axis=registration.front_axis,
            destination=destination,
            image_size=spec.image_size,
            supersample=spec.supersample,
            transparent=transparent,
        )
        del built
        gc.collect()
    print(f"rendered {asset_name}:{edit_kind} at {SHADOW_STRENGTH:.1f}", flush=True)
    return variant_ids


def _alpha_crop(path: Path, *, margin: int = 12) -> Image.Image:
    with Image.open(path) as source:
        image = source.convert("RGBA")
    mask = image.getchannel("A").point(lambda value: 255 if value > 8 else 0)
    bounds = mask.getbbox()
    if bounds is None:
        return image
    left, top, right, bottom = bounds
    return image.crop(
        (
            max(0, left - margin),
            max(0, top - margin),
            min(image.width, right + margin),
            min(image.height, bottom + margin),
        )
    )


def _fit_size(size: tuple[int, int], box_width: float, box_height: float) -> tuple[float, float]:
    width, height = size
    scale = min(box_width / width, box_height / height)
    return width * scale, height * scale


def _grid_layout() -> tuple[float, float]:
    slide_width = 2 * OUTER_MARGIN + GRID_COLUMNS * CELL_WIDTH + (GRID_COLUMNS - 1) * CELL_GAP
    slide_height = 2 * OUTER_MARGIN + GRID_ROWS * CELL_HEIGHT + (GRID_ROWS - 1) * CELL_GAP
    return slide_width, slide_height


def _cell_origin(row: int, column: int) -> tuple[float, float]:
    x = OUTER_MARGIN + column * (CELL_WIDTH + CELL_GAP)
    y = OUTER_MARGIN + row * (CELL_HEIGHT + CELL_GAP)
    return x, y


def _compose(
    crops: list[list[Image.Image]],
    *,
    render_root: Path,
    names: list[list[str]],
    transparent: bool,
) -> tuple[Image.Image, list[list[tuple[float, float, float, float]]]]:
    """Return the tight canvas plus per-cell placed rectangles in inches."""
    slide_width, slide_height = _grid_layout()
    canvas_size = (round(slide_width * PIXELS_PER_INCH), round(slide_height * PIXELS_PER_INCH))
    canvas = (
        Image.new("RGBA", canvas_size, (0, 0, 0, 0))
        if transparent
        else Image.new("RGB", canvas_size, BACKGROUND)
    )
    placed: list[list[tuple[float, float, float, float]]] = []
    for row, row_crops in enumerate(crops):
        placed_row: list[tuple[float, float, float, float]] = []
        for column, crop in enumerate(row_crops):
            fit_width, fit_height = _fit_size(crop.size, CELL_WIDTH, CELL_HEIGHT)
            origin_x, origin_y = _cell_origin(row, column)
            left = origin_x + (CELL_WIDTH - fit_width) / 2
            top = origin_y + (CELL_HEIGHT - fit_height) / 2
            resized = crop.resize(
                (round(fit_width * PIXELS_PER_INCH), round(fit_height * PIXELS_PER_INCH)),
                Image.LANCZOS,
            )
            origin = (round(left * PIXELS_PER_INCH), round(top * PIXELS_PER_INCH))
            if transparent:
                layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
                layer.paste(resized, origin)
                canvas.alpha_composite(layer)
                layer.close()
            else:
                canvas.paste(resized, origin)
            resized.close()
            placed_row.append((left, top, fit_width, fit_height))
        placed.append(placed_row)
    return canvas, placed


def _save_crops(
    crops: list[list[Image.Image]],
    *,
    render_root: Path,
    names: list[list[str]],
) -> list[list[Path]]:
    paths: list[list[Path]] = []
    for row_crops, row_names in zip(crops, names):
        row_paths: list[Path] = []
        for crop, name in zip(row_crops, row_names):
            asset_name, stem = name.split("/", 1)
            destination = render_root / asset_name / "crops" / f"{stem}.png"
            destination.parent.mkdir(parents=True, exist_ok=True)
            crop.save(destination, optimize=True)
            row_paths.append(destination)
        paths.append(row_paths)
    return paths


def _build_pptx(
    *,
    crop_paths: list[list[Path]],
    placed: list[list[tuple[float, float, float, float]]],
    detail_rows: list[list[Path]],
    notes: list[list[str]],
    destination: Path,
) -> None:
    slide_width, slide_height = _grid_layout()
    presentation = Presentation()
    presentation.slide_width = Emu(round(slide_width * EMU_PER_INCH))
    presentation.slide_height = Emu(round(slide_height * EMU_PER_INCH))
    blank = presentation.slide_layouts[6]

    overview = presentation.slides.add_slide(blank)
    for row_paths, row_placed in zip(crop_paths, placed):
        for path, (left, top, width, height) in zip(row_paths, row_placed):
            overview.shapes.add_picture(
                str(path),
                Emu(round(left * EMU_PER_INCH)),
                Emu(round(top * EMU_PER_INCH)),
                Emu(round(width * EMU_PER_INCH)),
                Emu(round(height * EMU_PER_INCH)),
            )

    margin = 0.3
    gap = 0.2
    cell_width = (slide_width - 2 * margin - 3 * gap) / 4
    cell_height = slide_height - 2 * margin
    for row_paths, row_notes in zip(detail_rows, notes):
        slide = presentation.slides.add_slide(blank)
        for column, path in enumerate(row_paths):
            with Image.open(path) as crop:
                fit_width, fit_height = _fit_size(crop.size, cell_width, cell_height)
            left = margin + column * (cell_width + gap) + (cell_width - fit_width) / 2
            top = margin + (cell_height - fit_height) / 2
            slide.shapes.add_picture(
                str(path),
                Emu(round(left * EMU_PER_INCH)),
                Emu(round(top * EMU_PER_INCH)),
                Emu(round(fit_width * EMU_PER_INCH)),
                Emu(round(fit_height * EMU_PER_INCH)),
            )
        slide.notes_slide.notes_text_frame.text = "; ".join(row_notes)

    presentation.save(destination)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--render-root", type=Path, default=None)
    parser.add_argument("--force-render", action="store_true")
    parser.add_argument("--skip-render", action="store_true")
    parser.add_argument(
        "--transparent-background",
        action="store_true",
        help="keep the Blender film alpha (transparent RGBA) instead of white",
    )
    args = parser.parse_args()
    transparent = args.transparent_background
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    render_root = (
        args.render_root.expanduser().resolve()
        if args.render_root
        else _render_root_for(output_dir, SHADOW_STRENGTH, transparent)
    )

    variant_ids_by_row: list[list[str]] = []
    if args.skip_render:
        for asset_name, edit_kind in PAPER_ROWS:
            spec, _ = validate_spec(SPEC_ROOT / f"{asset_name}.json")
            variant_ids_by_row.append(
                [v.variant_id for v in spec.variants if v.kind == edit_kind]
            )
    else:
        with tempfile.TemporaryDirectory(
            prefix="directed-editing-paper-ppt-", dir="/tmp"
        ) as temporary_text:
            build_root = Path(temporary_text) / "build"
            for asset_name, edit_kind in PAPER_ROWS:
                variant_ids_by_row.append(
                    _render_row(
                        asset_name,
                        edit_kind,
                        build_root=build_root,
                        render_root=render_root,
                        force=args.force_render,
                        transparent=transparent,
                    )
                )

    crops: list[list[Image.Image]] = []
    names: list[list[str]] = []
    notes: list[list[str]] = []
    for (asset_name, _edit_kind), variant_ids in zip(PAPER_ROWS, variant_ids_by_row):
        spec, _ = validate_spec(SPEC_ROOT / f"{asset_name}.json")
        labels = {"base": "Base"}
        labels.update(
            (v.variant_id, v.label) for v in spec.variants if v.variant_id in variant_ids
        )
        paths = _row_render_paths(render_root, asset_name, variant_ids)
        row_crops = [
            _alpha_crop(path) if transparent else _foreground_crop(path, margin=12)
            for path in paths
        ]
        crops.append(row_crops)
        names.append([f"{asset_name}/base", *(f"{asset_name}/{v}" for v in variant_ids)])
        notes.append([f"{asset_name} {labels.get('base', 'Base')}"] + [
            f"{asset_name} {labels.get(v, v)}" for v in variant_ids
        ])

    row_pairs = [(0, 1), (2, 3)]
    grid_crops: list[list[Image.Image]] = [
        crops[first] + crops[second] for first, second in row_pairs
    ]
    grid_names = [names[first] + names[second] for first, second in row_pairs]
    grid_notes = [notes[first] + notes[second] for first, second in row_pairs]

    canvas, placed = _compose(
        grid_crops, render_root=render_root, names=grid_names, transparent=transparent
    )
    png_path = output_dir / f"directed_3d_editing_shadow_{SHADOW_STRENGTH:.1f}_2rows_notext_tight.png"
    canvas.save(png_path, dpi=(600, 600), optimize=True)
    canvas.close()
    print(png_path, flush=True)

    row_crop_paths = _save_crops(crops, render_root=render_root, names=names)
    grid_crop_paths = [
        row_crop_paths[first] + row_crop_paths[second] for first, second in row_pairs
    ]
    pptx_path = output_dir / f"directed_3d_editing_shadow_{SHADOW_STRENGTH:.1f}_2rows.pptx"
    _build_pptx(
        crop_paths=grid_crop_paths,
        placed=placed,
        detail_rows=row_crop_paths,
        notes=notes,
        destination=pptx_path,
    )
    print(pptx_path, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
