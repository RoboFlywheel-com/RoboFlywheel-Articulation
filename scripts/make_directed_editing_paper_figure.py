#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Compose four directed-edit comparison rows into one paper figure."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ASSET_ROOT = REPO_ROOT / "specific_editing" / "outputs" / "single_variable"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "specific_editing" / "paper_figures"
VIEW_KEY = "closed__front_iso"

OUTPUT_DPI = 600
CANVAS_WIDTH = 4800
HEADER_HEIGHT = 176
ROW_HEIGHT = 850
BOTTOM_MARGIN = 56
LEFT_MARGIN = 68
CONTENT_X = 600
RIGHT_MARGIN = 72
CELL_GAP = 36
ASSET_TOP_PADDING = 20
ASSET_HEIGHT = 660
ASSET_Y_OFFSET = 24
LABEL_TOP_PADDING = 26
FERRIS_PAPER_RENDER_PATHS = (
    Path("paper_renders/count/base__closed__front_iso.png"),
    Path("paper_renders/count/count_5__closed__front_iso.png"),
    Path("paper_renders/count/count_12__closed__front_iso.png"),
    Path("paper_renders/count/count_20__closed__front_iso.png"),
)

BACKGROUND = (255, 255, 255)
TEXT = (35, 40, 47)
MUTED = (72, 81, 92)
ACCENT = (31, 101, 116)
LINE = (216, 222, 229)

REGULAR_FONT = Path("/usr/share/fonts/google-droid/DroidSans.ttf")
BOLD_FONT = Path("/usr/share/fonts/google-droid/DroidSans-Bold.ttf")


@dataclass(frozen=True)
class RowSpec:
    asset_name: str
    edit_kind: str
    title: str
    subtitle: str
    labels: tuple[str, str, str, str]
    use_comparison_sheet: bool = False


ROWS = (
    RowSpec(
        "table_football",
        "component",
        "Component",
        "Support structure",
        ("Tubular legs", "Splayed legs", "Side panels", "Cross trestles"),
    ),
    RowSpec(
        "ferris_wheel",
        "count",
        "Count",
        "Gondola count",
        ("Base (8 gondolas)", "5 gondolas", "12 gondolas", "20 gondolas"),
    ),
    RowSpec(
        "playground_chair_swing_carousel",
        "material",
        "Material",
        "Chair surfaces",
        ("Oak", "Red enamel", "Warm white", "Brushed silver"),
    ),
    RowSpec(
        "cabinet_paper_showcase",
        "size",
        "Size",
        "Cabinet width",
        ("1.00 m", "0.78 m", "1.26 m", "1.50 m"),
    ),
)


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size=size)


def _centered_text(
    draw: ImageDraw.ImageDraw,
    center_x: float,
    y: float,
    text: str,
    *,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int],
) -> None:
    bounds = draw.textbbox((0, 0), text, font=font)
    draw.text(
        (round(center_x - (bounds[2] - bounds[0]) / 2), round(y)),
        text,
        font=font,
        fill=fill,
    )


def _foreground_crop_image(image: Image.Image, *, margin: int = 12) -> Image.Image:
    image = image.convert("RGB")
    backdrop = Image.new("RGB", image.size, BACKGROUND)
    difference = ImageChops.difference(image, backdrop).convert("L")
    mask = difference.point(lambda value: 255 if value > 3 else 0)
    bounds = mask.getbbox()
    if bounds is None:
        return image
    left, top, right, bottom = bounds
    crop = image.crop(
        (
            max(0, left - margin),
            max(0, top - margin),
            min(image.width, right + margin),
            min(image.height, bottom + margin),
        )
    )
    image.close()
    return crop


def _foreground_crop(path: Path, *, margin: int = 12) -> Image.Image:
    return _foreground_crop_image(Image.open(path), margin=margin)


def _row_image_paths(
    row: RowSpec, *, asset_root: Path
) -> tuple[Path, Path, Path, Path]:
    root = asset_root / row.asset_name
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    base_path = root / manifest["base"]["renders"][VIEW_KEY]
    variants = [
        root / item["renders"][VIEW_KEY]
        for item in manifest["variants"]
        if item["variant"]["kind"] == row.edit_kind
    ]
    if len(variants) != 3:
        raise RuntimeError(
            f"{row.asset_name}:{row.edit_kind} needs three variants, found {len(variants)}"
        )
    return (base_path, variants[0], variants[1], variants[2])


def _paper_render_paths(
    row: RowSpec, *, asset_root: Path
) -> tuple[Path, Path, Path, Path] | None:
    if row.asset_name != "ferris_wheel" or row.edit_kind != "count":
        return None
    paths = tuple(asset_root / row.asset_name / path for path in FERRIS_PAPER_RENDER_PATHS)
    return paths if all(path.is_file() for path in paths) else None


def _comparison_sheet_strip(
    row: RowSpec, *, asset_root: Path, target_width: int
) -> Image.Image:
    path = (
        asset_root
        / row.asset_name
        / "comparisons"
        / row.edit_kind
        / f"{VIEW_KEY}.png"
    )
    sheet = Image.open(path).convert("RGB")
    # Labels occupy the bottom fifth of the source sheet. Keep the rendered
    # objects as one strip so panels that cross nominal cell edges stay intact.
    # Compact paper sheets use a 30 px label, 16 px leading, and 22 px
    # bottom padding. Keep the entire asset band above that fixed label area.
    asset_bottom = max(1, sheet.height - 68)
    strip = sheet.crop((0, 0, sheet.width, asset_bottom))
    sheet.close()

    difference = ImageChops.difference(strip, Image.new("RGB", strip.size, BACKGROUND)).convert(
        "L"
    )
    bounds = difference.point(lambda value: 255 if value > 3 else 0).getbbox()
    if bounds is not None:
        top = max(0, bounds[1] - 8)
        bottom = min(strip.height, bounds[3] + 8)
        trimmed = strip.crop((0, top, strip.width, bottom))
        strip.close()
        strip = trimmed

    scale = min(target_width / strip.width, (ASSET_HEIGHT - 32) / strip.height)
    size = (round(strip.width * scale), round(strip.height * scale))
    resized = strip.resize(size, Image.Resampling.LANCZOS)
    strip.close()
    sharpened = resized.filter(ImageFilter.UnsharpMask(radius=1.2, percent=105, threshold=3))
    resized.close()
    return sharpened


def _scaled_crops(
    row: RowSpec,
    *,
    asset_root: Path,
    cell_width: int,
    source_paths: tuple[Path, Path, Path, Path] | None = None,
    scale_multipliers: tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
) -> list[Image.Image]:
    crops = [
        _foreground_crop(path)
        for path in (source_paths or _row_image_paths(row, asset_root=asset_root))
    ]
    usable_width = cell_width - 60
    usable_height = ASSET_HEIGHT - 32
    common_scale = min(
        usable_width / max(crop.width for crop in crops),
        usable_height / max(crop.height for crop in crops),
    )
    scales = [common_scale * multiplier for multiplier in scale_multipliers]

    output: list[Image.Image] = []
    for crop, scale in zip(crops, scales, strict=True):
        size = (max(1, round(crop.width * scale)), max(1, round(crop.height * scale)))
        resized = crop.resize(size, Image.Resampling.LANCZOS)
        output.append(
            resized.filter(ImageFilter.UnsharpMask(radius=1.2, percent=105, threshold=3))
        )
        resized.close()
        crop.close()
    return output


def compose_figure(*, asset_root: Path = DEFAULT_ASSET_ROOT) -> Image.Image:
    content_width = CANVAS_WIDTH - CONTENT_X - RIGHT_MARGIN
    cell_width = (content_width - CELL_GAP * 3) // 4
    content_right = CONTENT_X + cell_width * 4 + CELL_GAP * 3
    canvas_height = HEADER_HEIGHT + ROW_HEIGHT * len(ROWS) + BOTTOM_MARGIN
    canvas = Image.new("RGB", (CANVAS_WIDTH, canvas_height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)

    header_font = _font(BOLD_FONT, 58)
    row_font = _font(BOLD_FONT, 64)
    subtitle_font = _font(BOLD_FONT, 48)
    letter_font = _font(REGULAR_FONT, 50)
    label_font = _font(REGULAR_FONT, 60)
    small_font = _font(REGULAR_FONT, 46)

    first_center = CONTENT_X + cell_width / 2
    edited_left = CONTENT_X + cell_width + CELL_GAP
    edited_center = edited_left + (cell_width * 3 + CELL_GAP * 2) / 2
    draw.text((LEFT_MARGIN, 54), "Edit type", font=small_font, fill=MUTED)
    _centered_text(draw, first_center, 44, "Original", font=header_font, fill=TEXT)
    _centered_text(
        draw, edited_center, 44, "Edited variants", font=header_font, fill=ACCENT
    )
    draw.line((LEFT_MARGIN, 144, content_right, 144), fill=LINE, width=4)

    for row_index, row in enumerate(ROWS):
        row_top = HEADER_HEIGHT + row_index * ROW_HEIGHT
        asset_top = row_top + ASSET_TOP_PADDING
        label_y = asset_top + ASSET_HEIGHT + LABEL_TOP_PADDING

        letter = f"({chr(ord('a') + row_index)})"
        title_bounds = draw.textbbox((0, 0), row.title, font=row_font)
        title_height = title_bounds[3] - title_bounds[1]
        subtitle_bounds = draw.textbbox((0, 0), row.subtitle, font=subtitle_font)
        subtitle_height = subtitle_bounds[3] - subtitle_bounds[1]
        block_height = title_height + 18 + subtitle_height
        title_y = row_top + (ASSET_HEIGHT - block_height) / 2
        draw.text((LEFT_MARGIN, title_y + 8), letter, font=letter_font, fill=MUTED)
        draw.text((182, title_y), row.title, font=row_font, fill=TEXT)
        draw.text(
            (182, title_y + title_height + 18),
            row.subtitle,
            font=subtitle_font,
            fill=MUTED,
        )

        paper_render_paths = _paper_render_paths(row, asset_root=asset_root)
        if paper_render_paths is not None:
            images = _scaled_crops(
                row,
                asset_root=asset_root,
                cell_width=cell_width,
                source_paths=paper_render_paths,
            )
            for column, image in enumerate(images):
                cell_left = CONTENT_X + column * (cell_width + CELL_GAP)
                x = cell_left + (cell_width - image.width) // 2
                y = asset_top + (ASSET_HEIGHT - image.height) // 2 + ASSET_Y_OFFSET
                canvas.paste(image, (x, y))
                image.close()
        else:
            images = _scaled_crops(row, asset_root=asset_root, cell_width=cell_width)
            for column, image in enumerate(images):
                cell_left = CONTENT_X + column * (cell_width + CELL_GAP)
                x = cell_left + (cell_width - image.width) // 2
                y = asset_top + (ASSET_HEIGHT - image.height) // 2 + ASSET_Y_OFFSET
                canvas.paste(image, (x, y))
                image.close()

        for column, label in enumerate(row.labels):
            cell_left = CONTENT_X + column * (cell_width + CELL_GAP)
            _centered_text(
                draw,
                cell_left + cell_width / 2,
                label_y,
                label,
                font=label_font,
                fill=TEXT if column == 0 else MUTED,
            )

        if row_index < len(ROWS) - 1:
            separator_y = row_top + ROW_HEIGHT - 1
            draw.line((LEFT_MARGIN, separator_y, content_right, separator_y), fill=LINE, width=4)

    divider_x = CONTENT_X + cell_width + CELL_GAP // 2
    draw.line(
        (divider_x, HEADER_HEIGHT - 8, divider_x, canvas_height - BOTTOM_MARGIN),
        fill=LINE,
        width=4,
    )

    return canvas


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset-root", type=Path, default=DEFAULT_ASSET_ROOT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--png-only", action="store_true")
    args = parser.parse_args()
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    image = compose_figure(asset_root=args.asset_root.expanduser().resolve())
    png_path = output_dir / "directed_3d_editing.png"
    pdf_path = output_dir / "directed_3d_editing.pdf"
    image.save(png_path, dpi=(OUTPUT_DPI, OUTPUT_DPI), optimize=True)
    print(png_path)
    if not args.png_only:
        image.save(pdf_path, "PDF", resolution=float(OUTPUT_DPI))
        print(pdf_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
