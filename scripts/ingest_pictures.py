# SPDX-License-Identifier: Apache-2.0

"""Ingest reference images from a categorized markdown export into picture/<大类>/<小类>/.

The markdown groups images as:  ``## 大类`` → ``### 小类`` → one or more
``![Image](<url>)`` lines.  This walks that structure, downloads each image, and
writes them as ``picture/<大类>/<小类>/001.png`` … in source order. Markdown name
escapes are unescaped; the only path-illegal char ('/') is sanitized to '_'. Every
download is validated as a real PNG. This is the INGEST step (SEGMENT 0) that feeds
the build-template pipeline — it only lays down picture folders + reference images;
it does NOT create any 3D asset (that is `external seed` + authoring).

    # preview the plan only (no downloads):
    uv run python scripts/ingest_pictures.py --md reference-images.md --categories "Healthcare,Agricultural" --dry-run
    # ingest specific 大类 (raw or sanitized name both accepted):
    uv run python scripts/ingest_pictures.py --md reference-images.md --categories "Electrical / Wiring"
    # ingest every 大类 in the markdown:
    uv run python scripts/ingest_pictures.py --md reference-images.md --all

Idempotent: an image whose dest file already exists is skipped unless --force. After
ingesting, run `uv run python scripts/picture_doctor.py` and restart the viewer.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
import urllib.request
from pathlib import Path

IMG_RE = re.compile(r"!\[Image\]\((https?://[^)]+)\)")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def unescape_md(name: str) -> str:
    return re.sub(r"\\(.)", r"\1", name).strip()


def sanitize_folder(name: str) -> str:
    # '/' is the only path-illegal char in these names; spaces/()/- are kept as-is.
    return name.replace(" / ", "_").replace("/", "_").strip()


def parse(md_path: Path, targets: set[str] | None) -> dict[tuple[str, str], list[str]]:
    """(大类folder, 小类folder) -> ordered image URLs. targets=None ⇒ every 大类.

    A 大类 matches when its raw name OR its sanitized folder name is in ``targets``.
    """
    out: dict[tuple[str, str], list[str]] = {}
    cat_raw: str | None = None
    keep = False
    cur: tuple[str, str] | None = None
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            cat_raw = unescape_md(line[3:])
            cat_folder = sanitize_folder(cat_raw)
            keep = targets is None or cat_raw in targets or cat_folder in targets
            cur = None
        elif line.startswith("### "):
            if keep and cat_raw is not None:
                cur = (sanitize_folder(cat_raw), sanitize_folder(unescape_md(line[4:])))
                out.setdefault(cur, [])
            else:
                cur = None
        else:
            m = IMG_RE.search(line)
            if m and cur is not None:
                out[cur].append(m.group(1))
    return out


def download(url: str, dest: Path, attempts: int = 3) -> int:
    last = b""
    for i in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                last = resp.read()
            if last[:8] == PNG_MAGIC:
                dest.write_bytes(last)
                return len(last)
        except Exception as exc:  # noqa: BLE001
            print(f"      attempt {i + 1} failed: {exc}")
            time.sleep(2)
    raise RuntimeError(f"not a valid PNG after {attempts} attempts ({len(last)} bytes)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--md", type=Path, default=Path("reference-images.md"))
    parser.add_argument(
        "--categories",
        default=None,
        help="Comma-separated 大类 to ingest (raw 'Electrical / Wiring' or sanitized "
        "'Electrical_Wiring' both work). Omit with --all to take every 大类.",
    )
    parser.add_argument("--all", action="store_true", help="Ingest every 大类 in the markdown.")
    parser.add_argument("--dry-run", action="store_true", help="Print the plan; download nothing.")
    parser.add_argument("--force", action="store_true", help="Re-download even if dest exists.")
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    md_path = args.md if args.md.is_absolute() else repo / args.md
    if not md_path.is_file():
        print(f"markdown not found: {md_path}")
        return 1
    if not args.all and not args.categories:
        print("specify --categories '<大类>,...' or --all")
        return 1
    targets = None if args.all else {c.strip() for c in args.categories.split(",") if c.strip()}

    plan = parse(md_path, targets)
    if not plan:
        print("no matching 大类/小类 found — check --categories against the markdown headers")
        return 1
    total = sum(len(v) for v in plan.values())
    cats = sorted({c for c, _ in plan})
    print(f"plan: 大类={cats}  小类={len(plan)}  images={total}\n")
    for (cat, sub), urls in plan.items():
        print(f"  {cat}/{sub}  ({len(urls)} img)")
    if args.dry_run:
        print("\n[dry-run] nothing downloaded.")
        return 0

    print()
    ok = skip = fail = 0
    for (cat, sub), urls in plan.items():
        folder = repo / "picture" / cat / sub
        folder.mkdir(parents=True, exist_ok=True)
        print(f"{cat}/{sub}  ({len(urls)} img)")
        for idx, url in enumerate(urls, start=1):
            dest = folder / f"{idx:03d}.png"
            if dest.exists() and not args.force:
                print(f"    {dest.name}: exists, skip")
                skip += 1
                continue
            try:
                n = download(url, dest)
                print(f"    {dest.name}: {n} bytes OK")
                ok += 1
            except Exception as exc:  # noqa: BLE001
                print(f"    {dest.name}: FAILED {exc}")
                fail += 1
    print(f"\ndone: {ok} downloaded, {skip} skipped, {fail} failed, across {len(plan)} 小类")
    if fail == 0:
        print("next: `uv run python scripts/picture_doctor.py`, then restart the :8765 viewer.")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
