# SPDX-License-Identifier: Apache-2.0

"""Semantic surface selectors shared by editing, highlighting, and export."""

from __future__ import annotations

import fnmatch
from collections.abc import Sequence
from typing import Any

_SCOPES = frozenset({"part", "visual", "surface", "builder", "class"})


def surface_key(part_name: str, visual_name: str) -> str:
    return f"{part_name}/{visual_name}"


def _selector(raw: str) -> tuple[str | None, str]:
    value = str(raw).strip().lower()
    scope: str | None = None
    prefix, separator, remainder = value.partition(":")
    if separator and prefix in _SCOPES:
        scope, value = prefix, remainder.strip()
    if value and not any(character in value for character in "*?["):
        value = f"*{value}*"
    return scope, value


def part_selectors(patterns: Sequence[str]) -> tuple[str, ...]:
    output: list[str] = []
    for pattern in patterns:
        prefix = str(pattern).split(":", 1)[0].strip().lower()
        output.append(str(pattern) if prefix in _SCOPES else f"part:{pattern}")
    return tuple(output)


def matches_surface(
    patterns: Sequence[str] | str,
    *,
    part_name: str,
    visual_name: str,
    visual: Any,
) -> bool:
    if isinstance(patterns, str):
        patterns = (patterns,)
    candidates = {
        "part": str(part_name).lower(),
        "visual": str(visual_name).lower(),
        "surface": surface_key(part_name, visual_name).lower(),
        "builder": str(getattr(visual, "builder", "") or "").lower(),
        "class": str(getattr(visual, "material_class_id", "") or "").lower(),
    }
    for raw in patterns:
        scope, pattern = _selector(str(raw))
        if not pattern:
            continue
        values = candidates.values() if scope is None else (candidates[scope],)
        if any(fnmatch.fnmatchcase(value, pattern) for value in values):
            return True
    return False


def matching_surface_keys(model: Any, patterns: Sequence[str] | str) -> tuple[str, ...]:
    matches: list[str] = []
    for part in getattr(model, "parts", ()):  # SDK object, kept duck-typed for small probes.
        part_name = str(getattr(part, "name", "part"))
        for index, visual in enumerate(getattr(part, "visuals", ())):
            visual_name = str(getattr(visual, "name", None) or f"visual_{index:03d}")
            if matches_surface(
                patterns,
                part_name=part_name,
                visual_name=visual_name,
                visual=visual,
            ):
                matches.append(surface_key(part_name, visual_name))
    return tuple(matches)


def part_names_from_surfaces(surfaces: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(surface.partition("/")[0] for surface in surfaces))


__all__ = [
    "matches_surface",
    "matching_surface_keys",
    "part_names_from_surfaces",
    "part_selectors",
    "surface_key",
]
