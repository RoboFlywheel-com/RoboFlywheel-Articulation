# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import types
from pathlib import Path

import pytest

from agent import template_check
from agent.template_sweep import SeedOutcome
from sdk import TemplateDomain, component_slot, corner_case, multiplicity_slot


def _pass(seed: int, config: dict[str, object] | None = None) -> SeedOutcome:
    return SeedOutcome(
        seed=seed,
        verdict="pass",
        config=dict(config or {"seed": seed}),
        failure_type=None,
        failure_type_normalized=None,
        failure_details=None,
        elapsed_s=0.01,
        artifact_dir=f"/fake/seed_{seed}",
        motion_qc_report={
            "schema_version": 1,
            "status": "pass",
            "collision_free": True,
            "required_pose_ids": [],
            "executed_pose_ids": [],
            "missing_pose_ids": [],
            "required_edges": [],
            "covered_edges": [],
            "missing_edges": [],
            "joints": [],
            "poses": [],
        },
    )


def _fail(seed: int, config: dict[str, object] | None = None) -> SeedOutcome:
    return SeedOutcome(
        seed=seed,
        verdict="fail",
        config=dict(config or {"seed": seed}),
        failure_type="sample_failure",
        failure_type_normalized="sample_failure",
        failure_details="failure",
        elapsed_s=0.01,
    )


def test_preflight_does_not_execute_config_for_determinism(monkeypatch, tmp_path: Path) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text("# importable template surface is supplied by the test\n", encoding="utf-8")

    def config_from_seed(_seed: int):
        raise AssertionError("preflight must not execute config_from_seed")

    module = types.SimpleNamespace(
        config_from_seed=config_from_seed,
        build_demo=lambda config, assets=None: (config, assets),
        run_demo_tests=lambda model, config: (model, config),
    )
    monkeypatch.setattr(template_check.importlib, "import_module", lambda _name: module)

    report = template_check.preflight_template(tmp_path, "demo", "demo")

    assert report["status"] == "pass"
    assert report["template_mode"] == "legacy"
    assert report["findings"] == []
    assert report["phases"]["contract"]["status"] == "pass"
    assert report["phases"]["contract"]["builds"] == 0
    assert report["phases"]["domain_resolution"]["status"] == "not_applicable"


def test_preflight_blocks_post_mechanical_library_imports(monkeypatch, tmp_path: Path) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text(
        "from articraft.physics import derive_part_mass_properties\n",
        encoding="utf-8",
    )
    module = types.SimpleNamespace(
        config_from_seed=lambda seed: {"seed": seed},
        build_demo=lambda config, assets=None: (config, assets),
        run_demo_tests=lambda model, config: (model, config),
    )
    monkeypatch.setattr(template_check.importlib, "import_module", lambda _name: module)

    report = template_check.preflight_template(tmp_path, "demo", "demo")

    assert report["status"] == "fail"
    forbidden = [
        finding
        for finding in report["findings"]
        if finding["code"] == "forbidden_runtime_import"
    ]
    assert [finding["detail"] for finding in forbidden] == ["articraft.physics"]


@pytest.mark.parametrize("stage", ["random-16", "random-36", "corner"])
def test_mechanical_stages_never_open_material_or_physics_libraries(
    monkeypatch, tmp_path: Path, stage: str
) -> None:
    touched: list[Path] = []
    original_open = Path.open

    def guarded_open(self, *args, **kwargs):
        if any(
            token in self.parts
            for token in ("pbr_material_library", "pbr_material_physics")
        ):
            touched.append(self)
            raise AssertionError(f"mechanical stage touched post-gate data: {self}")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded_open)
    monkeypatch.setattr(
        template_check,
        "preflight_template",
        lambda *_args, **_kwargs: {
            "status": "pass",
            "findings": [],
            "template_mode": "legacy",
            "quality_contract": {"version": 1, "sha256": "contract"},
        },
    )
    monkeypatch.setattr(
        template_check.importlib,
        "import_module",
        lambda _name: types.SimpleNamespace(config_from_seed=lambda seed: {"seed": seed}),
    )
    monkeypatch.setattr(template_check, "mechanical_hash", lambda *_args: "mechanical")
    monkeypatch.setattr(
        template_check,
        "_cached_seed_sweep",
        lambda **kwargs: ([_pass(seed) for seed in kwargs["seeds"]], [], [], 0.0),
    )
    monkeypatch.setattr(
        template_check,
        "_legacy_corner_stage",
        lambda **_kwargs: {
            "status": "pass",
            "passed": 1,
            "failed": 0,
            "repair_gate": {"status": "not_needed"},
        },
    )

    report = template_check.check_template(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        stage=stage,  # type: ignore[arg-type]
    )

    assert report["verdict"] == "pass"
    assert touched == []


def test_preflight_cache_reuses_probe_and_expected_contract_blocks_repair(
    monkeypatch,
    tmp_path: Path,
) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text("# module supplied by test\n", encoding="utf-8")
    calls = 0
    module = types.SimpleNamespace(
        config_from_seed=lambda seed: {"seed": seed},
        build_demo=lambda config, assets=None: (config, assets),
        run_demo_tests=lambda model, config: (model, config),
    )

    def import_module(_name: str):
        nonlocal calls
        calls += 1
        return module

    monkeypatch.setattr(template_check.importlib, "import_module", import_module)
    cache = tmp_path / "cache"
    first = template_check.preflight_template(
        tmp_path,
        "demo",
        "demo",
        cache_dir=cache,
    )
    repeated = template_check.preflight_template(
        tmp_path,
        "demo",
        "demo",
        cache_dir=cache,
    )
    guarded = template_check.preflight_template(
        tmp_path,
        "demo",
        "demo",
        cache_dir=cache,
        expected_quality_contract_sha256="different",
    )

    assert first["status"] == "pass"
    assert repeated["cache_hit"] is True
    assert calls == 1
    assert guarded["status"] == "fail"
    assert guarded["repair_gate"]["status"] == "repair_required"
    assert guarded["checks"]["design_alignment"]["status"] == "fail"
    assert guarded["phases"]["contract"]["status"] == "fail"
    assert guarded["phases"]["contract"]["blocking_finding_ids"] == [
        guarded["findings"][0]["finding_id"]
    ]
    assert {finding["code"] for finding in guarded["findings"]} == {
        "quality_contract_changed_during_repair"
    }


def test_preflight_requires_template_domain_when_design_exists(monkeypatch, tmp_path: Path) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text("# importable template surface is supplied by the test\n", encoding="utf-8")
    design = tmp_path / "articraft_template_authoring" / "designs" / "demo.json"
    design.parent.mkdir(parents=True)
    design.write_text("{}\n", encoding="utf-8")
    module = types.SimpleNamespace(
        config_from_seed=lambda seed: {"seed": seed},
        build_demo=lambda config, assets=None: (config, assets),
        run_demo_tests=lambda model, config: (model, config),
    )
    monkeypatch.setattr(template_check.importlib, "import_module", lambda _name: module)

    report = template_check.preflight_template(tmp_path, "demo", "demo")

    assert report["status"] == "fail"
    assert report["template_mode"] == "incomplete_migration"
    assert {finding["code"] for finding in report["findings"]} == {
        "required_export_missing",
        "template_design_invalid",
    }
    assert all(finding["blocking"] for finding in report["findings"])
    assert report["phases"]["contract"]["status"] == "fail"
    assert report["phases"]["domain_resolution"]["status"] == "not_run"


def test_generated_seed_and_corner_scripts_forward_template_domain() -> None:
    from agent.template_sweep import _GENERIC_MODEL_TEMPLATE
    from cli.template import GENERIC_MODEL_TEMPLATE

    for source in (_GENERIC_MODEL_TEMPLATE, GENERIC_MODEL_TEMPLATE):
        rendered = source.format(slug="demo", stem="demo", seed=0)
        assert 'TEMPLATE_DOMAIN = getattr(_template_module, "TEMPLATE_DOMAIN", None)' in rendered

    corner = template_check._corner_script("demo", "demo", {})
    assert "TEMPLATE_DOMAIN = _template.TEMPLATE_DOMAIN" in corner


def test_random_stages_reuse_cumulative_seed_cache(monkeypatch, tmp_path: Path) -> None:
    calls: list[list[int]] = []

    monkeypatch.setattr(
        template_check,
        "preflight_template",
        lambda *_args, **_kwargs: {
            "status": "pass",
            "findings": [],
            "template_imports": [],
            "single_file_status": "self_contained",
            "quality_contract": {"version": 1, "sha256": "contract"},
        },
    )
    monkeypatch.setattr(
        template_check.importlib,
        "import_module",
        lambda _name: types.SimpleNamespace(config_from_seed=lambda seed: {"seed": seed}),
    )
    monkeypatch.setattr(template_check, "mechanical_hash", lambda *_args: "mechanical")
    monkeypatch.setattr(template_check, "compiled_artifact_is_valid", lambda path: bool(path))

    def fake_run_seed_outcomes(*, seeds: list[int], **_kwargs):
        calls.append(list(seeds))
        return [_pass(seed) for seed in seeds]

    monkeypatch.setattr(template_check, "run_seed_outcomes", fake_run_seed_outcomes)

    common = {
        "repo_root": tmp_path,
        "slug": "demo",
        "stem": "demo",
        "cache_dir": tmp_path / "cache",
        "max_workers": 1,
    }
    first = template_check.check_template(stage="random-16", **common)
    promoted = template_check.check_template(stage="random-36", **common)
    repeated = template_check.check_template(stage="random-36", **common)

    assert first["random_sweep"]["cache_hits"] == 0
    assert first["random_sweep"]["cache_misses"] == 16
    assert promoted["random_sweep"]["cache_hits"] == 16
    assert promoted["random_sweep"]["cache_misses"] == 20
    assert repeated["random_sweep"]["cache_hits"] == 36
    assert repeated["random_sweep"]["cache_misses"] == 0
    assert calls == [list(range(16)), list(range(16, 36))]
    assert first["completion_status"] == "legacy_compatible"
    assert promoted["completion_status"] == "legacy_compatible"
    gate = first["random_sweep"]["repair_gate"]
    assert gate["quality_contract"]["sha256"] == "contract"
    assert gate["repair_rerun"] == {
        "stage": "random-16",
        "expected_quality_contract_sha256": "contract",
    }


def test_check_template_preflight_failure_stays_at_preflight(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    def failed_preflight(*_args, **kwargs):
        captured.update(kwargs)
        return {
            "status": "fail",
            "findings": [{"code": "parameter_no_structural_effect"}],
        }

    monkeypatch.setattr(template_check, "preflight_template", failed_preflight)
    report = template_check.check_template(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        stage="random-16",
        expected_quality_contract_sha256="before-repair",
    )

    assert report["verdict"] == "fail"
    assert report["next_stage"] == "preflight"
    assert report["random_sweep"] == {}
    assert captured["expected_quality_contract_sha256"] == "before-repair"


def test_default_random_threshold_is_ninety_percent() -> None:
    outcomes = [_pass(seed) for seed in range(15)]
    outcomes.append(
        SeedOutcome(
            seed=15,
            verdict="fail",
            config={"seed": 15},
            failure_type="sample_failure",
            failure_type_normalized="sample_failure",
            failure_details="failure",
            elapsed_s=0.01,
        )
    )
    summary = template_check._random_summary(
        seeds=list(range(16)),
        outcomes=outcomes,
        hits=[],
        misses=list(range(16)),
        elapsed_s=0.1,
        pass_threshold=0.90,
    )
    assert summary["status"] == "pass"
    assert summary["pass_rate"] == 0.9375


def test_rare_candidate_failing_everywhere_cannot_hide_under_the_threshold() -> None:
    """A candidate drawn once in seeds 0-15 used to ride random-16's tolerated failure.

    Measured on pictureX_0611_guitar_tuning_peg_mechanism: `open_plate` occurs in
    exactly 1 of seeds 0-15, and 15/16 = 0.9375 clears the 0.90 threshold, so a
    candidate broken in every seed that reaches it still passed the stage.
    """
    domain = TemplateDomain((component_slot("plate", ("closed_plate", "open_plate")),))
    outcomes = [_pass(seed, {"plate": "closed_plate"}) for seed in range(15)]
    outcomes.append(_fail(15, {"plate": "open_plate"}))

    summary = template_check._random_summary(
        seeds=list(range(16)),
        outcomes=outcomes,
        hits=[],
        misses=list(range(16)),
        elapsed_s=0.1,
        pass_threshold=0.90,
        domain=domain,
    )

    assert summary["threshold_pass"] is True
    assert summary["pass_rate"] == 0.9375
    assert summary["status"] == "fail"
    coverage = summary["candidate_coverage"]
    assert coverage["status"] == "fail"
    assert coverage["no_passing_seed"] == ["plate.open_plate"]
    assert "0/1 seeds pass" in coverage["reason"]


def test_candidate_never_drawn_is_uncovered_not_failed() -> None:
    """Corner owns candidates absent from cumulative seeds 0-35; random must not fail them."""
    domain = TemplateDomain((component_slot("plate", ("closed_plate", "open_plate")),))
    outcomes = [_pass(seed, {"plate": "closed_plate"}) for seed in range(16)]

    summary = template_check._random_summary(
        seeds=list(range(16)),
        outcomes=outcomes,
        hits=[],
        misses=list(range(16)),
        elapsed_s=0.1,
        pass_threshold=0.90,
        domain=domain,
    )

    coverage = summary["candidate_coverage"]
    assert summary["status"] == "pass"
    assert coverage["status"] == "pass"
    assert coverage["uncovered"] == ["plate.open_plate"]
    assert coverage["covered"] == 1
    assert coverage["declared"] == 2


def test_candidate_gate_covers_multiplicity_values() -> None:
    domain = TemplateDomain(
        (
            component_slot("plate", ("closed_plate",)),
            multiplicity_slot("banks", (1, 2, 3), item_slot="plate"),
        )
    )
    outcomes = [_pass(seed, {"plate": "closed_plate", "banks": 1}) for seed in range(15)]
    outcomes.append(_fail(15, {"plate": "closed_plate", "banks": 3}))

    summary = template_check._random_summary(
        seeds=list(range(16)),
        outcomes=outcomes,
        hits=[],
        misses=list(range(16)),
        elapsed_s=0.1,
        pass_threshold=0.90,
        domain=domain,
    )

    coverage = summary["candidate_coverage"]
    assert summary["status"] == "fail"
    assert coverage["no_passing_seed"] == ["banks.3"]
    assert coverage["uncovered"] == ["banks.2"]


def test_candidate_gate_is_not_applicable_without_a_domain() -> None:
    outcomes = [_pass(seed) for seed in range(15)]
    outcomes.append(_fail(15))

    summary = template_check._random_summary(
        seeds=list(range(16)),
        outcomes=outcomes,
        hits=[],
        misses=list(range(16)),
        elapsed_s=0.1,
        pass_threshold=0.90,
    )

    assert summary["status"] == "pass"
    assert summary["candidate_coverage"]["status"] == "not_applicable"


def test_strict_mode_enforces_ninety_percent_floor_and_reports_tolerance(
    monkeypatch, tmp_path: Path
) -> None:
    outcomes = [_pass(seed, {"door": "panel"}) for seed in range(33)]
    outcomes.extend(_fail(seed, {"door": "panel"}) for seed in range(33, 36))
    domain = TemplateDomain((component_slot("door", ("panel",)),))
    monkeypatch.setattr(
        template_check,
        "preflight_template",
        lambda *_args, **_kwargs: {
            "status": "pass",
            "template_mode": "strict",
            "quality_contract": {"version": 1, "sha256": "contract"},
        },
    )
    monkeypatch.setattr(
        template_check.importlib,
        "import_module",
        lambda _name: types.SimpleNamespace(TEMPLATE_DOMAIN=domain),
    )
    monkeypatch.setattr(template_check, "mechanical_hash", lambda *_args: "mechanical")
    monkeypatch.setattr(
        template_check,
        "_cached_seed_sweep",
        lambda **_kwargs: (outcomes, [], list(range(36)), 0.1),
    )
    monkeypatch.setattr(
        template_check,
        "_domain_corner_stage",
        lambda **_kwargs: {"status": "pass", "repair_gate": {}},
    )

    report = template_check.check_template(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        stage="corner",
        pass_threshold=0.25,
    )

    assert report["verdict"] == "pass"
    assert report["random_sweep"]["pass_threshold"] == 0.90
    assert report["random_sweep"]["pass_rate"] == 0.916667
    assert report["completion_status"] == "strict_ready_with_tolerance"
    assert report["pass_threshold_policy"] == {
        "requested": 0.25,
        "effective": 0.90,
        "strict_minimum": 0.90,
    }


def test_strict_corner_reports_full_ready_when_all_random_seeds_pass(
    monkeypatch, tmp_path: Path
) -> None:
    outcomes = [_pass(seed, {"door": "panel"}) for seed in range(36)]
    domain = TemplateDomain((component_slot("door", ("panel",)),))
    monkeypatch.setattr(
        template_check,
        "preflight_template",
        lambda *_args, **_kwargs: {
            "status": "pass",
            "template_mode": "strict",
            "quality_contract": {"version": 1, "sha256": "contract"},
        },
    )
    monkeypatch.setattr(
        template_check.importlib,
        "import_module",
        lambda _name: types.SimpleNamespace(TEMPLATE_DOMAIN=domain),
    )
    monkeypatch.setattr(template_check, "mechanical_hash", lambda *_args: "mechanical")
    monkeypatch.setattr(
        template_check,
        "_cached_seed_sweep",
        lambda **_kwargs: (outcomes, [], list(range(36)), 0.1),
    )
    monkeypatch.setattr(
        template_check,
        "_domain_corner_stage",
        lambda **_kwargs: {"status": "pass", "repair_gate": {}},
    )

    report = template_check.check_template(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        stage="corner",
    )

    assert report["verdict"] == "pass"
    assert report["completion_status"] == "strict_ready"


def test_repair_findings_group_seeds_and_map_entities_to_component_functions(
    tmp_path: Path,
) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text(
        "\n".join(
            (
                "def _door_panel_build():",
                "    return 'door__panel__body', 'door__panel__hinge'",
                "",
                "def _frame_post_build():",
                "    return 'frame__post__body'",
                "",
                "def build_demo(config, assets=None):",
                "    return _door_panel_build(), _frame_post_build()",
                "",
            )
        ),
        encoding="utf-8",
    )
    design = tmp_path / "articraft_template_authoring" / "designs" / "demo.json"
    design.parent.mkdir(parents=True)
    design.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "slug": "demo",
                "source_map_path": "source_maps/demo.md",
                "source_map_sha256": "abc",
                "slots": [
                    {
                        "name": "door",
                        "component_type": "door",
                        "candidates": [
                            {
                                "name": "panel",
                                "implementation_function": "_door_panel_build",
                                "record_id": "rec_door",
                                "revision": "rev_000001",
                                "source_spans": ["model.py:L10-L30"],
                            }
                        ],
                    },
                    {
                        "name": "frame",
                        "component_type": "frame",
                        "candidates": [
                            {
                                "name": "post",
                                "implementation_function": "_frame_post_build",
                                "record_id": "rec_frame",
                                "revision": "rev_000002",
                                "source_spans": ["model.py:L40-L70"],
                            }
                        ],
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    details = (
        "Part overlaps detected:\n"
        "pair=('door__panel__body','frame__post__body') "
        "elem_a=#0 'door_panel':Box elem_b=#0 'frame_post':Box "
        "pose={'door__panel__hinge': 1.57}"
    )

    def failed(seed: int, width: float) -> SeedOutcome:
        return SeedOutcome(
            seed=seed,
            verdict="fail",
            config={"door": "panel", "frame": "post", "width": width},
            failure_type="harness_motion_qc(joints=1,poses=3)",
            failure_type_normalized="harness_motion_qc",
            failure_details=details,
            elapsed_s=0.01,
            failures=(
                {
                    "check": "harness_motion_qc(joints=1,poses=3)",
                    "check_normalized": "harness_motion_qc",
                    "kind": "test_failure",
                    "code": "TEST_FAILURE",
                    "details": details,
                },
            ),
        )

    outcomes = [
        _pass(0),
        failed(1, 0.4),
        SeedOutcome(
            seed=2,
            verdict="pass",
            config={"door": "panel", "frame": "post", "width": 0.35},
            failure_type=None,
            failure_type_normalized=None,
            failure_details=None,
            elapsed_s=0.01,
        ),
        failed(3, 0.5),
    ]

    findings, localization = template_check.build_repair_findings(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        outcomes=outcomes,
    )

    assert localization["status"] == "available"
    assert localization["design"]["status"] == "available"
    assert len(findings) == 1
    finding = findings[0]
    assert finding["affected_seeds"] == [1, 3]
    assert finding["entities"]["joints"] == ["door__panel__hinge"]
    assert finding["suggested_scope"] == "assembly_or_interface"
    assert finding["config_evidence"]["varying_fields"] == ["width"]
    assert finding["config_evidence"]["nearest_passing"]["seed"] == 2
    owners = {owner["function"]: owner for owner in finding["code_owners"]}
    assert owners["_door_panel_build"]["slot"] == "door"
    assert owners["_frame_post_build"]["slot"] == "frame"
    assert owners["build_demo"]["confidence"] == "context"
    assert {item["function"] for item in finding["selected_component_context"]} == {
        "_door_panel_build",
        "_frame_post_build",
    }
    policy = finding["source_review_policy"]
    assert policy["decision"] == "recommended"
    assert policy["blocking"] is False
    assert policy["source_targets"] == [
        {
            "slot": "door",
            "candidate": "panel",
            "record_id": "rec_door",
            "revision": "rev_000001",
            "source_spans": ["model.py:L10-L30"],
        },
        {
            "slot": "frame",
            "candidate": "post",
            "record_id": "rec_frame",
            "revision": "rev_000002",
            "source_spans": ["model.py:L40-L70"],
        },
    ]
    assert template_check._repair_gate(findings)["status"] == "repair_allowed"


def test_interface_contract_requires_source_review_with_exact_target(tmp_path: Path) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text(
        "def _wheel_build():\n    return 'ground_support__rolling_caster_star__wheel_spin'\n",
        encoding="utf-8",
    )
    design = tmp_path / "articraft_template_authoring" / "designs" / "demo.json"
    design.parent.mkdir(parents=True)
    design.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "slug": "demo",
                "source_map_path": "source_maps/demo.md",
                "source_map_sha256": "abc",
                "slots": [
                    {
                        "name": "ground_support",
                        "component_type": "ground_support",
                        "candidates": [
                            {
                                "name": "rolling_caster_star",
                                "implementation_function": "_wheel_build",
                                "record_id": "rec_caster",
                                "revision": "rev_000003",
                                "source_spans": ["model.py:L178-L273"],
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    details = "joint='ground_support__rolling_caster_star__wheel_spin' axis drifted"
    outcome = SeedOutcome(
        seed=5,
        verdict="fail",
        config={"ground_support": "rolling_caster_star"},
        failure_type="fail_if_interface_mate_mismatch",
        failure_type_normalized="fail_if_interface_mate_mismatch",
        failure_details=details,
        elapsed_s=0.01,
        failures=(
            {
                "check": "fail_if_interface_mate_mismatch",
                "check_normalized": "fail_if_interface_mate_mismatch",
                "kind": "test_failure",
                "code": "TEST_FAILURE",
                "details": details,
            },
        ),
    )

    findings, _localization = template_check.build_repair_findings(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        outcomes=[outcome],
    )

    policy = findings[0]["source_review_policy"]
    assert policy == {
        "version": 1,
        "decision": "required",
        "blocking": True,
        "reason_codes": ["rotational_interface_contract"],
        "source_targets": [
            {
                "slot": "ground_support",
                "candidate": "rolling_caster_star",
                "record_id": "rec_caster",
                "revision": "rev_000003",
                "source_spans": ["model.py:L178-L273"],
            }
        ],
        "unresolved_owners": [],
        "next_action": "review_source_then_repair",
    }
    gate = template_check._repair_gate(findings)
    assert gate["status"] == "source_review_required"
    assert gate["blocking_finding_ids"] == [findings[0]["finding_id"]]
    assert gate["source_targets"] == policy["source_targets"]
    summary = template_check._random_summary(
        seeds=[5],
        outcomes=[outcome],
        hits=[],
        misses=[5],
        elapsed_s=0.1,
        pass_threshold=0.90,
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
    )
    assert summary["repair_gate"]["status"] == "source_review_required"
    assert summary["repair_gate"]["source_targets"] == policy["source_targets"]


def test_source_review_uses_selected_candidate_for_shared_builder(tmp_path: Path) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text(
        "def _shared_wheel_build():\n    return 'wheel_spin'\n",
        encoding="utf-8",
    )
    design = tmp_path / "articraft_template_authoring" / "designs" / "demo.json"
    design.parent.mkdir(parents=True)
    design.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "slug": "demo",
                "source_map_path": "source_maps/demo.md",
                "source_map_sha256": "abc",
                "slots": [
                    {
                        "name": "ground_support",
                        "component_type": "ground_support",
                        "candidates": [
                            {
                                "name": "fixed_wheel",
                                "implementation_function": "_shared_wheel_build",
                                "record_id": "rec_fixed",
                                "revision": "rev_000001",
                                "source_spans": ["model.py:L10-L30"],
                            },
                            {
                                "name": "rolling_caster_star",
                                "implementation_function": "_shared_wheel_build",
                                "record_id": "rec_caster",
                                "revision": "rev_000002",
                                "source_spans": ["model.py:L40-L80"],
                            },
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    outcome = SeedOutcome(
        seed=9,
        verdict="fail",
        config={"ground_support": "rolling_caster_star"},
        failure_type="fail_if_interface_mate_mismatch",
        failure_type_normalized="fail_if_interface_mate_mismatch",
        failure_details="joint='wheel_spin' axis drifted",
        elapsed_s=0.01,
    )

    findings, _localization = template_check.build_repair_findings(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        outcomes=[outcome],
    )

    assert findings[0]["source_review_policy"]["source_targets"] == [
        {
            "slot": "ground_support",
            "candidate": "rolling_caster_star",
            "record_id": "rec_caster",
            "revision": "rev_000002",
            "source_spans": ["model.py:L40-L80"],
        }
    ]


def test_required_source_review_blocks_when_design_mapping_is_incomplete(
    tmp_path: Path,
) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text(
        "def _wheel_build():\n    return 'ground_support__rolling_caster_star__wheel_spin'\n",
        encoding="utf-8",
    )
    design = tmp_path / "articraft_template_authoring" / "designs" / "demo.json"
    design.parent.mkdir(parents=True)
    design.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "slug": "demo",
                "source_map_path": "source_maps/demo.md",
                "source_map_sha256": "abc",
                "slots": [
                    {
                        "name": "ground_support",
                        "component_type": "ground_support",
                        "candidates": [
                            {
                                "name": "rolling_caster_star",
                                "implementation_function": "_wheel_build",
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    details = "joint='ground_support__rolling_caster_star__wheel_spin' axis drifted"
    outcome = SeedOutcome(
        seed=6,
        verdict="fail",
        config={"ground_support": "rolling_caster_star"},
        failure_type="fail_if_interface_mate_mismatch",
        failure_type_normalized="fail_if_interface_mate_mismatch",
        failure_details=details,
        elapsed_s=0.01,
    )

    findings, _localization = template_check.build_repair_findings(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        outcomes=[outcome],
    )

    policy = findings[0]["source_review_policy"]
    assert policy["decision"] == "required"
    assert policy["blocking"] is True
    assert policy["source_targets"] == []
    assert policy["unresolved_owners"] == [
        {"slot": "ground_support", "candidate": "rolling_caster_star"}
    ]
    assert "source_target_unresolved" in policy["reason_codes"]
    assert policy["next_action"] == "repair_source_mapping_before_template"


def test_required_source_review_blocks_when_declared_design_is_invalid(
    tmp_path: Path,
) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text(
        "def _wheel_build():\n    return 'wheel_spin'\n",
        encoding="utf-8",
    )
    design = tmp_path / "articraft_template_authoring" / "designs" / "demo.json"
    design.parent.mkdir(parents=True)
    design.write_text("{}\n", encoding="utf-8")
    outcome = SeedOutcome(
        seed=8,
        verdict="fail",
        config={"support": "rolling"},
        failure_type="fail_if_interface_mate_mismatch",
        failure_type_normalized="fail_if_interface_mate_mismatch",
        failure_details="joint='wheel_spin' axis drifted",
        elapsed_s=0.01,
    )

    findings, localization = template_check.build_repair_findings(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        outcomes=[outcome],
    )

    assert localization["design"]["status"] == "invalid"
    policy = findings[0]["source_review_policy"]
    assert policy["decision"] == "required"
    assert policy["blocking"] is True
    assert "source_target_unresolved" in policy["reason_codes"]
    assert policy["next_action"] == "repair_source_mapping_before_template"


def test_required_source_review_falls_back_to_selected_design_context(
    tmp_path: Path,
) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text(
        "def _bearing_build():\n"
        "    return object()\n\n"
        "def build_demo():\n"
        "    return 'beacon_spin'\n",
        encoding="utf-8",
    )
    design = tmp_path / "articraft_template_authoring" / "designs" / "demo.json"
    design.parent.mkdir(parents=True)
    design.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "slug": "demo",
                "source_map_path": "source_maps/demo.md",
                "source_map_sha256": "abc",
                "slots": [
                    {
                        "name": "bearing",
                        "component_type": "bearing",
                        "candidates": [
                            {
                                "name": "pedestal",
                                "implementation_function": "_bearing_build",
                                "record_id": "rec_demo",
                                "revision": "rev_000001",
                                "source_spans": ["model.py:L10-L20"],
                            }
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    outcome = SeedOutcome(
        seed=0,
        verdict="fail",
        config={"bearing": "pedestal"},
        failure_type="fail_if_articulation_origin_far_from_geometry",
        failure_type_normalized="fail_if_articulation_origin_far_from_geometry",
        failure_details="joint='beacon_spin' axis is far from the parent",
        elapsed_s=0.01,
    )

    findings, _localization = template_check.build_repair_findings(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        outcomes=[outcome],
    )

    policy = findings[0]["source_review_policy"]
    assert policy["decision"] == "required"
    assert policy["blocking"] is True
    assert policy["source_targets"] == [
        {
            "slot": "bearing",
            "candidate": "pedestal",
            "record_id": "rec_demo",
            "revision": "rev_000001",
            "source_spans": ["model.py:L10-L20"],
        }
    ]
    assert policy["unresolved_owners"] == []
    assert "source_target_unresolved" not in policy["reason_codes"]
    assert policy["next_action"] == "review_source_then_repair"


def test_legacy_interface_contract_recommends_review_without_blocking(tmp_path: Path) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text(
        "def _wheel_build():\n    return 'wheel_spin'\n",
        encoding="utf-8",
    )
    outcome = SeedOutcome(
        seed=7,
        verdict="fail",
        config={"support": "rolling"},
        failure_type="fail_if_interface_mate_mismatch",
        failure_type_normalized="fail_if_interface_mate_mismatch",
        failure_details="joint='wheel_spin' axis drifted",
        elapsed_s=0.01,
    )

    findings, localization = template_check.build_repair_findings(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        outcomes=[outcome],
    )

    assert localization["design"]["status"] == "undeclared"
    policy = findings[0]["source_review_policy"]
    assert policy["decision"] == "recommended"
    assert policy["blocking"] is False
    assert "legacy_source_mapping_unavailable" in policy["reason_codes"]
    assert template_check._repair_gate(findings)["status"] == "repair_allowed"


def test_repair_finding_maps_runtime_traceback_to_exact_function(tmp_path: Path) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text(
        "def _broken_build():\n"
        "    raise ValueError('bad radius')\n\n"
        "def build_demo(config, assets=None):\n"
        "    return _broken_build()\n",
        encoding="utf-8",
    )
    details = f"bad radius\nLocation: {template}:2\nCode: raise ValueError('bad radius')"
    outcome = SeedOutcome(
        seed=4,
        verdict="fail",
        config={"radius": -1.0},
        failure_type="COMPILE_RUNTIME_FAILURE",
        failure_type_normalized="COMPILE_RUNTIME_FAILURE",
        failure_details=details,
        elapsed_s=0.01,
    )

    findings, localization = template_check.build_repair_findings(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        outcomes=[outcome],
    )

    assert localization["design"]["status"] == "undeclared"
    assert findings[0]["suggested_scope"] == "runtime_function"
    assert findings[0]["code_owners"] == [
        {
            "function": "_broken_build",
            "path": "agent/templates/demo.py",
            "line": 1,
            "end_line": 2,
            "reasons": ["runtime_traceback"],
            "confidence": "exact",
        }
    ]
    assert findings[0]["source_review_policy"]["decision"] == "not_required"
    assert findings[0]["source_review_policy"]["blocking"] is False


def test_domain_corner_reports_named_repair_cases(monkeypatch, tmp_path: Path) -> None:
    template = tmp_path / "agent" / "templates" / "demo.py"
    template.parent.mkdir(parents=True)
    template.write_text(
        "def _door_build():\n"
        "    return 'door__panel__body'\n\n"
        "def build_demo(config, assets=None):\n"
        "    return _door_build()\n",
        encoding="utf-8",
    )
    domain = TemplateDomain((component_slot("door", ("panel",)),))
    module = types.SimpleNamespace(TEMPLATE_CORNERS=())
    details = "part='door__panel__body' connected=1/2"
    monkeypatch.setattr(
        template_check,
        "_run_domain_corner",
        lambda **_kwargs: (
            {
                "name": "door_at_upper",
                "status": "fail",
                "config": {"door": "panel"},
                "overrides": {"door": "panel"},
                "error": details,
                "failures": [
                    {
                        "check": "fail_if_isolated_parts()",
                        "check_normalized": "fail_if_isolated_parts",
                        "kind": "isolated_part",
                        "code": "TEST_ISOLATED_PART",
                        "details": details,
                    }
                ],
                "elapsed_s": 0.01,
            },
            False,
        ),
    )

    summary = template_check._domain_corner_stage(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        module=module,
        domain=domain,
        random_outcomes=[],
        cache_root=tmp_path / "cache",
        compile_timeout_s=1.0,
    )

    assert summary["status"] == "fail"
    assert summary["repair_findings"][0]["affected_cases"] == ["door_at_upper"]
    assert summary["repair_findings"][0]["affected_case_count"] == 1
    assert (
        summary["repair_findings"][0]["config_evidence"]["representative_failed_case"]
        == "door_at_upper"
    )
    assert summary["repair_findings"][0]["source_review_policy"]["decision"] == "recommended"
    assert summary["repair_gate"]["status"] == "repair_allowed"


def test_domain_corner_only_supplements_random_36_coverage() -> None:
    domain = TemplateDomain(
        (
            component_slot("door", ("panel", "slab")),
            multiplicity_slot("door_count", (1, 2, 3), item_slot="door"),
        )
    )
    cases, coverage = template_check._missing_domain_corner_cases(
        domain,
        [
            _pass(0, {"door": "panel", "door_count": 1}),
            _pass(1, {"door": "slab", "door_count": 2}),
        ],
    )

    assert [case.name for case in cases] == ["edge_door_count_3"]
    assert coverage["status"] == "supplemented"
    assert coverage["slots"]["door"]["missing"] == []
    assert coverage["slots"]["door_count"]["missing"] == [3]


def test_authored_corner_runs_even_when_random_coverage_is_complete(
    monkeypatch, tmp_path: Path
) -> None:
    domain = TemplateDomain((component_slot("door", ("panel",)),))
    authored = corner_case("risk_panel_open", {"door": "panel"})
    module = types.SimpleNamespace(TEMPLATE_CORNERS=(authored,))
    seen: list[str] = []

    def run_corner(**kwargs):
        case = kwargs["case"]
        seen.append(case.name)
        return (
            {
                "name": case.name,
                "status": "pass",
                "config": {"door": "panel"},
                "overrides": {"door": "panel"},
                "error": None,
                "failures": [],
                "elapsed_s": 0.01,
            },
            False,
        )

    monkeypatch.setattr(template_check, "_run_domain_corner", run_corner)
    summary = template_check._domain_corner_stage(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        module=module,
        domain=domain,
        random_outcomes=[_pass(0, {"door": "panel"})],
        cache_root=tmp_path / "cache",
        compile_timeout_s=1.0,
    )

    assert seen == ["risk_panel_open"]
    assert summary["status"] == "pass"
    assert summary["coverage"]["status"] == "complete"
    assert summary["supplemental_cases"] == []
    assert summary["authored_case_count"] == 1


def test_domain_corner_skips_redundant_automatic_cases(monkeypatch, tmp_path: Path) -> None:
    domain = TemplateDomain((component_slot("door", ("panel",)),))
    module = types.SimpleNamespace(TEMPLATE_CORNERS=())

    def fail_if_called(**_kwargs):
        raise AssertionError("complete random coverage should not rerun an automatic corner")

    monkeypatch.setattr(template_check, "_run_domain_corner", fail_if_called)
    summary = template_check._domain_corner_stage(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        module=module,
        domain=domain,
        random_outcomes=[_pass(0, {"door": "panel"})],
        cache_root=tmp_path / "cache",
        compile_timeout_s=1.0,
    )

    assert summary["status"] == "pass"
    assert summary["passed"] == 0
    assert summary["failed"] == 0
    assert summary["coverage"]["status"] == "complete"
    assert summary["supplemental_cases"] == []
    assert summary["authored_case_count"] == 0


def test_legacy_corner_carries_nonblocking_source_review_gate(monkeypatch, tmp_path: Path) -> None:
    plan = types.SimpleNamespace(
        status="ok",
        seeds=[4],
        to_dict=lambda: {"status": "ok", "seeds": [4]},
    )
    outcome = SeedOutcome(
        seed=4,
        verdict="fail",
        config={"support": "rolling"},
        failure_type="fail_if_interface_mate_mismatch",
        failure_type_normalized="fail_if_interface_mate_mismatch",
        failure_details="joint='wheel_spin' axis drifted",
        elapsed_s=0.01,
    )
    monkeypatch.setattr(template_check, "select_corner_seeds", lambda *_args, **_kwargs: plan)
    monkeypatch.setattr(
        template_check,
        "_cached_seed_sweep",
        lambda **_kwargs: ([outcome], [], [4], 0.1),
    )

    summary = template_check._legacy_corner_stage(
        repo_root=tmp_path,
        slug="demo",
        stem="demo",
        mechanical="mechanical",
        cache_root=tmp_path / "cache",
        max_workers=1,
        compile_timeout_s=1.0,
        progress=None,
    )

    assert summary["repair_findings"][0]["source_review_policy"]["decision"] == "recommended"
    assert summary["repair_gate"]["status"] == "repair_allowed"


def test_joint_motion_report_requires_bounded_edges() -> None:
    actual = {
        "status": "pass",
        "required_pose_ids": ["hinge:lower", "hinge:upper"],
        "executed_pose_ids": ["hinge:lower", "hinge:upper"],
        "required_pose_kind_counts": {"single_joint_edge": 2},
        "executed_pose_kind_counts": {"single_joint_edge": 2},
        "missing_edges": [],
        "joints": [
            {
                "joint": "hinge",
                "joint_type": "revolute",
                "required_edges": ["lower", "upper"],
                "covered_edges": ["lower", "upper"],
            }
        ],
    }
    report = template_check.joint_motion_edge_coverage([actual])
    assert report["status"] == "pass"
    assert report["joints"][0]["covered_edges"] == ["lower", "upper"]
    assert report["required_pose_kind_counts"] == {"single_joint_edge": 2}
    assert report["executed_pose_kind_counts"] == {"single_joint_edge": 2}


def test_joint_motion_report_rejects_missing_actual_execution_record() -> None:
    report = template_check.joint_motion_edge_coverage([None])

    assert report["status"] == "fail"
    assert report["missing_report_indexes"] == [0]
