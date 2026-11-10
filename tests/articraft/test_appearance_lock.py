# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

from articraft.appearance import (
    AppearanceRequest,
    MaterialPhysicsReference,
    MaterialRecord,
    ResolvedAppearance,
)
from articraft.appearance.lock import LOCK_SCHEMA_VERSION, materialize_appearance_lock


def test_materialize_lock_copies_selected_package_without_hashing(tmp_path: Path) -> None:
    source = tmp_path / "library" / "material.blend"
    source.parent.mkdir()
    source.write_bytes(b"selected package bytes")
    material = MaterialRecord(
        material_id="material-a",
        category_slug="metal",
        blend_path=source,
        sha256="f" * 64,
        license="cc_zero",
        provider="test",
        asset_base_id="asset-a",
        display_name="Material A",
        material_profile="texture_set",
        texture_size_m=0.5,
        mapping_profile="metric_uv_tangent",
        normal_space="tangent",
        requires_uv=True,
        physics_ref=MaterialPhysicsReference(
            path="physics/by-id/material-a.json",
            sha256="2" * 64,
            risk_tier="medium",
            reference_conditions_id="dry-steel-23c-v1",
        ),
    )
    request = AppearanceRequest(
        surface_key="body::shell",
        asset_type="pbr_material",
        material_class_id="metal.brushed_silver",
    )
    resolved = ResolvedAppearance(
        request=request,
        material=material,
        candidate_pool_count=1,
        candidate_pool_sha256="a" * 64,
        draw_order=0,
        selection_index=0,
        candidate_pool_material_class_id="metal.brushed_silver",
    )

    lock = materialize_appearance_lock(
        tmp_path / "seed",
        [resolved],
        slug="test_asset",
        seed=0,
        material_seed=7,
        template_sha256="c" * 64,
        model_urdf_sha256="d" * 64,
        library_snapshot_sha256="e" * 64,
        pool_index_sha256="1" * 64,
    )

    copied = tmp_path / "seed" / lock["bindings"][0]["material"]["package_path"]
    assert copied.read_bytes() == source.read_bytes()
    assert lock["schema_version"] == LOCK_SCHEMA_VERSION
    assert lock["bindings"][0]["material"]["sha256"] == "f" * 64
    assert lock["bindings"][0]["material"]["physics_ref"]["risk_tier"] == "medium"
    assert lock["bindings"][0]["appearance_only"] is False
    assert lock["retriever_version"] == "local-random-choice/v1"
    assert lock["bindings"][0]["selection"]["draw_order"] == 0
    assert lock["bindings"][0]["selection"]["selection_index"] == 0
    assert "selection_key_sha256" not in lock["bindings"][0]["selection"]
    assert "surface_slot" not in lock["bindings"][0]
    assert "reuse_group" not in lock["bindings"][0]
