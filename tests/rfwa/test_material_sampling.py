# SPDX-License-Identifier: Apache-2.0

"""Batch policy must preserve usable assets when one material export fails."""

from __future__ import annotations

import json

import pytest

from agent.template_sweep import SeedOutcome
from rfwa.cli import main


@pytest.mark.parametrize("failed_seeds", [set(), {1}, {0, 1, 2}])
def test_material_sampling_reports_each_seed_and_keeps_successes(
    monkeypatch, tmp_path, failed_seeds
):
    import agent.template_check
    import agent.template_sweep
    import articraft.materialization
    import rfwa.cli

    outcomes = [
        SeedOutcome(
            seed=i,
            verdict="pass",
            config={"seed": i},
            failure_type=None,
            failure_type_normalized=None,
            failure_details=None,
            elapsed_s=0,
        )
        for i in range(3)
    ]
    outcomes.append(
        SeedOutcome(
            seed=3,
            verdict="fail",
            config={},
            failure_type="bad_geometry",
            failure_type_normalized="bad_geometry",
            failure_details="fixture",
            elapsed_s=0,
        )
    )
    monkeypatch.setattr(agent.template_sweep, "run_seed_outcomes", lambda **kwargs: outcomes)
    monkeypatch.setattr(agent.template_check, "mechanical_hash", lambda *args: "fixture-hash")
    monkeypatch.setattr(rfwa.cli, "construction_provenance", lambda *args: {})
    exported = []

    def export(**kwargs):
        paths = []
        for seed in kwargs["seeds"]:
            if seed in failed_seeds:
                raise articraft.materialization.AssetExportError("fixture missing material class")
            target = kwargs["out_root"] / kwargs["slug"] / f"seed_{seed}"
            target.mkdir(parents=True)
            (target / "physics.json").write_text("{}")
            exported.append(seed)
            paths.append(target)
        return tuple(paths)

    monkeypatch.setattr(articraft.materialization, "export_template_assets", export)
    output = tmp_path / "output"
    code = main(
        [
            "--repo-root",
            str(tmp_path),
            "sample",
            "single_revolute_hinge",
            "--seeds",
            "0-3",
            "--library-pointer",
            str(tmp_path / "latest.json"),
            "--out",
            str(output),
        ]
    )
    expected = set(range(3)) - failed_seeds
    assert code == (0 if expected else 1)
    report = json.loads((output / "sampling.json").read_text())
    assert set(exported) == expected
    assert report["passed"] == len(expected)
    assert report["skipped"] == 4 - len(expected)
    assert report["status"] == ("partial" if expected else "fail")
    assert {row["seed"] for row in report["results"]} == set(range(4))
    for row in report["results"]:
        if row["seed"] in expected:
            assert row["verdict"] == "pass"
            assert (
                output / "single_revolute_hinge" / f"seed_{row['seed']}" / "physics.json"
            ).is_file()
        elif row["seed"] in failed_seeds:
            assert row["failure_type"] == "material_export_error"
