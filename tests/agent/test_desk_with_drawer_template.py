# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.desk_with_drawer import (
    DeskWithDrawerConfig,
    build_desk_with_drawer,
    config_from_seed,
    resolve_config,
    run_desk_with_drawer_tests,
)
from sdk import TestContext as SdkTestContext


def test_resolve_rejects_invalid_drawer_count() -> None:
    with pytest.raises(ValueError, match="drawer_count"):
        resolve_config(DeskWithDrawerConfig(drawer_count=0))


def test_seeded_configs_stay_on_stable_drawer_desk_family() -> None:
    configs = [config_from_seed(seed) for seed in range(40)]

    assert {config.desk_layout for config in configs} == {
        "writing_single_drawer",
        "side_pedestal",
        "double_pedestal",
    }
    assert {config.desktop_profile for config in configs} == {"rectangular"}
    assert {config.support_style for config in configs} <= {
        "four_legs",
        "single_pedestal",
        "double_pedestal",
    }
    assert {config.drawer_layout for config in configs} <= {
        "center_single",
        "side_stack",
        "double_stack",
    }
    assert {config.optional_feature for config in configs} == {"none"}
    assert {config.height_travel for config in configs} == {0.0}
    writing_counts = {
        config.drawer_count for config in configs if config.desk_layout == "writing_single_drawer"
    }
    side_counts = {
        config.drawer_count for config in configs if config.desk_layout == "side_pedestal"
    }
    double_counts = {
        config.drawer_count for config in configs if config.desk_layout == "double_pedestal"
    }
    assert writing_counts == {1, 2, 3}
    assert side_counts <= {3, 4, 5, 6}
    assert len(side_counts) >= 2
    assert double_counts <= {6, 8, 10, 12}
    assert len(double_counts) >= 2


def test_complex_legacy_layouts_are_coerced_to_stable_drawer_desk() -> None:
    resolved = resolve_config(
        DeskWithDrawerConfig(
            desk_layout="standing_l",
            desktop_profile="l_shaped",
            support_style="telescoping_columns",
            drawer_layout="keyboard_tray_plus_drawer",
            optional_feature="keyboard_tray",
            height_travel=0.25,
            has_keyboard_tray=True,
            has_drop_leaf=True,
            drawer_count=2,
        )
    )

    assert resolved.desk_layout == "double_pedestal"
    assert resolved.desktop_profile == "rectangular"
    assert resolved.support_style == "double_pedestal"
    assert resolved.drawer_layout == "double_stack"
    assert resolved.optional_feature == "none"
    assert resolved.height_travel == 0.0
    assert not resolved.has_keyboard_tray
    assert not resolved.has_drop_leaf
    assert resolved.drawer_count >= 6


def test_double_pedestal_derives_drawer_stack_count() -> None:
    config = DeskWithDrawerConfig(desk_layout="double_pedestal", drawer_count=1)
    resolved = resolve_config(config)
    model = build_desk_with_drawer(config)

    assert resolved.support_style == "double_pedestal"
    assert resolved.drawer_layout == "double_stack"
    assert resolved.drawer_count >= 6
    drawer_parts = {
        part.name
        for part in model.parts
        if part.name.startswith("drawer_") and part.name.removeprefix("drawer_").isdigit()
    }
    assert len(drawer_parts) == resolved.drawer_count


def test_seed_config_is_reproducible() -> None:
    assert config_from_seed(31) == config_from_seed(31)
    assert config_from_seed(31) != config_from_seed(32)


def test_run_desk_with_drawer_tests_passes() -> None:
    config = DeskWithDrawerConfig(desk_layout="double_pedestal", drawer_count=8)
    report = run_desk_with_drawer_tests(build_desk_with_drawer(config), config)

    assert report.passed, report.failures


def test_writing_desk_omits_front_apron_when_front_drawer_exists() -> None:
    model = build_desk_with_drawer(DeskWithDrawerConfig(desk_layout="writing_single_drawer"))
    desk_frame = model.get_part("desk_frame")
    visual_names = {visual.name for visual in desk_frame.visuals if visual.name}

    assert "front_apron" not in visual_names
    assert "rear_apron" in visual_names


def test_writing_desk_supports_one_row_of_multiple_drawers() -> None:
    config = DeskWithDrawerConfig(desk_layout="writing_single_drawer", drawer_count=3)
    resolved = resolve_config(config)
    model = build_desk_with_drawer(config)
    drawer_parts = {
        part.name
        for part in model.parts
        if part.name.startswith("drawer_") and part.name.removeprefix("drawer_").isdigit()
    }

    assert resolved.drawer_count == 3
    assert resolved.drawer_columns == 3
    assert resolved.drawer_rows == 1
    assert len(drawer_parts) == 3


def test_writing_desk_multi_drawer_row_has_tight_gaps_and_dividers() -> None:
    config = DeskWithDrawerConfig(desk_layout="writing_single_drawer", drawer_count=3)
    resolved = resolve_config(config)
    model = build_desk_with_drawer(config)
    drawer_xs = sorted(
        model.get_articulation(f"drawer_slide_{index}").origin.xyz[0]
        for index in range(resolved.drawer_count)
    )
    gaps = [
        drawer_xs[index + 1] - drawer_xs[index] - resolved.drawer_width
        for index in range(len(drawer_xs) - 1)
    ]
    housing_visuals = {visual.name for visual in model.get_part("drawer_housing").visuals}

    assert all(0.010 <= gap <= 0.018 for gap in gaps)
    assert {"front_vertical_stile_1", "front_vertical_stile_2"} <= housing_visuals


def test_double_pedestal_omits_rear_modesty_panel() -> None:
    model = build_desk_with_drawer(DeskWithDrawerConfig(desk_layout="double_pedestal"))
    desk_frame = model.get_part("desk_frame")
    visual_names = {visual.name for visual in desk_frame.visuals if visual.name}

    assert "modesty_panel" not in visual_names


@pytest.mark.parametrize(
    "config",
    [
        DeskWithDrawerConfig(desk_layout="writing_single_drawer", drawer_count=1),
        DeskWithDrawerConfig(desk_layout="side_pedestal", drawer_count=4),
        DeskWithDrawerConfig(desk_layout="double_pedestal", drawer_count=8),
    ],
)
def test_stable_layout_geometry_passes_validity_qc(config: DeskWithDrawerConfig) -> None:
    model = build_desk_with_drawer(config)
    ctx = SdkTestContext(model)

    ctx.check_model_valid()

    report = ctx.report()
    assert report.passed, report.failures
