# SPDX-License-Identifier: Apache-2.0

"""Compact authoring design between a SourceMap and a single-file template.

TemplateDesign records decisions that cannot be inferred mechanically from the
source map: component semantics, real parameters, interfaces, multiplicity and
cross-component derivations.  It deliberately contains no copied source code,
AST closure, snapshot, runtime import, or linker manifest.
"""

from __future__ import annotations

import dataclasses
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from agent.source_maps import SourceMapCandidate, SourceMapResolution, parse_source_map

ParameterMode = Literal["independent", "derived"]
InterfaceKind = Literal["plane", "axis"]
InterfaceRole = Literal["provider", "consumer", "bidirectional"]
_PARAMETER_UNITS = {"m", "rad", "ratio", "count"}


class TemplateDesignError(ValueError):
    """The compact design is malformed or internally inconsistent."""


def _identifier(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip()).strip("_").lower()
    if not text:
        return "component"
    if text[0].isdigit():
        text = f"component_{text}"
    return text


@dataclass(frozen=True, slots=True)
class ParameterDesign:
    name: str
    mode: ParameterMode = "independent"
    value_type: str = "float"
    unit: str | None = None
    minimum: float | int | None = None
    maximum: float | int | None = None
    choices: tuple[Any, ...] = ()
    expression: str = ""
    depends_on: tuple[str, ...] = ()
    rationale: str = ""

    def validate(self, owner: str) -> list[str]:
        findings: list[str] = []
        label = f"{owner}.{self.name}"
        if not self.name.strip():
            findings.append(f"{owner}: parameter name is empty")
        if self.mode not in {"independent", "derived"}:
            findings.append(f"{label}: invalid mode {self.mode!r}")
        if self.minimum is not None and self.maximum is not None and self.minimum > self.maximum:
            findings.append(f"{label}: minimum exceeds maximum")
        if self.mode == "derived" and not self.expression.strip():
            findings.append(f"{label}: derived parameter needs an expression")
        if self.mode == "independent" and self.expression.strip():
            findings.append(f"{label}: independent parameter cannot have an expression")
        if self.unit is not None and self.unit not in _PARAMETER_UNITS:
            findings.append(f"{label}: unit must be one of {sorted(_PARAMETER_UNITS)!r}")
        return findings


@dataclass(frozen=True, slots=True)
class SurfaceRelationDesign:
    """Category-authored relation between a subject and a local plane interface."""

    subject_role: str
    opening_expression: str
    normal_band_expression: str
    required_author_check: str
    motion_expression: str = ""

    def validate(self, owner: str) -> list[str]:
        findings: list[str] = []
        if not self.subject_role.strip():
            findings.append(f"{owner}: surface relation subject_role is empty")
        if not self.opening_expression.strip():
            findings.append(f"{owner}: surface relation opening_expression is empty")
        if not self.normal_band_expression.strip():
            findings.append(f"{owner}: surface relation normal_band_expression is empty")
        if not self.required_author_check.strip():
            findings.append(f"{owner}: surface relation required_author_check is empty")
        return findings


@dataclass(frozen=True, slots=True)
class InterfaceDesign:
    name: str
    kind: InterfaceKind
    role: InterfaceRole
    part: str
    frame: dict[str, Any] = field(default_factory=dict)
    dimensions: dict[str, str | float | int] = field(default_factory=dict)
    surface_relation: SurfaceRelationDesign | None = None

    def validate(self, owner: str) -> list[str]:
        findings: list[str] = []
        if not self.name.strip():
            findings.append(f"{owner}: interface name is empty")
        if self.kind not in {"plane", "axis"}:
            findings.append(f"{owner}.{self.name}: invalid interface kind {self.kind!r}")
        if self.role not in {"provider", "consumer", "bidirectional"}:
            findings.append(f"{owner}.{self.name}: invalid interface role {self.role!r}")
        if not self.part.strip():
            findings.append(f"{owner}.{self.name}: interface part is empty")
        if self.surface_relation is not None:
            if self.kind != "plane":
                findings.append(
                    f"{owner}.{self.name}: surface_relation requires a plane interface"
                )
            findings.extend(self.surface_relation.validate(f"{owner}.{self.name}"))
        return findings


@dataclass(frozen=True, slots=True)
class CandidateDesign:
    name: str
    record_id: str | None = None
    revision: str | None = None
    source_spans: tuple[str, ...] = ()
    evidence: str = ""
    implementation_function: str = ""
    parameters: tuple[ParameterDesign, ...] = ()
    interfaces: tuple[InterfaceDesign, ...] = ()
    notes: str = ""

    def validate(self, slot: str) -> list[str]:
        owner = f"slot {slot!r} candidate {self.name!r}"
        findings: list[str] = []
        if not self.name.strip():
            findings.append(f"slot {slot!r}: candidate name is empty")
        if not self.implementation_function.strip():
            findings.append(f"{owner}: implementation_function is empty")
        parameter_names = [item.name for item in self.parameters]
        if len(parameter_names) != len(set(parameter_names)):
            findings.append(f"{owner}: duplicate parameter names")
        interface_names = [item.name for item in self.interfaces]
        if len(interface_names) != len(set(interface_names)):
            findings.append(f"{owner}: duplicate interface names")
        for parameter in self.parameters:
            findings.extend(parameter.validate(owner))
        for interface in self.interfaces:
            findings.extend(interface.validate(owner))
        return findings


@dataclass(frozen=True, slots=True)
class SlotDesign:
    name: str
    component_type: str
    candidates: tuple[CandidateDesign, ...]
    required: bool = True

    def validate(self) -> list[str]:
        findings: list[str] = []
        if not self.name.strip():
            findings.append("slot name is empty")
        if not self.component_type.strip():
            findings.append(f"slot {self.name!r}: component_type is empty")
        if not self.candidates:
            findings.append(f"slot {self.name!r}: no candidates")
        names = [item.name for item in self.candidates]
        if len(names) != len(set(names)):
            findings.append(f"slot {self.name!r}: duplicate candidates")
        for candidate in self.candidates:
            findings.extend(candidate.validate(self.name))
        return findings


@dataclass(frozen=True, slots=True)
class MultiplicityDesign:
    name: str
    item_slot: str
    values: tuple[int, ...]
    spacing_expression: str
    host_capacity_expression: str

    def validate(self, slots: set[str]) -> list[str]:
        findings: list[str] = []
        if self.item_slot not in slots:
            findings.append(f"multiplicity {self.name!r}: unknown item_slot {self.item_slot!r}")
        if not self.values or any(
            not isinstance(value, int) or isinstance(value, bool) or value < 1
            for value in self.values
        ):
            findings.append(f"multiplicity {self.name!r}: values must be positive integers")
        if len(self.values) != len(set(self.values)):
            findings.append(f"multiplicity {self.name!r}: duplicate values")
        if not self.spacing_expression.strip():
            findings.append(f"multiplicity {self.name!r}: spacing_expression is empty")
        if not self.host_capacity_expression.strip():
            findings.append(f"multiplicity {self.name!r}: host_capacity_expression is empty")
        return findings


@dataclass(frozen=True, slots=True)
class AssemblyBindingDesign:
    binding_id: str
    provider: str
    consumer: str
    joint_type: str = "fixed"
    derived: tuple[ParameterDesign, ...] = ()

    def validate(self) -> list[str]:
        findings: list[str] = []
        if not self.binding_id.strip():
            findings.append("assembly binding id is empty")
        if "." not in self.provider or "." not in self.consumer:
            findings.append(
                f"binding {self.binding_id!r}: provider/consumer must use slot.interface"
            )
        for parameter in self.derived:
            findings.extend(parameter.validate(f"binding {self.binding_id!r}"))
        return findings


@dataclass(frozen=True, slots=True)
class CategoryAnchorAppliesTo:
    slot: str
    candidates: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CategoryRoleRequirement:
    role: str
    exact_count: int | None = None
    count_from: str | None = None

    def validate(self, owner: str) -> list[str]:
        findings: list[str] = []
        if not self.role.strip():
            findings.append(f"{owner}: required role is empty")
        count_modes = int(self.exact_count is not None) + int(self.count_from is not None)
        if count_modes != 1:
            findings.append(
                f"{owner}.{self.role}: exactly one of exact_count or count_from is required"
            )
        if self.exact_count is not None and (
            not isinstance(self.exact_count, int)
            or isinstance(self.exact_count, bool)
            or self.exact_count < 0
        ):
            findings.append(f"{owner}.{self.role}: exact_count must be a non-negative integer")
        if self.count_from is not None and not self.count_from.strip():
            findings.append(f"{owner}.{self.role}: count_from is empty")
        return findings


@dataclass(frozen=True, slots=True)
class CategoryRelationRequirement:
    parent_role: str
    child_role: str
    joint_type: str
    axis: tuple[float, float, float] | None = None

    def validate(self, owner: str) -> list[str]:
        findings: list[str] = []
        if not self.parent_role.strip() or not self.child_role.strip():
            findings.append(f"{owner}: relation parent_role and child_role are required")
        if self.joint_type not in {
            "fixed",
            "revolute",
            "continuous",
            "prismatic",
            "floating",
            "planar",
        }:
            findings.append(f"{owner}: unsupported joint_type {self.joint_type!r}")
        if self.axis is not None and len(self.axis) != 3:
            findings.append(f"{owner}: axis must contain exactly three values")
        return findings


@dataclass(frozen=True, slots=True)
class CategoryAnchorDesign:
    anchor_id: str
    applies_to: CategoryAnchorAppliesTo
    required_roles: tuple[CategoryRoleRequirement, ...]
    required_relations: tuple[CategoryRelationRequirement, ...] = ()
    required_author_checks: tuple[str, ...] = ()

    def validate(
        self,
        *,
        slots: dict[str, SlotDesign],
        multiplicities: set[str],
    ) -> list[str]:
        owner = f"category anchor {self.anchor_id!r}"
        findings: list[str] = []
        if not self.anchor_id.strip():
            findings.append("category anchor id is empty")
        slot = slots.get(self.applies_to.slot)
        if slot is None:
            findings.append(f"{owner}: unknown slot {self.applies_to.slot!r}")
        else:
            valid_candidates = {candidate.name for candidate in slot.candidates}
            unknown = sorted(set(self.applies_to.candidates) - valid_candidates)
            if unknown:
                findings.append(f"{owner}: unknown candidates {unknown!r}")
        if not self.applies_to.candidates:
            findings.append(f"{owner}: applies_to.candidates is empty")
        if len(self.applies_to.candidates) != len(set(self.applies_to.candidates)):
            findings.append(f"{owner}: duplicate applies_to candidates")
        if not self.required_roles:
            findings.append(f"{owner}: required_roles is empty")
        role_names = [requirement.role for requirement in self.required_roles]
        if len(role_names) != len(set(role_names)):
            findings.append(f"{owner}: duplicate required roles")
        for requirement in self.required_roles:
            findings.extend(requirement.validate(owner))
            if (
                requirement.count_from
                and requirement.count_from not in multiplicities
                and not requirement.count_from.startswith("resolved.")
            ):
                findings.append(
                    f"{owner}.{requirement.role}: unknown count_from "
                    f"{requirement.count_from!r}"
                )
        for relation in self.required_relations:
            findings.extend(relation.validate(owner))
        if any(not check.strip() for check in self.required_author_checks):
            findings.append(f"{owner}: required_author_checks contains an empty name")
        if len(self.required_author_checks) != len(set(self.required_author_checks)):
            findings.append(f"{owner}: duplicate required_author_checks")
        return findings


@dataclass(frozen=True, slots=True)
class TemplateDesign:
    slug: str
    source_map_path: str
    source_map_sha256: str
    slots: tuple[SlotDesign, ...]
    multiplicities: tuple[MultiplicityDesign, ...] = ()
    bindings: tuple[AssemblyBindingDesign, ...] = ()
    category_anchors: tuple[CategoryAnchorDesign, ...] = ()
    assembly_notes: str = ""
    schema_version: int = 1

    def validate(self) -> list[str]:
        findings: list[str] = []
        if self.schema_version != 1:
            findings.append(f"unsupported TemplateDesign schema_version {self.schema_version}")
        if not self.slug.strip():
            findings.append("template slug is empty")
        if not self.source_map_sha256.strip():
            findings.append("source_map_sha256 is empty")
        slot_names = [slot.name for slot in self.slots]
        if len(slot_names) != len(set(slot_names)):
            findings.append("duplicate slot names")
        for slot in self.slots:
            findings.extend(slot.validate())
        slot_set = set(slot_names)
        multiplicity_names = [item.name for item in self.multiplicities]
        if len(multiplicity_names) != len(set(multiplicity_names)):
            findings.append("duplicate multiplicity names")
        for multiplicity in self.multiplicities:
            findings.extend(multiplicity.validate(slot_set))
        for binding in self.bindings:
            findings.extend(binding.validate())
        anchor_ids = [anchor.anchor_id for anchor in self.category_anchors]
        if len(anchor_ids) != len(set(anchor_ids)):
            findings.append("duplicate category anchor ids")
        slot_index = {slot.name: slot for slot in self.slots}
        multiplicity_set = set(multiplicity_names)
        for anchor in self.category_anchors:
            findings.extend(
                anchor.validate(
                    slots=slot_index,
                    multiplicities=multiplicity_set,
                )
            )
        for slot in self.slots:
            for candidate in slot.candidates:
                matching_anchors = [
                    anchor
                    for anchor in self.category_anchors
                    if anchor.applies_to.slot == slot.name
                    and candidate.name in anchor.applies_to.candidates
                ]
                anchor_roles = {
                    requirement.role
                    for anchor in matching_anchors
                    for requirement in anchor.required_roles
                }
                anchor_checks = {
                    check
                    for anchor in matching_anchors
                    for check in anchor.required_author_checks
                }
                for interface in candidate.interfaces:
                    relation = interface.surface_relation
                    if relation is None:
                        continue
                    owner = (
                        f"slot {slot.name!r} candidate {candidate.name!r} "
                        f"interface {interface.name!r}"
                    )
                    if relation.subject_role not in anchor_roles:
                        findings.append(
                            f"{owner}: surface relation subject_role "
                            f"{relation.subject_role!r} is not required by a matching "
                            "category anchor"
                        )
                    if relation.required_author_check not in anchor_checks:
                        findings.append(
                            f"{owner}: surface relation required_author_check "
                            f"{relation.required_author_check!r} is not required by a "
                            "matching category anchor"
                        )
        return findings

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TemplateDesign":
        if "gates" in payload:
            raise TemplateDesignError(
                "TemplateDesign no longer supports gates; adapt the host, derive a "
                "transition/support geometry, or redefine inseparable candidates as one "
                "structural family"
            )

        def parameter(raw: dict[str, Any]) -> ParameterDesign:
            return ParameterDesign(
                **{
                    **raw,
                    "choices": tuple(raw.get("choices") or ()),
                    "depends_on": tuple(raw.get("depends_on") or ()),
                }
            )

        def interface(raw: dict[str, Any]) -> InterfaceDesign:
            relation = raw.get("surface_relation")
            return InterfaceDesign(
                **{
                    **raw,
                    "surface_relation": (
                        SurfaceRelationDesign(**relation) if relation is not None else None
                    ),
                }
            )

        def candidate(raw: dict[str, Any]) -> CandidateDesign:
            return CandidateDesign(
                **{
                    **raw,
                    "source_spans": tuple(raw.get("source_spans") or ()),
                    "parameters": tuple(parameter(item) for item in raw.get("parameters") or ()),
                    "interfaces": tuple(interface(item) for item in raw.get("interfaces") or ()),
                }
            )

        slots = tuple(
            SlotDesign(
                **{
                    **raw,
                    "candidates": tuple(candidate(item) for item in raw.get("candidates") or ()),
                }
            )
            for raw in payload.get("slots") or ()
        )
        multiplicities = tuple(
            MultiplicityDesign(**{**raw, "values": tuple(raw.get("values") or ())})
            for raw in payload.get("multiplicities") or ()
        )
        bindings = tuple(
            AssemblyBindingDesign(
                **{
                    **raw,
                    "derived": tuple(parameter(item) for item in raw.get("derived") or ()),
                }
            )
            for raw in payload.get("bindings") or ()
        )
        category_anchors = tuple(
            CategoryAnchorDesign(
                anchor_id=str(raw.get("anchor_id") or ""),
                applies_to=CategoryAnchorAppliesTo(
                    slot=str((raw.get("applies_to") or {}).get("slot") or ""),
                    candidates=tuple(
                        (raw.get("applies_to") or {}).get("candidates") or ()
                    ),
                ),
                required_roles=tuple(
                    CategoryRoleRequirement(**item)
                    for item in raw.get("required_roles") or ()
                ),
                required_relations=tuple(
                    CategoryRelationRequirement(
                        **{
                            **item,
                            "axis": (
                                tuple(item["axis"])
                                if item.get("axis") is not None
                                else None
                            ),
                        }
                    )
                    for item in raw.get("required_relations") or ()
                ),
                required_author_checks=tuple(
                    raw.get("required_author_checks") or ()
                ),
            )
            for raw in payload.get("category_anchors") or ()
        )
        return cls(
            slug=str(payload.get("slug") or ""),
            source_map_path=str(payload.get("source_map_path") or ""),
            source_map_sha256=str(payload.get("source_map_sha256") or ""),
            slots=slots,
            multiplicities=multiplicities,
            bindings=bindings,
            category_anchors=category_anchors,
            assembly_notes=str(payload.get("assembly_notes") or ""),
            schema_version=int(payload.get("schema_version") or 0),
        )


def _candidate_from_source(slot: str, source: SourceMapCandidate) -> CandidateDesign:
    return CandidateDesign(
        name=source.candidate,
        record_id=source.record_id,
        revision=source.revision,
        source_spans=tuple(span.code_ref for span in source.spans),
        evidence=source.evidence,
        implementation_function=f"_{_identifier(slot)}_{_identifier(source.candidate)}_build",
    )


def design_from_source_map(slug: str, resolution: SourceMapResolution) -> TemplateDesign:
    """Create a small editable design scaffold from accepted SourceMap rows."""

    grouped: dict[str, list[SourceMapCandidate]] = {}
    for candidate in resolution.accepted_candidates:
        grouped.setdefault(candidate.slot, []).append(candidate)
    slots = tuple(
        SlotDesign(
            name=slot,
            component_type=next(
                (item.source_type for item in candidates if item.source_type.strip()),
                slot,
            ),
            candidates=tuple(_candidate_from_source(slot, item) for item in candidates),
        )
        for slot, candidates in grouped.items()
    )
    return TemplateDesign(
        slug=slug,
        source_map_path=str(resolution.path),
        source_map_sha256=resolution.sha256,
        slots=slots,
    )


def load_template_design(path: Path) -> TemplateDesign:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TemplateDesignError("TemplateDesign JSON root must be an object")
    design = TemplateDesign.from_dict(payload)
    findings = design.validate()
    if findings:
        raise TemplateDesignError("; ".join(findings))
    return design


def write_template_design(design: TemplateDesign, path: Path) -> None:
    findings = design.validate()
    if findings:
        raise TemplateDesignError("; ".join(findings))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(design.to_dict(), indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def scaffold_template_design(
    *,
    slug: str,
    source_map: Path,
    records_root: Path,
) -> tuple[TemplateDesign, SourceMapResolution]:
    resolution = parse_source_map(source_map, records_root)
    if resolution.problems:
        raise TemplateDesignError("; ".join(resolution.problems))
    design = design_from_source_map(slug, resolution)
    findings = design.validate()
    if findings:
        raise TemplateDesignError("; ".join(findings))
    return design, resolution


__all__ = [
    "AssemblyBindingDesign",
    "CandidateDesign",
    "CategoryAnchorAppliesTo",
    "CategoryAnchorDesign",
    "CategoryRelationRequirement",
    "CategoryRoleRequirement",
    "InterfaceDesign",
    "MultiplicityDesign",
    "ParameterDesign",
    "SlotDesign",
    "TemplateDesign",
    "TemplateDesignError",
    "design_from_source_map",
    "load_template_design",
    "scaffold_template_design",
    "write_template_design",
]
