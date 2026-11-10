# SPDX-License-Identifier: Apache-2.0

"""Health-check for the picture→小类→资产 binding system (read-only).

The live workbench groups assets by each record's ``picture.json`` sidecar (written by
``external seed`` / fork inheritance / backfill) — the single source of truth. A record
is only correctly placed when it has a sidecar pointing at a real ``picture/<大类>/<小类>/``
folder. This doctor surfaces every way that contract can break, so adding new 小类 /
pictures / 资产 stays accurate.

Checks (all read-only):
  A. Binding coverage  — workbench records with NO sidecar (would be uncategorized).
  B. Bad pointers      — sidecar whose (大类/小类) has no picture/ folder, or whose image is gone.
  C. Structure lints   — 小类 slug collisions across 大类 (breaks the slug fallback),
                         picture 小类 with images but ZERO 资产 (seed candidates), empty folders.

Exit code is non-zero when a HARD problem exists (A unbound, B bad pointer). Structure
lints (C) are advisory and never fail the run.

    uv run python scripts/picture_doctor.py            # full report
    uv run python scripts/picture_doctor.py --quiet    # summary + problems only
    uv run python scripts/picture_doctor.py --limit 50 # cap per-list output
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from storage.picture_binding import read_binding
from storage.repo import StorageRepo
from storage.subcat_index import iter_workbench_records

_IMG_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


def _walk_picture_folders(picture_root: Path) -> dict[tuple[str, str], int]:
    """(大类, 小类) -> image count, straight from the picture/ tree."""
    found: dict[tuple[str, str], int] = {}
    if not picture_root.is_dir():
        return found
    for cat_dir in sorted(p for p in picture_root.iterdir() if p.is_dir()):
        for sub_dir in sorted(p for p in cat_dir.iterdir() if p.is_dir()):
            n = sum(1 for f in sub_dir.iterdir() if f.is_file() and f.suffix.lower() in _IMG_EXTS)
            found[(cat_dir.name, sub_dir.name)] = n
    return found


def _print_list(title: str, rows: list[str], limit: int) -> None:
    print(f"\n{title}  ({len(rows)})")
    if not rows:
        print("    none")
        return
    for r in rows[:limit]:
        print(f"    {r}")
    if len(rows) > limit:
        print(f"    … +{len(rows) - limit} more (raise --limit to see all)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--limit", type=int, default=30, help="Max rows per problem list.")
    parser.add_argument("--quiet", action="store_true", help="Summary + problems only.")
    args = parser.parse_args()

    repo = StorageRepo(args.repo_root.resolve())
    picture_root = repo.root / "picture"
    folders = _walk_picture_folders(picture_root)
    valid_subcats = set(folders)

    records = list(iter_workbench_records(repo))

    unbound: list[str] = []
    bad_folder: list[str] = []
    bad_image: list[str] = []
    assets_per_subcat: dict[tuple[str, str], int] = defaultdict(int)

    for record_id, _record, _sidecar in records:
        binding = read_binding(repo, record_id)
        if binding is None:
            unbound.append(record_id)
            continue
        key = (binding.category, binding.subcategory)
        assets_per_subcat[key] += 1

        # B. bad pointer — 小类 folder must exist; image (if named) must exist on disk.
        if key not in valid_subcats:
            bad_folder.append(
                f"{record_id}  ->  {binding.category}/{binding.subcategory} (no picture/ folder)"
            )
        if binding.path:
            if not (repo.root / binding.path).is_file():
                bad_image.append(f"{record_id}  ->  {binding.path} (image missing)")

    # C. structure lints -----------------------------------------------------
    # 小类 slug collisions across 大类 — breaks the slug fallback in store_picture.
    slug_owners: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for c, s in folders:
        slug = s.lower().strip().replace(" ", "_")
        slug_owners[slug].add((c, s))
    slug_collisions = [
        f"{slug}: " + ", ".join(f"{c}/{s}" for c, s in sorted(pairs))
        for slug, pairs in slug_owners.items()
        if len(pairs) > 1
    ]

    empty_folders = [f"{c}/{s}" for (c, s), n in sorted(folders.items()) if n == 0]
    seedless = [
        f"{c}/{s} ({n} img)"
        for (c, s), n in sorted(folders.items())
        if n > 0 and assets_per_subcat.get((c, s), 0) == 0
    ]

    # ------------------------------------------------------------------------
    bound = len(records) - len(unbound)
    hard = len(unbound) + len(bad_folder) + len(bad_image)

    print("=" * 68)
    print("picture / 小类 / 资产 binding doctor")
    print("=" * 68)
    print(
        f"picture 大类: {len({c for c, _ in folders})}   小类 folders: {len(folders)}   带图小类: "
        f"{sum(1 for n in folders.values() if n > 0)}"
    )
    print(f"workbench 资产: {len(records)}   有 sidecar: {bound}   无 sidecar: {len(unbound)}")
    print(
        f"\nHARD problems: {hard}   (unbound={len(unbound)} bad_folder={len(bad_folder)} "
        f"bad_image={len(bad_image)})"
    )
    print(
        f"advisory: 小类collision={len(slug_collisions)}  "
        f"empty_folder={len(empty_folders)}  seedless={len(seedless)}"
    )

    # --- HARD ---
    _print_list("[A] 无 sidecar 的 workbench 资产 (会变成未归类)", unbound, args.limit)
    _print_list("[B] sidecar 指向不存在的 小类 folder", bad_folder, args.limit)
    _print_list("[B] sidecar 指向不存在的图片文件", bad_image, args.limit)

    if not args.quiet:
        # --- advisory ---
        _print_list("[C] 小类 slug 跨大类冲突 (会废掉 slug 兜底)", slug_collisions, args.limit)
        _print_list("[C] 有图但 0 资产的 小类 (待造 seed 的候选)", seedless, args.limit)
        _print_list("[C] 空文件夹 (无图的 小类)", empty_folders, args.limit)

    print()
    if hard:
        print(f"FAIL: {hard} hard problem(s). 修复后重跑。")
        return 1
    print("OK: 无 hard problem(所有 workbench 资产都绑定到真实小类)。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
