# SPDX-License-Identifier: Apache-2.0

"""Verified mechanism idioms for template authoring.

Corpus facts (2026-07 census + repair campaign over 289 templates): ~45% of
templates hinge a lid/door/leaf/hatch, ~20% slide something, ~6% fold a chain
— and the genuine motion-穿模 defect list concentrated in exactly three root
causes: hinges swinging the WRONG WAY into their own body (manhole cover,
turnstile door, kettle bail), physically-coupled chains modeled as INDEPENDENT
joints (folding door, folder sheets, folding arm), and hand-written limits
letting a subtree sweep into geometry (turret, tank, scale, telescope).

These constructors make those bugs unrepresentable at build time. They do NOT
create geometry — authors keep full control of appearance; the idiom wires the
kinematics: emits the joint, verifies the swing direction actually moves the
panel toward the declared clear side, solves the safe travel against the rest
of the model with the SDK clearance solver, and wires mimic coupling for
chains. Prefer these over raw ``model.articulation(...)`` for matching
mechanisms; drop to raw joints only when no idiom fits (and say why).
"""

from __future__ import annotations

from typing import Iterable, Optional, Tuple

from sdk import (
    ArticulatedObject,
    ArticulationType,
    MatingContract,
    MotionLimits,
    Origin,
    coupled_chain,
    hinged_panel,
    max_joint_value,
)
from sdk._core.v0.motion_solve import _DEFAULT_MARGIN

__all__ = [
    "coupled_chain",
    "hinged_panel",
    "sliding_member",
]

# Fraction of the requested travel below which a solved range counts as
# collapsed: the mechanism is unusable and the caller must fix geometry, not
# ship a joint that barely moves.
_MIN_SOLVED_FRACTION = 0.05


def sliding_member(
    model: ArticulatedObject,
    *,
    joint_name: str,
    parent: object,
    slider: object,
    origin: Tuple[float, float, float],
    axis: Tuple[float, float, float],
    max_travel: float,
    margin: float = _DEFAULT_MARGIN,
    keepout: Optional[Iterable[str]] = None,
    allowed_pairs: Optional[Iterable[Tuple[str, str]]] = None,
    effort: float = 30.0,
    velocity: float = 0.3,
    mating: Optional[MatingContract] = None,
) -> MotionLimits:
    """Emit a drawer/tray/telescoping prismatic with solver-clamped travel.

    ``max_travel`` is the author's intent (full extension); the realized upper
    limit is the largest travel keeping the slider subtree ``margin`` clear of
    everything else — a tray can no longer rise into a closed lid, a sluice
    gate can no longer drop into a spinning wheel. Nested containment that is
    intentional (rail inside sleeve) goes in ``allowed_pairs`` element-scoped
    allowances on the template side, or a restricted ``keepout``.
    """
    parent_part = model.get_part(parent)
    slider_part = model.get_part(slider)
    limits = MotionLimits(effort=effort, velocity=velocity, lower=0.0, upper=float(max_travel))
    model.articulation(
        joint_name,
        ArticulationType.PRISMATIC,
        parent=parent_part,
        child=slider_part,
        origin=Origin(xyz=tuple(float(c) for c in origin)),
        axis=tuple(float(c) for c in axis),
        motion_limits=limits,
        mating=mating,
    )
    solved_upper = max_joint_value(
        model,
        joint=joint_name,
        limit=float(max_travel),
        margin=margin,
        keepout=keepout,
        allowed_pairs=allowed_pairs,
    )
    if solved_upper < float(max_travel) * _MIN_SOLVED_FRACTION:
        model.articulations[:] = [j for j in model.articulations if j.name != joint_name]
        raise ValueError(
            f"sliding_member({joint_name!r}): the clearance solver collapsed the travel "
            f"to {solved_upper:.4g} m (requested {float(max_travel):.4g}) — the slider "
            f"cannot move. Common cause: the prismatic axis points INTO the carcass "
            f"(flipped sign) or something blocks the path at rest. Fix the geometry "
            f"instead of shipping a drawer that doesn't open."
        )
    joint = next(j for j in model.articulations if j.name == joint_name)
    joint.motion_limits = MotionLimits(
        effort=effort, velocity=velocity, lower=0.0, upper=solved_upper
    )
    return joint.motion_limits
