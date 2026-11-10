# SPDX-License-Identifier: Apache-2.0

"""Modular coverage gate for `articraft template compile-sweep`.

The template authoring route is now modular-only. A sweep passes coverage when
the template declares `__modular__ = True`, exposes `slot_choices_for_seed`, and
**every registered slot key actually varies** across the passing seeds — i.e.
each slot realizes at least 2 distinct module values (unless it is reachably
constant). This per-axis coverage replaces the old ">=10 distinct whole-tuples"
count, which rewarded padding the tuple with multiplicity N; structural N is now
covered, never counted. See `articraft_template_authoring/VISUAL_DIVERSITY_MODEL.md`.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from agent.template_sweep import SeedOutcome

# Per-axis coverage floor: every registered slot key must realize at least this
# many distinct module values among the passing seeds, UNLESS the slot is
# reachably constant (then it is exempt + flagged as a single-candidate smell).
MIN_DISTINCT_PER_SLOT_KEY = 2
# Legacy whole-tuple distinct threshold. No longer the gate; kept for reference
# and back-compat with docs/tooling that cite the name.
MODULE_TOPOLOGY_MIN_DISTINCT = 10
# Dense deterministic probe used to estimate the space the sampler can reach:
# distinct whole tuples (denominator for `distinct_count`) AND per-key reachable
# value sets (the exemption for reachably-constant slots). Cheap: each probe is a
# pure `slot_choices_for_seed` call, no compile. Early-stops once no new tuple has
# appeared for PROBE_PATIENCE consecutive seeds.
MODULE_TOPOLOGY_PROBE_SEEDS = 2000
MODULE_TOPOLOGY_PROBE_PATIENCE = 300


@dataclass(slots=True)
class CoverageGateResult:
    name: str
    status: str  # "pass" | "fail" | "skipped"
    details: dict[str, Any] = field(default_factory=dict)
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status,
            "details": self.details,
            "reason": self.reason,
        }


@dataclass(slots=True)
class CoverageGates:
    module_topology_diversity: CoverageGateResult

    def _iter_gates(self):
        return (self.module_topology_diversity,)

    def to_dict(self) -> dict[str, Any]:
        return {
            "module_topology_diversity": self.module_topology_diversity.to_dict(),
        }

    def all_pass_or_skipped(self) -> bool:
        return all(gate.status in {"pass", "skipped"} for gate in self._iter_gates())

    def failing_gates(self) -> list[str]:
        return [gate.name for gate in self._iter_gates() if gate.status == "fail"]


def _template_module(slug: str):
    try:
        return importlib.import_module(f"agent.templates.{slug}")
    except ImportError:
        return None


def is_modular_template(slug: str) -> bool:
    module = _template_module(slug)
    return bool(getattr(module, "__modular__", False)) if module is not None else False


def _slot_choices_for_seed(slug: str, seed: int) -> Any:
    module = _template_module(slug)
    if module is None:
        raise ImportError(f"agent.templates.{slug} could not be imported")
    fn = getattr(module, "slot_choices_for_seed", None)
    if not callable(fn):
        raise AttributeError(
            f"agent.templates.{slug} is missing callable slot_choices_for_seed(seed)"
        )
    return fn(seed)


def _normalize_slot_choices(raw: Any) -> tuple[tuple[str, str], ...]:
    if isinstance(raw, Mapping):
        items = list(raw.items())
    elif isinstance(raw, Sequence) and not isinstance(raw, (str, bytes, bytearray)):
        items = list(raw)
    else:
        raise ValueError("slot_choices_for_seed must return a mapping or sequence of pairs")

    normalized: list[tuple[str, str]] = []
    for index, item in enumerate(items):
        if not (
            isinstance(item, Sequence)
            and not isinstance(item, (str, bytes, bytearray))
            and len(item) == 2
        ):
            raise ValueError(
                "slot_choices_for_seed entries must be (slot_name, module_name) pairs; "
                f"entry {index} was {item!r}"
            )
        slot_name, module_name = item
        if not isinstance(slot_name, str) or not isinstance(module_name, str):
            raise ValueError(
                "slot_choices_for_seed entries must contain string slot/module names; "
                f"entry {index} was {item!r}"
            )
        normalized.append((slot_name, module_name))

    if not normalized:
        raise ValueError("slot_choices_for_seed returned no slot choices")
    return tuple(normalized)


def _per_key_values(
    choice_tuples: Sequence[tuple[tuple[str, str], ...]],
) -> dict[str, set[str]]:
    """Collapse normalized (slot, module) tuples into per-slot-key value sets."""
    per_key: dict[str, set[str]] = {}
    for choices in choice_tuples:
        for slot_name, module_name in choices:
            per_key.setdefault(slot_name, set()).add(module_name)
    return per_key


# Probe results are deterministic per (slug, probe_seeds, patience) within a
# process — the pipeline re-evaluates gates at every stage (seed0/fast/medium/
# final/corner), and templates whose slot_choices_for_seed routes through an
# expensive resolve_config (grid searches, clearance solves) turn the "cheap
# pure probe" assumption into minutes of hidden wall-time without this cache.
_PROBE_CACHE: dict[tuple[str, int, int], tuple[dict[str, Any], dict[str, set[str]]]] = {}


def _probe_slot_choices(
    slug: str,
    *,
    probe_seeds: int = MODULE_TOPOLOGY_PROBE_SEEDS,
    patience: int = MODULE_TOPOLOGY_PROBE_PATIENCE,
) -> tuple[dict[str, Any], dict[str, set[str]]]:
    """Probe the sampler over a dense seed range; return (summary, per_key_values).

    ``summary`` is the JSON-safe distinct whole-tuple count info; ``per_key_values``
    maps each slot key to the set of module values reachable over the probe (the
    exemption denominator for the >=2 floor). Early-stops once no NEW whole tuple
    has appeared for ``patience`` consecutive seeds; the per-key sets are then a
    lower bound on the reachable values, which is sufficient for the floor.
    """
    cache_key = (slug, int(probe_seeds), int(patience))
    cached = _PROBE_CACHE.get(cache_key)
    if cached is not None:
        summary, per_key = cached
        return dict(summary), {k: set(v) for k, v in per_key.items()}

    distinct: set[tuple[tuple[str, str], ...]] = set()
    per_key: dict[str, set[str]] = {}
    since_new = 0
    used = 0
    saturated = False
    for seed in range(probe_seeds):
        used = seed + 1
        try:
            choices = _normalize_slot_choices(_slot_choices_for_seed(slug, seed))
        except Exception:  # noqa: BLE001 - skip seeds the sampler rejects
            continue
        for slot_name, module_name in choices:
            per_key.setdefault(slot_name, set()).add(module_name)
        if choices in distinct:
            since_new += 1
        else:
            distinct.add(choices)
            since_new = 0
        if since_new >= patience:
            saturated = True
            break
    summary = {
        "count": len(distinct),
        "probe_seeds_used": used,
        "saturated": saturated,
    }
    _PROBE_CACHE[cache_key] = (dict(summary), {k: set(v) for k, v in per_key.items()})
    return summary, per_key


def reachable_topology_count(
    slug: str,
    *,
    probe_seeds: int = MODULE_TOPOLOGY_PROBE_SEEDS,
    patience: int = MODULE_TOPOLOGY_PROBE_PATIENCE,
) -> dict[str, Any]:
    """Distinct whole-tuple count the sampler can reach (visibility only).

    Thin wrapper over ``_probe_slot_choices`` returning just the JSON-safe summary;
    does NOT affect the gate verdict.
    """
    summary, _per_key = _probe_slot_choices(slug, probe_seeds=probe_seeds, patience=patience)
    return summary


_LEGACY_NONMODULAR_FILE = Path(__file__).resolve().parent / "templates" / "_legacy_nonmodular.txt"
_LEGACY_NONMODULAR_CACHE: set[str] | None = None


def _legacy_nonmodular_slugs() -> set[str]:
    """Frozen allowlist of stock templates that predate the modular mandate.

    The module_topology_diversity gate SKIPS these instead of hard-failing —
    their migration is deferred by decision, and without slot_choices there is
    nothing to measure. New slugs must NOT be added (the file says so): a new
    non-modular template still hard-fails the gate.
    """
    global _LEGACY_NONMODULAR_CACHE
    if _LEGACY_NONMODULAR_CACHE is None:
        try:
            lines = _LEGACY_NONMODULAR_FILE.read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []
        _LEGACY_NONMODULAR_CACHE = {
            line.strip() for line in lines if line.strip() and not line.startswith("#")
        }
    return _LEGACY_NONMODULAR_CACHE


def check_module_topology_diversity(
    slug: str,
    outcomes: Sequence[SeedOutcome],
    *,
    min_per_key: int = MIN_DISTINCT_PER_SLOT_KEY,
) -> CoverageGateResult:
    # No sweep-size activation threshold: reachability comes from the dense
    # pure probe (not from swept seeds), so the >=2-per-key floor is enforced
    # whenever the gate is evaluated. The pipeline evaluates it per stage;
    # its verdict-relevant evaluation is the final stage (36 cumulative).

    if not is_modular_template(slug):
        if slug in _legacy_nonmodular_slugs():
            return CoverageGateResult(
                name="module_topology_diversity",
                status="skipped",
                details={"slug": slug, "__modular__": False, "legacy_nonmodular": True},
                reason=(
                    "legacy non-modular template (frozen allowlist "
                    "agent/templates/_legacy_nonmodular.txt): coverage is "
                    "unmeasurable without slot_choices; modular migration is "
                    "deferred debt, geometry gates still decide the verdict."
                ),
            )
        return CoverageGateResult(
            name="module_topology_diversity",
            status="fail",
            details={"slug": slug, "__modular__": False, "min_per_key": min_per_key},
            reason=(
                "template is not marked `__modular__ = True`; new parameterized "
                "templates must use the modular slot/module route."
            ),
        )

    passing = [outcome for outcome in outcomes if outcome.verdict == "pass"]
    distinct: dict[tuple[tuple[str, str], ...], list[int]] = {}
    errors: list[dict[str, Any]] = []
    for outcome in passing:
        try:
            choices = _normalize_slot_choices(_slot_choices_for_seed(slug, outcome.seed))
        except Exception as exc:  # noqa: BLE001 - report malformed seed choices as gate data
            errors.append(
                {
                    "seed": outcome.seed,
                    "error_kind": type(exc).__name__,
                    "error": str(exc),
                }
            )
            continue
        distinct.setdefault(choices, []).append(outcome.seed)

    realized = _per_key_values(list(distinct.keys()))
    reach_summary, reach_per_key = _probe_slot_choices(slug)

    per_key_coverage: list[dict[str, Any]] = []
    single_value_slots: list[str] = []
    for key in sorted(realized):
        got = realized[key]
        reachable_n = len(reach_per_key.get(key, got))
        required = min(min_per_key, reachable_n)
        ok = len(got) >= required
        if reachable_n <= 1:
            single_value_slots.append(key)
        per_key_coverage.append(
            {
                "key": key,
                "distinct_values": sorted(got),
                "count": len(got),
                "reachable": reachable_n,
                "required": required,
                "ok": ok,
            }
        )
    failing = [c for c in per_key_coverage if not c["ok"]]

    details: dict[str, Any] = {
        "total_outcomes": len(outcomes),
        "passing_seed_count": len(passing),
        "min_per_key": min_per_key,
        "distinct_count": len(distinct),
        "reachable_topology": reach_summary,
        "per_key_coverage": per_key_coverage,
        "single_value_slots": single_value_slots,
        "errors": errors,
    }

    if errors:
        return CoverageGateResult(
            name="module_topology_diversity",
            status="fail",
            details=details,
            reason=(
                "one or more passing seeds could not be mapped through "
                "slot_choices_for_seed(seed); fix the modular reporting function."
            ),
        )

    if not realized:
        return CoverageGateResult(
            name="module_topology_diversity",
            status="fail",
            details=details,
            reason=(
                "no passing seeds produced slot choices; cannot assess per-axis "
                "coverage. Fix failing seeds before the diversity gate can pass."
            ),
        )

    if failing:
        parts = ", ".join(
            f"{c['key']} ({c['count']}/{c['required']} distinct, reachable {c['reachable']})"
            for c in failing
        )
        return CoverageGateResult(
            name="module_topology_diversity",
            status="fail",
            details=details,
            reason=(
                f"slot key(s) under-covered: {parts}. Each registered slot must "
                f"realize at least {min_per_key} distinct values among passing seeds "
                "(a slot stuck at one value is a dead or orphaned axis). Register the "
                "missing variety, rebalance sampling weights, or repair failing "
                "module combinations."
            ),
        )

    return CoverageGateResult(
        name="module_topology_diversity",
        status="pass",
        details=details,
    )


def evaluate_gates(
    *,
    slug: str,
    outcomes: Sequence[SeedOutcome],
    repo_root: Path,
) -> CoverageGates:
    _ = repo_root
    return CoverageGates(
        module_topology_diversity=check_module_topology_diversity(slug, outcomes),
    )
