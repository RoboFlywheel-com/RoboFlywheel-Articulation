# SPDX-License-Identifier: Apache-2.0

"""Tests for `mount_fixed` (single-source FIXED placement) and the
MatingContract tangential-containment extension.

Both exist to kill the caster_trolley class of bug: a child mesh authored
centered while the FIXED joint origin is hand-written at a corner post, so the
assembled child cantilevers half a body off its parent while every mechanical
gate (connectivity, overlap, origin proximity, normal-only mating gap) passes.
"""

from __future__ import annotations

import pytest

from agent.templates._modular import mount_fixed
from sdk import (
    ArticulatedObject,
    ArticulationType,
    Box,
    Inertia,
    Inertial,
    MatingContract,
    Origin,
    TestContext,
)

# Frame deck: footprint x∈[-0.4, 0.4], y∈[-0.3, 0.3], top face at z=0.04.
_DECK_SIZE = (0.8, 0.6, 0.04)
# Tray authored centered: x∈[-0.35, 0.35], y∈[-0.25, 0.25], bottom at z=0.
_TRAY_SIZE = (0.7, 0.5, 0.04)
_POST_TOP = (0.35, 0.25, 0.04)


def _frame_and_tray(model: ArticulatedObject):
    frame = model.part("frame")
    frame.visual(Box(_DECK_SIZE), origin=Origin(xyz=(0.0, 0.0, 0.02)), name="deck_top")
    frame.visual(Box((0.04, 0.04, 0.04)), origin=Origin(xyz=(0.35, 0.25, 0.02)), name="post")
    tray = model.part("tray")
    tray.visual(Box(_TRAY_SIZE), origin=Origin(xyz=(0.0, 0.0, 0.02)), name="tray_bottom")
    return frame, tray


def _tray_mating(*, tangential: bool) -> MatingContract:
    return MatingContract(
        parent_face_geometry="deck_top",
        parent_face_side="positive_z",
        child_face_geometry="tray_bottom",
        child_face_side="negative_z",
        contact_tol=0.002,
        tangential_containment=tangential,
    )


# --------------------------------------------------------------------------- #
# Tangential containment on MatingContract
# --------------------------------------------------------------------------- #


def test_normal_only_mating_is_blind_to_lateral_offset() -> None:
    """Documents the blind spot: a corner-origin + centered-mesh mount kisses
    the deck (normal distance 0) while hanging far outside the footprint, and
    the default (normal-only) contract passes."""
    model = ArticulatedObject(name="cantilever_bug")
    frame, tray = _frame_and_tray(model)
    model.articulation(
        "frame_to_tray",
        ArticulationType.FIXED,
        parent=frame,
        child=tray,
        origin=Origin(xyz=_POST_TOP),
        mating=_tray_mating(tangential=False),
    )
    ctx = TestContext(model)
    assert ctx.fail_if_joint_mating_has_gap() is True
    assert ctx.report().passed


def test_tangential_containment_catches_lateral_offset() -> None:
    model = ArticulatedObject(name="cantilever_bug_gated")
    frame, tray = _frame_and_tray(model)
    model.articulation(
        "frame_to_tray",
        ArticulationType.FIXED,
        parent=frame,
        child=tray,
        origin=Origin(xyz=_POST_TOP),
        mating=_tray_mating(tangential=True),
    )
    ctx = TestContext(model)
    assert ctx.fail_if_joint_mating_has_gap() is False
    failure = ctx.report().failures[0]
    assert "mount-footprint containment violated" in failure.details
    # tray world x_hi = 0.35 + 0.35 = 0.70 vs deck x_hi = 0.40 -> 0.30 overhang
    assert "0.3" in failure.details


def test_tangential_containment_passes_for_contained_mount() -> None:
    model = ArticulatedObject(name="centered_ok")
    frame, tray = _frame_and_tray(model)
    model.articulation(
        "frame_to_tray",
        ArticulationType.FIXED,
        parent=frame,
        child=tray,
        origin=Origin(xyz=(0.0, 0.0, 0.04)),
        mating=_tray_mating(tangential=True),
    )
    ctx = TestContext(model)
    assert ctx.fail_if_joint_mating_has_gap() is True
    assert ctx.report().passed


def test_mating_contract_rejects_negative_tangential_tol() -> None:
    with pytest.raises(Exception, match="tangential_tol"):
        MatingContract(
            parent_face_geometry="a",
            parent_face_side="positive_z",
            child_face_geometry="b",
            child_face_side="negative_z",
            tangential_tol=-0.001,
        )


# --------------------------------------------------------------------------- #
# mount_fixed: single-source placement
# --------------------------------------------------------------------------- #


def test_mount_fixed_rebases_child_and_places_origin_on_anchor() -> None:
    model = ArticulatedObject(name="mounted")
    frame, tray = _frame_and_tray(model)
    tray.inertial = Inertial(
        mass=1.0,
        inertia=Inertia(ixx=0.01, ixy=0.0, ixz=0.0, iyy=0.01, iyz=0.0, izz=0.01),
        origin=Origin(xyz=(0.0, 0.0, 0.02)),
    )

    mount_fixed(
        model,
        joint_name="frame_to_tray",
        parent=frame,
        child=tray,
        parent_anchor=_POST_TOP,
        child_anchor=(0.35, 0.25, 0.0),
        mating=_tray_mating(tangential=True),
    )

    joint = model.articulations[0]
    assert joint.origin.xyz == pytest.approx(_POST_TOP)
    # Child visuals rebased so local origin sits on the mounted corner...
    assert tray.visuals[0].origin.xyz == pytest.approx((-0.35, -0.25, 0.02))
    assert tray.inertial.origin.xyz == pytest.approx((-0.35, -0.25, 0.02))
    # ...which puts the tray's world center back over the frame center:
    # child frame at (0.35, 0.25, 0.04) + visual (-0.35, -0.25, 0.02) = (0, 0, 0.06).
    ctx = TestContext(model)
    assert ctx.fail_if_joint_mating_has_gap() is True
    assert ctx.fail_if_articulation_origin_far_from_geometry() is True
    assert ctx.report().passed


def test_mount_fixed_default_child_anchor_keeps_geometry_untouched() -> None:
    model = ArticulatedObject(name="untouched")
    frame, tray = _frame_and_tray(model)
    before = tray.visuals[0].origin.xyz
    mount_fixed(
        model,
        joint_name="frame_to_tray",
        parent=frame,
        child=tray,
        parent_anchor=(0.0, 0.0, 0.04),
    )
    assert tray.visuals[0].origin.xyz == before


def test_mount_fixed_rejects_already_wired_child() -> None:
    model = ArticulatedObject(name="wired")
    frame, tray = _frame_and_tray(model)
    other = model.part("accessory")
    other.visual(Box((0.02, 0.02, 0.02)), name="knob")
    model.articulation(
        "tray_to_accessory",
        ArticulationType.FIXED,
        parent=tray,
        child=other,
        origin=Origin(xyz=(0.0, 0.0, 0.04)),
    )
    with pytest.raises(ValueError, match="already referenced"):
        mount_fixed(
            model,
            joint_name="frame_to_tray",
            parent=frame,
            child=tray,
            parent_anchor=_POST_TOP,
            child_anchor=(0.35, 0.25, 0.0),
        )


# --------------------------------------------------------------------------- #
# Island repair hints (gap vector + builder attribution)
# --------------------------------------------------------------------------- #


def _build_floating_ridge(part) -> None:
    part.visual(Box((0.2, 0.05, 0.02)), origin=Origin(xyz=(0.0, 0.0, 0.05)), name="roof_shell")
    # Floats 4mm above the shell top (shell top z=0.06, ridge bottom z=0.064).
    part.visual(Box((0.18, 0.02, 0.012)), origin=Origin(xyz=(0.0, 0.0, 0.07)), name="roof_ridge")


def test_island_finding_carries_gap_vector_and_builder() -> None:
    model = ArticulatedObject(name="island_hint")
    cap = model.part("cap")
    _build_floating_ridge(cap)
    ctx = TestContext(model)
    assert ctx.fail_if_part_contains_disconnected_geometry_islands() is False
    failure = ctx.report().failures[0]
    assert "roof_ridge" in failure.details
    assert "nearest=roof_shell" in failure.details
    assert "dist=0.004" in failure.details
    assert "-z 0.004" in failure.details
    assert "built_by=_build_floating_ridge" in failure.details
