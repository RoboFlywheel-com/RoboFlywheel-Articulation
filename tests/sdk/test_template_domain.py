# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import itertools

import pytest

from sdk import (
    TemplateDomain,
    TemplateDomainError,
    component_slot,
    multiplicity_slot,
)


def _pulley_domain() -> TemplateDomain:
    return TemplateDomain(
        slots=(
            component_slot("frame", ("open", "enclosed")),
            component_slot("sheave", ("deep_u", "narrow_v")),
            multiplicity_slot(
                "sheave_count",
                (1, 2, 3, 4),
                item_slot="sheave",
            ),
        )
    )


def test_domain_sampling_can_reach_the_full_declared_cartesian_domain() -> None:
    domain = _pulley_domain()

    samples = {
        tuple(domain.sample(seed)[name] for name in domain.slot_names) for seed in range(1000)
    }
    expected = set(
        itertools.product(
            ("open", "enclosed"),
            ("deep_u", "narrow_v"),
            (1, 2, 3, 4),
        )
    )

    assert samples == expected


def test_domain_audit_counts_core_without_multiplicity_and_raw_with_it() -> None:
    audit = _pulley_domain().audit()

    assert audit["core_domain"] == 4
    assert audit["raw_domain"] == 16
    assert audit["multiplicity"]["sheave_count"] == {
        "values": [1, 2, 3, 4],
        "minimum": 1,
        "maximum": 4,
        "item_slot": "sheave",
    }


def test_automatic_corners_cover_candidates_and_n_edges() -> None:
    cases = {case.name: case for case in _pulley_domain().automatic_corners()}

    assert set(cases) == {
        "candidate_frame_open",
        "candidate_frame_enclosed",
        "candidate_sheave_deep_u",
        "candidate_sheave_narrow_v",
        "edge_sheave_count_1",
        "edge_sheave_count_4",
    }


def test_domain_rejects_unknown_or_undeclared_values() -> None:
    domain = _pulley_domain()

    with pytest.raises(TemplateDomainError, match="unknown domain slots"):
        domain.complete({"unknown": "value"})
    with pytest.raises(TemplateDomainError, match="undeclared value"):
        domain.validate({"frame": "round"}, complete=False)


def test_domain_rejects_unknown_multiplicity_item_slot() -> None:
    with pytest.raises(TemplateDomainError, match="unknown component item_slot"):
        TemplateDomain(
            slots=(
                component_slot("sheave", ("deep_u",)),
                multiplicity_slot(
                    "sheave_count",
                    (1, 2),
                    item_slot="missing",
                ),
            )
        )
