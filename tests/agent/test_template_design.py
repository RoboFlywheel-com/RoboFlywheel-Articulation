# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from pathlib import Path

import pytest

from agent.template_design import (
    CandidateDesign,
    CategoryAnchorAppliesTo,
    CategoryAnchorDesign,
    CategoryRelationRequirement,
    CategoryRoleRequirement,
    InterfaceDesign,
    ParameterDesign,
    SlotDesign,
    SurfaceRelationDesign,
    TemplateDesign,
    TemplateDesignError,
    load_template_design,
    scaffold_template_design,
    write_template_design,
)


def _write_source_record(records: Path, record_id: str, *, lines: int = 60) -> None:
    record = records / record_id
    revision = record / "revisions" / "rev_000001"
    revision.mkdir(parents=True)
    (record / "collections").mkdir()
    (record / "record.json").write_text(
        '{"collections":["workbench"],"active_revision_id":"rev_000001"}',
        encoding="utf-8",
    )
    (record / "picture.json").write_text(
        '{"category":"Demo","subcategory":"widget"}',
        encoding="utf-8",
    )
    (record / "collections" / "workbench.json").write_text(
        '{"archived":false}',
        encoding="utf-8",
    )
    (revision / "model.py").write_text(
        "\n".join(f"# line {index}" for index in range(1, lines + 1)) + "\n",
        encoding="utf-8",
    )


def test_source_map_scaffolds_small_deterministic_design(tmp_path: Path) -> None:
    records = tmp_path / "records"
    _write_source_record(records, "rec_alpha")
    source_map = tmp_path / "source-map.md"
    source_map.write_text(
        """source_map_schema: 1
export_category: demo
picture_category: Demo
picture_subcategory: widget
category_scope: compact demonstration widget

sync_records:
  - rec_alpha

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_alpha/rev_000001 | reviewed | used | source-backed wheel |

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| wheel | spoked | wheel | rec_alpha/rev_000001 | model.py:L10-L40 | structure | hub and rim |
""",
        encoding="utf-8",
    )

    design, resolution = scaffold_template_design(
        slug="demo",
        source_map=source_map,
        records_root=records,
    )

    assert resolution.verdict == "pass"
    assert [slot.name for slot in design.slots] == ["wheel"]
    assert design.slots[0].candidates[0].implementation_function == "_wheel_spoked_build"

    output = tmp_path / "design.json"
    write_template_design(design, output)
    assert load_template_design(output) == design


def test_template_design_rejects_removed_gate_field(tmp_path: Path) -> None:
    path = tmp_path / "design.json"
    path.write_text(
        '{"schema_version": 1, "slug": "demo", "source_map_path": "map.md", '
        '"source_map_sha256": "abc", "slots": [], "gates": []}',
        encoding="utf-8",
    )

    with pytest.raises(TemplateDesignError, match="no longer supports gates"):
        load_template_design(path)


def test_parameter_design_accepts_semantic_units_and_rejects_unknown_unit() -> None:
    assert ParameterDesign(name="radius", unit="m").validate("candidate") == []
    assert ParameterDesign(name="angle", unit="rad").validate("candidate") == []
    assert ParameterDesign(name="count", value_type="int", unit="count").validate("candidate") == []
    assert ParameterDesign(name="radius", unit="centimeters").validate("candidate")


def test_template_design_round_trips_category_anchors(tmp_path: Path) -> None:
    design = TemplateDesign(
        slug="demo",
        source_map_path="map.md",
        source_map_sha256="abc",
        slots=(
            SlotDesign(
                name="family",
                component_type="tool_set",
                candidates=(
                    CandidateDesign(
                        name="rack",
                        implementation_function="_family_rack_build",
                    ),
                ),
            ),
        ),
        category_anchors=(
            CategoryAnchorDesign(
                anchor_id="rack_identity",
                applies_to=CategoryAnchorAppliesTo(
                    slot="family",
                    candidates=("rack",),
                ),
                required_roles=(
                    CategoryRoleRequirement(role="holder", exact_count=1),
                ),
                required_relations=(
                    CategoryRelationRequirement(
                        parent_role="holder",
                        child_role="tool",
                        joint_type="prismatic",
                        axis=(0.0, 1.0, 0.0),
                    ),
                ),
                required_author_checks=("category_anchor: real tool profile",),
            ),
        ),
    )
    output = tmp_path / "design.json"
    write_template_design(design, output)
    assert load_template_design(output) == design


def test_template_design_round_trips_surface_relation_contract(tmp_path: Path) -> None:
    author_check = "category_anchor: controls remain exposed through their openings"
    design = TemplateDesign(
        slug="demo",
        source_map_path="map.md",
        source_map_sha256="abc",
        slots=(
            SlotDesign(
                name="controls",
                component_type="surface controls",
                candidates=(
                    CandidateDesign(
                        name="buttons",
                        implementation_function="_controls_buttons_build",
                        interfaces=(
                            InterfaceDesign(
                                name="host_mount",
                                kind="plane",
                                role="consumer",
                                part="button_deck",
                                surface_relation=SurfaceRelationDesign(
                                    subject_role="button",
                                    opening_expression="button footprint plus 0.3 mm clearance",
                                    normal_band_expression=(
                                        "well floor <= cap base < cap crown <= face rim"
                                    ),
                                    motion_expression=(
                                        "pressed cap remains inside the opening across travel"
                                    ),
                                    required_author_check=author_check,
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
        category_anchors=(
            CategoryAnchorDesign(
                anchor_id="button_visibility",
                applies_to=CategoryAnchorAppliesTo(
                    slot="controls",
                    candidates=("buttons",),
                ),
                required_roles=(CategoryRoleRequirement(role="button", exact_count=1),),
                required_author_checks=(author_check,),
            ),
        ),
    )

    output = tmp_path / "design.json"
    write_template_design(design, output)
    assert load_template_design(output) == design
    assert design.validate() == []


def test_surface_relation_requires_matching_category_anchor_contract() -> None:
    design = TemplateDesign(
        slug="demo",
        source_map_path="map.md",
        source_map_sha256="abc",
        slots=(
            SlotDesign(
                name="controls",
                component_type="surface controls",
                candidates=(
                    CandidateDesign(
                        name="buttons",
                        implementation_function="_controls_buttons_build",
                        interfaces=(
                            InterfaceDesign(
                                name="host_mount",
                                kind="plane",
                                role="consumer",
                                part="button_deck",
                                surface_relation=SurfaceRelationDesign(
                                    subject_role="button",
                                    opening_expression="button opening",
                                    normal_band_expression="cap exposure band",
                                    required_author_check="category_anchor: button is visible",
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    findings = design.validate()
    assert any("subject_role 'button' is not required" in finding for finding in findings)
    assert any("required_author_check" in finding for finding in findings)


def test_category_anchor_rejects_bad_selector_and_count_contract() -> None:
    design = TemplateDesign(
        slug="demo",
        source_map_path="map.md",
        source_map_sha256="abc",
        slots=(
            SlotDesign(
                name="family",
                component_type="tool_set",
                candidates=(
                    CandidateDesign(
                        name="rack",
                        implementation_function="_family_rack_build",
                    ),
                ),
            ),
        ),
        category_anchors=(
            CategoryAnchorDesign(
                anchor_id="rack_identity",
                applies_to=CategoryAnchorAppliesTo(
                    slot="family",
                    candidates=("missing",),
                ),
                required_roles=(
                    CategoryRoleRequirement(
                        role="holder",
                        exact_count=1,
                        count_from="tool_count",
                    ),
                ),
            ),
        ),
    )
    findings = design.validate()
    assert any("unknown candidates" in finding for finding in findings)
    assert any("exactly one of exact_count or count_from" in finding for finding in findings)
