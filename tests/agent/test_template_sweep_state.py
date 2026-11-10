# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
from pathlib import Path

from agent.template_sweep_state import (
    DEFAULT_HISTORY_LIMIT,
    DEFAULT_STREAK_THRESHOLD,
    ClusterFingerprint,
    SweepStateRecord,
    SweepStateSnapshot,
    compute_escalation,
    load_state,
    save_state,
    update_streaks,
)


def _record(slug: str = "demo", **kw) -> SweepStateRecord:
    return SweepStateRecord(
        slug=slug,
        last_updated_at=kw.get("last_updated_at", "2026-01-01T00:00:00Z"),
        sweep_history=kw.get("sweep_history", []),
        cluster_streaks=kw.get("cluster_streaks", {}),
    )


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    record = _record(
        sweep_history=[
            SweepStateSnapshot(
                timestamp="2026-01-01T00:00:00Z",
                pass_rate=0.6,
                verdict="fail",
                cluster_signatures=["aaa", "bbb"],
            ),
            SweepStateSnapshot(
                timestamp="2026-01-01T00:05:00Z",
                pass_rate=0.8,
                verdict="fail",
                cluster_signatures=["aaa"],
            ),
        ],
        cluster_streaks={"aaa": 2, "bbb": 1},
    )
    save_state(tmp_path, record)
    loaded = load_state(tmp_path, "demo")
    assert loaded is not None
    assert loaded.slug == "demo"
    assert loaded.cluster_streaks == {"aaa": 2, "bbb": 1}
    assert len(loaded.sweep_history) == 2
    assert loaded.sweep_history[1].pass_rate == 0.8


def test_load_state_returns_none_for_missing_file(tmp_path: Path) -> None:
    assert load_state(tmp_path, "absent_slug") is None


def test_load_state_returns_none_for_corrupt_file(tmp_path: Path) -> None:
    (tmp_path / "broken.json").write_text("{not json", encoding="utf-8")
    assert load_state(tmp_path, "broken") is None


def test_update_streaks_increments_for_repeated_signatures() -> None:
    previous = _record(cluster_streaks={"sig1": 1, "sig2": 1})
    nxt = update_streaks(
        slug="demo",
        previous=previous,
        current_cluster_signatures=["sig1", "sig2"],
        current_pass_rate=0.5,
        current_verdict="fail",
        now_iso="2026-01-01T00:10:00Z",
    )
    assert nxt.cluster_streaks == {"sig1": 2, "sig2": 2}
    assert len(nxt.sweep_history) == 1


def test_update_streaks_drops_disappeared_signatures() -> None:
    previous = _record(cluster_streaks={"sig1": 3, "sig2": 1})
    nxt = update_streaks(
        slug="demo",
        previous=previous,
        current_cluster_signatures=["sig1"],
        current_pass_rate=0.9,
        current_verdict="fail",
    )
    assert nxt.cluster_streaks == {"sig1": 4}
    assert "sig2" not in nxt.cluster_streaks


def test_update_streaks_starts_at_one_for_new_signatures() -> None:
    previous = _record(cluster_streaks={"sig1": 5})
    nxt = update_streaks(
        slug="demo",
        previous=previous,
        current_cluster_signatures=["sig1", "newsig"],
        current_pass_rate=0.6,
        current_verdict="fail",
    )
    assert nxt.cluster_streaks == {"sig1": 6, "newsig": 1}


def test_update_streaks_handles_fresh_state() -> None:
    nxt = update_streaks(
        slug="demo",
        previous=None,
        current_cluster_signatures=["sig1"],
        current_pass_rate=0.0,
        current_verdict="fail",
    )
    assert nxt.cluster_streaks == {"sig1": 1}
    assert len(nxt.sweep_history) == 1


def test_update_streaks_trims_history_to_limit() -> None:
    previous = _record(
        sweep_history=[
            SweepStateSnapshot(
                timestamp=f"2026-01-01T00:{i:02d}:00Z",
                pass_rate=0.5,
                verdict="fail",
                cluster_signatures=[],
            )
            for i in range(DEFAULT_HISTORY_LIMIT)
        ],
    )
    nxt = update_streaks(
        slug="demo",
        previous=previous,
        current_cluster_signatures=[],
        current_pass_rate=0.7,
        current_verdict="fail",
    )
    assert len(nxt.sweep_history) == DEFAULT_HISTORY_LIMIT
    assert nxt.sweep_history[-1].pass_rate == 0.7


def _fp(signature: str, failure_type: str, axis_keys: list[str]) -> ClusterFingerprint:
    return ClusterFingerprint(signature=signature, failure_type=failure_type, axis_keys=axis_keys)


def test_update_streaks_fuzzy_carries_over_on_axis_drift() -> None:
    # Same persistent overlap bug, but the failing seed subset shifted so an
    # extra shared axis drifted in -> the signature changed. Exact matching
    # would reset to 1; fuzzy matching (Jaccard {hub} vs {hub,blade} = 0.5)
    # must carry the streak forward.
    previous = SweepStateRecord(
        slug="demo",
        last_updated_at="2026-01-01T00:00:00Z",
        cluster_streaks={"sigA": 2},
        cluster_fingerprints=[_fp("sigA", "overlap", ["hub_style"])],
    )
    nxt = update_streaks(
        slug="demo",
        previous=previous,
        current_clusters=[_fp("sigB", "overlap", ["hub_style", "blade_count"])],
        current_pass_rate=0.5,
        current_verdict="fail",
    )
    assert nxt.cluster_streaks == {"sigB": 3}


def test_update_streaks_fuzzy_resets_on_disjoint_axes() -> None:
    previous = SweepStateRecord(
        slug="demo",
        last_updated_at="t",
        cluster_streaks={"sigA": 2},
        cluster_fingerprints=[_fp("sigA", "overlap", ["hub_style"])],
    )
    nxt = update_streaks(
        slug="demo",
        previous=previous,
        current_clusters=[_fp("sigB", "overlap", ["door_width"])],
        current_pass_rate=0.5,
        current_verdict="fail",
    )
    assert nxt.cluster_streaks == {"sigB": 1}


def test_update_streaks_fuzzy_resets_on_different_failure_type() -> None:
    previous = SweepStateRecord(
        slug="demo",
        last_updated_at="t",
        cluster_streaks={"sigA": 2},
        cluster_fingerprints=[_fp("sigA", "overlap", ["hub_style"])],
    )
    nxt = update_streaks(
        slug="demo",
        previous=previous,
        current_clusters=[_fp("sigB", "isolated_parts", ["hub_style"])],
        current_pass_rate=0.5,
        current_verdict="fail",
    )
    assert nxt.cluster_streaks == {"sigB": 1}


def test_update_streaks_fuzzy_matches_empty_axis_singletons() -> None:
    previous = SweepStateRecord(
        slug="demo",
        last_updated_at="t",
        cluster_streaks={"sigA": 2},
        cluster_fingerprints=[_fp("sigA", "isolated_parts", [])],
    )
    nxt = update_streaks(
        slug="demo",
        previous=previous,
        current_clusters=[_fp("sigB", "isolated_parts", [])],
        current_pass_rate=0.5,
        current_verdict="fail",
    )
    assert nxt.cluster_streaks == {"sigB": 3}


def test_update_streaks_fuzzy_persists_fingerprints_round_trip(tmp_path) -> None:
    nxt = update_streaks(
        slug="demo",
        previous=None,
        current_clusters=[_fp("sigA", "overlap", ["hub_style"])],
        current_pass_rate=0.5,
        current_verdict="fail",
    )
    save_state(tmp_path, nxt)
    loaded = load_state(tmp_path, "demo")
    assert loaded is not None
    assert loaded.cluster_fingerprints[0].failure_type == "overlap"
    assert loaded.cluster_fingerprints[0].axis_keys == ["hub_style"]


def test_compute_escalation_triggers_on_streak_threshold() -> None:
    record = _record(cluster_streaks={"sig1": DEFAULT_STREAK_THRESHOLD, "sig2": 1})
    decision = compute_escalation(record)
    assert decision.required is True
    assert any("sig1" in r for r in decision.reasons)


def test_compute_escalation_no_trigger_when_below_threshold() -> None:
    record = _record(cluster_streaks={"sig1": DEFAULT_STREAK_THRESHOLD - 1})
    decision = compute_escalation(record)
    assert decision.required is False
    assert decision.reasons == []


def test_compute_escalation_triggers_on_non_improving_pass_rate_trend() -> None:
    record = _record(
        sweep_history=[
            SweepStateSnapshot("t1", 0.6, "fail", []),
            SweepStateSnapshot("t2", 0.55, "fail", []),
            SweepStateSnapshot("t3", 0.55, "fail", []),
        ],
        cluster_streaks={},
    )
    decision = compute_escalation(record)
    assert decision.required is True
    assert any("pass_rate" in r for r in decision.reasons)


def test_compute_escalation_no_trigger_when_pass_rate_improving() -> None:
    record = _record(
        sweep_history=[
            SweepStateSnapshot("t1", 0.6, "fail", []),
            SweepStateSnapshot("t2", 0.7, "fail", []),
            SweepStateSnapshot("t3", 0.85, "fail", []),
        ],
        cluster_streaks={},
    )
    decision = compute_escalation(record)
    assert decision.required is False


def test_compute_escalation_no_trigger_when_pass_rate_hits_1() -> None:
    record = _record(
        sweep_history=[
            SweepStateSnapshot("t1", 1.0, "pass", []),
            SweepStateSnapshot("t2", 1.0, "pass", []),
            SweepStateSnapshot("t3", 1.0, "pass", []),
        ],
    )
    decision = compute_escalation(record)
    assert decision.required is False


def test_state_file_layout(tmp_path: Path) -> None:
    save_state(tmp_path, _record(slug="layout_check"))
    files = list(tmp_path.iterdir())
    assert len(files) == 1
    assert files[0].name == "layout_check.json"
    payload = json.loads(files[0].read_text(encoding="utf-8"))
    assert payload["slug"] == "layout_check"
