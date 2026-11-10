# SPDX-License-Identifier: Apache-2.0

"""Reusable mechanism constructors with mechanical safety checks."""

from __future__ import annotations

import math
from typing import Dict, Iterable, Optional, Sequence, Tuple

from .articulated_object import ArticulatedObject
from .geometry_qc import compute_part_world_transforms
from .motion_solve import _DEFAULT_MARGIN, _child_subtree, clamp_joint_limits
from .types import ArticulationType, MatingContract, Mimic, MotionLimits, Origin

__all__ = ["coupled_chain", "hinged_panel"]

_MIN_SOLVED_FRACTION = 0.05


def _panel_world_centroid(
    model: ArticulatedObject,
    part_name: str,
    pose: Dict[str, float],
) -> Tuple[float, float, float]:
    """Return the mean world position of a part's visual origins."""

    transforms = compute_part_world_transforms(model, pose)
    tf = transforms[part_name]
    part = model.get_part(part_name)
    xs = ys = zs = 0.0
    count = 0
    for visual in part.visuals:
        x, y, z = visual.origin.xyz
        xs += tf[0][0] * x + tf[0][1] * y + tf[0][2] * z + tf[0][3]
        ys += tf[1][0] * x + tf[1][1] * y + tf[1][2] * z + tf[1][3]
        zs += tf[2][0] * x + tf[2][1] * y + tf[2][2] * z + tf[2][3]
        count += 1
    if count == 0:
        raise ValueError(f"part {part_name!r} has no visuals to reason about")
    return (xs / count, ys / count, zs / count)


def coupled_chain(
    model: ArticulatedObject,
    *,
    driver: str,
    followers: Sequence[str],
    multipliers: Optional[Sequence[float]] = None,
    fold_budget: Optional[float] = None,
    margin: float = _DEFAULT_MARGIN,
    keepout: Optional[Iterable[str]] = None,
    allowed_pairs: Optional[Iterable[Tuple[str, ...]]] = None,
) -> MotionLimits:
    """Couple an emitted serial joint chain and solve its safe driver range.

    Each follower becomes a ``Mimic`` of ``driver``. ``multipliers`` may
    reverse or scale follower motion, while ``fold_budget`` optionally caps
    the sum of absolute joint travel before collision-driven limit solving.
    Followers must live inside the driver's child subtree so the clearance
    solve covers the complete coupled mechanism.
    """

    follower_names = tuple(followers)
    follower_name_set = set(follower_names)
    driver_joint = None
    follower_joints = []
    for joint in model.articulations:
        if joint.name == driver:
            driver_joint = joint
        elif joint.name in follower_name_set:
            follower_joints.append(joint)
    if driver_joint is None:
        raise ValueError(f"coupled_chain: unknown driver joint {driver!r}")
    missing = follower_name_set - {joint.name for joint in follower_joints}
    if missing:
        raise ValueError(f"coupled_chain: unknown follower joint(s) {sorted(missing)}")

    subtree = _child_subtree(model, driver)
    child_of = {}
    for joint in model.articulations:
        child = (
            joint.child
            if isinstance(joint.child, str)
            else getattr(joint.child, "name", None)
        )
        if isinstance(child, str):
            child_of[joint.name] = child
    outside = [name for name in follower_names if child_of.get(name) not in subtree]
    if outside:
        raise ValueError(
            f"coupled_chain: follower joint(s) {outside} move parts OUTSIDE the driver's "
            "child subtree; chain the parts serially under the driver's child or solve "
            "each branch separately"
        )

    multiplier_values = (
        (1.0,) * len(follower_names) if multipliers is None else multipliers
    )
    gains = tuple(float(value) for value in multiplier_values)
    if len(gains) != len(follower_names):
        raise ValueError("coupled_chain: multipliers must match followers 1:1")
    by_name = {joint.name: joint for joint in follower_joints}
    for name, gain in zip(follower_names, gains):
        joint = by_name[name]
        joint.mimic = Mimic(joint=driver, multiplier=gain)
        limits = joint.motion_limits
        driver_limits = driver_joint.motion_limits
        if limits is not None and driver_limits is not None:
            lower, upper = sorted(
                (
                    float(driver_limits.lower or 0.0) * gain,
                    float(driver_limits.upper or 0.0) * gain,
                )
            )
            joint.motion_limits = MotionLimits(
                effort=limits.effort,
                velocity=limits.velocity,
                lower=lower,
                upper=upper,
            )

    if fold_budget is not None and driver_joint.motion_limits is not None:
        budget = float(fold_budget)
        if budget <= 0.0:
            raise ValueError("coupled_chain: fold_budget must be greater than zero")
        cap = budget / (1.0 + sum(abs(gain) for gain in gains))
        current = driver_joint.motion_limits
        driver_joint.motion_limits = MotionLimits(
            effort=current.effort,
            velocity=current.velocity,
            lower=max(float(current.lower or 0.0), -cap),
            upper=min(float(current.upper or 0.0), cap),
        )

    solved = clamp_joint_limits(
        model,
        driver,
        margin=margin,
        keepout=keepout,
        allowed_pairs=allowed_pairs,
    )
    for name, gain in zip(follower_names, gains):
        joint = by_name[name]
        if joint.motion_limits is None:
            continue
        lower, upper = sorted(
            (
                float(solved.lower or 0.0) * gain,
                float(solved.upper or 0.0) * gain,
            )
        )
        joint.motion_limits = MotionLimits(
            effort=joint.motion_limits.effort,
            velocity=joint.motion_limits.velocity,
            lower=lower,
            upper=upper,
        )
    return solved


def hinged_panel(
    model: ArticulatedObject,
    *,
    joint_name: str,
    parent: object,
    panel: object,
    hinge_origin: Tuple[float, float, float],
    axis: Tuple[float, float, float],
    open_toward: Tuple[float, float, float],
    max_open: float = math.radians(110.0),
    margin: float = _DEFAULT_MARGIN,
    keepout: Optional[Iterable[str]] = None,
    allowed_pairs: Optional[Iterable[Tuple[str, ...]]] = None,
    effort: float = 12.0,
    velocity: float = 1.2,
    mating: Optional[MatingContract] = None,
    solve_clearance: bool = True,
) -> MotionLimits:
    """Create a panel hinge, verify its opening side, and solve safe travel.

    ``open_toward`` is the world-frame direction in which the panel's visual
    centroid must initially move. A reversed axis or unusable clearance range
    raises ``ValueError`` and rolls back the newly created articulation.

    Build the panel geometry before calling this function. The returned
    ``MotionLimits`` are also written to the created revolute articulation.
    """

    parent_part = model.get_part(parent)
    panel_part = model.get_part(panel)
    requested_open = float(max_open)
    if requested_open <= 0.0:
        raise ValueError("hinged_panel: max_open must be greater than zero")
    if math.sqrt(sum(float(value) ** 2 for value in axis)) <= 1e-12:
        raise ValueError("hinged_panel: axis must be non-zero")
    open_norm = math.sqrt(sum(float(value) ** 2 for value in open_toward))
    if open_norm <= 1e-12:
        raise ValueError("hinged_panel: open_toward must be non-zero")

    limits = MotionLimits(
        effort=effort,
        velocity=velocity,
        lower=0.0,
        upper=requested_open,
    )
    model.articulation(
        joint_name,
        ArticulationType.REVOLUTE,
        parent=parent_part,
        child=panel_part,
        origin=Origin(xyz=tuple(float(value) for value in hinge_origin)),
        axis=tuple(float(value) for value in axis),
        motion_limits=limits,
        mating=mating,
    )

    def remove_joint() -> None:
        model.articulations[:] = [
            joint for joint in model.articulations if joint.name != joint_name
        ]

    probe_angle = min(0.15, requested_open / 2.0)
    rest = _panel_world_centroid(model, panel_part.name, {joint_name: 0.0})
    opened = _panel_world_centroid(model, panel_part.name, {joint_name: probe_angle})
    motion = tuple(
        opened_value - rest_value
        for opened_value, rest_value in zip(opened, rest)
    )
    magnitude = math.sqrt(sum(value * value for value in motion))
    if magnitude < 1e-9:
        remove_joint()
        raise ValueError(
            f"hinged_panel({joint_name!r}): the panel's visual centroid sits on the "
            "hinge axis, so the opening direction cannot be inferred; place the "
            "hinge on the panel edge or restructure the panel visuals"
        )
    opening_cosine = sum(
        movement * direction for movement, direction in zip(motion, open_toward)
    ) / (magnitude * open_norm)
    if opening_cosine < 0.6:
        remove_joint()
        raise ValueError(
            f"hinged_panel({joint_name!r}): opening moves {panel_part.name!r} by "
            f"{motion}, not toward open_toward={open_toward} (cos={opening_cosine:.3f}); "
            "this is a reversed-swing hinge, so flip the axis or move the pivot edge"
        )
    if not solve_clearance:
        return limits

    solved = clamp_joint_limits(
        model,
        joint_name,
        margin=margin,
        keepout=keepout,
        allowed_pairs=allowed_pairs,
    )
    solved_upper = float(solved.upper or 0.0)
    if solved_upper < requested_open * _MIN_SOLVED_FRACTION:
        remove_joint()
        raise ValueError(
            f"hinged_panel({joint_name!r}): the clearance solver collapsed the opening "
            f"range to {solved_upper:.4g} rad (requested {requested_open:.4g}); fix the "
            "blocking geometry instead of shipping a panel that cannot open"
        )
    return solved
