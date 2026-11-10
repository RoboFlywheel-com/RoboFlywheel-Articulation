#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Render paper assets once and compose exact shadow-strength variants."""

from __future__ import annotations

import argparse
import gc
import json
import tempfile
from pathlib import Path

from sdk import AssetContext
from specific_editing.generators import get_generator
from specific_editing.pipeline import build_variant, validate_spec
from specific_editing.render import (
    SceneFrame,
    _render_blender_batch,
    extract_visual_meshes,
    make_comparison_sheets,
)

from make_directed_editing_paper_figure import OUTPUT_DPI, compose_figure


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_ROOT = REPO_ROOT / "specific_editing" / "specs" / "single_variable"
SOURCE_ROOT = REPO_ROOT / "specific_editing" / "outputs" / "single_variable"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "specific_editing" / "paper_figures"
VIEW_KEY = "closed__front_iso"
STRENGTHS = (0.7, 0.8)
PAPER_ROWS = (
    ("table_football", "component"),
    ("fence", "count"),
    ("playground_chair_swing_carousel", "material"),
    ("cabinet_paper_showcase", "size"),
)


def _scene_frame(payload: dict[str, object]) -> SceneFrame:
    half_extents = payload.get("half_extents")
    return SceneFrame(
        center=tuple(payload["center"]),  # type: ignore[arg-type]
        radius=float(payload["radius"]),
        half_extents=tuple(half_extents) if half_extents is not None else None,  # type: ignore[arg-type]
    )


def _relative_render_path(*, variant_id: str | None = None) -> Path:
    if variant_id is None:
        return Path("base") / "renders" / f"{VIEW_KEY}.png"
    return Path("variants") / variant_id / "renders" / f"{VIEW_KEY}.png"


def _render_strength_pair(
    model: object,
    *,
    frame: SceneFrame,
    front_axis: str,
    relative_path: Path,
    strength_roots: dict[float, Path],
    image_size: tuple[int, int],
    supersample: int,
) -> None:
    destinations = {
        strength: root / relative_path for strength, root in strength_roots.items()
    }
    meshes = extract_visual_meshes(model, pose="closed")
    _render_blender_batch(
        meshes,
        (("front_iso", destinations[STRENGTHS[0]]),),
        front_axis=front_axis,
        frame=frame,
        image_size=image_size,
        supersample=supersample,
        background=(255, 255, 255),
        shadow_strength=STRENGTHS[0],
        additional_shadow_outputs={
            STRENGTHS[1]: (destinations[STRENGTHS[1]],),
        },
    )


def _write_minimal_manifest(
    *,
    root: Path,
    edit_kind: str,
    variant_ids: list[str],
) -> None:
    payload = {
        "base": {"renders": {VIEW_KEY: str(_relative_render_path())}},
        "variants": [
            {
                "variant": {"kind": edit_kind},
                "renders": {
                    VIEW_KEY: str(_relative_render_path(variant_id=variant_id))
                },
            }
            for variant_id in variant_ids
        ],
    }
    (root / "manifest.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def _render_row(
    asset_name: str,
    edit_kind: str,
    *,
    build_root: Path,
    strength_asset_roots: dict[float, Path],
) -> None:
    spec, _summary = validate_spec(SPEC_ROOT / f"{asset_name}.json")
    variants = [variant for variant in spec.variants if variant.kind == edit_kind]
    if len(variants) != 3:
        raise RuntimeError(f"{asset_name}:{edit_kind} needs three variants")

    source_manifest = json.loads((SOURCE_ROOT / asset_name / "manifest.json").read_text())
    frame_payload = source_manifest.get("comparison_frames", {}).get(
        edit_kind, source_manifest["shared_frame"]
    )
    frame = _scene_frame(frame_payload)
    registration = get_generator(spec.generator_id)
    per_strength_roots = {
        strength: asset_root / asset_name
        for strength, asset_root in strength_asset_roots.items()
    }

    base_config = registration.make_config(spec.base_config, seed=spec.seed)
    base_model = registration.build(
        base_config, assets=AssetContext(build_root / asset_name / "base")
    )
    base_model.meta["specific_editing_generator_id"] = spec.generator_id
    _render_strength_pair(
        base_model,
        frame=frame,
        front_axis=registration.front_axis,
        relative_path=_relative_render_path(),
        strength_roots=per_strength_roots,
        image_size=spec.image_size,
        supersample=spec.supersample,
    )
    del base_model
    gc.collect()

    for variant in variants:
        built = build_variant(
            spec, variant, build_root / asset_name / "variants" / variant.variant_id
        )
        _render_strength_pair(
            built.object_model,
            frame=frame,
            front_axis=registration.front_axis,
            relative_path=_relative_render_path(variant_id=variant.variant_id),
            strength_roots=per_strength_roots,
            image_size=spec.image_size,
            supersample=spec.supersample,
        )
        del built
        gc.collect()

    variant_ids = [variant.variant_id for variant in variants]
    for strength, asset_root in strength_asset_roots.items():
        row_root = asset_root / asset_name
        _write_minimal_manifest(
            root=row_root,
            edit_kind=edit_kind,
            variant_ids=variant_ids,
        )
        if edit_kind == "count":
            make_comparison_sheets(
                base_label="Base",
                base_images={VIEW_KEY: row_root / _relative_render_path()},
                variants=[
                    (
                        variant.label,
                        {
                            VIEW_KEY: row_root
                            / _relative_render_path(variant_id=variant.variant_id)
                        },
                    )
                    for variant in variants
                ],
                output_dir=row_root / "comparisons" / edit_kind,
                size=(1000, 700),
                columns=4,
                padding=22,
                compact_foreground=True,
                normalize_foreground=True,
            )
        print(f"rendered {asset_name}:{edit_kind} at {strength:.1f}", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(
        prefix="directed-editing-shadow-variants-", dir="/tmp"
    ) as temporary_text:
        temporary_root = Path(temporary_text)
        build_root = temporary_root / "build"
        strength_asset_roots = {
            strength: temporary_root / f"shadow_{strength:.1f}" / "specific_editing"
            for strength in STRENGTHS
        }
        for asset_name, edit_kind in PAPER_ROWS:
            _render_row(
                asset_name,
                edit_kind,
                build_root=build_root,
                strength_asset_roots=strength_asset_roots,
            )

        for strength, asset_root in strength_asset_roots.items():
            image = compose_figure(asset_root=asset_root)
            destination = output_dir / f"directed_3d_editing_shadow_{strength:.1f}.png"
            image.save(destination, dpi=(OUTPUT_DPI, OUTPUT_DPI), optimize=True)
            image.close()
            print(destination, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
