# SPDX-License-Identifier: Apache-2.0

"""Strict offline material-class annotations for generator visual callsites.

The final template runtime still receives one scalar ``material_class_id`` for
each resolved visual.  This module owns only the offline annotation contract:
one stable visual callsite may resolve to at most two classes across its
explicit Config domain.  Larger proposal sets are deterministically compressed
and every Config value remains mapped to one retained class.  A separate
role-routed policy covers the narrow case where one source helper callsite is
shared by materially different runtime component roles.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
from collections import defaultdict
from typing import Any, Iterable, Mapping

GENERATOR_CLASS_PROPOSALS_SCHEMA = "articraft-generator-material-class-proposals/v1"
GENERATOR_CLASS_ANNOTATIONS_SCHEMA = "articraft-generator-material-class-annotations/v1"
GENERATOR_CLASS_ANNOTATION_POLICY = "scalar-exact-class-max2/v1"
GENERATOR_CLASS_ROLE_ROUTED_ANNOTATIONS_SCHEMA = (
    "articraft-generator-material-class-annotations-role-routed/v1"
)
GENERATOR_CLASS_ROLE_ROUTED_ANNOTATION_POLICY = "scalar-exact-class-role-routed/v1"
GENERATOR_CLASS_ROLE_ROUTING_KIND = "source_material_name"
MAX_MATERIAL_CLASS_VARIANTS = 2

_CLASS_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SLUG_RE = re.compile(r"^[A-Za-z0-9_]+$")
_DECISIONS = {"material_class", "flat_color"}


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def annotation_digest(value: Mapping[str, Any]) -> str:
    """Return the content digest of a canonical annotation document."""

    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _object(value: object, *, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{field} must be an object")
    return value


def _exact_fields(value: Mapping[str, Any], expected: set[str], *, field: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise ValueError(f"{field} fields do not match v1; missing={missing}, unknown={unknown}")


def _text(value: object, *, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _sha256(value: object, *, field: str) -> str:
    result = _text(value, field=field)
    if _SHA256_RE.fullmatch(result) is None:
        raise ValueError(f"{field} must be a lowercase SHA256 digest")
    return result


def _class_id(value: object, *, field: str) -> str:
    result = _text(value, field=field)
    if _CLASS_ID_RE.fullmatch(result) is None:
        raise ValueError(f"{field} must be a lowercase dotted material_class_id")
    return result


def _string_list(
    value: object,
    *,
    field: str,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    if isinstance(value, (str, bytes)) or not isinstance(value, list):
        raise ValueError(f"{field} must be a list of strings")
    result = tuple(_text(item, field=f"{field}[{index}]") for index, item in enumerate(value))
    if not result and not allow_empty:
        raise ValueError(f"{field} must not be empty")
    if len(result) != len(set(result)):
        raise ValueError(f"{field} must not contain duplicates")
    return result


def _config_expression(value: object, *, field: str) -> str | None:
    if value is None:
        return None
    result = _text(value, field=field)
    try:
        node = ast.parse(result, mode="eval").body
    except SyntaxError as exc:
        raise ValueError(f"{field} must be a simple dotted Python expression") from exc
    while isinstance(node, ast.Attribute):
        node = node.value
    if not isinstance(node, ast.Name):
        raise ValueError(f"{field} must contain only a name and dotted attributes")
    return result


def _available_ids(values: Iterable[str]) -> frozenset[str]:
    result = frozenset(_class_id(value, field="available_material_class_ids") for value in values)
    if not result:
        raise ValueError("available_material_class_ids must not be empty")
    return result


def _validate_domain(
    *,
    config_expression: str | None,
    config_domain: tuple[str, ...],
    assignments: Iterable[tuple[tuple[str, ...], str]],
    field: str,
) -> None:
    if config_expression is None:
        if config_domain != ("*",):
            raise ValueError(f"{field}.config_domain must be ['*'] for a constant annotation")
    elif "*" in config_domain:
        raise ValueError(f"{field}.config_domain cannot contain '*' for a conditional annotation")

    seen: list[str] = []
    for config_values, _ in assignments:
        if config_expression is None and config_values != ("*",):
            raise ValueError(f"{field} constant branch must cover only '*'")
        if config_expression is not None and "*" in config_values:
            raise ValueError(f"{field} conditional branch cannot contain '*'")
        seen.extend(config_values)
    if len(seen) != len(set(seen)):
        raise ValueError(f"{field} repeats a Config value across branches")
    if set(seen) != set(config_domain):
        missing = sorted(set(config_domain) - set(seen))
        unknown = sorted(set(seen) - set(config_domain))
        raise ValueError(
            f"{field} does not partition config_domain; missing={missing}, unknown={unknown}"
        )


def _ranked_classes(
    proposals: tuple[tuple[tuple[str, ...], str, int, str], ...],
) -> tuple[str, ...]:
    priority: dict[str, int] = defaultdict(int)
    coverage: dict[str, int] = defaultdict(int)
    for config_values, material_class_id, score, _ in proposals:
        priority[material_class_id] = max(priority[material_class_id], score)
        coverage[material_class_id] += len(config_values)
    return tuple(
        sorted(
            priority,
            key=lambda class_id: (-priority[class_id], -coverage[class_id], class_id),
        )
    )


def _retain_classes(ranked: tuple[str, ...]) -> tuple[str, ...]:
    if len(ranked) <= MAX_MATERIAL_CLASS_VARIANTS:
        return ranked

    retained: list[str] = []
    parents: set[str] = set()
    for class_id in ranked:
        parent = class_id.split(".", 1)[0]
        if parent in parents:
            continue
        retained.append(class_id)
        parents.add(parent)
        if len(retained) == MAX_MATERIAL_CLASS_VARIANTS:
            return tuple(retained)
    for class_id in ranked:
        if class_id not in retained:
            retained.append(class_id)
        if len(retained) == MAX_MATERIAL_CLASS_VARIANTS:
            break
    return tuple(retained)


def _parse_proposal_callsite(
    raw: object,
    *,
    index: int,
    available: frozenset[str],
) -> dict[str, Any]:
    field = f"callsites[{index}]"
    row = _object(raw, field=field)
    base_fields = {"callsite_id", "visual_name", "decision"}
    decision = _text(row.get("decision"), field=f"{field}.decision")
    if decision not in _DECISIONS:
        raise ValueError(f"{field}.decision must be one of {sorted(_DECISIONS)}")
    callsite_id = _text(row.get("callsite_id"), field=f"{field}.callsite_id")
    visual_name = _text(row.get("visual_name"), field=f"{field}.visual_name")

    if decision == "flat_color":
        _exact_fields(row, base_fields, field=field)
        return {
            "callsite_id": callsite_id,
            "visual_name": visual_name,
            "decision": decision,
        }

    _exact_fields(
        row,
        base_fields | {"config_expression", "config_domain", "proposals"},
        field=field,
    )
    expression = _config_expression(
        row.get("config_expression"), field=f"{field}.config_expression"
    )
    domain = _string_list(row.get("config_domain"), field=f"{field}.config_domain")
    raw_proposals = row.get("proposals")
    if not isinstance(raw_proposals, list) or not raw_proposals:
        raise ValueError(f"{field}.proposals must be a non-empty list")

    proposals: list[tuple[tuple[str, ...], str, int, str]] = []
    for proposal_index, raw_proposal in enumerate(raw_proposals):
        proposal_field = f"{field}.proposals[{proposal_index}]"
        proposal = _object(raw_proposal, field=proposal_field)
        _exact_fields(
            proposal,
            {"config_values", "material_class_id", "priority", "rationale"},
            field=proposal_field,
        )
        config_values = _string_list(
            proposal.get("config_values"), field=f"{proposal_field}.config_values"
        )
        class_id = _class_id(
            proposal.get("material_class_id"),
            field=f"{proposal_field}.material_class_id",
        )
        if class_id not in available:
            raise ValueError(f"{proposal_field} references unavailable material class {class_id!r}")
        priority = proposal.get("priority")
        if isinstance(priority, bool) or not isinstance(priority, int) or not 0 <= priority <= 100:
            raise ValueError(f"{proposal_field}.priority must be an integer from 0 to 100")
        rationale = _text(proposal.get("rationale"), field=f"{proposal_field}.rationale")
        proposals.append((config_values, class_id, priority, rationale))

    proposal_tuple = tuple(proposals)
    _validate_domain(
        config_expression=expression,
        config_domain=domain,
        assignments=((values, class_id) for values, class_id, _, _ in proposal_tuple),
        field=field,
    )
    ranked = _ranked_classes(proposal_tuple)
    retained = _retain_classes(ranked)
    retained_set = set(retained)

    remap: dict[str, str] = {}
    for class_id in ranked:
        if class_id in retained_set:
            remap[class_id] = class_id
            continue
        parent_matches = [
            candidate
            for candidate in retained
            if candidate.split(".", 1)[0] == class_id.split(".", 1)[0]
        ]
        remap[class_id] = parent_matches[0] if parent_matches else retained[0]

    config_to_class: dict[str, str] = {}
    for values, class_id, _, _ in proposal_tuple:
        for config_value in values:
            config_to_class[config_value] = remap[class_id]
    branches = []
    for class_id in retained:
        values = [value for value in domain if config_to_class.get(value) == class_id]
        if values:
            branches.append(
                {
                    "config_values": values,
                    "material_class_id": class_id,
                }
            )
    final_class_ids = [branch["material_class_id"] for branch in branches]

    compression: dict[str, Any] | None = None
    if len(ranked) > MAX_MATERIAL_CLASS_VARIANTS:
        compression = {
            "source_material_class_count": len(ranked),
            "retained_material_class_ids": final_class_ids,
            "discarded": [
                {
                    "material_class_id": class_id,
                    "mapped_to_material_class_id": remap[class_id],
                    "reason": "hard_max2_auto_compression",
                }
                for class_id in ranked
                if class_id not in retained_set
            ],
        }

    return {
        "callsite_id": callsite_id,
        "visual_name": visual_name,
        "decision": decision,
        "config_expression": expression,
        "config_domain": list(domain),
        "branches": branches,
        "source_material_class_ids": list(ranked),
        "compression": compression,
    }


def build_generator_class_annotations(
    proposal_document: Mapping[str, Any],
    *,
    available_material_class_ids: Iterable[str],
    expected_library_snapshot_sha256: str,
    expected_template_source_sha256: str,
    expected_callsites: Mapping[str, str],
) -> dict[str, Any]:
    """Compress and validate one strict proposal document."""

    _exact_fields(
        proposal_document,
        {
            "schema_version",
            "policy_version",
            "library_snapshot_sha256",
            "template_slug",
            "template_source_sha256",
            "callsites",
        },
        field="proposal document",
    )
    if proposal_document.get("schema_version") != GENERATOR_CLASS_PROPOSALS_SCHEMA:
        raise ValueError("unsupported generator material-class proposal schema")
    if proposal_document.get("policy_version") != GENERATOR_CLASS_ANNOTATION_POLICY:
        raise ValueError("unsupported generator material-class annotation policy")
    library_sha = _sha256(
        proposal_document.get("library_snapshot_sha256"),
        field="library_snapshot_sha256",
    )
    if library_sha != expected_library_snapshot_sha256:
        raise ValueError("proposal formal library snapshot mismatch")
    source_sha = _sha256(
        proposal_document.get("template_source_sha256"),
        field="template_source_sha256",
    )
    if source_sha != expected_template_source_sha256:
        raise ValueError("proposal template source mismatch")
    template_slug = _text(proposal_document.get("template_slug"), field="template_slug")
    if _SLUG_RE.fullmatch(template_slug) is None:
        raise ValueError("template_slug must be a Python module stem")

    available = _available_ids(available_material_class_ids)
    raw_callsites = proposal_document.get("callsites")
    if not isinstance(raw_callsites, list):
        raise ValueError("proposal callsites must be a list")
    callsites = [
        _parse_proposal_callsite(row, index=index, available=available)
        for index, row in enumerate(raw_callsites)
    ]
    ids = [row["callsite_id"] for row in callsites]
    if len(ids) != len(set(ids)):
        raise ValueError("proposal repeats callsite_id")
    if set(ids) != set(expected_callsites):
        missing = sorted(set(expected_callsites) - set(ids))
        unknown = sorted(set(ids) - set(expected_callsites))
        raise ValueError(
            f"proposal callsite coverage mismatch; missing={missing}, unknown={unknown}"
        )
    for row in callsites:
        expected_name = expected_callsites[row["callsite_id"]]
        if row["visual_name"] != expected_name:
            raise ValueError(f"proposal visual name mismatch for {row['callsite_id']!r}")

    result = {
        "schema_version": GENERATOR_CLASS_ANNOTATIONS_SCHEMA,
        "policy_version": GENERATOR_CLASS_ANNOTATION_POLICY,
        "library_snapshot_sha256": library_sha,
        "template_slug": template_slug,
        "template_source_sha256": source_sha,
        "callsites": sorted(callsites, key=lambda row: row["callsite_id"]),
    }
    return validate_generator_class_annotations(
        result,
        available_material_class_ids=available,
        expected_library_snapshot_sha256=expected_library_snapshot_sha256,
        expected_template_source_sha256=expected_template_source_sha256,
        expected_callsites=expected_callsites,
    )


def _parse_final_callsite(
    raw: object,
    *,
    index: int,
    available: frozenset[str],
    allow_role_routing: bool = False,
) -> dict[str, Any]:
    field = f"callsites[{index}]"
    row = _object(raw, field=field)
    base_fields = {"callsite_id", "visual_name", "decision"}
    decision = _text(row.get("decision"), field=f"{field}.decision")
    if decision not in _DECISIONS:
        raise ValueError(f"{field}.decision must be one of {sorted(_DECISIONS)}")
    callsite_id = _text(row.get("callsite_id"), field=f"{field}.callsite_id")
    visual_name = _text(row.get("visual_name"), field=f"{field}.visual_name")
    if decision == "flat_color":
        _exact_fields(row, base_fields, field=field)
        return {
            "callsite_id": callsite_id,
            "visual_name": visual_name,
            "decision": decision,
        }

    material_fields = base_fields | {
        "config_expression",
        "config_domain",
        "branches",
        "source_material_class_ids",
        "compression",
    }
    routing_kind: str | None = None
    if row.get("routing_kind") is not None:
        if not allow_role_routing:
            raise ValueError(f"{field}.routing_kind requires the role-routed policy")
        routing_kind = _text(row.get("routing_kind"), field=f"{field}.routing_kind")
        if routing_kind != GENERATOR_CLASS_ROLE_ROUTING_KIND:
            raise ValueError(f"{field}.routing_kind must be {GENERATOR_CLASS_ROLE_ROUTING_KIND!r}")
        material_fields.add("routing_kind")
    _exact_fields(row, material_fields, field=field)
    expression = _config_expression(
        row.get("config_expression"), field=f"{field}.config_expression"
    )
    domain = _string_list(row.get("config_domain"), field=f"{field}.config_domain")
    source_ids = tuple(
        _class_id(value, field=f"{field}.source_material_class_ids")
        for value in _string_list(
            row.get("source_material_class_ids"),
            field=f"{field}.source_material_class_ids",
        )
    )
    if any(class_id not in available for class_id in source_ids):
        raise ValueError(f"{field} references an unavailable source material class")

    raw_branches = row.get("branches")
    if not isinstance(raw_branches, list) or not raw_branches:
        raise ValueError(f"{field}.branches must be a non-empty list")
    branches: list[tuple[tuple[str, ...], str]] = []
    for branch_index, raw_branch in enumerate(raw_branches):
        branch_field = f"{field}.branches[{branch_index}]"
        branch = _object(raw_branch, field=branch_field)
        _exact_fields(branch, {"config_values", "material_class_id"}, field=branch_field)
        values = _string_list(branch.get("config_values"), field=f"{branch_field}.config_values")
        class_id = _class_id(
            branch.get("material_class_id"), field=f"{branch_field}.material_class_id"
        )
        if class_id not in available:
            raise ValueError(f"{branch_field} references unavailable material class {class_id!r}")
        branches.append((values, class_id))
    _validate_domain(
        config_expression=expression,
        config_domain=domain,
        assignments=branches,
        field=field,
    )
    retained = tuple(class_id for _, class_id in branches)
    if len(retained) != len(set(retained)):
        raise ValueError(f"{field}.branches must merge equal material classes")
    if routing_kind is None and len(retained) > MAX_MATERIAL_CLASS_VARIANTS:
        raise ValueError(
            f"{field} exceeds the hard maximum of {MAX_MATERIAL_CLASS_VARIANTS} material classes"
        )

    compression = row.get("compression")
    if routing_kind is not None:
        if compression is not None:
            raise ValueError(f"{field} role-routed annotations cannot use max2 compression")
        if set(source_ids) != set(retained) or len(source_ids) != len(retained):
            raise ValueError(f"{field} role-routed source IDs must exactly match final branches")
        canonical_compression = None
    elif compression is None:
        if set(source_ids) != set(retained) or len(source_ids) > MAX_MATERIAL_CLASS_VARIANTS:
            raise ValueError(f"{field} requires an explicit max2 compression audit")
        canonical_compression = None
    else:
        value = _object(compression, field=f"{field}.compression")
        _exact_fields(
            value,
            {"source_material_class_count", "retained_material_class_ids", "discarded"},
            field=f"{field}.compression",
        )
        source_count = value.get("source_material_class_count")
        if (
            isinstance(source_count, bool)
            or not isinstance(source_count, int)
            or source_count != len(source_ids)
            or source_count <= MAX_MATERIAL_CLASS_VARIANTS
        ):
            raise ValueError(f"{field}.compression source count must prove a >2 source set")
        retained_ids = tuple(
            _class_id(item, field=f"{field}.compression.retained_material_class_ids")
            for item in _string_list(
                value.get("retained_material_class_ids"),
                field=f"{field}.compression.retained_material_class_ids",
            )
        )
        if retained_ids != retained:
            raise ValueError(f"{field}.compression retained IDs do not match final branches")
        raw_discarded = value.get("discarded")
        if not isinstance(raw_discarded, list) or not raw_discarded:
            raise ValueError(f"{field}.compression.discarded must be a non-empty list")
        discarded = []
        for discarded_index, raw_discard in enumerate(raw_discarded):
            discard_field = f"{field}.compression.discarded[{discarded_index}]"
            discard = _object(raw_discard, field=discard_field)
            _exact_fields(
                discard,
                {"material_class_id", "mapped_to_material_class_id", "reason"},
                field=discard_field,
            )
            source_class_id = _class_id(
                discard.get("material_class_id"), field=f"{discard_field}.material_class_id"
            )
            target_class_id = _class_id(
                discard.get("mapped_to_material_class_id"),
                field=f"{discard_field}.mapped_to_material_class_id",
            )
            reason = _text(discard.get("reason"), field=f"{discard_field}.reason")
            if reason != "hard_max2_auto_compression":
                raise ValueError(f"{discard_field}.reason must be 'hard_max2_auto_compression'")
            if target_class_id not in retained:
                raise ValueError(f"{discard_field} target is not retained")
            discarded.append((source_class_id, target_class_id, reason))
        discarded_ids = [source for source, _, _ in discarded]
        if len(discarded_ids) != len(set(discarded_ids)):
            raise ValueError(f"{field}.compression repeats a discarded class")
        if set(discarded_ids) != set(source_ids) - set(retained):
            raise ValueError(f"{field}.compression does not cover every discarded class")
        canonical_compression = {
            "source_material_class_count": source_count,
            "retained_material_class_ids": list(retained_ids),
            "discarded": [
                {
                    "material_class_id": source,
                    "mapped_to_material_class_id": target,
                    "reason": reason,
                }
                for source, target, reason in discarded
            ],
        }

    result = {
        "callsite_id": callsite_id,
        "visual_name": visual_name,
        "decision": decision,
        "config_expression": expression,
        "config_domain": list(domain),
        "branches": [
            {"config_values": list(values), "material_class_id": class_id}
            for values, class_id in branches
        ],
        "source_material_class_ids": list(source_ids),
        "compression": canonical_compression,
    }
    if routing_kind is not None:
        result["routing_kind"] = routing_kind
    return result


def validate_generator_class_annotations(
    annotation_document: Mapping[str, Any],
    *,
    available_material_class_ids: Iterable[str],
    expected_library_snapshot_sha256: str,
    expected_template_source_sha256: str,
    expected_callsites: Mapping[str, str],
) -> dict[str, Any]:
    """Validate and canonicalize one final annotation document."""

    _exact_fields(
        annotation_document,
        {
            "schema_version",
            "policy_version",
            "library_snapshot_sha256",
            "template_slug",
            "template_source_sha256",
            "callsites",
        },
        field="annotation document",
    )
    schema_version = annotation_document.get("schema_version")
    policy_version = annotation_document.get("policy_version")
    role_routed_document = (
        schema_version == GENERATOR_CLASS_ROLE_ROUTED_ANNOTATIONS_SCHEMA
        and policy_version == GENERATOR_CLASS_ROLE_ROUTED_ANNOTATION_POLICY
    )
    max2_document = (
        schema_version == GENERATOR_CLASS_ANNOTATIONS_SCHEMA
        and policy_version == GENERATOR_CLASS_ANNOTATION_POLICY
    )
    if not (max2_document or role_routed_document):
        raise ValueError("unsupported generator material-class annotation schema/policy pair")
    library_sha = _sha256(
        annotation_document.get("library_snapshot_sha256"),
        field="library_snapshot_sha256",
    )
    if library_sha != expected_library_snapshot_sha256:
        raise ValueError("annotation formal library snapshot mismatch")
    source_sha = _sha256(
        annotation_document.get("template_source_sha256"),
        field="template_source_sha256",
    )
    if source_sha != expected_template_source_sha256:
        raise ValueError("annotation template source mismatch")
    template_slug = _text(annotation_document.get("template_slug"), field="template_slug")
    if _SLUG_RE.fullmatch(template_slug) is None:
        raise ValueError("template_slug must be a Python module stem")

    available = _available_ids(available_material_class_ids)
    raw_callsites = annotation_document.get("callsites")
    if not isinstance(raw_callsites, list):
        raise ValueError("annotation callsites must be a list")
    callsites = [
        _parse_final_callsite(
            row,
            index=index,
            available=available,
            allow_role_routing=role_routed_document,
        )
        for index, row in enumerate(raw_callsites)
    ]
    if role_routed_document and not any(row.get("routing_kind") for row in callsites):
        raise ValueError("role-routed annotation document has no role-routed callsite")
    ids = [row["callsite_id"] for row in callsites]
    if len(ids) != len(set(ids)):
        raise ValueError("annotation repeats callsite_id")
    if set(ids) != set(expected_callsites):
        missing = sorted(set(expected_callsites) - set(ids))
        unknown = sorted(set(ids) - set(expected_callsites))
        raise ValueError(
            f"annotation callsite coverage mismatch; missing={missing}, unknown={unknown}"
        )
    for row in callsites:
        if row["visual_name"] != expected_callsites[row["callsite_id"]]:
            raise ValueError(f"annotation visual name mismatch for {row['callsite_id']!r}")

    return {
        "schema_version": schema_version,
        "policy_version": policy_version,
        "library_snapshot_sha256": library_sha,
        "template_slug": template_slug,
        "template_source_sha256": source_sha,
        "callsites": sorted(callsites, key=lambda row: row["callsite_id"]),
    }
