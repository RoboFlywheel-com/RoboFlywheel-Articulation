# SPDX-License-Identifier: Apache-2.0

"""Seed-quality preflight checks for ordinary single-file templates.

The checks in this module are authoring-time diagnostics.  They may import and
build a template, but they never participate in normal seed construction.
Only high-confidence output regressions are blocking; stale navigation metadata
and low-confidence static smells remain warnings.
"""

from __future__ import annotations

import ast
import dataclasses
import hashlib
import json
import re
import threading
from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from agent.template_design import ParameterDesign, TemplateDesign
from agent.template_policy import overlap_policy_result
from sdk import (
    TemplateDomain,
)

_QUALITY_CONTRACT_VERSION = 1
_INDEX_TOKEN = re.compile(r"(?<![A-Za-z])\d+(?![A-Za-z])")
# Tier 0-B walks the sampler until the declared domain saturates.  Bounds only
# guard a pathological sampler: `config_from_seed` + `resolve_config` cost
# microseconds (the winch's 864-combination core domain resolves in ~0.11 s), so
# these are nothing like the wall-clock budget the build probe used to carry.
_DOMAIN_SCAN_MAX_SEEDS = 4000
_DOMAIN_SCAN_PATIENCE = 400
# Reachability saturates the moment a candidate is seen once; parameter response
# does not.  A candidate observed a single time makes every one of its parameters
# look constant, so the scan keeps going until each candidate has been drawn this
# many times, and constancy is only reported for candidates that reach the floor.
_MIN_CANDIDATE_OBSERVATIONS = 4
_MIN_AUTHORED_CONTACT_TOL_M = 0.0005
_PROBE_PATCH_LOCK = threading.RLock()


def _json_identity(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str)


def _finding(
    code: str,
    detail: str,
    *,
    blocking: bool,
    confidence: str = "high",
    location: dict[str, Any] | None = None,
    owner: dict[str, Any] | None = None,
    next_action: str | None = None,
) -> dict[str, Any]:
    identity = _json_identity(
        {
            "code": code,
            "detail": detail,
            "location": location or {},
            "owner": owner or {},
        }
    )
    return {
        "finding_id": hashlib.sha1(identity.encode()).hexdigest()[:12],
        "code": code,
        "severity": "error" if blocking else "warning",
        "blocking": blocking,
        "confidence": confidence,
        "detail": detail,
        "location": dict(location or {}),
        "owner": dict(owner or {}),
        "next_action": next_action
        or (
            "repair_template_then_rerun_preflight"
            if blocking
            else "review_when_editing_related_code"
        ),
    }


def preflight_finding(
    code: str,
    detail: str,
    *,
    blocking: bool,
    confidence: str = "high",
    location: dict[str, Any] | None = None,
    owner: dict[str, Any] | None = None,
    next_action: str | None = None,
) -> dict[str, Any]:
    return _finding(
        code,
        detail,
        blocking=blocking,
        confidence=confidence,
        location=location,
        owner=owner,
        next_action=next_action,
    )


def _check_summary(
    findings: Iterable[dict[str, Any]],
    *,
    details: dict[str, Any] | None = None,
    not_applicable: bool = False,
) -> dict[str, Any]:
    rows = list(findings)
    blocking = [row for row in rows if row["blocking"]]
    warnings = [row for row in rows if not row["blocking"]]
    payload = dict(details or {})
    detail_status = payload.pop("status", None)
    if blocking:
        status = "fail"
    elif not_applicable:
        status = "not_applicable"
    elif detail_status in {"not_run", "not_applicable", "warn"}:
        status = detail_status
    else:
        status = "pass"
    return {
        "status": status,
        "blocking": len(blocking),
        "warnings": len(warnings),
        **payload,
    }


def _bound_names(node: ast.AST) -> list[str]:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return [node.name]
    if isinstance(node, (ast.Assign, ast.AnnAssign)):
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        return [target.id for target in targets if isinstance(target, ast.Name)]
    return []


def source_hygiene_checks(
    path: Path, *, required_exports: tuple[str, ...], forbid_overlap: bool = False
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError):
        return findings, {"status": "unavailable"}

    definitions: dict[str, list[tuple[int, str]]] = defaultdict(list)
    functions: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
    for node in tree.body:
        for name in _bound_names(node):
            definitions[name].append((getattr(node, "lineno", 0), type(node).__name__))
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.setdefault(node.name, node)

    for name, rows in sorted(definitions.items()):
        definition_rows = [
            row for row in rows if row[1] in {"FunctionDef", "AsyncFunctionDef", "ClassDef"}
        ]
        required_overwrite = name in required_exports and len(rows) > 1
        duplicate_definition = len(definition_rows) > 1
        if not required_overwrite and not duplicate_definition:
            continue
        locations = [line for line, _kind in rows]
        code = (
            "required_export_overwritten"
            if required_overwrite
            else "duplicate_top_level_definition"
        )
        findings.append(
            _finding(
                code,
                f"top-level name {name!r} is defined multiple times at lines {locations}",
                blocking=True,
                location={"path": str(path), "lines": locations},
                owner={"symbol": name},
            )
        )

    top_level_values: dict[str, ast.AST] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    top_level_values[target.id] = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.value is not None:
                top_level_values[node.target.id] = node.value

    # Track references through top-level values as well as direct calls.  This
    # keeps ordinary dispatch tables such as
    # `_BUILDERS = {"a": _build_a}` connected to the exported build function
    # that indexes `_BUILDERS`, without treating an unused registry as live.
    symbol_nodes: dict[str, ast.AST] = {**top_level_values, **functions}
    symbol_names = set(symbol_nodes)
    references: dict[str, set[str]] = {}
    for name, node in symbol_nodes.items():
        references[name] = {
            child.id
            for child in ast.walk(node)
            if isinstance(child, ast.Name)
            and isinstance(child.ctx, ast.Load)
            and child.id in symbol_names
            and child.id != name
        }
    roots = {
        name
        for name in (
            *required_exports,
            "resolve_config",
            "slot_choices_for_seed",
            "slot_choices_for_config",
        )
        if name in symbol_nodes
    }
    reachable_symbols = set(roots)
    pending = list(roots)
    while pending:
        name = pending.pop()
        for child in references.get(name, ()):
            if child not in reachable_symbols:
                reachable_symbols.add(child)
                pending.append(child)
    dead = sorted(
        name
        for name in functions
        if name.startswith("_") and not name.startswith("__") and name not in reachable_symbols
    )
    for name in dead:
        findings.append(
            _finding(
                "dead_private_code",
                f"private function {name!r} is not statically reachable from template exports",
                blocking=False,
                confidence="low",
                location={"path": str(path), "line": functions[name].lineno},
                owner={"symbol": name},
            )
        )
    micro_contact_tolerances: list[dict[str, Any]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for keyword in node.keywords:
            if keyword.arg != "contact_tol":
                continue
            try:
                value = ast.literal_eval(keyword.value)
            except (ValueError, TypeError):
                continue
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or float(value) >= _MIN_AUTHORED_CONTACT_TOL_M
            ):
                continue
            row = {
                "line": getattr(keyword.value, "lineno", getattr(node, "lineno", 0)),
                "value": float(value),
            }
            micro_contact_tolerances.append(row)
            findings.append(
                _finding(
                    "micro_contact_tolerance",
                    (
                        f"explicit contact_tol={float(value):g} m is below the "
                        "0.5 mm author-test default"
                    ),
                    blocking=False,
                    location={"path": str(path), "line": row["line"]},
                    owner={"symbol": "contact_tol"},
                    next_action=("use_0.0005_or_document_collision_geometry_precision_need"),
                )
            )
    if forbid_overlap:
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            called_name = (
                node.func.attr
                if isinstance(node.func, ast.Attribute)
                else node.func.id
                if isinstance(node.func, ast.Name)
                else ""
            )
            if called_name != "allow_overlap":
                continue
            policy = overlap_policy_result(
                repo_root=path.parent,
                slug=path.stem,
                allowances=("allow_overlap()",),
                design_backed=forbid_overlap,
                location={"path": str(path), "line": getattr(node, "lineno", 0)},
                owner={"symbol": "allow_overlap"},
            )
            if policy["finding"] is not None:
                findings.append(policy["finding"])
    return findings, {
        "status": "pass" if not any(row["blocking"] for row in findings) else "fail",
        "top_level_symbols": len(definitions),
        "dead_private_functions": dead,
        "overlap_policy": "forbidden" if forbid_overlap else "legacy_compatible",
        "micro_contact_tolerances": micro_contact_tolerances,
    }


def _parameter_contract(parameter: ParameterDesign) -> dict[str, Any]:
    return {
        "name": parameter.name,
        "mode": parameter.mode,
        "value_type": parameter.value_type,
        "unit": parameter.unit,
        "minimum": parameter.minimum,
        "maximum": parameter.maximum,
        "choices": list(parameter.choices),
        "expression": parameter.expression,
        "depends_on": list(parameter.depends_on),
    }


def quality_contract(
    design: TemplateDesign | None, domain: TemplateDomain | None
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "domain": [
            {
                "name": slot.name,
                "kind": slot.kind,
                "values": list(slot.values),
                "item_slot": slot.item_slot or None,
            }
            for slot in (domain.slots if domain is not None else ())
        ],
        "design": None,
    }
    if design is not None:
        payload["design"] = {
            "slots": [
                {
                    "name": slot.name,
                    "component_type": slot.component_type,
                    "required": slot.required,
                    "candidates": [
                        {
                            "name": candidate.name,
                            "parameters": [
                                _parameter_contract(parameter) for parameter in candidate.parameters
                            ],
                            "interfaces": [
                                {
                                    "name": interface.name,
                                    "kind": interface.kind,
                                    "role": interface.role,
                                    "part": interface.part,
                                    "frame": interface.frame,
                                    "dimensions": interface.dimensions,
                                    "surface_relation": (
                                        dataclasses.asdict(interface.surface_relation)
                                        if interface.surface_relation is not None
                                        else None
                                    ),
                                }
                                for interface in candidate.interfaces
                            ],
                        }
                        for candidate in slot.candidates
                    ],
                }
                for slot in design.slots
            ],
            "multiplicities": [
                {
                    "name": item.name,
                    "item_slot": item.item_slot,
                    "values": list(item.values),
                    "spacing_expression": item.spacing_expression,
                    "host_capacity_expression": item.host_capacity_expression,
                }
                for item in design.multiplicities
            ],
            "bindings": [
                {
                    "binding_id": binding.binding_id,
                    "provider": binding.provider,
                    "consumer": binding.consumer,
                    "joint_type": binding.joint_type,
                    "derived": [_parameter_contract(parameter) for parameter in binding.derived],
                }
                for binding in design.bindings
            ],
            "category_anchors": [dataclasses.asdict(anchor) for anchor in design.category_anchors],
        }
    encoded = _json_identity(payload).encode()
    return {
        "version": _QUALITY_CONTRACT_VERSION,
        "sha256": hashlib.sha256(encoded).hexdigest(),
    }


def _source_map_path(repo_root: Path, design: TemplateDesign) -> Path:
    raw = Path(design.source_map_path)
    return raw if raw.is_absolute() else repo_root / raw


def design_alignment_checks(
    *,
    repo_root: Path,
    path: Path,
    design: TemplateDesign,
    domain: TemplateDomain,
    top_level_functions: set[str],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    design_components = {
        slot.name: [candidate.name for candidate in slot.candidates] for slot in design.slots
    }
    runtime_components = {
        slot.name: list(slot.values) for slot in domain.slots if slot.kind == "component"
    }
    runtime_multiplicity = {
        slot.name: list(slot.values) for slot in domain.slots if slot.kind == "multiplicity"
    }
    runtime_multiplicity_item_slots = {
        slot.name: slot.item_slot or None for slot in domain.slots if slot.kind == "multiplicity"
    }
    if design_components != runtime_components:
        findings.append(
            _finding(
                "design_runtime_component_domain_mismatch",
                f"TemplateDesign component domain {design_components!r} does not match "
                f"TEMPLATE_DOMAIN {runtime_components!r}",
                blocking=True,
                owner={"design": design.slug},
            )
        )
    mismatched_item_slots = {
        item.name: {
            "design_item_slot": item.item_slot,
            "runtime_item_slot": runtime_multiplicity_item_slots.get(item.name),
        }
        for item in design.multiplicities
        if runtime_multiplicity_item_slots.get(item.name) != item.item_slot
    }
    if mismatched_item_slots:
        findings.append(
            _finding(
                "design_runtime_multiplicity_item_slot_mismatch",
                "TemplateDesign multiplicity item_slot bindings do not match "
                f"TEMPLATE_DOMAIN: {mismatched_item_slots!r}",
                blocking=True,
                owner={
                    "design": design.slug,
                    "multiplicity_item_slots": mismatched_item_slots,
                },
            )
        )
    source_map = _source_map_path(repo_root, design)
    if not source_map.is_file():
        findings.append(
            _finding(
                "source_map_unavailable",
                f"TemplateDesign source map is unavailable: {source_map}",
                blocking=False,
                location={"path": str(source_map)},
            )
        )
    else:
        actual = hashlib.sha256(source_map.read_bytes()).hexdigest()
        if actual != design.source_map_sha256:
            findings.append(
                _finding(
                    "source_map_hash_stale",
                    "TemplateDesign source_map_sha256 is stale; runtime probes remain authoritative",
                    blocking=False,
                    location={"path": str(source_map)},
                    owner={"expected": design.source_map_sha256, "actual": actual},
                )
            )
    stale_functions = sorted(
        {
            candidate.implementation_function
            for slot in design.slots
            for candidate in slot.candidates
            if candidate.implementation_function not in top_level_functions
        }
    )
    for function in stale_functions:
        findings.append(
            _finding(
                "implementation_function_stale",
                f"TemplateDesign implementation_function {function!r} is not a top-level function",
                blocking=False,
                location={"path": str(path)},
                owner={"function": function},
            )
        )
    return findings, {
        "status": "fail" if any(row["blocking"] for row in findings) else "pass",
        "component_slots": runtime_components,
        "multiplicity": runtime_multiplicity,
        "multiplicity_item_slots": runtime_multiplicity_item_slots,
        "stale_implementation_functions": stale_functions,
    }


def derivation_checks(
    design: TemplateDesign,
    *,
    source_text: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    groups: list[tuple[str, tuple[ParameterDesign, ...]]] = []
    for slot in design.slots:
        for candidate in slot.candidates:
            groups.append((f"{slot.name}.{candidate.name}", candidate.parameters))
    for binding in design.bindings:
        groups.append((f"binding.{binding.binding_id}", binding.derived))

    derived_count = 0
    for owner, parameters in groups:
        derived = {item.name: item for item in parameters if item.mode == "derived"}
        derived_count += len(derived)
        if source_text is not None:
            for item in derived.values():
                if re.search(rf"\b{re.escape(item.name)}\b", source_text) is None:
                    findings.append(
                        _finding(
                            "derived_parameter_source_name_unresolved",
                            f"{owner}.{item.name} is not statically named in the template; "
                            "runtime binding probes remain authoritative",
                            blocking=False,
                            confidence="low",
                            owner={"parameter": item.name, "scope": owner},
                        )
                    )
        for item in parameters:
            if item.mode == "independent" and item.value_type in {"float", "int"} and not item.unit:
                findings.append(
                    _finding(
                        "parameter_unit_missing",
                        f"{owner}.{item.name} has no semantic unit",
                        blocking=False,
                        owner={"parameter": item.name, "scope": owner},
                    )
                )
        graph = {
            name: {dependency for dependency in item.depends_on if dependency in derived}
            for name, item in derived.items()
        }
        for name, dependencies in graph.items():
            if name in dependencies or name in derived[name].depends_on:
                findings.append(
                    _finding(
                        "derived_parameter_self_dependency",
                        f"{owner}.{name} depends on itself",
                        blocking=True,
                        owner={"parameter": name, "scope": owner},
                    )
                )
        temporary: set[str] = set()
        permanent: set[str] = set()

        def visit(name: str, trail: tuple[str, ...]) -> None:
            if name in permanent:
                return
            if name in temporary:
                cycle = " -> ".join((*trail, name))
                findings.append(
                    _finding(
                        "derived_parameter_cycle",
                        f"{owner} derived DAG contains a cycle: {cycle}",
                        blocking=True,
                        owner={"scope": owner},
                    )
                )
                return
            temporary.add(name)
            for child in graph.get(name, ()):
                visit(child, (*trail, name))
            temporary.remove(name)
            permanent.add(name)

        for name in graph:
            visit(name, ())
    return findings, {
        "status": "fail" if any(row["blocking"] for row in findings) else "pass",
        "derived_parameters": derived_count,
    }


def category_anchor_wiring_checks(
    *,
    design: TemplateDesign,
    source_text: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Tier 0-A: the anchors' author checks must exist in the template, statically.

    The role-count and role/joint-relation semantics are *enforced* by those named
    author checks, and the sweep runs the template's author tests inside every
    built sample, on real geometry.  Re-deriving the same relations here from a
    stub-mesh probe build duplicated that work against worse inputs.  What is left
    is the part the sweep cannot see: whether the check the Design names is
    actually present in the file.
    """
    if not design.category_anchors:
        finding = _finding(
            "category_anchors_missing",
            "Design-backed template has no category_anchors; existing templates are "
            "not forced to migrate",
            blocking=False,
            confidence="low",
            owner={"design": design.slug},
            next_action="declare_category_anchors_when_the_template_is_next_rebuilt",
        )
        return [finding], {"status": "not_declared", "anchors": []}

    try:
        tree = ast.parse(source_text)
    except SyntaxError:
        return [], {"status": "unavailable"}
    names: set[str] = set()
    patterns: list[re.Pattern[str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            names.add(node.value)
        elif isinstance(node, ast.JoinedStr):
            # A per-item check name is normally interpolated -- e.g.
            # `f"drawer {index} pulls forward out of the carcass"`.  Match the
            # literal skeleton so an f-string counts as wiring the check.
            parts = [
                re.escape(item.value)
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
                else ".+?"
                for item in node.values
            ]
            if any(part != ".+?" for part in parts):
                patterns.append(re.compile("".join(parts) + r"\Z"))

    def wired(name: str) -> bool:
        return name in names or any(pattern.match(name) for pattern in patterns)

    findings: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for anchor in design.category_anchors:
        missing = sorted(name for name in anchor.required_author_checks if not wired(name))
        rows.append(
            {
                "anchor_id": anchor.anchor_id,
                "slot": anchor.applies_to.slot,
                "candidates": list(anchor.applies_to.candidates),
                "required_author_checks": list(anchor.required_author_checks),
                "missing_author_checks": missing,
                "status": "fail" if missing else "pass",
            }
        )
        if missing:
            findings.append(
                _finding(
                    "category_anchor_author_check_missing",
                    f"{anchor.anchor_id} names author check(s) that do not appear in the "
                    f"template: {missing!r}",
                    blocking=True,
                    owner={"anchor_id": anchor.anchor_id, "checks": missing},
                    next_action="emit_the_named_check_or_correct_the_design",
                )
            )
    return findings, {
        "status": "fail" if any(row["status"] == "fail" for row in rows) else "pass",
        "mode": "static_author_check_wiring",
        "anchors": rows,
    }


def corner_boundary_checks(
    *,
    module: Any,
    design: TemplateDesign,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Tier 0-A: declared numeric ranges must have an authored corner at an edge.

    Preflight used to build each candidate at one deterministic far numeric
    boundary.  That build is gone, and the corner stage is where boundaries
    belong -- its overrides already accept any Config field, not just domain
    slots (`_materialize_corner_config`).  What preflight can still do for free
    is check that the boundary is actually *authored*, so removing the probe does
    not silently leave the edge untested.
    """
    edges: dict[str, set[float]] = {}
    for slot in design.slots:
        for candidate in slot.candidates:
            for parameter in candidate.parameters:
                if parameter.mode != "independent":
                    continue
                if parameter.minimum is None or parameter.maximum is None:
                    continue
                if parameter.minimum == parameter.maximum:
                    continue
                bucket = edges.setdefault(parameter.name, set())
                bucket.add(float(parameter.minimum))
                bucket.add(float(parameter.maximum))
    if not edges:
        return [], {"status": "not_applicable", "reason": "no bounded independent parameters"}

    authored = getattr(module, "TEMPLATE_CORNERS", ()) or ()
    at_edge: set[str] = set()
    named_only: set[str] = set()
    for case in authored:
        for name, value in getattr(case, "overrides", ()) or ():
            key = str(name)
            if key not in edges:
                continue
            named_only.add(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                if any(abs(float(value) - edge) <= 1e-12 for edge in edges[key]):
                    at_edge.add(key)
    uncovered = sorted(set(edges) - at_edge)
    findings: list[dict[str, Any]] = []
    if uncovered:
        findings.append(
            _finding(
                "corner_numeric_boundary_unauthored",
                f"{len(uncovered)} bounded parameter(s) have no TEMPLATE_CORNERS override at a "
                f"declared edge: {', '.join(uncovered[:8])}",
                blocking=False,
                confidence="medium",
                owner={
                    "uncovered": uncovered,
                    "overridden_but_not_at_an_edge": sorted(named_only - at_edge),
                },
                next_action="author_a_corner_case_at_the_declared_edge",
            )
        )
    return findings, {
        "status": "warn" if uncovered else "pass",
        "bounded_parameters": sorted(edges),
        "at_declared_edge": sorted(at_edge),
        "uncovered": uncovered,
    }


def _slot_value_label(value: Any) -> str:
    return value if isinstance(value, str) else repr(value)


def _scan_domain(
    *,
    module: Any,
    domain: TemplateDomain,
    max_seeds: int,
    patience: int,
) -> dict[str, Any]:
    """Walk the sampler until the declared domain saturates; resolve every config.

    Enumeration goes through ``config_from_seed`` and never through
    ``dataclasses.replace``.  Candidate-local parameter bands make a
    hand-assembled combination something the sampler cannot emit -- swapping
    ``post_form`` while holding seed 0's ``gear_teeth`` produces 36 of the guitar
    tuner's 72 core combinations as ``ValueError``, none of which any seed can
    reproduce.  A scan reports what the sampler can actually reach.
    """
    component = [slot for slot in domain.slots if slot.kind == "component"]
    multiplicity = [slot for slot in domain.slots if slot.kind == "multiplicity"]
    want_values = {slot.name: {_slot_value_label(v) for v in slot.values} for slot in domain.slots}
    want_pairs: set[tuple[str, str, str, str]] = set()
    for index, left in enumerate(component):
        for right in component[index + 1 :]:
            for lv in left.values:
                for rv in right.values:
                    want_pairs.add(
                        (left.name, _slot_value_label(lv), right.name, _slot_value_label(rv))
                    )
    # Item-candidate x N stays a separate, blocking obligation: it is the one
    # combination class the sampler is contractually required to reach, and the
    # code name predates this tier.
    want_mult_pairs: set[tuple[str, str, str, str]] = set()
    for slot in multiplicity:
        item = next((s for s in component if s.name == slot.item_slot), None)
        if item is None:
            continue
        for iv in item.values:
            for nv in slot.values:
                want_mult_pairs.add(
                    (item.name, _slot_value_label(iv), slot.name, _slot_value_label(nv))
                )

    seen_values: dict[str, set[str]] = {slot.name: set() for slot in domain.slots}
    seen_pairs: set[tuple[str, str, str, str]] = set()
    seen_mult_pairs: set[tuple[str, str, str, str]] = set()
    # Resolved values of every field, bucketed by the slot choice in force, so a
    # candidate-local parameter is judged constant only over the seeds that
    # actually select its owning candidate.
    field_values: dict[tuple[str, str, str], set[str]] = {}
    observations: dict[tuple[str, str], int] = {}
    sample_failures: list[dict[str, Any]] = []
    resolve_failures: dict[str, dict[str, Any]] = {}
    # A template without `resolve_config` still gets reachability; only the
    # resolution half of the tier is unavailable, and saying so beats reporting
    # one `domain_combination_unresolvable` per scanned seed.
    resolver = getattr(module, "resolve_config", None)
    if not callable(resolver):
        resolver = None
    scanned = 0
    since_new = 0
    saturated = False
    for seed in range(max_seeds):
        scanned = seed + 1
        try:
            config = module.config_from_seed(seed)
        except Exception as exc:  # noqa: BLE001 - a sampler that raises is the finding
            if len(sample_failures) < 5:
                sample_failures.append(
                    {"seed": seed, "error_kind": type(exc).__name__, "error": str(exc)[:400]}
                )
            continue
        choices = {
            slot.name: _slot_value_label(getattr(config, slot.name, None)) for slot in domain.slots
        }
        fresh = False
        for name, value in choices.items():
            if value in want_values.get(name, set()) and value not in seen_values[name]:
                seen_values[name].add(value)
                fresh = True
        for index, left in enumerate(component):
            for right in component[index + 1 :]:
                key = (left.name, choices[left.name], right.name, choices[right.name])
                if key in want_pairs and key not in seen_pairs:
                    seen_pairs.add(key)
                    fresh = True
        for slot in multiplicity:
            if not slot.item_slot or slot.item_slot not in choices:
                continue
            key = (slot.item_slot, choices[slot.item_slot], slot.name, choices[slot.name])
            if key in want_mult_pairs and key not in seen_mult_pairs:
                seen_mult_pairs.add(key)
                fresh = True
        if resolver is None:
            since_new = 0 if fresh else since_new + 1
            continue
        try:
            resolved = resolver(config)
        except Exception as exc:  # noqa: BLE001 - an unresolvable declared combination is the finding
            signature = f"{type(exc).__name__}: {str(exc)[:200]}"
            entry = resolve_failures.setdefault(
                signature,
                {"error": signature, "seeds": [], "choices": dict(choices), "count": 0},
            )
            entry["count"] += 1
            if len(entry["seeds"]) < 8:
                entry["seeds"].append(seed)
            continue
        resolved_fields = _resolved_fields(resolved)
        for slot in domain.slots:
            choice = choices[slot.name]
            observations[(slot.name, choice)] = observations.get((slot.name, choice), 0) + 1
            for field_name, value in resolved_fields:
                bucket = field_values.setdefault((slot.name, choice, field_name), set())
                if len(bucket) <= 2:
                    bucket.add(value)
        since_new = 0 if fresh else since_new + 1
        if (
            seen_pairs >= want_pairs
            and seen_mult_pairs >= want_mult_pairs
            and all(seen_values[name] >= want_values[name] for name in want_values)
            and all(
                observations.get((name, value), 0) >= _MIN_CANDIDATE_OBSERVATIONS
                for name, values in want_values.items()
                for value in values
            )
        ):
            saturated = True
            break
        if since_new >= patience:
            saturated = True
            break
    return {
        "scanned_seeds": scanned,
        "saturated": saturated,
        "max_seeds": max_seeds,
        "patience": patience,
        "seen_values": seen_values,
        "want_values": want_values,
        "seen_pairs": seen_pairs,
        "want_pairs": want_pairs,
        "seen_mult_pairs": seen_mult_pairs,
        "want_mult_pairs": want_mult_pairs,
        "observations": observations,
        "field_values": field_values,
        "sample_failures": sample_failures,
        "resolve_failures": list(resolve_failures.values()),
        "resolver_available": resolver is not None,
    }


def _resolved_fields(resolved: Any) -> list[tuple[str, str]]:
    if dataclasses.is_dataclass(resolved) and not isinstance(resolved, type):
        names = [item.name for item in dataclasses.fields(resolved)]
    else:
        names = [name for name in vars(resolved) if not name.startswith("_")]
    out: list[tuple[str, str]] = []
    for name in names:
        try:
            out.append((name, _json_identity(getattr(resolved, name))))
        except Exception:  # noqa: BLE001 - unrepresentable fields are simply not compared
            continue
    return out


def domain_resolution_checks(
    *,
    module: Any,
    design: TemplateDesign,
    domain: TemplateDomain,
    max_seeds: int = _DOMAIN_SCAN_MAX_SEEDS,
    patience: int = _DOMAIN_SCAN_PATIENCE,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Tier 0-B: exhaust the declared domain through the sampler, building nothing.

    Every question here is answered by ``config_from_seed`` + ``resolve_config``,
    which cost microseconds -- the winch's whole 864-combination core domain
    resolves in ~0.11 s.  What it proves:

    * the sampler reaches every declared candidate, and every cross-slot
      candidate pair (hard boundary 7 is a claim about combinations, and nothing
      else in the pipeline reads it);
    * no config the sampler emits makes ``resolve_config`` raise;
    * no declared independent parameter is pinned to a single value over the
      seeds that select its owning candidate -- which is what a silent coercion
      inside ``resolve_config`` looks like from the outside.

    Geometry is not this tier's business.  Whether a candidate *builds* is proved
    by the sweep, which compiles it anyway and now splits its pass rate per
    candidate.
    """
    findings: list[dict[str, Any]] = []
    scan = _scan_domain(module=module, domain=domain, max_seeds=max_seeds, patience=patience)

    for entry in scan["sample_failures"]:
        findings.append(
            _finding(
                "domain_config_from_seed_failed",
                f"config_from_seed({entry['seed']}) raised {entry['error_kind']}: {entry['error']}",
                blocking=True,
                owner=entry,
                next_action="repair_the_sampler",
            )
        )
    for entry in scan["resolve_failures"]:
        findings.append(
            _finding(
                "domain_combination_unresolvable",
                f"resolve_config raised on a sampled combination ({entry['count']} seeds): "
                f"{entry['error']}",
                blocking=True,
                owner=entry,
                next_action="derive_the_combination_instead_of_rejecting_it",
            )
        )

    unreachable: list[str] = []
    for name, wanted in scan["want_values"].items():
        for value in sorted(wanted - scan["seen_values"][name]):
            unreachable.append(f"{name}.{value}")
    if unreachable:
        findings.append(
            _finding(
                "domain_candidate_unreachable",
                "declared value(s) the sampler never produced in "
                f"{scan['scanned_seeds']} seeds: {', '.join(unreachable)}",
                blocking=True,
                owner={"unreachable": unreachable, "scanned_seeds": scan["scanned_seeds"]},
                next_action="rebalance_the_sampler_or_withdraw_the_declaration",
            )
        )
    missing_pairs = sorted(
        f"{a}.{b} x {c}.{d}" for (a, b, c, d) in (scan["want_pairs"] - scan["seen_pairs"])
    )
    if missing_pairs:
        findings.append(
            _finding(
                "domain_pair_unreachable",
                f"{len(missing_pairs)} declared cross-slot pair(s) never sampled in "
                f"{scan['scanned_seeds']} seeds (first: {', '.join(missing_pairs[:5])})",
                blocking=False,
                confidence="medium",
                owner={
                    "missing": missing_pairs[:50],
                    "missing_count": len(missing_pairs),
                    "scanned_seeds": scan["scanned_seeds"],
                    "saturated": scan["saturated"],
                },
                next_action="confirm_the_pair_is_reachable_or_withdraw_the_declaration",
            )
        )

    missing_mult = sorted(
        f"{a}.{b} x {c}={d}" for (a, b, c, d) in (scan["want_mult_pairs"] - scan["seen_mult_pairs"])
    )
    if missing_mult:
        findings.append(
            _finding(
                "multiplicity_sampler_missing_combination",
                "sampler does not reach candidate x N combination(s) in "
                f"{scan['scanned_seeds']} seeds: {', '.join(missing_mult[:10])}",
                blocking=True,
                owner={"missing": missing_mult, "scanned_seeds": scan["scanned_seeds"]},
                next_action="rebalance_the_sampler_or_narrow_the_declared_n_range",
            )
        )

    pinned: list[dict[str, Any]] = []
    for slot in design.slots:
        for candidate in slot.candidates:
            for parameter in candidate.parameters:
                if parameter.mode != "independent":
                    continue
                if (
                    scan["observations"].get((slot.name, candidate.name), 0)
                    < _MIN_CANDIDATE_OBSERVATIONS
                ):
                    # too few draws to tell a pinned parameter from a thin sample
                    continue
                key = (slot.name, candidate.name, parameter.name)
                observed = scan["field_values"].get(key)
                if not observed or len(observed) > 1:
                    continue
                pinned.append(
                    {
                        "slot": slot.name,
                        "candidate": candidate.name,
                        "parameter": parameter.name,
                        "value": next(iter(observed)),
                    }
                )
    for entry in pinned:
        findings.append(
            _finding(
                "parameter_resolution_no_effect",
                f"{entry['slot']}.{entry['candidate']}.{entry['parameter']} resolves to a single "
                f"value ({entry['value']}) across every seed that selects the candidate",
                blocking=True,
                owner=entry,
                next_action="restore_the_parameter_or_withdraw_the_declaration",
            )
        )

    details = {
        "candidate_structure": {
            "status": "fail" if unreachable else "pass",
            "mode": "sampler_reachability_no_cad",
            "scanned_seeds": scan["scanned_seeds"],
            "saturated": scan["saturated"],
            "declared_values": sum(len(v) for v in scan["want_values"].values()),
            "reached_values": sum(len(v) for v in scan["seen_values"].values()),
            "declared_pairs": len(scan["want_pairs"]),
            "reached_pairs": len(scan["seen_pairs"]),
            "unreachable": unreachable,
        },
        "parameterization": {
            "status": "fail" if pinned else "pass",
            "mode": "candidate_scoped_resolution_no_cad",
            "pinned": pinned,
        },
        "derivations": {
            "status": "fail"
            if scan["resolve_failures"]
            else "pass"
            if scan["resolver_available"]
            else "not_run",
            "resolver_available": scan["resolver_available"],
            "unresolvable_combinations": scan["resolve_failures"],
        },
        "multiplicity": {
            "status": "fail" if missing_mult else "pass",
            "mode": "sampler_reachability_no_cad",
            "declared_pairs": len(scan["want_mult_pairs"]),
            "reached_pairs": len(scan["seen_mult_pairs"]),
            "missing": missing_mult,
        }
        if any(slot.kind == "multiplicity" for slot in domain.slots)
        else {"status": "not_applicable"},
    }
    return findings, details


def semantic_checks(
    *,
    path: Path,
    module: Any,
    stem: str,
    design: TemplateDesign,
    domain: TemplateDomain,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Backwards-compatible entry point; Tier 0-B carries no build budget."""
    _ = (path, stem)
    return domain_resolution_checks(module=module, design=design, domain=domain)


def preflight_repair_gate(findings: Iterable[dict[str, Any]]) -> dict[str, Any]:
    blocking = [row for row in findings if row["blocking"]]
    return {
        "status": "repair_required" if blocking else "not_needed",
        "blocking": bool(blocking),
        "blocking_finding_ids": [row["finding_id"] for row in blocking],
        "next_action": (
            "rerun_same_stage_after_preflight_pass" if blocking else "continue_to_requested_stage"
        ),
    }


def check_groups(
    findings: list[dict[str, Any]],
    details: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    codes = {
        "source_hygiene": {
            "template_missing",
            "template_parse_failed",
            "template_import_failed",
            "forbidden_runtime_import",
            "required_export_missing",
            "duplicate_top_level_definition",
            "required_export_overwritten",
            "dead_private_code",
            "overlap_allowance_forbidden",
            "micro_contact_tolerance",
        },
        "design_alignment": {
            "template_design_invalid",
            "quality_contract_changed_during_repair",
            "design_runtime_component_domain_mismatch",
            "design_runtime_multiplicity_item_slot_mismatch",
            "source_map_unavailable",
            "source_map_hash_stale",
            "implementation_function_stale",
            "domain_config_fields_missing",
            "semantic_probe_requires_dataclass_config",
        },
        "candidate_structure": {
            "domain_config_from_seed_failed",
            "domain_candidate_unreachable",
            "domain_pair_unreachable",
        },
        "parameterization": {
            "parameter_unit_missing",
            "parameter_runtime_mapping_stale",
            "parameter_resolution_no_effect",
        },
        "derivations": {
            "derived_parameter_self_dependency",
            "derived_parameter_cycle",
            "derived_parameter_source_name_unresolved",
            "binding_slot_unresolved",
            "binding_interface_unresolved",
            "domain_combination_unresolvable",
        },
        "multiplicity": {
            "multiplicity_sampler_missing_combination",
            "multiplicity_config_combination_invalid",
        },
        "category_fidelity": {
            "category_anchors_missing",
            "category_anchor_author_check_missing",
        },
        "corner_boundaries": {
            "corner_numeric_boundary_unauthored",
        },
    }
    result: dict[str, Any] = {}
    for name, owned_codes in codes.items():
        rows = [row for row in findings if row["code"] in owned_codes]
        result[name] = _check_summary(
            rows,
            details=details.get(name),
            not_applicable=name == "multiplicity"
            and details.get(name) == {"status": "not_applicable"},
        )
    return result


__all__ = [
    "category_anchor_wiring_checks",
    "check_groups",
    "corner_boundary_checks",
    "derivation_checks",
    "design_alignment_checks",
    "domain_resolution_checks",
    "preflight_finding",
    "preflight_repair_gate",
    "quality_contract",
    "semantic_checks",
    "source_hygiene_checks",
]
