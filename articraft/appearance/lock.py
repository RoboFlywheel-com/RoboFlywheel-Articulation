# SPDX-License-Identifier: Apache-2.0

"""Copy selected packages and write a self-contained appearance lock."""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Iterable

from .retrieval import MATERIAL_CLASS_SELECTION_ALGORITHM, ResolvedAppearance

LOCK_SCHEMA_VERSION = "articraft-appearance-lock/v6"


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _materialize_package(source: Path, destination: Path) -> None:
    if source.is_symlink() or not source.is_file():
        raise ValueError(f"selected material package is not a regular file: {source}")
    source_size = source.stat().st_size
    if source_size <= 0:
        raise ValueError(f"selected material package is empty: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if destination.is_symlink() or not destination.is_file():
            raise ValueError(f"existing material package is not a regular file: {destination}")
        if destination.stat().st_size != source_size:
            raise ValueError(f"existing material package has the wrong size: {destination}")
        return
    temporary = destination.with_name(f".{destination.name}.tmp-{os.getpid()}")
    try:
        try:
            os.link(source, temporary)
        except OSError:
            shutil.copy2(source, temporary)
        if temporary.stat().st_size != source_size:
            raise ValueError(f"material package size changed while copying: {source}")
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def _resolved_material_seed(*, seed: int, material_seed: int | None) -> int:
    return int(seed) if material_seed is None else int(material_seed)


def _resolved_mapping(row: ResolvedAppearance) -> dict[str, Any] | None:
    material = row.material
    if material is None:
        return None
    if material.material_profile == "texture_set":
        texture_size_m = material.texture_size_m
        return {
            "coordinate_space": "object_local_meters",
            "mode": "metric_uv",
            "normal_space": material.normal_space or "tangent",
            "requires_uv": True,
            "texture_size_m": texture_size_m,
            "true_displacement": False,
            "uv_area_density": (
                None if texture_size_m is None else 1.0 / (texture_size_m * texture_size_m)
            ),
            "uv_method": "smart_project",
        }
    if material.material_profile == "native_procedural":
        return {
            "coordinate_space": "material_native",
            "mode": "native_procedural",
            "normal_space": material.normal_space or "native",
            "requires_uv": bool(material.requires_uv),
            "texture_size_m": material.texture_size_m,
            "true_displacement": False,
        }
    raise ValueError(
        f"unsupported material profile in resolved appearance: {material.material_profile!r}"
    )


def materialize_appearance_lock(
    seed_dir: Path,
    resolved: Iterable[ResolvedAppearance],
    *,
    slug: str,
    seed: int,
    material_seed: int | None = None,
    template_sha256: str,
    model_urdf_sha256: str,
    library_snapshot_sha256: str,
    pool_index_sha256: str,
) -> dict[str, Any]:
    root = seed_dir.resolve()
    root.mkdir(parents=True, exist_ok=True)
    material_paths: dict[str, str] = {}
    rows = list(resolved)
    material_rows = [row for row in rows if row.material is not None]
    exact_class_rows = [row for row in rows if row.candidate_pool_material_class_id is not None]
    if len(exact_class_rows) != len(material_rows):
        raise ValueError("appearance lock accepts only exact material-class pools")
    if not library_snapshot_sha256 or not pool_index_sha256:
        raise ValueError("appearance lock requires formal library digests")
    resolved_material_seed = _resolved_material_seed(seed=seed, material_seed=material_seed)
    for row in rows:
        material = row.material
        if material is None or material.material_id in material_paths:
            continue
        suffix = material.blend_path.suffix or ".blend"
        relative = Path("materials") / material.sha256[:16] / f"material{suffix}"
        destination = (root / relative).resolve()
        try:
            destination.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"material destination escapes seed: {destination}") from exc
        _materialize_package(material.blend_path, destination)
        material_paths[material.material_id] = relative.as_posix()

    bindings: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: item.request.surface_key):
        request = row.request
        material = row.material
        binding: dict[str, Any] = {
            "appearance_only": bool(getattr(request, "appearance_only", False)),
            "asset_type": request.asset_type,
            "material_class_id": request.material_class_id,
            "rgba": None if request.rgba is None else list(request.rgba),
            "resolved_mapping": _resolved_mapping(row),
            "selection": (
                None
                if material is None
                else {
                    "candidate_pool_material_class_id": (row.candidate_pool_material_class_id),
                    "candidate_pool_count": row.candidate_pool_count,
                    "candidate_pool_sha256": row.candidate_pool_sha256,
                    "cross_component_avoidance": False,
                    "cross_component_deduplication": False,
                    "draw_order": row.draw_order,
                    "selection_index": row.selection_index,
                }
            ),
            "surface_key": request.surface_key,
        }
        if material is not None:
            if material.physics_ref is None:
                raise ValueError(
                    f"selected material {material.material_id!r} lacks formal physics_ref"
                )
            binding["material"] = {
                "asset_base_id": material.asset_base_id,
                "category_slug": material.category_slug,
                "display_name": material.display_name,
                "license": material.license,
                "material_id": material.material_id,
                "material_profile": material.material_profile,
                "mapping_profile": material.mapping_profile,
                "normal_space": material.normal_space,
                "package_path": material_paths[material.material_id],
                "provider": material.provider,
                "requires_uv": material.requires_uv,
                "sha256": material.sha256,
                "texture_size_m": material.texture_size_m,
                "physics_ref": material.physics_ref.canonical_row(),
            }
        else:
            binding["material"] = None
        bindings.append(binding)
    payload = {
        "schema_version": LOCK_SCHEMA_VERSION,
        "library": {
            "pool_index_sha256": pool_index_sha256,
            "snapshot_sha256": library_snapshot_sha256,
        },
        "model_urdf_sha256": model_urdf_sha256,
        "material_seed": resolved_material_seed,
        "retriever_version": MATERIAL_CLASS_SELECTION_ALGORITHM,
        "seed": int(seed),
        "slug": slug,
        "template_sha256": template_sha256,
        "bindings": bindings,
    }
    _atomic_json(root / "appearance.lock.json", payload)
    return payload
