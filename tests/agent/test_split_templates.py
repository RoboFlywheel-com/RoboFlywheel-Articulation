# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import importlib

from agent.template_registry import TEMPLATE_REGISTRY


def test_split_template_seed_domains_are_restricted() -> None:
    expected = {
        "barrier_gate_boom": ("barrier_layout", {"single_boom", "folding_boom"}),
        "barrier_gate_leaf_gate": (
            "barrier_layout",
            {
                "sliding_panel",
                "swing_leaf",
                "bifold_leaf",
                "rising_wedge",
                "telescoping_bollard",
                "vertical_lift_panel",
            },
        ),
        "blender_countertop": (
            "blender_layout",
            {"countertop_jug", "personal_cup", "commercial_hood", "vacuum_jug", "bar_blender"},
        ),
        "immersion_blender": ("blender_layout", {"immersion_wand"}),
        "ceiling_light_fixture_adjustable": (
            "fixture_layout",
            {"track_spot", "branching_arm", "pull_down_pendant"},
        ),
        "desk_with_drawer_card_catalog": ("desk_layout", {"card_catalog"}),
    }

    for slug, (field, allowed) in expected.items():
        module = importlib.import_module(f"agent.templates.{slug}")
        observed = {getattr(module.config_from_seed(seed), field) for seed in range(12)}
        assert observed <= allowed
        assert observed == allowed


def test_split_templates_are_registered_with_required_exports() -> None:
    split_slugs = {
        "barrier_gate_boom",
        "barrier_gate_leaf_gate",
        "blender_countertop",
        "immersion_blender",
        "ceiling_light_fixture_adjustable",
        "desk_with_drawer_card_catalog",
    }
    retired_slugs = {
        "barrier_gate",
        "blender",
        "car_sunroof_cassette",
        "ceiling_light_fixture",
    }

    assert split_slugs <= set(TEMPLATE_REGISTRY)
    assert not retired_slugs & set(TEMPLATE_REGISTRY)

    for slug in split_slugs:
        stem = TEMPLATE_REGISTRY[slug]
        module = importlib.import_module(f"agent.templates.{slug}")
        assert hasattr(module, "config_from_seed")
        assert hasattr(module, f"build_{stem}")
        assert hasattr(module, f"run_{stem}_tests")
