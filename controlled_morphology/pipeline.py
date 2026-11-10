# SPDX-License-Identifier: Apache-2.0

"""JSON-driven one-axis-at-a-time controlled morphology pipeline."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import os
import re
import shutil
import sys
import tempfile
import traceback
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from agent.compiler import compile_urdf_report_maybe_timeout
from controlled_morphology import __version__
from controlled_morphology.physics import build_physics_payload
from controlled_morphology.registry import (
    GeneratorRegistration,
    RegistryError,
    get_generator,
    list_generators,
)

SCHEMA_VERSION = 1
_SAFE_ID_RE = re.compile(r"[^a-zA-Z0-9_.-]+")
_METADATA_KEYS = (
    "target_joint",
    "target_link",
    "joint_type",
    "axis",
    "limits",
    "opening_sign",
    "opening_endpoint",
    "handle_frame",
    "front_axis",
    "up_axis",
)


class PipelineError(ValueError):
    """Raised for invalid specs, unsafe output requests, or inconsistent metadata."""


@dataclass(frozen=True, slots=True)
class AxisSpec:
    name: str
    levels: tuple[Any, ...]


@dataclass(frozen=True, slots=True)
class NuisanceBlock:
    block_id: str
    overrides: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ExperimentSpec:
    source_path: Path
    name: str
    generator_id: str
    base_config: dict[str, Any]
    axes: tuple[AxisSpec, ...]
    nuisance_blocks: tuple[NuisanceBlock, ...]
    raw: dict[str, Any]


@dataclass(frozen=True, slots=True)
class PlannedAsset:
    asset_id: str
    axis_name: str
    axis_index: int
    level: Any
    nuisance: NuisanceBlock
    requested_overrides: dict[str, Any]
    requested_config: dict[str, Any]
    resolved_config: dict[str, Any]
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class PipelineResult:
    output_root: Path
    manifest_path: Path
    assets_total: int
    assets_passed: int
    assets_failed: int

    @property
    def ok(self) -> bool:
        return self.assets_failed == 0


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {
            field.name: _jsonable(getattr(value, field.name)) for field in dataclasses.fields(value)
        }
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, "value"):
        return _jsonable(value.value)
    raise PipelineError(f"Value is not JSON serializable: {value!r}")


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        _jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    ).encode("utf-8")


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True, ensure_ascii=True, allow_nan=False)
        + "\n",
        encoding="utf-8",
    )


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _safe_id(value: str, *, fallback: str) -> str:
    cleaned = _SAFE_ID_RE.sub("-", value.strip()).strip("-._")
    return (cleaned or fallback)[:64]


def _level_id(value: Any) -> str:
    if isinstance(value, bool):
        label = "true" if value else "false"
    elif isinstance(value, float):
        label = format(value, ".8g")
    elif isinstance(value, (int, str)):
        label = str(value)
    else:
        label = _sha256_bytes(_canonical_json_bytes(value))[:10]
    return _safe_id(label, fallback="value")


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise PipelineError(f"{label} must be a JSON object with string keys")
    return dict(value)


def _parse_axes(value: Any) -> tuple[AxisSpec, ...]:
    entries: list[AxisSpec] = []
    if isinstance(value, dict):
        iterable: Iterable[tuple[Any, Any]] = value.items()
        for name, levels in iterable:
            if not isinstance(name, str):
                raise PipelineError("axes keys must be strings")
            if not isinstance(levels, list) or not levels:
                raise PipelineError(f"axes.{name} must be a non-empty JSON array")
            entries.append(AxisSpec(name=name, levels=tuple(levels)))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            entry = _require_mapping(item, f"axes[{index}]")
            name = entry.get("name")
            levels = entry.get("levels")
            if not isinstance(name, str) or not name.strip():
                raise PipelineError(f"axes[{index}].name must be a non-empty string")
            if not isinstance(levels, list) or not levels:
                raise PipelineError(f"axes[{index}].levels must be a non-empty JSON array")
            entries.append(AxisSpec(name=name, levels=tuple(levels)))
    else:
        raise PipelineError("axes must be an object or an array")
    if not entries:
        raise PipelineError("axes must contain at least one controlled axis")
    names = [entry.name for entry in entries]
    if len(names) != len(set(names)):
        raise PipelineError("controlled axis names must be unique")
    return tuple(entries)


def _parse_nuisance_blocks(value: Any) -> tuple[NuisanceBlock, ...]:
    if value is None:
        return (NuisanceBlock(block_id="fixed", overrides={}),)
    if not isinstance(value, list) or not value:
        raise PipelineError("nuisance_blocks must be a non-empty JSON array")
    blocks: list[NuisanceBlock] = []
    for index, item in enumerate(value):
        entry = _require_mapping(item, f"nuisance_blocks[{index}]")
        raw_id = entry.pop("id", f"n{index:02d}")
        if not isinstance(raw_id, str) or not raw_id.strip():
            raise PipelineError(f"nuisance_blocks[{index}].id must be a non-empty string")
        if "overrides" in entry:
            if set(entry) != {"overrides"}:
                raise PipelineError(
                    f"nuisance_blocks[{index}] cannot mix overrides with direct fields"
                )
            overrides = _require_mapping(entry["overrides"], f"nuisance_blocks[{index}].overrides")
        else:
            overrides = entry
        blocks.append(NuisanceBlock(block_id=raw_id, overrides=overrides))
    ids = [block.block_id for block in blocks]
    if len(ids) != len(set(ids)):
        raise PipelineError("nuisance block ids must be unique")
    return tuple(blocks)


def load_spec(path: str | Path) -> ExperimentSpec:
    """Load and structurally validate one JSON experiment spec."""

    source_path = Path(path).expanduser().resolve()
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PipelineError(f"Spec does not exist: {source_path}") from exc
    except json.JSONDecodeError as exc:
        raise PipelineError(f"Invalid JSON in {source_path}: {exc}") from exc
    raw = _require_mapping(payload, "spec")
    schema_version = raw.get("schema_version", SCHEMA_VERSION)
    if schema_version != SCHEMA_VERSION:
        raise PipelineError(
            f"Unsupported schema_version {schema_version!r}; expected {SCHEMA_VERSION}"
        )
    name = raw.get("name")
    generator_id = raw.get("generator")
    if not isinstance(name, str) or not name.strip():
        raise PipelineError("spec.name must be a non-empty string")
    if not isinstance(generator_id, str) or not generator_id.strip():
        raise PipelineError("spec.generator must be a non-empty string")
    base_config = _require_mapping(raw.get("base_config"), "base_config")
    axes = _parse_axes(raw.get("axes"))
    nuisance_blocks = _parse_nuisance_blocks(raw.get("nuisance_blocks"))
    controlled_names = {axis.name for axis in axes}
    for block in nuisance_blocks:
        overlap = sorted(controlled_names & set(block.overrides))
        if overlap:
            raise PipelineError(
                f"Nuisance block {block.block_id!r} overrides controlled axis: {', '.join(overlap)}"
            )
    return ExperimentSpec(
        source_path=source_path,
        name=name,
        generator_id=generator_id,
        base_config=base_config,
        axes=axes,
        nuisance_blocks=nuisance_blocks,
        raw=raw,
    )


def _values_equal(requested: Any, resolved: Any) -> bool:
    if isinstance(requested, bool) or isinstance(resolved, bool):
        return requested is resolved
    if isinstance(requested, (int, float)) and isinstance(resolved, (int, float)):
        return math.isclose(float(requested), float(resolved), rel_tol=1e-9, abs_tol=1e-12)
    return requested == resolved


def _validate_controlled_resolution(
    *, asset_label: str, axis_name: str, requested_level: Any, resolved_config: dict[str, Any]
) -> None:
    if axis_name not in resolved_config:
        raise PipelineError(
            f"{asset_label}: controlled axis {axis_name!r} is absent from ResolvedConfig"
        )
    resolved_level = resolved_config[axis_name]
    if not _values_equal(requested_level, resolved_level):
        raise PipelineError(
            f"{asset_label}: controlled axis {axis_name!r} was silently changed by resolve_config "
            f"from {requested_level!r} to {resolved_level!r}"
        )


def _finite_vector(value: Any, *, label: str) -> list[float]:
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise PipelineError(f"{label} must be a 3-vector")
    vector = [float(item) for item in value]
    if not all(math.isfinite(item) for item in vector):
        raise PipelineError(f"{label} must contain only finite values")
    return vector


def _metadata_articulations(metadata: dict[str, Any], *, label: str) -> list[dict[str, Any]]:
    if "articulations" not in metadata:
        return [metadata]
    raw = metadata["articulations"]
    if not isinstance(raw, list) or not raw:
        raise PipelineError(f"{label}: benchmark articulations must be a non-empty array")
    declarations: list[dict[str, Any]] = []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            raise PipelineError(f"{label}: benchmark articulations[{index}] must be an object")
        declarations.append(item)
    return declarations


def _validate_articulation_metadata(articulation: dict[str, Any], *, label: str) -> None:
    required = {
        "target_joint",
        "target_link",
        "joint_type",
        "axis",
        "limits",
        "opening_sign",
        "opening_endpoint",
        "handle_frame",
    }
    missing = sorted(required - set(articulation))
    if missing:
        raise PipelineError(f"{label}: missing fields: {', '.join(missing)}")
    for key in ("target_joint", "target_link", "joint_type"):
        if not isinstance(articulation.get(key), str) or not articulation[key]:
            raise PipelineError(f"{label}: {key} must be a non-empty string")
    if articulation["joint_type"] not in {"revolute", "prismatic"}:
        raise PipelineError(f"{label}: joint_type must be revolute or prismatic")
    _finite_vector(articulation.get("axis"), label=f"{label}: axis")
    if "joint_origin" in articulation:
        _finite_vector(articulation["joint_origin"], label=f"{label}: joint_origin")
    limits = articulation.get("limits")
    if not isinstance(limits, dict) or not {"lower", "upper"} <= set(limits):
        raise PipelineError(f"{label}: limits must contain lower and upper")
    lower = float(limits["lower"])
    upper = float(limits["upper"])
    endpoint = float(articulation.get("opening_endpoint"))
    opening_sign = float(articulation.get("opening_sign"))
    if not all(math.isfinite(item) for item in (lower, upper, endpoint, opening_sign)):
        raise PipelineError(f"{label}: limits and opening values must be finite")
    if lower > upper:
        raise PipelineError(f"{label}: lower limit exceeds upper limit")
    if endpoint < lower - 1e-10 or endpoint > upper + 1e-10:
        raise PipelineError(f"{label}: opening_endpoint is outside limits")
    if opening_sign == 0.0 or endpoint * opening_sign <= 0.0:
        raise PipelineError(f"{label}: opening_sign must match the non-zero opening_endpoint")
    handle_frame = articulation.get("handle_frame")
    if not isinstance(handle_frame, dict):
        raise PipelineError(f"{label}: handle_frame must be an object")
    for candidates in (("xyz", "origin_xyz"), ("rpy", "orientation_rpy")):
        key = next((candidate for candidate in candidates if candidate in handle_frame), None)
        if key is None:
            choices = " or ".join(candidates)
            raise PipelineError(f"{label}: benchmark handle_frame needs {choices}")
        _finite_vector(handle_frame[key], label=f"{label}: handle_frame.{key}")
    for key in ("approach_axis", "grip_axis"):
        _finite_vector(handle_frame.get(key), label=f"{label}: handle_frame.{key}")


def _validate_metadata_contract(metadata: dict[str, Any], *, label: str) -> None:
    _finite_vector(metadata.get("front_axis"), label=f"{label}: benchmark front_axis")
    _finite_vector(metadata.get("up_axis"), label=f"{label}: benchmark up_axis")
    declarations = _metadata_articulations(metadata, label=label)
    for index, articulation in enumerate(declarations):
        _validate_articulation_metadata(
            articulation,
            label=(
                label if "articulations" not in metadata else f"{label}: articulations[{index}]"
            ),
        )
    joint_names = [str(item["target_joint"]) for item in declarations]
    if len(joint_names) != len(set(joint_names)):
        raise PipelineError(f"{label}: benchmark articulations contain duplicate target joints")
    if "articulations" in metadata and metadata.get("target_joint") not in set(joint_names):
        raise PipelineError(
            f"{label}: legacy primary target_joint must refer to a declared articulation"
        )


def plan_assets(spec: ExperimentSpec) -> tuple[PlannedAsset, ...]:
    """Resolve all OAT cells and return a deterministic generation plan."""

    registration = get_generator(spec.generator_id)
    registration.validate_contract()
    variables = registration.variable_space()["variables"]
    for axis in spec.axes:
        if axis.name not in variables:
            raise PipelineError(
                f"Controlled axis {axis.name!r} is not declared by generator {spec.generator_id!r}"
            )
        level_keys = [_canonical_json_bytes(level) for level in axis.levels]
        if len(level_keys) != len(set(level_keys)):
            raise PipelineError(f"Controlled axis {axis.name!r} contains duplicate levels")
    plans: list[PlannedAsset] = []
    for nuisance in spec.nuisance_blocks:
        nuisance_id = _safe_id(nuisance.block_id, fallback="nuisance")
        for axis in spec.axes:
            for level_index, level in enumerate(axis.levels):
                requested_overrides = dict(spec.base_config)
                requested_overrides.update(nuisance.overrides)
                requested_overrides[axis.name] = level
                config = registration.make_config(requested_overrides)
                requested_config = _jsonable(config)
                resolved_config = _jsonable(registration.resolve_config(config))
                _validate_controlled_resolution(
                    asset_label=f"{axis.name}[{level_index}]/{nuisance.block_id}",
                    axis_name=axis.name,
                    requested_level=level,
                    resolved_config=resolved_config,
                )
                metadata = _jsonable(registration.benchmark_metadata(config))
                _validate_metadata_contract(
                    metadata,
                    label=f"{axis.name}[{level_index}]/{nuisance.block_id}",
                )
                identity = {
                    "experiment": spec.name,
                    "generator": spec.generator_id,
                    "axis": axis.name,
                    "axis_index": level_index,
                    "level": level,
                    "nuisance_id": nuisance.block_id,
                    "nuisance": nuisance.overrides,
                    "requested_config": requested_config,
                }
                digest = _sha256_bytes(_canonical_json_bytes(identity))[:10]
                asset_id = f"l{level_index:02d}-{_level_id(level)}__{nuisance_id}__{digest}"
                plans.append(
                    PlannedAsset(
                        asset_id=asset_id,
                        axis_name=axis.name,
                        axis_index=level_index,
                        level=_jsonable(level),
                        nuisance=nuisance,
                        requested_overrides=_jsonable(requested_overrides),
                        requested_config=requested_config,
                        resolved_config=resolved_config,
                        metadata=metadata,
                    )
                )
    ids = [plan.asset_id for plan in plans]
    if len(ids) != len(set(ids)):
        raise PipelineError("Stable asset id collision; rename duplicate axes or nuisance blocks")
    return tuple(plans)


def validate_spec(path: str | Path) -> tuple[ExperimentSpec, tuple[PlannedAsset, ...]]:
    """Validate generator fields, resolution, metadata, and expected asset count."""

    spec = load_spec(path)
    plans = plan_assets(spec)
    expected = sum(len(axis.levels) for axis in spec.axes) * len(spec.nuisance_blocks)
    if len(plans) != expected:
        raise PipelineError(f"Plan count mismatch: expected {expected}, got {len(plans)}")
    return spec, plans


_MODEL_TEMPLATE = """from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from sdk import AssetContext

_GENERATOR_PATH = Path(__file__).with_name("generator.py")
_SPEC = importlib.util.spec_from_file_location("_controlled_generator_snapshot", _GENERATOR_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise ImportError(f"Cannot load generator snapshot: {{_GENERATOR_PATH}}")
_generator = importlib.util.module_from_spec(_SPEC)
sys.modules[_SPEC.name] = _generator
_SPEC.loader.exec_module(_generator)

CONFIG_PAYLOAD = json.loads({config_json!r})
CONFIG = _generator.Config(**CONFIG_PAYLOAD)
ASSETS = AssetContext.from_script(__file__)


def build_object_model():
    return _generator.{build_function}(CONFIG, assets=ASSETS)


def run_tests():
    return _generator.{test_function}(object_model, CONFIG)


object_model = build_object_model()
"""


def _render_model_source(
    registration: GeneratorRegistration, requested_config: dict[str, Any]
) -> str:
    config_json = json.dumps(
        requested_config, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
    )
    return _MODEL_TEMPLATE.format(
        config_json=config_json,
        build_function=registration.build_function,
        test_function=registration.test_function,
    )


def _compile_report_success(report: Any, *, motion_qc: bool) -> dict[str, Any]:
    motion_report = _jsonable(report.motion_qc_report)
    if motion_qc and (not isinstance(motion_report, dict) or motion_report.get("status") != "pass"):
        raise PipelineError("motion QC did not return an actual-execution pass report")
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "pass",
        "compiler": {
            "sdk_package": "sdk",
            "target": "full",
            "run_checks": True,
            "authored_tests_enabled": True,
            "baseline_tests_enabled": True,
        },
        "warnings": [str(item) for item in report.warnings],
        "signal_bundle": report.signal_bundle.to_dict(),
        "motion_qc_enabled": motion_qc,
        "motion_qc": motion_report,
    }


def _compile_report_failure(exc: BaseException, *, motion_qc: bool) -> dict[str, Any]:
    bundle = getattr(exc, "compile_signal_bundle", None)
    bundle_payload = bundle.to_dict() if hasattr(bundle, "to_dict") else None
    motion_report = getattr(exc, "motion_qc_report", None)
    warnings = getattr(exc, "warnings", ()) or ()
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "fail",
        "compiler": {
            "sdk_package": "sdk",
            "target": "full",
            "run_checks": True,
            "authored_tests_enabled": True,
            "baseline_tests_enabled": True,
        },
        "error_type": type(exc).__name__,
        "error": str(exc),
        "warnings": [str(item) for item in warnings],
        "signal_bundle": bundle_payload,
        "motion_qc_enabled": motion_qc,
        "motion_qc": _jsonable(motion_report),
        "traceback": traceback.format_exc(limit=30),
    }


def _float_vector(raw: str) -> list[float]:
    return [float(item) for item in raw.split()]


def _verify_urdf_articulation(
    *,
    joint_element: ET.Element,
    link_names: set[str | None],
    articulation: dict[str, Any],
) -> None:
    target_joint = str(articulation["target_joint"])
    target_link = str(articulation["target_link"])
    if target_link not in link_names:
        raise PipelineError(f"benchmark target_link is absent from URDF: {target_link}")
    actual_type = joint_element.get("type")
    if actual_type != articulation["joint_type"]:
        raise PipelineError(
            f"joint type metadata mismatch for {target_joint}: "
            f"{articulation['joint_type']!r} != {actual_type!r}"
        )
    child = joint_element.find("child")
    if child is None or child.get("link") != target_link:
        raise PipelineError(f"target_joint {target_joint} does not move target_link {target_link}")
    axis_element = joint_element.find("axis")
    if axis_element is None or not axis_element.get("xyz"):
        raise PipelineError(f"target_joint {target_joint} has no URDF axis")
    actual_axis = _float_vector(str(axis_element.get("xyz")))
    expected_axis = [float(item) for item in articulation["axis"]]
    if len(actual_axis) != len(expected_axis) or any(
        not math.isclose(a, b, rel_tol=1e-8, abs_tol=1e-10)
        for a, b in zip(actual_axis, expected_axis)
    ):
        raise PipelineError(
            f"joint axis metadata mismatch for {target_joint}: {expected_axis} != {actual_axis}"
        )
    if "joint_origin" in articulation:
        origin_element = joint_element.find("origin")
        actual_origin = (
            [0.0, 0.0, 0.0]
            if origin_element is None or not origin_element.get("xyz")
            else _float_vector(str(origin_element.get("xyz")))
        )
        expected_origin = [float(item) for item in articulation["joint_origin"]]
        if len(actual_origin) != len(expected_origin) or any(
            not math.isclose(a, b, rel_tol=1e-8, abs_tol=1e-6)
            for a, b in zip(actual_origin, expected_origin)
        ):
            raise PipelineError(
                f"joint origin metadata mismatch for {target_joint}: "
                f"{expected_origin} != {actual_origin}"
            )
    limit_element = joint_element.find("limit")
    limits = articulation["limits"]
    if not isinstance(limits, dict) or not {"lower", "upper"} <= set(limits):
        raise PipelineError("benchmark limits must contain lower and upper")
    if limit_element is None:
        raise PipelineError(f"target_joint {target_joint} has no URDF limits")
    for key in ("lower", "upper"):
        expected = float(limits[key])
        actual = float(str(limit_element.get(key)))
        if not math.isclose(expected, actual, rel_tol=1e-8, abs_tol=1e-5):
            raise PipelineError(
                f"joint {key} metadata mismatch for {target_joint}: {expected} != {actual}"
            )
    endpoint = float(articulation["opening_endpoint"])
    if endpoint < float(limits["lower"]) - 1e-10 or endpoint > float(limits["upper"]) + 1e-10:
        raise PipelineError(f"opening_endpoint {endpoint} is outside target joint limits")


def _verify_urdf_metadata(urdf_xml: str, metadata: dict[str, Any]) -> None:
    try:
        root = ET.fromstring(urdf_xml)
    except ET.ParseError as exc:
        raise PipelineError(f"Compiler returned invalid URDF XML: {exc}") from exc
    declarations = _metadata_articulations(metadata, label="benchmark metadata")
    declared_names = [str(item["target_joint"]) for item in declarations]
    movable_joints = [
        element for element in root.findall("joint") if element.get("type") != "fixed"
    ]
    actual_by_name = {str(element.get("name")): element for element in movable_joints}
    declared_set = set(declared_names)
    actual_set = set(actual_by_name)
    if len(actual_by_name) != len(movable_joints):
        raise PipelineError("URDF contains duplicate movable joint names")
    if declared_set != actual_set:
        missing = sorted(declared_set - actual_set)
        unexpected = sorted(actual_set - declared_set)
        raise PipelineError(
            "URDF movable joints do not match benchmark declarations: "
            f"missing={missing}, unexpected={unexpected}"
        )
    link_names = {element.get("name") for element in root.findall("link")}
    for articulation in declarations:
        target_joint = str(articulation["target_joint"])
        _verify_urdf_articulation(
            joint_element=actual_by_name[target_joint],
            link_names=link_names,
            articulation=articulation,
        )


def _base_parameters(
    *,
    spec: ExperimentSpec,
    plan: PlannedAsset,
    registration: GeneratorRegistration,
    generator_sha256: str,
    spec_sha256: str,
) -> dict[str, Any]:
    variable_space = registration.variable_space()
    variable_descriptor = variable_space["variables"].get(plan.axis_name)
    resolved_level = plan.resolved_config[plan.axis_name]
    config_sha256 = _sha256_bytes(_canonical_json_bytes(plan.resolved_config))
    parameters = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_version": __version__,
        "asset_id": plan.asset_id,
        "experiment": spec.name,
        "spec": {
            "path": str(spec.source_path),
            "snapshot_path": "../../../experiment_spec.json",
            "sha256": spec_sha256,
        },
        "generator": {
            "id": registration.generator_id,
            "path": f"controlled_morphology/generators/{registration.source_filename}",
            "snapshot_path": "generator.py",
            "sha256": generator_sha256,
            "version": registration.version,
            "provenance": {
                "upstream_template_path": (
                    f"agent/templates/{registration.upstream_template_filename}"
                ),
                "upstream_template_sha256": registration.upstream_template_sha256(),
                "upstream_generator_id": registration.upstream_generator_id,
                "asset_category": registration.asset_category,
                "task_variant": registration.generator_id,
            },
        },
        "variable_space": {
            "snapshot_path": "../../../variable_space.json",
            "schema_version": variable_space["schema_version"],
        },
        "base_config": spec.base_config,
        "nuisance_block": {
            "id": plan.nuisance.block_id,
            "overrides": plan.nuisance.overrides,
        },
        "override": {plan.axis_name: plan.level},
        "controlled_axis": plan.axis_name,
        "controlled_axis_index": plan.axis_index,
        "controlled_level": plan.level,
        "intervention": {
            "variable": plan.axis_name,
            "requested_value": plan.level,
            "resolved_value": resolved_level,
            "descriptor": variable_descriptor,
        },
        "requested_overrides": plan.requested_overrides,
        "requested_config": plan.requested_config,
        "resolved_config": plan.resolved_config,
        "resolved_config_sha256": config_sha256,
        "urdf_sha256": None,
        "status": "pending",
    }
    for key in _METADATA_KEYS:
        parameters[key] = plan.metadata[key]
    for key, value in plan.metadata.items():
        if key not in parameters:
            parameters[key] = value
    return parameters


def _safe_remove_asset_dir(path: Path, assets_root: Path) -> None:
    resolved = path.resolve()
    resolved_root = assets_root.resolve()
    if resolved.parent != resolved_root or not resolved.name or resolved.name.startswith("."):
        raise PipelineError(f"Refusing to remove non-asset path: {resolved}")
    shutil.rmtree(resolved)


def _axis_assets_root(assets_root: Path, axis_name: str) -> Path:
    return assets_root / _safe_id(axis_name, fallback="axis")


def _asset_destination(assets_root: Path, plan: PlannedAsset) -> Path:
    return _axis_assets_root(assets_root, plan.axis_name) / plan.asset_id


def _publish_staging(staging: Path, destination: Path, assets_root: Path, overwrite: bool) -> None:
    if destination.exists():
        if not overwrite:
            raise PipelineError(f"Asset directory already exists: {destination}")
        _safe_remove_asset_dir(destination, assets_root)
    staging.rename(destination)


def _remove_python_bytecode(root: Path) -> None:
    for cache_dir in root.rglob("__pycache__"):
        if cache_dir.is_dir():
            shutil.rmtree(cache_dir)
    for bytecode in root.rglob("*.py[co]"):
        if bytecode.is_file():
            bytecode.unlink()


def _generate_one(
    *,
    spec: ExperimentSpec,
    plan: PlannedAsset,
    registration: GeneratorRegistration,
    assets_root: Path,
    motion_qc: bool,
    overwrite: bool,
    generator_sha256: str,
    spec_sha256: str,
) -> dict[str, Any]:
    axis_root = _axis_assets_root(assets_root, plan.axis_name)
    axis_root.mkdir(parents=True, exist_ok=True)
    destination = _asset_destination(assets_root, plan)
    staging = Path(tempfile.mkdtemp(prefix=f".{plan.asset_id}.", dir=axis_root))
    parameters = _base_parameters(
        spec=spec,
        plan=plan,
        registration=registration,
        generator_sha256=generator_sha256,
        spec_sha256=spec_sha256,
    )
    report_payload: dict[str, Any]
    error: str | None = None
    try:
        shutil.copy2(registration.source_path, staging / "generator.py")
        (staging / "model.py").write_text(
            _render_model_source(registration, plan.requested_config), encoding="utf-8"
        )
        try:
            report = compile_urdf_report_maybe_timeout(
                staging / "model.py",
                sdk_package="sdk",
                run_checks=True,
                target="full",
                rewrite_visual_glb=False,
                motion_qc=motion_qc,
            )
            report_payload = _compile_report_success(report, motion_qc=motion_qc)
            _verify_urdf_metadata(report.urdf_xml, plan.metadata)
            (staging / "model.urdf").write_text(report.urdf_xml, encoding="utf-8")
            parameters["urdf_sha256"] = _sha256_bytes(report.urdf_xml.encode("utf-8"))
            generator_module = registration.load_module()
            build_function = getattr(generator_module, registration.build_function)
            object_model = build_function(registration.make_config(plan.requested_config))
            physics_payload = build_physics_payload(
                object_model,
                model_urdf_sha256=parameters["urdf_sha256"],
            )
            _write_json(staging / "physics.json", physics_payload)
            parameters["status"] = "pass"
        except Exception as exc:  # one bad experiment cell must not hide later cells
            report_payload = _compile_report_failure(exc, motion_qc=motion_qc)
            parameters["status"] = "fail"
            error = f"{type(exc).__name__}: {exc}"
        _remove_python_bytecode(staging)
        _write_json(staging / "compile_report.json", report_payload)
        _write_json(staging / "parameters.json", parameters)
        _publish_staging(staging, destination, axis_root, overwrite)
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging, ignore_errors=True)
        raise
    hashes = {
        "model_py": _sha256_file(destination / "model.py"),
        "generator_py": _sha256_file(destination / "generator.py"),
        "parameters_json": _sha256_file(destination / "parameters.json"),
        "compile_report_json": _sha256_file(destination / "compile_report.json"),
        "model_urdf": (
            _sha256_file(destination / "model.urdf")
            if (destination / "model.urdf").is_file()
            else None
        ),
        "physics_json": (
            _sha256_file(destination / "physics.json")
            if (destination / "physics.json").is_file()
            else None
        ),
    }
    descriptor = parameters["intervention"]["descriptor"] or {}
    return {
        "asset_id": plan.asset_id,
        "status": parameters["status"],
        "path": (f"assets/{_safe_id(plan.axis_name, fallback='axis')}/{plan.asset_id}"),
        "controlled_axis": plan.axis_name,
        "controlled_axis_index": plan.axis_index,
        "controlled_level": plan.level,
        "resolved_level": parameters["intervention"]["resolved_value"],
        "priority": descriptor.get("priority"),
        "resolved_config_sha256": parameters["resolved_config_sha256"],
        "nuisance_block": plan.nuisance.block_id,
        "error": error,
        "hashes": hashes,
    }


def _write_manifest(
    *,
    output_root: Path,
    spec: ExperimentSpec,
    spec_sha256: str,
    generator_sha256: str,
    entries: Sequence[dict[str, Any]],
    planned_count: int,
) -> Path:
    passed = sum(entry["status"] == "pass" for entry in entries)
    failed = sum(entry["status"] == "fail" for entry in entries)
    registration = get_generator(spec.generator_id)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_version": __version__,
        "experiment": spec.name,
        "generator": spec.generator_id,
        "generator_version": registration.version,
        "generator_provenance": {
            "upstream_template_path": (
                f"agent/templates/{registration.upstream_template_filename}"
            ),
            "upstream_template_sha256": registration.upstream_template_sha256(),
            "upstream_generator_id": registration.upstream_generator_id,
            "asset_category": registration.asset_category,
            "task_variant": registration.generator_id,
        },
        "output_layout": (
            "<output_base>/<upstream_generator>/<experiment>/assets/<variable>/<asset>"
        ),
        "spec_sha256": spec_sha256,
        "spec_snapshot": "experiment_spec.json",
        "variable_space_snapshot": "variable_space.json",
        "generator_sha256": generator_sha256,
        "planned_count": planned_count,
        "completed_count": len(entries),
        "passed_count": passed,
        "failed_count": failed,
        "status": "pass" if len(entries) == planned_count and failed == 0 else "fail",
        "assets": list(entries),
    }
    path = output_root / "manifest.json"
    temporary = output_root / ".manifest.json.tmp"
    _write_json(temporary, manifest)
    os.replace(temporary, path)
    return path


def run_pipeline(
    spec_path: str | Path,
    output_base: str | Path,
    *,
    motion_qc: bool = False,
    overwrite: bool = False,
) -> PipelineResult:
    """Compile a spec below its upstream-generator and experiment folders."""

    spec, plans = validate_spec(spec_path)
    registration = get_generator(spec.generator_id)
    output_base = Path(output_base).expanduser().resolve()
    output_root = (
        output_base
        / registration.upstream_generator_id
        / _safe_id(spec.name, fallback="experiment")
    )
    assets_root = output_root / "assets"
    existing = [
        _asset_destination(assets_root, plan)
        for plan in plans
        if _asset_destination(assets_root, plan).exists()
    ]
    if existing and not overwrite:
        preview = "\n".join(f"  {path}" for path in existing[:10])
        suffix = "" if len(existing) <= 10 else f"\n  ... and {len(existing) - 10} more"
        raise PipelineError(
            "Refusing to replace existing asset directories without --overwrite:\n"
            f"{preview}{suffix}"
        )
    assets_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(spec.source_path, output_root / "experiment_spec.json")
    _write_json(output_root / "variable_space.json", registration.variable_space())
    generator_sha256 = registration.source_sha256()
    spec_sha256 = _sha256_file(spec.source_path)
    entries: list[dict[str, Any]] = []
    for plan in plans:
        try:
            entry = _generate_one(
                spec=spec,
                plan=plan,
                registration=registration,
                assets_root=assets_root,
                motion_qc=motion_qc,
                overwrite=overwrite,
                generator_sha256=generator_sha256,
                spec_sha256=spec_sha256,
            )
        except Exception as exc:
            descriptor = registration.variable_space()["variables"].get(plan.axis_name) or {}
            entry = {
                "asset_id": plan.asset_id,
                "status": "fail",
                "path": None,
                "controlled_axis": plan.axis_name,
                "controlled_axis_index": plan.axis_index,
                "controlled_level": plan.level,
                "resolved_level": plan.resolved_config.get(plan.axis_name),
                "priority": descriptor.get("priority"),
                "nuisance_block": plan.nuisance.block_id,
                "error": f"{type(exc).__name__}: {exc}",
                "hashes": {},
            }
        entries.append(entry)
        _write_manifest(
            output_root=output_root,
            spec=spec,
            spec_sha256=spec_sha256,
            generator_sha256=generator_sha256,
            entries=entries,
            planned_count=len(plans),
        )
    manifest_path = output_root / "manifest.json"
    failed = sum(entry["status"] == "fail" for entry in entries)
    return PipelineResult(
        output_root=output_root,
        manifest_path=manifest_path,
        assets_total=len(entries),
        assets_passed=len(entries) - failed,
        assets_failed=failed,
    )


def _plan_summary(spec: ExperimentSpec, plans: Sequence[PlannedAsset]) -> dict[str, Any]:
    registration = get_generator(spec.generator_id)
    variables = registration.variable_space()["variables"]
    return {
        "status": "valid",
        "experiment": spec.name,
        "generator": spec.generator_id,
        "upstream_generator": registration.upstream_generator_id,
        "output_subdirectory": (
            f"{registration.upstream_generator_id}/{_safe_id(spec.name, fallback='experiment')}"
        ),
        "axis_count": len(spec.axes),
        "axis_levels": {axis.name: len(axis.levels) for axis in spec.axes},
        "axis_semantics": {axis.name: variables.get(axis.name) for axis in spec.axes},
        "nuisance_block_count": len(spec.nuisance_blocks),
        "asset_count": len(plans),
        "asset_ids": [plan.asset_id for plan in plans],
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, help="JSON experiment spec")
    parser.add_argument(
        "--out",
        type=Path,
        help="output base; upstream-generator and experiment folders are added automatically",
    )
    parser.add_argument(
        "--motion-qc",
        action="store_true",
        help="optionally run compiler motion-pose QC",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace only exact asset directories planned by this spec",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="validate and print the stable generation plan without writing",
    )
    parser.add_argument(
        "--list-generators", action="store_true", help="list registered generator ids and exit"
    )
    parser.add_argument(
        "--describe-generator",
        metavar="GENERATOR_ID",
        help="print the machine-readable controlled variable space and exit",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.list_generators:
        for generator_id in list_generators():
            print(generator_id)
        return 0
    if args.describe_generator:
        try:
            payload = get_generator(args.describe_generator).variable_space()
        except RegistryError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    if args.spec is None:
        parser.error("--spec is required unless a generator inspection option is used")
    try:
        spec, plans = validate_spec(args.spec)
        if args.dry_run:
            print(json.dumps(_plan_summary(spec, plans), indent=2, sort_keys=True))
            return 0
        if args.out is None:
            parser.error("--out is required unless --dry-run or --list-generators is used")
        result = run_pipeline(
            args.spec,
            args.out,
            motion_qc=args.motion_qc,
            overwrite=args.overwrite,
        )
    except (PipelineError, RegistryError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": "pass" if result.ok else "fail",
                "assets_total": result.assets_total,
                "assets_passed": result.assets_passed,
                "assets_failed": result.assets_failed,
                "manifest": str(result.manifest_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "ExperimentSpec",
    "PipelineError",
    "PipelineResult",
    "PlannedAsset",
    "load_spec",
    "main",
    "plan_assets",
    "run_pipeline",
    "validate_spec",
]
