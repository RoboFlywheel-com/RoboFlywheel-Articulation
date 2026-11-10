# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

LFS_POINTER_HEADER = "version https://git-lfs.github.com/spec/v1"


def is_lfs_pointer_file(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False
    try:
        if path.stat().st_size > 1024:
            return False
        with path.open("rb") as handle:
            first_line = handle.readline(256).decode("utf-8", errors="replace").strip()
    except OSError:
        return False
    return first_line == LFS_POINTER_HEADER
