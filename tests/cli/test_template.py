# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from pathlib import Path

import pytest

from cli import template as template_cli


def test_parse_seed_spec_supports_ranges_and_lists() -> None:
    assert template_cli.parse_seed_spec("1-3") == [1, 2, 3]
    assert template_cli.parse_seed_spec("1,3,5-7") == [1, 3, 5, 6, 7]


def test_parse_seed_spec_rejects_empty_input() -> None:
    with pytest.raises(ValueError, match="At least one seed"):
        template_cli.parse_seed_spec("")


def test_batch_ferris_wheel_dry_run(tmp_path: Path) -> None:
    exit_code = template_cli.batch_ferris_wheel(
        tmp_path,
        seeds=[1, 2],
        agent="codex",
        category_slug=None,
        dry_run=True,
    )
    assert exit_code == 0
    assert not (tmp_path / "data" / "records").exists()


def _check_report(verdict: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "slug": "turntable",
        "stage": "random-16",
        "verdict": verdict,
        "random_sweep": {"cache_hits": 0, "cache_misses": 16},
    }


def test_check_cli_pass_returns_zero(monkeypatch, tmp_path: Path, capsys) -> None:
    captured: dict[str, object] = {}

    def fake_check_template(_service, **kwargs):
        captured.update(kwargs)
        return _check_report("pass")

    monkeypatch.setattr(
        template_cli.TemplatePipelineService,
        "run_check",
        fake_check_template,
    )
    exit_code = template_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "check",
            "turntable",
            "--stage",
            "random-16",
            "--quiet",
        ]
    )
    assert exit_code == 0
    assert captured["slug"] == "turntable"
    assert captured["stage"] == "random-16"
    assert '"verdict": "pass"' in capsys.readouterr().out


def test_check_cli_forwards_expected_quality_contract(
    monkeypatch,
    tmp_path: Path,
) -> None:
    captured: dict[str, object] = {}

    def fake_check_template(_service, **kwargs):
        captured.update(kwargs)
        return _check_report("pass")

    monkeypatch.setattr(
        template_cli.TemplatePipelineService,
        "run_check",
        fake_check_template,
    )
    exit_code = template_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "check",
            "turntable",
            "--stage",
            "random-16",
            "--expected-quality-contract-sha256",
            "abc123",
            "--quiet",
        ]
    )

    assert exit_code == 0
    assert captured["expected_quality_contract_sha256"] == "abc123"


def test_check_cli_fail_returns_one(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        template_cli.TemplatePipelineService,
        "run_check",
        lambda _service, **_kwargs: _check_report("fail"),
    )
    exit_code = template_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "check",
            "turntable",
            "--stage",
            "random-16",
            "--quiet",
        ]
    )
    assert exit_code == 1


def test_check_cli_out_writes_json(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        template_cli.TemplatePipelineService,
        "run_check",
        lambda _service, **_kwargs: _check_report("pass"),
    )
    out = tmp_path / "check.json"
    exit_code = template_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "check",
            "turntable",
            "--stage",
            "random-16",
            "--out",
            str(out),
            "--quiet",
        ]
    )
    assert exit_code == 0
    assert json.loads(out.read_text(encoding="utf-8"))["verdict"] == "pass"


@pytest.mark.parametrize(
    "argv",
    [
        ["material-annotation-init", "turntable", "--mechanical-receipt", "m.json"],
        [
            "material-annotation-apply",
            "turntable",
            "--init-receipt",
            "i.json",
            "--proposal",
            "p.json",
        ],
        ["seed-export-eligibility", "turntable", "--seed", "0"],
        [
            "export-materialized",
            "turntable",
            "--seeds",
            "0",
            "--material-seed",
            "0",
            "--annotation-receipt",
            "a.json",
            "--out",
            "out",
        ],
    ],
)
def test_post_mechanical_commands_are_not_registered(argv: list[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        template_cli._build_parser().parse_args(argv)
    assert exc_info.value.code == 2


def test_export_assets_cli_bypasses_pipeline_and_lists_every_seed(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    captured: dict[str, object] = {}

    class ForbiddenPipelineService:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            raise AssertionError("export-assets must not instantiate TemplatePipelineService")

    def fake_export(**kwargs: object) -> tuple[Path, ...]:
        captured.update(kwargs)
        out_root = Path(kwargs["out_root"])
        slug = str(kwargs["slug"])
        return tuple(out_root / slug / f"seed_{seed}" for seed in kwargs["seeds"])

    monkeypatch.setattr(template_cli, "TemplatePipelineService", ForbiddenPipelineService)
    monkeypatch.setattr(template_cli, "export_template_assets", fake_export)
    pointer = tmp_path / "library" / "unified" / "latest.json"
    exit_code = template_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "export-assets",
            "turntable",
            "--seeds",
            "2,5",
            "--out",
            str(tmp_path / "exports"),
            "--material-seed",
            "17",
            "--library-pointer",
            str(pointer),
        ]
    )

    assert exit_code == 0
    assert captured["seeds"] == [2, 5]
    assert captured["material_seed"] == 17
    assert captured["library_pointer"] == pointer
    output = capsys.readouterr().out
    assert f"exported seed=2 path={tmp_path / 'exports/turntable/seed_2'}" in output
    assert f"exported seed=5 path={tmp_path / 'exports/turntable/seed_5'}" in output


def _write_source_record(
    records: Path,
    record_id: str,
    *,
    picture_category: str = "Demo",
    picture_subcategory: str = "widget",
    lines: int = 60,
) -> None:
    record = records / record_id
    revision = record / "revisions" / "rev_000001"
    revision.mkdir(parents=True)
    (record / "collections").mkdir()
    (record / "record.json").write_text(
        '{"collections":["workbench"],"active_revision_id":"rev_000001"}',
        encoding="utf-8",
    )
    (record / "picture.json").write_text(
        json.dumps(
            {
                "category": picture_category,
                "subcategory": picture_subcategory,
            }
        ),
        encoding="utf-8",
    )
    (record / "collections" / "workbench.json").write_text(
        '{"archived":false}',
        encoding="utf-8",
    )
    (revision / "model.py").write_text(
        "\n".join(f"# line {index}" for index in range(1, lines + 1)) + "\n",
        encoding="utf-8",
    )


def test_design_init_writes_template_design(tmp_path: Path) -> None:
    records = tmp_path / "records"
    _write_source_record(records, "rec_demo")
    source_map = tmp_path / "demo-map.md"
    source_map.write_text(
        """source_map_schema: 1
export_category: demo
picture_category: Demo
picture_subcategory: widget
category_scope: compact demonstration widget

sync_records:
  - rec_demo

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_demo/rev_000001 | reviewed | used | compact enclosure source |

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| body | compact | enclosure | rec_demo/rev_000001 | model.py:L5-L25 | structure | panel enclosure |
""",
        encoding="utf-8",
    )
    output = tmp_path / "design.json"

    exit_code = template_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "design-init",
            "demo",
            "--source-map",
            str(source_map),
            "--records-root",
            str(records),
            "--out",
            str(output),
        ]
    )

    assert exit_code == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["slug"] == "demo"
    assert payload["slots"][0]["name"] == "body"
    assert payload["slots"][0]["candidates"][0]["name"] == "compact"


def test_source_map_init_scaffolds_every_discovered_record(tmp_path: Path, capsys) -> None:
    records = tmp_path / "records"
    _write_source_record(records, "rec_alpha")
    _write_source_record(records, "rec_beta")
    output = tmp_path / "source-map.md"

    exit_code = template_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "source-map-init",
            "demo",
            "--records-root",
            str(records),
            "--picture-category",
            "Demo",
            "--picture-subcategory",
            "widget",
            "--out",
            str(output),
        ]
    )

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "pending_review"
    assert payload["source_count"] == 2
    text = output.read_text(encoding="utf-8")
    assert "rec_alpha/rev_000001 | pending | pending" in text
    assert "rec_beta/rev_000001 | pending | pending" in text


def test_source_map_check_reports_pending_review(tmp_path: Path, capsys) -> None:
    records = tmp_path / "records"
    _write_source_record(records, "rec_demo")
    source_map = tmp_path / "source-map.md"

    init_code = template_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "source-map-init",
            "demo",
            "--records-root",
            str(records),
            "--picture-category",
            "Demo",
            "--picture-subcategory",
            "widget",
            "--out",
            str(source_map),
        ]
    )
    assert init_code == 0
    capsys.readouterr()

    check_code = template_cli.main(
        [
            "--repo-root",
            str(tmp_path),
            "source-map-check",
            "--source-map",
            str(source_map),
            "--records-root",
            str(records),
        ]
    )

    assert check_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["verdict"] == "fail"
    assert "source_not_reviewed:rec_demo" in payload["problems"]


def test_gen_seeds_uses_export_namespace_and_replaces_atomically(
    monkeypatch, tmp_path: Path
) -> None:
    final = tmp_path / "category/profile"
    final.mkdir(parents=True)
    (final / "old.txt").write_text("old", encoding="utf-8")

    def fake_gen(slug: str, stem: str, seed: int, seed_dir: Path, motion_qc: bool = True):
        seed_dir.mkdir(parents=True)
        (seed_dir / "new.txt").write_text(str(seed), encoding="utf-8")
        return seed, True, None

    monkeypatch.setattr(template_cli, "_gen_one_seed", fake_gen)
    result = template_cli.gen_seeds(
        slug="turntable",
        stem="turntable",
        seeds=[0, 1],
        out_root=tmp_path,
        export_namespace="category/profile",
        max_workers=1,
    )
    assert result == 0
    assert not (final / "old.txt").exists()
    assert (final / "seed_0/new.txt").read_text(encoding="utf-8") == "0"
    assert (final / "seed_1/new.txt").read_text(encoding="utf-8") == "1"


def test_gen_seeds_failure_preserves_existing_export(monkeypatch, tmp_path: Path) -> None:
    final = tmp_path / "turntable"
    final.mkdir()
    (final / "old.txt").write_text("old", encoding="utf-8")
    monkeypatch.setattr(
        template_cli,
        "_gen_one_seed",
        lambda slug, stem, seed, seed_dir, motion_qc=True: (
            seed,
            False,
            "mechanical failure",
        ),
    )
    result = template_cli.gen_seeds(
        slug="turntable",
        stem="turntable",
        seeds=[0],
        out_root=tmp_path,
        max_workers=1,
    )
    assert result == 1
    assert (final / "old.txt").read_text(encoding="utf-8") == "old"
