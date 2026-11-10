# SPDX-License-Identifier: Apache-2.0

"""Small cumulative checker for ordinary single-file Articraft templates.

The checker owns only preflight, persistent seed artifacts and the three public
stages.  It does not author components, extract source closure, validate source
fidelity, render images, or schedule repair Agents.
"""

from __future__ import annotations

import ast
import dataclasses
import hashlib
import importlib
import json
import os
import shutil
import sys
import tempfile
import time
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any, Literal

from agent.compiler import compile_urdf_report_maybe_timeout
from agent.template_axes import DEFAULT_MAX_CORNER_FAILURES, select_corner_seeds
from agent.template_design import TemplateDesign, TemplateDesignError, load_template_design
from agent.template_policy import overlap_policy_result
from agent.template_preflight import (
    category_anchor_wiring_checks,
    check_groups,
    corner_boundary_checks,
    derivation_checks,
    design_alignment_checks,
    domain_resolution_checks,
    preflight_finding,
    preflight_repair_gate,
    quality_contract,
    source_hygiene_checks,
)
from agent.template_sweep import (
    DEFAULT_COMPILE_TIMEOUT_S,
    DEFAULT_PASS_THRESHOLD,
    SeedOutcome,
    compiled_artifact_is_valid,
    disconnected_geometry_warning_details,
    extract_failure_entities,
    extract_failure_signals,
    joint_motion_edge_coverage,
    run_seed_outcomes,
)
from sdk import CornerCase, TemplateDomain, corner_case

CheckStage = Literal["random-16", "random-36", "corner"]
CHECK_STAGES: tuple[CheckStage, ...] = ("random-16", "random-36", "corner")
_CACHE_SCHEMA = 3
_CHECKER_POLICY = "simple-template-check-v6-contract-semantic-witness"
_FORBIDDEN_RUNTIME_IMPORTS = (
    "source_modules",
    "source_module_runtime",
    "source_bundle_runtime",
    "source_snapshots",
    "articraft.appearance",
    "articraft.materialization",
    "articraft.physics",
)
_SOURCE_REVIEW_POLICY_VERSION = 1
_SOURCE_REVIEW_NOT_REQUIRED_KINDS = {
    "compile_runtime",
    "mesh_assets",
    "missing_exact_geometry",
}
_SOURCE_REVIEW_RECOMMENDED_KINDS = {
    "disconnected_geometry",
    "exact_contact_gap",
    "isolated_part",
    "model_validity",
    "real_overlap",
    "test_failure",
}
_SOURCE_REVIEW_NOT_REQUIRED_FAILURE_PREFIXES = (
    "compile_runtime_failure",
    "compile_timeout",
    "missing_exact_geometry",
    "qc_mesh_assets",
    "subprocess_crash",
    "subprocess_error:",
    "test_missing_exact_geometry",
    "thread_error",
)


class TemplateCheckError(ValueError):
    pass


def _jsonable_config(value: object) -> object:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return dataclasses.asdict(value)
    if isinstance(value, dict):
        return value
    if hasattr(value, "__dict__"):
        return {key: item for key, item in vars(value).items() if not key.startswith("_")}
    return repr(value)


def _template_path(repo_root: Path, slug: str) -> Path:
    return repo_root / "agent" / "templates" / f"{slug}.py"


def _template_imports(path: Path) -> tuple[list[str], list[str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: list[str] = []
    template_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [item.name for item in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        for name in names:
            if name:
                imports.append(name)
            if name.startswith("agent.templates."):
                template_modules.append(name)
    return sorted(set(imports)), sorted(set(template_modules))


def _template_runtime_files(repo_root: Path, slug: str) -> list[Path]:
    """Resolve only direct/recursive template helper imports for cache invalidation.

    This is a millisecond AST import walk, not source-component closure and not
    an authoring artifact.
    """

    pending = [_template_path(repo_root, slug)]
    seen: set[Path] = set()
    while pending:
        path = pending.pop()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        try:
            _imports, modules = _template_imports(path)
        except (OSError, SyntaxError):
            continue
        for module in modules:
            candidate = repo_root.joinpath(*module.split(".")).with_suffix(".py")
            if candidate.is_file() and candidate not in seen:
                pending.append(candidate)
    return sorted(seen)


def mechanical_hash(repo_root: Path, slug: str, stem: str) -> str:
    files = _template_runtime_files(repo_root, slug)
    files.extend(
        path
        for path in (
            repo_root / "agent" / "compiler.py",
            repo_root / "agent" / "template_design.py",
            repo_root / "agent" / "template_preflight.py",
            repo_root / "agent" / "template_policy.py",
            repo_root / "agent" / "template_sweep.py",
            repo_root / "agent" / "template_check.py",
            repo_root / "pyproject.toml",
            repo_root / "uv.lock",
        )
        if path.is_file()
    )
    sdk_root = repo_root / "sdk" / "_core" / "v0"
    if sdk_root.is_dir():
        files.extend(sorted(sdk_root.rglob("*.py")))
    digest = hashlib.sha256()
    digest.update(_CHECKER_POLICY.encode())
    digest.update(stem.encode())
    for path in sorted(set(files)):
        digest.update(str(path.relative_to(repo_root)).encode())
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def _preflight_hash(repo_root: Path, slug: str, stem: str) -> str:
    digest = hashlib.sha256()
    digest.update(_CHECKER_POLICY.encode())
    digest.update(stem.encode())
    paths = [
        _template_path(repo_root, slug),
        repo_root / "articraft_template_authoring" / "designs" / f"{slug}.json",
        Path(__file__),
        Path(__file__).with_name("template_preflight.py"),
        Path(__file__).with_name("template_policy.py"),
        Path(__file__).with_name("template_design.py"),
        repo_root / "sdk" / "_core" / "v0" / "template_domain.py",
        repo_root / "sdk" / "_core" / "v0" / "types.py",
    ]
    design_path = paths[1]
    if design_path.is_file():
        try:
            raw = json.loads(design_path.read_text(encoding="utf-8"))
            source_map_raw = Path(str(raw.get("source_map_path") or ""))
            source_map = (
                source_map_raw if source_map_raw.is_absolute() else repo_root / source_map_raw
            )
            paths.append(source_map)
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    for path in paths:
        digest.update(str(path).encode())
        if path.is_file():
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def _load_preflight_cache(path: Path, fingerprint: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError):
        return None
    if payload.get("schema_version") != 1 or payload.get("preflight_hash") != fingerprint:
        return None
    report = payload.get("report")
    return dict(report) if isinstance(report, dict) else None


def _phase_finding_summary(findings: Iterable[dict[str, Any]]) -> dict[str, Any]:
    blocking_ids: list[str] = []
    advisory_counts: dict[str, int] = {}
    for finding in findings:
        if finding.get("blocking"):
            blocking_ids.append(str(finding.get("finding_id") or ""))
            continue
        code = str(finding.get("code") or "unknown")
        advisory_counts[code] = advisory_counts.get(code, 0) + 1
    return {
        "blocking_finding_ids": blocking_ids,
        "advisory_counts": advisory_counts,
    }


def preflight_template(
    repo_root: Path,
    slug: str,
    stem: str,
    *,
    cache_dir: Path | None = None,
    expected_quality_contract_sha256: str | None = None,
) -> dict[str, Any]:
    path = _template_path(repo_root, slug)
    fingerprint = _preflight_hash(repo_root, slug, stem)
    cache_path = (
        cache_dir / slug / "preflight" / f"{fingerprint}.json" if cache_dir is not None else None
    )
    if cache_path is not None:
        cached = _load_preflight_cache(cache_path, fingerprint)
        if cached is not None:
            cached["cache_hit"] = True
            contract_sha = str((cached.get("quality_contract") or {}).get("sha256") or "")
            if (
                expected_quality_contract_sha256
                and contract_sha != expected_quality_contract_sha256
            ):
                mismatch = preflight_finding(
                    "quality_contract_changed_during_repair",
                    "quality contract changed during sweep repair: "
                    f"expected {expected_quality_contract_sha256}, got {contract_sha}",
                    blocking=True,
                    owner={
                        "expected": expected_quality_contract_sha256,
                        "actual": contract_sha,
                    },
                    next_action="start_explicit_design_change_or_restore_contract",
                )
                cached["findings"] = [
                    row for row in cached.get("findings", []) if row.get("code") != mismatch["code"]
                ] + [mismatch]
                cached["status"] = "fail"
                checks = dict(cached.get("checks") or {})
                alignment = dict(checks.get("design_alignment") or {})
                alignment["status"] = "fail"
                alignment["blocking"] = int(alignment.get("blocking") or 0) + 1
                checks["design_alignment"] = alignment
                cached["checks"] = checks
                phases = dict(cached.get("phases") or {})
                contract_phase = dict(phases.get("contract") or {})
                contract_phase["status"] = "fail"
                contract_phase["blocking_finding_ids"] = list(
                    dict.fromkeys(
                        [
                            *contract_phase.get("blocking_finding_ids", ()),
                            mismatch["finding_id"],
                        ]
                    )
                )
                phases["contract"] = contract_phase
                cached["phases"] = phases
                cached["repair_gate"] = preflight_repair_gate(cached["findings"])
            return cached

    findings: list[dict[str, Any]] = []
    semantic_finding_start: int | None = None
    semantic_details: dict[str, Any] | None = None
    imports: list[str] = []
    template_imports: list[str] = []
    source_tree: ast.Module | None = None
    source_text: str | None = None
    design_path = repo_root / "articraft_template_authoring" / "designs" / f"{slug}.json"
    required = ("config_from_seed", f"build_{stem}", f"run_{stem}_tests")
    check_details: dict[str, dict[str, Any]] = {
        "source_hygiene": {"status": "not_run"},
        "design_alignment": {"status": "not_applicable"},
        "candidate_structure": {"status": "not_applicable"},
        "parameterization": {"status": "not_applicable"},
        "derivations": {"status": "not_applicable"},
        "multiplicity": {"status": "not_applicable"},
        "category_fidelity": {"status": "not_applicable"},
    }
    if not path.is_file():
        findings.append(preflight_finding("template_missing", str(path), blocking=True))
    else:
        try:
            source_text = path.read_text(encoding="utf-8")
            source_tree = ast.parse(source_text, filename=str(path))
            imports, template_imports = _template_imports(path)
        except (OSError, SyntaxError) as exc:
            findings.append(
                preflight_finding(
                    "template_parse_failed",
                    str(exc),
                    blocking=True,
                    location={"path": str(path)},
                )
            )
        hygiene, hygiene_details = source_hygiene_checks(
            path,
            required_exports=required,
            forbid_overlap=design_path.is_file(),
        )
        findings.extend(hygiene)
        check_details["source_hygiene"] = hygiene_details
    for imported in imports:
        if any(token in imported for token in _FORBIDDEN_RUNTIME_IMPORTS):
            findings.append(preflight_finding("forbidden_runtime_import", imported, blocking=True))

    module: object | None = None
    try:
        importlib.invalidate_caches()
        module_name = f"agent.templates.{slug}"
        module = (
            importlib.reload(sys.modules[module_name])
            if module_name in sys.modules
            else importlib.import_module(module_name)
        )
    except Exception as exc:  # noqa: BLE001
        findings.append(
            preflight_finding(
                "template_import_failed",
                f"{type(exc).__name__}: {exc}",
                blocking=True,
            )
        )
    design: TemplateDesign | None = None
    domain: TemplateDomain | None = None
    if module is not None:
        for name in required:
            if not callable(getattr(module, name, None)):
                findings.append(preflight_finding("required_export_missing", name, blocking=True))
        raw_domain = getattr(module, "TEMPLATE_DOMAIN", None)
        domain = raw_domain if isinstance(raw_domain, TemplateDomain) else None
        if design_path.is_file() and not isinstance(raw_domain, TemplateDomain):
            findings.append(
                preflight_finding(
                    "required_export_missing",
                    "TEMPLATE_DOMAIN (required for TemplateDesign templates)",
                    blocking=True,
                )
            )
    if design_path.is_file():
        try:
            design = load_template_design(design_path)
            if design.slug != slug:
                raise TemplateDesignError(
                    f"TemplateDesign slug {design.slug!r} does not match {slug!r}"
                )
        except (OSError, TemplateDesignError, TypeError, ValueError) as exc:
            findings.append(
                preflight_finding(
                    "template_design_invalid",
                    f"{type(exc).__name__}: {exc}",
                    blocking=True,
                    location={"path": str(design_path)},
                )
            )

    contract = quality_contract(design, domain)
    if expected_quality_contract_sha256 and contract["sha256"] != expected_quality_contract_sha256:
        findings.append(
            preflight_finding(
                "quality_contract_changed_during_repair",
                "quality contract changed during sweep repair: "
                f"expected {expected_quality_contract_sha256}, got {contract['sha256']}",
                blocking=True,
                owner={
                    "expected": expected_quality_contract_sha256,
                    "actual": contract["sha256"],
                },
                next_action="start_explicit_design_change_or_restore_contract",
            )
        )

    if design is not None and domain is not None and module is not None and source_tree is not None:
        top_level_functions = {
            node.name
            for node in source_tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        alignment, alignment_details = design_alignment_checks(
            repo_root=repo_root,
            path=path,
            design=design,
            domain=domain,
            top_level_functions=top_level_functions,
        )
        findings.extend(alignment)
        check_details["design_alignment"] = alignment_details
        derivations, derivation_details = derivation_checks(
            design,
            source_text=source_text,
        )
        findings.extend(derivations)
        check_details["derivations"] = derivation_details
        anchors, anchor_details = category_anchor_wiring_checks(
            design=design,
            source_text=source_text,
        )
        findings.extend(anchors)
        check_details["category_fidelity"] = anchor_details
        boundaries, boundary_details = corner_boundary_checks(module=module, design=design)
        findings.extend(boundaries)
        check_details["corner_boundaries"] = boundary_details
        if not any(row["blocking"] for row in findings):
            semantic_finding_start = len(findings)
            semantic, semantic_details = domain_resolution_checks(
                module=module,
                design=design,
                domain=domain,
            )
            findings.extend(semantic)
            check_details["candidate_structure"] = semantic_details["candidate_structure"]
            check_details["parameterization"] = semantic_details["parameterization"]
            check_details["derivations"] = {
                **derivation_details,
                **semantic_details["derivations"],
            }
            check_details["multiplicity"] = (
                semantic_details["multiplicity"]
                if design.multiplicities
                else {"status": "not_applicable"}
            )
        else:
            reason = "blocked by an earlier high-confidence preflight finding"
            check_details["candidate_structure"] = {
                "status": "not_run",
                "reason": reason,
            }
            check_details["parameterization"] = {
                "status": "not_run",
                "reason": reason,
            }
            if design.multiplicities:
                check_details["multiplicity"] = {
                    "status": "not_run",
                    "reason": reason,
                }
    checks = check_groups(findings, check_details)
    contract_findings = (
        findings if semantic_finding_start is None else findings[:semantic_finding_start]
    )
    semantic_findings = [] if semantic_finding_start is None else findings[semantic_finding_start:]
    scan_details = (semantic_details or {}).get("candidate_structure", {}) or {}
    template_mode = (
        "strict"
        if design_path.is_file() and domain is not None
        else "incomplete_migration"
        if design_path.is_file()
        else "legacy"
    )
    report = {
        "status": "fail" if any(row["blocking"] for row in findings) else "pass",
        "template_mode": template_mode,
        "findings": findings,
        "checks": checks,
        "phases": {
            "contract": {
                "status": ("fail" if any(row["blocking"] for row in contract_findings) else "pass"),
                "builds": 0,
                **_phase_finding_summary(contract_findings),
            },
            "domain_resolution": {
                "status": (
                    "not_applicable"
                    if not design_path.is_file()
                    else "not_run"
                    if semantic_finding_start is None
                    else "fail"
                    if any(row["blocking"] for row in semantic_findings)
                    else "pass"
                ),
                "builds": 0,
                "scanned_seeds": scan_details.get("scanned_seeds"),
                "saturated": scan_details.get("saturated"),
                "declared_values": scan_details.get("declared_values"),
                "reached_values": scan_details.get("reached_values"),
                "declared_pairs": scan_details.get("declared_pairs"),
                "reached_pairs": scan_details.get("reached_pairs"),
                **_phase_finding_summary(semantic_findings),
            },
        },
        "repair_gate": preflight_repair_gate(findings),
        "quality_contract": contract,
        "template_imports": template_imports,
        "single_file_status": "self_contained" if not template_imports else "legacy_compatible",
        "preflight_hash": fingerprint,
        "cache_hit": False,
    }
    if cache_path is not None:
        _atomic_json(
            cache_path,
            {
                "schema_version": 1,
                "preflight_hash": fingerprint,
                "report": report,
            },
        )
    return report


def _function_source_index(path: Path, repo_root: Path) -> dict[str, Any]:
    """Index ordinary functions and their string literals in one template file."""

    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError):
        return {"path": str(path), "functions": {}, "literal_functions": {}}
    try:
        display_path = str(path.relative_to(repo_root))
    except ValueError:
        display_path = str(path)
    functions: dict[str, dict[str, Any]] = {}
    literal_functions: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        functions[node.name] = {
            "function": node.name,
            "path": display_path,
            "line": node.lineno,
            "end_line": getattr(node, "end_lineno", node.lineno),
        }
        for child in ast.walk(node):
            if isinstance(child, ast.Constant) and isinstance(child.value, str):
                literal_functions.setdefault(child.value, set()).add(node.name)
    return {
        "path": display_path,
        "functions": functions,
        "literal_functions": {
            literal: sorted(names) for literal, names in literal_functions.items()
        },
    }


def _load_repair_design(repo_root: Path, slug: str) -> tuple[TemplateDesign | None, dict[str, Any]]:
    path = repo_root / "articraft_template_authoring" / "designs" / f"{slug}.json"
    try:
        display_path = str(path.relative_to(repo_root))
    except ValueError:
        display_path = str(path)
    if not path.is_file():
        return None, {
            "status": "undeclared",
            "path": display_path,
            "reason": "TemplateDesign is optional for legacy templates",
        }
    try:
        design = load_template_design(path)
    except (OSError, TemplateDesignError, TypeError, ValueError) as exc:
        return None, {
            "status": "invalid",
            "path": display_path,
            "reason": f"{type(exc).__name__}: {exc}",
        }
    if design.slug != slug:
        return None, {
            "status": "invalid",
            "path": display_path,
            "reason": f"TemplateDesign slug {design.slug!r} does not match {slug!r}",
        }
    return design, {"status": "available", "path": display_path}


def _failure_entries(outcome: SeedOutcome) -> list[dict[str, Any]]:
    entries = [dict(entry) for entry in outcome.failures]
    if not entries and outcome.failure_type is not None:
        details = outcome.failure_details or ""
        entries = [
            {
                "check": outcome.failure_type,
                "check_normalized": outcome.failure_type_normalized or outcome.failure_type,
                "kind": "unknown",
                "code": outcome.failure_type,
                "summary": outcome.failure_type,
                "source": "harness",
                "group": "qc",
                "details": details,
                "entities": extract_failure_entities(details),
            }
        ]
    for entry in entries:
        details = str(entry.get("details") or "")
        check = str(entry.get("check") or outcome.failure_type or "unknown_failure")
        entry.setdefault("check", check)
        entry.setdefault(
            "check_normalized",
            outcome.failure_type_normalized or check.split("(", 1)[0].strip(),
        )
        entry.setdefault("kind", "unknown")
        entry.setdefault("code", check)
        entry.setdefault("summary", check)
        entry.setdefault("source", "harness")
        entry.setdefault("group", "qc")
        if not isinstance(entry.get("entities"), dict):
            entry["entities"] = extract_failure_entities(details)
    return entries


def _merge_failure_entities(entries: Iterable[dict[str, Any]]) -> dict[str, Any]:
    simple = {name: set() for name in ("parts", "joints", "elements")}
    pairs: set[tuple[str, str]] = set()
    poses: list[dict[str, Any]] = []
    locations: list[dict[str, Any]] = []
    for entry in entries:
        entities = entry.get("entities")
        if not isinstance(entities, dict):
            continue
        for name in simple:
            simple[name].update(str(item) for item in entities.get(name) or ())
        for pair in entities.get("pairs") or ():
            if isinstance(pair, (list, tuple)) and len(pair) == 2:
                pairs.add(tuple(sorted((str(pair[0]), str(pair[1])))))
        for pose in entities.get("poses") or ():
            if isinstance(pose, dict) and pose not in poses:
                poses.append(dict(pose))
        for location in entities.get("locations") or ():
            if isinstance(location, dict) and location not in locations:
                locations.append(dict(location))
    return {
        "parts": sorted(simple["parts"]),
        "joints": sorted(simple["joints"]),
        "elements": sorted(simple["elements"]),
        "pairs": [list(pair) for pair in sorted(pairs)],
        "poses": poses,
        "locations": locations,
    }


def _json_identity(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)


def _failure_signature(entry: dict[str, Any]) -> tuple[Any, ...]:
    entities = _merge_failure_entities([entry])
    locations = tuple(
        (str(item.get("path") or ""), int(item.get("line") or 0)) for item in entities["locations"]
    )
    return (
        str(entry.get("check_normalized") or entry.get("check") or "unknown_failure"),
        tuple(entities["parts"]),
        tuple(entities["joints"]),
        tuple(entities["elements"]),
        locations,
    )


def _config_evidence(
    failed_outcomes: list[SeedOutcome], all_outcomes: list[SeedOutcome]
) -> dict[str, Any]:
    passing = [outcome for outcome in all_outcomes if outcome.verdict == "pass"]
    keys = sorted({key for outcome in failed_outcomes for key in outcome.config})
    common: dict[str, Any] = {}
    varying: list[str] = []
    correlations: list[dict[str, Any]] = []
    missing = object()
    for key in keys:
        values = [outcome.config.get(key, missing) for outcome in failed_outcomes]
        identities = {_json_identity(value) for value in values}
        if len(identities) != 1 or values[0] is missing:
            varying.append(key)
            continue
        value = values[0]
        common[key] = value
        passing_same = sum(
            key in outcome.config and _json_identity(outcome.config[key]) == _json_identity(value)
            for outcome in passing
        )
        correlations.append(
            {
                "field": key,
                "value": value,
                "failed_with_value": len(failed_outcomes),
                "passing_with_value": passing_same,
            }
        )
    correlations.sort(key=lambda row: (row["passing_with_value"], row["field"]))
    representative = min(failed_outcomes, key=lambda outcome: outcome.seed)
    nearest: dict[str, Any] | None = None
    if passing:
        candidates: list[tuple[int, int, SeedOutcome, list[str]]] = []
        for outcome in passing:
            compared_keys = sorted(set(representative.config) | set(outcome.config))
            differing = [
                key
                for key in compared_keys
                if _json_identity(representative.config.get(key, missing))
                != _json_identity(outcome.config.get(key, missing))
            ]
            candidates.append((len(differing), outcome.seed, outcome, differing))
        distance, _seed, outcome, differing = min(candidates, key=lambda item: (item[0], item[1]))
        nearest = {
            "seed": outcome.seed,
            "config_distance": distance,
            "differing_fields": differing,
            "config": outcome.config,
        }
    return {
        "note": "Config evidence is correlation for repair triage, not proof of causality.",
        "representative_failed_seed": representative.seed,
        "representative_failed_config": representative.config,
        "nearest_passing": nearest,
        "common_failed_values": common,
        "varying_fields": varying,
        "correlations": correlations,
    }


def _function_for_line(functions: dict[str, dict[str, Any]], line: int) -> str | None:
    matches = [
        (int(info["end_line"]) - int(info["line"]), name)
        for name, info in functions.items()
        if int(info["line"]) <= line <= int(info["end_line"])
    ]
    return min(matches)[1] if matches else None


def _repair_code_owners(
    *,
    entities: dict[str, Any],
    representative: SeedOutcome,
    design: TemplateDesign | None,
    source_index: dict[str, Any],
    stem: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    functions: dict[str, dict[str, Any]] = source_index["functions"]
    literal_functions: dict[str, list[str]] = source_index["literal_functions"]
    entities_flat = {
        *entities["parts"],
        *entities["joints"],
        *entities["elements"],
    }
    candidates_by_function: dict[str, list[tuple[str, Any]]] = {}
    selected_context: list[dict[str, Any]] = []
    if design is not None:
        for slot in design.slots:
            selected = representative.config.get(slot.name)
            for candidate in slot.candidates:
                candidates_by_function.setdefault(candidate.implementation_function, []).append(
                    (slot.name, candidate)
                )
                if selected is not None and str(selected) == candidate.name:
                    info = functions.get(candidate.implementation_function, {})
                    selected_context.append(
                        {
                            "slot": slot.name,
                            "candidate": candidate.name,
                            "function": candidate.implementation_function,
                            "path": info.get("path", source_index["path"]),
                            "line": info.get("line"),
                            "record_id": candidate.record_id,
                            "revision": candidate.revision,
                            "source_spans": list(candidate.source_spans),
                        }
                    )

    reasons: dict[str, set[str]] = {}
    for location in entities["locations"]:
        path = str(location.get("path") or "")
        if path.endswith(source_index["path"]) or path.endswith(Path(source_index["path"]).name):
            function = _function_for_line(functions, int(location.get("line") or 0))
            if function is not None:
                reasons.setdefault(function, set()).add("runtime_traceback")
    for entity in entities_flat:
        for function in literal_functions.get(entity, ()):
            reasons.setdefault(function, set()).add(f"entity_literal:{entity}")
    if design is not None:
        for function, candidate_rows in candidates_by_function.items():
            for slot_name, candidate in candidate_rows:
                prefixes = (
                    f"{slot_name}__{candidate.name}__",
                    f"{slot_name}_{candidate.name}_",
                )
                if any(entity.startswith(prefixes) for entity in entities_flat):
                    reasons.setdefault(function, set()).add("owned_name_prefix")
                interface_parts = {interface.part for interface in candidate.interfaces}
                if entities_flat & interface_parts:
                    reasons.setdefault(function, set()).add("declared_interface_part")

    owners: list[dict[str, Any]] = []
    for function in sorted(reasons):
        base_info = dict(
            functions.get(function) or {"function": function, "path": source_index["path"]}
        )
        candidate_rows = candidates_by_function.get(function, [])
        selected_rows = [
            (slot_name, candidate)
            for slot_name, candidate in candidate_rows
            if str(representative.config.get(slot_name)) == candidate.name
        ]
        resolved_rows = selected_rows or (candidate_rows if len(candidate_rows) == 1 else [])
        if not resolved_rows:
            resolved_rows = [(None, None)]
        for slot_name, candidate in resolved_rows:
            info = dict(base_info)
            if slot_name is not None and candidate is not None:
                info.update(
                    {
                        "slot": slot_name,
                        "candidate": candidate.name,
                        "record_id": candidate.record_id,
                        "revision": candidate.revision,
                        "source_spans": list(candidate.source_spans),
                    }
                )
            info["reasons"] = sorted(reasons[function])
            info["confidence"] = "exact" if "runtime_traceback" in reasons[function] else "strong"
            owners.append(info)

    if len({owner.get("slot") for owner in owners if owner.get("slot")}) > 1:
        assembly_name = f"build_{stem}"
        if assembly_name in functions:
            assembly = dict(functions[assembly_name])
            assembly.update(
                {
                    "reasons": ["cross_component_failure_context"],
                    "confidence": "context",
                }
            )
            owners.append(assembly)
    return owners, selected_context


def _source_targets_for_owners(
    owners: Iterable[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    targets: dict[tuple[str, str, str, str, tuple[str, ...]], dict[str, Any]] = {}
    unresolved: dict[tuple[str, str], dict[str, str]] = {}
    for owner in owners:
        slot = str(owner.get("slot") or "")
        candidate = str(owner.get("candidate") or "")
        if not slot or not candidate:
            continue
        record_id = str(owner.get("record_id") or "")
        revision = str(owner.get("revision") or "")
        source_spans = tuple(str(item) for item in owner.get("source_spans") or ())
        if not record_id or not revision or not source_spans:
            unresolved[(slot, candidate)] = {
                "slot": slot,
                "candidate": candidate,
            }
            continue
        key = (slot, candidate, record_id, revision, source_spans)
        targets[key] = {
            "slot": slot,
            "candidate": candidate,
            "record_id": record_id,
            "revision": revision,
            "source_spans": list(source_spans),
        }
    return (
        [targets[key] for key in sorted(targets)],
        [unresolved[key] for key in sorted(unresolved)],
    )


def _source_review_classification(
    *,
    check: str,
    failure_kind: str,
    failure_code: str,
    entities: dict[str, Any],
    suggested_scope: str,
) -> tuple[str, list[str]]:
    normalized = check.casefold().replace("-", "_").replace(" ", "_")
    kind = failure_kind.casefold()
    code = failure_code.casefold().replace("-", "_").replace(" ", "_")
    if kind in _SOURCE_REVIEW_NOT_REQUIRED_KINDS or normalized.startswith(
        _SOURCE_REVIEW_NOT_REQUIRED_FAILURE_PREFIXES
    ):
        return "not_required", ["implementation_or_infrastructure_failure"]

    required_reasons: list[str] = []
    if "interface_mate" in normalized or "interface_mate" in code:
        required_reasons.append("rotational_interface_contract")
    if "articulation_origin" in normalized or "articulation_origin" in code:
        required_reasons.append("articulation_origin_contract")
    if any(
        token in normalized
        for token in (
            "axis_contract",
            "joint_axis",
            "rotation_axis",
            "rotational_axis",
            "wheel_center_axis",
        )
    ):
        required_reasons.append("rotational_axis_contract")
    if kind == "single_root_policy" or any(
        token in normalized for token in ("joint_topology", "articulation_topology")
    ):
        required_reasons.append("joint_topology_contract")
    if kind == "model_validity" and entities.get("joints"):
        required_reasons.append("joint_topology_contract")
    if required_reasons:
        return "required", sorted(set(required_reasons))

    recommended_reasons: list[str] = []
    if kind in _SOURCE_REVIEW_RECOMMENDED_KINDS:
        recommended_reasons.append("mechanical_intent_may_need_source_evidence")
    if "motion_qc" in normalized or entities.get("poses"):
        recommended_reasons.append("motion_or_swept_clearance_failure")
    if entities.get("pairs") or suggested_scope == "assembly_or_interface":
        recommended_reasons.append("cross_component_or_contact_failure")
    if entities.get("joints"):
        recommended_reasons.append("joint_involved")
    if recommended_reasons:
        return "recommended", sorted(set(recommended_reasons))
    return "not_required", ["local_implementation_failure"]


def _source_review_policy(
    *,
    first: dict[str, Any],
    entities: dict[str, Any],
    owners: list[dict[str, Any]],
    selected_context: list[dict[str, Any]],
    suggested_scope: str,
    design_status: dict[str, Any],
) -> dict[str, Any]:
    check = str(first.get("check_normalized") or first.get("check") or "unknown_failure")
    decision, reason_codes = _source_review_classification(
        check=check,
        failure_kind=str(first.get("kind") or ""),
        failure_code=str(first.get("code") or ""),
        entities=entities,
        suggested_scope=suggested_scope,
    )
    source_targets, unresolved_owners = _source_targets_for_owners(owners)
    # Joint names are commonly authored in the assembly function while the
    # source-backed mechanical intent belongs to the selected slot candidates.
    # A strict Design already carries those exact record/revision/span links;
    # use them as a conservative fallback instead of declaring the mapping
    # unresolved merely because the assembly literal has no candidate owner.
    if decision == "required" and not source_targets and selected_context:
        source_targets, unresolved_owners = _source_targets_for_owners(selected_context)
    design_state = design_status.get("status")
    design_available = design_state == "available"
    legacy_template = design_state == "undeclared"

    if decision == "required" and legacy_template:
        return {
            "version": _SOURCE_REVIEW_POLICY_VERSION,
            "decision": "recommended",
            "blocking": False,
            "reason_codes": sorted({*reason_codes, "legacy_source_mapping_unavailable"}),
            "source_targets": source_targets,
            "unresolved_owners": unresolved_owners,
            "next_action": "review_source_if_available_then_repair",
        }

    if decision == "required":
        mapping_incomplete = not design_available or bool(unresolved_owners) or not source_targets
        return {
            "version": _SOURCE_REVIEW_POLICY_VERSION,
            "decision": "required",
            "blocking": True,
            "reason_codes": sorted(
                {
                    *reason_codes,
                    *(("source_target_unresolved",) if mapping_incomplete else ()),
                }
            ),
            "source_targets": source_targets,
            "unresolved_owners": unresolved_owners,
            "next_action": (
                "repair_source_mapping_before_template"
                if mapping_incomplete
                else "review_source_then_repair"
            ),
        }

    if decision == "recommended":
        return {
            "version": _SOURCE_REVIEW_POLICY_VERSION,
            "decision": "recommended",
            "blocking": False,
            "reason_codes": reason_codes,
            "source_targets": source_targets,
            "unresolved_owners": unresolved_owners,
            "next_action": "repair_or_review_source_if_intent_unclear",
        }
    return {
        "version": _SOURCE_REVIEW_POLICY_VERSION,
        "decision": "not_required",
        "blocking": False,
        "reason_codes": reason_codes,
        "source_targets": source_targets,
        "unresolved_owners": unresolved_owners,
        "next_action": "repair_directly",
    }


def _repair_gate(findings: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(findings)
    if not rows:
        return {
            "version": _SOURCE_REVIEW_POLICY_VERSION,
            "status": "not_needed",
            "blocking": False,
            "blocking_finding_ids": [],
            "source_targets": [],
            "next_action": "none",
        }
    blocking = [
        finding
        for finding in rows
        if bool((finding.get("source_review_policy") or {}).get("blocking"))
    ]
    targets: dict[str, dict[str, Any]] = {}
    for finding in blocking:
        policy = finding.get("source_review_policy") or {}
        for target in policy.get("source_targets") or ():
            identity = _json_identity(target)
            targets[identity] = dict(target)
    return {
        "version": _SOURCE_REVIEW_POLICY_VERSION,
        "status": "source_review_required" if blocking else "repair_allowed",
        "blocking": bool(blocking),
        "blocking_finding_ids": [str(finding.get("finding_id") or "") for finding in blocking],
        "source_targets": [targets[key] for key in sorted(targets)],
        "next_action": (
            "complete_source_review_before_repair"
            if blocking
            else "repair_highest_priority_finding"
        ),
    }


def _attach_quality_contract(
    gate: dict[str, Any],
    contract: dict[str, Any],
) -> dict[str, Any]:
    return {
        **gate,
        "quality_contract": {
            "version": contract.get("version"),
            "sha256": contract.get("sha256"),
        },
        "repair_rerun": {
            "stage": "random-16",
            "expected_quality_contract_sha256": contract.get("sha256"),
        },
    }


def build_repair_findings(
    *, repo_root: Path, slug: str, stem: str, outcomes: list[SeedOutcome]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build ephemeral, deterministic repair navigation for one cumulative sweep."""

    failed_outcomes = [outcome for outcome in outcomes if outcome.verdict != "pass"]
    design, design_status = _load_repair_design(repo_root, slug)
    source_index = _function_source_index(_template_path(repo_root, slug), repo_root)
    groups: dict[tuple[Any, ...], list[tuple[SeedOutcome, dict[str, Any]]]] = {}
    for outcome in failed_outcomes:
        seen_for_seed: set[tuple[Any, ...]] = set()
        for entry in _failure_entries(outcome):
            signature = _failure_signature(entry)
            if signature in seen_for_seed:
                continue
            seen_for_seed.add(signature)
            groups.setdefault(signature, []).append((outcome, entry))

    findings: list[dict[str, Any]] = []
    for signature, rows in groups.items():
        group_outcomes = list({outcome.seed: outcome for outcome, _entry in rows}.values())
        entries = [entry for _outcome, entry in rows]
        entities = _merge_failure_entities(entries)
        evidence = _config_evidence(group_outcomes, outcomes)
        representative_seed = int(evidence["representative_failed_seed"])
        representative = next(
            outcome for outcome in group_outcomes if outcome.seed == representative_seed
        )
        owners, selected_context = _repair_code_owners(
            entities=entities,
            representative=representative,
            design=design,
            source_index=source_index,
            stem=stem,
        )
        owner_slots = {owner.get("slot") for owner in owners if owner.get("slot")}
        if any("runtime_traceback" in owner.get("reasons", ()) for owner in owners):
            suggested_scope = "runtime_function"
        elif len(owner_slots) > 1:
            suggested_scope = "assembly_or_interface"
        elif owners:
            suggested_scope = "component_function"
        elif entities["pairs"]:
            suggested_scope = "assembly_or_interface"
        elif entities["joints"]:
            suggested_scope = "joint_or_assembly"
        else:
            suggested_scope = "template"
        finding_key = _json_identity(signature)
        finding_id = hashlib.sha1(finding_key.encode()).hexdigest()[:12]
        first = entries[0]
        finding = {
            "finding_id": finding_id,
            "check": first.get("check"),
            "check_normalized": first.get("check_normalized"),
            "failure_kind": first.get("kind"),
            "failure_code": first.get("code"),
            "affected_seed_count": len(group_outcomes),
            "affected_seeds": sorted(outcome.seed for outcome in group_outcomes),
            "entities": entities,
            "config_evidence": evidence,
            "code_owners": owners,
            "selected_component_context": selected_context,
            "suggested_scope": suggested_scope,
            "representative_details": str(first.get("details") or "")[:2000],
        }
        finding["source_review_policy"] = _source_review_policy(
            first=first,
            entities=entities,
            owners=owners,
            selected_context=selected_context,
            suggested_scope=suggested_scope,
            design_status=design_status,
        )
        findings.append(finding)
    findings.sort(
        key=lambda finding: (
            -int(finding["affected_seed_count"]),
            str(finding.get("check_normalized") or ""),
            str(finding["finding_id"]),
        )
    )
    for priority, finding in enumerate(findings, start=1):
        finding["repair_priority"] = priority
    return findings, {
        "status": "available" if failed_outcomes else "not_needed",
        "design": design_status,
        "template_path": source_index["path"],
        "finding_count": len(findings),
        "note": (
            "Findings are deterministic single-run repair navigation; they are not "
            "persistent clusters, sampling-domain edits, or proof of Config causality."
        ),
    }


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as stream:
        json.dump(payload, stream, indent=2, sort_keys=True, default=str, ensure_ascii=False)
        stream.write("\n")
        temporary = Path(stream.name)
    temporary.replace(path)


def _load_cached_outcome(path: Path, mechanical: str) -> SeedOutcome | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("schema_version") != _CACHE_SCHEMA:
            return None
        if payload.get("mechanical_hash") != mechanical:
            return None
        outcome = SeedOutcome.from_dict(payload["outcome"])
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None
    if outcome.verdict == "pass" and not compiled_artifact_is_valid(outcome.artifact_dir):
        return None
    return outcome


def _cached_seed_sweep(
    *,
    repo_root: Path,
    slug: str,
    stem: str,
    seeds: list[int],
    mechanical: str,
    cache_root: Path,
    max_workers: int | None,
    compile_timeout_s: float,
    progress: Callable[[SeedOutcome], None] | None,
) -> tuple[list[SeedOutcome], list[int], list[int], float]:
    outcomes: dict[int, SeedOutcome] = {}
    hits: list[int] = []
    misses: list[int] = []
    outcome_root = cache_root / "outcomes"
    for seed in seeds:
        cached = _load_cached_outcome(outcome_root / f"seed_{seed}.json", mechanical)
        if cached is None:
            misses.append(seed)
        else:
            hits.append(seed)
            outcomes[seed] = cached
    started = time.monotonic()
    fresh = (
        run_seed_outcomes(
            slug=slug,
            stem=stem,
            seeds=misses,
            repo_root=repo_root,
            max_workers=max_workers,
            compile_timeout_s=compile_timeout_s,
            motion_qc=True,
            artifact_root=cache_root / "artifacts",
            progress=progress,
        )
        if misses
        else []
    )
    for outcome in fresh:
        outcomes[outcome.seed] = outcome
        _atomic_json(
            outcome_root / f"seed_{outcome.seed}.json",
            {
                "schema_version": _CACHE_SCHEMA,
                "mechanical_hash": mechanical,
                "outcome": outcome.to_dict(),
            },
        )
    return [outcomes[seed] for seed in seeds], hits, misses, time.monotonic() - started


def _motion_reports(outcomes: Iterable[SeedOutcome]) -> list[dict[str, Any] | None]:
    return [outcome.motion_qc_report for outcome in outcomes if outcome.verdict == "pass"]


def candidate_pass_coverage(
    domain: TemplateDomain | None,
    outcomes: Iterable[SeedOutcome],
) -> dict[str, Any]:
    """Split the swept outcomes by declared candidate and gate on zero-pass candidates.

    The cumulative threshold is a whole-sweep ratio, so a candidate that fails in
    every seed it reaches still clears the stage whenever it is rare enough: a
    candidate drawn by exactly one of seeds 0-15 hides under random-16's single
    tolerated failure, and one drawn by three of seeds 0-35 hides under random-36's
    three.  Re-reading the same outcomes per candidate closes that hole without
    compiling anything extra -- every seed counted here was already built by the
    sweep.

    A candidate the sweep never drew is reported as ``uncovered`` rather than
    failed; the corner stage owns candidates absent from cumulative seeds 0-35.
    """
    if domain is None:
        return {
            "status": "not_applicable",
            "reason": "legacy template has no TEMPLATE_DOMAIN",
            "candidates": [],
        }
    seen: list[SeedOutcome] = list(outcomes)
    rows: list[dict[str, Any]] = []
    for slot in domain.slots:
        for value in slot.values:
            reached = [item for item in seen if item.config.get(slot.name) == value]
            passing = [item.seed for item in reached if item.verdict == "pass"]
            failing = [item.seed for item in reached if item.verdict != "pass"]
            if not reached:
                status = "uncovered"
            elif passing:
                status = "pass"
            else:
                status = "no_passing_seed"
            rows.append(
                {
                    "slot": slot.name,
                    "kind": slot.kind,
                    "candidate": value,
                    "status": status,
                    "seeds": sorted(item.seed for item in reached),
                    "passing_seeds": sorted(passing),
                    "failing_seeds": sorted(failing),
                    "passed": len(passing),
                    "failed": len(failing),
                    "pass_rate": round(len(passing) / len(reached), 6) if reached else None,
                }
            )
    broken = [row for row in rows if row["status"] == "no_passing_seed"]
    uncovered = [row for row in rows if row["status"] == "uncovered"]
    report: dict[str, Any] = {
        "status": "fail" if broken else "pass",
        "candidates": rows,
        "declared": len(rows),
        "covered": len(rows) - len(uncovered),
        "uncovered": [f"{row['slot']}.{row['candidate']}" for row in uncovered],
        "no_passing_seed": [f"{row['slot']}.{row['candidate']}" for row in broken],
    }
    if broken:
        parts = ", ".join(
            f"{row['slot']}.{row['candidate']} (0/{row['failed']} seeds pass: "
            f"{row['failing_seeds']})"
            for row in broken
        )
        report["reason"] = (
            f"candidate(s) with no passing seed: {parts}. The whole-sweep pass "
            "threshold cannot absolve a candidate that fails everywhere it is "
            "drawn; repair the candidate rather than relying on its rarity."
        )
    return report


def _random_summary(
    *,
    seeds: list[int],
    outcomes: list[SeedOutcome],
    hits: list[int],
    misses: list[int],
    elapsed_s: float,
    pass_threshold: float,
    repo_root: Path | None = None,
    slug: str | None = None,
    stem: str | None = None,
    domain: TemplateDomain | None = None,
) -> dict[str, Any]:
    failed = [outcome for outcome in outcomes if outcome.verdict != "pass"]
    pass_rate = (len(outcomes) - len(failed)) / len(outcomes)
    motion_coverage = joint_motion_edge_coverage(_motion_reports(outcomes))
    candidate_coverage = candidate_pass_coverage(domain, outcomes)
    threshold_pass = pass_rate >= pass_threshold
    repair_findings: list[dict[str, Any]] = []
    repair_localization: dict[str, Any] = {
        "status": "not_available",
        "reason": "repo_root/slug/stem were not supplied",
        "finding_count": 0,
    }
    if repo_root is not None and slug is not None and stem is not None:
        repair_findings, repair_localization = build_repair_findings(
            repo_root=repo_root,
            slug=slug,
            stem=stem,
            outcomes=outcomes,
        )
    return {
        "status": (
            "pass"
            if threshold_pass
            and motion_coverage["status"] == "pass"
            and candidate_coverage["status"] != "fail"
            else "fail"
        ),
        "threshold_pass": threshold_pass,
        "seeds": seeds,
        "passed": len(outcomes) - len(failed),
        "failed": len(failed),
        "pass_rate": round(pass_rate, 6),
        "pass_threshold": pass_threshold,
        "failed_outcomes": [outcome.to_dict() for outcome in failed],
        "repair_findings": repair_findings,
        "repair_localization": repair_localization,
        "repair_gate": _repair_gate(repair_findings),
        "cache_hits": len(hits),
        "cache_misses": len(misses),
        "cache_hit_seeds": hits,
        "new_seeds": misses,
        "compiled_artifacts": sum(
            compiled_artifact_is_valid(outcome.artifact_dir) for outcome in outcomes
        ),
        "joint_motion_coverage": motion_coverage,
        "candidate_coverage": candidate_coverage,
        "elapsed_s": round(elapsed_s, 3),
    }


def _domain_report(module: object) -> tuple[TemplateDomain | None, dict[str, Any]]:
    domain = getattr(module, "TEMPLATE_DOMAIN", None)
    if domain is None:
        return None, {
            "status": "undeclared",
            "core_domain": None,
            "raw_domain": None,
            "reason": "legacy template has no TEMPLATE_DOMAIN",
        }
    if not isinstance(domain, TemplateDomain):
        raise TemplateCheckError("TEMPLATE_DOMAIN must be sdk.TemplateDomain")
    return domain, dict(domain.audit())


def _domain_value_key(value: object) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)


def _missing_domain_corner_cases(
    domain: TemplateDomain,
    random_outcomes: Iterable[SeedOutcome],
) -> tuple[tuple[CornerCase, ...], dict[str, Any]]:
    """Return only candidate/N-edge cases absent from the cumulative random sweep."""

    observed: dict[str, set[str]] = {slot.name: set() for slot in domain.slots}
    for outcome in random_outcomes:
        for slot in domain.slots:
            if slot.name in outcome.config:
                observed[slot.name].add(_domain_value_key(outcome.config[slot.name]))

    cases: list[CornerCase] = []
    slot_reports: dict[str, dict[str, Any]] = {}
    for slot in domain.slots:
        required = (
            tuple(slot.values)
            if slot.kind == "component"
            else tuple(dict.fromkeys((min(slot.values), max(slot.values))))
        )
        missing = [
            value for value in required if _domain_value_key(value) not in observed[slot.name]
        ]
        slot_reports[slot.name] = {
            "kind": slot.kind,
            "required": list(required),
            "observed": [
                value for value in slot.values if _domain_value_key(value) in observed[slot.name]
            ],
            "missing": list(missing),
        }
        for value in missing:
            completed = domain.complete({slot.name: value})
            label = "candidate" if slot.kind == "component" else "edge"
            cases.append(
                corner_case(
                    f"{label}_{slot.name}_{value}",
                    completed,
                    reason=(
                        f"cumulative random-36 did not exercise {slot.kind} {slot.name}={value!r}"
                    ),
                )
            )
    return tuple(cases), {
        "status": "complete" if not cases else "supplemented",
        "slots": slot_reports,
        "supplemental_case_count": len(cases),
    }


def _materialize_corner_config(
    module: object,
    domain: TemplateDomain,
    case: CornerCase,
) -> tuple[object, dict[str, object]]:
    sampled_base = module.config_from_seed(0)  # type: ignore[attr-defined]
    if not dataclasses.is_dataclass(sampled_base) or isinstance(sampled_base, type):
        raise TemplateCheckError("TEMPLATE_DOMAIN corners require a dataclass Config")
    try:
        base = type(sampled_base)()
    except TypeError:
        base = sampled_base
    field_names = {item.name for item in dataclasses.fields(base)}
    missing = sorted(set(domain.slot_names) - field_names)
    if missing:
        raise TemplateCheckError("TEMPLATE_DOMAIN slots missing from Config: " + ", ".join(missing))
    explicit = dict(case.overrides)
    base_domain = {name: getattr(base, name) for name in domain.slot_names}
    domain_overrides = {
        name: value for name, value in explicit.items() if name in domain.slot_names
    }
    completed = domain.complete(domain_overrides, preferred=base_domain)
    replacements = {**completed, **explicit}
    domain.validate({name: replacements[name] for name in domain.slot_names})
    unknown = sorted(set(replacements) - field_names)
    if unknown:
        raise TemplateCheckError(
            f"corner {case.name!r} overrides unknown Config fields: {', '.join(unknown)}"
        )
    return dataclasses.replace(base, **replacements), replacements


def _corner_script(
    slug: str,
    stem: str,
    replacements: dict[str, object],
    *,
    config_payload: dict[str, object] | None = None,
) -> str:
    config_line = (
        f"CONFIG = _template.Config(**{config_payload!r})"
        if config_payload is not None
        else f"CONFIG = dataclasses.replace(BASE, **{replacements!r})"
    )
    return "\n".join(
        (
            "from __future__ import annotations",
            "import dataclasses",
            f"import agent.templates.{slug} as _template",
            "from sdk import AssetContext",
            "TEMPLATE_DOMAIN = _template.TEMPLATE_DOMAIN",
            "BASE = _template.config_from_seed(0)",
            config_line,
            "ASSETS = AssetContext.from_script(__file__)",
            "def build_object_model():",
            f"    return _template.build_{stem}(CONFIG, assets=ASSETS)",
            "object_model = build_object_model()",
            "def run_tests():",
            f"    return _template.run_{stem}_tests(object_model, CONFIG)",
            "",
        )
    )


def _run_domain_corner(
    *,
    repo_root: Path,
    slug: str,
    stem: str,
    module: object,
    domain: TemplateDomain,
    case: CornerCase,
    corner_root: Path,
    compile_timeout_s: float,
) -> tuple[dict[str, Any], bool]:
    started = time.monotonic()
    config, replacements = _materialize_corner_config(module, domain, case)
    config_payload = _jsonable_config(config)
    case_hash = hashlib.sha256(
        json.dumps(
            {
                "name": case.name,
                "replacements": replacements,
                "config": config_payload,
            },
            sort_keys=True,
            default=str,
        ).encode()
    ).hexdigest()
    case_dir = corner_root / case_hash
    result_path = case_dir / "result.json"
    try:
        cached = json.loads(result_path.read_text(encoding="utf-8"))
        if cached.get("schema_version") != _CACHE_SCHEMA:
            raise KeyError("stale cache")
        outcome = dict(cached["outcome"])
        if outcome.get("status") == "pass":
            if not compiled_artifact_is_valid(case_dir):
                raise KeyError("corner artifact missing")
        return outcome, True
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        pass

    with tempfile.TemporaryDirectory(prefix=f"corner_{slug}_{case.name}_") as raw:
        work_dir = Path(raw)
        script = work_dir / "model.py"
        script.write_text(
            _corner_script(
                slug,
                stem,
                replacements,
                config_payload=config_payload,
            ),
            encoding="utf-8",
        )
        previous_timeout = os.environ.get("URDF_COMPILE_TIMEOUT_SECONDS")
        os.environ["URDF_COMPILE_TIMEOUT_SECONDS"] = str(max(0.0, compile_timeout_s))
        try:
            report = compile_urdf_report_maybe_timeout(
                script,
                sdk_package="sdk",
                run_checks=True,
                target="full",
                rewrite_visual_glb=False,
                motion_qc=True,
            )
            overlap_policy = overlap_policy_result(
                repo_root=repo_root,
                slug=slug,
                allowances=getattr(
                    getattr(report, "test_report", None),
                    "allowances",
                    (),
                ),
            )
            if overlap_policy["detail"] is not None:
                raise RuntimeError(overlap_policy["detail"])
            disconnected = disconnected_geometry_warning_details(report.warnings)
            if disconnected:
                raise RuntimeError(disconnected)
            coverage = joint_motion_edge_coverage([report.motion_qc_report])
            if coverage["status"] != "pass":
                raise RuntimeError(f"joint edge coverage incomplete: {coverage['missing_edges']}")
        except Exception as exc:  # noqa: BLE001
            outcome = {
                "name": case.name,
                "status": "fail",
                "config": config_payload,
                "overrides": replacements,
                "reason": case.reason,
                "error": f"{type(exc).__name__}: {exc}",
                "failures": extract_failure_signals(exc),
                "joint_motion_coverage": locals().get(
                    "coverage", {"status": "not_run", "joints": [], "missing_edges": []}
                ),
                "elapsed_s": round(time.monotonic() - started, 3),
            }
        else:
            if case_dir.exists():
                shutil.rmtree(case_dir)
            shutil.copytree(work_dir, case_dir)
            (case_dir / "model.urdf").write_text(report.urdf_xml, encoding="utf-8")
            (case_dir / "artifact.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "slug": slug,
                        "case": case.name,
                        "urdf_sha256": hashlib.sha256(report.urdf_xml.encode()).hexdigest(),
                    },
                    indent=2,
                    sort_keys=True,
                )
                + "\n",
                encoding="utf-8",
            )
            outcome = {
                "name": case.name,
                "status": "pass",
                "config": config_payload,
                "overrides": replacements,
                "reason": case.reason,
                "error": None,
                "failures": [],
                "artifact_dir": str(case_dir.resolve()),
                "joint_motion_coverage": coverage,
                "elapsed_s": round(time.monotonic() - started, 3),
            }
        finally:
            if previous_timeout is None:
                os.environ.pop("URDF_COMPILE_TIMEOUT_SECONDS", None)
            else:
                os.environ["URDF_COMPILE_TIMEOUT_SECONDS"] = previous_timeout
    _atomic_json(result_path, {"schema_version": _CACHE_SCHEMA, "outcome": outcome})
    return outcome, False


def _domain_corner_stage(
    *,
    repo_root: Path,
    slug: str,
    stem: str,
    module: object,
    domain: TemplateDomain,
    random_outcomes: Iterable[SeedOutcome],
    cache_root: Path,
    compile_timeout_s: float,
) -> dict[str, Any]:
    authored = getattr(module, "TEMPLATE_CORNERS", ()) or ()
    if not isinstance(authored, (tuple, list)) or not all(
        isinstance(item, CornerCase) for item in authored
    ):
        raise TemplateCheckError("TEMPLATE_CORNERS must contain sdk.CornerCase values")
    supplemental, coverage = _missing_domain_corner_cases(domain, random_outcomes)
    cases = (*supplemental, *tuple(authored))
    names = [case.name for case in cases]
    if len(names) != len(set(names)):
        raise TemplateCheckError("supplemental and authored corner names must be unique")
    outcomes: list[dict[str, Any]] = []
    hits = 0
    for case in cases:
        outcome, hit = _run_domain_corner(
            repo_root=repo_root,
            slug=slug,
            stem=stem,
            module=module,
            domain=domain,
            case=case,
            corner_root=cache_root / "corners",
            compile_timeout_s=compile_timeout_s,
        )
        outcomes.append(outcome)
        hits += int(hit)
    failed = [item for item in outcomes if item.get("status") != "pass"]
    repair_outcomes = [
        SeedOutcome(
            seed=index,
            verdict="pass" if item.get("status") == "pass" else "fail",
            config=dict(item.get("config") or item.get("overrides") or {}),
            failure_type=(
                None
                if item.get("status") == "pass"
                else str(item.get("error") or "corner_case_failure")
            ),
            failure_type_normalized=(
                None if item.get("status") == "pass" else "corner_case_failure"
            ),
            failure_details=(
                None if item.get("status") == "pass" else str(item.get("error") or "")
            ),
            elapsed_s=float(item.get("elapsed_s") or 0.0),
            failures=tuple(dict(entry) for entry in item.get("failures") or ()),
        )
        for index, item in enumerate(outcomes)
    ]
    repair_findings, repair_localization = build_repair_findings(
        repo_root=repo_root,
        slug=slug,
        stem=stem,
        outcomes=repair_outcomes,
    )
    case_names = {index: str(item.get("name") or index) for index, item in enumerate(outcomes)}
    for finding in repair_findings:
        affected_indexes = list(finding.pop("affected_seeds"))
        finding["affected_cases"] = [case_names[index] for index in affected_indexes]
        finding["affected_case_count"] = finding.pop("affected_seed_count")
        config_evidence = finding["config_evidence"]
        representative_index = config_evidence.pop("representative_failed_seed")
        config_evidence["representative_failed_case"] = case_names[representative_index]
        nearest = config_evidence.get("nearest_passing")
        if isinstance(nearest, dict):
            nearest["case"] = case_names[int(nearest.pop("seed"))]
    return {
        "status": "pass" if not failed else "fail",
        "kind": "domain_cases",
        "cases": outcomes,
        "passed": len(outcomes) - len(failed),
        "failed": len(failed),
        "cache_hits": hits,
        "cache_misses": len(outcomes) - hits,
        "coverage": coverage,
        "supplemental_cases": [case.to_dict() for case in supplemental],
        "authored_case_count": len(authored),
        "repair_findings": repair_findings,
        "repair_localization": repair_localization,
        "repair_gate": _repair_gate(repair_findings),
    }


def _legacy_corner_stage(
    *,
    repo_root: Path,
    slug: str,
    stem: str,
    mechanical: str,
    cache_root: Path,
    max_workers: int | None,
    compile_timeout_s: float,
    progress: Callable[[SeedOutcome], None] | None,
) -> dict[str, Any]:
    plan = select_corner_seeds(slug, base_seeds=list(range(36)))
    if plan.status != "ok" or not plan.seeds:
        return {
            "status": "pass" if plan.status != "error" else "fail",
            "kind": "reachable_seed_corners",
            "plan": plan.to_dict(),
            "cases": [],
            "cache_hits": 0,
            "cache_misses": 0,
            "repair_findings": [],
            "repair_gate": _repair_gate(()),
        }
    outcomes, hits, misses, elapsed = _cached_seed_sweep(
        repo_root=repo_root,
        slug=slug,
        stem=stem,
        seeds=plan.seeds,
        mechanical=mechanical,
        cache_root=cache_root,
        max_workers=max_workers,
        compile_timeout_s=compile_timeout_s,
        progress=progress,
    )
    failed = [outcome for outcome in outcomes if outcome.verdict != "pass"]
    coverage = joint_motion_edge_coverage(_motion_reports(outcomes))
    repair_findings, repair_localization = build_repair_findings(
        repo_root=repo_root,
        slug=slug,
        stem=stem,
        outcomes=outcomes,
    )
    return {
        "status": (
            "pass"
            if len(failed) <= DEFAULT_MAX_CORNER_FAILURES and coverage["status"] == "pass"
            else "fail"
        ),
        "kind": "reachable_seed_corners",
        "plan": plan.to_dict(),
        "cases": [outcome.to_dict() for outcome in outcomes],
        "passed": len(outcomes) - len(failed),
        "failed": len(failed),
        "max_failures": DEFAULT_MAX_CORNER_FAILURES,
        "cache_hits": len(hits),
        "cache_misses": len(misses),
        "joint_motion_coverage": coverage,
        "repair_findings": repair_findings,
        "repair_localization": repair_localization,
        "repair_gate": _repair_gate(repair_findings),
        "elapsed_s": round(elapsed, 3),
    }


def check_template(
    *,
    repo_root: Path,
    slug: str,
    stem: str,
    stage: CheckStage,
    cache_dir: Path | None = None,
    pass_threshold: float = DEFAULT_PASS_THRESHOLD,
    max_workers: int | None = None,
    compile_timeout_s: float = DEFAULT_COMPILE_TIMEOUT_S,
    progress: Callable[[SeedOutcome], None] | None = None,
    expected_quality_contract_sha256: str | None = None,
) -> dict[str, Any]:
    if stage not in CHECK_STAGES:
        raise TemplateCheckError(f"unsupported stage {stage!r}")
    started = time.monotonic()
    repo_root = repo_root.resolve()
    cache_base = (cache_dir or repo_root / ".cache" / "template_check").resolve()
    preflight = preflight_template(
        repo_root,
        slug,
        stem,
        cache_dir=cache_base,
        expected_quality_contract_sha256=expected_quality_contract_sha256,
    )
    if preflight["status"] != "pass":
        template_mode = str(preflight.get("template_mode") or "legacy")
        return {
            "schema_version": 1,
            "slug": slug,
            "stage": stage,
            "verdict": "fail",
            "template_mode": template_mode,
            "completion_status": (
                "incomplete_migration" if template_mode == "incomplete_migration" else "failed"
            ),
            "preflight": preflight,
            "random_sweep": {},
            "corner_stage": {},
            "diversity": {"status": "not_run"},
            "next_stage": "preflight",
            "elapsed_s": round(time.monotonic() - started, 3),
        }
    module = importlib.import_module(f"agent.templates.{slug}")
    template_mode = str(preflight.get("template_mode") or "legacy")
    domain, diversity = _domain_report(module)
    mechanical = mechanical_hash(repo_root, slug, stem)
    cache_root = cache_base / slug / mechanical
    seed_count = 16 if stage == "random-16" else 36
    seeds = list(range(seed_count))
    outcomes, hits, misses, elapsed = _cached_seed_sweep(
        repo_root=repo_root,
        slug=slug,
        stem=stem,
        seeds=seeds,
        mechanical=mechanical,
        cache_root=cache_root,
        max_workers=max_workers,
        compile_timeout_s=compile_timeout_s,
        progress=progress,
    )
    effective_pass_threshold = (
        max(float(pass_threshold), DEFAULT_PASS_THRESHOLD)
        if template_mode == "strict"
        else float(pass_threshold)
    )
    random_summary = _random_summary(
        seeds=seeds,
        outcomes=outcomes,
        hits=hits,
        misses=misses,
        elapsed_s=elapsed,
        pass_threshold=effective_pass_threshold,
        repo_root=repo_root,
        slug=slug,
        stem=stem,
        domain=domain,
    )
    contract = dict(preflight.get("quality_contract") or {"version": 1, "sha256": ""})
    random_summary["repair_gate"] = _attach_quality_contract(
        random_summary["repair_gate"],
        contract,
    )
    corner_summary: dict[str, Any] = {"status": "not_run"}
    if stage == "corner" and random_summary["status"] == "pass":
        corner_summary = (
            _domain_corner_stage(
                repo_root=repo_root,
                slug=slug,
                stem=stem,
                module=module,
                domain=domain,
                random_outcomes=outcomes,
                cache_root=cache_root,
                compile_timeout_s=compile_timeout_s,
            )
            if domain is not None
            else _legacy_corner_stage(
                repo_root=repo_root,
                slug=slug,
                stem=stem,
                mechanical=mechanical,
                cache_root=cache_root,
                max_workers=max_workers,
                compile_timeout_s=compile_timeout_s,
                progress=progress,
            )
        )
    elif stage == "corner":
        corner_summary = {
            "status": "blocked",
            "reason": "random-36 must meet the pass threshold before corner",
        }
    if isinstance(corner_summary.get("repair_gate"), dict):
        corner_summary["repair_gate"] = _attach_quality_contract(
            corner_summary["repair_gate"],
            contract,
        )
    verdict = random_summary["status"]
    if stage == "corner":
        verdict = "pass" if verdict == "pass" and corner_summary.get("status") == "pass" else "fail"
    next_stage = {
        "random-16": "random-36" if verdict == "pass" else "random-16",
        "random-36": "corner" if verdict == "pass" else "random-36",
        "corner": "complete" if verdict == "pass" else "corner",
    }[stage]
    if verdict != "pass":
        completion_status = "failed"
    elif template_mode != "strict":
        completion_status = "legacy_compatible"
    elif stage == "random-16":
        completion_status = "strict_random_16_pass"
    elif stage == "random-36":
        completion_status = "strict_random_36_pass"
    else:
        completion_status = (
            "strict_ready"
            if int(random_summary.get("failed") or 0) == 0
            else "strict_ready_with_tolerance"
        )
    return {
        "schema_version": 1,
        "slug": slug,
        "stage": stage,
        "verdict": verdict,
        "template_mode": template_mode,
        "completion_status": completion_status,
        "pass_threshold_policy": {
            "requested": float(pass_threshold),
            "effective": effective_pass_threshold,
            "strict_minimum": DEFAULT_PASS_THRESHOLD,
        },
        "preflight": preflight,
        "random_sweep": random_summary,
        "corner_stage": corner_summary,
        "diversity": diversity,
        "cache": {
            "mechanical_hash": mechanical,
            "root": str(cache_root),
        },
        "next_stage": next_stage,
        "elapsed_s": round(time.monotonic() - started, 3),
    }


__all__ = [
    "CHECK_STAGES",
    "CheckStage",
    "TemplateCheckError",
    "build_repair_findings",
    "candidate_pass_coverage",
    "check_template",
    "mechanical_hash",
    "preflight_template",
]
