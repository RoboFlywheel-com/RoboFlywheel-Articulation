# SPDX-License-Identifier: Apache-2.0

"""Per-record picture/小类 binding.

The picture subcategory (小类) a record belongs to is stored deterministically as a
per-record sidecar ``data/records/<id>/picture.json`` instead of being fuzzy-inferred
from prompt text into a global index. The sidecar is the single source of truth:

- written explicitly at creation (``external init --picture picture/<大类>/<小类>/x.png``),
- inherited (copied) onto fork children so variants are self-contained,
- backfilled once for the legacy workbench originals.

Resolution falls back along record lineage (origin/parent) for records that predate
their own sidecar, so the viewer and the shard index always find a 小类 when one exists.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from storage.repo import StorageRepo

# Matches a reference image path anywhere in a string, e.g.
# "picture/Chair/Folding chair/001.png". Subcategory names may contain spaces.
_PICTURE_PATH_RE = re.compile(
    r"picture/[^\n\r\"'`]+?\.(?:png|jpe?g|webp|gif)",
    re.IGNORECASE,
)

BindingSource = str  # "explicit" | "inherited" | "backfill"


@dataclass(slots=True, frozen=True)
class PictureBinding:
    category: str
    subcategory: str
    path: str | None = None
    source: BindingSource = "explicit"

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "category": self.category,
            "subcategory": self.subcategory,
            "source": self.source,
        }
        if self.path:
            payload["path"] = self.path
        return payload


def _clean(value: Any) -> str | None:
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return None


def picture_path_to_subcat(path: str) -> tuple[str, str] | None:
    """Parse ``picture/<大类>/<小类>/<file>`` -> (category, subcategory).

    Accepts the path embedded anywhere in a larger string (e.g. a prompt).
    """
    text = (path or "").strip()
    if not text:
        return None
    match = _PICTURE_PATH_RE.search(text)
    candidate = match.group(0) if match else text
    parts = PurePosixPath(candidate.replace("\\", "/")).parts
    # Expect at least picture / <大类> / <小类> / <file>
    if len(parts) < 4 or parts[0] != "picture":
        return None
    category = parts[1].strip()
    subcategory = parts[2].strip()
    if not category or not subcategory:
        return None
    return category, subcategory


def binding_from_picture_path(
    path: str, *, source: BindingSource = "explicit"
) -> PictureBinding | None:
    parsed = picture_path_to_subcat(path)
    if parsed is None:
        return None
    category, subcategory = parsed
    match = _PICTURE_PATH_RE.search((path or "").strip())
    canonical = match.group(0) if match else None
    return PictureBinding(category=category, subcategory=subcategory, path=canonical, source=source)


def read_binding(repo: StorageRepo, record_id: str) -> PictureBinding | None:
    data = repo.read_json(repo.layout.record_picture_path(record_id))
    if not isinstance(data, dict):
        return None
    category = _clean(data.get("category"))
    subcategory = _clean(data.get("subcategory"))
    if category is None or subcategory is None:
        return None
    return PictureBinding(
        category=category,
        subcategory=subcategory,
        path=_clean(data.get("path")),
        source=_clean(data.get("source")) or "explicit",
    )


def write_binding(repo: StorageRepo, record_id: str, binding: PictureBinding) -> Path:
    path = repo.layout.record_picture_path(record_id)
    repo.write_json(path, binding.to_dict())
    return path


def _record_lineage(
    repo: StorageRepo, record_id: str, record: dict | None
) -> tuple[str | None, str | None]:
    if not isinstance(record, dict):
        record = repo.read_json(repo.layout.record_metadata_path(record_id)) or {}
    lineage = record.get("lineage") if isinstance(record.get("lineage"), dict) else {}
    return _clean(lineage.get("origin_record_id")), _clean(lineage.get("parent_record_id"))


def resolve_binding(
    repo: StorageRepo,
    record_id: str,
    *,
    record: dict | None = None,
    origin_record_id: str | None = None,
    parent_record_id: str | None = None,
) -> PictureBinding | None:
    """Resolve a record's 小类 binding: own sidecar, then origin, then parent."""
    own = read_binding(repo, record_id)
    if own is not None:
        return own
    if origin_record_id is None and parent_record_id is None:
        origin_record_id, parent_record_id = _record_lineage(repo, record_id, record)
    for candidate in (origin_record_id, parent_record_id):
        if candidate and candidate != record_id:
            inherited = read_binding(repo, candidate)
            if inherited is not None:
                return inherited
    return None


def inherit_picture_binding(
    repo: StorageRepo,
    *,
    child_record_id: str,
    parent_record_id: str,
) -> PictureBinding | None:
    """Copy the parent's resolved binding onto the fork child (self-contained variant).

    No-op when the parent has no binding (child stays unbound; the viewer falls back
    to lineage/map resolution). Never overwrites an existing child binding.
    """
    if read_binding(repo, child_record_id) is not None:
        return None
    parent_binding = resolve_binding(repo, parent_record_id)
    if parent_binding is None:
        return None
    child_binding = PictureBinding(
        category=parent_binding.category,
        subcategory=parent_binding.subcategory,
        path=parent_binding.path,
        source="inherited",
    )
    write_binding(repo, child_record_id, child_binding)
    return child_binding


def bind_input_picture(repo: StorageRepo, record_id: str, image_path: Path | None) -> None:
    """Bind canonical workspace images; leave arbitrary image inputs uncategorized."""
    if image_path is None or read_binding(repo, record_id) is not None:
        return
    try:
        relative = image_path.resolve().relative_to(repo.root).as_posix()
    except ValueError:
        return
    binding = binding_from_picture_path(relative)
    if binding is not None:
        write_binding(repo, record_id, binding)
        from storage.subcat_index import build_subcat_index

        build_subcat_index(repo)
