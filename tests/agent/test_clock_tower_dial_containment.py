# SPDX-License-Identifier: Apache-2.0

from agent.templates.clock_tower_with_rotating_hour_and_minute_hands import (
    config_from_seed,
    resolve_config,
)


def test_glazed_clock_room_contains_dial_and_bezel_across_sampled_seeds() -> None:
    for seed in range(4096):
        resolved = resolve_config(config_from_seed(seed))
        if resolved.tower_style != "glazed_multiface" or resolved.dial_style == "dual_housing":
            continue

        bezel_diameter = 2.0 * 1.15 * resolved.dial_radius
        assert resolved.head_height > bezel_diameter, seed
        assert resolved.head_size > bezel_diameter, seed


def test_reported_overflow_seeds_keep_a_visible_clock_room_border() -> None:
    for seed in (1946, 2314):
        resolved = resolve_config(config_from_seed(seed))
        bezel_diameter = 2.0 * 1.15 * resolved.dial_radius
        border = min(
            resolved.head_height - bezel_diameter,
            resolved.head_size - bezel_diameter,
        )
        assert border + 1e-9 >= 0.30 * bezel_diameter, seed
