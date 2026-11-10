#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Compare mechanical snapshots across an appearance-only migration.

The projection in this module is deliberately independent from the SDK.  It
accepts either live SDK-shaped objects or JSON/dict snapshots and keeps only
the fields whose equality establishes that an appearance migration did not
change the generated mechanism. Material registries, visual materials, and
material-class selectors are intentionally absent from the projection.

Config comparison is opt-in in the opposite direction: callers must name the
exact appearance fields to remove.  No field-name heuristic is used, because a
field such as ``finish`` can affect geometry in one template and appearance in
another.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from numbers import Integral, Real
from pathlib import Path
from typing import Any

MECHANICAL_SNAPSHOT_VERSION = "appearance-mechanical-snapshot/v1"
CONFIG_SNAPSHOT_VERSION = "appearance-filtered-config/v1"

_MISSING = object()
_GENERIC_IGNORED_FIELDS = {
    "_articulation_index",
    "_part_index",
    "assets",
    "materialized_path",
}


class MechanicalSnapshotError(ValueError):
    """Raised when an input cannot be represented deterministically."""


@dataclass(frozen=True)
class InvarianceResult:
    """Result of a mechanical or filtered-config comparison."""

    invariant: bool
    before_sha256: str
    after_sha256: str
    differences: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "invariant": self.invariant,
            "before_sha256": self.before_sha256,
            "after_sha256": self.after_sha256,
            "differences": list(self.differences),
        }


def _read(value: Any, *names: str, default: Any = _MISSING) -> Any:
    for name in names:
        if isinstance(value, Mapping) and name in value:
            return value[name]
        if not isinstance(value, Mapping) and hasattr(value, name):
            return getattr(value, name)
    if default is not _MISSING:
        return default
    joined = ", ".join(repr(name) for name in names)
    raise MechanicalSnapshotError(f"required field missing; expected one of {joined}")


def _field_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return {str(key): child for key, child in value.items()}
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: getattr(value, item.name) for item in fields(value)}
    if hasattr(value, "__dict__"):
        return {
            str(key): child for key, child in vars(value).items() if not str(key).startswith("_")
        }
    raise MechanicalSnapshotError(
        f"expected a mapping, dataclass, or attribute object; got {type(value).__name__}"
    )


def _canonical(value: Any, *, ignored_fields: frozenset[str] = frozenset()) -> Any:
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Enum):
        return _canonical(value.value, ignored_fields=ignored_fields)
    if isinstance(value, Integral):
        return int(value)
    if isinstance(value, Real):
        number = float(value)
        if not math.isfinite(number):
            raise MechanicalSnapshotError(f"non-finite mechanical number: {number!r}")
        return 0.0 if number == 0.0 else number
    if isinstance(value, os.PathLike):
        return os.fspath(value)
    if isinstance(value, (bytes, bytearray)):
        return {"sha256": hashlib.sha256(bytes(value)).hexdigest(), "size": len(value)}
    if (
        isinstance(value, Mapping)
        or (is_dataclass(value) and not isinstance(value, type))
        or hasattr(value, "__dict__")
    ):
        result: dict[str, Any] = {}
        for key, child in sorted(_field_mapping(value).items()):
            if key in ignored_fields or key in _GENERIC_IGNORED_FIELDS:
                continue
            result[key] = _canonical(child, ignored_fields=ignored_fields)
        return result
    if isinstance(value, Sequence):
        return [_canonical(child, ignored_fields=ignored_fields) for child in value]
    if isinstance(value, (set, frozenset)):
        children = [_canonical(child, ignored_fields=ignored_fields) for child in value]
        return sorted(children, key=_canonical_json)
    raise MechanicalSnapshotError(f"unsupported value type: {type(value).__name__}")


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _origin_snapshot(origin: Any) -> dict[str, Any]:
    if origin is None:
        origin = {}
    return {
        "xyz": _canonical(_read(origin, "xyz", default=(0.0, 0.0, 0.0))),
        "rpy": _canonical(_read(origin, "rpy", default=(0.0, 0.0, 0.0))),
    }


def _geometry_kind(geometry: Any) -> str:
    explicit = _read(geometry, "kind", "type", "geometry_type", default=None)
    if explicit is not None:
        text = str(explicit).rsplit(".", 1)[-1].lower()
    elif not isinstance(geometry, Mapping):
        text = type(geometry).__name__.lower()
    else:
        keys = set(str(key) for key in geometry)
        if "size" in keys:
            text = "box"
        elif {"radius", "length"} <= keys or {"radius", "height"} <= keys:
            text = "cylinder"
        elif "radius" in keys:
            text = "sphere"
        elif keys & {"filename", "source_geometry", "source_transform", "scale"}:
            text = "mesh"
        else:
            text = "mapping"
    aliases = {
        "boxgeometry": "box",
        "cylindergeometry": "cylinder",
        "meshgeometry": "mesh",
        "spheregeometry": "sphere",
    }
    return aliases.get(text, text)


def _geometry_snapshot(geometry: Any) -> dict[str, Any]:
    kind = _geometry_kind(geometry)
    if kind == "box":
        return {"kind": kind, "size": _canonical(_read(geometry, "size"))}
    if kind == "cylinder":
        return {
            "kind": kind,
            "radius": _canonical(_read(geometry, "radius")),
            "length": _canonical(_read(geometry, "length", "height")),
        }
    if kind == "sphere":
        return {"kind": kind, "radius": _canonical(_read(geometry, "radius"))}
    if kind == "mesh":
        return {
            "kind": kind,
            "filename": _canonical(_read(geometry, "filename", default=None)),
            "name": _canonical(_read(geometry, "name", default=None)),
            "scale": _canonical(_read(geometry, "scale", default=None)),
            "source_geometry": (
                _geometry_snapshot(source)
                if (source := _read(geometry, "source_geometry", default=None)) is not None
                else None
            ),
            "source_transform": _canonical(_read(geometry, "source_transform", default=None)),
        }
    payload = _canonical(geometry, ignored_fields=frozenset({"kind", "type", "geometry_type"}))
    return {"kind": kind, "payload": payload}


def _visual_snapshot(visual: Any) -> dict[str, Any]:
    # Only select mechanical/geometry fields.  In particular, do not traverse
    # visual appearance selectors, even if one contains geometry-like data.
    return {
        "name": _canonical(_read(visual, "name", default=None)),
        "geometry": _geometry_snapshot(_read(visual, "geometry")),
        "origin": _origin_snapshot(_read(visual, "origin", default=None)),
    }


def _collision_snapshot(collision: Any) -> dict[str, Any]:
    return {
        "name": _canonical(_read(collision, "name", default=None)),
        "geometry": _geometry_snapshot(_read(collision, "geometry")),
        "origin": _origin_snapshot(_read(collision, "origin", default=None)),
    }


def _inertial_snapshot(inertial: Any) -> dict[str, Any] | None:
    if inertial is None:
        return None
    return {
        "mass": _canonical(_read(inertial, "mass")),
        "inertia": _canonical(_read(inertial, "inertia")),
        "origin": _origin_snapshot(_read(inertial, "origin", default=None)),
    }


def _part_snapshot(part: Any) -> dict[str, Any]:
    return {
        "name": str(_read(part, "name")),
        "visuals": [_visual_snapshot(visual) for visual in _read(part, "visuals", default=())],
        "collisions": [
            _collision_snapshot(collision) for collision in _read(part, "collisions", default=())
        ],
        "inertial": _inertial_snapshot(_read(part, "inertial", default=None)),
        "meta": _canonical(_read(part, "meta", default={})),
    }


def _joint_snapshot(joint: Any) -> dict[str, Any]:
    return {
        "name": str(_read(joint, "name")),
        "joint_type": _canonical(_read(joint, "articulation_type", "joint_type", "type")),
        "parent": str(_read(joint, "parent")),
        "child": str(_read(joint, "child")),
        "origin": _origin_snapshot(_read(joint, "origin", default=None)),
        "axis": _canonical(_read(joint, "axis", default=(0.0, 0.0, 1.0))),
        "motion_limits": _canonical(_read(joint, "motion_limits", "limit", default=None)),
        "motion_properties": _canonical(
            _read(joint, "motion_properties", "dynamics", default=None)
        ),
        "mimic": _canonical(_read(joint, "mimic", default=None)),
        "mating": _canonical(_read(joint, "mating", default=None)),
        "meta": _canonical(_read(joint, "meta", default={})),
    }


def object_model_mechanical_snapshot(model: Any) -> dict[str, Any]:
    """Return the material-free mechanical projection of an object model."""

    return {
        "schema_version": MECHANICAL_SNAPSHOT_VERSION,
        "name": str(_read(model, "name", default="")),
        "parts": [_part_snapshot(part) for part in _read(model, "parts", "links")],
        "joints": [
            _joint_snapshot(joint) for joint in _read(model, "articulations", "joints", default=())
        ],
    }


def object_model_mechanical_fingerprint(model: Any) -> str:
    return _sha256(object_model_mechanical_snapshot(model))


def _drop_path(root: dict[str, Any], path: tuple[str, ...]) -> None:
    if not path or path[0] not in root:
        return
    if len(path) == 1:
        root.pop(path[0], None)
        return
    child = root.get(path[0])
    if not isinstance(child, dict):
        return
    _drop_path(child, path[1:])
    if not child:
        root.pop(path[0], None)


def _appearance_paths(appearance_fields: Sequence[str]) -> tuple[tuple[str, ...], ...]:
    paths: list[tuple[str, ...]] = []
    for raw in appearance_fields:
        path = tuple(part.strip() for part in str(raw).split("."))
        if not path or any(not part for part in path):
            raise MechanicalSnapshotError(f"invalid appearance field path: {raw!r}")
        paths.append(path)
    return tuple(sorted(set(paths)))


def config_mechanical_snapshot(
    config: Any, *, appearance_fields: Sequence[str] = ()
) -> dict[str, Any]:
    """Project a Config after removing only explicitly named appearance fields."""

    projected = _canonical(_field_mapping(config))
    if not isinstance(projected, dict):  # Defensive; _field_mapping always yields a dict.
        raise MechanicalSnapshotError("config projection is not a mapping")
    paths = _appearance_paths(appearance_fields)
    for path in paths:
        _drop_path(projected, path)
    return {
        "schema_version": CONFIG_SNAPSHOT_VERSION,
        "excluded_appearance_fields": [".".join(path) for path in paths],
        "config": projected,
    }


def config_mechanical_fingerprint(config: Any, *, appearance_fields: Sequence[str] = ()) -> str:
    return _sha256(config_mechanical_snapshot(config, appearance_fields=appearance_fields))


def _differences(before: Any, after: Any, *, limit: int) -> tuple[str, ...]:
    found: list[str] = []

    def visit(left: Any, right: Any, path: str) -> None:
        if len(found) >= limit:
            return
        if isinstance(left, dict) and isinstance(right, dict):
            for key in sorted(set(left) | set(right)):
                child_path = f"{path}.{key}"
                if key not in left:
                    found.append(f"{child_path}: added {right[key]!r}")
                elif key not in right:
                    found.append(f"{child_path}: removed {left[key]!r}")
                else:
                    visit(left[key], right[key], child_path)
                if len(found) >= limit:
                    return
            return
        if isinstance(left, list) and isinstance(right, list):
            if len(left) != len(right):
                found.append(f"{path}: length {len(left)} != {len(right)}")
                if len(found) >= limit:
                    return
            for index, (left_child, right_child) in enumerate(zip(left, right, strict=False)):
                visit(left_child, right_child, f"{path}[{index}]")
                if len(found) >= limit:
                    return
            return
        if left != right:
            found.append(f"{path}: {left!r} != {right!r}")

    visit(before, after, "$")
    return tuple(found)


def _compare(
    before: dict[str, Any], after: dict[str, Any], *, max_differences: int
) -> InvarianceResult:
    if max_differences < 1:
        raise ValueError("max_differences must be >= 1")
    differences = _differences(before, after, limit=max_differences)
    return InvarianceResult(
        invariant=not differences,
        before_sha256=_sha256(before),
        after_sha256=_sha256(after),
        differences=differences,
    )


def compare_object_models(
    before: Any, after: Any, *, max_differences: int = 50
) -> InvarianceResult:
    return _compare(
        object_model_mechanical_snapshot(before),
        object_model_mechanical_snapshot(after),
        max_differences=max_differences,
    )


def compare_configs(
    before: Any,
    after: Any,
    *,
    appearance_fields: Sequence[str] = (),
    max_differences: int = 50,
) -> InvarianceResult:
    return _compare(
        config_mechanical_snapshot(before, appearance_fields=appearance_fields),
        config_mechanical_snapshot(after, appearance_fields=appearance_fields),
        max_differences=max_differences,
    )


def _workspace_json(path: Path) -> Any:
    workspace = Path.cwd().resolve()
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(workspace)
    except ValueError as exc:
        raise MechanicalSnapshotError(
            f"input path is outside the current workspace: {resolved}"
        ) from exc
    return json.loads(resolved.read_text(encoding="utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path, help="Pre-migration JSON snapshot.")
    parser.add_argument("after", type=Path, help="Post-migration JSON snapshot.")
    parser.add_argument(
        "--kind",
        choices=("object-model", "config"),
        default="object-model",
    )
    parser.add_argument(
        "--appearance-field",
        action="append",
        default=[],
        help="Exact Config field or dotted field path to exclude; repeat as needed.",
    )
    parser.add_argument("--max-differences", type=int, default=50)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    before = _workspace_json(args.before)
    after = _workspace_json(args.after)
    if args.kind == "config":
        result = compare_configs(
            before,
            after,
            appearance_fields=args.appearance_field,
            max_differences=args.max_differences,
        )
    else:
        result = compare_object_models(
            before,
            after,
            max_differences=args.max_differences,
        )
    print(json.dumps(result.to_dict(), ensure_ascii=False, sort_keys=True))
    return 0 if result.invariant else 1


if __name__ == "__main__":
    raise SystemExit(main())
