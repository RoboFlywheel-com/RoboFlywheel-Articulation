# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
import trimesh
from PIL import Image, ImageDraw

from sdk import ArticulatedObject, AssetContext, Box, Inertial
from sdk._core.v0.types import Collision
from specific_editing.export import export_visual_assets
from specific_editing.generators import get_generator, list_generators
from specific_editing.pbr_materials import (
    BLACK_RUBBER,
    BRASS,
    BRUSHED_SILVER,
    GREEN_FELT,
    OAK,
    RED_PAINT,
    SMOKED_GLASS,
    SOLAR_CELL,
    WALNUT,
    WHITE_PAINT,
    curated_material_id,
)
from specific_editing.pipeline import (
    PipelineError,
    _comparison_group_names,
    apply_material_override,
    run_pipeline,
    validate_spec,
)
from specific_editing.render import extract_visual_meshes, make_contact_sheet, render_model
from specific_editing.selectors import matching_surface_keys

EXPECTED_GENERATORS = {
    "cabinet",
    "drawers",
    "fan",
    "fence",
    "ferris_wheel",
    "hinge",
    "monitor_mount",
    "parabolic_dish_on_azimuth_elevation_mount",
    "playground_chair_swing_carousel",
    "playground_swing",
    "table_football",
    "turbine",
}
EXPECTED_EDIT_KINDS = {"component", "count", "material", "size"}
BLENDER_EXECUTABLE = Path("/tmp/blender-4.2.21-linux-x64/blender")


def _write_spec(path: Path, *, edit: dict[str, object], name: str = "hinge_test") -> Path:
    payload = {
        "schema_version": 1,
        "name": name,
        "generator": "hinge",
        "base_config": {
            "fixed_style": "leaf_with_knuckles",
            "moving_style": "opposing_leaf",
            "hinge_line_style": "interleaved_knuckles_pin_in_leaf",
            "palette_theme": "brass",
            "knuckle_count": 3,
            "leaf_height": 0.07,
            "leaf_x": 0.03,
        },
        "edits": [edit],
        "render": {
            "backend": "software",
            "views": ["front_iso"],
            "poses": ["closed"],
            "image_size": [128, 128],
        },
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _visual_model_with_physics() -> ArticulatedObject:
    model = ArticulatedObject(name="visual_export_probe")
    material = model.material("display_blue", rgba=(0.18, 0.42, 0.78, 1.0))
    part = model.part("display_panel")
    visual_geometry = Box((0.20, 0.12, 0.04))
    part.visual(visual_geometry, material=material, name="display_surface")
    part.inertial = Inertial.from_geometry(visual_geometry, mass=2.0)
    part.collisions.append(Collision(Box((0.18, 0.10, 0.03)), name="physics_collision"))
    return model


def test_catalog_exposes_registered_generators_with_all_edit_kinds() -> None:
    assert set(list_generators()) == EXPECTED_GENERATORS

    for generator_name in EXPECTED_GENERATORS:
        registration = get_generator(generator_name)
        assert {axis.kind for axis in registration.axes} == EXPECTED_EDIT_KINDS
        assert all(axis.values for axis in registration.axes)
        assert registration.axis("material").field == "material_override"
        assert registration.material_patterns
        assert registration.source_path.is_file()


def test_catalog_default_material_targets_match_real_surfaces(tmp_path: Path) -> None:
    for generator_name in EXPECTED_GENERATORS:
        registration = get_generator(generator_name)
        target = registration.axis("material").target
        model = registration.build(
            registration.make_config(),
            assets=AssetContext(tmp_path / generator_name),
        )

        matched = matching_surface_keys(model, registration.material_patterns[target])

        assert matched, f"{generator_name}:{target} matched no visual surfaces"












def test_parabolic_dish_mount_spec_exposes_two_count_axes() -> None:
    spec, summary = validate_spec(
        Path("specific_editing/specs/single_variable/parabolic_dish_on_azimuth_elevation_mount.json")
    )

    assert spec.generator_id == "parabolic_dish_on_azimuth_elevation_mount"
    assert summary["variant_count"] == 14
    count_targets = {
        variant["target"] for variant in summary["variants"] if variant["kind"] == "count"
    }
    assert count_targets == {"support_leg_count", "feed_strut_count"}


@pytest.mark.parametrize(
    ("name", "variant_count"),
    [
        ("ferris_wheel", 12),
        ("table_football", 10),
        ("playground_chair_swing_carousel", 10),
        ("fence", 10),
        ("playground_swing", 10),
        ("monitor_mount", 10),
    ],
)
def test_new_showcase_specs_cover_all_directed_edit_kinds(name: str, variant_count: int) -> None:
    spec, summary = validate_spec(Path("specific_editing/specs/single_variable") / f"{name}.json")

    assert spec.generator_id == name
    assert summary["variant_count"] == variant_count
    assert {variant["kind"] for variant in summary["variants"]} == EXPECTED_EDIT_KINDS


def test_comparison_groups_number_duplicate_edit_kinds_without_overwriting() -> None:
    groups = {
        ("count", "solar_array_module"): [],
        ("count", "panel_segment_count"): [],
        ("component", "payload_module"): [],
    }

    names = _comparison_group_names(groups)

    assert names[("component", "payload_module")] == "component"
    assert names[("count", "panel_segment_count")] == "count"
    assert names[("count", "solar_array_module")] == "count_1"


def test_monitor_mount_count_axis_builds_real_serial_links(tmp_path: Path) -> None:
    registration = get_generator("monitor_mount")
    axis = registration.axis_for_target("count", "arm_segment_count")
    base_segment_length = registration.resolve(
        registration.make_config({"arm_segment_count": 5})
    ).segment_length

    assert axis.values == (2, 5, 20)
    for count in axis.values:
        config = registration.make_config({"arm_segment_count": count})
        resolved = registration.resolve(config)
        model = registration.build(
            config,
            assets=AssetContext(tmp_path / f"monitor_mount_{count}"),
        )
        segments = [part for part in model.parts if part.name.startswith("arm_segment_")]
        moving_joints = [
            joint
            for joint in model.articulations
            if str(getattr(joint.articulation_type, "value", joint.articulation_type))
            != "fixed"
        ]

        assert len(segments) == count
        assert len(moving_joints) == count + 3
        assert model.meta["arm_segment_count"] == count
        assert resolved.segment_length == pytest.approx(base_segment_length)
        assert model.meta["arm_segment_length"] == pytest.approx(base_segment_length)
        assert all(
            joint.child == f"arm_segment_{index + 1:02d}"
            for index, joint in enumerate(moving_joints[1 : count + 1])
        )


def test_validate_spec_accepts_registered_count_target(tmp_path: Path) -> None:
    spec_path = _write_spec(
        tmp_path / "valid.json",
        edit={
            "kind": "count",
            "target": "knuckle_count",
            "label": "Knuckle count",
            "values": [3, 5],
        },
    )

    spec, summary = validate_spec(spec_path)

    assert spec.generator_id == "hinge"
    assert summary["status"] == "valid"
    assert summary["variant_count"] == 2
    assert [variant["value"] for variant in summary["variants"]] == [3, 5]


def test_blender_is_default_and_vtk_is_not_a_public_backend(tmp_path: Path) -> None:
    spec_path = _write_spec(
        tmp_path / "backend.json",
        edit={"kind": "count", "target": "knuckle_count", "values": [3]},
    )
    payload = json.loads(spec_path.read_text(encoding="utf-8"))
    payload["render"].pop("backend")
    spec_path.write_text(json.dumps(payload), encoding="utf-8")

    spec, _summary = validate_spec(spec_path)
    assert spec.renderer == "blender"
    assert spec.frame_scope == "global"

    payload["render"]["backend"] = "vtk"
    spec_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(PipelineError, match="blender.*software"):
        validate_spec(spec_path)


def test_edit_group_frame_scope_keeps_comparison_axes_independent(tmp_path: Path) -> None:
    spec_path = _write_spec(
        tmp_path / "grouped_frames.json",
        name="hinge_grouped_frames",
        edit={"kind": "size", "target": "leaf_height", "values": [0.08]},
    )
    payload = json.loads(spec_path.read_text(encoding="utf-8"))
    payload["edits"].append(
        {"kind": "count", "target": "knuckle_count", "values": [5]}
    )
    payload["render"]["frame_scope"] = "edit_group"
    spec_path.write_text(json.dumps(payload), encoding="utf-8")

    result = run_pipeline(spec_path, tmp_path / "output")
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))

    assert result.variant_count == 2
    assert result.image_count == 6
    assert manifest["render_contract"]["frame_scope"] == "edit_group"
    assert manifest["render_contract"]["camera"] == "shared_world_space_frame_per_edit_group"
    assert set(manifest["comparison_frames"]) == {"count", "size"}
    assert set(manifest["base"]["comparison_renders"]) == {"count", "size"}


def test_compact_contact_sheet_removes_cell_whitespace(tmp_path: Path) -> None:
    sources: list[Path] = []
    for index, width in enumerate((48, 112)):
        image = Image.new("RGB", (200, 120), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle((12, 62, 12 + width, 94), fill=(24, 28, 32))
        source = tmp_path / f"source_{index}.png"
        image.save(source)
        image.close()
        sources.append(source)

    regular = make_contact_sheet(
        sources,
        tmp_path / "regular.png",
        labels=("Base", "Segment count: 20"),
        columns=2,
        cell_size=(160, 96),
    )
    compact = make_contact_sheet(
        sources,
        tmp_path / "compact.png",
        labels=("Base", "Segment count: 20"),
        columns=2,
        cell_size=(160, 96),
        compact_foreground=True,
    )

    assert compact.quality.width < regular.quality.width
    assert compact.quality.height < regular.quality.height


def test_validate_spec_rejects_undeclared_target(tmp_path: Path) -> None:
    spec_path = _write_spec(
        tmp_path / "invalid.json",
        edit={
            "kind": "size",
            "target": "blade_span",
            "values": [0.4],
        },
    )

    with pytest.raises(PipelineError, match="blade_span.*not declared"):
        validate_spec(spec_path)


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ({"name": "bad", "rgba": [0.2, 0.3, float("nan")]}, "rgba"),
        ({"name": "bad", "rgba": [0.2, 0.3, 0.4], "metallic": None}, "metallic"),
        (
            {
                "name": "bad",
                "rgba": [0.2, 0.3, 0.4],
                "parts": ["moving_half"],
                "surfaces": ["visual:moving_leaf"],
            },
            "parts or surfaces",
        ),
        ({"name": "bad", "rgba": [0.2, 0.3, 0.4], "material_id": ""}, "material_id"),
    ],
)
def test_validate_spec_rejects_invalid_material_values(
    tmp_path: Path, value: dict[str, object], message: str
) -> None:
    spec_path = _write_spec(
        tmp_path / "invalid_material.json",
        edit={"kind": "material", "target": "hinge_leaves", "values": [value]},
    )

    with pytest.raises(PipelineError, match=message):
        validate_spec(spec_path)


def test_material_override_changes_only_matching_part() -> None:
    model = ArticulatedObject(name="material_target_probe")
    original = model.material("original", rgba=(0.52, 0.32, 0.16, 1.0))
    door = model.part("door_leaf_0")
    door.visual(Box((0.4, 0.04, 0.7)), material=original, name="door_panel")
    door.visual(Box((0.04, 0.05, 0.12)), material=original, name="door_handle")
    carcass = model.part("carcass")
    carcass.visual(Box((0.5, 0.3, 0.8)), material=original, name="cabinet_shell")

    matched = apply_material_override(
        model,
        target="door",
        material={
            "name": "brushed aluminum",
            "material_id": WALNUT,
            "rgba": [0.62, 0.66, 0.70, 1.0],
            "metallic": 0.85,
            "roughness": 0.24,
            "surfaces": ["surface:door_leaf_*/door_panel"],
        },
    )

    assert matched == ("door_leaf_0/door_panel",)
    assert door.visuals[0].material.name == "brushed-aluminum"
    assert door.visuals[0].material.rgba == pytest.approx((0.62, 0.66, 0.70, 1.0))
    assert door.visuals[1].material is original
    assert carcass.visuals[0].material is original
    assert model.meta["specific_editing_material_overrides"][0]["parts"] == ["door_leaf_0"]
    assert model.meta["specific_editing_material_overrides"][0]["surfaces"] == [
        "door_leaf_0/door_panel"
    ]
    assert model.meta["specific_editing_material_overrides"][0]["material_id"] == WALNUT
    rendered_surfaces = {surface.key: surface for surface in extract_visual_meshes(model)}
    assert rendered_surfaces["door_leaf_0/door_panel"].pbr_material_id == WALNUT
    assert rendered_surfaces["door_leaf_0/door_panel"].metallic == pytest.approx(0.85)
    assert rendered_surfaces["door_leaf_0/door_panel"].roughness == pytest.approx(0.24)
    assert rendered_surfaces["door_leaf_0/door_handle"].metallic == pytest.approx(0.0)


def test_curated_theme_uses_semantic_generator_material_names() -> None:
    assert curated_material_id("cabinet", "cabinet_7_wood") == OAK
    assert curated_material_id("cabinet", "cabinet_2_panel") == OAK
    assert curated_material_id("drawers", "chest_4_wood") == WALNUT
    assert (
        curated_material_id(
            "parabolic_dish_on_azimuth_elevation_mount", "dish_reflector_inner"
        )
        == WHITE_PAINT
    )
    assert curated_material_id("ferris_wheel", "frame_main_painted_white") == WHITE_PAINT
    assert curated_material_id("ferris_wheel", "cabin_body_red_and_cream") == RED_PAINT
    assert (
        curated_material_id("table_football", "foosball_pitch_natural_wood_red_blue") == GREEN_FELT
    )
    assert curated_material_id("playground_chair_swing_carousel", "seat_seat") == OAK
    assert curated_material_id("fence", "fence_picket_safety_orange") == RED_PAINT
    assert curated_material_id("playground_swing", "swing_0_seat") == BLACK_RUBBER
    assert curated_material_id("playground_swing", "swing_2_wood") == OAK
    assert curated_material_id("monitor_mount", "monitor_mount_link") == BRUSHED_SILVER
    assert curated_material_id("monitor_mount", "monitor_mount_screen") == SMOKED_GLASS
    assert curated_material_id("unknown", "cabinet_7_wood") is None


def test_visual_exports_omit_inertial_and_collision_geometry(tmp_path: Path) -> None:
    model = _visual_model_with_physics()

    outputs = export_visual_assets(model, tmp_path / "exports")

    root = ET.fromstring(outputs["visual_urdf"].read_text(encoding="utf-8"))
    assert len(root.findall(".//visual")) == 1
    assert root.findall(".//inertial") == []
    assert root.findall(".//collision") == []

    scene = trimesh.load_scene(outputs["scene_glb"], process=False)
    assert len(scene.geometry) == 1
    assert b"physics_collision" not in outputs["scene_glb"].read_bytes()

    receipt = json.loads(outputs["receipt"].read_text(encoding="utf-8"))
    assert receipt["purpose"] == "visualization_only"
    assert receipt["physics_exported"] is False
    assert receipt["glb"]["surface_count"] == 1


def test_small_software_pipeline_smoke(tmp_path: Path) -> None:
    spec_path = _write_spec(
        tmp_path / "smoke.json",
        name="hinge_software_smoke",
        edit={
            "kind": "size",
            "target": "leaf_height",
            "label": "Leaf height",
            "values": [0.08],
        },
    )

    result = run_pipeline(spec_path, tmp_path / "output")

    assert result.variant_count == 1
    assert result.image_count == 3
    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["purpose"] == "directed_3d_editing_visualization"
    assert manifest["validation_level"] == "build_and_render_only"
    assert manifest["render_contract"]["background_hex"] == "#FFFFFF"
    assert manifest["render_contract"]["shadow"] == "none"
    assert len(manifest["variants"]) == 1

    relative_renders = [
        *manifest["base"]["renders"].values(),
        *manifest["variants"][0]["renders"].values(),
    ]
    assert len(relative_renders) == 2
    for relative_path in relative_renders:
        image_path = result.output_root / relative_path
        assert image_path.is_file()
        with Image.open(image_path) as image:
            assert image.size == (128, 128)
            assert len(image.convert("RGB").getcolors(maxcolors=128 * 128) or ()) > 1

    assert len(manifest["comparisons"]) == 1
    comparison_path = result.output_root / next(iter(manifest["comparisons"].values()))
    with Image.open(comparison_path) as comparison:
        assert comparison.width > 128
        assert comparison.height > 128
        assert (
            len(
                comparison.convert("RGB").getcolors(maxcolors=comparison.width * comparison.height)
                or ()
            )
            > 1
        )

    for section in (manifest["base"], manifest["variants"][0]):
        for relative_path in section["exports"].values():
            assert (result.output_root / relative_path).is_file()


@pytest.mark.skipif(not BLENDER_EXECUTABLE.is_file(), reason="documented Blender is unavailable")
def test_blender_batch_render_smoke(tmp_path: Path) -> None:
    records = render_model(
        _visual_model_with_physics(),
        tmp_path / "renders",
        views=("front_iso", "side"),
        renderer="blender",
        image_size=(128, 128),
        supersample=1,
    )

    assert [record.renderer for record in records] == ["blender", "blender"]
    assert [record.view for record in records] == ["front_iso", "side"]
    for record in records:
        assert record.quality.width == 128
        assert record.quality.height == 128
        assert record.quality.foreground_fraction > 0.01
        with Image.open(record.path) as image:
            corner = image.convert("RGB").getpixel((0, 0))
            assert corner == (255, 255, 255)
