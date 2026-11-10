# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent import template_sweep
from agent.template_sweep import (
    SeedOutcome,
    SweepReport,
    _config_to_dict,
    _extract_failure,
    _normalize_failure_type,
    disconnected_geometry_warning_details,
    extract_failure_entities,
    parse_seed_spec,
    report_to_json,
    run_sweep,
)
from agent.template_sweep_coverage import CoverageGateResult, CoverageGates


def test_parse_seed_spec_handles_ranges_and_lists() -> None:
    assert parse_seed_spec("0-2") == [0, 1, 2]
    assert parse_seed_spec("1,3,5") == [1, 3, 5]
    assert parse_seed_spec("0-2, 5, 8-9") == [0, 1, 2, 5, 8, 9]


def test_parse_seed_spec_dedups_repeats() -> None:
    assert parse_seed_spec("0-2, 1") == [0, 1, 2]


def test_parse_seed_spec_rejects_inverted_range() -> None:
    with pytest.raises(ValueError, match="Invalid seed range"):
        parse_seed_spec("5-1")


def test_parse_seed_spec_rejects_empty() -> None:
    with pytest.raises(ValueError, match="At least one seed"):
        parse_seed_spec("   ")


def test_normalize_failure_type_strips_param_parens() -> None:
    assert (
        _normalize_failure_type("fail_if_articulation_origin_far_from_geometry(tol=0.015)")
        == "fail_if_articulation_origin_far_from_geometry"
    )


def test_extract_failure_entities_preserves_mechanical_and_code_context() -> None:
    entities = extract_failure_entities(
        "Part overlaps detected:\n"
        "pair=('door__panel__body','frame__post__body') "
        "elem_a=#0 'door_panel':Box elem_b=#1 'frame_post':Mesh "
        "pose={'door__panel__hinge': 1.57}\n"
        "part='floating_knob' connected=1/2\n"
        "bounded movable joint(s) without limits: ['lift_joint']\n"
        "Location: agent/templates/demo.py:42"
    )

    assert entities["pairs"] == [["door__panel__body", "frame__post__body"]]
    assert entities["parts"] == [
        "door__panel__body",
        "floating_knob",
        "frame__post__body",
    ]
    assert entities["elements"] == ["door_panel", "frame_post"]
    assert entities["joints"] == ["door__panel__hinge", "lift_joint"]
    assert entities["poses"] == [{"door__panel__hinge": 1.57}]
    assert entities["locations"] == [{"path": "agent/templates/demo.py", "line": 42}]
    assert _normalize_failure_type("fail_if_isolated_parts()") == "fail_if_isolated_parts"
    assert _normalize_failure_type("ValueError") == "ValueError"
    assert _normalize_failure_type(None) is None


def test_config_to_dict_handles_dataclass_plain_object_and_unknown() -> None:
    from dataclasses import dataclass

    @dataclass
    class Cfg:
        a: int
        b: str

    assert _config_to_dict(Cfg(1, "x")) == {"a": 1, "b": "x"}

    class Plain:
        def __init__(self) -> None:
            self.c = 3
            self._private = 99

    out = _config_to_dict(Plain())
    assert out == {"c": 3}

    out = _config_to_dict(7)
    assert "_repr" in out and out["_repr"] == "7"


def test_extract_failure_uses_attached_test_report() -> None:
    from sdk import TestReport
    from sdk._core.v0._testing.core import TestFailure

    failure = TestFailure(
        name="fail_if_articulation_origin_far_from_geometry(tol=0.015)",
        details="joint='x' dist_parent=0.5 tol=0.015",
    )
    report = TestReport(
        passed=False,
        checks_run=1,
        checks=("fail_if_articulation_origin_far_from_geometry(tol=0.015)",),
        failures=(failure,),
        warnings=(),
    )
    exc = ValueError("URDF tests failed: ...")
    setattr(exc, "test_report", report)
    failure_type, details = _extract_failure(exc)
    assert failure_type == "fail_if_articulation_origin_far_from_geometry(tol=0.015)"
    assert "dist_parent" in details


def test_extract_failure_for_bare_runtime_exception_uses_signal_code() -> None:
    # No attached test_report -> compile_signal_bundle_from_exception synthesises
    # a runtime-failure signal with code='COMPILE_RUNTIME_FAILURE'.
    exc = RuntimeError("boom")
    failure_type, details = _extract_failure(exc)
    assert failure_type == "COMPILE_RUNTIME_FAILURE"
    assert "boom" in details


def test_disconnected_geometry_warning_details_promotes_template_warning() -> None:
    details = disconnected_geometry_warning_details(
        [
            "unrelated warning",
            "warn_if_part_contains_disconnected_geometry_islands(tol=1e-06): "
            "Disconnected geometry islands detected:\n"
            "part='head' connected=2/3 disconnected=[stylus_tip:Box]",
        ]
    )

    assert details is not None
    assert "Template sweep treats compiler disconnected-geometry warnings as failures" in details
    assert "stylus_tip" in details


def test_run_sweep_handles_mixed_pass_fail(monkeypatch, tmp_path: Path) -> None:
    """Stub `_compile_one` to simulate mixed outcomes; verify aggregation."""

    def fake_compile_one(
        slug: str, stem: str, seed: int, sdk_package: str, motion_qc: bool = True
    ) -> SeedOutcome:
        if seed in {1, 4}:
            return SeedOutcome(
                seed=seed,
                verdict="fail",
                config={"x": seed, "shape": "square"},
                failure_type="fail_if_parts_overlap_in_current_pose()",
                failure_type_normalized="fail_if_parts_overlap_in_current_pose",
                failure_details=f"seed-{seed}-overlap",
                elapsed_s=0.01,
            )
        return SeedOutcome(
            seed=seed,
            verdict="pass",
            config={"x": seed},
            failure_type=None,
            failure_type_normalized=None,
            failure_details=None,
            elapsed_s=0.01,
        )

    # Stub the template module existence check.
    fake_template = tmp_path / "templates" / "stub_slug.py"
    fake_template.parent.mkdir(parents=True)
    fake_template.write_text("x = 1\n" * 42, encoding="utf-8")

    def fake_template_module_path(slug: str, *, repo_root: Path) -> Path:
        return fake_template

    monkeypatch.setattr(template_sweep, "_compile_one", fake_compile_one)
    monkeypatch.setattr(template_sweep, "_template_module_path", fake_template_module_path)

    report = run_sweep(
        slug="stub_slug",
        stem="stub",
        seeds=[0, 1, 2, 3, 4],
        sdk_package="sdk",
        pass_threshold=0.95,
        max_workers=1,
        repo_root=tmp_path,
    )

    assert isinstance(report, SweepReport)
    assert report.total_seeds == 5
    assert sorted(report.passed_seeds) == [0, 2, 3]
    assert {o.seed for o in report.failed_outcomes} == {1, 4}
    assert report.pass_rate == pytest.approx(0.6)
    assert report.verdict == "fail"  # below 0.95 threshold


def test_run_sweep_passes_when_threshold_met(monkeypatch, tmp_path: Path) -> None:
    def fake_compile_one(
        slug: str, stem: str, seed: int, sdk_package: str, motion_qc: bool = True
    ) -> SeedOutcome:
        return SeedOutcome(
            seed=seed,
            verdict="pass",
            config={"x": seed},
            failure_type=None,
            failure_type_normalized=None,
            failure_details=None,
            elapsed_s=0.0,
        )

    fake_template = tmp_path / "templates" / "stub_slug.py"
    fake_template.parent.mkdir(parents=True)
    fake_template.write_text("\n" * 1500, encoding="utf-8")

    monkeypatch.setattr(template_sweep, "_compile_one", fake_compile_one)
    monkeypatch.setattr(
        template_sweep,
        "_template_module_path",
        lambda slug, *, repo_root: fake_template,
    )
    monkeypatch.setattr(
        "agent.template_sweep_coverage.evaluate_gates",
        lambda **kwargs: CoverageGates(
            module_topology_diversity=CoverageGateResult(
                name="module_topology_diversity",
                status="pass",
                details={"distinct_count": 10},
            )
        ),
    )

    report = run_sweep(
        slug="stub_slug",
        stem="stub",
        seeds=list(range(10)),
        max_workers=1,
        repo_root=tmp_path,
    )
    assert report.pass_rate == 1.0
    assert report.verdict == "pass"


def test_run_sweep_raises_when_template_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        run_sweep(
            slug="nonexistent_template_zz",
            stem="zz",
            seeds=[0],
            max_workers=1,
            repo_root=tmp_path,
        )


def test_timeout_outcome_helper_produces_compile_timeout_failure_type() -> None:
    from agent.template_sweep import _timeout_outcome

    outcome = _timeout_outcome(seed=7, timeout_s=30.0)
    assert outcome.verdict == "fail"
    assert outcome.seed == 7
    assert outcome.failure_type_normalized == "compile_timeout"
    assert "30s" in outcome.failure_type or "30s" in outcome.failure_details


def test_compile_one_via_subprocess_returns_timeout_when_worker_hangs(
    monkeypatch, tmp_path: Path
) -> None:
    """Force a hanging worker by replacing the subprocess source with an
    infinite loop; verify the parent SIGKILLs and returns a compile_timeout
    outcome instead of blocking."""
    from agent import template_sweep
    from agent.template_sweep import _compile_one_via_subprocess

    monkeypatch.setattr(
        template_sweep,
        "_SUBPROCESS_WORKER_SOURCE",
        "import time\nwhile True: time.sleep(0.1)\n",
    )

    outcome = _compile_one_via_subprocess(
        slug="any_slug",
        stem="any_stem",
        seed=99,
        sdk_package="sdk",
        timeout_s=1.5,
        repo_root=tmp_path,
    )
    assert outcome.verdict == "fail"
    assert outcome.failure_type_normalized == "compile_timeout"
    assert outcome.seed == 99
    assert outcome.elapsed_s >= 1.5


def test_compile_one_via_subprocess_returns_crash_on_non_zero_rc(
    monkeypatch, tmp_path: Path
) -> None:
    from agent import template_sweep
    from agent.template_sweep import _compile_one_via_subprocess

    monkeypatch.setattr(
        template_sweep,
        "_SUBPROCESS_WORKER_SOURCE",
        "import sys\nsys.stderr.write('explicit failure')\nsys.exit(2)\n",
    )

    outcome = _compile_one_via_subprocess(
        slug="any_slug",
        stem="any_stem",
        seed=11,
        sdk_package="sdk",
        timeout_s=10.0,
        repo_root=tmp_path,
    )
    assert outcome.verdict == "fail"
    assert outcome.failure_type_normalized == "subprocess_crash"
    assert "explicit failure" in (outcome.failure_details or "")


def test_report_to_json_round_trip(monkeypatch, tmp_path: Path) -> None:
    def fake_compile_one(
        slug: str, stem: str, seed: int, sdk_package: str, motion_qc: bool = True
    ) -> SeedOutcome:
        return SeedOutcome(
            seed=seed,
            verdict="pass",
            config={"x": seed},
            failure_type=None,
            failure_type_normalized=None,
            failure_details=None,
            elapsed_s=0.0,
        )

    fake_template = tmp_path / "templates" / "stub_slug.py"
    fake_template.parent.mkdir(parents=True)
    fake_template.write_text("\n" * 1200, encoding="utf-8")

    monkeypatch.setattr(template_sweep, "_compile_one", fake_compile_one)
    monkeypatch.setattr(
        template_sweep,
        "_template_module_path",
        lambda slug, *, repo_root: fake_template,
    )

    report = run_sweep(
        slug="stub_slug",
        stem="stub",
        seeds=[0, 1, 2],
        max_workers=1,
        repo_root=tmp_path,
    )
    payload = report_to_json(report)
    decoded = json.loads(payload)
    assert decoded["slug"] == "stub_slug"
    assert decoded["total_seeds"] == 3
    assert decoded["passed_seeds"] == [0, 1, 2]
    assert decoded["failed_seeds"] == []
    assert decoded["verdict"] == "pass"
    # Coverage gates are REPORT-ONLY: the non-modular stub fails the
    # module_topology_diversity gate (the seed-count activation threshold is
    # retired), but the verdict follows pass_rate alone and stays "pass". The
    # gate result is still reported in the JSON for visibility.
    assert "coverage_gates" in decoded
    assert decoded["coverage_gates"]["module_topology_diversity"]["status"] == "fail"


def test_rigid_seed_detail_rejects_only_joint_less_models() -> None:
    """Every exported seed must be an articulated object, with no exemption."""

    from agent.template_policy import rigid_seed_detail

    assert rigid_seed_detail('<joint name="a" type="revolute"/>') is None
    assert rigid_seed_detail('<joint name="a" type="prismatic"/>') is None
    assert rigid_seed_detail('<joint name="a" type="continuous"/>') is None
    assert rigid_seed_detail("") is not None
    detail = rigid_seed_detail('<joint name="a" type="fixed"/>')
    assert detail is not None and "rigid body" in detail
