# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import pytest

from agent.templates.display_freezer_with_sliding_glass_lids import (
    DisplayFreezerWithSlidingGlassLidsConfig,
    build_display_freezer,
    build_seeded_display_freezer,
    config_from_seed,
    resolve_config,
    run_display_freezer_tests,
)
from sdk._core.v0.testing import TestContext as SDKTestContext


def _assert_template_qc_passes(config: DisplayFreezerWithSlidingGlassLidsConfig) -> None:
    model = build_display_freezer(config)
    report = run_display_freezer_tests(model, config)
    assert report.passed, report.failures


def _visual_by_name(part, name: str):
    return next(visual for visual in part.visuals if visual.name == name)


def _axis_min(visual, axis: int) -> float:
    return visual.origin.xyz[axis] - visual.geometry.size[axis] * 0.5


def _axis_max(visual, axis: int) -> float:
    return visual.origin.xyz[axis] + visual.geometry.size[axis] * 0.5


def test_template_line_floor() -> None:
    template_path = Path("agent/templates/display_freezer_with_sliding_glass_lids.py")
    assert len(template_path.read_text().splitlines()) >= 1000


def test_seed_reproducibility() -> None:
    assert config_from_seed(10) == config_from_seed(10)
    assert config_from_seed(10) != config_from_seed(11)
    assert build_seeded_display_freezer(10).name == "seeded_display_freezer_10"


def test_seeded_configs_stay_in_display_freezer_domain() -> None:
    configs = [config_from_seed(seed) for seed in range(32)]
    assert {cfg.body_profile for cfg in configs} <= {
        "flat_rectangular_chest",
        "rounded_commercial_tub",
        "compact_deli_counter",
        "three_bay_island",
    }
    assert {cfg.lid_layout for cfg in configs} <= {
        "two_overlapping_flat",
        "single_deli_slider",
        "three_independent_bays",
        "curved_barrel_pair",
        "upper_lower_tier",
    }
    assert all(cfg.basket_count >= 0 for cfg in configs)
    assert len({cfg.interior_storage_layout for cfg in configs}) >= 3


def test_body_lid_rail_storage_compatibility_matrix() -> None:
    compact = resolve_config(
        DisplayFreezerWithSlidingGlassLidsConfig(
            body_profile="compact_deli_counter",
            lid_layout="three_independent_bays",
            rail_layout="three_bay_tracks",
            interior_storage_layout="bay_divider_grid",
        )
    )
    island = resolve_config(
        DisplayFreezerWithSlidingGlassLidsConfig(
            body_profile="three_bay_island",
            lid_layout="single_deli_slider",
            rail_layout="guide_shelves",
            interior_storage_layout="product_tray_rows",
        )
    )
    rounded = resolve_config(
        DisplayFreezerWithSlidingGlassLidsConfig(
            body_profile="rounded_commercial_tub",
            lid_layout="single_deli_slider",
            rail_layout="guide_shelves",
            interior_storage_layout="product_tray_rows",
        )
    )

    assert compact.lid_layout == "single_deli_slider"
    assert compact.rail_layout in {"guide_shelves", "center_spine_two_tier"}
    assert compact.interior_storage_layout in {"product_tray_rows", "removable_bin_grid"}

    assert island.lid_layout == "three_independent_bays"
    assert island.rail_layout == "three_bay_tracks"
    assert island.interior_storage_layout == "bay_divider_grid"
    assert island.bay_count == 3
    assert island.lid_count == 3

    assert rounded.lid_layout == "curved_barrel_pair"
    assert rounded.rail_layout == "center_spine_two_tier"
    assert rounded.interior_storage_layout == "wire_basket_array"


def test_three_bay_lids_share_one_contact_tier() -> None:
    config = DisplayFreezerWithSlidingGlassLidsConfig(
        body_profile="three_bay_island",
        lid_layout="three_independent_bays",
        rail_layout="three_bay_tracks",
        interior_storage_layout="bay_divider_grid",
    )
    resolved = resolve_config(config)
    model = build_display_freezer(config)
    lid_zs = [
        articulation.origin.xyz[2]
        for articulation in model.articulations
        if articulation.name.startswith("lid_slide_")
    ]

    assert resolved.rail_tier_count == 1
    assert len(lid_zs) == 3
    assert max(lid_zs) - min(lid_zs) == pytest.approx(0.0)


def test_sliding_lids_use_continuous_contact_channels() -> None:
    model = build_display_freezer(
        DisplayFreezerWithSlidingGlassLidsConfig(
            body_profile="three_bay_island",
            lid_layout="three_independent_bays",
            rail_layout="three_bay_tracks",
            interior_storage_layout="bay_divider_grid",
        )
    )
    cabinet_visuals = {visual.name for visual in model.get_part("cabinet").visuals}

    assert not any(name.startswith("lid_slide_anchor_") for name in cabinet_visuals)
    assert not any("contact_pad" in name for name in cabinet_visuals)
    assert not any("wear_strip" in name for name in cabinet_visuals)
    assert "front_lid_contact_channel_tier_0" in cabinet_visuals
    assert "rear_lid_contact_channel_tier_0" in cabinet_visuals
    assert "front_inner_runner_shelf_tier_0" in cabinet_visuals
    assert "rear_inner_runner_shelf_tier_0" in cabinet_visuals
    assert "front_recessed_track_groove_tier_0" in cabinet_visuals
    assert "rear_recessed_track_groove_tier_0" in cabinet_visuals


def test_three_bay_has_no_full_depth_floating_cross_stop() -> None:
    model = build_display_freezer(
        DisplayFreezerWithSlidingGlassLidsConfig(
            body_profile="three_bay_island",
            lid_layout="three_independent_bays",
            rail_layout="three_bay_tracks",
            interior_storage_layout="bay_divider_grid",
        )
    )
    cabinet_visuals = {visual.name for visual in model.get_part("cabinet").visuals}

    assert not any(name.startswith("cross_bay_track_stop") for name in cabinet_visuals)
    assert any(name.startswith("front_bay_track_stop") for name in cabinet_visuals)
    assert any(name.startswith("rear_bay_track_stop") for name in cabinet_visuals)


def test_lid_handles_are_flush_recessed_not_raised_bars() -> None:
    for handle_style in ("front_bar", "edge_pull", "recessed_grip", "round_knob"):
        model = build_display_freezer(
            DisplayFreezerWithSlidingGlassLidsConfig(
                body_profile="flat_rectangular_chest",
                lid_layout="two_overlapping_flat",
                handle_style=handle_style,
            )
        )
        lid = model.get_part("sliding_lid_0")
        lid_visuals = {visual.name for visual in lid.visuals}
        front_frame = _visual_by_name(lid, "front_frame")
        grip = _visual_by_name(lid, "recessed_finger_slot")

        assert "front_pull_bar" not in lid_visuals
        assert not any(name.startswith("front_pull_bar_") for name in lid_visuals)
        assert "edge_pull_grip" not in lid_visuals
        assert "round_knob_pull" not in lid_visuals
        assert _axis_min(grip, 1) >= _axis_min(front_frame, 1)
        assert _axis_max(grip, 1) <= _axis_max(front_frame, 1)
        assert _axis_min(grip, 2) >= _axis_min(front_frame, 2)
        assert _axis_max(grip, 2) <= _axis_max(front_frame, 2)


def test_curved_lids_do_not_add_raised_glass_strips_or_top_spines() -> None:
    model = build_display_freezer(
        DisplayFreezerWithSlidingGlassLidsConfig(
            body_profile="rounded_commercial_tub",
            lid_layout="curved_barrel_pair",
            lid_profile="curved_barrel_glass",
        )
    )
    cabinet_visuals = {visual.name for visual in model.get_part("cabinet").visuals}
    lid_visuals = {visual.name for visual in model.get_part("sliding_lid_0").visuals}

    assert not any(name.startswith("curved_glass_strip") for name in lid_visuals)
    assert "center_spine_track" not in cabinet_visuals
    assert not any(name.startswith("center_origin_contact_spine") for name in cabinet_visuals)


def test_lid_has_no_full_depth_top_side_struts() -> None:
    model = build_display_freezer(
        DisplayFreezerWithSlidingGlassLidsConfig(
            body_profile="flat_rectangular_chest",
            lid_layout="two_overlapping_flat",
        )
    )
    lid_visuals = {visual.name for visual in model.get_part("sliding_lid_0").visuals}

    assert "left_side_frame" not in lid_visuals
    assert "right_side_frame" not in lid_visuals
    assert "left_front_corner_cap" in lid_visuals
    assert "right_rear_corner_cap" in lid_visuals


def test_internal_dividers_are_low_floor_anchored_cell_guides() -> None:
    config = DisplayFreezerWithSlidingGlassLidsConfig(
        body_profile="three_bay_island",
        lid_layout="three_independent_bays",
        rail_layout="three_bay_tracks",
        interior_storage_layout="bay_divider_grid",
    )
    resolved = resolve_config(config)
    model = build_display_freezer(config)
    dividers = [
        visual
        for visual in model.get_part("cabinet").visuals
        if visual.name.startswith("bay_divider_")
        or visual.name.startswith("storage_vertical_divider_")
    ]

    assert dividers
    assert not any(visual.name.startswith("storage_vertical_divider_") for visual in dividers)
    for divider in dividers:
        assert _axis_min(divider, 2) == pytest.approx(resolved.liner_floor_z)
        assert divider.geometry.size[0] <= 0.014
        assert divider.geometry.size[1] <= resolved.usable_storage_depth + resolved.storage_gap
        assert divider.geometry.size[2] <= min(
            resolved.cell_height * 0.46,
            resolved.liner_height * 0.28,
            0.135,
        )
        assert _axis_max(divider, 2) <= resolved.liner_floor_z + resolved.cell_height * 0.55


def test_guide_shelf_fixed_panel_is_transparent_glass_not_gray_plank() -> None:
    config = DisplayFreezerWithSlidingGlassLidsConfig(
        body_profile="compact_deli_counter",
        lid_layout="single_deli_slider",
        rail_layout="guide_shelves",
    )
    resolved = resolve_config(config)
    model = build_display_freezer(config)
    fixed_panel = _visual_by_name(model.get_part("cabinet"), "fixed_rear_glass_shelf")

    assert fixed_panel.material.name == "display_freezer_glass"
    assert fixed_panel.material.rgba[3] < 0.7
    assert fixed_panel.geometry.size[0] <= resolved.cabinet_width * 0.40
    assert fixed_panel.geometry.size[1] <= resolved.cabinet_depth * 0.25
    assert fixed_panel.geometry.size[2] == pytest.approx(resolved.glass_thickness)


def test_seed_four_passes_strict_current_pose_overlap_gate() -> None:
    model = build_display_freezer(config_from_seed(4))
    ctx = SDKTestContext(model)

    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)

    assert ctx.report().passed


def test_storage_grid_count_and_cell_dimensions_are_envelope_derived() -> None:
    resolved = resolve_config(
        DisplayFreezerWithSlidingGlassLidsConfig(
            cabinet_width=1.8,
            cabinet_depth=0.88,
            cabinet_height=0.82,
            interior_storage_layout="wire_basket_array",
            storage_grid_cols=4,
            storage_grid_rows=3,
            storage_tier_count=2,
            basket_count=99,
            storage_margin=0.05,
            storage_gap=0.03,
        )
    )
    expected_cell_width = (
        resolved.usable_storage_width - (resolved.storage_grid_cols - 1) * resolved.storage_gap
    ) / resolved.storage_grid_cols
    expected_cell_depth = (
        resolved.usable_storage_depth - (resolved.storage_grid_rows - 1) * resolved.storage_gap
    ) / resolved.storage_grid_rows
    capacity = resolved.storage_grid_cols * resolved.storage_grid_rows * resolved.storage_tier_count

    assert resolved.basket_count <= capacity
    assert resolved.cell_width == pytest.approx(expected_cell_width)
    assert resolved.cell_depth == pytest.approx(expected_cell_depth)
    assert resolved.cell_width >= 0.08
    assert resolved.cell_depth >= 0.08


def test_invalid_lid_count_rejected() -> None:
    with pytest.raises(ValueError, match="lid_count"):
        resolve_config(
            DisplayFreezerWithSlidingGlassLidsConfig(
                lid_count=4,
            )
        )


@pytest.mark.parametrize("seed", range(12))
def test_seeded_configs_pass_template_qc(seed: int) -> None:
    _assert_template_qc_passes(config_from_seed(seed))
