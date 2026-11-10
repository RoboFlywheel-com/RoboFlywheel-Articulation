#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Split one locked BlenderKit plan into independently syncable category plans."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = ROOT.parent
DOWNLOADER_PATH = WORKSPACE_ROOT / "download_blenderkit_materials.py"
SPEC = importlib.util.spec_from_file_location("download_blenderkit_materials", DOWNLOADER_PATH)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError(f"cannot load downloader: {DOWNLOADER_PATH}")
DOWNLOADER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DOWNLOADER
SPEC.loader.exec_module(DOWNLOADER)


SCHEMA_VERSION = "articraft-blenderkit-category-plan-bundle/v1"
DEFAULT_CATEGORY_ORDER = (
    "metal",
    "wood",
    "fabric",
    "plastic",
    "glass",
    "rubber",
    "stone",
    "concrete",
    "ceramic",
    "leather",
    "organic",
    "tech",
    "paper",
    "marble",
    "plaster",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def split_plan_by_category(
    plan_path: Path,
    output_dir: Path,
    *,
    category_order: Sequence[str] = DEFAULT_CATEGORY_ORDER,
) -> dict[str, Any]:
    source_path = plan_path.resolve(strict=True)
    source = DOWNLOADER._load_locked_plan(source_path)
    materials = source["materials"]
    actual_categories = {str(row["category_slug"]) for row in materials}
    ordered_categories = tuple(dict.fromkeys(category_order))
    if len(ordered_categories) != len(category_order):
        raise ValueError("category_order contains duplicates")
    if set(ordered_categories) != actual_categories:
        missing = sorted(actual_categories - set(ordered_categories))
        extra = sorted(set(ordered_categories) - actual_categories)
        raise ValueError(f"category_order mismatch: missing={missing}, extra={extra}")

    destination = output_dir.resolve()
    entries: list[dict[str, Any]] = []
    seen_material_ids: set[str] = set()
    total_bytes = 0
    for sequence, category_slug in enumerate(ordered_categories, 1):
        category_materials = [
            deepcopy(row) for row in materials if row["category_slug"] == category_slug
        ]
        category_profiles = [
            deepcopy(row) for row in source["profiles"] if row["category_slug"] == category_slug
        ]
        if not category_materials or not category_profiles:
            raise ValueError(f"category {category_slug!r} has no material/profile rows")
        material_ids = {str(row["material_id"]) for row in category_materials}
        if seen_material_ids & material_ids:
            raise ValueError(f"category {category_slug!r} reuses a material ID")
        seen_material_ids.update(material_ids)
        expected_bytes = sum(
            int(row["selected_file"]["expected_size_bytes"]) for row in category_materials
        )
        total_bytes += expected_bytes

        child = deepcopy(source)
        child["materials"] = category_materials
        child["profiles"] = category_profiles
        child["selected_count"] = len(category_materials)
        child["expected_download_bytes"] = expected_bytes
        child["shortfall"] = sum(int(row.get("shortfall") or 0) for row in category_profiles)
        child["parent_plan_sha256"] = source["plan_sha256"]
        child["bundle_category_slug"] = category_slug
        child["bundle_sequence"] = sequence
        child["plan_sha256"] = DOWNLOADER._plan_content_sha256(child)

        plan_name = f"{sequence:02d}_{category_slug}.json"
        child_path = destination / plan_name
        _atomic_json(child_path, child)
        reopened = DOWNLOADER._load_locked_plan(child_path)
        if reopened["plan_sha256"] != child["plan_sha256"]:
            raise ValueError(f"failed to verify category plan: {child_path}")
        entries.append(
            {
                "sequence": sequence,
                "category_slug": category_slug,
                "plan_path": plan_name,
                "plan_file_sha256": _sha256(child_path),
                "plan_sha256": child["plan_sha256"],
                "material_count": len(category_materials),
                "expected_download_bytes": expected_bytes,
            }
        )

    if seen_material_ids != {str(row["material_id"]) for row in materials}:
        raise ValueError("split plans do not conserve parent material IDs")
    if total_bytes != int(source["expected_download_bytes"]):
        raise ValueError("split plans do not conserve parent download bytes")

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "source_plan_path": os.fspath(source_path),
        "source_plan_file_sha256": _sha256(source_path),
        "source_plan_sha256": source["plan_sha256"],
        "category_count": len(entries),
        "material_count": len(materials),
        "expected_download_bytes": total_bytes,
        "categories": entries,
    }
    _atomic_json(destination / "manifest.json", manifest)
    return manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--category-order",
        nargs="+",
        default=list(DEFAULT_CATEGORY_ORDER),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    manifest = split_plan_by_category(
        args.plan,
        args.output_dir,
        category_order=args.category_order,
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
