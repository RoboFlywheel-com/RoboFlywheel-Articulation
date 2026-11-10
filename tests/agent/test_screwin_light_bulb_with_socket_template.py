# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.screwin_light_bulb_with_socket import (
    SOURCE_ADAPTATION_MAP,
    SOURCE_IDS,
    ScrewinLightBulbWithSocketConfig,
    build_screwin_light_bulb_with_socket,
    build_seeded_screwin_light_bulb_with_socket,
    config_from_seed,
    resolve_config,
    run_screwin_light_bulb_with_socket_tests,
)
from sdk import TestContext as ArticraftTestContext


def _assert_basic_qc_passes(model) -> None:
    ctx = ArticraftTestContext(model)
    ctx.check_model_valid()
    ctx.fail_if_isolated_parts()
    report = ctx.report()
    assert report.passed, report.failures


def test_seed_config_is_reproducible() -> None:
    assert config_from_seed(7) == config_from_seed(7)
    assert config_from_seed(7) != config_from_seed(8)
    assert (
        build_seeded_screwin_light_bulb_with_socket(7).name
        == "seeded_screwin_light_bulb_with_socket_7"
    )


def test_invalid_config_rejections() -> None:
    with pytest.raises(ValueError):
        resolve_config(ScrewinLightBulbWithSocketConfig(socket_style="loose_wire"))  # type: ignore[arg-type]


def test_default_identity_and_validator() -> None:
    config = ScrewinLightBulbWithSocketConfig()
    model = build_screwin_light_bulb_with_socket(config)
    report = run_screwin_light_bulb_with_socket_tests(model, config)
    assert report.passed, report.failures
    assert any(j.axis == (0.0, 0.0, 1.0) for j in model.articulations)


def test_source_adaptation_map_covers_core_semantics() -> None:
    assert SOURCE_IDS
    assert SOURCE_ADAPTATION_MAP
    assert len(SOURCE_IDS) >= 13


def test_representative_seeded_models_pass_basic_qc() -> None:
    for seed in range(3):
        _assert_basic_qc_passes(build_seeded_screwin_light_bulb_with_socket(seed))
