# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.chest_freezer_with_hinged_lid import (
    ChestFreezerWithHingedLidConfig,
    build_chest_freezer,
    build_seeded_chest_freezer,
    config_from_seed,
    resolve_config,
    run_chest_freezer_tests,
)
from sdk import TestContext as ArticraftTestContext


def _assert_strict_qc_passes(config: ChestFreezerWithHingedLidConfig) -> None:
    model = build_chest_freezer(config)
    report = run_chest_freezer_tests(model, config)
    assert report.passed, report.failures
    ctx = ArticraftTestContext(model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    ctx.fail_if_parts_overlap_in_current_pose(overlap_tol=0.003, overlap_volume_tol=1e-7)
    report = ctx.report()
    assert report.passed, report.failures


def test_seed_reproducibility() -> None:
    assert config_from_seed(11) == config_from_seed(11)
    assert config_from_seed(11) != config_from_seed(12)
    assert build_seeded_chest_freezer(11).name == "seeded_chest_freezer_11"


def test_seeded_configs_stay_on_hinged_freezer_family() -> None:
    configs = [config_from_seed(seed) for seed in range(40)]
    assert {cfg.lid_layout for cfg in configs} == {"single_hinged", "split_hinged"}
    assert {cfg.lid_material_style for cfg in configs} == {"solid_insulated"}
    assert {cfg.hinge_style for cfg in configs} <= {"barrel_pair", "center_spine"}
    assert "display_products" not in {cfg.accessory_set for cfg in configs}
    assert "commercial_display" not in {cfg.body_style for cfg in configs}
    assert {cfg.interior_bin_count for cfg in configs} <= {0, 1, 2, 3, 4}
    assert len({cfg.interior_bin_count for cfg in configs}) > 1
    assert all(
        cfg.accessory_set != "stay_and_drain" for cfg in configs if cfg.lid_layout == "split_hinged"
    )


def test_validator_layout_contracts() -> None:
    config = ChestFreezerWithHingedLidConfig(
        lid_layout="single_hinged", hinge_count=2, hinge_style="barrel_pair"
    )
    model = build_chest_freezer(config)
    report = run_chest_freezer_tests(model, config)
    assert report.passed, report.failures


def test_invalid_dimension_rejected() -> None:
    with pytest.raises(ValueError, match="body_height"):
        resolve_config(ChestFreezerWithHingedLidConfig(body_height=0.1))


def test_supported_split_and_legacy_sliding_layouts() -> None:
    split = resolve_config(
        ChestFreezerWithHingedLidConfig(
            lid_layout="split_hinged",
            body_style="split_lid_cooler",
            hinge_style="center_spine",
            accessory_set="stay_and_drain",
        )
    )
    sliding = resolve_config(
        ChestFreezerWithHingedLidConfig(lid_layout="sliding_glass", hinge_style="guide_rail")
    )

    assert split.lid_layout == "split_hinged"
    assert split.lid_material_style == "solid_insulated"
    assert split.hinge_count == 2
    assert split.hinge_style == "center_spine"
    assert split.accessory_set == "control_vent"
    assert split.lid_count == 2

    assert sliding.lid_layout == "single_hinged"
    assert sliding.lid_material_style == "solid_insulated"
    assert sliding.hinge_count in {2, 3}
    assert sliding.hinge_style == "barrel_pair"
    assert sliding.lid_count == 1


def test_interior_bin_count_is_clamped_by_freezer_length() -> None:
    small = resolve_config(
        ChestFreezerWithHingedLidConfig(
            body_length=0.95, interior_bin_count=4, lid_layout="single_hinged"
        )
    )
    medium = resolve_config(
        ChestFreezerWithHingedLidConfig(
            body_length=1.55, interior_bin_count=4, lid_layout="single_hinged"
        )
    )
    assert small.interior_bin_count == 1
    assert medium.interior_bin_count == 3


def test_split_lids_cover_the_opening_from_their_closed_pose_hinges() -> None:
    config = ChestFreezerWithHingedLidConfig(
        body_style="split_lid_cooler",
        lid_layout="split_hinged",
        hinge_style="center_spine",
        handle_style="front_bar",
    )
    resolved = resolve_config(config)
    model = build_chest_freezer(config)
    world_centers: list[float] = []

    for index, sign in enumerate((1.0, -1.0)):
        lid = model.get_part(f"lid_{index}")
        shell = lid.get_visual("lid_shell")
        joint = model.get_articulation(f"lid_{index}_hinge")
        shell_width = shell.geometry.size[1]
        world_center_y = joint.origin.xyz[1] + shell.origin.xyz[1]
        world_inner_y = world_center_y - sign * shell_width * 0.5
        world_outer_y = world_center_y + sign * shell_width * 0.5
        world_centers.append(world_center_y)

        assert world_inner_y == pytest.approx(joint.origin.xyz[1])
        assert world_outer_y == pytest.approx(joint.origin.xyz[1] + sign * shell_width)
        assert sign * world_inner_y <= resolved.opening_width * 0.5
        assert sign * world_outer_y >= resolved.opening_width * 0.5
        world_bottom_z = joint.origin.xyz[2] + shell.origin.xyz[2] - resolved.lid_thickness * 0.5
        world_top_z = joint.origin.xyz[2] + shell.origin.xyz[2] + resolved.lid_thickness * 0.5
        assert world_bottom_z == pytest.approx(resolved.body_height)
        assert world_top_z == pytest.approx(resolved.body_height + resolved.lid_thickness)
        assert lid.inertial is not None
        assert lid.inertial.origin.xyz[1] == pytest.approx(shell.origin.xyz[1])

    assert world_centers[0] == pytest.approx(-world_centers[1])


def test_public_config_keeps_expected_fields() -> None:
    cfg = ChestFreezerWithHingedLidConfig()
    for attr in (
        "body_style",
        "lid_layout",
        "lid_material_style",
        "hinge_style",
        "handle_style",
        "gasket_style",
        "interior_bin_count",
    ):
        assert hasattr(cfg, attr)


@pytest.mark.parametrize("seed", range(12))
def test_seeded_configs_pass_strict_qc(seed: int) -> None:
    _assert_strict_qc_passes(config_from_seed(seed))
