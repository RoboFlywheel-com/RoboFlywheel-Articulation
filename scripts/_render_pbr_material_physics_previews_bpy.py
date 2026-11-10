#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Render deterministic PBR material previews inside the pinned bpy environment."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import math
import os
import signal
import tempfile
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

try:
    from scripts._pbr_material_preview_common import (
        _bind_metric_uv_images,
        _choose_library_material,
        _disconnect_true_displacement,
        _RuntimeMaterialMapping,
        _smart_project_metric_uv,
    )
except ModuleNotFoundError:
    from _pbr_material_preview_common import (
        _bind_metric_uv_images,
        _choose_library_material,
        _disconnect_true_displacement,
        _RuntimeMaterialMapping,
        _smart_project_metric_uv,
    )

RENDER_SCHEMA = "articraft-pbr-material-physics-render/v1"
RENDERER_VERSION = "articraft-pbr-material-physics-renderer/v4"
RENDER_HELPER = Path(__file__).with_name("_pbr_material_preview_common.py")


class RenderItemTimeout(TimeoutError):
    """One material exceeded its configured render wall-time budget."""


def _timeout_handler(_signum: int, _frame: object) -> None:
    raise RenderItemTimeout("material render exceeded the per-item timeout")


def _set_parent_death_signal() -> None:
    """Ask Linux to terminate this worker if its orchestrator disappears."""
    libc = ctypes.CDLL(None, use_errno=True)
    prctl = libc.prctl
    prctl.argtypes = [
        ctypes.c_int,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.c_ulong,
        ctypes.c_ulong,
    ]
    prctl.restype = ctypes.c_int
    if prctl(1, signal.SIGTERM, 0, 0, 0) != 0:  # PR_SET_PDEATHSIG
        error_number = ctypes.get_errno()
        raise OSError(error_number, os.strerror(error_number))
    if os.getppid() == 1:
        os.kill(os.getpid(), signal.SIGTERM)


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _digest(value: object) -> str:
    payload = (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


RENDERER_SCRIPT_SHA256 = _sha256_path(Path(__file__).resolve())
HELPER_SCRIPT_SHA256 = _sha256_path(RENDER_HELPER.resolve())


def _atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()
    fd, raw_tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp = Path(raw_tmp)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def _contained(root: Path, relative: str, *, must_exist: bool = False) -> Path:
    raw = Path(relative)
    if raw.is_absolute():
        raise ValueError(f"relative path required: {relative!r}")
    candidate = (root / raw).resolve(strict=must_exist)
    if not candidate.is_relative_to(root):
        raise ValueError(f"path escapes root: {relative!r}")
    return candidate


def _read_inventory(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"inventory row {line_number} is not an object")
            rows.append(value)
    return rows


def _look_at(obj: Any, target: tuple[float, float, float]) -> None:
    import mathutils

    direction = mathutils.Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def _new_principled(name: str, color: tuple[float, float, float, float], roughness: float) -> Any:
    import bpy

    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = roughness
    return material


def _assign(obj: Any, material: Any) -> None:
    obj.data.materials.clear()
    obj.data.materials.append(material)


def _add_area_light(
    name: str,
    location: tuple[float, float, float],
    energy: float,
    size: float,
    target: tuple[float, float, float],
) -> None:
    import bpy

    data = bpy.data.lights.new(name, "AREA")
    data.energy = energy
    data.shape = "DISK"
    data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    _look_at(obj, target)


def _setup_scene(*, width: int, height: int, samples: int, threads: int) -> tuple[Any, ...]:
    import bpy

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.threads_mode = "FIXED"
    scene.render.threads = threads
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = False
    scene.render.use_file_extension = True
    if hasattr(scene, "view_settings"):
        try:
            scene.view_settings.view_transform = "AgX"
            scene.view_settings.look = "AgX - Medium High Contrast"
        except (TypeError, ValueError):
            pass

    world = bpy.data.worlds.new("Physics Preview World")
    world.use_nodes = True
    background = world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.055, 0.065, 0.08, 1.0)
    background.inputs["Strength"].default_value = 0.3
    scene.world = world

    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=64, ring_count=32, radius=0.72, location=(-0.72, 0, 0.82)
    )
    sphere = bpy.context.object
    sphere.name = "Material Sphere"
    for polygon in sphere.data.polygons:
        polygon.use_smooth = True

    bpy.ops.mesh.primitive_cube_add(size=1.15, location=(0.78, 0.02, 0.64))
    cube = bpy.context.object
    cube.name = "Material Rounded Cube"
    bevel = cube.modifiers.new("Rounded edges", "BEVEL")
    bevel.width = 0.12
    bevel.segments = 5
    bpy.context.view_layer.objects.active = cube
    cube.select_set(True)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    for polygon in cube.data.polygons:
        polygon.use_smooth = True

    bpy.ops.mesh.primitive_plane_add(size=8.0, location=(0, 0, 0))
    ground = bpy.context.object
    ground.name = "Neutral Ground"
    _assign(ground, _new_principled("Neutral Ground", (0.16, 0.18, 0.21, 1), 0.82))

    bpy.ops.mesh.primitive_plane_add(
        size=7.0,
        location=(0, 1.55, 2.2),
        rotation=(math.radians(90), 0, 0),
    )
    backdrop = bpy.context.object
    backdrop.name = "Neutral Backdrop"
    _assign(backdrop, _new_principled("Neutral Backdrop", (0.32, 0.35, 0.40, 1), 0.72))

    target = (0.05, 0.0, 0.72)
    _add_area_light("Key", (-3.4, -4.2, 5.0), 1050, 3.0, target)
    _add_area_light("Fill", (4.0, -2.2, 2.8), 700, 3.3, target)
    _add_area_light("Rim", (1.2, 2.8, 4.3), 900, 2.2, target)

    camera_data = bpy.data.cameras.new("Camera")
    camera = bpy.data.objects.new("Camera", camera_data)
    bpy.context.collection.objects.link(camera)
    camera.location = (3.65, -5.25, 2.85)
    camera.data.lens = 58
    _look_at(camera, target)
    scene.camera = camera
    return sphere, cube


def _validate_pixels(path: Path) -> dict[str, Any]:
    from PIL import Image, ImageStat

    with Image.open(path) as image:
        rgb = image.convert("RGB")
        thumbnail = rgb.resize((64, 64))
        width, height = rgb.size
        object_crops = (
            rgb.crop(
                (
                    int(width * 0.16),
                    int(height * 0.28),
                    int(width * 0.50),
                    int(height * 0.72),
                )
            ),
            rgb.crop(
                (
                    int(width * 0.50),
                    int(height * 0.30),
                    int(width * 0.88),
                    int(height * 0.78),
                )
            ),
        )
    stats = ImageStat.Stat(thumbnail)
    mean = [round(float(value), 6) for value in stats.mean]
    stddev = [round(float(value), 6) for value in stats.stddev]
    if sum(mean) / 3.0 < 5.0 or max(stddev) < 2.0:
        raise RuntimeError(f"render failed the nonblank pixel gate: mean={mean}, stddev={stddev}")
    object_metrics: list[dict[str, list[float]]] = []
    for index, crop in enumerate(object_crops):
        crop_stats = ImageStat.Stat(crop.resize((32, 32)))
        crop_mean = [round(float(value), 6) for value in crop_stats.mean]
        crop_stddev = [round(float(value), 6) for value in crop_stats.stddev]
        if sum(crop_mean) / 3.0 < 3.0 or max(crop_stddev) < 1.0:
            raise RuntimeError(
                f"render object region {index} failed the visibility gate: "
                f"mean={crop_mean}, stddev={crop_stddev}"
            )
        object_metrics.append({"rgb_mean": crop_mean, "rgb_stddev": crop_stddev})
    return {"rgb_mean": mean, "rgb_stddev": stddev, "object_regions": object_metrics}


def _load_material(package: Path, display_name: str) -> Any:
    import bpy

    with bpy.data.libraries.load(str(package), link=False) as (source, target):
        target.materials = sorted(str(name) for name in source.materials if name)
    material = _choose_library_material(tuple(target.materials), display_name)
    _disconnect_true_displacement(material)
    _bind_metric_uv_images(material)
    return material


def _render_one(
    row: Mapping[str, Any],
    *,
    snapshot_root: Path,
    output_root: Path,
    width: int,
    height: int,
    samples: int,
    threads: int,
) -> dict[str, Any]:
    import bpy

    material_key = str(row["material_key"])
    output_dir = output_root / "by-id" / material_key[:2]
    png_path = output_dir / f"{material_key}.png"
    report_path = output_dir / f"{material_key}.json"
    request = {
        "renderer_version": RENDERER_VERSION,
        "renderer_script_sha256": RENDERER_SCRIPT_SHA256,
        "helper_script_sha256": HELPER_SCRIPT_SHA256,
        "material_id": row["material_id"],
        "blend_sha256": row["blend_sha256"],
        "texture_size_m": row["texture_size_m"],
        "width": width,
        "height": height,
        "samples": samples,
        "threads": threads,
        "engine": "CYCLES_CPU",
        "blender_version": bpy.app.version_string,
    }
    request_sha256 = _digest(request)
    if report_path.is_file() and png_path.is_file():
        try:
            cached = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cached = None
        if (
            isinstance(cached, dict)
            and cached.get("status") == "success"
            and cached.get("request_sha256") == request_sha256
            and cached.get("png_sha256") == _sha256_path(png_path)
        ):
            return {"material_key": material_key, "status": "cache_hit"}

    started = time.monotonic()
    output_dir.mkdir(parents=True, exist_ok=True)
    try:
        package = _contained(snapshot_root, str(row["blend_path"]), must_exist=True)
        actual_blend_sha256 = _sha256_path(package)
        if actual_blend_sha256 != row["blend_sha256"]:
            raise ValueError(
                f"material package SHA mismatch: expected {row['blend_sha256']}, "
                f"got {actual_blend_sha256}"
            )
        sphere, cube = _setup_scene(
            width=width,
            height=height,
            samples=samples,
            threads=threads,
        )
        material = _load_material(package, str(row["display_name"]))
        mapping = _RuntimeMaterialMapping(
            material_profile="texture_set",
            mode="metric_uv",
            texture_size_m=float(row["texture_size_m"]),
            coordinate_space="metric_uv",
            uv_method="smart_project",
            preserve_node_graph=True,
            opaque=False,
        )
        for obj in (sphere, cube):
            _smart_project_metric_uv(bpy, obj, __import__("mathutils"), mapping)
            _assign(obj, material)
        scene = bpy.context.scene
        scene.render.filepath = str(png_path)
        bpy.ops.render.render(write_still=True)
        if not png_path.is_file() or png_path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("renderer did not produce a valid PNG")
        pixel_metrics = _validate_pixels(png_path)
        report = {
            "schema_version": RENDER_SCHEMA,
            "status": "success",
            "finished_at": _now(),
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "request": request,
            "request_sha256": request_sha256,
            "material_key": material_key,
            "material_id": row["material_id"],
            "png_path": str(png_path.relative_to(output_root)),
            "png_sha256": _sha256_path(png_path),
            "png_size_bytes": png_path.stat().st_size,
            "pixel_metrics": pixel_metrics,
        }
        _atomic_json(report_path, report)
        return {"material_key": material_key, "status": "success"}
    except Exception as exc:
        png_path.unlink(missing_ok=True)
        report = {
            "schema_version": RENDER_SCHEMA,
            "status": "failed",
            "finished_at": _now(),
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "request": request,
            "request_sha256": request_sha256,
            "material_key": material_key,
            "material_id": row.get("material_id"),
            "error_type": type(exc).__name__,
            "error": str(exc)[:2000],
            "traceback": traceback.format_exc(limit=8)[-6000:],
        }
        _atomic_json(report_path, report)
        return {"material_key": material_key, "status": "failed", "error": str(exc)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--snapshot-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--samples", type=int, default=16)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--item-timeout-seconds", type=float, default=1_200.0)
    parser.add_argument("--terminal-keys", type=Path)
    parser.add_argument("--limit", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.shard_count < 1 or not 0 <= args.shard_index < args.shard_count:
        raise SystemExit("invalid shard index/count")
    if min(args.width, args.height) < 128 or args.samples < 1 or args.threads < 1:
        raise SystemExit("invalid render dimensions, samples, or threads")
    if args.item_timeout_seconds <= 0:
        raise SystemExit("item timeout must be positive")
    _set_parent_death_signal()
    signal.signal(signal.SIGALRM, _timeout_handler)
    inventory = _read_inventory(args.inventory.resolve(strict=True))
    terminal_keys: set[str] = set()
    if args.terminal_keys is not None and args.terminal_keys.is_file():
        value = json.loads(args.terminal_keys.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or not isinstance(value.get("material_keys"), list):
            raise SystemExit("terminal render key file is invalid")
        terminal_keys = {str(key) for key in value["material_keys"] if isinstance(key, str)}
    selected = [
        row for index, row in enumerate(inventory) if index % args.shard_count == args.shard_index
    ]
    if args.limit is not None:
        selected = selected[: args.limit]
    counts = {"success": 0, "cache_hit": 0, "failed": 0}
    heartbeat_path = args.output_root / f"shard-{args.shard_index:02d}.heartbeat.json"
    for completed, row in enumerate(selected, 1):
        material_key = str(row["material_key"])
        _atomic_json(
            heartbeat_path,
            {
                "schema_version": RENDER_SCHEMA,
                "status": "rendering",
                "pid": os.getpid(),
                "shard_index": args.shard_index,
                "material_key": material_key,
                "material_id": row["material_id"],
                "started_epoch_seconds": time.time(),
                "updated_at": _now(),
            },
        )
        if material_key in terminal_keys:
            result = {
                "material_key": material_key,
                "status": "failed",
                "error": "isolated_after_repeated_worker_failure",
            }
        else:
            signal.setitimer(signal.ITIMER_REAL, args.item_timeout_seconds)
            try:
                result = _render_one(
                    row,
                    snapshot_root=args.snapshot_root.resolve(strict=True),
                    output_root=args.output_root.resolve(),
                    width=args.width,
                    height=args.height,
                    samples=args.samples,
                    threads=args.threads,
                )
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
        _atomic_json(
            heartbeat_path,
            {
                "schema_version": RENDER_SCHEMA,
                "status": result["status"],
                "pid": os.getpid(),
                "shard_index": args.shard_index,
                "material_key": material_key,
                "material_id": row["material_id"],
                "completed": completed,
                "scheduled": len(selected),
                "updated_epoch_seconds": time.time(),
                "updated_at": _now(),
            },
        )
        counts[str(result["status"])] += 1
        print(
            json.dumps(
                {
                    "completed": completed,
                    "scheduled": len(selected),
                    "material_key": result["material_key"],
                    "status": result["status"],
                    "shard_index": args.shard_index,
                },
                sort_keys=True,
            ),
            flush=True,
        )
    summary = {
        "schema_version": RENDER_SCHEMA,
        "finished_at": _now(),
        "shard_index": args.shard_index,
        "shard_count": args.shard_count,
        "scheduled": len(selected),
        **counts,
    }
    _atomic_json(args.output_root / f"shard-{args.shard_index:02d}.summary.json", summary)
    _atomic_json(
        heartbeat_path,
        {
            "schema_version": RENDER_SCHEMA,
            "status": "complete",
            "pid": os.getpid(),
            "shard_index": args.shard_index,
            "scheduled": len(selected),
            "updated_epoch_seconds": time.time(),
            "updated_at": _now(),
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
