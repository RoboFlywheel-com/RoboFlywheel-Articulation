# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from pathlib import Path

from agent.source_maps import (
    discover_source_pool,
    parse_source_map,
    render_source_map_scaffold,
)


def _write_source_record(
    records: Path,
    record_id: str,
    *,
    picture_category: str = "Demo",
    picture_subcategory: str = "widget",
    revision: str = "rev_000001",
    lines: int = 60,
    archived: bool = False,
) -> None:
    record = records / record_id
    revision_dir = record / "revisions" / revision
    revision_dir.mkdir(parents=True)
    (record / "collections").mkdir()
    (record / "record.json").write_text(
        json.dumps(
            {
                "collections": ["workbench"],
                "active_revision_id": revision,
            }
        ),
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
        json.dumps({"archived": archived}),
        encoding="utf-8",
    )
    (revision_dir / "model.py").write_text(
        "\n".join(f"# line {index}" for index in range(1, lines + 1)) + "\n",
        encoding="utf-8",
    )


def _complete_source_map(*, records: tuple[str, ...] = ("rec_alpha",)) -> str:
    sync_rows = "\n".join(f"  - {record_id}" for record_id in records)
    review_rows = "\n".join(
        f"| {record_id}/rev_000001 | reviewed | used | inspected source |" for record_id in records
    )
    candidate_rows = "\n".join(
        f"| body | compact_{index} | enclosure | {record_id}/rev_000001 | "
        "model.py:L5-L25 | structure | source panel enclosure |"
        for index, record_id in enumerate(records)
    )
    return f"""source_map_schema: 1
export_category: demo
picture_category: Demo
picture_subcategory: widget
category_scope: compact demonstration widget

sync_records:
{sync_rows}

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
{review_rows}

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
{candidate_rows}
"""


def test_discover_source_pool_uses_exact_active_workbench_subcategory(
    tmp_path: Path,
) -> None:
    records = tmp_path / "records"
    _write_source_record(records, "rec_alpha")
    _write_source_record(records, "rec_other", picture_subcategory="other")
    _write_source_record(records, "rec_archived", archived=True)

    resolution = discover_source_pool(
        records,
        picture_category="Demo",
        picture_subcategory="widget",
    )

    assert resolution.verdict == "pass"
    assert [record.record_id for record in resolution.records] == ["rec_alpha"]


def test_render_source_map_scaffold_accounts_for_every_record(tmp_path: Path) -> None:
    records = tmp_path / "records"
    _write_source_record(records, "rec_alpha")
    _write_source_record(records, "rec_beta")
    pool = discover_source_pool(
        records,
        picture_category="Demo",
        picture_subcategory="widget",
    )

    text = render_source_map_scaffold(
        slug="demo",
        picture_category="Demo",
        picture_subcategory="widget",
        source_pool=pool,
    )

    assert text.count("| pending | pending |") == 2
    assert "  - rec_alpha" in text
    assert "  - rec_beta" in text


def test_parse_source_map_accepts_complete_review_and_candidates(tmp_path: Path) -> None:
    records = tmp_path / "records"
    _write_source_record(records, "rec_alpha")
    source_map = tmp_path / "source-map.md"
    source_map.write_text(_complete_source_map(), encoding="utf-8")

    resolution = parse_source_map(source_map, records)

    assert resolution.verdict == "pass"
    assert resolution.problems == ()
    assert resolution.reviews[0].decision == "used"
    assert resolution.candidates[0].evidence == "source panel enclosure"


def test_parse_source_map_blocks_unaccounted_discovered_source(tmp_path: Path) -> None:
    records = tmp_path / "records"
    _write_source_record(records, "rec_alpha")
    _write_source_record(records, "rec_beta")
    source_map = tmp_path / "source-map.md"
    source_map.write_text(_complete_source_map(), encoding="utf-8")

    resolution = parse_source_map(source_map, records)

    assert resolution.verdict == "fail"
    assert any(
        problem.startswith("source_pool_records_missing_from_sync:rec_beta")
        for problem in resolution.problems
    )


def test_parse_source_map_blocks_pending_review(tmp_path: Path) -> None:
    records = tmp_path / "records"
    _write_source_record(records, "rec_alpha")
    source_map = tmp_path / "source-map.md"
    source_map.write_text(
        _complete_source_map().replace(
            "| rec_alpha/rev_000001 | reviewed | used | inspected source |",
            "| rec_alpha/rev_000001 | pending | pending | TODO inspect source |",
        ),
        encoding="utf-8",
    )

    resolution = parse_source_map(source_map, records)

    assert "source_not_reviewed:rec_alpha" in resolution.problems


def test_parse_source_map_blocks_stale_revision_and_bad_span(tmp_path: Path) -> None:
    records = tmp_path / "records"
    _write_source_record(records, "rec_alpha", revision="rev_000002", lines=20)
    source_map = tmp_path / "source-map.md"
    source_map.write_text(
        _complete_source_map().replace("rev_000001", "rev_000002"),
        encoding="utf-8",
    )

    resolution = parse_source_map(source_map, records)

    assert "candidate_source_span_out_of_range:compact_0" in resolution.problems


def test_parse_source_map_requires_used_sources_to_contribute_candidate(
    tmp_path: Path,
) -> None:
    records = tmp_path / "records"
    _write_source_record(records, "rec_alpha")
    _write_source_record(records, "rec_beta")
    text = _complete_source_map(records=("rec_alpha", "rec_beta"))
    text = text.replace(
        "| body | compact_1 | enclosure | rec_beta/rev_000001 | "
        "model.py:L5-L25 | structure | source panel enclosure |\n",
        "",
    )
    source_map = tmp_path / "source-map.md"
    source_map.write_text(text, encoding="utf-8")

    resolution = parse_source_map(source_map, records)

    assert "used_source_has_no_candidate:rec_beta" in resolution.problems


def test_source_pool_does_not_omit_records_missing_from_cached_shard(tmp_path):
    records = tmp_path / "data/records"
    _write_source_record(records, "rec_old")
    _write_source_record(records, "rec_new")
    shard = tmp_path / "data/index/subcat/Demo__widget.jsonl"
    shard.parent.mkdir(parents=True)
    shard.write_text(
        json.dumps(
            {
                "record_id": "rec_old",
                "picture_category": "Demo",
                "picture_subcategory": "widget",
                "archived": False,
            }
        )
        + "\n"
    )
    pool = discover_source_pool(records, picture_category="Demo", picture_subcategory="widget")
    assert pool.verdict == "pass"
    assert {r.record_id for r in pool.records} == {"rec_old", "rec_new"}


def test_source_pool_uses_current_archive_state_instead_of_stale_cache(tmp_path):
    records = tmp_path / "data/records"
    _write_source_record(records, "rec_restored", archived=False)
    shard = tmp_path / "data/index/subcat/Demo__widget.jsonl"
    shard.parent.mkdir(parents=True)
    shard.write_text(
        json.dumps(
            {
                "record_id": "rec_restored",
                "picture_category": "Demo",
                "picture_subcategory": "widget",
                "archived": True,
            }
        )
        + "\n"
    )
    pool = discover_source_pool(records, picture_category="Demo", picture_subcategory="widget")
    assert pool.verdict == "pass"
    assert [r.record_id for r in pool.records] == ["rec_restored"]
