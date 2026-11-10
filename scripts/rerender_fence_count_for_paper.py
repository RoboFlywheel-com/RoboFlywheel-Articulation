#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Render crisp, individually framed Fence count assets for the paper figure."""

from __future__ import annotations

import argparse
import gc
import shutil
import tempfile
from pathlib import Path

from sdk import AssetContext
from specific_editing.generators import get_generator
from specific_editing.pipeline import build_variant, validate_spec
from specific_editing.render import render_variant, shared_frame


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "specific_editing" / "specs" / "single_variable" / "fence.json"
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT
    / "specific_editing"
    / "outputs"
    / "single_variable"
    / "fence"
    / "paper_renders"
    / "count"
)
VIEW_KEY = "closed__front_iso"
OUTPUT_NAMES = {
    2: "base__closed__front_iso.png",
    3: "count_3__closed__front_iso.png",
    4: "count_4__closed__front_iso.png",
    10: "count_10__closed__front_iso.png",
}


def _render_one(
    model: object,
    *,
    output_dir: Path,
    front_axis: str,
    image_size: tuple[int, int],
    supersample: int,
    shadow_strength: float,
) -> Path:
    frame = shared_frame(
        [model],
        poses=("closed",),
        front_axis=front_axis,
        size=image_size,
    )
    rendered = render_variant(
        model,
        output_dir,
        views=("front_iso",),
        poses=("closed",),
        front_axis=front_axis,
        size=image_size,
        backend="blender",
        frame=frame,
        supersample=supersample,
        shadow_strength=shadow_strength,
    )
    return rendered[VIEW_KEY]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    spec, _summary = validate_spec(SPEC_PATH)
    variants = [variant for variant in spec.variants if variant.kind == "count"]
    if [variant.value for variant in variants] != [3, 4, 10]:
        raise RuntimeError("Fence count variants must be ordered as 3, 4, 10")

    registration = get_generator(spec.generator_id)
    output_dir = args.output_dir.expanduser().resolve()
    with tempfile.TemporaryDirectory(prefix="fence-paper-render-", dir="/tmp") as temp_text:
        temp_root = Path(temp_text)
        rendered_paths: dict[int, Path] = {}

        base_config = registration.make_config(spec.base_config, seed=spec.seed)
        base_model = registration.build(
            base_config,
            assets=AssetContext(temp_root / "build" / "base"),
        )
        base_model.meta["specific_editing_generator_id"] = spec.generator_id
        rendered_paths[2] = _render_one(
            base_model,
            output_dir=temp_root / "renders" / "base",
            front_axis=registration.front_axis,
            image_size=spec.image_size,
            supersample=spec.supersample,
            shadow_strength=spec.shadow_strength,
        )
        del base_model
        gc.collect()

        for variant in variants:
            built = build_variant(
                spec,
                variant,
                temp_root / "build" / variant.variant_id,
            )
            count = int(variant.value)
            rendered_paths[count] = _render_one(
                built.object_model,
                output_dir=temp_root / "renders" / variant.variant_id,
                front_axis=registration.front_axis,
                image_size=spec.image_size,
                supersample=spec.supersample,
                shadow_strength=spec.shadow_strength,
            )
            del built
            gc.collect()

        output_dir.mkdir(parents=True, exist_ok=True)
        for count, filename in OUTPUT_NAMES.items():
            destination = output_dir / filename
            shutil.copy2(rendered_paths[count], destination)
            print(destination, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
