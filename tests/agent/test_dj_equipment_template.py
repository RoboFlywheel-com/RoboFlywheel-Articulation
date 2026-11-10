# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.dj_equipment import (
    DJEquipmentConfig,
    build_seeded_dj_equipment,
    config_from_seed,
    resolve_config,
)


def test_seed_config_is_reproducible() -> None:
    assert config_from_seed(17) == config_from_seed(17)
    assert config_from_seed(17) != config_from_seed(18)


@pytest.mark.parametrize("seed", [0, 1, 3, 7, 22])
def test_seeded_builds_have_expected_seven_parts(seed: int) -> None:
    model = build_seeded_dj_equipment(seed)
    part_names = {p.name for p in model.parts}
    expected = {
        "housing",
        "left_platter",
        "right_platter",
        "crossfader",
        "left_volume_fader",
        "right_volume_fader",
        "carry_handle",
    }
    assert expected.issubset(part_names), f"Missing parts: {expected - part_names}"


def test_joint_topology_matches_anchor() -> None:
    model = build_seeded_dj_equipment(0)
    topology = {(a.parent, a.child, a.articulation_type.name) for a in model.articulations}
    expected = {
        ("housing", "left_platter", "REVOLUTE"),
        ("housing", "right_platter", "REVOLUTE"),
        ("housing", "crossfader", "PRISMATIC"),
        ("housing", "left_volume_fader", "PRISMATIC"),
        ("housing", "right_volume_fader", "PRISMATIC"),
        ("housing", "carry_handle", "REVOLUTE"),
    }
    assert topology == expected


def test_housing_has_three_mesh_visuals() -> None:
    """Per primitive_complexity_lower_bound, the housing must retain the
    anchor's 3 Mesh visuals (wall_ring / bottom_panel / top_deck)."""
    from sdk import Mesh

    model = build_seeded_dj_equipment(0)
    housing = model.get_part("housing")
    mesh_count = sum(1 for v in housing.visuals if isinstance(v.geometry, Mesh))
    assert mesh_count >= 3, f"Expected ≥3 Mesh visuals on housing, got {mesh_count}"


def test_resolve_config_rejects_invalid_controller_layout() -> None:
    with pytest.raises(ValueError, match="controller_layout"):
        resolve_config(DJEquipmentConfig(controller_layout="unknown"))  # type: ignore[arg-type]
