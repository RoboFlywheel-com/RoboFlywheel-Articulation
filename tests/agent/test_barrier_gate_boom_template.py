# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.barrier_gate_boom import (
    BarrierGateConfig,
    build_barrier_gate,
    build_seeded_barrier_gate,
    config_from_seed,
    resolve_config,
    run_barrier_gate_tests,
)


def _visual_names(config: BarrierGateConfig, part_name: str) -> set[str]:
    part = build_barrier_gate(config).get_part(part_name)
    assert part is not None
    return {visual.name for visual in part.visuals if visual.name}


def test_seeded_support_profile_stays_observable() -> None:
    configs = [config_from_seed(seed) for seed in range(80)]

    assert {config.barrier_layout for config in configs} == {"single_boom", "folding_boom"}
    assert {
        config.boom_support_profile for config in configs if config.barrier_layout == "single_boom"
    } == {"slim_cabinet", "round_pedestal", "box_head"}
    for config in configs:
        resolved = resolve_config(config)
        assert resolved.boom_support_profile == config.boom_support_profile


def test_single_boom_supports_round_pedestal_truss_counterweight_and_warning_bands() -> None:
    config = BarrierGateConfig(
        barrier_layout="single_boom",
        boom_support_profile="round_pedestal",
        boom_section="trussed",
        counterweight_style="counter_arm",
        stripe_pattern="segmented_red_bands",
    )

    support_names = _visual_names(config, "fixed_support")
    boom_names = _visual_names(config, "boom_arm")

    assert "round_pedestal_post" in support_names
    assert "upper_chord" in boom_names
    assert "counter_arm_weight" in boom_names
    assert any(name.startswith("warning_band_front_") for name in boom_names)


def test_tapered_and_folding_boom_variants_pass_template_tests() -> None:
    tapered = BarrierGateConfig(
        barrier_layout="single_boom",
        boom_support_profile="box_head",
        boom_section="tapered_box",
        boom_end_style="tapered_tip",
        stripe_pattern="long_red_strip",
    )
    folding = BarrierGateConfig(
        barrier_layout="folding_boom",
        boom_section="trussed",
        stripe_pattern="yellow_hazard_bands",
    )

    for config in (tapered, folding):
        report = run_barrier_gate_tests(build_barrier_gate(config), config)
        assert report.passed, report.failures


def test_build_seeded_barrier_gate_runs_template_tests() -> None:
    model = build_seeded_barrier_gate(7)
    report = run_barrier_gate_tests(model, config_from_seed(7))
    assert report.passed, report.failures
