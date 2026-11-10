# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from copy import deepcopy

import pytest

from articraft.appearance import (
    GENERATOR_CLASS_ANNOTATION_POLICY,
    GENERATOR_CLASS_ANNOTATIONS_SCHEMA,
    GENERATOR_CLASS_PROPOSALS_SCHEMA,
    GENERATOR_CLASS_ROLE_ROUTED_ANNOTATION_POLICY,
    GENERATOR_CLASS_ROLE_ROUTED_ANNOTATIONS_SCHEMA,
    GENERATOR_CLASS_ROLE_ROUTING_KIND,
    MAX_MATERIAL_CLASS_VARIANTS,
    annotation_digest,
    build_generator_class_annotations,
    validate_generator_class_annotations,
)

LIBRARY_SHA = "1" * 64
SOURCE_SHA = "2" * 64
AVAILABLE = {
    "wood.natural_generic",
    "wood.painted_clean",
    "plastic.opaque_generic",
    "metal.generic_plain",
}
CALLSITES = {
    "fixture:10:4": "body",
    "fixture:20:4": "marker",
}


def _document(body: dict) -> dict:
    return {
        "schema_version": GENERATOR_CLASS_PROPOSALS_SCHEMA,
        "policy_version": GENERATOR_CLASS_ANNOTATION_POLICY,
        "library_snapshot_sha256": LIBRARY_SHA,
        "template_slug": "fixture",
        "template_source_sha256": SOURCE_SHA,
        "callsites": [
            body,
            {
                "callsite_id": "fixture:20:4",
                "visual_name": "marker",
                "decision": "flat_color",
            },
        ],
    }


def _proposal(
    config_value: str,
    material_class_id: str,
    priority: int,
) -> dict:
    return {
        "config_values": [config_value],
        "material_class_id": material_class_id,
        "priority": priority,
        "rationale": f"source branch {config_value}",
    }


def _build(document: dict) -> dict:
    return build_generator_class_annotations(
        document,
        available_material_class_ids=AVAILABLE,
        expected_library_snapshot_sha256=LIBRARY_SHA,
        expected_template_source_sha256=SOURCE_SHA,
        expected_callsites=CALLSITES,
    )


def test_constant_and_two_class_rules_remain_scalar() -> None:
    constant = _document(
        {
            "callsite_id": "fixture:10:4",
            "visual_name": "body",
            "decision": "material_class",
            "config_expression": None,
            "config_domain": ["*"],
            "proposals": [_proposal("*", "wood.natural_generic", 100)],
        }
    )
    constant_result = _build(constant)
    constant_body = constant_result["callsites"][0]
    assert constant_body["branches"] == [
        {
            "config_values": ["*"],
            "material_class_id": "wood.natural_generic",
        }
    ]
    assert constant_body["compression"] is None

    conditional = deepcopy(constant)
    conditional["callsites"][0].update(
        config_expression="r.body_material",
        config_domain=["wood", "plastic"],
        proposals=[
            _proposal("wood", "wood.natural_generic", 100),
            _proposal("plastic", "plastic.opaque_generic", 90),
        ],
    )
    conditional_result = _build(conditional)
    conditional_body = conditional_result["callsites"][0]
    assert len(conditional_body["branches"]) == 2
    assert conditional_body["compression"] is None
    assert {branch["material_class_id"] for branch in conditional_body["branches"]} == {
        "wood.natural_generic",
        "plastic.opaque_generic",
    }


def test_four_classes_are_deterministically_compressed_to_two() -> None:
    body = {
        "callsite_id": "fixture:10:4",
        "visual_name": "body",
        "decision": "material_class",
        "config_expression": "r.body_material",
        "config_domain": ["natural", "painted", "plastic", "metal"],
        "proposals": [
            _proposal("natural", "wood.natural_generic", 100),
            _proposal("painted", "wood.painted_clean", 95),
            _proposal("plastic", "plastic.opaque_generic", 90),
            _proposal("metal", "metal.generic_plain", 80),
        ],
    }

    result = _build(_document(body))
    reversed_result = _build(_document({**body, "proposals": list(reversed(body["proposals"]))}))

    assert result == reversed_result
    annotation = result["callsites"][0]
    assert len(annotation["branches"]) == MAX_MATERIAL_CLASS_VARIANTS
    assert annotation["compression"] == {
        "source_material_class_count": 4,
        "retained_material_class_ids": [
            "wood.natural_generic",
            "plastic.opaque_generic",
        ],
        "discarded": [
            {
                "material_class_id": "wood.painted_clean",
                "mapped_to_material_class_id": "wood.natural_generic",
                "reason": "hard_max2_auto_compression",
            },
            {
                "material_class_id": "metal.generic_plain",
                "mapped_to_material_class_id": "wood.natural_generic",
                "reason": "hard_max2_auto_compression",
            },
        ],
    }
    by_value = {
        config_value: branch["material_class_id"]
        for branch in annotation["branches"]
        for config_value in branch["config_values"]
    }
    assert by_value == {
        "natural": "wood.natural_generic",
        "painted": "wood.natural_generic",
        "plastic": "plastic.opaque_generic",
        "metal": "wood.natural_generic",
    }
    assert len(annotation_digest(result)) == 64


def test_final_schema_rejects_more_than_two_or_incomplete_config_coverage() -> None:
    result = _build(
        _document(
            {
                "callsite_id": "fixture:10:4",
                "visual_name": "body",
                "decision": "material_class",
                "config_expression": "r.body_material",
                "config_domain": ["natural", "plastic"],
                "proposals": [
                    _proposal("natural", "wood.natural_generic", 100),
                    _proposal("plastic", "plastic.opaque_generic", 90),
                ],
            }
        )
    )
    invalid = deepcopy(result)
    body = invalid["callsites"][0]
    body["config_domain"].append("missing")
    with pytest.raises(ValueError, match="does not partition config_domain"):
        validate_generator_class_annotations(
            invalid,
            available_material_class_ids=AVAILABLE,
            expected_library_snapshot_sha256=LIBRARY_SHA,
            expected_template_source_sha256=SOURCE_SHA,
            expected_callsites=CALLSITES,
        )

    over_limit = deepcopy(result)
    body = over_limit["callsites"][0]
    body["config_domain"] = ["a", "b", "c", "d"]
    body["branches"] = [
        {"config_values": [value], "material_class_id": class_id}
        for value, class_id in zip(
            body["config_domain"],
            sorted(AVAILABLE),
            strict=True,
        )
    ]
    body["source_material_class_ids"] = sorted(AVAILABLE)
    body["compression"] = None
    with pytest.raises(ValueError, match="hard maximum of 2"):
        validate_generator_class_annotations(
            over_limit,
            available_material_class_ids=AVAILABLE,
            expected_library_snapshot_sha256=LIBRARY_SHA,
            expected_template_source_sha256=SOURCE_SHA,
            expected_callsites=CALLSITES,
        )

    compressed = _build(
        _document(
            {
                "callsite_id": "fixture:10:4",
                "visual_name": "body",
                "decision": "material_class",
                "config_expression": "r.body_material",
                "config_domain": ["natural", "painted", "plastic"],
                "proposals": [
                    _proposal("natural", "wood.natural_generic", 100),
                    _proposal("painted", "wood.painted_clean", 90),
                    _proposal("plastic", "plastic.opaque_generic", 80),
                ],
            }
        )
    )
    compressed["callsites"][0]["compression"]["discarded"][0]["reason"] = "manual"
    with pytest.raises(ValueError, match="hard_max2_auto_compression"):
        validate_generator_class_annotations(
            compressed,
            available_material_class_ids=AVAILABLE,
            expected_library_snapshot_sha256=LIBRARY_SHA,
            expected_template_source_sha256=SOURCE_SHA,
            expected_callsites=CALLSITES,
        )


def test_role_routed_policy_allows_exact_source_roles_without_max2_compression() -> None:
    standard = _build(
        _document(
            {
                "callsite_id": "fixture:10:4",
                "visual_name": "body",
                "decision": "material_class",
                "config_expression": "material.name",
                "config_domain": ["glass", "frame"],
                "proposals": [
                    _proposal("glass", "plastic.opaque_generic", 100),
                    _proposal("frame", "metal.generic_plain", 90),
                ],
            }
        )
    )
    role_routed = deepcopy(standard)
    role_routed["schema_version"] = GENERATOR_CLASS_ROLE_ROUTED_ANNOTATIONS_SCHEMA
    role_routed["policy_version"] = GENERATOR_CLASS_ROLE_ROUTED_ANNOTATION_POLICY
    body = role_routed["callsites"][0]
    body["config_domain"] = ["glass", "frame", "plant", "rock"]
    body["branches"] = [
        {"config_values": [value], "material_class_id": class_id}
        for value, class_id in zip(body["config_domain"], sorted(AVAILABLE), strict=True)
    ]
    body["source_material_class_ids"] = sorted(AVAILABLE)
    body["compression"] = None
    body["routing_kind"] = GENERATOR_CLASS_ROLE_ROUTING_KIND

    assert (
        validate_generator_class_annotations(
            role_routed,
            available_material_class_ids=AVAILABLE,
            expected_library_snapshot_sha256=LIBRARY_SHA,
            expected_template_source_sha256=SOURCE_SHA,
            expected_callsites=CALLSITES,
        )
        == role_routed
    )

    missing_routing = deepcopy(role_routed)
    missing_routing["callsites"][0].pop("routing_kind")
    with pytest.raises(ValueError, match="hard maximum of 2"):
        validate_generator_class_annotations(
            missing_routing,
            available_material_class_ids=AVAILABLE,
            expected_library_snapshot_sha256=LIBRARY_SHA,
            expected_template_source_sha256=SOURCE_SHA,
            expected_callsites=CALLSITES,
        )

    no_role_callsite = deepcopy(standard)
    no_role_callsite["schema_version"] = GENERATOR_CLASS_ROLE_ROUTED_ANNOTATIONS_SCHEMA
    no_role_callsite["policy_version"] = GENERATOR_CLASS_ROLE_ROUTED_ANNOTATION_POLICY
    with pytest.raises(ValueError, match="has no role-routed callsite"):
        validate_generator_class_annotations(
            no_role_callsite,
            available_material_class_ids=AVAILABLE,
            expected_library_snapshot_sha256=LIBRARY_SHA,
            expected_template_source_sha256=SOURCE_SHA,
            expected_callsites=CALLSITES,
        )


def test_old_or_loose_documents_are_not_accepted() -> None:
    valid = _document(
        {
            "callsite_id": "fixture:10:4",
            "visual_name": "body",
            "decision": "material_class",
            "config_expression": None,
            "config_domain": ["*"],
            "proposals": [_proposal("*", "wood.natural_generic", 100)],
        }
    )
    old = deepcopy(valid)
    old["schema_version"] = "articraft-generator-material-class-proposals/v0"
    with pytest.raises(ValueError, match="unsupported"):
        _build(old)

    loose = deepcopy(valid)
    loose["callsites"][0]["category_variants"] = []
    with pytest.raises(ValueError, match="fields do not match v1"):
        _build(loose)

    unknown = deepcopy(valid)
    unknown["callsites"][0]["proposals"][0]["material_class_id"] = "wood.unknown"
    with pytest.raises(ValueError, match="unavailable material class"):
        _build(unknown)


def test_callsite_coverage_and_source_digest_are_hard_boundaries() -> None:
    valid = _document(
        {
            "callsite_id": "fixture:10:4",
            "visual_name": "body",
            "decision": "material_class",
            "config_expression": None,
            "config_domain": ["*"],
            "proposals": [_proposal("*", "wood.natural_generic", 100)],
        }
    )
    missing = deepcopy(valid)
    missing["callsites"].pop()
    with pytest.raises(ValueError, match="callsite coverage mismatch"):
        _build(missing)

    stale = deepcopy(valid)
    stale["template_source_sha256"] = "3" * 64
    with pytest.raises(ValueError, match="template source mismatch"):
        _build(stale)

    assert GENERATOR_CLASS_ANNOTATIONS_SCHEMA.endswith("/v1")
