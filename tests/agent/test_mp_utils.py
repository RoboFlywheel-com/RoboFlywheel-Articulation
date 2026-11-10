# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent import mp_utils


def test_resolve_mp_start_method_prefers_spawn(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ARTICRAFT_MP_START_METHOD", raising=False)
    monkeypatch.setattr(mp_utils.mp, "get_all_start_methods", lambda: ["spawn", "forkserver"])

    assert mp_utils.resolve_mp_start_method() == "spawn"


def test_configured_mp_start_method_override_returns_trimmed_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ARTICRAFT_MP_START_METHOD", " fork ")

    assert mp_utils.configured_mp_start_method_override() == "fork"


def test_resolve_mp_start_method_prefers_fork_when_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ARTICRAFT_MP_START_METHOD", raising=False)
    monkeypatch.setattr(
        mp_utils.mp,
        "get_all_start_methods",
        lambda: ["spawn", "forkserver", "fork"],
    )

    assert mp_utils.resolve_mp_start_method(prefer_fork=True) == "fork"


def test_resolve_mp_start_method_uses_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARTICRAFT_MP_START_METHOD", "spawn")
    monkeypatch.setattr(mp_utils.mp, "get_all_start_methods", lambda: ["spawn", "forkserver"])

    assert mp_utils.resolve_mp_start_method() == "spawn"


def test_resolve_mp_start_method_rejects_unknown_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ARTICRAFT_MP_START_METHOD", "fork")
    monkeypatch.setattr(mp_utils.mp, "get_all_start_methods", lambda: ["spawn", "forkserver"])

    with pytest.raises(ValueError, match="ARTICRAFT_MP_START_METHOD"):
        mp_utils.resolve_mp_start_method()


def test_resolve_mp_start_method_falls_back_to_first_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("ARTICRAFT_MP_START_METHOD", raising=False)
    monkeypatch.setattr(mp_utils.mp, "get_all_start_methods", lambda: ["spawn"])

    assert mp_utils.resolve_mp_start_method() == "spawn"


def test_get_mp_context_preloads_forkserver_modules(monkeypatch: pytest.MonkeyPatch) -> None:
    sentinel = object()
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        mp_utils,
        "resolve_mp_start_method",
        lambda prefer_fork=False: "forkserver",
    )
    monkeypatch.setattr(
        mp_utils.mp,
        "set_forkserver_preload",
        lambda modules: captured.setdefault("modules", list(modules)),
    )

    def fake_get_context(method: str) -> object:
        captured["method"] = method
        return sentinel

    monkeypatch.setattr(mp_utils.mp, "get_context", fake_get_context)

    context = mp_utils.get_mp_context(forkserver_preload=["cadquery", "OCP"])

    assert context is sentinel
    assert captured["method"] == "forkserver"
    assert captured["modules"] == ["cadquery", "OCP"]
