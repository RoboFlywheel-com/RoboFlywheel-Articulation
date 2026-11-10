# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

from agent.template_sweep import SeedOutcome
from agent.template_sweep_coverage import (
    CoverageGateResult,
    CoverageGates,
    _normalize_slot_choices,
    check_module_topology_diversity,
    evaluate_gates,
    reachable_topology_count,
)


def _outcome(
    seed: int,
    verdict: str = "pass",
) -> SeedOutcome:
    return SeedOutcome(
        seed=seed,
        verdict=verdict,
        config={"seed": seed},
        failure_type=None if verdict == "pass" else "fail_if_isolated_parts()",
        failure_type_normalized=None if verdict == "pass" else "fail_if_isolated_parts",
        failure_details=None if verdict == "pass" else "isolated antenna",
        elapsed_s=0.0,
    )


def _patch_modular_choices(monkeypatch, choices_by_seed: dict[int, object]) -> None:
    monkeypatch.setattr("agent.template_sweep_coverage.is_modular_template", lambda slug: True)
    monkeypatch.setattr(
        "agent.template_sweep_coverage._slot_choices_for_seed",
        lambda slug, seed: choices_by_seed[seed],
    )


def test_normalize_slot_choices_accepts_mapping_and_pairs() -> None:
    assert _normalize_slot_choices({"base": "tripod", "head": "pan_tilt"}) == (
        ("base", "tripod"),
        ("head", "pan_tilt"),
    )
    assert _normalize_slot_choices([("base", "tripod")]) == (("base", "tripod"),)


def test_normalize_slot_choices_rejects_invalid_shape() -> None:
    try:
        _normalize_slot_choices(["base_only"])
    except ValueError as exc:
        assert "pairs" in str(exc)
    else:
        raise AssertionError("expected invalid slot choices to fail")


def test_module_topology_diversity_enforced_at_any_sweep_size(monkeypatch) -> None:
    """The activation threshold is retired: reachability comes from the pure
    probe, so the per-key floor applies whenever the gate is evaluated."""
    choices = {seed: [("base", "base_0"), ("head", f"head_{seed % 2}")] for seed in range(6)}
    _patch_modular_choices(monkeypatch, choices)

    gate = check_module_topology_diversity("demo", [_outcome(seed) for seed in range(6)])

    assert gate.status in ("pass", "fail")  # never "skipped" for a modular slug


def test_module_topology_diversity_fails_when_template_not_modular(monkeypatch) -> None:
    monkeypatch.setattr("agent.template_sweep_coverage.is_modular_template", lambda slug: False)
    gate = check_module_topology_diversity("demo", [_outcome(seed) for seed in range(20)])
    assert gate.status == "fail"
    assert "__modular__ = True" in gate.reason


def test_module_topology_diversity_fails_when_slot_report_missing(monkeypatch) -> None:
    monkeypatch.setattr("agent.template_sweep_coverage.is_modular_template", lambda slug: True)

    def missing_slot_report(slug: str, seed: int):
        raise AttributeError("missing callable slot_choices_for_seed(seed)")

    monkeypatch.setattr("agent.template_sweep_coverage._slot_choices_for_seed", missing_slot_report)
    gate = check_module_topology_diversity("demo", [_outcome(seed) for seed in range(20)])
    assert gate.status == "fail"
    assert gate.details["errors"][0]["error_kind"] == "AttributeError"
    assert "slot_choices_for_seed" in gate.reason


def test_module_topology_diversity_passes_with_ten_distinct_passing_tuples(
    monkeypatch,
) -> None:
    choices = {
        seed: [("base", f"base_{seed % 10}"), ("head", f"head_{seed % 2}")] for seed in range(20)
    }
    _patch_modular_choices(monkeypatch, choices)

    gate = check_module_topology_diversity("demo", [_outcome(seed) for seed in range(20)])

    assert gate.status == "pass"
    assert gate.details["distinct_count"] >= 10
    assert gate.details["passing_seed_count"] == 20


def test_module_topology_diversity_fails_when_a_reachable_slot_is_stuck_at_one_value(
    monkeypatch,
) -> None:
    # `base` CAN be base_0/base_1 (reachable=2), but every PASSING seed realizes
    # base_0 (the base_1 seeds fail). The base axis never varies in the output -> fail.
    choices = {
        seed: [("base", "base_0" if seed < 18 else "base_1"), ("head", f"head_{seed % 2}")]
        for seed in range(20)
    }
    _patch_modular_choices(monkeypatch, choices)
    outcomes = [_outcome(seed, "pass" if seed < 18 else "fail") for seed in range(20)]

    gate = check_module_topology_diversity("demo", outcomes)

    assert gate.status == "fail"
    cov = {c["key"]: c for c in gate.details["per_key_coverage"]}
    assert cov["base"]["count"] == 1
    assert cov["base"]["reachable"] == 2
    assert cov["base"]["ok"] is False
    assert cov["head"]["ok"] is True
    assert "under-covered" in gate.reason


def test_module_topology_diversity_exempts_reachably_constant_slot(monkeypatch) -> None:
    # `base` is constant across the ENTIRE reachable domain (1 value) -> exempt +
    # flagged as a single-candidate smell; `head` varies -> overall pass.
    choices = {seed: [("base", "same"), ("head", f"head_{seed % 2}")] for seed in range(20)}
    _patch_modular_choices(monkeypatch, choices)

    gate = check_module_topology_diversity("demo", [_outcome(seed) for seed in range(20)])

    assert gate.status == "pass"
    assert "base" in gate.details["single_value_slots"]
    cov = {c["key"]: c for c in gate.details["per_key_coverage"]}
    assert cov["base"]["reachable"] == 1
    assert cov["base"]["ok"] is True


def test_module_topology_diversity_counts_only_passing_seeds(monkeypatch) -> None:
    # `base` is a fresh value per seed (reachable=20) but only 4 seeds pass; per-key
    # coverage uses the 4 passing seeds only -> base realizes 4 distinct (>=2 -> ok).
    choices = {seed: [("base", f"base_{seed}")] for seed in range(20)}
    _patch_modular_choices(monkeypatch, choices)
    outcomes = [_outcome(seed, "pass" if seed < 4 else "fail") for seed in range(20)]

    gate = check_module_topology_diversity("demo", outcomes)

    assert gate.details["passing_seed_count"] == 4
    cov = {c["key"]: c for c in gate.details["per_key_coverage"]}
    assert cov["base"]["count"] == 4
    assert gate.status == "pass"


def test_module_topology_diversity_fails_on_invalid_slot_choices(monkeypatch) -> None:
    choices = {seed: [("base", f"base_{seed % 5}")] for seed in range(20)}
    choices[7] = ["bad"]
    _patch_modular_choices(monkeypatch, choices)

    gate = check_module_topology_diversity("demo", [_outcome(seed) for seed in range(20)])

    assert gate.status == "fail"
    assert gate.details["errors"][0]["seed"] == 7
    assert gate.details["errors"][0]["error_kind"] == "ValueError"


def test_reachable_topology_count_saturates(monkeypatch) -> None:
    # Sampler can reach exactly 3 distinct topologies; the probe should find all
    # 3 and report saturated once repeats accumulate.
    monkeypatch.setattr(
        "agent.template_sweep_coverage._slot_choices_for_seed",
        lambda slug, seed: [("base", f"b{seed % 3}")],
    )
    result = reachable_topology_count("demo", probe_seeds=100, patience=10)
    assert result["count"] == 3
    assert result["saturated"] is True
    assert result["probe_seeds_used"] <= 100


def test_reachable_topology_count_skips_rejected_seeds(monkeypatch) -> None:
    def sampler(slug: str, seed: int):
        if seed % 2:  # half the domain is rejected by the sampler
            raise ValueError("invalid seed domain")
        return [("base", f"b{seed % 4}")]

    monkeypatch.setattr("agent.template_sweep_coverage._slot_choices_for_seed", sampler)
    result = reachable_topology_count("demo", probe_seeds=200, patience=20)
    # Even seeds map to b0/b2 -> 2 reachable topologies; odd seeds raise and are skipped.
    assert result["count"] == 2


def test_module_topology_diversity_reports_reachable_topology(monkeypatch) -> None:
    choices = {
        seed: [("base", f"base_{seed % 10}"), ("head", f"head_{seed % 2}")] for seed in range(20)
    }
    _patch_modular_choices(monkeypatch, choices)

    gate = check_module_topology_diversity("demo", [_outcome(seed) for seed in range(20)])

    assert "reachable_topology" in gate.details
    assert gate.details["reachable_topology"]["count"] >= gate.details["distinct_count"]


def test_evaluate_gates_returns_only_module_topology(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "agent.template_sweep_coverage.check_module_topology_diversity",
        lambda slug, outcomes: CoverageGateResult(
            name="module_topology_diversity",
            status="pass",
            details={"distinct_count": 10},
        ),
    )

    gates = evaluate_gates(
        slug="demo",
        outcomes=[_outcome(seed) for seed in range(20)],
        repo_root=tmp_path,
    )

    assert isinstance(gates, CoverageGates)
    assert gates.to_dict().keys() == {"module_topology_diversity"}
    assert gates.module_topology_diversity.status == "pass"
    assert gates.all_pass_or_skipped() is True
    assert gates.failing_gates() == []


def test_legacy_nonmodular_templates_skip_the_gate() -> None:
    """Frozen-allowlist stock templates skip module_topology_diversity (their
    modular migration is deferred debt); NEW non-modular slugs still hard-fail."""
    outcomes = [_outcome(seed) for seed in range(20)]

    legacy = check_module_topology_diversity("box_fan_with_control_knob", outcomes)
    assert legacy.status == "skipped"
    assert legacy.details.get("legacy_nonmodular") is True

    new = check_module_topology_diversity("brand_new_nonmodular_thing", outcomes)
    assert new.status == "fail"
