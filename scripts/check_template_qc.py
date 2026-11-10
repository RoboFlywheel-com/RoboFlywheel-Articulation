# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import argparse
import importlib
from pathlib import Path

from agent.template_registry import TEMPLATE_REGISTRY
from sdk import AssetContext
from sdk._core.v0.testing import TestContext

DEFAULT_SLUGS = (
    "barrier_gate_boom",
    "barrier_gate_leaf_gate",
    "bicycle_crankset_and_pedal_assembly",
    "blender_countertop",
    "immersion_blender",
    "box_fan_with_control_knob",
    "camcorder_with_flipout_screen",
    "camera_flash",
    "camera_lens",    "cantilever_articulated_arm",
    "car_sunroof_cassette_soft_top",    "ceiling_fan",
    "ceiling_light_fixture_adjustable",
    "chest_freezer_with_hinged_lid",
    "coaxial_rotary_stack",
    "crane_tower",
    "desk_with_drawer",
    "desk_with_drawer_card_catalog",
    "desktop_monitor_with_tilt_swivel_stand",
    "desktop_pc_tower",
)


def _parse_seeds(spec: str) -> list[int]:
    seeds: list[int] = []
    for chunk in spec.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            start_s, end_s = chunk.split("-", 1)
            start = int(start_s)
            end = int(end_s)
            if end < start:
                raise ValueError(f"Invalid seed range: {chunk}")
            seeds.extend(range(start, end + 1))
        else:
            seeds.append(int(chunk))
    if not seeds:
        raise ValueError("At least one seed is required")
    return seeds


def _run_qc(slug: str, seed: int, asset_root: Path) -> list[tuple[str, str]]:
    stem = TEMPLATE_REGISTRY[slug]
    module = importlib.import_module(f"agent.templates.{slug}")
    assets = AssetContext(asset_root / slug / f"seed_{seed}")
    config = module.config_from_seed(seed)
    model = getattr(module, f"build_{stem}")(config, assets=assets)

    ctx = TestContext(model, asset_root=assets.root)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
    report = ctx.report()
    return [(failure.name, failure.details) for failure in report.failures]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slugs", default=",".join(DEFAULT_SLUGS))
    parser.add_argument("--seeds", default="0-2")
    parser.add_argument(
        "--asset-root", type=Path, default=Path("/tmp/articraft_template_qc_assets")
    )
    args = parser.parse_args()

    slugs = [slug.strip() for slug in args.slugs.split(",") if slug.strip()]
    seeds = _parse_seeds(args.seeds)
    missing = [slug for slug in slugs if slug not in TEMPLATE_REGISTRY]
    if missing:
        raise SystemExit(f"Unknown template slug(s): {', '.join(missing)}")

    failure_count = 0
    for slug in slugs:
        slug_failures = 0
        for seed in seeds:
            failures = _run_qc(slug, seed, args.asset_root)
            if not failures:
                continue
            slug_failures += len(failures)
            print(f"\n## {slug} seed={seed}")
            for name, details in failures:
                first_line = details.splitlines()[0] if details else ""
                print(f"- {name}: {first_line}")
        if slug_failures:
            failure_count += slug_failures

    if failure_count:
        print(f"\nQC failed with {failure_count} failure(s).")
        return 1
    print("QC passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
