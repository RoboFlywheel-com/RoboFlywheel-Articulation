#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Render individually framed Ferris-wheel count assets for the paper figure."""

from __future__ import annotations

import argparse
import gc
import json
import shutil
import tempfile
from pathlib import Path

from sdk import AssetContext
from specific_editing.generators import get_generator
from specific_editing.pipeline import apply_material_override, validate_spec
from specific_editing.pbr_materials import BRUSHED_SILVER
from specific_editing.render import render_variant, shared_frame


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "specific_editing" / "specs" / "single_variable" / "ferris_wheel.json"
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT
    / "specific_editing"
    / "outputs"
    / "single_variable"
    / "ferris_wheel"
    / "paper_renders"
    / "count"
)
VIEW_KEY = "closed__front_iso"
BASE_COUNT = 8
EDIT_COUNTS = (5, 12, 20)
IMAGE_SIZE = (1600, 1120)
SUPERsample = 2
SHADOW_STRENGTH = 0.6
OUTPUT_NAMES = {
    BASE_COUNT: "base__closed__front_iso.png",
    5: "count_5__closed__front_iso.png",
    12: "count_12__closed__front_iso.png",
    20: "count_20__closed__front_iso.png",
}


def _apply_wheel_finish(model: object) -> None:
    """Give the rotating wheel a readable neutral-metal finish while preserving cabins."""

    apply_material_override(
        model,
        target="wheel",
        material={
            "name": "brushed silver wheel",
            "parts": ["wheel"],
            "rgba": [0.63, 0.67, 0.71, 1.0],
            "metallic": 0.86,
            "roughness": 0.24,
            "material_id": BRUSHED_SILVER,
        },
    )


def _render_one(
    model: object,
    *,
    output_dir: Path,
    front_axis: str,
) -> Path:
    frame = shared_frame(
        [model],
        poses=("closed",),
        front_axis=front_axis,
        size=IMAGE_SIZE,
        padding=1.05,
    )
    rendered = render_variant(
        model,
        output_dir,
        views=("front_iso",),
        poses=("closed",),
        front_axis=front_axis,
        size=IMAGE_SIZE,
        backend="blender",
        frame=frame,
        supersample=SUPERsample,
        shadow_strength=SHADOW_STRENGTH,
    )
    return rendered[VIEW_KEY]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    spec, _summary = validate_spec(SPEC_PATH)
    registration = get_generator(spec.generator_id)
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    counts = (BASE_COUNT, *EDIT_COUNTS)
    with tempfile.TemporaryDirectory(prefix="ferris-paper-render-", dir="/tmp") as temp_text:
        temp_root = Path(temp_text)
        rendered_paths: dict[int, Path] = {}
        for count in counts:
            config_values = dict(spec.base_config)
            config_values.update(
                {
                    "num_gondolas": count,
                    "frame_palette": "painted_white",
                }
            )
            config = registration.make_config(config_values, seed=spec.seed)
            model = registration.build(
                config,
                assets=AssetContext(temp_root / "build" / f"count_{count}"),
            )
            model.meta["specific_editing_generator_id"] = spec.generator_id
            _apply_wheel_finish(model)
            rendered_paths[count] = _render_one(
                model,
                output_dir=temp_root / "renders" / f"count_{count}",
                front_axis=registration.front_axis,
            )
            del model
            gc.collect()

        for count, filename in OUTPUT_NAMES.items():
            destination = output_dir / filename
            shutil.copy2(rendered_paths[count], destination)
            print(destination, flush=True)

    receipt = {
        "base_count": BASE_COUNT,
        "edit_counts": list(EDIT_COUNTS),
        "image_size": list(IMAGE_SIZE),
        "supersample": SUPERsample,
        "shadow_strength": SHADOW_STRENGTH,
        "wheel_finish": "brushed_silver",
    }
    (output_dir / "render_receipt.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
