# SPDX-License-Identifier: Apache-2.0

"""Clearance-driven joint-limit solving.

The recurring template bug family is "a joint's limit lets its subtree sweep
into other geometry": lids into buttons, sail blades into towers, breeches
into hulls, armrests into each other. Template authors keep hand-deriving the
safe travel with per-template trigonometry; this module makes the derivation a
library call built on the same FK (`compute_part_world_transforms`) and FCL
distance machinery the motion-QC gate uses, so "the limit the solver returns"
and "the poses the gate checks" can't disagree.

Typical use in a template, after parts and joints are built::

    from sdk import clamp_joint_limits

    clamp_joint_limits(
        model,
        "body_to_lid",
        margin=0.008,           # keep >= 8mm from everything it could hit
        keepout=["flush_button"],  # optional: restrict the keep-out set
    )

Semantics: the moving set is the joint's child subtree; the keep-out set is
every other part (minus declared/passed allowed pairs), or the explicit
``keepout`` list. ``allowed_pairs`` entries may be part-level ``(part_a,
part_b)`` or element-scoped ``(part_a, part_b, elem_a, elem_b)``; the latter
exempts only one visual-vs-visual contact (e.g. a spindle seated in its
bearing socket) so an always-on coaxial overlap cannot mask a genuine sweep
collision elsewhere in the same part pair. ``max_joint_value`` finds the
largest value in
``[start, limit]`` such that every pose on the way keeps the moving set at
least ``margin`` away from the keep-out set — a coarse scan finds the first
violating step (robust to non-monotonic clearance), then bisection refines
the boundary. Solving is deterministic and typically costs a few dozen FCL
distance queries.
"""

from __future__ import annotations

import logging

from typing import Dict, Iterable, List, Optional, Tuple

from .errors import ValidationError
from .geometry_qc import (
    _collision_scene_for_model,
    compile_object_model_with_exact_collisions,
    resolve_asset_root,
)
from .types import MotionLimits

logger = logging.getLogger(__name__)

#: Minimum travel applied when clearance solving collapses a joint's range to
#: zero (the rest pose already violates the margin). A zero-width limit is a
#: degenerate revolute/prismatic declaration; flooring keeps the joint valid
#: and the warning surfaces the collapse for production QC.
ZERO_RANGE_FLOOR = 0.01

__all__ = [
    "ClearanceProbe",
    "clamp_joint_limits",
    "max_joint_value",
    "min_clearance_at_pose",
]

_DEFAULT_MARGIN = 0.008
_DEFAULT_SCAN_STEPS = 16
_DEFAULT_BISECT_ITERS = 20


def _resolve_links_and_joints(model: object) -> Tuple[list, list]:
    links = getattr(model, "parts", None) or getattr(model, "links", None)
    joints = getattr(model, "articulations", None) or getattr(model, "joints", None)
    if not isinstance(links, list) or not isinstance(joints, list):
        raise ValidationError("model must expose .parts and .articulations lists")
    return links, joints


def _joint_by_name(model: object, joint_name: str):
    _, joints = _resolve_links_and_joints(model)
    for joint in joints:
        if getattr(joint, "name", None) == joint_name:
            return joint
    raise ValidationError(f"Unknown articulation: {joint_name!r}")


def _child_subtree(model: object, joint_name: str) -> set[str]:
    """Names of every part rooted at the joint's child (the moving set)."""
    joint = _joint_by_name(model, joint_name)
    child = getattr(joint, "child", None)
    child_name = child if isinstance(child, str) else getattr(child, "name", None)
    if not isinstance(child_name, str):
        raise ValidationError(f"Articulation {joint_name!r} has no child part name")
    _, joints = _resolve_links_and_joints(model)
    children_of: Dict[str, List[str]] = {}
    for j in joints:
        parent = getattr(j, "parent", None)
        parent_name = parent if isinstance(parent, str) else getattr(parent, "name", None)
        c = getattr(j, "child", None)
        c_name = c if isinstance(c, str) else getattr(c, "name", None)
        if isinstance(parent_name, str) and isinstance(c_name, str):
            children_of.setdefault(parent_name, []).append(c_name)
    subtree = {child_name}
    queue = [child_name]
    while queue:
        for grandchild in children_of.get(queue.pop(), []):
            if grandchild not in subtree:
                subtree.add(grandchild)
                queue.append(grandchild)
    return subtree


def _normalized_pair(a: str, b: str) -> Tuple[str, str]:
    return (a, b) if a <= b else (b, a)


class ClearanceProbe:
    """Compiled-once distance probe between a moving subtree and keep-out parts.

    Use this when one template needs many clearance queries on the same model,
    such as a binary search over a coupled multi-joint pose. For a single query,
    prefer :func:`min_clearance_at_pose`.
    """

    def __init__(
        self,
        model: object,
        *,
        joint_name: str,
        keepout: Optional[Iterable[str]] = None,
        allowed_pairs: Optional[Iterable[Tuple[str, ...]]] = None,
        asset_root=None,
    ) -> None:
        self._model = model
        self._compiled = compile_object_model_with_exact_collisions(
            model,  # type: ignore[arg-type]
            asset_root=asset_root,
            validate=False,
        )
        self._asset_root = resolve_asset_root(asset_root, self._compiled, model)
        self._scene = _collision_scene_for_model(
            self._compiled,
            asset_root=self._asset_root,
        )
        moving = _child_subtree(model, joint_name)
        links, _ = _resolve_links_and_joints(self._compiled)
        all_names = {
            name for link in links if isinstance((name := getattr(link, "name", None)), str)
        }
        if keepout is not None:
            keepout_set = {str(name) for name in keepout}
            unknown = keepout_set - all_names
            if unknown:
                raise ValidationError(f"Unknown keepout part(s): {sorted(unknown)}")
        else:
            keepout_set = all_names - moving
        self._moving_links = [link for link in links if getattr(link, "name", None) in moving]
        self._keepout_links = [
            link
            for link in links
            if getattr(link, "name", None) in keepout_set
            and getattr(link, "name", None) not in moving
        ]
        # ``allowed_pairs`` entries are either part-level 2-tuples
        # ``(part_a, part_b)`` (the whole part pair is exempt — e.g. a
        # telescoping stack that legitimately self-nests) or element-scoped
        # 4-tuples ``(part_a, part_b, elem_a, elem_b)`` (only that one
        # visual-vs-visual contact is exempt — e.g. a spindle seated in its
        # bearing socket, whose coaxial overlap is invariant to the joint value
        # and must not mask a genuine sweep collision elsewhere in the same
        # part pair).
        self._allowed: set[Tuple[str, str]] = set()
        self._allowed_elems: set[frozenset] = set()
        for entry in allowed_pairs or ():
            items = tuple(entry)
            if len(items) == 2:
                a, b = items
                self._allowed.add(_normalized_pair(str(a), str(b)))
            elif len(items) == 4:
                pa, pb, ea, eb = items
                self._allowed_elems.add(frozenset({(str(pa), str(ea)), (str(pb), str(eb))}))
            else:
                raise ValidationError(
                    "allowed_pairs entries must be (part_a, part_b) or "
                    f"(part_a, part_b, elem_a, elem_b); got {items!r}"
                )
    def min_clearance(self, joint_positions: Dict[str, float]) -> float:
        """Min FCL distance between moving and keep-out sets at the pose.

        Returns 0.0 when the sets interpenetrate; ``inf`` when either set has
        no collidable geometry.
        """
        view = self._scene.pose_view(dict(joint_positions))
        best = float("inf")
        moving_entries = []
        for link in self._moving_links:
            name = getattr(link, "name", None)
            entries = list(view.entries_by_part.get(str(name), ()))
            moving_entries.append((name, entries))
        for link in self._keepout_links:
            k_name = getattr(link, "name", None)
            k_entries = list(view.entries_by_part.get(str(k_name), ()))
            for m_name, m_entries in moving_entries:
                if _normalized_pair(str(m_name), str(k_name)) in self._allowed:
                    continue
                for m_entry in m_entries:
                    for k_entry in k_entries:
                        if self._allowed_elems and (
                            frozenset(
                                {
                                    (str(m_name), str(getattr(m_entry, "name", None))),
                                    (str(k_name), str(getattr(k_entry, "name", None))),
                                }
                            )
                            in self._allowed_elems
                        ):
                            continue
                        metrics = self._scene.pair_metrics(
                            view,
                            m_entry,
                            k_entry,
                            need_distance=True,
                        )
                        current = (
                            0.0
                            if metrics.collided
                            else float(
                                metrics.distance
                                if metrics.distance is not None
                                else float("inf")
                            )
                        )
                        if current < best:
                            best = current
                        if best <= 0.0:
                            return 0.0
        return best


# Compatibility for templates that imported the former private implementation.
_ClearanceProbe = ClearanceProbe


def min_clearance_at_pose(
    model: object,
    *,
    joint: str,
    joint_positions: Dict[str, float],
    keepout: Optional[Iterable[str]] = None,
    allowed_pairs: Optional[Iterable[Tuple[str, ...]]] = None,
    asset_root=None,
) -> float:
    """Min distance between ``joint``'s child subtree and the keep-out set."""
    probe = ClearanceProbe(
        model,
        joint_name=joint,
        keepout=keepout,
        allowed_pairs=allowed_pairs,
        asset_root=asset_root,
    )
    return probe.min_clearance(joint_positions)


def max_joint_value(
    model: object,
    *,
    joint: str,
    limit: float,
    start: float = 0.0,
    margin: float = _DEFAULT_MARGIN,
    keepout: Optional[Iterable[str]] = None,
    allowed_pairs: Optional[Iterable[Tuple[str, ...]]] = None,
    base_pose: Optional[Dict[str, float]] = None,
    scan_steps: int = _DEFAULT_SCAN_STEPS,
    bisect_iters: int = _DEFAULT_BISECT_ITERS,
    asset_root=None,
) -> float:
    """Largest joint value toward ``limit`` keeping >= ``margin`` clearance.

    Works for either direction: ``limit`` may be less than ``start`` (e.g.
    solving a negative lower limit). Every scanned pose between ``start`` and
    the returned value clears; the first violating scan step brackets a
    bisection that refines the boundary. If ``start`` itself violates, returns
    ``start`` (the caller should treat that as "this mechanism needs a
    geometry fix, not a limit").
    """
    if scan_steps < 2:
        raise ValidationError("scan_steps must be >= 2")
    probe = ClearanceProbe(
        model,
        joint_name=joint,
        keepout=keepout,
        allowed_pairs=allowed_pairs,
        asset_root=asset_root,
    )
    pose = dict(base_pose or {})

    def safe(value: float) -> bool:
        pose[joint] = float(value)
        return probe.min_clearance(pose) >= margin

    if start == limit:
        return start
    if not safe(start):
        return start
    span = limit - start
    last_safe = start
    first_bad: Optional[float] = None
    for step in range(1, scan_steps + 1):
        value = start + span * (step / scan_steps)
        if safe(value):
            last_safe = value
        else:
            first_bad = value
            break
    if first_bad is None:
        return limit
    lo, hi = last_safe, first_bad
    for _ in range(bisect_iters):
        mid = (lo + hi) / 2.0
        if safe(mid):
            lo = mid
        else:
            hi = mid
    return lo


def clamp_joint_limits(
    model: object,
    joint: str,
    *,
    margin: float = _DEFAULT_MARGIN,
    keepout: Optional[Iterable[str]] = None,
    allowed_pairs: Optional[Iterable[Tuple[str, ...]]] = None,
    base_pose: Optional[Dict[str, float]] = None,
    scan_steps: int = _DEFAULT_SCAN_STEPS,
    asset_root=None,
) -> MotionLimits:
    """Solve both travel directions of ``joint`` and write the tightened limits.

    Reads the joint's declared ``MotionLimits`` as the candidate range, keeps
    each bound only as far as the subtree stays ``margin`` clear of the
    keep-out set, mutates ``joint.motion_limits`` in place, and returns the
    new limits. Zero (the rest pose) must be inside the declared range.
    """
    articulation = _joint_by_name(model, joint)
    limits = getattr(articulation, "motion_limits", None)
    if limits is None:
        raise ValidationError(f"Articulation {joint!r} has no motion_limits to clamp")
    lower = float(limits.lower)
    upper = float(limits.upper)
    if not (lower <= 0.0 <= upper):
        raise ValidationError(
            f"clamp_joint_limits expects the rest pose 0 within [{lower}, {upper}] "
            f"for {joint!r}; solve custom ranges with max_joint_value directly"
        )
    common = dict(
        margin=margin,
        keepout=keepout,
        allowed_pairs=allowed_pairs,
        base_pose=base_pose,
        scan_steps=scan_steps,
        asset_root=asset_root,
    )
    new_upper = max_joint_value(model, joint=joint, limit=upper, start=0.0, **common)
    new_lower = max_joint_value(model, joint=joint, limit=lower, start=0.0, **common)
    if new_lower == 0.0 and new_upper == 0.0 and (lower != 0.0 or upper != 0.0):
        logger.warning(
            "clamp_joint_limits(%r): safe range collapsed to zero; flooring to "
            "[-%s, %s]",
            joint,
            ZERO_RANGE_FLOOR,
            ZERO_RANGE_FLOOR,
        )
        new_lower, new_upper = -ZERO_RANGE_FLOOR, ZERO_RANGE_FLOOR
    new_limits = MotionLimits(
        effort=limits.effort,
        velocity=limits.velocity,
        lower=new_lower,
        upper=new_upper,
    )
    articulation.motion_limits = new_limits
    return new_limits
