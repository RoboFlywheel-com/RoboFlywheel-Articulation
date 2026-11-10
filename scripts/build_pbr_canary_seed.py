#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Build one self-contained exact-class PBR canary seed.

The template remains the runtime source of truth. This exporter derives stable
``part::visual`` surface keys, resolves each scalar ``material_class_id`` only
against the content-addressed formal PBR library, and writes
``appearance.lock.json``. Physics is intentionally postponed: this path does
not resolve physical properties or emit a placeholder ``physics.lock.json``.
``model.urdf`` and its normal ``assets/meshes`` tree remain the geometry
contract; a flattened render job is available only as an explicit debugging
aid.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import importlib
import json
import os
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path, PureWindowsPath
from typing import Any

import numpy as np
import trimesh

from agent.template_registry import TEMPLATE_REGISTRY
from articraft.appearance import (
    appearance_requests_from_model,
    load_material_pools,
    materialize_appearance_lock,
    resolve_appearances_from_pools,
)
from scripts.check_appearance_mechanical_invariance import (
    config_mechanical_fingerprint,
    object_model_mechanical_fingerprint,
)
from sdk import AssetContext, Box, Cylinder, Mesh, Sphere
from sdk._core.v0._urdf_export import compile_object_to_urdf_xml
from sdk._core.v0.assets import AssetSession, activate_asset_session, resolve_mesh_path
from sdk._core.v0.geometry_qc import _origin_to_mat4, compute_part_world_transforms

CANARY_SLUGS = (
    "Handtools_clothes_peg",
    "Container_Plastic_can",
    "Urban_Environment_Large_Trashcan",
    "Container_Glass_bottle",
    "loom_shuttle",
)
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PBR_LIBRARY = REPO_ROOT / "pbr_material_library" / "latest.json"
RENDER_JOB_SCHEMA = "articraft-pbr-render-job/v1"
SEED_MANIFEST_SCHEMA = "articraft-pbr-canary-seed/v6"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_default(value: object) -> object:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return dataclasses.asdict(value)
    if isinstance(value, (set, frozenset, tuple)):
        return list(value)
    if isinstance(value, Path):
        return value.as_posix()
    raise TypeError(f"cannot serialize {type(value).__name__}")


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(
            payload,
            default=_json_default,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _validate_urdf_mesh_assets(urdf: str, seed_root: Path) -> tuple[Path, ...]:
    """Return the contained files referenced by URDF ``mesh`` elements.

    A published seed must be portable: absolute paths, parent traversal,
    Windows drive/UNC paths, missing files, directories, and symlinks escaping
    the seed root are all rejected before the staging directory is published.
    """

    root = seed_root.resolve(strict=True)
    try:
        document = ET.fromstring(urdf)
    except ET.ParseError as exc:
        raise ValueError(f"invalid model URDF: {exc}") from exc

    resolved_assets: list[Path] = []
    for index, mesh_element in enumerate(document.findall(".//mesh")):
        raw_ref = mesh_element.get("filename")
        if raw_ref is None or not raw_ref.strip():
            raise ValueError(f"URDF mesh[{index}] has no filename")
        mesh_ref = raw_ref.strip()
        ref_path = Path(mesh_ref)
        windows_path = PureWindowsPath(mesh_ref)
        if (
            ref_path.is_absolute()
            or windows_path.is_absolute()
            or bool(windows_path.drive)
            or "\\" in mesh_ref
            or ".." in ref_path.parts
        ):
            raise ValueError(f"URDF mesh[{index}] is not a safe seed-relative path: {mesh_ref!r}")

        candidate = root / ref_path
        try:
            resolved = candidate.resolve(strict=True)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"URDF mesh[{index}] is missing from the seed: {mesh_ref!r}"
            ) from exc
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"URDF mesh[{index}] escapes the seed root: {mesh_ref!r}") from exc
        if not resolved.is_file():
            raise ValueError(f"URDF mesh[{index}] is not a file: {mesh_ref!r}")
        resolved_assets.append(resolved)
    return tuple(resolved_assets)


def _strip_build_cache(seed_root: Path) -> None:
    """Drop duplicate CadQuery cache files, matching normal ``gen-seeds`` output."""

    cache_dir = seed_root / "assets" / ".cadquery_cache"
    if cache_dir.exists():
        shutil.rmtree(cache_dir)


def _safe_name(value: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return result or "visual"


def _primitive_mesh(geometry: object) -> trimesh.Trimesh | None:
    if isinstance(geometry, Box):
        return trimesh.creation.box(extents=geometry.size)
    if isinstance(geometry, Cylinder):
        return trimesh.creation.cylinder(
            radius=geometry.radius,
            height=geometry.length,
            sections=48,
        )
    if isinstance(geometry, Sphere):
        return trimesh.creation.uv_sphere(radius=geometry.radius, count=(32, 32))
    return None


def _visual_mesh(geometry: object, *, assets: AssetContext) -> trimesh.Trimesh:
    if isinstance(geometry, Mesh):
        if geometry.source_geometry is not None:
            mesh = _primitive_mesh(geometry.source_geometry)
            if mesh is None:
                raise TypeError(f"unsupported source primitive: {geometry.source_geometry!r}")
            if geometry.source_transform is not None:
                mesh.apply_transform(np.asarray(geometry.source_transform, dtype=float))
        else:
            path_text = geometry.materialized_path or geometry.filename
            if not path_text:
                raise ValueError(f"mesh has no materialized path: {geometry!r}")
            path = Path(path_text)
            if not path.is_absolute() and geometry.materialized_path is None:
                path = resolve_mesh_path(path, assets=assets, ensure_dir=False)
            loaded = trimesh.load(path, force="mesh", process=False)
            if not isinstance(loaded, trimesh.Trimesh):
                raise TypeError(f"mesh source did not resolve to one mesh: {path}")
            mesh = loaded.copy()
        if geometry.scale is not None:
            scale = np.eye(4)
            scale[0, 0], scale[1, 1], scale[2, 2] = geometry.scale
            mesh.apply_transform(scale)
        return mesh
    mesh = _primitive_mesh(geometry)
    if mesh is None:
        raise TypeError(f"unsupported visual geometry: {type(geometry).__name__}")
    return mesh


def _build_model(slug: str, seed: int, assets: AssetContext) -> tuple[Any, Any, Path]:
    if slug not in TEMPLATE_REGISTRY:
        raise ValueError(f"unknown template slug: {slug}")
    module = importlib.import_module(f"agent.templates.{slug}")
    config = module.config_from_seed(seed)
    build = getattr(module, f"build_{TEMPLATE_REGISTRY[slug]}")
    session = AssetSession(assets.root, mesh_subdir=assets.mesh_subdir)
    with activate_asset_session(session):
        model = build(config, assets=assets)
    model.validate(strict=True)
    source_path = Path(module.__file__).resolve(strict=True)
    return model, config, source_path


def build_canary_seed(
    *,
    slug: str,
    seed: int,
    material_seed: int | None = None,
    pbr_library: Path = DEFAULT_PBR_LIBRARY,
    output_dir: Path,
    emit_debug_render_job: bool = False,
) -> dict[str, Any]:
    """Build and atomically publish one seed directory."""

    resolved_material_seed = int(seed) if material_seed is None else int(material_seed)
    destination = output_dir.resolve()
    if destination.exists():
        raise FileExistsError(f"seed output already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=f".{destination.name}.", dir=destination.parent) as raw:
        staging = Path(raw)
        assets = AssetContext(staging)
        model, config, template_path = _build_model(slug, seed, assets)
        _strip_build_cache(staging)
        urdf = compile_object_to_urdf_xml(
            model,
            asset_root=staging,
            include_physical_collisions=False,
            validate=True,
        )
        mesh_assets = _validate_urdf_mesh_assets(urdf, staging)
        urdf_path = staging / "model.urdf"
        urdf_path.write_text(urdf, encoding="utf-8")
        model_urdf_sha256 = _sha256(urdf_path)
        template_sha256 = _sha256(template_path)

        part_world = compute_part_world_transforms(model, {}) if emit_debug_render_job else None
        render_mesh_dir = staging / "render_meshes" if emit_debug_render_job else None
        if render_mesh_dir is not None:
            render_mesh_dir.mkdir(parents=True)
        requests = list(appearance_requests_from_model(model, require_all=True))
        requests_by_surface = {request.surface_key: request for request in requests}
        visuals: list[dict[str, Any]] = []
        for part in model.parts:
            for index, visual in enumerate(part.visuals):
                visual_name = visual.name or f"visual_{index}"
                surface_key = f"{part.name}::{visual_name}"
                request = requests_by_surface[surface_key]

                if render_mesh_dir is not None and part_world is not None:
                    mesh = _visual_mesh(visual.geometry, assets=assets)
                    mesh_filename = (
                        f"{len(visuals):04d}_{_safe_name(part.name)}_{_safe_name(visual_name)}.obj"
                    )
                    mesh_path = render_mesh_dir / mesh_filename
                    mesh.export(mesh_path, file_type="obj")
                    world = np.asarray(part_world[part.name], dtype=float) @ np.asarray(
                        _origin_to_mat4(visual.origin),
                        dtype=float,
                    )
                    visuals.append(
                        {
                            "asset_type": request.asset_type,
                            "mesh_path": mesh_path.relative_to(staging).as_posix(),
                            "name": visual_name,
                            "part_name": part.name,
                            "surface_key": surface_key,
                            "world_matrix": world.tolist(),
                        }
                    )

        material_class_ids = {
            request.material_class_id
            for request in requests
            if request.material_class_id is not None
        }
        library = load_material_pools(pbr_library, material_class_ids)
        resolved = resolve_appearances_from_pools(
            requests,
            library.pools,
            library.pool_sha256,
            slug=slug,
            material_seed=resolved_material_seed,
        )
        lock = materialize_appearance_lock(
            staging,
            resolved,
            slug=slug,
            seed=seed,
            material_seed=resolved_material_seed,
            template_sha256=template_sha256,
            model_urdf_sha256=model_urdf_sha256,
            library_snapshot_sha256=library.library_snapshot_sha256,
            pool_index_sha256=library.pool_index_sha256,
        )
        if emit_debug_render_job:
            render_job = {
                "schema_version": RENDER_JOB_SCHEMA,
                "seed": int(seed),
                "slug": slug,
                "visuals": visuals,
            }
            _write_json(staging / "render_job.json", render_job)
        _write_json(staging / "config.json", config)
        manifest = {
            "schema_version": SEED_MANIFEST_SCHEMA,
            "appearance_lock_sha256": _sha256(staging / "appearance.lock.json"),
            "config_mechanical_sha256": config_mechanical_fingerprint(config),
            "flat_color_binding_count": sum(
                row["asset_type"] == "flat_color" for row in lock["bindings"]
            ),
            "material_binding_count": sum(row["material"] is not None for row in lock["bindings"]),
            "material_seed": resolved_material_seed,
            "mechanical_sha256": object_model_mechanical_fingerprint(model),
            "mesh_asset_count": len(set(mesh_assets)),
            "model_urdf_sha256": model_urdf_sha256,
            "pbr_library_logical_snapshot_sha256": library.library_snapshot_sha256,
            "pbr_library_manifest_sha256": library.manifest_sha256,
            "pbr_library_pointer_sha256": library.pointer_sha256,
            "pbr_library_pool_index_sha256": library.pool_index_sha256,
            "physics": {"status": "not_resolved"},
            "seed": int(seed),
            "slug": slug,
            "template_sha256": template_sha256,
            "visual_count": len(requests),
        }
        _write_json(staging / "seed_manifest.json", manifest)
        os.replace(staging, destination)
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slug", choices=CANARY_SLUGS)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--material-seed",
        type=int,
        default=None,
        help="appearance seed (defaults to --seed without changing geometry sampling)",
    )
    parser.add_argument(
        "--pbr-library",
        type=Path,
        default=DEFAULT_PBR_LIBRARY,
        help="formal PBR library latest.json pointer",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--emit-debug-render-job",
        action="store_true",
        help="also emit flattened render_meshes/render_job.json for debugging only",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = build_canary_seed(
        slug=args.slug,
        seed=args.seed,
        material_seed=args.material_seed,
        pbr_library=args.pbr_library,
        output_dir=args.output,
        emit_debug_render_job=args.emit_debug_render_job,
    )
    print(json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
