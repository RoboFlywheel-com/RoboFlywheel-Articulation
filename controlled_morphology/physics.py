# SPDX-License-Identifier: Apache-2.0

"""Deterministic physics-only bindings for controlled morphology assets."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

from articraft.appearance.retrieval import appearance_requests_from_model
from articraft.appearance.unified_runtime import (
    PHYSICS_FIELDS,
    UnifiedMaterialLibrary,
    load_unified_material_library,
)

PHYSICS_SCHEMA = "articraft-seed-physics/v1"
SELECTION_ALGORITHM = "canonical-class-pool-first/v1"


@cache
def _load_library(pointer_path: Path) -> UnifiedMaterialLibrary:
    return load_unified_material_library(pointer_path)


def default_library_pointer() -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    return repo_root / "pbr_material_library" / "unified" / "latest.json"


def build_physics_payload(
    object_model: object,
    *,
    model_urdf_sha256: str,
    library_pointer: Path | None = None,
) -> dict[str, Any]:
    """Bind every visual surface to one stable physical profile by material class."""

    pointer = (library_pointer or default_library_pointer()).expanduser().resolve()
    library = _load_library(pointer)
    requests = appearance_requests_from_model(object_model, require_all=True)
    if not requests:
        raise ValueError("object model has no visual surfaces to bind")

    classes: dict[str, Any] = {}
    bindings: list[dict[str, Any]] = []
    for request in requests:
        material_class_id = request.material_class_id
        if material_class_id is None:
            raise ValueError(
                f"visual {request.surface_key!r} has no material_class_id for physics export"
            )
        if material_class_id not in classes:
            pool = library.load_pool(material_class_id)
            material = pool[0]
            classes[material_class_id] = {
                "material": material,
                "pool_count": len(pool),
                "pool_sha256": library.pool_sha256(material_class_id),
            }
        selected = classes[material_class_id]["material"]
        bindings.append(
            {
                "appearance_only": False,
                "material_class_id": material_class_id,
                "material_id": selected.material_id,
                "surface_key": request.surface_key,
                "values": {
                    field_name: selected.physics_values[field_name] for field_name in PHYSICS_FIELDS
                },
            }
        )

    selections = {
        material_class_id: {
            "material_id": row["material"].material_id,
            "material_key": row["material"].material_key,
            "pool_count": row["pool_count"],
            "pool_sha256": row["pool_sha256"],
            "selection_index": 0,
        }
        for material_class_id, row in sorted(classes.items())
    }
    return {
        "schema_version": PHYSICS_SCHEMA,
        "mode": "physics_only",
        "appearance_materialized": False,
        "selection_algorithm": SELECTION_ALGORITHM,
        "model_urdf_sha256": model_urdf_sha256,
        "fields": list(PHYSICS_FIELDS),
        "library": {
            "catalog_sha256": library.catalog_sha256,
            "manifest_sha256": library.manifest_sha256,
            "pointer_sha256": library.pointer_sha256,
            "pool_index_sha256": library.pool_index_sha256,
            "snapshot_sha256": library.snapshot_sha256,
        },
        "class_selections": selections,
        "bindings": sorted(bindings, key=lambda row: str(row["surface_key"])),
    }


__all__ = [
    "PHYSICS_SCHEMA",
    "SELECTION_ALGORITHM",
    "build_physics_payload",
    "default_library_pointer",
]
