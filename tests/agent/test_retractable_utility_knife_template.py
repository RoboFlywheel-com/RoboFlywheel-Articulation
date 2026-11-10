# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.retractable_utility_knife import (
    RetractableUtilityKnifeConfig,
    build_seeded_retractable_utility_knife,
    config_from_seed,
    resolve_config,
)


def test_seed_config_is_reproducible() -> None:
    assert config_from_seed(7) == config_from_seed(7)
    assert config_from_seed(7) != config_from_seed(8)


@pytest.mark.parametrize("seed", [0, 1, 2, 5, 12])
def test_seeded_builds_succeed(seed: int) -> None:
    model = build_seeded_retractable_utility_knife(seed)
    part_names = {p.name for p in model.parts}
    assert "body_shell" in part_names
    assert "blade_carrier" in part_names
    assert "blade" in part_names
    assert "thumb_slider" in part_names

    joint_topology = {(a.parent, a.child, a.articulation_type.name) for a in model.articulations}
    assert ("body_shell", "blade_carrier", "PRISMATIC") in joint_topology
    assert ("blade_carrier", "blade", "FIXED") in joint_topology
    assert ("blade_carrier", "thumb_slider", "FIXED") in joint_topology


def test_resolve_config_clamps_oversized_handle() -> None:
    cfg = RetractableUtilityKnifeConfig(handle_length=0.50)
    r = resolve_config(cfg)
    assert r.handle_length <= 0.200


def test_resolve_config_rejects_invalid_blade_style() -> None:
    with pytest.raises(ValueError, match="blade_style"):
        resolve_config(RetractableUtilityKnifeConfig(blade_style="unknown"))  # type: ignore[arg-type]


def test_lock_wheel_skipped_when_lock_style_none() -> None:
    cfg = RetractableUtilityKnifeConfig(lock_style="none")
    model = build_seeded_retractable_utility_knife(0)
    # The seeded model may or may not have lock; build from explicit config:
    from agent.templates.retractable_utility_knife import build_retractable_utility_knife

    model = build_retractable_utility_knife(cfg)
    assert all(p.name != "lock_wheel" for p in model.parts)
