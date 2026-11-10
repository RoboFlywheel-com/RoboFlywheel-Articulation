# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.templates.folding_arm_chain import (
    FoldingArmChainConfig,
    build_folding_arm_chain,
    config_from_seed,
    resolve_config,
    run_folding_arm_chain_tests,
    slot_choices_for_seed,
)


def test_seed_slot_choices_match_resolved_config() -> None:
    for seed in range(24):
        config = config_from_seed(seed)
        resolved = resolve_config(config)
        choices = dict(slot_choices_for_seed(seed))
        assert choices["root_support"] == resolved.root_support
        assert choices["chain_multiplicity"] == resolved.chain_multiplicity
        assert choices["link_profile"] == resolved.link_profile
        assert choices["terminal_module"] == resolved.terminal_module
        assert choices["axis_family"] == resolved.axis_family


def test_representative_module_subfamilies_pass_self_tests() -> None:
    configs = [
        FoldingArmChainConfig(
            axis_family="z_planar_stack",
            root_support="compact_service_plate",
            chain_multiplicity="two_link_service_chain",
            link_profile="slotted_flat_bar",
            terminal_module="service_plate",
        ),
        FoldingArmChainConfig(
            axis_family="y_clevis_stack",
            root_support="bridge_hanger_clevis",
            chain_multiplicity="three_link_stay_chain",
            link_profile="forked_bar_link",
            terminal_module="hook_tab",
        ),
        FoldingArmChainConfig(
            axis_family="heavy_twin_strap",
            root_support="low_profile_root_plate",
            chain_multiplicity="four_link_end_bracket_chain",
            link_profile="twin_strap_inspection_link",
            terminal_module="heavy_end_bracket",
        ),
        FoldingArmChainConfig(
            axis_family="z_planar_stack",
            root_support="four_bolt_flat_foot",
            chain_multiplicity="five_link_slot_stack_chain",
            link_profile="slotted_flat_bar",
            terminal_module="integral_end_pad",
        ),
    ]

    for config in configs:
        model = build_folding_arm_chain(config)
        report = run_folding_arm_chain_tests(model, config)
        assert report.passed, str(report)


def test_five_link_slot_stack_preserves_multiplicity() -> None:
    config = FoldingArmChainConfig(
        axis_family="z_planar_stack",
        root_support="four_bolt_flat_foot",
        chain_multiplicity="five_link_slot_stack_chain",
        link_profile="twin_strap_inspection_link",
        terminal_module="tool_plate",
    )
    resolved = resolve_config(config)
    model = build_folding_arm_chain(config)

    assert resolved.link_count == 5
    assert resolved.link_profile == "slotted_flat_bar"
    assert not resolved.moving_terminal
    assert len(model.joints) == 5
    assert {f"link_{index}" for index in range(1, 6)}.issubset({part.name for part in model.parts})

    report = run_folding_arm_chain_tests(model, config)
    assert report.passed, str(report)
