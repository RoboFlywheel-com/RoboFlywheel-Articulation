# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    import resource
except ImportError:  # pragma: no cover
    resource = None  # type: ignore[assignment]


@dataclass(slots=True, frozen=True)
class OpenFileWorkerCap:
    worker_cap: int
    soft_limit: int
    open_files: int
    reserve_files: int
    per_worker_budget: int


def open_file_soft_limit() -> int | None:
    if resource is None or not hasattr(resource, "RLIMIT_NOFILE"):
        return None
    try:
        soft_limit, _ = resource.getrlimit(resource.RLIMIT_NOFILE)
    except Exception:
        return None
    if not isinstance(soft_limit, int) or soft_limit <= 0:
        return None
    return soft_limit


def current_open_file_count() -> int | None:
    for fd_root in ("/dev/fd", "/proc/self/fd"):
        try:
            return len(os.listdir(fd_root))
        except OSError:
            continue
    return None


def open_file_worker_cap(
    *,
    reserve_files: int,
    per_worker_budget: int,
) -> OpenFileWorkerCap | None:
    if reserve_files < 0:
        raise ValueError("Reserve file count must be zero or greater.")
    if per_worker_budget <= 0:
        raise ValueError("Per-worker FD budget must be greater than zero.")

    soft_limit = open_file_soft_limit()
    open_files = current_open_file_count()
    if soft_limit is None or open_files is None:
        return None

    usable = soft_limit - open_files - reserve_files
    if usable <= 0:
        worker_cap = 1
    else:
        worker_cap = max(1, usable // per_worker_budget)

    return OpenFileWorkerCap(
        worker_cap=worker_cap,
        soft_limit=soft_limit,
        open_files=open_files,
        reserve_files=reserve_files,
        per_worker_budget=per_worker_budget,
    )
