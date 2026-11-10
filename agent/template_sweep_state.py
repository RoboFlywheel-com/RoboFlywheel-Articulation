# SPDX-License-Identifier: Apache-2.0

"""Cross-call streak state for `articraft template compile-sweep`.

Persists a short rolling history of sweeps per slug under
`<state_dir>/<slug>.json` and tracks how many consecutive sweeps each
FailureCluster signature has appeared in. This lets the CLI emit an
`escalation` block when the same structural failure pattern persists across
multiple iterations of the authoring loop, which signals the agent should
stop trying to patch the failing seed(s) directly and instead narrow
`config_from_seed` or split the template into multiple slugs.

This module deliberately operates on data only (no compile / no SDK imports)
so unit tests can drive it with synthetic state.
"""

from __future__ import annotations

import datetime as dt
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_STREAK_THRESHOLD = 3
DEFAULT_HISTORY_LIMIT = 10
# Two clusters from consecutive sweeps are treated as "the same persistent
# failure" when they share a failure_type and their shared-config-axis *key*
# sets overlap by at least this Jaccard ratio. Matching on a fuzzy key-set
# (rather than the exact signature) keeps a streak alive when the failing seed
# subset shifts between sweeps and an extra axis drifts in/out of the shared
# set — the case where exact-signature matching would spuriously reset the
# streak and miss a real non-convergence.
DEFAULT_AXIS_MATCH_JACCARD = 0.5


@dataclass(slots=True)
class SweepStateSnapshot:
    """One sweep's summary, retained in `sweep_history` for trend detection."""

    timestamp: str
    pass_rate: float
    verdict: str
    cluster_signatures: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "pass_rate": self.pass_rate,
            "verdict": self.verdict,
            "cluster_signatures": list(self.cluster_signatures),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SweepStateSnapshot":
        return cls(
            timestamp=str(payload.get("timestamp", "")),
            pass_rate=float(payload.get("pass_rate", 0.0)),
            verdict=str(payload.get("verdict", "fail")),
            cluster_signatures=[str(s) for s in payload.get("cluster_signatures", [])],
        )


@dataclass(slots=True)
class ClusterFingerprint:
    """Stable descriptor of one failure cluster, used for cross-sweep matching.

    ``signature`` is the per-sweep cluster id (also the streak key). ``failure_type``
    and ``axis_keys`` are the durable invariants the fuzzy matcher compares so a
    streak survives a drifting ``shared_config_axes`` set.
    """

    signature: str
    failure_type: str
    axis_keys: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "signature": self.signature,
            "failure_type": self.failure_type,
            "axis_keys": list(self.axis_keys),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ClusterFingerprint":
        return cls(
            signature=str(payload.get("signature", "")),
            failure_type=str(payload.get("failure_type", "")),
            axis_keys=[str(k) for k in payload.get("axis_keys", [])],
        )


@dataclass(slots=True)
class SweepStateRecord:
    """Per-slug persistent state."""

    slug: str
    last_updated_at: str
    sweep_history: list[SweepStateSnapshot] = field(default_factory=list)
    cluster_streaks: dict[str, int] = field(default_factory=dict)
    cluster_fingerprints: list[ClusterFingerprint] = field(default_factory=list)
    # Allowance strings observed on the most recent PASSING sweep. The next
    # run's allowance audit diffs against this to flag newly added allowances
    # (the cheapest way to whitewash a genuine overlap is a new allow_overlap).
    passing_allowances: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "slug": self.slug,
            "last_updated_at": self.last_updated_at,
            "sweep_history": [snap.to_dict() for snap in self.sweep_history],
            "cluster_streaks": dict(self.cluster_streaks),
            "cluster_fingerprints": [fp.to_dict() for fp in self.cluster_fingerprints],
            "passing_allowances": list(self.passing_allowances),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SweepStateRecord":
        history = [
            SweepStateSnapshot.from_dict(item)
            for item in payload.get("sweep_history", [])
            if isinstance(item, dict)
        ]
        fingerprints = [
            ClusterFingerprint.from_dict(item)
            for item in payload.get("cluster_fingerprints", [])
            if isinstance(item, dict)
        ]
        return cls(
            slug=str(payload.get("slug", "")),
            last_updated_at=str(payload.get("last_updated_at", "")),
            sweep_history=history,
            cluster_streaks={
                str(k): int(v) for k, v in (payload.get("cluster_streaks") or {}).items()
            },
            cluster_fingerprints=fingerprints,
            passing_allowances=[str(a) for a in payload.get("passing_allowances", [])],
        )


def _state_path(state_dir: Path, slug: str) -> Path:
    return state_dir / f"{slug}.json"


def load_state(state_dir: Path, slug: str) -> SweepStateRecord | None:
    path = _state_path(state_dir, slug)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return SweepStateRecord.from_dict(payload)


def save_state(state_dir: Path, record: SweepStateRecord) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    path = _state_path(state_dir, record.slug)
    path.write_text(
        json.dumps(record.to_dict(), indent=2, sort_keys=False),
        encoding="utf-8",
    )


def _utc_now_iso() -> str:
    return dt.datetime.now(tz=dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _axis_jaccard(a: list[str], b: list[str]) -> float:
    """Jaccard similarity of two axis-key sets. Two empty sets count as identical."""
    set_a, set_b = set(a), set(b)
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def _carryover_streak(
    current: ClusterFingerprint,
    prev_fingerprints: list[ClusterFingerprint],
    prev_streaks: dict[str, int],
    axis_match_jaccard: float,
) -> int:
    """Streak count a current cluster inherits from the best-matching prior cluster.

    A prior cluster matches when it shares the same ``failure_type`` and its
    axis-key set overlaps the current one by at least ``axis_match_jaccard``.
    Among matches, the highest-Jaccard prior wins; its streak is carried forward.
    Returns 0 when nothing matches (the cluster is new -> streak starts at 1).
    """
    best_streak = 0
    best_jaccard = axis_match_jaccard
    for prev in prev_fingerprints:
        if prev.failure_type != current.failure_type:
            continue
        jaccard = _axis_jaccard(current.axis_keys, prev.axis_keys)
        if jaccard >= best_jaccard:
            best_jaccard = jaccard
            best_streak = prev_streaks.get(prev.signature, 0)
    return best_streak


def update_streaks(
    *,
    slug: str,
    previous: SweepStateRecord | None,
    current_cluster_signatures: list[str] | None = None,
    current_clusters: list[ClusterFingerprint] | None = None,
    current_pass_rate: float,
    current_verdict: str,
    axis_match_jaccard: float = DEFAULT_AXIS_MATCH_JACCARD,
    history_limit: int = DEFAULT_HISTORY_LIMIT,
    now_iso: str | None = None,
) -> SweepStateRecord:
    """Return the next SweepStateRecord with updated streaks and trimmed history.

    Streak rule: a cluster's streak is the number of consecutive sweeps a matching
    cluster has appeared in. Pass ``current_clusters`` (rich fingerprints) to get
    fuzzy matching that survives a drifting ``shared_config_axes`` set — a current
    cluster inherits a prior streak when it shares the prior cluster's
    ``failure_type`` and its axis keys overlap by ``axis_match_jaccard`` (see
    `_carryover_streak`). ``current_cluster_signatures`` remains supported for
    exact-signature matching (legacy callers / tests); clusters absent from the
    current sweep drop out (streak resets to 0 once the cluster goes away).
    """
    timestamp = now_iso or _utc_now_iso()
    prev_streaks = dict(previous.cluster_streaks) if previous else {}

    if current_clusters is not None:
        prev_fingerprints = list(previous.cluster_fingerprints) if previous else []
        next_streaks = {
            cluster.signature: _carryover_streak(
                cluster, prev_fingerprints, prev_streaks, axis_match_jaccard
            )
            + 1
            for cluster in current_clusters
        }
        next_fingerprints = list(current_clusters)
        signatures = [cluster.signature for cluster in current_clusters]
    else:
        signatures = list(current_cluster_signatures or [])
        next_streaks = {sig: prev_streaks.get(sig, 0) + 1 for sig in signatures}
        next_fingerprints = []

    prev_history = list(previous.sweep_history) if previous else []
    snapshot = SweepStateSnapshot(
        timestamp=timestamp,
        pass_rate=round(current_pass_rate, 6),
        verdict=current_verdict,
        cluster_signatures=signatures,
    )
    prev_history.append(snapshot)
    trimmed = prev_history[-history_limit:]

    return SweepStateRecord(
        slug=slug,
        last_updated_at=timestamp,
        sweep_history=trimmed,
        cluster_streaks=next_streaks,
        cluster_fingerprints=next_fingerprints,
    )


@dataclass(slots=True)
class EscalationDecision:
    """Top-level escalation decision attached to the sweep report."""

    required: bool
    reasons: list[str]
    cluster_streaks: dict[str, int]
    pass_rate_trend: list[float]

    def to_dict(self) -> dict[str, Any]:
        return {
            "required": self.required,
            "reasons": list(self.reasons),
            "cluster_streaks": dict(self.cluster_streaks),
            "pass_rate_trend": list(self.pass_rate_trend),
        }


def compute_escalation(
    record: SweepStateRecord,
    *,
    streak_threshold: int = DEFAULT_STREAK_THRESHOLD,
    require_history_for_pass_trend: int = 3,
) -> EscalationDecision:
    """Decide whether the agent should escalate (stop patching, narrow scope).

    Triggers:
    - Any cluster_signature has streak >= streak_threshold (a persistent bug).
    - Last `require_history_for_pass_trend` snapshots show non-improving pass_rate
      AND all of them are below 1.0.
    """
    reasons: list[str] = []
    for sig, streak in record.cluster_streaks.items():
        if streak >= streak_threshold:
            reasons.append(
                f"cluster signature {sig} unchanged for {streak} consecutive sweeps "
                f"(>= {streak_threshold}); narrow config_from_seed, fix the shared "
                f"failure axis, or split the template into multiple slugs."
            )

    trend = [snap.pass_rate for snap in record.sweep_history]
    if len(record.sweep_history) >= require_history_for_pass_trend and all(
        snap.pass_rate < 1.0 for snap in record.sweep_history[-require_history_for_pass_trend:]
    ):
        recent = trend[-require_history_for_pass_trend:]
        if all(b <= a for a, b in zip(recent, recent[1:])):
            reasons.append(
                f"pass_rate has not improved over the last "
                f"{require_history_for_pass_trend} sweeps "
                f"(trend={[round(x, 3) for x in recent]}); the current fix strategy is not converging."
            )

    return EscalationDecision(
        required=bool(reasons),
        reasons=reasons,
        cluster_streaks=dict(record.cluster_streaks),
        pass_rate_trend=[round(x, 6) for x in trend],
    )
