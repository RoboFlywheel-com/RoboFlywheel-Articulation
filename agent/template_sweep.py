# SPDX-License-Identifier: Apache-2.0

"""Multi-seed compile sweep for procedural templates.

This is the core engine behind `articraft template compile-sweep`. For each
seed in the requested range, it:

1. Calls `<template_module>.config_from_seed(seed)` to materialize the config.
2. Writes a synthetic `model.py` under a temp directory using the same
   `GENERIC_MODEL_TEMPLATE` shape that `articraft template batch` uses.
3. Invokes `agent.compiler.compile_urdf_report(target="full")`, which runs
   both the author-defined `run_tests()` and the compiler-owned baseline
   (single-root, mesh assets, isolated parts, overlap, articulation-origin
   distance). Template sweep also promotes compiler disconnected-geometry
   warnings to seed failures so part-internal floating visual islands do not
   pass as acceptable template variants.
4. Records the verdict, primary failure type, and failure details.

The lightweight ``template check`` wrapper adds cumulative caching and an
ephemeral repair summary.  Legacy compile-sweep reporting remains available,
but formal template checks do not use persistent clusters, streak state, or
coverage gates.
"""

from __future__ import annotations

import ast
import concurrent.futures
import dataclasses
import hashlib
import importlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable

from agent.compiler import compile_urdf_report
from agent.feedback import compile_signal_bundle_from_exception
from agent.template_policy import (
    RIGID_SEED_POLICY_CODE,
    overlap_policy_result,
    rigid_seed_detail,
)

DEFAULT_PASS_THRESHOLD = 0.90
DEFAULT_SEED_COUNT = 50
DEFAULT_COMPILE_TIMEOUT_S = 60.0
_DISCONNECTED_GEOMETRY_WARNING = "Disconnected geometry islands detected"
_DISCONNECTED_GEOMETRY_FAILURE_TYPE = (
    "fail_if_part_contains_disconnected_geometry_islands(tol=1e-06)"
)
_PAIR_RE = re.compile(r"\bpair=\(\s*(?P<a>['\"][^'\"]+['\"])\s*,\s*(?P<b>['\"][^'\"]+['\"])\s*\)")
_PART_RE = re.compile(r"\bpart=(?P<name>['\"][^'\"]+['\"])")
_JOINT_RE = re.compile(r"\bjoint=(?P<name>['\"][^'\"]+['\"])")
_JOINT_DICT_RE = re.compile(r"['\"]joint['\"]\s*:\s*(?P<name>['\"][^'\"]+['\"])")
_JOINT_LIST_RE = re.compile(
    r"\bjoint(?:\(s\)|s)?[^\n]*?:\s*(?P<names>\[[^\]\n]*\])",
    re.IGNORECASE,
)
_ELEMENT_RE = re.compile(r"\belem_[ab]=(?:#[0-9]+\s+)?(?P<name>['\"][^'\"]+['\"])(?::[^\s]+)?")
_POSE_RE = re.compile(r"\bpose=(?P<pose>\{[^\n]*\})")
_LOCATION_RE = re.compile(
    r"^Location:\s+(?P<path>.+?):(?P<line>[1-9][0-9]*)(?::(?P<column>[1-9][0-9]*))?\s*$",
    re.MULTILINE,
)

# Same shape as cli.template.GENERIC_MODEL_TEMPLATE; duplicated here to avoid a
# circular import between cli.template and agent.template_sweep. If the canonical
# template under cli.template ever changes, mirror it here too.
_GENERIC_MODEL_TEMPLATE = """from __future__ import annotations

import agent.templates.{slug} as _template_module
from agent.templates.{slug} import (
    build_{stem},
    config_from_seed,
    run_{stem}_tests,
)
from sdk import AssetContext

SEED = {seed}
CONFIG = config_from_seed(SEED)
ASSETS = AssetContext.from_script(__file__)
TEMPLATE_DOMAIN = getattr(_template_module, "TEMPLATE_DOMAIN", None)


def build_object_model():
    return build_{stem}(CONFIG, assets=ASSETS)


def run_tests():
    return run_{stem}_tests(object_model, CONFIG)


object_model = build_object_model()
"""


@dataclass(slots=True, frozen=True)
class SeedOutcome:
    """Per-seed compile result.

    ``failure_type``/``failure_details`` describe the primary (first) failure
    for stable clustering; ``failures`` carries EVERY failure signal from the
    compile as structured entries ({check, check_normalized, details}) so
    repair tooling can triage the seed's full defect list in one pass.
    ``allowances`` records the template's declared allowances (allow_overlap
    etc.) for report-level abuse auditing.
    """

    seed: int
    verdict: str  # "pass" | "fail"
    config: dict[str, Any]
    failure_type: str | None
    failure_type_normalized: str | None
    failure_details: str | None
    elapsed_s: float
    failures: tuple[dict[str, Any], ...] = ()
    allowances: tuple[str, ...] = ()
    artifact_dir: str | None = None
    motion_qc_report: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SeedOutcome":
        return cls(
            seed=int(payload["seed"]),
            verdict=str(payload["verdict"]),
            config=dict(payload.get("config") or {}),
            failure_type=payload.get("failure_type"),
            failure_type_normalized=payload.get("failure_type_normalized"),
            failure_details=payload.get("failure_details"),
            elapsed_s=float(payload.get("elapsed_s") or 0.0),
            failures=tuple(dict(entry) for entry in payload.get("failures") or ()),
            allowances=tuple(str(item) for item in payload.get("allowances") or ()),
            artifact_dir=payload.get("artifact_dir"),
            motion_qc_report=(
                dict(payload["motion_qc_report"])
                if isinstance(payload.get("motion_qc_report"), dict)
                else None
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "verdict": self.verdict,
            "config": self.config,
            "failure_type": self.failure_type,
            "failure_type_normalized": self.failure_type_normalized,
            "failure_details": self.failure_details,
            "elapsed_s": self.elapsed_s,
            "failures": [dict(entry) for entry in self.failures],
            "allowances": list(self.allowances),
            "artifact_dir": self.artifact_dir,
            "motion_qc_report": self.motion_qc_report,
        }


def joint_motion_edge_coverage(
    reports: Iterable[dict[str, Any] | None],
) -> dict[str, Any]:
    """Aggregate coverage from compiler-recorded execution, never from URDF limits."""

    rows = list(reports)
    missing_reports = [index for index, report in enumerate(rows) if not isinstance(report, dict)]
    valid_reports = [report for report in rows if isinstance(report, dict)]
    missing_edges: list[dict[str, Any]] = []
    joints: dict[tuple[str, str], dict[str, Any]] = {}
    executed_pose_count = 0
    required_pose_count = 0
    executed_pose_kind_counts: dict[str, int] = {}
    required_pose_kind_counts: dict[str, int] = {}
    repeat_groups: list[dict[str, Any]] = []
    failed_reports = 0
    for report in valid_reports:
        executed_pose_count += len(report.get("executed_pose_ids") or ())
        required_pose_count += len(report.get("required_pose_ids") or ())
        executed_kinds = report.get("executed_pose_kind_counts")
        if isinstance(executed_kinds, dict):
            for kind, count in executed_kinds.items():
                executed_pose_kind_counts[str(kind)] = executed_pose_kind_counts.get(
                    str(kind), 0
                ) + int(count)
        required_kinds = report.get("required_pose_kind_counts")
        if isinstance(required_kinds, dict):
            for kind, count in required_kinds.items():
                required_pose_kind_counts[str(kind)] = required_pose_kind_counts.get(
                    str(kind), 0
                ) + int(count)
        for group in report.get("repeat_groups") or ():
            if isinstance(group, dict):
                repeat_groups.append(dict(group))
        if report.get("status") != "pass":
            failed_reports += 1
        for edge in report.get("missing_edges") or ():
            if isinstance(edge, dict):
                missing_edges.append(dict(edge))
        for row in report.get("joints") or ():
            if not isinstance(row, dict):
                continue
            key = (str(row.get("joint") or ""), str(row.get("joint_type") or ""))
            aggregate = joints.setdefault(
                key,
                {
                    "joint": key[0],
                    "joint_type": key[1],
                    "required_edges": set(),
                    "covered_edges": set(),
                },
            )
            aggregate["required_edges"].update(row.get("required_edges") or ())
            aggregate["covered_edges"].update(row.get("covered_edges") or ())
    joint_rows = []
    for key in sorted(joints):
        row = joints[key]
        joint_rows.append(
            {
                "joint": row["joint"],
                "joint_type": row["joint_type"],
                "required_edges": sorted(row["required_edges"]),
                "covered_edges": sorted(row["covered_edges"]),
            }
        )
    complete = bool(rows) and not missing_reports and not missing_edges and not failed_reports
    return {
        "status": "pass" if complete else "fail",
        "report_count": len(valid_reports),
        "missing_report_indexes": missing_reports,
        "failed_reports": failed_reports,
        "required_pose_count": required_pose_count,
        "executed_pose_count": executed_pose_count,
        "required_pose_kind_counts": dict(sorted(required_pose_kind_counts.items())),
        "executed_pose_kind_counts": dict(sorted(executed_pose_kind_counts.items())),
        "repeat_groups": repeat_groups,
        "joints": joint_rows,
        "missing_edges": missing_edges,
    }


def compiled_artifact_is_valid(path: str | Path | None) -> bool:
    if not path:
        return False
    root = Path(path)
    urdf_path = root / "model.urdf"
    metadata_path = root / "artifact.json"
    if not root.is_dir() or not urdf_path.is_file() or not metadata_path.is_file():
        return False
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    expected = metadata.get("urdf_sha256")
    return (
        isinstance(expected, str) and expected == hashlib.sha256(urdf_path.read_bytes()).hexdigest()
    )


def _publish_compiled_artifact(
    work_dir: Path,
    *,
    artifact_root: Path,
    slug: str,
    seed: int,
    config: dict[str, Any],
    urdf_xml: str,
) -> Path:
    (work_dir / "model.urdf").write_text(urdf_xml, encoding="utf-8")
    (work_dir / "artifact.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "slug": slug,
                "seed": seed,
                "config": config,
                "urdf_sha256": hashlib.sha256(urdf_xml.encode()).hexdigest(),
            },
            indent=2,
            sort_keys=True,
            default=str,
        )
        + "\n",
        encoding="utf-8",
    )
    destination = artifact_root / f"seed_{seed}"
    if compiled_artifact_is_valid(destination):
        return destination.resolve()
    if destination.is_dir():
        shutil.rmtree(destination)
    elif destination.exists():
        destination.unlink()
    work_dir.replace(destination)
    return destination.resolve()


@dataclass(slots=True)
class SweepReport:
    """Aggregate report for a sweep."""

    slug: str
    stem: str
    total_seeds: int
    seeds_requested: list[int]
    passed_seeds: list[int]
    failed_outcomes: list[SeedOutcome]
    pass_rate: float
    pass_threshold: float
    verdict: str
    elapsed_s: float
    failure_clusters: list[Any] = field(default_factory=list)
    cluster_streaks: dict[str, int] = field(default_factory=dict)
    escalation: dict[str, Any] | None = None
    coverage_gates: dict[str, Any] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def _cluster_dict(self, cluster: Any) -> dict[str, Any]:
        d = cluster.to_dict()
        d["streak_count"] = int(self.cluster_streaks.get(d.get("cluster_signature", ""), 1))
        return d

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "slug": self.slug,
            "stem": self.stem,
            "total_seeds": self.total_seeds,
            "seeds_requested": self.seeds_requested,
            "passed_seeds": self.passed_seeds,
            "failed_seeds": [outcome.to_dict() for outcome in self.failed_outcomes],
            "failure_clusters": [self._cluster_dict(c) for c in self.failure_clusters],
            "pass_rate": self.pass_rate,
            "pass_threshold": self.pass_threshold,
            "verdict": self.verdict,
            "elapsed_s": self.elapsed_s,
        }
        if self.escalation is not None:
            payload["escalation"] = self.escalation
        if self.coverage_gates is not None:
            payload["coverage_gates"] = self.coverage_gates
        payload.update({k: v for k, v in self.extra.items() if k not in payload})
        return payload


def parse_seed_spec(spec: str) -> list[int]:
    """Parse a seed spec like '0-49' or '1,3,5-8' into an ordered list of ints."""
    seeds: list[int] = []
    seen: set[int] = set()
    for chunk in spec.split(","):
        part = chunk.strip()
        if not part:
            continue
        if "-" in part:
            start_text, end_text = part.split("-", 1)
            start = int(start_text.strip())
            end = int(end_text.strip())
            if end < start:
                raise ValueError(f"Invalid seed range: {part}")
            for seed in range(start, end + 1):
                if seed not in seen:
                    seen.add(seed)
                    seeds.append(seed)
        else:
            seed = int(part)
            if seed not in seen:
                seen.add(seed)
                seeds.append(seed)
    if not seeds:
        raise ValueError("At least one seed is required")
    return seeds


def _config_to_dict(config: Any) -> dict[str, Any]:
    if dataclasses.is_dataclass(config):
        return dataclasses.asdict(config)
    if hasattr(config, "__dict__"):
        return {k: v for k, v in vars(config).items() if not k.startswith("_")}
    return {"_repr": repr(config)}


def _normalize_failure_type(failure_type: str | None) -> str | None:
    """Strip parameter parens from a check_name so clusters group across tol values."""
    if failure_type is None:
        return None
    base = failure_type.split("(")[0].strip()
    return base or failure_type


def extract_failure_entities(details: str) -> dict[str, Any]:
    """Extract stable mechanical/code entities from compiler-owned detail text.

    The harness already emits machine-shaped fragments such as ``pair=(...)``,
    ``part=...``, ``elem_a=...`` and ``pose={...}``.  Preserve those as JSON so
    repair tooling never has to rediscover them by rereading a prose blob.
    Unknown detail formats remain available verbatim on the failure signal.
    """

    parts: set[str] = set()
    joints: set[str] = set()
    elements: set[str] = set()
    pairs: set[tuple[str, str]] = set()
    poses: list[dict[str, Any]] = []
    locations: list[dict[str, Any]] = []

    def literal_name(raw: str) -> str:
        try:
            value = ast.literal_eval(raw)
        except (SyntaxError, ValueError):
            return raw.strip("'\"")
        return str(value)

    for match in _PAIR_RE.finditer(details):
        pair = (literal_name(match.group("a")), literal_name(match.group("b")))
        pairs.add(tuple(sorted(pair)))
        parts.update(pair)
    parts.update(literal_name(match.group("name")) for match in _PART_RE.finditer(details))
    joints.update(literal_name(match.group("name")) for match in _JOINT_RE.finditer(details))
    joints.update(literal_name(match.group("name")) for match in _JOINT_DICT_RE.finditer(details))
    for match in _JOINT_LIST_RE.finditer(details):
        try:
            names = ast.literal_eval(match.group("names"))
        except (SyntaxError, ValueError):
            continue
        if isinstance(names, (list, tuple, set)):
            joints.update(str(name) for name in names)
    elements.update(literal_name(match.group("name")) for match in _ELEMENT_RE.finditer(details))
    for match in _POSE_RE.finditer(details):
        try:
            pose = ast.literal_eval(match.group("pose"))
        except (SyntaxError, ValueError):
            continue
        if not isinstance(pose, dict):
            continue
        normalized = {str(key): value for key, value in pose.items()}
        if normalized not in poses:
            poses.append(normalized)
        joints.update(normalized)
    for match in _LOCATION_RE.finditer(details):
        location: dict[str, Any] = {
            "path": match.group("path"),
            "line": int(match.group("line")),
        }
        if match.group("column") is not None:
            location["column"] = int(match.group("column"))
        if location not in locations:
            locations.append(location)
    return {
        "parts": sorted(parts),
        "joints": sorted(joints),
        "elements": sorted(elements),
        "pairs": [list(pair) for pair in sorted(pairs)],
        "poses": poses,
        "locations": locations,
    }


def extract_failure_signals(exc: BaseException) -> list[dict[str, Any]]:
    """Return EVERY failure signal from a compile exception as structured
    {check, check_normalized, details} entries. All checks run and record
    before the compiler raises, so this is the seed's full defect list."""
    bundle = compile_signal_bundle_from_exception(exc)
    entries: list[dict[str, Any]] = []
    for signal in bundle.signals:
        if signal.severity != "failure":
            continue
        check = signal.check_name or signal.code or signal.kind or "unknown_failure"
        details = (signal.details or signal.summary or "").strip()
        entries.append(
            {
                "check": check,
                "check_normalized": _normalize_failure_type(check),
                "kind": signal.kind,
                "code": signal.code,
                "summary": signal.summary,
                "source": signal.source,
                "group": signal.group,
                "details": details[:4000],
                "entities": extract_failure_entities(details),
            }
        )
    return entries


def _extract_failure(exc: BaseException) -> tuple[str, str]:
    """Pick the (failure_type, details) tuple from a compile exception.

    ``failure_type`` is the first failure signal (stable for clustering);
    ``details`` carry that signal's details PLUS every remaining failure
    signal from the same compile, so one iteration surfaces the seed's full
    defect list instead of unmasking one check per round.
    """
    entries = extract_failure_signals(exc)
    if entries:
        primary = entries[0]
        details = primary["details"]
        rest = entries[1:]
        if rest:
            extra_lines = [f"[{entry['check']}] {entry['details'][:1200]}" for entry in rest]
            details = (
                f"{details}\n\nADDITIONAL FAILURES in the same seed ({len(rest)}):\n"
                + "\n".join(extra_lines)
            )
        return primary["check"], details
    return type(exc).__name__, str(exc)


def _report_allowances(source: object) -> tuple[str, ...]:
    """Best-effort allowance strings from a compile report / exception."""
    test_report = getattr(source, "test_report", None)
    allowances = getattr(test_report, "allowances", ()) or ()
    return tuple(str(item) for item in allowances)


def _template_module_path(slug: str, *, repo_root: Path) -> Path:
    return repo_root / "agent" / "templates" / f"{slug}.py"


def _resolve_config_from_seed(slug: str, seed: int) -> Any:
    module = importlib.import_module(f"agent.templates.{slug}")
    config_from_seed = getattr(module, "config_from_seed", None)
    if not callable(config_from_seed):
        raise AttributeError(
            f"agent.templates.{slug} is missing a callable config_from_seed(seed)."
        )
    return config_from_seed(seed)


def disconnected_geometry_warning_details(warnings: Iterable[str]) -> str | None:
    """Escalate the compiler's disconnected-geometry warning to a failure detail.

    A part that fell into islands is a broken asset, not an advisory, so this is
    the shared rule for every gate that decides whether a seed is usable: the
    sweep's verdict and ``template gen-seeds``' keep/reject both call it. They
    already compile identically (target="full", run_checks, motion_qc); when only
    the sweep applied this escalation, gen-seeds exported seeds the sweep failed.
    """
    for warning in warnings:
        text = str(warning)
        if _DISCONNECTED_GEOMETRY_WARNING in text:
            return (
                "Template sweep treats compiler disconnected-geometry warnings as failures. "
                "Fix floating visuals inside the named part by embedding them into the "
                "supporting surface, adding a real bridge/cantilever, or splitting them "
                "into separate fixed parts.\n"
                f"{text[:2000]}"
            )
    return None


def _compile_one(
    slug: str,
    stem: str,
    seed: int,
    sdk_package: str,
    motion_qc: bool = True,
    artifact_root: str | Path | None = None,
) -> SeedOutcome:
    """Run a single (slug, seed) compile and return its outcome.

    Designed to be safe in either main process or a subprocess.
    """
    start = time.monotonic()
    config = _resolve_config_from_seed(slug, seed)
    config_dict = _config_to_dict(config)
    resolved_artifact_root = Path(artifact_root).resolve() if artifact_root else None
    if resolved_artifact_root is not None:
        resolved_artifact_root.mkdir(parents=True, exist_ok=True)
    work_dir = Path(tempfile.mkdtemp(prefix=f".sweep_{slug}_{seed}_", dir=resolved_artifact_root))
    policy_root = Path(__file__).resolve().parents[1]
    try:
        script_path = work_dir / "model.py"
        script_path.write_text(
            _GENERIC_MODEL_TEMPLATE.format(slug=slug, stem=stem, seed=seed),
            encoding="utf-8",
        )
        try:
            compile_report = compile_urdf_report(
                script_path,
                sdk_package=sdk_package,
                run_checks=True,
                target="full",
                rewrite_visual_glb=False,
                motion_qc=motion_qc,
            )
            overlap_policy = overlap_policy_result(
                repo_root=policy_root,
                slug=slug,
                allowances=_report_allowances(compile_report),
            )
            if overlap_policy["detail"] is not None:
                overlap_details = overlap_policy["detail"]
                return SeedOutcome(
                    seed=seed,
                    verdict="fail",
                    config=config_dict,
                    failure_type="overlap_allowance_forbidden",
                    failure_type_normalized="overlap_allowance_forbidden",
                    failure_details=overlap_details,
                    elapsed_s=time.monotonic() - start,
                    failures=(
                        {
                            "check": "overlap_allowance_forbidden",
                            "check_normalized": "overlap_allowance_forbidden",
                            "details": overlap_details,
                        },
                    ),
                    allowances=_report_allowances(compile_report),
                )
            rigid_details = rigid_seed_detail(getattr(compile_report, "urdf_xml", "") or "")
            if rigid_details is not None:
                return SeedOutcome(
                    seed=seed,
                    verdict="fail",
                    config=config_dict,
                    failure_type=RIGID_SEED_POLICY_CODE,
                    failure_type_normalized=RIGID_SEED_POLICY_CODE,
                    failure_details=rigid_details,
                    elapsed_s=time.monotonic() - start,
                    failures=(
                        {
                            "check": RIGID_SEED_POLICY_CODE,
                            "check_normalized": RIGID_SEED_POLICY_CODE,
                            "details": rigid_details,
                        },
                    ),
                    allowances=_report_allowances(compile_report),
                )
            disconnected_details = disconnected_geometry_warning_details(compile_report.warnings)
            if disconnected_details is not None:
                return SeedOutcome(
                    seed=seed,
                    verdict="fail",
                    config=config_dict,
                    failure_type=_DISCONNECTED_GEOMETRY_FAILURE_TYPE,
                    failure_type_normalized=_normalize_failure_type(
                        _DISCONNECTED_GEOMETRY_FAILURE_TYPE
                    ),
                    failure_details=disconnected_details,
                    elapsed_s=time.monotonic() - start,
                    failures=(
                        {
                            "check": _DISCONNECTED_GEOMETRY_FAILURE_TYPE,
                            "check_normalized": _normalize_failure_type(
                                _DISCONNECTED_GEOMETRY_FAILURE_TYPE
                            ),
                            "details": disconnected_details[:4000],
                        },
                    ),
                    allowances=_report_allowances(compile_report),
                )
        except Exception as exc:  # noqa: BLE001 — captured into structured outcome
            overlap_policy = overlap_policy_result(
                repo_root=policy_root,
                slug=slug,
                allowances=_report_allowances(exc),
            )
            if overlap_policy["detail"] is not None:
                overlap_details = overlap_policy["detail"]
                return SeedOutcome(
                    seed=seed,
                    verdict="fail",
                    config=config_dict,
                    failure_type="overlap_allowance_forbidden",
                    failure_type_normalized="overlap_allowance_forbidden",
                    failure_details=overlap_details,
                    elapsed_s=time.monotonic() - start,
                    failures=(
                        {
                            "check": "overlap_allowance_forbidden",
                            "check_normalized": "overlap_allowance_forbidden",
                            "details": overlap_details,
                        },
                    ),
                    allowances=_report_allowances(exc),
                )
            failure_type, details = _extract_failure(exc)
            return SeedOutcome(
                seed=seed,
                verdict="fail",
                config=config_dict,
                failure_type=failure_type,
                failure_type_normalized=_normalize_failure_type(failure_type),
                failure_details=details,
                elapsed_s=time.monotonic() - start,
                failures=tuple(extract_failure_signals(exc)),
                allowances=_report_allowances(exc),
                motion_qc_report=(
                    dict(getattr(exc, "motion_qc_report"))
                    if isinstance(getattr(exc, "motion_qc_report", None), dict)
                    else None
                ),
            )
        motion_report = compile_report.motion_qc_report
        if motion_qc and (
            not isinstance(motion_report, dict) or motion_report.get("status") != "pass"
        ):
            details = "motion QC completed without a valid actual-execution coverage report"
            return SeedOutcome(
                seed=seed,
                verdict="fail",
                config=config_dict,
                failure_type="motion_qc_coverage_incomplete",
                failure_type_normalized="motion_qc_coverage_incomplete",
                failure_details=details,
                elapsed_s=time.monotonic() - start,
                failures=(
                    {
                        "check": "motion_qc_coverage_incomplete",
                        "check_normalized": "motion_qc_coverage_incomplete",
                        "details": details,
                    },
                ),
                allowances=_report_allowances(compile_report),
                motion_qc_report=(dict(motion_report) if isinstance(motion_report, dict) else None),
            )
        published: Path | None = None
        if resolved_artifact_root is not None:
            published = _publish_compiled_artifact(
                work_dir,
                artifact_root=resolved_artifact_root,
                slug=slug,
                seed=seed,
                config=config_dict,
                urdf_xml=compile_report.urdf_xml,
            )
        return SeedOutcome(
            seed=seed,
            verdict="pass",
            config=config_dict,
            failure_type=None,
            failure_type_normalized=None,
            failure_details=None,
            elapsed_s=time.monotonic() - start,
            allowances=_report_allowances(compile_report),
            artifact_dir=str(published) if published is not None else None,
            motion_qc_report=(dict(motion_report) if isinstance(motion_report, dict) else None),
        )
    finally:
        if work_dir.exists():
            shutil.rmtree(work_dir, ignore_errors=True)


_SUBPROCESS_WORKER_SOURCE = """
import json
import sys
import traceback
from agent.template_sweep import _compile_one
try:
    outcome = _compile_one(
        {slug!r}, {stem!r}, {seed}, {sdk_package!r}, motion_qc={motion_qc!r},
        artifact_root={artifact_root!r}
    )
    sys.stdout.write(json.dumps(outcome.to_dict()))
except BaseException as exc:
    sys.stderr.write(traceback.format_exc())
    raise
"""


def _seed_outcome_from_dict(payload: dict) -> SeedOutcome:
    return SeedOutcome.from_dict(payload)


def _timeout_outcome(seed: int, timeout_s: float) -> SeedOutcome:
    return SeedOutcome(
        seed=seed,
        verdict="fail",
        config={},
        failure_type=f"compile_timeout({timeout_s:.0f}s)",
        failure_type_normalized="compile_timeout",
        failure_details=(
            f"per-seed compile exceeded the {timeout_s:.0f}s wall-time budget "
            "and the worker subprocess was SIGKILL'd. Likely cause: a geometry "
            "QC step (fcl distance / trimesh boolean) entered a non-terminating "
            "loop on degenerate geometry produced by this seed."
        ),
        elapsed_s=float(timeout_s),
        failures=(
            {
                "check": f"compile_timeout({timeout_s:.0f}s)",
                "check_normalized": "compile_timeout",
                "details": f"per-seed compile exceeded the {timeout_s:.0f}s wall-time budget",
            },
        ),
    )


def _subprocess_crash_outcome(seed: int, returncode: int, stderr: str) -> SeedOutcome:
    return SeedOutcome(
        seed=seed,
        verdict="fail",
        config={},
        failure_type=f"subprocess_crash(rc={returncode})",
        failure_type_normalized="subprocess_crash",
        failure_details=stderr[:2000] if stderr else f"non-zero return code {returncode}",
        elapsed_s=0.0,
    )


def _compile_one_via_subprocess(
    slug: str,
    stem: str,
    seed: int,
    sdk_package: str,
    *,
    timeout_s: float,
    repo_root: Path,
    motion_qc: bool = True,
    artifact_root: str | Path | None = None,
) -> SeedOutcome:
    """Run a single (slug, seed) compile in a fresh Python subprocess with a hard
    wall-time timeout. On timeout, the subprocess is SIGKILL'd and a synthetic
    `compile_timeout` SeedOutcome is returned so the sweep can continue past
    templates that hang inside non-Python-interruptible QC code (e.g. fcl)."""
    code = _SUBPROCESS_WORKER_SOURCE.format(
        slug=slug,
        stem=stem,
        seed=seed,
        sdk_package=sdk_package,
        motion_qc=motion_qc,
        artifact_root=str(artifact_root) if artifact_root is not None else None,
    )
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            cwd=str(repo_root),
        )
    except subprocess.TimeoutExpired:
        return _timeout_outcome(seed, timeout_s)
    if proc.returncode != 0:
        return _subprocess_crash_outcome(seed, proc.returncode, proc.stderr)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return _subprocess_crash_outcome(
            seed,
            0,
            f"could not decode worker JSON: {exc}\nstdout preview: {proc.stdout[:500]!r}",
        )
    return _seed_outcome_from_dict(payload)


def _run_seeds_sequential(
    slug: str,
    stem: str,
    seeds: Iterable[int],
    sdk_package: str,
    progress: Callable[[SeedOutcome], None] | None = None,
    *,
    compile_timeout_s: float = 0.0,
    repo_root: Path | None = None,
    motion_qc: bool = True,
    artifact_root: str | Path | None = None,
) -> list[SeedOutcome]:
    outcomes: list[SeedOutcome] = []
    for seed in seeds:
        if compile_timeout_s > 0.0:
            outcome = _compile_one_via_subprocess(
                slug,
                stem,
                seed,
                sdk_package,
                timeout_s=compile_timeout_s,
                repo_root=repo_root or Path(__file__).resolve().parents[1],
                motion_qc=motion_qc,
                artifact_root=artifact_root,
            )
        else:
            if artifact_root is None:
                outcome = _compile_one(slug, stem, seed, sdk_package, motion_qc)
            else:
                outcome = _compile_one(
                    slug,
                    stem,
                    seed,
                    sdk_package,
                    motion_qc,
                    artifact_root,
                )
        outcomes.append(outcome)
        if progress is not None:
            progress(outcome)
    return outcomes


def _run_seeds_parallel(
    slug: str,
    stem: str,
    seeds: list[int],
    sdk_package: str,
    max_workers: int,
    progress: Callable[[SeedOutcome], None] | None = None,
    *,
    compile_timeout_s: float = 0.0,
    repo_root: Path | None = None,
    motion_qc: bool = True,
    artifact_root: str | Path | None = None,
) -> list[SeedOutcome]:
    """Parallel seed runner.

    When `compile_timeout_s > 0`, each seed compile happens inside a fresh
    subprocess invoked via `subprocess.run(..., timeout=...)`. The parent
    parallelizes those via a ThreadPoolExecutor (threads block on .run()'s
    pipe), and SIGKILLs the subprocess on timeout — bulletproof against
    non-interruptible C-level hangs in geometry QC.

    When `compile_timeout_s == 0`, the legacy ProcessPoolExecutor path is used
    (faster on healthy templates, but a single hung seed will block one worker
    indefinitely).
    """
    outcomes: dict[int, SeedOutcome] = {}

    if compile_timeout_s > 0.0:
        root = repo_root or Path(__file__).resolve().parents[1]
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {
                executor.submit(
                    _compile_one_via_subprocess,
                    slug,
                    stem,
                    seed,
                    sdk_package,
                    timeout_s=compile_timeout_s,
                    repo_root=root,
                    motion_qc=motion_qc,
                    artifact_root=artifact_root,
                ): seed
                for seed in seeds
            }
            for future in concurrent.futures.as_completed(future_map):
                seed = future_map[future]
                try:
                    outcome = future.result()
                except Exception as exc:  # noqa: BLE001 — should not happen now, but be safe
                    outcome = SeedOutcome(
                        seed=seed,
                        verdict="fail",
                        config={},
                        failure_type=f"thread_error:{type(exc).__name__}",
                        failure_type_normalized="thread_error",
                        failure_details=str(exc),
                        elapsed_s=0.0,
                    )
                outcomes[seed] = outcome
                if progress is not None:
                    progress(outcome)
        return [outcomes[seed] for seed in seeds]

    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        if artifact_root is None:
            future_map = {
                executor.submit(_compile_one, slug, stem, seed, sdk_package, motion_qc): seed
                for seed in seeds
            }
        else:
            future_map = {
                executor.submit(
                    _compile_one,
                    slug,
                    stem,
                    seed,
                    sdk_package,
                    motion_qc,
                    artifact_root,
                ): seed
                for seed in seeds
            }
        for future in concurrent.futures.as_completed(future_map):
            seed = future_map[future]
            try:
                outcome = future.result()
            except Exception as exc:  # noqa: BLE001 — subprocess crash
                outcome = SeedOutcome(
                    seed=seed,
                    verdict="fail",
                    config={},
                    failure_type=f"subprocess_error:{type(exc).__name__}",
                    failure_type_normalized=f"subprocess_error:{type(exc).__name__}",
                    failure_details=str(exc),
                    elapsed_s=0.0,
                )
            outcomes[seed] = outcome
            if progress is not None:
                progress(outcome)
    return [outcomes[seed] for seed in seeds]


def run_seed_outcomes(
    *,
    slug: str,
    stem: str,
    seeds: list[int],
    sdk_package: str = "sdk",
    max_workers: int | None = None,
    repo_root: Path | None = None,
    progress: Callable[[SeedOutcome], None] | None = None,
    compile_timeout_s: float = 0.0,
    motion_qc: bool = True,
    artifact_root: str | Path | None = None,
) -> list[SeedOutcome]:
    """Compile the requested seeds and return raw per-seed outcomes.

    `max_workers=1` (or `None` when there is a single seed) runs sequentially in
    the current process. Anything else uses a ProcessPoolExecutor (in-process
    workers) by default, or a ThreadPool+subprocess scheme when
    `compile_timeout_s > 0` so each seed has a hard wall-time budget enforced
    via SIGKILL.
    """
    if not seeds:
        raise ValueError("seeds must contain at least one entry")
    repo_root = repo_root or Path(__file__).resolve().parents[1]
    template_path = _template_module_path(slug, repo_root=repo_root)
    if not template_path.exists():
        raise FileNotFoundError(f"agent/templates/{slug}.py not found (looked at {template_path})")

    workers = max_workers if max_workers is not None else min(len(seeds), 8)
    if workers <= 1 or len(seeds) == 1:
        return _run_seeds_sequential(
            slug,
            stem,
            seeds,
            sdk_package,
            progress,
            compile_timeout_s=compile_timeout_s,
            repo_root=repo_root,
            motion_qc=motion_qc,
            artifact_root=artifact_root,
        )
    return _run_seeds_parallel(
        slug,
        stem,
        seeds,
        sdk_package,
        workers,
        progress,
        compile_timeout_s=compile_timeout_s,
        repo_root=repo_root,
        motion_qc=motion_qc,
        artifact_root=artifact_root,
    )


def build_sweep_report_from_outcomes(
    *,
    slug: str,
    stem: str,
    seeds: list[int],
    outcomes: list[SeedOutcome],
    pass_threshold: float = DEFAULT_PASS_THRESHOLD,
    repo_root: Path | None = None,
    state_dir: Path | None = None,
    elapsed_s: float = 0.0,
) -> SweepReport:
    """Aggregate existing outcomes into the same report shape used by run_sweep."""
    if not seeds:
        raise ValueError("seeds must contain at least one entry")
    repo_root = repo_root or Path(__file__).resolve().parents[1]
    template_path = _template_module_path(slug, repo_root=repo_root)
    if not template_path.exists():
        raise FileNotFoundError(f"agent/templates/{slug}.py not found (looked at {template_path})")

    passed_seeds = [o.seed for o in outcomes if o.verdict == "pass"]
    failed_outcomes = [o for o in outcomes if o.verdict == "fail"]
    pass_rate = len(passed_seeds) / len(seeds) if seeds else 0.0

    # Local imports to avoid top-level cycles.
    from agent.template_sweep_clusters import cluster_failures
    from agent.template_sweep_coverage import evaluate_gates

    clusters = cluster_failures(failed_outcomes)
    cluster_signatures = [c.cluster_signature for c in clusters]

    gates = evaluate_gates(
        slug=slug,
        outcomes=outcomes,
        repo_root=repo_root,
    )

    # Coverage gates are REPORT-ONLY (user decision 2026-07-04): per-slot
    # realization lives in the axis_realization report and corner seeds
    # deterministically probe unrealized combos, so declared-diversity drift
    # is visible without gating the verdict. Verdict = pass_rate alone.
    verdict = "pass" if pass_rate >= pass_threshold else "fail"

    report = SweepReport(
        slug=slug,
        stem=stem,
        total_seeds=len(seeds),
        seeds_requested=list(seeds),
        passed_seeds=passed_seeds,
        failed_outcomes=failed_outcomes,
        pass_rate=round(pass_rate, 6),
        pass_threshold=pass_threshold,
        verdict=verdict,
        elapsed_s=round(elapsed_s, 3),
        failure_clusters=clusters,
        cluster_streaks={sig: 1 for sig in cluster_signatures},
        escalation=None,
        coverage_gates=gates.to_dict(),
    )
    if state_dir is not None:
        record_sweep_state(report, outcomes, state_dir=state_dir)
    return report


def record_sweep_state(
    report: SweepReport, outcomes: list[SeedOutcome], *, state_dir: Path
) -> None:
    """Persist streak/allowance state for a finished sweep and update the
    report's ``cluster_streaks``/``escalation`` in place.

    Uses the report's FINAL verdict — callers that override the verdict after
    building (e.g. the pipeline's corner gate) must call this AFTER the
    override, or a corner-only failure would be recorded as a pass and refresh
    the allowance baseline with unvetted allowances.
    """
    from agent.template_sweep_state import (
        ClusterFingerprint,
        compute_escalation,
        load_state,
        save_state,
        update_streaks,
    )

    cluster_fingerprints = [
        ClusterFingerprint(
            signature=c.cluster_signature,
            failure_type=c.shared_failure_type,
            axis_keys=sorted(c.shared_config_axes.keys()),
        )
        for c in report.failure_clusters
    ]
    previous = load_state(state_dir, report.slug)
    next_state = update_streaks(
        slug=report.slug,
        previous=previous,
        current_clusters=cluster_fingerprints,
        current_pass_rate=report.pass_rate,
        current_verdict=report.verdict,
    )
    # Allowance baseline: refresh on PASSING sweeps only, so the next run's
    # audit can diff and flag newly added allowances; a failing run keeps the
    # last-good baseline.
    if report.verdict == "pass":
        next_state.passing_allowances = sorted(
            {allowance for outcome in outcomes for allowance in (outcome.allowances or ())}
        )
    elif previous is not None:
        next_state.passing_allowances = list(previous.passing_allowances)
    save_state(state_dir, next_state)
    report.cluster_streaks = dict(next_state.cluster_streaks)
    report.escalation = compute_escalation(next_state).to_dict()


def run_sweep(
    *,
    slug: str,
    stem: str,
    seeds: list[int],
    sdk_package: str = "sdk",
    pass_threshold: float = DEFAULT_PASS_THRESHOLD,
    max_workers: int | None = None,
    repo_root: Path | None = None,
    progress: Callable[[SeedOutcome], None] | None = None,
    state_dir: Path | None = None,
    compile_timeout_s: float = 0.0,
    motion_qc: bool = True,
) -> SweepReport:
    """Run a multi-seed compile sweep and return the structured report."""
    started = time.monotonic()
    outcomes = run_seed_outcomes(
        slug=slug,
        stem=stem,
        seeds=seeds,
        sdk_package=sdk_package,
        max_workers=max_workers,
        repo_root=repo_root,
        progress=progress,
        compile_timeout_s=compile_timeout_s,
        motion_qc=motion_qc,
    )
    elapsed = time.monotonic() - started
    return build_sweep_report_from_outcomes(
        slug=slug,
        stem=stem,
        seeds=seeds,
        outcomes=outcomes,
        pass_threshold=pass_threshold,
        repo_root=repo_root,
        state_dir=state_dir,
        elapsed_s=elapsed,
    )


def report_to_json(report: SweepReport, *, indent: int | None = 2) -> str:
    """Serialize report to JSON string."""
    return json.dumps(report.to_dict(), indent=indent, sort_keys=False, default=str)


def write_report(report: SweepReport, *, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report_to_json(report), encoding="utf-8")


def _ascii_progress_line(outcome: SeedOutcome, *, total: int, done_count: int) -> str:
    state = "PASS" if outcome.verdict == "pass" else "FAIL"
    elapsed = f"{outcome.elapsed_s:.2f}s"
    if outcome.verdict == "fail":
        ft = outcome.failure_type_normalized or outcome.failure_type or "unknown"
        return f"[{done_count}/{total}] seed={outcome.seed} {state} ({elapsed}) {ft}"
    return f"[{done_count}/{total}] seed={outcome.seed} {state} ({elapsed})"


def stderr_progress_reporter(total: int) -> Callable[[SeedOutcome], None]:
    """Return a progress callback that writes one short line per seed to stderr."""
    import sys

    state = {"count": 0}

    def _report(outcome: SeedOutcome) -> None:
        state["count"] += 1
        line = _ascii_progress_line(outcome, total=total, done_count=state["count"])
        print(line, file=sys.stderr, flush=True)

    return _report
