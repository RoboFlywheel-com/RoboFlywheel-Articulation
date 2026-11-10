# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import asyncio
import copy
from pathlib import Path

import pytest

from scripts import annotate_pbr_material_physics_qwen as target


def _estimate(value: float, low: float, high: float) -> dict[str, object]:
    return {
        "value": value,
        "low": low,
        "high": high,
        "confidence": 0.6,
        "applicability": "native",
        "basis": "Representative engineering proxy.",
    }


def _annotation() -> dict[str, object]:
    return {
        "interpretation": {
            "material_family": "steel",
            "assumed_bulk_material": "low-carbon steel",
            "bulk_form": "solid",
            "surface_state": "dry and clean",
            "anisotropic": False,
            "ambiguities": [],
        },
        "properties": {
            "youngs_modulus_pa": _estimate(2.0e11, 1.8e11, 2.2e11),
            "poissons_ratio": _estimate(0.29, 0.27, 0.31),
            "density_kg_m3": _estimate(7_850, 7_700, 8_000),
            "static_friction_coefficient": _estimate(0.6, 0.4, 0.8),
            "dynamic_friction_coefficient": _estimate(0.45, 0.3, 0.65),
            "restitution_coefficient": _estimate(0.55, 0.35, 0.7),
        },
        "quality": {"risk_tier": "medium", "warnings": []},
    }


def test_high_reasoning_and_twenty_minute_timeout_are_frozen() -> None:
    assert target.MODEL == "qwen-max"
    assert target.REASONING_EFFORT == "high"
    assert target.REQUEST_TIMEOUT_SECONDS == 1_200.0
    assert target.MAX_TIMEOUT_COUNT == 2


def test_annotation_validation_enforces_cross_property_constraints() -> None:
    validated = target.validate_annotation(_annotation())
    assert validated["properties"]["density_kg_m3"]["value"] == 7_850

    invalid = copy.deepcopy(_annotation())
    invalid["properties"]["static_friction_coefficient"]["value"] = 0.3
    invalid["properties"]["static_friction_coefficient"]["low"] = 0.2
    with pytest.raises(ValueError, match="static friction"):
        target.validate_annotation(invalid)

    extra = copy.deepcopy(_annotation())
    extra["properties"]["density_kg_m3"]["unit"] = "kg/m3"
    with pytest.raises(ValueError, match="keys mismatch"):
        target.validate_annotation(extra)


class APITimeoutError(Exception):
    pass


class _TimeoutCompletions:
    def __init__(self) -> None:
        self.call_count = 0

    async def create(self, **_: object) -> object:
        self.call_count += 1
        raise APITimeoutError("simulated request timeout")


class _TimeoutClient:
    def __init__(self) -> None:
        self.completions = _TimeoutCompletions()
        self.chat = self


def test_second_timeout_is_terminal_and_resume_does_not_call_again(tmp_path: Path) -> None:
    image_path = tmp_path / "evidence.bin"
    image_path.write_bytes(b"test-image-payload")
    evidence = [
        {
            "kind": "standard_bpy_render",
            "path": image_path.name,
            "sha256": target._sha256_path(image_path),
            "mime_type": "image/png",
            "size_bytes": image_path.stat().st_size,
        }
    ]
    row = {
        "material_key": "a" * 64,
        "material_id": "blenderkit:asset:version",
        "asset_base_id": "asset",
        "material_text": {},
    }
    descriptor = {"request_sha256": "b" * 64}
    settings = {
        "max_attempts": 6,
        "retry_base_seconds": 0.0,
        "retry_max_seconds": 0.0,
    }
    client = _TimeoutClient()

    first = asyncio.run(
        target._request_one(
            client=client,
            settings=settings,
            run_dir=tmp_path,
            row=row,
            evidence=evidence,
            descriptor=descriptor,
            repair_round=1,
        )
    )
    assert first["status"] == "failed"
    assert first["failure"] == "request_timeout_limit_exhausted"
    assert first["terminal"] is True
    assert client.completions.call_count == 2

    resumed = asyncio.run(
        target._request_one(
            client=client,
            settings=settings,
            run_dir=tmp_path,
            row=row,
            evidence=evidence,
            descriptor=descriptor,
            repair_round=2,
        )
    )
    assert resumed["failure"] == "request_timeout_limit_exhausted"
    assert client.completions.call_count == 2

    changed_request = asyncio.run(
        target._request_one(
            client=client,
            settings=settings,
            run_dir=tmp_path,
            row=row,
            evidence=evidence,
            descriptor={"request_sha256": "c" * 64},
            repair_round=3,
        )
    )
    assert changed_request["failure"] == "request_timeout_limit_exhausted"
    assert client.completions.call_count == 2
    changed_attempt = target._read_json(target._item_path(tmp_path, "attempts", "a" * 64))
    assert changed_attempt["request_sha256"] == "c" * 64
    assert changed_attempt["terminal_failure"] == "request_timeout_limit_exhausted"

    attempt = target._read_json(target._item_path(tmp_path, "attempts", "a" * 64))
    assert attempt["timeout_count"] == 2
    assert attempt["terminal_failure"] == "request_timeout_limit_exhausted"
    assert len(attempt["events"]) == 2


def test_non_timeout_terminal_is_reset_when_request_changes(tmp_path: Path) -> None:
    key = "d" * 64
    image_path = tmp_path / "evidence.bin"
    image_path.write_bytes(b"test-image-payload")
    evidence = [
        {
            "kind": "standard_bpy_render",
            "path": image_path.name,
            "sha256": target._sha256_path(image_path),
            "mime_type": "image/png",
            "size_bytes": image_path.stat().st_size,
        }
    ]
    row = {
        "material_key": key,
        "material_id": "blenderkit:asset:version",
        "asset_base_id": "asset",
        "material_text": {},
    }
    target._atomic_json(
        target._item_path(tmp_path, "attempts", key),
        {
            "schema_version": target.ATTEMPT_SCHEMA,
            "material_key": key,
            "material_id": row["material_id"],
            "request_sha256": "b" * 64,
            "attempt_count": 1,
            "retry_count": 0,
            "timeout_count": 0,
            "terminal_failure": "non_retryable_transport_error",
            "events": [],
        },
    )
    client = _TimeoutClient()
    result = asyncio.run(
        target._request_one(
            client=client,
            settings={
                "max_attempts": 2,
                "retry_base_seconds": 0.0,
                "retry_max_seconds": 0.0,
            },
            run_dir=tmp_path,
            row=row,
            evidence=evidence,
            descriptor={"request_sha256": "c" * 64},
            repair_round=1,
        )
    )

    assert result["failure"] == "request_timeout_limit_exhausted"
    assert client.completions.call_count == 2


def test_record_tree_rejects_noncanonical_entries(tmp_path: Path) -> None:
    key = "a" * 64
    canonical = target._record_path(tmp_path, key)
    canonical.parent.mkdir(parents=True)
    canonical.write_text("{}\n", encoding="utf-8")
    extra = tmp_path / "records" / "by-id" / "aa" / "nested" / "extra.json"
    extra.parent.mkdir(parents=True)
    extra.write_text("{}\n", encoding="utf-8")

    files, issues = target._record_tree(tmp_path)

    assert files == [canonical]
    assert any(issue["error"] == "noncanonical_record_file" for issue in issues)


def test_begin_run_archives_old_completion_marker(tmp_path: Path) -> None:
    target._atomic_json(tmp_path / "COMPLETE.json", {"status": "complete"})

    target._begin_run(tmp_path)

    assert not (tmp_path / "COMPLETE.json").exists()
    assert len(list((tmp_path / "history").glob("COMPLETE.*.json"))) == 1
    assert target._read_json(tmp_path / "IN_PROGRESS.json")["status"] == "in_progress"


def test_partial_renderer_startup_cleans_started_process(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_python = tmp_path / "renderer-python"
    fake_python.write_text("# fixture: subprocess creation is mocked")
    monkeypatch.setattr(target, "BPY_PYTHON", fake_python)

    class FakeProcess:
        pid = 123_456

        def __init__(self) -> None:
            self.finished = False

        def poll(self) -> int | None:
            return -15 if self.finished else None

        def wait(self, timeout: float) -> int:
            assert timeout == 10
            self.finished = True
            return -15

    fake_process = FakeProcess()
    launches = 0

    def fake_popen(*_args: object, **_kwargs: object) -> FakeProcess:
        nonlocal launches
        launches += 1
        if launches == 1:
            return fake_process
        raise OSError("simulated second worker launch failure")

    killed: list[tuple[int, int]] = []
    monkeypatch.setattr(target.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(target.os, "killpg", lambda pid, signum: killed.append((pid, signum)))

    with pytest.raises(OSError, match="second worker launch failure"):
        target._render_previews(
            tmp_path,
            [{"material_key": "a" * 64}, {"material_key": "b" * 64}],
            tmp_path,
            workers=2,
        )

    assert fake_process.finished is True
    assert killed == [(fake_process.pid, target.signal.SIGTERM)]
