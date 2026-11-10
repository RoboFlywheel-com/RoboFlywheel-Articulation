# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json

from rfwa.cli import main


def test_seeded_configuration_is_reproducible_without_provider_keys(monkeypatch, capsys):
    for key in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEYS", "OPENROUTER_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    assert main(["config", "single_revolute_hinge", "--seed", "0"]) == 0
    first = json.loads(capsys.readouterr().out)
    assert main(["config", "single_revolute_hinge", "--seed", "0"]) == 0
    assert json.loads(capsys.readouterr().out) == first


def test_sample_refuses_existing_output_before_build(tmp_path, capsys):
    (tmp_path / "keep.txt").write_text("preserve")
    assert main(["sample", "single_revolute_hinge", "--out", str(tmp_path)]) == 1
    assert "must be empty" in capsys.readouterr().err
    assert (tmp_path / "keep.txt").read_text() == "preserve"


def test_edit_forwards_leading_flags(monkeypatch):
    import specific_editing.pipeline

    seen = []
    monkeypatch.setattr(specific_editing.pipeline, "main", lambda args: seen.append(args) or 0)
    assert main(["edit", "--describe-generator", "cabinet"]) == 0
    assert seen == [["--describe-generator", "cabinet"]]


def test_source_places_repository_option_after_subcommand(monkeypatch, tmp_path):
    import cli.main

    seen = []
    monkeypatch.setattr(cli.main, "main", lambda args: seen.append(args) or 0)
    assert main(["--repo-root", str(tmp_path), "source", "generate", "a cabinet"]) == 0
    assert seen == [["generate", "--repo-root", str(tmp_path), "a cabinet"]]


def test_author_check_uses_current_checkout_records(monkeypatch, tmp_path):
    import cli.template

    seen = []

    class Service:
        def __init__(self, *, repo_root, records_root):
            seen.append(records_root)

        def run_check(self, **kwargs):
            return {"verdict": "pass"}

    monkeypatch.setattr(cli.template, "TemplatePipelineService", Service)
    assert (
        main(
            [
                "--repo-root",
                str(tmp_path),
                "author",
                "check",
                "single_revolute_hinge",
                "--stage",
                "random-16",
                "--quiet",
            ]
        )
        == 0
    )
    assert seen == [tmp_path / "data" / "records"]
