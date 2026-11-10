# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import copy
import json
from types import SimpleNamespace

import pytest

from rfwa.revision import check_generator, release_findings


def valid_report():
    return {
        "stage": "corner",
        "verdict": "pass",
        "template_mode": "strict",
        "preflight": {"status": "pass"},
        "random_sweep": {
            "passed": 36,
            "failed": 0,
            "joint_motion_coverage": {"status": "pass"},
            "candidate_coverage": {
                "candidates": [
                    {"slot": "door", "candidate": "plain", "passing_seeds": [0]},
                    {"slot": "door", "candidate": "glass", "passing_seeds": []},
                ]
            },
        },
        "corner_stage": {
            "status": "pass",
            "failed": 0,
            "cases": [
                {"status": "pass", "config": {"door": "glass"}},
            ],
        },
    }


def test_release_accepts_choice_only_covered_by_passing_corner():
    assert release_findings(valid_report()) == []


@pytest.mark.parametrize(
    "fault", ["tolerance", "legacy", "uncovered", "motion", "empty", "corner_failure"]
)
def test_release_rejects_incomplete_or_tolerated_evidence(fault):
    report = copy.deepcopy(valid_report())
    if fault == "tolerance":
        report["random_sweep"].update(passed=35, failed=1)
    elif fault == "legacy":
        report["template_mode"] = "legacy"
    elif fault == "uncovered":
        report["corner_stage"]["cases"] = []
    elif fault == "motion":
        report["random_sweep"]["joint_motion_coverage"]["status"] = "fail"
    elif fault == "empty":
        report = {}
    else:
        report["corner_stage"].update(failed=1, status="fail")
    assert release_findings(report)


def test_failed_corner_is_retested_after_generator_revision(monkeypatch, tmp_path):
    import agent.template_check
    import rfwa.revision

    module = SimpleNamespace(TEMPLATE_CORNERS=())
    observed = []

    def check(**kwargs):
        assert kwargs["pass_threshold"] == 1.0
        observed.append(module.TEMPLATE_CORNERS)
        return {
            "stage": "corner",
            "verdict": "fail",
            "corner_stage": {
                "cases": [
                    {"status": "fail", "config": {"width": 0.12, "door": "glass"}},
                ]
            },
        }

    monkeypatch.setattr(rfwa.revision, "registered_stem", lambda _: "demo")
    monkeypatch.setattr(rfwa.revision.importlib, "import_module", lambda _: module)
    monkeypatch.setattr(agent.template_check, "check_template", check)
    for _ in range(2):
        check_generator(tmp_path, "demo", "corner", state_root=tmp_path / "state", strict=True)
    assert observed[0] == ()
    assert dict(observed[1][0].overrides) == {"width": 0.12, "door": "glass"}
    assert module.TEMPLATE_CORNERS == ()
    assert len(json.loads((tmp_path / "state/demo/regressions.json").read_text())) == 1


def test_default_check_keeps_generator_with_some_failed_seeds(monkeypatch, tmp_path):
    import agent.template_check
    import rfwa.revision

    module = SimpleNamespace(TEMPLATE_CORNERS=())

    def check(**kwargs):
        assert kwargs["pass_threshold"] == 0.9
        return {
            "stage": "random-16",
            "verdict": "pass",
            "template_mode": "legacy",
            "preflight": {"status": "pass"},
            "random_sweep": {"passed": 15, "failed": 1},
        }

    monkeypatch.setattr(rfwa.revision, "registered_stem", lambda _: "demo")
    monkeypatch.setattr(rfwa.revision.importlib, "import_module", lambda _: module)
    monkeypatch.setattr(agent.template_check, "check_template", check)
    report = check_generator(tmp_path, "demo", "random-16", state_root=tmp_path / "state")
    assert report["verdict"] == "pass"
    assert report["completion_status"] == "ready_for_sampling"
    assert report["warnings"]


def test_practical_readiness_does_not_require_legacy_blueprint(monkeypatch, tmp_path):
    import rfwa.revision

    stages = []

    def check(root, slug, stage, **kwargs):
        stages.append(stage)
        return {"stage": stage, "verdict": "pass", "warnings": []}

    monkeypatch.setattr(rfwa.revision, "registered_stem", lambda _: "demo")
    monkeypatch.setattr(rfwa.revision, "check_generator", check)
    result = rfwa.revision.release_generator(tmp_path, "demo", state_root=tmp_path / "state")
    assert result["status"] == "ready_for_sampling"
    assert stages == ["random-16", "random-36"]
    assert result["warnings"]
