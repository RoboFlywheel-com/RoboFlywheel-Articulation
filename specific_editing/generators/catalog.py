# SPDX-License-Identifier: Apache-2.0

"""Catalog of template snapshots used by the specific-editing visualizer.

This module deliberately keeps the contract smaller than the controlled
morphology experiment registry.  A visual edit is described by a target part,
an upstream config field, and a direction in which a reviewer should read the
change.  No physics/material simulation contract is attached to an adapter.
"""

from __future__ import annotations

import dataclasses
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Mapping

from sdk import AssetSession, activate_asset_session


class CatalogError(ValueError):
    """Raised when a visual generator or edit field is not available."""


@dataclass(frozen=True, slots=True)
class AxisDescriptor:
    """A paper-facing edit axis exposed by one generator."""

    name: str
    kind: str
    target: str
    field: str
    values: tuple[Any, ...]
    direction: str
    description: str
    labels: Mapping[str, str] = dataclasses.field(default_factory=dict)

    def label_for(self, value: Any) -> str:
        key = json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
        return str(self.labels.get(key, value))


@dataclass(frozen=True, slots=True)
class GeneratorAdapter:
    """Runtime adapter for one local source-template snapshot."""

    name: str
    source_filename: str
    source_template: str
    config_class: str
    build_function: str
    resolve_function: str
    seed_function: str
    axes: tuple[AxisDescriptor, ...]
    target_patterns: Mapping[str, tuple[str, ...]]
    material_patterns: Mapping[str, tuple[str, ...]]
    display_name: str
    front_axis: str

    @property
    def source_path(self) -> Path:
        return Path(__file__).resolve().parent / "source" / self.source_filename

    @property
    def source_sha256(self) -> str:
        return hashlib.sha256(self.source_path.read_bytes()).hexdigest()

    def module(self) -> ModuleType:
        """Load the snapshot by path, avoiding imports from production templates."""

        cached = _MODULE_CACHE.get(self.name)
        if cached is not None:
            return cached
        if not self.source_path.is_file():
            raise CatalogError(f"Missing generator snapshot: {self.source_path}")
        module_name = f"specific_editing_snapshot_{self.name}"
        spec = importlib.util.spec_from_file_location(module_name, self.source_path)
        if spec is None or spec.loader is None:
            raise CatalogError(f"Cannot load generator snapshot: {self.source_path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        _MODULE_CACHE[self.name] = module
        return module

    def _config_type(self) -> type:
        config_type = getattr(self.module(), self.config_class, None)
        if not isinstance(config_type, type) or not dataclasses.is_dataclass(config_type):
            raise CatalogError(
                f"{self.name} snapshot does not expose dataclass {self.config_class}"
            )
        return config_type

    def _base_values(self, seed: int | None) -> dict[str, Any]:
        module = self.module()
        if seed is None:
            config = self._config_type()()
        else:
            factory = getattr(module, self.seed_function, None)
            if not callable(factory):
                raise CatalogError(f"{self.name} snapshot lacks {self.seed_function}()")
            config = factory(int(seed))
        return dataclasses.asdict(config)

    @staticmethod
    def _coerce_value(value: Any, current: Any, field_name: str) -> Any:
        """Normalize JSON arrays for tuple/dict fields used by source templates."""

        if field_name == "accessory_modules" and isinstance(value, list):
            return tuple(value)
        if isinstance(current, tuple) and isinstance(value, list):
            return tuple(value)
        if isinstance(current, dict) and isinstance(value, dict):
            converted: dict[str, Any] = {}
            for key, item in value.items():
                if isinstance(item, list):
                    converted[str(key)] = tuple(item)
                else:
                    converted[str(key)] = item
            return converted
        return value

    def make_config(
        self, overrides: Mapping[str, Any] | None = None, *, seed: int | None = None
    ) -> Any:
        """Create a source config from a seed plus explicit visual overrides."""

        values = self._base_values(seed)
        fields = {field.name for field in dataclasses.fields(self._config_type())}
        overrides = dict(overrides or {})
        unknown = sorted(set(overrides) - fields)
        if unknown:
            raise CatalogError(f"Unknown config field(s) for {self.name}: {', '.join(unknown)}")
        for key, value in overrides.items():
            values[key] = self._coerce_value(value, values.get(key), key)
        try:
            return self._config_type()(**values)
        except TypeError as exc:
            raise CatalogError(f"Invalid config for {self.name}: {exc}") from exc

    def resolve(self, config: Any) -> Any:
        resolver = getattr(self.module(), self.resolve_function, None)
        if not callable(resolver):
            raise CatalogError(f"{self.name} snapshot lacks {self.resolve_function}()")
        return resolver(config)

    def build(self, config: Any, *, assets: Any) -> Any:
        builder = getattr(self.module(), self.build_function, None)
        if not callable(builder):
            raise CatalogError(f"{self.name} snapshot lacks {self.build_function}()")

        def invoke() -> Any:
            try:
                return builder(config, assets=assets)
            except TypeError as exc:
                # A few older templates do not expose the optional keyword.
                if "assets" not in str(exc):
                    raise
                return builder(config)

        if assets is None:
            return invoke()
        asset_root = Path(getattr(assets, "asset_root", assets))
        mesh_subdir = str(getattr(assets, "mesh_subdir", "assets/meshes"))
        with activate_asset_session(AssetSession(asset_root, mesh_subdir=mesh_subdir)):
            return invoke()

    def source_test(self, model: Any, config: Any) -> Any:
        function = getattr(self.module(), self._test_function_name(), None)
        if not callable(function):
            return None
        return function(model, config)

    def _test_function_name(self) -> str:
        names = [
            name
            for name in dir(self.module())
            if name.startswith("run_") and name.endswith("_tests")
        ]
        return names[0] if len(names) == 1 else ""

    def describe(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "front_axis": self.front_axis,
            "material_targets": {
                name: list(patterns) for name, patterns in self.material_patterns.items()
            },
            "source_snapshot": f"specific_editing/generators/source/{self.source_filename}",
            "source_template": self.source_template,
            "source_sha256": self.source_sha256,
            "axes": [
                {
                    "name": axis.name,
                    "kind": axis.kind,
                    "target": axis.target,
                    "field": axis.field,
                    "values": list(axis.values),
                    "direction": axis.direction,
                    "description": axis.description,
                    "labels": dict(axis.labels),
                }
                for axis in self.axes
            ],
        }

    def axis(self, name: str) -> AxisDescriptor:
        for axis in self.axes:
            if axis.name == name or axis.kind == name or axis.field == name:
                return axis
        choices = ", ".join(axis.name for axis in self.axes)
        raise CatalogError(f"Unknown edit axis {name!r} for {self.name}; choose from: {choices}")

    def axis_for_target(self, kind: str, target: str) -> AxisDescriptor:
        """Resolve an axis when a generator exposes multiple fields per kind."""

        candidates = tuple(
            axis for axis in self.axes if axis.kind == str(kind) or axis.name == str(kind)
        )
        for axis in candidates:
            if axis.field == str(target) or axis.target == str(target):
                return axis
        choices = ", ".join(axis.field for axis in candidates)
        raise CatalogError(
            f"Unknown {kind!r} target {target!r} for {self.name}; choose from: {choices}"
        )


def _labels(values: list[Any], labels: list[str]) -> dict[str, str]:
    return {
        json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")): label
        for value, label in zip(values, labels, strict=True)
    }


def _axis(
    name: str,
    kind: str,
    target: str,
    field: str,
    values: list[Any],
    direction: str,
    description: str,
    labels: list[str] | None = None,
) -> AxisDescriptor:
    return AxisDescriptor(
        name=name,
        kind=kind,
        target=target,
        field=field,
        values=tuple(values),
        direction=direction,
        description=description,
        labels=_labels(values, labels) if labels else {},
    )


_MATERIAL_EXAMPLES = [
    {
        "name": "walnut veneer",
        "rgba": [0.29, 0.12, 0.055, 1.0],
        "metallic": 0.0,
        "roughness": 0.42,
    },
    {
        "name": "brushed aluminum",
        "rgba": [0.63, 0.67, 0.71, 1.0],
        "metallic": 0.86,
        "roughness": 0.24,
    },
]


_HINGE_AXES = (
    _axis(
        "component",
        "component",
        "hinge_line",
        "hinge_line_style",
        [
            "interleaved_knuckles_pin_in_leaf",
            "separate_pin_part",
            "barrel_with_collars",
        ],
        "hinge_axis",
        "Replace the hinge-line module while keeping both leaves fixed.",
    ),
    _axis(
        "repetition",
        "count",
        "hinge_line",
        "knuckle_count",
        [3, 5, 7],
        "hinge_axis",
        "Change the number of visible knuckle bands along the hinge pin.",
    ),
    _axis(
        "material",
        "material",
        "hinge_leaves",
        "material_override",
        _MATERIAL_EXAMPLES,
        "surface",
        "Replace the selected hinge surfaces without changing topology.",
    ),
    _axis(
        "size",
        "size",
        "hinge_leaves",
        "leaf_height",
        [0.07, 0.10, 0.14],
        "z",
        "Adjust the hinge leaf height along the pin direction.",
        ["70 mm", "100 mm", "140 mm"],
    ),
)

_CABINET_AXES = (
    _axis(
        "component",
        "component",
        "door",
        "door_kind",
        ["flush_slab", "raised_panel", "framed_cane", "glazed_curtain"],
        "front",
        "Replace the selected door face treatment.",
    ),
    _axis(
        "repetition",
        "count",
        "door",
        "door_count",
        [1, 2, 3, 4],
        "x",
        "Change the number of side-hinged door leaves.",
        ["1 door", "2 doors", "3 doors", "4 doors"],
    ),
    _axis(
        "material",
        "material",
        "door",
        "material_override",
        _MATERIAL_EXAMPLES,
        "surface",
        "Replace only the selected door finish while holding structure fixed.",
    ),
    _axis(
        "size",
        "size",
        "carcass",
        "carcass_width_m",
        [0.72, 1.00, 1.30],
        "x",
        "Resize the host width; dependent door geometry follows the opening.",
        ["0.72 m", "1.00 m", "1.30 m"],
    ),
)

_DRAWER_AXES = (
    _axis(
        "component",
        "component",
        "drawer_front",
        "drawer_front",
        ["flat_panel", "framed_cane", "gothic_arch", "applique_moulded"],
        "front",
        "Replace the front module on every drawer.",
    ),
    _axis(
        "repetition",
        "count",
        "drawer",
        "drawer_count",
        [2, 3, 4, 5, 6],
        "z",
        "Change the number of pull-out drawer instances.",
        ["2 drawers", "3 drawers", "4 drawers", "5 drawers", "6 drawers"],
    ),
    _axis(
        "material",
        "material",
        "drawer_front",
        "material_override",
        _MATERIAL_EXAMPLES,
        "surface",
        "Replace only the drawer-front finish.",
    ),
    _axis(
        "size",
        "size",
        "carcass",
        "carcass_width_m",
        [0.70, 1.00, 1.30],
        "x",
        "Resize the host width and recompute drawer clearances.",
        ["0.70 m", "1.00 m", "1.30 m"],
    ),
)

_FAN_AXES = (
    _axis(
        "component",
        "component",
        "blade",
        "blade_shape",
        ["straight_plank", "tapered_paddle", "rounded_airfoil"],
        "radial",
        "Replace the repeated blade profile around the rotor.",
    ),
    _axis(
        "repetition",
        "count",
        "blade",
        "blade_count",
        [3, 4, 5, 6],
        "radial",
        "Change the number of repeated blades around the hub.",
        ["3 blades", "4 blades", "5 blades", "6 blades"],
    ),
    _axis(
        "material",
        "material",
        "blade",
        "material_override",
        _MATERIAL_EXAMPLES,
        "surface",
        "Replace only the repeated blade surfaces.",
    ),
    _axis(
        "size",
        "size",
        "blade",
        "blade_span",
        [0.60, 0.80, 1.00],
        "radial",
        "Adjust blade reach from the hub.",
        ["0.60 m", "0.80 m", "1.00 m"],
    ),
)

_TURBINE_AXES = (
    _axis(
        "component",
        "component",
        "rotor",
        "rotor_module",
        ["monolithic_rotor", "fixed_socket_blades", "pitching_blades"],
        "rotor_axis",
        "Replace the rotor assembly module.",
    ),
    _axis(
        "repetition",
        "count",
        "blade",
        "blade_count",
        [2, 3, 4, 5],
        "rotor_axis",
        "Change the repeated rotor blade count.",
        ["2 blades", "3 blades", "4 blades", "5 blades"],
    ),
    _axis(
        "material",
        "material",
        "blade",
        "material_override",
        _MATERIAL_EXAMPLES,
        "surface",
        "Replace only the rotor blade shells.",
    ),
    _axis(
        "size",
        "size",
        "blade",
        "blade_span",
        [0.30, 0.45, 0.60],
        "radial",
        "Adjust rotor blade span.",
        ["0.30 m", "0.45 m", "0.60 m"],
    ),
)

_PARABOLIC_DISH_MOUNT_AXES = (
    _axis(
        "component",
        "component",
        "dish_reflector",
        "reflector_style",
        ["lathe_feed", "portable_ribbed", "cadquery_spoked"],
        "reflector_face",
        "Replace the authored reflector module while keeping the azimuth/elevation mount fixed.",
        ["smooth lathe", "portable ribbed", "spoked reflector"],
    ),
    _axis(
        "repetition",
        "count",
        "support_legs",
        "support_leg_count",
        [3, 4],
        "radial",
        "Change the number of splayed support legs on the tripod mount.",
        ["3 support legs", "4 support legs"],
    ),
    _axis(
        "repetition_feed",
        "count",
        "feed_struts",
        "feed_strut_count",
        [2, 3, 4],
        "radial",
        "Change the number of converging feed-support struts in front of the dish.",
        ["2 feed struts", "3 feed struts", "4 feed struts"],
    ),
    _axis(
        "material",
        "material",
        "reflector_surface",
        "material_override",
        [
            {
                "name": "warm white reflector",
                "rgba": [0.88, 0.88, 0.84, 1.0],
                "metallic": 0.18,
                "roughness": 0.28,
            },
            {
                "name": "brushed silver reflector",
                "rgba": [0.63, 0.67, 0.71, 1.0],
                "metallic": 0.86,
                "roughness": 0.24,
            },
            {
                "name": "deep blue reflector",
                "rgba": [0.055, 0.11, 0.22, 1.0],
                "metallic": 0.72,
                "roughness": 0.26,
            },
        ],
        "surface",
        "Replace only the concave reflector surface while preserving the mount and feed hardware.",
    ),
    _axis(
        "size",
        "size",
        "dish_reflector",
        "dish_radius",
        [0.50, 0.62, 0.78],
        "radial",
        "Adjust the dish radius while holding the tripod and feed count fixed.",
        ["0.50 m radius", "0.62 m radius", "0.78 m radius"],
    ),
)

_FERRIS_WHEEL_AXES = (
    _axis(
        "component",
        "component",
        "gondola",
        "gondola_style",
        ["box_cabin", "open_basket", "glass_capsule", "bucket_seat", "rounded_pod"],
        "wheel_rim",
        "Replace every repeated passenger gondola with another authored module.",
        ["box cabin", "open basket", "glass capsule", "bucket seat", "rounded pod"],
    ),
    _axis(
        "repetition",
        "count",
        "gondola",
        "num_gondolas",
        [8, 12, 16, 20],
        "wheel_rim",
        "Change the number of gondolas distributed around the wheel.",
        ["8 gondolas", "12 gondolas", "16 gondolas", "20 gondolas"],
    ),
    _axis(
        "material",
        "material",
        "gondola_body",
        "material_override",
        _MATERIAL_EXAMPLES,
        "surface",
        "Replace only the gondola body finish while preserving glazing and trim.",
    ),
    _axis(
        "size",
        "size",
        "wheel",
        "rim_radius",
        [0.70, 0.98, 1.28],
        "radial",
        "Adjust the wheel radius and recompute the supporting frame and axle height.",
        ["0.70 m radius", "0.98 m radius", "1.28 m radius"],
    ),
)

_TABLE_FOOTBALL_AXES = (
    _axis(
        "component",
        "component",
        "support",
        "leg_form",
        ["splayed_legs_4", "side_panels_full_height", "cross_x_trestles", "tubular_legs_4"],
        "under_cabinet",
        "Replace the complete under-table support module.",
        ["splayed legs", "full-height panels", "cross trestles", "tubular legs"],
    ),
    _axis(
        "repetition",
        "count",
        "player_rods",
        "rod_count",
        [6, 8, 10],
        "table_length",
        "Change the number of articulated player-rod assemblies.",
        ["6 rods", "8 rods", "10 rods"],
    ),
    _axis(
        "material",
        "material",
        "pitch",
        "material_override",
        _MATERIAL_EXAMPLES,
        "surface",
        "Replace only the playing-pitch finish and keep its markings unchanged.",
    ),
    _axis(
        "size",
        "size",
        "cabinet",
        "cabinet_length_scale",
        [0.92, 1.0, 1.10],
        "table_length",
        "Resize the cabinet length and recompute rod spacing and player clearance.",
        ["92% length", "100% length", "110% length"],
    ),
)

_CHAIR_SWING_CAROUSEL_AXES = (
    _axis(
        "component",
        "component",
        "chairs",
        "seat_type_module",
        ["flat_platform_seat", "slatted_bucket_rail", "deep_bucket_seat"],
        "radial",
        "Replace every hanging chair with another authored seat module.",
        ["platform chairs", "slatted chairs", "deep bucket chairs"],
    ),
    _axis(
        "repetition",
        "count",
        "chairs",
        "seat_count",
        [2, 4, 6, 8],
        "radial",
        "Change the number of chair stations around the rotor.",
        ["2 chairs", "4 chairs", "6 chairs", "8 chairs"],
    ),
    _axis(
        "material",
        "material",
        "seat_surfaces",
        "material_override",
        _MATERIAL_EXAMPLES,
        "surface",
        "Replace only the sitting surfaces while retaining hangers and safety rails.",
    ),
    _axis(
        "size",
        "size",
        "carousel_radius",
        "seat_radius_scale",
        [0.85, 1.0, 1.20],
        "radial",
        "Adjust the chair-ring radius while keeping the seat count fixed.",
        ["85% radius", "100% radius", "120% radius"],
    ),
)

_FENCE_AXES = (
    _axis(
        "component",
        "component",
        "panel_infill",
        "panel_style",
        ["picket_tubular", "mesh_infill", "solid_half_panel"],
        "panel_face",
        "Replace the infill module in every articulated fence panel.",
        ["tubular pickets", "welded mesh", "solid half panel"],
    ),
    _axis(
        "repetition",
        "count",
        "panels",
        "panel_count",
        [2, 3, 4, 10],
        "chain",
        "Change the number of fence panels in the articulated cascade.",
        ["2 panels", "3 panels", "4 panels", "10 panels"],
    ),
    _axis(
        "material",
        "material",
        "panel_infill",
        "material_override",
        _MATERIAL_EXAMPLES,
        "surface",
        "Replace only the panel infill finish while keeping frames and hinges fixed.",
    ),
    _axis(
        "size",
        "size",
        "panels",
        "panel_len_scale",
        [0.90, 1.0, 1.12],
        "panel_length",
        "Adjust every panel length while preserving the hinge chain.",
        ["90% panel length", "100% panel length", "112% panel length"],
    ),
)

_PLAYGROUND_SWING_AXES = (
    _axis(
        "component",
        "component",
        "seat",
        "seat_type",
        ["rubber_belt_seat", "plank_seat", "tire_seat"],
        "front",
        "Replace every swing seat while retaining the frame and suspension.",
        ["rubber belt", "plank seat", "tire seat"],
    ),
    _axis(
        "repetition",
        "count",
        "swing",
        "swing_count",
        [1, 2, 3, 4],
        "crossbeam",
        "Change the number of independently articulated swings.",
        ["1 swing", "2 swings", "3 swings", "4 swings"],
    ),
    _axis(
        "material",
        "material",
        "seat_surface",
        "material_override",
        _MATERIAL_EXAMPLES,
        "surface",
        "Replace only the seat surfaces and preserve suspension hardware.",
    ),
    _axis(
        "size",
        "size",
        "frame",
        "frame_scale",
        [0.92, 1.0, 1.10],
        "uniform",
        "Scale the playground frame and all dependent suspension geometry.",
        ["92% frame", "100% frame", "110% frame"],
    ),
)

_MONITOR_MOUNT_AXES = (
    _axis(
        "component",
        "component",
        "wall_mount",
        "wall_style",
        ["wall_plate_lugs", "wall_plate_compact", "wall_plate_long"],
        "wall",
        "Replace the grounded wall-mount module while keeping the arm chain fixed.",
        ["lugged wall plate", "compact wall plate", "long wall plate"],
    ),
    _axis(
        "repetition",
        "count",
        "arm_chain",
        "arm_segment_count",
        [2, 5, 20],
        "serial_chain",
        "Change the number of indexed articulated links between the wall mount and display head.",
        ["2 arm segments", "5 arm segments", "20 arm segments"],
    ),
    _axis(
        "material",
        "material",
        "arm_links",
        "material_override",
        _MATERIAL_EXAMPLES,
        "surface",
        "Replace only the repeated arm-link finish while preserving joints and covers.",
    ),
    _axis(
        "size",
        "size",
        "arm_chain",
        "arm_span",
        [0.86, 1.10, 1.34],
        "reach",
        "Adjust the arm span and recompute every repeated link and joint origin.",
        ["0.86 m nominal span", "1.10 m nominal span", "1.34 m nominal span"],
    ),
)


_REGISTRY: dict[str, GeneratorAdapter] = {
    "hinge": GeneratorAdapter(
        name="hinge",
        source_filename="single_revolute_hinge.py",
        source_template="agent/templates/single_revolute_hinge.py",
        config_class="SingleRevoluteHingeConfig",
        build_function="build_single_revolute_hinge",
        resolve_function="resolve_config",
        seed_function="config_from_seed",
        axes=_HINGE_AXES,
        target_patterns={
            "moving_half": ("part:moving_half",),
            "hinge_line": ("visual:*knuckle*", "visual:pin_*", "visual:collar_*"),
            "hinge_leaves": ("visual:*leaf*",),
            "all_surfaces": ("surface:*",),
        },
        material_patterns={
            "moving_half": ("part:moving_half",),
            "hinge_line": ("visual:*knuckle*", "visual:pin_*", "visual:collar_*"),
            "hinge_leaves": ("visual:*leaf*",),
            "all_surfaces": ("surface:*",),
        },
        display_name="Single revolute hinge",
        front_axis="+y",
    ),
    "cabinet": GeneratorAdapter(
        name="cabinet",
        source_filename="cabinet_doors.py",
        source_template="agent/templates/pictureX_0611_Cabinet_with_doors.py",
        config_class="Config",
        build_function="build_pictureX_0611_Cabinet_with_doors",
        resolve_function="resolve_config",
        seed_function="config_from_seed",
        axes=_CABINET_AXES,
        target_patterns={
            "door": ("part:*door_leaf*",),
            "carcass": ("part:*carcass*",),
            "all_surfaces": ("surface:*",),
        },
        material_patterns={
            "door": (
                "surface:*door_leaf*/*door_slab*",
                "surface:*door_leaf*/*panel_slab*",
                "surface:*door_leaf*/*raise_*",
                "surface:*door_leaf*/*outer_stile*",
                "surface:*door_leaf*/*inner_stile*",
                "surface:*door_leaf*/*top_rail*",
                "surface:*door_leaf*/*bottom_rail*",
                "surface:*door_leaf*/*cane_*",
                "surface:*door_leaf*/*glass_panel*",
                "surface:*door_leaf*/*curtain_*",
            ),
            "carcass": ("part:*carcass*",),
            "all_surfaces": ("surface:*",),
        },
        display_name="Side-hinged cabinet",
        front_axis="-y",
    ),
    "drawers": GeneratorAdapter(
        name="drawers",
        source_filename="drawer_cabinet.py",
        source_template="agent/templates/drawer_cabinet_with_sliding_drawers.py",
        config_class="Config",
        build_function="build_drawer_cabinet_with_sliding_drawers",
        resolve_function="resolve_config",
        seed_function="config_from_seed",
        axes=_DRAWER_AXES,
        target_patterns={
            "drawer_front": (
                "visual:*__drawer_front",
                "visual:*__cane_*",
                "visual:*__gothic_*",
                "visual:*__centre_crest",
                "visual:*__corner_scroll*",
            ),
            "drawer": ("part:drawer_front__*__drawer_*",),
            "carcass": ("part:carcass",),
            "all_surfaces": ("surface:*",),
        },
        material_patterns={
            "drawer_front": ("visual:drawer_front__*__drawer_front",),
            "drawer": ("part:drawer_front__*__drawer_*",),
            "carcass": ("part:carcass",),
            "all_surfaces": ("surface:*",),
        },
        display_name="Sliding-drawer cabinet",
        front_axis="-y",
    ),
    "fan": GeneratorAdapter(
        name="fan",
        source_filename="ceiling_fan.py",
        source_template="agent/templates/ceiling_fan.py",
        config_class="CeilingFanConfig",
        build_function="build_ceiling_fan",
        resolve_function="resolve_config",
        seed_function="config_from_seed",
        axes=_FAN_AXES,
        target_patterns={
            "blade": ("visual:blade_*",),
            "all_surfaces": ("surface:*",),
        },
        material_patterns={
            "blade": ("visual:blade_surface_*",),
            "all_surfaces": ("surface:*",),
        },
        display_name="Ceiling fan",
        front_axis="+y",
    ),
    "turbine": GeneratorAdapter(
        name="turbine",
        source_filename="wind_turbine.py",
        source_template="agent/templates/wind_turbine.py",
        config_class="WindTurbineConfig",
        build_function="build_wind_turbine",
        resolve_function="resolve_config",
        seed_function="config_from_seed",
        axes=_TURBINE_AXES,
        target_patterns={
            "rotor": ("part:rotor", "part:blade_*"),
            "blade": ("part:blade_*", "visual:blade_shell_*"),
            "all_surfaces": ("surface:*",),
        },
        material_patterns={
            "rotor": ("part:rotor",),
            "blade": ("visual:blade_shell", "visual:blade_shell_*"),
            "all_surfaces": ("surface:*",),
        },
        display_name="Wind turbine",
        front_axis="+x",
    ),
    "parabolic_dish_on_azimuth_elevation_mount": GeneratorAdapter(
        name="parabolic_dish_on_azimuth_elevation_mount",
        source_filename="parabolic_dish_on_azimuth_elevation_mount.py",
        source_template="agent/templates/parabolic_dish_on_azimuth_elevation_mount.py",
        config_class="ParabolicDishConfig",
        build_function="build_parabolic_dish",
        resolve_function="resolve_config",
        seed_function="config_from_seed",
        axes=_PARABOLIC_DISH_MOUNT_AXES,
        target_patterns={
            "dish_reflector": (
                "part:dish_assembly",
            ),
            "support_legs": (
                "visual:tripod_splayed_leg_*",
                "visual:tripod_rubber_foot_*",
                "visual:tripod_lower_foot_tie_*",
            ),
            "feed_struts": ("visual:feed_strut_*",),
            "reflector_surface": ("visual:concave_parabolic_reflector_shell",),
            "all_surfaces": ("surface:*",),
        },
        material_patterns={
            "reflector_surface": (
                "surface:dish_assembly/concave_parabolic_reflector_shell",
            ),
            "dish_reflector": ("part:dish_assembly",),
            "all_surfaces": ("surface:*",),
        },
        display_name="Parabolic dish on azimuth/elevation mount",
        front_axis="-y",
    ),
    "ferris_wheel": GeneratorAdapter(
        name="ferris_wheel",
        source_filename="ferris_wheel.py",
        source_template="agent/templates/ferris_wheel.py",
        config_class="FerrisWheelConfig",
        build_function="build_ferris_wheel",
        resolve_function="resolve_config",
        seed_function="config_from_seed",
        axes=_FERRIS_WHEEL_AXES,
        target_patterns={
            "gondola": ("part:gondola_*",),
            "wheel": ("part:wheel", "part:support_frame"),
            "all_surfaces": ("surface:*",),
        },
        material_patterns={
            "gondola_body": ("surface:gondola_*/cabin_body",),
            "gondola": ("part:gondola_*",),
            "all_surfaces": ("surface:*",),
        },
        display_name="Ferris wheel",
        front_axis="+x",
    ),
    "table_football": GeneratorAdapter(
        name="table_football",
        source_filename="Sports_Table_football.py",
        source_template="agent/templates/Sports_Table_football.py",
        config_class="FoosballConfig",
        build_function="build_foosball_table",
        resolve_function="resolve_config",
        seed_function="config_from_seed",
        axes=_TABLE_FOOTBALL_AXES,
        target_patterns={
            "support": (
                "visual:leg_*",
                "visual:side_panel_*",
                "visual:trestle_*",
                "visual:tubular_leg_*",
            ),
            "player_rods": ("part:rod_*",),
            "cabinet": ("part:cabinet",),
            "all_surfaces": ("surface:*",),
        },
        material_patterns={
            "pitch": ("surface:cabinet/pitch",),
            "cabinet": ("surface:cabinet/cabinet_base", "visual:*panel*"),
            "all_surfaces": ("surface:*",),
        },
        display_name="Table football",
        front_axis="+y",
    ),
    "playground_chair_swing_carousel": GeneratorAdapter(
        name="playground_chair_swing_carousel",
        source_filename="Playground_playground_chair_swing_carousel.py",
        source_template="agent/templates/Playground_playground_chair_swing_carousel.py",
        config_class="PlaygroundChairSwingCarouselConfig",
        build_function="build_playground_chair_swing_carousel",
        resolve_function="resolve_config",
        seed_function="config_from_seed",
        axes=_CHAIR_SWING_CAROUSEL_AXES,
        target_patterns={
            "chairs": ("part:seat_*",),
            "carousel_radius": ("part:rotor", "part:seat_*"),
            "all_surfaces": ("surface:*",),
        },
        material_patterns={
            "seat_surfaces": (
                "surface:seat_*/platform",
                "surface:seat_*/floor_pan",
                "surface:seat_*/slat_*",
                "surface:seat_*/bucket_shell",
            ),
            "chairs": ("part:seat_*",),
            "all_surfaces": ("surface:*",),
        },
        display_name="Playground chair-swing carousel",
        front_axis="+x",
    ),
    "fence": GeneratorAdapter(
        name="fence",
        source_filename="Fence_Cascade_fences_MORE_THAN_1.py",
        source_template="agent/templates/Fence_Cascade_fences_MORE_THAN_1.py",
        config_class="FenceCascadeConfig",
        build_function="build_fence_cascade",
        resolve_function="resolve_config",
        seed_function="config_from_seed",
        axes=_FENCE_AXES,
        target_patterns={
            "panel_infill": ("visual:infill",),
            "panels": ("part:panel_*",),
            "all_surfaces": ("surface:*",),
        },
        material_patterns={
            "panel_infill": ("surface:panel_*/infill",),
            "panels": ("part:panel_*",),
            "all_surfaces": ("surface:*",),
        },
        display_name="Articulated cascade fence",
        front_axis="+y",
    ),
    "playground_swing": GeneratorAdapter(
        name="playground_swing",
        source_filename="Playground_swing.py",
        source_template="agent/templates/Playground_swing.py",
        config_class="PlaygroundSwingSetConfig",
        build_function="build_playground_swing_set",
        resolve_function="resolve_config",
        seed_function="config_from_seed",
        axes=_PLAYGROUND_SWING_AXES,
        target_patterns={
            "seat": (
                "visual:belt_seat",
                "visual:plank_seat",
                "visual:tire_shell",
            ),
            "swing": ("part:swing_*",),
            "frame": ("surface:*",),
            "all_surfaces": ("surface:*",),
        },
        material_patterns={
            "seat_surface": (
                "surface:swing_*/belt_seat",
                "surface:swing_*/plank_seat",
                "surface:swing_*/tire_shell",
            ),
            "swing": ("part:swing_*",),
            "all_surfaces": ("surface:*",),
        },
        display_name="Playground swing set",
        front_axis="+x",
    ),
    "monitor_mount": GeneratorAdapter(
        name="monitor_mount",
        source_filename="monitor_mount.py",
        source_template="agent/templates/monitor_mount.py",
        config_class="MonitorMountConfig",
        build_function="build_monitor_mount",
        resolve_function="resolve_config",
        seed_function="config_from_seed",
        axes=_MONITOR_MOUNT_AXES,
        target_patterns={
            "wall_mount": ("part:wall_bracket",),
            "arm_chain": ("part:arm_segment_*",),
            "arm_links": (
                "visual:link_side_rail_*",
                "visual:link_box_beam",
                "visual:simple_link_beam",
            ),
            "all_surfaces": ("surface:*",),
        },
        material_patterns={
            "arm_links": (
                "surface:arm_segment_*/link_side_rail_*",
                "surface:arm_segment_*/link_box_beam",
                "surface:arm_segment_*/simple_link_beam",
            ),
            "wall_mount": ("part:wall_bracket",),
            "all_surfaces": ("surface:*",),
        },
        display_name="Multi-segment monitor mount",
        front_axis="-y",
    ),
}

_ALIASES = {
    "single_revolute_hinge": "hinge",
    "cabinet_doors": "cabinet",
    "drawer_cabinet": "drawers",
    "ceiling_fan": "fan",
    "wind_turbine": "turbine",
    "parabolic_dish_mount": "parabolic_dish_on_azimuth_elevation_mount",
    "Parabolic_dish_on_azimuth_elevation_mount": "parabolic_dish_on_azimuth_elevation_mount",
    "Sports_Table_football": "table_football",
    "Table_football": "table_football",
    "Playground_playground_chair_swing_carousel": "playground_chair_swing_carousel",
    "Fence_Cascade_fences_MORE_THAN_1": "fence",
    "Playground_swing": "playground_swing",
    "counterbalanced_monitor_mount": "monitor_mount",
}
_MODULE_CACHE: dict[str, ModuleType] = {}


def list_generators() -> tuple[str, ...]:
    return tuple(sorted(_REGISTRY))


def get_generator(name: str) -> GeneratorAdapter:
    key = _ALIASES.get(str(name).strip(), str(name).strip())
    try:
        return _REGISTRY[key]
    except KeyError as exc:
        choices = ", ".join(list_generators())
        raise CatalogError(f"Unknown visual generator {name!r}; choose from: {choices}") from exc


__all__ = ["AxisDescriptor", "CatalogError", "GeneratorAdapter", "get_generator", "list_generators"]
