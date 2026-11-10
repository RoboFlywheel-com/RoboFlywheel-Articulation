# SPDX-License-Identifier: Apache-2.0

"""Visual-only 3D export helpers for directed editing figures."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import trimesh

from sdk import Box, Cylinder, Mesh, Sphere
from sdk._core.v0._urdf_export import compile_object_to_urdf_xml
from sdk._core.v0.assets import resolve_mesh_path
from sdk._core.v0.geometry_qc import _origin_to_mat4, compute_part_world_transforms
from sdk._core.v0.viewer_assets import convert_urdf_visual_meshes_to_glb
from specific_editing.selectors import surface_key


class VisualExportError(RuntimeError):
    """Raised when a model has no exportable visual geometry."""


def _matrix(value: Any) -> np.ndarray:
    return np.asarray(value, dtype=float)


def _geometry_mesh(geometry: Any, *, assets: Any) -> trimesh.Trimesh | None:
    if isinstance(geometry, Box):
        return trimesh.creation.box(extents=geometry.size)
    if isinstance(geometry, Cylinder):
        return trimesh.creation.cylinder(
            radius=float(geometry.radius), height=float(geometry.length), sections=48
        )
    if isinstance(geometry, Sphere):
        return trimesh.creation.uv_sphere(radius=float(geometry.radius), count=(28, 28))
    if not isinstance(geometry, Mesh):
        return None

    path_text = geometry.materialized_path or geometry.filename
    if not path_text:
        return None
    path = Path(path_text)
    if not path.is_absolute() and geometry.materialized_path is None:
        path = resolve_mesh_path(path, assets=assets, ensure_dir=False)
    if not path.is_file():
        raise VisualExportError(f"Visual mesh is missing: {path}")
    loaded = trimesh.load(path, force="mesh", process=False)
    if not isinstance(loaded, trimesh.Trimesh):
        raise VisualExportError(f"Visual asset did not load as a mesh: {path}")
    if geometry.scale:
        loaded = loaded.copy()
        loaded.apply_scale(tuple(float(value) for value in geometry.scale))
    return loaded


def _rgba(material: Any, model: Any) -> tuple[float, float, float, float]:
    resolved = material
    if isinstance(material, str):
        resolved = next(
            (candidate for candidate in model.materials if candidate.name == material), None
        )
    value = getattr(resolved, "rgba", None)
    if isinstance(value, (tuple, list)) and len(value) in {3, 4}:
        rgba = tuple(float(item) for item in value)
        return rgba + (1.0,) if len(rgba) == 3 else rgba  # type: ignore[return-value]
    return (0.64, 0.66, 0.68, 1.0)


def _appearance_for(part_name: str, visual: Any, visual_index: int, model: Any) -> dict[str, Any]:
    visual_name = str(getattr(visual, "name", None) or f"visual_{visual_index:03d}")
    key = surface_key(part_name, visual_name)
    for override in model.meta.get("specific_editing_material_overrides", ()):  # type: ignore[union-attr]
        surfaces = override.get("surfaces", ())
        if key in surfaces or (not surfaces and part_name in override.get("parts", ())):
            return dict(override)

    material_class = str(getattr(visual, "material_class_id", "") or "")
    metallic = 0.0
    roughness = 0.56
    transmission = 0.0
    if material_class.startswith("metal."):
        metallic, roughness = 0.78, 0.32
    elif material_class.startswith(("glass.", "optical.")):
        roughness, transmission = 0.12, 0.78
    elif material_class.startswith(("rubber.", "fabric.")):
        roughness = 0.88
    material = getattr(visual, "material", None)
    return {
        "name": str(getattr(material, "name", material) or material_class or "surface"),
        "rgba": list(_rgba(material, model)),
        "metallic": metallic,
        "roughness": roughness,
        "transmission": transmission,
        "ior": 1.45,
    }


def _pbr_material(spec: Mapping[str, Any]) -> trimesh.visual.material.PBRMaterial:
    rgba = np.clip(np.asarray(spec["rgba"], dtype=float), 0.0, 1.0)
    return trimesh.visual.material.PBRMaterial(
        name=str(spec.get("name", "surface")),
        baseColorFactor=np.rint(rgba * 255.0).astype(np.uint8),
        metallicFactor=float(spec.get("metallic", 0.0)),
        roughnessFactor=float(spec.get("roughness", 0.5)),
        alphaMode="BLEND" if float(rgba[3]) < 0.999 else "OPAQUE",
        doubleSided=True,
    )


def _strip_physics_elements(xml: str) -> tuple[str, dict[str, int]]:
    root = ET.fromstring(xml)
    removed = {"collision": 0, "inertial": 0}
    for link in root.findall("link"):
        for tag in removed:
            for element in list(link.findall(tag)):
                link.remove(element)
                removed[tag] += 1
    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode"), removed


def _missing_visual_meshes(xml: str, *, asset_root: Path) -> list[str]:
    root = ET.fromstring(xml)
    missing: list[str] = []
    for mesh in root.findall(".//visual/geometry/mesh"):
        filename = str(mesh.attrib.get("filename", "")).strip()
        if not filename:
            continue
        path = Path(filename)
        if not path.is_absolute():
            path = resolve_mesh_path(path, assets=asset_root, ensure_dir=False)
        if not path.is_file():
            missing.append(filename)
    return missing


def export_scene_glb(
    model: Any,
    path: str | Path,
    *,
    joint_positions: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Bake one articulated pose into a complete, materialized GLB scene."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    world = compute_part_world_transforms(model, dict(joint_positions or {}))
    scene = trimesh.Scene(base_frame="world")
    surface_count = 0
    triangle_count = 0
    for part_index, part in enumerate(model.parts):
        part_world = _matrix(world[part.name])
        for visual_index, visual in enumerate(part.visuals):
            mesh = _geometry_mesh(visual.geometry, assets=getattr(part, "assets", None))
            if mesh is None:
                continue
            mesh = mesh.copy()
            appearance = _appearance_for(part.name, visual, visual_index, model)
            mesh.visual = trimesh.visual.TextureVisuals(material=_pbr_material(appearance))
            node_name = f"{part.name}__{getattr(visual, 'name', '') or visual_index}"
            transform = part_world @ _matrix(_origin_to_mat4(visual.origin))
            scene.add_geometry(
                mesh,
                node_name=node_name,
                geom_name=f"surface_{part_index:03d}_{visual_index:03d}",
                transform=transform,
                metadata={
                    "part": part.name,
                    "visual": getattr(visual, "name", None),
                    "material_class_id": getattr(visual, "material_class_id", None),
                },
            )
            surface_count += 1
            triangle_count += len(mesh.faces)
    if surface_count == 0:
        raise VisualExportError("Model contains no exportable visual geometry")
    output.write_bytes(scene.export(file_type="glb"))
    return {
        "path": str(output),
        "bytes": output.stat().st_size,
        "surface_count": surface_count,
        "triangle_count": triangle_count,
        "node_count": len(scene.graph.nodes_geometry),
    }


def export_visual_urdf(model: Any, path: str | Path) -> dict[str, Any]:
    """Export display geometry and joints without collision or inertial materialization."""

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    xml = compile_object_to_urdf_xml(
        model,
        asset_root=output.parent,
        include_physical_collisions=False,
        validate=False,
    )
    xml, removed = _strip_physics_elements(xml)
    xml, warnings = convert_urdf_visual_meshes_to_glb(xml, asset_root=output.parent)
    missing = _missing_visual_meshes(xml, asset_root=output.parent)
    if missing:
        preview = ", ".join(missing[:5])
        suffix = "" if len(missing) <= 5 else f" (+{len(missing) - 5} more)"
        raise VisualExportError(f"Visual URDF references missing meshes: {preview}{suffix}")
    output.write_text(xml, encoding="utf-8")
    return {
        "path": str(output),
        "bytes": output.stat().st_size,
        "warnings": warnings,
        "removed_physics_nodes": removed,
        "part_count": len(model.parts),
        "joint_count": len(model.articulations),
    }


def export_visual_assets(model: Any, output_dir: str | Path) -> dict[str, Path]:
    """Write the two reusable 3D formats plus a small export receipt."""

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    urdf_path = root / "model.urdf"
    glb_path = root / "scene.glb"
    urdf_receipt = export_visual_urdf(model, urdf_path)
    glb_receipt = export_scene_glb(model, glb_path)
    receipt_path = root / "exports.json"
    receipt_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "purpose": "visualization_only",
                "physics_exported": False,
                "urdf": urdf_receipt,
                "glb": glb_receipt,
            },
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"visual_urdf": urdf_path, "scene_glb": glb_path, "receipt": receipt_path}


__all__ = [
    "VisualExportError",
    "export_scene_glb",
    "export_visual_assets",
    "export_visual_urdf",
]
