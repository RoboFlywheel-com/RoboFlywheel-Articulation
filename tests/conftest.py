# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# pytest-xdist already provides process-level parallelism.  Keep native numeric
# libraries single-threaded so each worker does not create another CPU-sized
# thread pool during collection or CAD checks.
for _thread_env in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[_thread_env] = "1"

REPO_ROOT = Path(__file__).resolve().parents[1]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# --- Known-failure baseline (diff-regression) --------------------------------
#
# `tests/known_failures.txt` lists test node ids that were already failing
# before the current change (one per line, `#` comments allowed). They are
# marked xfail (non-strict) so the suite goes green on pre-existing debt and
# ONLY NEW failures are attributed to the change under test. A baseline test
# that starts passing shows up as XPASS — prune it from the file to shrink the
# baseline. Do not add new entries to hide a failure your change introduced.

_KNOWN_FAILURES_PATH = Path(__file__).with_name("known_failures.txt")


def _load_known_failures() -> frozenset[str]:
    try:
        lines = _KNOWN_FAILURES_PATH.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return frozenset()
    entries = set()
    for line in lines:
        text = line.strip()
        if text and not text.startswith("#"):
            entries.add(text)
    return frozenset(entries)


def pytest_collection_modifyitems(config, items):  # noqa: ARG001 - pytest hook signature
    known = _load_known_failures()
    if not known:
        return
    for item in items:
        if item.nodeid in known:
            item.add_marker(
                pytest.mark.xfail(
                    reason="known-failure baseline (tests/known_failures.txt)",
                    strict=False,
                )
            )
