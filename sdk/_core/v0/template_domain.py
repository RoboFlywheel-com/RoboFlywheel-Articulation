# SPDX-License-Identifier: Apache-2.0

"""Finite semantic template domains with deterministic legal sampling.

The domain is deliberately small: it describes component choices and bounded
multiplicity only.  Continuous dimensions, palettes, names, and decorative
detail stay in the authored Config and do not inflate structural diversity.
"""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Literal

SlotKind = Literal["component", "multiplicity"]


class TemplateDomainError(ValueError):
    """Raised when a domain declaration or requested completion is invalid."""


@dataclass(frozen=True, slots=True)
class DomainSlot:
    name: str
    values: tuple[object, ...]
    kind: SlotKind = "component"
    role: str = ""
    item_slot: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise TemplateDomainError("domain slot name must be non-empty")
        if self.kind not in {"component", "multiplicity"}:
            raise TemplateDomainError(f"invalid domain slot kind {self.kind!r}")
        if not self.values:
            raise TemplateDomainError(f"domain slot {self.name!r} has no values")
        if len(self.values) != len({_stable_value(value) for value in self.values}):
            raise TemplateDomainError(f"domain slot {self.name!r} has duplicate values")
        if self.kind == "multiplicity" and any(
            not isinstance(value, int) or isinstance(value, bool) for value in self.values
        ):
            raise TemplateDomainError(
                f"multiplicity slot {self.name!r} accepts bounded integers only"
            )
        if self.kind == "component" and self.item_slot:
            raise TemplateDomainError(
                f"component slot {self.name!r} cannot declare an item_slot"
            )


@dataclass(frozen=True, slots=True)
class CornerCase:
    name: str
    overrides: tuple[tuple[str, object], ...]
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise TemplateDomainError("corner case name must be non-empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "overrides": dict(self.overrides),
            "reason": self.reason,
        }


def _stable_value(value: object) -> tuple[str, str]:
    return (type(value).__name__, repr(value))


def component_slot(
    name: str,
    values: Sequence[object],
    *,
    role: str = "",
) -> DomainSlot:
    return DomainSlot(name=name, values=tuple(values), kind="component", role=role)


def multiplicity_slot(
    name: str,
    values: Sequence[int],
    *,
    role: str = "",
    item_slot: str = "",
) -> DomainSlot:
    return DomainSlot(
        name=name,
        values=tuple(values),
        kind="multiplicity",
        role=role,
        item_slot=item_slot,
    )


def corner_case(
    name: str,
    overrides: Mapping[str, object],
    *,
    reason: str = "",
) -> CornerCase:
    return CornerCase(name, tuple(overrides.items()), reason)


@dataclass(frozen=True, slots=True)
class TemplateDomain:
    slots: tuple[DomainSlot, ...]

    def __post_init__(self) -> None:
        if not self.slots:
            raise TemplateDomainError("template domain needs at least one slot")
        slot_names = [slot.name for slot in self.slots]
        if len(slot_names) != len(set(slot_names)):
            raise TemplateDomainError("template domain has duplicate slot names")
        component_names = {slot.name for slot in self.slots if slot.kind == "component"}
        for slot in self.slots:
            if (
                slot.kind == "multiplicity"
                and slot.item_slot
                and slot.item_slot not in component_names
            ):
                raise TemplateDomainError(
                    f"multiplicity slot {slot.name!r} references unknown component "
                    f"item_slot {slot.item_slot!r}"
                )

    @property
    def slot_names(self) -> tuple[str, ...]:
        return tuple(slot.name for slot in self.slots)

    def _validate_partial(self, partial: Mapping[str, object]) -> None:
        declared = {slot.name: slot for slot in self.slots}
        unknown = sorted(set(partial) - set(declared))
        if unknown:
            raise TemplateDomainError(f"unknown domain slots: {', '.join(unknown)}")
        for name, value in partial.items():
            if value not in declared[name].values:
                raise TemplateDomainError(f"slot {name!r} uses undeclared value {value!r}")

    def complete(
        self,
        partial: Mapping[str, object],
        *,
        preferred: Mapping[str, object] | None = None,
    ) -> dict[str, object]:
        self._validate_partial(partial)
        selected = dict(partial)
        preferred = preferred or {}
        for slot in self.slots:
            if slot.name in selected:
                continue
            preferred_value = preferred.get(slot.name)
            selected[slot.name] = (
                preferred_value if preferred_value in slot.values else slot.values[0]
            )
        return {slot.name: selected[slot.name] for slot in self.slots}

    def validate(self, values: Mapping[str, object], *, complete: bool = True) -> None:
        self._validate_partial(values)
        if complete and set(values) != set(self.slot_names):
            missing = sorted(set(self.slot_names) - set(values))
            raise TemplateDomainError(f"domain choice is missing slots: {', '.join(missing)}")

    def sample(self, seed: int | random.Random) -> dict[str, object]:
        rng = seed if isinstance(seed, random.Random) else random.Random(int(seed))
        return {slot.name: rng.choice(slot.values) for slot in self.slots}

    def audit(self) -> dict[str, object]:
        component_slots = tuple(slot for slot in self.slots if slot.kind == "component")
        core_domain = 1
        for slot in component_slots:
            core_domain *= len(slot.values)
        raw_domain = 1
        for slot in self.slots:
            raw_domain *= len(slot.values)
        return {
            "status": "declared",
            "core_domain": core_domain,
            "raw_domain": raw_domain,
            "component_slots": {slot.name: list(slot.values) for slot in component_slots},
            "multiplicity": {
                slot.name: {
                    "values": list(slot.values),
                    "minimum": min(slot.values),
                    "maximum": max(slot.values),
                    "item_slot": slot.item_slot or None,
                }
                for slot in self.slots
                if slot.kind == "multiplicity"
            },
        }

    def automatic_corners(self) -> tuple[CornerCase, ...]:
        baseline = self.complete({})
        cases: list[CornerCase] = []
        names: set[str] = set()

        def add(case: CornerCase) -> None:
            if case.name in names:
                raise TemplateDomainError(f"duplicate automatic corner name {case.name!r}")
            names.add(case.name)
            cases.append(case)

        for slot in self.slots:
            if slot.kind == "component":
                targets = slot.values
            else:
                targets = tuple(dict.fromkeys((min(slot.values), max(slot.values))))
            for value in targets:
                completed = self.complete({slot.name: value}, preferred=baseline)
                label = "candidate" if slot.kind == "component" else "edge"
                add(
                    corner_case(
                        f"{label}_{slot.name}_{value}",
                        completed,
                        reason=f"automatic {slot.kind} coverage for {slot.name}={value!r}",
                    )
                )

        return tuple(cases)


__all__ = [
    "CornerCase",
    "DomainSlot",
    "TemplateDomain",
    "TemplateDomainError",
    "component_slot",
    "corner_case",
    "multiplicity_slot",
]
