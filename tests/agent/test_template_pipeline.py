# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import threading
from pathlib import Path

import pytest

from agent.template_pipeline import (
    TemplatePipelineBusyError,
    TemplatePipelineScheduler,
    TemplatePipelineService,
)


def _write_source_record(records: Path, record_id: str, *, lines: int = 60) -> None:
    record = records / record_id
    revision = record / "revisions" / "rev_000001"
    revision.mkdir(parents=True)
    (record / "collections").mkdir()
    (record / "record.json").write_text(
        '{"collections":["workbench"],"active_revision_id":"rev_000001"}',
        encoding="utf-8",
    )
    (record / "picture.json").write_text(
        '{"category":"Demo","subcategory":"widget"}',
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


def _reviewed_source_map() -> str:
    return """source_map_schema: 1
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
"""


def test_service_orders_source_review_before_design(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    records = tmp_path / "records"
    repo.mkdir()
    _write_source_record(records, "rec_demo")
    service = TemplatePipelineService(repo_root=repo, records_root=records)

    created = service.source_map_init(
        slug="demo",
        picture_category="Demo",
        picture_subcategory="widget",
    )

    assert created["status"] == "pending_review"
    assert service.inspect(slug="demo")["next_step"] == "source-review"

    source_map = service.paths("demo").source_map
    source_map.write_text(_reviewed_source_map(), encoding="utf-8")
    checked = service.source_map_check(slug="demo")
    assert checked["verdict"] == "pass"

    design = service.design_init(slug="demo")
    assert design["slot_count"] == 1
    assert design["candidate_count"] == 1
    assert service.inspect(slug="demo")["next_step"] == "write-template"


def test_scheduler_is_idempotent_and_serializes_one_slug(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = TemplatePipelineService(
        repo_root=tmp_path,
        records_root=tmp_path / "records",
    )
    started = threading.Event()
    release = threading.Event()

    def fake_check(**_kwargs):
        started.set()
        assert release.wait(timeout=2.0)
        return {"verdict": "pass"}

    monkeypatch.setattr(service, "run_check", fake_check)
    scheduler = TemplatePipelineScheduler(
        service=service,
        template_stems={"demo": "demo"},
    )
    try:
        first = scheduler.submit_check(
            slug="demo",
            stage="random-16",
            idempotency_key="request-1",
        )
        assert started.wait(timeout=2.0)
        duplicate = scheduler.submit_check(
            slug="demo",
            stage="random-16",
            idempotency_key="request-1",
        )
        assert duplicate.job_id == first.job_id
        with pytest.raises(ValueError, match="different request"):
            scheduler.submit_check(
                slug="demo",
                stage="random-16",
                idempotency_key="request-1",
                pass_threshold=0.8,
            )
        with pytest.raises(TemplatePipelineBusyError):
            scheduler.submit_check(
                slug="demo",
                stage="corner",
                idempotency_key="request-2",
            )
        release.set()
        for _index in range(100):
            finished = scheduler.get_job(first.job_id)
            assert finished is not None
            if finished.status == "completed":
                break
            threading.Event().wait(0.01)
        assert finished.status == "completed"
        assert finished.verdict == "pass"
        assert finished.report_path is not None
    finally:
        release.set()
        scheduler.close()


def test_ready_corner_is_terminal_and_writes_no_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = TemplatePipelineService(repo_root=tmp_path, records_root=tmp_path / "records")
    ready = {
        "slug": "demo",
        "stage": "corner",
        "verdict": "pass",
        "completion_status": "strict_ready",
    }
    monkeypatch.setattr("agent.template_pipeline.check_template", lambda **_kwargs: dict(ready))

    report = service.run_check(slug="demo", stem="demo", stage="corner")

    assert report == ready
    assert not (tmp_path / ".artifacts" / "template_pipeline").exists()
