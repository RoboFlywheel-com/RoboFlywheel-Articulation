# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import ast
import copy
from pathlib import Path

import pytest

from scripts import migrate_generator_material_classes_qwen as target

TEMPLATE_SOURCE = """\
from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal

MaterialKind = Literal["metal", "wood"]
FINISHES: tuple[str, ...] = ("matte", "gloss")


@dataclass(frozen=True)
class Config:
    kind: MaterialKind
    finish: str


@dataclass(frozen=True)
class ResolvedConfig:
    kind: MaterialKind
    finish: Literal["matte", "gloss"]


def config_from_seed(seed: int) -> Config:
    rng = random.Random(seed)
    return Config(kind=rng.choice(("metal", "wood")), finish=rng.choice(FINISHES))


def resolve_config(config: Config) -> ResolvedConfig:
    return ResolvedConfig(kind=config.kind, finish=config.finish)


def build(model, r: ResolvedConfig, material):
    part = model.part("body")
    part.visual(object(), name="shell", material=material)
    part.visual(object(), name="trim", material=material)
    part.visual(object(), name="label", material=material)
"""

COMPOSITION_SOURCE = """\
from dependency import build_dependency


def build():
    return build_dependency()
"""

AQUARIUM_HELPER_SOURCE = """\
def _wv(part, material, name):
    part.visual(object(), material=material, name=name)
"""


def _inventory(source: str = TEMPLATE_SOURCE, *, slug: str = "fixture") -> dict[str, object]:
    tree = ast.parse(source)
    class_domains, named_domains = target._config_domains(tree)
    visitor = target._CallsiteVisitor(
        source=source,
        slug=slug,
        class_domains=class_domains,
    )
    visitor.visit(tree)
    return {
        "template_slug": slug,
        "relative_path": f"agent/templates/{slug}.py",
        "template_source_sha256": target._sha256_bytes(source.encode()),
        "source_line_count": source.count("\n"),
        "visual_callsite_count": len(visitor.rows),
        "config_domains": class_domains,
        "named_literal_domains": named_domains,
        "callsites": sorted(visitor.rows, key=lambda row: str(row["callsite_id"])),
        **target._source_fingerprints(source),
    }


def _callsites_by_name(inventory: dict[str, object]) -> dict[str, dict[str, object]]:
    rows = inventory["callsites"]
    assert isinstance(rows, list)
    return {str(row["visual_name"]): row for row in rows}


def _proposal(inventory: dict[str, object]) -> dict[str, object]:
    by_name = _callsites_by_name(inventory)
    return {
        "callsites": [
            {
                "callsite_id": by_name["shell"]["callsite_id"],
                "visual_name": "shell",
                "decision": "material_class",
                "config_expression": None,
                "config_domain": ["*"],
            },
            {
                "callsite_id": by_name["trim"]["callsite_id"],
                "visual_name": "trim",
                "decision": "material_class",
                "config_expression": "r.kind",
                "config_domain": ["metal", "wood"],
            },
            {
                "callsite_id": by_name["label"]["callsite_id"],
                "visual_name": "label",
                "decision": "flat_color",
            },
        ]
    }


def _annotation(inventory: dict[str, object]) -> dict[str, object]:
    proposal = _proposal(inventory)
    rows = proposal["callsites"]
    assert isinstance(rows, list)
    rows[0]["branches"] = [{"config_values": ["*"], "material_class_id": "metal.brushed_steel"}]
    rows[1]["branches"] = [
        {"config_values": ["metal"], "material_class_id": "metal.brushed_steel"},
        {"config_values": ["wood"], "material_class_id": "wood.natural_generic"},
    ]
    return proposal


def _add_material_proposals(proposal: dict[str, object]) -> None:
    rows = proposal["callsites"]
    assert isinstance(rows, list)
    by_name = {str(row["visual_name"]): row for row in rows}
    by_name["shell"]["proposals"] = [
        {
            "config_values": ["*"],
            "material_class_id": "metal.brushed_steel",
            "priority": 100,
            "rationale": "constant shell",
        }
    ]
    by_name["trim"]["proposals"] = [
        {
            "config_values": ["metal"],
            "material_class_id": "metal.brushed_steel",
            "priority": 100,
            "rationale": "metal trim",
        },
        {
            "config_values": ["wood"],
            "material_class_id": "wood.natural_generic",
            "priority": 90,
            "rationale": "wood trim",
        },
    ]


def test_config_literal_domains_and_proposal_domains_are_source_proven() -> None:
    inventory = _inventory()

    assert inventory["config_domains"] == {
        "Config": {
            "kind": ["metal", "wood"],
            "finish": ["matte", "gloss"],
        },
        "ResolvedConfig": {
            "kind": ["metal", "wood"],
            "finish": ["matte", "gloss"],
        },
    }
    named = inventory["named_literal_domains"]
    assert isinstance(named, dict)
    assert named["MaterialKind"] == ["metal", "wood"]
    assert named["FINISHES"] == ["matte", "gloss"]

    proposal = _proposal(inventory)
    target.validate_proposal_source_domains(proposal, inventory)

    incomplete = copy.deepcopy(proposal)
    incomplete["callsites"][1]["config_domain"] = ["metal"]
    with pytest.raises(ValueError, match="config domain mismatch"):
        target.validate_proposal_source_domains(incomplete, inventory)

    invented = copy.deepcopy(proposal)
    invented["callsites"][1]["config_expression"] = "r.not_a_config_field"
    with pytest.raises(ValueError, match="not a source-proven"):
        target.validate_proposal_source_domains(invented, inventory)


def test_staged_source_override_proves_scope_and_rejects_sha_drift() -> None:
    inventory = _inventory()
    proposal = _proposal(inventory)
    rows = inventory["callsites"]
    assert isinstance(rows, list)
    trim = next(row for row in rows if row["visual_name"] == "trim")
    trim["allowed_config_expressions"] = {}

    target.validate_proposal_source_domains(
        proposal,
        inventory,
        source_override=TEMPLATE_SOURCE,
    )

    with pytest.raises(ValueError, match="scope source override does not match inventory SHA"):
        target.validate_proposal_source_domains(
            proposal,
            inventory,
            source_override=TEMPLATE_SOURCE + "\n",
        )


def test_scalar_constant_domain_recovery_preserves_material_payload_and_is_idempotent() -> None:
    inventory = _inventory()
    proposal = _proposal(inventory)
    _add_material_proposals(proposal)
    rows = proposal["callsites"]
    assert isinstance(rows, list)
    shell = next(row for row in rows if row["visual_name"] == "shell")
    shell["config_domain"] = "*"
    original_material_payloads = {
        str(row["callsite_id"]): copy.deepcopy(row.get("proposals"))
        for row in rows
        if row["decision"] == "material_class"
    }

    normalized, audits = target._normalize_received_proposal(proposal, inventory)
    normalized_rows = normalized["callsites"]
    assert isinstance(normalized_rows, list)
    normalized_shell = next(row for row in normalized_rows if row["visual_name"] == "shell")
    assert normalized_shell["config_domain"] == ["*"]
    assert {
        str(row["callsite_id"]): row.get("proposals")
        for row in normalized_rows
        if row["decision"] == "material_class"
    } == original_material_payloads
    assert [audit["reason"] for audit in audits] == ["strict_json_container_recovery"]

    normalized_again, second_audits = target._normalize_received_proposal(normalized, inventory)
    assert normalized_again == normalized
    assert second_audits == []

    unsafe = copy.deepcopy(proposal)
    unsafe_rows = unsafe["callsites"]
    assert isinstance(unsafe_rows, list)
    unsafe_shell = next(row for row in unsafe_rows if row["visual_name"] == "shell")
    unsafe_shell["config_expression"] = "r.kind"
    with pytest.raises(ValueError, match="unsafe scalar config_domain"):
        target._normalize_received_proposal(unsafe, inventory)


def test_visual_name_recovery_is_narrow_and_rejects_unrelated_names() -> None:
    inventory = _inventory()
    proposal = _proposal(inventory)
    rows = proposal["callsites"]
    assert isinstance(rows, list)
    shell = next(row for row in rows if row["visual_name"] == "shell")
    shell["visual_name"] = "(shell)"

    normalized, audits = target._normalize_received_proposal(proposal, inventory)
    normalized_rows = normalized["callsites"]
    assert isinstance(normalized_rows, list)
    assert (
        next(row for row in normalized_rows if row["callsite_id"] == shell["callsite_id"])[
            "visual_name"
        ]
        == "shell"
    )
    assert [audit["reason"] for audit in audits] == ["source_inventory_canonical_echo"]
    assert target._recoverable_visual_name("f'shell_{r.kind}", "f'shell_{r.kind}'")
    assert not target._recoverable_visual_name("trim", "shell")
    assert not target._recoverable_visual_name(None, "shell")

    unrelated = copy.deepcopy(proposal)
    unrelated_rows = unrelated["callsites"]
    assert isinstance(unrelated_rows, list)
    unrelated_shell = next(
        row for row in unrelated_rows if row["callsite_id"] == shell["callsite_id"]
    )
    unrelated_shell["visual_name"] = "unrelated"
    with pytest.raises(ValueError, match="unrecoverable visual-name mismatch"):
        target._normalize_received_proposal(unrelated, inventory)


def test_config_type_expression_recovery_requires_one_matching_scope_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inventory = _inventory()
    proposal = _proposal(inventory)
    _add_material_proposals(proposal)
    rows = proposal["callsites"]
    assert isinstance(rows, list)
    trim = next(row for row in rows if row["visual_name"] == "trim")
    trim["config_expression"] = "ResolvedConfig.kind"
    original_proposals = copy.deepcopy(trim["proposals"])

    monkeypatch.setattr(
        target,
        "_scope_domains_for_inventory",
        lambda _inventory_row, _callsite_id: {"r.kind": ["metal", "wood"]},
    )
    normalized, audits = target._normalize_received_proposal(proposal, inventory)
    normalized_rows = normalized["callsites"]
    assert isinstance(normalized_rows, list)
    normalized_trim = next(row for row in normalized_rows if row["visual_name"] == "trim")
    assert normalized_trim["config_expression"] == "r.kind"
    assert normalized_trim["proposals"] == original_proposals
    assert [audit["reason"] for audit in audits] == ["unique_in_scope_resolved_config_root"]

    ambiguous = copy.deepcopy(proposal)
    monkeypatch.setattr(
        target,
        "_scope_domains_for_inventory",
        lambda _inventory_row, _callsite_id: {
            "r.kind": ["metal", "wood"],
            "resolved.kind": ["metal", "wood"],
        },
    )
    ambiguous_normalized, ambiguous_audits = target._normalize_received_proposal(
        ambiguous, inventory
    )
    ambiguous_rows = ambiguous_normalized["callsites"]
    assert isinstance(ambiguous_rows, list)
    ambiguous_trim = next(row for row in ambiguous_rows if row["visual_name"] == "trim")
    assert ambiguous_trim["config_expression"] == "ResolvedConfig.kind"
    assert ambiguous_audits == []
    with pytest.raises(ValueError, match="not a source-proven"):
        target.validate_proposal_source_domains(ambiguous_normalized, inventory)


def test_flat_pbr_correction_is_exactly_source_and_callsite_guarded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inventory = _inventory()
    proposal = _proposal(inventory)
    by_name = _callsites_by_name(inventory)
    label_id = str(by_name["label"]["callsite_id"])
    correction = target._constant_pbr_correction(
        "plastic.opaque_glossy_molded",
        "The fixture label is treated as a physical molded insert.",
    )
    monkeypatch.setattr(
        target,
        "FLAT_PBR_CORRECTIONS",
        {
            "fixture": {
                "source_sha256": inventory["template_source_sha256"],
                "callsites": {label_id: correction},
            }
        },
    )

    normalized, audits = target._normalize_received_proposal(proposal, inventory)
    normalized_rows = normalized["callsites"]
    assert isinstance(normalized_rows, list)
    label = next(row for row in normalized_rows if row["callsite_id"] == label_id)
    assert label["decision"] == "material_class"
    assert label["proposals"] == correction["proposals"]
    assert [audit["reason"] for audit in audits] == ["flat_color_hard_rule_pbr_correction"]
    assert target._flat_correction(inventory, str(by_name["shell"]["callsite_id"])) is None

    normalized_again, second_audits = target._normalize_received_proposal(normalized, inventory)
    assert normalized_again == normalized
    assert second_audits == []

    source_drift = copy.deepcopy(inventory)
    source_drift["template_source_sha256"] = "0" * 64
    with pytest.raises(ValueError, match="flat correction source SHA drifted"):
        target._normalize_received_proposal(proposal, source_drift)

    conflicting = copy.deepcopy(normalized)
    conflicting_rows = conflicting["callsites"]
    assert isinstance(conflicting_rows, list)
    conflicting_label = next(row for row in conflicting_rows if row["callsite_id"] == label_id)
    conflicting_label["proposals"][0]["material_class_id"] = "metal.brushed_steel"
    with pytest.raises(ValueError, match="normalized flat correction drifted"):
        target._normalize_received_proposal(conflicting, inventory)


def test_reachable_domain_override_is_exactly_source_and_callsite_guarded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inventory = _inventory()
    proposal = _proposal(inventory)
    by_name = _callsites_by_name(inventory)
    trim_id = str(by_name["trim"]["callsite_id"])
    rows = proposal["callsites"]
    assert isinstance(rows, list)
    trim = next(row for row in rows if row["callsite_id"] == trim_id)
    trim["config_domain"] = ["metal"]
    override = {
        "config_expression": "r.kind",
        "config_domain": ["metal"],
        "proof": "fixture helper is reachable only for the metal branch",
    }
    monkeypatch.setattr(
        target,
        "REACHABLE_DOMAIN_OVERRIDES",
        {
            (
                "fixture",
                str(inventory["template_source_sha256"]),
                trim_id,
            ): override
        },
    )

    audits = target.validate_proposal_source_domains(proposal, inventory)
    assert audits == [
        {
            "callsite_id": trim_id,
            "kind": "current_source_reachable_domain",
            "config_expression": "r.kind",
            "field_domain": ["metal", "wood"],
            "reachable_domain": ["metal"],
            "proof": override["proof"],
        }
    ]

    source_drift = copy.deepcopy(inventory)
    source_drift["template_source_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="config domain mismatch"):
        target.validate_proposal_source_domains(proposal, source_drift)

    monkeypatch.setattr(
        target,
        "REACHABLE_DOMAIN_OVERRIDES",
        {
            (
                "fixture",
                str(inventory["template_source_sha256"]),
                "fixture:999:0",
            ): override
        },
    )
    with pytest.raises(ValueError, match="config domain mismatch"):
        target.validate_proposal_source_domains(proposal, inventory)


def test_constant_dual_and_flat_rewrite_preserves_source_contracts() -> None:
    inventory = _inventory()
    annotation = _annotation(inventory)
    original = TEMPLATE_SOURCE.encode()
    before_ids = set(target._source_call_nodes(TEMPLATE_SOURCE, slug="fixture"))
    before_fingerprints = target._source_fingerprints(TEMPLATE_SOURCE)

    shadow, insertions = target.apply_annotations_to_source(
        original,
        slug="fixture",
        annotation=annotation,
    )
    shadow_text = shadow.decode()

    assert original.count(b"\n") == shadow.count(b"\n")
    assert 'name="shell", material_class_id="metal.brushed_steel", material=material' in shadow_text
    assert (
        'name="trim", material_class_id=("metal.brushed_steel" if r.kind == "metal" '
        'else "wood.natural_generic"), material=material'
    ) in shadow_text
    assert 'part.visual(object(), name="label", material=material)' in shadow_text
    assert 'name="label", material_class_id=' not in shadow_text
    assert len(insertions) == 2
    assert {row["material_class_ids"][0] for row in insertions} == {"metal.brushed_steel"}

    after_ids = set(target._source_call_nodes(shadow_text, slug="fixture"))
    assert after_ids == before_ids
    assert target._source_fingerprints(shadow_text) == before_fingerprints

    verification = target._verify_shadow_source(
        original=original,
        shadow=shadow,
        inventory_row=inventory,
        annotation=annotation,
    )
    assert verification["source_line_count"] == inventory["source_line_count"]
    assert verification["visual_callsite_count"] == 3
    assert verification["pbr_visual_count"] == 2
    assert verification["flat_color_visual_count"] == 1
    assert verification["mechanical_ast_sha256"] == before_fingerprints["mechanical_ast_sha256"]
    assert verification["rng_ast_sha256"] == before_fingerprints["rng_ast_sha256"]


def test_material_class_keyword_threading_is_appearance_only() -> None:
    before = """\
def _add(part, shape, name):
    part.visual(shape, name=name)


def build(part, shape):
    _add(part, shape, "shell")
"""
    after = """\
def _add(part, shape, name, *, material_class_id="metal.paint_coated"):
    part.visual(shape, name=name, material_class_id=material_class_id)


def build(part, shape):
    _add(part, shape, "shell", material_class_id="wood.bark")
"""

    assert target._source_fingerprints(after) == target._source_fingerprints(before)


def test_dual_material_helper_writeback_and_tamper_guards(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inventory = _inventory()
    annotation = _annotation(inventory)
    trim_id = str(_callsites_by_name(inventory)["trim"]["callsite_id"])
    monkeypatch.setattr(target, "MATERIAL_HELPER_CALLSITE_IDS", frozenset({trim_id}))
    original = TEMPLATE_SOURCE.encode()
    before_nodes = target._source_call_nodes(TEMPLATE_SOURCE, slug="fixture")
    before_names = {
        callsite_id: target._visual_name(node)[0] for callsite_id, (node, _) in before_nodes.items()
    }
    before_fingerprints = target._source_fingerprints(TEMPLATE_SOURCE)

    shadow, insertions = target.apply_annotations_to_source(
        original,
        slug="fixture",
        annotation=annotation,
    )
    shadow_text = shadow.decode()
    expected_call = (
        'material_class_id=_material_class_id(r.kind, ("metal",), '
        '"metal.brushed_steel", "wood.natural_generic")'
    )
    assert expected_call in shadow_text
    assert shadow_text.count("def _material_class_id(") == 1
    assert shadow.endswith(b"\n\n" + target.MATERIAL_CLASS_HELPER_DEFINITION.encode("ascii"))
    assert {row["callsite_id"]: row["writeback_mode"] for row in insertions} == {
        str(_callsites_by_name(inventory)["shell"]["callsite_id"]): "inline_scalar",
        trim_id: "material_helper",
    }

    after_nodes = target._source_call_nodes(shadow_text, slug="fixture")
    after_names = {
        callsite_id: target._visual_name(node)[0] for callsite_id, (node, _) in after_nodes.items()
    }
    assert set(after_nodes) == set(before_nodes)
    assert after_names == before_names
    assert target._source_fingerprints(shadow_text) == before_fingerprints

    verification = target._verify_shadow_source(
        original=original,
        shadow=shadow,
        inventory_row=inventory,
        annotation=annotation,
    )
    assert verification["material_class_helper_count"] == 1
    for fingerprint, expected in before_fingerprints.items():
        assert verification[fingerprint] == expected

    tampered_helper = shadow.replace(
        b"return first_id if value in first_values else second_id",
        b"return second_id if value in first_values else first_id",
        1,
    )
    assert tampered_helper != shadow
    with pytest.raises(ValueError, match="unexpected material-class helper"):
        target._verify_shadow_source(
            original=original,
            shadow=tampered_helper,
            inventory_row=inventory,
            annotation=annotation,
        )

    tampered_call = shadow.replace(
        b"_material_class_id(r.kind,",
        b"_material_class_id(r.finish,",
        1,
    )
    assert tampered_call != shadow
    with pytest.raises(ValueError, match="material expression drifted"):
        target._verify_shadow_source(
            original=original,
            shadow=tampered_call,
            inventory_row=inventory,
            annotation=annotation,
        )


def test_aquarium_role_routed_helper_maps_every_palette_material_and_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inventory = _inventory(AQUARIUM_HELPER_SOURCE, slug="aquarium")
    row = _callsites_by_name(inventory)["name"]
    callsite_id = str(row["callsite_id"])
    monkeypatch.setattr(target, "AQUARIUM_ROLE_ROUTED_CALLSITE_ID", callsite_id)
    monkeypatch.setattr(
        target,
        "AQUARIUM_ROLE_ROUTED_SOURCE_SHA256",
        str(inventory["template_source_sha256"]),
    )
    monkeypatch.setattr(
        target,
        "MATERIAL_HELPER_CALLSITE_IDS",
        target.MATERIAL_HELPER_CALLSITE_IDS | {callsite_id},
    )
    annotation = {
        "schema_version": "fixture",
        "policy_version": "fixture",
        "callsites": [
            {
                "callsite_id": callsite_id,
                "visual_name": "name",
                "decision": "material_class",
                "config_expression": None,
                "config_domain": ["*"],
                "branches": [
                    {
                        "config_values": ["*"],
                        "material_class_id": "plastic.opaque_generic",
                    }
                ],
                "source_material_class_ids": ["plastic.opaque_generic"],
                "compression": None,
            }
        ],
    }

    corrected, audits = target._apply_role_routed_annotation_overrides(
        annotation,
        inventory,
    )
    corrected_row = corrected["callsites"][0]
    assert corrected_row["routing_kind"] == target.GENERATOR_CLASS_ROLE_ROUTING_KIND
    assert len(corrected_row["branches"]) == 8
    assert len(corrected_row["config_domain"]) == 60
    assert audits[0]["runtime_material_name_count"] == 60

    original = AQUARIUM_HELPER_SOURCE.encode()
    shadow, insertions = target.apply_annotations_to_source(
        original,
        slug="aquarium",
        annotation=corrected,
    )
    assert insertions[0]["expression"] == "_material_class_id(material.name)"
    verification = target._verify_shadow_source(
        original=original,
        shadow=shadow,
        inventory_row=inventory,
        annotation=corrected,
    )
    assert verification["material_class_helper_count"] == 1

    helper = next(
        node
        for node in ast.parse(shadow.decode()).body
        if isinstance(node, ast.FunctionDef) and node.name == "_material_class_id"
    )
    namespace: dict[str, object] = {}
    exec(compile(ast.Module(body=[helper], type_ignores=[]), "<helper>", "exec"), namespace)
    material_class_id = namespace["_material_class_id"]
    assert callable(material_class_id)
    for material_name, expected_class_id in target.AQUARIUM_MATERIAL_CLASS_BY_NAME.items():
        assert material_class_id(material_name) == expected_class_id
    with pytest.raises(ValueError, match="Unsupported aquarium material role"):
        material_class_id("aq_unknown_classic_warm")

    usage = target._annotation_usage(
        [corrected], class_ids=set(corrected_row["source_material_class_ids"])
    )
    assert usage["role_routed_helper_callsite_count"] == 1


def test_composition_source_must_remain_byte_identical() -> None:
    original = COMPOSITION_SOURCE.encode()
    inventory = _inventory(COMPOSITION_SOURCE, slug="composition")

    verification = target._verify_shadow_source(
        original=original,
        shadow=original,
        inventory_row=inventory,
        annotation=None,
    )
    assert verification["visual_callsite_count"] == 0
    assert verification["original_sha256"] == verification["shadow_sha256"]

    equivalent_but_not_identical = COMPOSITION_SOURCE.replace(
        "build_dependency()", "build_dependency( )"
    ).encode()
    with pytest.raises(ValueError, match="must remain byte-identical"):
        target._verify_shadow_source(
            original=original,
            shadow=equivalent_but_not_identical,
            inventory_row=inventory,
            annotation=None,
        )


def test_flat_color_without_existing_material_is_rejected() -> None:
    source = """\
def build(model):
    part = model.part("body")
    part.visual(object(), name="label")
"""
    inventory = _inventory(source, slug="invalid_flat")
    row = _callsites_by_name(inventory)["label"]
    annotation = {
        "callsites": [
            {
                "callsite_id": row["callsite_id"],
                "visual_name": "label",
                "decision": "flat_color",
            }
        ]
    }

    with pytest.raises(ValueError, match="lacks an explicit existing material"):
        target.apply_annotations_to_source(
            source.encode(),
            slug="invalid_flat",
            annotation=annotation,
        )


def test_fleet_constants_protect_canaries_support_files_and_composition() -> None:
    assert target.CANARY_FILES == (
        "Container_Glass_bottle.py",
        "Container_Plastic_can.py",
        "Handtools_clothes_peg.py",
        "Urban_Environment_Large_Trashcan.py",
        "loom_shuttle.py",
    )
    assert target.SUPPORT_FILES == ("__init__.py", "_mechanisms.py", "_modular.py")
    assert set(target.CANARY_FILES).isdisjoint(target.SUPPORT_FILES)
    assert target.EXPECTED_GENERATOR_COUNT == 531
    assert target.EXPECTED_REMAINING_COUNT == (
        target.EXPECTED_GENERATOR_COUNT - len(target.CANARY_FILES)
    )
    assert target.EXPECTED_REMAINING_CALLSITE_COUNT == 17_640
    assert target.EXPECTED_COMPOSITION_ONLY == "Urban_Environment_Public_toilet1.py"
    assert target.COMPOSITION_DEPENDENCIES == {
        "Urban_Environment_Public_toilet1.py": (
            "Urban_Environment_Public_toilet.py",
            "Bathroom_toilet.py",
        )
    }


def test_record_gates_requires_exactly_all_six_passes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    summary_path = Path("summary.json")
    writes: list[dict[str, object]] = []
    monkeypatch.setattr(target, "_run_path", lambda _run_dir, *_parts: summary_path)
    monkeypatch.setattr(target, "_json_object", lambda _path: {"status": "verified"})
    monkeypatch.setattr(
        target,
        "_atomic_json",
        lambda _path, payload: writes.append(copy.deepcopy(payload)),
    )
    required = sorted(target.REQUIRED_FINAL_GATES)
    assert len(required) == 6

    partial = target.record_gates(Path("unused"), [f"{name}=pass" for name in required[:-1]])
    assert partial["status"] == "verified"

    one_failed = target.record_gates(
        Path("unused"),
        [f"{name}={'fail' if index == 0 else 'pass'}" for index, name in enumerate(required)],
    )
    assert one_failed["status"] == "verified"

    extra = target.record_gates(
        Path("unused"),
        [*(f"{name}=pass" for name in required), "unexpected=pass"],
    )
    assert extra["status"] == "verified"

    complete = target.record_gates(Path("unused"), [f"{name}=pass" for name in required])
    assert complete["status"] == "complete"
    assert complete["gates"] == {name: "pass" for name in required}
    assert writes[-1] == complete


def test_writeback_loads_inventory_without_live_source_verification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[Path, bool]] = []

    class StopAfterInventoryLoad(Exception):
        pass

    def fake_load_inventory(run_dir: Path, *, verify_sources: bool = True) -> dict[str, object]:
        calls.append((run_dir, verify_sources))
        raise StopAfterInventoryLoad

    monkeypatch.setattr(target, "load_inventory", fake_load_inventory)
    run_dir = Path("unused")
    with pytest.raises(StopAfterInventoryLoad):
        target.writeback(run_dir)
    assert calls == [(run_dir, False)]
