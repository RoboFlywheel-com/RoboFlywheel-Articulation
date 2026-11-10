# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.screwcap_bottle import (
    SOURCE_ADAPTATION_MAP,
    SOURCE_IDS,
    ScrewcapBottleConfig,
    build_screwcap_bottle,
    build_seeded_screwcap_bottle,
    config_from_seed,
    resolve_config,
    run_screwcap_bottle_tests,
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
    assert build_seeded_screwcap_bottle(7).name == "seeded_screwcap_bottle_7"


def test_invalid_config_rejections() -> None:
    with pytest.raises(ValueError):
        resolve_config(ScrewcapBottleConfig(bottle_profile="paint_can"))  # type: ignore[arg-type]


def test_default_identity_and_validator() -> None:
    config = ScrewcapBottleConfig()
    model = build_screwcap_bottle(config)
    report = run_screwcap_bottle_tests(model, config)
    assert report.passed, report.failures
    assert model.get_articulation("cap_spin").axis == (0.0, 0.0, 1.0)


def test_source_adaptation_map_covers_core_semantics() -> None:
    assert SOURCE_IDS
    assert SOURCE_ADAPTATION_MAP
    assert len(SOURCE_IDS) >= 11


def test_representative_seeded_models_pass_basic_qc() -> None:
    for seed in range(3):
        _assert_basic_qc_passes(build_seeded_screwcap_bottle(seed))
