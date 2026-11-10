# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.articulated_task_lamp import (
    SOURCE_ADAPTATION_MAP,
    SOURCE_IDS,
    ArticulatedTaskLampConfig,
    build_seeded_articulated_task_lamp,
    config_from_seed,
    resolve_config,
    run_articulated_task_lamp_tests,
)
from sdk import TestContext


def test_seed_config_is_reproducible() -> None:
    assert config_from_seed(7) == config_from_seed(7)
    assert config_from_seed(7) != config_from_seed(8)
    assert build_seeded_articulated_task_lamp(7).name == "seeded_articulated_task_lamp_7"


def test_seed_0_passes_run_articulated_task_lamp_tests() -> None:
    config = config_from_seed(0)
    model = build_seeded_articulated_task_lamp(0)
    report = run_articulated_task_lamp_tests(model, config)
    assert report.passed, report.failures
    assert config.mount_style == "weighted_round_disk"
    assert config.arm_style == "twin_rail_two_link"
    assert config.shade_style == "rect_architect"


@pytest.mark.parametrize("seed", [0, 1, 2, 3, 5, 7, 11])
def test_representative_seeded_models_pass_basic_qc(seed: int) -> None:
    config = config_from_seed(seed)
    model = build_seeded_articulated_task_lamp(seed)
    report = run_articulated_task_lamp_tests(model, config)
    assert report.passed, report.failures

    ctx = TestContext(model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    basic = ctx.report()
    assert basic.passed, basic.failures


def test_resolve_config_rejects_invalid_combos() -> None:
    with pytest.raises(ValueError, match="mount_style"):
        resolve_config(ArticulatedTaskLampConfig(mount_style="floor_torchiere"))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="arm_style"):
        resolve_config(ArticulatedTaskLampConfig(arm_style="gooseneck_telescoping"))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="shade_style"):
        resolve_config(ArticulatedTaskLampConfig(shade_style="cadquery_loft"))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="material_style"):
        resolve_config(ArticulatedTaskLampConfig(material_style="neon_pink"))  # type: ignore[arg-type]


def test_resolve_config_keeps_wall_mount_slot_choice() -> None:
    resolved = resolve_config(
        ArticulatedTaskLampConfig(
            mount_style="wall_plate",
            arm_style="twin_rail_two_link",
            shade_style="lathe_conical",
        )
    )
    assert resolved.arm_style == "twin_rail_two_link"
    assert resolved.pitch_axis_family == "pos_y_wall"


def test_source_ids_present() -> None:
    assert SOURCE_IDS
    assert SOURCE_ADAPTATION_MAP
    assert len(SOURCE_IDS) >= 18
    assert "S1" in SOURCE_IDS
    assert "twin_rail_segment" in SOURCE_ADAPTATION_MAP
