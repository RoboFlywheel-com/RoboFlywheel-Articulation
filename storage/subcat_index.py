# SPDX-License-Identifier: Apache-2.0

"""Workbench-scoped, per-小类 shard index for the picture→variant→template pipeline.

The workbench grid only ever shows the ~1k workbench-collection records (picture
originals + fork variants), not the ~10k curated dataset. Instead of rebuilding the
16MB global ``records_index.jsonl`` (a full 12k-record scan) to surface them, this
keeps one slim shard per picture subcategory:

    data/index/subcat/<大类>__<小类>.jsonl      # rows for that 小类
    data/index/subcat/_unassigned.jsonl         # workbench records with no 小类 yet

Each parallel agent works on one 小类, so a 10-way fan-out writes 10 disjoint shard
files — no global-index contention. Membership is read from the per-record workbench
sidecars (glob of ~1k files) rather than scanning every record.json.
"""

from __future__ import annotations

import json
import re
from typing import Any, Iterator

from storage.lfs_pointers import is_lfs_pointer_file
from storage.picture_binding import resolve_binding
from storage.repo import StorageRepo, atomic_write_text

UNASSIGNED_SHARD = "_unassigned"

_SHARD_SANITIZE_RE = re.compile(r"[^0-9A-Za-z一-鿿._-]+")


def shard_name(category: str | None, subcategory: str | None) -> str:
    if not category or not subcategory:
        return UNASSIGNED_SHARD
    raw = f"{category}__{subcategory}"
    cleaned = _SHARD_SANITIZE_RE.sub("_", raw).strip("_")
    return cleaned or UNASSIGNED_SHARD


def _coerce_str(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def iter_workbench_records(repo: StorageRepo) -> Iterator[tuple[str, dict, dict]]:
    """Yield (record_id, record.json, workbench sidecar) for every workbench record.

    Membership comes from the per-record ``collections/workbench.json`` sidecars, so
    this reads ~1k small files instead of scanning every record.json on disk.
    """
    records_root = repo.layout.records_root
    if not records_root.is_dir():
        return
    for sidecar_path in sorted(records_root.glob("*/collections/workbench.json")):
        record_id = sidecar_path.parent.parent.name
        record_path = repo.layout.record_metadata_path(record_id)
        if not record_path.exists() or is_lfs_pointer_file(record_path):
            continue
        record = repo.read_json(record_path)
        if not isinstance(record, dict):
            continue
        collections = record.get("collections")
        if not (isinstance(collections, list) and "workbench" in collections):
            continue
        sidecar = repo.read_json(sidecar_path, default={})
        yield record_id, record, sidecar if isinstance(sidecar, dict) else {}


def _build_row(repo: StorageRepo, record_id: str, record: dict, sidecar: dict) -> tuple[str, dict]:
    lineage = record.get("lineage") if isinstance(record.get("lineage"), dict) else {}
    origin_record_id = _coerce_str(lineage.get("origin_record_id"))
    parent_record_id = _coerce_str(lineage.get("parent_record_id"))
    binding = resolve_binding(
        repo,
        record_id,
        record=record,
        origin_record_id=origin_record_id,
        parent_record_id=parent_record_id,
    )
    display = record.get("display") if isinstance(record.get("display"), dict) else {}
    row = {
        "record_id": record_id,
        "kind": _coerce_str(record.get("kind")),
        "title": _coerce_str(display.get("title")) or record_id,
        "rating": record.get("rating"),
        "origin_record_id": origin_record_id,
        "parent_record_id": parent_record_id,
        "picture_category": binding.category if binding else None,
        "picture_subcategory": binding.subcategory if binding else None,
        "picture_path": binding.path if binding else None,
        "added_at": _coerce_str(sidecar.get("added_at")),
        "label": _coerce_str(sidecar.get("label")),
        "archived": bool(sidecar.get("archived", False)),
    }
    name = shard_name(row["picture_category"], row["picture_subcategory"])
    return name, row


def _write_shard(repo: StorageRepo, name: str, rows: list[dict]) -> None:
    rows_sorted = sorted(rows, key=lambda r: str(r.get("added_at") or ""), reverse=True)
    text = "".join(
        json.dumps(row, separators=(",", ":"), sort_keys=True, ensure_ascii=False) + "\n"
        for row in rows_sorted
    )
    atomic_write_text(repo.layout.subcat_shard_path(name), text)


def build_subcat_index(repo: StorageRepo) -> dict[str, int]:
    """Rebuild every shard from current workbench membership. Single-writer (reconcile).

    Returns a mapping shard_name -> row count. Removes shards that no longer have rows.
    """
    grouped: dict[str, list[dict]] = {}
    for record_id, record, sidecar in iter_workbench_records(repo):
        name, row = _build_row(repo, record_id, record, sidecar)
        grouped.setdefault(name, []).append(row)

    root = repo.layout.subcat_index_root
    root.mkdir(parents=True, exist_ok=True)
    # Drop stale shards (a 小类 that lost all its records) before writing fresh ones.
    for existing in root.glob("*.jsonl"):
        if existing.stem not in grouped:
            existing.unlink()
    for name, rows in grouped.items():
        _write_shard(repo, name, rows)
    return {name: len(rows) for name, rows in sorted(grouped.items())}


def load_subcat_index(repo: StorageRepo) -> list[dict]:
    """Read every shard row (the whole workbench population)."""
    root = repo.layout.subcat_index_root
    if not root.is_dir():
        return []
    rows: list[dict] = []
    for shard in sorted(root.glob("*.jsonl")):
        for line in shard.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(row, dict) and row.get("record_id"):
                rows.append(row)
    return rows


def subcat_index_signature(repo: StorageRepo) -> int | None:
    """Max mtime across shards, for cache invalidation (None if no index)."""
    root = repo.layout.subcat_index_root
    if not root.is_dir():
        return None
    mtimes = [shard.stat().st_mtime_ns for shard in root.glob("*.jsonl")]
    return max(mtimes) if mtimes else None
