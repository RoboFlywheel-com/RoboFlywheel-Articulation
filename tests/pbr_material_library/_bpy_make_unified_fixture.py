#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Create a compact nested-group material fixture for unified exporter tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import bpy  # type: ignore[import-not-found]


def _packed_image(name: str, offset: float) -> object:
    image = bpy.data.images.new(name, width=8, height=8, alpha=True)
    image.use_fake_user = True
    pixels: list[float] = []
    for y in range(8):
        for x in range(8):
            value = ((x + y) % 8) / 7.0
            pixels.extend((value, (value + offset) % 1.0, 1.0 - value, 1.0))
    image.pixels.foreach_set(pixels)
    image.pack()
    return image


def main() -> int:
    output_dir = Path(sys.argv[1]).resolve()
    material_id = sys.argv[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)

    base_image = _packed_image("Fixture Base Color", 0.2)
    roughness_image = _packed_image("Fixture Roughness", 0.4)
    height_image = _packed_image("Fixture Height", 0.6)
    ao_image = _packed_image("Fixture AO", 0.8)
    _packed_image("Fixture Orphan", 0.1)

    material = bpy.data.materials.new("Unified Nested Fixture")
    material.use_fake_user = True
    material.use_nodes = True
    material["articraft_material_id"] = material_id
    tree = material.node_tree
    tree.nodes.clear()
    output = tree.nodes.new("ShaderNodeOutputMaterial")
    output.name = "Material Output"

    group_tree = bpy.data.node_groups.new("Fixture Surface Group", "ShaderNodeTree")
    group_tree.interface.new_socket(
        name="Base Color", in_out="INPUT", socket_type="NodeSocketColor"
    )
    group_tree.interface.new_socket(name="Metallic", in_out="INPUT", socket_type="NodeSocketFloat")
    group_tree.interface.new_socket(name="IOR", in_out="INPUT", socket_type="NodeSocketFloat")
    group_tree.interface.new_socket(
        name="Dead Input", in_out="INPUT", socket_type="NodeSocketFloat"
    )
    group_tree.interface.new_socket(name="Shader", in_out="OUTPUT", socket_type="NodeSocketShader")
    group_input = group_tree.nodes.new("NodeGroupInput")
    group_input.name = "Group Input"
    group_output = group_tree.nodes.new("NodeGroupOutput")
    group_output.name = "Group Output"
    principled = group_tree.nodes.new("ShaderNodeBsdfPrincipled")
    principled.name = "Nested Principled"
    texcoord = group_tree.nodes.new("ShaderNodeTexCoord")
    texcoord.name = "Generated Coordinates"
    mapping = group_tree.nodes.new("ShaderNodeMapping")
    mapping.name = "Preserved Mapping"
    mapping.inputs["Scale"].default_value = (2.0, 3.0, 1.0)

    roughness = group_tree.nodes.new("ShaderNodeTexImage")
    roughness.name = "Roughness Image"
    roughness.image = roughness_image
    ao = group_tree.nodes.new("ShaderNodeTexImage")
    ao.name = "AO Image"
    ao.image = ao_image
    multiply = group_tree.nodes.new("ShaderNodeMixRGB")
    multiply.name = "AO Multiply"
    multiply.blend_type = "MULTIPLY"
    multiply.inputs["Fac"].default_value = 1.0
    constant_value = group_tree.nodes.new("ShaderNodeValue")
    constant_value.name = "Linked Constant Value"
    constant_value.outputs["Value"].default_value = 0.25
    constant_math = group_tree.nodes.new("ShaderNodeMath")
    constant_math.name = "Linked Constant Math"
    constant_math.operation = "MULTIPLY"
    constant_math.inputs[1].default_value = 2.0
    constant_roughness = group_tree.nodes.new("ShaderNodeMath")
    constant_roughness.name = "Linked Constant Roughness"
    constant_roughness.operation = "MULTIPLY_ADD"
    constant_roughness.inputs[1].default_value = 0.0
    constant_roughness.inputs[2].default_value = 0.4
    tilted_normal = group_tree.nodes.new("ShaderNodeRGB")
    tilted_normal.name = "Tilted Constant Normal Color"
    tilted_normal.outputs["Color"].default_value = (0.75, 0.5, 1.0, 1.0)
    normal_map = group_tree.nodes.new("ShaderNodeNormalMap")
    normal_map.name = "Tilted Constant Normal"
    group_tree.nodes.new("ShaderNodeLightPath").name = "Dead Light Path"

    group_tree.links.new(texcoord.outputs["Generated"], mapping.inputs["Vector"])
    for image_node in (roughness, ao):
        group_tree.links.new(mapping.outputs["Vector"], image_node.inputs["Vector"])
    group_tree.links.new(group_input.outputs["Base Color"], multiply.inputs[1])
    group_tree.links.new(ao.outputs["Color"], multiply.inputs[2])
    group_tree.links.new(multiply.outputs["Color"], principled.inputs["Base Color"])
    group_tree.links.new(roughness.outputs["Color"], constant_roughness.inputs[0])
    group_tree.links.new(constant_roughness.outputs["Value"], principled.inputs["Roughness"])
    group_tree.links.new(constant_value.outputs["Value"], constant_math.inputs[0])
    group_tree.links.new(constant_math.outputs["Value"], principled.inputs["Emission Strength"])
    group_tree.links.new(group_input.outputs["Metallic"], principled.inputs["Metallic"])
    group_tree.links.new(group_input.outputs["IOR"], principled.inputs["IOR"])
    group_tree.links.new(tilted_normal.outputs["Color"], normal_map.inputs["Color"])
    group_tree.links.new(normal_map.outputs["Normal"], principled.inputs["Normal"])
    group_tree.links.new(principled.outputs["BSDF"], group_output.inputs["Shader"])

    group = tree.nodes.new("ShaderNodeGroup")
    group.name = "SurfaceGroup"
    group.node_tree = group_tree
    outer_texcoord = tree.nodes.new("ShaderNodeTexCoord")
    outer_texcoord.name = "Outer Generated Coordinates"
    outer_mapping = tree.nodes.new("ShaderNodeMapping")
    outer_mapping.name = "Outer Preserved Mapping"
    outer_mapping.inputs["Scale"].default_value = (4.0, 5.0, 1.0)
    base = tree.nodes.new("ShaderNodeTexImage")
    base.name = "Outer Base Image"
    base.image = base_image
    height = tree.nodes.new("ShaderNodeTexImage")
    height.name = "Outer Height Image"
    height.image = height_image
    displacement = tree.nodes.new("ShaderNodeDisplacement")
    displacement.name = "Output Height Displacement"
    geometry = tree.nodes.new("ShaderNodeNewGeometry")
    geometry.name = "Outer Component Dependent Geometry"
    metallic = tree.nodes.new("ShaderNodeValue")
    metallic.name = "Outer Linked Constant Metallic"
    metallic.outputs["Value"].default_value = 0.3
    glass = tree.nodes.new("ShaderNodeBsdfGlass")
    glass.name = "Fallback Glass"
    translucent = tree.nodes.new("ShaderNodeBsdfTranslucent")
    translucent.name = "Ignored Translucent"
    glass_translucent = tree.nodes.new("ShaderNodeMixShader")
    glass_translucent.name = "Glass Translucent Mix"
    light_path = tree.nodes.new("ShaderNodeLightPath")
    light_path.name = "Ignored Light Path"
    mix = tree.nodes.new("ShaderNodeMixShader")
    mix.name = "Ignored Multi BSDF"
    volume = tree.nodes.new("ShaderNodeVolumePrincipled")
    volume.name = "Ignored Volume"
    tree.links.new(outer_texcoord.outputs["Generated"], outer_mapping.inputs["Vector"])
    tree.links.new(outer_mapping.outputs["Vector"], base.inputs["Vector"])
    tree.links.new(outer_mapping.outputs["Vector"], height.inputs["Vector"])
    tree.links.new(base.outputs["Color"], group.inputs["Base Color"])
    tree.links.new(height.outputs["Color"], displacement.inputs["Height"])
    tree.links.new(metallic.outputs["Value"], group.inputs["Metallic"])
    tree.links.new(geometry.outputs["Backfacing"], group.inputs["IOR"])
    tree.links.new(light_path.outputs["Ray Length"], group.inputs["Dead Input"])
    tree.links.new(glass.outputs["BSDF"], glass_translucent.inputs[1])
    tree.links.new(translucent.outputs["BSDF"], glass_translucent.inputs[2])
    tree.links.new(light_path.outputs["Is Camera Ray"], mix.inputs[0])
    tree.links.new(group.outputs["Shader"], mix.inputs[1])
    tree.links.new(glass_translucent.outputs["Shader"], mix.inputs[2])
    tree.links.new(mix.outputs["Shader"], output.inputs["Surface"])
    tree.links.new(displacement.outputs["Displacement"], output.inputs["Displacement"])
    tree.links.new(volume.outputs["Volume"], output.inputs["Volume"])

    bpy.ops.wm.save_as_mainfile(filepath=str(output_dir / "material.blend"))
    metadata = {
        "schema_version": "fixture/v1",
        "material_id": material_id,
        # Node QA counts image-node references; reopen QA counts unique packed
        # image datablocks, which is the converter's source-map coverage unit.
        "node_qa": {"packed_image_count": 8},
        "package": {"reopen_qa": {"packed_image_count": 5}},
        "channel_qa": {
            "channels": [
                {
                    "node_path": "root/Outer Base Image",
                    "image_name": base_image.name,
                    "role": "base_color",
                },
                {
                    "node_path": "root/SurfaceGroup/Roughness Image",
                    "image_name": roughness_image.name,
                    "role": "roughness",
                },
                {
                    "node_path": "root/Outer Height Image",
                    "image_name": height_image.name,
                    "role": "height",
                },
                {
                    "node_path": "root/SurfaceGroup/AO Image",
                    "image_name": ao_image.name,
                    "role": "ambient_occlusion",
                },
            ]
        },
    }
    (output_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
