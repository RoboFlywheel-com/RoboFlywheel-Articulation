# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from agent.template_sweep import SeedOutcome
from agent.template_sweep_clusters import (
    DIAGNOSIS_HINTS,
    GENERIC_HINT,
    cluster_failures,
)


def _outcome(
    *,
    seed: int,
    verdict: str = "fail",
    config: dict | None = None,
    failure_type: str | None = "fail_if_articulation_origin_far_from_geometry(tol=0.015)",
    failure_type_normalized: str | None = "fail_if_articulation_origin_far_from_geometry",
    failure_details: str = "joint='x' dist_parent=0.5",
) -> SeedOutcome:
    return SeedOutcome(
        seed=seed,
        verdict=verdict,
        config=config or {},
        failure_type=failure_type,
        failure_type_normalized=failure_type_normalized,
        failure_details=failure_details,
        elapsed_s=0.01,
    )


def test_cluster_groups_by_failure_type_normalized() -> None:
    outcomes = [
        _outcome(seed=1, failure_type_normalized="fail_if_isolated_parts"),
        _outcome(seed=2, failure_type_normalized="fail_if_isolated_parts"),
        _outcome(seed=3, failure_type_normalized="fail_if_parts_overlap_in_current_pose"),
    ]
    clusters = cluster_failures(outcomes)
    assert len(clusters) == 2
    by_ft = {c.shared_failure_type: c for c in clusters}
    assert sorted(by_ft["fail_if_isolated_parts"].seeds) == [1, 2]
    assert by_ft["fail_if_parts_overlap_in_current_pose"].seeds == [3]


def test_cluster_orders_by_descending_size_then_failure_type() -> None:
    outcomes = [
        _outcome(seed=1, failure_type_normalized="zeta"),
        _outcome(seed=2, failure_type_normalized="alpha"),
        _outcome(seed=3, failure_type_normalized="alpha"),
        _outcome(seed=4, failure_type_normalized="alpha"),
    ]
    clusters = cluster_failures(outcomes)
    assert [c.shared_failure_type for c in clusters] == ["alpha", "zeta"]
    assert clusters[0].seeds == [2, 3, 4]
    assert clusters[1].seeds == [1]


def test_cluster_shared_axes_keeps_only_universal_values() -> None:
    outcomes = [
        _outcome(seed=1, config={"blade_shape": "swept", "size": 0.5, "n": 1}),
        _outcome(seed=2, config={"blade_shape": "swept", "size": 0.7, "n": 1}),
        _outcome(seed=3, config={"blade_shape": "swept", "size": 0.9, "n": 1}),
    ]
    clusters = cluster_failures(outcomes)
    assert len(clusters) == 1
    shared = clusters[0].shared_config_axes
    assert shared == {"blade_shape": "swept", "n": 1}
    # size differs across seeds -> excluded
    assert "size" not in shared


def test_cluster_singleton_has_empty_shared_axes_and_is_marked() -> None:
    outcomes = [
        _outcome(seed=1, config={"a": 1, "b": 2}),
    ]
    clusters = cluster_failures(outcomes)
    assert len(clusters) == 1
    assert clusters[0].is_singleton is True
    assert clusters[0].shared_config_axes == {}


def test_cluster_skips_passing_outcomes() -> None:
    outcomes = [
        _outcome(seed=1, verdict="pass", failure_type=None, failure_type_normalized=None),
        _outcome(seed=2),
    ]
    clusters = cluster_failures(outcomes)
    assert len(clusters) == 1
    assert clusters[0].seeds == [2]


def test_cluster_diagnosis_hint_lookup() -> None:
    outcomes = [
        _outcome(seed=1, failure_type_normalized="fail_if_articulation_origin_far_from_geometry"),
    ]
    cluster = cluster_failures(outcomes)[0]
    assert (
        cluster.diagnosis_hint == DIAGNOSIS_HINTS["fail_if_articulation_origin_far_from_geometry"]
    )


def test_cluster_diagnosis_hint_falls_back_to_generic() -> None:
    outcomes = [
        _outcome(seed=1, failure_type_normalized="some_unregistered_check_xyz"),
    ]
    cluster = cluster_failures(outcomes)[0]
    assert cluster.diagnosis_hint == GENERIC_HINT


def test_cluster_signature_is_stable_across_runs() -> None:
    outcomes_a = [
        _outcome(seed=1, config={"x": "a"}),
        _outcome(seed=2, config={"x": "a"}),
    ]
    outcomes_b = [
        _outcome(seed=11, config={"x": "a"}),
        _outcome(seed=12, config={"x": "a"}),
    ]
    sig_a = cluster_failures(outcomes_a)[0].cluster_signature
    sig_b = cluster_failures(outcomes_b)[0].cluster_signature
    assert sig_a == sig_b  # seeds differ but failure_type + shared_axes match


def test_cluster_signature_changes_when_axes_change() -> None:
    a = cluster_failures(
        [_outcome(seed=1, config={"x": "a"}), _outcome(seed=2, config={"x": "a"})]
    )[0].cluster_signature
    b = cluster_failures(
        [_outcome(seed=1, config={"x": "b"}), _outcome(seed=2, config={"x": "b"})]
    )[0].cluster_signature
    assert a != b


def test_cluster_handles_nested_config_via_flatten() -> None:
    outcomes = [
        _outcome(
            seed=1,
            config={"hub": {"style": "spherical", "size": 0.1}, "blade_count": 3},
        ),
        _outcome(
            seed=2,
            config={"hub": {"style": "spherical", "size": 0.2}, "blade_count": 3},
        ),
    ]
    clusters = cluster_failures(outcomes)
    assert len(clusters) == 1
    shared = clusters[0].shared_config_axes
    assert shared.get("hub.style") == "spherical"
    assert "hub.size" not in shared
    assert shared.get("blade_count") == 3
