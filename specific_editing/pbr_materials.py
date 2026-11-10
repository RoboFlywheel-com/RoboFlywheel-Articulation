# SPDX-License-Identifier: Apache-2.0

"""Curated PBR themes for publication-facing directed-edit renders.

Generator palettes are intentionally not sampled here.  Paper comparisons
need one stable, aesthetically coherent material treatment so the requested
structural edit remains the only changing variable.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from articraft.appearance.unified_runtime import load_unified_material_library

OAK = "blenderkit:7e14e091-1d16-4cfd-b31e-a9d9a70abe54:76b0f36a-c66f-42ea-9a46-fa55cb75a3ad"
WALNUT = "blenderkit:c3f5ca2f-ba80-4b72-8f44-48d57e732fa3:df9aa2a3-5f5a-43cc-b5d4-1930beefcc2e"
PLYWOOD = "blenderkit:84696c02-08f5-4ad5-aa80-0b2dcb0883ce:4fe267f0-4fcd-419f-afed-4fd8ddf56485"
BRASS = "blenderkit:a20dfdf1-11e3-4787-98b4-7318060ecd80:209f75fd-8eda-41dd-bf69-22a44b784583"
BRUSHED_SILVER = (
    "blenderkit:c3ab2079-1dc6-4b6b-94d9-c56eb2339e91:3f4ded88-44d7-484c-8376-8a29ef92d331"
)
RED_PAINT = "blenderkit:940ca40e-25bd-4eab-8645-f11e37cf26a6:423ad6b6-81d2-46a0-a031-4bd57e10a13a"
WHITE_PAINT = "blenderkit:802fed00-3ed7-4fa1-8d0d-c4e264e59148:2c78ac26-ff2d-47ba-9b7b-a963b0b399e7"
SMOKED_GLASS = (
    "blenderkit:eadd253d-ad6f-4f92-b848-b3e486bb3975:c18a0d67-6cc9-4a4b-83c3-3a5cf188b0a9"
)
BLACKENED_METAL = (
    "blenderkit:f70e3613-d4d0-418f-894d-3d2e79556ab7:2d017450-f344-46dd-8f74-f1cbdaa2c2cc"
)
WARM_WHITE_PLASTIC = (
    "blenderkit:df65d4a6-6d67-4cda-818d-0698b42042b3:4da03638-efb2-4b35-94c5-1d693adf288d"
)
BEIGE_FABRIC = (
    "blenderkit:9e270774-6d38-4348-9238-2a46fa81bd21:715976df-cb40-4bca-90c9-f21cb93b8448"
)
CLEAR_GLASS = "blenderkit:d1d1886f-9bb1-4e68-a291-5f8fcae0d21b:2d2a524f-2409-49bc-acd0-bc8cce882cae"
SOLAR_CELL = "blenderkit:230aadd3-560d-4912-b273-7a4d17364750:6042c4c0-12d8-4d50-aa3b-66a017263c3d"
GREEN_FELT = "blenderkit:99fc871f-e793-4ad7-9ab2-fb5d08db4385:a64e78de-b78a-4176-89b5-4e139115a743"
BLACK_RUBBER = (
    "blenderkit:fd1bcf0d-f49a-43a6-9e41-37c07bcf012c:b1544876-1b35-4664-9f05-39f93bbac149"
)

_LIBRARY_POINTER = (
    Path(__file__).resolve().parent.parent / "pbr_material_library" / "unified" / "latest.json"
)
_RENDER_CHANNELS = frozenset(
    {"base_color", "metallic", "roughness", "normal", "alpha", "transmission", "ior"}
)

CURATED_THEMES: dict[str, dict[str, str]] = {
    "cabinet": {
        "wood": OAK,
        "panel": OAK,
        "dark": WALNUT,
        "metal": BRASS,
        "glass": CLEAR_GLASS,
        "accent": BEIGE_FABRIC,
    },
    "drawers": {
        "wood": WALNUT,
        "panel": WALNUT,
        "dark": BLACKENED_METAL,
        "metal": BRASS,
        "tray": PLYWOOD,
        "accent": BRASS,
    },
    "turbine": {
        "tower": WHITE_PAINT,
        "nacelle": WHITE_PAINT,
        "steel": BRUSHED_SILVER,
        "dark": BLACKENED_METAL,
        "blade": WARM_WHITE_PLASTIC,
        "warning": RED_PAINT,
    },
    "hinge": {
        "leaf": BRASS,
        "knuckle": BRASS,
        "pin": BRUSHED_SILVER,
        "accent": BLACKENED_METAL,
    },
    "fan": {
        "metal": BRASS,
        "dark": BLACKENED_METAL,
        "blade": WALNUT,
        "blade_grain": WALNUT,
        "black_screw_detail": BLACKENED_METAL,
    },
    "parabolic_dish_on_azimuth_elevation_mount": {
        "support": BRUSHED_SILVER,
        "support_dark": BLACKENED_METAL,
        "reflector": WHITE_PAINT,
        "reflector_inner": WHITE_PAINT,
        "rim": BRUSHED_SILVER,
        "feed": BLACKENED_METAL,
        "accent": BRASS,
        "rubber": BLACK_RUBBER,
    },
    "ferris_wheel": {
        "frame_main": WHITE_PAINT,
        "frame_accent": BRUSHED_SILVER,
        "platform_panels": BLACKENED_METAL,
        "cabin_body": RED_PAINT,
        "cabin_trim": WHITE_PAINT,
        "glass": CLEAR_GLASS,
    },
    "table_football": {
        "cabinet": WALNUT,
        "rim": BLACKENED_METAL,
        "pitch": GREEN_FELT,
        "mark": WHITE_PAINT,
        "leg": WALNUT,
        "chrome": BRUSHED_SILVER,
        "steel": BRUSHED_SILVER,
        "team_a": RED_PAINT,
        "team_b": WHITE_PAINT,
    },
    "playground_chair_swing_carousel": {
        "column": RED_PAINT,
        "metal": BRUSHED_SILVER,
        "dark": BLACKENED_METAL,
        "band": BRASS,
        "seat": OAK,
        "accent": BRASS,
    },
    "fence": {
        "frame": BLACKENED_METAL,
        "picket": RED_PAINT,
        "plate": BLACKENED_METAL,
        "coupler": BRUSHED_SILVER,
    },
    "playground_swing": {
        "frame_paint": RED_PAINT,
        "frame_brace": BLACKENED_METAL,
        "pivot_steel": BRUSHED_SILVER,
        "steel": BRUSHED_SILVER,
        "seat": BLACK_RUBBER,
        "rubber": BLACK_RUBBER,
        "dark": BLACKENED_METAL,
        "accent": BRASS,
        "rope": BEIGE_FABRIC,
        "wood": OAK,
    },
    "monitor_mount": {
        "base": BLACKENED_METAL,
        "link": BRUSHED_SILVER,
        "joint": BLACKENED_METAL,
        "accent": BRASS,
        "cover": WHITE_PAINT,
        "bezel": BLACKENED_METAL,
        "screen": SMOKED_GLASS,
    },
}


def _semantic_slot(generator_id: str, material_name: str) -> str | None:
    """Resolve a generator material name to one curated semantic slot."""

    name = material_name.strip().lower().replace("-", "_")
    if generator_id == "cabinet" and name.startswith("cabinet_"):
        return name.rsplit("_", 1)[-1]
    if generator_id == "drawers" and name.startswith("chest_"):
        return name.rsplit("_", 1)[-1]
    if generator_id == "turbine":
        return name if name in CURATED_THEMES["turbine"] else None
    if generator_id == "hinge":
        return name if name in CURATED_THEMES["hinge"] else None
    if generator_id == "fan":
        if name == "black_screw_detail":
            return name
        if "blade_grain" in name:
            return "blade_grain"
        if "blade" in name:
            return "blade"
        if "dark" in name:
            return "dark"
        if "metal" in name:
            return "metal"
    if generator_id == "parabolic_dish_on_azimuth_elevation_mount":
        if name.startswith("dish_"):
            name = name[5:]
        return name if name in CURATED_THEMES[generator_id] else None
    if generator_id == "ferris_wheel":
        for slot in CURATED_THEMES[generator_id]:
            if name.startswith(f"{slot}_"):
                return slot
    if generator_id == "table_football" and name.startswith("foosball_"):
        for slot in sorted(CURATED_THEMES[generator_id], key=len, reverse=True):
            if name.startswith(f"foosball_{slot}_"):
                return slot
    if generator_id == "playground_chair_swing_carousel":
        prefix, _, slot = name.partition("_")
        if prefix in {"base", "rotor", "seat"} and slot in CURATED_THEMES[generator_id]:
            return slot
    if generator_id == "fence" and name.startswith("fence_"):
        for slot in CURATED_THEMES[generator_id]:
            if name.startswith(f"fence_{slot}_"):
                return slot
    if generator_id == "playground_swing":
        if name in {"frame_paint", "frame_brace", "pivot_steel"}:
            return name
        fields = name.split("_", 2)
        if len(fields) == 3 and fields[0] == "swing" and fields[1].isdigit():
            return fields[2] if fields[2] in CURATED_THEMES[generator_id] else None
    if generator_id == "monitor_mount" and name.startswith("monitor_mount_"):
        slot = name.removeprefix("monitor_mount_")
        return slot if slot in CURATED_THEMES[generator_id] else None
    return None


def curated_material_id(generator_id: str, material_name: str) -> str | None:
    """Return the fixed paper material for one authored generator material."""

    theme = CURATED_THEMES.get(str(generator_id))
    if theme is None:
        return None
    slot = _semantic_slot(str(generator_id), str(material_name))
    return theme.get(slot) if slot is not None else None


def theme_receipt(generator_id: str) -> dict[str, Any]:
    """Return a stable JSON receipt for the curated theme used by a generator."""

    assignments = CURATED_THEMES.get(str(generator_id), {})
    return {
        "policy": "curated_fixed_pbr_theme",
        "generator": str(generator_id),
        "library_pointer": str(_LIBRARY_POINTER),
        "assignments": dict(assignments),
    }


@lru_cache(maxsize=1)
def _library() -> Any:
    return load_unified_material_library(_LIBRARY_POINTER)


@lru_cache(maxsize=32)
def blender_pbr_spec(material_id: str) -> dict[str, Any]:
    """Resolve one exact library material into a Blender-worker payload."""

    library = _library()
    material = library.materials_by_id.get(str(material_id))
    if material is None:
        raise ValueError(f"unified PBR library has no material {material_id!r}")
    mapping = material.appearance.get("mapping_contract", {})
    tile_size_m = mapping.get("tile_size_m")
    if not isinstance(tile_size_m, (int, float)) or isinstance(tile_size_m, bool):
        raise ValueError(f"PBR material {material_id!r} has no metric tile size")

    channels: dict[str, dict[str, Any]] = {}
    for channel_name, raw_channel in material.appearance.get("channels", {}).items():
        if channel_name not in _RENDER_CHANNELS or not isinstance(raw_channel, dict):
            continue
        channel = dict(raw_channel)
        if channel.get("kind") == "texture":
            source = library.texture_source(
                material,
                str(channel.get("path")),
                str(channel.get("sha256")),
            )
            channel["path"] = str(source)
            channel.pop("sha256", None)
            channel.pop("normal_convention", None)
        channels[str(channel_name)] = channel

    return {
        "material_id": material.material_id,
        "material_class_id": material.material_class_id,
        "tile_size_m": float(tile_size_m),
        "channels": channels,
    }


__all__ = [
    "BEIGE_FABRIC",
    "BLACK_RUBBER",
    "BLACKENED_METAL",
    "BRASS",
    "BRUSHED_SILVER",
    "CLEAR_GLASS",
    "CURATED_THEMES",
    "GREEN_FELT",
    "OAK",
    "PLYWOOD",
    "RED_PAINT",
    "SMOKED_GLASS",
    "SOLAR_CELL",
    "WALNUT",
    "WARM_WHITE_PLASTIC",
    "WHITE_PAINT",
    "blender_pbr_spec",
    "curated_material_id",
    "theme_receipt",
]
