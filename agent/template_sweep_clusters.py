# SPDX-License-Identifier: Apache-2.0

"""Failure clustering + diagnosis hints for `articraft template compile-sweep`.

Groups per-seed failures by normalized failure_type and identifies shared
configuration axes across the cluster. Hands each cluster a textual diagnosis
hint that tells the authoring agent where in `_build_*` / `resolve_config` to
look first.

The hint catalog mirrors the spirit of `agent.harness_guidance` (which the
internal record-generation harness injects on known failure patterns) but is
self-contained and CLI-friendly. New failure types can be added to
`DIAGNOSIS_HINTS` without touching the clustering logic.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

from agent.template_sweep import SeedOutcome

GENERIC_HINT = (
    "No specific diagnosis registered for this failure_type. Read failure_details "
    "and inspect the corresponding _build_* / resolve_config section for the "
    "shared config axes listed above."
)

DIAGNOSIS_HINTS: Mapping[str, str] = {
    "fail_if_articulation_origin_far_from_geometry": (
        "Joint origin (in parent frame) falls outside parent or child visual "
        "geometry. Likely causes: (1) joint xyz is not anchored to a parent face "
        "and was picked from an unrelated dimension axis; (2) child visual is "
        "offset from child link origin without compensating the joint xyz; "
        "(3) _build_* derives parent and child origins independently instead of "
        "from a shared constraint datum. Fix: pick the joint origin from the "
        "exact face/axis where the two parts mate, then derive child geometry "
        "from the same datum."
    ),
    "fail_if_isolated_parts": (
        "One or more parts have geometry that does not touch the connected tree "
        "within contact_tol. Common causes: a decorative or interface part is "
        "placed in air; a fixed joint has an origin that doesn't bring the "
        "geometries within contact; or a child link is positioned far from its "
        "parent's nearest face. Fix: identify which parent face the part should "
        "mate with and align the child's visual + joint xyz to that face."
    ),
    "fail_if_parts_overlap_in_current_pose": (
        "Two or more parts geometrically overlap in the closed/zero pose. "
        "Likely causes: child link origin lies inside the parent solid (joint "
        "origin should be on a parent face, not inside it); sibling parts share "
        "volume because their positions are independently parameterized rather "
        "than derived from a common envelope/rail/axis. Fix: use the parent's "
        "mating face as the datum, then offset child origin OUTWARD along the "
        "joint normal so geometries meet but don't overlap."
    ),
    "fail_if_parts_overlap_in_sampled_poses": (
        "Parts overlap in one or more sampled poses, even if the closed pose is "
        "clean. Likely cause: joint range is too wide for the geometry envelope "
        "(door swings through neighbor part) or the child geometry sweeps into "
        "a sibling. Fix: tighten motion_limits or push the offending sibling "
        "outside the swept volume."
    ),
    "warn_if_part_contains_disconnected_geometry_islands": (
        "A single part has visual islands that don't connect. Likely cause: two "
        "decorative visuals were added to the same part with separated positions. "
        "Fix by embedding thin labels/markers into their supporting surface, adding "
        "a real bridge/cantilever, or splitting semantic pieces into separate parts "
        "joined by a fixed articulation."
    ),
    "fail_if_part_contains_disconnected_geometry_islands": (
        "A single part has visual islands that don't connect. In template sweep this "
        "is a hard failure because it usually renders as part-internal floating "
        "geometry. Fix by embedding thin labels/markers into their supporting "
        "surface, adding a real bridge/cantilever, or splitting semantic pieces into "
        "separate parts joined by a fixed articulation."
    ),
    "check_model_valid": (
        "Model.validate(strict=True) raised. Read failure_details for the "
        "specific validator complaint (missing axis on revolute joint, duplicate "
        "part name, invalid joint reference, malformed Origin, etc.)."
    ),
    "check_single_root_part": (
        "Model has more than one root part. Articulated objects must have exactly "
        "one root. Likely cause: a part was add_part'd but never connected via "
        "object_model.articulation(). Fix: attach the orphan to its semantic "
        "parent or remove it."
    ),
    "check_mesh_assets_ready": (
        "A visual references a mesh file that does not exist on disk yet. Likely "
        "cause: mesh export path is referenced before the export step runs, or "
        "asset_root/AssetContext is misconfigured. Fix: ensure the mesh-emitting "
        "helper runs before the visual is attached, or hard-code primitive "
        "geometry (Box/Cylinder) instead of file-backed meshes."
    ),
    "COMPILE_RUNTIME_FAILURE": (
        "Template raised a Python exception before tests could run. Read "
        "failure_details for the traceback. Typical culprits: enum value not "
        "handled in a _build_* branch; KeyError on a config field; ZeroDivision "
        "in a parameter-derived dimension; NaN/Inf coming from a transform."
    ),
}


@dataclass(slots=True, frozen=True)
class FailureCluster:
    """A group of seeds that share a failure_type_normalized and config axes."""

    cluster_id: int
    cluster_signature: str
    shared_failure_type: str
    shared_config_axes: dict[str, Any]
    seeds: list[int]
    example_failure_details: str
    diagnosis_hint: str
    is_singleton: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "cluster_signature": self.cluster_signature,
            "shared_failure_type": self.shared_failure_type,
            "shared_config_axes": self.shared_config_axes,
            "seeds": self.seeds,
            "example_failure_details": self.example_failure_details,
            "diagnosis_hint": self.diagnosis_hint,
            "is_singleton": self.is_singleton,
        }


def _flatten_config(config: Mapping[str, Any], prefix: str = "") -> dict[str, Any]:
    """Flatten nested-dict config so we can detect per-axis sharing.

    Lists and tuples are passed through as-is; nested dicts become dot-joined keys.
    """
    out: dict[str, Any] = {}
    for key, value in config.items():
        path = f"{prefix}{key}"
        if isinstance(value, Mapping):
            out.update(_flatten_config(value, prefix=f"{path}."))
        else:
            out[path] = value
    return out


def _hashable(value: Any) -> Any:
    if isinstance(value, (list, tuple)):
        return tuple(_hashable(v) for v in value)
    if isinstance(value, Mapping):
        return tuple(sorted((k, _hashable(v)) for k, v in value.items()))
    return value


def _shared_axes(configs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Return only the (key, value) pairs that are identical across ALL configs."""
    if not configs:
        return {}
    flattened = [_flatten_config(cfg) for cfg in configs]
    base_keys = set(flattened[0].keys())
    for flat in flattened[1:]:
        base_keys &= flat.keys()

    shared: dict[str, Any] = {}
    for key in base_keys:
        first = _hashable(flattened[0][key])
        if all(_hashable(flat[key]) == first for flat in flattened[1:]):
            # Drop noisy axes that are always present (like 'name' which is per-seed).
            value = flattened[0][key]
            if isinstance(value, str) and value.endswith(f"_{flattened[0].get('seed', '')}"):
                continue
            shared[key] = value
    return shared


def _example_details(outcomes: Sequence[SeedOutcome]) -> str:
    if not outcomes:
        return ""
    head = outcomes[0]
    return head.failure_details or ""


def _cluster_signature(failure_type: str, shared_axes: Mapping[str, Any]) -> str:
    """Stable signature so streak tracking can compare clusters across sweeps."""
    payload = {
        "failure_type": failure_type,
        "shared_axes": sorted((k, repr(_hashable(v))) for k, v in shared_axes.items()),
    }
    raw = repr(payload).encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:12]


def _hint_for(failure_type: str) -> str:
    return DIAGNOSIS_HINTS.get(failure_type, GENERIC_HINT)


def cluster_failures(failed_outcomes: Iterable[SeedOutcome]) -> list[FailureCluster]:
    """Group failed outcomes into clusters.

    1. Bucket by `failure_type_normalized` (falls back to raw failure_type).
    2. For each bucket with ≥2 seeds, compute the (key, value) pairs shared
       across every config in the bucket; singletons get an empty shared map.
    3. Attach a diagnosis hint from `DIAGNOSIS_HINTS`.
    4. Return clusters ordered by descending size, then by failure_type for
       reproducibility.
    """
    bucket: dict[str, list[SeedOutcome]] = {}
    for outcome in failed_outcomes:
        if outcome.verdict != "fail":
            continue
        key = outcome.failure_type_normalized or outcome.failure_type or "unknown_failure"
        bucket.setdefault(key, []).append(outcome)

    clusters: list[FailureCluster] = []
    next_id = 1
    for failure_type, outcomes in sorted(bucket.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        configs = [o.config for o in outcomes if isinstance(o.config, Mapping)]
        is_singleton = len(outcomes) == 1
        shared = {} if is_singleton else _shared_axes(configs)
        signature = _cluster_signature(failure_type, shared)
        cluster = FailureCluster(
            cluster_id=next_id,
            cluster_signature=signature,
            shared_failure_type=failure_type,
            shared_config_axes=shared,
            seeds=sorted(o.seed for o in outcomes),
            example_failure_details=_example_details(outcomes),
            diagnosis_hint=_hint_for(failure_type),
            is_singleton=is_singleton,
        )
        clusters.append(cluster)
        next_id += 1
    return clusters
