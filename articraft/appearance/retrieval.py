# SPDX-License-Identifier: Apache-2.0

"""Zero-token deterministic retrieval from exact local material-class pools."""

from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence

from sdk import AppearanceOnlySpec

from .catalog import MaterialRecord

MATERIAL_CLASS_SELECTION_ALGORITHM = "local-random-choice/v1"
_MATERIAL_ASSET_TYPES = frozenset({"pbr_material", "optical_material"})
_OPTICAL_MATERIAL_CLASS_PARENTS = frozenset({"glass", "liquid"})
_ASSET_TYPES = _MATERIAL_ASSET_TYPES | {"appearance_only", "flat_color"}
_MATERIAL_CLASS_ID_RE = re.compile(r"^[a-z][a-z0-9_-]*(?:\.[a-z][a-z0-9_-]*)+$")


def _text(value: object, *, field: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise ValueError(f"appearance request {field} must be a non-empty string")
    return normalized


def _optional_text(value: object) -> str | None:
    normalized = str(value or "").strip()
    return normalized or None


def _rgba(value: object, *, field: str) -> tuple[float, float, float, float]:
    if not isinstance(value, (tuple, list)) or len(value) not in (3, 4):
        raise ValueError(f"appearance request {field} must contain three or four values")
    result = tuple(float(component) for component in value)
    if len(result) == 3:
        result = result + (1.0,)
    if any(
        not math.isfinite(component) or component < 0.0 or component > 1.0 for component in result
    ):
        raise ValueError(f"appearance request {field} values must be finite and in [0, 1]")
    return result  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class AppearanceRequest:
    surface_key: str
    asset_type: str
    material_class_id: str | None = None
    rgba: tuple[float, float, float, float] | None = None
    material_name: str | None = None
    texture: str | None = None
    selection_group_key: str | None = None
    appearance_only: AppearanceOnlySpec | None = None

    def __post_init__(self) -> None:
        surface_key = _text(self.surface_key, field="surface_key")
        appearance_only = self.appearance_only
        if appearance_only is not None and not isinstance(appearance_only, AppearanceOnlySpec):
            raise ValueError(
                "appearance request appearance_only must be an AppearanceOnlySpec or None"
            )
        asset_type = _text(self.asset_type, field="asset_type")
        if asset_type not in _ASSET_TYPES:
            raise ValueError(f"appearance request has unsupported asset_type {asset_type!r}")
        material_class_id = _optional_text(self.material_class_id)
        if (
            material_class_id is not None
            and _MATERIAL_CLASS_ID_RE.fullmatch(material_class_id) is None
        ):
            raise ValueError("appearance request material_class_id must be lowercase and dotted")
        if asset_type in _MATERIAL_ASSET_TYPES:
            if material_class_id is None:
                raise ValueError("material appearance request requires material_class_id")
        if asset_type not in _MATERIAL_ASSET_TYPES and material_class_id is not None:
            raise ValueError(f"{asset_type} appearance request cannot have material_class_id")
        if asset_type == "appearance_only" and appearance_only is None:
            raise ValueError("appearance_only request requires an AppearanceOnlySpec")
        if asset_type != "appearance_only" and appearance_only is not None:
            raise ValueError(f"{asset_type} appearance request cannot have appearance_only")

        rgba = None if self.rgba is None else _rgba(self.rgba, field="rgba")
        if asset_type == "flat_color" and rgba is None:
            raise ValueError("flat_color appearance request requires rgba")
        if asset_type not in {"appearance_only", "flat_color"} and rgba is not None:
            raise ValueError(f"{asset_type} appearance request cannot have rgba")

        material_name = _optional_text(self.material_name)
        texture = _optional_text(self.texture)
        if asset_type == "appearance_only":
            if material_name is None:
                raise ValueError("appearance_only request requires material_name")
            if rgba is None and texture is None:
                raise ValueError("appearance_only request requires rgba or texture")
        elif material_name is not None or texture is not None:
            raise ValueError(
                f"{asset_type} appearance request cannot have material_name or texture"
            )

        selection_group_key = _optional_text(self.selection_group_key)
        if asset_type in _MATERIAL_ASSET_TYPES:
            selection_group_key = selection_group_key or surface_key
        elif selection_group_key is not None:
            raise ValueError(f"{asset_type} appearance request cannot have selection_group_key")

        object.__setattr__(self, "surface_key", surface_key)
        object.__setattr__(self, "asset_type", asset_type)
        object.__setattr__(self, "material_class_id", material_class_id)
        object.__setattr__(self, "rgba", rgba)
        object.__setattr__(self, "material_name", material_name)
        object.__setattr__(self, "texture", texture)
        object.__setattr__(self, "selection_group_key", selection_group_key)


def _resolved_visual_material(
    object_model: object, visual: object, *, surface_key: str
) -> tuple[str, tuple[float, float, float, float] | None, str | None]:
    material = getattr(visual, "material", None)
    if isinstance(material, str):
        matches = [
            candidate
            for candidate in getattr(object_model, "materials", ())
            if getattr(candidate, "name", None) == material
        ]
        if len(matches) != 1:
            raise ValueError(
                f"appearance-only visual {surface_key!r} must resolve exactly one named material"
            )
        material = matches[0]
    material_name = _optional_text(getattr(material, "name", None))
    if material_name is None:
        raise ValueError(f"appearance-only visual {surface_key!r} requires an explicit material")
    rgba = getattr(material, "rgba", None)
    normalized_rgba = None if rgba is None else _rgba(rgba, field=f"visual {surface_key!r} rgba")
    texture = _optional_text(getattr(material, "texture", None))
    if normalized_rgba is None and texture is None:
        raise ValueError(
            f"appearance-only visual {surface_key!r} requires material rgba or texture"
        )
    return material_name, normalized_rgba, texture


def _visual_material_group(visual: object, *, surface_key: str) -> str:
    material = getattr(visual, "material", None)
    if isinstance(material, str):
        material_name = _optional_text(material)
    else:
        material_name = _optional_text(getattr(material, "name", None))
    if material_name is None:
        return f"surface:{surface_key}"
    return f"material:{material_name}"


def appearance_requests_from_model(
    object_model: object,
    *,
    require_all: bool = True,
) -> tuple[AppearanceRequest, ...]:
    """Derive runtime requests without generator-authored retrieval metadata.

    Physical visuals declare ``material_class_id`` and enter one exact local
    pool. Rendering-only visuals declare ``AppearanceOnlySpec`` and preserve
    their generator-authored material without entering a PBR pool.
    """

    parts = getattr(object_model, "parts", None)
    if parts is None:
        raise TypeError("appearance request source must expose object_model.parts")

    visual_rows: list[tuple[str, object]] = []
    surface_keys: set[str] = set()
    for part in parts:
        part_name = _text(getattr(part, "name", None), field="part.name")
        visuals = getattr(part, "visuals", None)
        if visuals is None:
            raise TypeError(f"appearance request part {part_name!r} must expose visuals")
        for index, visual in enumerate(visuals):
            visual_name = _text(
                getattr(visual, "name", None) or f"visual_{index}",
                field=f"part {part_name!r} visual name",
            )
            if "::" in part_name or "::" in visual_name:
                raise ValueError("part and visual names must not contain '::'")
            surface_key = f"{part_name}::{visual_name}"
            if surface_key in surface_keys:
                raise ValueError(f"duplicate visual surface key: {surface_key}")
            surface_keys.add(surface_key)
            visual_rows.append((surface_key, visual))

    requests: list[AppearanceRequest] = []
    for surface_key, visual in visual_rows:
        material_class_id = _optional_text(getattr(visual, "material_class_id", None))
        appearance_only = getattr(visual, "appearance_only", None)
        if appearance_only is not None and not isinstance(appearance_only, AppearanceOnlySpec):
            raise ValueError(
                f"visual {surface_key!r} appearance_only must be an AppearanceOnlySpec"
            )
        if material_class_id is not None and appearance_only is not None:
            raise ValueError(
                f"visual {surface_key!r} cannot combine material_class_id and appearance_only"
            )
        if material_class_id is not None:
            parent_category = material_class_id.split(".", 1)[0]
            requests.append(
                AppearanceRequest(
                    surface_key=surface_key,
                    asset_type=(
                        "optical_material"
                        if parent_category in _OPTICAL_MATERIAL_CLASS_PARENTS
                        else "pbr_material"
                    ),
                    material_class_id=material_class_id,
                    selection_group_key=_visual_material_group(
                        visual,
                        surface_key=surface_key,
                    ),
                )
            )
            continue
        if appearance_only is None:
            if require_all:
                raise ValueError(
                    f"visual {surface_key!r} must declare exactly one of "
                    "material_class_id or appearance_only"
                )
            continue
        material_name, rgba, texture = _resolved_visual_material(
            object_model,
            visual,
            surface_key=surface_key,
        )
        requests.append(
            AppearanceRequest(
                surface_key=surface_key,
                asset_type="appearance_only",
                rgba=rgba,
                material_name=material_name,
                texture=texture,
                appearance_only=appearance_only,
            )
        )

    return tuple(requests)


@dataclass(frozen=True, slots=True)
class ResolvedAppearance:
    request: AppearanceRequest
    material: MaterialRecord | None
    candidate_pool_count: int = 0
    candidate_pool_sha256: str | None = None
    candidate_pool_material_class_id: str | None = None
    draw_order: int | None = None
    selection_index: int | None = None


def resolve_appearances_from_pools(
    requests: Iterable[AppearanceRequest],
    pools: Mapping[str, Sequence[MaterialRecord]],
    pool_sha256: Mapping[str, str],
    *,
    slug: str,
    material_seed: int,
) -> tuple[ResolvedAppearance, ...]:
    """Use one seeded local RNG and one direct choice per exact-class group.

    ``slug`` remains an API compatibility field and is deliberately absent from
    the random seed. Pool and snapshot hashes are provenance only.
    """

    del slug
    ordered_requests = sorted(requests, key=lambda row: row.surface_key)
    material_groups: dict[tuple[str, str], AppearanceRequest] = {}
    for request in ordered_requests:
        if request.asset_type not in _MATERIAL_ASSET_TYPES:
            if request.material_class_id is not None:
                raise ValueError(
                    f"non-material request {request.surface_key!r} has material_class_id"
                )
            continue
        material_class_id = request.material_class_id
        if material_class_id is None:
            raise ValueError(f"material request {request.surface_key!r} requires material_class_id")
        group_key = request.selection_group_key or request.surface_key
        material_groups.setdefault((group_key, material_class_id), request)

    rng = random.Random(int(material_seed))
    selected_groups: dict[tuple[str, str], tuple[MaterialRecord, int, str, int, int]] = {}
    for draw_order, group_key in enumerate(sorted(material_groups)):
        _, material_class_id = group_key
        candidates = tuple(pools.get(material_class_id, ()))
        if not candidates:
            raise ValueError(f"formal material library has no pool {material_class_id!r}")
        if tuple(sorted(candidates, key=lambda row: row.material_id)) != candidates:
            raise ValueError(f"formal material pool {material_class_id!r} is not canonical")
        if len({record.material_id for record in candidates}) != len(candidates):
            raise ValueError(f"formal material pool {material_class_id!r} repeats material IDs")
        if any(record.category_slug != material_class_id.split(".", 1)[0] for record in candidates):
            raise ValueError(f"formal material pool {material_class_id!r} crosses parent category")
        published_pool_sha256 = pool_sha256.get(material_class_id)
        if not published_pool_sha256:
            raise ValueError(f"formal material pool {material_class_id!r} lacks a published SHA")
        chosen = rng.choice(candidates)
        selected_groups[group_key] = (
            chosen,
            len(candidates),
            published_pool_sha256,
            draw_order,
            candidates.index(chosen),
        )

    resolved: list[ResolvedAppearance] = []
    for request in ordered_requests:
        if request.asset_type not in _MATERIAL_ASSET_TYPES:
            resolved.append(ResolvedAppearance(request=request, material=None))
            continue
        material_class_id = request.material_class_id
        if material_class_id is None:  # guarded while building material_groups
            raise AssertionError("material request lost its class")
        group_key = (request.selection_group_key or request.surface_key, material_class_id)
        chosen, candidate_count, published_pool_sha256, draw_order, selection_index = (
            selected_groups[group_key]
        )
        resolved.append(
            ResolvedAppearance(
                request=request,
                material=chosen,
                candidate_pool_count=candidate_count,
                candidate_pool_sha256=published_pool_sha256,
                candidate_pool_material_class_id=material_class_id,
                draw_order=draw_order,
                selection_index=selection_index,
            )
        )

    return tuple(resolved)
