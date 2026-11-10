# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from storage.repo import StorageRepo


@dataclass(slots=True)
class BatchSpecStore:
    repo: StorageRepo

    def copy_spec(self, source: Path, batch_id: str) -> Path:
        destination = self.repo.layout.batch_spec_path(batch_id)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return destination
