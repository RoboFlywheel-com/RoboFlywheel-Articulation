# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass

from storage.datasets import DatasetStore
from storage.repo import StorageRepo


@dataclass(slots=True)
class ManifestStore:
    repo: StorageRepo
    datasets: DatasetStore

    def dataset_manifest(self) -> dict:
        return self.datasets.dataset_manifest()

    def write_dataset_manifest(self) -> dict:
        manifest = self.dataset_manifest()
        self.repo.write_json(self.repo.layout.dataset_manifest_path(), manifest)
        return manifest
