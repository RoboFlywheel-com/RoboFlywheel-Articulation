#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Read-only Blender worker for native material bake eligibility scans."""

from __future__ import annotations

import collections
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

CLASSIFIER_VERSION = "articraft-native-bake-classifier/v1"
RESULT_SCHEMA = "articraft-native-bake-eligibility/v1"
SAFE_DECISION = "reusable_texture_set"
WORKER_PREFIX = "ARTICRAFT_NATIVE_BAKE_SCAN\t"

_PROCEDURAL_TEXTURE_TYPES = frozenset(
    {
        "TEX_BRICK",
        "TEX_CHECKER",
        "TEX_GRADIENT",
        "TEX_MAGIC",
        "TEX_MUSGRAVE",
        "TEX_NOISE",
        "TEX_POINTDENSITY",
        "TEX_SKY",
        "TEX_VORONOI",
        "TEX_WAVE",
        "TEX_WHITE_NOISE",
    }
)
_IRREDUCIBLE_NODE_TYPES = frozenset(
    {
        "BSDF_GLASS",
        "BSDF_HAIR",
        "BSDF_HAIR_PRINCIPLED",
        "BSDF_REFRACTION",
        "CAMERA",
        "FRESNEL",
        "HAIR_INFO",
        "HOLDOUT",
        "LAYER_WEIGHT",
        "LIGHT_PATH",
        "PARTICLE_INFO",
        "SCRIPT",
        "TEX_ENVIRONMENT",
        "TEX_IES",
        "TEX_POINTDENSITY",
        "TEX_SKY",
        "VOLUME_ABSORPTION",
        "VOLUME_INFO",
        "VOLUME_PRINCIPLED",
        "VOLUME_SCATTER",
    }
)
_COMPONENT_DEPENDENT_NODE_TYPES = frozenset(
    {
        "AMBIENT_OCCLUSION",
        "ATTRIBUTE",
        "BEVEL",
        "GEOMETRY",
        "NEW_GEOMETRY",
        "NORMAL",
        "OBJECT_INFO",
        "POINT_INFO",
        "TANGENT",
        "VERTEX_COLOR",
        "VECT_TRANSFORM",
        "VECTOR_TRANSFORM",
    }
)
_UNSUPPORTED_PRINCIPLED_WEIGHTS = (
    "Anisotropic",
    "Anisotropic IOR Level",
    "Clearcoat",
    "Coat Weight",
    "Sheen",
    "Sheen Weight",
    "Subsurface",
    "Subsurface Weight",
    "Thin Film Weight",
    "Transmission",
    "Transmission Weight",
)
_ALLOWED_LINKED_PRINCIPLED_INPUTS = frozenset(
    {
        "Alpha",
        "Base Color",
        "Emission Color",
        "Emission Strength",
        "Metallic",
        "Normal",
        "Roughness",
    }
)


class PackageIntegrityError(RuntimeError):
    pass


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _is_packed(image: Any) -> bool:
    if getattr(image, "packed_file", None) is not None:
        return True
    return bool(getattr(image, "packed_files", None))


def _node_trees(root: Any) -> tuple[tuple[str, Any], ...]:
    pending = [("root", root)]
    seen: set[int] = set()
    rows: list[tuple[str, Any]] = []
    while pending:
        path, tree = pending.pop()
        pointer = int(tree.as_pointer())
        if pointer in seen:
            continue
        seen.add(pointer)
        rows.append((path, tree))
        nested = []
        for node in tree.nodes:
            node_tree = getattr(node, "node_tree", None)
            if node_tree is not None:
                nested.append((f"{path}/{node.name}", node_tree))
        pending.extend(sorted(nested, key=lambda item: item[0], reverse=True))
    return tuple(rows)


def _group_output_input(group_node: Any, output_socket: Any) -> tuple[Any, Any] | None:
    tree = getattr(group_node, "node_tree", None)
    if tree is None:
        return None
    candidates = [node for node in tree.nodes if node.type == "GROUP_OUTPUT"]
    candidates.sort(key=lambda node: (not getattr(node, "is_active_output", True), node.name))
    wanted_identifier = str(getattr(output_socket, "identifier", "") or "")
    wanted_name = str(getattr(output_socket, "name", "") or "")
    for group_output in candidates:
        for socket in group_output.inputs:
            if wanted_identifier and getattr(socket, "identifier", "") == wanted_identifier:
                return tree, socket
            if socket.name == wanted_name:
                return tree, socket
    return None


def _shader_terminals(tree: Any, socket: Any, seen: set[int]) -> list[tuple[Any, Any]]:
    terminals: list[tuple[Any, Any]] = []
    for link in tuple(socket.links):
        source = link.from_socket
        pointer = int(source.as_pointer())
        if pointer in seen:
            continue
        seen.add(pointer)
        node = source.node
        if node.type == "REROUTE" and node.inputs:
            terminals.extend(_shader_terminals(tree, node.inputs[0], seen))
        elif node.type == "GROUP":
            nested = _group_output_input(node, source)
            if nested is None:
                terminals.append((tree, node))
            else:
                terminals.extend(_shader_terminals(nested[0], nested[1], seen))
        elif node.type in {"ADD_SHADER", "MIX_SHADER"}:
            for candidate in node.inputs:
                if candidate.type == "SHADER" and candidate.is_linked:
                    terminals.extend(_shader_terminals(tree, candidate, seen))
        else:
            terminals.append((tree, node))
    return terminals


def _coordinate_roots(tree: Any, output: Any, seen: set[int]) -> set[str]:
    pointer = int(output.as_pointer())
    if pointer in seen:
        return {"coordinate_cycle"}
    seen.add(pointer)
    node = output.node
    if node.type == "UVMAP":
        return {"uv"}
    if node.type == "TEX_COORD":
        name = str(output.name).strip().casefold().replace(" ", "_")
        return {"uv" if name == "uv" else f"texture_coordinate:{name}"}
    if node.type == "GROUP_INPUT":
        return {"group_input_unknown"}
    if node.type == "REROUTE" and node.inputs and node.inputs[0].is_linked:
        roots: set[str] = set()
        for link in tuple(node.inputs[0].links):
            roots.update(_coordinate_roots(tree, link.from_socket, seen))
        return roots
    if node.type == "GROUP":
        nested = _group_output_input(node, output)
        if nested is None:
            return {"group_output_unknown"}
        roots: set[str] = set()
        for link in tuple(nested[1].links):
            roots.update(_coordinate_roots(nested[0], link.from_socket, seen))
        return roots or {"group_output_constant"}
    linked_inputs = [socket for socket in node.inputs if socket.is_linked]
    if not linked_inputs:
        return {"constant"}
    roots: set[str] = set()
    for socket in linked_inputs:
        for link in tuple(socket.links):
            roots.update(_coordinate_roots(tree, link.from_socket, seen))
    return roots


def _input_is_active(socket: Any) -> bool:
    if socket.is_linked:
        return True
    value = getattr(socket, "default_value", 0.0)
    if isinstance(value, (int, float)):
        return math.isfinite(float(value)) and abs(float(value)) > 1e-6
    return bool(value)


def _has_animation(tree: Any) -> bool:
    animation = getattr(tree, "animation_data", None)
    return bool(animation and (getattr(animation, "action", None) or animation.drivers))


def inspect_material(material: Any) -> dict[str, Any]:
    if not material.use_nodes or material.node_tree is None:
        return {"scan_error": "material_has_no_node_tree"}
    trees = _node_trees(material.node_tree)
    nodes = [(path, tree, node) for path, tree in trees for node in tree.nodes]
    all_counts = collections.Counter(str(node.type) for _, _, node in nodes)
    linked_types = sorted(
        {
            str(node.type)
            for _, _, node in nodes
            if any(socket.is_linked for socket in node.inputs)
            or any(socket.is_linked for socket in node.outputs)
        }
    )
    active_outputs = [
        node
        for node in material.node_tree.nodes
        if node.type == "OUTPUT_MATERIAL" and getattr(node, "is_active_output", True)
    ]
    connected_outputs = [
        node
        for node in active_outputs
        if node.inputs.get("Surface") is not None and node.inputs["Surface"].is_linked
    ]
    terminals: list[tuple[Any, Any]] = []
    if len(connected_outputs) == 1:
        terminals = _shader_terminals(
            material.node_tree, connected_outputs[0].inputs["Surface"], set()
        )
    terminal_types = sorted(node.type for _, node in terminals)
    principled = [node for _, node in terminals if node.type == "BSDF_PRINCIPLED"]
    unsupported_inputs: list[str] = []
    for node in principled:
        for socket in node.inputs:
            if socket.is_linked and socket.name not in _ALLOWED_LINKED_PRINCIPLED_INPUTS:
                unsupported_inputs.append(f"{socket.name}:linked")
        for name in _UNSUPPORTED_PRINCIPLED_WEIGHTS:
            socket = node.inputs.get(name)
            if socket is not None and _input_is_active(socket):
                unsupported_inputs.append(name)

    coordinate_sources: set[str] = set()
    image_count = 0
    unpacked_count = 0
    nonflat_image_count = 0
    nonrepeat_image_count = 0
    unsupported_image_source_count = 0
    for _path, tree, node in nodes:
        if node.type != "TEX_IMAGE":
            continue
        image_count += 1
        if node.image is None or not _is_packed(node.image):
            unpacked_count += 1
        projection = str(getattr(node, "projection", "FLAT") or "FLAT").upper()
        nonflat_image_count += int(projection != "FLAT")
        extension = str(getattr(node, "extension", "") or "").upper()
        nonrepeat_image_count += int(extension != "REPEAT")
        image_source = str(getattr(node.image, "source", "") or "").upper()
        unsupported_image_source_count += int(image_source not in {"FILE", "TILED"})
        vector = node.inputs.get("Vector")
        if vector is None or not vector.is_linked:
            coordinate_sources.add("image_unlinked")
        else:
            for link in tuple(vector.links):
                coordinate_sources.update(_coordinate_roots(tree, link.from_socket, set()))

    volume_links = 0
    displacement_links = 0
    for output in active_outputs:
        volume = output.inputs.get("Volume")
        displacement = output.inputs.get("Displacement")
        volume_links += len(volume.links) if volume is not None else 0
        displacement_links += len(displacement.links) if displacement is not None else 0
    return {
        "active_output_count": len(active_outputs),
        "connected_surface_output_count": len(connected_outputs),
        "surface_terminal_types": terminal_types,
        "principled_terminal_count": len(principled),
        "node_type_counts": dict(sorted(all_counts.items())),
        "linked_node_types": linked_types,
        "procedural_texture_node_count": sum(
            all_counts[node_type] for node_type in _PROCEDURAL_TEXTURE_TYPES
        ),
        "image_texture_count": image_count,
        "unpacked_image_count": unpacked_count,
        "nonflat_image_projection_count": nonflat_image_count,
        "nonrepeat_image_extension_count": nonrepeat_image_count,
        "unsupported_image_source_count": unsupported_image_source_count,
        "coordinate_sources": sorted(coordinate_sources),
        "unsupported_principled_inputs": sorted(set(unsupported_inputs)),
        "volume_link_count": volume_links,
        "displacement_link_count": displacement_links,
        "has_animation_or_drivers": bool(getattr(material, "animation_data", None))
        or any(_has_animation(tree) for _, tree in trees),
    }


def classify_evidence(job: Mapping[str, Any], evidence: Mapping[str, Any]) -> tuple[str, list[str]]:
    keep_native: list[str] = []
    component_only: list[str] = []
    if evidence.get("scan_error"):
        return "review", ["scan_error"]
    linked_types = set(str(value) for value in evidence.get("linked_node_types", ()))
    irreducible = sorted(linked_types & _IRREDUCIBLE_NODE_TYPES)
    dependent = sorted(linked_types & _COMPONENT_DEPENDENT_NODE_TYPES)
    if irreducible:
        keep_native.append("irreducible_node_dependency")
    if job.get("optical_policy_present"):
        keep_native.append("optical_material")
    if int(evidence.get("volume_link_count") or 0):
        keep_native.append("volume_output_connected")
    terminals = list(evidence.get("surface_terminal_types") or ())
    if any(value in _IRREDUCIBLE_NODE_TYPES for value in terminals):
        keep_native.append("irreducible_surface_closure")
    if any(
        str(name).split(":", 1)[0] in {"Transmission", "Transmission Weight"}
        for name in evidence.get("unsupported_principled_inputs", ())
    ):
        keep_native.append("transmissive_surface")
    if keep_native:
        return "keep_native", sorted(set(keep_native))

    if job.get("node_qa_status") != "pass":
        component_only.append("normalized_node_qa_not_pass")
    if job.get("source_animated"):
        component_only.append("source_declared_animated")
    tile_size = job.get("texture_size_m")
    if (
        not isinstance(tile_size, (int, float))
        or not math.isfinite(float(tile_size))
        or tile_size <= 0
    ):
        component_only.append("texture_size_m_missing")
    if int(job.get("source_true_displacement_link_count") or 0):
        component_only.append("source_true_displacement")
    if (
        evidence.get("active_output_count") != 1
        or evidence.get("connected_surface_output_count") != 1
    ):
        component_only.append("surface_output_not_unique")
    if terminals != ["BSDF_PRINCIPLED"] or evidence.get("principled_terminal_count") != 1:
        component_only.append("surface_not_single_principled")
    if int(evidence.get("procedural_texture_node_count") or 0):
        component_only.append("procedural_texture_not_proven_periodic")
    if int(evidence.get("displacement_link_count") or 0):
        component_only.append("normalized_displacement_connected")
    if int(evidence.get("unpacked_image_count") or 0):
        component_only.append("image_not_packed")
    if int(evidence.get("nonflat_image_projection_count") or 0):
        component_only.append("nonflat_image_projection")
    if int(evidence.get("nonrepeat_image_extension_count") or 0):
        component_only.append("image_extension_not_repeat")
    if int(evidence.get("unsupported_image_source_count") or 0):
        component_only.append("image_source_not_static_file_or_tiled")
    if evidence.get("has_animation_or_drivers"):
        component_only.append("animated_or_driven_graph")
    if evidence.get("unsupported_principled_inputs"):
        component_only.append("nonstandard_principled_lobe")
    if dependent:
        component_only.append("component_dependent_node")
    allowed_coordinates = {"uv", "image_unlinked", "constant"}
    coordinates = set(str(value) for value in evidence.get("coordinate_sources", ()))
    if not coordinates.issubset(allowed_coordinates):
        component_only.append("non_uv_coordinate_dependency")
    if component_only:
        return "component_bake_only", sorted(set(component_only))
    return SAFE_DECISION, ["generic_repeatable_image_or_constant_pbr"]


def scan_one(job: Mapping[str, Any], bpy: Any) -> dict[str, Any]:
    package = Path(str(job["package_path"]))
    observed_sha256 = _sha256_file(package)
    if observed_sha256 != job.get("package_sha256"):
        raise PackageIntegrityError(f"package SHA changed for {job.get('material_id')}")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(str(package), link=False) as (source, target):
        names = sorted(str(name) for name in source.materials if name)
        target.materials = names
    materials = [material for material in target.materials if material is not None]
    if len(materials) != 1:
        evidence: dict[str, Any] = {
            "scan_error": "normalized_package_material_count",
            "material_count": len(materials),
        }
    else:
        evidence = inspect_material(materials[0])
    decision, reasons = classify_evidence(job, evidence)
    return {
        "schema_version": RESULT_SCHEMA,
        "classifier_version": CLASSIFIER_VERSION,
        "bpy_version": ".".join(str(value) for value in bpy.app.version),
        "material_id": job["material_id"],
        "display_name": job.get("display_name", ""),
        "category_slug": job.get("category_slug", ""),
        "catalog_sha256": job["catalog_sha256"],
        "package_relative_path": job["package_relative_path"],
        "package_sha256": observed_sha256,
        "input_sha256": job["input_sha256"],
        "decision": decision,
        "recommended_action": (
            "repackage_texture_set"
            if decision == SAFE_DECISION and evidence.get("image_texture_count", 0)
            else "materialize_constant_texture_set"
            if decision == SAFE_DECISION
            else "excluded_from_reusable_texture_set"
        ),
        "reason_codes": reasons,
        "evidence": evidence,
    }


def main() -> int:
    import bpy  # type: ignore[import-not-found]

    payload = json.loads(sys.stdin.read())
    if not isinstance(payload, dict) or payload.get("classifier_version") != CLASSIFIER_VERSION:
        raise SystemExit("invalid classifier job")
    materials = payload.get("materials")
    if not isinstance(materials, Sequence) or isinstance(materials, (str, bytes)):
        raise SystemExit("classifier job materials must be a list")
    for job in materials:
        if not isinstance(job, Mapping):
            raise SystemExit("classifier material job must be an object")
        try:
            result = scan_one(job, bpy)
        except PackageIntegrityError:
            raise
        except Exception as exc:  # keep one malformed material from losing the batch
            result = {
                "schema_version": RESULT_SCHEMA,
                "classifier_version": CLASSIFIER_VERSION,
                "bpy_version": ".".join(str(value) for value in bpy.app.version),
                "material_id": job.get("material_id"),
                "display_name": job.get("display_name", ""),
                "category_slug": job.get("category_slug", ""),
                "catalog_sha256": job.get("catalog_sha256"),
                "package_relative_path": job.get("package_relative_path"),
                "package_sha256": job.get("package_sha256"),
                "input_sha256": job.get("input_sha256"),
                "decision": "review",
                "recommended_action": "excluded_from_reusable_texture_set",
                "reason_codes": ["scan_error"],
                "evidence": {"scan_error": type(exc).__name__, "detail": str(exc)[:500]},
            }
        print(WORKER_PREFIX + json.dumps(result, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
