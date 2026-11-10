# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.monitor_mount import (
    MonitorMountConfig,
    build_seeded_monitor_mount,
    config_from_seed,
    resolve_config,
)


def test_seed_config_is_reproducible() -> None:
    assert config_from_seed(11) == config_from_seed(11)
    assert config_from_seed(11) != config_from_seed(12)


@pytest.mark.parametrize("seed", [0, 1, 2, 5, 12])
def test_seeded_builds_have_expected_six_parts(seed: int) -> None:
    model = build_seeded_monitor_mount(seed)
    part_names = {p.name for p in model.parts}
    expected = {
        "wall_bracket",
        "pan_carriage",
        "primary_arm",
        "secondary_arm",
        "head_knuckle",
        "tilt_head",
    }
    assert expected.issubset(part_names), f"Missing parts: {expected - part_names}"


def test_joint_topology_matches_anchor() -> None:
    model = build_seeded_monitor_mount(0)
    topology = {(a.parent, a.child, a.articulation_type.name) for a in model.articulations}
    expected = {
        ("wall_bracket", "pan_carriage", "REVOLUTE"),
        ("pan_carriage", "primary_arm", "REVOLUTE"),
        ("primary_arm", "secondary_arm", "REVOLUTE"),
        ("secondary_arm", "head_knuckle", "REVOLUTE"),
        ("head_knuckle", "tilt_head", "REVOLUTE"),
    }
    assert topology == expected


def test_resolve_config_rejects_invalid_arm_style() -> None:
    with pytest.raises(ValueError, match="arm_style"):
        resolve_config(MonitorMountConfig(arm_style="unknown"))  # type: ignore[arg-type]
