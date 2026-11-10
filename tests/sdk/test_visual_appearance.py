# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import pytest

from sdk import (
    BLENDERKIT_MATERIAL_CATEGORIES,
    AppearanceOnlyKind,
    AppearanceOnlySpec,
    ArticulatedObject,
    Box,
    Material,
    Origin,
    ValidationError,
    Visual,
)


def test_official_blenderkit_category_contract_contains_runtime_parents() -> None:
    assert {"fabric", "glass", "metal", "plastic", "rubber", "wood"}.issubset(
        BLENDERKIT_MATERIAL_CATEGORIES
    )


def test_visual_positional_core_fields_are_unchanged() -> None:
    visual = Visual(
        Box((0.1, 0.1, 0.1)),
        Origin(),
        "ordinary_material",
        "shell",
        "_build_shell",
    )

    assert visual.material == "ordinary_material"
    assert visual.name == "shell"
    assert visual.builder == "_build_shell"
    assert visual.material_class_id is None
    assert visual.appearance_only is None
    assert not hasattr(visual, "appearance")
    assert not hasattr(visual, "graphic")
    assert not hasattr(visual, "cavity_mode")


def test_part_visual_accepts_scalar_class_with_authoring_material() -> None:
    model = ArticulatedObject(name="material_class")
    fallback = model.material("fallback", rgba=(0.1, 0.2, 0.3, 1.0))
    visual = model.part("body").visual(
        Box((0.1, 0.1, 0.1)),
        material=fallback,
        material_class_id="metal.brushed_steel",
        name="shell",
    )

    assert visual.material_class_id == "metal.brushed_steel"
    assert visual.material is fallback
    model.validate(strict=True)


@pytest.mark.parametrize("removed_keyword", ["appearance", "graphic", "cavity_mode"])
def test_part_visual_rejects_removed_appearance_keywords(removed_keyword: str) -> None:
    part = ArticulatedObject(name="removed").part("body")

    with pytest.raises(TypeError, match="unexpected keyword"):
        part.visual(Box((0.1, 0.1, 0.1)), **{removed_keyword: object()})


@pytest.mark.parametrize("class_id", ["Metal.brushed", "composite.carbon", "metal"])
def test_part_visual_rejects_invalid_material_class(class_id: str) -> None:
    part = ArticulatedObject(name="invalid").part("body")

    with pytest.raises(ValidationError):
        part.visual(Box((0.1, 0.1, 0.1)), material_class_id=class_id)


def test_part_visual_accepts_explicit_flat_color() -> None:
    model = ArticulatedObject(name="flat_color")
    panel = model.part("panel")
    color = model.material("marking", rgba=(0.1, 0.2, 0.3, 1.0))
    marking = panel.visual(
        Box((0.1, 0.1, 0.001)),
        name="marking",
        material=color,
    )

    assert marking.material is color
    assert isinstance(marking.material, Material)
    assert marking.material.rgba == (0.1, 0.2, 0.3, 1.0)
    model.validate(strict=True)


def test_part_visual_accepts_typed_appearance_only_payload() -> None:
    model = ArticulatedObject(name="decal")
    ink = model.material("warning_ink", rgba=(0.9, 0.1, 0.0, 0.75), texture="warning.png")
    spec = AppearanceOnlySpec(
        kind="decal",
        alpha_mode="blend",
        uv_offset=(0.1, 0.2),
        uv_scale=(2.0, 0.5),
        uv_rotation_rad=0.25,
    )

    visual = model.part("panel").visual(
        Box((0.1, 0.1, 0.001)),
        name="warning",
        material=ink,
        appearance_only=spec,
    )

    assert visual.appearance_only is spec
    assert spec.kind is AppearanceOnlyKind.DECAL
    assert spec.alpha_mode == "blend"
    assert spec.uv_offset == (0.1, 0.2)
    model.validate(strict=True)


def test_appearance_only_payload_validates_kind_specific_fields() -> None:
    emission = AppearanceOnlySpec(
        kind="emission",
        emission_color=(0.1, 0.4, 1.0),
        emission_strength=3.5,
    )
    text = AppearanceOnlySpec(kind="text", text="EXIT", alpha_mode="mask", alpha_cutoff=0.5)

    assert emission.kind is AppearanceOnlyKind.EMISSION
    assert emission.emission_strength == 3.5
    assert text.text == "EXIT"

    with pytest.raises(ValidationError, match="requires text"):
        AppearanceOnlySpec(kind="text")
    with pytest.raises(ValidationError, match="only valid for emission or screen"):
        AppearanceOnlySpec(kind="overlay", emission_strength=1.0)
    with pytest.raises(ValidationError, match="only valid when alpha_mode='mask'"):
        AppearanceOnlySpec(kind="decal", alpha_cutoff=0.5)


def test_part_visual_rejects_legacy_boolean_appearance_only() -> None:
    part = ArticulatedObject(name="legacy_bool").part("body")

    with pytest.raises(ValidationError, match="AppearanceOnlySpec"):
        part.visual(Box((0.1, 0.1, 0.1)), appearance_only=True)  # type: ignore[arg-type]


def test_mechanical_model_validation_does_not_require_pbr_annotation() -> None:
    model = ArticulatedObject(name="mechanical_only")
    model.part("body").visual(Box((0.1, 0.1, 0.1)), name="shell")

    model.validate(strict=True)


def test_model_validation_rechecks_directly_mutated_class() -> None:
    model = ArticulatedObject(name="mutated")
    visual = model.part("body").visual(
        Box((0.1, 0.1, 0.1)),
        material_class_id="metal.brushed_steel",
    )
    visual.material_class_id = "Metal.invalid"

    with pytest.raises(ValidationError, match="material_class_id"):
        model.validate(strict=True)
