# SPDX-License-Identifier: Apache-2.0

"""Import source records without rewriting ratings, revisions, or collection metadata."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

from rfwa.revision import write_json


def import_record(source_root: Path, destination_root: Path, record_id: str) -> Path:
    if not re.fullmatch(r"rec_[A-Za-z0-9_.-]+", record_id) or ".." in record_id:
        raise ValueError("expected a record ID such as rec_example")
    source = source_root / "data" / "records" / record_id
    destination = destination_root / "data" / "records" / record_id
    if source.is_symlink():
        raise ValueError("source record must not be a symlink")
    if not source.is_dir() or not (source / "record.json").is_file():
        raise ValueError(f"source record is missing: {source}")
    if source.resolve() == destination.resolve() or destination.exists():
        raise FileExistsError(f"record already exists: {destination}")
    # A portable import must not silently read files outside its source record.
    for entry in source.rglob("*"):
        if entry.is_symlink():
            raise ValueError(f"source record contains a symlink: {entry.relative_to(source)}")
    # Preserve the referenced category image as well as record-local inputs.
    picture_source = None
    picture_target = None
    picture_status = "unbound"
    picture_sha256 = None
    sidecar = source / "picture.json"
    if sidecar.is_file():
        binding = json.loads(sidecar.read_text())
        if not isinstance(binding, dict):
            raise ValueError("picture binding must be a JSON object")
        picture_path = binding.get("path")
        if picture_path is not None and not isinstance(picture_path, str):
            raise ValueError("reference picture path must be a string")
        if picture_path:
            relative = Path(picture_path)
            if (
                not relative.parts
                or relative.is_absolute()
                or ".." in relative.parts
                or relative.parts[0] != "picture"
            ):
                raise ValueError("unsafe picture binding path")
            picture_source = source_root / relative
            picture_target = destination_root / relative
            if picture_source.is_symlink() or not picture_source.resolve().is_relative_to(
                source_root.resolve()
            ):
                raise ValueError("reference picture must stay within the source workspace")
            if picture_source.is_file():
                if (
                    picture_target.exists()
                    and picture_target.read_bytes() != picture_source.read_bytes()
                ):
                    raise FileExistsError(
                        f"different reference picture already exists: {picture_target}"
                    )
                picture_status = "copied"
                picture_sha256 = hashlib.sha256(picture_source.read_bytes()).hexdigest()
            else:
                picture_status = "missing_in_source"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="rfwa-import-", dir=destination.parent) as raw:
        staged = Path(raw) / record_id
        shutil.copytree(source, staged)
        hashes = {
            p.relative_to(staged).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(staged.rglob("*"))
            if p.is_file()
        }
        if destination.exists():
            raise FileExistsError(f"record appeared during import: {destination}")
        # Copy the reference before committing the record. A failed image copy
        # must leave the record ID available for retry, rather than half-imported.
        if picture_status == "copied":
            picture_target.parent.mkdir(parents=True, exist_ok=True)
            if not picture_target.exists():
                shutil.copy2(picture_source, picture_target)
        staged.rename(destination)
    from storage.repo import StorageRepo
    from storage.subcat_index import build_subcat_index

    build_subcat_index(StorageRepo(destination_root))
    write_json(
        destination_root / "data" / "source_imports" / f"{record_id}.json",
        {
            "schema": "rfwa-source-import/v1",
            "record_id": record_id,
            "files": hashes,
            "metadata_preserved": True,
            "reference_picture": picture_status,
            "reference_picture_sha256": picture_sha256,
        },
    )
    return destination
