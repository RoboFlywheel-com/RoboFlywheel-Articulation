# SPDX-License-Identifier: Apache-2.0

"""Small runtime policy helpers shared by template checks and seed export."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Any

OVERLAP_POLICY_CODE = "overlap_allowance_forbidden"
OVERLAP_POLICY_NEXT_ACTION = "remove_allow_overlap_and_repair_geometry_or_interfaces"

RIGID_SEED_POLICY_CODE = "rigid_seed_no_movable_joint"
RIGID_SEED_NEXT_ACTION = "add_real_articulation_or_drop_the_static_candidate"

#: Joint types that make a seed an articulated object.  ``fixed`` and ``floating``
#: do not count: a model whose joints are all fixed is a rigid body.
MOVABLE_JOINT_TYPES = frozenset({"revolute", "prismatic", "continuous"})

_URDF_JOINT_TYPE = re.compile(r"<joint\b[^>]*\btype=\"([^\"]+)\"")


def movable_joint_types_in_urdf(urdf_xml: str) -> tuple[str, ...]:
    """Return the movable joint types declared by a compiled URDF."""

    return tuple(
        joint_type
        for joint_type in _URDF_JOINT_TYPE.findall(urdf_xml or "")
        if joint_type.strip().lower() in MOVABLE_JOINT_TYPES
    )


def rigid_seed_detail(urdf_xml: str) -> str | None:
    """Reject a seed that compiled into a rigid body.

    This pipeline exists to produce articulated objects, so every seed must
    carry at least one real non-fixed joint.  The rule is unconditional and
    matches the upstream variant contract: a candidate that would strip all
    articulation is blocked at authoring time, not exported as a rigid asset.
    Motion QC cannot catch this on its own — with zero movable joints it has no
    required poses and passes vacuously — so the keep/reject gates check here.
    """

    if movable_joint_types_in_urdf(urdf_xml):
        return None
    return (
        "Seed compiled into a rigid body: zero revolute/prismatic/continuous joints. "
        "Every seed must be an articulated object. Either give the sampled candidate "
        "its real mechanism, or remove the static candidate from the slot so no seed "
        "can reach it. Motion QC passes vacuously on a rigid model and cannot catch this."
    )


def template_is_design_backed(repo_root: Path, slug: str) -> bool:
    """Return whether a template has the current authoring Design contract."""

    return (
        repo_root / "articraft_template_authoring" / "designs" / f"{slug}.json"
    ).is_file()


def forbidden_overlap_allowances(
    allowances: Iterable[object],
) -> tuple[str, ...]:
    """Return whole or element-scoped allow_overlap records.

    allow_isolated_part and other authored allowance types are deliberately
    left untouched by this policy.
    """

    return tuple(
        str(item)
        for item in allowances
        if str(item).lstrip().startswith("allow_overlap(")
    )


def overlap_policy_result(
    *,
    repo_root: Path,
    slug: str,
    allowances: Iterable[object] = (),
    location: dict[str, Any] | None = None,
    owner: dict[str, Any] | None = None,
    design_backed: bool | None = None,
) -> dict[str, Any]:
    """Evaluate the shared Design-backed overlap policy.

    All pipeline stages use this function so the applicability rule, finding
    shape, and repair action cannot drift between preflight, sweep, corner,
    and seed export.  ``allow_isolated_part`` is intentionally not evaluated.
    """

    applicable = (
        template_is_design_backed(repo_root, slug)
        if design_backed is None
        else design_backed
    )
    if not applicable:
        return {"applicable": False, "forbidden": (), "detail": None, "finding": None}

    forbidden = forbidden_overlap_allowances(allowances)
    if not forbidden:
        return {"applicable": True, "forbidden": (), "detail": None, "finding": None}

    detail = (
        "Design-backed template emitted forbidden allow_overlap allowance(s): "
        f"{list(forbidden)!r}. Remove the allowance and repair clearance, support "
        "geometry, or the explicit interface."
    )
    finding_location = dict(location or {})
    finding_owner = dict(owner or {})
    identity = json.dumps(
        {
            "code": OVERLAP_POLICY_CODE,
            "detail": detail,
            "location": finding_location,
            "owner": finding_owner,
        },
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )
    finding = {
        "finding_id": hashlib.sha1(identity.encode()).hexdigest()[:12],
        "code": OVERLAP_POLICY_CODE,
        "severity": "error",
        "blocking": True,
        "confidence": "high",
        "detail": detail,
        "location": finding_location,
        "owner": finding_owner,
        "next_action": OVERLAP_POLICY_NEXT_ACTION,
    }
    return {
        "applicable": True,
        "forbidden": forbidden,
        "detail": detail,
        "finding": finding,
    }


__all__ = [
    "MOVABLE_JOINT_TYPES",
    "OVERLAP_POLICY_CODE",
    "OVERLAP_POLICY_NEXT_ACTION",
    "RIGID_SEED_NEXT_ACTION",
    "RIGID_SEED_POLICY_CODE",
    "movable_joint_types_in_urdf",
    "rigid_seed_detail",
    "forbidden_overlap_allowances",
    "overlap_policy_result",
    "template_is_design_backed",
]
