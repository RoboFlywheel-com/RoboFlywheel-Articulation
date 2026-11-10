# SPDX-License-Identifier: Apache-2.0

"""JSON-driven pipeline for directed edits of structured 3D generators."""

from __future__ import annotations

import argparse
import dataclasses
import gc
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from sdk import AssetContext, Material
from specific_editing import __version__
from specific_editing.export import export_visual_assets
from specific_editing.generators import CatalogError, get_generator, list_generators
from specific_editing.pbr_materials import theme_receipt
from specific_editing.selectors import (
    matches_surface,
    matching_surface_keys,
    part_names_from_surfaces,
    part_selectors,
    surface_key,
)

SCHEMA_VERSION = 1
EDIT_KINDS = frozenset({"component", "count", "material", "size"})
_COMPACT_COMPARISON_PADDING = 22
VALID_VIEWS = frozenset({"front", "rear", "side", "left", "top", "iso", "front_iso", "rear_iso"})
VALID_POSES = frozenset({"closed", "rest", "neutral", "mid", "half", "open", "max"})
VALID_FRAME_SCOPES = frozenset({"global", "edit_group"})
_SAFE_ID_RE = re.compile(r"[^a-zA-Z0-9_.-]+")


class PipelineError(ValueError):
    """Raised for an invalid editing spec or a failed variant build."""


@dataclass(frozen=True, slots=True)
class EditVariant:
    variant_id: str
    label: str
    kind: str
    target: str
    value: Any
    overrides: dict[str, Any]
    material_override: dict[str, Any] | None
    highlight_parts: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EditingSpec:
    source_path: Path
    name: str
    generator_id: str
    seed: int | None
    base_config: dict[str, Any]
    variants: tuple[EditVariant, ...]
    views: tuple[str, ...]
    poses: tuple[str, ...]
    image_size: tuple[int, int]
    supersample: int
    shadow_strength: float
    renderer: str
    frame_scope: str
    compact_comparison_kinds: tuple[str, ...]
    normalize_comparison_foreground: bool
    raw: dict[str, Any]


@dataclass(frozen=True, slots=True)
class BuiltVariant:
    variant: EditVariant
    requested_config: dict[str, Any]
    resolved_config: dict[str, Any]
    object_model: Any
    target_parts: tuple[str, ...]
    target_surfaces: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PipelineResult:
    output_root: Path
    manifest_path: Path
    variant_count: int
    image_count: int


def _safe_id(value: str, *, fallback: str) -> str:
    cleaned = _SAFE_ID_RE.sub("-", value.strip()).strip("-._")
    return (cleaned or fallback)[:80]


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return {
            field.name: _jsonable(getattr(value, field.name)) for field in dataclasses.fields(value)
        }
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if hasattr(value, "value"):
        return _jsonable(value.value)
    return repr(value)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_jsonable(payload), indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise PipelineError(f"{label} must be a JSON object with string keys")
    return dict(value)


def _parse_string_list(value: Any, label: str, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None:
        return default
    if not isinstance(value, list) or not value or not all(isinstance(item, str) for item in value):
        raise PipelineError(f"{label} must be a non-empty string array")
    return tuple(value)


def _parse_variants(value: Any) -> tuple[EditVariant, ...]:
    if not isinstance(value, list) or not value:
        raise PipelineError("edits must be a non-empty JSON array")
    variants: list[EditVariant] = []
    seen_ids: set[str] = set()
    for edit_index, item in enumerate(value):
        entry = _require_mapping(item, f"edits[{edit_index}]")
        kind = entry.get("kind")
        target = entry.get("target")
        values = entry.get("values")
        if kind not in EDIT_KINDS:
            raise PipelineError(f"edits[{edit_index}].kind must be one of {sorted(EDIT_KINDS)}")
        if not isinstance(target, str) or not target.strip():
            raise PipelineError(f"edits[{edit_index}].target must be a non-empty string")
        if not isinstance(values, list) or not values:
            raise PipelineError(f"edits[{edit_index}].values must be a non-empty array")
        label_prefix = entry.get("label", target)
        if not isinstance(label_prefix, str):
            raise PipelineError(f"edits[{edit_index}].label must be a string")
        highlights = _parse_string_list(entry.get("highlight_parts"), "highlight_parts", ())
        for value_index, item_value in enumerate(values):
            if kind == "material":
                material = _require_mapping(
                    item_value, f"edits[{edit_index}].values[{value_index}]"
                )
                display_value = material.get("name", f"material-{value_index + 1}")
                overrides: dict[str, Any] = {}
            else:
                material = None
                display_value = item_value
                overrides = {target: item_value}
            display_label = (
                display_value.replace("_", " ") if isinstance(display_value, str) else display_value
            )
            raw_id = f"{kind}-{target}-{display_value}"
            variant_id = _safe_id(raw_id, fallback=f"edit-{edit_index}-{value_index}")
            if variant_id in seen_ids:
                variant_id = f"{variant_id}-{value_index + 1}"
            seen_ids.add(variant_id)
            variants.append(
                EditVariant(
                    variant_id=variant_id,
                    label=f"{label_prefix}: {display_label}",
                    kind=str(kind),
                    target=target,
                    value=item_value,
                    overrides=overrides,
                    material_override=material,
                    highlight_parts=highlights,
                )
            )
    return tuple(variants)


def load_spec(path: str | Path) -> EditingSpec:
    source_path = Path(path).expanduser().resolve()
    try:
        raw = _require_mapping(json.loads(source_path.read_text(encoding="utf-8")), "spec")
    except FileNotFoundError as exc:
        raise PipelineError(f"Spec does not exist: {source_path}") from exc
    except OSError as exc:
        raise PipelineError(f"Cannot read spec {source_path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise PipelineError(f"Invalid JSON in {source_path}: {exc}") from exc
    if raw.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
        raise PipelineError(f"Only schema_version={SCHEMA_VERSION} is supported")
    name = raw.get("name")
    generator_id = raw.get("generator")
    if not isinstance(name, str) or not name.strip():
        raise PipelineError("name must be a non-empty string")
    if not isinstance(generator_id, str) or not generator_id.strip():
        raise PipelineError("generator must be a non-empty string")
    seed = raw.get("seed")
    if seed is not None and (not isinstance(seed, int) or isinstance(seed, bool)):
        raise PipelineError("seed must be an integer or null")
    render = _require_mapping(raw.get("render", {}), "render")
    size = render.get("image_size", [720, 560])
    if (
        not isinstance(size, list)
        or len(size) != 2
        or any(not isinstance(item, int) or isinstance(item, bool) or item < 128 for item in size)
    ):
        raise PipelineError("render.image_size must be [width, height] with values >= 128")
    renderer = render.get("backend", "blender")
    if not isinstance(renderer, str) or renderer not in {"blender", "software"}:
        raise PipelineError("render.backend must be 'blender' or 'software'")
    frame_scope = render.get("frame_scope", "global")
    if not isinstance(frame_scope, str) or frame_scope not in VALID_FRAME_SCOPES:
        raise PipelineError("render.frame_scope must be 'global' or 'edit_group'")
    compact_comparison_kinds = _parse_string_list(
        render.get("compact_comparison_kinds"),
        "render.compact_comparison_kinds",
        (),
    )
    invalid_compact_kinds = sorted(set(compact_comparison_kinds) - EDIT_KINDS)
    if invalid_compact_kinds:
        raise PipelineError(
            "render.compact_comparison_kinds contains unknown edit kinds: "
            + ", ".join(invalid_compact_kinds)
        )
    normalize_comparison_foreground = render.get("normalize_comparison_foreground", False)
    if not isinstance(normalize_comparison_foreground, bool):
        raise PipelineError("render.normalize_comparison_foreground must be a boolean")
    supersample = render.get("supersample", 2)
    if (
        not isinstance(supersample, int)
        or isinstance(supersample, bool)
        or not 1 <= supersample <= 4
    ):
        raise PipelineError("render.supersample must be an integer in [1, 4]")
    shadow_strength = render.get("shadow_strength", 1.0)
    if (
        not isinstance(shadow_strength, (int, float))
        or isinstance(shadow_strength, bool)
        or not math.isfinite(float(shadow_strength))
        or not 0.0 <= float(shadow_strength) <= 1.0
    ):
        raise PipelineError("render.shadow_strength must be a number in [0, 1]")
    views = _parse_string_list(render.get("views"), "render.views", ("front_iso", "side"))
    invalid_views = [
        view for view in views if view.strip().lower().replace("-", "_") not in VALID_VIEWS
    ]
    if invalid_views:
        raise PipelineError(f"Unknown render view(s): {', '.join(invalid_views)}")
    poses = _parse_string_list(render.get("poses"), "render.poses", ("closed",))
    invalid_poses = [pose for pose in poses if pose.strip().lower() not in VALID_POSES]
    if invalid_poses:
        raise PipelineError(f"Unknown render pose(s): {', '.join(invalid_poses)}")
    return EditingSpec(
        source_path=source_path,
        name=name,
        generator_id=generator_id,
        seed=seed,
        base_config=_require_mapping(raw.get("base_config", {}), "base_config"),
        variants=_parse_variants(raw.get("edits")),
        views=views,
        poses=poses,
        image_size=(size[0], size[1]),
        supersample=supersample,
        shadow_strength=float(shadow_strength),
        renderer=renderer,
        frame_scope=frame_scope,
        compact_comparison_kinds=compact_comparison_kinds,
        normalize_comparison_foreground=normalize_comparison_foreground,
        raw=raw,
    )


def _validate_edit_target(spec: EditingSpec, variant: EditVariant) -> None:
    registration = get_generator(spec.generator_id)
    if variant.kind == "material":
        allowed = tuple(registration.material_patterns)
    else:
        allowed = tuple(
            axis.field
            for axis in registration.axes
            if axis.kind == variant.kind or axis.name == variant.kind
        )
    if variant.target not in allowed:
        raise PipelineError(
            f"{variant.kind} edit target {variant.target!r} is not declared for "
            f"{spec.generator_id}; choose one of: {', '.join(allowed)}"
        )


def _material_rgba(material: Mapping[str, Any]) -> tuple[float, float, float, float]:
    rgba = material.get("rgba")
    if not isinstance(rgba, list) or len(rgba) not in {3, 4}:
        raise PipelineError("material value must include rgba with 3 or 4 numeric values")
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in rgba):
        raise PipelineError("material rgba entries must be numeric")
    values = tuple(float(value) for value in rgba)
    if any(not math.isfinite(value) or value < 0.0 or value > 1.0 for value in values):
        raise PipelineError("material rgba entries must be in [0, 1]")
    return values + (1.0,) if len(values) == 3 else values  # type: ignore[return-value]


def _material_number(
    material: Mapping[str, Any], field: str, default: float, lower: float, upper: float
) -> float:
    value = material.get(field, default)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise PipelineError(f"material.{field} must be numeric")
    resolved = float(value)
    if not math.isfinite(resolved) or not lower <= resolved <= upper:
        raise PipelineError(f"material.{field} must be in [{lower:g}, {upper:g}]")
    return resolved


def _validate_material_override(material: Mapping[str, Any]) -> dict[str, Any]:
    rgba = _material_rgba(material)
    name = material.get("name", "directed_material")
    if not isinstance(name, str) or not name.strip():
        raise PipelineError("material.name must be a non-empty string")
    if "parts" in material and "surfaces" in material:
        raise PipelineError("material may define parts or surfaces, not both")
    for field in ("parts", "surfaces"):
        if field not in material:
            continue
        selectors = material[field]
        if (
            not isinstance(selectors, list)
            or not selectors
            or not all(isinstance(item, str) and item.strip() for item in selectors)
        ):
            raise PipelineError(f"material.{field} must be a non-empty string array")
    material_id = material.get("material_id")
    if material_id is not None and (not isinstance(material_id, str) or not material_id.strip()):
        raise PipelineError("material.material_id must be a non-empty string")
    appearance = {
        "name": name,
        "rgba": list(rgba),
        "metallic": _material_number(material, "metallic", 0.0, 0.0, 1.0),
        "roughness": _material_number(material, "roughness", 0.5, 0.0, 1.0),
        "transmission": _material_number(material, "transmission", 0.0, 0.0, 1.0),
        "ior": _material_number(material, "ior", 1.45, 1.0, 3.0),
    }
    if material_id is not None:
        appearance["material_id"] = material_id.strip()
    return appearance


def apply_material_override(
    object_model: Any, *, target: str, material: Mapping[str, Any]
) -> tuple[str, ...]:
    appearance = _validate_material_override(material)
    patterns_value = material.get("surfaces")
    if patterns_value is None:
        part_patterns = material.get("parts", [target])
        if not isinstance(part_patterns, list) or not all(
            isinstance(item, str) and item for item in part_patterns
        ):
            raise PipelineError("material.parts must be a string array")
        patterns_value = list(part_selectors(part_patterns))
    if not isinstance(patterns_value, list) or not all(
        isinstance(item, str) and item for item in patterns_value
    ):
        raise PipelineError("material.surfaces must be a string array")
    rgba = tuple(appearance["rgba"])
    name = appearance["name"]
    replacement = Material(name=_safe_id(name, fallback="directed_material"), rgba=rgba)
    matched_surfaces: list[str] = []
    for part in object_model.parts:
        for visual_index, visual in enumerate(part.visuals):
            visual_name = str(visual.name or f"visual_{visual_index:03d}")
            if not matches_surface(
                patterns_value,
                part_name=part.name,
                visual_name=visual_name,
                visual=visual,
            ):
                continue
            visual.material = replacement
            matched_surfaces.append(surface_key(part.name, visual_name))
    if not matched_surfaces:
        available = ", ".join(
            surface_key(part.name, str(visual.name or f"visual_{index:03d}"))
            for part in object_model.parts
            for index, visual in enumerate(part.visuals)
        )
        raise PipelineError(
            f"Material target selectors {patterns_value!r} matched no surfaces; available: {available}"
        )
    matched_parts = part_names_from_surfaces(matched_surfaces)
    appearance.update({"parts": list(matched_parts), "surfaces": matched_surfaces})
    object_model.meta.setdefault("specific_editing_material_overrides", []).append(appearance)
    return tuple(matched_surfaces)


def _requested_config(spec: EditingSpec, variant: EditVariant | None = None) -> dict[str, Any]:
    values = dict(spec.base_config)
    if variant is not None:
        values.update(variant.overrides)
    return values


def _assert_resolved_value(variant: EditVariant, resolved: Mapping[str, Any]) -> None:
    if variant.kind == "material":
        return
    if variant.target not in resolved:
        raise PipelineError(f"Resolved config does not expose edited target {variant.target!r}")
    if resolved[variant.target] != variant.value:
        raise PipelineError(
            f"Edit {variant.target!r}={variant.value!r} resolved to "
            f"{resolved[variant.target]!r}; use an in-range value"
        )


def build_variant(spec: EditingSpec, variant: EditVariant, assets_root: Path) -> BuiltVariant:
    _validate_edit_target(spec, variant)
    registration = get_generator(spec.generator_id)
    requested = _requested_config(spec, variant)
    config = registration.make_config(requested, seed=spec.seed)
    resolved = _jsonable(registration.resolve(config))
    if not isinstance(resolved, dict):
        raise PipelineError("resolve_config() did not return a dataclass or mapping")
    _assert_resolved_value(variant, resolved)
    object_model = registration.build(config, assets=AssetContext(assets_root))
    object_model.meta["specific_editing_generator_id"] = spec.generator_id
    target_surfaces: tuple[str, ...]
    if variant.material_override is not None:
        material = dict(variant.material_override)
        if "surfaces" not in material and "parts" not in material:
            material["surfaces"] = list(
                registration.material_patterns.get(variant.target, (f"part:{variant.target}",))
            )
        target_surfaces = apply_material_override(
            object_model, target=variant.target, material=material
        )
    else:
        axis = registration.axis_for_target(variant.kind, variant.target)
        patterns = variant.highlight_parts or registration.target_patterns.get(axis.target, ())
        target_surfaces = matching_surface_keys(object_model, patterns)
    target_parts = part_names_from_surfaces(target_surfaces)
    return BuiltVariant(
        variant=variant,
        requested_config=requested,
        resolved_config=resolved,
        object_model=object_model,
        target_parts=target_parts,
        target_surfaces=target_surfaces,
    )


def validate_spec(path: str | Path) -> tuple[EditingSpec, dict[str, Any]]:
    spec = load_spec(path)
    registration = get_generator(spec.generator_id)
    base = registration.make_config(spec.base_config, seed=spec.seed)
    base_resolved = _jsonable(registration.resolve(base))
    for variant in spec.variants:
        _validate_edit_target(spec, variant)
        requested = _requested_config(spec, variant)
        resolved = _jsonable(
            registration.resolve(registration.make_config(requested, seed=spec.seed))
        )
        if not isinstance(resolved, dict):
            raise PipelineError("resolve_config() did not return a dataclass or mapping")
        _assert_resolved_value(variant, resolved)
        if variant.material_override is not None:
            _validate_material_override(variant.material_override)
    return spec, {
        "status": "valid",
        "name": spec.name,
        "generator": spec.generator_id,
        "base_resolved_config": base_resolved,
        "variant_count": len(spec.variants),
        "variants": [
            {
                "id": variant.variant_id,
                "label": variant.label,
                "kind": variant.kind,
                "target": variant.target,
                "value": variant.value,
            }
            for variant in spec.variants
        ],
        "render": {
            "backend": spec.renderer,
            "frame_scope": spec.frame_scope,
            "compact_comparison_kinds": spec.compact_comparison_kinds,
            "normalize_comparison_foreground": spec.normalize_comparison_foreground,
            "views": spec.views,
            "poses": spec.poses,
            "image_size": spec.image_size,
            "supersample": spec.supersample,
            "shadow_strength": spec.shadow_strength,
        },
    }


def _model_summary(model: Any) -> dict[str, Any]:
    moving = [
        joint
        for joint in model.articulations
        if str(getattr(joint.articulation_type, "value", joint.articulation_type)) != "fixed"
    ]
    return {
        "name": model.name,
        "part_count": len(model.parts),
        "parts": [part.name for part in model.parts],
        "moving_joint_count": len(moving),
        "moving_joints": [joint.name for joint in moving],
        "slot_choices": _jsonable(model.meta.get("slot_choices", ())),
    }


def _comparison_group_names(
    groups: Mapping[tuple[str, str], object],
) -> dict[tuple[str, str], str]:
    """Give each edit axis its own stable comparison directory.

    A generator can expose more than one axis with the same public kind.  Keep
    the first (legacy) directory name, then add numeric suffixes so a new axis
    cannot overwrite an earlier comparison sheet (for example ``count`` and
    ``count_1`` for two different count targets).
    """

    names: dict[tuple[str, str], str] = {}
    kinds: dict[str, list[tuple[str, str]]] = {}
    for kind, target in groups:
        kinds.setdefault(kind, []).append((kind, target))
    for kind, keys in kinds.items():
        # Target ordering is deterministic and keeps panel_segment_count in
        # the existing ``count`` directory before solar_array_module.
        for index, key in enumerate(sorted(keys, key=lambda item: item[1])):
            names[key] = kind if index == 0 else f"{kind}_{index}"
    return names


def run_pipeline(spec_path: str | Path, output_base: str | Path) -> PipelineResult:
    from specific_editing.render import (
        make_comparison_sheets,
        merge_frames,
        render_variant,
        shared_frame,
    )

    spec, _summary = validate_spec(spec_path)
    registration = get_generator(spec.generator_id)
    output_root = Path(output_base).expanduser().resolve() / _safe_id(spec.name, fallback="edit")
    output_root.mkdir(parents=True, exist_ok=True)
    _write_json(output_root / "edit_spec.json", spec.raw)
    _write_json(output_root / "generator_capabilities.json", registration.describe())

    variant_groups: dict[tuple[str, str], list[EditVariant]] = {}
    for variant in spec.variants:
        variant_groups.setdefault((variant.kind, variant.target), []).append(variant)
    comparison_group_names = _comparison_group_names(variant_groups)
    primary_group = next(iter(variant_groups))

    base_config = registration.make_config(spec.base_config, seed=spec.seed)
    base_probe = registration.build(base_config, assets=AssetContext(output_root / "base"))
    base_probe.meta["specific_editing_generator_id"] = spec.generator_id
    base_probe_frame = shared_frame(
        [base_probe],
        poses=spec.poses,
        front_axis=registration.front_axis,
        size=spec.image_size,
        padding=1.0,
    )
    del base_probe
    gc.collect()

    if spec.frame_scope == "global":
        global_model_frames = [base_probe_frame]
        grouped_model_frames: dict[tuple[str, str], list[Any]] = {}
    else:
        global_model_frames = []
        grouped_model_frames = {key: [base_probe_frame] for key in variant_groups}
    for variant in spec.variants:
        variant_root = output_root / "variants" / variant.variant_id
        built_probe = build_variant(spec, variant, variant_root)
        variant_frame = shared_frame(
            [built_probe.object_model],
            poses=spec.poses,
            front_axis=registration.front_axis,
            size=spec.image_size,
            padding=1.0,
        )
        if spec.frame_scope == "global":
            global_model_frames.append(variant_frame)
        else:
            grouped_model_frames[(variant.kind, variant.target)].append(variant_frame)
        del built_probe
        gc.collect()

    if spec.frame_scope == "global":
        global_frame = merge_frames(global_model_frames)
        comparison_frames = {key: global_frame for key in variant_groups}
    else:
        comparison_frames = {
            key: merge_frames(group_frames) for key, group_frames in grouped_model_frames.items()
        }
    base_render_frame = comparison_frames[primary_group]
    del global_model_frames, grouped_model_frames
    gc.collect()

    base_model = registration.build(base_config, assets=AssetContext(output_root / "base"))
    base_model.meta["specific_editing_generator_id"] = spec.generator_id
    base_exports = export_visual_assets(base_model, output_root / "base")
    base_images = render_variant(
        base_model,
        output_root / "base" / "renders",
        views=spec.views,
        poses=spec.poses,
        front_axis=registration.front_axis,
        size=spec.image_size,
        backend=spec.renderer,
        highlight_parts=(),
        frame=base_render_frame,
        supersample=spec.supersample,
        shadow_strength=spec.shadow_strength,
    )
    base_comparison_images = {primary_group: base_images}
    if spec.frame_scope == "edit_group":
        for group_key, group_frame in comparison_frames.items():
            if group_key == primary_group:
                continue
            group_name = comparison_group_names[group_key]
            base_comparison_images[group_key] = render_variant(
                base_model,
                output_root / "base" / "comparison_renders" / group_name,
                views=spec.views,
                poses=spec.poses,
                front_axis=registration.front_axis,
                size=spec.image_size,
                backend=spec.renderer,
                highlight_parts=(),
                frame=group_frame,
                supersample=spec.supersample,
                shadow_strength=spec.shadow_strength,
            )
    else:
        base_comparison_images.update(
            (group_key, base_images) for group_key in variant_groups if group_key != primary_group
        )
    base_summary = _model_summary(base_model)
    base_resolved_config = _jsonable(registration.resolve(base_config))
    del base_model
    gc.collect()

    variants_manifest: list[dict[str, Any]] = []
    all_images = list(base_images.values())
    if spec.frame_scope == "edit_group":
        for group_key, group_images in base_comparison_images.items():
            if group_key != primary_group:
                all_images.extend(group_images.values())
    comparison_inputs: dict[tuple[str, str], list[tuple[str, dict[str, Path]]]] = {}
    for variant in spec.variants:
        variant_root = output_root / "variants" / variant.variant_id
        built = build_variant(spec, variant, variant_root)
        exports = export_visual_assets(built.object_model, variant_root)
        highlighted = built.target_surfaces if variant.highlight_parts else ()
        images = render_variant(
            built.object_model,
            variant_root / "renders",
            views=spec.views,
            poses=spec.poses,
            front_axis=registration.front_axis,
            size=spec.image_size,
            backend=spec.renderer,
            highlight_parts=highlighted,
            frame=comparison_frames[(variant.kind, variant.target)],
            supersample=spec.supersample,
            shadow_strength=spec.shadow_strength,
        )
        all_images.extend(images.values())
        comparison_inputs.setdefault((variant.kind, variant.target), []).append(
            (variant.label, images)
        )
        metadata = {
            "schema_version": SCHEMA_VERSION,
            "pipeline_version": __version__,
            "variant": _jsonable(variant),
            "requested_config": built.requested_config,
            "resolved_config": built.resolved_config,
            "target_parts": built.target_parts,
            "target_surfaces": built.target_surfaces,
            "model": _model_summary(built.object_model),
            "exports": {key: str(path.relative_to(output_root)) for key, path in exports.items()},
            "renders": {key: str(path.relative_to(output_root)) for key, path in images.items()},
        }
        _write_json(variant_root / "edit_metadata.json", metadata)
        variants_manifest.append(metadata)
        del built
        gc.collect()

    sheets: dict[str, Path] = {}
    cell_width = min(spec.image_size[0], 1000)
    comparison_cell_size = (
        cell_width,
        max(1, round(spec.image_size[1] * cell_width / spec.image_size[0])),
    )
    comparison_groups: dict[str, dict[str, str]] = {}
    for (edit_kind, target), kind_variants in comparison_inputs.items():
        group_key = (edit_kind, target)
        group_name = comparison_group_names[group_key]
        kind_sheets = make_comparison_sheets(
            base_label="Base",
            base_images=base_comparison_images[group_key],
            variants=kind_variants,
            output_dir=output_root / "comparisons" / group_name,
            size=comparison_cell_size,
            columns=min(len(kind_variants) + 1, 5),
            padding=(
                _COMPACT_COMPARISON_PADDING
                if edit_kind in spec.compact_comparison_kinds
                else 14
            ),
            compact_foreground=edit_kind in spec.compact_comparison_kinds,
            normalize_foreground=(
                spec.normalize_comparison_foreground
                and edit_kind in spec.compact_comparison_kinds
            ),
        )
        comparison_groups[group_name] = {"kind": edit_kind, "target": target}
        sheets.update((f"{group_name}/{key}", path) for key, path in kind_sheets.items())
    all_images.extend(sheets.values())
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "pipeline_version": __version__,
        "name": spec.name,
        "generator": spec.generator_id,
        "purpose": "directed_3d_editing_visualization",
        "validation_level": "build_and_render_only",
        "render_contract": {
            "backend": spec.renderer,
            "engine": "cycles" if spec.renderer == "blender" else "software",
            "background_rgb": [255, 255, 255],
            "background_hex": "#FFFFFF",
            "shadow": (
                "cycles_shadow_catcher_ratio_softened" if spec.renderer == "blender" else "none"
            ),
            "shadow_strength": spec.shadow_strength if spec.renderer == "blender" else 0.0,
            "camera": (
                "shared_world_space_frame"
                if spec.frame_scope == "global"
                else "shared_world_space_frame_per_edit_group"
            ),
            "frame_scope": spec.frame_scope,
            "compact_comparison_kinds": list(spec.compact_comparison_kinds),
            "normalize_comparison_foreground": spec.normalize_comparison_foreground,
            "front_axis": registration.front_axis,
            "views": list(spec.views),
            "poses": list(spec.poses),
            "image_size": list(spec.image_size),
            "supersample": spec.supersample,
        },
        "pbr_theme": theme_receipt(spec.generator_id),
        "shared_frame": _jsonable(base_render_frame),
        "comparison_frames": {
            comparison_group_names[group_key]: _jsonable(group_frame)
            for group_key, group_frame in comparison_frames.items()
        },
        "base": {
            "config": spec.base_config,
            "resolved_config": base_resolved_config,
            "model": base_summary,
            "exports": {
                key: str(path.relative_to(output_root)) for key, path in base_exports.items()
            },
            "renders": {
                key: str(path.relative_to(output_root)) for key, path in base_images.items()
            },
            "comparison_renders": {
                comparison_group_names[group_key]: {
                    key: str(path.relative_to(output_root)) for key, path in images.items()
                }
                for group_key, images in base_comparison_images.items()
            },
        },
        "variants": variants_manifest,
        "comparison_groups": comparison_groups,
        "comparisons": {key: str(path.relative_to(output_root)) for key, path in sheets.items()},
    }
    manifest_path = output_root / "manifest.json"
    _write_json(manifest_path, manifest)
    return PipelineResult(
        output_root=output_root,
        manifest_path=manifest_path,
        variant_count=len(spec.variants),
        image_count=len(all_images),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, help="directed-edit JSON spec")
    parser.add_argument("--out", type=Path, help="output base directory")
    parser.add_argument("--dry-run", action="store_true", help="validate and print the edit plan")
    parser.add_argument("--list-generators", action="store_true")
    parser.add_argument("--describe-generator", metavar="GENERATOR_ID")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        if args.list_generators:
            for generator_id in list_generators():
                print(generator_id)
            return 0
        if args.describe_generator:
            print(json.dumps(get_generator(args.describe_generator).describe(), indent=2))
            return 0
        if args.spec is None:
            parser.error("--spec is required")
        if args.dry_run:
            _spec, summary = validate_spec(args.spec)
            print(json.dumps(_jsonable(summary), indent=2, sort_keys=True))
            return 0
        if args.out is None:
            parser.error("--out is required unless --dry-run is used")
        result = run_pipeline(args.spec, args.out)
    except (PipelineError, CatalogError, OSError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "status": "pass",
                "variant_count": result.variant_count,
                "image_count": result.image_count,
                "manifest": str(result.manifest_path),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "BuiltVariant",
    "EditingSpec",
    "EditVariant",
    "PipelineError",
    "PipelineResult",
    "apply_material_override",
    "build_variant",
    "load_spec",
    "main",
    "run_pipeline",
    "validate_spec",
]
