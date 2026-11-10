# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from storage.layout import StorageLayout
from storage.lfs_pointers import is_lfs_pointer_file


def atomic_write_text(path: Path, text: str) -> None:
    """Write ``text`` to ``path`` atomically (tmp file in the same dir + os.replace).

    Concurrent readers never observe a truncated/half-written file, and two
    concurrent writers degrade to last-writer-wins instead of interleaved bytes.
    This matters for the single-file derived indexes (records_index.jsonl,
    subcat shards) under parallel agent batches.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


@dataclass(slots=True)
class StorageRepo:
    root: Path
    layout: StorageLayout = field(init=False)

    def __post_init__(self) -> None:
        self.root = Path(self.root).resolve()
        self.layout = StorageLayout(self.root)

    def ensure_layout(self) -> None:
        self.layout.ensure_base_dirs()

    def read_json(self, path: Path, *, default: Any = None) -> Any:
        if not path.exists():
            return default
        if is_lfs_pointer_file(path):
            return default
        return json.loads(path.read_text(encoding="utf-8"))

    def write_json(self, path: Path, data: Any) -> None:
        atomic_write_text(path, json.dumps(data, indent=2) + "\n")

    def write_text(self, path: Path, text: str) -> None:
        atomic_write_text(path, text)
