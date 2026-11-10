# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import dataclasses
import types
from dataclasses import dataclass
from pathlib import Path

from agent import template_preflight
from agent.template_design import (
    AssemblyBindingDesign,
    CandidateDesign,
    CategoryAnchorAppliesTo,
    CategoryAnchorDesign,
    CategoryRelationRequirement,
    CategoryRoleRequirement,
    MultiplicityDesign,
    ParameterDesign,
    SlotDesign,
    TemplateDesign,
)
from agent.template_policy import forbidden_overlap_allowances, overlap_policy_result
from agent.template_preflight import (
    derivation_checks,
    design_alignment_checks,
    quality_contract,
    source_hygiene_checks,
)
from sdk import (
    TemplateDomain,
    component_slot,
    multiplicity_slot,
)


def _candidate(name: str, **kwargs) -> CandidateDesign:
    return CandidateDesign(
        name=name,
        implementation_function=f"_build_{name}",
        **kwargs,
    )


def _design(
    slots: tuple[SlotDesign, ...],
    *,
    multiplicities: tuple[MultiplicityDesign, ...] = (),
    bindings: tuple[AssemblyBindingDesign, ...] = (),
    category_anchors: tuple[CategoryAnchorDesign, ...] = (),
) -> TemplateDesign:
    return TemplateDesign(
        slug="demo",
        source_map_path="source_maps/demo.md",
        source_map_sha256="abc",
        slots=slots,
        multiplicities=multiplicities,
        bindings=bindings,
        category_anchors=category_anchors,
    )


def test_source_hygiene_blocks_duplicate_definitions_but_not_reassigned_constants(
    tmp_path: Path,
) -> None:
    path = tmp_path / "demo.py"
    path.write_text(
        "VALUE = 1\n"
        "VALUE = 2\n\n"
        "def helper():\n"
        "    return 1\n\n"
        "def helper():\n"
        "    return 2\n\n"
        "def run_demo_tests():\n"
        "    return True\n\n"
        "run_demo_tests = helper\n",
        encoding="utf-8",
    )

    findings, _details = source_hygiene_checks(
        path,
        required_exports=("run_demo_tests",),
    )

    assert {finding["code"] for finding in findings if finding["blocking"]} == {
        "duplicate_top_level_definition",
        "required_export_overwritten",
    }
    assert all(finding["owner"].get("symbol") != "VALUE" for finding in findings)


def test_source_hygiene_blocks_allow_overlap_only_when_policy_enabled(tmp_path: Path) -> None:
    path = tmp_path / "demo.py"
    path.write_text(
        "def run_demo_tests(ctx):\n    ctx.allow_overlap('base', 'child', reason='captured')\n",
        encoding="utf-8",
    )

    legacy_findings, _ = source_hygiene_checks(
        path,
        required_exports=("run_demo_tests",),
    )
    design_findings, details = source_hygiene_checks(
        path,
        required_exports=("run_demo_tests",),
        forbid_overlap=True,
    )

    assert not any(item["code"] == "overlap_allowance_forbidden" for item in legacy_findings)
    assert any(
        item["code"] == "overlap_allowance_forbidden" and item["blocking"]
        for item in design_findings
    )
    assert details["overlap_policy"] == "forbidden"


def test_source_hygiene_warns_for_explicit_micron_contact_tolerance(
    tmp_path: Path,
) -> None:
    path = tmp_path / "demo.py"
    path.write_text(
        "def run_demo_tests(ctx):\n"
        "    ctx.expect_contact('base', 'child', contact_tol=1e-6)\n"
        "    ctx.expect_contact('base', 'lid', contact_tol=0.0005)\n",
        encoding="utf-8",
    )

    findings, details = source_hygiene_checks(
        path,
        required_exports=("run_demo_tests",),
    )

    warnings = [item for item in findings if item["code"] == "micro_contact_tolerance"]
    assert len(warnings) == 1
    assert warnings[0]["blocking"] is False
    assert warnings[0]["location"]["line"] == 2
    assert warnings[0]["next_action"] == (
        "use_0.0005_or_document_collision_geometry_precision_need"
    )
    assert details["micro_contact_tolerances"] == [{"line": 2, "value": 1e-6}]


def test_source_hygiene_follows_used_dispatch_tables_only(tmp_path: Path) -> None:
    path = tmp_path / "demo.py"
    path.write_text(
        "def _used_helper():\n"
        "    return 'used'\n\n"
        "def _build_a():\n"
        "    return _used_helper()\n\n"
        "def _build_b():\n"
        "    return 'b'\n\n"
        "def _registry_only():\n"
        "    return 'not reachable'\n\n"
        "def _actually_dead():\n"
        "    return 'dead'\n\n"
        "_BUILDERS = {'a': _build_a, 'b': _build_b}\n"
        "_UNUSED_BUILDERS = {'x': _registry_only}\n\n"
        "def build_demo(kind='a'):\n"
        "    return _BUILDERS[kind]()\n\n"
        "def config_from_seed(seed):\n"
        "    return {'kind': 'a' if seed % 2 else 'b'}\n\n"
        "def run_demo_tests():\n"
        "    return build_demo()\n",
        encoding="utf-8",
    )

    findings, details = source_hygiene_checks(
        path,
        required_exports=("config_from_seed", "build_demo", "run_demo_tests"),
    )

    dead = {
        finding["owner"]["symbol"] for finding in findings if finding["code"] == "dead_private_code"
    }
    assert dead == {"_actually_dead", "_registry_only"}
    assert details["dead_private_functions"] == ["_actually_dead", "_registry_only"]


def test_overlap_policy_leaves_isolated_allowance_untouched() -> None:
    assert forbidden_overlap_allowances(
        (
            "allow_overlap('base', 'child'): captured",
            "allow_isolated_part('child'): joint retained",
        )
    ) == ("allow_overlap('base', 'child'): captured",)


def test_shared_overlap_policy_owns_finding_and_legacy_boundary(tmp_path: Path) -> None:
    allowances = ("allow_overlap('base', 'child'): captured",)
    design_result = overlap_policy_result(
        repo_root=tmp_path,
        slug="demo",
        allowances=allowances,
        design_backed=True,
    )
    legacy_result = overlap_policy_result(
        repo_root=tmp_path,
        slug="demo",
        allowances=allowances,
        design_backed=False,
    )

    assert design_result["finding"]["code"] == "overlap_allowance_forbidden"
    assert design_result["finding"]["next_action"] == (
        "remove_allow_overlap_and_repair_geometry_or_interfaces"
    )
    assert legacy_result["finding"] is None


def test_derived_parameter_cycle_is_blocking() -> None:
    design = _design(
        (
            SlotDesign(
                name="body",
                component_type="body",
                candidates=(
                    _candidate(
                        "linked",
                        parameters=(
                            ParameterDesign(
                                name="a",
                                mode="derived",
                                expression="b",
                                depends_on=("b",),
                            ),
                            ParameterDesign(
                                name="b",
                                mode="derived",
                                expression="a",
                                depends_on=("a",),
                            ),
                        ),
                    ),
                ),
            ),
        )
    )

    findings, _details = derivation_checks(design)

    assert "derived_parameter_cycle" in {
        finding["code"] for finding in findings if finding["blocking"]
    }


@dataclass(frozen=True)
class CandidateConfig:
    body: str = "box"


def _candidate_design_and_domain():
    design = _design(
        (
            SlotDesign(
                name="body",
                component_type="body",
                candidates=(_candidate("box"), _candidate("other")),
            ),
        )
    )
    domain = TemplateDomain((component_slot("body", ("box", "other")),))
    return design, domain


def _parameter_design_and_domain():
    design = _design(
        (
            SlotDesign(
                name="body",
                component_type="body",
                candidates=(
                    _candidate(
                        "adjustable",
                        parameters=(
                            ParameterDesign(
                                name="length",
                                minimum=1.0,
                                maximum=2.0,
                                unit="m",
                            ),
                        ),
                    ),
                ),
            ),
        )
    )
    domain = TemplateDomain((component_slot("body", ("adjustable",)),))
    return design, domain


@dataclass(frozen=True)
class MultiplicityConfig:
    item: str = "many"
    count: int = 1


@dataclass(frozen=True)
class DualMultiplicityConfig:
    item_a: str = "a"
    count_a: int = 1
    item_b: str = "b"
    count_b: int = 1


def _multiplicity_design_and_domain(*, partial: bool = False):
    candidates = (_candidate("single"), _candidate("many")) if partial else (_candidate("many"),)
    design = _design(
        (
            SlotDesign(
                name="item",
                component_type="item",
                candidates=candidates,
            ),
        ),
        multiplicities=(
            MultiplicityDesign(
                name="count",
                item_slot="item",
                values=(1, 2, 3),
                spacing_expression="uniform",
                host_capacity_expression="count <= 3",
            ),
        ),
    )
    domain = TemplateDomain(
        (
            component_slot("item", tuple(candidate.name for candidate in candidates)),
            multiplicity_slot("count", (1, 2, 3), item_slot="item"),
        )
    )
    return design, domain


def test_multiplicity_item_slot_binding_must_match_runtime_domain(
    tmp_path: Path,
) -> None:
    item = SlotDesign(
        name="item",
        component_type="item",
        candidates=(_candidate("many"),),
    )
    other = SlotDesign(
        name="other",
        component_type="other",
        candidates=(_candidate("other"),),
    )
    design = _design(
        (item, other),
        multiplicities=(
            MultiplicityDesign(
                name="count",
                item_slot="item",
                values=(1, 2, 3),
                spacing_expression="uniform",
                host_capacity_expression="count <= 3",
            ),
        ),
    )
    domain = TemplateDomain(
        (
            component_slot("item", ("many",)),
            component_slot("other", ("other",)),
            multiplicity_slot("count", (1, 2, 3), item_slot="other"),
        )
    )
    path = tmp_path / "demo.py"
    path.write_text("", encoding="utf-8")

    findings, _details = design_alignment_checks(
        repo_root=tmp_path,
        path=path,
        design=design,
        domain=domain,
        top_level_functions={"_build_many", "_build_other"},
    )

    assert "design_runtime_multiplicity_item_slot_mismatch" in {
        finding["code"] for finding in findings if finding["blocking"]
    }


def test_quality_contract_ignores_source_navigation_but_guards_ranges() -> None:
    candidate = _candidate(
        "adjustable",
        record_id="rec_old",
        revision="rev_000001",
        source_spans=("model.py:L1-L10",),
        parameters=(
            ParameterDesign(
                name="length",
                minimum=1.0,
                maximum=2.0,
                unit="m",
            ),
        ),
    )
    design = _design(
        (
            SlotDesign(
                name="body",
                component_type="body",
                candidates=(candidate,),
            ),
        )
    )
    domain = TemplateDomain((component_slot("body", ("adjustable",)),))
    navigation_only = dataclasses.replace(
        design,
        slots=(
            dataclasses.replace(
                design.slots[0],
                candidates=(
                    dataclasses.replace(
                        candidate,
                        record_id="rec_new",
                        revision="rev_000002",
                        source_spans=("model.py:L100-L200",),
                        implementation_function="_renamed_builder",
                    ),
                ),
            ),
        ),
    )
    changed_range = dataclasses.replace(
        design,
        slots=(
            dataclasses.replace(
                design.slots[0],
                candidates=(
                    dataclasses.replace(
                        candidate,
                        parameters=(
                            dataclasses.replace(
                                candidate.parameters[0],
                                maximum=3.0,
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )

    assert quality_contract(design, domain) == quality_contract(
        navigation_only,
        domain,
    )
    assert quality_contract(design, domain) != quality_contract(
        changed_range,
        domain,
    )


@dataclass(frozen=True)
class CategoryConfig:
    family: str = "rack"
    tool_count: int = 2


def _category_design() -> tuple[TemplateDesign, TemplateDomain]:
    anchor = CategoryAnchorDesign(
        anchor_id="rack_identity",
        applies_to=CategoryAnchorAppliesTo(
            slot="family",
            candidates=("rack",),
        ),
        required_roles=(
            CategoryRoleRequirement(role="holder", exact_count=1),
            CategoryRoleRequirement(role="wrench", count_from="tool_count"),
        ),
        required_relations=(
            CategoryRelationRequirement(
                parent_role="holder",
                child_role="wrench",
                joint_type="prismatic",
                axis=(0.0, 1.0, 0.0),
            ),
        ),
        required_author_checks=("category_anchor: real wrench profile",),
    )
    design = _design(
        (
            SlotDesign(
                name="family",
                component_type="wrench_set",
                candidates=(_candidate("rack"),),
            ),
        ),
        multiplicities=(
            MultiplicityDesign(
                name="tool_count",
                item_slot="family",
                values=(2,),
                spacing_expression="pitch(tool_count)",
                host_capacity_expression="tool_count <= 2",
            ),
        ),
        category_anchors=(anchor,),
    )
    domain = TemplateDomain(
        (
            component_slot("family", ("rack",)),
            multiplicity_slot("tool_count", (2,), item_slot="family"),
        )
    )
    return design, domain


def test_quality_contract_guards_category_anchors() -> None:
    design, domain = _category_design()
    changed = dataclasses.replace(
        design,
        category_anchors=(
            dataclasses.replace(
                design.category_anchors[0],
                required_author_checks=("category_anchor: forged wrench ends",),
            ),
        ),
    )
    assert quality_contract(design, domain) != quality_contract(changed, domain)


# --- Tier 0-B: exhaust the declared domain through the sampler, build nothing ---


@dataclass(frozen=True)
class ScanConfig:
    body: str = "box"
    gap_m: float = 0.01


@dataclass(frozen=True)
class ScanResolved:
    body: str
    gap_m: float


def _scan_module(*, sampler, resolver=None):
    def build_demo(*_args, **_kwargs):
        raise AssertionError("Tier 0-B must not build")

    return types.SimpleNamespace(
        config_from_seed=sampler,
        resolve_config=resolver or (lambda cfg: ScanResolved(body=cfg.body, gap_m=cfg.gap_m)),
        build_demo=build_demo,
        run_demo_tests=build_demo,
    )


def _scan_design_and_domain(*, parameters: dict[str, tuple[ParameterDesign, ...]] | None = None):
    parameters = parameters or {}
    design = _design(
        (
            SlotDesign(
                name="body",
                component_type="body",
                candidates=tuple(
                    _candidate(name, parameters=parameters.get(name, ()))
                    for name in ("box", "other")
                ),
            ),
        )
    )
    domain = TemplateDomain((component_slot("body", ("box", "other")),))
    return design, domain


def _codes(findings):
    return {row["code"] for row in findings}


def test_tier0b_builds_nothing() -> None:
    """The architectural invariant: preflight resolves configs, it does not compile."""
    design, domain = _scan_design_and_domain()
    module = _scan_module(
        sampler=lambda seed: ScanConfig(body="box" if seed % 2 else "other", gap_m=0.01 + seed)
    )

    findings, details = template_preflight.domain_resolution_checks(
        module=module, design=design, domain=domain
    )

    assert findings == []
    assert details["candidate_structure"]["status"] == "pass"
    assert details["candidate_structure"]["reached_values"] == 2


def test_tier0b_blocks_a_declared_candidate_the_sampler_never_reaches() -> None:
    design, domain = _scan_design_and_domain()
    module = _scan_module(sampler=lambda seed: ScanConfig(body="box", gap_m=0.01 + seed))

    findings, details = template_preflight.domain_resolution_checks(
        module=module, design=design, domain=domain, max_seeds=200, patience=50
    )

    assert "domain_candidate_unreachable" in _codes(findings)
    assert all(row["blocking"] for row in findings if row["code"] == "domain_candidate_unreachable")
    assert details["candidate_structure"]["unreachable"] == ["body.other"]


def test_tier0b_blocks_a_sampled_combination_resolve_config_rejects() -> None:
    """Hard boundary 7 is a claim about combinations; nothing else in the pipeline reads it."""
    design, domain = _scan_design_and_domain()

    def resolver(cfg):
        if cfg.body == "other":
            raise ValueError("other is not supported with this body length")
        return ScanResolved(body=cfg.body, gap_m=cfg.gap_m)

    module = _scan_module(
        sampler=lambda seed: ScanConfig(body="box" if seed % 2 else "other", gap_m=0.01 + seed),
        resolver=resolver,
    )

    findings, details = template_preflight.domain_resolution_checks(
        module=module, design=design, domain=domain, max_seeds=40, patience=20
    )

    blocking = [row for row in findings if row["code"] == "domain_combination_unresolvable"]
    assert blocking and blocking[0]["blocking"] is True
    assert "not supported" in blocking[0]["detail"]
    assert details["derivations"]["status"] == "fail"


def test_tier0b_reports_a_parameter_pinned_by_a_silent_coercion() -> None:
    """point_of_sale_terminal's `resolve_config` coerced one candidate's parameter to 0.

    Nothing built is needed to see it: over the seeds that select the candidate the
    parameter never takes a second value.
    """
    gap = ParameterDesign(name="gap_m", mode="independent", unit="m", minimum=0.0, maximum=0.05)
    design, domain = _scan_design_and_domain(parameters={"box": (gap,), "other": (gap,)})

    def resolver(cfg):
        # the coercion: `other` pins the parameter, `box` honours it
        return ScanResolved(body=cfg.body, gap_m=0.0 if cfg.body == "other" else cfg.gap_m)

    module = _scan_module(
        sampler=lambda seed: ScanConfig(
            body="box" if seed % 2 else "other", gap_m=0.001 * (seed + 1)
        ),
        resolver=resolver,
    )

    findings, details = template_preflight.domain_resolution_checks(
        module=module, design=design, domain=domain, max_seeds=40, patience=20
    )

    pinned = details["parameterization"]["pinned"]
    assert [entry["candidate"] for entry in pinned] == ["other"]
    assert pinned[0]["parameter"] == "gap_m"
    assert "parameter_resolution_no_effect" in _codes(findings)


def test_tier0b_scopes_parameter_constancy_to_the_owning_candidate() -> None:
    """A candidate-local parameter is constant wherever its candidate is not selected."""
    gap = ParameterDesign(name="gap_m", mode="independent", unit="m", minimum=0.0, maximum=0.05)
    design, domain = _scan_design_and_domain(parameters={"box": (gap,), "other": (gap,)})
    module = _scan_module(
        sampler=lambda seed: ScanConfig(
            body="box" if seed % 2 else "other", gap_m=0.001 * (seed + 1)
        )
    )

    findings, details = template_preflight.domain_resolution_checks(
        module=module, design=design, domain=domain, max_seeds=40, patience=20
    )

    assert details["parameterization"]["pinned"] == []
    assert "parameter_resolution_no_effect" not in _codes(findings)


def test_tier0b_blocks_unreached_candidate_by_n_combinations() -> None:
    design, domain = _multiplicity_design_and_domain(partial=True)

    @dataclass(frozen=True)
    class Cfg:
        item: str
        count: int

    module = _scan_module(
        sampler=lambda seed: Cfg(item="many" if seed % 2 else "single", count=1 + seed % 2),
        resolver=lambda cfg: cfg,
    )

    findings, details = template_preflight.domain_resolution_checks(
        module=module, design=design, domain=domain, max_seeds=200, patience=50
    )

    assert "multiplicity_sampler_missing_combination" in _codes(findings)
    row = next(r for r in findings if r["code"] == "multiplicity_sampler_missing_combination")
    assert row["blocking"] is True
    assert details["multiplicity"]["status"] == "fail"
    # the sampler couples item to count, so only 2 of the 6 declared pairs occur
    assert details["multiplicity"]["declared_pairs"] == 6
    assert details["multiplicity"]["reached_pairs"] == 2
    assert set(details["multiplicity"]["missing"]) == {
        "item.many x count=1",
        "item.many x count=3",
        "item.single x count=2",
        "item.single x count=3",
    }


def test_tier0b_cross_slot_pair_gap_is_advisory_not_blocking() -> None:
    """A bounded scan cannot distinguish unreachable from rare, so pairs stay advisory."""

    @dataclass(frozen=True)
    class Cfg:
        left: str
        right: str

    design = _design(
        (
            SlotDesign(
                name="left", component_type="l", candidates=(_candidate("a"), _candidate("b"))
            ),
            SlotDesign(
                name="right", component_type="r", candidates=(_candidate("x"), _candidate("y"))
            ),
        )
    )
    domain = TemplateDomain(
        (component_slot("left", ("a", "b")), component_slot("right", ("x", "y")))
    )
    # the sampler locks left/right together: a x y and b x x never occur
    module = _scan_module(
        sampler=lambda seed: Cfg(left="a" if seed % 2 else "b", right="x" if seed % 2 else "y"),
        resolver=lambda cfg: cfg,
    )

    findings, details = template_preflight.domain_resolution_checks(
        module=module, design=design, domain=domain, max_seeds=200, patience=50
    )

    pair = next(row for row in findings if row["code"] == "domain_pair_unreachable")
    assert pair["blocking"] is False
    assert pair["owner"]["missing_count"] == 2
    assert details["candidate_structure"]["status"] == "pass"


def test_category_anchor_author_check_wiring_is_checked_statically() -> None:
    design, _domain = _category_design()
    names = [name for anchor in design.category_anchors for name in anchor.required_author_checks]
    assert names, "fixture must declare at least one required author check"

    missing, missing_details = template_preflight.category_anchor_wiring_checks(
        design=design, source_text="def run_demo_tests(model, config):\n    return model\n"
    )
    wired, wired_details = template_preflight.category_anchor_wiring_checks(
        design=design,
        source_text="".join(f'ctx.check("{name}")\n' for name in names),
    )

    assert "category_anchor_author_check_missing" in _codes(missing)
    assert missing_details["status"] == "fail"
    assert wired == []
    assert wired_details["status"] == "pass"


def _bounded(name: str, minimum: float, maximum: float) -> ParameterDesign:
    return ParameterDesign(
        name=name, mode="independent", unit="m", minimum=minimum, maximum=maximum
    )


def _boundary_design(parameters):
    return _design(
        (
            SlotDesign(
                name="body",
                component_type="body",
                candidates=(_candidate("box", parameters=parameters),),
            ),
        )
    )


def test_corner_boundary_check_requires_an_override_at_a_declared_edge() -> None:
    """Preflight no longer builds a far numeric boundary; the corner must author it."""
    design = _boundary_design((_bounded("gap_m", 0.01, 0.05),))
    from sdk import corner_case

    at_edge = types.SimpleNamespace(
        TEMPLATE_CORNERS=(corner_case("wide", {"body": "box", "gap_m": 0.05}, reason="max gap"),)
    )
    inside = types.SimpleNamespace(
        TEMPLATE_CORNERS=(corner_case("mid", {"body": "box", "gap_m": 0.03}, reason="mid gap"),)
    )
    absent = types.SimpleNamespace(TEMPLATE_CORNERS=())

    ok, ok_details = template_preflight.corner_boundary_checks(module=at_edge, design=design)
    near, near_details = template_preflight.corner_boundary_checks(module=inside, design=design)
    none, none_details = template_preflight.corner_boundary_checks(module=absent, design=design)

    assert ok == [] and ok_details["status"] == "pass"
    assert ok_details["at_declared_edge"] == ["gap_m"]

    assert near_details["status"] == "warn"
    assert near_details["uncovered"] == ["gap_m"]
    assert near[0]["blocking"] is False
    assert near[0]["owner"]["overridden_but_not_at_an_edge"] == ["gap_m"]

    assert none_details["uncovered"] == ["gap_m"]
    assert none[0]["code"] == "corner_numeric_boundary_unauthored"


def test_corner_boundary_check_is_not_applicable_without_declared_ranges() -> None:
    design = _boundary_design(
        (ParameterDesign(name="style", mode="independent", value_type="str"),)
    )
    module = types.SimpleNamespace(TEMPLATE_CORNERS=())

    findings, details = template_preflight.corner_boundary_checks(module=module, design=design)

    assert findings == []
    assert details["status"] == "not_applicable"
