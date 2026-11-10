# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from agent.templates.pictureX_0611_kitchen_cabinet import (
    Config,
    build_pictureX_0611_kitchen_cabinet,
)


def _visual_classes(config: Config) -> dict[str, str | None]:
    model = build_pictureX_0611_kitchen_cabinet(config)
    return {
        str(visual.name): getattr(visual, "material_class_id", None)
        for part in model.parts
        for visual in part.visuals
    }


@pytest.mark.parametrize(
    "config",
    [
        Config(
            access_module="hinged_doors",
            door_face="reeded_slab",
            top_treatment="stone_slab_worktop",
            support_base="adjustable_legs",
        ),
        Config(
            access_module="drawer_stack",
            door_face="shaker_panel",
            top_treatment="laminate_worktop",
            support_base="solid_plinth",
        ),
        Config(
            access_module="lift_up_flap",
            door_face="seamed_slab",
            top_treatment="worktop_with_upstand",
            support_base="block_feet",
        ),
        Config(
            access_module="drawer_stack",
            door_face="flat_panel",
            top_treatment="laminate_worktop",
            support_base="legs_with_toe_board",
        ),
        Config(
            cabinet_body="plinth_deck_cabinet",
            access_module="hinged_doors",
            door_face="flat_panel",
            top_treatment="laminate_worktop",
            support_base="solid_plinth",
        ),
    ],
)
def test_every_visual_has_a_supported_material_pool(config: Config) -> None:
    classes = _visual_classes(config)

    assert classes
    assert set(classes.values()) <= {
        "metal.stainless_matte",
        "rubber.smooth_plain",
        "stone.polished_granite",
        "wood.engineered_board",
    }
    assert None not in classes.values()


def test_stone_worktop_keeps_one_stone_class_across_box_and_round_geometry() -> None:
    classes = _visual_classes(Config(top_treatment="stone_slab_worktop"))
    worktop_classes = {
        material_class_id
        for name, material_class_id in classes.items()
        if name.startswith("top_treatment__stone_slab_worktop__")
    }

    assert worktop_classes == {"stone.polished_granite"}


@pytest.mark.parametrize("access_module", ["hinged_doors", "lift_up_flap"])
def test_hinge_hardware_is_metal_even_when_the_visual_is_a_box(access_module: str) -> None:
    classes = _visual_classes(Config(access_module=access_module))
    hardware = {
        name: material_class_id
        for name, material_class_id in classes.items()
        if any(token in name for token in ("knuckle", "barrel", "hinge_strap", "__stay_"))
    }

    assert hardware
    assert set(hardware.values()) == {"metal.stainless_matte"}


def test_reeded_wood_front_stays_wood_across_box_and_round_geometry() -> None:
    classes = _visual_classes(Config(door_face="reeded_slab"))
    reeded_front = {
        material_class_id
        for name, material_class_id in classes.items()
        if name.startswith("door_face__reeded_slab__") and "__pull_" not in name
    }

    assert reeded_front == {"wood.engineered_board"}


def test_support_materials_distinguish_rubber_metal_and_wood() -> None:
    adjustable = _visual_classes(Config(support_base="adjustable_legs"))
    block = _visual_classes(Config(support_base="block_feet"))

    assert {
        material_class_id for name, material_class_id in adjustable.items() if "__foot_" in name
    } == {"rubber.smooth_plain"}
    assert {
        material_class_id
        for name, material_class_id in adjustable.items()
        if "__stem_" in name or "__mount_" in name
    } == {"metal.stainless_matte"}
    assert {
        material_class_id for name, material_class_id in block.items() if "__glide_" in name
    } == {"rubber.smooth_plain"}
    assert {
        material_class_id for name, material_class_id in block.items() if "__foot_block_" in name
    } == {"wood.engineered_board"}
    assert {
        material_class_id for name, material_class_id in block.items() if "__block_cap_" in name
    } == {"metal.stainless_matte"}


def test_drawer_slide_hardware_is_metal() -> None:
    classes = _visual_classes(Config(access_module="drawer_stack", access_count=2))
    slide_hardware = {
        material_class_id
        for name, material_class_id in classes.items()
        if "__tray_runner_" in name or "__runner_rail_" in name
    }

    assert slide_hardware == {"metal.stainless_matte"}


def test_drawer_level_rails_are_wooden_support_boards() -> None:
    classes = _visual_classes(Config(access_module="drawer_stack", access_count=3))
    level_rails = {
        material_class_id for name, material_class_id in classes.items() if "__level_rail_" in name
    }

    assert level_rails == {"wood.engineered_board"}
