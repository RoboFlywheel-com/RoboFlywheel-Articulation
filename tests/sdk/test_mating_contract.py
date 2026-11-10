# SPDX-License-Identifier: Apache-2.0

"""Tests for the MatingContract schema and `fail_if_joint_mating_has_gap`."""

from __future__ import annotations

import pytest

from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    MatingContract,
    Origin,
    TestContext,
)


def _build_model_with_mating(
    *,
    body_visual_at: tuple[float, float, float] = (0.0, 0.0, 0.05),
    body_visual_size: tuple[float, float, float] = (0.1, 0.1, 0.1),
    child_visual_at: tuple[float, float, float] = (0.0, 0.0, 0.05),
    child_visual_size: tuple[float, float, float] = (0.1, 0.1, 0.1),
    joint_origin: tuple[float, float, float] = (0.0, 0.0, 0.1),
    parent_face_side: str = "positive_z",
    child_face_side: str = "negative_z",
    contact_tol: float = 0.001,
) -> ArticulatedObject:
    """Helper: two-part model with a configurable MatingContract."""
    model = ArticulatedObject(name="mating_demo")
    body = model.part("body")
    body.visual(Box(body_visual_size), origin=Origin(xyz=body_visual_at), name="body_top")
    child = model.part("lid")
    child.visual(Box(child_visual_size), origin=Origin(xyz=child_visual_at), name="lid_bottom")
    model.articulation(
        "body_to_lid",
        ArticulationType.FIXED,
        parent=body,
        child=child,
        origin=Origin(xyz=joint_origin),
        mating=MatingContract(
            parent_face_geometry="body_top",
            parent_face_side=parent_face_side,
            child_face_geometry="lid_bottom",
            child_face_side=child_face_side,
            contact_tol=contact_tol,
        ),
    )
    return model


# --------------------------------------------------------------------------- #
# Dataclass-level validation
# --------------------------------------------------------------------------- #


def test_mating_contract_requires_known_face_side() -> None:
    with pytest.raises(Exception, match="parent_face_side"):
        MatingContract(
            parent_face_geometry="a",
            parent_face_side="not_a_face",
            child_face_geometry="b",
            child_face_side="positive_z",
        )


def test_mating_contract_rejects_empty_geometry_name() -> None:
    with pytest.raises(Exception, match="parent_face_geometry"):
        MatingContract(
            parent_face_geometry="",
            parent_face_side="positive_z",
            child_face_geometry="b",
            child_face_side="negative_z",
        )


def test_mating_contract_rejects_negative_tol() -> None:
    with pytest.raises(Exception, match="contact_tol"):
        MatingContract(
            parent_face_geometry="a",
            parent_face_side="positive_z",
            child_face_geometry="b",
            child_face_side="negative_z",
            contact_tol=-0.001,
        )


def test_mating_contract_normalises_inputs() -> None:
    mc = MatingContract(
        parent_face_geometry="  body_top  ",
        parent_face_side=" POSITIVE_Z ",
        child_face_geometry="lid_bottom",
        child_face_side="negative_z",
        contact_tol=0.002,
    )
    assert mc.parent_face_geometry == "body_top"
    assert mc.parent_face_side == "positive_z"
    assert mc.contact_tol == 0.002


# --------------------------------------------------------------------------- #
# Articulation accepts mating field
# --------------------------------------------------------------------------- #


def test_articulation_accepts_mating_field() -> None:
    model = _build_model_with_mating()
    joint = model.articulations[0]
    assert joint.mating is not None
    assert joint.mating.parent_face_geometry == "body_top"


# --------------------------------------------------------------------------- #
# fail_if_joint_mating_has_gap behaviour
# --------------------------------------------------------------------------- #


def test_check_passes_when_mating_faces_are_in_contact() -> None:
    # body_top top face at world z = 0.05 + 0.05 = 0.10
    # joint origin at world (0, 0, 0.10) — child link world origin
    # lid_bottom visual at child xyz=(0,0,0.05) -> world (0,0,0.15), extent [0.10, 0.20]
    # child's negative_z face center = world (0, 0, 0.10)
    # distance = 0  ✓
    model = _build_model_with_mating()
    ctx = TestContext(model)
    assert ctx.fail_if_joint_mating_has_gap() is True
    report = ctx.report()
    assert report.passed


def test_check_fails_when_mating_faces_have_visible_gap() -> None:
    # joint origin at (0, 0, 0.20) but body top face is at (0, 0, 0.10) → 10cm gap
    model = _build_model_with_mating(joint_origin=(0.0, 0.0, 0.20))
    ctx = TestContext(model)
    assert ctx.fail_if_joint_mating_has_gap() is False
    report = ctx.report()
    assert not report.passed
    failure = report.failures[0]
    assert "Joint mating-face gaps detected" in failure.details
    assert "distance=0.1" in failure.details


def test_check_skips_joints_without_mating_contract() -> None:
    """Joints without `mating` set are grandfathered — the check passes vacuously."""
    model = ArticulatedObject(name="no_mating")
    body = model.part("body")
    body.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.0, 0.0, 0.05)), name="body_top")
    child = model.part("lid")
    child.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.0, 0.0, 0.05)), name="lid_bottom")
    # joint origin far from any face but no mating contract -> check should pass
    model.articulation(
        "body_to_lid",
        ArticulationType.FIXED,
        parent=body,
        child=child,
        origin=Origin(xyz=(1.0, 0.0, 0.0)),
    )
    ctx = TestContext(model)
    assert ctx.fail_if_joint_mating_has_gap() is True
    assert ctx.report().passed


def test_check_reports_missing_visual_name() -> None:
    """When the mating contract references a visual name that doesn't exist,
    the check fails with a clear reason instead of crashing."""
    model = ArticulatedObject(name="missing_visual")
    body = model.part("body")
    body.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.0, 0.0, 0.05)), name="body_top")
    child = model.part("lid")
    child.visual(Box((0.1, 0.1, 0.1)), origin=Origin(xyz=(0.0, 0.0, 0.05)), name="lid_bottom")
    model.articulation(
        "body_to_lid",
        ArticulationType.FIXED,
        parent=body,
        child=child,
        origin=Origin(xyz=(0.0, 0.0, 0.10)),
        mating=MatingContract(
            parent_face_geometry="nonexistent_visual",
            parent_face_side="positive_z",
            child_face_geometry="lid_bottom",
            child_face_side="negative_z",
        ),
    )
    ctx = TestContext(model)
    assert ctx.fail_if_joint_mating_has_gap() is False
    failure = ctx.report().failures[0]
    assert "nonexistent_visual" in failure.details
    assert "not found on part" in failure.details
