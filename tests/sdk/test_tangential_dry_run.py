# SPDX-License-Identifier: Apache-2.0

"""Tangential-containment DRY-RUN path: auto-enabled by the modular assembler,
reports warnings only — never failures, never affects the build. The opt-in
hard path (tangential_containment=True) keeps failing as before."""

from __future__ import annotations

from sdk import ArticulatedObject, ArticulationType, Box, MatingContract, Origin, TestContext


def _stacked_model(*, hang_off: bool, rpy=(0.0, 0.0, 0.0), **contract_kwargs):
    """Frame with a tray mounted on top; hang_off shifts the tray half off."""
    model = ArticulatedObject(name="stack")
    frame = model.part("frame")
    frame.visual(Box((0.4, 0.4, 0.02)), origin=Origin(xyz=(0.0, 0.0, 0.01)), name="deck")
    tray = model.part("tray")
    tray_x = 0.3 if hang_off else 0.0
    tray.visual(Box((0.4, 0.4, 0.02)), origin=Origin(xyz=(tray_x, 0.0, 0.01), rpy=rpy), name="pan")
    model.articulation(
        "frame_to_tray",
        ArticulationType.FIXED,
        parent=frame,
        child=tray,
        origin=Origin(xyz=(0.0, 0.0, 0.02)),
        mating=MatingContract(
            parent_face_geometry="deck",
            parent_face_side="positive_z",
            child_face_geometry="pan",
            child_face_side="negative_z",
            contact_tol=0.002,
            **contract_kwargs,
        ),
    )
    return model


def test_dry_run_violation_warns_but_never_fails() -> None:
    ctx = TestContext(_stacked_model(hang_off=True, tangential_dry_run=True))
    assert ctx.fail_if_joint_mating_has_gap()
    report = ctx.report()
    assert report.passed, report.failures
    assert any(
        "[tangential dry-run]" in w and "mount-footprint containment violated" in w
        for w in report.warnings
    )


def test_dry_run_clean_stack_no_warning() -> None:
    ctx = TestContext(_stacked_model(hang_off=False, tangential_dry_run=True))
    assert ctx.fail_if_joint_mating_has_gap()
    report = ctx.report()
    assert report.passed
    assert not any("[tangential dry-run]" in w for w in report.warnings)


def test_dry_run_rotated_face_skips_with_warning() -> None:
    ctx = TestContext(_stacked_model(hang_off=True, rpy=(0.0, 0.0, 0.4), tangential_dry_run=True))
    assert ctx.fail_if_joint_mating_has_gap()
    report = ctx.report()
    assert report.passed
    assert any("dry-run SKIPPED" in w and "rotated" in w for w in report.warnings)
    assert not any("mount-footprint containment violated" in w for w in report.warnings)


def test_opt_in_hard_path_still_fails() -> None:
    ctx = TestContext(_stacked_model(hang_off=True, tangential_containment=True))
    assert not ctx.fail_if_joint_mating_has_gap()
    assert not ctx.report().passed


def test_opt_in_takes_precedence_over_dry_run() -> None:
    ctx = TestContext(
        _stacked_model(hang_off=True, tangential_containment=True, tangential_dry_run=True)
    )
    assert not ctx.fail_if_joint_mating_has_gap()


def test_assembler_sets_dry_run_only_with_reliable_extents() -> None:
    from agent.templates._modular import InterfaceSpec, _emit_chain_joint

    def iface(part, visual, side, extents):
        return InterfaceSpec(
            interface_name="i",
            part_name=part,
            visual_name=visual,
            face_side=side,
            anchor_local=(0.0, 0.0, 0.0),
            face_extents_uv=extents,
        )

    def build(extents_parent, extents_child):
        model = ArticulatedObject(name="asm")
        a = model.part("a")
        a.visual(Box((0.2, 0.2, 0.02)), origin=Origin(xyz=(0.0, 0.0, -0.01)), name="top")
        b = model.part("b")
        b.visual(Box((0.2, 0.2, 0.02)), origin=Origin(xyz=(0.0, 0.0, 0.01)), name="bot")
        _emit_chain_joint(
            model,
            joint_name="a_to_b",
            parent_iface=iface("a", "top", "positive_z", extents_parent),
            child_iface=iface("b", "bot", "negative_z", extents_child),
        )
        return model.get_articulation("a_to_b").mating

    assert build((0.2, 0.2), (0.2, 0.2)).tangential_dry_run is True
    assert build((0.0, 0.0), (0.2, 0.2)).tangential_dry_run is False
    assert build((0.2, 0.2), (0.0, 0.0)).tangential_dry_run is False
