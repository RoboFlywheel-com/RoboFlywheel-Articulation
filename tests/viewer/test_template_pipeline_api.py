# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import threading
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from viewer.api.app import create_app


def _write_source_record(records: Path, record_id: str) -> None:
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
        "\n".join(f"# line {index}" for index in range(1, 31)) + "\n",
        encoding="utf-8",
    )


@pytest.mark.parametrize("external_records", [False, True])
def test_template_pipeline_api_initializes_and_inspects_source_map(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    external_records: bool,
) -> None:
    repo = tmp_path / "template-repo"
    records = tmp_path / "records" if external_records else repo / "data" / "records"
    repo.mkdir()
    _write_source_record(records, "rec_demo")
    monkeypatch.delenv("RFWA_RECORDS_ROOT", raising=False)
    monkeypatch.delenv("ARTICRAFT_RECORDS_ROOT", raising=False)
    if external_records:
        monkeypatch.setenv("ARTICRAFT_RECORDS_ROOT", str(records))
    monkeypatch.setenv("ARTICRAFT_VIEWER_SKIP_SEARCH_INDEX", "1")

    with TestClient(create_app(repo_root=repo)) as client:
        created = client.post(
            "/api/template-pipeline/source-maps",
            json={
                "slug": "demo",
                "picture_category": "Demo",
                "picture_subcategory": "widget",
            },
        )
        assert created.status_code == 201
        assert created.json()["source_count"] == 1

        inspected = client.get("/api/template-pipeline/demo")
        assert inspected.status_code == 200
        payload = inspected.json()
        assert payload["source_map"]["source_count"] == 1
        assert payload["next_step"] == "source-review"


def test_template_pipeline_api_schedules_idempotent_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "template-repo"
    repo.mkdir()
    monkeypatch.setenv("ARTICRAFT_VIEWER_SKIP_SEARCH_INDEX", "1")
    app = create_app(repo_root=repo)
    app.state.template_pipeline_scheduler.template_stems["demo"] = "demo"
    monkeypatch.setattr(
        app.state.template_pipeline_service,
        "run_check",
        lambda **_kwargs: {"verdict": "pass", "stage": "random-16"},
    )

    with TestClient(app) as client:
        submitted = client.post(
            "/api/template-pipeline/demo/checks",
            json={
                "stage": "random-16",
                "idempotency_key": "demo-request-1",
            },
        )
        assert submitted.status_code == 202
        job_id = submitted.json()["job_id"]

        duplicate = client.post(
            "/api/template-pipeline/demo/checks",
            json={
                "stage": "random-16",
                "idempotency_key": "demo-request-1",
            },
        )
        assert duplicate.status_code == 202
        assert duplicate.json()["job_id"] == job_id

        for _index in range(100):
            inspected = client.get(
                f"/api/template-pipeline/jobs/{job_id}",
                params={"include_report": "true"},
            )
            assert inspected.status_code == 200
            if inspected.json()["status"] == "completed":
                break
            threading.Event().wait(0.01)
        assert inspected.json()["verdict"] == "pass"
        assert inspected.json()["report"]["stage"] == "random-16"
