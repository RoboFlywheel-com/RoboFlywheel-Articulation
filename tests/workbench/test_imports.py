# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

from cli.workbench import main as workbench_main
from storage.repo import StorageRepo


def test_workbench_imports() -> None:
    assert callable(workbench_main)
    repo = StorageRepo(Path.cwd())
    assert repo.layout.runs_root.name == "runs"
