# SPDX-License-Identifier: Apache-2.0

"""Config-axis introspection shared by the template sweep.

Templates expose exactly one sampling surface — ``config_from_seed(seed)``
(plus the modular ``slot_choices_for_seed(seed)`` reporting hook). Everything
here works through that surface only: each probe is a pure function call (no
compile), so dense deterministic probes are cheap.

Consumers:

- ``select_corner_seeds`` — deterministic corner-seed selection for the sweep
  pipeline: extra seeds that hit per-numeric-field extremes and slot combos the
  base sweep never realized. Selection-based, so every corner seed is a real
  reachable seed; a corner failure is a defect a batch user can hit.
- ``build_axis_realization`` — report-only declared-vs-realized distribution
  section (per-slot value counts + per-numeric-field range/histogram).
"""

from __future__ import annotations

import dataclasses
import importlib
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, Mapping, Sequence

from agent.template_sweep import SeedOutcome
from agent.template_sweep_coverage import _normalize_slot_choices

DEFAULT_CORNER_PROBE_SEEDS = 512
DEFAULT_MAX_CORNER_SEEDS = 12
# Corner seeds are enriched for extremes on purpose; tolerate this many corner
# failures per run before the corner stage gates the pipeline (mirrors the ~5%
# tolerance the 50-seed base sweep already grants).
DEFAULT_MAX_CORNER_FAILURES = 1
DEFAULT_HISTOGRAM_BINS = 8

# Config fields that track the seed itself rather than a geometric axis.
_EXCLUDED_LEAF_NAMES = {"seed", "name"}
# Categorical fallback (no slot_choices_for_seed): string fields with more
# distinct values than this are per-seed labels, not axes.
_MAX_CATEGORICAL_DISTINCT = 16

ConfigFn = Callable[[int], Any]
SlotFn = Callable[[int], Any]


def _leaf_name(key: str) -> str:
    return key.rsplit(".", 1)[-1].split("#", 1)[0]


def flatten_config(value: Any, *, prefix: str = "") -> dict[str, Any]:
    """Flatten a config (dataclass/mapping tree) into dotted scalar keys.

    Sequences contribute only their length (``key#len``): element-wise axes are
    template-internal detail, but a varying count is a real multiplicity axis.
    """
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        value = dataclasses.asdict(value)
    if isinstance(value, Mapping):
        flat: dict[str, Any] = {}
        for key in value:
            child = f"{prefix}.{key}" if prefix else str(key)
            flat.update(flatten_config(value[key], prefix=child))
        return flat
    if isinstance(value, (list, tuple, set, frozenset)):
        return {f"{prefix}#len": len(value)} if prefix else {}
    return {prefix: value} if prefix else {}


def _is_numeric(value: Any) -> bool:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(float(value))


@dataclass(slots=True)
class _ProbeSample:
    seed: int
    flat: dict[str, Any]
    combo: tuple[tuple[str, str], ...] | None


def _combo_text(combo: tuple[tuple[str, str], ...] | None) -> str | None:
    if combo is None:
        return None
    return "|".join(f"{slot}={module}" for slot, module in combo)


def _probe_samples(
    config_fn: ConfigFn, slot_fn: SlotFn | None, seeds: Iterable[int]
) -> tuple[list[_ProbeSample], int]:
    samples: list[_ProbeSample] = []
    errors = 0
    for seed in seeds:
        try:
            flat = flatten_config(config_fn(seed))
        except Exception:  # noqa: BLE001 - skip seeds the sampler rejects
            errors += 1
            continue
        combo: tuple[tuple[str, str], ...] | None = None
        if slot_fn is not None:
            try:
                combo = _normalize_slot_choices(slot_fn(seed))
            except Exception:  # noqa: BLE001 - combo unavailable for this seed
                combo = None
        samples.append(_ProbeSample(seed=seed, flat=flat, combo=combo))
    return samples, errors


def _assign_categorical_combos(samples: list[_ProbeSample]) -> None:
    """Fallback combo signature from categorical config fields (no slot hook)."""
    distinct: dict[str, set[str]] = {}
    usable: dict[str, bool] = {}
    for sample in samples:
        for key, value in sample.flat.items():
            if _leaf_name(key) in _EXCLUDED_LEAF_NAMES:
                continue
            if isinstance(value, (str, bool)):
                distinct.setdefault(key, set()).add(str(value))
                usable.setdefault(key, True)
            elif key in usable:
                usable[key] = False
    keys = sorted(
        key
        for key, values in distinct.items()
        if usable.get(key, False) and 2 <= len(values) <= _MAX_CATEGORICAL_DISTINCT
    )
    if not keys:
        return
    for sample in samples:
        sample.combo = tuple((key, str(sample.flat.get(key))) for key in keys)


def _numeric_axes(samples: Sequence[_ProbeSample]) -> dict[str, dict[str, Any]]:
    values_by_key: dict[str, list[tuple[float, int]]] = {}
    for sample in samples:
        for key, value in sample.flat.items():
            if _leaf_name(key) in _EXCLUDED_LEAF_NAMES:
                continue
            if _is_numeric(value):
                values_by_key.setdefault(key, []).append((float(value), sample.seed))
    axes: dict[str, dict[str, Any]] = {}
    for key in sorted(values_by_key):
        pairs = values_by_key[key]
        distinct = {value for value, _seed in pairs}
        if len(distinct) < 2:
            continue
        axes[key] = {
            "min": min(distinct),
            "max": max(distinct),
            "distinct": len(distinct),
            "samples": len(pairs),
        }
    return axes


@dataclass(slots=True)
class _Token:
    token_id: str
    kind: str  # "extreme" | "combo"
    candidates: set[int]


@dataclass(slots=True)
class CornerSeedPlan:
    """Deterministic corner-seed selection result (JSON-safe via to_dict)."""

    status: str  # "ok" | "unavailable" | "error"
    reason: str = ""
    seeds: list[int] = field(default_factory=list)
    probe_seed_count: int = 0
    probe_errors: int = 0
    numeric_fields: dict[str, dict[str, Any]] = field(default_factory=dict)
    combo_summary: dict[str, Any] = field(default_factory=dict)
    selection: list[dict[str, Any]] = field(default_factory=list)
    uncovered_tokens: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "reason": self.reason,
            "seeds": list(self.seeds),
            "probe_seed_count": self.probe_seed_count,
            "probe_errors": self.probe_errors,
            "numeric_fields": dict(self.numeric_fields),
            "combo_summary": dict(self.combo_summary),
            "selection": list(self.selection),
            "uncovered_tokens": list(self.uncovered_tokens),
        }


def select_corner_seeds_from_fns(
    config_fn: ConfigFn,
    slot_fn: SlotFn | None,
    *,
    base_seeds: Sequence[int],
    probe_seeds: int = DEFAULT_CORNER_PROBE_SEEDS,
    max_corner_seeds: int = DEFAULT_MAX_CORNER_SEEDS,
) -> CornerSeedPlan:
    """Pick extra seeds that hit numeric extremes / base-unrealized slot combos.

    Token universe: for every varying numeric config axis, ``field@min`` and
    ``field@max`` (measured over the probe range); plus one token per slot
    combo reachable in the probe but never realized by the base seeds. Tokens
    already hit by a base seed are dropped — the base sweep compiles them
    anyway. Selection is a deterministic greedy cover: extremes first, then
    combos by probe frequency; ties prefer seeds covering more uncovered
    tokens, then unseen combos (spreads gated axes across topologies), then
    the lowest seed.
    """
    base_list: list[int] = []
    base_set: set[int] = set()
    for seed in base_seeds:
        if seed not in base_set:
            base_set.add(seed)
            base_list.append(seed)
    probe_list = sorted(set(range(max(0, probe_seeds))) | base_set)
    samples, errors = _probe_samples(config_fn, slot_fn, probe_list)
    if not samples:
        return CornerSeedPlan(
            status="error",
            reason=f"config_from_seed failed for all {len(probe_list)} probe seeds",
            probe_seed_count=len(probe_list),
            probe_errors=errors,
        )
    if slot_fn is None or all(sample.combo is None for sample in samples):
        _assign_categorical_combos(samples)

    axes = _numeric_axes(samples)

    combo_counts: dict[tuple[tuple[str, str], ...], int] = {}
    combo_seeds: dict[tuple[tuple[str, str], ...], list[int]] = {}
    base_combos: set[tuple[tuple[str, str], ...]] = set()
    for sample in samples:
        if sample.combo is None:
            continue
        combo_counts[sample.combo] = combo_counts.get(sample.combo, 0) + 1
        combo_seeds.setdefault(sample.combo, []).append(sample.seed)
        if sample.seed in base_set:
            base_combos.add(sample.combo)

    tokens: list[_Token] = []
    for key in sorted(axes):
        stats = axes[key]
        for bound, token_suffix in ((stats["min"], "min"), (stats["max"], "max")):
            hitters = {
                sample.seed
                for sample in samples
                if key in sample.flat
                and _is_numeric(sample.flat[key])
                and float(sample.flat[key]) == bound
            }
            if hitters & base_set:
                continue  # the base sweep already compiles this extreme
            candidates = hitters - base_set
            if candidates:
                tokens.append(_Token(f"{key}@{token_suffix}", "extreme", candidates))
    uncovered_combos = sorted(
        (combo for combo in combo_counts if combo not in base_combos),
        key=lambda combo: (-combo_counts[combo], _combo_text(combo)),
    )
    for combo in uncovered_combos:
        candidates = {seed for seed in combo_seeds[combo] if seed not in base_set}
        if candidates:
            tokens.append(_Token(f"combo:{_combo_text(combo)}", "combo", candidates))

    seed_tokens: dict[int, set[str]] = {}
    for token in tokens:
        for seed in token.candidates:
            seed_tokens.setdefault(seed, set()).add(token.token_id)
    combo_by_seed = {sample.seed: sample.combo for sample in samples}

    covered: set[str] = set()
    selected: list[int] = []
    selected_combos: set[Any] = set()
    selection_detail: list[dict[str, Any]] = []
    for token in tokens:
        if token.token_id in covered:
            continue
        if len(selected) >= max_corner_seeds:
            break

        def _rank(seed: int) -> tuple[int, int, int]:
            new_cover = len(seed_tokens.get(seed, set()) - covered)
            combo_seen = 1 if combo_by_seed.get(seed) in selected_combos else 0
            return (-new_cover, combo_seen, seed)

        pick = min(token.candidates, key=_rank)
        newly = sorted(seed_tokens.get(pick, set()) - covered)
        covered.update(newly)
        selected.append(pick)
        selected_combos.add(combo_by_seed.get(pick))
        selection_detail.append(
            {
                "seed": pick,
                "tokens": newly,
                "combo": _combo_text(combo_by_seed.get(pick)),
            }
        )

    uncovered_after = sorted(token.token_id for token in tokens if token.token_id not in covered)
    reason = ""
    if not tokens:
        reason = "base seeds already cover every extreme/combo token"
    return CornerSeedPlan(
        status="ok",
        reason=reason,
        seeds=sorted(selected),
        probe_seed_count=len(probe_list),
        probe_errors=errors,
        numeric_fields=axes,
        combo_summary={
            "reachable": len(combo_counts),
            "realized_by_base": len(base_combos),
            "unrealized_by_base": len(uncovered_combos),
        },
        selection=selection_detail,
        uncovered_tokens=uncovered_after,
    )


def select_corner_seeds(
    slug: str,
    *,
    base_seeds: Sequence[int],
    probe_seeds: int = DEFAULT_CORNER_PROBE_SEEDS,
    max_corner_seeds: int = DEFAULT_MAX_CORNER_SEEDS,
) -> CornerSeedPlan:
    """Resolve ``agent.templates.<slug>`` and run corner-seed selection.

    Never raises: templates without the sampling surface (or import failures)
    yield status="unavailable"; selection bugs yield status="error". The sweep
    pipeline simply skips the corner stage in both cases.
    """
    try:
        module = importlib.import_module(f"agent.templates.{slug}")
    except Exception as exc:  # noqa: BLE001 - report, never raise
        return CornerSeedPlan(
            status="unavailable",
            reason=f"template module not importable: {type(exc).__name__}: {exc}",
        )
    config_fn = getattr(module, "config_from_seed", None)
    if not callable(config_fn):
        return CornerSeedPlan(
            status="unavailable",
            reason="template does not expose callable config_from_seed(seed)",
        )
    slot_fn = getattr(module, "slot_choices_for_seed", None)
    if not callable(slot_fn):
        slot_fn = None
    try:
        return select_corner_seeds_from_fns(
            config_fn,
            slot_fn,
            base_seeds=base_seeds,
            probe_seeds=probe_seeds,
            max_corner_seeds=max_corner_seeds,
        )
    except Exception as exc:  # noqa: BLE001 - report, never raise
        return CornerSeedPlan(
            status="error",
            reason=f"corner-seed selection failed: {type(exc).__name__}: {exc}",
        )


def build_axis_realization(
    slug: str,
    outcomes: Sequence[SeedOutcome],
    *,
    histogram_bins: int = DEFAULT_HISTOGRAM_BINS,
) -> dict[str, Any]:
    """Report-only realized-distribution section for the sweep report.

    Shows what the swept seeds actually realized per axis so declared-vs-
    realized drift (dead ranges, skew, gated axes stuck at defaults) is visible
    without recomputing anything: numeric fields get min/max/mean + a fixed-bin
    histogram, slot keys get per-value counts. Never affects the verdict.
    """
    flats: list[tuple[SeedOutcome, dict[str, Any]]] = []
    for outcome in outcomes:
        if not outcome.config:
            continue
        try:
            flats.append((outcome, flatten_config(outcome.config)))
        except Exception:  # noqa: BLE001 - malformed config payloads are skipped
            continue

    numeric: dict[str, dict[str, Any]] = {}
    values_by_key: dict[str, list[float]] = {}
    for _outcome, flat in flats:
        for key, value in flat.items():
            if _leaf_name(key) in _EXCLUDED_LEAF_NAMES:
                continue
            if _is_numeric(value):
                values_by_key.setdefault(key, []).append(float(value))
    for key in sorted(values_by_key):
        values = values_by_key[key]
        vmin, vmax = min(values), max(values)
        entry: dict[str, Any] = {
            "count": len(values),
            "min": vmin,
            "max": vmax,
            "mean": sum(values) / len(values),
            "distinct": len(set(values)),
        }
        if vmax > vmin:
            counts = [0] * histogram_bins
            span = vmax - vmin
            for value in values:
                index = min(histogram_bins - 1, int((value - vmin) / span * histogram_bins))
                counts[index] += 1
            entry["histogram"] = {"bins": counts, "lo": vmin, "hi": vmax}
        numeric[key] = entry

    slot_values: dict[str, dict[str, int]] = {}
    slot_errors = 0
    module = None
    try:
        module = importlib.import_module(f"agent.templates.{slug}")
    except Exception:  # noqa: BLE001 - slot section is best-effort
        module = None
    slot_fn = getattr(module, "slot_choices_for_seed", None) if module is not None else None
    if callable(slot_fn):
        for outcome in outcomes:
            if outcome.verdict != "pass":
                continue
            try:
                combo = _normalize_slot_choices(slot_fn(outcome.seed))
            except Exception:  # noqa: BLE001 - counted, reported, not fatal
                slot_errors += 1
                continue
            for slot_name, module_name in combo:
                per_slot = slot_values.setdefault(slot_name, {})
                per_slot[module_name] = per_slot.get(module_name, 0) + 1

    return {
        "seed_count": len(outcomes),
        "configs_seen": len(flats),
        "numeric_fields": numeric,
        "slot_value_counts": {
            key: dict(sorted(v.items())) for key, v in sorted(slot_values.items())
        },
        "slot_choice_errors": slot_errors,
    }
